"""Minimal message-driven loop for the controlled data-analysis prototype."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from . import config
from .answers import answers_match
from .executor import ExecResult, format_observation, run_step
from .llm import Model, ScriptExhaustedError
from .logger import StepLogger
from .parser import Action, format_error, parse_action


@dataclass(frozen=True)
class RunResult:
    final_answer: str | None
    terminated_reason: str
    matches_reference: bool | None


def _task_prompt(task: Mapping[str, object]) -> str:
    task_id = task.get("task_id", "unknown")
    question = task.get("question", "")
    guidelines = task.get("guidelines", "")
    return (
        f"Task ID: {task_id}\nQuestion: {question}\nGuidelines: {guidelines}\n"
        "Use Python code blocks to inspect the provided data and print intermediate "
        "results. The data is available at data/context/payments.csv relative to "
        "the execution directory. Finish with exactly one line: FINAL ANSWER: <value>."
    )


def _record(
    *,
    task_id: object,
    step: int,
    model_name: str,
    completion_text: str,
    action: Action,
    run_id: str,
    observation: str | None = None,
    execution: ExecResult | None = None,
    temperature: float = 0.0,
    terminated_reason: str | None = None,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "task_id": task_id,
        "step": step,
        "model": model_name,
        "temperature": temperature,
        "prompt_version": config.PROMPT_VERSION,
        "raw_output": completion_text,
        "action_type": action.type,
        "code": action.payload if action.type == "code" else None,
        "final_answer": action.payload if action.type == "final" else None,
        "observation": observation,
        "stdout": execution.stdout if execution else "",
        "stderr": execution.stderr if execution else "",
        "returncode": execution.returncode if execution else None,
        "timed_out": execution.timed_out if execution else False,
        "truncated": execution.truncated if execution else False,
        "stdout_len": execution.stdout_len if execution else 0,
        "terminated_reason": terminated_reason,
    }


def run_agent(
    task: Mapping[str, object],
    model: Model,
    logger: StepLogger,
    *,
    run_id: str = "run",
    max_steps: int = config.MAX_STEPS,
    max_invalid: int = config.MAX_INVALID,
    temperature: float = 0.0,
) -> RunResult:
    """Run one task until a protocol-valid final answer or a configured limit."""
    if max_steps < 1 or max_invalid < 1:
        raise ValueError("max_steps and max_invalid must be at least 1")

    prompt_path = Path(__file__).with_name("prompts") / f"{config.PROMPT_VERSION}.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": _task_prompt(task)},
    ]
    prior_codes: list[str] = []
    invalid_count = 0
    task_id = task.get("task_id")
    model_name = getattr(model, "model_name", type(model).__name__)

    for step in range(1, max_steps + 1):
        try:
            completions = model.generate(messages, n=1, temperature=temperature)
        except ScriptExhaustedError:
            return RunResult(None, "model_exhausted", None)
        if len(completions) != 1:
            raise ValueError("model.generate(n=1) must return exactly one completion")

        completion = completions[0]
        action = parse_action(completion.text)
        messages.append({"role": "assistant", "content": completion.text})
        observation: str | None = None
        execution: ExecResult | None = None

        if action.type == "invalid":
            invalid_count += 1
            observation = format_error(action.reason)
            messages.append({"role": "user", "content": observation})
        elif action.type == "code":
            invalid_count = 0
            execution = run_step(prior_codes, action.payload)
            observation = format_observation(execution)
            if execution.ok:
                prior_codes.append(action.payload)
            messages.append({"role": "user", "content": observation})
        else:
            invalid_count = 0

        if action.type == "final":
            terminated_reason = "final"
        elif invalid_count >= max_invalid:
            terminated_reason = "max_invalid"
        elif step == max_steps:
            terminated_reason = "max_steps"
        else:
            terminated_reason = None

        logger.log(
            _record(
                task_id=task_id,
                step=step,
                model_name=model_name,
                completion_text=completion.text,
                action=action,
                run_id=run_id,
                observation=observation,
                execution=execution,
                temperature=temperature,
                terminated_reason=terminated_reason,
            )
        )

        if action.type == "final":
            expected = task.get("answer")
            matches = (
                answers_match(action.payload, str(expected))
                if expected is not None
                else None
            )
            return RunResult(action.payload, "final", matches)
        if terminated_reason is not None:
            return RunResult(None, terminated_reason, None)

    raise AssertionError("unreachable: loop exits only by returning")

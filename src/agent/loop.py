"""Minimal message-driven loop for the controlled data-analysis prototype."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from . import config
from .executor import ExecResult, format_observation, run_step
from .llm import ApiFailedError, Model, ScriptExhaustedError
from .logger import StepLogger
from .parser import (
    DISCARDED_FINAL_NOTE,
    EARLY_FINAL_REASON,
    Action,
    check_protocol,
    format_error,
    parse_action,
)
from .pathscan import scan_code


@dataclass(frozen=True)
class RunResult:
    final_answer: str | None
    terminated_reason: str
    # Always None from run_agent: the loop never reads answers (D9). Run scripts
    # fill it from tasks/dev_tasks.json after the run returns.
    matches_reference: bool | None = None
    # D5 code-scan flags of all steps (each dict also carries "step"). The run
    # keeps going when a step is flagged; scripts merge this with the checksum flag.
    path_flags: tuple = ()


PROMPTS_DIR = Path(__file__).with_name("prompts")


def system_prompt_path(version: str) -> Path:
    path = PROMPTS_DIR / f"{version}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"unknown prompt version {version!r} (no {path.name})")
    return path


def system_prompt_sha256(version: str) -> str:
    """SHA-256 of the system prompt file's exact bytes."""
    return hashlib.sha256(system_prompt_path(version).read_bytes()).hexdigest()


# First user message per prompt version. Only {task_id}, {question} and
# {guidelines} are filled in; the values are inserted as-is (never re-parsed).
# system_v0 must stay byte-identical to baseline-v0.
TASK_TEMPLATES = {
    "system_v0": (
        "Task ID: {task_id}\nQuestion: {question}\nGuidelines: {guidelines}\n"
        "Use Python code blocks to inspect the provided data and print intermediate "
        "results. The data is available at data/context/payments.csv relative to "
        "the execution directory. Finish with exactly one line: FINAL ANSWER: <value>."
    ),
    # v1: drops the sentence naming only payments.csv (the system prompt lists all files).
    "system_v1": (
        "Task ID: {task_id}\nQuestion: {question}\nGuidelines: {guidelines}\n"
        "Use Python code blocks to inspect the provided data and print intermediate "
        "results. Finish with exactly one line: FINAL ANSWER: <value>."
    ),
}


def task_template(version: str) -> str:
    try:
        return TASK_TEMPLATES[version]
    except KeyError:
        raise KeyError(f"no task-message template for prompt version {version!r}") from None


def check_prompt_version(version: str) -> None:
    """Raise if the version lacks a system prompt file or a task-message template."""
    system_prompt_path(version)
    task_template(version)


def prompt_sha256(version: str) -> str:
    """SHA-256 over the system prompt bytes AND the task-message template (manifests)."""
    h = hashlib.sha256()
    h.update(system_prompt_path(version).read_bytes())
    h.update(b"\n--- task-message template ---\n")
    h.update(task_template(version).encode("utf-8"))
    return h.hexdigest()


def _task_prompt(task: Mapping[str, object], prompt_version: str = config.PROMPT_VERSION) -> str:
    return task_template(prompt_version).format_map({
        "task_id": task.get("task_id", "unknown"),
        "question": task.get("question", ""),
        "guidelines": task.get("guidelines", ""),
    })


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
    path_flags: list | None = None,
    prompt_version: str = config.PROMPT_VERSION,
    protocol: str = "v0",
    final_answer_discarded: bool = False,
) -> dict[str, object]:
    record = {
        "run_id": run_id,
        "task_id": task_id,
        "step": step,
        "model": model_name,
        "temperature": temperature,
        "prompt_version": prompt_version,
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
        "path_flags": list(path_flags or []),
    }
    if protocol != "v0":   # v0 records keep exactly the fields they had before
        record["protocol"] = protocol
        record["final_answer_discarded"] = final_answer_discarded
    return record


def run_agent(
    task: Mapping[str, object],
    model: Model,
    logger: StepLogger,
    *,
    workdir: Path | str,
    run_id: str = "run",
    max_steps: int = config.MAX_STEPS,
    max_invalid: int = config.MAX_INVALID,
    temperature: float = 0.0,
    prompt_version: str = config.PROMPT_VERSION,
    protocol: str = config.PROTOCOL_VERSION,
    max_tokens: int = 1024,
) -> RunResult:
    """Run one task until a protocol-valid final answer or a configured limit.

    ``workdir`` is the run's working folder (see workspace.create_workspace);
    executed code runs there and nowhere else by default.

    protocol "v0": baseline behaviour. protocol "v1" (D1, Track A):
      rule 1: one code block + one FINAL ANSWER line -> the code runs, the answer
              is discarded, the observation says so; logged final_answer_discarded.
      rule 2: a FINAL ANSWER before any code block has run without error is
              rejected as a format error (counts toward max_invalid).
    """
    if max_steps < 1 or max_invalid < 1:
        raise ValueError("max_steps and max_invalid must be at least 1")
    check_protocol(protocol)

    system_prompt = system_prompt_path(prompt_version).read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": _task_prompt(task, prompt_version)},
    ]
    prior_codes: list[str] = []
    run_flags: list[dict[str, object]] = []
    invalid_count = 0
    task_id = task.get("task_id")
    model_name = getattr(model, "model_name", type(model).__name__)

    for step in range(1, max_steps + 1):
        # Optional hook so a real model can tag its call log with (run_id, step).
        begin_step = getattr(model, "begin_step", None)
        if callable(begin_step):
            begin_step(run_id, step)
        try:
            completions = model.generate(messages, n=1, temperature=temperature,
                                         max_tokens=max_tokens)
        except ScriptExhaustedError:
            return RunResult(None, "model_exhausted", None, tuple(run_flags))
        except ApiFailedError:
            # Details (status, every attempt) are in the model's call log.
            return RunResult(None, "api_failed", None, tuple(run_flags))
        if len(completions) != 1:
            raise ValueError("model.generate(n=1) must return exactly one completion")

        completion = completions[0]
        action = parse_action(completion.text, protocol)
        # v1 rule 2: no FINAL ANSWER until some code block has run without error.
        if protocol == "v1" and action.type == "final" and not prior_codes:
            action = Action("invalid", "", EARLY_FINAL_REASON)
        messages.append({"role": "assistant", "content": completion.text})
        observation: str | None = None
        execution: ExecResult | None = None
        # D5 scan of the logged code block. The run is NOT stopped on a flag.
        step_flags = scan_code(action.payload) if action.type == "code" else []
        run_flags.extend({"step": step, **f} for f in step_flags)

        if action.type == "invalid":
            invalid_count += 1
            if action.reason == EARLY_FINAL_REASON:
                observation = f"Format error: {EARLY_FINAL_REASON}."
            else:
                observation = format_error(action.reason)
            messages.append({"role": "user", "content": observation})
        elif action.type == "code":
            invalid_count = 0
            execution = run_step(prior_codes, action.payload, workdir)
            observation = format_observation(execution)
            if action.discarded_final:   # v1 rule 1
                observation += "\n" + DISCARDED_FINAL_NOTE
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
                path_flags=step_flags,
                prompt_version=prompt_version,
                protocol=protocol,
                final_answer_discarded=bool(action.discarded_final),
            )
        )

        if action.type == "final":
            return RunResult(action.payload, "final", None, tuple(run_flags))
        if terminated_reason is not None:
            return RunResult(None, terminated_reason, None, tuple(run_flags))

    raise AssertionError("unreachable: loop exits only by returning")

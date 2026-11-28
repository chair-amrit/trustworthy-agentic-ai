"""Real runs with the Gemini backend (Track A, step 3; model settings per D3).

    python scripts/run_real.py --task 5 --runs 1

Per run:
  - new run_id and working folder config.WORK_ROOT/<run_id>/ (D5), read-only inputs
  - agent side loads only the answer-free task (D9); the API key stays in this process
  - step log      runs/<run_id>.jsonl
  - call log      runs/<run_id>.calls.jsonl   (each call carries run_id and step)
  - manifest      runs/<run_id>.manifest.json (D3 settings, git commit, flags, result)
  - path-scan and checksum flags; flagged lines go to runs/review_list.jsonl
  - matches_reference is filled from tasks/dev_tasks.json only AFTER the run returns.

Executed model code runs in a local subprocess. This is not a sandbox.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from agent import config  # noqa: E402
from agent.llm import GeminiLLM  # noqa: E402
from agent.logger import StepLogger  # noqa: E402
from agent.parser import PROTOCOLS  # noqa: E402
from agent.loop import (  # noqa: E402
    check_prompt_version, prompt_sha256, run_agent, system_prompt_sha256,
)
from agent.tasks import load_agent_task  # noqa: E402
from agent.workspace import create_workspace  # noqa: E402
from scripts.run_fake import fill_matches_reference, write_run_outputs  # noqa: E402

RUNS_DIR = ROOT / "runs"
DEFAULT_PROMPT = "system_v1"
DEFAULT_PROTOCOL = "v1"
THINKING_LEVELS = ("minimal", "low")   # flag choices; D3 default is "minimal"


def git_state(repo: Path = ROOT) -> dict[str, object]:
    def _git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                                  timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    changed = [line[3:] for line in _git("status", "--porcelain").splitlines() if line.strip()]
    return {"git_commit": _git("rev-parse", "HEAD") or None,
            "git_dirty": bool(changed), "git_changed_files": changed}


def _sum(records: list[dict], key: str) -> int | None:
    values = [r.get(key) for r in records if r.get("status") == "ok"]
    known = [v for v in values if v is not None]
    return sum(known) if known else None


def call_summary(records: list[dict]) -> dict[str, object]:
    return {
        "n_calls": len(records),
        "n_attempts": sum(r.get("n_attempts", 0) for r in records),
        "n_failed_calls": sum(1 for r in records if r.get("status") != "ok"),
        "input_tokens": _sum(records, "input_tokens"),
        "output_tokens": _sum(records, "output_tokens"),
        "thinking_tokens": _sum(records, "thinking_tokens"),   # null if never reported
        "thinking_tokens_missing_in_calls": sum(
            1 for r in records if r.get("status") == "ok" and r.get("thinking_tokens") is None),
        "total_tokens": _sum(records, "total_tokens"),
    }


def run_once(task_id: int, llm: GeminiLLM, run_index: int, *, runs_dir: Path = RUNS_DIR,
             work_root: Path | None = None, prompt_version: str = DEFAULT_PROMPT,
             protocol: str = DEFAULT_PROTOCOL) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"gemini-task-{task_id}-{stamp}-r{run_index}"
    step_log = runs_dir / f"{run_id}.jsonl"
    call_log = runs_dir / f"{run_id}.calls.jsonl"

    task = load_agent_task(task_id)
    ws = create_workspace(run_id, work_root=work_root)
    llm.start_run(run_id, call_log)
    started = datetime.now(timezone.utc).isoformat()

    result = run_agent(task, llm, StepLogger(step_log), workdir=ws.root, run_id=run_id,
                       temperature=config.GEMINI_TEMPERATURE, prompt_version=prompt_version,
                       protocol=protocol, max_tokens=llm.max_output_tokens)
    result = fill_matches_reference(result, task_id)   # evaluator-side, after the run

    steps_used = (len(step_log.read_text(encoding="utf-8").splitlines())
                  if step_log.exists() else 0)
    extra = {
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "status": result.terminated_reason,
        "final_answer": result.final_answer,
        "matches_reference": result.matches_reference,
        "steps_used": steps_used,
        "max_steps": config.MAX_STEPS,
        "protocol": protocol,
        "prompt_version": prompt_version,
        "prompt_sha256": prompt_sha256(prompt_version),          # system prompt + task template
        "system_prompt_sha256": system_prompt_sha256(prompt_version),
        "thinking_level": llm.thinking_level,
        "max_output_tokens": llm.max_output_tokens,
        "settings_are_d3_default": (llm.thinking_level, llm.max_output_tokens) == (
            config.GEMINI_THINKING_LEVEL, config.GEMINI_MAX_OUTPUT_TOKENS),
        "settings": llm.settings(),
        **call_summary(llm.call_records),
        "finish_reasons": [r.get("finish_reason") for r in llm.call_records],
        **git_state(),
        "step_log": step_log.name,
        "call_log": call_log.name,
    }
    return write_run_outputs(run_id, task_id, llm.model_name, result, ws, runs_dir, extra)


def main(argv: list[str] | None = None, llm: GeminiLLM | None = None, *,
         runs_dir: Path = RUNS_DIR, work_root: Path | None = None) -> list[dict]:
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, required=True)
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--prompt", default=DEFAULT_PROMPT,
                   help=f"system prompt version, a file in src/agent/prompts/ (default {DEFAULT_PROMPT})")
    p.add_argument("--protocol", default=DEFAULT_PROTOCOL, choices=PROTOCOLS,
                   help=f"action protocol (default {DEFAULT_PROTOCOL})")
    p.add_argument("--thinking", default=config.GEMINI_THINKING_LEVEL, choices=THINKING_LEVELS,
                   help=f"Gemini thinking_level (default {config.GEMINI_THINKING_LEVEL}, D3)")
    p.add_argument("--max-output-tokens", type=int, default=config.GEMINI_MAX_OUTPUT_TOKENS,
                   help=f"max output tokens incl. thinking (default "
                        f"{config.GEMINI_MAX_OUTPUT_TOKENS}, D3)")
    args = p.parse_args(argv)
    if args.runs < 1:
        p.error("--runs must be at least 1")
    if args.max_output_tokens < 1:
        p.error("--max-output-tokens must be at least 1")
    try:
        check_prompt_version(args.prompt)
    except (FileNotFoundError, KeyError) as exc:
        p.error(str(exc))

    # one instance: pacing carries over between runs
    if llm is None:
        llm = GeminiLLM(thinking_level=args.thinking, max_output_tokens=args.max_output_tokens)
    elif (llm.thinking_level, llm.max_output_tokens) != (args.thinking, args.max_output_tokens):
        p.error("the given model's thinking/max-output-tokens differ from the flags")
    manifests = []
    for i in range(1, args.runs + 1):
        m = run_once(args.task, llm, i, runs_dir=runs_dir, work_root=work_root,
                     prompt_version=args.prompt, protocol=args.protocol)
        manifests.append(m)
        print(json.dumps({k: m[k] for k in (
            "run_id", "protocol", "prompt_version", "thinking_level", "max_output_tokens",
            "status", "final_answer", "matches_reference",
            "steps_used", "n_calls",
            "n_attempts", "total_tokens", "flagged", "flag_reasons")}, indent=2))
    return manifests


if __name__ == "__main__":
    main()

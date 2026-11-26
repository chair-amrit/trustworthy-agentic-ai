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
from agent.loop import run_agent  # noqa: E402
from agent.tasks import load_agent_task  # noqa: E402
from agent.workspace import create_workspace  # noqa: E402
from scripts.run_fake import fill_matches_reference, write_run_outputs  # noqa: E402

RUNS_DIR = ROOT / "runs"


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
             work_root: Path | None = None) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"gemini-task-{task_id}-{stamp}-r{run_index}"
    step_log = runs_dir / f"{run_id}.jsonl"
    call_log = runs_dir / f"{run_id}.calls.jsonl"

    task = load_agent_task(task_id)
    ws = create_workspace(run_id, work_root=work_root)
    llm.start_run(run_id, call_log)
    started = datetime.now(timezone.utc).isoformat()

    result = run_agent(task, llm, StepLogger(step_log), workdir=ws.root, run_id=run_id,
                       temperature=config.GEMINI_TEMPERATURE)
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
        "prompt_version": config.PROMPT_VERSION,
        "settings": llm.settings(),
        **call_summary(llm.call_records),
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
    args = p.parse_args(argv)
    if args.runs < 1:
        p.error("--runs must be at least 1")

    llm = llm or GeminiLLM()   # one instance: pacing carries over between runs
    manifests = []
    for i in range(1, args.runs + 1):
        m = run_once(args.task, llm, i, runs_dir=runs_dir, work_root=work_root)
        manifests.append(m)
        print(json.dumps({k: m[k] for k in (
            "run_id", "status", "final_answer", "matches_reference", "steps_used", "n_calls",
            "n_attempts", "total_tokens", "flagged", "flag_reasons")}, indent=2))
    return manifests


if __name__ == "__main__":
    main()

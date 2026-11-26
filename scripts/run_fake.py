"""Run the deterministic fake model on DABStep development task 5.

Each run gets its own working folder outside the repo (D5):
config.WORK_ROOT/<run_id>/. The step log and a run manifest (input checksums,
flagged) are written to runs/ in the repo (git-ignored).

Answers (D9): the agent side loads the answer-free tasks/agent/dabstep_dev.json.
This script reads tasks/dev_tasks.json only AFTER run_agent has returned, to
fill matches_reference.
"""
import dataclasses
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.answers import answers_match
from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import RunResult, run_agent
from agent.tasks import load_agent_task
from agent.workspace import create_workspace, input_report


REFERENCE_PATH = ROOT / "tasks" / "dev_tasks.json"   # evaluator side: has answers
RUNS_DIR = ROOT / "runs"

TASK_5_CODE = """```python
import pandas as pd
payments = pd.read_csv('data/context/payments.csv')
print(payments['issuing_country'].value_counts().idxmax())
```"""


def fill_matches_reference(
    result: RunResult, task_id: int, reference_path: Path = REFERENCE_PATH
) -> RunResult:
    """Score a finished run against the public reference answer (after the run only)."""
    if result.final_answer is None:
        return result
    rows = json.loads(reference_path.read_text(encoding="utf-8"))
    expected = next(r for r in rows if r["task_id"] == task_id).get("answer")
    if expected is None:
        return result
    return dataclasses.replace(
        result, matches_reference=answers_match(result.final_answer, str(expected))
    )


def main() -> None:
    run_id = "fake-task-5-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = RUNS_DIR / f"{run_id}.jsonl"
    manifest_path = RUNS_DIR / f"{run_id}.manifest.json"

    task = load_agent_task(5)
    ws = create_workspace(run_id)
    model = FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"])
    result = run_agent(
        task,
        model,
        StepLogger(log_path),
        workdir=ws.root,
        run_id=run_id,
    )
    result = fill_matches_reference(result, 5)
    report = input_report(ws)
    manifest = {"run_id": run_id, "task_id": 5, "model": model.model_name, **report}
    RUNS_DIR.mkdir(exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Task 5: answer={result.final_answer!r}, "
        f"matches_reference={result.matches_reference}, "
        f"terminated_reason={result.terminated_reason}, flagged={report['flagged']}\n"
        f"workspace={ws.root}\nlog={log_path}\nmanifest={manifest_path}"
    )
    if result.final_answer is None or result.matches_reference is not True or report["flagged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

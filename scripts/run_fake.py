"""Run the deterministic fake model on DABStep development task 5.

Each run gets its own working folder outside the repo (D5):
config.WORK_ROOT/<run_id>/. The step log and a run manifest (input checksums,
flagged) are written to runs/ in the repo (git-ignored).
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.workspace import create_workspace, input_report


TASKS_PATH = ROOT / "tasks" / "dev_tasks.json"
RUNS_DIR = ROOT / "runs"

TASK_5_CODE = """```python
import pandas as pd
payments = pd.read_csv('data/context/payments.csv')
print(payments['issuing_country'].value_counts().idxmax())
```"""


def main() -> None:
    run_id = "fake-task-5-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = RUNS_DIR / f"{run_id}.jsonl"
    manifest_path = RUNS_DIR / f"{run_id}.manifest.json"

    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    task = next(task for task in tasks if task["task_id"] == 5)
    ws = create_workspace(run_id)
    model = FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"])
    result = run_agent(
        task,
        model,
        StepLogger(log_path),
        workdir=ws.root,
        run_id=run_id,
    )
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

"""Run the deterministic fake model on DABStep development task 5."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent


TASKS_PATH = ROOT / "tasks" / "dev_tasks.json"
LOG_PATH = ROOT / "runs" / "fake_task_5.jsonl"

TASK_5_CODE = """```python
import pandas as pd
payments = pd.read_csv('data/context/payments.csv')
print(payments['issuing_country'].value_counts().idxmax())
```"""


def main() -> None:
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    task = next(task for task in tasks if task["task_id"] == 5)
    model = FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"])
    result = run_agent(
        task,
        model,
        StepLogger(LOG_PATH),
        run_id="fake-task-5",
    )
    print(
        f"Task 5: answer={result.final_answer!r}, "
        f"matches_reference={result.matches_reference}, "
        f"terminated_reason={result.terminated_reason}, log={LOG_PATH}"
    )
    if result.final_answer is None or result.matches_reference is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

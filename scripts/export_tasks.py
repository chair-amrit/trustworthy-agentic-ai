"""Export the DABStep dev tasks (public answers) to tasks/dev_tasks.json.

Run from the repo root:  python scripts/export_tasks.py
All 10 dev tasks are exported unchanged; no task selection is made here.
"""
import json
from pathlib import Path

from datasets import load_dataset

REPO = "adyen/DABstep"
OUT = Path(__file__).resolve().parents[1] / "tasks" / "dev_tasks.json"


def main() -> None:
    dev = load_dataset(REPO, name="tasks", split="dev")
    rows = [
        {
            "task_id": int(r["task_id"]),
            "level": r["level"],
            "question": r["question"],
            "guidelines": r["guidelines"],
            "answer": r["answer"],
        }
        for r in dev
    ]
    rows.sort(key=lambda r: r["task_id"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {len(rows)} tasks to {OUT}")


if __name__ == "__main__":
    main()
"""Regenerate the answer-free agent task file (D9).

    python scripts/make_agent_tasks.py

Reads tasks/dev_tasks.json (evaluator side, has answers) and writes
tasks/agent/dabstep_dev.json with the "answer" field removed. No network.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.tasks import AGENT_TASKS_PATH, load_agent_tasks, strip_answers

SOURCE = ROOT / "tasks" / "dev_tasks.json"


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    agent_rows = strip_answers(rows)
    AGENT_TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_TASKS_PATH.write_text(
        json.dumps(agent_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    load_agent_tasks(AGENT_TASKS_PATH)  # re-read and verify: raises if an answer slipped through
    print(f"Wrote {len(agent_rows)} answer-free tasks to {AGENT_TASKS_PATH}")


if __name__ == "__main__":
    main()

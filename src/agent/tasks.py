"""Agent-side task loading (D9, Track A slice d).

The agent side reads ONLY the answer-free file tasks/agent/dabstep_dev.json.
Reference answers live in tasks/dev_tasks.json and are read by the run scripts
after run_agent returns, never by the agent runtime.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from . import config

AGENT_TASKS_PATH = config.REPO_ROOT / "tasks" / "agent" / "dabstep_dev.json"
FORBIDDEN_KEYS = frozenset({"answer"})


class AnswerLeakError(ValueError):
    """A task given to the agent side still carries a reference answer."""


def strip_answers(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Copy of the tasks with every forbidden key removed (used by the generator script)."""
    return [{k: v for k, v in row.items() if k not in FORBIDDEN_KEYS} for row in rows]


def check_answer_free(task: Mapping[str, object]) -> None:
    leaked = FORBIDDEN_KEYS & set(task)
    if leaked:
        raise AnswerLeakError(
            f"task {task.get('task_id')!r} has forbidden key(s) {sorted(leaked)}; "
            "the agent side must only load answer-free tasks"
        )


def load_agent_tasks(path: Path | str = AGENT_TASKS_PATH) -> list[dict[str, object]]:
    """Load the answer-free task file; refuse it if any task has an answer key."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    for row in rows:
        check_answer_free(row)
    return rows


def load_agent_task(task_id: int, path: Path | str = AGENT_TASKS_PATH) -> dict[str, object]:
    for row in load_agent_tasks(path):
        if row.get("task_id") == task_id:
            return row
    raise KeyError(f"task {task_id} not in {path}")

"""Slice d (D9): the agent side never holds or reads reference answers."""
import json
from collections.abc import Mapping

import pytest

from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.tasks import (
    AGENT_TASKS_PATH,
    AnswerLeakError,
    load_agent_task,
    load_agent_tasks,
    strip_answers,
)
from scripts.run_fake import REFERENCE_PATH, fill_matches_reference


def test_agent_file_has_no_answer_key():
    rows = json.loads(AGENT_TASKS_PATH.read_text(encoding="utf-8"))
    assert rows and all("answer" not in r for r in rows)


def test_agent_file_matches_reference_file_minus_answers():
    reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    assert load_agent_tasks() == strip_answers(reference)


def test_loader_rejects_task_with_answer(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"task_id": 1, "question": "q"},
                               {"task_id": 2, "question": "q", "answer": "x"}]), encoding="utf-8")
    with pytest.raises(AnswerLeakError):
        load_agent_tasks(bad)
    with pytest.raises(AnswerLeakError):
        load_agent_task(1, bad)


class TrapTask(Mapping):
    """A task whose 'answer' exists but raises if anything reads it."""

    def __init__(self, data):
        self._data = dict(data, answer="TRAP")

    def __getitem__(self, key):
        if key == "answer":
            raise AssertionError("run_agent read the answer")
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


def test_run_agent_never_reads_answer(tmp_path):
    workdir = tmp_path / "work"
    workdir.mkdir()
    task = TrapTask(load_agent_task(5))
    result = run_agent(
        task,
        FakeLLM(["```python\nprint('NL')\n```", "FINAL ANSWER: NL"]),
        StepLogger(tmp_path / "trap.jsonl"),
        workdir=workdir,
    )
    assert result.terminated_reason == "final" and result.final_answer == "NL"
    assert result.matches_reference is None


def test_scoring_happens_after_the_run_only(tmp_path):
    from agent.loop import RunResult
    assert fill_matches_reference(RunResult("NL", "final"), 5).matches_reference is True
    assert fill_matches_reference(RunResult("XX", "final"), 5).matches_reference is False
    assert fill_matches_reference(RunResult(None, "max_steps"), 5).matches_reference is None

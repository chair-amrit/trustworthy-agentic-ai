import json

from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from scripts.run_fake import TASK_5_CODE, TASKS_PATH


def _task_5():
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    return next(task for task in tasks if task["task_id"] == 5)


def test_fake_agent_solves_task_5_and_writes_step_records(tmp_path):
    path = tmp_path / "task5.jsonl"
    result = run_agent(
        _task_5(),
        FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"]),
        StepLogger(path),
        run_id="test-task-5",
    )

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert result.final_answer == "NL"
    assert result.matches_reference is True
    assert result.terminated_reason == "final"
    assert len(records) == 2
    assert records[0]["action_type"] == "code"
    assert records[0]["returncode"] == 0
    assert "NL" in records[0]["observation"]
    assert records[1]["action_type"] == "final"
    assert records[1]["terminated_reason"] == "final"


def test_failed_code_is_logged_and_not_treated_as_success(tmp_path):
    responses = [
        "```python\nraise RuntimeError('boom')\n```",
        "```python\nprint('NL')\n```",
        "FINAL ANSWER: NL",
    ]
    path = tmp_path / "failure-recovery.jsonl"

    result = run_agent(
        _task_5(), FakeLLM(responses), StepLogger(path), run_id="failure-recovery"
    )

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert result.final_answer == "NL" and result.matches_reference is True
    assert records[0]["returncode"] != 0
    assert records[0]["action_type"] == "code"
    assert "Execution failed" in records[0]["observation"]
    assert records[1]["returncode"] == 0


def test_fake_agent_stops_at_step_limit_without_claiming_answer(tmp_path):
    result = run_agent(
        _task_5(),
        FakeLLM([TASK_5_CODE]),
        StepLogger(tmp_path / "limited.jsonl"),
        max_steps=1,
    )

    assert result.final_answer is None
    assert result.terminated_reason == "max_steps"

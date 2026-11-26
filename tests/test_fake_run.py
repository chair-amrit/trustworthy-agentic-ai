import json
from pathlib import Path

import pytest

from agent import config
from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.tasks import load_agent_task
from agent.workspace import create_workspace, input_report
from scripts.run_fake import TASK_5_CODE, fill_matches_reference

GOLDEN = Path(__file__).parent / "golden" / "fake_task_5.jsonl"


def _task_5():
    return load_agent_task(5)


@pytest.fixture(scope="module")
def shared_ws(tmp_path_factory):
    """One real-data workspace shared by the tests below (copying 24 MB once)."""
    return create_workspace("fake-run-tests", work_root=tmp_path_factory.mktemp("work"))


def test_fake_run_reproduces_golden_log(tmp_path):
    ws = create_workspace("fake-task-5", work_root=tmp_path / "work")
    path = tmp_path / "task5.jsonl"
    run_agent(
        _task_5(),
        FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"]),
        StepLogger(path),
        workdir=ws.root,
        run_id="fake-task-5",
    )
    got = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    want = [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines()]
    # Slice e added one field to every step record; the golden file predates it.
    assert [r.pop("path_flags") for r in got] == [[], []]
    assert got == want
    assert input_report(ws)["flagged"] is False


def test_fake_agent_solves_task_5_and_writes_step_records(tmp_path, shared_ws):
    path = tmp_path / "task5.jsonl"
    result = run_agent(
        _task_5(),
        FakeLLM([TASK_5_CODE, "FINAL ANSWER: NL"]),
        StepLogger(path),
        workdir=shared_ws.root,
        run_id="test-task-5",
    )
    assert result.matches_reference is None          # the loop never scores (D9)
    result = fill_matches_reference(result, 5)       # scored after the run, by the script

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


def test_failed_code_is_logged_and_not_treated_as_success(tmp_path, shared_ws):
    responses = [
        "```python\nraise RuntimeError('boom')\n```",
        "```python\nprint('NL')\n```",
        "FINAL ANSWER: NL",
    ]
    path = tmp_path / "failure-recovery.jsonl"

    result = run_agent(
        _task_5(), FakeLLM(responses), StepLogger(path),
        workdir=shared_ws.root, run_id="failure-recovery",
    )
    result = fill_matches_reference(result, 5)

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert result.final_answer == "NL" and result.matches_reference is True
    assert records[0]["returncode"] != 0
    assert records[0]["action_type"] == "code"
    assert "Execution failed" in records[0]["observation"]
    assert records[1]["returncode"] == 0


def test_fake_agent_stops_at_step_limit_without_claiming_answer(tmp_path, shared_ws):
    result = run_agent(
        _task_5(),
        FakeLLM([TASK_5_CODE]),
        StepLogger(tmp_path / "limited.jsonl"),
        workdir=shared_ws.root,
        max_steps=1,
    )

    assert result.final_answer is None
    assert result.terminated_reason == "max_steps"


def test_default_work_root_is_outside_repo():
    root = config.WORK_ROOT.resolve()
    assert config.REPO_ROOT.resolve() not in (root, *root.parents)

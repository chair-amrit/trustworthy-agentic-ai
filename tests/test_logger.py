import json

import pytest

from agent.logger import StepLogger


def test_step_logger_appends_records_as_json_lines(tmp_path):
    path = tmp_path / "runs" / "run.jsonl"
    logger = StepLogger(path)
    logger.log(
        {
            "task_id": 5,
            "step": 1,
            "model": "fake-scripted",
            "action_type": "code",
            "observation": "Observation:\n2",
            "returncode": 0,
        }
    )
    logger.log(
        {
            "task_id": 5,
            "step": 2,
            "model": "fake-scripted",
            "action_type": "final",
            "final_answer": "NL",
            "terminated_reason": "final",
        }
    )

    lines = path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == 2
    assert records[0]["observation"] == "Observation:\n2"
    assert records[1]["final_answer"] == "NL"


def test_step_logger_rejects_unapproved_fields_before_writing(tmp_path):
    path = tmp_path / "run.jsonl"
    logger = StepLogger(path)

    with pytest.raises(ValueError, match="unsupported step field"):
        logger.log({"task_id": 5, "api_key": "should-not-be-logged"})

    assert not path.exists()


def test_step_logger_rejects_non_json_numbers(tmp_path):
    logger = StepLogger(tmp_path / "run.jsonl")

    with pytest.raises(ValueError):
        logger.log({"task_id": 5, "temperature": float("nan")})

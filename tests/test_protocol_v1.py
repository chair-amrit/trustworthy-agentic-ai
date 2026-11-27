"""Protocol v1 (D1, Track A): rule 1 (code + answer -> run code, discard answer).
v0 is unchanged."""
import json

import pytest

from agent import config
from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.parser import (
    DISCARDED_FINAL_NOTE,
    Action,
    parse_action,
)
from agent.tasks import load_agent_task

CODE = "```python\nprint('NL')\n```"
CODE_PLUS_ANSWER = CODE + "\n\nFINAL ANSWER: XX"
BAD_CODE = "```python\nraise ValueError('boom')\n```"


def _run(responses, tmp_path, protocol="v1", name="run", **kw):
    base = tmp_path / name                 # one folder per run: the logger appends
    log = base / "steps.jsonl"
    workdir = base / "work"
    workdir.mkdir(parents=True)
    result = run_agent(load_agent_task(5), FakeLLM(responses), StepLogger(log),
                       workdir=workdir, protocol=protocol, **kw)
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    return result, records


# --- parser ------------------------------------------------------------------

def test_parser_v1_code_plus_answer_is_code_with_discarded_answer():
    a = parse_action(CODE_PLUS_ANSWER, "v1")
    assert a == Action("code", "print('NL')", discarded_final="XX")


def test_parser_v0_code_plus_answer_still_invalid():
    a = parse_action(CODE_PLUS_ANSWER, "v0")
    assert a.type == "invalid" and "both a code block and a FINAL ANSWER" in a.reason
    assert parse_action(CODE_PLUS_ANSWER) == a      # default is v0


@pytest.mark.parametrize("text,reason", [
    (CODE + "\n" + CODE + "\nFINAL ANSWER: X", "both a code block"),   # two blocks
    (CODE + "\nFINAL ANSWER: A\nFINAL ANSWER: B", "both a code block"),  # two answers
    ("```python\n\n```\nFINAL ANSWER: X", "both a code block"),         # empty block
])
def test_parser_v1_other_mixed_cases_stay_invalid(text, reason):
    a = parse_action(text, "v1")
    assert a.type == "invalid" and reason in a.reason


def test_parser_rejects_unknown_protocol():
    with pytest.raises(ValueError):
        parse_action(CODE, "v9")


# --- rule 1 ------------------------------------------------------------------

def test_rule1_code_runs_answer_discarded_and_noted(tmp_path):
    result, recs = _run([CODE_PLUS_ANSWER, "FINAL ANSWER: NL"], tmp_path)
    assert result.final_answer == "NL" and result.terminated_reason == "final"
    s1 = recs[0]
    assert s1["action_type"] == "code" and s1["code"] == "print('NL')"
    assert s1["returncode"] == 0 and s1["stdout"] == "NL\n"
    assert s1["final_answer"] is None and s1["final_answer_discarded"] is True
    assert s1["observation"] == "Observation:\nNL\n" + DISCARDED_FINAL_NOTE
    assert s1["protocol"] == "v1"
    assert recs[1]["final_answer_discarded"] is False


def test_rule1_note_also_added_when_code_fails(tmp_path):
    _, recs = _run([BAD_CODE + "\nFINAL ANSWER: XX", CODE, "FINAL ANSWER: NL"], tmp_path)
    assert recs[0]["returncode"] != 0 and recs[0]["final_answer_discarded"] is True
    assert recs[0]["observation"].endswith(DISCARDED_FINAL_NOTE)


# --- v0 unchanged ------------------------------------------------------------

def test_v0_keeps_old_behaviour_and_record_fields(tmp_path):
    result, recs = _run(["FINAL ANSWER: XX"], tmp_path, protocol="v0")
    assert result.final_answer == "XX" and result.terminated_reason == "final"
    assert "protocol" not in recs[0] and "final_answer_discarded" not in recs[0]
    _, recs = _run([CODE_PLUS_ANSWER, "FINAL ANSWER: NL"], tmp_path, protocol="v0", name="run2")
    assert recs[0]["action_type"] == "invalid"
    assert config.PROTOCOL_VERSION == "v0"


def test_run_agent_rejects_unknown_protocol(tmp_path):
    with pytest.raises(ValueError):
        _run(["FINAL ANSWER: X"], tmp_path, protocol="v2")

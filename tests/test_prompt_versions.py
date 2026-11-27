"""Prompt versions: v0 stays byte-identical to baseline-v0; v1 task message differs only
by the dropped payments.csv sentence; the manifest hash covers system prompt + template."""
import pytest

from agent import loop
from agent.loop import _task_prompt, check_prompt_version, prompt_sha256, system_prompt_sha256
from agent.tasks import load_agent_tasks


def _baseline_v0_task_prompt(task):
    """Exact copy of baseline-v0's _task_prompt (before prompt versions existed)."""
    task_id = task.get("task_id", "unknown")
    question = task.get("question", "")
    guidelines = task.get("guidelines", "")
    return (
        f"Task ID: {task_id}\nQuestion: {question}\nGuidelines: {guidelines}\n"
        "Use Python code blocks to inspect the provided data and print intermediate "
        "results. The data is available at data/context/payments.csv relative to "
        "the execution directory. Finish with exactly one line: FINAL ANSWER: <value>."
    )


SENTENCE = ("The data is available at data/context/payments.csv relative to "
            "the execution directory. ")


@pytest.mark.parametrize("task", load_agent_tasks(), ids=lambda t: str(t["task_id"]))
def test_v0_task_message_is_byte_identical(task):
    assert _task_prompt(task, "system_v0").encode() == _baseline_v0_task_prompt(task).encode()
    assert _task_prompt(task).encode() == _baseline_v0_task_prompt(task).encode()  # default


@pytest.mark.parametrize("task", load_agent_tasks(), ids=lambda t: str(t["task_id"]))
def test_v1_task_message_only_drops_the_payments_sentence(task):
    v1 = _task_prompt(task, "system_v1")
    assert "payments.csv" not in v1
    assert v1 == _baseline_v0_task_prompt(task).replace(SENTENCE, "")


def test_values_with_braces_are_inserted_as_is():
    t = {"task_id": 1, "question": "a {guidelines} {0} b", "guidelines": "g {x}"}
    assert "Question: a {guidelines} {0} b\nGuidelines: g {x}\n" in _task_prompt(t, "system_v1")


def test_prompt_hash_covers_system_prompt_and_template(monkeypatch):
    before = prompt_sha256("system_v1")
    assert len(before) == 64 and before != system_prompt_sha256("system_v1")
    assert prompt_sha256("system_v0") != before
    monkeypatch.setitem(loop.TASK_TEMPLATES, "system_v1", loop.TASK_TEMPLATES["system_v1"] + " ")
    assert prompt_sha256("system_v1") != before          # template change -> new hash
    assert system_prompt_sha256("system_v1") == system_prompt_sha256("system_v1")


def test_unknown_version_is_refused():
    with pytest.raises(FileNotFoundError):
        check_prompt_version("system_v9")
    with pytest.raises(KeyError):
        loop.task_template("system_v9")

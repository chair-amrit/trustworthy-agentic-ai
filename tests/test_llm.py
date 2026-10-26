import pytest

from agent.llm import Completion, FakeLLM, ScriptExhaustedError


def test_fake_llm_returns_scripted_completions_in_order():
    llm = FakeLLM(["first", Completion("second", finish_reason="length")])

    first = llm.generate([{"role": "user", "content": "task"}])
    second = llm.generate([], temperature=0.7, seed=12)

    assert first == [Completion("first")]
    assert second == [Completion("second", finish_reason="length")]
    assert llm.model_name == "fake-scripted"


def test_fake_llm_returns_requested_number_of_completions():
    llm = FakeLLM(["a", "b"])

    assert [item.text for item in llm.generate([], n=2)] == ["a", "b"]


def test_fake_llm_exhaustion_is_explicit_and_does_not_partially_consume():
    llm = FakeLLM(["only response"])

    with pytest.raises(ScriptExhaustedError, match="only 1 remain"):
        llm.generate([], n=2)

    assert llm.generate([], n=1)[0].text == "only response"


def test_fake_llm_rejects_nonpositive_n():
    with pytest.raises(ValueError, match="at least 1"):
        FakeLLM([]).generate([], n=0)

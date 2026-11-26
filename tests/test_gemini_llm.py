"""Step 2: GeminiLLM adapter, fully offline (mocked client, fake clock; no API calls)."""
import json
from types import SimpleNamespace

import httpx2
import pytest
from google.genai import errors

from agent import config
from agent.llm import ApiFailedError, GeminiLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.tasks import load_agent_task

KEY = "TEST-KEY-abc123-do-not-log"


class FakeClock:
    def __init__(self):
        self.t = 1000.0
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class FakeClient:
    """Mimics client.models.generate_content; plays back responses or exceptions."""

    def __init__(self, behaviours):
        self.behaviours = list(behaviours)
        self.calls = []
        self.models = self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        b = self.behaviours.pop(0) if self.behaviours else _response()
        if isinstance(b, Exception):
            raise b
        return b


def _response(text="```python\nprint(1)\n```", thinking=None):
    usage = SimpleNamespace(
        prompt_token_count=182,
        candidates_token_count=72,
        total_token_count=254 if thinking is None else 254 + thinking,
        **({} if thinking is None else {"thoughts_token_count": thinking}),
    )
    part = SimpleNamespace(text=text, thought=None)
    cand = SimpleNamespace(content=SimpleNamespace(parts=[part]),
                           finish_reason=SimpleNamespace(name="STOP"))
    return SimpleNamespace(text=text, model_version="gemini-3.1-flash-lite",
                           response_id="resp-1", usage_metadata=usage, candidates=[cand])


def _err(code):
    status = {429: "RESOURCE_EXHAUSTED", 500: "INTERNAL", 503: "UNAVAILABLE",
              400: "INVALID_ARGUMENT", 401: "UNAUTHENTICATED"}[code]
    cls = errors.ServerError if code >= 500 else errors.ClientError
    return cls(code, {"error": {"code": code, "message": f"m {KEY}", "status": status}})


MESSAGES = [
    {"role": "system", "content": "SYS"},
    {"role": "user", "content": "task"},
    {"role": "assistant", "content": "```python\nprint(1)\n```"},
    {"role": "user", "content": "Observation:\n1"},
]


def _llm(behaviours, tmp_path=None, clock=None):
    clock = clock or FakeClock()
    client = FakeClient(behaviours)
    llm = GeminiLLM(client=client, api_key=KEY, sleep=clock.sleep, clock=clock,
                    call_log_path=(tmp_path / "calls.jsonl") if tmp_path else None)
    return llm, client, clock


def _gen(llm):
    return llm.generate(MESSAGES, temperature=config.GEMINI_TEMPERATURE,
                        max_tokens=config.GEMINI_MAX_OUTPUT_TOKENS)


def test_settings_are_passed_correctly():
    llm, client, _ = _llm([_response()])
    out = _gen(llm)
    call = client.calls[0]
    cfg = call["config"]
    assert call["model"] == "gemini-3.1-flash-lite" == config.GEMINI_MODEL_ID
    assert cfg.temperature == 1.0
    assert cfg.max_output_tokens == 1024
    assert "minimal" in str(cfg.thinking_config.thinking_level).lower()
    assert cfg.thinking_config.include_thoughts is False
    assert cfg.system_instruction == "SYS"
    assert [c.role for c in call["contents"]] == ["user", "model", "user"]
    assert out[0].text == "```python\nprint(1)\n```" and out[0].finish_reason == "STOP"


def test_real_client_has_sdk_retries_off_and_timeout():
    llm = GeminiLLM(api_key="dummy-offline-key")   # builds a client, makes no call
    api = llm._client._api_client
    assert api._retry.stop.max_attempt_number == 1
    assert api._http_options.timeout == 120_000     # SDK unit is milliseconds
    assert llm.settings()["request_timeout_s"] == 120


def test_mismatched_settings_are_refused():
    llm, _, _ = _llm([])
    with pytest.raises(ValueError, match="temperature"):
        llm.generate(MESSAGES, temperature=0.0, max_tokens=1024)
    with pytest.raises(ValueError, match="max_tokens"):
        llm.generate(MESSAGES, temperature=1.0, max_tokens=512)
    with pytest.raises(NotImplementedError):
        llm.generate(MESSAGES, temperature=1.0, max_tokens=1024, want_logprobs=True)


def test_call_record_has_all_fields(tmp_path):
    llm, _, _ = _llm([_response(thinking=7)], tmp_path)
    _gen(llm)
    rec = json.loads((tmp_path / "calls.jsonl").read_text(encoding="utf-8"))
    for k in ("ts_utc", "model_version", "response_id", "input_tokens", "output_tokens",
              "thinking_tokens", "total_tokens", "latency_s", "finish_reason", "n_attempts",
              "attempts", "settings"):
        assert k in rec, k
    assert rec["status"] == "ok" and rec["thinking_tokens"] == 7 and rec["n_attempts"] == 1
    assert rec["settings"]["temperature"] == 1.0 and rec["settings"]["thinking_level"] == "minimal"
    assert rec["ts_utc"].endswith("+00:00")


def test_503_then_success_two_attempts_both_logged(tmp_path):
    llm, client, clock = _llm([_err(503), _response()], tmp_path)
    _gen(llm)
    rec = llm.call_records[0]
    assert rec["status"] == "ok" and rec["n_attempts"] == 2 and len(client.calls) == 2
    a1, a2 = rec["attempts"]
    assert a1["status"] == 503 and a1["wait_before_retry_s"] == 5
    assert a2["status"] == "ok"
    assert clock.sleeps == [5]


def test_429_is_retried_too():
    llm, _, clock = _llm([_err(429), _response()])
    _gen(llm)
    assert llm.call_records[0]["n_attempts"] == 2 and clock.sleeps == [5]


def test_500_is_retried_too():
    llm, _, clock = _llm([_err(500), _response()])
    _gen(llm)
    assert llm.call_records[0]["n_attempts"] == 2 and clock.sleeps == [5]


def test_connection_error_then_success(tmp_path):
    llm, client, clock = _llm([httpx2.ConnectError("connection refused"), _response()], tmp_path)
    out = _gen(llm)
    rec = llm.call_records[0]
    assert out[0].text and rec["status"] == "ok" and rec["n_attempts"] == 2
    a1, a2 = rec["attempts"]
    assert a1["status"] is None and a1["error_kind"] == "network"
    assert a1["wait_before_retry_s"] == 5 and "ConnectError" in a1["error"]
    assert a2["status"] == "ok" and clock.sleeps == [5] and len(client.calls) == 2


def test_timeout_then_success(tmp_path):
    llm, _, clock = _llm([httpx2.ReadTimeout("read timed out"), _response()], tmp_path)
    _gen(llm)
    a1 = llm.call_records[0]["attempts"][0]
    assert a1["error_kind"] == "timeout" and a1["wait_before_retry_s"] == 5
    assert llm.call_records[0]["n_attempts"] == 2 and clock.sleeps == [5]


@pytest.mark.parametrize("exc", [
    ConnectionResetError("reset"), TimeoutError("t"),
    httpx2.WriteTimeout("w"), httpx2.ReadError("r"), httpx2.RemoteProtocolError("dropped"),
])
def test_other_transient_errors_are_retried(exc):
    llm, _, clock = _llm([exc, _response()])
    _gen(llm)
    assert llm.call_records[0]["n_attempts"] == 2 and clock.sleeps == [5]


def test_repeated_timeouts_exhaust_retries():
    llm, client, clock = _llm([httpx2.ConnectTimeout("t")] * 5)
    with pytest.raises(ApiFailedError, match="retries exhausted") as ei:
        _gen(llm)
    assert ei.value.attempts == 5 and ei.value.status is None
    assert clock.sleeps == [5, 15, 45, 90] and len(client.calls) == 5


@pytest.mark.parametrize("exc", [
    "http401", httpx2.ProxyError("proxy"), ValueError("bug"), KeyError("k"),
])
def test_other_errors_stay_non_retryable(exc):
    exc = _err(401) if exc == "http401" else exc
    llm, client, clock = _llm([exc, _response()])
    with pytest.raises(ApiFailedError, match="non-retryable"):
        _gen(llm)
    assert len(client.calls) == 1 and clock.sleeps == []


def test_five_503s_raise_api_failed(tmp_path):
    llm, client, clock = _llm([_err(503)] * 5, tmp_path)
    with pytest.raises(ApiFailedError) as ei:
        _gen(llm)
    assert ei.value.attempts == 5 and ei.value.status == 503
    assert len(client.calls) == 5
    assert clock.sleeps == [5, 15, 45, 90]
    rec = llm.call_records[0]
    assert rec["status"] == "api_failed" and [a["status"] for a in rec["attempts"]] == [503] * 5


def test_non_retryable_error_raises_immediately():
    llm, client, clock = _llm([_err(400), _response()])
    with pytest.raises(ApiFailedError) as ei:
        _gen(llm)
    assert ei.value.attempts == 1 and ei.value.status == 400
    assert len(client.calls) == 1 and clock.sleeps == []


def test_key_never_in_log_or_error(tmp_path):
    llm, _, _ = _llm([_err(503), _err(400)], tmp_path)
    with pytest.raises(ApiFailedError) as ei:
        _gen(llm)
    assert KEY not in str(ei.value) and "***" in str(ei.value)
    log_text = (tmp_path / "calls.jsonl").read_text(encoding="utf-8")
    assert KEY not in log_text
    assert KEY not in json.dumps(llm.call_records) and KEY not in repr(llm)


def test_missing_thinking_tokens_logged_as_null(tmp_path):
    llm, _, _ = _llm([_response(thinking=None)], tmp_path)
    out = _gen(llm)
    rec = json.loads((tmp_path / "calls.jsonl").read_text(encoding="utf-8"))
    assert rec["thinking_tokens"] is None and '"thinking_tokens": null' in (
        tmp_path / "calls.jsonl").read_text(encoding="utf-8")
    assert out[0].usage["thinking_tokens"] is None


def test_pacing_waits_after_12_requests_in_a_minute():
    llm, _, clock = _llm([_response() for _ in range(13)])
    for _ in range(12):
        _gen(llm)
    assert clock.sleeps == []
    _gen(llm)                                  # 13th request within the same minute
    assert clock.sleeps == [60.0]
    assert llm.call_records[-1]["attempts"][0]["pace_wait_s"] == 60.0


def test_pacing_does_not_wait_when_spread_out():
    llm, _, clock = _llm([_response() for _ in range(13)])
    for _ in range(13):
        _gen(llm)
        clock.t += 5.0                         # 13 calls over 65 s
    assert clock.sleeps == []


def test_run_stops_with_api_failed(tmp_path):
    llm, _, _ = _llm([_err(503)] * 5)
    workdir = tmp_path / "work"
    workdir.mkdir()
    result = run_agent(load_agent_task(5), llm, StepLogger(tmp_path / "steps.jsonl"),
                       workdir=workdir, temperature=config.GEMINI_TEMPERATURE)
    assert result.terminated_reason == "api_failed" and result.final_answer is None

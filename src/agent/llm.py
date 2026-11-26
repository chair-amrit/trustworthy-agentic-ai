"""Small model interface and deterministic scripted implementation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Completion:
    """One model response and optional generation metadata."""

    text: str
    token_logprobs: list[float] | None = None
    finish_reason: str = "stop"
    usage: dict[str, int | None] | None = None   # missing counts stay None, never 0


class Model(Protocol):
    """Interface used by the agent loop for model generation."""

    model_name: str

    def generate(
        self,
        messages: Sequence[dict[str, str]],
        n: int = 1,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        seed: int | None = None,
        want_logprobs: bool = False,
    ) -> list[Completion]: ...


class ScriptExhaustedError(RuntimeError):
    """Raised when a fake model has fewer scripted responses than requested."""


class FakeLLM:
    """Return prewritten responses in order without making network calls."""

    model_name = "fake-scripted"

    def __init__(self, responses: Sequence[str | Completion]):
        self._responses = tuple(
            response if isinstance(response, Completion) else Completion(response)
            for response in responses
        )
        self._index = 0

    def generate(
        self,
        messages: Sequence[dict[str, str]],
        n: int = 1,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        seed: int | None = None,
        want_logprobs: bool = False,
    ) -> list[Completion]:
        """Consume and return exactly ``n`` scripted completions.

        Generation options and messages are accepted for interface compatibility;
        the fake is deterministic and intentionally does not interpret them.
        """
        if n < 1:
            raise ValueError("n must be at least 1")
        end = self._index + n
        if end > len(self._responses):
            available = len(self._responses) - self._index
            raise ScriptExhaustedError(
                f"requested {n} completion(s), but only {available} remain"
            )
        result = list(self._responses[self._index:end])
        self._index = end
        return result


# --------------------------------------------------------------------------
# Real backend: Gemini API (D3, Track A).
# --------------------------------------------------------------------------

class ApiFailedError(RuntimeError):
    """The API call failed for good; the run stops with terminated_reason 'api_failed'.

    The message is already redacted (the API key never appears in it).
    """

    def __init__(self, message: str, status: int | None, attempts: int):
        super().__init__(message)
        self.status = status
        self.attempts = attempts


def _transient_network_types() -> tuple[type, ...]:
    """Exception types that mean 'network/connection problem or timeout'."""
    types_: list[type] = [ConnectionError, TimeoutError]
    for mod_name in ("httpx2", "httpx"):
        try:
            mod = __import__(mod_name)
        except ImportError:
            continue
        for name in ("TimeoutException", "NetworkError", "RemoteProtocolError"):
            cls = getattr(mod, name, None)
            if isinstance(cls, type):
                types_.append(cls)
    return tuple(types_)


def is_transient_network_error(exc: BaseException) -> str | None:
    """Return "timeout" or "network" for a retryable transport error, else None."""
    if not isinstance(exc, _transient_network_types()):
        return None
    if isinstance(exc, TimeoutError) or "Timeout" in type(exc).__name__:
        return "timeout"
    return "network"


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class GeminiLLM:
    """Gemini API model with the same interface as FakeLLM.

    - Settings come from config (D3). A call that asks for a different
      temperature or max_tokens is refused, so logs never show a setting that
      was not actually used. Log probabilities are not requested (unchecked, D3).
    - The API key is read from .env in this (parent) process, passed directly to
      the client, and never put into os.environ, logs or error messages.
    - The SDK's own retries are off. This class retries only on the statuses in
      config.API_RETRY_STATUSES and on network/connection errors and timeouts,
      waiting config.API_RETRY_WAITS_S, and records every attempt. After the last
      failure it raises ApiFailedError. Each attempt has a request timeout of
      config.API_REQUEST_TIMEOUT_S.
    - Pacing: at most config.API_MAX_REQUESTS_PER_MINUTE requests (attempts) in
      any 60-second window.
    - One JSON record per call is appended to ``call_log_path`` (if given) and
      kept in ``self.call_records``. Hidden thoughts are never requested or logged;
      only the thinking token count is.
    """

    def __init__(
        self,
        *,
        client=None,
        api_key: str | None = None,
        env_path=None,
        call_log_path=None,
        model_id: str | None = None,
        temperature: float | None = None,
        thinking_level: str | None = None,
        max_output_tokens: int | None = None,
        retry_statuses: Sequence[int] | None = None,
        retry_waits_s: Sequence[float] | None = None,
        max_requests_per_minute: int | None = None,
        sleep=None,
        clock=None,
    ):
        import time
        from collections import deque
        from pathlib import Path

        from . import config
        from .envfile import read_env_key

        self.model_name = model_id or config.GEMINI_MODEL_ID
        self.temperature = config.GEMINI_TEMPERATURE if temperature is None else temperature
        self.thinking_level = thinking_level or config.GEMINI_THINKING_LEVEL
        self.max_output_tokens = max_output_tokens or config.GEMINI_MAX_OUTPUT_TOKENS
        self.retry_statuses = tuple(retry_statuses or config.API_RETRY_STATUSES)
        self.retry_waits_s = tuple(config.API_RETRY_WAITS_S if retry_waits_s is None else retry_waits_s)
        self.max_rpm = max_requests_per_minute or config.API_MAX_REQUESTS_PER_MINUTE
        self.request_timeout_s = config.API_REQUEST_TIMEOUT_S
        self.sdk = config.GEMINI_SDK
        self._sleep = sleep or time.sleep
        self._clock = clock or time.monotonic
        self._request_times: deque[float] = deque()
        self.call_log_path = Path(call_log_path) if call_log_path else None
        self.call_records: list[dict] = []
        self._calls = 0

        key = api_key or read_env_key(Path(env_path) if env_path else config.ENV_PATH)
        self._secret = key  # kept only to redact error text; never logged
        if client is None:
            if not key:
                raise ValueError("MODEL_API_KEY is missing or empty in .env")
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=key,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(attempts=1),
                    timeout=int(self.request_timeout_s * 1000),   # SDK unit: milliseconds
                ),
            )
        self._client = client

    def __repr__(self) -> str:  # never show the key
        return f"GeminiLLM(model={self.model_name!r})"

    # -- settings ---------------------------------------------------------
    def settings(self, seed: int | None = None) -> dict[str, object]:
        return {
            "model_requested": self.model_name,
            "temperature": self.temperature,
            "thinking_level": self.thinking_level,
            "include_thoughts": False,
            "max_output_tokens": self.max_output_tokens,
            "seed": seed,
            "sdk_retries": "off",
            "retry_statuses": list(self.retry_statuses),
            "retry_on_network_errors_and_timeouts": True,
            "retry_waits_s": list(self.retry_waits_s),
            "request_timeout_s": self.request_timeout_s,
            "max_requests_per_minute": self.max_rpm,
            "sdk": self.sdk,
        }

    def _redact(self, text: str) -> str:
        return text.replace(self._secret, "***") if self._secret else text

    # -- pacing -----------------------------------------------------------
    def _pace(self) -> float:
        now = self._clock()
        while self._request_times and self._request_times[0] <= now - 60.0:
            self._request_times.popleft()
        waited = 0.0
        if len(self._request_times) >= self.max_rpm:
            waited = self._request_times[0] + 60.0 - now
            if waited > 0:
                self._sleep(waited)
            now = self._clock()
            while self._request_times and self._request_times[0] <= now - 60.0:
                self._request_times.popleft()
        self._request_times.append(self._clock())
        return max(waited, 0.0)

    # -- request building -------------------------------------------------
    def _build_request(self, messages, seed):
        from google.genai import types

        system = None
        contents = []
        for m in messages:
            role, text = m["role"], m["content"]
            if role == "system":
                system = text if system is None else system + "\n" + text
                continue
            gem_role = "model" if role == "assistant" else "user"
            contents.append(types.Content(role=gem_role, parts=[types.Part(text=text)]))
        cfg = types.GenerateContentConfig(
            system_instruction=system,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            seed=seed,
            thinking_config=types.ThinkingConfig(
                thinking_level=self.thinking_level, include_thoughts=False
            ),
        )
        return contents, cfg

    @staticmethod
    def _reply_text(response) -> str:
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []
            if parts:
                return "".join(
                    p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False)
                )
        return getattr(response, "text", None) or ""

    @staticmethod
    def _finish_reason(response) -> str | None:
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            return None
        fr = getattr(candidates[0], "finish_reason", None)
        if fr is None:
            return None
        return getattr(fr, "name", None) or str(fr)

    def _write(self, record: dict) -> None:
        import json

        self.call_records.append(record)
        if self.call_log_path is not None:
            self.call_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.call_log_path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(self._redact(json.dumps(record, ensure_ascii=False)) + "\n")

    # -- main entry -------------------------------------------------------
    def generate(
        self,
        messages: Sequence[dict[str, str]],
        n: int = 1,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        seed: int | None = None,
        want_logprobs: bool = False,
    ) -> list[Completion]:
        if n != 1:
            raise ValueError("GeminiLLM supports n=1 only")
        if want_logprobs:
            raise NotImplementedError("log probabilities are not requested in Track A (D3)")
        if temperature != self.temperature:
            raise ValueError(
                f"temperature {temperature} differs from the configured {self.temperature} (D3); "
                "pass temperature=config.GEMINI_TEMPERATURE to run_agent"
            )
        if max_tokens != self.max_output_tokens:
            raise ValueError(
                f"max_tokens {max_tokens} differs from the configured {self.max_output_tokens} (D3)"
            )

        self._calls += 1
        contents, cfg = self._build_request(messages, seed)
        record: dict[str, object] = {
            "call_index": self._calls,
            "ts_utc": _utc_now(),
            "settings": self.settings(seed),
            "attempts": [],
        }
        max_attempts = len(self.retry_waits_s) + 1

        for attempt in range(1, max_attempts + 1):
            pace_wait = self._pace()
            att: dict[str, object] = {
                "attempt": attempt,
                "ts_utc": _utc_now(),
                "pace_wait_s": round(pace_wait, 3),
            }
            t0 = self._clock()
            try:
                response = self._client.models.generate_content(
                    model=self.model_name, contents=contents, config=cfg
                )
            except Exception as exc:  # any API/network error
                status = getattr(exc, "code", None)
                status = status if isinstance(status, int) else None
                kind = is_transient_network_error(exc) if status is None else None
                att.update(
                    status=status,
                    error_kind=kind or ("http" if status is not None else "other"),
                    error=self._redact(f"{type(exc).__name__}: {exc}")[:500],
                    latency_s=round(self._clock() - t0, 3),
                )
                transient = status in self.retry_statuses or kind is not None
                retryable = transient and attempt < max_attempts
                if retryable:
                    wait = self.retry_waits_s[attempt - 1]
                    att["wait_before_retry_s"] = wait
                    record["attempts"].append(att)
                    self._sleep(wait)
                    continue
                record["attempts"].append(att)
                record.update(status="api_failed", n_attempts=attempt, error=att["error"])
                self._write(record)
                why = "retries exhausted" if transient else "non-retryable error"
                raise ApiFailedError(
                    f"api_failed after {attempt} attempt(s) ({why}): {att['error']}",
                    status,
                    attempt,
                ) from None

            latency = self._clock() - t0
            usage = getattr(response, "usage_metadata", None)
            tokens = {
                "input_tokens": getattr(usage, "prompt_token_count", None),
                "output_tokens": getattr(usage, "candidates_token_count", None),
                "thinking_tokens": getattr(usage, "thoughts_token_count", None),
                "total_tokens": getattr(usage, "total_token_count", None),
            }
            finish = self._finish_reason(response)
            att.update(status="ok", latency_s=round(latency, 3))
            record["attempts"].append(att)
            record.update(
                status="ok",
                n_attempts=attempt,
                model_version=getattr(response, "model_version", None),
                response_id=getattr(response, "response_id", None),
                finish_reason=finish,
                latency_s=round(latency, 3),
                **tokens,
            )
            self._write(record)
            return [
                Completion(
                    text=self._reply_text(response),
                    finish_reason=finish or "unknown",
                    usage=tokens,
                )
            ]

        raise AssertionError("unreachable")

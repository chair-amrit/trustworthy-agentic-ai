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
    usage: dict[str, int] | None = None


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

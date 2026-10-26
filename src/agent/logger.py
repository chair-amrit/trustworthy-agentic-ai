"""Append-only JSON Lines logging for agent step records."""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path


STEP_FIELDS = frozenset(
    {
        "run_id",
        "task_id",
        "step",
        "prefix_id",
        "model",
        "temperature",
        "seed",
        "prompt_version",
        "raw_output",
        "action_type",
        "code",
        "final_answer",
        "observation",
        "stdout",
        "stderr",
        "returncode",
        "timed_out",
        "truncated",
        "stdout_len",
        "logprobs",
        "terminated_reason",
    }
)


class StepLogger:
    """Append one JSON-serializable, allowlisted record per call."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def log(self, record: Mapping[str, object]) -> None:
        """Validate and append a step record without replacing existing records."""
        if not isinstance(record, Mapping):
            raise TypeError("record must be a mapping")
        unknown = set(record) - STEP_FIELDS
        if unknown:
            raise ValueError(f"unsupported step field(s): {', '.join(sorted(unknown))}")

        line = json.dumps(dict(record), ensure_ascii=False, allow_nan=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line + "\n")
            stream.flush()

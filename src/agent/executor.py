"""Executor (spec v0.1, section 3).

Each step runs in a FRESH subprocess: all earlier successful code blocks are
re-executed in order, a marker line is printed, then the current block runs.
The observation is the stdout after the marker (plus stderr). Live execution
and replay use this same function.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import config

MARKER = "<<<AGENT_STEP_OUTPUT_START>>>"

# Runs inside the child process (passed with -c). Code blocks share one
# namespace; tracebacks are trimmed so the model only sees its own frames.
_RUNNER = r'''
import json, sys, traceback
payload = json.loads(sys.stdin.read())
g = {"__name__": "__main__"}

def run(src, name):
    exec(compile(src, name, "exec"), g)

for i, src in enumerate(payload["prior"], 1):
    run(src, "<prior step %d>" % i)
print(payload["marker"], flush=True)
try:
    run(payload["code"], "<current step>")
except BaseException as e:
    tb = e.__traceback__
    while tb is not None and tb.tb_frame.f_code.co_filename == "<string>":
        tb = tb.tb_next
    traceback.print_exception(type(e), e, tb)
    sys.exit(1)
'''


class PriorStepError(RuntimeError):
    """Earlier successful blocks did not reproduce (state cannot be rebuilt)."""


@dataclass(frozen=True)
class ExecResult:
    stdout: str          # stdout after the marker, truncated to max_chars
    stderr: str          # tail of stderr, truncated to max_chars
    returncode: int
    timed_out: bool
    truncated: bool
    stdout_len: int      # untruncated length of stdout after the marker

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def _env() -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env.pop("PYTHONPATH", None)
    return env


def run_step(
    prior_codes: list[str],
    code: str,
    workdir: Path | str = config.DATA_ROOT,
    timeout_s: int = config.TIMEOUT_S,
    max_chars: int = config.MAX_OBS_CHARS,
) -> ExecResult:
    payload = json.dumps({"prior": list(prior_codes), "code": code, "marker": MARKER})
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(workdir),
            env=_env(),
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        # Partial output is not reproducible, so it is discarded.
        return ExecResult(
            stdout="",
            stderr=f"TimeoutError: step exceeded {timeout_s} seconds",
            returncode=-1,
            timed_out=True,
            truncated=False,
            stdout_len=0,
        )

    stdout = proc.stdout.replace("\r\n", "\n")
    stderr = proc.stderr.replace("\r\n", "\n")

    before, sep, after = stdout.partition(MARKER)
    if not sep:
        raise PriorStepError(
            f"prior steps did not reproduce (returncode {proc.returncode}): "
            f"{stderr[-500:]}"
        )
    after = after.removeprefix("\n")

    stdout_len = len(after)
    out = after[:max_chars]
    err = stderr[-max_chars:]
    return ExecResult(
        stdout=out,
        stderr=err,
        returncode=proc.returncode,
        timed_out=False,
        truncated=stdout_len > max_chars or len(stderr) > max_chars,
        stdout_len=stdout_len,
    )


def format_observation(r: ExecResult) -> str:
    """Fixed observation template sent back to the model."""
    out = r.stdout.rstrip("\n")
    err = r.stderr.rstrip("\n")
    parts = ["Observation:"]
    if out:
        parts.append(out)
    if err:
        parts.append(err)
    if not out and not err:
        parts.append("(no output)")
    if r.truncated:
        parts.append("[output truncated]")
    return "\n".join(parts)
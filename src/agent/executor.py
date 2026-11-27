"""Executor (spec v0.1, section 3).

Each step runs in a FRESH subprocess: all earlier successful code blocks are
re-executed in order, a marker line is printed, then the current block runs.
The observation is the stdout after the marker (plus stderr). Live execution
and replay use this same function.
"""
from __future__ import annotations

import json
import os
import re
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


# Strict allowlist (D5): the child starts from an EMPTY environment and gets
# only these variables from the parent. Everything else (API keys, tokens,
# HOME/USERPROFILE/APPDATA, PYTHONPATH, ...) is dropped.
ENV_PASSTHROUGH = (
    "SYSTEMROOT",              # needed by Python's random/crypto/socket on Windows
    "WINDIR",
    "PATH",                    # DLL lookup for numpy/pandas
    "PATHEXT",
    "COMSPEC",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
)
ENV_FIXED = {
    "PYTHONUTF8": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
}
ENV_TMP_VARS = ("TEMP", "TMP", "MPLCONFIGDIR")   # all point at <workdir>/tmp
ENV_ALLOWED = frozenset(ENV_PASSTHROUGH) | frozenset(ENV_FIXED) | frozenset(ENV_TMP_VARS)

# -P: do not put the working folder on sys.path (a planted json.py/pandas.py
#     cannot replace the real module); -s: ignore the user site-packages.
CHILD_FLAGS = ("-P", "-s")


def _env(tmp_dir: Path) -> dict:
    env = {}
    for name in ENV_PASSTHROUGH:
        value = os.environ.get(name)
        if value:
            env[name] = value
    env.update(ENV_FIXED)
    for name in ENV_TMP_VARS:
        env[name] = str(tmp_dir)
    return env


# --- Path scrubbing of error output (D5) -------------------------------------
# Tracebacks from library code contain absolute paths such as
# D:\...\venv\Lib\site-packages\pandas\core\indexes\base.py, which would tell
# the model where the repository (and its answer file) lives. Before error
# output is shown, every absolute path is rewritten:
#   inside the working folder        -> relative path (data/context/x.csv)
#   site-packages / standard library -> <python-lib>/pandas/core/...
#   the Python installation itself   -> <python>/...
#   anything else (repo, home, ...)  -> <outside-path>
_SEP = r"(?:\\\\|\\|/)"                       # "\\" (repr-escaped), "\" or "/"
_TAIL = rf"((?:{_SEP}[^\\/\s\"'<>|]+)*)"      # the rest of the path, segment by segment
_OUTSIDE = "<outside-path>"
# Outside paths may contain spaces ("C:\Users\First Last\..."), so for them the
# whole rest of the path up to a quote or the end of the line is replaced.
# Over-hiding is the safe direction here.
_GREEDY_TAIL = r"""((?:\\\\|\\|/)[^"'\r\n<>|]*)?"""
# Fallback for any other absolute path: a drive (C:\ C:/ C:\\) or a UNC prefix
# (\\server or, repr-escaped, \\\\server), only at the START of a token, so a
# relative repr path like 'data\\x' is left alone.
_ANY_ABS = re.compile(
    r"""(?<![^\s"'(\[=,])(?:[A-Za-z]:(?:\\\\|\\|/)|\\\\\\\\|\\\\)[^"'\r\n<>|]*"""
)


def _root_pattern(root: str, greedy: bool = False) -> re.Pattern:
    parts = [p for p in re.split(r"[\\/]+", root) if p]
    body = _SEP.join(re.escape(p) for p in parts)
    if greedy:
        return re.compile(body + _GREEDY_TAIL + r"""(?![^\\/\s"'<>|])""", re.IGNORECASE)
    return re.compile(body + _TAIL + r"(?![^\\/\s\"'<>|])", re.IGNORECASE)


def _path_roots(workdir: Path) -> list[tuple[re.Pattern, str]]:
    """(pattern, label) pairs, most specific first. label None = make relative."""
    import sysconfig

    def forms(p) -> list[str]:
        out = []
        for cand in (str(p), str(Path(p).resolve())):
            if cand and cand not in out:
                out.append(cand)
        return out

    paths = sysconfig.get_paths()
    roots: list[tuple[str, str | None]] = []
    roots += [(f, None) for f in forms(workdir)]
    for key in ("purelib", "platlib", "stdlib", "platstdlib"):
        if paths.get(key):
            roots += [(f, "<python-lib>") for f in forms(paths[key])]
    for prefix in {sys.prefix, sys.base_prefix, sys.exec_prefix}:
        roots += [(f, "<python>") for f in forms(prefix)]
    # Known outside locations: the whole path (tail included) becomes <outside-path>.
    for outside in (config.REPO_ROOT, Path.home()):
        roots += [(f, _OUTSIDE) for f in forms(outside)]
    # Longest root first so the most specific one wins.
    roots.sort(key=lambda r: len(r[0]), reverse=True)
    return [(_root_pattern(r, greedy=(label == _OUTSIDE)), label) for r, label in roots]


def scrub_paths(text: str, workdir: Path | str) -> str:
    """Rewrite absolute paths in ``text`` so no host location is revealed."""
    if not text:
        return text
    for pattern, label in _path_roots(Path(workdir)):
        def repl(m: re.Match, label=label) -> str:
            tail = re.sub(_SEP, "/", m.group(1)).lstrip("/")
            if label is None:
                return tail or "."
            if label == _OUTSIDE:
                return _OUTSIDE
            return f"{label}/{tail}" if tail else label
        text = pattern.sub(repl, text)
    return _ANY_ABS.sub(_OUTSIDE, text)


def run_step(
    prior_codes: list[str],
    code: str,
    workdir: Path | str,
    timeout_s: int = config.TIMEOUT_S,
    max_chars: int = config.MAX_OBS_CHARS,
) -> ExecResult:
    payload = json.dumps({"prior": list(prior_codes), "code": code, "marker": MARKER})
    tmp_dir = Path(workdir) / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    try:
        proc = subprocess.run(
            [sys.executable, *CHILD_FLAGS, "-c", _RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(workdir),
            env=_env(tmp_dir),
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
    # Error output is scrubbed of absolute paths before the model can see it (D5).
    stderr = scrub_paths(proc.stderr.replace("\r\n", "\n"), workdir)

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
    if r.timed_out:
        parts.append("Execution timed out.")
    elif r.returncode != 0:
        parts.append(f"Execution failed (return code {r.returncode}).")
    if out:
        parts.append(out)
    if err:
        parts.append(err)
    if not out and not err:
        parts.append("(no output)")
    if r.truncated:
        parts.append("[output truncated]")
    return "\n".join(parts)

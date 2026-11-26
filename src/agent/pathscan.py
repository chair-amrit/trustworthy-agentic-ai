"""D5 code scan (Track A slice e, E1 only): flag code that MENTIONS a path or a
path-building name that may lead outside the run's working folder.

This is a static scan of each logged code block using Python's ast module.
It does not observe what the code actually touched at runtime (no audit hook),
so paths built at runtime (e.g. "C:" + "\\\\x", getattr(sys, "executable"))
are missed. A flag means "mentions", to be reviewed; it is not proof of access.

Code that does not parse is not flagged: the executor compiles a block before
running it, so a block with a syntax error runs no statement at all.

What is flagged (reason):
  absolute_path   string starting with a drive (C:\\ or C:/), a UNC prefix
                  (\\\\server or //server), or "/" followed by a name ("/x")
  parent_dir      string with ".." as a path part ("..", "../x", "a\\..\\b");
                  "Loading..." is NOT flagged
  home_dir        string starting with "~" ("~", "~/x", "~user")
  path_builder    sys.executable / sys.prefix / sys.base_prefix / sys.exec_prefix,
                  __file__, Path.home, expanduser, os.environ, os.getenv
                  (also when imported: from os import environ, getenv, ...)
Relative paths inside the folder, like data/context/payments.csv, are not flagged.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Iterable, Mapping

_ABS_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|//|/[^/\s])")
_PARENT_RE = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)")
_HOME_RE = re.compile(r"^~")

_SYS_ATTRS = {"executable", "prefix", "base_prefix", "exec_prefix"}
_OS_ATTRS = {"environ", "environb", "getenv", "getenvb"}
_IMPORTED_NAMES = {
    "sys": _SYS_ATTRS,
    "os": _OS_ATTRS,
    "os.path": {"expanduser"},
}


def _dotted(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _string_reasons(value: str) -> list[str]:
    reasons = []
    if _ABS_RE.search(value):
        reasons.append("absolute_path")
    if _PARENT_RE.search(value):
        reasons.append("parent_dir")
    if _HOME_RE.search(value):
        reasons.append("home_dir")
    return reasons


def _builder(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name) and node.id == "__file__":
        return "__file__"
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        if node.attr in _SYS_ATTRS and base == "sys":
            return f"sys.{node.attr}"
        if node.attr in _OS_ATTRS and base == "os":
            return f"os.{node.attr}"
        if node.attr == "expanduser":
            return "expanduser"
        if node.attr == "home" and base is not None and base.split(".")[-1] == "Path":
            return "Path.home"
    if isinstance(node, ast.ImportFrom) and node.module in _IMPORTED_NAMES:
        for alias in node.names:
            if alias.name in _IMPORTED_NAMES[node.module]:
                return f"{node.module}.{alias.name}"
    return None


def scan_code(code: str) -> list[dict[str, object]]:
    """Return one flag per (line, reason, match); [] if nothing is flagged."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    lines = code.splitlines()
    flags: list[dict[str, object]] = []
    seen: set[tuple] = set()

    def add(node: ast.AST, reason: str, match: str) -> None:
        lineno = getattr(node, "lineno", 0)
        key = (lineno, reason, match)
        if key in seen:
            return
        seen.add(key)
        code_line = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
        flags.append({"reason": reason, "match": match, "line": lineno, "code_line": code_line})

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for reason in _string_reasons(node.value):
                add(node, reason, node.value)
        else:
            name = _builder(node)
            if name:
                add(node, "path_builder", name)
    flags.sort(key=lambda f: (f["line"], f["reason"], f["match"]))
    return flags


def merge_run_flags(
    path_flags: Iterable[Mapping[str, object]], input_report: Mapping[str, object]
) -> dict[str, object]:
    """Run-level flag: code-scan flags merged with the checksum flag from workspace."""
    path_flags = list(path_flags)
    reasons = list(input_report.get("flag_reasons", []))
    if path_flags:
        reasons.append("path_scan")
    return {
        "flagged": bool(reasons),
        "flag_reasons": reasons,
        "path_flag_count": len(path_flags),
    }


def review_entries(
    run_id: str,
    path_flags: Iterable[Mapping[str, object]],
    input_report: Mapping[str, object],
) -> list[dict[str, object]]:
    """One review-list line per path flag, plus one per changed input file."""
    entries = [
        {
            "run_id": run_id,
            "step": f.get("step"),
            "reason": f["reason"],
            "match": f["match"],
            "code_line": f["code_line"],
        }
        for f in path_flags
    ]
    for change in input_report.get("input_changes", []):
        entries.append(
            {
                "run_id": run_id,
                "step": None,
                "reason": "input_changed",
                "match": f"{change['change']}: {change['path']}",
                "code_line": None,
            }
        )
    return entries


def append_review_list(path: Path | str, entries: Iterable[Mapping[str, object]]) -> int:
    entries = list(entries)
    if not entries:
        return 0
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        for e in entries:
            f.write(json.dumps(dict(e), ensure_ascii=False) + "\n")
    return len(entries)

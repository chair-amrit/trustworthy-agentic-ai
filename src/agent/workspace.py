"""Per-run working folder outside the repository (D5, Track A slice b+c).

Layout:   <work_root>/<run_id>/
            data/context/<inputs>   copies of the DABStep context files, read-only
            tmp/                    TEMP/TMP/MPLCONFIGDIR of the child process

The read-only attribute only deters writes: code running as the same user can
remove it. Changes are DETECTED by comparing SHA-256 checksums before and after
the run. This is not a sandbox.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path

from . import config

RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
INPUT_SUBDIR = Path("data") / "context"


@dataclass(frozen=True)
class Workspace:
    run_id: str
    root: Path                  # working folder (cwd) of executed code
    data_dir: Path              # root / data / context
    tmp_dir: Path               # root / tmp
    checksums: dict[str, str]   # path relative to root (posix) -> sha256, taken at creation


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def create_workspace(
    run_id: str,
    work_root: Path | str | None = None,
    source: Path | str | None = None,
    repo_root: Path | str | None = None,
) -> Workspace:
    """Create <work_root>/<run_id>/ with read-only copies of the input files."""
    if not RUN_ID_RE.match(run_id):
        raise ValueError(f"unsafe run_id {run_id!r}: use letters, digits, '.', '_' or '-'")
    work_root = Path(work_root if work_root is not None else config.WORK_ROOT)
    source = Path(source if source is not None else config.CONTEXT_SOURCE)
    repo_root = Path(repo_root if repo_root is not None else config.REPO_ROOT)

    if _is_inside(work_root, repo_root):
        raise ValueError(f"work_root {work_root} is inside the repository {repo_root} (D5)")
    if not source.is_dir():
        raise FileNotFoundError(f"input source folder not found: {source}")

    root = work_root / run_id
    if root.exists():
        raise FileExistsError(f"run folder already exists, refusing to reuse it: {root}")

    data_dir = root / INPUT_SUBDIR
    tmp_dir = root / "tmp"
    data_dir.mkdir(parents=True)
    tmp_dir.mkdir()

    checksums: dict[str, str] = {}
    for src in sorted(p for p in source.iterdir() if p.is_file()):
        expected = sha256_file(src)
        dst = data_dir / src.name
        shutil.copyfile(src, dst)
        actual = sha256_file(dst)
        if actual != expected:
            raise OSError(f"copy of {src.name} does not match its source checksum")
        os.chmod(dst, stat.S_IREAD)
        checksums[(INPUT_SUBDIR / src.name).as_posix()] = actual

    return Workspace(run_id, root, data_dir, tmp_dir, checksums)


def verify_inputs(ws: Workspace) -> list[dict[str, str]]:
    """Compare the input folder with the checksums taken at creation.

    Returns one entry per difference: change is "modified", "missing" or "added".
    An empty list means the inputs are unchanged.
    """
    changes: list[dict[str, str]] = []
    for rel, digest in sorted(ws.checksums.items()):
        path = ws.root / rel
        if not path.is_file():
            changes.append({"path": rel, "change": "missing"})
        elif sha256_file(path) != digest:
            changes.append({"path": rel, "change": "modified"})
    data_root = ws.root / "data"
    for path in sorted(p for p in data_root.rglob("*") if p.is_file()):
        rel = path.relative_to(ws.root).as_posix()
        if rel not in ws.checksums:
            changes.append({"path": rel, "change": "added"})
    return changes


def input_report(ws: Workspace) -> dict[str, object]:
    """Run-level summary for the manifest: a mismatch flags the run."""
    changes = verify_inputs(ws)
    return {
        "workspace": str(ws.root),
        "inputs_sha256": dict(ws.checksums),
        "input_changes": changes,
        "flagged": bool(changes),
        "flag_reasons": ["input_changed"] if changes else [],
    }

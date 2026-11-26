"""Read a single value from a simple KEY=VALUE .env file (parent process only).

The value is returned to the caller; it is never put into os.environ, so child
processes started by the executor cannot inherit it.
"""
from __future__ import annotations

from pathlib import Path


def read_env_key(path: Path, name: str = "MODEL_API_KEY") -> str | None:
    """Return the value of ``name`` from a simple KEY=VALUE .env file, or None."""
    path = Path(path)
    if not path.exists():
        return None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            value = value.strip().strip('"').strip("'")
            return value or None
    return None

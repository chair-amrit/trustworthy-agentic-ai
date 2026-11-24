"""Offline tests for scripts/smoke_gemini.py (no network, no API key)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("smoke_gemini", ROOT / "scripts" / "smoke_gemini.py")
smoke = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(smoke)


def test_read_env_key(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# comment\nOTHER=1\nMODEL_API_KEY = \"abc123\"\n", encoding="utf-8")
    assert smoke.read_env_key(env) == "abc123"


def test_read_env_key_missing_or_empty(tmp_path):
    assert smoke.read_env_key(tmp_path / "nope.env") is None
    env = tmp_path / ".env"
    env.write_text("MODEL_API_KEY=\n# MODEL_API_KEY=commented\n", encoding="utf-8")
    assert smoke.read_env_key(env) is None


def test_prompt_b_matches_baseline_and_has_no_answer():
    prompts = smoke.build_prompts()
    b = prompts["b_task5_step1"]
    tasks = json.loads((ROOT / "tasks" / "dev_tasks.json").read_text(encoding="utf-8"))
    task = next(t for t in tasks if t["task_id"] == 5)
    system = (ROOT / "src" / "agent" / "prompts" / "system_v0.txt").read_text(encoding="utf-8")
    assert b["system"] == system
    assert b["user"].startswith("Task ID: 5\nQuestion: " + task["question"])
    assert str(task["answer"]) not in b["user"] + b["system"]
    assert prompts["a_ok"] == {"system": None, "user": "Reply with OK"}


def test_redact():
    assert smoke._redact("bad key abc in msg", "abc") == "bad key *** in msg"
    assert smoke._redact("text", None) == "text"

"""One-off smoke test of the Gemini API (Track A, day-1 free-API test).

Makes exactly two calls, no retries:
  (a) "Reply with OK"
  (b) the first-step prompt baseline-v0 builds for DABStep task 5

The reply is only printed; no model-written code is executed.
The API key is read from MODEL_API_KEY in .env, passed explicitly to the client,
never put into os.environ, never printed and never saved.

Usage:
  python scripts/smoke_gemini.py            # real calls (needs MODEL_API_KEY in .env)
  python scripts/smoke_gemini.py --dry-run  # build and show prompts, no network
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent import config  # noqa: E402
from agent.loop import _task_prompt  # noqa: E402  (exact baseline-v0 prompt builder)

ENV_PATH = ROOT / ".env"
TASKS_PATH = ROOT / "tasks" / "dev_tasks.json"
OUT_PATH = ROOT / "runs" / "smoke_gemini.json"

MODEL_ID = "gemini-3.5-flash-lite"
THINKING_LEVEL = "minimal"
TEMPERATURE = 1.0          # Google's recommended default for Gemini 3
MAX_OUTPUT_TOKENS = 1024   # thinking tokens count toward this limit
PREVIEW_CHARS = 500


def read_env_key(path: Path, name: str = "MODEL_API_KEY") -> str | None:
    """Return the value of ``name`` from a simple KEY=VALUE .env file, or None."""
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


def build_prompts() -> dict[str, dict[str, str | None]]:
    """Build both prompts. The task's answer is removed before anything is built."""
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    task = dict(next(t for t in tasks if t["task_id"] == 5))
    reference = task.pop("answer", None)
    assert "answer" not in task

    system_prompt = (
        Path(config.__file__).with_name("prompts") / f"{config.PROMPT_VERSION}.txt"
    ).read_text(encoding="utf-8")
    user_prompt = _task_prompt(task)

    if reference is not None:
        ref = str(reference)
        if ref in system_prompt or ref in user_prompt:
            raise SystemExit("ABORT: reference answer text found in prompt (b).")

    return {
        "a_ok": {"system": None, "user": "Reply with OK"},
        "b_task5_step1": {"system": system_prompt, "user": user_prompt},
    }


def _redact(text: str, secret: str | None) -> str:
    return text.replace(secret, "***") if secret else text


def _settings() -> dict[str, object]:
    return {
        "model_requested": MODEL_ID,
        "thinking_level": THINKING_LEVEL,
        "include_thoughts": False,
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "retry_attempts": 1,
        "prompt_version": config.PROMPT_VERSION,
    }


def _save(record: dict[str, object]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="build and print prompts and settings; make no API calls")
    args = parser.parse_args()

    prompts = build_prompts()

    if args.dry_run:
        print("DRY RUN: no API calls.")
        print(json.dumps(_settings(), indent=2))
        for name, p in prompts.items():
            print(f"\n=== {name} ===")
            if p["system"]:
                print(f"--- system ---\n{p['system']}")
            print(f"--- user ---\n{p['user']}")
        return 0

    key = read_env_key(ENV_PATH)
    if not key:
        print("MODEL_API_KEY is missing or empty in .env. No calls made.")
        return 1

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(
            # SDK default is already one attempt; stated explicitly so no retry happens.
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    record: dict[str, object] = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "sdk": f"google-genai {genai.__version__}",
        "settings": _settings(),
        "calls": [],
    }

    for name, p in prompts.items():
        cfg = types.GenerateContentConfig(
            system_instruction=p["system"],
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(
                thinking_level=THINKING_LEVEL, include_thoughts=False
            ),
        )
        t0 = time.perf_counter()
        try:
            response = client.models.generate_content(
                model=MODEL_ID, contents=p["user"], config=cfg
            )
        except Exception as exc:  # any error, including 429: report and stop
            latency = time.perf_counter() - t0
            err = _redact(f"{type(exc).__name__}: {exc}", key)
            print(f"\n=== {name} === ERROR after {latency:.2f}s\n{err}\nStopping. No retries.")
            record["calls"].append({"name": name, "error": err, "latency_s": round(latency, 3)})
            _save(record)
            return 1
        latency = time.perf_counter() - t0

        usage = response.usage_metadata
        candidate = response.candidates[0] if response.candidates else None
        finish = getattr(getattr(candidate, "finish_reason", None), "name", None) if candidate else None
        text = response.text or ""
        call = {
            "name": name,
            "model_version": response.model_version,
            "response_id": response.response_id,
            "finish_reason": finish,
            "input_tokens": getattr(usage, "prompt_token_count", None),
            "output_tokens": getattr(usage, "candidates_token_count", None),
            "thinking_tokens": getattr(usage, "thoughts_token_count", None),
            "total_tokens": getattr(usage, "total_token_count", None),
            "latency_s": round(latency, 3),
            "reply_chars": len(text),
            "reply_preview": _redact(text[:PREVIEW_CHARS], key),
        }
        record["calls"].append(call)

        print(f"\n=== {name} ===")
        print(f"model_version : {call['model_version']}")
        print(f"finish_reason : {call['finish_reason']}")
        print(f"tokens in/out/thinking/total : {call['input_tokens']} / "
              f"{call['output_tokens']} / {call['thinking_tokens']} / {call['total_tokens']}")
        print(f"latency       : {call['latency_s']} s")
        print(f"reply (first {PREVIEW_CHARS} of {call['reply_chars']} chars):\n{call['reply_preview']}")

    _save(record)
    print(f"\nSaved metadata (no key) to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

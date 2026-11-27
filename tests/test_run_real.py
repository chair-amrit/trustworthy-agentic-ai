"""Step 3: offline test of scripts/run_real.py with a mocked Gemini client (no API calls)."""
import json

from agent.llm import GeminiLLM
from scripts import run_real
from tests.test_gemini_llm import FakeClient, FakeClock, KEY, _err, _response

CODE = ("```python\nimport pandas as pd\n"
        "print(pd.read_csv('data/context/payments.csv')['issuing_country'].value_counts().idxmax())\n```")


def _mock_llm(behaviours):
    clock = FakeClock()
    return GeminiLLM(client=FakeClient(behaviours), api_key=KEY, sleep=clock.sleep, clock=clock)


def _read_jsonl(p):
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()]


def test_run_real_offline_success(tmp_path):
    runs, work = tmp_path / "runs", tmp_path / "work"
    llm = _mock_llm([_response(CODE), _err(503), _response("FINAL ANSWER: NL")])
    [m] = run_real.main(["--task", "5"], llm, runs_dir=runs, work_root=work)

    assert m["status"] == "final" and m["final_answer"] == "NL" and m["matches_reference"] is True
    assert m["steps_used"] == 2 and m["n_calls"] == 2 and m["n_attempts"] == 3
    assert m["total_tokens"] == 2 * 254 and m["thinking_tokens"] is None
    assert m["thinking_tokens_missing_in_calls"] == 2
    assert m["flagged"] is False and m["flag_reasons"] == []
    s = m["settings"]
    assert (s["model_requested"], s["temperature"], s["thinking_level"], s["max_output_tokens"]) == (
        "gemini-3.1-flash-lite", 1.0, "minimal", 1024)
    assert "git_commit" in m and "git_dirty" in m
    assert m["workspace"].startswith(str(work))
    from agent.loop import prompt_sha256, system_prompt_sha256
    assert m["prompt_version"] == "system_v1"
    assert m["prompt_sha256"] == prompt_sha256("system_v1")
    assert m["system_prompt_sha256"] == system_prompt_sha256("system_v1")
    first = llm._client.calls[0]
    sent_system = first["config"].system_instruction
    assert "data/context/fees.json" in sent_system and "payments-readme.md" in sent_system
    sent_task = first["contents"][0].parts[0].text
    assert sent_task.startswith("Task ID: 5\n") and "payments.csv" not in sent_task

    steps = _read_jsonl(runs / m["step_log"])
    calls = _read_jsonl(runs / m["call_log"])
    assert [(r["run_id"], r["step"]) for r in steps] == [(c["run_id"], c["step"]) for c in calls]
    assert all(r["temperature"] == 1.0 and r["model"] == "gemini-3.1-flash-lite" for r in steps)
    assert steps[0]["observation"] == "Observation:\nNL"

    text = "".join(p.read_text(encoding="utf-8") for p in runs.iterdir())
    assert KEY not in text and '"answer"' not in text


def test_run_real_prompt_is_selectable(tmp_path):
    llm = _mock_llm([_response("FINAL ANSWER: NL")])
    [m] = run_real.main(["--task", "5", "--prompt", "system_v0"], llm,
                        runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m["prompt_version"] == "system_v0"
    steps = _read_jsonl(tmp_path / "runs" / m["step_log"])
    assert steps[0]["prompt_version"] == "system_v0"


def test_run_real_offline_api_failed(tmp_path):
    runs = tmp_path / "runs"
    llm = _mock_llm([_err(503)] * 5)
    [m] = run_real.main(["--task", "5"], llm, runs_dir=runs, work_root=tmp_path / "work")
    assert m["status"] == "api_failed" and m["final_answer"] is None
    assert m["matches_reference"] is None
    assert m["n_calls"] == 1 and m["n_attempts"] == 5 and m["n_failed_calls"] == 1
    assert m["steps_used"] == 0
    [c] = _read_jsonl(runs / m["call_log"])
    assert c["status"] == "api_failed" and c["step"] == 1


def test_two_runs_get_separate_ids_and_folders(tmp_path):
    llm = _mock_llm([_response("FINAL ANSWER: NL"), _response("FINAL ANSWER: XX")])
    m1, m2 = run_real.main(["--task", "5", "--runs", "2"], llm,
                           runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m1["run_id"] != m2["run_id"] and m1["workspace"] != m2["workspace"]
    assert (m1["matches_reference"], m2["matches_reference"]) == (True, False)
    assert m1["n_calls"] == m2["n_calls"] == 1

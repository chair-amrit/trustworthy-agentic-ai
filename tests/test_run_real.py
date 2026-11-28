"""Step 3: offline test of scripts/run_real.py with a mocked Gemini client (no API calls)."""
import json

import pytest

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
    [m] = run_real.main(["--task", "5", "--prompt", "system_v0", "--protocol", "v0"], llm,
                        runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m["prompt_version"] == "system_v0"
    steps = _read_jsonl(tmp_path / "runs" / m["step_log"])
    assert steps[0]["prompt_version"] == "system_v0"


def test_defaults_are_d3_and_recorded(tmp_path):
    llm = _mock_llm([_response(CODE), _response("FINAL ANSWER: NL")])
    [m] = run_real.main(["--task", "5"], llm, runs_dir=tmp_path / "runs",
                        work_root=tmp_path / "work")
    assert (m["thinking_level"], m["max_output_tokens"]) == ("minimal", 1024)
    assert m["settings_are_d3_default"] is True
    assert m["finish_reasons"] == ["STOP", "STOP"]


def test_thinking_and_max_tokens_flags_build_the_model(tmp_path, monkeypatch):
    built = {}

    def fake_gemini(**kwargs):
        built.update(kwargs)
        clock = FakeClock()
        return GeminiLLM(client=FakeClient([_response(CODE), _response("FINAL ANSWER: NL")]),
                         api_key=KEY, sleep=clock.sleep, clock=clock, **kwargs)

    monkeypatch.setattr(run_real, "GeminiLLM", fake_gemini)
    [m] = run_real.main(["--task", "5", "--thinking", "low", "--max-output-tokens", "4096"],
                        runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert built == {"thinking_level": "low", "max_output_tokens": 4096}
    assert (m["thinking_level"], m["max_output_tokens"]) == ("low", 4096)
    assert m["settings_are_d3_default"] is False
    assert (m["settings"]["thinking_level"], m["settings"]["max_output_tokens"]) == ("low", 4096)
    assert m["status"] == "final" and m["matches_reference"] is True


def test_flags_reach_the_api_request(tmp_path):
    clock = FakeClock()
    client = FakeClient([_response(CODE), _response("FINAL ANSWER: NL")])
    llm = GeminiLLM(client=client, api_key=KEY, sleep=clock.sleep, clock=clock,
                    thinking_level="low", max_output_tokens=4096)
    run_real.main(["--task", "5", "--thinking", "low", "--max-output-tokens", "4096"], llm,
                  runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    cfg = client.calls[0]["config"]
    assert cfg.max_output_tokens == 4096
    assert "low" in str(cfg.thinking_config.thinking_level).lower()


@pytest.mark.parametrize("argv", [
    ["--thinking", "high"], ["--thinking", "medium"], ["--max-output-tokens", "0"],
])
def test_bad_flag_values_are_refused(tmp_path, argv):
    with pytest.raises(SystemExit):
        run_real.main(["--task", "5", *argv], _mock_llm([]), runs_dir=tmp_path / "runs",
                      work_root=tmp_path / "work")


def test_flags_must_match_an_injected_model(tmp_path):
    with pytest.raises(SystemExit):
        run_real.main(["--task", "5", "--thinking", "low"], _mock_llm([]),
                      runs_dir=tmp_path / "runs", work_root=tmp_path / "work")


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
    llm = _mock_llm([_response(CODE), _response("FINAL ANSWER: NL"),
                     _response(CODE), _response("FINAL ANSWER: XX")])
    m1, m2 = run_real.main(["--task", "5", "--runs", "2"], llm,
                           runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m1["run_id"] != m2["run_id"] and m1["workspace"] != m2["workspace"]
    assert (m1["matches_reference"], m2["matches_reference"]) == (True, False)
    assert m1["n_calls"] == m2["n_calls"] == 2
    assert m1["protocol"] == m2["protocol"] == "v1"


def test_protocol_is_selectable_and_recorded(tmp_path):
    # v0 accepts an immediate answer; v1 (default) would reject it (rule 2).
    llm = _mock_llm([_response("FINAL ANSWER: NL")])
    [m] = run_real.main(["--task", "5", "--protocol", "v0"], llm,
                        runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m["protocol"] == "v0" and m["status"] == "final" and m["n_calls"] == 1
    steps = _read_jsonl(tmp_path / "runs" / m["step_log"])
    assert "protocol" not in steps[0]


def test_default_protocol_v1_rejects_immediate_answer(tmp_path):
    llm = _mock_llm([_response("FINAL ANSWER: NL"), _response(CODE), _response("FINAL ANSWER: NL")])
    [m] = run_real.main(["--task", "5"], llm,
                        runs_dir=tmp_path / "runs", work_root=tmp_path / "work")
    assert m["protocol"] == "v1" and m["status"] == "final" and m["matches_reference"] is True
    steps = _read_jsonl(tmp_path / "runs" / m["step_log"])
    assert [s["action_type"] for s in steps] == ["invalid", "code", "final"]
    assert all(s["protocol"] == "v1" for s in steps)

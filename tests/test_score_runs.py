"""Step 5: scripts/score_runs.py with made-up answers and runs (no real references)."""
import csv
import json

import pytest

from scripts import score_runs as sr

REFS = [
    {"task_id": 1, "question": "q", "guidelines": "g", "answer": "B. BE"},
    {"task_id": 2, "question": "q", "guidelines": "g", "answer": "29, 78, 312"},
    {"task_id": 3, "question": "q", "guidelines": "g", "answer": "E:13.57"},
    {"task_id": 4, "question": "q", "guidelines": "g", "answer": "0.123217"},
    {"task_id": 5, "question": "q", "guidelines": "g", "answer": "SECRETREF"},
]


# --- official score ------------------------------------------------------------

@pytest.mark.parametrize("final,ref,score", [
    ("B. BE", "B. BE", 1),
    ("BE", "B. BE", 0),
    ("312, 29, 78", "29, 78, 312", 1),      # list order already ignored by answers.py
    ("F29, F78, F312", "29, 78, 312", 0),
    ("0.1232170", "0.123217", 1),
    (None, "x", None),
    ("x", None, None),
])
def test_official_score(final, ref, score):
    assert sr.score_answer(final, ref) == score


# --- diagnostic --------------------------------------------------------------

@pytest.mark.parametrize("final,ref", [
    ("BE", "B. BE"),                        # option letter dropped
    ("A. BE", "BE"),                        # option letter added
    ("F29, F78, F312", "29, 78, 312"),      # F prefix on IDs
    ("f312,f29 , 78", "29, 78, 312"),       # lower-case f, spaces, order
    ("E: 13.57", "E:13.57"),                # whitespace inside a value
])
def test_format_only_mismatch_true(final, ref):
    assert sr.score_answer(final, ref) == 0
    assert sr.format_only_mismatch(final, ref) is True


@pytest.mark.parametrize("final,ref", [
    ("A. NL", "B. BE"),                     # different content
    ("F29, F78", "29, 78, 312"),            # missing item
    ("nl", "NL"),                           # case is NOT normalised
    ("A:13.57", "E:13.57"),                 # "E:" is part of the answer, not an option letter
    ("Not Applicable", "0.5"),
])
def test_format_only_mismatch_false_for_real_errors(final, ref):
    assert sr.format_only_mismatch(final, ref) is False


def test_format_only_is_false_for_correct_and_missing_answers():
    assert sr.format_only_mismatch("B. BE", "B. BE") is False
    assert sr.format_only_mismatch(None, "B. BE") is False


# --- whole script ------------------------------------------------------------

def _manifest(runs, run_id, task_id, final, status="final", **extra):
    m = {"run_id": run_id, "task_id": task_id, "model": "gemini-x", "final_answer": final,
         "status": status, "started_utc": f"2026-11-28T00:00:{len(list(runs.iterdir())):02d}",
         **extra}
    (runs / f"{run_id}.manifest.json").write_text(json.dumps(m), encoding="utf-8")


@pytest.fixture
def setup(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    ref_path = tmp_path / "dev_tasks.json"
    ref_path.write_text(json.dumps(REFS), encoding="utf-8")
    new = dict(git_commit="bbbbbbb1234", prompt_version="system_v1", protocol="v1")
    _manifest(runs, "new-1", 1, "B. BE", **new)                    # correct
    _manifest(runs, "new-2", 2, "F29, F78, F312", **new)           # wrong, format-only
    _manifest(runs, "new-3", 3, "A:13.57", **new)                  # wrong, real error
    _manifest(runs, "new-4", 4, None, status="max_steps", **new)   # no answer
    _manifest(runs, "new-5", 5, "WRONG", **new)
    old = dict(git_commit="aaaaaaa9999", prompt_version="system_v0")  # no protocol field
    _manifest(runs, "old-1", 1, "BE", **old)                       # wrong, format-only
    # early fake-run manifest: no final_answer/status/prompt/protocol/commit -> step log
    (runs / "fake-1.manifest.json").write_text(json.dumps(
        {"run_id": "fake-1", "task_id": 4, "model": "fake-scripted"}), encoding="utf-8")
    (runs / "fake-1.jsonl").write_text(
        json.dumps({"action_type": "code", "final_answer": None, "terminated_reason": None}) + "\n"
        + json.dumps({"action_type": "final", "final_answer": "0.123217",
                      "terminated_reason": "final"}) + "\n", encoding="utf-8")
    return runs, ref_path


def test_rows_scores_and_implied_fields(setup):
    runs, ref_path = setup
    rows = {r["run_id"]: r for r in sr.collect_rows(runs, ref_path)}
    assert rows["new-1"]["score"] == 1 and rows["new-1"]["format_only_mismatch"] is False
    assert rows["new-2"]["score"] == 0 and rows["new-2"]["format_only_mismatch"] is True
    assert rows["new-3"]["score"] == 0 and rows["new-3"]["format_only_mismatch"] is False
    assert rows["new-4"]["score"] is None and rows["new-4"]["status"] == "max_steps"
    assert rows["old-1"]["protocol"] == "v0" and rows["old-1"]["format_only_mismatch"] is True
    f = rows["fake-1"]
    assert (f["final_answer"], f["status"], f["score"]) == ("0.123217", "final", 1)
    assert (f["prompt"], f["protocol"]) == ("system_v0", "v0")
    assert rows["new-1"]["batch"] == "bbbbbbb|gemini-x|system_v1|v1|n/a|n/a"
    assert rows["old-1"]["batch"] == "aaaaaaa|gemini-x|system_v0|v0|n/a|n/a"
    assert rows["fake-1"]["batch"] == "no-commit|fake-scripted|system_v0|v0|n/a|n/a"


def test_batch_key_separates_thinking_settings_at_same_commit(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    ref_path = tmp_path / "dev_tasks.json"
    ref_path.write_text(json.dumps(REFS), encoding="utf-8")
    same = dict(git_commit="ccccccc0000", prompt_version="system_v1", protocol="v1")
    _manifest(runs, "min-1", 1, "B. BE", thinking_level="minimal", max_output_tokens=1024, **same)
    _manifest(runs, "low-1", 1, "BE", thinking_level="low", max_output_tokens=4096, **same)
    # older manifest: settings only inside "settings"
    _manifest(runs, "old-min", 1, "B. BE",
              settings={"thinking_level": "minimal", "max_output_tokens": 1024}, **same)
    rows = {r["run_id"]: r for r in sr.collect_rows(runs, ref_path)}
    assert rows["min-1"]["batch"] == "ccccccc|gemini-x|system_v1|v1|minimal|1024"
    assert rows["low-1"]["batch"] == "ccccccc|gemini-x|system_v1|v1|low|4096"
    assert rows["old-min"]["batch"] == rows["min-1"]["batch"]
    batches = sr.summarise(list(rows.values()))
    assert batches["ccccccc|gemini-x|system_v1|v1|minimal|1024"]["runs"] == 2
    assert batches["ccccccc|gemini-x|system_v1|v1|low|4096"]["runs"] == 1


def test_csv_written_with_required_columns(setup):
    runs, ref_path = setup
    sr.main([], runs_dir=runs, reference_path=ref_path)
    with (runs / "scores.csv").open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for col in ("run_id", "task_id", "prompt", "protocol", "status", "final_answer",
                "score", "format_only_mismatch"):
        assert col in reader.fieldnames
    by_id = {r["run_id"]: r for r in rows}
    assert by_id["new-2"]["score"] == "0" and by_id["new-2"]["format_only_mismatch"] == "true"
    assert by_id["new-4"]["score"] == "" and by_id["new-4"]["final_answer"] == ""
    assert len(rows) == 7


def test_summary_per_batch_and_no_reference_printed(setup, capsys):
    runs, ref_path = setup
    batches = sr.summarise(sr.collect_rows(runs, ref_path))
    b = batches["bbbbbbb|gemini-x|system_v1|v1|n/a|n/a"]
    assert (b["runs"], b["correct"], b["wrong"], b["no_answer"], b["format_only"]) == (5, 1, 3, 1, 1)
    assert batches["aaaaaaa|gemini-x|system_v0|v0|n/a|n/a"]["protocol_implied"] is True
    sr.main([], runs_dir=runs, reference_path=ref_path)
    out = capsys.readouterr().out
    assert "correct 1/5" in out and "format-only diagnostic: 1" in out
    for ref in ("SECRETREF", "B. BE", "E:13.57", "29, 78, 312", "0.123217"):
        assert ref not in out

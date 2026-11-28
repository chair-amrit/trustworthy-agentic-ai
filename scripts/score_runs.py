"""Score final answers of all runs (Track A, step 5). EVALUATOR SIDE ONLY.

    python scripts/score_runs.py

For every runs/*.manifest.json:
  - score            the OFFICIAL score for this project: agent.answers.answers_match
                     against tasks/dev_tasks.json (1 = correct, 0 = wrong, empty = no answer)
  - format_only_mismatch
                     a DIAGNOSTIC, NOT a score: for a wrong answer, would it match after
                     stripping an option letter ("A. "), an "F" prefix on IDs ("F29"),
                     whitespace, and list order? true/false (false for correct/no answer)

Writes runs/scores.csv and prints a per-batch summary (batch = commit + model + prompt
+ protocol + thinking_level + max_output_tokens). Reference answers are NEVER printed;
only scores and counts.

Older manifests lack some fields:
  - protocol missing   -> "v0" (protocols were added in commit 6a5543c; earlier code = v0)
  - prompt missing     -> "system_v0" (the only/default prompt at that time)
  - final_answer/status missing (early fake runs) -> read from runs/<run_id>.jsonl
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.answers import answers_match  # noqa: E402

RUNS_DIR = ROOT / "runs"
REFERENCE_PATH = ROOT / "tasks" / "dev_tasks.json"   # evaluator side: has answers
CSV_COLUMNS = ["run_id", "task_id", "prompt", "protocol", "status", "final_answer",
               "score", "format_only_mismatch", "batch"]


# --- official score ----------------------------------------------------------

def load_references(path: Path = REFERENCE_PATH) -> dict[int, str]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return {int(r["task_id"]): str(r["answer"]) for r in rows if r.get("answer") is not None}


def score_answer(final_answer: str | None, reference: str | None) -> int | None:
    """Official score: 1/0 via answers.answers_match; None if no answer or no reference."""
    if final_answer is None or reference is None:
        return None
    return int(answers_match(final_answer, reference))


# --- diagnostic (NOT the score) ----------------------------------------------

_OPTION_LETTER = re.compile(r"^[A-Z][.)]\s*")   # "A. NL", "B) BE"  (not "E:13.57")
_F_ID = re.compile(r"^[Ff](\d+)$")              # "F29" -> "29"


def _diag_normalise(text: str) -> str:
    text = _OPTION_LETTER.sub("", text.strip())
    items = text.split(",") if "," in text else [text]
    items = [re.sub(r"\s+", "", item) for item in items]
    items = [_F_ID.sub(r"\1", item) for item in items]
    return ",".join(items)


def format_only_mismatch(final_answer: str | None, reference: str | None) -> bool:
    """DIAGNOSTIC: True only if the answer is officially WRONG but would match after
    the format normalisation above (applied to both sides). Not a score."""
    if final_answer is None or reference is None or answers_match(final_answer, reference):
        return False
    return answers_match(_diag_normalise(final_answer), _diag_normalise(reference))


# --- collecting runs ---------------------------------------------------------

def thinking_settings(m: dict) -> tuple[str, str]:
    """(thinking_level, max_output_tokens) for the batch key.

    Newer manifests have them at top level; older real runs only inside "settings";
    fake runs have neither ("n/a")."""
    settings = m.get("settings") or {}
    thinking = m.get("thinking_level") or settings.get("thinking_level") or "n/a"
    max_out = m.get("max_output_tokens") or settings.get("max_output_tokens") or "n/a"
    return str(thinking), str(max_out)

def _from_step_log(runs_dir: Path, run_id: str) -> tuple[str | None, str | None]:
    log = runs_dir / f"{run_id}.jsonl"
    if not log.exists():
        return None, None
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
    if not records:
        return None, None
    last = records[-1]
    final = last.get("final_answer") if last.get("action_type") == "final" else None
    return final, last.get("terminated_reason")


def collect_rows(runs_dir: Path = RUNS_DIR, reference_path: Path = REFERENCE_PATH) -> list[dict]:
    refs = load_references(reference_path)
    rows = []
    for path in sorted(Path(runs_dir).glob("*.manifest.json")):
        m = json.loads(path.read_text(encoding="utf-8"))
        run_id, task_id = m["run_id"], int(m["task_id"])
        if "final_answer" in m and "status" in m:
            final, status = m["final_answer"], m["status"]
        else:
            final, status = _from_step_log(Path(runs_dir), run_id)
        prompt = m.get("prompt_version") or "system_v0"
        protocol = m.get("protocol") or "v0"
        commit = (m.get("git_commit") or "")[:7] or "no-commit"
        thinking, max_out = thinking_settings(m)
        batch = f"{commit}|{m.get('model', '?')}|{prompt}|{protocol}|{thinking}|{max_out}"
        ref = refs.get(task_id)
        rows.append({
            "run_id": run_id,
            "task_id": task_id,
            "prompt": prompt,
            "protocol": protocol,
            "status": status or "unknown",
            "final_answer": final,
            "score": score_answer(final, ref),
            "format_only_mismatch": format_only_mismatch(final, ref),
            "batch": batch,
            "_protocol_implied": "protocol" not in m,
            "_started": m.get("started_utc") or run_id,
        })
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r,
                        "final_answer": "" if r["final_answer"] is None else r["final_answer"],
                        "score": "" if r["score"] is None else r["score"],
                        "format_only_mismatch": str(r["format_only_mismatch"]).lower()})


def summarise(rows: list[dict]) -> "OrderedDict[str, dict]":
    batches: "OrderedDict[str, dict]" = OrderedDict()
    for r in sorted(rows, key=lambda r: (r["_started"], r["run_id"])):
        b = batches.setdefault(r["batch"], {"runs": 0, "correct": 0, "wrong": 0, "no_answer": 0,
                                            "format_only": 0, "protocol_implied": False,
                                            "first": r["_started"]})
        b["runs"] += 1
        b["protocol_implied"] |= r["_protocol_implied"]
        if r["score"] is None:
            b["no_answer"] += 1
        elif r["score"] == 1:
            b["correct"] += 1
        else:
            b["wrong"] += 1
            b["format_only"] += r["format_only_mismatch"]
    return batches


def print_summary(batches) -> None:
    """Scores and counts only. Never prints reference answers."""
    print("Per batch (commit | model | prompt | protocol | thinking | max_output_tokens). "
          "Official score = answers.py.")
    for key, b in batches.items():
        note = "  [protocol not in manifest -> v0]" if b["protocol_implied"] else ""
        print(f"- {key}{note}")
        print(f"    correct {b['correct']}/{b['runs']} | wrong {b['wrong']} "
              f"(format-only diagnostic: {b['format_only']}) | no answer {b['no_answer']}")


def main(argv: list[str] | None = None, runs_dir: Path = RUNS_DIR,
         reference_path: Path = REFERENCE_PATH) -> list[dict]:
    rows = collect_rows(runs_dir, reference_path)
    out = Path(runs_dir) / "scores.csv"
    write_csv(rows, out)
    print_summary(summarise(rows))
    print(f"Wrote {len(rows)} rows to {out}")
    return rows


if __name__ == "__main__":
    main()

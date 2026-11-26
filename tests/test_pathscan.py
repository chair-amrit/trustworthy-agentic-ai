"""Slice e (D5, E1): static code scan for paths outside the working folder."""
import json

import pytest

from agent.llm import FakeLLM
from agent.logger import StepLogger
from agent.loop import run_agent
from agent.pathscan import merge_run_flags, scan_code
from agent.tasks import load_agent_task
from agent.workspace import create_workspace
from scripts.run_fake import write_run_outputs


def _reasons(code):
    return sorted({(f["reason"], f["match"]) for f in scan_code(code)})


FLAGGED = [
    ("open('C:\\\\Users\\\\x.txt')", ("absolute_path", "C:\\Users\\x.txt")),
    ("open('D:/data/x.csv')", ("absolute_path", "D:/data/x.csv")),
    ("open(r'\\\\server\\share\\f')", ("absolute_path", "\\\\server\\share\\f")),
    ("open('/etc/passwd')", ("absolute_path", "/etc/passwd")),
    ("open('../../tasks/dev_tasks.json')", ("parent_dir", "../../tasks/dev_tasks.json")),
    ("open('data\\\\..\\\\..\\\\x')", ("parent_dir", "data\\..\\..\\x")),
    ("import os\nos.listdir('..')", ("parent_dir", "..")),
    ("open('~/secrets.txt')", ("home_dir", "~/secrets.txt")),
    ("import sys\nprint(sys.executable)", ("path_builder", "sys.executable")),
    ("import sys\nprint(sys.prefix)", ("path_builder", "sys.prefix")),
    ("print(__file__)", ("path_builder", "__file__")),
    ("from pathlib import Path\nPath.home()", ("path_builder", "Path.home")),
    ("import pathlib\npathlib.Path.home()", ("path_builder", "Path.home")),
    ("import os\nos.path.expanduser('x')", ("path_builder", "expanduser")),
    ("import os\nos.environ['X']", ("path_builder", "os.environ")),
    ("import os\nos.getenv('X')", ("path_builder", "os.getenv")),
    ("from os import environ", ("path_builder", "os.environ")),
    ("from sys import executable", ("path_builder", "sys.executable")),
    ("p = f'{1}/../x'", ("parent_dir", "/../x")),
]


@pytest.mark.parametrize("code,expected", FLAGGED)
def test_flagged(code, expected):
    assert expected in _reasons(code)


NOT_FLAGGED = [
    "import pandas as pd\npd.read_csv('data/context/payments.csv')",
    "open('data\\\\context\\\\fees.json')",
    "open('./data/context/manual.md')",
    "print('Loading...')",
    "print('approx ~5 rows')",
    "x = '2023/01/02'.split('/')",
    "print(10 / 2)",
    "df = None\nprint('a/b')",
    "url = 'https://example.com/x'",
    "def (",                                # syntax error: never runs, so not flagged
    "import os\nos.listdir('.')",
    "# open('C:/x') in a comment only",
]


@pytest.mark.parametrize("code", NOT_FLAGGED)
def test_not_flagged(code):
    assert scan_code(code) == []


def test_flag_carries_line_and_code_line():
    flags = scan_code("x = 1\nopen('../secret')\n")
    assert flags == [{"reason": "parent_dir", "match": "../secret", "line": 2,
                      "code_line": "open('../secret')"}]


def test_merge_run_flags():
    clean = {"flag_reasons": [], "input_changes": []}
    assert merge_run_flags([], clean) == {"flagged": False, "flag_reasons": [], "path_flag_count": 0}
    both = merge_run_flags([{"reason": "parent_dir"}], {"flag_reasons": ["input_changed"]})
    assert both == {"flagged": True, "flag_reasons": ["input_changed", "path_scan"],
                    "path_flag_count": 1}


def test_fake_run_reading_answer_file_is_flagged_and_reviewed(tmp_path):
    ws = create_workspace("leak-run", work_root=tmp_path / "work")
    log = tmp_path / "leak.jsonl"
    leak_code = "```python\nprint(open('../../tasks/dev_tasks.json').read()[:10])\n```"
    result = run_agent(
        load_agent_task(5),
        FakeLLM([leak_code, "```python\nprint('NL')\n```", "FINAL ANSWER: NL"]),
        StepLogger(log),
        workdir=ws.root,
        run_id="leak-run",
    )
    # The run keeps going after the flag.
    assert result.terminated_reason == "final" and result.final_answer == "NL"

    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert [len(r["path_flags"]) for r in records] == [1, 0, 0]
    assert records[0]["path_flags"][0]["reason"] == "parent_dir"

    runs_dir = tmp_path / "runs"
    manifest = write_run_outputs("leak-run", 5, "fake-scripted", result, ws, runs_dir)
    assert manifest["flagged"] is True and manifest["flag_reasons"] == ["path_scan"]

    review = [json.loads(line) for line in
              (runs_dir / "review_list.jsonl").read_text(encoding="utf-8").splitlines()]
    assert review == [{
        "run_id": "leak-run",
        "step": 1,
        "reason": "parent_dir",
        "match": "../../tasks/dev_tasks.json",
        "code_line": "print(open('../../tasks/dev_tasks.json').read()[:10])",
    }]


def test_clean_run_writes_no_review_entry(tmp_path):
    ws = create_workspace("clean-run", work_root=tmp_path / "work")
    result = run_agent(
        load_agent_task(5),
        FakeLLM(["```python\nprint(open('data/context/fees.json').read(1))\n```", "FINAL ANSWER: NL"]),
        StepLogger(tmp_path / "clean.jsonl"),
        workdir=ws.root,
    )
    runs_dir = tmp_path / "runs"
    manifest = write_run_outputs("clean-run", 5, "fake-scripted", result, ws, runs_dir)
    assert manifest["flagged"] is False
    assert not (runs_dir / "review_list.jsonl").exists()

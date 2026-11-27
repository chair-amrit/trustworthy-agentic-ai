"""D5: absolute paths are scrubbed from error output before the model sees it."""
import re
import sysconfig
from pathlib import Path

from agent import config
from agent.executor import run_step, scrub_paths

DRIVE_PATH = re.compile(r"[A-Za-z]:[\\/]")


def test_pandas_error_shows_no_drive_paths(tmp_path):
    r = run_step([], "import pandas as pd\npd.DataFrame({'a': [1]})['zz']", tmp_path)
    assert not r.ok and "KeyError" in r.stderr
    assert not DRIVE_PATH.search(r.stderr), r.stderr
    assert "<python-lib>/pandas/" in r.stderr
    assert str(config.REPO_ROOT).lower() not in r.stderr.lower()


def test_absolute_path_inside_workdir_becomes_relative(tmp_path):
    target = tmp_path / "data" / "context" / "missing.csv"
    r = run_step([], f"open({str(target)!r})", tmp_path)
    assert "FileNotFoundError" in r.stderr
    assert not DRIVE_PATH.search(r.stderr), r.stderr
    assert "data/context/missing.csv" in r.stderr


def test_relative_path_stays_relative(tmp_path):
    r = run_step([], "open('data/context/nope.csv')", tmp_path)
    assert "'data/context/nope.csv'" in r.stderr


def test_path_outside_workdir_is_replaced(tmp_path):
    r = run_step([], r"open(r'D:\some_other_place\secret.txt')", tmp_path)
    assert "FileNotFoundError" in r.stderr
    assert "<outside-path>" in r.stderr and "secret.txt" not in r.stderr


def test_answer_file_path_is_hidden(tmp_path):
    answers = config.REPO_ROOT / "tasks" / "missing_dev_tasks.json"
    r = run_step([], f"open({str(answers)!r})", tmp_path)
    assert "<outside-path>" in r.stderr
    assert "mycodes" not in r.stderr and "missing_dev_tasks" not in r.stderr


def test_scrub_paths_unit(tmp_path):
    lib = sysconfig.get_paths()["purelib"]
    wd = tmp_path / "run-1"
    text = "\n".join([
        f'  File "{lib}\\pandas\\core\\frame.py", line 1, in f',
        f"No such file: '{str(wd / 'data' / 'context' / 'x.csv')}'",
        "repr: '" + str(wd / "tmp" / "y.txt").replace("\\", "\\\\") + "'",
        f"home: {Path.home() / 'Documents' / 'notes.txt'}",
        r"other: E:\elsewhere\z.txt",
        r"unc: \\server\share\f",
        r"spaces: 'E:\some folder\a b.txt' end",
        r"relative stays: 'data\\context\\fees.json' and data/context/payments.csv",
        "not a path: 3:4 ratio, http://example.com/x",
    ])
    out = scrub_paths(text, wd)
    assert '"<python-lib>/pandas/core/frame.py"' in out
    assert "'data/context/x.csv'" in out
    assert "'tmp/y.txt'" in out
    assert "home: <outside-path>" in out and "Documents" not in out
    assert "other: <outside-path>" in out and "elsewhere" not in out
    assert "unc: <outside-path>" in out and "server" not in out
    assert "spaces: '<outside-path>' end" in out and "folder" not in out
    assert r"'data\\context\\fees.json' and data/context/payments.csv" in out
    assert "3:4 ratio, http://example.com/x" in out
    assert not DRIVE_PATH.search(out.replace("http://", ""))


def test_similar_folder_name_is_not_treated_as_workdir(tmp_path):
    wd = tmp_path / "run1"
    other = tmp_path / "run10" / "x.txt"
    out = scrub_paths(f"see {other}", wd)
    assert "run10" not in out and "x.txt" not in out


def test_system_v1_lists_every_context_file():
    from agent.loop import system_prompt_path, system_prompt_sha256
    text = system_prompt_path("system_v1").read_text(encoding="utf-8")
    if config.CONTEXT_SOURCE.is_dir():
        names = sorted(p.name for p in config.CONTEXT_SOURCE.iterdir() if p.is_file())
        listed = sorted(re.findall(r"^- data/context/(\S+)$", text, re.MULTILINE))
        assert listed == names
    assert "manual.md" in text and "payments-readme.md" in text
    assert len(system_prompt_sha256("system_v1")) == 64
    assert system_prompt_sha256("system_v0") != system_prompt_sha256("system_v1")

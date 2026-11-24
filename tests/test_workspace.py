"""Slice b+c (D5): per-run working folder outside the repo, read-only inputs, checksums."""
import os
import stat

import pytest

from agent import config
from agent.executor import run_step
from agent.workspace import create_workspace, input_report, sha256_file, verify_inputs


@pytest.fixture
def source(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    (src / "payments.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (src / "fees.json").write_text('{"x": 1}', encoding="utf-8")
    return src


@pytest.fixture
def ws(tmp_path, source):
    return create_workspace("run-1", work_root=tmp_path / "work", source=source)


def test_layout_and_copies(ws, source):
    assert ws.root.name == "run-1"
    assert ws.data_dir == ws.root / "data" / "context"
    assert ws.tmp_dir.is_dir()
    assert sorted(p.name for p in ws.data_dir.iterdir()) == ["fees.json", "payments.csv"]
    for name in ("fees.json", "payments.csv"):
        assert sha256_file(ws.data_dir / name) == sha256_file(source / name)
    assert set(ws.checksums) == {"data/context/fees.json", "data/context/payments.csv"}


def test_only_inputs_are_copied_no_answers(ws):
    files = [p for p in ws.root.rglob("*") if p.is_file()]
    assert all(p.parent == ws.data_dir for p in files)
    for p in files:
        assert "dev_tasks" not in p.name
        assert '"answer"' not in p.read_text(encoding="utf-8")


def test_inputs_are_read_only(ws):
    for p in ws.data_dir.iterdir():
        assert not os.stat(p).st_mode & stat.S_IWRITE


def test_existing_run_id_is_refused(tmp_path, source, ws):
    with pytest.raises(FileExistsError):
        create_workspace("run-1", work_root=tmp_path / "work", source=source)


@pytest.mark.parametrize("bad", ["../x", "a/b", "a\\b", "", ".hidden", "C:x", "a b"])
def test_unsafe_run_id_is_refused(tmp_path, source, bad):
    with pytest.raises(ValueError):
        create_workspace(bad, work_root=tmp_path / "work", source=source)


def test_work_root_inside_repo_is_refused(source):
    with pytest.raises(ValueError, match="inside the repository"):
        create_workspace("run-x", work_root=config.REPO_ROOT / "runs" / "work", source=source)
    assert not (config.REPO_ROOT / "runs" / "work" / "run-x").exists()


def test_unchanged_inputs_are_not_flagged(ws):
    run_step([], "print(open('data/context/payments.csv').read())", ws.root)
    report = input_report(ws)
    assert report["flagged"] is False and report["input_changes"] == []


def test_child_write_to_input_fails(ws):
    r = run_step([], "open('data/context/payments.csv', 'a').write('x')", ws.root)
    assert not r.ok and "PermissionError" in r.stderr
    assert verify_inputs(ws) == []


def test_forced_modification_is_detected_and_flags_run(ws):
    code = (
        "import os, stat\n"
        "p = 'data/context/payments.csv'\n"
        "os.chmod(p, stat.S_IWRITE | stat.S_IREAD)\n"
        "open(p, 'a').write('tampered')\n"
    )
    assert run_step([], code, ws.root).ok
    report = input_report(ws)
    assert report["flagged"] is True and report["flag_reasons"] == ["input_changed"]
    assert report["input_changes"] == [{"path": "data/context/payments.csv", "change": "modified"}]


def test_deleted_and_added_inputs_are_detected(ws):
    code = (
        "import os, stat\n"
        "p = 'data/context/fees.json'\n"
        "os.chmod(p, stat.S_IWRITE | stat.S_IREAD)\n"
        "os.remove(p)\n"
        "open('data/context/new.csv', 'w').write('x')\n"
    )
    assert run_step([], code, ws.root).ok
    assert verify_inputs(ws) == [
        {"path": "data/context/fees.json", "change": "missing"},
        {"path": "data/context/new.csv", "change": "added"},
    ]


def test_scratch_files_outside_data_are_not_flagged(ws):
    assert run_step([], "open('out.txt', 'w').write('ok')", ws.root).ok
    assert verify_inputs(ws) == []

"""Slice a (D5): the child process gets a strict environment allowlist."""
import json
import re

from agent.executor import ENV_ALLOWED, run_step

SECRET_LIKE = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH", re.IGNORECASE)


def _child_env(tmp_path):
    r = run_step([], "import os, json\nprint(json.dumps(sorted(os.environ)))", tmp_path)
    assert r.ok, r.stderr
    return json.loads(r.stdout)


def test_secrets_in_parent_do_not_reach_child(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "should-not-leak")
    monkeypatch.setenv("HF_TOKEN", "should-not-leak")
    monkeypatch.setenv("MY_SECRET", "should-not-leak")
    names = _child_env(tmp_path)
    assert not [n for n in names if SECRET_LIKE.search(n)]
    r = run_step([], "import os\nprint(os.environ.get('MODEL_API_KEY'))", tmp_path)
    assert r.stdout == "None\n"


def test_child_env_is_subset_of_allowlist(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "C:\\somewhere")
    monkeypatch.setenv("USERPROFILE", "C:\\Users\\someone")
    names = {n.upper() for n in _child_env(tmp_path)}
    assert names <= {n.upper() for n in ENV_ALLOWED}


def test_temp_points_inside_workdir(tmp_path):
    r = run_step([], "import tempfile\nprint(tempfile.gettempdir())", tmp_path)
    assert r.ok, r.stderr
    assert r.stdout.strip().lower() == str(tmp_path / "tmp").lower()


def test_pandas_and_numpy_work_under_allowlist(tmp_path):
    (tmp_path / "t.csv").write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    r = run_step([], "import numpy as np, pandas as pd\n"
                     "print(int(pd.read_csv('t.csv')['b'].sum()), np.arange(3).sum())", tmp_path)
    assert r.ok, r.stderr
    assert r.stdout == "6 3\n"


def test_planted_module_in_workdir_is_not_imported(tmp_path):
    # Without -P, this json.py would replace the json module the runner itself uses.
    (tmp_path / "json.py").write_text("raise RuntimeError('planted module ran')", encoding="utf-8")
    (tmp_path / "pandas.py").write_text("raise RuntimeError('planted module ran')", encoding="utf-8")
    r = run_step([], "import pandas\nprint(pandas.__name__)", tmp_path)
    assert r.ok, r.stderr
    assert "planted" not in r.stderr


def test_user_site_is_disabled(tmp_path):
    r = run_step([], "import site, sys\nprint(site.ENABLE_USER_SITE, sys.flags.no_user_site)", tmp_path)
    assert r.ok, r.stderr
    assert r.stdout == "False 1\n"

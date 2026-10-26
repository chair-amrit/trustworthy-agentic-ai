import pytest

from agent.executor import ExecResult, PriorStepError, format_observation, run_step


def test_simple_print(tmp_path):
    r = run_step([], "print(1 + 1)", tmp_path)
    assert r.ok and r.stdout == "2\n"


def test_state_carries_over_from_prior_blocks(tmp_path):
    r = run_step(["import math\nx = math.sqrt(16)"], "print(x)", tmp_path)
    assert r.stdout == "4.0\n"


def test_prior_output_is_not_in_observation(tmp_path):
    r = run_step(["print('hidden')"], "print('shown')", tmp_path)
    assert r.stdout == "shown\n"


def test_runtime_error_and_clean_traceback(tmp_path):
    r = run_step([], "x = 1\n1/0", tmp_path)
    assert not r.ok and r.returncode == 1
    assert "ZeroDivisionError" in r.stderr
    assert "<current step>" in r.stderr
    assert "<string>" not in r.stderr


def test_syntax_error(tmp_path):
    r = run_step([], "def (", tmp_path)
    assert not r.ok and "SyntaxError" in r.stderr


def test_timeout(tmp_path):
    r = run_step([], "import time\ntime.sleep(5)", tmp_path, timeout_s=1)
    assert r.timed_out and not r.ok
    assert r.stdout == "" and "TimeoutError" in r.stderr


def test_truncation(tmp_path):
    r = run_step([], "print('a' * 5000)", tmp_path, max_chars=100)
    assert r.stdout == "a" * 100
    assert r.truncated and r.stdout_len == 5001


def test_unicode_output(tmp_path):
    r = run_step([], "print('h\u00e9llo \u20b9')", tmp_path)
    assert r.stdout == "h\u00e9llo \u20b9\n"


def test_relative_paths_use_workdir(tmp_path):
    (tmp_path / "data.txt").write_text("hello", encoding="utf-8")
    r = run_step([], "print(open('data.txt').read())", tmp_path)
    assert r.stdout == "hello\n"


def test_input_does_not_hang(tmp_path):
    r = run_step([], "input()", tmp_path)
    assert not r.ok and "EOFError" in r.stderr


def test_hash_seed_is_fixed(tmp_path):
    a = run_step([], "print(hash('abc'))", tmp_path)
    b = run_step([], "print(hash('abc'))", tmp_path)
    assert a.stdout == b.stdout


def test_same_inputs_same_result(tmp_path):
    a = run_step(["v = 3"], "print(v * 2)", tmp_path)
    b = run_step(["v = 3"], "print(v * 2)", tmp_path)
    assert a == b


def test_failed_prior_block_raises(tmp_path):
    with pytest.raises(PriorStepError):
        run_step(["raise ValueError('boom')"], "print(1)", tmp_path)


def test_format_observation_variants():
    assert format_observation(ExecResult("42\n", "", 0, False, False, 3)) == "Observation:\n42"
    assert format_observation(ExecResult("a\n", "err\n", 1, False, False, 2)) == (
        "Observation:\nExecution failed (return code 1).\na\nerr"
    )
    assert format_observation(ExecResult("", "", 0, False, False, 0)) == "Observation:\n(no output)"
    assert format_observation(ExecResult("x", "", 0, False, True, 9)).endswith("[output truncated]")


def test_failed_execution_without_output_is_not_success_no_output():
    failed = format_observation(ExecResult("", "", 1, False, False, 0))
    succeeded = format_observation(ExecResult("", "", 0, False, False, 0))
    assert failed == "Observation:\nExecution failed (return code 1).\n(no output)"
    assert failed != succeeded


def test_timeout_is_explicit_in_observation():
    assert format_observation(ExecResult("", "", -1, True, False, 0)) == (
        "Observation:\nExecution timed out.\n(no output)"
    )

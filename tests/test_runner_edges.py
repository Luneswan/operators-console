"""The grader against what learners really write (2026-09-22 edge-case sweep).

Each of these failed before the fix it pins: output after the answer made a
pass unreadable, a lingering thread made it a timeout, a json.py in the
workspace broke every later run, tracebacks opened with the grader's code, a
pasted BOM was a syntax error, a frozen Pool worker opened a second app,
Windows had no memory cap, a deep recursion's traceback took longer to format
than the run was allowed, and output written past the capture was held whole
by the app.
"""
from __future__ import annotations

import sys

import pytest

from operators_console.core import runner
from operators_console.core.models import TestCase as Case
from operators_console.core.runner import run_exercise

VALUE = [Case("value is set", "assert value == 1")]


# ---------------------------------------------------------------------------
# Nothing written after the answer can spoil it
# ---------------------------------------------------------------------------

def test_a_class_with_a_printing_destructor_is_graded_normally():
    """OOP lessons demo __del__ with a print; it ran at shutdown, after the
    answer, and made the whole answer unreadable."""
    code = (
        "class Resource:\n"
        "    def __init__(self, name):\n"
        "        self.name = name\n"
        "    def __del__(self):\n"
        "        print('released', self.name)\n"
        "\n"
        "r = Resource('db')\n"
        "value = 1\n")
    result = run_exercise(code, VALUE, timeout=20)
    assert result.ok, result.summary


def test_an_atexit_handler_that_prints_is_graded_normally():
    code = "import atexit\natexit.register(print, 'bye')\nvalue = 1\n"
    result = run_exercise(code, VALUE, timeout=20)
    assert result.ok, result.summary


def test_a_thread_that_prints_after_the_checks_is_graded_normally():
    code = (
        "import threading, time\n"
        "def worker():\n"
        "    time.sleep(0.3)\n"
        "    print('late')\n"
        "threading.Thread(target=worker).start()\n"
        "value = 1\n")
    result = run_exercise(code, VALUE, timeout=20)
    assert result.ok, result.summary


def test_a_lingering_thread_does_not_turn_a_pass_into_a_timeout():
    code = (
        "import threading, time\n"
        "def spin():\n"
        "    while True:\n"
        "        time.sleep(0.05)\n"
        "threading.Thread(target=spin).start()\n"
        "value = 1\n")
    result = run_exercise(code, VALUE, timeout=5)
    assert not result.timed_out, result.summary
    assert result.ok


# ---------------------------------------------------------------------------
# The workspace cannot shadow the standard library
# ---------------------------------------------------------------------------

@pytest.mark.skipif(getattr(sys, "frozen", False),
                    reason="frozen builds never put the cwd on sys.path")
def test_a_file_the_learner_wrote_cannot_break_every_later_run():
    first = run_exercise("open('json.py', 'w').write('')\nvalue = 1\n",
                         VALUE, timeout=20)
    assert first.ok
    later = run_exercise("value = 1\n", VALUE, timeout=20)
    assert later.ok, later.summary


# ---------------------------------------------------------------------------
# Errors show the learner's code, and only theirs
# ---------------------------------------------------------------------------

def test_a_runtime_error_shows_only_the_learners_code():
    result = run_exercise("value = 1\n1/0\n", VALUE, timeout=20)
    assert "ZeroDivisionError" in result.error
    assert "exec(compile" not in result.error, result.error
    assert 'File "your_code.py", line 2' in result.error


def test_a_syntax_error_shows_only_the_learners_code():
    result = run_exercise("def f(:\n    pass\n", VALUE, timeout=20)
    assert "SyntaxError" in result.error
    assert "exec(compile" not in result.error, result.error


def test_a_chained_exception_shows_both_errors():
    code = ("try:\n    {}['k']\nexcept KeyError as exc:\n"
            "    raise ValueError('bad key') from exc\n")
    result = run_exercise(code, VALUE, timeout=20)
    assert "KeyError" in result.error
    assert "direct cause" in result.error
    assert result.summary == "ValueError: bad key"


def test_deep_recursion_after_raising_the_limit_is_not_called_a_timeout():
    """sys.setrecursionlimit(10**6) is the stock fix learners find. Formatting
    a million-frame traceback used to take longer than the timeout."""
    code = ("import sys\nsys.setrecursionlimit(10**6)\n"
            "def f(n):\n    return f(n + 1)\nf(0)\n")
    result = run_exercise(code, VALUE, timeout=10)
    assert not result.timed_out, result.summary
    assert "RecursionError" in result.summary
    assert "more calls like these" in result.error
    assert result.error.count('File "your_code.py"') <= (
        runner.TRACE_FIRST + runner.TRACE_LAST + 1)


def test_a_byte_order_mark_at_the_start_of_pasted_code_is_harmless():
    result = run_exercise("﻿value = 1\n", VALUE, timeout=20)
    assert result.ok, result.summary


# ---------------------------------------------------------------------------
# Process pools
# ---------------------------------------------------------------------------

def test_the_frozen_entry_point_does_not_launch_the_gui_for_a_worker(
        monkeypatch):
    """A frozen Pool worker is this executable with --multiprocessing-fork;
    without freeze_support() it opened a second copy of the app."""
    import operators_console.__main__ as entry
    import operators_console.app as app_module

    launched = []
    monkeypatch.setattr(app_module, "run",
                        lambda argv=None: launched.append(argv) or 0)
    worker_argv = ["--multiprocessing-fork", "parent_pid=1", "pipe_handle=2"]
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "argv", ["operators-console.exe"] + worker_argv)
    monkeypatch.setattr("multiprocessing.spawn.spawn_main",
                        lambda *a, **k: None, raising=False)
    try:
        entry.main(worker_argv)
    except SystemExit:
        pass
    assert not launched, "a worker process started the GUI"


def test_a_process_pool_failure_explains_itself():
    """Workers cannot import code that only exists in the editor. Making it
    work would re-run the learner's top level in every worker, and no
    exercise needs a pool, so the grader says why instead.

    Where the platform starts workers by forking (Linux before 3.14), they
    inherit the code and the pool simply works - which is fine too."""
    import multiprocessing
    code = (
        "from concurrent.futures import ProcessPoolExecutor\n"
        "def square(x):\n"
        "    return x * x\n"
        "with ProcessPoolExecutor(2) as pool:\n"
        "    squares = list(pool.map(square, [1, 2, 3]))\n"
        "value = 1\n")
    result = run_exercise(code, VALUE, timeout=60)
    if multiprocessing.get_context().get_start_method() == "fork":
        assert result.ok, result.summary
        return
    assert not result.ok
    assert result.error.startswith(runner.POOL_NOTE)


# ---------------------------------------------------------------------------
# Memory and output are bounded
# ---------------------------------------------------------------------------

@pytest.mark.skipif(sys.platform != "win32", reason="POSIX has RLIMIT_AS")
def test_a_runaway_allocation_is_capped_on_windows_too():
    code = "blob = bytearray(1100 * 1024 * 1024)\nvalue = 1\n"
    result = run_exercise(code, VALUE, timeout=30)
    assert not result.ok, "a 1.1 GB allocation succeeded in the grader"
    assert "MemoryError" in (result.error + result.summary)


def test_output_written_past_the_capture_is_bounded_in_the_app(monkeypatch):
    kept = {}
    real = runner._collect

    def measure(proc, payload, timeout):
        out, err, timed_out = real(proc, payload, timeout)
        kept["chars"] = len(out)
        return out, err, timed_out
    monkeypatch.setattr(runner, "_collect", measure)
    code = ("import sys\nblock = 'x' * (1 << 20)\n"
            "for _ in range(48):\n    sys.__stdout__.write(block)\n"
            "value = 1\n")
    result = run_exercise(code, VALUE, timeout=60)
    assert result.ok, result.summary
    assert kept["chars"] <= runner.PIPE_TAIL + runner.READ_CHUNK


def test_a_print_loop_stays_small_until_the_timeout():
    result = run_exercise("while True:\n    print('x' * 1000)\n", VALUE,
                          timeout=3)
    assert result.timed_out


def test_the_capture_keeps_the_start_and_says_it_stopped():
    buffer = runner.CappedText(10)
    for _ in range(5):
        buffer.write("abcdef")
    assert buffer.getvalue() == "abcdefabcd\n... output truncated ..."


def test_a_huge_assertion_message_is_shortened():
    check = [Case("big", "assert False, 'x' * 100000")]
    result = run_exercise("value = 1\n", check, timeout=20)
    assert len(result.cases[0].message) < runner.MESSAGE_CAP + 50

"""The grader against code a student will genuinely write.

Sandboxing is out of scope - the code runs on the learner's own machine with
the learner's own permissions, which is documented in docs/AUDIT-core.md. What
is in scope is that nothing a student writes can hang the application or cost
them the text in their editor.
"""
from __future__ import annotations

import io

import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

from operators_console.core import paths
from operators_console.core.runner import run_exercise


@dataclass(frozen=True)
class Case:
    name: str
    code: str


PASS = [Case("check", "assert True")]


def test_a_runaway_grandchild_cannot_hang_the_application(tmp_path):
    """`subprocess.Popen` in a submission used to hold the run open.

    Killing the direct child on timeout left the grandchild alive, and the
    grandchild still held the inherited stdout pipe - so the parent's own
    read blocked until the grandchild chose to exit. A student writing

        subprocess.Popen([sys.executable, "spin.py"])
        while True: pass

    hung grading for as long as the grandchild lived, twenty seconds here and
    forever with a longer-lived one.
    """
    marker = tmp_path / "grandchild.txt"
    spinner = tmp_path / "spin.py"
    spinner.write_text(
        "import time\n"
        "for i in range(60):\n"
        "    open(%r, 'a').write('tick\\n')\n"
        "    time.sleep(0.5)\n" % str(marker),
        encoding="utf-8")

    code = ("import subprocess, sys, time\n"
            "subprocess.Popen([sys.executable, %r])\n"
            "while True:\n"
            "    time.sleep(0.2)\n" % str(spinner))

    started = time.monotonic()
    result = run_exercise(code, PASS, timeout=3)
    elapsed = time.monotonic() - started

    assert result.timed_out
    # The timeout plus the grace period, not the grandchild's lifetime.
    assert elapsed < 12, "the run outlived its timeout by %.1fs" % elapsed

    # And the grandchild is not still writing.
    time.sleep(2.5)
    ticks = len(marker.read_text().splitlines()) if marker.exists() else 0
    time.sleep(2.0)
    later = len(marker.read_text().splitlines()) if marker.exists() else 0
    assert later == ticks, "the grandchild survived the kill"


def test_an_endless_loop_is_killed_within_the_timeout():
    started = time.monotonic()
    result = run_exercise("while True:\n    pass\n", PASS, timeout=2)
    assert result.timed_out
    assert time.monotonic() - started < 10
    assert "endless loop" in result.summary


def test_a_check_that_never_returns_is_killed_too():
    started = time.monotonic()
    result = run_exercise("value = 1", [Case("hang", "while True:\n    pass")],
                          timeout=2)
    assert result.timed_out
    assert time.monotonic() - started < 10


def test_an_output_bomb_does_not_reach_the_interface():
    """Printing forever must not hand the app a gigabyte of text."""
    result = run_exercise("while True:\n    print('x' * 1000)\n", PASS,
                          timeout=3)
    assert result.timed_out
    assert len(result.stdout) < 100_000


def test_a_large_but_finite_print_is_truncated():
    result = run_exercise("for _ in range(60000):\n    print('y' * 40)\n",
                          [Case("check", "assert True")], timeout=25)
    assert result.ok
    assert len(result.stdout) <= 20_100
    assert "truncated" in result.stdout


def test_unicode_survives_the_whole_round_trip():
    """Code, printed output and failure messages are all UTF-8."""
    result = run_exercise(
        "message = '你好 \U0001f600 café'\nprint(message)\n",
        [Case("check", "assert message == '你好 \U0001f600 café'")],
        timeout=20)
    assert result.ok
    assert result.stdout.strip() == "你好 \U0001f600 café"

    failing = run_exercise(
        "message = 'wrong'",
        [Case("check", "assert message == 'right', '✖ 你好'")],
        timeout=20)
    assert not failing.ok
    assert failing.cases[0].message == "✖ 你好"


def test_a_child_that_dies_without_answering_is_reported_not_swallowed():
    result = run_exercise("import os\nos._exit(3)\n", PASS, timeout=20)
    assert not result.ok
    assert not result.timed_out
    assert result.summary


def test_closing_stdout_is_a_failure_not_a_hang():
    result = run_exercise("import os\nos.close(1)\nvalue = 1\n",
                          [Case("check", "assert value")], timeout=20)
    assert not result.ok
    assert not result.timed_out


def test_student_files_land_in_the_workspace_and_nowhere_else():
    result = run_exercise(
        "import pathlib, os\n"
        "pathlib.Path('scribble.txt').write_text('hi')\n"
        "value = os.getcwd()\n",
        [Case("check", "assert value")], timeout=20)
    assert result.ok
    workspace = paths.workspace_dir()
    assert (workspace / "scribble.txt").exists()
    # The database is not a sibling of the scratch directory.
    assert not (workspace / "progress.db").exists()


def test_the_learners_database_is_not_in_the_working_directory():
    assert paths.db_path().parent != paths.workspace_dir()


def test_a_submission_printing_the_result_marker_cannot_forge_a_pass():
    """The grader takes the last marker, so a printed one is just output."""
    from operators_console.core.runner import RESULT_MARKER
    code = ("print(%r + '{\"ok\": true, \"cases\": [{\"name\": \"fake\", "
            "\"passed\": true}]}')\n" % RESULT_MARKER)
    result = run_exercise(code, [Case("real", "assert False, 'no'")],
                          timeout=20)
    assert not result.ok
    assert [c.name for c in result.cases] == ["real"]


def test_the_frozen_build_calls_itself_rather_than_an_interpreter(monkeypatch):
    """sys.executable is the bundle when frozen, so -m must be dropped."""
    seen = {}

    class FakeProc:
        pid = 1
        stdin, stdout, stderr = io.StringIO(), io.StringIO(), io.StringIO()

        def wait(self, timeout=None):
            return 0

    def fake_popen(argv, **kwargs):
        seen["argv"] = argv
        return FakeProc()

    monkeypatch.setattr("subprocess.Popen", fake_popen)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(Path(tempfile.gettempdir())
                                               / "operators-console.exe"),
                        raising=False)
    run_exercise("value = 1", PASS, timeout=5)
    assert "-m" not in seen["argv"]
    assert seen["argv"][0].endswith("operators-console.exe")


def test_running_from_source_passes_the_module(monkeypatch):
    seen = {}

    class FakeProc:
        pid = 1
        stdin, stdout, stderr = io.StringIO(), io.StringIO(), io.StringIO()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr("subprocess.Popen",
                        lambda argv, **kw: (seen.update(argv=argv), FakeProc())[1])
    monkeypatch.delattr(sys, "frozen", raising=False)
    run_exercise("value = 1", PASS, timeout=5)
    # -P keeps the workspace off sys.path (a learner's json.py once shadowed
    # the standard library for every later run).
    assert seen["argv"][1:4] == ["-P", "-m", "operators_console"]


@pytest.mark.parametrize("timeout", [0, -1])
def test_a_nonsense_timeout_fails_fast_instead_of_hanging(timeout):
    result = run_exercise("value = 1", PASS, timeout=timeout)
    assert result.timed_out or not result.ok

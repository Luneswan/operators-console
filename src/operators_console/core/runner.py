"""Running the learner's code and grading it.

Exercises are graded by executing the submitted code in a separate process and
then running each test case against the namespace it produced. A separate
process is what makes the feature safe to use for hours: an endless loop, a
sys.exit, a crash inside a C extension or a runaway allocation kills the child
and leaves the application untouched.

The child is this same program relaunched with --exercise-runner. That works
identically whether the app runs from source or from a frozen one-file build,
where sys.executable is the bundle rather than a Python interpreter.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass

from . import paths

RUNNER_FLAG = "--exercise-runner"
RESULT_MARKER = "\n<<<OPCON-RESULT>>>"
SUBMISSION_FILE = "your_code.py"
SUBMISSION_MODULE = "your_code"
DEFAULT_TIMEOUT = 10


@dataclass(frozen=True, slots=True)
class CaseResult:
    name: str
    passed: bool
    message: str = ""


@dataclass(frozen=True, slots=True)
class RunResult:
    ok: bool
    cases: tuple = ()
    stdout: str = ""
    error: str = ""
    timed_out: bool = False
    duration_ms: int = 0

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.cases if c.passed)

    @property
    def total_count(self) -> int:
        return len(self.cases)

    @property
    def summary(self) -> str:
        if self.timed_out:
            return "Timed out - is there an endless loop?"
        if self.error and not self.cases:
            lines = [l for l in self.error.strip().splitlines() if l.strip()]
            return lines[-1] if lines else "Failed to run"
        return "%d of %d checks passed" % (self.passed_count, self.total_count)


def _payload(code: str, setup: str, tests) -> str:
    return json.dumps({
        "code": code,
        "setup": setup,
        "tests": [{"name": t.name, "code": t.code} for t in tests],
    })


def run_exercise(code: str, tests, setup: str = "",
                 timeout: int = DEFAULT_TIMEOUT) -> RunResult:
    """Execute code, then grade it against tests."""
    frozen = bool(getattr(sys, "frozen", False))
    argv = [sys.executable]
    if not frozen:
        argv += ["-m", "operators_console"]
    argv.append(RUNNER_FLAG)

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OPERATORS_CONSOLE_CHILD"] = "1"
    if not frozen:
        src_root = str(paths.bundled_data_dir().parent.parent)
        prior = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = src_root + os.pathsep + prior if prior else src_root

    flags = 0
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    started = time.monotonic()
    try:
        proc = subprocess.run(
            argv, input=_payload(code, setup, tests), capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout,
            cwd=str(paths.workspace_dir()), env=env, creationflags=flags)
    except subprocess.TimeoutExpired:
        return RunResult(
            ok=False, timed_out=True,
            duration_ms=int((time.monotonic() - started) * 1000),
            error="Execution exceeded %d seconds." % timeout)
    except OSError as exc:
        return RunResult(ok=False, error="Could not start the runner: %s" % exc)

    elapsed = int((time.monotonic() - started) * 1000)
    raw = proc.stdout or ""
    marker = raw.rfind(RESULT_MARKER)
    if marker == -1:
        detail = (proc.stderr or raw or "The runner produced no output.").strip()
        return RunResult(ok=False, duration_ms=elapsed, error=detail)

    try:
        result = json.loads(raw[marker + len(RESULT_MARKER):])
    except json.JSONDecodeError:
        return RunResult(ok=False, duration_ms=elapsed,
                         error="The runner returned unreadable output.")

    cases = tuple(CaseResult(c["name"], c["passed"], c.get("message", ""))
                  for c in result.get("cases", []))
    return RunResult(ok=bool(result.get("ok")), cases=cases,
                     stdout=result.get("stdout", ""),
                     error=result.get("error", ""), duration_ms=elapsed)


# ---------------------------------------------------------------------------
# child process
# ---------------------------------------------------------------------------

def child_main() -> int:
    """Entry point for the grader subprocess. Never runs in the GUI process."""
    import contextlib
    import io
    import traceback

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.stdout.write(RESULT_MARKER + json.dumps(
            {"ok": False, "cases": [], "stdout": "",
             "error": "The grader received no work to do."}))
        return 1

    _limit_resources()

    code = payload.get("code") or ""
    module = _prepare_module(code)
    namespace = module.__dict__
    buffer = io.StringIO()
    error = ""
    ok = True

    setup = payload.get("setup") or ""
    if setup:
        try:
            exec(compile(setup, "<setup>", "exec"), namespace)
        except Exception:
            error = "Exercise setup failed:\n" + traceback.format_exc()
            ok = False

    if ok:
        try:
            with contextlib.redirect_stdout(buffer), \
                    contextlib.redirect_stderr(buffer):
                exec(compile(code, SUBMISSION_FILE, "exec"), namespace)
        except SystemExit:
            pass
        except BaseException:
            ok = False
            error = _clean_traceback(traceback.format_exc())

    cases = []
    if ok:
        for test in payload.get("tests") or []:
            name = test.get("name", "check")
            try:
                with contextlib.redirect_stdout(buffer), \
                        contextlib.redirect_stderr(buffer):
                    # Each check gets its own binding map, so a name it
                    # creates cannot leak into the next one. Objects are
                    # shared rather than copied: some exercises deliberately
                    # build a database connection or a counter in setup and
                    # expect every check to see the same one.
                    exec(compile(test.get("code", ""), "<check>", "exec"),
                         dict(namespace))
                cases.append({"name": name, "passed": True, "message": ""})
            except AssertionError as exc:
                ok = False
                cases.append({"name": name, "passed": False,
                              "message": str(exc) or "Wrong result."})
            except BaseException as exc:
                ok = False
                cases.append({"name": name, "passed": False,
                              "message": "%s: %s" % (type(exc).__name__, exc)})

    output = buffer.getvalue()
    if len(output) > 20000:
        output = output[:20000] + "\n... output truncated ..."

    sys.stdout.write(RESULT_MARKER + json.dumps({
        "ok": ok and bool(cases),
        "cases": cases,
        "stdout": output,
        "error": error,
    }))
    sys.stdout.flush()
    return 0


def _prepare_module(code: str):
    """Give the submission a real module identity.

    Two things need it. `inspect.getsource` reads through `linecache`, so
    without a cache entry every check that inspects the learner's own code
    fails with OSError. And `dataclasses` looks the defining module up in
    `sys.modules` when it resolves annotations, so a namespace that belongs to
    no module raises AttributeError on `@dataclass`.
    """
    import linecache
    import types

    module = types.ModuleType(SUBMISSION_MODULE)
    module.__file__ = SUBMISSION_FILE
    sys.modules[SUBMISSION_MODULE] = module

    lines = code.splitlines(keepends=True)
    linecache.cache[SUBMISSION_FILE] = (
        len(code), None, lines, SUBMISSION_FILE)
    return module


def _clean_traceback(text: str) -> str:
    """Hide the grader frames so the learner sees only their own code."""
    marker = 'File "' + SUBMISSION_FILE + '"'
    lines = text.splitlines()
    keep = []
    started = False
    for line in lines:
        if marker in line:
            started = True
        if started or not line.lstrip().startswith("File "):
            keep.append(line)
    body = "\n".join(keep) if keep else text
    return body.replace("Traceback (most recent call last):\n", "").strip()


def _limit_resources() -> None:
    """Best-effort guard rails. POSIX only; Windows relies on the timeout."""
    try:
        import resource
    except ImportError:
        return
    for name, soft in (("RLIMIT_AS", 1024 ** 3), ("RLIMIT_CPU", 15)):
        limit = getattr(resource, name, None)
        if limit is None:
            continue
        try:
            resource.setrlimit(limit, (soft, soft))
        except (ValueError, OSError):
            pass

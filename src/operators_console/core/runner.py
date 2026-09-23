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

import ast
import collections
import io
import json
import math
import os
import reprlib
import subprocess
import sys
import threading
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
    #: The values behind `message`, on their own lines under it. Kept apart
    #: so the list line beside the check name stays one sentence long.
    detail: str = ""


@dataclass(frozen=True, slots=True)
class RunResult:
    ok: bool
    cases: tuple = ()
    stdout: str = ""
    error: str = ""
    timed_out: bool = False
    duration_ms: int = 0
    cancelled: bool = False

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.cases if c.passed)

    @property
    def total_count(self) -> int:
        return len(self.cases)

    @property
    def summary(self) -> str:
        if self.cancelled:
            return "Stopped."
        if self.timed_out:
            return "Timed out - is there an endless loop?"
        if self.error and not self.cases:
            lines = [x for x in self.error.strip().splitlines() if x.strip()]
            return lines[-1] if lines else "Failed to run"
        return "%d of %d checks passed" % (self.passed_count, self.total_count)


class RunHandle:
    """A way to stop a run that is already under way.

    The learner presses Stop; the grader is a whole process tree by then
    (a submission is free to start processes of its own), so the cancel has
    to reach the same killer the timeout uses. A cancel that arrives before
    the process exists is remembered and applied the moment it does, which
    is the race a plain `proc.kill()` on a shared attribute always lost.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proc = None
        self.cancelled = False

    def attach(self, proc) -> bool:
        """Hand the handle the live process. False if Stop already came."""
        with self._lock:
            if not self.cancelled:
                self._proc = proc
                return True
        _kill_tree(proc)
        return False

    def cancel(self) -> None:
        with self._lock:
            self.cancelled = True
            proc = self._proc
        if proc is not None:
            _kill_tree(proc)


def _payload(code: str, setup: str, tests) -> str:
    return json.dumps({
        "code": code,
        "setup": setup,
        "tests": [{"name": t.name, "code": t.code} for t in tests],
    })


def run_exercise(code: str, tests, setup: str = "",
                 timeout: int = DEFAULT_TIMEOUT,
                 handle: "RunHandle | None" = None) -> RunResult:
    """Execute code, then grade it against tests.

    `handle` is optional; pass a `RunHandle` to be able to stop the run.
    """
    frozen = bool(getattr(sys, "frozen", False))
    argv = [sys.executable]
    if not frozen:
        # -P: the workspace is the child's working directory, and without it
        # a json.py the learner once saved there would shadow the standard
        # library for every later run. (A frozen build never adds the cwd.)
        argv += ["-P", "-m", "operators_console"]
    argv.append(RUNNER_FLAG)

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OPERATORS_CONSOLE_CHILD"] = "1"
    if not frozen:
        src_root = str(paths.bundled_data_dir().parent.parent)
        prior = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = src_root + os.pathsep + prior if prior else src_root

    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    else:
        # Its own session, so the whole tree can be signalled at once.
        kwargs["start_new_session"] = True

    started = time.monotonic()
    try:
        proc = subprocess.Popen(
            argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            errors="replace", cwd=str(paths.workspace_dir()), env=env,
            **kwargs)
    except OSError as exc:
        return RunResult(ok=False, error="Could not start the runner: %s" % exc)

    if handle is not None:
        handle.attach(proc)

    out, err, timed_out = _collect(proc, _payload(code, setup, tests),
                                   timeout)

    elapsed = int((time.monotonic() - started) * 1000)
    if handle is not None and handle.cancelled:
        # Stop wins over every other reading: the child was killed part way
        # through, so whatever it managed to say is not a verdict.
        return RunResult(ok=False, cancelled=True, duration_ms=elapsed,
                         error="Stopped.")
    if timed_out:
        return RunResult(
            ok=False, timed_out=True, duration_ms=elapsed,
            error="Execution exceeded %d seconds." % timeout)

    raw = out or ""
    marker = raw.rfind(RESULT_MARKER)
    if marker == -1:
        detail = (err or raw or "The runner produced no output.").strip()
        return RunResult(ok=False, duration_ms=elapsed, error=detail)

    try:
        # raw_decode, not loads: anything that still reached stdout after the
        # answer (a thread, a destructor) must not make the answer unreadable.
        result, _end = json.JSONDecoder().raw_decode(
            raw, marker + len(RESULT_MARKER))
    except json.JSONDecodeError:
        return RunResult(ok=False, duration_ms=elapsed,
                         error="The runner returned unreadable output.")

    cases = tuple(CaseResult(c["name"], c["passed"], c.get("message", ""),
                             c.get("detail", ""))
                  for c in result.get("cases", []))
    return RunResult(ok=bool(result.get("ok")), cases=cases,
                     stdout=result.get("stdout", ""),
                     error=result.get("error", ""), duration_ms=elapsed)


GRACE_SECONDS = 3.0


def _kill_tree(proc) -> None:
    """Kill the grader and everything it started.

    Killing only the direct child is not enough. A submission that calls
    subprocess.Popen leaves a grandchild that keeps running and, worse, keeps
    the inherited stdout pipe open - so the parent's own read blocks until
    that grandchild decides to finish. A student who writes

        while True:
            subprocess.Popen([sys.executable, "spin.py"])

    would otherwise hang the app for as long as the grandchildren live.
    """
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=GRACE_SECONDS)
            return
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return
        except (OSError, ProcessLookupError):
            pass
    try:
        proc.kill()
    except OSError:
        pass


# The answer is the last thing the child writes, so stdout keeps its tail;
# stderr keeps its head, where the reason a run failed to start is.
PIPE_TAIL = 4 * 1024 * 1024
PIPE_HEAD = 64 * 1024
READ_CHUNK = 64 * 1024


def _collect(proc, payload: str, timeout: float):
    """Feed the child, read what it says within bounds, and wait for it.

    communicate() keeps everything, and a submission can write straight to
    the real stdout (sys.__stdout__, os.write) past the print capture, which
    would hand this process as much text as it cares to produce. Readers
    that keep only a bounded tail or head make that harmless.
    Returns (stdout, stderr, timed_out).
    """
    out, err = collections.deque(), []
    readers = [threading.Thread(target=_keep_tail, args=(proc.stdout, out),
                                daemon=True),
               threading.Thread(target=_keep_head, args=(proc.stderr, err),
                                daemon=True)]
    feeder = threading.Thread(target=_feed, args=(proc.stdin, payload),
                              daemon=True)
    for thread in (*readers, feeder):
        thread.start()

    timed_out = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_tree(proc)
        try:
            proc.wait(timeout=GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    for thread in readers:
        thread.join(GRACE_SECONDS)
    if any(thread.is_alive() for thread in readers):
        # Something detached itself far enough to survive the child and is
        # still holding the pipe. Let go of our end rather than block the
        # learner; whatever was read already is kept.
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            try:
                if stream is not None:
                    stream.close()
            except (OSError, ValueError):
                pass
    if timed_out:
        return "", "", True
    return "".join(out), "".join(err), False


def _feed(stream, payload: str) -> None:
    try:
        stream.write(payload)
        stream.close()
    except (OSError, ValueError):
        pass                    # the child died before reading it


def _keep_tail(stream, sink) -> None:
    kept = 0
    try:
        while True:
            chunk = stream.read(READ_CHUNK)
            if not chunk:
                return
            sink.append(chunk)
            kept += len(chunk)
            while len(sink) > 1 and kept - len(sink[0]) >= PIPE_TAIL:
                kept -= len(sink.popleft())
    except (OSError, ValueError):
        pass


def _keep_head(stream, sink) -> None:
    kept = 0
    try:
        while True:
            chunk = stream.read(READ_CHUNK)
            if not chunk:
                return
            if kept < PIPE_HEAD:
                sink.append(chunk[:PIPE_HEAD - kept])
                kept += len(sink[-1])
    except (OSError, ValueError):
        pass


# ---------------------------------------------------------------------------
# child process
# ---------------------------------------------------------------------------

def child_main() -> int:
    """Entry point for the grader subprocess. Never runs in the GUI process."""
    import contextlib
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
    if code.startswith("\ufeff"):        # pasted from an editor that adds one
        code = code[1:]
    module = _prepare_module(code)
    namespace = module.__dict__
    buffer = CappedText(OUTPUT_CAP)
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
        except BaseException as exc:
            ok = False
            error = _learner_traceback(exc)

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
                    exec(compile(test.get("code", ""), CHECK_FILE, "exec"),
                         dict(namespace))
                cases.append({"name": name, "passed": True, "message": "",
                              "detail": ""})
            except AssertionError as exc:
                ok = False
                # Under the capture: working out why the check failed
                # re-runs part of it, and anything that prints while it does
                # belongs in the learner's output, not behind the answer.
                with contextlib.redirect_stdout(buffer), \
                        contextlib.redirect_stderr(buffer):
                    said = explain_assertion(test.get("code", ""), exc)
                cases.append(_case(name, said))
            except BaseException as exc:
                ok = False
                with contextlib.redirect_stdout(buffer), \
                        contextlib.redirect_stderr(buffer):
                    said = explain_error(exc)
                cases.append(_case(name, said))

    output = buffer.getvalue()

    # sys.__stdout__, not sys.stdout: the submission may have replaced it.
    # The caller exits straight after this, before any destructor, atexit
    # hook or lingering thread gets a chance to write behind the answer.
    answer = sys.__stdout__ or sys.stdout
    answer.write(RESULT_MARKER + json.dumps({
        "ok": ok and bool(cases),
        "cases": cases,
        "stdout": output,
        "error": _explain(error),
    }))
    answer.flush()
    return 0


def exit_now(code: int) -> None:
    """Leave the grader without running interpreter shutdown.

    Shutdown runs the submission's __del__ methods and atexit hooks and joins
    its threads. Their output would land behind the answer, and a thread that
    never ends would turn a pass into a timeout.
    """
    for stream in (sys.__stdout__, sys.__stderr__):
        try:
            if stream is not None:
                stream.flush()
        except (OSError, ValueError):
            pass
    os._exit(code)


OUTPUT_CAP = 20000
MESSAGE_CAP = 2000


class CappedText(io.TextIOBase):
    """Where the submission's prints go: the first 20,000 characters kept.

    A StringIO kept everything, so a print loop grew it until the memory
    limit killed the grader in the middle of writing its answer.
    """

    def __init__(self, cap: int) -> None:
        super().__init__()
        self.cap = cap
        self.parts = []
        self.kept = 0
        self.dropped = 0

    def writable(self) -> bool:
        return True

    def write(self, text) -> int:
        text = str(text)
        room = self.cap - self.kept
        if room > 0:
            piece = text[:room]
            self.parts.append(piece)
            self.kept += len(piece)
        self.dropped += len(text) - max(0, min(room, len(text)))
        return len(text)

    def getvalue(self) -> str:
        body = "".join(self.parts)
        if self.dropped:
            body += "\n... output truncated ..."
        return body


def _short(message: str) -> str:
    if len(message) <= MESSAGE_CAP:
        return message
    return message[:MESSAGE_CAP] + " ... (shortened)"


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


TRACE_FIRST, TRACE_LAST = 3, 12

POOL_NOTE = (
    "Process pools cannot run inside the grader: their worker processes "
    "cannot see code typed into the editor. Save it as a file and run it with "
    "python in a terminal to try one.")


def _learner_traceback(exc: BaseException, depth: int = 0) -> str:
    """The error as the learner should see it: their own frames only.

    The grader's frames are dropped, and a deep recursion is cut to its first
    and last few calls. The chain is walked by hand because the standard
    formatter builds every frame first: after sys.setrecursionlimit(10**6)
    that alone took longer than the run's timeout.
    """
    import collections
    import linecache
    import traceback

    first, last = [], collections.deque(maxlen=TRACE_LAST)
    seen = 0
    tb = exc.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        if code.co_filename == SUBMISSION_FILE:
            entry = (tb.tb_lineno, code.co_name)
            if len(first) < TRACE_FIRST:
                first.append(entry)
            else:
                last.append(entry)
            seen += 1
        tb = tb.tb_next

    def frame(entry) -> str:
        lineno, name = entry
        text = '  File "%s", line %d, in %s\n' % (SUBMISSION_FILE, lineno, name)
        source = linecache.getline(SUBMISSION_FILE, lineno).strip()
        return text + ("    %s\n" % source if source else "")

    parts = [frame(entry) for entry in first]
    hidden = seen - len(first) - len(last)
    if hidden > 0:
        parts.append("  ... %d more calls like these ...\n" % hidden)
    parts += [frame(entry) for entry in last]
    parts += traceback.format_exception_only(type(exc), exc)
    body = "".join(parts)

    cause = exc.__cause__ or (None if exc.__suppress_context__
                              else exc.__context__)
    if cause is not None and depth < 3:
        link = ("The above exception was the direct cause of the following "
                "exception:" if exc.__cause__ is not None else
                "During handling of the above exception, another exception "
                "occurred:")
        body = "%s\n\n%s\n\n%s" % (_learner_traceback(cause, depth + 1),
                                    link, body)
    return body.strip()


def _explain(error: str) -> str:
    """Add the one explanation a raw error cannot give on its own."""
    if error and any(sign in error for sign in (
            "BrokenProcessPool", "Can't get attribute", "Can't pickle")):
        return POOL_NOTE + "\n\n" + error
    return error


# ---------------------------------------------------------------------------
# why a check failed
#
# A bare `assert total == 6` raises AssertionError with an empty message, so
# every failing check used to read "Wrong result." - five identical lines that
# tell a learner nothing at all. Everything below turns one of those into a
# sentence: which values were compared, how they differ, and what usually
# causes that difference. It runs in the child, where the values still exist.
#
# Nothing here may raise, print or change anything: a broken __repr__, a check
# that cannot be parsed, or a value that cannot be read a second time must all
# degrade to the plain message rather than lose the whole run.
# ---------------------------------------------------------------------------

CHECK_FILE = "<check>"
FALLBACK = "Wrong result."
VALUE_CAP = 200
#: Characters either side of the first difference in a string excerpt.
CARET_WINDOW = 24

_UNREADABLE = object()          # a value that could not be re-read
_MISSING = object()

_REPR = reprlib.Repr()
_REPR.maxlevel = 4
_REPR.maxstring = VALUE_CAP
_REPR.maxother = VALUE_CAP
_REPR.maxlong = VALUE_CAP
_REPR.maxlist = _REPR.maxtuple = _REPR.maxset = _REPR.maxfrozenset = 12
_REPR.maxdeque = _REPR.maxarray = 12
_REPR.maxdict = 8

KIND_NAMES = {
    "str": "a string", "int": "a whole number", "float": "a decimal number",
    "bool": "True or False", "list": "a list", "tuple": "a tuple",
    "dict": "a dictionary", "set": "a set", "frozenset": "a frozen set",
    "NoneType": "None", "bytes": "bytes", "range": "a range",
    "complex": "a complex number", "function": "a function",
}

PLAIN_KINDS = {"list": "list", "tuple": "tuple", "set": "set",
               "frozenset": "set", "dict": "dictionary", "str": "text"}

ORDER_WORDS = {
    ast.Lt: "less than", ast.LtE: "less than or equal to",
    ast.Gt: "greater than", ast.GtE: "greater than or equal to",
}


def _clip(text, cap: int = VALUE_CAP) -> str:
    text = str(text)
    if len(text) <= cap:
        return text
    return text[:max(0, cap - 3)] + "..."


def _show(value, cap: int = VALUE_CAP) -> str:
    """A bounded repr. Never raises and never grows with the learner's data."""
    try:
        text = _REPR.repr(value)
    except BaseException:
        try:
            text = "<a %s that cannot be shown>" % type(value).__name__
        except BaseException:
            return "<a value that cannot be shown>"
    return _clip(text, cap)


def _kind(value) -> str:
    name = type(value).__name__
    return KIND_NAMES.get(name, "a %s" % name)


def _plain_kind(value) -> str:
    name = type(value).__name__
    return PLAIN_KINDS.get(name, name)


def _listed(values, cap: int = 3) -> str:
    """'a', 'b' and 'c' - capped, so a huge difference stays one line."""
    values = list(values)
    shown = [_show(value, 60) for value in values[:cap]]
    if not shown:
        return "nothing"
    if len(shown) == 1:
        text = shown[0]
    else:
        text = "%s and %s" % (", ".join(shown[:-1]), shown[-1])
    if len(values) > cap:
        text += " and %d more" % (len(values) - cap)
    return text


def _ordered(values) -> list:
    try:
        return sorted(values)
    except TypeError:
        try:
            return sorted(values, key=repr)
        except TypeError:
            return list(values)


# -- the reason ------------------------------------------------------------


def describe_difference(expected, got) -> str:
    """Why these two values are not the same, in one plain sentence.

    The first line is always that sentence. A string comparison adds a short
    excerpt with a caret under the first character that differs. Returns ""
    when there is nothing useful to say beyond the values themselves.
    """
    try:
        return _difference(expected, got)
    except BaseException:
        return ""


def _difference(expected, got) -> str:
    if got is None and expected is not None:
        return "Your function returned None - is a `return` missing?"
    if expected is None and got is not None:
        return ("The check expects None, and your code gave back %s."
                % _show(got))
    if _bool_mix(expected, got):
        return ("True and False are not the same as 1 and 0: the check "
                "expects %s and your code gave back %s."
                % (_show(expected), _show(got)))
    if isinstance(expected, bool) and isinstance(got, bool):
        return ("The check expects %s and your code gave back %s."
                % (expected, got))
    if _numberish(expected) and _numberish(got):
        return _number_difference(expected, got)
    if type(expected) is not type(got):
        return ("You returned %s; the check expects %s."
                % (_kind(got), _kind(expected)))
    if isinstance(expected, str):
        return _text_difference(expected, got)
    if isinstance(expected, dict):
        return _mapping_difference(expected, got)
    if isinstance(expected, (set, frozenset)):
        return _set_difference(expected, got)
    if isinstance(expected, (list, tuple)):
        return _sequence_difference(expected, got)
    return ""


def _bool_mix(expected, got) -> bool:
    pair = (expected, got)
    return (all(isinstance(value, int) for value in pair)
            and any(isinstance(value, bool) for value in pair)
            and not all(isinstance(value, bool) for value in pair))


def _numberish(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number_difference(expected, got) -> str:
    try:
        close = math.isclose(got, expected, rel_tol=1e-6, abs_tol=1e-9)
    except (TypeError, ValueError, OverflowError):
        close = False
    if close:
        return ("%s is not exactly %s - that is floating point; compare with "
                "round() or math.isclose." % (_show(got), _show(expected)))
    return ("The numbers are different: the check expects %s and your code "
            "gave back %s." % (_show(expected), _show(got)))


def _text_difference(expected: str, got: str) -> str:
    if expected == got:
        return ""
    if expected.lower() == got.lower():
        return ("The letters are right but the capitals are not - check "
                "where you used upper and lower case.")
    if "".join(expected.split()) == "".join(got.split()):
        return ("The characters are right but the spacing is not - check the "
                "spaces, tabs and line breaks.")
    index = _first_difference(expected, got)
    if index >= len(got):
        return ("Your text stops early - %s is missing from the end."
                % _show(expected[index:]))
    if index >= len(expected):
        return ("Your text carries on too far - %s should not be on the end."
                % _show(got[index:]))
    sentence = ("They differ at character %d: expected %s, got %s."
                % (index + 1, _show(expected[index]), _show(got[index])))
    excerpt = _caret(expected, got, index)
    return sentence + ("\n" + excerpt if excerpt else "")


def _first_difference(expected, got) -> int:
    for index, (want, have) in enumerate(zip(expected, got, strict=False)):
        if want != have:
            return index
    return min(len(expected), len(got))


def _caret(expected: str, got: str, index: int) -> str:
    """The two strings side by side with a caret under the first difference."""
    start = max(0, index - CARET_WINDOW)
    stop = index + CARET_WINDOW
    left, right = expected[start:stop], got[start:stop]
    if any(ch in left or ch in right for ch in "\n\r\t"):
        return ""               # a caret cannot line up under a line break
    lead = "..." if start else ""
    pad = " " * (len(lead) + index - start)
    return ("  expected  %s%s\n  got       %s%s\n            %s^"
            % (lead, left, lead, right, pad))


def _mapping_difference(expected: dict, got: dict) -> str:
    missing = [key for key in expected if key not in got]
    if missing:
        return ("Your dictionary has no %s %s in it."
                % ("keys" if len(missing) > 1 else "key", _listed(missing)))
    extra = [key for key in got if key not in expected]
    if extra:
        return ("Your dictionary has %s in it that the check does not expect."
                % _listed(extra))
    for key in expected:
        if got[key] != expected[key]:
            return ("The value under %s is wrong: expected %s, got %s."
                    % (_show(key, 60), _show(expected[key], 60),
                       _show(got[key], 60)))
    return ""


def _set_difference(expected, got) -> str:
    missing = _ordered(set(expected) - set(got))
    extra = _ordered(set(got) - set(expected))
    if missing and extra:
        return ("Your set is missing %s and has %s that should not be there."
                % (_listed(missing), _listed(extra)))
    if missing:
        return "Your set is missing %s." % _listed(missing)
    if extra:
        return ("Your set has %s in it that should not be there."
                % _listed(extra))
    return ""


def _sequence_difference(expected, got) -> str:
    if len(expected) != len(got):
        return ("Your %s has %d item%s, %d %s expected."
                % (_plain_kind(got), len(got), "" if len(got) == 1 else "s",
                   len(expected), "was" if len(expected) == 1 else "were"))
    if _same_multiset(expected, got):
        return "The right values in the wrong order."
    for index, (want, have) in enumerate(zip(expected, got, strict=False)):
        if want != have:
            nested = _difference(want, have) if _both_containers(want, have) \
                else ""
            head = ("They differ at index %d: expected %s, got %s."
                    % (index, _show(want, 80), _show(have, 80)))
            return head + (" " + nested if nested else "")
    return ""


def _both_containers(want, have) -> bool:
    kinds = (list, tuple, dict, set, frozenset)
    return isinstance(want, kinds) and isinstance(have, kinds)


def _same_multiset(expected, got) -> bool:
    try:
        return collections.Counter(expected) == collections.Counter(got)
    except TypeError:
        pass
    try:
        return sorted(expected, key=repr) == sorted(got, key=repr)
    except TypeError:
        return False


# -- reading the failed assert ---------------------------------------------


def explain_assertion(test_code: str, exc: BaseException) -> str:
    """Why an `assert` inside a check failed, in the learner's terms.

    The first line is the sentence shown beside the check name; anything
    after it is detail for the lines underneath. Never raises.
    """
    author = _author_message(exc)
    try:
        reason, values, plain = _assert_parts(test_code, exc)
    except BaseException:
        reason, values, plain = "", "", ""

    lines = []
    if author:
        lines.append(author)
        if reason:
            lines.append(reason)
    elif reason:
        lines.append(reason)
    elif plain:
        lines.append(plain)
    else:
        lines.append(FALLBACK)
    if values:
        lines.append(values)
    return _short("\n".join(lines))


def _author_message(exc: BaseException) -> str:
    try:
        return str(exc).strip()
    except BaseException:
        return ""


def _assert_parts(test_code: str, exc: BaseException):
    """(reason, values, plain) read off the assert that actually failed."""
    line, column, frame = _failing_frame(exc)
    if not line or frame is None:
        return "", "", ""
    node = _assert_node(test_code, line, column)
    if node is None:
        return "", "", ""
    plain = _plain_check(node)
    test = node.test

    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        got = _try_eval(test.left, frame)
        expected = _try_eval(test.comparators[0], frame)
        if got is _UNREADABLE or expected is _UNREADABLE:
            return "", "", plain
        reason, values = _compare_parts(test.ops[0], expected, got)
        return reason, values, plain

    if (isinstance(test, ast.Call) and _called(test.func) == "isinstance"
            and len(test.args) == 2):
        value = _try_eval(test.args[0], frame)
        if value is _UNREADABLE:
            return "", "", plain
        return ("The check wants %s to be %s, and yours is %s."
                % (_code_span(test.args[0]), _code_span(test.args[1]),
                   _kind(value))), "", plain

    if isinstance(test, (ast.Name, ast.Attribute, ast.Subscript)):
        # A bare `assert result`: re-reading a name costs nothing and says
        # far more than repeating the source line does.
        value = _try_eval(test, frame)
        if value is not _UNREADABLE:
            return "", "its value was %s" % _show(value), plain
    return "", "", plain


def _compare_parts(op, expected, got):
    values = _values(expected, got)
    if isinstance(op, ast.Eq):
        return describe_difference(expected, got), values
    if isinstance(op, ast.Is):
        if expected is None:
            return ("Your code gave back %s where the check needs None "
                    "itself." % _show(got)), values
        if _looks_equal(expected, got):
            # Equal but not identical: the one case where identity is the
            # whole story. `assert f() is True` with f returning 1 is not
            # that case - it is a wrong kind of value, and says so below.
            return ("These are two separate objects - `is` asks whether they "
                    "are the same one, not whether they look alike."), values
        # `assert is_leap(1900) is False` failing because the function said
        # True is a wrong answer, not an identity problem.
        return describe_difference(expected, got), values
    if isinstance(op, ast.NotEq):
        return ("The check needs these two to be different, and they are the "
                "same."), "both were %s" % _show(got)
    if isinstance(op, ast.IsNot):
        if expected is None or isinstance(expected, bool):
            return ("The check needs something other than %s, and your code "
                    "gave back %s." % (_show(expected), _show(got))), ""
        return ("The check needs these two to be separate objects, and they "
                "are the same one."), "both were %s" % _show(got)
    if isinstance(op, ast.In):
        return ("%s is not in %s." % (_show(got), _show(expected))), ""
    if isinstance(op, ast.NotIn):
        return ("%s is in %s, and the check needs it not to be."
                % (_show(got), _show(expected))), ""
    word = ORDER_WORDS.get(type(op))
    if word:
        return ("%s is not %s %s." % (_show(got), word, _show(expected))), ""
    return "", values


def _looks_equal(expected, got) -> bool:
    """True when the two compare equal and are not a True-versus-1 mix."""
    if _bool_mix(expected, got):
        return False
    try:
        return bool(expected == got)
    except BaseException:
        return False


def _values(expected, got) -> str:
    left, right = _show(expected), _show(got)
    if "\n" in left or "\n" in right:
        return "expected:\n%s\ngot:\n%s" % (left, right)
    return "expected %s, got %s" % (left, right)


def _failing_frame(exc: BaseException):
    """The last frame inside the check, the line it stopped on, and the column.

    The column tells two asserts on one line apart (`assert a; assert b`).
    It is -1 when the interpreter cannot say.
    """
    line, column, frame = 0, -1, None
    tb = getattr(exc, "__traceback__", None)
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == CHECK_FILE:
            line, frame = tb.tb_lineno, tb.tb_frame
            column = _column(tb)
        tb = tb.tb_next
    return line, column, frame


def _column(tb) -> int:
    """Where on its line the instruction that raised starts, or -1."""
    try:
        positions = list(tb.tb_frame.f_code.co_positions())
        start_line, _end, column, _end_column = positions[tb.tb_lasti // 2]
    except BaseException:
        return -1
    if start_line != tb.tb_lineno or column is None:
        return -1
    return column


def _assert_node(test_code: str, line: int, column: int = -1):
    """The assert that failed: it spans `line` and starts at or before `column`.

    Of those, the one that starts last wins, so with two asserts on one line
    the failing one is chosen rather than the first one on the line.
    """
    tree = ast.parse(test_code, CHECK_FILE)
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        end = getattr(node, "end_lineno", None) or node.lineno
        if not node.lineno <= line <= end:
            continue
        if column >= 0 and node.lineno == line and node.col_offset > column:
            continue            # starts after the instruction that failed
        if best is None or ((node.lineno, node.col_offset)
                            > (best.lineno, best.col_offset)):
            best = node
    return best


def _try_eval(node, frame):
    """Read one operand again, in the frame the check stopped in.

    Guarded to the hilt: this re-runs the learner's own code, which is free
    to raise, exit or take a while, and none of that may lose the verdict.
    """
    try:
        expression = ast.Expression(body=node)
        ast.fix_missing_locations(expression)
        return eval(compile(expression, CHECK_FILE, "eval"),
                    frame.f_globals, frame.f_locals)
    except BaseException:
        return _UNREADABLE


def _plain_check(node) -> str:
    try:
        source = "assert " + ast.unparse(node.test)
    except BaseException:
        return ""
    return "The check `%s` was false." % _clip(source.replace("\n", " "), 120)


def _code_span(node) -> str:
    try:
        return "`%s`" % _clip(ast.unparse(node).replace("\n", " "), 60)
    except BaseException:
        return "that value"


def _called(func) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


# -- everything that is not an assert --------------------------------------


def explain_error(exc: BaseException) -> str:
    """`TypeError: ...` as before, plus a line saying what usually causes it."""
    try:
        head = "%s: %s" % (type(exc).__name__, exc)
    except BaseException:
        head = type(exc).__name__
    try:
        hint = _error_hint(exc)
    except BaseException:
        hint = ""
    return _short(head.replace("\n", " ") + ("\n" + hint if hint else ""))


def _error_hint(exc: BaseException) -> str:
    text = str(exc)
    if isinstance(exc, RecursionError):
        return ("Your function keeps calling itself and never stops - it "
                "needs a case that gives an answer without calling again.")
    if isinstance(exc, ZeroDivisionError):
        return ("Something was divided by zero - check the divisor before "
                "you use it.")
    if isinstance(exc, NameError):
        name = getattr(exc, "name", "") or _quoted(text)
        if name:
            return ("Nothing in your code defines `%s` - check the spelling, "
                    "and that it is defined before it is used." % name)
        return "That name is not defined anywhere in your code."
    if isinstance(exc, AttributeError):
        if getattr(exc, "obj", _MISSING) is None or "NoneType" in text:
            return ("You used a dot on None, so something earlier gave "
                    "nothing back - is a `return` missing?")
        name = getattr(exc, "name", "") or ""
        if name:
            return ("That object has no `%s` - check the spelling, and that "
                    "it is the kind of object you think it is." % name)
        return ""
    if isinstance(exc, IndexError):
        return ("You asked for a position that is not there - a list of 3 "
                "items has positions 0, 1 and 2.")
    if isinstance(exc, KeyError):
        key = _show(exc.args[0], 60) if exc.args else ""
        if key:
            return ("There is no %s key in that dictionary - check the "
                    "spelling, or use .get() if it might be absent." % key)
        return ""
    if isinstance(exc, TypeError):
        return _type_error_hint(text)
    if isinstance(exc, OverflowError):
        return ("A number grew too large for a float - with exponentials, "
                "subtract the largest value first so the biggest power is 0.")
    if isinstance(exc, StopIteration):
        return ("next() was called on an iterator that had nothing left - "
                "check where the loop stops, or give next() a default.")
    if isinstance(exc, ValueError):
        return _value_error_hint(text)
    return ""


def _value_error_hint(text: str) -> str:
    if "invalid literal for int()" in text:
        return ("int() was given text that is not a whole number - strip it "
                "first, or catch the ValueError if bad input is expected.")
    if "could not convert string to float" in text:
        return ("float() was given text that is not a number - strip it "
                "first, or catch the ValueError if bad input is expected.")
    if "values to unpack" in text:
        return ("The number of names on the left of = does not match the "
                "number of values on the right.")
    if ("math domain error" in text or "nonnegative input" in text
            or "positive input" in text):
        return ("A maths function was given a value it cannot take, such as "
                "the square root or logarithm of a negative number.")
    if "not in list" in text:
        return ("list.index() raises when the value is absent - test with "
                "`in` first if it might not be there.")
    return ("The value was the right type but not one the function can "
            "use - look at what was passed in.")


def _type_error_hint(text: str) -> str:
    counting = ("positional argument" in text
                or ("argument" in text
                    and ("takes" in text or "missing" in text
                         or "required" in text)))
    if counting:
        return ("The number of values passed in does not match what your "
                "function takes - count the names in your `def` line.")
    if "not callable" in text:
        return ("You used () on something that is not a function - check "
                "whether that name is holding something else.")
    if ("unsupported operand" in text or "can only concatenate" in text
            or "must be str" in text):
        return ("Those two kinds of value cannot be combined - convert one "
                "of them first, with str() or int().")
    if "not subscriptable" in text:
        return ("You used [] on something that does not hold items - check "
                "what that name is holding.")
    if "NoneType" in text:
        return ("One of the values is None, so something earlier gave "
                "nothing back - is a `return` missing?")
    if "unhashable" in text:
        return ("A list cannot be used as a dictionary key or put in a set - "
                "a tuple can.")
    return ""


def _quoted(text: str) -> str:
    start = text.find("'")
    if start == -1:
        return ""
    end = text.find("'", start + 1)
    return text[start + 1:end] if end > start else ""


def _case(name: str, said: str) -> dict:
    """Split one explanation into the list line and the detail under it."""
    head, _, rest = said.partition("\n")
    return {"name": name, "passed": False, "message": _short(head.strip()),
            "detail": _short(rest.strip())}


MEMORY_LIMIT = 1024 ** 3


def _limit_resources() -> None:
    """Best-effort guard rails: 1 GiB of memory, and on POSIX 15 s of CPU."""
    if sys.platform == "win32":
        _limit_windows_memory(MEMORY_LIMIT)
        return
    try:
        import resource
    except ImportError:
        return
    for name, soft in (("RLIMIT_AS", MEMORY_LIMIT), ("RLIMIT_CPU", 15)):
        limit = getattr(resource, name, None)
        if limit is None:
            continue
        try:
            resource.setrlimit(limit, (soft, soft))
        except (ValueError, OSError):
            pass


def _limit_windows_memory(limit: int) -> None:
    """Put the grader in a Job Object that caps each process's memory.

    Windows has no RLIMIT_AS. A job does the same and more: the learner's own
    subprocesses inherit it, and closing it - which happens when the grader
    exits - kills anything they left running.
    """
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return

    class BasicLimits(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount",
            "OtherOperationCount", "ReadTransferCount",
            "WriteTransferCount", "OtherTransferCount")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BasicLimits),
                    ("IoInfo", IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    limit_process_memory = 0x00000100
    kill_on_job_close = 0x00002000
    extended_limit_information = 9
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.AssignProcessToJobObject.argtypes = [
            wintypes.HANDLE, wintypes.HANDLE]
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return
        info = ExtendedLimits()
        info.BasicLimitInformation.LimitFlags = (limit_process_memory
                                                 | kill_on_job_close)
        info.ProcessMemoryLimit = limit
        if kernel32.SetInformationJobObject(
                job, extended_limit_information, ctypes.byref(info),
                ctypes.sizeof(info)):
            # The handle stays open for the life of the process on purpose.
            kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess())
    except (OSError, AttributeError):
        pass

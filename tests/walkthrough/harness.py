"""The net the walk runs inside.

Everything that could go wrong quietly is turned into something loud:

* every unhandled exception in a Qt slot (Qt calls ``sys.excepthook`` and
  carries on, so without this a broken handler is invisible),
* every Qt warning or critical message,
* every dialog that opens - answered automatically and recorded,
* every step that takes longer than three seconds,
* every transient top level window that appears and is not the main window,
* every URL the app tried to open (nothing is ever really opened).

The recorder is a module level singleton because ``sys.excepthook`` and the Qt
message handler are process wide and have nowhere to carry a fixture.
"""
from __future__ import annotations

import inspect
import os
import sys
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
SHOT_DIR = Path(
    os.environ.get(
        "WALK_SHOT_DIR",
        r"C:\Users\anasa\AppData\Local\Temp\claude"
        r"\C--Users-anasa-OneDrive-Desktop-random-stuff"
        r"\7578096e-ce63-4118-b841-50086d9eb836\scratchpad\console\walk"))

SLOW_STEP_MS = 3000

SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2, "polish": 3}

#: Complaints from the offscreen plugin itself, not from the application.
PLATFORM_NOISE = (
    "does not support propagateSizeHints",
    "QWindowsWindow::setGeometry",
    "This plugin does not support",
)


@dataclass
class Step:
    view: str
    action: str
    result: str
    ms: int


@dataclass
class Finding:
    id: str
    severity: str
    view: str
    title: str
    repro: str
    detail: str = ""
    screenshot: str = ""


@dataclass
class Recorder:
    steps: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    exceptions: list = field(default_factory=list)
    qt_messages: list = field(default_factory=list)
    dialogs: list = field(default_factory=list)
    urls: list = field(default_factory=list)
    hits: set = field(default_factory=set)          # (relpath, lineno)
    shortcut_hits: set = field(default_factory=set)  # key sequence text
    unreached: list = field(default_factory=list)
    counters: dict = field(default_factory=dict)
    _n: int = 0

    # -- recording ---------------------------------------------------------

    def step(self, view: str, action: str, result: str, ms: int) -> None:
        self.steps.append(Step(view, action, result, ms))

    def bump(self, key: str, by: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + by

    def find(self, severity: str, view: str, title: str, repro: str,
             detail: str = "", screenshot: str = "") -> Finding:
        """Record a defect. Duplicates of the same title collapse into one."""
        for existing in self.findings:
            if existing.title == title and existing.view == view:
                return existing
        self._n += 1
        finding = Finding("W-%02d" % self._n, severity, view, title, repro,
                          detail, screenshot)
        self.findings.append(finding)
        return finding

    def cannot_reach(self, what: str, why: str) -> None:
        self.unreached.append((what, why))

    @property
    def sorted_findings(self) -> list:
        return sorted(self.findings,
                      key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.id))


REC = Recorder()


# -- sensors ---------------------------------------------------------------


class _Sensors:
    """Installed once for the session, removed at the end."""

    def __init__(self) -> None:
        self.previous_excepthook = None
        self.previous_handler = None
        self.patched = []

    # sys.excepthook -------------------------------------------------------

    def _excepthook(self, kind, value, tb) -> None:
        text = "".join(traceback.format_exception(kind, value, tb))
        REC.exceptions.append(text)

    def install(self) -> None:
        from PySide6.QtCore import QtMsgType, qInstallMessageHandler
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtWidgets import (
            QDialog, QFileDialog, QInputDialog, QMessageBox,
        )

        self.previous_excepthook = sys.excepthook
        sys.excepthook = self._excepthook

        def handler(mode, _context, message):
            name = {QtMsgType.QtDebugMsg: "debug",
                    QtMsgType.QtInfoMsg: "info",
                    QtMsgType.QtWarningMsg: "warning",
                    QtMsgType.QtCriticalMsg: "critical",
                    QtMsgType.QtFatalMsg: "fatal"}.get(mode, str(mode))
            if name in ("warning", "critical", "fatal"):
                if any(noise in message for noise in PLATFORM_NOISE):
                    return
                REC.qt_messages.append((name, message))

        self.previous_handler = qInstallMessageHandler(handler)

        # -- the dialog auto answerer --------------------------------------
        # Every modal exec() is answered instead of blocking the walk, and
        # what appeared is written down so the report can show it.

        def patch(owner, name, replacement):
            original = getattr(owner, name)
            self.patched.append((owner, name, original))
            setattr(owner, name, replacement)
            return original

        original_dialog_exec = QDialog.exec

        def dialog_exec(dialog):
            REC.dialogs.append(("dialog", type(dialog).__name__,
                                dialog.windowTitle()))
            return QDialog.DialogCode.Accepted.value

        def messagebox_exec(box):
            REC.dialogs.append(("messagebox", box.windowTitle(), box.text()))
            buttons = box.buttons()
            if not buttons:
                return QMessageBox.StandardButton.No.value
            answer = ANSWERS.get("messagebox")
            if answer is None:
                # Left alone, always take the cautious way out.
                answer = _safe_button_index(box, buttons)
            if isinstance(answer, str):
                wanted = [b for b in buttons
                          if answer.lower() in b.text().replace("&", "").lower()]
                assert wanted, (
                    "no button named %r in %r"
                    % (answer, [b.text() for b in buttons]))
                chosen = wanted[0]
            else:
                chosen = buttons[min(answer, len(buttons) - 1)]
            # Press it for real: QMessageBox only fills in clickedButton(),
            # which is what the application reads, from its own click slot.
            chosen.click()
            return box.result()

        patch(QDialog, "exec", dialog_exec)
        patch(QDialog, "exec_", dialog_exec)
        patch(QMessageBox, "exec", messagebox_exec)
        patch(QMessageBox, "exec_", messagebox_exec)

        def static_question(_parent, title, text, *_a, **_k):
            REC.dialogs.append(("question", title, text))
            return ANSWERS.get("question",
                               QMessageBox.StandardButton.No)

        def static_note(_parent, title, text="", *_a, **_k):
            REC.dialogs.append(("notice", title, text))
            return QMessageBox.StandardButton.Ok

        patch(QMessageBox, "question", staticmethod(static_question))
        patch(QMessageBox, "information", staticmethod(static_note))
        patch(QMessageBox, "warning", staticmethod(static_note))
        patch(QMessageBox, "critical", staticmethod(static_note))
        patch(QMessageBox, "about", staticmethod(static_note))

        def save_name(_parent, caption="", directory="", *_a, **_k):
            REC.dialogs.append(("save file", caption, directory))
            return (ANSWERS.get("save_path", ""), "")

        def open_name(_parent, caption="", directory="", *_a, **_k):
            REC.dialogs.append(("open file", caption, directory))
            return (ANSWERS.get("open_path", ""), "")

        def open_folder(_parent, caption="", directory="", *_a, **_k):
            REC.dialogs.append(("open folder", caption, directory))
            return ANSWERS.get("folder_path", "")

        patch(QFileDialog, "getExistingDirectory", staticmethod(open_folder))
        patch(QFileDialog, "getSaveFileName", staticmethod(save_name))
        patch(QFileDialog, "getOpenFileName", staticmethod(open_name))
        patch(QInputDialog, "getText",
              staticmethod(lambda *a, **k: ("", False)))

        # -- never open a real URL -----------------------------------------

        def fake_open(url):
            text = url.toString() if hasattr(url, "toString") else str(url)
            REC.urls.append(text)
            return True

        patch(QDesktopServices, "openUrl", staticmethod(fake_open))
        from operators_console.ui.widgets import common as common_module
        patch(common_module, "QDesktopServices",
              type("FakeDesktopServices", (), {"openUrl": staticmethod(fake_open)}))

        self._patch_origins()
        self._unused = original_dialog_exec

    # -- where every control was created -----------------------------------

    def _patch_origins(self) -> None:
        """Stamp each button and action with the source line that made it.

        That is what turns "which controls did the walk press" into an exact
        answer rather than a guess at matching visible labels.
        """
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import QPushButton

        def origin():
            frame = inspect.currentframe()
            while frame is not None:
                info = frame.f_code.co_filename
                try:
                    rel = Path(info).resolve().relative_to(SRC)
                except (ValueError, OSError):
                    frame = frame.f_back
                    continue
                # The shared button() factory is not a control of its own:
                # credit the page that asked for the button. Everything else
                # in common.py - LinkRow's Open, for instance - is.
                if (frame.f_code.co_name == "button"
                        and rel.name == "common.py"):
                    frame = frame.f_back
                    continue
                return (rel.as_posix(), frame.f_lineno)
            return None

        for cls in (QPushButton, QAction):
            original = cls.__init__

            def patched(self, *args, __original=original, **kwargs):
                __original(self, *args, **kwargs)
                try:
                    self._walk_origin = origin()
                except Exception:
                    pass

            self.patched.append((cls, "__init__", original))
            cls.__init__ = patched

    def remove(self) -> None:
        from PySide6.QtCore import qInstallMessageHandler
        if self.previous_excepthook is not None:
            sys.excepthook = self.previous_excepthook
        qInstallMessageHandler(self.previous_handler)
        for owner, name, original in reversed(self.patched):
            setattr(owner, name, original)
        self.patched.clear()


def _safe_button_index(box, buttons) -> int:
    from PySide6.QtWidgets import QMessageBox
    cautious = (QMessageBox.ButtonRole.RejectRole,
                QMessageBox.ButtonRole.NoRole)
    for index, widget in enumerate(buttons):
        if box.buttonRole(widget) in cautious:
            return index
    return len(buttons) - 1


#: What the auto answerer says. Tests flip these for one step at a time.
ANSWERS: dict = {}


@contextmanager
def answering(**values):
    previous = dict(ANSWERS)
    ANSWERS.update(values)
    try:
        yield
    finally:
        ANSWERS.clear()
        ANSWERS.update(previous)


SENSORS = _Sensors()


# -- driving ---------------------------------------------------------------


def pump(app, rounds: int = 3) -> None:
    for _ in range(rounds):
        app.processEvents()


def wait_for(app, predicate, seconds: float = 30) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


def note_origin(widget) -> None:
    where = getattr(widget, "_walk_origin", None)
    if where:
        REC.hits.add(where)


def click(app, widget, pump_rounds: int = 2) -> None:
    """Press a control the way a mouse would, and mark it exercised.

    The events are pumped *before* the press as well as after. A control that
    a previous action has just rebuilt has not been laid out yet, and a
    synthetic click on it is quietly dropped - which reads as a defect in the
    application when it is only an artifact of driving Qt without an event
    loop of its own.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    pump(app, 2)
    note_origin(widget)
    if widget.isEnabled():
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
    else:
        REC.bump("clicks on disabled controls")
    pump(app, pump_rounds)


def trigger(app, action, pump_rounds: int = 2) -> None:
    note_origin(action)
    action.trigger()
    pump(app, pump_rounds)


def type_text(app, widget, text: str) -> None:
    from PySide6.QtTest import QTest
    widget.setFocus()
    QTest.keyClicks(widget, text)
    pump(app)


def press(app, widget, key, modifier=None) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    modifier = modifier or Qt.KeyboardModifier.NoModifier
    QTest.keyClick(widget, key, modifier)
    pump(app)


def shortcut(app, window, sequence: str) -> None:
    """Send a key sequence and record it as an exercised shortcut."""
    from PySide6.QtGui import QKeySequence
    from PySide6.QtTest import QTest
    seq = QKeySequence(sequence)
    REC.shortcut_hits.add(seq.toString())
    for index in range(seq.count()):
        combination = seq[index]
        QTest.keyClick(window, combination.key(),
                       combination.keyboardModifiers())
    pump(app)


def settle(app) -> None:
    """Let Qt actually delete what the app asked it to delete.

    ``processEvents`` alone does not run deferred deletes outside a real
    event loop, so a page that was torn down correctly still looks like it
    leaked dozens of parentless widgets. Without this the top level sentinel
    cries wolf on every rebuilt page.
    """
    from PySide6.QtCore import QCoreApplication, QEvent
    app.processEvents()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


def top_levels():
    from PySide6.QtWidgets import QApplication
    return set(QApplication.topLevelWidgets())


def screenshot(widget, name: str) -> str:
    """Grab the widget. Offscreen renders fine into a pixmap."""
    try:
        SHOT_DIR.mkdir(parents=True, exist_ok=True)
        target = SHOT_DIR / ("%s.png" % name.replace("/", "_"))
        widget.grab().save(str(target))
        return str(target)
    except Exception:
        return ""


@contextmanager
def step(app, view: str, action: str, window=None, allow_dialog: bool = False,
         budget: int = SLOW_STEP_MS, expect_exception: bool = False):
    """One learner action, watched from every side.

    ``budget`` is raised only for steps that are *meant* to wait - an exercise
    that has to hit its own timeout, say - so that a real freeze is never
    confused with a deliberate one.
    """
    before_exceptions = len(REC.exceptions)
    before_messages = len(REC.qt_messages)
    before_dialogs = len(REC.dialogs)
    before_windows = top_levels()
    started = time.perf_counter()
    result = "ok"
    try:
        yield
    except Exception as exc:
        ms = int((time.perf_counter() - started) * 1000)
        shot = screenshot(window, "fail-%s-%s" % (view, _slug(action))) \
            if window is not None else ""
        REC.find("blocker", view, "%s raised %s" % (action, type(exc).__name__),
                 "Open %s and %s." % (view, action),
                 traceback.format_exc()[-1200:], shot)
        REC.step(view, action, "EXCEPTION %s" % type(exc).__name__, ms)
        raise
    ms = int((time.perf_counter() - started) * 1000)

    new_exceptions = REC.exceptions[before_exceptions:]
    if new_exceptions and expect_exception:
        result = "raised, as the step was probing for"
    elif new_exceptions:
        result = "unhandled exception"
        shot = screenshot(window, "exc-%s-%s" % (view, _slug(action))) \
            if window is not None else ""
        REC.find("blocker", view,
                 "unhandled exception during: %s" % action,
                 "Open %s and %s." % (view, action),
                 new_exceptions[-1][-1200:], shot)

    new_messages = REC.qt_messages[before_messages:]
    for level, message in new_messages:
        REC.find("major" if level != "warning" else "minor", view,
                 "Qt %s: %s" % (level, message.strip()[:90]),
                 "Open %s and %s." % (view, action), message)

    if ms > budget:
        REC.find("major", view, "step blocks for %d ms: %s" % (ms, action),
                 "Open %s and %s; the interface is frozen for %.1f s."
                 % (view, action, ms / 1000.0))
        result = "slow (%d ms)" % ms

    if not allow_dialog and len(REC.dialogs) > before_dialogs:
        opened = REC.dialogs[before_dialogs:]
        REC.find("minor", view, "unexpected dialog during: %s" % action,
                 "Open %s and %s." % (view, action), repr(opened))
        result = "dialog: %s" % (opened[0][1],)

    settle(app)
    stray = []
    for widget in top_levels() - before_windows:
        try:
            if widget.isVisible() and not _expected_window(widget, window):
                stray.append(widget)
        except RuntimeError:
            continue           # Qt deleted it while we were looking.
    if stray:
        names = ", ".join("%s(%r)" % (type(w).__name__, w.windowTitle())
                          for w in stray[:6])
        REC.find("minor", view, "transient top level window: %s" % names,
                 "Open %s and %s; a window flashes up." % (view, action))
        result = "stray window"

    REC.step(view, action, result, ms)


def _expected_window(widget, window) -> bool:
    from PySide6.QtWidgets import QMenu
    if window is not None and widget is window:
        return True
    # A popup list or menu belongs to whatever opened it.
    if isinstance(widget, QMenu):
        return True
    return type(widget).__name__ in ("QListWidget", "QComboBoxPrivateContainer",
                                     "QTipLabel", "QToolTip")


def _slug(text: str) -> str:
    keep = [c if c.isalnum() else "-" for c in text.lower()]
    return "".join(keep)[:60].strip("-")

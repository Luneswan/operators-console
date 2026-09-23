"""Keyboard focus is drawn. Mouse focus is not.

Qt has no `:focus-visible`. Every `:focus` rule in a stylesheet fires
however the focus arrived, so a control the mouse has just pressed - or one
Qt parked the focus on after a page was rebuilt - wears a ring it never
earned. On screen that reads as damage rather than as focus.

So the ring waits for the keyboard: a widget is marked `kbd` only when the
last thing the learner did was press a key, and every ring in the sheet
keys off that property. Text fields are the documented exception and keep
their plain `:focus` border - clicking into one is how you start typing,
and the border is what says the typing lands there.

The watching is deliberately cheap. An application-wide event filter sees
every event of every object - 31,000 calls to open one phase page, which
cost more than the page - so this listens to two signals instead and filters
only the window, where key and mouse presses arrive.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QWidget

POINTER_EVENTS = frozenset({
    QEvent.Type.MouseButtonPress,
    QEvent.Type.MouseButtonDblClick,
    QEvent.Type.Wheel,
    QEvent.Type.TouchBegin,
})

_WATCHER = "_opcon_focus_watcher"


class FocusWatcher(QObject):
    """Remembers whether the keyboard or the mouse moved the focus."""

    def __init__(self, app, parent=None) -> None:
        super().__init__(parent or app)
        self.keyboard = False
        self._windows = set()
        app.focusChanged.connect(self._focus_changed)
        app.focusWindowChanged.connect(self.watch)
        for window in app.topLevelWindows():
            self.watch(window)

    def watch(self, target) -> None:
        """Filter one window's or widget's input.

        The window is where a real key press arrives, before it reaches the
        widget that has the focus. The main window is watched as well, for
        events sent straight to it - which is how QTest delivers a key, and
        how a shortcut reaches a menu.

        Harmless to call twice for the same object.
        """
        if target is None or id(target) in self._windows:
            return
        self._windows.add(id(target))
        target.installEventFilter(self)

    def note_keyboard(self, keyboard: bool) -> None:
        self.keyboard = bool(keyboard)

    def eventFilter(self, watched, event) -> bool:
        kind = event.type()
        if kind == QEvent.Type.KeyPress:
            self.keyboard = True
        elif kind in POINTER_EVENTS:
            self.keyboard = False
        return False

    def _focus_changed(self, old, new) -> None:
        """One key press rings one control, and only the one it moved to.

        The flag is consumed here rather than left standing: typing in a
        field and then having a page rebuilt underneath you must not ring
        whatever Qt hands the focus to next.
        """
        mark(old, False)
        mark(new, self.keyboard)
        self.keyboard = False


def mark(widget, keyboard: bool) -> None:
    """Set or clear the property, and only repolish when it changed."""
    if not isinstance(widget, QWidget):
        return
    try:
        if bool(widget.property("kbd")) == keyboard:
            return
        widget.setProperty("kbd", keyboard)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
    except RuntimeError:
        pass        # the widget was torn down as it lost the focus


def watcher(app):
    """The one watcher this application has, or None before it is made."""
    return getattr(app, _WATCHER, None)


def install(app) -> FocusWatcher:
    """Install once per application, whatever number of windows follow."""
    existing = watcher(app)
    if existing is None:
        existing = FocusWatcher(app)
        setattr(app, _WATCHER, existing)
    return existing

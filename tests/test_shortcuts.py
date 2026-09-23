"""Keyboard shortcuts: all listed, none clashing, the new ones working."""
from __future__ import annotations

from PySide6.QtGui import QKeySequence

from conftest import pump


def _menu_actions(window):
    for top in window.menuBar().actions():
        if top.menu() is not None:
            yield from top.menu().actions()


def test_the_list_shows_every_bound_menu_shortcut(qt_app, window):
    from operators_console.ui.shortcuts import ShortcutsDialog

    bound = [a for a in _menu_actions(window) if not a.shortcut().isEmpty()]
    dialog = ShortcutsDialog(window)
    try:
        assert len(dialog.rows) == len(bound)
        listed = " | ".join(meaning for _keys, meaning in dialog.rows)
        for action in bound:
            assert action.text().replace("&", "").rstrip(".") in listed
    finally:
        dialog.deleteLater()


def test_no_two_menu_actions_share_a_key(window):
    seen = {}
    for action in _menu_actions(window):
        for key in action.shortcuts():
            text = key.toString(QKeySequence.SequenceFormat.PortableText)
            assert seen.get(text, action) is action, "%s is bound to both %r and %r" % (
                text, seen[text].text(), action.text())
            seen[text] = action


def test_f1_opens_the_list(qt_app, window, monkeypatch):
    from operators_console.ui import shortcuts
    opened = []
    monkeypatch.setattr(shortcuts.ShortcutsDialog, "exec",
                        lambda self: opened.append(len(self.rows)) or 0)
    action = next(a for a in _menu_actions(window)
                  if a.shortcut() == QKeySequence("F1"))
    action.trigger()
    assert opened and opened[0] > 10


def test_ctrl_comma_opens_settings(qt_app, window):
    action = next(a for a in _menu_actions(window)
                  if a.shortcut() == QKeySequence("Ctrl+,"))
    action.trigger()
    pump(qt_app)
    assert window.current_key == "settings"

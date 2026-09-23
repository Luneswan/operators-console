"""Three things the learner walkthrough caught after the theme rework.

- Redo was bound to Ctrl+Y twice (a StandardKey inside a list collapses to
  its first binding), so Qt called it ambiguous and neither key worked.
- The practice autosave fired 700 ms after a quick quit, against the
  closed store.
- A long status message widened the whole window.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from conftest import pump

from operators_console.ui.widgets.common import CheckRow


def _keys(window):
    return [s.toString() for s in window.redo_action.shortcuts()]


def test_redo_carries_both_advertised_keys_once_each(window):
    keys = _keys(window)
    assert "Ctrl+Y" in keys and "Ctrl+Shift+Z" in keys
    assert len(keys) == len(set(keys)), keys


def test_ctrl_shift_z_and_ctrl_y_both_redo(qt_app, window, store, curriculum):
    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    row = window.views["phase"].findChildren(CheckRow)[0]
    row.box.setChecked(True)
    pump(qt_app)
    assert store.is_checked(row.item_id)
    window.activateWindow()
    ctrl = Qt.KeyboardModifier.ControlModifier
    shift = Qt.KeyboardModifier.ShiftModifier
    QTest.keyClick(window, Qt.Key.Key_Z, ctrl)
    pump(qt_app)
    assert not store.is_checked(row.item_id)
    QTest.keyClick(window, Qt.Key.Key_Z, ctrl | shift)
    pump(qt_app)
    assert store.is_checked(row.item_id), "Ctrl+Shift+Z did not redo"
    QTest.keyClick(window, Qt.Key.Key_Z, ctrl)
    pump(qt_app)
    assert not store.is_checked(row.item_id)
    QTest.keyClick(window, Qt.Key.Key_Y, ctrl)
    pump(qt_app)
    assert store.is_checked(row.item_id), "Ctrl+Y did not redo"


def test_closing_stops_every_timer_before_the_store_closes(qt_app, window,
                                                           curriculum):
    window.go("practice", curriculum.exercises[0].id)
    pump(qt_app)
    practice = window.views["practice"]
    practice.editor.set_code("# typed a moment before quitting\n")
    pump(qt_app)
    assert practice._autosave.isActive()
    window.close()
    armed = [t for t in window.findChildren(QTimer) if t.isActive()]
    assert armed == [], [t.objectName() or t.parent() for t in armed]
    assert not window.ctx.store.is_open


def test_a_long_toast_is_cut_not_the_window(qt_app, window):
    quiet = window.statusBar().minimumSizeHint().width()
    message = "The update could not be applied: " + "x" * 400
    window.toast(message)
    pump(qt_app)
    assert window.status_label.text() == message      # readers see it whole
    assert window.statusBar().minimumSizeHint().width() == quiet
    window.status_label.grab()                        # paints, so it elides
    assert window.status_label.toolTip() == message
    window.toast("Saved.")
    window.status_label.grab()
    assert window.status_label.toolTip() == ""

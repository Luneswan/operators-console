"""A ring belongs to the keyboard. A click must not leave one.

Qt has no `:focus-visible`, so every `:focus` rule fired however the focus
arrived: a pressed control, or whatever Qt parked the focus on after a page
was rebuilt, wore a dashed ring that read as damage. `ui/focus.py` marks
keyboard focus with the `kbd` property and the sheet keys every ring off it.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QCheckBox

from conftest import pump

from operators_console.ui.theme import DARK, LIGHT, stylesheet

RING_SELECTORS = (
    'QPushButton[nav="true"][kbd="true"]:focus',
    'QPushButton[nav="true"][active="true"][kbd="true"]:focus',
    '#DisclosureToggle[kbd="true"]:focus',
    'QPushButton[kbd="true"]:focus',
    'QPushButton[kind="primary"][kbd="true"]:focus',
    'QPushButton[kind="quiet"][kbd="true"]:focus',
    'QCheckBox[kbd="true"]::indicator:focus',
    'QRadioButton[kbd="true"]::indicator:focus',
    'QTabBar[kbd="true"]::tab:focus',
)

UNGATED = (
    'QPushButton[nav="true"]:focus {',
    'QPushButton:focus {',
    '#DisclosureToggle:focus {',
    'QCheckBox::indicator:focus {',
    'QTabBar::tab:focus {',
)


def test_every_ring_in_the_sheet_waits_for_the_keyboard():
    for palette in (DARK, LIGHT):
        sheet = stylesheet(palette)
        for selector in RING_SELECTORS:
            assert selector in sheet, (palette.name, selector)
        for selector in UNGATED:
            assert selector not in sheet, (palette.name, selector)


def test_no_control_wears_a_dashed_border():
    for palette in (DARK, LIGHT):
        assert "dashed" not in stylesheet(palette), palette.name


def test_a_text_field_still_shows_focus_when_it_is_clicked():
    # The documented exception: clicking into a field is how you start
    # typing, and the border is what says the typing lands there.
    sheet = stylesheet(DARK)
    assert "QLineEdit:focus" in sheet
    assert 'QLineEdit[kbd="true"]:focus' not in sheet


def test_a_mouse_click_leaves_no_mark_but_a_key_does(qt_app, window):
    from operators_console.ui.focus import watcher

    watching = watcher(qt_app)
    button = window.nav_buttons["roadmap"]
    watching.note_keyboard(False)           # as a mouse press leaves it
    button.setFocus()
    pump(qt_app)
    assert not button.property("kbd")

    button.clearFocus()
    pump(qt_app)
    watching.note_keyboard(True)            # as any key press leaves it
    button.setFocus()
    pump(qt_app)
    assert button.property("kbd") is True

    window.search.setFocus()
    pump(qt_app)
    assert not button.property("kbd"), "the mark outlived the focus"
    assert not window.search.property("kbd"), (
        "one key press rang two controls: the flag was not consumed")


def test_the_watcher_reads_the_keyboard_from_real_events(qt_app, window):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent, QMouseEvent
    from PySide6.QtCore import QPointF
    from operators_console.ui.focus import watcher

    watching = watcher(qt_app)
    press = QKeyEvent(QEvent.Type.KeyPress, int(Qt.Key.Key_Tab),
                      Qt.KeyboardModifier.NoModifier)
    watching.eventFilter(window, press)
    assert watching.keyboard is True
    click = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(1, 1),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier)
    watching.eventFilter(window, click)
    assert watching.keyboard is False


def test_tabbing_through_the_window_marks_what_it_lands_on(qt_app, window):
    window.go("settings", "")
    pump(qt_app)
    window.activateWindow()
    window.search.setFocus(Qt.FocusReason.MouseFocusReason)
    pump(qt_app)
    marked = []
    for _ in range(6):
        QTest.keyClick(window, Qt.Key.Key_Tab)
        pump(qt_app)
        focused = qt_app.focusWidget()
        if focused is not None:
            marked.append(bool(focused.property("kbd")))
    assert marked and all(marked), marked


def test_rebuilding_a_page_does_not_ring_whatever_qt_focuses(qt_app, window,
                                                             store):
    # A theme change tears down every page that is not on screen; Qt then
    # hands the focus to whatever is left, and that must not look chosen -
    # not even straight after the learner typed something.
    from operators_console.ui.focus import watcher

    window.go("today", "")
    pump(qt_app)
    watcher(qt_app).note_keyboard(True)
    store.set_setting("theme", "dark")
    window.ctx.refresh_palette()
    pump(qt_app)
    ringed = [w for w in qt_app.allWidgets() if w.property("kbd")]
    assert ringed == [], [type(w).__name__ for w in ringed]


def test_the_checked_box_draws_the_theme_tick_not_qt_stock_one(qt_app):
    for palette in (DARK, LIGHT):
        sheet = stylesheet(palette)
        assert "standardbutton-apply" not in sheet, palette.name
        assert "check-%s.png" % palette.on_accent.lstrip("#") in sheet
    box = QCheckBox("x")
    box.setChecked(True)
    assert box.isChecked()          # the drawing never changes the state


def test_a_folded_group_says_that_it_is_optional(qt_app, window, curriculum):
    from operators_console.ui.widgets.common import Disclosure

    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    folds = window.views["phase"].findChildren(Disclosure)
    tagged = [f for f in folds if f.tag is not None]
    if folds:
        assert tagged, "a folded group carried no tag"
        assert tagged[0].tag.text() == "OPTIONAL"
    window.go("projects", "")
    pump(qt_app)
    extra = window.views["projects"]._extra
    if extra is not None:
        assert extra.tag is None    # its caption already says what it is

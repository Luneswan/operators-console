"""The code editor's line commands: Ctrl+/ to comment, Tab to indent."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest


@pytest.fixture
def editor(qt_app):
    from operators_console.ui.theme import LIGHT
    from operators_console.ui.widgets.editor import CodeEditor
    widget = CodeEditor(LIGHT)
    yield widget
    widget.deleteLater()


def _select(editor, first_line, last_line, end_at_next_line_start=False):
    """Select whole lines the way a mouse drag does."""
    document = editor.document()
    cursor = editor.textCursor()
    cursor.setPosition(document.findBlockByNumber(first_line).position())
    end = document.findBlockByNumber(last_line)
    if end_at_next_line_start:
        target = end.next().position()
    else:
        target = end.position() + len(end.text())
    cursor.setPosition(target, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)


def _caret_on(editor, line):
    cursor = editor.textCursor()
    cursor.setPosition(editor.document().findBlockByNumber(line).position() + 1)
    editor.setTextCursor(cursor)


def test_ctrl_slash_comments_the_line_the_caret_is_on(editor):
    editor.set_code("x = 1\ny = 2\n")
    _caret_on(editor, 1)
    QTest.keyClick(editor, Qt.Key.Key_Slash, Qt.KeyboardModifier.ControlModifier)
    assert editor.code() == "x = 1\n# y = 2\n"
    QTest.keyClick(editor, Qt.Key.Key_Slash, Qt.KeyboardModifier.ControlModifier)
    assert editor.code() == "x = 1\ny = 2\n"


def test_a_block_is_commented_at_its_shared_indent_and_blanks_are_kept(editor):
    editor.set_code("def f():\n    a = 1\n\n        b = 2\n    return a\n")
    _select(editor, 1, 4)
    editor.toggle_comment()
    assert editor.code() == ("def f():\n    # a = 1\n\n    #     b = 2\n"
                             "    # return a\n")


def test_uncomment_only_when_every_line_is_a_comment(editor):
    editor.set_code("# a\nb\n")
    _select(editor, 0, 1)
    editor.toggle_comment()
    assert editor.code() == "# # a\n# b\n"
    _select(editor, 0, 1)
    editor.toggle_comment()
    assert editor.code() == "# a\nb\n"


def test_a_hash_without_a_space_is_uncommented_too(editor):
    editor.set_code("    #x = 1\n")
    _caret_on(editor, 0)
    editor.toggle_comment()
    assert editor.code() == "    x = 1\n"


def test_one_undo_takes_the_whole_toggle_back(editor):
    editor.set_code("a\nb\nc\n")
    _select(editor, 0, 2)
    editor.toggle_comment()
    editor.undo()
    assert editor.code() == "a\nb\nc\n"


def test_only_blank_lines_changes_nothing(editor):
    editor.set_code("\n   \n")
    _select(editor, 0, 1)
    editor.toggle_comment()
    assert editor.code() == "\n   \n"


def test_a_drag_over_whole_lines_does_not_touch_the_next_one(editor):
    """Found 2026-09-22: Tab also indented the line below the selection."""
    editor.set_code("a\nb\nc\n")
    _select(editor, 0, 1, end_at_next_line_start=True)
    QTest.keyClick(editor, Qt.Key.Key_Tab)
    assert editor.code() == "    a\n    b\nc\n"

    editor.set_code("a\nb\nc\n")
    _select(editor, 0, 1, end_at_next_line_start=True)
    editor.toggle_comment()
    assert editor.code() == "# a\n# b\nc\n"


def test_shift_tab_outdents_the_selected_lines_only(editor):
    editor.set_code("    a\n    b\n    c\n")
    _select(editor, 1, 2)
    QTest.keyClick(editor, Qt.Key.Key_Backtab, Qt.KeyboardModifier.ShiftModifier)
    assert editor.code() == "    a\nb\nc\n"

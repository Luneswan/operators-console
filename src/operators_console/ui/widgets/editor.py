"""A small Python editor: line numbers, syntax colours and sane indentation.

Deliberately not an IDE. It has to be good enough that writing twenty lines of
Python is pleasant, and no more, because the learner should graduate to a real
editor as soon as the exercises stop being the point.
"""
from __future__ import annotations

import keyword
import re

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor, QFont, QPainter, QSyntaxHighlighter, QTextCharFormat, QTextCursor,
    QTextFormat, QTextOption,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from ..theme import Palette, mono_family

BUILTINS = (
    "abs all any bool bytes callable chr dict dir divmod enumerate filter "
    "float format frozenset getattr hasattr hash hex id input int isinstance "
    "issubclass iter len list map max min next object oct open ord pow print "
    "range repr reversed round set setattr slice sorted str sum super tuple "
    "type vars zip"
).split()


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document, palette: Palette) -> None:
        super().__init__(document)
        self.rules = []
        self.set_palette(palette)

    def set_palette(self, palette: Palette) -> None:
        def fmt(colour: str, bold: bool = False, italic: bool = False):
            f = QTextCharFormat()
            f.setForeground(QColor(colour))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            f.setFontItalic(italic)
            return f

        kw = fmt(palette.accent, bold=True)
        builtin = fmt(palette.accent_soft)
        text = fmt(palette.done)
        number = fmt(palette.warn)
        comment = fmt(palette.ink_faint, italic=True)
        decorator = fmt(palette.warn, bold=True)
        defname = fmt(palette.ink, bold=True)

        self.rules = [
            (re.compile(r"\b(%s)\b" % "|".join(keyword.kwlist)), kw),
            (re.compile(r"\b(%s)\b" % "|".join(BUILTINS)), builtin),
            (re.compile(r"\b(True|False|None)\b"), kw),
            (re.compile(r"\b\d+\.?\d*\b"), number),
            (re.compile(r"(?<=\bdef )\w+|(?<=\bclass )\w+"), defname),
            (re.compile(r"@\w+"), decorator),
            (re.compile(r"'''.*?'''|\"\"\".*?\"\"\"", re.S), text),
            (re.compile(r"'[^'\n]*'|\"[^\"\n]*\""), text),
            (re.compile(r"#[^\n]*"), comment),
        ]
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        for pattern, style in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(),
                               style)


class _Gutter(QWidget):
    def __init__(self, editor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.gutter_width(), 0)

    def paintEvent(self, event) -> None:
        self.editor.paint_gutter(event)


class CodeEditor(QPlainTextEdit):
    """Plain text editing with the handful of conveniences that actually help."""

    run_requested = Signal()

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_colours = palette
        self.setProperty("role", "code")
        font = QFont(mono_family())
        font.setPointSize(11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.highlighter = PythonHighlighter(self.document(), palette)

        self.gutter = _Gutter(self)
        self.blockCountChanged.connect(lambda _n: self._update_margin())
        self.updateRequest.connect(self._on_update)
        self.cursorPositionChanged.connect(self._highlight_line)
        self._update_margin()
        self._highlight_line()

    # -- gutter ----------------------------------------------------------

    def gutter_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_margin(self) -> None:
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def _on_update(self, rect, dy: int) -> None:
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_margin()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        box = self.contentsRect()
        self.gutter.setGeometry(
            QRect(box.left(), box.top(), self.gutter_width(), box.height()))

    def paint_gutter(self, event) -> None:
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), QColor(self.palette_colours.paper_2))
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        current = self.textCursor().blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(
                    self.palette_colours.ink_soft if number == current
                    else self.palette_colours.ink_faint))
                painter.drawText(0, int(top), self.gutter.width() - 7,
                                 self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight,
                                 str(number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            number += 1

    def _current_line_colour(self) -> QColor:
        """A band just off the code background, in either theme."""
        base = QColor(self.palette_colours.code_bg)
        return base.lighter(118) if base.lightness() < 128 else base.darker(104)

    def _highlight_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(self._current_line_colour())
        selection.format.setProperty(
            QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    # -- editing conveniences ---------------------------------------------

    def set_theme(self, palette: Palette) -> None:
        self.palette_colours = palette
        self.highlighter.set_palette(palette)
        self._highlight_line()
        self.gutter.update()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        mods = event.modifiers()
        ctrl = mods & Qt.KeyboardModifier.ControlModifier
        meta = mods & Qt.KeyboardModifier.MetaModifier

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (ctrl or meta):
            self.run_requested.emit()
            return

        if key == Qt.Key.Key_Tab and not self.textCursor().hasSelection():
            self.insertPlainText("    ")
            return

        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab) and \
                self.textCursor().hasSelection():
            self._shift_selection(outdent=key == Qt.Key.Key_Backtab)
            return

        if key == Qt.Key.Key_Backspace and not self.textCursor().hasSelection():
            cursor = self.textCursor()
            before = cursor.block().text()[:cursor.positionInBlock()]
            if before and not before.strip() and len(before) % 4 == 0:
                for _ in range(4):
                    cursor.deletePreviousChar()
                return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._newline_with_indent()
            return

        super().keyPressEvent(event)

    def _newline_with_indent(self) -> None:
        cursor = self.textCursor()
        line = cursor.block().text()
        indent = len(line) - len(line.lstrip(" "))
        stripped = line[:cursor.positionInBlock()].rstrip()
        if stripped.endswith(":"):
            indent += 4
        elif stripped.startswith(("return", "pass", "break", "continue",
                                  "raise")):
            indent = max(0, indent - 4)
        cursor.insertText("\n" + " " * indent)
        self.setTextCursor(cursor)

    def _shift_selection(self, outdent: bool) -> None:
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        cursor.beginEditBlock()
        cursor.setPosition(start)
        first = cursor.blockNumber()
        cursor.setPosition(end)
        last = cursor.blockNumber()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for _ in range(first):
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        for _ in range(last - first + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            if outdent:
                text = cursor.block().text()
                strip = min(4, len(text) - len(text.lstrip(" ")))
                for _ in range(strip):
                    cursor.deleteChar()
            else:
                cursor.insertText("    ")
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def set_code(self, text: str) -> None:
        self.setPlainText(text)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def code(self) -> str:
        return self.toPlainText()

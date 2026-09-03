"""Small building blocks shared by every view."""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ..theme import mono_family

_EM = re.compile(r"</?em>")


def plain(text: str) -> str:
    """Strip the curriculum's inline code markers."""
    return _EM.sub("", text)


def rich(text: str) -> str:
    """Render the curriculum's <em> markers as inline code."""
    escaped = (text.replace("&", "&amp;")
               .replace("<em>", "\x01").replace("</em>", "\x02")
               .replace("<", "&lt;").replace(">", "&gt;")
               .replace("\x01", "<code>").replace("\x02", "</code>"))
    return escaped


def label(text: str, object_name: str = "", wrap: bool = True,
          selectable: bool = False) -> QLabel:
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    widget.setWordWrap(wrap)
    if selectable:
        widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
    return widget


def heading(text: str) -> QLabel:
    return label(text, "SectionTitle", wrap=False)


def muted(text: str) -> QLabel:
    return label(text, "Muted")


def soft(text: str) -> QLabel:
    return label(text, "Soft")


def divider() -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    return line


def spacer(height: int = 0) -> QWidget:
    widget = QWidget()
    if height:
        widget.setFixedHeight(height)
    else:
        widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Expanding)
    return widget


def button(text: str, kind: str = "", tooltip: str = "") -> QPushButton:
    btn = QPushButton(text)
    if kind:
        btn.setProperty("kind", kind)
    if tooltip:
        btn.setToolTip(tooltip)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def pill(text: str, tone: str = "") -> QLabel:
    widget = QLabel(text)
    widget.setObjectName("Pill")
    if tone:
        widget.setProperty("tone", tone)
    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return widget


def meter(value: int, maximum: int = 100, tone: str = "") -> QProgressBar:
    bar = QProgressBar()
    bar.setRange(0, max(maximum, 1))
    bar.setValue(value)
    bar.setTextVisible(False)
    bar.setFixedHeight(6)
    if tone:
        bar.setProperty("tone", tone)
    return bar


def mono_label(text: str) -> QLabel:
    widget = label(text, "Mono", wrap=False)
    font = QFont(mono_family())
    font.setPointSize(10)
    widget.setFont(font)
    return widget


class Card(QFrame):
    """A bordered panel with a vertical layout already in place."""

    def __init__(self, flat: bool = False, padding: int = 14,
                 spacing: int = 9, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CardFlat" if flat else "Card")
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(padding, padding, padding, padding)
        self.box.setSpacing(spacing)

    def add(self, widget: QWidget, stretch: int = 0):
        self.box.addWidget(widget, stretch)
        return widget

    def add_row(self, *widgets, spacing: int = 8) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(spacing)
        row.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            if widget is None:
                row.addStretch(1)
            else:
                row.addWidget(widget)
        self.box.addLayout(row)
        return row


class Scroller(QScrollArea):
    """A vertical scroll area with a ready-made content column."""

    def __init__(self, margins=(28, 24, 28, 40), spacing: int = 16,
                 parent=None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body = QWidget()
        self.column = QVBoxLayout(self.body)
        self.column.setContentsMargins(*margins)
        self.column.setSpacing(spacing)
        self.setWidget(self.body)

    def add(self, widget: QWidget, stretch: int = 0):
        self.column.addWidget(widget, stretch)
        return widget

    def add_layout(self, layout):
        self.column.addLayout(layout)
        return layout

    def add_stretch(self) -> None:
        self.column.addStretch(1)

    def clear(self) -> None:
        while self.column.count():
            item = self.column.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout() is not None:
                _drop_layout(item.layout())


def _drop_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _drop_layout(item.layout())


class CheckRow(QWidget):
    """One curriculum line with its checkbox, plus a right-click menu."""

    toggled = Signal(str, bool)
    review_requested = Signal(str)

    def __init__(self, item_id: str, text: str, checked: bool,
                 parent=None) -> None:
        super().__init__(parent)
        self.item_id = item_id
        self.raw_text = text
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(9)

        self.box = QCheckBox()
        self.box.setChecked(checked)
        self.box.setFixedWidth(20)
        self.box.stateChanged.connect(self._on_toggle)
        row.addWidget(self.box, 0, Qt.AlignmentFlag.AlignTop)

        self.text = QLabel(rich(text))
        self.text.setWordWrap(True)
        self.text.setTextFormat(Qt.TextFormat.RichText)
        self.text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(self.text, 1)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)
        self._restyle(checked)

    def _on_toggle(self) -> None:
        state = self.box.isChecked()
        self._restyle(state)
        self.toggled.emit(self.item_id, state)

    def _restyle(self, checked: bool) -> None:
        self.text.setProperty("done", "true" if checked else "false")
        self.text.setStyleSheet(
            "color: palette(placeholder-text); text-decoration: line-through;"
            if checked else "")

    def set_checked(self, checked: bool) -> None:
        blocked = self.box.blockSignals(True)
        self.box.setChecked(checked)
        self.box.blockSignals(blocked)
        self._restyle(checked)

    def _menu(self, point) -> None:
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction(
            "Add to review deck",
            lambda: self.review_requested.emit(self.item_id))
        menu.addAction(
            "Copy text",
            lambda: _copy(plain(self.raw_text)))
        menu.exec(self.mapToGlobal(point))


def _copy(text: str) -> None:
    from PySide6.QtWidgets import QApplication
    QApplication.clipboard().setText(text)


class LinkRow(QWidget):
    """A resource line: name, why it is worth your time, and an open button."""

    def __init__(self, name: str, why: str, url: str, kind: str = "",
                 parent=None) -> None:
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 3, 0, 3)
        row.setSpacing(10)

        column = QVBoxLayout()
        column.setSpacing(1)
        title = QLabel(name)
        title.setStyleSheet("font-weight: 600; font-size: 12.5px;")
        title.setWordWrap(True)
        column.addWidget(title)
        if why:
            column.addWidget(muted(why))
        row.addLayout(column, 1)

        if kind:
            row.addWidget(pill(kind), 0, Qt.AlignmentFlag.AlignTop)
        if url:
            open_button = button("Open", "quiet", url)
            open_button.clicked.connect(lambda: open_url(url))
            row.addWidget(open_button, 0, Qt.AlignmentFlag.AlignTop)


def open_url(url: str) -> None:
    from PySide6.QtCore import QUrl
    if url:
        QDesktopServices.openUrl(QUrl(url))


class StatTile(Card):
    """A single headline number with a caption."""

    def __init__(self, value: str, caption: str, hint: str = "",
                 parent=None) -> None:
        super().__init__(padding=14, spacing=2, parent=parent)
        self.value_label = label(value, "Big", wrap=False)
        self.box.addWidget(self.value_label)
        self.caption_label = label(caption, "Soft", wrap=False)
        self.box.addWidget(self.caption_label)
        if hint:
            self.box.addWidget(muted(hint))

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

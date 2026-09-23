"""A progress ring: the one number a page is about, drawn rather than boxed."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..theme import Palette


class ProgressRing(QWidget):
    """A ring that fills clockwise from the top, with the value inside.

    `value_label` is a real QLabel, so whatever reads the number reads the
    same text a learner sees.
    """

    THICKNESS = 7

    def __init__(self, palette: Palette, size: int = 84, parent=None) -> None:
        super().__init__(parent)
        self.colours = palette
        self._value = 0
        self.setFixedSize(size, size)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self.value_label = QLabel("0%")
        self.value_label.setObjectName("RingValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.value_label)

    def set_value(self, percent: int) -> None:
        self._value = max(0, min(100, int(percent)))
        self.value_label.setText("%d%%" % self._value)
        self.update()

    def set_theme(self, palette: Palette) -> None:
        self.colours = palette
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = self.THICKNESS / 2 + 1
        box = QRectF(inset, inset, self.width() - 2 * inset,
                     self.height() - 2 * inset)
        track = QPen(QColor(self.colours.surface_3), self.THICKNESS)
        painter.setPen(track)
        painter.drawEllipse(box)
        if self._value:
            colour = (self.colours.done if self._value >= 100
                      else self.colours.accent)
            pen = QPen(QColor(colour), self.THICKNESS)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            # Qt angles are 1/16 of a degree, anticlockwise from 3 o'clock.
            painter.drawArc(box, 90 * 16, -int(360 * 16 * self._value / 100))
        painter.end()

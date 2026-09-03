"""Two small painted charts. No plotting dependency for two shapes."""
from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..theme import Palette


class ActivityGrid(QWidget):
    """A year of study activity, one square per day."""

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.colours = palette
        self.data: dict = {}
        self.weeks = 27
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

    def set_data(self, activity: dict) -> None:
        self.data = activity
        self.update()

    def set_theme(self, palette: Palette) -> None:
        self.colours = palette
        self.update()

    def _weight(self, day: str) -> float:
        row = self.data.get(day)
        if not row:
            return 0.0
        score = (row.get("minutes", 0) / 60.0
                 + row.get("items", 0) * 0.25
                 + row.get("reviews", 0) * 0.05
                 + row.get("exercises", 0) * 0.5)
        return min(score / 4.0, 1.0)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        gap = 3
        caption_height = 20
        by_width = (self.width() - gap * self.weeks) // self.weeks
        by_height = (self.height() - caption_height - gap * 7) // 7
        cell = max(6, min(20, by_width, by_height))
        base = QColor(self.colours.paper_2)
        accent = QColor(self.colours.accent)
        done = QColor(self.colours.done)

        today = date.today()
        start = today - timedelta(days=today.weekday() + 7 * (self.weeks - 1))
        painter.setPen(Qt.PenStyle.NoPen)
        for week in range(self.weeks):
            for weekday in range(7):
                day = start + timedelta(days=week * 7 + weekday)
                if day > today:
                    continue
                weight = self._weight(day.isoformat())
                if weight <= 0:
                    colour = base
                else:
                    blend = done if weight > 0.75 else accent
                    colour = QColor(blend)
                    colour.setAlphaF(0.28 + 0.72 * weight)
                painter.setBrush(colour)
                painter.drawRect(
                    week * (cell + gap), weekday * (cell + gap), cell, cell)

        painter.setPen(QPen(QColor(self.colours.ink_faint)))
        painter.drawText(
            QRectF(0, 7 * (cell + gap) + 2, self.width(), caption_height),
            Qt.AlignmentFlag.AlignLeft,
            "Last %d weeks - darker squares are heavier days" % self.weeks)

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(400, 150)


class BarChart(QWidget):
    """A labelled bar chart, used for the review forecast."""

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.colours = palette
        self.values: list = []
        self.labels: list = []
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

    def set_data(self, values, labels=None) -> None:
        self.values = list(values)
        self.labels = list(labels or [])
        self.update()

    def set_theme(self, palette: Palette) -> None:
        self.colours = palette
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        if not self.values or not any(self.values):
            painter.setPen(QPen(QColor(self.colours.ink_faint)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Nothing scheduled yet")
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        top_margin = 6
        bottom = 20
        height = self.height() - top_margin - bottom
        peak = max(self.values) or 1
        count = len(self.values)
        slot = self.width() / count
        width = max(3.0, slot - 3)

        for index, value in enumerate(self.values):
            bar = height * (value / peak)
            colour = QColor(self.colours.accent if index == 0
                            else self.colours.accent_soft)
            colour.setAlphaF(0.9 if index == 0 else 0.65)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(colour)
            painter.drawRoundedRect(
                QRectF(index * slot, top_margin + height - bar, width, bar),
                2, 2)

        painter.setPen(QPen(QColor(self.colours.ink_faint)))
        for index, text in enumerate(self.labels):
            if not text:
                continue
            painter.drawText(
                QRectF(index * slot - slot / 2, self.height() - bottom + 2,
                       slot * 2, 16),
                Qt.AlignmentFlag.AlignCenter, text)

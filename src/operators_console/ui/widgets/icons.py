"""Line icons drawn with QPainter, so they ship on every platform.

No icon font is bundled and the system ones differ by OS, so each glyph is a
few strokes on a 20-unit grid: 1.7 px lines, round caps, the theme's own
ink. Cached by name, colour, size and pixel ratio; a colour change makes a
new pixmap rather than tinting an old one, so edges stay crisp.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

_CACHE: dict = {}


def icon(name: str, colour: str, size: int = 16, ratio: float = 1.0) -> QIcon:
    return QIcon(pixmap(name, colour, size, ratio))


def pixmap(name: str, colour: str, size: int = 16,
           ratio: float = 1.0) -> QPixmap:
    key = (name, colour, size, round(ratio, 2))
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    out = QPixmap(round(size * ratio), round(size * ratio))
    out.setDevicePixelRatio(ratio)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 20.0, size / 20.0)
    pen = QPen(QColor(colour), 1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    drawer = _DRAWERS.get(name)
    if drawer is not None:
        drawer(painter, QColor(colour))
    painter.end()
    _CACHE[key] = out
    return out


def mark(accent: str, ink: str, size: int = 22, ratio: float = 1.0) -> QPixmap:
    """The app's mark: a rounded square with a prompt in it."""
    key = ("mark", accent, ink, size, round(ratio, 2))
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    out = QPixmap(round(size * ratio), round(size * ratio))
    out.setDevicePixelRatio(ratio)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 22.0, size / 22.0)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(accent))
    painter.drawRoundedRect(QRectF(0, 0, 22, 22), 6, 6)
    pen = QPen(QColor(ink), 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawPolyline([QPointF(6.5, 7.5), QPointF(10.5, 11),
                          QPointF(6.5, 14.5)])
    painter.drawLine(QPointF(12, 15), QPointF(16, 15))
    painter.end()
    _CACHE[key] = out
    return out


# -- the glyphs, on a 20 x 20 grid ------------------------------------------

def _today(p, c):
    p.drawEllipse(QPointF(10, 10), 6.5, 6.5)
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(10, 10), 2.2, 2.2)


def _roadmap(p, c):
    path = QPainterPath(QPointF(5, 15.5))
    path.cubicTo(QPointF(5, 9), QPointF(15, 11), QPointF(15, 4.5))
    p.drawPath(path)
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(5, 15.5), 2, 2)
    p.drawEllipse(QPointF(15, 4.5), 2, 2)


def _phase(p, c):
    p.drawPolygon([QPointF(10, 3.5), QPointF(16.5, 7), QPointF(10, 10.5),
                   QPointF(3.5, 7)])
    p.drawPolyline([QPointF(3.5, 11), QPointF(10, 14.5), QPointF(16.5, 11)])
    p.drawPolyline([QPointF(3.5, 14.5), QPointF(10, 18), QPointF(16.5, 14.5)])


def _practice(p, c):
    p.drawPolyline([QPointF(7, 6), QPointF(3, 10), QPointF(7, 14)])
    p.drawPolyline([QPointF(13, 6), QPointF(17, 10), QPointF(13, 14)])
    p.drawLine(QPointF(11.5, 4), QPointF(8.5, 16))


def _quiz(p, c):
    p.drawEllipse(QPointF(10, 10), 7, 7)
    path = QPainterPath(QPointF(7.6, 8.2))
    path.cubicTo(QPointF(7.6, 5.4), QPointF(12.6, 5.4), QPointF(12.4, 8.2))
    path.cubicTo(QPointF(12.3, 10), QPointF(10, 9.8), QPointF(10, 12))
    p.drawPath(path)
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(10, 14.6), 1.1, 1.1)


def _review(p, c):
    p.drawRoundedRect(QRectF(3.5, 6, 11, 10.5), 2, 2)
    p.drawPolyline([QPointF(6.5, 6), QPointF(6.5, 3.5), QPointF(17, 3.5),
                    QPointF(17, 13)])


def _projects(p, c):
    p.drawPolygon([QPointF(10, 2.8), QPointF(16.8, 6.6), QPointF(16.8, 13.4),
                   QPointF(10, 17.2), QPointF(3.2, 13.4), QPointF(3.2, 6.6)])
    p.drawPolyline([QPointF(3.4, 6.7), QPointF(10, 10.3), QPointF(16.6, 6.7)])
    p.drawLine(QPointF(10, 10.3), QPointF(10, 17))


def _log(p, c):
    p.drawLine(QPointF(4, 5.5), QPointF(16, 5.5))
    p.drawLine(QPointF(4, 10), QPointF(16, 10))
    p.drawLine(QPointF(4, 14.5), QPointF(11, 14.5))


def _progress(p, c):
    p.drawLine(QPointF(5, 16), QPointF(5, 11))
    p.drawLine(QPointF(10, 16), QPointF(10, 6))
    p.drawLine(QPointF(15, 16), QPointF(15, 8.5))
    p.drawLine(QPointF(3, 17.5), QPointF(17, 17.5))


def _library(p, c):
    p.drawRoundedRect(QRectF(3.5, 3.5, 13, 13), 1.5, 1.5)
    p.drawLine(QPointF(7.5, 3.5), QPointF(7.5, 16.5))
    p.drawLine(QPointF(10.5, 7), QPointF(13.5, 7))
    p.drawLine(QPointF(10.5, 10), QPointF(13.5, 10))


def _settings(p, c):
    p.drawEllipse(QPointF(10, 10), 3, 3)
    for step in range(8):
        angle = math.radians(step * 45)
        inner, outer = 6.2, 8.4
        p.drawLine(QPointF(10 + inner * math.cos(angle),
                           10 + inner * math.sin(angle)),
                   QPointF(10 + outer * math.cos(angle),
                           10 + outer * math.sin(angle)))


def _search(p, c):
    p.drawEllipse(QPointF(8.5, 8.5), 5.5, 5.5)
    p.drawLine(QPointF(12.7, 12.7), QPointF(17, 17))


def _check(p, c):
    p.drawPolyline([QPointF(4, 10.5), QPointF(8.2, 14.5), QPointF(16, 6)])


def _dot(p, c):
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(10, 10), 3, 3)


def _flame(p, c):
    path = QPainterPath(QPointF(10, 2.5))
    path.cubicTo(QPointF(10, 6), QPointF(5, 8), QPointF(5, 12.5))
    path.cubicTo(QPointF(5, 15.5), QPointF(7.2, 17.5), QPointF(10, 17.5))
    path.cubicTo(QPointF(12.8, 17.5), QPointF(15, 15.5), QPointF(15, 12.5))
    path.cubicTo(QPointF(15, 10), QPointF(13, 8.5), QPointF(12.5, 6.5))
    path.cubicTo(QPointF(11.5, 8), QPointF(10.5, 5), QPointF(10, 2.5))
    p.drawPath(path)


def _clock(p, c):
    p.drawEllipse(QPointF(10, 10), 7, 7)
    p.drawPolyline([QPointF(10, 6), QPointF(10, 10.3), QPointF(13, 12.3)])


_DRAWERS = {
    "today": _today, "roadmap": _roadmap, "phase": _phase,
    "practice": _practice, "quiz": _quiz, "review": _review,
    "projects": _projects, "journal": _log, "stats": _progress,
    "library": _library, "settings": _settings, "search": _search,
    "check": _check, "dot": _dot, "flame": _flame, "clock": _clock,
}

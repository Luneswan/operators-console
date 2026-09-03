"""Draw the application icon and write every format the installers need.

The mark is a monospace caret and a filled progress bar on a paper ground: a
console that is measuring something. Drawing it in code avoids shipping binary
assets that nobody can regenerate.
"""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QColor, QGuiApplication, QImage, QPainter, QPen, QPolygonF,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "icons"
PAPER = "#E7EAE3"
INK = "#16201C"
OXIDE = "#9E3B1B"
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)


def draw(size: int) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

    radius = size * 0.18
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(PAPER))
    painter.drawRoundedRect(QRectF(0, 0, size, size), radius, radius)

    painter.setPen(QPen(QColor(INK), max(1.0, size * 0.022)))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inset = size * 0.035
    painter.drawRoundedRect(
        QRectF(inset, inset, size - inset * 2, size - inset * 2),
        radius * 0.85, radius * 0.85)

    # The caret is drawn as geometry rather than text: a font that is
    # missing on the build machine would silently render as tofu boxes.
    stroke = max(1.6, size * 0.075)
    pen = QPen(QColor(INK), stroke)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    chevron = QPolygonF([
        QPointF(size * 0.255, size * 0.265),
        QPointF(size * 0.475, size * 0.435),
        QPointF(size * 0.255, size * 0.605),
    ])
    painter.drawPolyline(chevron)

    underscore = QPen(QColor(INK), stroke)
    underscore.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(underscore)
    painter.drawLine(QPointF(size * 0.545, size * 0.605),
                     QPointF(size * 0.775, size * 0.605))

    bar_height = max(2.0, size * 0.085)
    bar_top = size * 0.665
    left = size * 0.20
    width = size * 0.60
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#C4CBBF"))
    painter.drawRect(QRectF(left, bar_top, width, bar_height))
    painter.setBrush(QColor(OXIDE))
    painter.drawRect(QRectF(left, bar_top, width * 0.62, bar_height))

    painter.end()
    return image


def write_png(size: int, path: Path) -> None:
    draw(size).save(str(path), "PNG")


def write_ico(path: Path, sizes=(16, 24, 32, 48, 64, 128, 256)) -> None:
    """An ICO is a tiny header plus embedded PNGs, so no library is needed."""
    payloads = []
    for size in sizes:
        temp = OUT / ("_tmp-%d.png" % size)
        write_png(size, temp)
        payloads.append((size, temp.read_bytes()))
        temp.unlink()

    header = struct.pack("<HHH", 0, 1, len(payloads))
    offset = 6 + 16 * len(payloads)
    entries, blobs = b"", b""
    for size, blob in payloads:
        dimension = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dimension, dimension, 0, 0, 1, 32,
                               len(blob), offset)
        offset += len(blob)
        blobs += blob
    path.write_bytes(header + entries + blobs)


def write_iconset(root: Path) -> None:
    """The folder layout `iconutil` expects on macOS."""
    iconset = root / "operators-console.iconset"
    iconset.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 128, 256, 512):
        write_png(size, iconset / ("icon_%dx%d.png" % (size, size)))
        write_png(size * 2, iconset / ("icon_%dx%d@2x.png" % (size, size)))


def main() -> int:
    QGuiApplication(sys.argv[:1])
    OUT.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        write_png(size, OUT / ("operators-console-%d.png" % size))
    write_png(512, OUT / "operators-console.png")
    write_ico(OUT / "operators-console.ico")
    write_iconset(OUT)
    print("icons written to", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

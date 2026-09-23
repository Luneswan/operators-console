"""A checklist line keeps its shape when the mouse passes over it."""
from PySide6.QtCore import QPointF
from PySide6.QtGui import QEnterEvent

from conftest import pump

from operators_console.ui.widgets.common import CheckRow


def _hover(qt_app, row):
    event = QEnterEvent(QPointF(5, 5), QPointF(5, 5), QPointF(5, 5))
    qt_app.sendEvent(row, event)
    pump(qt_app)


def test_hovering_a_line_does_not_make_it_taller(qt_app, window, curriculum):
    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    rows = window.views["phase"].findChildren(CheckRow)[:6]
    before = [r.height() for r in rows]
    for row in rows:
        _hover(qt_app, row)
    after = [r.height() for r in rows]
    assert after == before, (before, after)
    assert all(r._more is not None for r in rows)
    assert all(r._more.height() <= r.line_height() for r in rows)


def test_the_text_starts_level_with_its_checkbox(qt_app, window, curriculum):
    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    for row in window.views["phase"].findChildren(CheckRow)[:6]:
        _hover(qt_app, row)
        assert abs(row.text.y() - row.box.y()) <= 3, (row.text.y(), row.box.y())


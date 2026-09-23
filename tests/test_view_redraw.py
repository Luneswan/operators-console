"""Pages redraw when something they show changed, and only then.

Roadmap and Stats used to tear down and rebuild everything on every visit.
They now skip the rebuild while the store's write counter (and, for Stats,
the date) is where it was when they last drew - so correctness never depends
on some code path remembering to emit a change signal.
"""
from __future__ import annotations

import time

from conftest import pump


def _cards(layout):
    return [layout.itemAt(i).widget() for i in range(layout.count())
            if layout.itemAt(i).widget() is not None]


def _visit(window, qt_app, key):
    window.go("today")
    pump(qt_app)
    window.go(key)
    pump(qt_app)
    return window.views[key]


def test_a_roadmap_visit_with_nothing_new_keeps_its_cards(window, qt_app):
    view = _visit(window, qt_app, "roadmap")
    before = [id(w) for w in _cards(view.holder)]
    assert before
    _visit(window, qt_app, "roadmap")
    assert [id(w) for w in _cards(view.holder)] == before


def test_a_roadmap_repeat_visit_is_fast(window, qt_app):
    _visit(window, qt_app, "roadmap")
    timings = []
    for _ in range(3):
        window.go("today")
        pump(qt_app)
        start = time.perf_counter()
        window.go("roadmap")
        pump(qt_app)
        timings.append((time.perf_counter() - start) * 1000)
    assert min(timings) < 40, timings        # 90-136 ms before


def test_a_tick_anywhere_redraws_the_roadmap(window, qt_app, curriculum):
    view = _visit(window, qt_app, "roadmap")
    before = [id(w) for w in _cards(view.holder)]
    phase = next(p for p in curriculum.phases if p.items)
    window.ctx.set_checked(phase.items[0].id, True)
    view = _visit(window, qt_app, "roadmap")
    assert [id(w) for w in _cards(view.holder)] != before


def test_undo_redraws_the_roadmap(window, qt_app, curriculum):
    phase = next(p for p in curriculum.phases if p.items)
    window.ctx.set_checked(phase.items[0].id, True)
    view = _visit(window, qt_app, "roadmap")
    drawn = [id(w) for w in _cards(view.holder)]
    window.undo()
    pump(qt_app)
    view = _visit(window, qt_app, "roadmap")
    assert [id(w) for w in _cards(view.holder)] != drawn


def test_a_new_track_redraws_the_roadmap(window, qt_app, store):
    view = _visit(window, qt_app, "roadmap")
    count = len(_cards(view.holder))
    store.set_setting("track", "beginner")
    view = _visit(window, qt_app, "roadmap")
    assert len(_cards(view.holder)) != count


def test_stats_skips_a_visit_with_nothing_new(window, qt_app, monkeypatch):
    view = _visit(window, qt_app, "stats")
    drew = []
    monkeypatch.setattr(view, "_draw", lambda: drew.append(1))
    _visit(window, qt_app, "stats")
    assert drew == []


def test_stats_redraws_on_a_new_day_even_with_no_writes(window, qt_app,
                                                         monkeypatch):
    import datetime as datetime_module
    view = _visit(window, qt_app, "stats")
    drew = []
    monkeypatch.setattr(view, "_draw", lambda: drew.append(1))

    real = datetime_module.date

    class Tomorrow(real):
        @classmethod
        def today(cls):
            return real.today() + datetime_module.timedelta(days=1)

    monkeypatch.setattr(datetime_module, "date", Tomorrow)
    _visit(window, qt_app, "stats")
    assert drew == [1]


def test_a_replaced_store_always_redraws(window, qt_app, store, monkeypatch):
    """A restored backup arrives as a different store object."""
    view = _visit(window, qt_app, "roadmap")
    drew = []
    monkeypatch.setattr(view, "_draw", lambda: drew.append(1))

    class Other:
        db = store.db
    monkeypatch.setattr(window.ctx, "store", Other())
    view.refresh()
    assert drew == [1]

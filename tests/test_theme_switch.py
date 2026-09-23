"""A theme change costs what is on screen, not every page ever opened.

The walkthrough measured a 5.6 s freeze on switching theme with every page
built, 82 s on pushing the text-size spinner from end to end, and 45 s on a
switch after that: Qt re-polishes every live widget at about a millisecond
each. Pages that are not on screen now give up their widgets first and
rebuild on the next visit; a page mid-task keeps them.
"""
from __future__ import annotations

import time

from PySide6.QtWidgets import QApplication

from conftest import pump

from operators_console.ui.main_window import NAV


def _build_every_page(window, qt_app):
    for key, _text, _factory in NAV:
        window.go(key, "")
        pump(qt_app)
    window.go("today", "")
    pump(qt_app)


def _flip(window, qt_app, store, theme):
    store.set_setting("theme", theme)
    window.ctx.refresh_palette()
    pump(qt_app)


def test_a_theme_switch_with_every_page_built_is_quick(qt_app, window, store):
    _build_every_page(window, qt_app)
    before = len(qt_app.allWidgets())
    assert before > 2000
    started = time.perf_counter()
    _flip(window, qt_app, store, "dark")
    elapsed = time.perf_counter() - started
    # The structural proof: the sheet had a few hundred widgets to polish,
    # not a few thousand (the pages are torn down and deleted before it is
    # applied). The clock is a loose backstop so a busy machine cannot fail
    # this on its own; measured 0.69 s alone against 3.8 s before the
    # teardown and 2.5 s before `Scroller.reset` dropped each page's tree
    # in one move instead of retiring three thousand widgets one at a time.
    after = len(qt_app.allWidgets())
    assert after < before // 4, (before, after)
    assert elapsed < 2.5, "%.2f s" % elapsed
    assert window.views["today"]._built
    assert not window.views["projects"]._built
    assert not window.views["library"]._built


def test_torn_down_pages_come_back_whole(qt_app, window, store, curriculum):
    _build_every_page(window, qt_app)
    _flip(window, qt_app, store, "dark")
    window.go("roadmap", "")
    pump(qt_app)
    view = window.views["roadmap"]
    assert view._built
    assert view.holder.count() == len(window.ctx.planner.roadmap())
    window.go("projects", "")
    pump(qt_app)
    assert window.views["projects"].card_for(curriculum.projects[0].id)
    window.go("library", "")
    pump(qt_app)
    assert window.views["library"].tabs.count() == 4


def test_the_open_phase_survives_a_theme_switch(qt_app, window, store,
                                                curriculum):
    phase = curriculum.phases[3]
    window.go("phase", phase.id)
    pump(qt_app)
    window.go("settings", "")
    pump(qt_app)
    _flip(window, qt_app, store, "dark")
    assert not window.views["phase"]._built
    window.go("phase", "")
    pump(qt_app)
    assert window.views["phase"].current_id == phase.id


def test_a_quiz_under_way_is_not_thrown_away(qt_app, window, store,
                                             curriculum):
    quiz = curriculum.quizzes[0]
    window.go("quiz", quiz.id)
    pump(qt_app)
    view = window.views["quiz"]
    view._answer(0)
    window.go("settings", "")
    pump(qt_app)
    _flip(window, qt_app, store, "dark")
    assert view._built and view.quiz is quiz
    assert len(view.answers) == 1


def test_typed_notes_are_saved_before_a_page_is_torn_down(qt_app, window,
                                                          store, curriculum):
    phase = curriculum.phases[2]
    window.go("phase", phase.id)
    pump(qt_app)
    window.views["phase"].notes.setPlainText("keep this")
    project = curriculum.projects[0]
    window.go("projects", project.id)
    pump(qt_app)
    window.views["projects"].card_for(project.id).notes.setPlainText("and this")
    window.go("today", "")
    pump(qt_app)
    _flip(window, qt_app, store, "dark")
    assert store.note("phase:" + phase.id) == "keep this"
    assert store.project(project.id)["notes"] == "and this"
    # And the torn-down page is safe to hide again (its cards are gone).
    window.views["projects"].flush_notes()


def test_the_text_size_spinner_applies_once_per_burst(qt_app, window,
                                                      monkeypatch):
    from operators_console.ui.views import settings as settings_module

    monkeypatch.setattr(settings_module, "FONT_APPLY_MS", 60)
    window.go("settings", "")
    pump(qt_app)
    view = window.views["settings"]
    applied = []
    window.ctx.theme_changed.connect(lambda: applied.append(1))
    for step in range(12):
        view.font_scale.setValue(1.0 + 0.05 * (step + 1))
    assert applied == []
    deadline = time.monotonic() + 3
    while not applied and time.monotonic() < deadline:
        qt_app.processEvents()
        time.sleep(0.02)
    assert applied == [1]
    view.font_scale.setValue(1.0)
    deadline = time.monotonic() + 3
    while len(applied) < 2 and time.monotonic() < deadline:
        qt_app.processEvents()
        time.sleep(0.02)
    assert applied == [1, 1]
    assert QApplication.instance().font().pointSizeF() > 0

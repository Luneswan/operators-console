"""The Projects page: built once, kept in step, and honest about the plan.

It used to destroy and recreate every card (about 2,100 widgets) on each
visit and on each status press, never scrolled to the project it was sent to,
wrote the notes box to disk on every keystroke, left a card's progress bar
still after a tick, and counted all 22 projects while Today counted the plan.
"""
from __future__ import annotations

import time

from conftest import pump


def _projects(window, qt_app):
    window.go("projects")
    pump(qt_app)
    return window.views["projects"]


def _off_plan(ctx):
    return [p for p in ctx.curriculum.projects
            if not ctx.progress.is_in_plan(p.phase)]


# -- built once --------------------------------------------------------------

def test_a_second_visit_reuses_every_card(window, qt_app):
    view = _projects(window, qt_app)
    before = {p.id: id(view.card_for(p.id))
              for p in window.ctx.curriculum.projects}
    window.go("today")
    pump(qt_app)
    window.go("projects")
    pump(qt_app)
    after = {p.id: id(view.card_for(p.id))
             for p in window.ctx.curriculum.projects}
    assert before == after, "the page rebuilt its cards on a plain visit"


def test_a_repeat_visit_is_fast(window, qt_app):
    _projects(window, qt_app)
    timings = []
    for _ in range(3):
        window.go("today")
        pump(qt_app)
        start = time.perf_counter()
        window.go("projects")
        pump(qt_app)
        timings.append((time.perf_counter() - start) * 1000)
    # It was 450-550 ms offscreen (2-3 s on a real screen) before the rewrite.
    assert min(timings) < 150, timings


def test_a_status_press_changes_the_card_in_place(window, qt_app, store):
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    card = view.card_for(project.id)
    view._set_status(project.id, "in-progress")
    pump(qt_app)
    assert view.card_for(project.id) is card
    assert card.status_pill.text() == "IN PROGRESS"
    assert card.status_buttons["in-progress"].property("kind") == "primary"
    assert card.status_buttons["not-started"].property("kind") == "quiet"
    assert store.project(project.id)["status"] == "in-progress"


# -- the numbers move when the learner acts ------------------------------------

def test_a_tick_moves_the_bar_and_the_count_at_once(window, qt_app):
    view = _projects(window, qt_app)
    project = next(p for p in window.ctx.curriculum.projects
                   if len(p.requirement_ids) >= 2)
    card = view.card_for(project.id)
    assert card.meter.value() == 0
    card.rows[project.requirement_ids[0]].box.click()
    pump(qt_app)
    total = len(project.requirement_ids)
    assert card.done_label.text() == "1 of %d requirements met" % total
    assert card.meter.value() == round(100 / total)


def test_undo_puts_the_card_back(window, qt_app):
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    view._set_status(project.id, "shipped")
    pump(qt_app)
    window.undo()
    pump(qt_app)
    assert view.card_for(project.id).status_pill.text() == "NOT STARTED"


# -- the notes box --------------------------------------------------------------

def test_typing_notes_saves_once_after_the_typing_stops(window, qt_app, store,
                                                       monkeypatch):
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    card = view.card_for(project.id)
    writes = []
    real = store.set_project

    def counting(project_id, **kwargs):
        writes.append(kwargs)
        return real(project_id, **kwargs)
    monkeypatch.setattr(store, "set_project", counting)

    for ch in "decided on argparse":
        card.notes.insertPlainText(ch)
    pump(qt_app, 1)
    assert not writes, "notes were written while the learner was typing"

    card.flush_notes()
    assert [w for w in writes if "notes" in w] == [
        {"notes": "decided on argparse"}]
    assert store.project(project.id)["notes"] == "decided on argparse"


def test_leaving_the_page_saves_notes_still_waiting(window, qt_app, store):
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    card = view.card_for(project.id)
    card.notes.insertPlainText("half a thought")
    window.go("today")                                  # hides the page
    pump(qt_app, 1)
    assert store.project(project.id)["notes"] == "half a thought"


def test_quitting_saves_notes_typed_a_moment_ago(window, qt_app):
    """closeEvent closes the store; the waiting save must happen first."""
    from operators_console.core.storage import Store
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    view.card_for(project.id).notes.insertPlainText("last words")
    window.close()
    reopened = Store()
    try:
        assert reopened.project(project.id)["notes"] == "last words"
    finally:
        reopened.close()


def test_a_visit_never_overwrites_notes_waiting_to_be_saved(window, qt_app):
    view = _projects(window, qt_app)
    project = window.ctx.curriculum.projects[0]
    card = view.card_for(project.id)
    card.notes.insertPlainText("typing")
    view.refresh()                                      # e.g. an undo elsewhere
    assert card.notes.toPlainText() == "typing"


# -- only the plan is the plan ----------------------------------------------------

def test_the_counter_agrees_with_today(window, qt_app):
    view = _projects(window, qt_app)
    for project in window.ctx.curriculum.projects:
        window.ctx.set_project_status(project.id, "shipped")
    view.refresh()
    overview = window.ctx.progress.overview()
    assert ("%d of %d in your plan shipped"
            % (overview.projects_total, overview.projects_total)
            in view.counter.text()), view.counter.text()


def test_projects_outside_the_track_are_folded(window, qt_app, store):
    store.set_setting("track", "beginner")
    view = _projects(window, qt_app)
    outside = _off_plan(window.ctx)
    assert outside, "the beginner track should leave some projects out"
    assert view._extra is not None
    for project in window.ctx.curriculum.projects:
        folded = view._extra.isAncestorOf(view.card_for(project.id))
        assert folded == (project in outside), project.id
    assert "%d more outside your track" % len(outside) in view.counter.text()


def test_changing_track_rearranges_without_rebuilding(window, qt_app, store):
    view = _projects(window, qt_app)
    ids = {p.id: id(view.card_for(p.id))
           for p in window.ctx.curriculum.projects}
    store.set_setting("track", "beginner")
    view.refresh()
    assert {p.id: id(view.card_for(p.id))
            for p in window.ctx.curriculum.projects} == ids
    assert view._extra is not None


# -- being sent to a project -------------------------------------------------------

def test_being_sent_to_a_project_scrolls_to_it(window, qt_app):
    window.resize(1100, 700)
    view = _projects(window, qt_app)
    target = window.ctx.curriculum.projects[-1]
    window.go("projects", target.id)
    pump(qt_app, 4)
    card = view.card_for(target.id)
    viewport = view.scroller.viewport()
    top = card.mapTo(viewport, card.rect().topLeft()).y()
    assert 0 <= top < viewport.height(), (
        "the target card is at y=%d, outside the %d px viewport"
        % (top, viewport.height()))


def test_being_sent_to_a_folded_project_opens_the_fold(window, qt_app, store):
    store.set_setting("track", "beginner")
    view = _projects(window, qt_app)
    target = _off_plan(window.ctx)[0]
    view._extra.set_open(False, animate=False)
    window.go("projects", target.id)
    pump(qt_app, 4)
    assert view._extra.is_open


def test_a_filter_never_hides_the_target(window, qt_app):
    view = _projects(window, qt_app)
    view.filter.setCurrentText("Shipped")
    target = window.ctx.curriculum.projects[0]
    window.go("projects", target.id)
    pump(qt_app, 2)
    assert view.filter.currentText() == "All"
    assert view.card_for(target.id).isVisible()


def test_the_page_can_be_hidden_before_it_was_ever_built(qt_app, store,
                                                         curriculum):
    """Qt hides a page when the stack first adopts it - before build()."""
    from operators_console.ui.context import AppContext
    from operators_console.ui.views.projects import ProjectsView
    view = ProjectsView(AppContext(store=store, curriculum=curriculum))
    view.show()
    view.hide()                                         # must not raise
    assert view.card_for("anything") is None

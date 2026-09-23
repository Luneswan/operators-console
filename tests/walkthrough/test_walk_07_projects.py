"""Projects: all twenty-two, every requirement, every status."""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_full]


def _cards(view):
    """Every project's card in curriculum order, wherever it is placed: the
    plan's cards sit in `holder`, the ones outside the track in the fold."""
    return [view.card_for(p.id) for p in view.ctx.curriculum.projects]


def _named(card, text):
    from PySide6.QtWidgets import QPushButton
    for widget in card.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def test_every_project_is_shown_with_everything_it_promises(walk_app, window,
                                                            curriculum):
    from operators_console.ui.widgets.common import CheckRow
    window.go("projects", "")
    pump(walk_app, 3)
    view = window.views["projects"]
    with step(walk_app, "projects", "read all %d project cards"
              % len(curriculum.projects), window):
        cards = _cards(view)
        assert len(cards) == len(curriculum.projects), (
            "%d cards for %d projects" % (len(cards), len(curriculum.projects)))
        for card, project in zip(cards, curriculum.projects, strict=True):
            rows = card.findChildren(CheckRow)
            assert len(rows) == len(project.requirements), (
                "%s drew %d requirement rows for %d requirements"
                % (project.id, len(rows), len(project.requirements)))
            text = card.findChildren(type(card))  # nested cards, if any
            assert text is not None
    REC.bump("projects listed", len(curriculum.projects))
    REC.bump("project requirements drawn",
             sum(len(p.requirements) for p in curriculum.projects))


def test_every_requirement_ticks_and_unticks(walk_app, window, store,
                                             curriculum):
    from operators_console.ui.widgets.common import CheckRow
    window.go("projects", "")
    pump(walk_app, 3)
    view = window.views["projects"]
    ticked = 0
    for project in curriculum.projects:
        card = _cards(view)[list(curriculum.projects).index(project)]
        rows = {r.item_id: r for r in card.findChildren(CheckRow)}
        with step(walk_app, "projects", "meet every requirement of %s"
                  % project.id, window):
            for req_id in project.requirement_ids:
                assert req_id in rows, "%s has no row" % req_id
                rows[req_id].box.setChecked(True)
                ticked += 1
            pump(walk_app, 1)
            missing = [i for i in project.requirement_ids
                       if not store.is_checked(i)]
            assert not missing, missing
    REC.bump("project requirements ticked", ticked)

    with step(walk_app, "projects", "the meters agree once everything is met",
              window):
        window.go("projects", "")
        pump(walk_app, 3)
        checked = store.checked_ids()
        for project in curriculum.projects:
            done = sum(1 for i in project.requirement_ids if i in checked)
            assert done == len(project.requirement_ids), project.id

    for project in curriculum.projects:
        card = _cards(window.views["projects"])[
            list(curriculum.projects).index(project)]
        rows = {r.item_id: r for r in card.findChildren(CheckRow)}
        with step(walk_app, "projects", "untick %s again" % project.id,
                  window):
            for req_id in project.requirement_ids:
                rows[req_id].box.setChecked(False)
            pump(walk_app, 1)
            assert not [i for i in project.requirement_ids
                        if store.is_checked(i)]


def test_every_project_can_be_marked_through_every_status(walk_app, window,
                                                          store, curriculum):
    from operators_console.ui.views.projects import STATUSES
    window.go("projects", "")
    pump(walk_app, 3)
    for project in curriculum.projects:
        for value, text, _tone in STATUSES:
            view = window.views["projects"]
            card = _cards(view)[list(curriculum.projects).index(project)]
            widget = _named(card, text)
            assert widget is not None, "%s has no %r button" % (project.id, text)
            with step(walk_app, "projects", "mark %s as %s"
                      % (project.id, text), window):
                click(walk_app, widget, pump_rounds=1)
                assert store.project(project.id)["status"] == value
    REC.bump("project status changes",
             len(curriculum.projects) * len(STATUSES))


def test_the_filter_and_the_repo_and_notes_fields(walk_app, window, store,
                                                  curriculum):
    from PySide6.QtWidgets import QLineEdit, QPlainTextEdit
    window.go("projects", "")
    pump(walk_app, 3)
    view = window.views["projects"]
    with step(walk_app, "projects", "try each filter", window):
        for mode in ("Not started", "In progress", "Shipped", "All"):
            view.filter.setCurrentIndex(view.filter.findText(mode))
            pump(walk_app, 1)
            assert view.counter.text()
        assert len(_cards(view)) == len(curriculum.projects)

    project = curriculum.projects[0]
    card = _cards(view)[0]
    with step(walk_app, "projects", "record a repo and some notes", window):
        line = card.findChildren(QLineEdit)[0]
        line.setText("https://example.invalid/mine")
        line.editingFinished.emit()
        notes = card.findChildren(QPlainTextEdit)[0]
        notes.setPlainText("Decided to use a queue.")
        # Notes save on a short debounce rather than per keystroke, so give
        # the timer the moment a learner's next glance would.
        from PySide6.QtTest import QTest
        for _ in range(60):
            QTest.qWait(50)
            if store.project(project.id)["notes"]:
                break
        state = store.project(project.id)
        assert state["repo_url"] == "https://example.invalid/mine"
        assert state["notes"] == "Decided to use a queue."

    before = len(REC.urls)
    with step(walk_app, "projects", "press Open next to the repo", window):
        click(walk_app, _named(card, "Open"))
        assert len(REC.urls) == before + 1
        assert REC.urls[-1] == "https://example.invalid/mine"

    with step(walk_app, "projects", "jump to the project's phase", window):
        phase = curriculum.phase(project.phase)
        go = _named(card, "Go to phase %s" % (phase.num if phase else ""))
        assert go is not None
        click(walk_app, go)
        assert window.current_key == "phase"


def test_shipping_everything_moves_the_headline_number(walk_app, window,
                                                       store, curriculum):
    window.go("projects", "")
    pump(walk_app, 3)
    view = window.views["projects"]
    with step(walk_app, "projects", "ship all %d projects"
              % len(curriculum.projects), window):
        for project in curriculum.projects:
            window.ctx.set_project_status(project.id, "shipped")
        window.go("projects", "")
        pump(walk_app, 3)
        overview = window.ctx.progress.overview()
        # The page counts the learner's plan, exactly as Today does.
        assert "%d of %d in your plan shipped" % (
            overview.projects_total, overview.projects_total) \
            in view.counter.text(), view.counter.text()
    with step(walk_app, "today", "Today agrees", window):
        window.go("today", "")
        pump(walk_app, 2)
        overview = window.ctx.progress.overview()
        assert overview.projects_shipped == overview.projects_total
        # Both pages count the learner's plan; a project outside it sits
        # under "Not in your plan" on the Projects page, and is not a
        # disagreement between the two.
        REC.bump("projects outside the plan",
                 len(curriculum.projects) - overview.projects_total)


@pytest.mark.walk_fast
def test_how_long_one_status_button_takes(walk_app, window, store,
                                          curriculum):
    """One press should not cost most of a second."""
    import time
    window.go("projects", "")
    pump(walk_app, 4)
    view = window.views["projects"]
    project = curriculum.projects[0]
    timings = []
    for value in ["not-started", "in-progress", "shipped"] * 3:
        started = time.perf_counter()
        view._set_status(project.id, value)
        pump(walk_app, 1)
        timings.append((time.perf_counter() - started) * 1000)
        assert store.project(project.id)["status"] == value
    worst = int(max(timings))
    typical = int(sorted(timings)[len(timings) // 2])
    REC.bump("milliseconds for a typical project status press", typical)
    REC.step("projects", "press a status button", "%d ms" % typical, typical)
    if typical > 250:
        REC.find("major", "projects",
                 "every project status press redraws all %d project cards"
                 % len(curriculum.projects),
                 "Open Projects, press 'In progress' on any project: the "
                 "page stalls for about %d ms before anything moves."
                 % typical,
                 "ProjectsView._set_status calls _fill(), which clears the "
                 "layout and rebuilds every card - requirements, stretch "
                 "goals, rubric, notes box and repo field - for a change "
                 "that touches one card. Median %d ms, worst %d ms over %d "
                 "presses. The same rebuild runs on every refresh, which is "
                 "why arriving on the page costs about half a second too."
                 % (typical, worst, len(timings)))

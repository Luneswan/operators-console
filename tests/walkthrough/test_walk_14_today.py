"""Today as something you can act on, and the day the plan runs out.

The first thirteen walks study a learner in the middle of the course. This
one covers the two ends of it: a morning where the list is not quite what
they want to do, and the morning after the last checkbox, when every other
page still says "YOU ARE HERE" about a phase finished weeks ago.

Every control added for those two mornings is pressed here the way a learner
presses it - the "Not today" on the focus card and on a compact row, the way
back, and all three buttons on the completion hero, including the export,
whose file dialog is answered and whose file is then read off disk.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from .harness import REC, answering, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


# -- finding things on the page -------------------------------------------


def _all_named(root, text):
    from PySide6.QtWidgets import QPushButton
    return [w for w in root.findChildren(QPushButton) if w.text() == text]


def _named(root, text):
    found = _all_named(root, text)
    return found[0] if found else None


def _starting(root, prefix):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text().startswith(prefix):
            return widget
    return None


def _page_text(root) -> str:
    from PySide6.QtWidgets import QLabel
    return "\n".join(w.text() for w in root.findChildren(QLabel))


def _finish_the_plan(store, curriculum, progress) -> int:
    """Read and prove every phase: ticks alone no longer finish a plan.

    A phase counts once its gate is ticked, its quiz passed at 85%, 60% of
    its exercises passed and one project shipped.
    """
    ids = []
    for pid in progress.active_phase_ids():
        phase = curriculum.phase(pid)
        if phase is not None:
            ids.extend(phase.trackable_ids)
    store.set_many_checked(ids, True)
    for pid in progress.active_phase_ids():
        for quiz in curriculum.quizzes_for(pid):
            store.record_quiz(quiz.id, 17, 20, 30)
        for exercise in curriculum.exercises_for(pid):
            store.record_exercise_run(exercise.id, "pass", True)
        for project in curriculum.projects_for(pid)[:1]:
            store.set_project(project.id, status="shipped")
    return len(ids)


def _ship_and_ace(store, curriculum, progress) -> None:
    plan = set(progress.active_phase_ids())
    for project in curriculum.projects:
        if project.phase in plan:
            store.set_project(project.id, status="shipped")
    for quiz in curriculum.quizzes:
        if quiz.phase in plan:
            store.record_quiz(quiz.id, 10, 10, 30)


# -- a morning that is not quite what the learner wants --------------------


def test_the_learner_pushes_two_things_off_and_takes_them_back(
        walk_app, window, store):
    window.go("today", "")
    pump(walk_app, 2)
    view = window.views["today"]

    with step(walk_app, "today", "read the note above the list", window):
        store.add_log(date.today().isoformat(), "Generators", 1.5,
                      "A streaming pipeline", "closures", "")
        view.refresh()
        pump(walk_app, 2)
        note = view.plan_note.text()
        assert "logged today" in note, note
        REC.bump("plan notes read")

    with step(walk_app, "today", "push the first item off until tomorrow",
              window):
        before = len(view.ctx.today.build())
        assert before >= 2, "not enough on the list to push anything off"
        skip = _named(view, "Not today")
        assert skip is not None, "the list still cannot be acted on"
        click(walk_app, skip)
        assert len(view.ctx.today.dismissed_keys()) == 1
        assert len(view.ctx.today.build()) == before - 1
        REC.bump("plan actions dismissed")

    with step(walk_app, "today", "push a second one off from a compact row",
              window):
        skips = _all_named(view, "Not today")
        assert len(skips) >= 2, "only the focus card can be pushed off"
        click(walk_app, skips[-1])
        assert len(view.ctx.today.dismissed_keys()) == 2
        REC.bump("plan actions dismissed")

    with step(walk_app, "today", "find the way back to what was hidden",
              window):
        back = _starting(view, "Show ")
        assert back is not None, "nothing hidden can ever be seen again"
        assert back.text() == "Show 2 hidden", back.text()
        click(walk_app, back)
        assert view.ctx.today.dismissed_keys() == set()
        assert _starting(view, "Show ") is None


def test_what_the_learner_promised_last_night_is_on_the_list(
        walk_app, window, store):
    with step(walk_app, "today", "yesterday's 'first thing tomorrow' returns",
              window):
        store.add_log((date.today() - timedelta(days=1)).isoformat(),
                      "Generators", 2.0, "A pipeline", "closures",
                      "Read itertools properly")
        window.go("today", "")
        pump(walk_app, 2)
        view = window.views["today"]
        text = _page_text(view)
        assert "You said you'd start with: Read itertools properly" in text, (
            "the log asks for it every evening and never shows it again")
        REC.bump("log promises surfaced")


def test_a_quiet_day_and_a_finished_plan_do_not_say_the_same_thing(
        walk_app, window, store, curriculum):
    window.go("today", "")
    pump(walk_app, 2)
    view = window.views["today"]

    with step(walk_app, "today", "push everything off for a quiet evening",
              window):
        for action in list(view.ctx.today.build()):
            view.ctx.today.dismiss(action)
        view.refresh()
        pump(walk_app, 2)
        quiet = _page_text(view)
        assert "Nothing outstanding today." in quiet, quiet
        assert "take the evening off" in quiet
        view.ctx.today.restore()

    with step(walk_app, "today", "finish the entire curriculum", window):
        ticked = _finish_the_plan(store, curriculum, window.ctx.progress)
        assert ticked > 0
        assert window.ctx.progress.is_finished is True
        _ship_and_ace(store, curriculum, window.ctx.progress)
        store.add_log(date.today().isoformat(), "The last day", 1.0, "", "",
                      "")
        view.refresh()
        pump(walk_app, 2)
        done = _page_text(view)
        assert "Nothing due, and nothing left to learn." in done, done
        assert "take the evening off" not in done
        REC.bump("curriculum completions reached")


# -- the morning after the last checkbox -----------------------------------


def test_the_completion_hero_and_all_three_of_its_buttons(
        walk_app, window, store, curriculum, tmp_path):
    store.set_setting("started_on", "2026-01-04")
    store.add_log(date.today().isoformat(), "The last day", 2.0,
                  "Shipped the final project", "", "")
    _finish_the_plan(store, curriculum, window.ctx.progress)
    window.go("today", "")
    pump(walk_app, 2)
    view = window.views["today"]

    with step(walk_app, "today", "read what the finished plan says", window):
        assert view.position_heading.text() == "What you did"
        text = _page_text(view.position_card)
        assert "You finished it." in text, text
        assert "COMPLETE" in text
        assert "2026-01-04 to %s" % date.today().isoformat() in text
        assert "hours logged" in text

    with step(walk_app, "today", "keep reviewing from the hero", window):
        click(walk_app, _named(view.position_card, "Keep reviewing"))
        assert window.stack.currentWidget() is window.views["review"]

    window.go("today", "")
    pump(walk_app, 2)
    view = window.views["today"]
    with step(walk_app, "today", "change track from the hero", window):
        click(walk_app, _named(view.position_card, "Change track"))
        assert window.stack.currentWidget() is window.views["settings"]

    window.go("today", "")
    pump(walk_app, 2)
    view = window.views["today"]
    target = tmp_path / "python-progress.md"
    with step(walk_app, "today", "export the report from the hero", window,
              allow_dialog=True):
        with answering(save_path=str(target)):
            click(walk_app, _named(view.position_card, "Export report"))
        assert target.exists(), "the hero's export wrote nothing"
        body = target.read_text(encoding="utf-8")
        assert body.strip(), "the report is empty"
        REC.bump("progress reports written")


def test_the_roadmap_stops_saying_you_are_here(walk_app, window, store,
                                               curriculum):
    from operators_console.ui.views.roadmap import CURRENT, Rail

    window.go("roadmap", "")
    pump(walk_app, 2)
    with step(walk_app, "roadmap", "the marker is there while work remains",
              window):
        assert "YOU ARE HERE" in _page_text(window.views["roadmap"])

    _finish_the_plan(store, curriculum, window.ctx.progress)
    window.go("today", "")
    pump(walk_app, 2)
    window.go("roadmap", "")
    pump(walk_app, 2)
    with step(walk_app, "roadmap", "and is gone once there is nowhere to go",
              window):
        view = window.views["roadmap"]
        text = _page_text(view)
        assert "YOU ARE HERE" not in text
        assert "PLAN COMPLETE" in text, text
        assert not [r for r in view.findChildren(Rail) if r.state == CURRENT]


# -- the Progress table, which used to look like a control -----------------


def test_a_progress_row_opens_its_phase_by_mouse_and_by_keyboard(
        walk_app, window):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    window.go("stats", "")
    pump(walk_app, 3)
    view = window.views["stats"]
    table = view.table
    assert table.rowCount() > 2

    with step(walk_app, "stats", "click a phase row", window):
        wanted = table.item(1, 0).data(Qt.ItemDataRole.UserRole)
        rect = table.visualRect(table.model().index(1, 0))
        QTest.mouseClick(table.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, rect.center())
        pump(walk_app, 3)
        assert window.stack.currentWidget() is window.views["phase"], (
            "the table still looks interactive and is not")
        assert window.views["phase"].current_id == wanted
        REC.bump("progress rows opened")

    window.go("stats", "")
    pump(walk_app, 3)
    view = window.views["stats"]
    table = view.table
    with step(walk_app, "stats", "select a row and press Enter", window):
        table.setFocus()
        table.setCurrentCell(2, 0)
        wanted = table.item(2, 0).data(Qt.ItemDataRole.UserRole)
        QTest.keyClick(table, Qt.Key.Key_Return)
        pump(walk_app, 3)
        assert window.stack.currentWidget() is window.views["phase"]
        assert window.views["phase"].current_id == wanted


def test_the_quiz_column_shows_how_the_attempts_went(walk_app, window, store,
                                                     curriculum):
    quiz = curriculum.quizzes[0]
    for score in (4, 6, 8):
        store.record_quiz(quiz.id, score, 10, 60)
    window.go("stats", "")
    pump(walk_app, 3)
    table = window.views["stats"].table
    with step(walk_app, "stats", "hover the quiz column for the trend",
              window):
        tips = [table.item(row, 3).toolTip()
                for row in range(table.rowCount())]
        assert any("40% -> 60% -> 80%" in tip for tip in tips), tips
        REC.bump("quiz trends shown", sum(1 for t in tips if "->" in t))


# -- the Phase page --------------------------------------------------------


def test_the_phase_page_admits_its_right_click_menu_and_grows_its_notes(
        walk_app, window, curriculum):
    from operators_console.ui.views.phase import (
        NOTE_MAX_HEIGHT, NOTE_MIN_HEIGHT,
    )

    phase = next(p for p in curriculum.phases if p.sections)
    window.go("phase", phase.id)
    pump(walk_app, 3)
    view = window.views["phase"]

    with step(walk_app, "phase", "the way into the review deck is announced",
              window):
        text = _page_text(view)
        assert "review deck" in text
        for way in ("right-click", "...", "Shift+F10"):
            assert way in text, way

    with step(walk_app, "phase", "write a long note into the box", window):
        assert view.notes.height() == NOTE_MIN_HEIGHT
        view.notes.setPlainText(
            "\n".join("What clicked today, line %d." % n for n in range(30)))
        pump(walk_app, 2)
        grown = view.notes.height()
        assert grown > NOTE_MIN_HEIGHT, (
            "a long note is still written into a two-line window")
        assert grown <= NOTE_MAX_HEIGHT
        REC.bump("phase notes written")

    with step(walk_app, "phase", "and it shrinks back for a short one",
              window):
        view.notes.setPlainText("Short.")
        pump(walk_app, 2)
        assert view.notes.height() == NOTE_MIN_HEIGHT
        view.flush_note()
        assert window.ctx.store.note("phase:" + phase.id) == "Short."

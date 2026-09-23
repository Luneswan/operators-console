"""The gaps between "the plan" and "a day", closed.

Six of them, all learner-facing:

* finishing the curriculum was undefined - the marker pinned "YOU ARE HERE"
  to the last phase for ever and Today offered the evening off,
* the "first thing tomorrow" the Log asks for every evening was never read
  by anything again,
* Today was a list that could not be acted on: no way to push one item to
  tomorrow, and no sense of what had already been done today,
* the Progress table looked like a control and was not one,
* the Phase page hid its own right-click menu and wrote notes into a fixed
  two-line window,
* and an empty list said the same thing whether the day was quiet or the
  whole course was behind you.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from conftest import pump

from operators_console.core.adaptive import Planner
from operators_console.core.progress import Progress
from operators_console.core.today import DISMISSED_SETTING, TodayPlan, plan_key


# -- helpers ---------------------------------------------------------------


def plan_for(curriculum, store):
    progress = Progress(curriculum, store)
    planner = Planner(curriculum, store, progress)
    return progress, planner, TodayPlan(curriculum, store, progress, planner)


def tick_the_plan(store, curriculum, progress) -> int:
    """Tick every line the meter counts, in every phase of the plan."""
    ids = []
    for pid in progress.active_phase_ids():
        phase = curriculum.phase(pid)
        if phase is not None:
            ids.extend(phase.trackable_ids)
    store.set_many_checked(ids, True)
    return len(ids)


def finish_the_plan(store, curriculum, progress) -> int:
    """Read and prove every phase of the plan.

    Finishing used to mean ticking every line. A phase now counts once its
    gate is ticked, its quiz passed at 85%, 60% of its exercises passed and
    one project shipped - so this passes each quiz at exactly 85% (a score
    still worth one more sitting), every exercise, and the first project of
    each phase, leaving any second project unbuilt.
    """
    ticked = tick_the_plan(store, curriculum, progress)
    plan = progress.active_phase_ids()
    for pid in plan:
        for quiz in curriculum.quizzes_for(pid):
            store.record_quiz(quiz.id, 17, 20, 30)
        for exercise in curriculum.exercises_for(pid):
            store.record_exercise_run(exercise.id, "pass", True)
        for project in curriculum.projects_for(pid)[:1]:
            store.set_project(project.id, status="shipped")
    return ticked


def ship_every_project(store, curriculum, progress) -> None:
    plan = set(progress.active_phase_ids())
    for project in curriculum.projects:
        if project.phase in plan:
            store.set_project(project.id, status="shipped")


def ace_every_quiz(store, curriculum, progress) -> None:
    plan = set(progress.active_phase_ids())
    for quiz in curriculum.quizzes:
        if quiz.phase in plan:
            store.record_quiz(quiz.id, 10, 10, 30)


def make_due(store, card_id: str, phase: str) -> None:
    """A card that was due two days ago, so it is due now."""
    from datetime import datetime, timezone

    from operators_console.core.srs import Memory, State

    overdue = datetime.now(timezone.utc) - timedelta(days=2)
    store.save_memory(card_id, "concept", phase,
                      Memory(stability=3.0, difficulty=5.0,
                             state=State.REVIEW, due=overdue,
                             last_review=overdue - timedelta(days=3), reps=2))


def buttons(root):
    from PySide6.QtWidgets import QPushButton
    return root.findChildren(QPushButton)


def named(root, text):
    for widget in buttons(root):
        if widget.text() == text:
            return widget
    return None


def starting(root, prefix):
    for widget in buttons(root):
        if widget.text().startswith(prefix):
            return widget
    return None


def labels(root):
    from PySide6.QtWidgets import QLabel
    return [w.text() for w in root.findChildren(QLabel)]


def page_text(root) -> str:
    return "\n".join(labels(root))


# ---------------------------------------------------------------------------
# 1. finishing the curriculum
# ---------------------------------------------------------------------------


def test_a_fresh_plan_is_not_finished(progress):
    assert progress.is_finished is False


def test_a_plan_with_nothing_trackable_in_it_is_not_finished(curriculum,
                                                             store):
    """There was never anything to finish, so "finished" would be a lie."""
    import copy

    blank = copy.copy(curriculum)
    blank.phases = ()
    blank._phase_by_id = {}
    progress = Progress(blank, store)
    assert progress.active_phase_ids() == []
    assert progress.is_finished is False


def test_ticking_every_line_in_the_plan_finishes_it(curriculum, store,
                                                    progress):
    """Ticking is reading; the plan is finished once every phase is proven.

    This pinned the old meaning, where ticks alone finished the plan.
    """
    assert tick_the_plan(store, curriculum, progress) > 0
    assert progress.is_finished is False, "reading alone finished the plan"
    finish_the_plan(store, curriculum, progress)
    assert progress.is_finished is True


def test_one_line_short_is_not_finished(curriculum, store, progress):
    finish_the_plan(store, curriculum, progress)
    last = curriculum.phase(progress.active_phase_ids()[-1])
    store.set_checked(last.trackable_ids[-1], False)
    assert progress.is_finished is False


def test_the_marker_still_names_a_phase_when_the_plan_is_finished(
        curriculum, store, progress):
    """`current_phase_id` is unchanged: pages that need somewhere to stand
    still get somewhere. What changed is that nothing reads it as a position
    without asking `is_finished` first."""
    finish_the_plan(store, curriculum, progress)
    assert progress.current_phase_id() == progress.active_phase_ids()[-1]


def test_started_on_falls_back_to_the_first_day_with_any_activity(store,
                                                                  progress):
    assert progress.started_on() == ""
    store.bump_activity(minutes=30, day="2026-01-04")
    store.bump_activity(minutes=30, day="2026-02-02")
    assert progress.started_on() == "2026-01-04"
    store.set_setting("started_on", "2025-12-30")
    assert progress.started_on() == "2025-12-30"


# ---------------------------------------------------------------------------
# 2. the maintenance plan
# ---------------------------------------------------------------------------


def test_a_finished_plan_stops_offering_the_last_phase_for_ever(
        curriculum, store):
    progress, _planner, today = plan_for(curriculum, store)
    finish_the_plan(store, curriculum, progress)
    kinds = {a.kind for a in today.build()}
    assert "learn" not in kinds, "still sending the learner back to study"
    assert "gate" not in kinds
    assert "practice" not in kinds


def test_a_finished_plan_offers_the_projects_that_were_never_shipped(
        curriculum, store):
    progress, _planner, today = plan_for(curriculum, store)
    finish_the_plan(store, curriculum, progress)
    projects = [a for a in today.build() if a.kind == "project"]
    assert projects, "an unbuilt project is the obvious thing left to do"
    plan = set(progress.active_phase_ids())
    allowed = {p.id for p in curriculum.projects if p.phase in plan}
    assert all(a.target in allowed for a in projects)


def test_a_finished_plan_asks_for_one_weak_quiz_back(curriculum, store):
    progress, _planner, today = plan_for(curriculum, store)
    finish_the_plan(store, curriculum, progress)
    ship_every_project(store, curriculum, progress)
    quizzes = [a for a in today.build() if a.kind == "quiz"]
    assert len(quizzes) == 1, "one revisit, not a re-sit of the whole course"


def test_a_finished_plan_with_everything_done_has_an_empty_list(curriculum,
                                                               store):
    progress, _planner, today = plan_for(curriculum, store)
    finish_the_plan(store, curriculum, progress)
    ship_every_project(store, curriculum, progress)
    ace_every_quiz(store, curriculum, progress)
    store.add_log(date.today().isoformat(), "Wrapping up", 1.0, "", "", "")
    assert today.build() == []


def test_due_reviews_still_come_first_after_the_plan_is_finished(curriculum,
                                                                 store):
    progress, _planner, today = plan_for(curriculum, store)
    finish_the_plan(store, curriculum, progress)
    make_due(store, "concept:one", progress.active_phase_ids()[0])
    actions = today.build()
    assert actions and actions[0].kind == "review"


# ---------------------------------------------------------------------------
# 3. the promise the learner wrote in the Log
# ---------------------------------------------------------------------------


def test_yesterdays_first_thing_tomorrow_comes_back(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    store.add_log(yesterday, "Generators", 2.0, "A pipeline", "closures",
                  "Read itertools properly")
    text, said_on = today.promise()
    assert text == "Read itertools properly"
    assert said_on == yesterday
    promised = [a for a in today.build()
                if a.title.startswith("You said you'd start with:")]
    assert promised, "the one line the learner wrote is still never shown"
    assert promised[0].title.endswith("Read itertools properly")
    assert promised[0].minutes == 15
    assert promised[0].kind == "learn"


def test_a_promise_older_than_three_days_is_left_alone(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    stale = (date.today() - timedelta(days=9)).isoformat()
    store.add_log(stale, "Decorators", 2.0, "", "", "Finish the cache")
    assert today.promise() == ("", "")
    assert not [a for a in today.build()
                if a.title.startswith("You said you'd start with:")]


def test_the_newest_promise_wins_and_blank_ones_are_skipped(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    store.add_log((date.today() - timedelta(days=2)).isoformat(),
                  "Typing", 2.0, "", "", "Older promise")
    store.add_log((date.today() - timedelta(days=1)).isoformat(),
                  "Asyncio", 2.0, "", "", "")
    assert today.promise()[0] == "Older promise"
    store.add_log(date.today().isoformat(), "Testing", 1.0, "", "",
                  "Newest promise")
    assert today.promise()[0] == "Newest promise"


# ---------------------------------------------------------------------------
# 4. "not today"
# ---------------------------------------------------------------------------


def test_an_action_key_survives_the_number_in_its_title(curriculum, store):
    """The title moves as the day goes on; the key must not."""
    progress, _planner, today = plan_for(curriculum, store)
    phase = progress.active_phase_ids()[0]
    for index in range(3):
        make_due(store, "concept:%d" % index, phase)
    first = [a for a in today.build() if a.kind == "review"][0]
    store.suspend_card("concept:0", True)
    second = [a for a in today.build() if a.kind == "review"][0]
    assert first.title != second.title
    assert plan_key(first) == plan_key(second) == "review:"


def test_dismissing_hides_one_action_and_promotes_the_next(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    before = today.build()
    assert len(before) >= 2
    today.dismiss(before[0])
    shown, hidden = today.split()
    assert [plan_key(a) for a in hidden] == [plan_key(before[0])]
    assert plan_key(before[0]) not in {plan_key(a) for a in shown}
    assert shown and plan_key(shown[0]) == plan_key(before[1])


def test_dismissing_twice_is_not_two_entries(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    action = today.build()[0]
    today.dismiss(action)
    today.dismiss(action)
    assert len(today.dismissed_keys()) == 1


def test_what_was_hidden_is_remembered_per_day(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    action = today.build()[0]
    today.dismiss(action)
    stored = store.setting(DISMISSED_SETTING, {})
    assert list(stored) == [date.today().isoformat()]
    assert stored[date.today().isoformat()] == [plan_key(action)]
    # Tomorrow is a different day, and a clean one.
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert today.dismissed_keys(tomorrow) == set()


def test_yesterdays_dismissals_are_pruned_rather_than_kept_for_ever(
        curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    old = (date.today() - timedelta(days=40)).isoformat()
    store.set_setting(DISMISSED_SETTING, {old: ["quiz:q99"]})
    today.dismiss(today.build()[0])
    assert old not in store.setting(DISMISSED_SETTING, {})


def test_restoring_brings_everything_back(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    before = [plan_key(a) for a in today.build()]
    today.dismiss(today.build()[0])
    today.dismiss(today.build()[0])
    assert len(today.split()[1]) == 2
    today.restore()
    assert today.split()[1] == []
    assert [plan_key(a) for a in today.build()] == before


def test_a_dismissed_set_that_is_not_a_dict_is_ignored(curriculum, store):
    """Settings are JSON and a hand-edited profile can hold anything."""
    _progress, _planner, today = plan_for(curriculum, store)
    for junk in ("nonsense", 7, ["quiz:q1"], None):
        store.set_setting(DISMISSED_SETTING, junk)
        assert today.dismissed_keys() == set()
        assert today.build()


def test_hours_today_counts_only_todays_entries(curriculum, store):
    _progress, _planner, today = plan_for(curriculum, store)
    assert today.hours_today() == 0.0
    store.add_log(date.today().isoformat(), "Morning", 1.0, "", "", "")
    store.add_log(date.today().isoformat(), "Evening", 0.5, "", "", "")
    store.add_log((date.today() - timedelta(days=1)).isoformat(),
                  "Yesterday", 4.0, "", "", "")
    assert today.hours_today() == 1.5


# ---------------------------------------------------------------------------
# Today, on screen
# ---------------------------------------------------------------------------


def test_today_says_how_much_of_the_day_is_already_logged(qt_app, window):
    window.ctx.store.set_setting("hours_per_day", 3.0)
    window.ctx.store.add_log(date.today().isoformat(), "Generators", 1.5,
                             "", "", "")
    window.go("today", "")
    pump(qt_app)
    note = window.views["today"].plan_note.text()
    assert "1.5 h of your 3 h logged today" in note


def test_not_today_hides_a_row_and_show_hidden_brings_it_back(qt_app, window):
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]
    before = len(view.ctx.today.build())
    assert before >= 2

    skip = named(view, "Not today")
    assert skip is not None, "no way to push anything off the list"
    skip.click()
    pump(qt_app)
    assert len(view.ctx.today.dismissed_keys()) == 1

    back = starting(view, "Show ")
    assert back is not None and back.text() == "Show 1 hidden"
    back.click()
    pump(qt_app)
    assert view.ctx.today.dismissed_keys() == set()
    assert starting(view, "Show ") is None


def test_the_hidden_row_counts_only_what_is_still_relevant(qt_app, window):
    """A key dismissed for something that has since gone must not be counted."""
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]
    view.ctx.today.dismiss("project:nothing-like-this")
    view.refresh()
    pump(qt_app)
    assert starting(view, "Show ") is None


def test_the_empty_list_reads_differently_when_the_plan_is_finished(
        qt_app, window, curriculum):
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]
    store, progress = window.ctx.store, window.ctx.progress

    for action in list(view.ctx.today.build()):
        view.ctx.today.dismiss(action)
    view.refresh()
    pump(qt_app)
    quiet = page_text(view)
    assert "Nothing outstanding today." in quiet
    assert "take the evening off" in quiet

    view.ctx.today.restore()
    finish_the_plan(store, curriculum, progress)
    ship_every_project(store, curriculum, progress)
    ace_every_quiz(store, curriculum, progress)
    store.add_log(date.today().isoformat(), "Wrapping up", 1.0, "", "", "")
    view.refresh()
    pump(qt_app)
    done = page_text(view)
    assert "Nothing due, and nothing left to learn." in done
    assert "take the evening off" not in done


def test_the_completion_hero_replaces_where_you_are(qt_app, window,
                                                    curriculum):
    store, progress = window.ctx.store, window.ctx.progress
    store.set_setting("started_on", "2026-01-04")
    store.add_log(date.today().isoformat(), "The last day", 2.0, "", "", "")
    finish_the_plan(store, curriculum, progress)
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]

    assert view.position_heading.text() == "What you did"
    text = page_text(view.position_card)
    assert "You finished it." in text
    assert "COMPLETE" in text
    assert "2026-01-04 to %s" % date.today().isoformat() in text
    assert "hours logged" in text
    for wanted in ("Export report", "Keep reviewing", "Change track"):
        assert named(view.position_card, wanted) is not None, wanted


def test_the_heros_buttons_go_where_they_say(qt_app, window, curriculum):
    finish_the_plan(window.ctx.store, curriculum, window.ctx.progress)
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]

    named(view.position_card, "Keep reviewing").click()
    pump(qt_app)
    assert window.stack.currentWidget() is window.views["review"]

    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]
    named(view.position_card, "Change track").click()
    pump(qt_app)
    assert window.stack.currentWidget() is window.views["settings"]


def test_export_report_runs_the_file_menus_own_handler(qt_app, window,
                                                       curriculum,
                                                       monkeypatch):
    finish_the_plan(window.ctx.store, curriculum, window.ctx.progress)
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]

    called = []
    monkeypatch.setattr(type(window), "_report",
                        lambda self: called.append(True))
    named(view.position_card, "Export report").click()
    pump(qt_app)
    assert called == [True], "the hero has its own copy of the export"


def test_the_ten_minute_skip_still_notices_a_dismissal(qt_app, window):
    """Today skips its redraw while nothing it reads has moved. What the
    learner pushed off is one of the things it reads."""
    window.go("today", "")
    pump(qt_app)
    view = window.views["today"]
    view.refresh()
    drawn = view._drawn_key
    view.refresh()
    assert view._drawn_key == drawn, "redrew with nothing changed"
    view.ctx.today.dismiss(view.ctx.today.build()[0])
    view.refresh()
    assert view._drawn_key != drawn


# ---------------------------------------------------------------------------
# the roadmap, once there is nowhere left to go
# ---------------------------------------------------------------------------


def test_the_roadmap_drops_you_are_here_when_the_plan_is_finished(
        qt_app, window, curriculum):
    window.go("roadmap", "")
    pump(qt_app)
    view = window.views["roadmap"]
    assert "YOU ARE HERE" in page_text(view)
    assert view.finished_banner.isVisibleTo(view) is False

    finish_the_plan(window.ctx.store, curriculum, window.ctx.progress)
    window.go("today", "")
    pump(qt_app)
    window.go("roadmap", "")
    pump(qt_app)
    view = window.views["roadmap"]
    text = page_text(view)
    assert "YOU ARE HERE" not in text
    assert "PLAN COMPLETE" in text
    assert "You have walked the whole plan." in text
    assert "all of it behind you" in view.summary.text()


def test_the_roadmap_rail_has_no_current_node_when_finished(qt_app, window,
                                                            curriculum):
    from operators_console.ui.views.roadmap import CURRENT, Rail

    finish_the_plan(window.ctx.store, curriculum, window.ctx.progress)
    window.go("roadmap", "")
    pump(qt_app)
    rails = window.views["roadmap"].findChildren(Rail)
    assert rails
    assert not [r for r in rails if r.state == CURRENT]


# ---------------------------------------------------------------------------
# the Progress table
# ---------------------------------------------------------------------------


def test_a_progress_row_opens_its_phase(qt_app, window):
    window.go("stats", "")
    pump(qt_app)
    view = window.views["stats"]
    assert view.table.rowCount() > 1

    wanted = view.table.item(1, 0).data(0x0100)      # Qt.UserRole
    view.table.cellClicked.emit(1, 0)
    pump(qt_app)
    assert window.stack.currentWidget() is window.views["phase"]
    assert window.views["phase"].current_id == wanted


def test_enter_on_the_selected_progress_row_opens_it(qt_app, window):
    window.go("stats", "")
    pump(qt_app)
    view = window.views["stats"]
    view.table.setCurrentCell(2, 0)
    wanted = view.table.item(2, 0).data(0x0100)
    view.table.activated.emit(view.table.currentIndex())
    pump(qt_app)
    assert window.stack.currentWidget() is window.views["phase"]
    assert window.views["phase"].current_id == wanted


def test_the_progress_table_is_still_read_only(qt_app, window):
    from PySide6.QtWidgets import QTableWidget

    window.go("stats", "")
    pump(qt_app)
    table = window.views["stats"].table
    assert table.editTriggers() == QTableWidget.EditTrigger.NoEditTriggers
    assert (table.selectionBehavior()
            == QTableWidget.SelectionBehavior.SelectRows)


def test_the_quiz_column_carries_the_attempt_trend(qt_app, window,
                                                   curriculum):
    quiz = curriculum.quizzes[0]
    for score in (4, 6, 8):
        window.ctx.store.record_quiz(quiz.id, score, 10, 60)
    window.go("stats", "")
    pump(qt_app)
    table = window.views["stats"].table
    tips = [table.item(row, 3).toolTip() for row in range(table.rowCount())]
    assert any("40% -> 60% -> 80%" in tip for tip in tips), tips
    assert any("not attempted yet" in tip for tip in tips)


# ---------------------------------------------------------------------------
# the Phase page
# ---------------------------------------------------------------------------


def test_the_phase_page_says_how_to_reach_the_review_deck(qt_app, window,
                                                          curriculum):
    """All three ways in, not just the mouse one."""
    phase = next(p for p in curriculum.phases if p.sections)
    window.go("phase", phase.id)
    pump(qt_app)
    text = page_text(window.views["phase"])
    assert "review deck" in text
    for way in ("right-click", "...", "Shift+F10"):
        assert way in text, way


def test_a_phase_with_no_checklist_does_not_advertise_the_menu(qt_app, window,
                                                               curriculum):
    empty = next((p for p in curriculum.phases if not p.sections), None)
    if empty is None:
        pytest.skip("every phase in this curriculum has a checklist")
    window.go("phase", empty.id)
    pump(qt_app)
    assert "Right-click any line" not in page_text(window.views["phase"])


def test_the_notes_box_grows_with_what_is_written_in_it(qt_app, window,
                                                        curriculum):
    from operators_console.ui.views.phase import (
        NOTE_MAX_HEIGHT, NOTE_MIN_HEIGHT,
    )

    window.go("phase", curriculum.phases[1].id)
    pump(qt_app)
    notes = window.views["phase"].notes
    assert notes.height() == NOTE_MIN_HEIGHT

    notes.setPlainText("\n".join("line %d" % n for n in range(40)))
    pump(qt_app)
    tall = notes.height()
    assert tall > NOTE_MIN_HEIGHT, "still a two-line window on a long note"
    assert tall <= NOTE_MAX_HEIGHT, "grew past the page"

    notes.setPlainText("one line")
    pump(qt_app)
    assert notes.height() == NOTE_MIN_HEIGHT


def test_the_note_still_saves_while_the_box_is_resizing(qt_app, window,
                                                        curriculum):
    phase = curriculum.phases[1]
    window.go("phase", phase.id)
    pump(qt_app)
    view = window.views["phase"]
    view.notes.setPlainText("Something worth keeping.\n" * 12)
    pump(qt_app)
    view.flush_note()
    assert window.ctx.store.note("phase:" + phase.id).startswith(
        "Something worth keeping.")

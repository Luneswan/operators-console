"""The gaps the Practice page still had once the grader could explain itself.

Each test here pins one thing a learner could not do, or was told wrongly:

* a run could not be stopped, so an endless loop held the page for its whole
  timeout and then recorded a failed attempt for the trouble,
* the hint ladder wrapped while its label counted up, so a fourth press on a
  three-hint exercise said "Hint 4 of 3" and showed hint one again,
* reading the answer was recorded and then shown to nobody,
* the code that last passed was overwritten by the next experiment,
* ninety-six exercises had no search and no difficulty filter,
* Next on the last exercise did nothing at all, silently,
* an exercise with no hints hid the button rather than explaining it,
* and one failed attempt was labelled "IN PROGRESS", which it is not.
"""
from __future__ import annotations

import pytest
from conftest import pump, wait_for
from PySide6.QtWidgets import QLabel


def _open(qt_app, window, exercise):
    window.go("practice", exercise.id)
    pump(qt_app)
    view = window.views["practice"]
    assert view.current is not None and view.current.id == exercise.id
    return view


def _text(widget) -> str:
    return "\n".join(child.text() for child in widget.findChildren(QLabel))


def _with_hints(curriculum, count: int = 2):
    return next(e for e in curriculum.exercises if len(e.hints) >= count)


def _without_hints(curriculum):
    return next((e for e in curriculum.exercises if not e.hints), None)


# ---------------------------------------------------------------------------
# 2 - a run can be stopped
# ---------------------------------------------------------------------------

def test_stop_kills_the_run_and_records_nothing(qt_app, window, store,
                                                curriculum):
    target = curriculum.exercises[0]
    store.set_setting("exercise_timeout", 30)
    view = _open(qt_app, window, target)
    view.editor.set_code("import time\ntime.sleep(30)\n")

    view.run_button.click()
    assert wait_for(qt_app, lambda: view._running, 10), "the run never started"
    # Run has become Stop in the same place on the row.
    assert not view.run_button.isVisible()
    assert view.stop_button.isVisible() and view.stop_button.isEnabled()

    view.stop_button.click()
    assert wait_for(qt_app, lambda: not view._running, 30), "Stop did nothing"
    pump(qt_app)

    assert view.run_button.isVisible() and view.run_button.isEnabled()
    assert not view.stop_button.isVisible()
    assert view.stop_button.text() == "Stop"
    assert "Stopped." in _text(view.results)
    # A run the learner called off is not an attempt against them.
    assert store.exercise(target.id)["attempts"] == 0
    assert store.exercise(target.id)["status"] == "new"


def test_a_cancelled_result_carries_the_flag_rather_than_a_failure():
    from operators_console.core.runner import RunHandle, run_exercise
    from operators_console.core.models import TestCase as Case

    handle = RunHandle()
    handle.cancel()             # Stop pressed before the process even exists
    result = run_exercise("value = 1\n", [Case("c", "assert value == 1")],
                          timeout=20, handle=handle)
    assert result.cancelled and not result.ok
    assert result.summary == "Stopped."


# ---------------------------------------------------------------------------
# 3 - the hint ladder
# ---------------------------------------------------------------------------

def test_the_hint_ladder_stops_at_the_last_hint(qt_app, window, curriculum):
    target = _with_hints(curriculum, 2)
    view = _open(qt_app, window, target)
    from operators_console.ui.views.practice import _hints_for
    # The written hints, then the shape of an answer.
    total = len(_hints_for(target))
    assert total == len(target.hints) + 1

    for _ in range(total):
        view.hint_button.click()
    assert view.hint_index == total
    assert "Hint %d of %d" % (total, total) in view.hint_label.text()
    # It used to wrap to hint one while the label kept counting.
    assert view.hint_label.text().count("Hint ") == total
    assert not view.hint_button.isEnabled()
    assert view.hint_button.toolTip() == "That is every hint for this one."

    view.hint_button.click()            # a press that can no longer mislead
    assert view.hint_index == total
    assert "Hint %d of %d" % (total + 1, total) not in view.hint_label.text()


def test_every_hint_read_so_far_stays_on_screen(qt_app, window, curriculum):
    target = _with_hints(curriculum, 2)
    view = _open(qt_app, window, target)
    view.hint_button.click()
    view.hint_button.click()
    # Rendered: backticks become code, so compare as the learner reads it.
    from operators_console.ui.views.practice import _markup
    shown = view.hint_label.text()
    assert _markup(target.hints[0]) in shown and _markup(target.hints[1]) in shown


def test_hints_used_is_recorded_and_shown_in_the_meta_line(
        qt_app, window, store, curriculum):
    target = _with_hints(curriculum, 2)
    view = _open(qt_app, window, target)

    view.hint_button.click()
    assert store.exercise(target.id)["hints_used"] == 1
    assert "1 hint used" in view.ex_meta.text()

    view.hint_button.click()
    assert store.exercise(target.id)["hints_used"] == 2
    assert "2 hints used" in view.ex_meta.text()


def test_reopening_an_exercise_does_not_inflate_the_hint_count(
        qt_app, window, store, curriculum):
    first, second = _with_hints(curriculum, 2), curriculum.exercises[3]
    view = _open(qt_app, window, first)
    view.hint_button.click()
    _open(qt_app, window, second)
    view = _open(qt_app, window, first)
    view.hint_button.click()            # the same first hint, read again
    assert store.exercise(first.id)["hints_used"] == 1


# ---------------------------------------------------------------------------
# 8 - an exercise with no hints
# ---------------------------------------------------------------------------

def test_an_exercise_with_no_hints_shows_a_disabled_button(qt_app, window,
                                                           curriculum):
    target = _without_hints(curriculum)
    if target is None:
        pytest.skip("every exercise in the bank ships with hints")
    view = _open(qt_app, window, target)
    # Visible, so the row does not silently change shape, and it says why.
    assert view.hint_button.isVisible()
    assert not view.hint_button.isEnabled()
    assert view.hint_button.toolTip() == "No hints for this one."


# ---------------------------------------------------------------------------
# 4 - reading the answer is shown, and can be taken back
# ---------------------------------------------------------------------------

def test_reading_the_answer_gives_the_list_a_third_status(qt_app, window,
                                                          store, curriculum):
    from operators_console.ui.views.practice import STATUS_WORD
    target = next(e for e in curriculum.exercises if e.solution)
    view = _open(qt_app, window, target)
    store.record_exercise_run(target.id, target.solution, True)
    store.reveal_solution(target.id)
    view._fill_list()
    view._show_header(target)

    from PySide6.QtCore import Qt
    item = view.list.item(view.list.currentRow())
    accessible = item.data(Qt.ItemDataRole.AccessibleTextRole)
    assert STATUS_WORD["revealed"] == "solved after reading"
    assert "solved after reading" in accessible
    assert view.ex_status.text() == "PASSED - READ"


def test_an_answer_read_without_passing_reads_differently(qt_app, window,
                                                          store, curriculum):
    target = next(e for e in curriculum.exercises if e.solution)
    view = _open(qt_app, window, target)
    store.reveal_solution(target.id)
    view._fill_list()
    view._show_header(target)
    assert view.ex_status.text() == "ANSWER READ"

    from PySide6.QtCore import Qt
    item = view.list.item(view.list.currentRow())
    assert "not passed yet" in item.data(Qt.ItemDataRole.AccessibleTextRole)


def test_the_show_filter_can_list_only_the_revealed_ones(qt_app, window,
                                                         store, curriculum):
    target = curriculum.exercises[1]
    view = _open(qt_app, window, target)
    store.reveal_solution(target.id)
    view.status_filter.setCurrentIndex(view.status_filter.findText("Revealed"))
    pump(qt_app)
    assert view.list.count() == 1
    assert view.current.id == target.id


def test_try_again_puts_the_starter_back_and_unsolves_the_exercise(
        qt_app, window, store, curriculum):
    target = next(e for e in curriculum.exercises if e.solution)
    view = _open(qt_app, window, target)
    store.record_exercise_run(target.id, "mine = 1\n", True)
    store.reveal_solution(target.id)
    view._load(target)
    assert view.again_button.isVisible()

    view.again_button.click()
    assert view.editor.code() == target.starter
    state = store.exercise(target.id)
    assert state["status"] == "new"
    assert state["attempts"] == 0
    assert not state["revealed"]
    assert target.id not in store.passed_exercise_ids()
    # One undoable edit, exactly like Reset.
    view.editor.undo()
    assert view.editor.code() == "mine = 1\n"


def test_try_again_is_hidden_on_an_exercise_that_was_never_solved(
        qt_app, window, curriculum):
    view = _open(qt_app, window, curriculum.exercises[2])
    assert not view.again_button.isVisible()


# ---------------------------------------------------------------------------
# 5 - the last version that passed
# ---------------------------------------------------------------------------

def test_the_passing_code_is_kept_and_can_be_restored(qt_app, window, store,
                                                      curriculum):
    target = curriculum.exercises[2]
    view = _open(qt_app, window, target)
    good = "answer = 42\n"
    store.record_exercise_run(target.id, good, True)
    assert store.exercise(target.id)["passing_code"] == good

    view._load(target)
    view.editor.replace_code("answer = 'broken now'\n")
    pump(qt_app)
    assert view.restore_button.isVisible()

    view.restore_button.click()
    assert view.editor.code() == good
    assert store.exercise(target.id)["code"] == good
    assert not view.restore_button.isVisible()


def test_a_later_failure_does_not_overwrite_the_passing_code(store,
                                                             curriculum):
    target = curriculum.exercises[2]
    store.record_exercise_run(target.id, "good = 1\n", True)
    store.record_exercise_run(target.id, "broken = 1\n", False)
    state = store.exercise(target.id)
    assert state["code"] == "broken = 1\n"
    assert state["passing_code"] == "good = 1\n"
    assert state["status"] == "passed"


def test_restore_is_offered_only_when_there_is_something_to_restore(
        qt_app, window, curriculum):
    view = _open(qt_app, window, curriculum.exercises[2])
    assert not view.restore_button.isVisible()


# ---------------------------------------------------------------------------
# 6 - finding one exercise among ninety-six
# ---------------------------------------------------------------------------

def test_the_search_narrows_the_list_by_title_topic_and_brief(
        qt_app, window, curriculum):
    target = curriculum.exercises[0]
    view = _open(qt_app, window, target)
    view.phase_filter.setCurrentIndex(0)
    pump(qt_app)
    everything = view.list.count()

    view.search.setText(target.title)
    pump(qt_app)
    assert 0 < view.list.count() < everything
    assert view.current.id == target.id

    view.search.setText("zzzz-nothing-matches-this")
    pump(qt_app)
    assert view.list.count() == 0
    assert view.current is None
    assert "Nothing matches" in view.ex_title.text()

    view.search.clear()
    pump(qt_app)
    assert view.list.count() == everything


def test_the_difficulty_filter_keeps_only_that_level(qt_app, window,
                                                     curriculum):
    view = _open(qt_app, window, curriculum.exercises[0])
    view.phase_filter.setCurrentIndex(0)
    pump(qt_app)
    for level in range(1, 6):
        index = view.difficulty_filter.findData(level)
        assert index >= 0
        view.difficulty_filter.setCurrentIndex(index)
        pump(qt_app)
        expected = [e for e in curriculum.exercises if e.difficulty == level]
        assert view.list.count() == len(expected), level
    view.difficulty_filter.setCurrentIndex(0)
    pump(qt_app)
    assert view.list.count() == len(curriculum.exercises)


def test_the_selection_survives_a_filter_that_still_shows_it(qt_app, window,
                                                             curriculum):
    target = curriculum.exercises[0]
    view = _open(qt_app, window, target)
    index = view.difficulty_filter.findData(target.difficulty)
    view.difficulty_filter.setCurrentIndex(index)
    pump(qt_app)
    assert view.current.id == target.id


def test_navigating_to_an_exercise_a_filter_hides_still_arrives(
        qt_app, window, curriculum):
    view = _open(qt_app, window, curriculum.exercises[0])
    view.search.setText("zzzz-nothing-matches-this")
    pump(qt_app)
    assert view.list.count() == 0

    target = curriculum.exercises[4]
    window.go("practice", target.id)
    pump(qt_app)
    assert view.current is not None and view.current.id == target.id
    assert view.search.text() == ""


def test_the_counter_says_how_many_are_shown_when_a_filter_is_on(
        qt_app, window, curriculum):
    view = _open(qt_app, window, curriculum.exercises[0])
    view.phase_filter.setCurrentIndex(0)
    pump(qt_app)
    assert "shown" not in view.counter.text()
    view.difficulty_filter.setCurrentIndex(
        view.difficulty_filter.findData(5))
    pump(qt_app)
    assert "shown" in view.counter.text()


# ---------------------------------------------------------------------------
# 7 - Next on the last exercise
# ---------------------------------------------------------------------------

def test_next_is_disabled_on_the_last_exercise_and_says_why(qt_app, window,
                                                            curriculum):
    view = _open(qt_app, window, curriculum.exercises[0])
    view.phase_filter.setCurrentIndex(0)
    pump(qt_app)
    assert view.next_button.isEnabled()
    assert view.next_button.toolTip() == "The next exercise"

    view.list.setCurrentRow(view.list.count() - 1)
    pump(qt_app)
    assert not view.next_button.isEnabled()
    assert view.next_button.toolTip() == "That is the last one in this filter."


# ---------------------------------------------------------------------------
# 9 - what one failed attempt is called
# ---------------------------------------------------------------------------

def test_one_failed_attempt_is_not_called_in_progress(qt_app, window, store,
                                                      curriculum):
    from operators_console.ui.views.practice import STATUS_MARK, STATUS_WORD
    assert "IN PROGRESS" not in STATUS_MARK.values()
    assert STATUS_MARK["attempted"] == "ATTEMPTED"
    assert STATUS_WORD["attempted"] == "not passed yet"

    target = curriculum.exercises[3]
    view = _open(qt_app, window, target)
    store.record_exercise_run(target.id, "wrong = 1\n", False)
    view._show_header(target)
    view._fill_list()
    assert view.ex_status.text() == "ATTEMPTED"

    from PySide6.QtCore import Qt
    item = view.list.item(view.list.currentRow())
    assert "not passed yet" in item.data(Qt.ItemDataRole.AccessibleTextRole)


# ---------------------------------------------------------------------------
# 10 - what the exported report carries
# ---------------------------------------------------------------------------

def test_the_report_carries_notes_and_a_table_of_every_phase(
        curriculum, store, progress, tmp_path):
    from operators_console.core.export import export_report

    phase = curriculum.phases[1]
    store.set_note("phase:" + phase.id, "Comprehensions took me two days.")
    project = curriculum.projects[0]
    store.set_project(project.id, notes="The repo is half finished.")
    store.reveal_solution(curriculum.exercises[0].id)

    target = export_report(curriculum, store, progress, tmp_path / "r.md")
    text = target.read_text(encoding="utf-8")

    assert "## Notes" in text
    assert "Comprehensions took me two days." in text
    assert "%s %s" % (phase.num, phase.name) in text
    assert "The repo is half finished." in text
    assert "Project: %s" % project.title in text

    assert "### Every phase in detail" in text
    assert "| Phase | Checks | Exercises | Gate | Best quiz | Projects |" \
        in text
    for one in curriculum.phases:
        assert "| %s %s |" % (one.num, one.name) in text
    assert "| Exercises whose answer was read | 1 |" in text


def test_a_report_with_no_notes_leaves_the_section_out(curriculum, store,
                                                       progress, tmp_path):
    from operators_console.core.export import export_report
    text = export_report(curriculum, store, progress,
                         tmp_path / "r.md").read_text(encoding="utf-8")
    assert "## Notes" not in text
    assert "### Every phase in detail" in text


# ---------------------------------------------------------------------------
# the store underneath all of it
# ---------------------------------------------------------------------------

def test_a_store_written_before_the_new_columns_gains_them(tmp_path):
    """The columns reach an existing file, not only a brand new one."""
    import sqlite3

    path = tmp_path / "old.db"
    db = sqlite3.connect(path)
    db.executescript(
        "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);"
        "INSERT INTO meta VALUES ('schema_version','1');"
        "CREATE TABLE exercise_state ("
        "  exercise_id TEXT PRIMARY KEY,"
        "  code        TEXT NOT NULL DEFAULT '',"
        "  status      TEXT NOT NULL DEFAULT 'new',"
        "  attempts    INTEGER NOT NULL DEFAULT 0,"
        "  passed_at   TEXT,"
        "  updated_at  TEXT NOT NULL,"
        "  revealed    INTEGER NOT NULL DEFAULT 0);"
        "INSERT INTO exercise_state(exercise_id,code,status,attempts,"
        "updated_at) VALUES ('p01.001','mine = 1','attempted',4,'2026-01-01');")
    db.commit()
    db.close()

    from operators_console.core.storage import Store
    store = Store(path)
    try:
        row = store.exercise("p01.001")
        assert row["hints_used"] == 0 and row["passing_code"] == ""
        assert row["code"] == "mine = 1" and row["attempts"] == 4
        store.use_hint("p01.001", 2)
        assert store.hints_used("p01.001") == 2
    finally:
        store.close()


def test_use_hint_keeps_the_highest_count_rather_than_adding_up(store):
    store.use_hint("p01.001", 2)
    store.use_hint("p01.001", 1)
    assert store.hints_used("p01.001") == 2
    store.use_hint("p01.001", 3)
    assert store.hints_used("p01.001") == 3


def test_use_hint_on_its_own_counts_one(store):
    store.use_hint("p01.001")
    assert store.hints_used("p01.001") == 1


def test_exercise_rows_answers_status_reveal_and_hints_in_one_pass(store):
    store.record_exercise_run("p01.001", "a = 1\n", True)
    store.reveal_solution("p01.001")
    store.use_hint("p01.001", 2)
    rows = store.exercise_rows()
    assert rows["p01.001"]["status"] == "passed"
    assert rows["p01.001"]["revealed"]
    assert rows["p01.001"]["hints_used"] == 2
    assert rows["p01.001"]["passing_code"] == "a = 1\n"


def test_rearm_keeps_the_hints_and_the_passing_code(store):
    store.record_exercise_run("p01.001", "a = 1\n", True)
    store.use_hint("p01.001", 2)
    store.reveal_solution("p01.001")
    store.rearm_exercise("p01.001")
    row = store.exercise("p01.001")
    assert row["status"] == "new" and row["attempts"] == 0
    assert not row["revealed"] and row["passed_at"] is None
    # Nothing the learner is trying to undo goes with it.
    assert row["hints_used"] == 2
    assert row["passing_code"] == "a = 1\n"


def test_revealed_exercise_ids_lists_only_the_read_ones(store):
    store.reveal_solution("p01.001")
    store.record_exercise_run("p01.002", "a = 1\n", True)
    assert store.revealed_exercise_ids() == {"p01.001"}


def test_a_backup_taken_now_still_restores(store, curriculum):
    """The new columns must not break the round trip."""
    store.record_exercise_run("p01.001", "a = 1\n", True)
    store.use_hint("p01.001", 2)
    payload = store.dump()
    store.reset_progress()
    store.restore(payload)
    row = store.exercise("p01.001")
    assert row["hints_used"] == 2 and row["passing_code"] == "a = 1\n"


def test_an_older_backup_without_the_new_columns_still_restores(store):
    store.record_exercise_run("p01.001", "a = 1\n", True)
    payload = store.dump()
    for row in payload["tables"]["exercise_state"]:
        row.pop("hints_used", None)
        row.pop("passing_code", None)
    store.restore(payload)
    row = store.exercise("p01.001")
    assert row["hints_used"] == 0 and row["passing_code"] == ""
    assert row["status"] == "passed"

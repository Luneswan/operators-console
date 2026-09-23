"""Practice: all ninety-six exercises, graded three ways each."""
from __future__ import annotations

import time

import pytest

from .harness import (
    REC, answering, click, pump, screenshot, step, wait_for,
)

pytestmark = [pytest.mark.walk]

RUN_SECONDS = 60


def _open(walk_app, window, exercise_id):
    window.go("practice", exercise_id)
    pump(walk_app, 2)
    view = window.views["practice"]
    assert view.current is not None and view.current.id == exercise_id, (
        "asked for %s, the page shows %s"
        % (exercise_id, view.current.id if view.current else None))
    return view


def _run_and_wait(walk_app, view, seconds=RUN_SECONDS):
    click(walk_app, view.run_button, pump_rounds=1)
    finished = wait_for(walk_app, lambda: view.run_button.isEnabled(), seconds)
    assert finished, "the Run button never came back"
    return finished


@pytest.mark.walk_fast
def test_the_filters_narrow_the_list(walk_app, window, curriculum):
    view = _open(walk_app, window, curriculum.exercises[0].id)
    phases = sorted({e.phase for e in curriculum.exercises})
    with step(walk_app, "practice", "filter the list by every phase", window):
        for pid in phases:
            index = view.phase_filter.findData(pid)
            assert index >= 0, pid
            view.phase_filter.setCurrentIndex(index)
            pump(walk_app, 1)
            assert view.list.count() == len(curriculum.exercises_for(pid))
        view.phase_filter.setCurrentIndex(0)
        pump(walk_app, 1)
        assert view.list.count() == len(curriculum.exercises)
    REC.bump("practice phase filters used", len(phases))

    with step(walk_app, "practice", "switch the status filter three ways",
              window):
        for mode in ("Not passed", "Passed", "All"):
            view.status_filter.setCurrentIndex(
                view.status_filter.findText(mode))
            pump(walk_app, 1)
        assert view.list.count() == len(curriculum.exercises)

    with step(walk_app, "practice", "walk the list with Next exercise",
              window):
        view.list.setCurrentRow(0)
        pump(walk_app, 1)
        for _ in range(5):
            row = view.list.currentRow()
            click(walk_app, view.next_button, pump_rounds=1)
            assert view.list.currentRow() == row + 1


@pytest.mark.walk_fast
def test_an_endless_loop_times_out_and_keeps_your_work(walk_app, window,
                                                       store, curriculum):
    store.set_setting("exercise_timeout", 3)
    target = curriculum.exercises[0]
    view = _open(walk_app, window, target.id)
    endless = "while True:\n    pass  # my work in progress\n"
    with step(walk_app, "practice", "run an endless loop and wait it out",
              window, budget=12000):
        view.editor.set_code(endless)
        _run_and_wait(walk_app, view, seconds=40)
        assert view.editor.code() == endless, "the editor lost the learner's text"
        assert view.run_button.text() == "Run checks"
        assert store.exercise(target.id)["code"] == endless
    store.set_setting("exercise_timeout", 10)
    REC.bump("endless loops timed out", 1)


@pytest.mark.walk_fast
def test_reading_the_answer_early_asks_first(walk_app, window, store,
                                             curriculum):
    target = [e for e in curriculum.exercises if e.solution][1]
    view = _open(walk_app, window, target.id)
    before = len(REC.dialogs)
    with step(walk_app, "practice", "ask for the solution before passing",
              window, allow_dialog=True):
        with answering(messagebox="Keep trying"):
            click(walk_app, view.solution_button)
        assert len(REC.dialogs) > before, "no confirmation was shown"
        assert not store.exercise(target.id).get("revealed"), (
            "declining the warning still marked the exercise as revealed")
    with step(walk_app, "practice", "insist on the solution", window,
              allow_dialog=True):
        with answering(messagebox="Show it anyway"):
            click(walk_app, view.solution_button)
        assert store.exercise(target.id).get("revealed")


@pytest.mark.walk_fast
def test_reset_puts_the_starter_back(walk_app, window, store, curriculum):
    target = curriculum.exercises[2]
    view = _open(walk_app, window, target.id)
    with step(walk_app, "practice", "type, then press Reset", window):
        view.editor.set_code("# scribbled over\n")
        pump(walk_app)
        click(walk_app, view.reset_button)
        assert view.editor.code() == target.starter
        assert store.exercise(target.id)["code"] == target.starter


@pytest.mark.walk_full
def test_every_exercise_grades_an_empty_editor_a_wrong_answer_and_the_answer(
        walk_app, window, store, curriculum):
    """The whole bank, three submissions each, through the real page.

    The reference solution is the one shipped with the exercise - the same
    source ``tests/test_content_solutions.py`` grades - so a solution that
    passes the runner but not the interface shows up here.
    """
    empty_passed, starter_passed, solution_failed = [], [], []
    no_hints, hidden_results = [], []
    for exercise in curriculum.exercises:
        view = _open(walk_app, window, exercise.id)

        with step(walk_app, "practice", "%s: read the brief" % exercise.id,
                  window):
            assert view.ex_title.text() == exercise.title
            assert view.prompt.text()
            assert view.editor.code() == exercise.starter

        with step(walk_app, "practice", "%s: reveal every hint" % exercise.id,
                  window):
            if exercise.hints:
                for index in range(len(exercise.hints)):
                    click(walk_app, view.hint_button, pump_rounds=0)
                    assert not view.hint_label.isHidden()
                    assert exercise.hints[index] in view.hint_label.text()
                # One more press holds at the last hint: it used to wrap
                # round to the first while the label still said "3 of 3".
                click(walk_app, view.hint_button, pump_rounds=0)
                assert exercise.hints[-1] in view.hint_label.text()
            else:
                no_hints.append(exercise.id)
                assert not view.hint_button.isEnabled()

        with step(walk_app, "practice", "%s: run an empty editor"
                  % exercise.id, window):
            view.editor.set_code("")
            _run_and_wait(walk_app, view)
            if store.exercise(exercise.id)["status"] == "passed":
                empty_passed.append(exercise.id)
            # The panel is filled and then hidden again; its contents are
            # the honest signal here. See the finding raised below.
            assert view.results.box.count() > 0
            if view.results.isHidden():
                hidden_results.append(exercise.id)

        with step(walk_app, "practice", "%s: run the untouched starter"
                  % exercise.id, window):
            view.editor.set_code(exercise.starter)
            _run_and_wait(walk_app, view)
            if store.exercise(exercise.id)["status"] == "passed":
                starter_passed.append(exercise.id)

        with step(walk_app, "practice", "%s: run the reference solution"
                  % exercise.id, window):
            view.editor.set_code(exercise.solution)
            _run_and_wait(walk_app, view)
            state = store.exercise(exercise.id)
            if state["status"] != "passed":
                solution_failed.append(exercise.id)
            assert state["attempts"] >= 3

        with step(walk_app, "practice", "%s: read the solution once passed"
                  % exercise.id, window):
            click(walk_app, view.solution_button, pump_rounds=0)
            assert store.exercise(exercise.id).get("revealed")

        REC.bump("exercises fully exercised")
        REC.bump("graded submissions", 3)

    if empty_passed:
        REC.find("blocker", "practice",
                 "an empty editor passes the checks",
                 "Open the exercise, clear the editor, press Run checks.",
                 "exercises: %s" % empty_passed)
    if starter_passed:
        REC.find("blocker", "practice",
                 "the untouched starter already passes",
                 "Open the exercise and press Run checks without typing.",
                 "exercises: %s" % starter_passed)
    if solution_failed:
        REC.find("blocker", "practice",
                 "the shipped solution does not pass its own checks",
                 "Open the exercise, press Show solution, paste it, Run.",
                 "exercises: %s" % solution_failed)
    if hidden_results:
        REC.find("blocker", "practice",
                 "the grading result is hidden the instant it is drawn",
                 "Open any exercise, press Run checks: the result panel is "
                 "filled and then hidden again before it can be read.",
                 "%d of %d exercises. PracticeView._on_result calls "
                 "_render_result, which shows the panel, and then "
                 "_fill_list, whose re-selection re-enters _on_select -> "
                 "_load, which runs results.setVisible(False)."
                 % (len(hidden_results), len(curriculum.exercises)))
    if no_hints:
        REC.find("polish", "practice", "exercises that ship with no hints",
                 "Open the exercise: the Hint button is there but disabled, "
                 "and says so. Content still to write, not a defect.",
                 "exercises: %s" % no_hints)
    assert not empty_passed and not starter_passed and not solution_failed

    with step(walk_app, "practice", "the counter agrees with the store",
              window):
        passed = len(store.passed_exercise_ids())
        assert "%d of %d passed" % (passed, len(curriculum.exercises)) \
            in view.counter.text()
        assert passed == len(curriculum.exercises)


@pytest.mark.walk_fast
def test_the_result_panel_survives_being_drawn(walk_app, window, store,
                                               curriculum):
    """Press Run checks and look at what the learner is left with."""
    target = curriculum.exercises[0]
    view = _open(walk_app, window, target.id)
    loads = []
    original = view._load
    view._load = lambda exercise: (loads.append(exercise.id),
                                   original(exercise))[1]
    view.editor.set_code(target.solution)
    if target.hints:
        click(walk_app, view.hint_button, pump_rounds=0)
        assert not view.hint_label.isHidden()
    with step(walk_app, "practice", "press Run checks and read the result",
              window):
        _run_and_wait(walk_app, view)
        assert store.exercise(target.id)["status"] == "passed"
        assert view.results.box.count() > 0, "nothing was rendered at all"
        if view.results.isHidden():
            shot = screenshot(window, "W-practice-results-hidden")
            REC.find("blocker", "practice",
                     "the grading result is hidden the instant it is drawn",
                     "Open Practice, pick any exercise, press Run checks. The "
                     "result panel is filled and then hidden again, so the "
                     "learner is told nothing.",
                     "_on_result -> _render_result shows the panel, then "
                     "_fill_list re-selects the same row, which re-enters "
                     "_on_select -> _load -> results.setVisible(False). "
                     "_load was re-entered after the run: %s" % loads, shot)
        if target.hints and view.hint_label.isHidden():
            REC.find("major", "practice",
                     "the hint you opened closes itself when you run",
                     "Open Practice, press Hint, then press Run checks: the "
                     "hint disappears and the counter restarts at 1.",
                     "the same _load re-entry resets hint_index to 0")
    view._load = original


@pytest.mark.walk_fast
def test_quitting_while_a_run_is_in_flight(walk_app, ctx, store, curriculum,
                                           quiet_update_check, capfd):
    """A learner who closes the window mid-run should not be shouted at.

    PySide6 swallows a failure inside ``QRunnable.run`` and prints it from C,
    so this one is read off the real file descriptor rather than from the
    excepthook sensor.
    """
    from operators_console.ui.main_window import MainWindow
    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 2)
    store.set_setting("exercise_timeout", 10)
    main.go("practice", curriculum.exercises[0].id)
    pump(walk_app, 2)
    view = main.views["practice"]
    view.editor.set_code("import time\ntime.sleep(2)\n")
    capfd.readouterr()
    noise = ""
    with step(walk_app, "practice", "close the window while a run is in "
                                    "flight", main, allow_dialog=True,
              budget=15000, expect_exception=True):
        click(walk_app, view.run_button, pump_rounds=1)
        main.close()
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            pump(walk_app, 2)
            noise += capfd.readouterr().err
            if "Error calling Python override" in noise:
                break
            time.sleep(0.05)
    trouble = [text for text in REC.exceptions
               if "Cannot operate on a closed database" in text
               and "_on_result" in text]
    if trouble:
        REC.find("major", "practice",
                 "quitting mid-run crashes the handler that reports the "
                 "result",
                 "Open Practice, press Run checks, close the window before "
                 "the run finishes.",
                 "PracticeView._on_result runs after MainWindow.closeEvent "
                 "has closed the store. " + trouble[-1][-700:])
    if "Error calling Python override" in noise:
        REC.find("minor", "practice",
                 "closing the window mid-run raises in the worker thread",
                 "Open Practice, press Run checks on something slow, close "
                 "the window before it finishes.",
                 noise.strip()[-700:])
    if not trouble and "Error calling Python override" not in noise:
        REC.bump("clean shutdowns with a run in flight")

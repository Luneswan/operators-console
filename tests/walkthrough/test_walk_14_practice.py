"""Practice, pressed where walk 04 never could.

Walk 04 proves the bank grades. This one drives the controls that did not
exist while it was written: Stop, the search and level filters, Restore my
passing version and Try this one again from scratch - and it reads what a
failing check actually says now, which is the whole point of the change.
"""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel

from .harness import REC, answering, click, pump, step, wait_for

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]

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
    finished = wait_for(walk_app, lambda: not view._running, seconds)
    assert finished, "the run never finished"
    pump(walk_app, 2)


def _panel_text(view) -> str:
    return "\n".join(child.text() for child in view.results.findChildren(QLabel))


def _with_hints(curriculum, count: int = 2):
    return next(e for e in curriculum.exercises if len(e.hints) >= count)


# ---------------------------------------------------------------------------
# a failing check has to explain itself
# ---------------------------------------------------------------------------

def test_a_failing_check_says_why_it_failed(walk_app, window, store,
                                            curriculum):
    """The defect the page existed with: five identical "Wrong result." lines."""
    target = curriculum.exercises[0]
    view = _open(walk_app, window, target.id)
    with step(walk_app, "practice", "submit an empty editor and read the "
                                    "reasons", window, budget=20000):
        view.editor.set_code("")
        _run_and_wait(walk_app, view)
        failures = [c for c in _cases(view) if not c.passed]
        assert failures, "an empty editor passed every check"
        said = _panel_text(view)
        assert "Wrong result." not in said, (
            "the grader is still saying nothing: %s" % said[:400])
        for case in failures:
            assert case.message.strip(), "%s said nothing" % case.name
            assert len(case.message) > len(case.name), case.message
        assert any(case.detail.strip() for case in failures), (
            "no check offered any detail under its sentence")
    REC.bump("failing checks that explained themselves", len(failures))

    with step(walk_app, "practice", "put the real answer back", window,
              budget=20000):
        view.editor.set_code(target.solution)
        _run_and_wait(walk_app, view)
        assert store.exercise(target.id)["status"] == "passed"
        assert all(case.passed for case in _cases(view))


def test_a_nearly_right_answer_is_told_exactly_what_is_wrong(
        walk_app, window, store, curriculum):
    """One real exercise, one believable slip, read the way a learner reads it."""
    target = curriculum.exercise("p01.001")
    if target is None:
        pytest.skip("the greeting exercise is no longer in the bank")
    view = _open(walk_app, window, target.id)
    with step(walk_app, "practice", "forget the exclamation mark and run",
              window, budget=20000):
        view.editor.set_code('def greet(name):\n'
                             '    return "Hello, " + name\n')
        _run_and_wait(walk_app, view)
        failing = [case for case in _cases(view) if not case.passed]
        assert len(failing) == 3, [c.name for c in failing]
        for case in failing:
            assert case.message == ("Your text stops early - '!' is missing "
                                    "from the end."), case.message
            assert case.detail.startswith("expected "), case.detail
        # Each check shows the values it actually used, not a generic line.
        said = _panel_text(view)
        assert "'Hello, Ada!'" in said and "'Hello, Linus!'" in said
        assert len({case.detail for case in failing}) == 3

    with step(walk_app, "practice", "get one character wrong instead", window,
              budget=20000):
        view.editor.set_code('def greet(name):\n'
                             '    return "Hello: " + name + "!"\n')
        _run_and_wait(walk_app, view)
        failing = [case for case in _cases(view) if not case.passed]
        assert failing
        assert failing[0].message == ("They differ at character 6: expected "
                                      "',', got ':'."), failing[0].message
        # The caret excerpt is drawn under the character that differs.
        assert "^" in failing[0].detail

    with step(walk_app, "practice", "get only the capital wrong", window,
              budget=20000):
        view.editor.set_code('def greet(name):\n'
                             '    return "hello, " + name + "!"\n')
        _run_and_wait(walk_app, view)
        failing = [case for case in _cases(view) if not case.passed]
        assert failing
        assert failing[0].message.startswith(
            "The letters are right but the capitals are not"), \
            failing[0].message
    REC.bump("wrong answers explained down to the character", 1)


def _cases(view):
    """The last result the page rendered, read back off the view."""
    return getattr(view, "_walk_last_cases", ())


@pytest.fixture(autouse=True)
def _remember_cases(monkeypatch):
    """Keep each rendered result, so a test can read the cases it showed."""
    from operators_console.ui.views.practice import PracticeView
    original = PracticeView._render_result

    def remembering(self, result):
        self._walk_last_cases = tuple(result.cases)
        return original(self, result)

    monkeypatch.setattr(PracticeView, "_render_result", remembering)


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------

def test_an_endless_loop_can_be_stopped(walk_app, window, store, curriculum):
    target = curriculum.exercises[0]
    store.set_setting("exercise_timeout", 60)
    view = _open(walk_app, window, target.id)
    mine = "while True:\n    pass  # my work in progress\n"
    with step(walk_app, "practice", "start an endless run and press Stop",
              window, budget=30000):
        view.editor.set_code(mine)
        click(walk_app, view.run_button, pump_rounds=1)
        assert view._running, "the run never started"
        assert view.stop_button.isVisible(), "Run did not become Stop"
        assert not view.run_button.isVisible()

        click(walk_app, view.stop_button, pump_rounds=1)
        assert wait_for(walk_app, lambda: not view._running, 30), (
            "Stop did not stop it")
        pump(walk_app, 2)
        assert "Stopped." in _panel_text(view)
        assert view.run_button.isVisible() and view.run_button.isEnabled()
        assert not view.stop_button.isVisible()
        assert view.editor.code() == mine, "Stop cost the learner their work"
        # A run the learner called off is not an attempt against them.
        assert store.exercise(target.id)["attempts"] == 0
    store.set_setting("exercise_timeout", 10)
    REC.bump("runs stopped by hand", 1)


# ---------------------------------------------------------------------------
# hints
# ---------------------------------------------------------------------------

def test_the_hint_ladder_stops_where_it_should(walk_app, window, store,
                                               curriculum):
    from operators_console.ui.views.practice import _hints_for
    target = _with_hints(curriculum, 2)
    # The written hints, rendered, then the shape of an answer.
    ladder = _hints_for(target)
    total = len(ladder)
    assert total == len(target.hints) + 1
    view = _open(walk_app, window, target.id)
    with step(walk_app, "practice", "read every hint, then press once more",
              window):
        for index in range(total):
            click(walk_app, view.hint_button, pump_rounds=1)
            assert ladder[index][1] in view.hint_label.text()
            # Everything read so far is still on screen.
            for earlier in range(index + 1):
                assert ladder[earlier][1] in view.hint_label.text()
        assert not view.hint_button.isEnabled()
        assert view.hint_button.toolTip() == "That is every hint for this one."
        click(walk_app, view.hint_button, pump_rounds=1)
        assert "Hint %d of %d" % (total + 1, total) not in \
            view.hint_label.text()
        assert "%d hints used" % total in view.ex_meta.text()
        assert store.exercise(target.id)["hints_used"] == total
    REC.bump("hint ladders read to the end", 1)

    hintless = next((e for e in curriculum.exercises if not e.hints), None)
    if hintless is not None:
        view = _open(walk_app, window, hintless.id)
        with step(walk_app, "practice", "meet an exercise with no hints",
                  window):
            assert view.hint_button.isVisible(), "the button vanished again"
            assert not view.hint_button.isEnabled()
            assert view.hint_button.toolTip() == "No hints for this one."
            click(walk_app, view.hint_button, pump_rounds=1)


# ---------------------------------------------------------------------------
# finding one exercise among ninety-six
# ---------------------------------------------------------------------------

def test_the_search_and_the_level_filter(walk_app, window, curriculum):
    target = curriculum.exercises[0]
    view = _open(walk_app, window, target.id)
    view.phase_filter.setCurrentIndex(0)
    pump(walk_app, 2)
    everything = view.list.count()

    with step(walk_app, "practice", "search for one exercise by its title",
              window):
        view.search.setText(target.title)
        pump(walk_app, 2)
        assert 0 < view.list.count() < everything
        assert view.current.id == target.id

    with step(walk_app, "practice", "search for something that is not there",
              window):
        view.search.setText("zzzz-nothing-matches-this")
        pump(walk_app, 2)
        assert view.list.count() == 0
        assert view.current is None
        assert "Nothing matches" in view.ex_title.text()
        assert not view.run_button.isEnabled()

    with step(walk_app, "practice", "clear the search", window):
        view.search.clear()
        pump(walk_app, 2)
        assert view.list.count() == everything

    with step(walk_app, "practice", "filter by every difficulty", window):
        for level in range(1, 6):
            view.difficulty_filter.setCurrentIndex(
                view.difficulty_filter.findData(level))
            pump(walk_app, 1)
            expected = [e for e in curriculum.exercises
                        if e.difficulty == level]
            assert view.list.count() == len(expected), level
            assert "shown" in view.counter.text()
        view.difficulty_filter.setCurrentIndex(0)
        pump(walk_app, 1)
        assert view.list.count() == everything
    REC.bump("practice difficulty filters used", 5)

    with step(walk_app, "practice", "show only the revealed ones", window):
        view.status_filter.setCurrentIndex(
            view.status_filter.findText("Revealed"))
        pump(walk_app, 2)
        assert view.list.count() == len(
            [e for e in curriculum.exercises
             if window.ctx.store.exercise(e.id).get("revealed")])
        view.status_filter.setCurrentIndex(0)
        pump(walk_app, 2)


def test_next_stops_at_the_end_of_the_filter(walk_app, window, curriculum):
    view = _open(walk_app, window, curriculum.exercises[0].id)
    view.phase_filter.setCurrentIndex(0)
    pump(walk_app, 2)
    with step(walk_app, "practice", "walk to the last exercise and press "
                                    "Next again", window):
        assert view.next_button.isEnabled()
        view.list.setCurrentRow(view.list.count() - 2)
        pump(walk_app, 1)
        click(walk_app, view.next_button, pump_rounds=1)
        assert view.list.currentRow() == view.list.count() - 1
        assert not view.next_button.isEnabled()
        assert view.next_button.toolTip() == \
            "That is the last one in this filter."
        click(walk_app, view.next_button, pump_rounds=1)
        assert view.list.currentRow() == view.list.count() - 1


# ---------------------------------------------------------------------------
# the two ways back
# ---------------------------------------------------------------------------

def test_restoring_the_version_that_passed(walk_app, window, store,
                                           curriculum):
    target = curriculum.exercises[0]
    view = _open(walk_app, window, target.id)
    store.set_setting("exercise_timeout", 30)
    with step(walk_app, "practice", "pass the exercise", window,
              budget=40000):
        view.editor.set_code(target.solution)
        _run_and_wait(walk_app, view)
        assert store.exercise(target.id)["status"] == "passed"
        assert store.exercise(target.id)["passing_code"] == target.solution

    with step(walk_app, "practice", "carry on experimenting and break it",
              window):
        view.editor.set_code("# I wondered what would happen\n")
        pump(walk_app, 2)
        assert view.restore_button.isVisible(), (
            "nothing offered the passing version back")

    with step(walk_app, "practice", "press Restore my passing version",
              window):
        click(walk_app, view.restore_button)
        assert view.editor.code() == target.solution
        assert store.exercise(target.id)["code"] == target.solution
        assert not view.restore_button.isVisible()

    with step(walk_app, "practice", "press Reset, then restore once more",
              window):
        click(walk_app, view.reset_button)
        assert view.editor.code() == target.starter
        assert view.restore_button.isVisible(), (
            "Reset left no way back to the version that passed")
        click(walk_app, view.restore_button)
        assert view.editor.code() == target.solution
    REC.bump("passing versions restored", 2)


def test_reading_the_answer_then_trying_again_from_scratch(
        walk_app, window, store, curriculum):
    target = next(e for e in curriculum.exercises[1:] if e.solution)
    view = _open(walk_app, window, target.id)
    with step(walk_app, "practice", "read the answer", window,
              allow_dialog=True):
        with answering(messagebox="Show it anyway"):
            click(walk_app, view.solution_button)
        assert store.exercise(target.id).get("revealed")
        assert view.ex_status.text() == "ANSWER READ"
        assert view.again_button.isVisible()

    from PySide6.QtCore import Qt
    with step(walk_app, "practice", "check the list says so too", window):
        row = view.list.currentRow()
        said = view.list.item(row).data(Qt.ItemDataRole.AccessibleTextRole)
        assert "not passed yet" in said

    with step(walk_app, "practice", "press Try this one again from scratch",
              window):
        click(walk_app, view.again_button)
        state = store.exercise(target.id)
        assert view.editor.code() == target.starter
        assert not state["revealed"]
        assert state["status"] == "new" and state["attempts"] == 0
        assert not view.again_button.isVisible()
    REC.bump("exercises re-armed from scratch", 1)

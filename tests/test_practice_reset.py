"""Reset puts the starter back without destroying the learner's work.

Found 2026-09-22: Reset sits next to Hint, and it replaced the code through
`setPlainText`, which also wipes the editor's undo history - so one misclick
threw away everything typed so far, with no way back.
"""
from __future__ import annotations

from conftest import pump


def _open(qt_app, window, exercise):
    window.go("practice", exercise.id)
    pump(qt_app)
    return window.views["practice"]


def test_reset_can_be_undone_and_the_undo_is_saved(qt_app, window, store,
                                                   curriculum):
    exercise = curriculum.exercises[2]
    view = _open(qt_app, window, exercise)
    mine = "def mine():\n    return 'an hour of work'\n"
    view.editor.replace_code(mine)
    view._save_code()

    view.reset_button.click()
    assert view.editor.code() == exercise.starter
    assert store.exercise(exercise.id)["code"] == exercise.starter

    view.editor.undo()
    assert view.editor.code() == mine
    view._save_code()               # the autosave timer, without the wait
    assert store.exercise(exercise.id)["code"] == mine


def test_reset_says_what_happened_and_how_to_take_it_back(qt_app, window,
                                                          curriculum):
    exercise = curriculum.exercises[2]
    view = _open(qt_app, window, exercise)
    said = []
    window.ctx.toast.connect(said.append)
    view.editor.replace_code("print('changed')\n")

    view.reset_button.click()
    assert said and "Ctrl+Z" in said[-1]


def test_reset_on_untouched_code_changes_nothing(qt_app, window, curriculum):
    exercise = curriculum.exercises[2]
    view = _open(qt_app, window, exercise)
    view.editor.set_code(exercise.starter)
    said = []
    window.ctx.toast.connect(said.append)

    view.reset_button.click()
    assert view.editor.code() == exercise.starter
    assert not view.editor.document().isUndoAvailable()
    assert said == ["This is already the starter code."]


def test_loading_another_exercise_still_starts_a_fresh_history(
        qt_app, window, curriculum):
    """Undo must never pull one exercise's code into another."""
    first, second = curriculum.exercises[2], curriculum.exercises[3]
    view = _open(qt_app, window, first)
    view.editor.replace_code("print('first')\n")
    view = _open(qt_app, window, second)
    assert not view.editor.document().isUndoAvailable()

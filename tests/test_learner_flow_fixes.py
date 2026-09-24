"""What a learner does, pinned against the bugs the 2026-09-22 reviews found.

The layout audit, the skeptic pass and the edge-case sweep each found places
where the app did something other than what the learner meant: results that
vanished after a run, answers that could be counted twice, typing lost on
quit, a page that ignored another copy of the app, a form that kept
yesterday's date, and an update that failed without a word.
"""
from __future__ import annotations

import time

from PySide6.QtCore import QDate

from conftest import pump

from operators_console.core.runner import CaseResult, RunResult


def _open_exercise(qt_app, window, exercise):
    window.go("practice", exercise.id)
    pump(qt_app)
    return window.views["practice"]


def _result(ok):
    return RunResult(ok=ok, cases=(CaseResult("the check", ok,
                                              "" if ok else "Wrong result."),))


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

def test_the_result_and_the_hint_stay_after_a_run(qt_app, window, curriculum):
    """Refilling the list re-selected the exercise, which reloaded it: the
    result the learner had just produced disappeared, and the hint too."""
    exercise = next(e for e in curriculum.exercises if e.hints)
    view = _open_exercise(qt_app, window, exercise)
    view._next_hint()
    view._on_result(exercise.id, _result(False))
    pump(qt_app)
    assert view.results.isVisibleTo(view)
    assert view.hint_label.isVisibleTo(view)


def test_a_run_keeps_the_editors_undo_history(qt_app, window, curriculum):
    exercise = curriculum.exercises[4]
    view = _open_exercise(qt_app, window, exercise)
    view.editor.replace_code("x = 1\n")
    view._on_result(exercise.id, _result(False))
    pump(qt_app)
    assert view.editor.document().isUndoAvailable()


def test_passing_updates_the_status_without_a_reload(qt_app, window,
                                                     curriculum):
    from operators_console.ui.views.practice import STATUS_MARK
    exercise = curriculum.exercises[4]
    view = _open_exercise(qt_app, window, exercise)
    view._on_result(exercise.id, _result(True))
    pump(qt_app)
    assert view.ex_status.text() == STATUS_MARK["passed"]
    assert "1 attempt" in view.ex_meta.text()


def test_after_a_restore_the_editor_shows_the_restored_code(qt_app, window,
                                                            store, curriculum):
    """And the code typed before the restore is never saved over it."""
    exercise = curriculum.exercises[4]
    view = _open_exercise(qt_app, window, exercise)
    view.editor.replace_code("restored = True\n")
    view._save_code()
    snapshot = store.backup(tag="manual")
    view.editor.replace_code("typed afterwards = True\n")
    view._save_code()

    store.restore_snapshot(snapshot)
    view._save_code()               # an autosave that fires after the restore
    assert store.exercise(exercise.id)["code"] == "restored = True\n"
    window.go("today")
    window.go("practice")
    pump(qt_app)
    assert view.editor.code() == "restored = True\n"


# ---------------------------------------------------------------------------
# Quiz and Review: one answer, one rating
# ---------------------------------------------------------------------------

def test_a_quiz_answer_counts_once(qt_app, window, curriculum, monkeypatch):
    quiz = curriculum.quizzes[0]
    window.go("quiz", quiz.id)
    pump(qt_app)
    view = window.views["quiz"]
    rated = []
    monkeypatch.setattr(window.ctx.review, "answer",
                        lambda card, rating, now=None: rated.append(rating))
    view.group.buttons()[0].setChecked(True)
    skip, submit = view._question_controls
    submit.click()
    submit.click()                  # the second press of an impatient learner
    view._answer(0)
    assert len(view.answers) == 1
    assert len(rated) <= 1
    assert not submit.isVisibleTo(view) and not skip.isVisibleTo(view)


def test_a_review_card_is_answered_once(qt_app, window, store, curriculum,
                                        monkeypatch):
    phase = next(p for p in curriculum.phases if curriculum.quizzes_for(p.id))
    store.set_many_checked([i.id for i in phase.items][:3], True)
    window.go("review")
    pump(qt_app)
    view = window.views["review"]
    if view.card is None:
        view.refresh()
        pump(qt_app)
    assert view.card is not None, "no card to review; the test is void"
    applied = []
    monkeypatch.setattr(view, "_rating_buttons",
                        lambda suggested: applied.append("buttons"))
    monkeypatch.setattr(view, "_apply", lambda rating: applied.append(rating))
    skip, action = view._card_controls
    if view.group is not None:
        view.group.buttons()[view.card.correct].setChecked(True)
    action.click()
    action.click()
    assert len(applied) == 1
    assert not action.isVisibleTo(view) and not skip.isVisibleTo(view)


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------

def test_the_log_form_follows_the_calendar_past_midnight(qt_app, window):
    window.go("journal")
    view = window.views["journal"]
    yesterday = QDate.currentDate().addDays(-1)
    view._default_day = yesterday           # the page was built yesterday
    view.date.setDate(yesterday)
    window.go("today")
    window.go("journal")
    assert view.date.date() == QDate.currentDate()


def test_a_date_the_learner_picked_is_kept(qt_app, window):
    window.go("journal")
    view = window.views["journal"]
    chosen = QDate.currentDate().addDays(-3)
    view.date.setDate(chosen)               # backfilling an old entry
    window.go("today")
    window.go("journal")
    assert view.date.date() == chosen


# ---------------------------------------------------------------------------
# Quitting keeps what was just typed
# ---------------------------------------------------------------------------

def test_a_repo_url_typed_then_quit_is_saved(qt_app, window, store,
                                            curriculum):
    """The field saves on focus-out, which Qt used to deliver after the
    store had closed."""
    from PySide6.QtTest import QTest
    from operators_console.core.storage import Store

    window.go("projects")
    pump(qt_app)
    project = curriculum.projects[0]
    card = window.views["projects"].card_for(project.id)
    window.activateWindow()
    card.repo.setFocus()
    pump(qt_app)
    assert card.repo.hasFocus(), "offscreen focus did not take; test is void"
    QTest.keyClicks(card.repo, "https://github.com/me/first-project")
    window.close()
    pump(qt_app)

    reopened = Store()
    try:
        assert reopened.project(project.id)["repo_url"] == \
            "https://github.com/me/first-project"
    finally:
        reopened.close()


# ---------------------------------------------------------------------------
# A second copy of the app
# ---------------------------------------------------------------------------

def test_a_tick_from_another_copy_of_the_app_redraws_the_roadmap(
        qt_app, window, curriculum):
    from operators_console.core.storage import Store

    window.go("roadmap")
    pump(qt_app)
    view = window.views["roadmap"]
    today = time.strftime("%Y-%m-%d")       # the roadmap's dates count from it
    assert view.store_unchanged(today)
    other = Store()
    try:
        phase = next(p for p in curriculum.phases if p.items)
        other.set_checked(phase.items[0].id, True)
    finally:
        other.close()
    assert not view.store_unchanged(today)


# ---------------------------------------------------------------------------
# An update that did not install says so
# ---------------------------------------------------------------------------

def test_a_failed_update_is_explained_and_offered_again(qt_app, window,
                                                        monkeypatch):
    from operators_console.core import updates
    from operators_console.ui.main_window import MainWindow
    from operators_console.ui.updater import UpdateManager

    checks = []
    monkeypatch.setattr(UpdateManager, "maybe_check",
                        lambda self, force=False: checks.append(force))
    updates.record_failure("the download did not match its checksum")
    again = MainWindow(window.ctx)
    try:
        pump(qt_app)
        assert "did not install" in again.status_label.text()
        assert "checksum" in again.status_label.text()
        again._first_check.timeout.emit()
        assert checks == [True], "no fresh check, so no button until tomorrow"
    finally:
        again.deleteLater()
    assert updates.take_failure() == "", "the note must be shown only once"


# ---------------------------------------------------------------------------
# A saved line comes back with a cue, not "this"
# ---------------------------------------------------------------------------

def test_a_concept_card_says_what_to_recall(window, curriculum):
    """It asked "Can you explain, and use, this from memory?" and never said
    what "this" was; the line itself was only on the back."""
    from operators_console.core.review import concept_cue
    item = next(i for p in curriculum.phases for i in p.items
                if len(curriculum.item_text(i.id).split()) > 6)
    window.ctx.review.add_concept(item.id)
    card = next(c for c in window.ctx.review.all_cards() if c.id == item.id)
    assert card.front == concept_cue(card.back)
    assert "this from memory" not in card.front
    assert card.front.rstrip(". ") != card.back.rstrip(". ")


def test_the_cue_is_the_topic_or_half_the_line():
    from operators_console.core.review import concept_cue
    assert concept_cue("Authentication vs authorization \u2014 they are "
                       "different problems.") == \
        "Authentication vs authorization ..."
    assert concept_cue("Sessions vs JWT: tradeoffs, revocation, refresh.") == \
        "Sessions vs JWT ..."
    assert concept_cue("Role and permission checks at the boundary, not "
                       "scattered in handlers.") == \
        "Role and permission checks at ..."
    assert concept_cue("Use <em>git bisect</em>.") == "Use git bisect."


# ---------------------------------------------------------------------------
# The Library scrolls as one page
# ---------------------------------------------------------------------------

def test_the_library_scrolls_as_one_page(qt_app, window):
    """Each tab was its own scroll area inside the scrolling page: a
    260-pixel window on a 640-pixel screen, under a header that never
    scrolled away."""
    from PySide6.QtWidgets import QScrollArea
    window.go("library")
    pump(qt_app)
    view = window.views["library"]
    assert not view.tabs.findChildren(QScrollArea)
    heights = []
    for index in range(view.tabs.count()):
        view.tabs.setCurrentIndex(index)
        pump(qt_app)
        heights.append(view.tabs.sizeHint().height())
    assert len(set(heights)) > 1, "every tab took the tallest tab's height"

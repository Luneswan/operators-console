"""The report form, and the career ladder that shows progress as levels."""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest

from conftest import pump

from operators_console.core import feedback
from operators_console.core.progress import LEVELS, Progress


# -- report or request ------------------------------------------------------

def test_a_bug_report_has_its_sections():
    title, body = feedback.issue_text("bug", " Timer   stuck ", "It froze.",
                                      True, "1. Start a quiz")
    assert title == "Bug: Timer stuck"
    assert "## What happened" in body
    assert "## Steps to reproduce" in body
    assert "App version:" in body


def test_system_details_are_optional():
    _title, body = feedback.issue_text("feature", "Dark map", "Please.", False)
    assert "App version" not in body


def test_empty_fields_are_refused():
    with pytest.raises(ValueError):
        feedback.issue_text("bug", "", "x", True)
    with pytest.raises(ValueError):
        feedback.issue_text("bug", "x", "  ", True)


def test_the_link_opens_githubs_new_issue_page_with_the_text():
    url, complete = feedback.issue_url("bug", "Bug: x", "Details here")
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    assert complete
    assert url.startswith("https://github.com/Luneswan/operators-console/issues/new?")
    assert query["title"] == ["Bug: x"]
    assert query["body"] == ["Details here"]
    assert query["labels"] == ["bug"]


def test_a_long_report_is_cut_and_says_so():
    url, complete = feedback.issue_url("other", "Feedback: x", "word " * 5000)
    assert not complete
    assert len(url) <= feedback.URL_LIMIT
    assert "clipboard" in parse_qs(urlparse(url).query)["body"][0]


def test_the_dialog_never_opens_a_browser_on_bad_input(qt_app, window,
                                                       monkeypatch):
    from operators_console.ui import feedback as dialog_module
    opened = []
    monkeypatch.setattr(dialog_module, "open_url", opened.append)
    dialog = dialog_module.FeedbackDialog(window.ctx, window)
    dialog._open()
    assert opened == []
    assert dialog.status.isVisibleTo(dialog)
    dialog.title.setText("Timer stuck")
    dialog.details.setPlainText("It froze.")
    dialog._open()
    assert len(opened) == 1
    assert opened[0].startswith("https://github.com/")


def test_settings_and_help_reach_the_form(qt_app, window):
    from PySide6.QtWidgets import QPushButton
    window.go("settings")
    pump(qt_app)
    labels = [b.text() for b in window.views["settings"].findChildren(QPushButton)]
    assert "Report a bug..." in labels
    assert "Request a feature..." in labels
    help_texts = [a.text() for m in window.menuBar().actions()
                  for a in (m.menu().actions() if m.menu() else [])]
    assert "Report a problem or request a feature..." in help_texts


# -- the career ladder -------------------------------------------------------

def _prove(store, curriculum, pid):
    """Tick the phase and its gate, pass its quiz, exercises and project."""
    phase = curriculum.phase(pid)
    for item_id in phase.trackable_ids:
        store.set_checked(item_id, True)
    for quiz in curriculum.quizzes_for(pid):
        store.record_quiz(quiz.id, len(quiz.questions), len(quiz.questions), 60)
    for exercise in curriculum.exercises_for(pid):
        store.record_exercise_run(exercise.id, exercise.solution, True)
    for project in curriculum.projects_for(pid):
        store.set_project(project.id, status="shipped")


def test_a_new_learner_is_starting_out(curriculum, store):
    career = Progress(curriculum, store).career()
    assert career.level == 0
    assert career.name == LEVELS[0]
    assert career.next_name == "Beginner"
    assert career.needs == ("Python foundations",)


def test_proving_foundations_climbs_the_ladder(curriculum, store):
    progress = Progress(curriculum, store)
    _prove(store, curriculum, "p01")
    assert progress.career().name == "Beginner"
    for pid in ("p02", "p03"):
        _prove(store, curriculum, pid)
    career = progress.career()
    assert career.name == "Junior"
    assert career.next_name == "Mid-level"


def test_senior_needs_every_core_phase_and_senior_plus_a_mastery_phase(
        curriculum, store):
    store.set_setting("track", "gamedev")
    progress = Progress(curriculum, store)
    track = curriculum.track("gamedev")
    for pid in track.core:
        _prove(store, curriculum, pid)
    assert progress.career().name == "Senior"
    _prove(store, curriculum, "p99")
    career = progress.career()
    assert career.name == "Senior+"
    assert career.top


def test_ticking_alone_does_not_raise_the_level(curriculum, store):
    phase = curriculum.phase("p01")
    for item_id in phase.trackable_ids:
        store.set_checked(item_id, True)
    assert Progress(curriculum, store).career().level == 0


def test_today_shows_the_level(qt_app, window):
    window.go("today")
    pump(qt_app)
    card = window.views["today"].career
    assert card.level.text() == "STARTING OUT"
    assert "Beginner" in card.next.text()


def test_reaching_a_level_is_announced_once(qt_app, window, store, curriculum):
    window.ctx.changed()
    pump(qt_app)
    _prove(store, curriculum, "p01")
    window.ctx.changed()
    pump(qt_app)
    assert "New level: Beginner" in window.status_label.text()
    window.status_label.setText("")
    window.ctx.changed()
    pump(qt_app)
    assert window.status_label.text() == ""

"""The controls the first eleven walks never pressed.

The coverage walk listed them: the help and settings shortcuts, the shortcut
and snapshot dialogs, onboarding's Back and Continue, the update dialog's
button, a quiz's score-page buttons, a concept card's Reveal, the next
exercise, the Open buttons on resources, in the Library and on a project,
and a project's status buttons. Each is pressed here the way a learner
would press it, with no dialog left blocking and no URL really opened.
"""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, shortcut, step, wait_for

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def _starting(root, prefix):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text().startswith(prefix):
            return widget
    return None


# -- help, settings, dialogs ----------------------------------------------


def test_f1_opens_the_shortcut_list_and_ctrl_comma_opens_settings(
        walk_app, window, monkeypatch):
    from operators_console.ui.shortcuts import ShortcutsDialog

    seen = {}

    def run(dialog):
        dialog.show()
        pump(walk_app, 2)
        seen["rows"] = len(dialog.rows)
        click(walk_app, _named(dialog, "Close"))
        return 0
    monkeypatch.setattr(ShortcutsDialog, "exec", run)

    with step(walk_app, "help", "press F1 and close the shortcut list",
              window):
        shortcut(walk_app, window, "F1")
        assert seen.get("rows", 0) > 10
    with step(walk_app, "menu", "press Ctrl+, for Settings", window):
        # The dialog took window activation with it; a shortcut only fires
        # in the active window, as it would for a learner.
        window.activateWindow()
        pump(walk_app, 2)
        shortcut(walk_app, window, "Ctrl+,")
        assert window.current_key == "settings"


def test_the_snapshot_dialog_can_be_cancelled_and_used(walk_app, window,
                                                       store, monkeypatch):
    from operators_console.ui.snapshots import SnapshotDialog

    window.go("settings", "")
    pump(walk_app, 2)
    view = window.views["settings"]

    def cancel(dialog):
        dialog.show()
        pump(walk_app, 2)
        click(walk_app, _named(dialog, "Open the backups folder"))
        click(walk_app, _named(dialog, "Cancel"))
        return dialog.result()
    monkeypatch.setattr(SnapshotDialog, "exec", cancel)
    with step(walk_app, "settings", "open the snapshot list and cancel",
              window):
        click(walk_app, view.restore_button)

    store.set_checked("p01.s0.0", True)
    click(walk_app, view.snapshot_button)
    store.set_checked("p01.s0.0", False)

    def restore(dialog):
        dialog.show()
        pump(walk_app, 2)
        dialog.list.setCurrentRow(0)
        click(walk_app, dialog.restore_button)
        return dialog.result()
    monkeypatch.setattr(SnapshotDialog, "exec", restore)
    with step(walk_app, "settings", "restore the snapshot just taken",
              window):
        click(walk_app, view.restore_button)
        assert store.is_checked("p01.s0.0")
    REC.bump("snapshots restored", 1)


def test_onboarding_goes_forward_and_back(walk_app, ctx, window):
    from operators_console.ui.onboarding import Onboarding

    dialog = Onboarding(ctx, window)
    try:
        dialog.show()
        pump(walk_app, 2)
        with step(walk_app, "onboarding", "Continue, Continue, Back", window):
            click(walk_app, dialog.next_button)
            assert dialog.step == 1
            click(walk_app, dialog.next_button)
            assert dialog.step == 2
            click(walk_app, dialog.back_button)
            assert dialog.step == 1
    finally:
        dialog.close()
        dialog.deleteLater()
        pump(walk_app, 2)


def test_the_update_dialog_reports_a_failed_download(walk_app, ctx, window,
                                                     monkeypatch):
    from operators_console.core import updates
    from operators_console.core.updates import Asset, Release, parse_version
    from operators_console.ui.updater import UpdateDialog

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")

    def offline(*args, **kwargs):
        raise OSError("the network is off for the walk")
    monkeypatch.setattr(updates, "download", offline)

    release = Release(
        version=parse_version("v99.1.0"), tag="v99.1.0", name="A test",
        notes="Notes. " * 60, url="https://example.invalid/release",
        assets=(Asset("operators-console-99.1.0-windows-setup.exe",
                      "https://example.invalid/setup.exe", 24 * 1024 * 1024,
                      sha256="0" * 64),))
    dialog = UpdateDialog(ctx, release, window)
    try:
        dialog.show()
        pump(walk_app, 2)
        with step(walk_app, "update", "press Update and restart while offline",
                  window):
            click(walk_app, dialog.go_button)
            assert wait_for(walk_app,
                            lambda: "failed" in dialog.status.text(), 10)
            assert dialog.go_button.isEnabled(), "a failed download left a dead button"
            click(walk_app, dialog.page_button)
            click(walk_app, dialog.later_button)
    finally:
        dialog.deleteLater()
        pump(walk_app, 2)


# -- pages -----------------------------------------------------------------


def _finish_quiz(walk_app, view):
    for _ in range(80):
        if _named(view, "Other quizzes"):
            return True
        nxt = _named(view, "Next question") or _named(view, "See your score")
        if nxt is not None:
            click(walk_app, nxt)
            continue
        check = _named(view, "Check answer")
        if check is None:
            return False
        view.group.buttons()[0].setChecked(True)
        click(walk_app, check)
    return False


def test_the_score_page_buttons(walk_app, window, curriculum):
    quiz = curriculum.quizzes[0]
    view = window.views["quiz"]

    window.go("quiz", quiz.id)
    pump(walk_app, 2)
    with step(walk_app, "quiz", "finish a quiz and go back to its phase",
              window):
        assert _finish_quiz(walk_app, view)
        click(walk_app, _named(view, "Back to the phase"))
        assert window.current_key == "phase"
        assert window.views["phase"].current_id == quiz.phase

    window.go("quiz", quiz.id)
    pump(walk_app, 2)
    with step(walk_app, "quiz", "finish a quiz and pick another", window):
        assert _finish_quiz(walk_app, view)
        click(walk_app, _named(view, "Other quizzes"))
        assert view.quiz is None


def test_a_concept_card_is_revealed_and_rated(walk_app, window, store,
                                             curriculum):
    from operators_console.core.review import CONCEPT

    phase = next(p for p in curriculum.phases if p.items)
    for item in phase.items[:3]:
        window.ctx.review.add_concept(item.id)
    store.set_setting("new_cards_per_day", 200)
    window.go("review", "")
    pump(walk_app, 2)
    view = window.views["review"]

    with step(walk_app, "review", "skip to a concept card, reveal, rate",
              window):
        for _ in range(60):
            if view.card is None:
                view.refresh()
                pump(walk_app, 2)
            if view.card is None:
                break
            skip, action = view._card_controls
            if view.card.kind == CONCEPT:
                click(walk_app, action)             # Reveal
                good = _starting(view, "Good")
                assert good is not None
                click(walk_app, good)
                REC.bump("concept cards revealed", 1)
                return
            click(walk_app, skip)
        REC.cannot_reach("a concept card in the review session",
                         "the session never offered one")


def test_next_exercise_and_the_resource_open_buttons(walk_app, window,
                                                     curriculum):
    from operators_console.ui.widgets.common import LinkRow

    exercise = curriculum.exercises[0]
    window.go("practice", exercise.id)
    pump(walk_app, 2)
    view = window.views["practice"]
    with step(walk_app, "practice", "press Next", window):
        click(walk_app, view.next_button)
        assert view.current is not None and view.current.id != exercise.id

    phase = next(p for p in curriculum.phases if p.resources)
    window.go("phase", phase.id)
    pump(walk_app, 2)
    rows = [r for r in window.views["phase"].findChildren(LinkRow)
            if r.open_button is not None]
    with step(walk_app, "phase", "open the first resource", window):
        assert rows
        click(walk_app, rows[0].open_button)


def test_every_library_button(walk_app, window):
    from PySide6.QtWidgets import QPushButton

    window.go("library", "")
    pump(walk_app, 2)
    view = window.views["library"]
    pressed = 0
    for index in range(view.tabs.count()):
        view.tabs.setCurrentIndex(index)
        pump(walk_app, 2)
        tab = view.tabs.widget(index)
        with step(walk_app, "library", "press every button on tab %d" % index,
                  window):
            for widget in list(tab.findChildren(QPushButton))[:12]:
                if widget.isVisibleTo(view):
                    click(walk_app, widget)
                    pressed += 1
    REC.bump("library buttons pressed", pressed)
    assert pressed


def test_a_projects_open_and_status_buttons(walk_app, window, store,
                                            curriculum):
    project = curriculum.projects[0]
    window.go("projects", project.id)
    pump(walk_app, 2)
    view = window.views["projects"]
    card = view.card_for(project.id)
    with step(walk_app, "projects", "open the repo link", window):
        card.repo.setText("https://example.invalid/mine")
        card.repo.editingFinished.emit()
        click(walk_app, _named(card, "Open"))
    with step(walk_app, "projects", "press every status button", window):
        for value, widget in card.status_buttons.items():
            click(walk_app, widget)
            assert store.project(project.id)["status"] == value
        click(walk_app, _starting(card, "Go to phase"))
        assert window.current_key == "phase"

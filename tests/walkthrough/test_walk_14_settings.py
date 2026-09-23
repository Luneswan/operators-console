"""Setup, settings and the ways out that were missing.

Everything a learner gained after "my options were not saved and teh
onboarding is ugly": the wizard walked end to end and skipped, the same wizard
run again from Settings, a quiz that can be left and picked up again, a second
copy of the backups on another disk, and an Open button that waits until there
is something to open.
"""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton

from .harness import REC, answering, click, pump, step, type_text

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def _wizard(walk_app, window):
    from operators_console.ui.onboarding import Onboarding
    dialog = Onboarding(window.ctx, window)
    dialog.show()
    pump(walk_app, 4)
    return dialog


# -- the setup wizard ------------------------------------------------------


def test_the_wizard_is_walked_from_the_first_step_to_the_plan(walk_app, window,
                                                              store):
    wizard = _wizard(walk_app, window)
    try:
        with step(walk_app, "onboarding", "type a name and continue", wizard):
            type_text(walk_app, wizard.name, "Walker")
            assert wizard.segments[0].value() == 100
            click(walk_app, wizard.next_button)
            assert wizard.kicker.text() == "STEP 2 OF 4"

        with step(walk_app, "onboarding", "choose an experience card", wizard):
            click(walk_app, wizard.experience_buttons[2])
            assert wizard.experience_buttons[2].isChecked()
            chosen = [o for o in wizard.experience_buttons if o.isChecked()]
            assert len(chosen) == 1, "two answers were chosen at once"
            click(walk_app, wizard.next_button)

        with step(walk_app, "onboarding", "tick two goals", wizard):
            picked = list(wizard.goal_boxes)[:2]
            for gid in picked:
                click(walk_app, wizard.goal_boxes[gid])
            assert wizard.track_name.text(), "no track was suggested"
            assert "core phases" in wizard.track_meta.text()
            click(walk_app, wizard.next_button)

        with step(walk_app, "onboarding", "go back a step and forward again",
                  wizard):
            click(walk_app, wizard.back_button)
            assert wizard.kicker.text() == "STEP 3 OF 4"
            click(walk_app, wizard.next_button)
            assert wizard.next_button.text() == "Build my plan"

        with step(walk_app, "onboarding", "set a pace and build the plan",
                  wizard):
            wizard.hours.setValue(2.5)
            wizard.days.setValue(7)
            pump(walk_app, 1)
            assert "17.5 hours a week" in wizard.pace_preview.text()
            click(walk_app, wizard.check_updates)
            assert not wizard.check_updates.isChecked()
            click(walk_app, wizard.next_button)
            assert store.setting("onboarded") is True
            assert len(store.setting("goals")) == 2
            assert store.setting("check_for_updates") is False
            assert store.setting("learner_name") == "Walker"
    finally:
        wizard.deleteLater()
    REC.bump("onboarding steps walked", 4)


def test_the_wizard_can_always_be_skipped(walk_app, window, store):
    store.set_setting("onboarded", False)
    store.set_setting("started_on", "2026-09-03")
    wizard = _wizard(walk_app, window)
    try:
        with step(walk_app, "onboarding", "skip the whole thing", wizard):
            click(walk_app, wizard.skip_button)
            assert store.setting("onboarded") is True
            assert store.setting("started_on") == "2026-09-03", (
                "skipping moved day one")
    finally:
        wizard.deleteLater()


def test_the_wizard_can_be_run_again_from_settings(walk_app, window):
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    with step(walk_app, "settings", "press Run setup again", window,
              allow_dialog=True):
        click(walk_app, view.setup_button)
        assert view.name.text() == window.ctx.store.setting("learner_name")
    REC.bump("ways back into the setup wizard", 1)


# -- a quiz you can walk away from ----------------------------------------


def test_a_quiz_can_be_left_and_picked_up_again(walk_app, window, store,
                                                curriculum):
    window.go("quiz", "")
    pump(walk_app, 3)
    view = window.views["quiz"]
    quiz = curriculum.quizzes[0]

    with step(walk_app, "quiz", "start one and skip a question", window):
        view._start(quiz)
        pump(walk_app, 2)
        skip = _named(view, "Skip (counts as wrong)")
        assert skip is not None, "Skip still does not say what it costs"
        assert "wrong answer" in skip.toolTip()
        click(walk_app, skip)
        assert len(view.answers) == 1
        assert store.setting("quiz_in_progress"), "the attempt was not saved"

    with step(walk_app, "quiz", "move on to the next question", window):
        click(walk_app, _named(view, "Next question")
              or _named(view, "See your score"))

    with step(walk_app, "quiz", "think better of leaving", window,
              allow_dialog=True):
        with answering(question=QMessageBox.StandardButton.No):
            click(walk_app, _named(view, "Leave this quiz"))
        assert view.quiz is not None, "No did not mean no"

    with step(walk_app, "quiz", "leave the quiz", window, allow_dialog=True):
        with answering(question=QMessageBox.StandardButton.Yes):
            click(walk_app, _named(view, "Leave this quiz"))
        assert view.quiz is None, "there is still no way out of a quiz"
        assert store.setting("quiz_in_progress") is None

    with step(walk_app, "quiz", "close the app in the middle of one", window):
        view._start(quiz)
        pump(walk_app, 2)
        click(walk_app, _named(view, "Skip (counts as wrong)"))
        view.quiz = None                    # what a relaunch looks like
        view._pick_screen()
        pump(walk_app, 2)
        assert _named(view, "Resume") is not None, "nothing was offered back"

    with step(walk_app, "quiz", "resume where it was left", window):
        click(walk_app, _named(view, "Resume"))
        assert view.quiz is not None
        assert len(view.answers) == 1, "the answer already given was lost"

    with step(walk_app, "quiz", "start it over instead", window):
        view.quiz = None
        view._pick_screen()
        pump(walk_app, 2)
        click(walk_app, _named(view, "Start over"))
        assert view.answers == {}
        assert store.setting("quiz_in_progress") is None

    view._forget()
    view._reset_to_picker()
    pump(walk_app, 2)
    REC.bump("ways out of a quiz", 2)


# -- a second copy of everything ------------------------------------------


def test_the_backups_can_be_mirrored_to_another_disk(walk_app, window, store,
                                                     tmp_path, monkeypatch):
    from operators_console.ui.views.settings import MIRROR_NAME
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    target = tmp_path / "second disk"
    REC.cannot_reach(
        "the real folder chooser",
        "QFileDialog.getExistingDirectory is a static that builds and execs "
        "its dialog in C++, so the walk's dialog answerer - which patches "
        "QDialog.exec in Python - cannot reach it. It is stubbed here the "
        "way getSaveFileName is stubbed in the harness.")
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        staticmethod(lambda *a, **k: str(target)))

    with step(walk_app, "settings", "nothing has left this machine yet",
              window):
        assert "never" in view.last_export.text()
        assert "No second copy" in view.mirror_path.text()

    with step(walk_app, "settings", "choose a second copy folder", window):
        click(walk_app, view.mirror_button)
        assert store.setting("backup_mirror") == str(target)
        assert str(target) in view.mirror_path.text()

    with step(walk_app, "settings", "copy everything there now", window):
        store.set_checked("p01.s0.0", True)
        store.backup(tag="manual")
        click(walk_app, view.mirror_now_button)
        assert (target / MIRROR_NAME).exists(), "no second copy was written"
        assert list(target.glob("progress-*.db")), "the snapshot stayed put"
        assert "never" not in view.last_export.text()
    REC.bump("copies of the backups off this disk", 1)


def test_a_restore_says_what_it_changed(walk_app, window, store, tmp_path):
    from operators_console.core.export import export_backup
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    backup = tmp_path / "before.json"
    store.set_checked("p01.s0.0", True)
    export_backup(store, backup)
    store.reset_progress()

    with step(walk_app, "settings", "import a backup and read the summary",
              window, allow_dialog=True):
        # _import asks through the static QMessageBox.question, which the
        # answerer keys as "question" rather than as "messagebox".
        with answering(open_path=str(backup),
                       question=QMessageBox.StandardButton.Yes):
            click(walk_app, _named(view, "Import backup"))
        pump(walk_app, 2)
        assert view.change_summary.isVisibleTo(view), (
            "an import still says only 'Imported'")
        assert "checks 0 -> 1" in view.change_summary.text()
        assert "log entries" in view.change_summary.text()


# -- a button that opens nothing ------------------------------------------


def test_the_open_button_waits_for_a_link(walk_app, window, curriculum):
    window.go("projects", "")
    pump(walk_app, 4)
    project = curriculum.projects[0]
    card = window.views["projects"].card_for(project.id)
    assert card is not None

    with step(walk_app, "projects", "press Open with nothing to open",
              window):
        assert not card.open_button.isEnabled(), (
            "Open was pressable with an empty repo field")
        assert card.open_button.toolTip()
        click(walk_app, card.open_button)

    with step(walk_app, "projects", "type a repo address", window):
        card.repo.setText("https://github.com/walker/first-project")
        pump(walk_app, 1)
        assert card.open_button.isEnabled(), "Open stayed dead with a link"
        before = len(REC.urls)
        click(walk_app, card.open_button)
        assert len(REC.urls) > before, "Open opened nothing"

    with step(walk_app, "projects", "replace it with a note to self", window):
        card.repo.setText("ask Sam for the link")
        pump(walk_app, 1)
        assert not card.open_button.isEnabled()
        card.repo.setText("")
        pump(walk_app, 1)
    REC.bump("dead controls that now say so", 1)

"""The gap between what a settings page shows and what the store holds.

"My options were not saved." The cause was two copies of the app on one
database (see `test_single_instance.py`); what follows pins the flow itself,
the whole way along: answer it in the wizard, see it in Settings, change it
there, then tear the page down and build it again the way a theme change does
- and find the same answer at every stop.

The setup wizard is also checked here for the two things that made it feel
unfinished: that it opens on the answers already stored rather than on its own
defaults, and that it fits at both text sizes.
"""
from __future__ import annotations

import json
from datetime import date

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton, QWidget

from conftest import pump

from operators_console.core.adaptive import EXPERIENCE_LEVELS, GOALS
from operators_console.core.export import export_backup
from operators_console.ui import onboarding as onboarding_module
from operators_console.ui.onboarding import Onboarding
from operators_console.ui.theme import base_font, stylesheet
from operators_console.ui.views import settings as settings_module
from operators_console.ui.views.settings import (
    TALLY, describe_change, mirror_latest, tally,
)


def _settings(qt_app, window):
    window.go("settings")
    pump(qt_app)
    return window.views["settings"]


def _rebuilt(qt_app, window):
    """Exactly what a theme change does to a page: drop it, build it again."""
    window.go("today")
    pump(qt_app)
    window.views["settings"].teardown()
    window.go("settings")
    pump(qt_app)
    return window.views["settings"]


def _wizard(window):
    return Onboarding(window.ctx, window)


def _ticked(view):
    return {gid for gid, box in view.goal_boxes.items() if box.isChecked()}


# ---------------------------------------------------------------------------
# The round trip
# ---------------------------------------------------------------------------

def test_two_goals_survive_the_wizard_settings_and_a_rebuild(qt_app, window,
                                                             store):
    first, second = GOALS[0][0], GOALS[3][0]
    wizard = _wizard(window)
    wizard.goal_boxes[first].setChecked(True)
    wizard.goal_boxes[second].setChecked(True)
    wizard._finish()
    assert store.setting("goals") == sorted([first, second])

    view = _settings(qt_app, window)
    assert _ticked(view) == {first, second}, "Settings showed other goals"

    view.goal_boxes[second].setChecked(False)
    pump(qt_app)
    assert store.setting("goals") == [first]

    view = _rebuilt(qt_app, window)
    assert store.setting("goals") == [first], "the rebuild wrote goals back"
    assert _ticked(view) == {first}


def test_the_name_track_experience_and_pace_make_the_same_trip(qt_app, window,
                                                               store,
                                                               curriculum):
    wizard = _wizard(window)
    wizard.name.setText("  Ana  ")
    wizard.experience_buttons[2].setChecked(True)
    wizard.hours.setValue(1.5)
    wizard.days.setValue(4)
    wizard._finish()
    assert store.setting("learner_name") == "Ana"
    assert store.setting("experience") == EXPERIENCE_LEVELS[2][0]
    assert store.setting("hours_per_day") == 1.5
    assert store.setting("days_per_week") == 4

    view = _settings(qt_app, window)
    assert view.name.text() == "Ana"
    assert view.experience.currentData() == EXPERIENCE_LEVELS[2][0]
    assert view.hours.value() == 1.5
    assert view.days.value() == 4

    other = next(t for t in curriculum.tracks
                 if t.id != store.setting("track"))
    view.track.setCurrentIndex(view.track.findData(other.id))
    view.experience.setCurrentIndex(view.experience.findData("working"))
    view.name.setText("Ana Lovelace")
    view.name.editingFinished.emit()
    view.hours.setValue(2.5)
    view.days.setValue(6)
    pump(qt_app)
    assert store.setting("track") == other.id
    assert store.setting("experience") == "working"
    assert store.setting("learner_name") == "Ana Lovelace"
    assert store.setting("hours_per_day") == 2.5
    assert store.setting("days_per_week") == 6

    view = _rebuilt(qt_app, window)
    assert store.setting("track") == other.id
    assert view.track.currentData() == other.id
    assert view.experience.currentData() == "working"
    assert view.name.text() == "Ana Lovelace"
    assert view.hours.value() == 2.5
    assert view.days.value() == 6


def test_the_theme_and_the_text_size_survive_a_rebuild(qt_app, window, store):
    view = _settings(qt_app, window)
    view.theme.setCurrentIndex(view.theme.findData("dark"))
    view.font_scale.setValue(1.25)
    pump(qt_app)
    assert store.setting("theme") == "dark"
    assert store.setting("font_scale") == 1.25

    view = _rebuilt(qt_app, window)
    assert store.setting("theme") == "dark", "the rebuild reset the theme"
    assert store.setting("font_scale") == 1.25
    assert view.theme.currentData() == "dark"
    assert view.font_scale.value() == 1.25
    view.font_scale.setValue(1.0)
    view.theme.setCurrentIndex(view.theme.findData("system"))
    pump(qt_app)


def test_a_rebuilt_page_writes_nothing_of_its_own(qt_app, window, store):
    """A page that saved its own defaults while drawing is how nine goals
    appear where two were chosen."""
    store.set_setting("goals", [GOALS[1][0]])
    before = dict(store.all_settings())
    _settings(qt_app, window)
    _rebuilt(qt_app, window)
    after = dict(store.all_settings())
    assert after == before, "building Settings changed the settings"


# ---------------------------------------------------------------------------
# The wizard
# ---------------------------------------------------------------------------

def test_the_wizard_opens_on_the_answers_already_stored(window, store):
    store.set_setting("learner_name", "Ada")
    store.set_setting("experience", "working")
    store.set_setting("goals", ["web"])
    store.set_setting("hours_per_day", 1.5)
    store.set_setting("days_per_week", 3)
    store.set_setting("check_for_updates", False)

    wizard = _wizard(window)
    assert wizard.name.text() == "Ada"
    assert wizard.goal_boxes["web"].isChecked()
    assert not wizard.goal_boxes["data"].isChecked()
    assert wizard.hours.value() == 1.5
    assert wizard.days.value() == 3
    assert not wizard.check_updates.isChecked()
    chosen = next(o for o in wizard.experience_buttons if o.isChecked())
    assert chosen.property("value") == "working"

    wizard._finish()            # the last press must not wipe any of it
    assert store.setting("goals") == ["web"]
    assert store.setting("learner_name") == "Ada"
    assert store.setting("experience") == "working"


def test_the_start_date_is_never_written_twice(window, store):
    store.set_setting("started_on", "2026-09-03")
    _wizard(window)._finish()
    assert store.setting("started_on") == "2026-09-03"
    _wizard(window)._skip()
    assert store.setting("started_on") == "2026-09-03"


def test_a_real_first_run_stamps_today(window, store):
    store.set_setting("started_on", "")
    _wizard(window)._skip()
    assert store.setting("started_on") == date.today().isoformat()


def test_escape_skips_and_asks_nothing(window, store):
    store.set_setting("onboarded", False)
    wizard = _wizard(window)
    wizard.reject()             # what Escape does in a QDialog
    assert store.setting("onboarded") is True
    assert wizard.result() == Onboarding.DialogCode.Accepted


def test_the_update_check_is_asked_for_before_it_is_used(qt_app, window,
                                                         store):
    """First launch phoned GitHub without asking anybody."""
    wizard = _wizard(window)
    assert wizard.check_updates.isChecked(), "it must arrive pre-ticked"
    assert "GitHub" in wizard.check_updates.text()
    assert "downloads nothing" in wizard.check_updates.text()
    wizard.check_updates.setChecked(False)
    wizard._finish()
    assert store.setting("check_for_updates") is False
    assert _settings(qt_app, window).check_updates.isChecked() is False


def test_the_suggested_track_and_the_estimate_follow_the_answers(window):
    wizard = _wizard(window)
    for box in wizard.goal_boxes.values():
        box.setChecked(False)
    wizard.hours.setValue(2.5)
    wizard.days.setValue(7)
    assert "17.5 hours a week" in wizard.pace_preview.text()
    assert "weeks" in wizard.pace_preview.text()
    assert wizard.pace_months.text()

    wizard.goal_boxes["ai"].setChecked(True)
    assert wizard.track_name.text(), "no track was suggested"
    assert wizard.track_preview_label.text()
    assert "core phases" in wizard.track_meta.text()
    assert wizard.track_preview.objectName() == "FocusCard"


def test_choosing_is_carried_by_the_card_not_only_the_dot(window):
    """The whole card is the target, and the chosen one is tinted."""
    from operators_console.ui.onboarding import _SelectCard
    wizard = _wizard(window)
    cards = wizard.stack.widget(1).findChildren(_SelectCard)
    assert len(cards) == len(EXPERIENCE_LEVELS)
    assert cards[0].objectName() == "FocusCard", "nothing looked chosen"
    assert cards[1].objectName() == "Card"

    cards[1].control.click()
    assert cards[1].control.isChecked()
    assert cards[1].objectName() == "FocusCard"
    assert cards[0].objectName() == "Card", "two cards looked chosen at once"
    # The semantics a screen reader reads are still a radio button's.
    assert cards[1].control.accessibleName() == EXPERIENCE_LEVELS[1][1]
    assert cards[1].control.accessibleDescription()


def test_every_option_is_reachable_from_the_keyboard(window):
    from PySide6.QtCore import Qt
    wizard = _wizard(window)
    for option in wizard.experience_buttons:
        assert option.focusPolicy() != Qt.FocusPolicy.NoFocus
    for box in wizard.goal_boxes.values():
        assert box.focusPolicy() != Qt.FocusPolicy.NoFocus
    # One group across four cards: arrow keys walk it, and only one wins.
    assert wizard.experience_group.exclusive()
    assert len(wizard.experience_group.buttons()) == len(EXPERIENCE_LEVELS)
    assert wizard.next_button.isDefault(), "Enter did not mean Continue"


def test_the_steps_are_four_and_the_progress_says_which(qt_app, window):
    wizard = _wizard(window)
    assert len(wizard.segments) == 4
    for step in range(4):
        assert wizard.kicker.text() == "STEP %d OF 4" % (step + 1)
        assert wizard.segments[step].value() == 100
        assert all(s.value() == 0 for s in wizard.segments[step + 1:])
        if step < 3:
            wizard.next_button.click()
            pump(qt_app)
    assert wizard.next_button.text() == "Build my plan"
    wizard.back_button.click()
    pump(qt_app)
    assert wizard.kicker.text() == "STEP 3 OF 4"


@pytest.mark.parametrize("scale", [1.0, 1.6])
def test_the_wizard_fits_at_one_and_at_one_point_six(qt_app, window, store,
                                                     scale):
    """Rendered with the real font and the real sheet, at both extremes."""
    store.set_setting("font_scale", scale)
    was_font, was_sheet = qt_app.font(), qt_app.styleSheet()
    qt_app.setFont(base_font(scale))
    qt_app.setStyleSheet(stylesheet(window.ctx.palette, scale))
    wizard = _wizard(window)
    try:
        wizard.show()
        pump(qt_app, 4)
        for step in range(4):
            pump(qt_app, 3)
            squeezed = _squeezed(wizard)
            assert not squeezed, ("step %d at %sx: %s"
                                  % (step + 1, scale, squeezed[:4]))
            bottom = wizard.next_button.mapTo(
                wizard, wizard.next_button.rect().bottomRight())
            assert bottom.y() <= wizard.height(), (
                "the button row fell off the bottom at %sx" % scale)
            assert bottom.x() <= wizard.width()
            if step < 3:
                wizard.next_button.click()
        wizard.close()
    finally:
        wizard.deleteLater()
        qt_app.setFont(was_font)
        qt_app.setStyleSheet(was_sheet)
        pump(qt_app, 2)


def _squeezed(root) -> list:
    """Widgets handed less room than they need - clipping, before it shows."""
    bad = []
    for child in root.findChildren(QWidget):
        if not child.isVisible():
            continue
        if child.minimumHeight() == child.maximumHeight():
            continue            # a fixed size is a decision, not a squeeze
        need = child.minimumSizeHint()
        if need.height() > 0 and child.height() + 1 < need.height():
            bad.append("%s %r height %d < %d"
                       % (type(child).__name__, child.objectName(),
                          child.height(), need.height()))
        if isinstance(child, QPushButton) and child.width() + 1 < need.width():
            bad.append("%s %r width %d < %d"
                       % (type(child).__name__, child.text(),
                          child.width(), need.width()))
    return bad


# ---------------------------------------------------------------------------
# Running it again, from Settings
# ---------------------------------------------------------------------------

def test_settings_can_run_the_wizard_again(qt_app, window, store,
                                           monkeypatch):
    opened = []

    def answer_it(self):
        opened.append(self)
        self.goal_boxes["data"].setChecked(True)
        self._finish()
        return Onboarding.DialogCode.Accepted

    monkeypatch.setattr(onboarding_module.Onboarding, "exec", answer_it)
    view = _settings(qt_app, window)
    view.setup_button.click()
    pump(qt_app)
    assert opened, "Run setup again opened nothing"
    assert "data" in store.setting("goals")
    assert view.goal_boxes["data"].isChecked(), "the page did not refresh"


# ---------------------------------------------------------------------------
# A second copy of the backups, somewhere else
# ---------------------------------------------------------------------------

def test_mirror_latest_writes_an_export_and_the_newest_snapshot(store,
                                                                tmp_path):
    store.set_checked("p01.s0.0", True)
    store.backup(tag="manual")
    target = tmp_path / "other disk" / "console"
    written = mirror_latest(store, target)
    assert written == target / settings_module.MIRROR_NAME
    assert json.loads(written.read_text(encoding="utf-8"))
    assert list(target.glob("progress-*.db")), "no snapshot came with it"
    # Running it twice overwrites rather than piles up.
    mirror_latest(store, target)
    assert len(list(target.glob("*.json"))) == 1


def test_the_second_copy_goes_where_the_learner_points_it(qt_app, window,
                                                          store, tmp_path,
                                                          monkeypatch):
    target = tmp_path / "usb stick"
    view = _settings(qt_app, window)
    assert "never" in view.last_export.text()
    assert "No second copy" in view.mirror_path.text()

    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        staticmethod(lambda *a, **k: str(target)))
    view.mirror_button.click()
    pump(qt_app)
    assert store.setting("backup_mirror") == str(target)
    assert str(target) in view.mirror_path.text()

    store.backup(tag="manual")
    view.mirror_now_button.click()
    pump(qt_app)
    assert (target / settings_module.MIRROR_NAME).exists()
    assert store.setting("last_export") == date.today().isoformat()
    assert "never" not in view.last_export.text()
    view = _rebuilt(qt_app, window)
    assert str(target) in view.mirror_path.text()
    assert date.today().isoformat() in view.last_export.text()


def test_an_export_stamps_the_date_on_the_page(qt_app, window, store,
                                               tmp_path, monkeypatch):
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "b.json"), "")))
    view = _settings(qt_app, window)
    view._export()
    pump(qt_app)
    assert store.setting("last_export") == date.today().isoformat()
    assert date.today().isoformat() in view.last_export.text()


def test_cancelling_the_folder_chooser_changes_nothing(qt_app, window, store,
                                                       monkeypatch):
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        staticmethod(lambda *a, **k: ""))
    view = _settings(qt_app, window)
    view.mirror_button.click()
    view.mirror_now_button.click()      # no folder: it asks, then gives up
    pump(qt_app)
    assert not store.setting("backup_mirror", "")


# ---------------------------------------------------------------------------
# What a restore actually did
# ---------------------------------------------------------------------------

def test_an_import_says_what_it_changed(qt_app, window, store, tmp_path,
                                        monkeypatch, curriculum):
    backup = tmp_path / "before.json"
    store.set_checked("p01.s0.0", True)
    project = curriculum.projects[0]
    store.set_project(project.id, status="shipped")
    store.add_log(date.today().isoformat(), "reading", 1.0, "", "", "")
    export_backup(store, backup)
    full = tally(store)
    store.reset_progress()
    assert tally(store)["checks"] == 0

    said = []
    window.ctx.toast.connect(said.append)
    view = _settings(qt_app, window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        staticmethod(lambda *a, **k: (str(backup), "")))
    monkeypatch.setattr(
        QMessageBox, "question",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes))
    view._import()
    pump(qt_app)

    assert said and said[-1].startswith("Imported.")
    for name in TALLY:
        assert name in said[-1], "%s was left out of the summary" % name
    assert "checks 0 -> %d" % full["checks"] in said[-1]
    assert "projects shipped 0 -> 1" in said[-1]
    assert view.change_summary.isVisibleTo(view)
    assert view.change_summary.text().startswith("Imported - ")


def test_a_restore_still_opens_with_the_words_the_menu_promises(qt_app,
                                                                window,
                                                                store,
                                                                monkeypatch):
    """Other pages read this toast; the summary is added, not substituted."""
    from operators_console.ui.snapshots import SnapshotDialog
    store.set_checked("p01.s0.0", True)
    snapshot = store.backup(tag="manual")
    store.reset_progress()

    def run(dialog):
        dialog.restored = snapshot
        store.restore_snapshot(snapshot)
        return SnapshotDialog.DialogCode.Accepted

    monkeypatch.setattr(SnapshotDialog, "exec", run)
    said = []
    window.ctx.toast.connect(said.append)
    view = _settings(qt_app, window)
    view.restore_snapshot()
    pump(qt_app)
    assert said and said[-1].startswith("Restored: ")
    assert "checks 0 -> 1" in said[-1]
    assert view.change_summary.text().startswith("Restored - ")


def test_describe_change_names_every_number():
    before = {name: 0 for name in TALLY}
    after = dict(before, checks=40)
    text = describe_change(before, after)
    assert "checks 0 -> 40" in text
    for name in TALLY:
        assert name in text
    assert describe_change({}, {}) .count("0 -> 0") == len(TALLY)

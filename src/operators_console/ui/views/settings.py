"""Settings: goals, pace, review tuning, appearance and your data."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QGridLayout,
    QHBoxLayout, QLineEdit, QMessageBox, QSpinBox,
)

from ...core import paths
from ...core.adaptive import EXPERIENCE_LEVELS, GOALS
from ...core.export import export_backup, export_report, import_backup
from ...core.storage import Store
from ..widgets.common import (
    Card, button, divider, heading, label, muted,
)
from .base import View


# One label column for every card, so the fields line up down the page.
LABEL_COLUMN = 112
FONT_APPLY_MS = 250

#: The name the second copy is written under, so it is overwritten rather
#: than accumulated: this is a mirror, not an archive.
MIRROR_NAME = "operators-console-backup.json"

#: What a restore or an import is measured in - things the learner made,
#: rather than "Restored" and nothing else.
TALLY = ("checks", "exercises passed", "projects shipped", "log entries")


def mirror_latest(store, folder) -> Path:
    """Write a second copy of everything into a folder of the owner's choice.

    Every snapshot lives in one directory inside the data folder, so a single
    dead disk takes the progress and all of its backups together. This writes
    a fresh export - and the newest snapshot beside it, when there is one -
    somewhere else entirely. Reusable, and deliberately free of Qt: a copy is
    a copy whether a button or a test asked for it.
    """
    target = Path(folder)
    target.mkdir(parents=True, exist_ok=True)
    written = target / MIRROR_NAME
    export_backup(store, written)
    snapshots = Store.snapshots()
    if snapshots:
        shutil.copy2(snapshots[0], target / snapshots[0].name)
    return written


def tally(store) -> dict:
    """The four numbers a learner would count to see whether it worked."""
    return {
        "checks": len(store.checked_ids()),
        "exercises passed": len(store.passed_exercise_ids()),
        "projects shipped": sum(
            1 for status in store.project_statuses().values()
            if status == "shipped"),
        "log entries": len(store.logs(limit=1_000_000)),
    }


def describe_change(before: dict, after: dict) -> str:
    """Every number, moved or not: "checks 4 -> 40, log entries 2 -> 2"."""
    return ", ".join("%s %d -> %d" % (name, before.get(name, 0),
                                      after.get(name, 0))
                     for name in TALLY)


class SettingsView(View):
    title = "Settings"

    def build(self) -> None:
        self.header("Settings", "make it yours",
                    "Changing your track or goals reshapes the roadmap "
                    "immediately. Nothing you have already done is lost.")
        self._loading = False

        plan = Card()
        plan.add(heading("Your plan"))
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, LABEL_COLUMN)
        grid.setSpacing(8)
        self.name = QLineEdit()
        self.name.setPlaceholderText("What should the app call you?")
        self.name.editingFinished.connect(
            lambda: self._set("learner_name", self.name.text().strip()))
        grid.addWidget(muted("NAME"), 0, 0)
        grid.addWidget(self.name, 0, 1)

        self.track = QComboBox()
        for track in self.ctx.curriculum.tracks:
            self.track.addItem(track.name, track.id)
        self.track.currentIndexChanged.connect(self._on_track)
        grid.addWidget(muted("TRACK"), 1, 0)
        grid.addWidget(self.track, 1, 1)

        self.experience = QComboBox()
        for value, text in EXPERIENCE_LEVELS:
            self.experience.addItem(text, value)
        self.experience.currentIndexChanged.connect(
            lambda _i: self._set("experience", self.experience.currentData()))
        grid.addWidget(muted("EXPERIENCE"), 2, 0)
        grid.addWidget(self.experience, 2, 1)
        plan.box.addLayout(grid)

        self.track_blurb = muted("")
        plan.add(self.track_blurb)
        plan.add(divider())
        plan.add(heading("What you want to build"))
        plan.add(muted("These add relevant phases to your roadmap and change "
                       "what Today suggests."))
        self.goal_boxes = {}
        goals_grid = QGridLayout()
        goals_grid.setSpacing(8)
        for index, (gid, text, _tags) in enumerate(GOALS):
            box = QCheckBox(text)
            box.stateChanged.connect(lambda _s: self._save_goals())
            self.goal_boxes[gid] = box
            goals_grid.addWidget(box, index // 2, index % 2)
        plan.box.addLayout(goals_grid)
        plan.add(divider())
        setup_row = QHBoxLayout()
        setup_row.setSpacing(8)
        self.setup_button = button("Run setup again")
        self.setup_button.clicked.connect(self._run_setup)
        setup_row.addWidget(self.setup_button)
        setup_row.addWidget(muted("The four questions from your first launch, "
                                  "with your answers already filled in."), 1)
        plan.box.addLayout(setup_row)
        self.scroller.add(plan)

        pace = Card()
        pace.add(heading("Pace"))
        pace.add(muted("Used for the finish estimate and the size of the daily "
                       "plan. Be realistic rather than aspirational."))
        pace_grid = QGridLayout()
        pace_grid.setColumnMinimumWidth(0, LABEL_COLUMN)
        pace_grid.setSpacing(8)
        pace_grid.setColumnStretch(2, 1)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.5, 16.0)
        self.hours.setSingleStep(0.5)
        self.hours.setSuffix(" hours a day")
        self.hours.valueChanged.connect(
            lambda v: self._set("hours_per_day", float(v)))
        pace_grid.addWidget(muted("STUDY TIME"), 0, 0)
        pace_grid.addWidget(self.hours, 0, 1)
        self.days = QSpinBox()
        self.days.setRange(1, 7)
        self.days.setSuffix(" days a week")
        self.days.valueChanged.connect(
            lambda v: self._set("days_per_week", int(v)))
        pace_grid.addWidget(muted("FREQUENCY"), 1, 0)
        pace_grid.addWidget(self.days, 1, 1)
        pace.box.addLayout(pace_grid)
        self.pace_note = muted("")
        pace.add(self.pace_note)
        self.scroller.add(pace)

        review = Card()
        review.add(heading("Review"))
        review.add(muted(
            "A higher retention target means shorter intervals and more work "
            "per day. Ninety percent is the sensible default."))
        review_grid = QGridLayout()
        review_grid.setColumnMinimumWidth(0, LABEL_COLUMN)
        review_grid.setSpacing(8)
        review_grid.setColumnStretch(2, 1)
        self.retention = QSpinBox()
        self.retention.setRange(70, 97)
        self.retention.setSuffix(" % target retention")
        self.retention.valueChanged.connect(self._on_retention)
        review_grid.addWidget(muted("TARGET"), 0, 0)
        review_grid.addWidget(self.retention, 0, 1)
        self.new_cards = QSpinBox()
        self.new_cards.setRange(0, 200)
        self.new_cards.setSuffix(" new cards a day")
        self.new_cards.valueChanged.connect(
            lambda v: self._set("new_cards_per_day", int(v)))
        review_grid.addWidget(muted("NEW"), 1, 0)
        review_grid.addWidget(self.new_cards, 1, 1)
        self.max_reviews = QSpinBox()
        self.max_reviews.setRange(10, 1000)
        self.max_reviews.setSuffix(" reviews a day")
        self.max_reviews.valueChanged.connect(
            lambda v: self._set("max_reviews_per_day", int(v)))
        review_grid.addWidget(muted("CEILING"), 2, 0)
        review_grid.addWidget(self.max_reviews, 2, 1)
        self.timeout = QSpinBox()
        self.timeout.setRange(3, 60)
        self.timeout.setSuffix(" second exercise timeout")
        self.timeout.valueChanged.connect(
            lambda v: self._set("exercise_timeout", int(v)))
        review_grid.addWidget(muted("RUNNER"), 3, 0)
        review_grid.addWidget(self.timeout, 3, 1)
        review.box.addLayout(review_grid)
        self.scroller.add(review)

        look = Card()
        look.add(heading("Appearance"))
        look_grid = QGridLayout()
        look_grid.setColumnMinimumWidth(0, LABEL_COLUMN)
        look_grid.setSpacing(8)
        look_grid.setColumnStretch(2, 1)
        self.theme = QComboBox()
        self.theme.addItem("Match the system", "system")
        self.theme.addItem("Light", "light")
        self.theme.addItem("Dark", "dark")
        self.theme.currentIndexChanged.connect(self._on_theme)
        look_grid.addWidget(muted("THEME"), 0, 0)
        look_grid.addWidget(self.theme, 0, 1)
        self.font_scale = QDoubleSpinBox()
        self.font_scale.setRange(0.8, 1.6)
        self.font_scale.setSingleStep(0.05)
        self.font_scale.setSuffix(" x text size")
        self.font_scale.valueChanged.connect(self._on_font)
        look_grid.addWidget(muted("TEXT"), 1, 0)
        look_grid.addWidget(self.font_scale, 1, 1)
        look.box.addLayout(look_grid)
        self.scroller.add(look)

        updates_card = Card()
        updates_card.add(heading("Updates"))
        updates_card.add(muted(
            "The only time this app touches the network. It asks GitHub "
            "whether a newer version exists when it starts, every few minutes "
            "while it is open and when you come back to it, and downloads "
            "nothing until you press the button."))
        self.check_updates = QCheckBox("Tell me when a new version is out")
        self.check_updates.stateChanged.connect(
            lambda _s: self._set("check_for_updates",
                                 self.check_updates.isChecked()))
        updates_card.add(self.check_updates)
        check_now = button("Check now")
        check_now.clicked.connect(self._check_now)
        updates_card.add_row(None, check_now)
        self.scroller.add(updates_card)

        data = Card()
        data.add(heading("Your data"))
        data.add(muted(
            "Everything is stored locally, in one folder, and saved the moment "
            "you change it. Nothing is uploaded anywhere."))
        self.location = label("", "Mono", wrap=True, selectable=True)
        data.add(self.location)
        row = QHBoxLayout()
        row.setSpacing(8)
        for text, handler in (("Open folder", self._open_folder),
                              ("Export backup", self._export),
                              ("Import backup", self._import),
                              ("Export report", self._report)):
            widget = button(text)            # actions, not links
            widget.clicked.connect(handler)
            row.addWidget(widget)
        row.addStretch(1)
        data.box.addLayout(row)
        self.last_export = muted("")
        data.add(self.last_export)

        data.add(divider())
        data.add(label("Second copy", "SectionTitle", wrap=False))
        data.add(muted(
            "Every backup lives in one folder on one disk, which is one "
            "failure away from none. Point this at another drive, or at a "
            "folder that syncs, and Copy now writes a fresh export and the "
            "newest snapshot there as well."))
        self.mirror_path = label("", "Mono", wrap=True, selectable=True)
        data.add(self.mirror_path)
        mirror_row = QHBoxLayout()
        mirror_row.setSpacing(8)
        self.mirror_button = button("Choose folder...")
        self.mirror_button.clicked.connect(self._choose_mirror)
        mirror_row.addWidget(self.mirror_button)
        self.mirror_now_button = button("Copy now")
        self.mirror_now_button.clicked.connect(self._mirror_now)
        mirror_row.addWidget(self.mirror_now_button)
        mirror_row.addStretch(1)
        data.box.addLayout(mirror_row)

        data.add(divider())
        data.add(label("Snapshots", "SectionTitle", wrap=False))
        data.add(muted(
            "A copy of your progress is taken automatically each day you "
            "open the app, and before every reset, import or upgrade. The "
            "last %d daily copies and %d others are kept."
            % (Store.KEEP_DAILY, Store.KEEP_SNAPSHOTS)))
        snaps = QHBoxLayout()
        snaps.setSpacing(8)
        self.snapshot_button = button("Snapshot now")
        self.snapshot_button.clicked.connect(self._snapshot)
        snaps.addWidget(self.snapshot_button)
        self.restore_button = button("Restore a snapshot...")
        self.restore_button.clicked.connect(self.restore_snapshot)
        snaps.addWidget(self.restore_button)
        snaps.addStretch(1)
        data.box.addLayout(snaps)
        # What a restore or an import actually did, in numbers, rather than
        # the word "Restored" and a leap of faith.
        self.change_summary = muted("")
        self.change_summary.setVisible(False)
        data.add(self.change_summary)
        data.add(divider())
        danger = QHBoxLayout()
        reset = button("Reset all progress", "bad")
        reset.clicked.connect(self._reset)
        danger.addWidget(reset)
        danger.addWidget(muted("A snapshot is taken first, so a reset can be "
                               "undone. Settings are kept."), 1)
        data.box.addLayout(danger)
        self.scroller.add(data)

        about = Card()
        about.add(heading("About"))
        self.about_text = muted("")
        about.add(self.about_text)
        self.scroller.add(about)
        self.scroller.add_stretch()

    # -- refresh -----------------------------------------------------------

    def refresh(self) -> None:
        store = self.ctx.store
        self._loading = True
        self.name.setText(store.setting("learner_name", ""))
        index = self.track.findData(store.setting("track", "generalist"))
        self.track.setCurrentIndex(max(0, index))
        index = self.experience.findData(store.setting("experience", "none"))
        self.experience.setCurrentIndex(max(0, index))
        chosen = set(store.setting("goals", []) or [])
        for gid, box in self.goal_boxes.items():
            box.setChecked(gid in chosen)
        self.hours.setValue(float(store.setting("hours_per_day", 3.0)))
        self.days.setValue(int(store.setting("days_per_week", 5)))
        self.retention.setValue(
            int(round(float(store.setting("desired_retention", 0.9)) * 100)))
        self.new_cards.setValue(int(store.setting("new_cards_per_day", 15)))
        self.max_reviews.setValue(int(store.setting("max_reviews_per_day", 120)))
        self.timeout.setValue(int(store.setting("exercise_timeout", 10)))
        index = self.theme.findData(store.setting("theme", "system"))
        self.theme.setCurrentIndex(max(0, index))
        self.font_scale.setValue(float(store.setting("font_scale", 1.0)))
        self.check_updates.setChecked(
            bool(store.setting("check_for_updates", True)))
        self._loading = False

        self._update_track_blurb()
        self._update_pace_note()
        self._update_data_lines()
        self.location.setText(str(paths.data_dir()))

        from ...version import APP_NAME, __version__
        counts = (len(self.ctx.curriculum.phases),
                  len(self.ctx.curriculum.exercises),
                  len(self.ctx.curriculum.all_questions),
                  len(self.ctx.curriculum.projects))
        self.about_text.setText(
            "%s %s - %d phases, %d graded exercises, %d review questions, "
            "%d projects. Scheduling by FSRS-6. Curriculum revision %s."
            % (APP_NAME, __version__, counts[0], counts[1], counts[2],
               counts[3], self.ctx.curriculum.generated))

    def _update_track_blurb(self) -> None:
        track = self.ctx.curriculum.track(self.track.currentData())
        if track is None:
            return
        self.track_blurb.setText(
            "%s  -  %d core phases, %d optional."
            % (track.blurb, len(track.core), len(track.optional)))

    def _update_data_lines(self) -> None:
        """The two facts about your data that change without a redraw."""
        when = str(self.ctx.store.setting("last_export", "") or "")
        self.last_export.setText("Last export: %s" % (when or "never"))
        folder = str(self.ctx.store.setting("backup_mirror", "") or "")
        self.mirror_path.setText(folder or "No second copy yet.")

    def _update_pace_note(self) -> None:
        days = self.ctx.progress.estimated_days_left()
        self.pace_note.setText(
            "At this pace the remaining plan takes about %d weeks."
            % max(1, round(days / 7)) if days > 0
            else "You have finished everything in the current plan.")

    # -- handlers ----------------------------------------------------------

    def _set(self, key: str, value) -> None:
        if self._loading:
            return
        self.ctx.store.set_setting(key, value)
        self.ctx.settings_changed.emit()
        self.ctx.changed()

    def _on_track(self, _index: int) -> None:
        if self._loading:
            return
        self._set("track", self.track.currentData())
        self._update_track_blurb()
        self._update_pace_note()
        self.ctx.announce("Roadmap updated.")

    def _save_goals(self) -> None:
        if self._loading:
            return
        chosen = sorted(gid for gid, box in self.goal_boxes.items()
                        if box.isChecked())
        self._set("goals", chosen)

    def _on_retention(self, value: int) -> None:
        if self._loading:
            return
        self._set("desired_retention", round(value / 100.0, 2))
        self.ctx.rebuild_review()

    def _on_theme(self, _index: int) -> None:
        if self._loading:
            return
        self.ctx.store.set_setting("theme", self.theme.currentData())
        self.ctx.refresh_palette()

    def _on_font(self, value: float) -> None:
        if self._loading:
            return
        self.ctx.store.set_setting("font_scale", round(float(value), 2))
        # A spin from 1.0 to 1.6 is twelve steps; the sheet is applied once,
        # when the hand comes off the control.
        if not hasattr(self, "_font_timer"):
            self._font_timer = QTimer(self)
            self._font_timer.setSingleShot(True)
            self._font_timer.timeout.connect(self._apply_font)
        self._font_timer.start(FONT_APPLY_MS)

    def _apply_font(self) -> None:
        self.ctx.settings_changed.emit()
        self.ctx.theme_changed.emit()

    def _check_now(self) -> None:
        window = self.window()
        if hasattr(window, "check_for_updates"):
            window.check_for_updates()

    def _run_setup(self) -> None:
        """The first-launch wizard, on demand.

        It was reachable exactly once in the life of an install, which made
        the four questions feel irreversible when they are the most reversible
        thing in the app.
        """
        from ..onboarding import Onboarding
        dialog = Onboarding(self.ctx, self.window())
        if int(dialog.exec()) == int(Onboarding.DialogCode.Accepted):
            self.refresh()
            self.ctx.announce("Your plan is up to date.")

    # -- data ---------------------------------------------------------------

    def _open_folder(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(paths.data_dir())))

    def _export(self) -> None:
        target, _filter = QFileDialog.getSaveFileName(
            self, "Export your progress",
            str(Path.home() / "operators-console-backup.json"),
            "JSON files (*.json)")
        if not target:
            return
        try:
            export_backup(self.ctx.store, Path(target))
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        self._stamp_export()
        self.ctx.announce("Exported to %s" % target)

    def _stamp_export(self) -> None:
        """When the last copy left the building, so the page can say so."""
        self.ctx.store.set_setting("last_export", date.today().isoformat())
        self._update_data_lines()

    def _choose_mirror(self) -> None:
        start = str(self.ctx.store.setting("backup_mirror", "")
                    or str(Path.home()))
        folder = QFileDialog.getExistingDirectory(
            self, "Where should the second copy go?", start)
        if not folder:
            return
        self.ctx.store.set_setting("backup_mirror", folder)
        self._update_data_lines()
        self.ctx.announce("Second copies will go to %s" % folder)

    def _mirror_now(self) -> None:
        folder = str(self.ctx.store.setting("backup_mirror", "") or "")
        if not folder:
            self._choose_mirror()
            folder = str(self.ctx.store.setting("backup_mirror", "") or "")
            if not folder:
                return
        try:
            written = mirror_latest(self.ctx.store, folder)
        except OSError as exc:
            QMessageBox.warning(self, "Copy failed", str(exc))
            return
        self._stamp_export()
        self.ctx.announce("Second copy written to %s" % written.parent)

    def _import(self) -> None:
        source, _filter = QFileDialog.getOpenFileName(
            self, "Import a backup", str(Path.home()), "JSON files (*.json)")
        if not source:
            return
        confirm = QMessageBox.question(
            self, "Replace everything?",
            "Importing replaces all of your current progress.\n\n"
            "A backup of the current state is taken first, into the backups "
            "folder. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        before = tally(self.ctx.store)
        try:
            import_backup(self.ctx.store, Path(source))
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        self.ctx.rebuild_review()
        self.ctx.settings_changed.emit()
        self.ctx.changed()
        self.refresh()
        summary = describe_change(before, tally(self.ctx.store))
        self._show_change("Imported", summary)
        self.ctx.announce("Imported. %s" % summary)

    def _show_change(self, what: str, summary: str) -> None:
        """Leave the before-and-after on the page, not only in a toast."""
        self.change_summary.setText("%s - %s" % (what, summary))
        self.change_summary.setVisible(True)

    def _report(self) -> None:
        target, _filter = QFileDialog.getSaveFileName(
            self, "Export a progress report",
            str(Path.home() / "python-progress.md"),
            "Markdown files (*.md)")
        if not target:
            return
        try:
            export_report(self.ctx.curriculum, self.ctx.store,
                          self.ctx.progress, Path(target))
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        self.ctx.announce("Report written to %s" % target)

    def _snapshot(self) -> None:
        try:
            target = self.ctx.store.backup(tag="manual")
        except OSError as exc:
            QMessageBox.warning(self, "Snapshot failed", str(exc))
            return
        self.ctx.announce("Snapshot saved as %s" % target.name)

    def restore_snapshot(self) -> None:
        from ..snapshots import SnapshotDialog, snapshot_title
        before = tally(self.ctx.store)
        dialog = SnapshotDialog(self.ctx, self.window())
        accepted = dialog.exec() == SnapshotDialog.DialogCode.Accepted
        if not accepted or dialog.restored is None:
            return
        self.ctx.rebuild_review()
        self.ctx.settings_changed.emit()
        self.ctx.changed()
        self.refresh()
        summary = describe_change(before, tally(self.ctx.store))
        self._show_change("Restored", summary)
        self.ctx.announce("Restored: %s. %s"
                          % (snapshot_title(dialog.restored), summary))

    def _reset(self) -> None:
        confirm = QMessageBox.question(
            self, "Reset all progress?",
            "This clears every checkbox, exercise, review, project and log "
            "entry.\n\nA snapshot is taken first, so Restore a snapshot "
            "(here in Settings) can bring it all back. Your settings are "
            "kept.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.ctx.store.reset_progress()
        self.ctx.rebuild_review()
        self.ctx.changed()
        self.refresh()
        self.ctx.announce("Progress reset. Restore a snapshot in Settings "
                          "brings it back.")

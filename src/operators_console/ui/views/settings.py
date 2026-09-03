"""Settings: goals, pace, review tuning, appearance and your data."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QGridLayout,
    QHBoxLayout, QLineEdit, QMessageBox, QSpinBox,
)

from ...core import paths
from ...core.adaptive import EXPERIENCE_LEVELS, GOALS
from ...core.export import export_backup, export_report, import_backup
from ..widgets.common import (
    Card, button, divider, heading, label, muted,
)
from .base import View


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
        grid.setSpacing(9)
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
        goals_grid.setSpacing(6)
        for index, (gid, text, _tags) in enumerate(GOALS):
            box = QCheckBox(text)
            box.stateChanged.connect(lambda _s: self._save_goals())
            self.goal_boxes[gid] = box
            goals_grid.addWidget(box, index // 2, index % 2)
        plan.box.addLayout(goals_grid)
        self.scroller.add(plan)

        pace = Card()
        pace.add(heading("Pace"))
        pace.add(muted("Used for the finish estimate and the size of the daily "
                       "plan. Be realistic rather than aspirational."))
        pace_grid = QGridLayout()
        pace_grid.setSpacing(9)
        pace_grid.setColumnStretch(2, 1)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.5, 16.0)
        self.hours.setSingleStep(0.5)
        self.hours.setSuffix(" hours a day")
        self.hours.setMaximumWidth(220)
        self.hours.valueChanged.connect(
            lambda v: self._set("hours_per_day", float(v)))
        pace_grid.addWidget(muted("STUDY TIME"), 0, 0)
        pace_grid.addWidget(self.hours, 0, 1)
        self.days = QSpinBox()
        self.days.setRange(1, 7)
        self.days.setSuffix(" days a week")
        self.days.setMaximumWidth(220)
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
        review_grid.setSpacing(9)
        review_grid.setColumnStretch(2, 1)
        self.retention = QSpinBox()
        self.retention.setRange(70, 97)
        self.retention.setSuffix(" % target retention")
        self.retention.valueChanged.connect(self._on_retention)
        review_grid.addWidget(muted("TARGET"), 0, 0)
        self.retention.setMaximumWidth(260)
        review_grid.addWidget(self.retention, 0, 1)
        self.new_cards = QSpinBox()
        self.new_cards.setRange(0, 200)
        self.new_cards.setSuffix(" new cards a day")
        self.new_cards.valueChanged.connect(
            lambda v: self._set("new_cards_per_day", int(v)))
        review_grid.addWidget(muted("NEW"), 1, 0)
        self.new_cards.setMaximumWidth(260)
        review_grid.addWidget(self.new_cards, 1, 1)
        self.max_reviews = QSpinBox()
        self.max_reviews.setRange(10, 1000)
        self.max_reviews.setSuffix(" reviews a day")
        self.max_reviews.valueChanged.connect(
            lambda v: self._set("max_reviews_per_day", int(v)))
        review_grid.addWidget(muted("CEILING"), 2, 0)
        self.max_reviews.setMaximumWidth(260)
        review_grid.addWidget(self.max_reviews, 2, 1)
        self.timeout = QSpinBox()
        self.timeout.setRange(3, 60)
        self.timeout.setSuffix(" second exercise timeout")
        self.timeout.valueChanged.connect(
            lambda v: self._set("exercise_timeout", int(v)))
        review_grid.addWidget(muted("RUNNER"), 3, 0)
        self.timeout.setMaximumWidth(260)
        review_grid.addWidget(self.timeout, 3, 1)
        review.box.addLayout(review_grid)
        self.scroller.add(review)

        look = Card()
        look.add(heading("Appearance"))
        look_grid = QGridLayout()
        look_grid.setSpacing(9)
        look_grid.setColumnStretch(2, 1)
        self.theme = QComboBox()
        self.theme.addItem("Match the system", "system")
        self.theme.addItem("Light", "light")
        self.theme.addItem("Dark", "dark")
        self.theme.currentIndexChanged.connect(self._on_theme)
        look_grid.addWidget(muted("THEME"), 0, 0)
        self.theme.setMaximumWidth(260)
        look_grid.addWidget(self.theme, 0, 1)
        self.font_scale = QDoubleSpinBox()
        self.font_scale.setRange(0.8, 1.6)
        self.font_scale.setSingleStep(0.05)
        self.font_scale.setSuffix(" x text size")
        self.font_scale.valueChanged.connect(self._on_font)
        look_grid.addWidget(muted("TEXT"), 1, 0)
        self.font_scale.setMaximumWidth(260)
        look_grid.addWidget(self.font_scale, 1, 1)
        look.box.addLayout(look_grid)
        self.scroller.add(look)

        updates_card = Card()
        updates_card.add(heading("Updates"))
        updates_card.add(muted(
            "The only time this app touches the network. It asks GitHub once a "
            "day whether a newer version exists, and downloads nothing until "
            "you press the button."))
        self.check_updates = QCheckBox("Tell me when a new version is out")
        self.check_updates.stateChanged.connect(
            lambda _s: self._set("check_for_updates",
                                 self.check_updates.isChecked()))
        updates_card.add(self.check_updates)
        check_now = button("Check now", "quiet")
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
                              ("Export report", self._report),
                              ("Snapshot now", self._snapshot)):
            widget = button(text, "quiet")
            widget.clicked.connect(handler)
            row.addWidget(widget)
        row.addStretch(1)
        data.box.addLayout(row)
        data.add(divider())
        danger = QHBoxLayout()
        reset = button("Reset all progress", "bad")
        reset.clicked.connect(self._reset)
        danger.addWidget(reset)
        danger.addWidget(muted("Takes a backup first. Settings are kept."), 1)
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
        self.ctx.settings_changed.emit()
        self.ctx.theme_changed.emit()

    def _check_now(self) -> None:
        window = self.window()
        if hasattr(window, "check_for_updates"):
            window.check_for_updates()

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
        self.ctx.announce("Exported to %s" % target)

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
        try:
            import_backup(self.ctx.store, Path(source))
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        self.ctx.rebuild_review()
        self.ctx.settings_changed.emit()
        self.ctx.changed()
        self.refresh()
        self.ctx.announce("Imported. Everything has been restored.")

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

    def _reset(self) -> None:
        confirm = QMessageBox.question(
            self, "Reset all progress?",
            "This clears every checkbox, exercise, review, project and log "
            "entry.\n\nA backup is taken first, and your settings are kept. "
            "This cannot be undone from inside the app.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.ctx.store.reset_progress()
        self.ctx.rebuild_review()
        self.ctx.changed()
        self.refresh()
        self.ctx.announce("Progress reset. A backup is in the backups folder.")

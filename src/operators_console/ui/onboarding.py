"""First run: four short questions, then a plan.

Deliberately skippable. Someone who wants to start reading immediately should
be able to, and change their answers later without penalty.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLineEdit, QRadioButton, QSpinBox, QStackedWidget, QVBoxLayout, QWidget,
)

from ..core.adaptive import EXPERIENCE_LEVELS, GOALS
from .widgets.common import Card, button, divider, label, muted


class Onboarding(QDialog):
    """A four-step wizard that writes straight into settings."""

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("Set up your plan")
        self.setModal(True)
        self.resize(680, 560)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 22)
        outer.setSpacing(14)

        self.kicker = label("STEP 1 OF 4", "PageKicker", wrap=False)
        outer.addWidget(self.kicker)
        self.title = label("", "PageTitle")
        outer.addWidget(self.title)
        self.blurb = label("", "PageAim")
        outer.addWidget(self.blurb)
        outer.addWidget(divider())

        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        self.stack.addWidget(self._step_name())
        self.stack.addWidget(self._step_experience())
        self.stack.addWidget(self._step_goals())
        self.stack.addWidget(self._step_pace())

        controls = QHBoxLayout()
        self.skip_button = button("Skip - I will decide later", "quiet")
        self.skip_button.clicked.connect(self._skip)
        controls.addWidget(self.skip_button)
        controls.addStretch(1)
        self.back_button = button("Back", "quiet")
        self.back_button.clicked.connect(self._back)
        controls.addWidget(self.back_button)
        self.next_button = button("Continue", "primary")
        self.next_button.clicked.connect(self._next)
        controls.addWidget(self.next_button)
        outer.addLayout(controls)

        self.step = 0
        self._render()

    # -- steps -------------------------------------------------------------

    def _step_name(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setSpacing(10)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Your name, or anything you like")
        self.name.setMaximumWidth(340)
        column.addWidget(self.name)
        column.addWidget(muted(
            "Only used to say hello. It never leaves this machine."))
        column.addStretch(1)
        return page

    def _step_experience(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setSpacing(8)
        self.experience_buttons = []
        for value, text in EXPERIENCE_LEVELS:
            option = QRadioButton(text)
            option.setProperty("value", value)
            option.setStyleSheet("font-size: 14px; padding: 6px 0;")
            column.addWidget(option)
            self.experience_buttons.append(option)
        self.experience_buttons[0].setChecked(True)
        column.addWidget(muted(
            "This changes the tone of the advice, not the content. Nothing is "
            "hidden from you either way."))
        column.addStretch(1)
        return page

    def _step_goals(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setSpacing(6)
        grid = QGridLayout()
        grid.setSpacing(6)
        self.goal_boxes = {}
        for index, (gid, text, _tags) in enumerate(GOALS):
            box = QCheckBox(text)
            box.setStyleSheet("font-size: 13.5px; padding: 4px 0;")
            box.stateChanged.connect(self._preview_track)
            self.goal_boxes[gid] = box
            grid.addWidget(box, index // 2, index % 2)
        column.addLayout(grid)
        self.track_preview = Card()
        self.track_preview_label = label("", "Soft")
        self.track_preview.add(self.track_preview_label)
        column.addWidget(self.track_preview)
        column.addStretch(1)
        return page

    def _step_pace(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setSpacing(10)
        grid = QGridLayout()
        grid.setSpacing(9)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.5, 16.0)
        self.hours.setSingleStep(0.5)
        self.hours.setValue(2.0)
        self.hours.setSuffix(" hours a day")
        self.hours.valueChanged.connect(lambda _v: self._preview_pace())
        grid.addWidget(muted("STUDY TIME"), 0, 0)
        grid.addWidget(self.hours, 0, 1)
        self.days = QSpinBox()
        self.days.setRange(1, 7)
        self.days.setValue(5)
        self.days.setSuffix(" days a week")
        self.days.valueChanged.connect(lambda _v: self._preview_pace())
        grid.addWidget(muted("FREQUENCY"), 1, 0)
        grid.addWidget(self.days, 1, 1)
        column.addLayout(grid)
        self.pace_preview = muted("")
        column.addWidget(self.pace_preview)
        column.addWidget(muted(
            "Pick what you will actually do on a bad week. A plan built for "
            "your best week is a plan you will abandon."))
        column.addStretch(1)
        self._preview_pace()
        return page

    # -- wizard flow -------------------------------------------------------

    COPY = (
        ("Welcome", "This takes a minute and can be changed at any time. "
                    "It decides which phases go into your roadmap and how big "
                    "each day looks."),
        ("How much programming have you done?",
         "There is no wrong answer, and nothing gets locked either way."),
        ("What do you want to be able to build?",
         "Pick as many as you like, or none. Your answers add relevant phases "
         "and change what the app suggests each day."),
        ("How much time do you really have?",
         "Used for the finish estimate and to size the daily plan."),
    )

    def _render(self) -> None:
        title, blurb = self.COPY[self.step]
        self.kicker.setText("STEP %d OF %d" % (self.step + 1, len(self.COPY)))
        self.title.setText(title)
        self.blurb.setText(blurb)
        self.stack.setCurrentIndex(self.step)
        self.back_button.setEnabled(self.step > 0)
        self.next_button.setText(
            "Build my plan" if self.step == len(self.COPY) - 1 else "Continue")
        if self.step == 2:
            self._preview_track()

    def _back(self) -> None:
        if self.step > 0:
            self.step -= 1
            self._render()

    def _next(self) -> None:
        if self.step < len(self.COPY) - 1:
            self.step += 1
            self._render()
            return
        self._finish()

    def _chosen_goals(self) -> set:
        return {gid for gid, box in self.goal_boxes.items() if box.isChecked()}

    def _preview_track(self) -> None:
        goals = self._chosen_goals()
        track_id = self.ctx.planner.suggested_track(goals)
        track = self.ctx.curriculum.track(track_id)
        if track is None:
            return
        hours = 0
        for pid in track.core:
            phase = self.ctx.curriculum.phase(pid)
            if phase is not None:
                hours += phase.est_hours
        self.track_preview_label.setText(
            "Suggested track: %s\n\n%s\n\n%d core phases, roughly %d hours."
            % (track.name, track.blurb, len(track.core), hours))

    def _preview_pace(self) -> None:
        goals = self._chosen_goals() if hasattr(self, "goal_boxes") else set()
        track_id = self.ctx.planner.suggested_track(goals)
        track = self.ctx.curriculum.track(track_id)
        hours = 0
        if track is not None:
            for pid in track.core:
                phase = self.ctx.curriculum.phase(pid)
                if phase is not None:
                    hours += phase.est_hours
        weekly = self.hours.value() * self.days.value()
        weeks = hours / weekly if weekly else 0
        self.pace_preview.setText(
            "That is %.1f hours a week, so the core of your track takes about "
            "%d weeks - a little over %d months."
            % (weekly, round(weeks), round(weeks / 4.35)))

    def _finish(self) -> None:
        from datetime import date
        store = self.ctx.store
        goals = sorted(self._chosen_goals())
        experience = "none"
        for option in self.experience_buttons:
            if option.isChecked():
                experience = option.property("value")
                break
        store.set_setting("learner_name", self.name.text().strip())
        store.set_setting("experience", experience)
        store.set_setting("goals", goals)
        store.set_setting("track", self.ctx.planner.suggested_track(set(goals)))
        store.set_setting("hours_per_day", float(self.hours.value()))
        store.set_setting("days_per_week", int(self.days.value()))
        store.set_setting("started_on", date.today().isoformat())
        store.set_setting("onboarded", True)
        self.ctx.settings_changed.emit()
        self.ctx.changed()
        self.accept()

    def _skip(self) -> None:
        from datetime import date
        self.ctx.store.set_setting("onboarded", True)
        self.ctx.store.set_setting("started_on", date.today().isoformat())
        self.ctx.settings_changed.emit()
        self.accept()

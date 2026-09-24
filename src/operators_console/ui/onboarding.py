"""First run: four short questions, then a plan.

Deliberately skippable. Someone who wants to start reading immediately should
be able to, and change their answers later without penalty.

It is also the first thing anyone ever sees of this app, so it is built out of
the same pieces as every other page rather than out of bare form controls: one
segment of a thin meter per step, options that are cards you press instead of
radio dots in a column, and the estimates written out on a focus card. The
wizard starts from what is already stored, so running it again from Settings
shows your answers back to you instead of wiping them.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QDialog, QDoubleSpinBox, QGridLayout,
    QHBoxLayout, QLineEdit, QRadioButton, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from ..core.adaptive import EXPERIENCE_LEVELS, GOALS
from .widgets.common import (
    Card, Scroller, button, divider, label, meter, muted, repolish,
)

#: One line under each experience level, so the choice is about what happens
#: next rather than about how the learner would like to describe themselves.
EXPERIENCE_NOTES = {
    "none": "Starts from zero.",
    "some": "Keeps the basics, with more practice.",
    "other": "Skims syntax. Covers what is specific to Python.",
    "working": "Goes straight to engineering. Fundamentals as review.",
}

#: The same for each goal: what picking it actually adds to the roadmap.
GOAL_NOTES = {
    "web": "HTTP, databases, APIs, deployment.",
    "data": "pandas, charts, SQL, pipelines.",
    "ai": "The math, the libraries, how models work.",
    "vision": "Images, video, detection models.",
    "nlp": "Text classification, extraction, search.",
    "automation": "Scripts, scraping, repetitive tasks.",
    "bots": "Chat bots, webhooks, scheduled jobs.",
    "gui": "Qt, packaging, installable apps.",
    "cli": "Terminal tools other people install.",
    "games": "Game loops, rendering, audio and video.",
    "science": "Numerical methods, simulation, solvers.",
    "finance": "Market data, backtesting, risk.",
    "devops": "Linux, containers, CI, production.",
    "netauto": "Configuring and validating networks.",
    "security": "Attacks, secure code, security tooling.",
    "testing": "Test strategy from unit to end-to-end.",
    "embedded": "Microcontrollers, sensors, MQTT.",
    "blockchain": "Chain data and smart contracts.",
    "interview": "Data structures, algorithms, explaining your reasoning.",
    "fundamentals": "Memory, the interpreter, internals.",
    "langtools": "Parsers, interpreters, compilers.",
}

#: The label column in the pace step, in pixels at a 1.0x text size.
LABEL_COLUMN = 112


class _SelectCard(Card):
    """One option: a real radio button or checkbox, and a line about it.

    The whole card is the target, and the chosen one carries the accent tint
    by wearing the app's own ``#FocusCard`` rather than a stylesheet of its
    own. The control inside keeps the semantics, so Tab and Space still work
    and a screen reader still hears a radio button with a description.
    """

    def __init__(self, control, note: str = "", parent=None) -> None:
        super().__init__(padding=12, spacing=2, parent=parent)
        self.control = control
        self.add(control)
        if note:
            self.add(muted(note))
        control.setAccessibleName(control.text())
        control.setAccessibleDescription(note)
        control.toggled.connect(lambda _on: self.sync())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync()

    def mouseReleaseEvent(self, event) -> None:
        # Pressing anywhere on the card chooses it: a 14 px radio dot is a
        # cruel target, and the description beside it reads as part of the
        # same answer.
        self.control.setFocus(Qt.FocusReason.MouseFocusReason)
        self.control.click()
        event.accept()

    def sync(self) -> None:
        name = "FocusCard" if self.control.isChecked() else "Card"
        if self.objectName() != name:
            self.setObjectName(name)
            repolish(self)


class Onboarding(QDialog):
    """A four-step wizard that writes straight into settings."""

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("Set up your plan")
        self.setModal(True)
        # Opened at the size its words need: at a larger text size the fixed
        # 680 x 560 squeezed the suggested-track summary to half its height.
        try:
            scale = max(1.0, float(ctx.store.setting("font_scale", 1.0)))
        except (TypeError, ValueError):
            scale = 1.0
        self.scale = scale
        width, height = round(680 * scale), round(600 * scale)
        screen = self.screen()
        if screen is not None:
            room = screen.availableGeometry()
            width = min(width, room.width() - 40)
            height = min(height, room.height() - 60)
        self.resize(width, height)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 22)
        outer.setSpacing(16)

        # -- where you are, in something other than words ------------------
        top = QHBoxLayout()
        top.setSpacing(8)
        self.kicker = label("STEP 1 OF 4", "PageKicker", wrap=False)
        top.addWidget(self.kicker)
        top.addStretch(1)
        self.segments = []
        for index in range(len(self.COPY)):
            segment = meter(0)
            segment.setFixedWidth(round(32 * scale))
            segment.setAccessibleName("Step %d of %d"
                                      % (index + 1, len(self.COPY)))
            top.addWidget(segment, 0, Qt.AlignmentFlag.AlignVCenter)
            self.segments.append(segment)
        outer.addLayout(top)

        self.title = label("", "PageTitle")
        outer.addWidget(self.title)
        self.blurb = label("", "PageAim")
        outer.addWidget(self.blurb)
        outer.addWidget(divider())

        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        # Each step scrolls rather than clips: at a 1.6x text size the goal
        # tiles are taller than any dialog a laptop screen will allow.
        for page in (self._step_name(), self._step_experience(),
                     self._step_goals(), self._step_pace()):
            self.stack.addWidget(self._scrolled(page))

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.skip_button = button("Skip for now", "quiet")
        self.skip_button.setAutoDefault(False)
        self.skip_button.clicked.connect(self._skip)
        controls.addWidget(self.skip_button)
        controls.addStretch(1)
        self.back_button = button("Back", "quiet")
        self.back_button.setAutoDefault(False)
        self.back_button.clicked.connect(self._back)
        controls.addWidget(self.back_button)
        self.next_button = button("Continue", "primary")
        # Enter anywhere in the dialog, including in the name field, means
        # Continue.
        self.next_button.setAutoDefault(True)
        self.next_button.setDefault(True)
        self.next_button.clicked.connect(self._next)
        controls.addWidget(self.next_button)
        outer.addLayout(controls)

        self.step = 0
        self._load()
        self._render()

    @staticmethod
    def _scrolled(page: QWidget) -> Scroller:
        holder = Scroller(margins=(0, 0, 8, 0), spacing=0)
        holder.add(page, 1)
        return holder

    # -- steps -------------------------------------------------------------

    def _step_name(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(12)
        card = Card(padding=20, spacing=8)
        card.setObjectName("FocusCard")
        card.add(label("What should the app call you?", "FocusTitle"))
        self.name = QLineEdit()
        self.name.setPlaceholderText("Your name, or anything you like")
        self.name.setAccessibleName("Your name")
        # Sized to the words it holds rather than to the dialog: a fixed
        # 340 px showed two thirds of its own placeholder at 1.6x text.
        self.name.setMaximumWidth(
            self.name.fontMetrics().horizontalAdvance("W" * 24) + 32)
        card.add(self.name)
        card.add(muted(
            "Used only for greetings. It stays on this computer."))
        column.addWidget(card)
        column.addStretch(1)
        return page

    def _step_experience(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        self.experience_buttons = []
        # One group across four separate cards: exclusivity in Qt otherwise
        # goes by parent widget, and the arrow keys walk the group.
        self.experience_group = QButtonGroup(self)
        for value, text in EXPERIENCE_LEVELS:
            option = QRadioButton(text)
            option.setProperty("value", value)
            self.experience_group.addButton(option)
            column.addWidget(_SelectCard(option, EXPERIENCE_NOTES.get(value, "")))
            self.experience_buttons.append(option)
        self.experience_buttons[0].setChecked(True)
        column.addWidget(muted(
            "This changes the advice, not the content. Nothing is hidden."))
        column.addStretch(1)
        return page

    def _step_goals(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(12)
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self.goal_boxes = {}
        for index, (gid, text, _tags) in enumerate(GOALS):
            box = QCheckBox(text)
            box.stateChanged.connect(lambda _s: self._preview_track())
            self.goal_boxes[gid] = box
            grid.addWidget(_SelectCard(box, GOAL_NOTES.get(gid, "")),
                           index // 2, index % 2)
        column.addLayout(grid)

        self.track_preview = Card(padding=16, spacing=4)
        self.track_preview.setObjectName("FocusCard")
        self.track_preview.add(label("SUGGESTED TRACK", "PageKicker",
                                     wrap=False))
        self.track_name = label("", "FocusTitle")
        self.track_preview.add(self.track_name)
        self.track_preview_label = label("", "Soft")
        self.track_preview.add(self.track_preview_label)
        self.track_meta = muted("")
        self.track_preview.add(self.track_meta)
        column.addWidget(self.track_preview)
        column.addStretch(1)
        return page

    def _step_pace(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(12)
        grid = QGridLayout()
        grid.setSpacing(8)
        # Labels in one column, fields sized to their text, the slack in a
        # spare column - as in Settings, rather than a wide empty label
        # column pushing the fields to the right.
        grid.setColumnMinimumWidth(0, round(LABEL_COLUMN * self.scale))
        grid.setColumnStretch(2, 1)
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0.5, 16.0)
        self.hours.setSingleStep(0.5)
        self.hours.setValue(2.0)
        self.hours.setSuffix(" hours a day")
        self.hours.setAccessibleName("Study time, hours a day")
        self.hours.valueChanged.connect(lambda _v: self._preview_pace())
        grid.addWidget(muted("STUDY TIME"), 0, 0)
        grid.addWidget(self.hours, 0, 1)
        self.days = QSpinBox()
        self.days.setRange(1, 7)
        self.days.setValue(5)
        self.days.setSuffix(" days a week")
        self.days.setAccessibleName("Frequency, days a week")
        self.days.valueChanged.connect(lambda _v: self._preview_pace())
        grid.addWidget(muted("FREQUENCY"), 1, 0)
        grid.addWidget(self.days, 1, 1)
        column.addLayout(grid)

        estimate = Card(padding=16, spacing=4)
        estimate.setObjectName("FocusCard")
        self.pace_preview = label("", "FocusTitle")
        estimate.add(self.pace_preview)
        self.pace_months = muted("")
        estimate.add(self.pace_months)
        estimate.add(muted(
            "Pick what you can keep up in a busy week."))
        column.addWidget(estimate)

        self.check_updates = QCheckBox(
            "Tell me when a new version is out (asks GitHub, downloads "
            "nothing)")
        self.check_updates.setChecked(True)
        self.check_updates.setToolTip(
            "Checks GitHub at start, every few minutes while open, and when "
            "you return to the app. Turn it off in Settings.")
        column.addWidget(self.check_updates)
        column.addStretch(1)
        self._preview_pace()
        return page

    # -- wizard flow -------------------------------------------------------

    COPY = (
        ("Welcome", "Four questions. They set which phases are in your "
                    "roadmap and how much each day holds. You can change them "
                    "later."),
        ("How much programming have you done?",
         "Nothing gets locked either way."),
        ("What do you want to be able to build?",
         "Pick any number, or none. Each one adds phases to your plan."),
        ("How much time do you have?",
         "Sets the daily plan and the finish estimate."),
    )

    def _load(self) -> None:
        """Start from the stored answers.

        Run again from Settings, the wizard used to open on its defaults and
        write them all back over the learner's choices on the last press.
        """
        store = self.ctx.store
        self.name.setText(str(store.setting("learner_name", "") or ""))
        experience = store.setting("experience", "none")
        for option in self.experience_buttons:
            if option.property("value") == experience:
                option.setChecked(True)
                break
        chosen = set(store.setting("goals", []) or [])
        for gid, box in self.goal_boxes.items():
            box.setChecked(gid in chosen)
        try:
            self.hours.setValue(float(store.setting("hours_per_day", 2.0)))
            self.days.setValue(int(store.setting("days_per_week", 5)))
        except (TypeError, ValueError):
            pass
        self.check_updates.setChecked(
            bool(store.setting("check_for_updates", True)))

    def _render(self) -> None:
        title, blurb = self.COPY[self.step]
        self.kicker.setText("STEP %d OF %d" % (self.step + 1, len(self.COPY)))
        self.title.setText(title)
        self.blurb.setText(blurb)
        self.stack.setCurrentIndex(self.step)
        self.back_button.setEnabled(self.step > 0)
        self.next_button.setText(
            "Build my plan" if self.step == len(self.COPY) - 1 else "Continue")
        for index, segment in enumerate(self.segments):
            segment.setValue(100 if index <= self.step else 0)
            tone = "done" if index < self.step else ""
            if (segment.property("tone") or "") != tone:
                segment.setProperty("tone", tone)
                repolish(segment)
        if self.step == 2:
            self._preview_track()
        elif self.step == 3:
            self._preview_pace()

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

    def _track_hours(self, track) -> int:
        hours = 0
        if track is not None:
            for pid in track.core:
                phase = self.ctx.curriculum.phase(pid)
                if phase is not None:
                    hours += phase.est_hours
        return hours

    def _preview_track(self) -> None:
        goals = self._chosen_goals()
        track_id = self.ctx.planner.suggested_track(goals)
        track = self.ctx.curriculum.track(track_id)
        if track is None:
            return
        self.track_name.setText(track.name)
        self.track_preview_label.setText(track.blurb)
        self.track_meta.setText(
            "%d core phases, roughly %d hours."
            % (len(track.core), self._track_hours(track)))
        # The estimate on the last step is built from these goals too.
        if hasattr(self, "hours"):
            self._preview_pace()

    def _preview_pace(self) -> None:
        goals = self._chosen_goals() if hasattr(self, "goal_boxes") else set()
        track_id = self.ctx.planner.suggested_track(goals)
        hours = self._track_hours(self.ctx.curriculum.track(track_id))
        weekly = self.hours.value() * self.days.value()
        weeks = hours / weekly if weekly else 0
        self.pace_preview.setText(
            "%.1f hours a week. The core of your track takes about %d weeks." % (weekly, round(weeks)))
        months = max(1, round(weeks / 4.35))
        self.pace_months.setText(
            "About %d month%s at that pace."
            % (months, "" if months == 1 else "s"))

    # -- leaving -----------------------------------------------------------

    def _stamp_start(self) -> None:
        """Day one is the day the app was first opened, and never moves.

        Running the wizard again from Settings used to reset it, which moved
        the finish estimate and every "day N" in the app with it.
        """
        if not self.ctx.store.setting("started_on", ""):
            self.ctx.store.set_setting("started_on", date.today().isoformat())

    def _finish(self) -> None:
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
        store.set_setting("check_for_updates", self.check_updates.isChecked())
        self._stamp_start()
        store.set_setting("onboarded", True)
        self.ctx.settings_changed.emit()
        self.ctx.changed()
        self.accept()

    def _skip(self) -> None:
        self.ctx.store.set_setting("onboarded", True)
        self._stamp_start()
        self.ctx.settings_changed.emit()
        self.accept()

    def reject(self) -> None:
        """Escape asks nothing and skips, exactly like the Skip button."""
        self._skip()

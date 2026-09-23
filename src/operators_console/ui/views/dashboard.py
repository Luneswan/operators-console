"""Today: the only page a learner has to look at to know what to do.

One ring for how far along they are, one strip of numbers, one action that
gets the whole card, and the rest as a short list.
"""
from __future__ import annotations

import time
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from ...core import today as plan_kinds
from ...core.progress import _number as _setting_number
from ...core.progress import proof_line
from ..widgets.common import (
    Card, StatTile, button, clear_layout, empty_state, heading, label, meter,
    muted, pill,
)
from ..widgets.ring import ProgressRing
from .base import View

KIND_LABEL = {
    plan_kinds.REVIEW: ("Review", "accent"),
    plan_kinds.LEARN: ("Study", ""),
    plan_kinds.PRACTICE: ("Practise", ""),
    plan_kinds.QUIZ: ("Quiz", ""),
    plan_kinds.PROJECT: ("Project", "warn"),
    plan_kinds.GATE: ("Gate", "done"),
    plan_kinds.LOG: ("Log", ""),
}

KIND_ROUTE = {
    plan_kinds.REVIEW: "review",
    plan_kinds.LEARN: "phase",
    plan_kinds.PRACTICE: "practice",
    plan_kinds.QUIZ: "quiz",
    plan_kinds.PROJECT: "projects",
    plan_kinds.GATE: "phase",
    plan_kinds.LOG: "journal",
}


def _vdivider() -> QFrame:
    line = QFrame()
    line.setObjectName("VDivider")
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFixedWidth(1)
    return line


def _row_divider() -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    return line


class DashboardView(View):
    title = "Today"

    def build(self) -> None:
        hero = QHBoxLayout()
        hero.setSpacing(24)
        words = QVBoxLayout()
        words.setSpacing(6)
        words.addWidget(label("YOUR POSITION", "PageKicker", wrap=False))
        self.greeting = label("", "PageTitle")
        words.addWidget(self.greeting)
        self.subtitle = label("", "PageAim")
        words.addWidget(self.subtitle)
        words.addStretch(1)
        hero.addLayout(words, 1)
        self.ring = ProgressRing(self.ctx.palette, 88)
        self.tile_percent = self.ring          # the ring is the percent tile
        hero.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignTop)
        self.scroller.add_layout(hero)

        strip = QWidget()
        strip.setObjectName("StatStrip")
        strip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        row = QHBoxLayout(strip)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(0)
        self.tile_streak = StatTile("0", "Day streak")
        self.tile_due = StatTile("0", "Cards due")
        self.tile_hours = StatTile("0", "Hours logged")
        self.tile_phases = StatTile("0", "Phases proven")
        for index, tile in enumerate((self.tile_streak, self.tile_due,
                                      self.tile_hours, self.tile_phases)):
            if index:
                row.addWidget(_vdivider())
            row.addWidget(tile, 1)
        self.scroller.add(strip)
        self.overall_meter = meter(0)
        self.overall_meter.setVisible(False)    # the ring shows it
        self.scroller.add(self.overall_meter)
        self.overall_caption = muted("")
        self.scroller.add(self.overall_caption)

        plan_head = QHBoxLayout()
        plan_head.addWidget(heading("The next few hours"))
        plan_head.addStretch(1)
        self.plan_note = muted("")
        plan_head.addWidget(self.plan_note)
        self.scroller.add_layout(plan_head)
        self.plan_holder = QVBoxLayout()
        self.plan_holder.setSpacing(10)
        self.scroller.add_layout(self.plan_holder)

        self.position_heading = heading("Where you are")
        self.scroller.add(self.position_heading)
        self.position_card = Card()
        self.scroller.add(self.position_card)

        self.scroller.add_stretch()

    # -- refresh -----------------------------------------------------------

    def refresh(self) -> None:
        # The greeting follows the hour and the due count the clock, so the
        # ten-minute bucket is part of what the page was drawn from.
        # What the learner pushed off is part of it too: "Not today" is the
        # one input to this page that is not a row in the store's tables.
        now = time.localtime()
        stamp = (now.tm_yday, now.tm_hour, now.tm_min // 10,
                 tuple(sorted(self.ctx.today.dismissed_keys())))
        if self.store_unchanged(stamp):
            return
        store = self.ctx.store
        overview = self.ctx.progress.overview()
        name = store.setting("learner_name", "").strip()
        self.greeting.setText(_greeting(name))

        track = self.ctx.curriculum.track(store.setting("track", "generalist"))
        days = self.ctx.progress.estimated_days_left()
        # Settings are JSON and a restored profile can hold anything; the
        # first screen of the app must not open on a traceback over it.
        pace = "%.1f h/day, %d days a week" % (
            _setting_number(store.setting("hours_per_day", 3.0), 3.0),
            int(_setting_number(store.setting("days_per_week", 5), 5.0)))
        finish = ("about %d weeks left at %s" % (max(1, round(days / 7)), pace)
                  if days > 0 else "the plan is complete")
        self.subtitle.setText("%s - %s." % (
            track.name if track else "Custom plan", finish))

        self.ring.set_value(overview.percent)
        self.tile_streak.set_value(str(overview.streak))
        self.tile_due.set_value(str(overview.due_cards))
        self.tile_hours.set_value("%.0f" % overview.hours)
        self.tile_phases.set_value("%d/%d" % (overview.phases_complete,
                                             overview.phases_total))

        self.overall_meter.setValue(overview.percent)
        self.overall_caption.setText(
            "%d of %d checks - %d of %d phases proven - %d of %d exercises "
            "passed - %d of %d projects shipped"
            % (overview.done, overview.total, overview.phases_complete,
               overview.phases_total, overview.exercises_done,
               overview.exercises_total, overview.projects_shipped,
               overview.projects_total))

        self._fill_plan()
        self._fill_position()
        self.mark_drawn(stamp)

    def on_theme(self) -> None:
        if self._built:
            self.ring.set_theme(self.ctx.palette)

    def _fill_plan(self) -> None:
        clear_layout(self.plan_holder)
        actions, hidden = self.ctx.today.split()
        self.plan_note.setText(
            self._plan_note(sum(a.minutes for a in actions)))
        if actions:
            self.plan_holder.addWidget(self._focus_card(actions[0]))
            if len(actions) > 1:
                self.plan_holder.addWidget(self._action_list(actions[1:]))
        else:
            self.plan_holder.addWidget(self._nothing_card())
        if hidden:
            self.plan_holder.addWidget(self._hidden_row(len(hidden)))

    def _plan_note(self, minutes: int) -> str:
        """How long the list is, against what the learner has actually done.

        "about 95 min" on its own is a demand. Beside the hours already
        logged it is a position: most of a short day is gone, or none of a
        long one is.
        """
        logged = self.ctx.today.hours_today()
        target = _setting_number(
            self.ctx.store.setting("hours_per_day", 3.0), 3.0)
        bits = []
        if minutes:
            bits.append("about %d min" % minutes)
        if target > 0:
            bits.append("%s h of your %s h logged today"
                        % (_hours(logged), _hours(target)))
        elif logged:
            bits.append("%s h logged today" % _hours(logged))
        return "  -  ".join(bits)

    def _nothing_card(self) -> Card:
        """The empty list. Finishing the plan is not the same as a quiet day."""
        if self.ctx.progress.is_finished:
            return empty_state(
                "Nothing due, and nothing left to learn.",
                "Every phase in your plan is finished. Keep the review deck "
                "ticking over, ship something of your own, or pick a new "
                "track in Settings.")
        return empty_state(
            "Nothing outstanding today.",
            "Pick any phase and push it forward, or take the evening off. "
            "The plan will still be here tomorrow.")

    def _hidden_row(self, count: int) -> QWidget:
        """The way back from "Not today"."""
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(10, 0, 10, 0)
        box.setSpacing(8)
        back = button("Show %d hidden" % count, "quiet",
                      "Put back what you pushed off today")
        back.clicked.connect(self._restore_hidden)
        box.addWidget(back)
        box.addWidget(muted("They come back tomorrow anyway."), 1)
        return row

    def _dismiss_button(self, action):
        """One factory, so "Not today" reads and behaves the same everywhere."""
        skip = button("Not today", "quiet",
                      "Hide this for the rest of the day")
        skip.clicked.connect(lambda _=False, a=action: self._dismiss(a))
        return skip

    def _dismiss(self, action) -> None:
        self.ctx.today.dismiss(action)
        self.ctx.announce("Hidden until tomorrow.")
        self.refresh()

    def _restore_hidden(self) -> None:
        self.ctx.today.restore()
        self.ctx.announce("Back on today's list.")
        self.refresh()

    def _start_button(self, action, kind: str = "primary"):
        go = button("Start", kind)
        route = KIND_ROUTE.get(action.kind, "roadmap")
        go.clicked.connect(
            lambda _=False, r=route, t=action.target:
            self.ctx.navigate.emit(r, t))
        return go

    def _focus_card(self, action) -> Card:
        """The next thing to do gets the whole card."""
        card = Card(padding=20, spacing=8)
        card.setObjectName("FocusCard")
        text, tone = KIND_LABEL.get(action.kind, (action.kind.title(), ""))
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(label("UP NEXT", "PageKicker", wrap=False))
        top.addWidget(pill(text, tone))
        top.addStretch(1)
        top.addWidget(muted("%d min" % action.minutes))
        card.box.addLayout(top)
        card.add(label(action.title, "FocusTitle", wrap=True))
        if action.detail:
            card.add(label(action.detail, "Soft"))
        go = self._start_button(action)
        go.setMinimumHeight(34)
        go.setMinimumWidth(96)
        card.add_row(go, self._dismiss_button(action), None)
        return card

    def _action_list(self, actions) -> Card:
        """Everything after the first, one compact row each."""
        card = Card(padding=6, spacing=0)
        for index, action in enumerate(actions):
            if index:
                card.add(_row_divider())
            card.add(self._action_row(action))
        return card

    def _action_row(self, action) -> QWidget:
        row = QWidget()
        row.setObjectName("ActionRow")
        row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box = QHBoxLayout(row)
        box.setContentsMargins(10, 8, 10, 8)
        box.setSpacing(10)
        text, tone = KIND_LABEL.get(action.kind, (action.kind.title(), ""))
        box.addWidget(pill(text, tone))
        box.addWidget(label(action.title, "RowTitle", wrap=True), 1)
        box.addWidget(muted("%d min" % action.minutes))
        box.addWidget(self._start_button(action, ""))
        box.addWidget(self._dismiss_button(action))
        return row

    def _fill_position(self) -> None:
        clear_layout(self.position_card.box)

        # Finishing has to be a state of its own. The position marker names
        # the last phase whatever happens, so read on its own it says "you
        # are here" about a phase that was finished weeks ago.
        if self.ctx.progress.is_finished:
            self.position_heading.setText("What you did")
            self._fill_completion()
            return
        self.position_heading.setText("Where you are")

        pid = self.ctx.progress.current_phase_id()
        phase = self.ctx.curriculum.phase(pid)
        if phase is None:
            return
        stats = self.ctx.progress.phase(phase)
        open_button = button("Open this phase", "primary")
        open_button.clicked.connect(
            lambda: self.ctx.navigate.emit("phase", pid))
        heading_row = QHBoxLayout()
        heading_row.setSpacing(12)
        heading_row.addWidget(label("PHASE %s  -  %s" % (phase.num, phase.when),
                                    "Muted", wrap=False))
        heading_row.addStretch(1)
        heading_row.addWidget(open_button)
        self.position_card.box.addLayout(heading_row)

        self.position_card.add(label(phase.name, "FocusTitle"))
        self.position_card.add(label(phase.aim, "Soft"))
        self.position_card.add(meter(stats.percent))
        self.position_card.add(muted(
            "%d of %d checks - %d of %d exercises - gate %s"
            % (stats.done, stats.total, stats.exercises_done,
               stats.exercises_total,
               "cleared" if stats.gate_cleared
               else "%d/%d" % (stats.gate_done, stats.gate_total))))
        # The marker moves on proof, so the card says what is holding it.
        self.position_card.add(label(proof_line(stats), "Soft"))


    # -- the end of the plan -----------------------------------------------

    def _fill_completion(self) -> None:
        """Today, for someone who has finished the whole curriculum.

        The numbers they earned, the span they took, and the three things
        there are left to do with the app.
        """
        overview = self.ctx.progress.overview()
        card = self.position_card

        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(label("THE WHOLE PLAN", "PageKicker", wrap=False))
        top.addWidget(pill("COMPLETE", "done"))
        top.addStretch(1)
        card.box.addLayout(top)

        card.add(label("You finished it.", "FocusTitle"))
        card.add(label(
            "%d of %d checks ticked, %d of %d phases proven, %d of %d "
            "exercises passed and %d of %d projects shipped."
            % (overview.done, overview.total, overview.phases_complete,
               overview.phases_total, overview.exercises_done,
               overview.exercises_total, overview.projects_shipped,
               overview.projects_total), "Soft"))
        card.add(muted(self._span_line(overview)))

        self.report_button = button("Export report", "primary",
                                    "Write the whole record out as Markdown")
        self.report_button.clicked.connect(self._export_report)
        self.reviewing_button = button(
            "Keep reviewing", "", "Your deck still comes due")
        self.reviewing_button.clicked.connect(
            lambda: self.ctx.navigate.emit("review", ""))
        self.track_button = button("Change track", "quiet",
                                   "Take on a different plan in Settings")
        self.track_button.clicked.connect(
            lambda: self.ctx.navigate.emit("settings", ""))
        card.add_row(self.report_button, self.reviewing_button,
                     self.track_button, None)

    def _span_line(self, overview) -> str:
        started = self.ctx.progress.started_on()
        today = date.today()
        hours = "%.0f hours logged" % overview.hours
        streak = "longest streak %d days" % overview.longest_streak
        try:
            first = date.fromisoformat(started)
        except (TypeError, ValueError):
            first = None
        if first is None or first > today:
            return "%s  -  %s" % (hours, streak)
        return "%s to %s - %d days - %s - %s" % (
            started, today.isoformat(), (today - first).days + 1, hours,
            streak)

    def _export_report(self) -> None:
        """The File menu's "Export progress report...", pressed from here.

        The same handler rather than a copy of it, so there is one file
        dialog, one error message and one announcement in the app.
        """
        window = self.window()
        handler = getattr(window, "_report", None)
        if callable(handler):
            handler()
            return
        self.ctx.navigate.emit("settings", "")


def _hours(value: float) -> str:
    """3.0 reads as 3; 1.5 stays 1.5."""
    return ("%.1f" % value).rstrip("0").rstrip(".") or "0"


def _greeting(name: str) -> str:
    from datetime import datetime
    hour = datetime.now().hour
    part = ("Good morning" if hour < 12
            else "Good afternoon" if hour < 18 else "Good evening")
    return "%s, %s." % (part, name) if name else part + "."

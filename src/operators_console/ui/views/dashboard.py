"""Today: the only page a learner has to look at to know what to do."""
from __future__ import annotations


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout

from ...core import today as plan_kinds
from ..widgets.common import (
    Card, StatTile, button, divider, heading, label, meter, muted, pill,
)
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


class DashboardView(View):
    title = "Today"

    def build(self) -> None:
        self.greeting = label("", "PageTitle")
        self.scroller.add(label("YOUR POSITION", "PageKicker", wrap=False))
        self.scroller.add(self.greeting)
        self.subtitle = label("", "PageAim")
        self.scroller.add(self.subtitle)

        self.tiles = QGridLayout()
        self.tiles.setSpacing(12)
        self.tile_percent = StatTile("0%", "Curriculum complete")
        self.tile_streak = StatTile("0", "Day streak")
        self.tile_due = StatTile("0", "Cards due")
        self.tile_hours = StatTile("0", "Hours logged")
        for column, tile in enumerate(
                (self.tile_percent, self.tile_streak, self.tile_due,
                 self.tile_hours)):
            self.tiles.addWidget(tile, 0, column)
        self.scroller.add_layout(self.tiles)

        self.overall_meter = meter(0)
        self.scroller.add(self.overall_meter)
        self.overall_caption = muted("")
        self.scroller.add(self.overall_caption)

        self.scroller.add(divider())
        self.scroller.add(heading("The next few hours"))
        self.plan_holder = QVBoxLayout()
        self.plan_holder.setSpacing(9)
        self.scroller.add_layout(self.plan_holder)

        self.scroller.add(heading("Where you are"))
        self.position_card = Card()
        self.scroller.add(self.position_card)

        self.scroller.add_stretch()

    # -- refresh -----------------------------------------------------------

    def refresh(self) -> None:
        store = self.ctx.store
        overview = self.ctx.progress.overview()
        name = store.setting("learner_name", "").strip()
        self.greeting.setText(_greeting(name))

        track = self.ctx.curriculum.track(store.setting("track", "generalist"))
        days = self.ctx.progress.estimated_days_left()
        pace = "%.1f h/day, %d days a week" % (
            float(store.setting("hours_per_day", 3.0)),
            int(store.setting("days_per_week", 5)))
        finish = ("about %d weeks left at %s" % (max(1, round(days / 7)), pace)
                  if days > 0 else "the plan is complete")
        self.subtitle.setText("%s - %s." % (
            track.name if track else "Custom plan", finish))

        self.tile_percent.set_value("%d%%" % overview.percent)
        self.tile_streak.set_value(str(overview.streak))
        self.tile_due.set_value(str(overview.due_cards))
        self.tile_hours.set_value("%.0f" % overview.hours)

        self.overall_meter.setValue(overview.percent)
        self.overall_caption.setText(
            "%d of %d checks - %d of %d phases finished - %d of %d exercises "
            "passed - %d of %d projects shipped"
            % (overview.done, overview.total, overview.phases_complete,
               overview.phases_total, overview.exercises_done,
               overview.exercises_total, overview.projects_shipped,
               overview.projects_total))

        self._fill_plan()
        self._fill_position()

    def _fill_plan(self) -> None:
        _clear(self.plan_holder)
        actions = self.ctx.today.build()
        if not actions:
            card = Card()
            card.add(label("Nothing outstanding. Pick any phase and push it "
                           "forward, or take the evening off.", "Soft"))
            self.plan_holder.addWidget(card)
            return
        for action in actions:
            self.plan_holder.addWidget(self._action_card(action))

    def _action_card(self, action) -> Card:
        card = Card()
        text, tone = KIND_LABEL.get(action.kind, (action.kind.title(), ""))
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(pill(text, tone), 0, Qt.AlignmentFlag.AlignTop)
        title = label(action.title, wrap=True)
        title.setStyleSheet("font-weight: 700; font-size: 14px;")
        top.addWidget(title, 1)
        top.addWidget(muted("%d min" % action.minutes), 0,
                      Qt.AlignmentFlag.AlignTop)
        card.box.addLayout(top)
        if action.detail:
            card.add(label(action.detail, "Soft"))
        go = button("Start", "primary")
        route = KIND_ROUTE.get(action.kind, "roadmap")
        go.clicked.connect(
            lambda _=False, r=route, t=action.target:
            self.ctx.navigate.emit(r, t))
        card.add_row(None, go)
        return card

    def _fill_position(self) -> None:
        while self.position_card.box.count():
            item = self.position_card.box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout() is not None:
                _clear(item.layout())

        pid = self.ctx.progress.current_phase_id()
        phase = self.ctx.curriculum.phase(pid)
        if phase is None:
            return
        stats = self.ctx.progress.phase(phase)
        heading_row = QHBoxLayout()
        heading_row.addWidget(muted("PHASE %s" % phase.num))
        heading_row.addStretch(1)
        heading_row.addWidget(muted(phase.when))
        self.position_card.box.addLayout(heading_row)

        name = label(phase.name)
        name.setStyleSheet("font-size: 17px; font-weight: 700;")
        self.position_card.add(name)
        self.position_card.add(label(phase.aim, "Soft"))
        self.position_card.add(meter(stats.percent))
        self.position_card.add(muted(
            "%d of %d checks - %d of %d exercises - gate %s"
            % (stats.done, stats.total, stats.exercises_done,
               stats.exercises_total,
               "cleared" if stats.gate_cleared
               else "%d/%d" % (stats.gate_done, stats.gate_total))))
        open_button = button("Open this phase", "primary")
        open_button.clicked.connect(
            lambda: self.ctx.navigate.emit("phase", pid))
        self.position_card.add_row(None, open_button)


def _greeting(name: str) -> str:
    from datetime import datetime
    hour = datetime.now().hour
    part = ("Good morning" if hour < 12
            else "Good afternoon" if hour < 18 else "Good evening")
    return "%s, %s." % (part, name) if name else part + "."


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())

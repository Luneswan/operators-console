"""The roadmap: every phase in the learner's plan, in teaching order."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from ..widgets.common import (
    Card, button, divider, heading, label, meter, muted, pill,
)
from .base import View

ROLE_TONE = {"core": "accent", "optional": "", "extra": "warn"}
ROLE_TEXT = {"core": "CORE", "optional": "OPTIONAL", "extra": "ADDED FOR YOU"}


class RoadmapView(View):
    title = "Roadmap"

    def build(self) -> None:
        self.header("Your roadmap", "the plan",
                    "Ordered so that nothing asks you to use something you have "
                    "not been taught. Phases are never locked - the state is "
                    "advice, not a gate.")
        self.summary = muted("")
        self.scroller.add(self.summary)
        self.scroller.add(divider())
        self.holder = QVBoxLayout()
        self.holder.setSpacing(11)
        self.scroller.add_layout(self.holder)

        self.scroller.add(divider())
        self.scroller.add(heading("Not in your plan"))
        self.scroller.add(muted(
            "Available any time. Change your track in Settings to bring one "
            "into the plan."))
        self.extras = QVBoxLayout()
        self.extras.setSpacing(8)
        self.scroller.add_layout(self.extras)
        self.scroller.add_stretch()

    def refresh(self) -> None:
        _clear(self.holder)
        _clear(self.extras)
        rows = self.ctx.planner.roadmap()
        stats = self.ctx.progress.all_phases()
        in_plan = {row.phase_id for row in rows}

        track = self.ctx.curriculum.track(
            self.ctx.store.setting("track", "generalist"))
        hours = sum(self.ctx.curriculum.phase(r.phase_id).est_hours
                    for r in rows
                    if self.ctx.curriculum.phase(r.phase_id) is not None)
        self.summary.setText(
            "%s - %d phases, roughly %d hours of work."
            % (track.name if track else "Custom", len(rows), hours))

        current = self.ctx.progress.current_phase_id()
        for row in rows:
            phase = self.ctx.curriculum.phase(row.phase_id)
            if phase is None:
                continue
            self.holder.addWidget(
                self._phase_card(phase, row, stats.get(phase.id),
                                 phase.id == current))

        for phase in self.ctx.curriculum.phases:
            if phase.id in in_plan or phase.no_progress:
                continue
            self.extras.addWidget(self._compact_card(phase, stats.get(phase.id)))

    # -- cards -------------------------------------------------------------

    def _phase_card(self, phase, row, stats, is_current: bool) -> Card:
        card = Card()
        top = QHBoxLayout()
        top.setSpacing(9)
        top.addWidget(pill(phase.num, "accent" if is_current else ""))
        title = label(phase.name)
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        top.addWidget(title, 1)
        if is_current:
            top.addWidget(pill("YOU ARE HERE", "accent"))
        elif stats and stats.is_complete:
            top.addWidget(pill("DONE", "done"))
        elif not row.unlocked:
            top.addWidget(pill("EARLY", "warn"))
        top.addWidget(pill(ROLE_TEXT.get(row.role, ""), ROLE_TONE.get(row.role, "")))
        card.box.addLayout(top)

        card.add(label(phase.aim, "Soft"))
        card.add(muted("%s - about %d hours - %s"
                       % (phase.when, phase.est_hours, row.reason)))

        percent = stats.percent if stats else 0
        card.add(meter(percent, tone="done" if percent >= 100 else ""))

        if stats:
            bits = ["%d/%d checks" % (stats.done, stats.total)]
            if stats.exercises_total:
                bits.append("%d/%d exercises"
                            % (stats.exercises_done, stats.exercises_total))
            if stats.gate_total:
                bits.append("gate %d/%d" % (stats.gate_done, stats.gate_total))
            if stats.projects_total:
                bits.append("%d/%d projects"
                            % (stats.projects_shipped, stats.projects_total))
            card.add(muted("  -  ".join(bits)))

        if not row.unlocked:
            names = [self.ctx.curriculum.phase(p).name
                     for p in phase.prereq
                     if self.ctx.curriculum.phase(p) is not None]
            card.add(muted("Usually taken after: " + ", ".join(names)))

        open_button = button("Open", "primary" if is_current else "")
        open_button.clicked.connect(
            lambda _=False, pid=phase.id: self.ctx.navigate.emit("phase", pid))
        card.add_row(None, open_button)
        return card

    def _compact_card(self, phase, stats) -> Card:
        card = Card(padding=11, spacing=5)
        row = QHBoxLayout()
        row.setSpacing(9)
        row.addWidget(pill(phase.num))
        title = label(phase.name, wrap=False)
        title.setStyleSheet("font-weight: 700;")
        row.addWidget(title, 1)
        if stats and stats.is_started:
            row.addWidget(muted("%d%%" % stats.percent))
        open_button = button("Open", "quiet")
        open_button.clicked.connect(
            lambda _=False, pid=phase.id: self.ctx.navigate.emit("phase", pid))
        row.addWidget(open_button)
        card.box.addLayout(row)
        card.add(muted(phase.aim))
        return card


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())

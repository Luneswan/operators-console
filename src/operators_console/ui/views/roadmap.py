"""The roadmap: every phase in the learner's plan, as a timeline.

A rail runs down the left with one node per phase - a tick where a phase is
done, the accent where the learner is, a number where they have not been
yet - so the shape of the whole plan is visible before a word is read.
"""
from __future__ import annotations

import time

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ...core.estimate import format_day, format_hours
from ...core.progress import QUIZ_PROOF
from ..widgets import icons
from ..widgets.common import (
    Card, Disclosure, button, clear_layout, divider, heading, label, meter,
    muted, pill,
)
from .base import View

ROLE_TONE = {"core": "accent", "optional": "", "extra": "warn"}
ROLE_TEXT = {"core": "CORE", "optional": "OPTIONAL", "extra": "ADDED FOR YOU"}

DONE, CURRENT, AHEAD = "done", "current", "ahead"


class Rail(QWidget):
    """The node and the line through it, for one row of the timeline."""

    WIDTH = 40
    NODE_Y = 15
    RADIUS = 11

    def __init__(self, palette, state: str, number: str, first: bool,
                 last: bool, parent=None) -> None:
        super().__init__(parent)
        self.colours = palette
        self.state = state
        self.number = number
        self.first, self.last = first, last
        self.setFixedWidth(self.WIDTH)

    def set_theme(self, palette) -> None:
        self.colours = palette
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        centre_x = self.RADIUS + 2
        line = QPen(QColor(self.colours.rule_2), 2)
        painter.setPen(line)
        top = self.NODE_Y if self.first else 0
        bottom = self.NODE_Y if self.last else self.height()
        if bottom > top:
            painter.drawLine(QPointF(centre_x, top), QPointF(centre_x, bottom))

        node = QRectF(centre_x - self.RADIUS, self.NODE_Y - self.RADIUS,
                      2 * self.RADIUS, 2 * self.RADIUS)
        if self.state == DONE:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.colours.done))
            painter.drawEllipse(node)
            painter.drawPixmap(
                int(centre_x - 7), int(self.NODE_Y - 7),
                icons.pixmap("check", self.colours.on_accent, 14,
                             self.devicePixelRatioF()))
            painter.end()
            return
        if self.state == CURRENT:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.colours.accent))
            text = self.colours.on_accent
        else:
            painter.setPen(QPen(QColor(self.colours.rule_strong), 1.5))
            painter.setBrush(QColor(self.colours.surface))
            text = self.colours.ink_soft
        painter.drawEllipse(node)
        font = QFont(self.font())
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(text))
        painter.drawText(node, Qt.AlignmentFlag.AlignCenter, self.number)
        painter.end()


class RoadmapView(View):
    title = "Roadmap"

    def build(self) -> None:
        self.header("Your roadmap", "the plan",
                    "Each phase comes after what it needs. Dates follow your "
                    "measured pace and study hours. None are locked.")
        self.summary = muted("")
        self.scroller.add(self.summary)

        # The whole plan in four numbers, then what they rest on.
        self.overview = Card(padding=14, spacing=6)
        numbers = QHBoxLayout()
        numbers.setSpacing(18)
        self.left_value = self._figure(numbers, "LEFT AT YOUR PACE")
        self.finish_value = self._figure(numbers, "DONE AROUND")
        self.proven_value = self._figure(numbers, "PHASES PROVEN")
        self.pace_value = self._figure(numbers, "YOUR PACE")
        numbers.addStretch(1)
        self.overview.box.addLayout(numbers)
        self.overview_bar = meter(0, 1000, "done")
        self.overview.add(self.overview_bar)
        self.overview_basis = muted("")
        self.overview.add(self.overview_basis)
        self.scroller.add(self.overview)

        # Shown only once every phase in the plan is complete. The timeline
        # then has no "you are here" on it at all, and an unmarked rail on
        # its own would read as a bug rather than as an ending.
        self.finished_banner = Card()
        banner_top = QHBoxLayout()
        banner_top.setSpacing(8)
        banner_top.addWidget(label("Plan complete.",
                                   "FocusTitle"), 1)
        banner_top.addWidget(pill("PLAN COMPLETE", "done"))
        self.finished_banner.box.addLayout(banner_top)
        self.finished_banner.add(muted(
            "Open any phase to revisit it, or change your track in Settings "
            "to add phases."))
        self.finished_banner.setVisible(False)
        self.scroller.add(self.finished_banner)

        self.holder = QVBoxLayout()
        self.holder.setSpacing(0)          # the rail runs unbroken
        self.scroller.add_layout(self.holder)

        self.scroller.add(divider())
        self.scroller.add(heading("Not in your plan"))
        self.scroller.add(muted(
            "Open any time. Change your track or goals in Settings to add "
            "them to the plan."))
        # Folded: with every pathway in the course this list is long, and it
        # is reference, not the plan.
        self.outside = Disclosure(0, "phases outside your plan",
                                  store=self.ctx.store,
                                  key="roadmap:outside", tag="", more=False)
        self.scroller.add(self.outside)
        self.extras = self.outside.stack
        self.scroller.add_stretch()

    def refresh(self) -> None:
        # Every visit used to tear down and rebuild all of the phase cards.
        # Dates count from today, so a new day redraws too.
        today = time.strftime("%Y-%m-%d")
        if self.store_unchanged(today):
            return
        self._draw()
        self.mark_drawn(today)

    def on_theme(self) -> None:
        if not self._built:
            return
        for rail in self.findChildren(Rail):
            rail.set_theme(self.ctx.palette)

    @staticmethod
    def _figure(row, caption: str):
        column = QVBoxLayout()
        column.setSpacing(2)
        value = label("", "RowTitle", wrap=False)
        value.setAccessibleName(caption.capitalize())
        column.addWidget(value)
        column.addWidget(muted(caption))
        row.addLayout(column)
        return value

    def _draw(self) -> None:
        from ..widgets.time_left import basis_text, other_date_text
        clear_layout(self.holder)
        clear_layout(self.extras)
        rows = self.ctx.planner.roadmap()
        stats = self.ctx.progress.all_phases()
        in_plan = {row.phase_id for row in rows}
        estimate = self.ctx.estimator.estimate()
        milestones = self.ctx.progress.career_milestones()

        track = self.ctx.curriculum.track(
            self.ctx.store.setting("track", "generalist"))
        finished = self.ctx.progress.is_finished
        self.finished_banner.setVisible(finished)
        self.summary.setText(
            "%s - %d phases, %s of work at the course estimate%s"
            % (track.name if track else "Custom", len(rows),
               format_hours(estimate.total_minutes),
               ", all done." if finished else "."))
        proven = sum(1 for r in rows if stats.get(r.phase_id)
                     and stats[r.phase_id].is_proven)
        self.left_value.setText(format_hours(estimate.left_personal)
                                if estimate.left_minutes > 0 else "None")
        self.finish_value.setText(format_day(estimate.finish))
        self.proven_value.setText("%d of %d" % (proven, len(rows)))
        factor = estimate.pace.factor
        self.pace_value.setText("%.2fx the estimate" % factor
                                if estimate.pace.measured else "Not measured")
        self.overview_bar.setValue(round(estimate.done_fraction * 1000))
        self.overview_bar.setToolTip("%d%% of the estimated work is done"
                                     % round(estimate.done_fraction * 100))
        other = other_date_text(estimate)
        self.overview_basis.setText(
            basis_text(estimate) + (" " + other if other else "")
            + ("" if estimate.pace.measured else
               " Time your sessions (Study > Start, Ctrl+T) to measure it."))

        # The marker always names a phase, so on a finished plan it pins
        # "YOU ARE HERE" to the last one for ever. There is no here any more.
        current = "" if finished else self.ctx.progress.current_phase_id()
        phases = [(row, self.ctx.curriculum.phase(row.phase_id)) for row in rows]
        phases = [(row, phase) for row, phase in phases if phase is not None]
        for index, (row, phase) in enumerate(phases):
            self.holder.addWidget(self._timeline_row(
                phase, row, stats.get(phase.id), phase.id == current,
                first=index == 0, last=index == len(phases) - 1,
                timing=estimate.phase(phase.id), factor=factor,
                reached=milestones.get(phase.id, ())))

        outside = [p for p in self.ctx.curriculum.phases
                   if p.id not in in_plan and not p.no_progress]
        for phase in outside:
            self.extras.addWidget(self._compact_card(phase, stats.get(phase.id)))
        self.outside.set_count(len(outside))
        self.outside.setVisible(bool(outside))

    # -- rows --------------------------------------------------------------

    def _timeline_row(self, phase, row, stats, is_current: bool,
                      first: bool, last: bool, timing=None, factor=1.0,
                      reached=()) -> QWidget:
        holder = QWidget()
        holder.setObjectName("TimelineRow")
        line = QHBoxLayout(holder)
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(6)

        # Done means proven - the gate, the quiz, the exercises and a
        # project - not every box ticked.
        state = (CURRENT if is_current
                 else DONE if stats and stats.is_proven else AHEAD)
        line.addWidget(Rail(self.ctx.palette, state, phase.num, first, last))

        body = QVBoxLayout()
        body.setContentsMargins(0, 4, 0, 26)
        body.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(8)
        title = label(phase.name, "TimelineTitle")
        top.addWidget(title, 1)
        if is_current:
            top.addWidget(pill("YOU ARE HERE", "accent"))
        elif stats and stats.is_proven:
            top.addWidget(pill("DONE", "done"))
        elif stats and stats.is_read:
            top.addWidget(pill("READ, NOT PROVEN", "warn"))
        elif not row.unlocked:
            top.addWidget(pill("EARLY", "warn"))
        top.addWidget(pill(ROLE_TEXT.get(row.role, ""),
                           ROLE_TONE.get(row.role, "")))
        open_button = button("Open", "primary" if is_current else "")
        open_button.clicked.connect(
            lambda _=False, pid=phase.id: self.ctx.navigate.emit("phase", pid))
        top.addSpacing(4)
        top.addWidget(open_button)
        body.addLayout(top)

        body.addWidget(label(phase.aim, "Soft"))
        body.addWidget(muted(self._when_line(phase, stats, timing, factor)
                             + " - " + row.reason))

        percent = stats.percent if stats else 0
        progress = QHBoxLayout()
        progress.setSpacing(12)
        bar = meter(percent, tone="done" if percent >= 100 else "")
        bar.setMaximumWidth(260)
        progress.addWidget(bar)
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
            if stats.proof():
                bits.append("proven %d%%" % stats.proof_percent)
            progress.addWidget(label("  -  ".join(bits), "Muted", wrap=False))
        progress.addStretch(1)
        body.addLayout(progress)
        left = _left_line(stats)
        if left:
            body.addWidget(muted(left))
        if reached:
            body.addWidget(pill("PROVE THIS TO REACH %s"
                                % " AND ".join(n.upper() for n in reached),
                                "done"))

        if not row.unlocked and not row.reason.startswith("Builds on"):
            names = [self.ctx.curriculum.phase(p).name
                     for p in phase.prereq
                     if self.ctx.curriculum.phase(p) is not None]
            body.addWidget(muted("Usually taken after: " + ", ".join(names)))
        line.addLayout(body, 1)
        return holder

    @staticmethod
    def _when_line(phase, stats, timing, factor) -> str:
        """Hours and dates for one phase, from the estimate, not the fixed
        week numbers the curriculum was written with."""
        if stats and stats.is_proven:
            return "Proven"
        if timing is None or timing.total_minutes <= 0:
            return phase.when or "Ongoing"
        total = timing.total_minutes * factor
        if timing.left_minutes <= 0:
            return "Work done, %s" % format_hours(total)
        if timing.left_minutes >= timing.total_minutes - 1:
            text = "About %s" % format_hours(total)
        else:
            text = "%s left of %s" % (format_hours(timing.left_personal),
                                      format_hours(total))
        if timing.start and timing.finish:
            text += ", %s to %s" % (format_day(timing.start),
                                    format_day(timing.finish))
        return text

    def _compact_card(self, phase, stats) -> Card:
        card = Card(padding=11, spacing=5)
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(pill(phase.num))
        title = label(phase.name, "RowTitle", wrap=False)
        row.addWidget(title, 1)
        if stats and stats.is_started:
            row.addWidget(muted("%d%%" % stats.percent))
        elif phase.est_hours:
            row.addWidget(muted("about %d h" % phase.est_hours))
        open_button = button("Open", "quiet")
        open_button.clicked.connect(
            lambda _=False, pid=phase.id: self.ctx.navigate.emit("phase", pid))
        row.addWidget(open_button)
        card.box.addLayout(row)
        card.add(muted(phase.aim))
        return card


def _left_line(stats) -> str:
    """What still stands between a phase and proven, by kind."""
    if stats is None or stats.is_proven or not stats.total:
        return ""
    steps = (stats.total - stats.gate_total) - (stats.done - stats.gate_done)
    parts = []
    if steps > 0:
        parts.append("%d study step%s" % (steps, "" if steps == 1 else "s"))
    gate = stats.gate_total - stats.gate_done
    if gate > 0:
        parts.append("%d gate check%s" % (gate, "" if gate == 1 else "s"))
    exercises = stats.exercises_total - stats.exercises_done
    if exercises > 0:
        parts.append("%d exercise%s" % (exercises,
                                        "" if exercises == 1 else "s"))
    if stats.quizzes_total and stats.quiz_best < QUIZ_PROOF:
        parts.append("the quiz at %d%%" % round(QUIZ_PROOF * 100))
    projects = stats.core_projects_total - stats.core_projects_shipped
    if projects > 0:
        parts.append("%d project%s" % (projects, "" if projects == 1 else "s"))
    return ("Left: " + ", ".join(parts) + ".") if parts else ""

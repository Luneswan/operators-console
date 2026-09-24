"""Time left: new material still to do at this learner's measured pace, when
it is done, and what the running session has produced so far."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout

from ...core.estimate import format_day, format_hours
from .common import Card, label, meter, muted


def basis_text(estimate) -> str:
    """The inputs behind the date, in one sentence."""
    if estimate.basis == "recent":
        week = ("what you studied in the last four weeks: %.1f h a week"
                % estimate.recent_week_hours)
    else:
        week = "your plan: %s = %s a week (change it in Settings > Pace)" % (
            _plan_sum(estimate), _hours(estimate.plan_week_hours))
    text = "Based on %s" % week
    if estimate.review_week_hours >= 0.1:
        text += ", less about %.1f h of review cards" % (
            estimate.review_week_hours)
    text += ". Pace: %s." % estimate.pace.describe()
    return text


def _hours(value: float) -> str:
    return ("%g h" % round(value, 1))


def _plan_sum(estimate) -> str:
    days = estimate.plan_days
    return "%s a day × %d day%s a week" % (
        _hours(estimate.plan_day_hours), days, "" if days == 1 else "s")


def other_date_text(estimate) -> str:
    """The date at the other rate, when both are known and they differ."""
    if not (estimate.finish_plan and estimate.finish_recent):
        return ""
    if estimate.finish_plan == estimate.finish_recent:
        return ""
    return "At your plan (%s): %s." % (
        _plan_sum(estimate), format_day(estimate.finish_plan))


def session_text(ctx) -> str:
    """What the running session has produced so far, or ''."""
    window = ctx.timer.window()
    if window is None:
        return ""
    started, now, seconds = window
    work = ctx.estimator.work(started, now, seconds)
    done = work.lines()
    if not done:
        return ("This session: nothing marked done yet. Tick lines, pass "
                "exercises or take a quiz and it counts here.")
    return "This session: %s - about %s of estimated work." % (
        ", ".join(done), format_hours(work.credited_minutes))


class TimeLeftCard(Card):
    def __init__(self, parent=None) -> None:
        super().__init__(padding=14, spacing=6, parent=parent)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(muted("TIME LEFT"))
        self.left = label("", "RowTitle", wrap=False)
        self.left.setAccessibleName("New material left")
        top.addWidget(self.left)
        self.left_note = label("", "Soft")
        top.addWidget(self.left_note, 1)
        self.finish = label("", "RowTitle", wrap=False)
        self.finish.setAccessibleName("Estimated finish")
        top.addWidget(self.finish)
        self.box.addLayout(top)
        self.bar = meter(0, 1000, "done")
        self.box.addWidget(self.bar)
        self.basis = muted("")
        self.box.addWidget(self.basis)
        self.other = muted("")
        self.box.addWidget(self.other)
        self.current = label("", "Soft")
        self.box.addWidget(self.current)
        self.session = label("", "Soft")
        self.box.addWidget(self.session)
        self.hint = muted(
            "Press Start studying (Ctrl+T) when you sit down and Stop when "
            "you finish. The app reads what you marked done in between and "
            "corrects the estimate to your real pace.")
        self.box.addWidget(self.hint)

    def show_estimate(self, ctx) -> None:
        estimate = ctx.estimator.estimate()
        if estimate.left_minutes <= 0:
            self.left.setText("Nothing left")
            self.left_note.setText("in your plan. Keep your reviews up.")
            self.finish.setText("")
        else:
            self.left.setText(format_hours(estimate.left_personal))
            self.left_note.setText(
                "of new material at your pace (%s at the course estimate)"
                % format_hours(estimate.left_minutes))
            self.finish.setText("Done around %s" % format_day(estimate.finish))
        self.bar.setValue(round(estimate.done_fraction * 1000))
        self.bar.setToolTip("%d%% of the plan's estimated work is done"
                            % round(estimate.done_fraction * 100))
        self.basis.setText(basis_text(estimate))
        other = other_date_text(estimate)
        self.other.setText(other)
        self.other.setVisible(bool(other))

        phase_id = ctx.progress.current_phase_id()
        phase = ctx.curriculum.phase(phase_id)
        row = estimate.phase(phase_id)
        if phase is not None and row is not None and row.left_minutes > 0:
            self.current.setText(
                "Phase %s, %s: %s left of %s, done around %s." % (
                    phase.num, phase.name, format_hours(row.left_personal),
                    format_hours(row.total_minutes * estimate.pace.factor),
                    format_day(row.finish)))
            self.current.setVisible(True)
        else:
            self.current.setVisible(False)

        text = session_text(ctx)
        self.session.setText(text)
        self.session.setVisible(bool(text))
        self.hint.setVisible(not estimate.pace.measured and not text)

"""Stopping the study timer: what the session produced, the time to record,
and the estimate before and after. Saving writes a log entry and a session
row; the pace and the finish date are recomputed from them."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QLineEdit, QMessageBox, QSpinBox,
    QVBoxLayout,
)

from ..core.estimate import SESSION_CREDIT_CAP, format_day, format_hours
from ..core.session import LONG_SECONDS, MIN_SECONDS, clock_text
from .widgets.common import button, label, muted


def local_day(started_iso: str) -> str:
    """The learner's calendar day the session started on."""
    try:
        return datetime.fromisoformat(started_iso).astimezone().date(
            ).isoformat()
    except ValueError:
        return datetime.now().date().isoformat()


def record_session(ctx, started: str, ended: str, seconds: int,
                   focus: str, next_up: str = "") -> int:
    """Save a finished session as a log entry plus a session row."""
    work = ctx.estimator.work(started, ended, seconds)
    day = local_day(started)
    built = "; ".join(work.lines())
    log_id = ctx.store.add_log(day, focus.strip() or "Study session",
                               round(seconds / 3600.0, 2), built, "",
                               next_up.strip())
    session_id = ctx.store.add_session(started, ended, seconds, focus.strip(),
                                       log_id, day)
    ctx.timer.discard()
    return session_id


class SessionDialog(QDialog):
    """Opened by Stop. Save, discard, or keep the timer running."""

    KEEP = 2

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("Save this study session")
        self.setMinimumWidth(540)
        state = ctx.timer.state()
        self.started, self.ended, self.seconds = ctx.timer.window()
        self.work = ctx.estimator.work(self.started, self.ended, self.seconds)

        column = QVBoxLayout(self)
        column.setContentsMargins(24, 20, 24, 18)
        column.setSpacing(10)
        column.addWidget(label("Session: %s" % clock_text(self.seconds),
                               "PageTitle"))

        lines = self.work.lines()
        if lines:
            column.addWidget(label("You finished: %s." % ", ".join(lines),
                                   "Soft"))
            spent = self.work.new_minutes
            credited = self.work.credited_minutes
            text = "About %s of estimated work" % format_hours(credited)
            if spent >= 5 and credited > spent * SESSION_CREDIT_CAP:
                text += (" in %s. Some of it was probably done before the "
                         "timer started, so your pace counts at most %d "
                         "times the session's length" % (
                             format_hours(spent), SESSION_CREDIT_CAP))
            elif spent >= 5 and credited > 0:
                ratio = spent / credited
                if ratio < 0.95:
                    text += ", done in %s: faster than the estimate" % (
                        format_hours(spent))
                elif ratio > 1.05:
                    text += ", done in %s: slower than the estimate" % (
                        format_hours(spent))
                else:
                    text += ", done in %s: on the estimate" % (
                        format_hours(spent))
            column.addWidget(muted(text + "."))
        else:
            column.addWidget(label(
                "Nothing was marked done in this session.", "Soft"))
            column.addWidget(muted(
                "The time still counts toward your study hours. Reading "
                "shows up in the estimate once you tick what you read."))

        estimate = ctx.estimator.estimate()
        before = state.left_minutes if state else 0.0
        after = estimate.left_personal
        if before > 0 and estimate.left_minutes > 0:
            column.addWidget(muted(
                "New material left: %s when you started, %s now. Done "
                "around %s." % (format_hours(before), format_hours(after),
                                format_day(estimate.finish))))

        self.long_note = muted(
            "The timer ran %s. If you stopped studying earlier, set the "
            "minutes you actually studied." % clock_text(self.seconds))
        self.long_note.setVisible(self.seconds > LONG_SECONDS)
        column.addWidget(self.long_note)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self.minutes = QSpinBox()
        self.minutes.setRange(1, 24 * 60)
        self.minutes.setSuffix(" min")
        self.minutes.setValue(max(1, round(self.seconds / 60)))
        self.minutes.setAccessibleName("Minutes to record")
        grid.addWidget(muted("TIME"), 0, 0)
        grid.addWidget(self.minutes, 0, 1)
        self.focus = QLineEdit(state.focus if state else "")
        self.focus.setPlaceholderText("What you worked on")
        self.focus.setAccessibleName("What you worked on")
        grid.addWidget(muted("ON"), 1, 0)
        grid.addWidget(self.focus, 1, 1)
        self.next_up = QLineEdit()
        self.next_up.setPlaceholderText(
            "Where to start next time (shown on Today)")
        self.next_up.setAccessibleName("Where to start next time")
        grid.addWidget(muted("NEXT"), 2, 0)
        grid.addWidget(self.next_up, 2, 1)
        grid.setColumnStretch(1, 1)
        column.addLayout(grid)

        row = QHBoxLayout()
        row.setSpacing(8)
        discard = button("Discard", "quiet", "Throw this session away")
        discard.clicked.connect(self._discard)
        row.addWidget(discard)
        row.addStretch(1)
        keep = button("Keep going", "quiet", "Close this and keep timing")
        keep.clicked.connect(lambda: self.done(self.KEEP))
        row.addWidget(keep)
        self.save_button = button("Save to log", "primary")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._save)
        row.addWidget(self.save_button)
        column.addLayout(row)

    def _save(self) -> None:
        seconds = self.minutes.value() * 60
        record_session(self.ctx, self.started, self.ended, seconds,
                       self.focus.text(), self.next_up.text())
        self.accept()

    def _discard(self) -> None:
        if self.seconds >= 10 * 60:
            answer = QMessageBox.question(
                self, "Discard session?",
                "Throw away %s of study time? It will not be logged."
                % clock_text(self.seconds))
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.ctx.timer.discard()
        self.reject()


def too_short(ctx) -> bool:
    window = ctx.timer.window()
    return window is not None and window[2] < MIN_SECONDS

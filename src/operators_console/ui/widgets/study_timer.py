"""The study timer in the top bar: Start studying, then the clock, Pause and
Stop. It is on every page, so a session keeps counting while the learner
moves between a phase, Practice and Review."""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ...core.session import clock_text
from .common import button, mono_label, pill


class StudyTimerBar(QWidget):
    def __init__(self, ctx, on_start, on_stop, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        self.start_button = button(
            "Start studying", "",
            "Time this session (Ctrl+T). What you finish while it runs sets "
            "your pace and the time-left estimate.")
        self.start_button.clicked.connect(on_start)
        row.addWidget(self.start_button)
        self.state_pill = pill("STUDYING", "accent")
        row.addWidget(self.state_pill)
        self.clock = mono_label("0:00:00")
        self.clock.setAccessibleName("Study time this session")
        row.addWidget(self.clock)
        self.pause_button = button("Pause", "quiet",
                                   "Pause or resume the timer (Ctrl+Shift+T)")
        self.pause_button.clicked.connect(self.toggle_pause)
        row.addWidget(self.pause_button)
        self.stop_button = button("Stop", "quiet",
                                  "Stop and save the session (Ctrl+T)")
        self.stop_button.clicked.connect(on_stop)
        row.addWidget(self.stop_button)
        # One label changes once a second; nothing else is touched.
        self.ticker = QTimer(self)
        self.ticker.setInterval(1000)
        self.ticker.timeout.connect(self._tick)
        self.sync()

    def toggle_pause(self) -> None:
        timer = self.ctx.timer
        state = timer.state()
        if state is None:
            return
        if state.paused:
            timer.resume()
        else:
            timer.pause()
        self.sync()

    def sync(self) -> None:
        """Show the controls for the timer's state, as the store has it."""
        state = self.ctx.timer.state()
        active = state is not None
        self.start_button.setVisible(not active)
        for widget in (self.state_pill, self.clock, self.pause_button,
                       self.stop_button):
            widget.setVisible(active)
        if not active:
            self.ticker.stop()
            return
        if state.paused:
            self.state_pill.setText("PAUSED")
            self.state_pill.setProperty("tone", "warn")
            self.pause_button.setText("Resume")
            self.ticker.stop()
        else:
            self.state_pill.setText("STUDYING")
            self.state_pill.setProperty("tone", "accent")
            self.pause_button.setText("Pause")
            self.ticker.start()
        style = self.state_pill.style()
        style.unpolish(self.state_pill)
        style.polish(self.state_pill)
        self._tick()

    def _tick(self) -> None:
        self.clock.setText(clock_text(self.ctx.timer.elapsed()))

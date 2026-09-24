"""The study timer: start, pause, resume, stop.

The running timer lives in the store's settings, so closing the app does not
lose it; reopening shows the same session still counting (or paused). When
it stops, the caller saves the session with Store.add_session and a log
entry, and the work done in it is read back from the store's timestamps.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

SETTING = "study_timer"
MIN_SECONDS = 60             # shorter than this is a misclick, not a session
LONG_SECONDS = 6 * 3600      # longer than this was probably left running


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds")


def _parse(text):
    try:
        moment = datetime.fromisoformat(str(text))
    except (TypeError, ValueError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def clock_text(seconds: int) -> str:
    seconds = max(0, int(seconds))
    return "%d:%02d:%02d" % (seconds // 3600, seconds // 60 % 60, seconds % 60)


@dataclass(frozen=True, slots=True)
class TimerState:
    started: datetime
    paused_at: datetime | None
    paused_seconds: int
    left_minutes: float          # the estimate when the session started
    focus: str

    @property
    def paused(self) -> bool:
        return self.paused_at is not None

    def elapsed(self, now: datetime) -> int:
        end = self.paused_at or now
        return max(0, int((end - self.started).total_seconds())
                   - self.paused_seconds)


class StudyTimer:
    def __init__(self, store, clock=utc_now) -> None:
        self.s = store
        self.clock = clock

    def state(self) -> TimerState | None:
        raw = self.s.setting(SETTING, None)
        if not isinstance(raw, dict):
            return None
        started = _parse(raw.get("started"))
        if started is None:
            return None
        paused_at = _parse(raw.get("paused_at")) if raw.get("paused_at") \
            else None
        try:
            paused_seconds = max(0, int(raw.get("paused_seconds", 0) or 0))
            left = float(raw.get("left_minutes", 0) or 0)
        except (TypeError, ValueError):
            paused_seconds, left = 0, 0.0
        return TimerState(started=started, paused_at=paused_at,
                          paused_seconds=paused_seconds, left_minutes=left,
                          focus=str(raw.get("focus", "") or ""))

    @property
    def running(self) -> bool:
        state = self.state()
        return state is not None and not state.paused

    @property
    def active(self) -> bool:
        return self.state() is not None

    def elapsed(self) -> int:
        state = self.state()
        return state.elapsed(self.clock()) if state else 0

    def _save(self, state: TimerState) -> None:
        self.s.set_setting(SETTING, {
            "started": iso(state.started),
            "paused_at": iso(state.paused_at) if state.paused_at else None,
            "paused_seconds": state.paused_seconds,
            "left_minutes": round(state.left_minutes, 2),
            "focus": state.focus,
        })

    def start(self, focus: str = "", left_minutes: float = 0.0) -> TimerState:
        existing = self.state()
        if existing is not None:
            return existing
        state = TimerState(started=self.clock(), paused_at=None,
                           paused_seconds=0, left_minutes=left_minutes,
                           focus=focus)
        self._save(state)
        return state

    def pause(self) -> None:
        state = self.state()
        if state is None or state.paused:
            return
        self._save(TimerState(state.started, self.clock(),
                              state.paused_seconds, state.left_minutes,
                              state.focus))

    def resume(self) -> None:
        state = self.state()
        if state is None or not state.paused:
            return
        gap = max(0, int((self.clock() - state.paused_at).total_seconds()))
        self._save(TimerState(state.started, None,
                              state.paused_seconds + gap, state.left_minutes,
                              state.focus))

    def discard(self) -> None:
        self.s.set_setting(SETTING, None)

    def window(self) -> tuple:
        """(started, now, active seconds) as the session stands."""
        state = self.state()
        if state is None:
            return None
        now = self.clock()
        return iso(state.started), iso(state.paused_at or now), \
            state.elapsed(now)

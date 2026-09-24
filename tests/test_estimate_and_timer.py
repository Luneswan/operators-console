"""Time left, the measured pace, and the study timer.

Owner, 09-24: "estimates depending on what you learn, time and day should be
accurate ... start a timer in app and stop it when done, and then it will see
what you ticked or finished in that period and re-estimate continuously and
show how much new is left".
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from conftest import pump

from operators_console.core.estimate import (
    PRIOR_MINUTES, SESSION_CREDIT_CAP, Estimator, finish_date, format_hours,
)
from operators_console.core.progress import Progress
from operators_console.core.session import StudyTimer, iso


def _estimator(curriculum, store, today=date.today):
    return Estimator(curriculum, store, Progress(curriculum, store), today)


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 9, 24, 9, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, **kw) -> None:
        self.now += timedelta(**kw)


# -- the unit estimate --------------------------------------------------------

def test_every_phase_splits_into_exactly_its_hours(curriculum, store):
    units = _estimator(curriculum, store).units()
    estimator = _estimator(curriculum, store)
    for phase in curriculum.phases:
        if phase.no_progress or phase.est_hours <= 0:
            continue
        total, left = estimator.phase_minutes(phase)
        assert round(total, 3) == phase.est_hours * 60, phase.id
        assert round(left, 3) == round(total, 3), phase.id
    assert units


def test_harder_exercises_are_worth_more_minutes(curriculum, store):
    units = _estimator(curriculum, store).units()
    exercises = curriculum.exercises_for("p01")
    easy = min(exercises, key=lambda e: e.difficulty)
    hard = max(exercises, key=lambda e: e.difficulty)
    assert hard.difficulty > easy.difficulty
    assert units[hard.id] > units[easy.id]


def test_ticking_a_line_takes_its_minutes_off_what_is_left(curriculum, store):
    estimator = _estimator(curriculum, store)
    before = estimator.estimate().left_minutes
    item = curriculum.phase("p01").core_items[0]
    store.set_checked(item.id, True)
    after = estimator.estimate().left_minutes
    assert round(before - after, 6) == round(estimator.units()[item.id], 6)


def test_stretch_lines_are_credited_but_never_left(curriculum, store):
    estimator = _estimator(curriculum, store)
    stretch = [i for p in curriculum.phases for s in p.sections if s.optional
               for i in s.items]
    assert stretch
    before = estimator.estimate().left_minutes
    store.set_checked(stretch[0].id, True)
    assert estimator.estimate().left_minutes == before
    assert estimator.units()[stretch[0].id] > 0


# -- the measured pace ----------------------------------------------------------

def _session(store, minutes, tick):
    start = iso(datetime.now(timezone.utc) - timedelta(seconds=2))
    for item_id in tick:
        store.set_checked(item_id, True)
    end = iso(datetime.now(timezone.utc) + timedelta(seconds=2))
    store.add_session(start, end, minutes * 60)


def test_no_sessions_means_the_course_estimate(curriculum, store):
    pace = _estimator(curriculum, store).pace()
    assert pace.factor == 1.0
    assert not pace.measured


def test_a_slow_session_slows_the_pace_but_not_all_the_way(curriculum, store):
    estimator = _estimator(curriculum, store)
    item = curriculum.phase("p01").core_items[0]
    unit = estimator.units()[item.id]
    _session(store, round(unit * 2), [item.id])        # took twice as long
    pace = estimator.pace()
    assert pace.measured
    assert 1.0 < pace.factor < 2.0
    expected = (round(unit * 2) + PRIOR_MINUTES) / (unit + PRIOR_MINUTES)
    assert round(pace.factor, 6) == round(expected, 6)


def test_ticking_old_work_is_capped_at_a_few_times_the_session(curriculum,
                                                               store):
    estimator = _estimator(curriculum, store)
    items = [i.id for i in curriculum.phase("p01").core_items]
    _session(store, 10, items)                  # 10 minutes, a whole phase
    pace = estimator.pace()
    assert pace.credited_minutes == 10 * SESSION_CREDIT_CAP
    assert pace.factor > 0.9


def test_review_time_is_not_new_material(curriculum, store):
    estimator = _estimator(curriculum, store)
    start = iso(datetime.now(timezone.utc) - timedelta(seconds=2))
    for _ in range(6):
        store.log_review("some-card", 3, True)
    end = iso(datetime.now(timezone.utc) + timedelta(seconds=2))
    work = estimator.work(start, end, 600)
    assert work.reviews == 6
    assert work.new_minutes == 8.0          # 10 min less 6 x 20 s


# -- the finish date --------------------------------------------------------------

def test_the_finish_date_is_what_is_left_over_hours_a_week():
    start = date(2026, 9, 24)
    assert finish_date(15 * 60, 15.0, start) == start + timedelta(days=7)
    assert finish_date(0, 15.0, start) is None


def test_the_plan_sets_the_rate_until_there_is_history(curriculum, store):
    store.set_setting("hours_per_day", 2.0)
    store.set_setting("days_per_week", 5)
    estimate = _estimator(curriculum, store).estimate()
    assert estimate.basis == "plan"
    assert estimate.plan_week_hours == 10.0
    days = (estimate.finish - date.today()).days
    weeks = estimate.left_personal / 60 / estimate.new_week_hours
    assert abs(days - weeks * 7) <= 1


def test_four_weeks_of_real_study_set_the_rate(curriculum, store):
    today = date(2026, 9, 24)
    for back in range(28):                      # 28 days of 30 min: 14 h
        store.bump_activity(minutes=30,
                            day=(today - timedelta(days=back)).isoformat())
    estimate = _estimator(curriculum, store, lambda: today).estimate()
    assert estimate.basis == "recent"
    assert round(estimate.recent_week_hours, 2) == 3.5
    assert estimate.finish == estimate.finish_recent
    assert estimate.finish_plan is not None


def test_format_hours():
    assert format_hours(45) == "45 min"
    assert format_hours(90) == "1.5 h"
    assert format_hours(125 * 60) == "125 h"


# -- the timer ---------------------------------------------------------------------

def test_the_timer_counts_pauses_out_and_survives_a_restart(store):
    clock = Clock()
    timer = StudyTimer(store, clock)
    timer.start(focus="Phase 01")
    clock.advance(minutes=20)
    timer.pause()
    clock.advance(minutes=30)
    assert timer.elapsed() == 20 * 60
    timer.resume()
    clock.advance(minutes=10)
    again = StudyTimer(store, clock)            # as if the app reopened
    assert again.running
    assert again.elapsed() == 30 * 60
    assert again.state().focus == "Phase 01"
    again.discard()
    assert not again.active


def test_a_damaged_timer_setting_is_no_timer(store):
    store.set_setting("study_timer", {"started": "yesterday-ish"})
    assert StudyTimer(store).state() is None


def test_saving_a_session_logs_it_and_deleting_the_log_forgets_it(
        qt_app, window, curriculum, store):
    from operators_console.ui.session_dialog import record_session
    ctx = window.ctx
    ctx.timer.start(focus="Phase 01")
    started = ctx.timer.state().started - timedelta(minutes=30)
    store.set_setting("study_timer", dict(
        store.setting("study_timer"), started=iso(started)))
    item = curriculum.phase("p01").core_items[0]
    ctx.set_checked(item.id, True)
    begin, end, seconds = ctx.timer.window()
    assert seconds >= 30 * 60
    record_session(ctx, begin, end, seconds, "Phase 01", "generators")
    assert not ctx.timer.active
    sessions = store.sessions()
    assert len(sessions) == 1
    log = store.logs(limit=1)[0]
    assert "1 study step ticked" in log["built"]
    assert log["next_up"] == "generators"
    assert ctx.estimator.pace().measured
    store.delete_log(log["id"])
    assert store.sessions() == []


def test_a_backup_from_before_sessions_still_restores(store):
    payload = store.dump()
    del payload["tables"]["sessions"]
    store.restore(payload)          # must not call the backup incomplete


# -- the window ----------------------------------------------------------------------

def test_start_and_a_too_short_stop_from_the_window(qt_app, window):
    window.start_study()
    pump(qt_app)
    bar = window.study_bar
    assert window.ctx.timer.running
    assert bar.stop_button.isVisibleTo(window)
    assert not bar.start_button.isVisibleTo(window)
    window.pause_study()
    assert bar.pause_button.text() == "Resume"
    window.stop_study()                  # under a minute: nothing saved
    pump(qt_app)
    assert not window.ctx.timer.active
    assert window.ctx.store.sessions() == []
    assert bar.start_button.isVisibleTo(window)


def test_ctrl_t_is_the_timer_shortcut(qt_app, window):
    keys = [k.toString() for k in window.study_action.shortcuts()]
    assert "Ctrl+T" in keys


def test_today_and_the_roadmap_show_time_left(qt_app, window):
    window.go("today")
    pump(qt_app)
    card = window.views["today"].time_left
    assert card.left.text().endswith("h")
    assert card.finish.text().startswith("Done around")
    window.go("roadmap")
    pump(qt_app)
    view = window.views["roadmap"]
    assert view.left_value.text().endswith("h")
    texts = [w.text() for w in view.findChildren(type(card.left))]
    assert any(t.startswith("Left: ") for t in texts)
    assert any(t.startswith("PROVE THIS TO REACH") for t in texts)


@pytest.mark.parametrize("hours", [1.0, 6.0])
def test_more_hours_a_day_means_an_earlier_finish(curriculum, store, hours):
    store.set_setting("hours_per_day", hours)
    estimate = _estimator(curriculum, store).estimate()
    week = hours * 5
    days = (estimate.finish - date.today()).days
    assert abs(days - estimate.left_personal / 60 / week * 7) <= 1

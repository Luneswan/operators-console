"""First run: the wizard, every answer it can take, then Today."""
from __future__ import annotations

import itertools

import pytest

from .harness import REC, click, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _wizard(window):
    from operators_console.ui.onboarding import Onboarding
    return Onboarding(window.ctx, window)


def test_the_wizard_opens_on_a_store_that_has_never_been_used(
        walk_app, raw_window, store):
    assert store.setting("onboarded", False) is False
    with step(walk_app, "onboarding", "open the wizard on first run",
              raw_window):
        wizard = _wizard(raw_window)
        assert wizard.step == 0
        assert wizard.kicker.text() == "STEP 1 OF 4"
        assert not wizard.back_button.isEnabled()
    wizard.reject()


def test_walking_forward_and_back_through_every_step(walk_app, raw_window):
    wizard = _wizard(raw_window)
    for index in range(3):
        with step(walk_app, "onboarding", "continue from step %d" % (index + 1),
                  raw_window):
            click(walk_app, wizard.next_button)
            assert wizard.step == index + 1
            assert wizard.stack.currentIndex() == index + 1
    assert wizard.next_button.text() == "Build my plan"
    for index in range(3, 0, -1):
        with step(walk_app, "onboarding", "back from step %d" % (index + 1),
                  raw_window):
            click(walk_app, wizard.back_button)
            assert wizard.step == index - 1
    wizard.reject()


def test_every_experience_level_can_be_chosen(walk_app, raw_window, store):
    from operators_console.core.adaptive import EXPERIENCE_LEVELS
    for value, text in EXPERIENCE_LEVELS:
        wizard = _wizard(raw_window)
        with step(walk_app, "onboarding", "experience: %s" % text, raw_window):
            for option in wizard.experience_buttons:
                if option.property("value") == value:
                    click(walk_app, option)
            wizard._finish()
            assert store.setting("experience") == value
        wizard.deleteLater()
    REC.bump("onboarding experience levels", len(EXPERIENCE_LEVELS))


def _goal_patterns(count: int) -> list:
    """None, all, every single goal, every pair, and 512 seeded random
    patterns. With 21 goals the full 2**21 is two million previews."""
    import random
    patterns = {(False,) * count, (True,) * count}
    for i in range(count):
        patterns.add(tuple(k == i for k in range(count)))
    for i, j in itertools.combinations(range(count), 2):
        patterns.add(tuple(k in (i, j) for k in range(count)))
    rng = random.Random(20260924)
    while len(patterns) < 2 + count + count * (count - 1) // 2 + 512:
        patterns.add(tuple(rng.random() < 0.5 for _ in range(count)))
    return sorted(patterns)


def test_goal_combinations_the_dialog_can_express(walk_app, raw_window):
    """Singles, pairs, none, all and a seeded sample, each previewed the way
    the learner sees it."""
    from operators_console.core.adaptive import GOALS

    wizard = _wizard(raw_window)
    wizard.step = 2
    wizard._render()
    ids = [gid for gid, _text, _tags in GOALS]
    patterns = _goal_patterns(len(ids))
    tracks = set()
    with step(walk_app, "onboarding",
              "tick %d goal combinations" % len(patterns), raw_window):
        for pattern in patterns:
            for gid, wanted in zip(ids, pattern, strict=True):
                box = wizard.goal_boxes[gid]
                if box.isChecked() != wanted:
                    box.setChecked(wanted)
            chosen = {gid for gid, on in zip(ids, pattern, strict=True) if on}
            suggested = wizard.ctx.planner.suggested_track(chosen)
            assert wizard.ctx.curriculum.track(suggested) is not None, chosen
            tracks.add(suggested)
            assert wizard.track_preview_label.text()
    REC.bump("goal combinations previewed", len(patterns))
    REC.bump("distinct tracks reachable from goals", len(tracks))
    wizard.reject()


def test_every_goal_on_its_own_builds_a_plan(walk_app, raw_window, store):
    from operators_console.core.adaptive import GOALS
    for gid, text, _tags in GOALS:
        store.set_setting("goals", [])      # the wizard prefills from here
        wizard = _wizard(raw_window)
        with step(walk_app, "onboarding", "finish with goal: %s" % text,
                  raw_window):
            wizard.name.setText("Walker")
            wizard.goal_boxes[gid].setChecked(True)
            wizard.hours.setValue(3.5)
            wizard.days.setValue(6)
            wizard._finish()
            assert store.setting("onboarded") is True
            assert store.setting("goals") == [gid]
            assert store.setting("hours_per_day") == 3.5
            assert store.setting("days_per_week") == 6
            assert wizard.ctx.curriculum.track(store.setting("track"))
        wizard.deleteLater()


def test_the_pace_extremes_are_accepted(walk_app, raw_window, store):
    for hours, days in ((0.5, 1), (16.0, 7)):
        wizard = _wizard(raw_window)
        with step(walk_app, "onboarding", "pace %s h x %s days" % (hours, days),
                  raw_window):
            wizard.hours.setValue(hours)
            wizard.days.setValue(days)
            assert wizard.pace_preview.text()
            wizard._finish()
            assert store.setting("hours_per_day") == hours
        wizard.deleteLater()


def test_skipping_leaves_a_usable_app(walk_app, raw_window, store):
    wizard = _wizard(raw_window)
    with step(walk_app, "onboarding", "skip the wizard", raw_window):
        click(walk_app, wizard.skip_button)
        assert store.setting("onboarded") is True
    with step(walk_app, "today", "land on Today after skipping", raw_window):
        raw_window.go("today", "")
        pump(walk_app)
        assert raw_window.stack.currentWidget() is raw_window.views["today"]
        assert raw_window.views["today"].greeting.text()


def test_today_shows_a_plan_and_every_start_button_navigates(
        walk_app, window, store, curriculum):
    from PySide6.QtWidgets import QPushButton

    phase = curriculum.phase("p01")
    store.set_many_checked([i.id for i in phase.items][:4], True)
    window.go("today", "")
    pump(walk_app)
    view = window.views["today"]

    with step(walk_app, "today", "read the four headline tiles", window):
        assert view.tile_percent.value_label.text().endswith("%")
        assert view.tile_streak.value_label.text().isdigit()
        assert view.tile_due.value_label.text().isdigit()
        assert view.overall_caption.text()

    def plan_starts():
        out = []
        for index in range(view.plan_holder.count()):
            card = view.plan_holder.itemAt(index).widget()
            if card is None:
                continue
            out += [b for b in card.findChildren(QPushButton)
                    if b.text() == "Start"]
        return out

    total = len(plan_starts())
    assert total, "Today offered no actions at all"
    REC.bump("Today plan actions offered", total)
    for index in range(total):
        window.go("today", "")
        pump(walk_app)
        buttons = plan_starts()
        if index >= len(buttons):
            break
        with step(walk_app, "today", "press Start on plan row %d" % (index + 1),
                  window):
            click(walk_app, buttons[index])
            assert window.current_key
    window.go("today", "")
    pump(walk_app)

    with step(walk_app, "today", "open the current phase from Where you are",
              window):
        opens = [b for b in view.position_card.findChildren(QPushButton)
                 if b.text() == "Open this phase"]
        assert opens
        click(walk_app, opens[0])
        assert window.current_key == "phase"

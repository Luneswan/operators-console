"""A study session from start to saved, and the guides on a phase page.

Owner, 09-24: start a timer, stop it when done, see what was finished in
between and how much is left; and phases fleshed out with how to do each
line and where to learn it. Every control added for that is pressed here:
the timer's buttons, its menu actions and shortcuts, the three buttons of
the session dialog, How, Show all guides and the guide's links. The report
form and the profile controls from 1.2.0 are pressed too.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from .harness import REC, click, pump, shortcut, step, trigger

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def _backdate(ctx, minutes: int) -> None:
    """Move the running timer's start back, as if studied that long."""
    from operators_console.core.session import iso
    state = ctx.timer.state()
    raw = dict(ctx.store.setting("study_timer"))
    raw["started"] = iso(state.started - timedelta(minutes=minutes))
    ctx.store.set_setting("study_timer", raw)


def test_a_timed_session_is_saved_with_what_it_produced(walk_app, window,
                                                        store, curriculum):
    from operators_console.ui.session_dialog import SessionDialog
    ctx = window.ctx
    bar = window.study_bar
    with step(walk_app, "study", "start the timer from the top bar", window):
        click(walk_app, bar.start_button)
        assert ctx.timer.running
    with step(walk_app, "study", "pause and resume", window):
        click(walk_app, bar.pause_button)
        assert not ctx.timer.running
        click(walk_app, bar.pause_button)
        assert ctx.timer.running
    with step(walk_app, "study", "pause and resume by shortcut", window):
        shortcut(walk_app, window, "Ctrl+Shift+T")
        assert not ctx.timer.running
        shortcut(walk_app, window, "Ctrl+Shift+T")
        assert ctx.timer.running
    _backdate(ctx, 40)
    item = curriculum.phase("p01").core_items[0]
    ctx.set_checked(item.id, True)
    with step(walk_app, "study", "Today shows the session so far", window):
        window.go("today")
        pump(walk_app, 2)
        assert "study step ticked" in window.views["today"].time_left \
            .session.text()
    with step(walk_app, "study", "Keep going leaves the timer running",
              window):
        dialog = SessionDialog(ctx, window)
        click(walk_app, _named(dialog, "Keep going"))
        assert ctx.timer.running
        dialog.deleteLater()
    with step(walk_app, "study", "save the session to the log", window):
        dialog = SessionDialog(ctx, window)
        dialog.next_up.setText("generators")
        click(walk_app, _named(dialog, "Save to log"))
        dialog.deleteLater()
        assert not ctx.timer.active
        assert len(store.sessions()) == 1
        assert store.logs(limit=1)[0]["next_up"] == "generators"
        assert ctx.estimator.pace().measured
    REC.bump("study sessions saved", 1)


def test_the_study_menu_and_a_discarded_session(walk_app, window, store):
    from operators_console.ui.session_dialog import SessionDialog
    ctx = window.ctx
    with step(walk_app, "study", "start from the Study menu", window):
        trigger(walk_app, window.study_action)
        assert ctx.timer.running
    with step(walk_app, "study", "Ctrl+T under a minute saves nothing",
              window):
        shortcut(walk_app, window, "Ctrl+T")
        assert not ctx.timer.active
        assert store.sessions() == []
    with step(walk_app, "study", "discard a session", window):
        shortcut(walk_app, window, "Ctrl+T")
        _backdate(ctx, 5)
        dialog = SessionDialog(ctx, window)
        click(walk_app, _named(dialog, "Discard"))
        dialog.deleteLater()
        assert not ctx.timer.active
    with step(walk_app, "study", "Stop from the top bar", window):
        click(walk_app, window.study_bar.start_button)
        click(walk_app, window.study_bar.stop_button)
        assert not ctx.timer.active          # under a minute: dropped


def test_every_guide_opens_and_its_links_go_to_the_browser(walk_app, window,
                                                           curriculum):
    from PySide6.QtWidgets import QLabel
    from operators_console.ui.widgets.guide import GuidedItem
    view = window.views["phase"]
    opened = links = 0
    for phase in curriculum.phases:
        if not phase.sections:
            continue
        window.go("phase", phase.id)
        pump(walk_app, 2)
        with step(walk_app, "phase", "open every guide in %s" % phase.num,
                  window):
            for guided in view.scroller.body.findChildren(GuidedItem):
                if not guided.is_open:
                    guided.toggle_link.linkActivated.emit("how")
                assert guided.is_open, guided.item.id
                opened += 1
                where = [w for w in guided.panel.findChildren(QLabel)
                         if "Learn it" in w.text()]
                assert where, "%s has no links" % guided.item.id
                where[0].linkActivated.emit(guided.item.where[0].url)
                links += 1
    before = len(REC.urls)
    assert before >= links                   # every link reached the fake
    with step(walk_app, "phase", "Show all guides, then hide them", window):
        window.go("phase", "p02")
        pump(walk_app, 2)
        click(walk_app, view.guides_button)
        assert all(g.is_open
                   for g in view.scroller.body.findChildren(GuidedItem))
        click(walk_app, view.guides_button)
        assert not any(g.is_open
                       for g in view.scroller.body.findChildren(GuidedItem))
    REC.bump("study guides opened", opened)
    REC.bump("guide links followed", links)


def test_the_report_form_and_the_profile_controls(walk_app, window):
    from operators_console.ui.feedback import FeedbackDialog
    window.go("settings")
    pump(walk_app, 2)
    view = window.views["settings"]
    with step(walk_app, "settings", "the report buttons open the form",
              window):
        for text in ("Report a bug...", "Request a feature...",
                     "Report a course mistake..."):
            click(walk_app, _named(view, text))
    with step(walk_app, "settings", "fill in and send a report", window):
        dialog = FeedbackDialog(window.ctx, window)
        dialog.title.setText("Walk report")
        dialog.details.setPlainText("Filed by the walkthrough.")
        click(walk_app, _named(dialog, "Copy text"))
        click(walk_app, _named(dialog, "Open on GitHub"))
        assert any("issues/new" in url for url in REC.urls)
        dialog = FeedbackDialog(window.ctx, window)
        click(walk_app, _named(dialog, "Cancel"))
    with step(walk_app, "settings", "New profile asks for a name", window):
        click(walk_app, _named(view.profiles_card, "New profile..."))

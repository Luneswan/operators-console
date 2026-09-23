"""A release published while the app is open shows up without a restart.

The manager looked once, 2.5 s after launch, and never again: a learner who
keeps the window open for days saw nothing until they relaunched. Now it
also looks every POLL_MINUTES, announces a release once, and never takes
the keyboard away to do it.
"""
from __future__ import annotations

from PySide6.QtWidgets import QApplication

from conftest import pump, wait_for
from test_updates import ALL_ASSETS, make_release

from operators_console.core import updates
from operators_console.ui import updater


def _armed(monkeypatch, release):
    """The next look at GitHub finds `release`, on this machine, opted in."""
    monkeypatch.setattr(updater, "_release_now", lambda: release)
    monkeypatch.setattr(updates, "can_self_update", lambda: True)


def test_the_manager_keeps_looking_while_the_window_is_open(window):
    timer = window.updates._poll
    assert timer.isActive()
    assert timer.interval() == updater.POLL_MINUTES * 60 * 1000
    # Prompt for us; polite to GitHub because unchanged answers are 304s.
    assert 1 <= updater.POLL_MINUTES <= 5


def test_a_poll_announces_a_new_release_without_taking_focus(
        qt_app, window, store, monkeypatch):
    window.go("practice", "")
    pump(qt_app)
    window.views["practice"].editor.setFocus()
    pump(qt_app)
    _armed(monkeypatch, make_release("v99.0.0", ALL_ASSETS))
    assert not window.update_button.isVisible()
    window.updates.poll()
    assert wait_for(qt_app, lambda: window.update_button.isVisible(), 10)
    assert "99.0.0" in window.update_button.text()
    assert "99.0.0" in window.status_label.text()
    assert QApplication.focusWidget() is not window.update_button


def test_the_same_release_is_announced_once(qt_app, window, store,
                                             monkeypatch):
    seen = []
    window.updates.available.connect(lambda r: seen.append(r.tag))
    _armed(monkeypatch, make_release("v99.0.0", ALL_ASSETS))
    window.updates.poll()
    assert wait_for(qt_app, lambda: seen == ["v99.0.0"], 10)
    window.status_label.setText("")
    window.updates.poll()
    pump(qt_app, 20)
    assert seen == ["v99.0.0"]
    assert window.status_label.text() == ""


def test_a_newer_release_than_the_announced_one_replaces_it(
        qt_app, window, store, monkeypatch):
    _armed(monkeypatch, make_release("v99.0.0", ALL_ASSETS))
    window.updates.poll()
    assert wait_for(qt_app, lambda: "99.0.0" in window.update_button.text(), 10)
    _armed(monkeypatch, make_release("v99.0.1", ALL_ASSETS))
    window.updates.poll()
    assert wait_for(qt_app, lambda: "99.0.1" in window.update_button.text(), 10)


def test_the_poll_respects_the_opt_out(qt_app, window, store, monkeypatch):
    looked = []
    monkeypatch.setattr(updater, "_release_now",
                        lambda: looked.append(1) or None)
    monkeypatch.setattr(updates, "can_self_update", lambda: True)
    store.set_setting("check_for_updates", False)
    window.updates.poll()
    pump(qt_app, 20)
    assert looked == []
    store.set_setting("check_for_updates", True)
    window.updates.poll()
    assert wait_for(qt_app, lambda: looked == [1], 10)


def test_closing_the_window_stops_the_poll(qt_app, window):
    window.close()
    assert not window.updates._poll.isActive()

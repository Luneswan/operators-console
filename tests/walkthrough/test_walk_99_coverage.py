"""The controls the rest of the walk does not reach on its way past.

Runs last, so the coverage table in the report is the whole walk's, not this
file's. Nothing here presses anything that would touch the network or replace
the running program.
"""
from __future__ import annotations

import pytest

from .harness import REC, answering, click, pump, shortcut, step, trigger
from .inventory import coverage, scan

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


def test_the_quiz_picker_start_buttons(walk_app, window, curriculum):
    window.go("quiz", "")
    pump(walk_app, 3)
    view = window.views["quiz"]
    with step(walk_app, "quiz", "start a quiz from the picker", window):
        card = view.stage.itemAt(0).widget()
        start = _named(card, "Start")
        assert start is not None, "the picker has no Start button"
        click(walk_app, start)
        assert view.quiz is not None
    with step(walk_app, "quiz", "leave and start a different one", window):
        view._reset_to_picker()
        pump(walk_app, 2)
        card = view.stage.itemAt(1).widget()
        click(walk_app, _named(card, "Start"))
        assert view.quiz is not None
    REC.bump("quizzes started from the picker", 2)


def test_review_check_for_more(walk_app, window, store, curriculum):
    from operators_console.core.srs import Rating
    for phase in curriculum.phases[:2]:
        ids = [i.id for i in phase.items][:2]
        if ids:
            store.set_many_checked(ids, True)
    store.set_setting("new_cards_per_day", 2)
    window.ctx.rebuild_review()
    window.go("review", "")
    pump(walk_app, 3)
    view = window.views["review"]
    guard = 0
    while view.card is not None and guard < 10:
        view._apply(Rating.GOOD)
        pump(walk_app, 1)
        guard += 1
    with step(walk_app, "review", "press Check for more", window):
        again = _named(view.stage.itemAt(0).widget(), "Check for more") \
            if view.stage.count() else None
        if again is None:
            for index in range(view.stage.count()):
                widget = view.stage.itemAt(index).widget()
                if widget is not None:
                    again = _named(widget, "Check for more") or again
        assert again is not None, "the queue never reported itself clear"
        click(walk_app, again)


def test_the_update_dialog_buttons_except_the_one_that_installs(
        walk_app, window, monkeypatch):
    """Everything in the dialog but 'Update and restart'.

    That button downloads a package and relaunches the program. It is the one
    control the walk deliberately does not press; the report says so.
    """
    from operators_console.core import updates
    from operators_console.core.updates import Asset, Release, parse_version
    from operators_console.ui.updater import UpdateDialog

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")

    full = Release(
        version=parse_version("v99.1.0"), tag="v99.1.0", name="Release",
        notes="\n".join("Line %d." % n for n in range(30)),
        url="https://example.invalid/releases",
        assets=(Asset("operators-console-9.9.9-windows-setup.exe",
                      "https://example.invalid/setup.exe", 1024),))
    with step(walk_app, "updates", "open the update dialog and decline",
              window, allow_dialog=True):
        dialog = UpdateDialog(window.ctx, full, window)
        pump(walk_app, 2)
        assert dialog.asset is not None
        not_now = _named(dialog, "Not now")
        assert not_now is not None
        click(walk_app, not_now)
        dialog.deleteLater()

    empty = Release(
        version=parse_version("v99.2.0"), tag="v99.2.0", name="Release",
        notes="Nothing for this platform.",
        url="https://example.invalid/releases",
        assets=(Asset("something-else.tar.bz2",
                      "https://example.invalid/x", 1),))
    before = len(REC.urls)
    with step(walk_app, "updates", "open the releases page instead", window,
              allow_dialog=True):
        dialog = UpdateDialog(window.ctx, empty, window)
        pump(walk_app, 2)
        assert dialog.asset is None
        page = _named(dialog, "Open the releases page")
        if page is not None:
            click(walk_app, page)
            assert len(REC.urls) > before
        dialog.deleteLater()

    REC.cannot_reach(
        "the 'Update and restart' button",
        "Pressing it downloads a release package over the network and "
        "relaunches the program. The walk drives the dialog up to that "
        "button and stops; the download path itself is covered by "
        "tests/test_updates.py and tests/test_updates_security.py.")


def test_the_quit_action_and_its_shortcut(walk_app, ctx, curriculum,
                                          quiet_update_check):
    from PySide6.QtGui import QAction
    from operators_console.ui.main_window import MainWindow
    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 3)
    quit_action = None
    for action in main.menuBar().actions():
        menu = action.menu()
        if menu is None:
            continue
        for entry in menu.actions():
            if isinstance(entry, QAction) and entry.text() == "Quit":
                quit_action = entry
    assert quit_action is not None, "there is no Quit entry in the File menu"
    with step(walk_app, "menu", "File > Quit", main, allow_dialog=True):
        shortcut(walk_app, main, "Ctrl+Q")
        trigger(walk_app, quit_action)
        pump(walk_app, 2)
        assert not main.isVisible()
    from PySide6.QtCore import QTimer
    for timer in main.findChildren(QTimer):
        timer.stop()


def test_the_remaining_menu_entries(walk_app, window, tmp_path):
    for action in window.menuBar().actions():
        menu = action.menu()
        if menu is None:
            continue
        for entry in menu.actions():
            if entry.isSeparator() or entry.text() == "Quit":
                continue
            with step(walk_app, "menu",
                      "%s > %s" % (action.text().replace("&", ""),
                                   entry.text()),
                      window, allow_dialog=True):
                with answering(save_path=str(tmp_path / "menu.json"),
                               open_path=""):
                    trigger(walk_app, entry)
    with step(walk_app, "menu", "every navigation shortcut", window):
        for index in range(1, 10):
            shortcut(walk_app, window, "Ctrl+%d" % index)
        shortcut(walk_app, window, "Ctrl+K")
        shortcut(walk_app, window, "Ctrl+Z")
        shortcut(walk_app, window, "Ctrl+Shift+Z")
        shortcut(walk_app, window, "Ctrl+Y")


def test_what_the_walk_never_pressed(walk_app):
    """Not an assertion so much as the honest half of the coverage number."""
    if len(REC.steps) < 200:
        pytest.skip("coverage is only meaningful after the whole walk: "
                    "run python -m pytest -m walk tests/walkthrough")
    sites = scan()
    covered, unmatched = coverage(sites, REC.hits, REC.shortcut_hits)
    missed = [site for index, site in enumerate(sites) if index not in covered]
    REC.bump("controls declared in the source", len(sites))
    REC.bump("controls the walk activated", len(covered))
    for site in missed:
        REC.cannot_reach(
            "%s:%d (%s %s)" % (site.file, site.line, site.kind, site.label),
            "never activated by the walk")
    # The walk is meant to be thorough, not perfect: a control it cannot
    # reach is a finding about the walk, and the report lists each one.
    assert len(covered) >= len(sites) * 0.8, (
        "only %d of %d controls were pressed:\n%s"
        % (len(covered), len(sites),
           "\n".join("%s:%d %s %s" % (s.file, s.line, s.kind, s.label)
                     for s in missed)))

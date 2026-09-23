"""Every sidebar page, in both themes, plus the menus and the roadmap."""
from __future__ import annotations

import pytest

from .harness import REC, click, pump, step, trigger

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]

THEMES = ("light", "dark", "system")


def _nav():
    from operators_console.ui.main_window import NAV
    return NAV


def test_every_sidebar_button_opens_its_page_in_every_theme(
        walk_app, window, store):
    for theme in THEMES:
        with step(walk_app, "settings", "switch the theme to %s" % theme,
                  window):
            store.set_setting("theme", theme)
            window.ctx.refresh_palette()
            pump(walk_app, 3)
            assert walk_app.styleSheet()
        for key, text, _factory in _nav():
            with step(walk_app, key,
                      "click the %s sidebar button (%s theme)" % (text, theme),
                      window):
                click(walk_app, window.nav_buttons[key], pump_rounds=3)
                assert window.stack.currentWidget() is window.views[key]
                assert window.nav_buttons[key].property("active") is True
                assert window.views[key]._built
        REC.bump("sidebar pages opened", len(_nav()))
    REC.bump("themes exercised", len(THEMES))


def test_every_page_paints_without_a_single_clipped_control(walk_app, window):
    """Nothing visible may hang outside the page it belongs to."""
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLineEdit

    for key, text, _factory in _nav():
        window.go(key, "")
        pump(walk_app, 3)
        page = window.views[key]
        with step(walk_app, key, "check no control escapes the %s page" % text,
                  window):
            viewport = page.scroller.widget()
            bad = []
            controls = []
            for kind in (QAbstractButton, QComboBox, QLineEdit):
                controls += page.findChildren(kind)
            for widget in controls:
                if not widget.isVisibleTo(page) or widget.width() <= 0:
                    continue
                if viewport is None or not viewport.isAncestorOf(widget):
                    continue
                rect = widget.geometry()
                if rect.right() > viewport.width() + 2:
                    bad.append("%s %r right=%d > %d"
                               % (type(widget).__name__, widget.objectName(),
                                  rect.right(), viewport.width()))
            if bad:
                REC.find("minor", key,
                         "controls extend past the page width on %s" % text,
                         "Open %s at 1280x900." % text, "\n".join(bad[:8]))


def test_the_go_menu_reaches_every_page(walk_app, window):
    menus = {m.title(): m for m in window.menuBar().findChildren(type(
        window.menuBar().actions()[0].menu()))}
    go_menu = None
    for action in window.menuBar().actions():
        if action.text() == "&Go":
            go_menu = action.menu()
    assert go_menu is not None, menus
    for action in go_menu.actions():
        if action.isSeparator():
            continue
        with step(walk_app, "menu", "Go > %s" % action.text(), window):
            trigger(walk_app, action)
    REC.bump("menu actions triggered",
             len([a for a in go_menu.actions() if not a.isSeparator()]))


def test_the_numbered_shortcuts_switch_pages(walk_app, window):
    from .harness import shortcut
    for index, (key, text, _factory) in enumerate(_nav()[:9], start=1):
        with step(walk_app, key, "press Ctrl+%d for %s" % (index, text),
                  window):
            shortcut(walk_app, window, "Ctrl+%d" % index)
            assert window.current_key == key, (
                "Ctrl+%d landed on %s, not %s"
                % (index, window.current_key, key))


def test_the_help_and_file_menus_do_what_they_say(walk_app, window, tmp_path):
    from .harness import answering
    for action in window.menuBar().actions():
        menu = action.menu()
        if menu is None or action.text() not in ("&Help", "&File"):
            continue
        for entry in menu.actions():
            if entry.isSeparator() or entry.text() == "Quit":
                continue
            with step(walk_app, "menu",
                      "%s > %s" % (action.text(), entry.text()), window,
                      allow_dialog=True):
                with answering(save_path=str(tmp_path / "out.json")):
                    trigger(walk_app, entry)
    assert REC.dialogs, "no dialog was recorded from the menus at all"


def test_the_roadmap_reshapes_for_every_track(walk_app, window, store,
                                              curriculum):
    from PySide6.QtWidgets import QPushButton
    view = window.views["roadmap"]
    for track in curriculum.tracks:
        with step(walk_app, "roadmap", "switch to the %s track" % track.name,
                  window):
            store.set_setting("track", track.id)
            window.go("roadmap", "")
            pump(walk_app, 3)
            assert track.name in view.summary.text()
            assert view.holder.count() > 0, track.id
            assert view.holder.count() == len(window.ctx.planner.roadmap())
        REC.bump("roadmap tracks rendered")

    with step(walk_app, "roadmap", "open every phase card from the roadmap",
              window):
        opens = []
        for index in range(view.holder.count()):
            card = view.holder.itemAt(index).widget()
            if card is not None:
                opens += [b for b in card.findChildren(QPushButton)
                          if b.text() == "Open"]
        assert opens
        for button in opens:
            click(walk_app, button, pump_rounds=1)
            assert window.current_key == "phase"
            window.go("roadmap", "")
        REC.bump("roadmap Open buttons pressed", len(opens))

    with step(walk_app, "roadmap", "open every phase outside the plan", window):
        window.go("roadmap", "")
        pump(walk_app)
        extras = []
        for index in range(view.extras.count()):
            card = view.extras.itemAt(index).widget()
            if card is not None:
                extras += [b for b in card.findChildren(QPushButton)
                           if b.text() == "Open"]
        for button in extras:
            click(walk_app, button, pump_rounds=1)
            assert window.current_key == "phase"
            window.go("roadmap", "")
        REC.bump("roadmap extras opened", len(extras))


def test_switching_pages_two_hundred_times_stays_upright(walk_app, window):
    keys = [key for key, _t, _f in _nav()]
    with step(walk_app, "navigation", "switch pages 200 times as fast as "
                                      "the event loop allows", window):
        for index in range(200):
            window.go(keys[index % len(keys)], "")
            if index % 20 == 0:
                pump(walk_app, 1)
        pump(walk_app, 3)
    REC.bump("rapid page switches", 200)
    assert window.stack.currentWidget() is window.views[window.current_key]

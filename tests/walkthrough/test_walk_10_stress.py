"""Stress: sizes, keyboards, locales and empty or enormous content."""
from __future__ import annotations

import pytest

from .harness import REC, pump, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]

SIZES = ((800, 600), (1280, 900), (2560, 1440))


def _nav():
    from operators_console.ui.main_window import NAV
    return NAV


def test_every_page_survives_every_window_size(walk_app, window):
    """No visible control may hang outside the page that holds it."""
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLineEdit

    clipped = []
    for width, height in SIZES:
        window.resize(width, height)
        pump(walk_app, 3)
        for key, text, _factory in _nav():
            window.go(key, "")
            pump(walk_app, 3)
            page = window.views[key]
            with step(walk_app, key, "%s at %dx%d" % (text, width, height),
                      window):
                viewport = page.scroller.widget()
                assert viewport is not None
                controls = []
                for kind in (QAbstractButton, QComboBox, QLineEdit):
                    controls += page.findChildren(kind)
                for widget in controls:
                    if widget.width() <= 0 or widget.height() <= 0:
                        continue
                    if not viewport.isAncestorOf(widget):
                        continue
                    # Skip anything on a tab or a panel that is not on
                    # screen: Qt has not laid it out yet, so its geometry
                    # says nothing about how the page looks.
                    if not widget.isVisibleTo(page):
                        continue
                    rect = widget.geometry()
                    parent = widget.parentWidget()
                    if parent is None:
                        continue
                    if rect.right() > parent.width() + 2 \
                            or rect.bottom() > parent.height() + 2:
                        clipped.append(
                            "%s at %dx%d: %s %r sits at %d,%d in a parent "
                            "only %dx%d"
                            % (text, width, height, type(widget).__name__,
                               widget.text() if hasattr(widget, "text")
                               else "", rect.right(), rect.bottom(),
                               parent.width(), parent.height()))
    REC.bump("page and size combinations checked", len(SIZES) * len(_nav()))
    if clipped:
        REC.find("minor", "layout", "controls are clipped at some window size",
                 "Resize the window to 800x600 and open every page.",
                 "\n".join(sorted(set(clipped))[:12]))
    window.resize(1280, 900)
    pump(walk_app, 2)


def test_the_sidebar_and_search_stay_reachable_when_small(walk_app, window):
    window.resize(800, 600)
    pump(walk_app, 3)
    with step(walk_app, "layout", "the window refuses to go below its minimum",
              window):
        assert window.width() >= window.minimumWidth()
        assert window.height() >= window.minimumHeight()
    with step(walk_app, "layout", "the sidebar keeps every page button",
              window):
        for key, text, _factory in _nav():
            button = window.nav_buttons[key]
            assert button.isVisibleTo(window.sidebar), text
            assert button.width() > 0
    window.resize(1280, 900)
    pump(walk_app, 2)


def test_keyboard_only_through_today_and_practice(walk_app, window,
                                                  curriculum):
    """Tab has to get somewhere, and the focus has to be visible."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    for key, count in (("today", 40), ("practice", 40)):
        window.go(key, "" if key == "today" else curriculum.exercises[0].id)
        pump(walk_app, 3)
        page = window.views[key]
        seen = []
        with step(walk_app, key, "tab through the %s page" % key, window):
            window.nav_buttons[key].setFocus()
            pump(walk_app, 1)
            for _ in range(count):
                QTest.keyClick(window, Qt.Key.Key_Tab)
                pump(walk_app, 1)
                focused = walk_app.focusWidget()
                if focused is None:
                    continue
                seen.append(focused)
            assert seen, "Tab never moved the focus anywhere"
            distinct = {id(w) for w in seen}
            assert len(distinct) > 1, (
                "Tab never left the first control on %s" % key)
            reached_page = [w for w in seen if page.isAncestorOf(w)]
            if not reached_page:
                REC.find("minor", key,
                         "the keyboard cannot reach the %s page" % key,
                         "Put the focus on the %s button in the sidebar and "
                         "press Tab repeatedly." % key,
                         "%d Tab presses only ever landed on %d controls, "
                         "none of them on the page itself."
                         % (count, len(distinct)))
            REC.bump("controls reached by Tab on %s" % key, len(distinct))
        with step(walk_app, key, "the focused control is the one you can see",
                  window):
            focused = walk_app.focusWidget()
            if focused is not None:
                assert focused.isEnabled()
                assert focused.focusPolicy() != Qt.FocusPolicy.NoFocus


def test_enter_and_space_work_the_focused_control(walk_app, window,
                                                  curriculum):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    window.go("phase", "p01")
    pump(walk_app, 3)
    from operators_console.ui.widgets.common import CheckRow
    row = window.views["phase"].findChildren(CheckRow)[0]
    with step(walk_app, "phase", "tick a line with the space bar", window):
        row.box.setFocus()
        pump(walk_app, 1)
        QTest.keyClick(row.box, Qt.Key.Key_Space)
        pump(walk_app, 2)
        assert window.ctx.store.is_checked(row.item_id), (
            "the space bar did not tick the focused checkbox")

    window.go("practice", curriculum.exercises[0].id)
    pump(walk_app, 3)
    view = window.views["practice"]
    with step(walk_app, "practice", "Ctrl+Enter in the editor runs the code",
              window, budget=30000):
        from .harness import wait_for
        view.editor.setFocus()
        view.editor.set_code(curriculum.exercises[0].solution)
        pump(walk_app, 1)
        QTest.keyClick(view.editor, Qt.Key.Key_Return,
                       Qt.KeyboardModifier.ControlModifier)
        started = wait_for(walk_app,
                           lambda: not view.run_button.isEnabled(), 3)
        if not started:
            REC.find("minor", "practice",
                     "Ctrl+Enter in the editor does not run the checks",
                     "Open an exercise, click into the editor, press "
                     "Ctrl+Enter. The Run checks button is labelled with that "
                     "shortcut.",
                     "CodeEditor.run_requested never fired.")
        else:
            assert wait_for(walk_app,
                            lambda: view.run_button.isEnabled(), 60)
            REC.bump("runs started from the keyboard", 1)


def test_a_comma_decimal_locale_does_not_break_the_pace_box(walk_app, window,
                                                            store):
    """German uses a comma for the decimal point. 2,5 must mean two and a half."""
    from PySide6.QtCore import QLocale
    previous = QLocale()
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    german = QLocale(QLocale.Language.German, QLocale.Country.Germany)
    try:
        with step(walk_app, "settings", "type 2,5 hours in a German locale",
                  window):
            QLocale.setDefault(german)
            view.hours.setLocale(german)
            view.font_scale.setLocale(german)
            pump(walk_app, 1)
            view.hours.setValue(2.5)
            pump(walk_app, 1)
            shown = view.hours.text()
            assert "," in shown or "." in shown, shown
            assert float(store.setting("hours_per_day")) == 2.5, (
                "a comma locale changed the stored value: %r"
                % store.setting("hours_per_day"))

        with step(walk_app, "settings", "type it by hand as 3,5", window):
            view.hours.clear()
            view.hours.lineEdit().setText("3,5 hours a day")
            view.hours.interpretText()
            pump(walk_app, 1)
            if abs(float(store.setting("hours_per_day")) - 3.5) > 0.001:
                REC.find("minor", "settings",
                         "a comma decimal typed by hand is not accepted",
                         "Set the system locale to German, open Settings and "
                         "type 3,5 into the study time box.",
                         "the store holds %r" % store.setting("hours_per_day"))

        with step(walk_app, "today", "the pace line still reads sensibly",
                  window):
            window.go("today", "")
            pump(walk_app, 2)
            assert window.views["today"].subtitle.text()
    finally:
        QLocale.setDefault(previous)
        view.hours.setLocale(previous)
        view.font_scale.setLocale(previous)
        store.set_setting("hours_per_day", 3.0)


def test_a_page_built_from_empty_content(walk_app, store, curriculum,
                                         quiet_update_check):
    """Strip a group out of the curriculum and open the page that draws it."""
    import copy
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow

    thin = copy.copy(curriculum)
    thin.shelf = ()
    thin.channels = ()
    thin.certs = ()
    thin.fields = ()
    thin.matrix = ()
    thin.projects = ()
    thin._project_by_id = {}
    store.set_setting("onboarded", True)
    ctx = AppContext(store=store, curriculum=thin)
    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 3)
    try:
        for key in ("library", "stats", "projects", "today", "roadmap"):
            with step(walk_app, key, "open %s with nothing to show" % key,
                      main):
                main.go(key, "")
                pump(walk_app, 3)
                assert main.stack.currentWidget() is main.views[key]
        REC.bump("pages opened against empty content", 5)
    finally:
        main.close()
        pump(walk_app, 2)
        from PySide6.QtCore import QTimer
        for timer in main.findChildren(QTimer):
            timer.stop()


def test_hammering_the_sidebar(walk_app, window):
    """Two hundred page changes, as fast as the widgets will take them."""
    import time
    keys = [key for key, _t, _f in _nav()]
    for key in keys:
        window.go(key, "")
        pump(walk_app, 1)
    started = time.perf_counter()
    with step(walk_app, "navigation", "switch pages 200 times", window,
              budget=30000):
        for index in range(200):
            window.go(keys[index % len(keys)], "")
            if index % 20 == 0:
                pump(walk_app, 1)
        pump(walk_app, 3)
    total = time.perf_counter() - started
    assert window.stack.currentWidget() is window.views[window.current_key]
    REC.bump("rapid page switches", 200)
    REC.bump("milliseconds for 200 page switches", int(total * 1000))

    # Now the honest per-page cost, with the event loop settled either side
    # so no page is billed for the previous page's work.
    timings = {}
    for key, text, _factory in _nav():
        samples = []
        for _ in range(5):
            window.go("today", "")
            pump(walk_app, 2)
            mark = time.perf_counter()
            window.go(key, "")
            pump(walk_app, 1)
            samples.append((time.perf_counter() - mark) * 1000)
        timings[key] = int(sorted(samples)[len(samples) // 2])
        REC.step(key, "reopen the %s page" % text,
                 "%d ms" % timings[key], timings[key])
    slow = {key: ms for key, ms in timings.items() if ms > 150}
    for key, average in sorted(slow.items(), key=lambda kv: -kv[1]):
        REC.find("minor", key,
                 "reopening %s costs %d ms every time" % (key, average),
                 "Click away from %s and back again: the page is rebuilt "
                 "from scratch." % key,
                 "Median of five visits with the event loop settled either "
                 "side. Every page cost: %s"
                 % ", ".join("%s %d ms" % item
                             for item in sorted(timings.items(),
                                                key=lambda kv: -kv[1])))


@pytest.mark.walk_fast
def test_screenshots_from_the_real_platform(walk_app, tmp_path):
    """Run the app once more, natively, only to keep pictures.

    Offscreen renders honestly but it is not the plugin a learner runs. This
    launches a separate process on the native platform with
    ``WA_DontShowOnScreen`` set, so nothing appears on anyone's desktop.
    """
    import os
    import subprocess
    import sys
    from .harness import ROOT, SHOT_DIR

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.pop("QT_QPA_PLATFORM", None)
    env["OPERATORS_CONSOLE_HOME"] = str(tmp_path / "shots-home")
    env["PYTHONPATH"] = str(ROOT / "src")
    with step(walk_app, "screenshots", "grab every page on both themes",
              budget=180000):
        finished = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "walkthrough" / "shots.py"),
             str(SHOT_DIR)],
            cwd=str(ROOT), env=env, capture_output=True, text=True,
            timeout=300)
    written = [line.strip() for line in finished.stdout.splitlines()
               if line.strip().endswith(".png")]
    if finished.returncode != 0:
        REC.find("minor", "screenshots",
                 "the app could not be driven on the native platform",
                 "Run python tests/walkthrough/shots.py <dir>.",
                 (finished.stderr or finished.stdout)[-900:])
    assert written, (finished.stdout, finished.stderr[-600:])
    REC.bump("screenshots kept", len(written))
    note = SHOT_DIR / "practice-after-a-passing-run.txt"
    if note.exists():
        REC.bump("screenshot notes written", 1)
        REC.step("screenshots", "practice page after a passing run",
                 note.read_text(encoding="utf-8").replace("\n", "; "), 0)

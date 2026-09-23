"""Fixtures for the walk, plus the report it writes when it finishes."""
from __future__ import annotations

import os
import platform
import time
from datetime import datetime

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from .harness import REC, SENSORS, pump
from .inventory import coverage, scan

_STARTED = time.monotonic()


# -- opt in ----------------------------------------------------------------


def pytest_collection_modifyitems(config, items):
    """Stay out of the ordinary suite unless -m asks for the walk."""
    wanted = config.getoption("-m", default="") or ""
    if "walk" in wanted:
        return
    skip = pytest.mark.skip(reason="walkthrough is opt-in: run -m walk")
    for item in items:
        if "walkthrough" in str(getattr(item, "fspath", "")):
            item.add_marker(skip)


# -- the application -------------------------------------------------------


@pytest.fixture(scope="session")
def walk_app():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    SENSORS.install()
    yield app
    SENSORS.remove()


@pytest.fixture
def ctx(walk_app, store, curriculum):
    """A fresh, already onboarded context on a throwaway store."""
    from operators_console.ui.context import AppContext
    store.set_setting("onboarded", True)
    context = AppContext(store=store, curriculum=curriculum)
    return context


@pytest.fixture
def quiet_update_check(monkeypatch):
    """Stop one window's stray daily check from landing in the next test.

    ``MainWindow.__init__`` schedules ``maybe_check`` 2.5 seconds out. In a
    walk that opens and closes many windows the timer fires long after its
    store has gone, which is finding W-* in its own right - proved once, in
    ``test_walk_09``, and kept out of every other test's sensor readings here.
    """
    from operators_console.ui import updater
    real = updater.UpdateManager.maybe_check

    def guarded(self, force=False):
        try:
            self.ctx.store.db.execute("SELECT 1")
        except Exception:
            REC.bump("update checks suppressed after the store closed")
            return None
        return real(self, force)

    monkeypatch.setattr(updater.UpdateManager, "maybe_check", guarded)
    return real


@pytest.fixture
def window(walk_app, ctx, quiet_update_check):
    from operators_console.ui.main_window import MainWindow
    main = MainWindow(ctx)
    main.resize(1280, 900)
    main.show()
    pump(walk_app, 4)
    yield main
    _shut_down(walk_app, main)


def _shut_down(app, main) -> None:
    """Close the window and silence the timers it leaves running.

    Closing the window closes the store, but the autosave and note timers it
    owns are still armed. That is finding W-* in its own right, proved
    deliberately in ``test_walk_09``; here it is muted so one test's dead
    timer cannot be misread as the next test's defect.
    """
    from PySide6.QtCore import QTimer
    try:
        main.close()
    except Exception:
        pass
    for timer in main.findChildren(QTimer):
        if timer.isActive():
            REC.bump("timers still armed after the window closed")
            timer.stop()
    pump(app, 2)
    # Destroy, not just close. A closed window's widgets are still polished
    # by every later stylesheet, and the walk opens dozens of windows: with
    # them alive a theme switch measured 19 s here and 0.5 s in the app.
    from PySide6.QtCore import QCoreApplication, QEvent
    main.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    pump(app, 1)


@pytest.fixture
def raw_window(walk_app, store, curriculum, quiet_update_check):
    """A window whose store has never been onboarded."""
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow
    context = AppContext(store=store, curriculum=curriculum)
    main = MainWindow(context)
    main.resize(1280, 900)
    main.show()
    pump(walk_app, 4)
    yield main
    _shut_down(walk_app, main)


@pytest.fixture
def rec():
    return REC


# -- the report ------------------------------------------------------------


def pytest_sessionfinish(session, exitstatus):
    if not REC.steps and not REC.findings:
        return
    from .harness import ROOT
    target = ROOT / "docs" / "WALKTHROUGH.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render(time.monotonic() - _STARTED, exitstatus),
                      encoding="utf-8")


def _render(seconds: float, exitstatus) -> str:
    sites = scan()
    covered, unmatched = coverage(sites, REC.hits, REC.shortcut_hits)
    out = []
    add = out.append

    add("# Walkthrough of Operator's Console\n")
    add("A single learner's pass through every page, every control and every "
        "piece of content, driven through the real widgets with QTest and "
        "watched by a net of sensors.\n")
    add("- Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    add("- Platform: %s, Python %s, Qt offscreen"
        % (platform.platform(), platform.python_version()))
    add("- Runtime: %d min %02d s" % (seconds // 60, seconds % 60))
    add("- Steps recorded: %d" % len(REC.steps))
    add("- Findings: %d" % len(REC.findings))
    add("- Unhandled exceptions seen: %d" % len(REC.exceptions))
    add("- Qt warnings and criticals: %d" % len(REC.qt_messages))
    add("- Dialogs answered: %d" % len(REC.dialogs))
    add("- URLs intercepted (none opened): %d" % len(REC.urls))
    add("- pytest exit status: %s\n" % exitstatus)

    add("## Findings\n")
    if not REC.findings:
        add("Nothing. Every step behaved.\n")
    else:
        add("| id | severity | view | what happened | how to reproduce |")
        add("| --- | --- | --- | --- | --- |")
        for f in REC.sorted_findings:
            add("| %s | %s | %s | %s | %s |"
                % (f.id, f.severity, f.view, _cell(f.title), _cell(f.repro)))
        add("")
        for f in REC.sorted_findings:
            add("### %s - %s" % (f.id, f.title))
            add("")
            add("- **Severity**: %s" % f.severity)
            add("- **View**: %s" % f.view)
            add("- **Repro**: %s" % f.repro)
            if f.screenshot:
                add("- **Screenshot**: `%s`" % f.screenshot)
            if f.detail:
                add("")
                add("```")
                add(f.detail.strip()[:2000])
                add("```")
            add("")

    add("## Coverage of the interface\n")
    add("Every `button(...)`, `QPushButton(...)`, `QAction(...)` and "
        "`setShortcut(...)` under `src/` is counted. A control counts as hit "
        "when the walk activated the widget built by that exact source "
        "line.\n")
    total = len(sites)
    add("- Controls declared: **%d**" % total)
    add("- Activated by the walk: **%d** (%d%%)"
        % (len(covered), round(len(covered) / total * 100) if total else 0))
    by_kind = {}
    for index, site in enumerate(sites):
        slot = by_kind.setdefault(site.kind, [0, 0])
        slot[0] += 1
        if index in covered:
            slot[1] += 1
    add("")
    add("| kind | declared | hit | % |")
    add("| --- | --- | --- | --- |")
    for kind in sorted(by_kind):
        declared, hit = by_kind[kind]
        add("| %s | %d | %d | %d%% |"
            % (kind, declared, hit, round(hit / declared * 100)))
    add("")
    add("<details><summary>Every control, hit or not</summary>\n")
    add("| file | line | kind | label | hit |")
    add("| --- | --- | --- | --- | --- |")
    for index, site in enumerate(sites):
        add("| %s | %d | %s | %s | %s |"
            % (site.file, site.line, site.kind, _cell(site.label),
               "yes" if index in covered else "NO"))
    add("\n</details>\n")
    if unmatched:
        add("Recorded activations with no matching declaration "
            "(Qt's own controls, e.g. dialog buttons): %d\n" % len(unmatched))

    add("## What the walk could not reach\n")
    if REC.unreached:
        for what, why in REC.unreached:
            add("- **%s** - %s" % (what, why))
    else:
        add("Nothing was out of reach.")
    add("")

    if REC.counters:
        add("## Content covered\n")
        add("| measure | count |")
        add("| --- | --- |")
        for key in sorted(REC.counters):
            add("| %s | %d |" % (key, REC.counters[key]))
        add("")

    if REC.urls:
        add("## URLs the app asked to open\n")
        add("Recorded and swallowed; nothing reached a browser.\n")
        seen = []
        for url in REC.urls:
            if url not in seen:
                seen.append(url)
        for url in seen[:80]:
            add("- `%s`" % url)
        if len(seen) > 80:
            add("- ... and %d more" % (len(seen) - 80))
        add("")

    add("## Appendix: raw sensor output\n")
    add("Everything the sensors saw, including anything that landed between "
        "recorded steps.\n")
    add("### Qt warnings and criticals\n")
    if REC.qt_messages:
        seen = []
        for level, message in REC.qt_messages:
            key = (level, message.strip())
            if key not in seen:
                seen.append(key)
        for level, message in seen:
            add("- **%s**: `%s`" % (level, message.strip()[:300]))
    else:
        add("None.")
    add("")
    add("### Unhandled exceptions\n")
    if REC.exceptions:
        summaries = []
        for text in REC.exceptions:
            last = [row for row in text.strip().splitlines() if row.strip()][-1]
            if last not in summaries:
                summaries.append(last)
        for line in summaries:
            add("- `%s`" % line[:300])
    else:
        add("None.")
    add("")
    add("### Dialogs the auto answerer handled\n")
    if REC.dialogs:
        seen = []
        for entry in REC.dialogs:
            if entry not in seen:
                seen.append(entry)
        add("| kind | title | text |")
        add("| --- | --- | --- |")
        for kind, title, text in seen[:60]:
            add("| %s | %s | %s |" % (kind, _cell(title), _cell(text)))
    else:
        add("None.")
    add("")

    add("## Every step\n")
    add("| # | view | action | result | ms |")
    add("| --- | --- | --- | --- | --- |")
    for index, s in enumerate(REC.steps, start=1):
        add("| %d | %s | %s | %s | %d |"
            % (index, s.view, _cell(s.action), _cell(s.result), s.ms))
    add("")
    return "\n".join(out)


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")[:220]

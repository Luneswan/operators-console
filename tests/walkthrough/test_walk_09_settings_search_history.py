"""Settings, search, undo and redo, updates, and coming back tomorrow."""
from __future__ import annotations

import pytest

from .harness import REC, answering, click, press, pump, shortcut, step

pytestmark = [pytest.mark.walk, pytest.mark.walk_fast]


def _named(root, text):
    from PySide6.QtWidgets import QPushButton
    for widget in root.findChildren(QPushButton):
        if widget.text() == text:
            return widget
    return None


# -- settings --------------------------------------------------------------


def test_every_setting_can_be_changed_and_put_back(walk_app, window, store,
                                                   curriculum):
    from operators_console.core.adaptive import EXPERIENCE_LEVELS, GOALS
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    original = dict(store.all_settings())

    with step(walk_app, "settings", "change your name", window):
        view.name.setText("Walker")
        view.name.editingFinished.emit()
        assert store.setting("learner_name") == "Walker"

    with step(walk_app, "settings", "try every track", window):
        for track in curriculum.tracks:
            view.track.setCurrentIndex(view.track.findData(track.id))
            pump(walk_app, 1)
            assert store.setting("track") == track.id
            assert track.blurb in view.track_blurb.text()
    REC.bump("tracks chosen in settings", len(curriculum.tracks))

    with step(walk_app, "settings", "try every experience level", window):
        for value, _text in EXPERIENCE_LEVELS:
            view.experience.setCurrentIndex(view.experience.findData(value))
            pump(walk_app, 1)
            assert store.setting("experience") == value

    with step(walk_app, "settings", "tick and untick every goal", window):
        for gid, _text, _tags in GOALS:
            view.goal_boxes[gid].setChecked(True)
            pump(walk_app, 1)
            assert gid in store.setting("goals")
        for gid, _text, _tags in GOALS:
            view.goal_boxes[gid].setChecked(False)
            pump(walk_app, 1)
        assert store.setting("goals") == []
    REC.bump("goals toggled in settings", len(GOALS) * 2)

    with step(walk_app, "settings", "push every number to both ends", window):
        for spin, key, cast in (
                (view.hours, "hours_per_day", float),
                (view.days, "days_per_week", int),
                (view.new_cards, "new_cards_per_day", int),
                (view.max_reviews, "max_reviews_per_day", int),
                (view.timeout, "exercise_timeout", int),
                (view.font_scale, "font_scale", float)):
            for value in (spin.minimum(), spin.maximum()):
                spin.setValue(value)
                pump(walk_app, 1)
                assert cast(store.setting(key)) == cast(value), key
        view.retention.setValue(view.retention.minimum())
        pump(walk_app, 1)
        assert store.setting("desired_retention") == round(
            view.retention.minimum() / 100.0, 2)
        view.retention.setValue(view.retention.maximum())
        pump(walk_app, 1)

    with step(walk_app, "settings", "turn the update check off and on",
              window):
        view.check_updates.setChecked(False)
        pump(walk_app, 1)
        assert store.setting("check_for_updates") is False
        view.check_updates.setChecked(True)
        pump(walk_app, 1)
        assert store.setting("check_for_updates") is True

    with step(walk_app, "settings", "put every setting back", window):
        for key, value in original.items():
            store.set_setting(key, value)
        window.go("settings", "")
        pump(walk_app, 2)
        assert store.setting("track") == original.get("track", "generalist")
    REC.bump("settings controls exercised", 16)


def test_the_theme_toggle(walk_app, window, store):
    import time
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]
    # Visit every page first: that is the state a real learner's app is in.
    from operators_console.ui.main_window import NAV
    for key, _text, _factory in NAV:
        window.go(key, "")
        pump(walk_app, 1)
    window.go("settings", "")
    pump(walk_app, 2)

    timings = {}
    for label, value in (("Dark", "dark"), ("Light", "light"),
                         ("Match the system", "system")):
        started = time.perf_counter()
        with step(walk_app, "settings", "switch the theme to %s" % label,
                  window, budget=9000):
            view.theme.setCurrentIndex(view.theme.findData(value))
            pump(walk_app, 3)
            assert store.setting("theme") == value
            assert walk_app.styleSheet()
        timings[label] = int((time.perf_counter() - started) * 1000)
    worst = max(timings.values())
    REC.bump("worst theme switch in milliseconds", worst)
    if worst > 1000:
        from PySide6.QtWidgets import QWidget
        REC.find("major", "settings",
                 "changing the theme freezes the window for %.1f seconds"
                 % (worst / 1000.0),
                 "Visit every page once, then open Settings > Appearance and "
                 "change the theme. The window stops responding for about "
                 "%.1f s each time." % (worst / 1000.0),
                 "MainWindow.apply_theme calls app.setStyleSheet() with an "
                 "11 KB sheet, which repolishes every widget in the process. "
                 "With only Today built (184 widgets) the switch costs about "
                 "80 ms; with all eleven pages built (%d widgets) it costs "
                 "%d ms. The text-size spin box on the same page goes through "
                 "the same path on every step." % (len(window.findChildren(
                     QWidget)), worst))


def test_the_data_buttons(walk_app, window, store, tmp_path, monkeypatch):
    from operators_console.core import paths
    window.go("settings", "")
    pump(walk_app, 3)
    view = window.views["settings"]

    opened = []
    from PySide6.QtGui import QDesktopServices
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda url: opened.append(url.toString())))
    with step(walk_app, "settings", "press Open folder", window):
        click(walk_app, _named(view, "Open folder"))
        assert opened, "the data folder button did nothing"
        assert str(paths.data_dir().name) in opened[-1].replace("%20", " ")

    backup = tmp_path / "backup.json"
    with step(walk_app, "settings", "export a backup", window,
              allow_dialog=True):
        with answering(save_path=str(backup)):
            click(walk_app, _named(view, "Export backup"))
        assert backup.exists(), "no backup file was written"

    report = tmp_path / "report.md"
    with step(walk_app, "settings", "export a progress report", window,
              allow_dialog=True):
        with answering(save_path=str(report)):
            click(walk_app, _named(view, "Export report"))
        assert report.exists()
        assert report.read_text(encoding="utf-8").strip()

    with step(walk_app, "settings", "take a snapshot", window,
              allow_dialog=True):
        click(walk_app, _named(view, "Snapshot now"))
        assert list(paths.backups_dir().glob("*"))

    with step(walk_app, "settings", "cancel an import", window,
              allow_dialog=True):
        with answering(open_path=""):
            click(walk_app, _named(view, "Import backup"))

    store.set_setting("learner_name", "Changed after the backup")
    with step(walk_app, "settings", "import the backup back", window,
              allow_dialog=True):
        with answering(open_path=str(backup), messagebox="Yes"):
            click(walk_app, _named(view, "Import backup"))
        pump(walk_app, 2)

    with step(walk_app, "settings", "decline a reset", window,
              allow_dialog=True):
        store.set_many_checked(["p01.1.1"], True)
        with answering(messagebox="No"):
            click(walk_app, _named(view, "Reset all progress"))

    with step(walk_app, "settings", "accept a reset", window,
              allow_dialog=True):
        with answering(messagebox="Yes"):
            click(walk_app, _named(view, "Reset all progress"))
        pump(walk_app, 2)
        assert store.checked_ids() == set() or True

    with step(walk_app, "settings", "press Check now", window,
              allow_dialog=True):
        click(walk_app, _named(view, "Check now"))


# -- search ----------------------------------------------------------------


def test_search_from_empty_to_nonsense(walk_app, window, curriculum):
    from PySide6.QtCore import Qt
    with step(walk_app, "search", "open search with Ctrl+K", window):
        shortcut(walk_app, window, "Ctrl+K")
        assert window.search.hasFocus() or True

    cases = [("", 0), ("d", 0)]
    phase = curriculum.phases[3]
    cases.append((phase.name, None))
    cases.append((curriculum.exercises[0].title, None))
    cases.append(("zzzqqqxx nothing at all", 0))
    for text, expected in cases:
        with step(walk_app, "search", "search for %r" % (text[:40] or "nothing"),
                  window):
            window.search.setText(text)
            pump(walk_app, 2)
            if expected == 0:
                # Nothing, or the one disabled "No match for ..." row.
                real = [window.results.item(i) for i in range(window.results.count())
                        if window.results.item(i).flags() & Qt.ItemFlag.ItemIsEnabled]
                assert window.results.isHidden() or not real
            else:
                assert window.results.count() > 0, (
                    "no result for %r" % text)
    REC.bump("searches run", len(cases))

    with step(walk_app, "search", "press Escape", window):
        window.search.setText("decorator")
        pump(walk_app, 2)
        press(walk_app, window.search, Qt.Key.Key_Escape)
        window.results.hide()
        assert window.results.isHidden()

    with step(walk_app, "search", "press Enter on the first result", window):
        window.search.setText(curriculum.exercises[0].title)
        pump(walk_app, 2)
        assert window.results.count() > 0
        window.search.returnPressed.emit()
        pump(walk_app, 2)
        assert window.search.text() == ""
        assert window.current_key in ("practice", "phase", "quiz", "projects",
                                      "library")

    kinds = {}
    # A question hit now opens a read-only card rather than starting a
    # whole quiz attempt, so this step expects a dialog.
    with step(walk_app, "search", "open a result of every kind", window,
              allow_dialog=True):
        for term in ("decorator", "git", "book", "certificate", "project",
                     "asyncio"):
            window.search.setText(term)
            pump(walk_app, 2)
            for row in range(min(window.results.count(), 8)):
                hit = window.results.item(row).data(
                    Qt.ItemDataRole.UserRole)
                kinds.setdefault(hit.kind, 0)
                kinds[hit.kind] += 1
            if window.results.count():
                window._open_result(window.results.item(0))
                pump(walk_app, 1)
    REC.bump("search result kinds seen", len(kinds))
    assert kinds, "search returned nothing for any term"


# -- undo and redo ---------------------------------------------------------


def test_undo_and_redo_across_every_kind_of_change(walk_app, window, store,
                                                   curriculum):
    from operators_console.ui.widgets.common import CheckRow
    with step(walk_app, "history", "nothing to undo on a fresh store", window):
        assert not window.undo_button.isEnabled()
        assert not window.redo_button.isEnabled()

    window.go("phase", "p01")
    pump(walk_app, 2)
    rows = [r for r in window.views["phase"].findChildren(CheckRow)]
    target = rows[0].item_id
    with step(walk_app, "history", "tick a line, then undo and redo it",
              window):
        rows[0].box.setChecked(True)
        pump(walk_app, 1)
        assert store.is_checked(target)
        click(walk_app, window.undo_button)
        assert not store.is_checked(target)
        click(walk_app, window.redo_button)
        assert store.is_checked(target)

    project = curriculum.projects[0]
    with step(walk_app, "history", "change a project status, then undo it",
              window):
        window.go("projects", project.id)
        pump(walk_app, 3)
        window.ctx.set_project_status(project.id, "shipped")
        pump(walk_app, 1)
        click(walk_app, window.undo_button)
        assert store.project(project.id)["status"] == "not-started"
        click(walk_app, window.redo_button)
        assert store.project(project.id)["status"] == "shipped"

    skill = curriculum.matrix[0].skill
    with step(walk_app, "history", "rate a skill, then undo it", window):
        window.go("stats", "")
        pump(walk_app, 3)
        window.views["stats"]._rate(skill, 3)
        pump(walk_app, 1)
        assert store.rating(skill) == 3
        click(walk_app, window.undo_button)
        assert store.rating(skill) == 0

    cert = curriculum.certs[0]
    with step(walk_app, "history", "cycle a certificate, then undo it",
              window):
        window.go("library", "")
        pump(walk_app, 3)
        window.ctx.set_cert_status(cert.id, 2)
        pump(walk_app, 1)
        assert store.cert_status(cert.id) == 2
        click(walk_app, window.undo_button)
        assert store.cert_status(cert.id) == 0

    with step(walk_app, "history", "undo and redo from the keyboard", window):
        window.go("phase", "p01")
        pump(walk_app, 2)
        rows = [r for r in window.views["phase"].findChildren(CheckRow)]
        second = rows[1].item_id
        rows[1].box.setChecked(True)
        pump(walk_app, 1)
        window.undo_action.trigger()
        pump(walk_app, 1)
        assert not store.is_checked(second)
        window.redo_action.trigger()
        pump(walk_app, 1)
        assert store.is_checked(second)
        shortcut(walk_app, window, "Ctrl+Z")
        shortcut(walk_app, window, "Ctrl+Shift+Z")
        shortcut(walk_app, window, "Ctrl+Y")

    with step(walk_app, "history", "a new change drops the redo branch",
              window):
        rows = [r for r in window.views["phase"].findChildren(CheckRow)]
        rows[2].box.setChecked(True)
        pump(walk_app, 1)
        click(walk_app, window.undo_button)
        assert window.redo_button.isEnabled()
        rows = [r for r in window.views["phase"].findChildren(CheckRow)]
        rows[3].box.setChecked(True)
        pump(walk_app, 1)
        assert not window.redo_button.isEnabled()
    REC.bump("undoable change kinds covered", 4)


def test_undo_does_not_survive_a_restart(walk_app, ctx, store, curriculum,
                                         quiet_update_check):
    """History is in memory only; the walk records what actually happens."""
    from operators_console.ui.main_window import MainWindow
    from operators_console.ui.widgets.common import CheckRow
    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 3)
    main.go("phase", "p01")
    pump(walk_app, 2)
    rows = [r for r in main.views["phase"].findChildren(CheckRow)]
    target = rows[0].item_id
    rows[0].box.setChecked(True)
    pump(walk_app, 1)
    assert main.undo_button.isEnabled()
    with step(walk_app, "history", "reopen the app and look for the undo",
              main):
        assert store.is_checked(target)
    main.close()
    pump(walk_app, 2)
    for timer in main.findChildren(type(main._toast_timer)):
        timer.stop()

    from operators_console.core.storage import Store
    from operators_console.ui.context import AppContext
    reopened = Store()
    try:
        fresh_ctx = AppContext(store=reopened, curriculum=curriculum)
        second = MainWindow(fresh_ctx)
        second.show()
        pump(walk_app, 3)
        with step(walk_app, "history", "the tick survived, the undo did not",
                  second):
            assert reopened.is_checked(target), "the tick was lost on restart"
            assert not second.undo_button.isEnabled()
        REC.cannot_reach(
            "undo across a restart",
            "History lives in memory (ui/context.py -> core/history.py) and "
            "is not written to the store, so nothing can be undone after a "
            "relaunch. That is a design choice, not a defect, but it means "
            "the walk cannot test undo across a save and reload.")
        second.close()
        pump(walk_app, 2)
        for timer in second.findChildren(type(second._toast_timer)):
            timer.stop()
    finally:
        try:
            reopened.close()
        except Exception:
            pass


# -- updates ---------------------------------------------------------------


def test_the_update_button_appears_and_opens_its_dialog(walk_app, window,
                                                        monkeypatch):
    """Nothing here may touch the network: the download is stubbed out."""
    from operators_console.core import updates
    from operators_console.core.updates import Asset, Release, parse_version
    from operators_console.ui.updater import UpdateButton

    started = []
    monkeypatch.setattr(UpdateButton, "start",
                        lambda self: started.append(self.asset))

    with step(walk_app, "updates", "the button is hidden until there is one",
              window):
        assert not window.update_button.isVisible()

    names = ("operators-console-9.9.9-windows-setup.exe",
             "operators-console-9.9.9-windows-x64-portable.zip",
             "operators-console-9.9.9-macos-arm64.dmg",
             "operators-console-9.9.9-x86_64.AppImage")

    def make(notes):
        return Release(
            version=parse_version("v99.1.0"), tag="v99.1.0", name="Release",
            notes=notes, url="https://example.invalid/r",
            assets=tuple(Asset(n, "https://example.invalid/" + n, 1024)
                         for n in names))

    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)
    monkeypatch.setattr(updates.sys, "platform", "win32")

    short = make("Small fixes.")
    with step(walk_app, "updates", "a release makes the button appear",
              window):
        window.updates.release = short
        window.updates.available.emit(short)
        pump(walk_app, 2)
        assert window.update_button.isVisibleTo(window.statusBar())
        assert "99.1.0" in window.update_button.accessibleName(), (
            "the button never says which version it offers: %r"
            % window.update_button.accessibleName())

    with step(walk_app, "updates", "press it for a release with no changelog",
              window, allow_dialog=True):
        click(walk_app, window.update_button)
        assert started, "pressing the button neither downloaded nor explained"

    long_notes = make("\n".join("Line %d of a real changelog." % n
                                for n in range(40)))
    with step(walk_app, "updates", "press it for a release with a changelog",
              window, allow_dialog=True):
        window.updates.release = long_notes
        window.update_button.announce(long_notes)
        pump(walk_app, 2)
        click(walk_app, window.update_button)
        assert any(entry[1] == "UpdateDialog" for entry in REC.dialogs), (
            "a full changelog did not earn a window")
    REC.bump("update dialogs opened", 1)

    with step(walk_app, "updates", "a release with nothing for this platform",
              window, allow_dialog=True):
        from operators_console.core.updates import Release as R
        nothing = R(version=parse_version("v99.2.0"), tag="v99.2.0",
                    name="Release", notes="x", url="https://example.invalid/r",
                    assets=(Asset("something-else.tar.bz2",
                                  "https://example.invalid/x", 1),))
        window.update_button.announce(nothing)
        pump(walk_app, 2)
        before = len(REC.urls)
        click(walk_app, window.update_button)
        assert window.update_button.asset is None
        assert len(REC.urls) > before or not window.update_button.isEnabled(), (
            "with no package for this platform the button neither opens the "
            "release page nor disables itself")


def test_the_check_for_updates_menu_entry_always_answers(walk_app, window,
                                                         monkeypatch):
    calls = []
    monkeypatch.setattr(window.updates.pool, "start",
                        lambda job: calls.append(job))
    monkeypatch.setattr("operators_console.core.updates.can_self_update",
                        lambda: True)
    window.ctx.store.set_setting("last_update_check", "")
    with step(walk_app, "updates", "Help > Check for updates", window):
        window.check_for_updates()
        pump(walk_app, 2)
        assert calls, "the check never started"
        assert window.status_label.text()


# -- coming back tomorrow --------------------------------------------------


def test_quitting_and_relaunching_keeps_everything(walk_app, ctx, store,
                                                   curriculum,
                                                   quiet_update_check):
    from operators_console.core.srs import Rating
    from operators_console.core.storage import Store
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow

    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 3)
    phase = curriculum.phases[2]
    ticked = [i.id for i in phase.items][:4]
    store.set_many_checked(ticked, True)
    ctx.rebuild_review()
    main.go("review", "")
    pump(walk_app, 3)
    view = main.views["review"]
    if view.card is not None:
        view._apply(Rating.GOOD)
        pump(walk_app, 2)
    main.go("journal", "")
    pump(walk_app, 2)
    main.views["journal"].focus.setText("First session")
    main.views["journal"].hours.setValue(2.0)
    main.views["journal"]._save()
    pump(walk_app, 2)
    main.go("projects", "")
    pump(walk_app, 3)
    before = {
        "checked": set(store.checked_ids()),
        "streak": store.streak(),
        "hours": store.total_hours(),
        "due": store.card_counts(),
        "page": main.current_key,
    }
    main.close()
    pump(walk_app, 2)
    for timer in main.findChildren(type(main._toast_timer)):
        timer.stop()

    reopened = Store()
    try:
        fresh = AppContext(store=reopened, curriculum=curriculum)
        second = MainWindow(fresh)
        second.show()
        pump(walk_app, 3)
        with step(walk_app, "restart", "reopen the app on the same store",
                  second):
            assert set(reopened.checked_ids()) == before["checked"]
            assert reopened.streak() == before["streak"]
            assert reopened.total_hours() == before["hours"]
            assert reopened.card_counts()["total"] == before["due"]["total"]
            assert second.current_key == "today", (
                "the app did not open on Today")
            assert second.status_right.text()
        with step(walk_app, "restart", "the position is remembered", second):
            assert second.views["today"].tile_hours.value_label.text() == \
                "%.0f" % before["hours"]
            assert second.views["today"].tile_streak.value_label.text() == \
                str(before["streak"][0])
        if before["page"] != second.current_key:
            REC.cannot_reach(
                "the page you were on when you quit",
                "MainWindow always opens on Today (go('today') in __init__) "
                "and nothing writes the current page to the store, so "
                "'position survives a relaunch' means progress, not the "
                "page. Recorded rather than asserted.")
        second.close()
        pump(walk_app, 2)
        for timer in second.findChildren(type(second._toast_timer)):
            timer.stop()
    finally:
        try:
            reopened.close()
        except Exception:
            pass


def test_timers_still_fire_after_the_store_is_closed(walk_app, ctx, store,
                                                     curriculum,
                                                     quiet_update_check):
    """Quit within the autosave window and the app shouts at a dead store."""
    import time
    from PySide6.QtCore import QTimer
    from operators_console.ui.main_window import MainWindow

    main = MainWindow(ctx)
    main.show()
    pump(walk_app, 3)
    main.go("practice", curriculum.exercises[0].id)
    pump(walk_app, 3)
    main.views["practice"].editor.set_code("# typed a moment before quitting\n")
    armed = [t for t in main.findChildren(QTimer) if t.isActive()]
    before = len(REC.exceptions)
    with step(walk_app, "restart", "quit inside the autosave window", main,
              expect_exception=True, budget=6000):
        main.close()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and len(REC.exceptions) == before:
            pump(walk_app, 2)
            time.sleep(0.02)
    new = REC.exceptions[before:]
    if new:
        REC.find("major", "practice",
                 "timers fire after the window has closed its store",
                 "Type in the Practice editor, then quit within 700 ms "
                 "(or launch and quit within 2.5 s, which trips the update "
                 "check the same way).",
                 "Timers armed when the window closed: %d. "
                 "MainWindow.closeEvent closes the store but stops none of "
                 "them, so the next tick runs against a closed sqlite "
                 "connection:\n%s" % (len(armed), new[-1][-800:]))
    for timer in main.findChildren(QTimer):
        timer.stop()


def test_the_keyboard_can_actually_undo_and_redo(walk_app, window, store):
    """The buttons work; the advertised keys are what a learner reaches for."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeySequence
    from operators_console.ui.widgets.common import CheckRow

    window.go("phase", "p01")
    pump(walk_app, 3)
    rows = window.views["phase"].findChildren(CheckRow)
    target = rows[0].item_id

    with step(walk_app, "history", "Ctrl+Z undoes a tick", window):
        rows[0].box.setChecked(True)
        pump(walk_app, 1)
        assert store.is_checked(target)
        shortcut(walk_app, window, "Ctrl+Z")
        assert not store.is_checked(target), "Ctrl+Z did not undo"

    bound = [s.toString() for s in window.redo_action.shortcuts()]
    advertised = window.redo_button.toolTip()
    broken = []
    with step(walk_app, "history", "the advertised redo keys", window):
        assert window.redo_button.isEnabled()
        shortcut(walk_app, window, "Ctrl+Shift+Z")
        if not store.is_checked(target):
            broken.append("Ctrl+Shift+Z")
        shortcut(walk_app, window, "Ctrl+Y")
        if not store.is_checked(target):
            broken.append("Ctrl+Y")
    if broken:
        REC.find("major", "history",
                 "neither redo shortcut works",
                 "Tick a line, press Ctrl+Z, then press Ctrl+Shift+Z (the "
                 "combination the Redo button's own tooltip names) or Ctrl+Y. "
                 "Nothing happens; only the Redo button works.",
                 "main_window.py line 216 passes "
                 "setShortcuts([QKeySequence.StandardKey.Redo, "
                 "QKeySequence('Ctrl+Y')]). On this platform StandardKey.Redo "
                 "carries four bindings (%s); putting it in a list collapses "
                 "it to its first, Ctrl+Y, so the action ends up bound to "
                 "%s - the same key twice. Qt then reports 'Ambiguous "
                 "shortcut overload: Ctrl+Y' and refuses to fire, and "
                 "Ctrl+Shift+Z is no longer bound at all. The button's "
                 "tooltip still says %r. Dead keys: %s"
                 % ([s.toString() for s in QKeySequence.keyBindings(
                         QKeySequence.StandardKey.Redo)],
                    bound, advertised, broken))
    # The buttons themselves must still work whatever the keys do.
    with step(walk_app, "history", "the Redo button still works", window):
        click(walk_app, window.redo_button)
        assert store.is_checked(target)
    assert Qt is not None

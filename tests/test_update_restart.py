"""The last step of an update: the app goes away and comes back, and nothing else.

Two findings from 2026-09-22 are pinned here.

* On Windows a running program can be renamed but never overwritten. The
  helper used to run from the very folder the installer overwrites, so an
  installed build's update could not replace its own executable - the
  installer failed and the old version reopened, every time. The helper now
  runs from a copy in the staging folder.
* Inno Setup's /SILENT still shows its progress window. /VERYSILENT does not.

And the app reopens on the page the learner was on.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from conftest import pump

from operators_console.core import updates

ROOT = Path(__file__).resolve().parent.parent


def _frozen_build(folder: Path) -> Path:
    """The shape PyInstaller leaves: an executable and its _internal folder."""
    (folder / "_internal" / "PySide6").mkdir(parents=True)
    (folder / "_internal" / "shiboken6").mkdir()
    (folder / "_internal" / "python314.dll").write_bytes(b"python")
    (folder / "_internal" / "PySide6" / "Qt6Core.dll").write_bytes(b"qt" * 64)
    (folder / "_internal" / "shiboken6" / "shiboken6.pyd").write_bytes(b"s")
    (folder / "unins000.exe").write_bytes(b"uninstaller")
    exe = folder / "operators-console.exe"
    exe.write_bytes(b"bootloader")
    return exe


def _pretend_frozen(monkeypatch, exe: Path) -> None:
    monkeypatch.setattr(updates.sys, "platform", "win32")
    monkeypatch.setattr(updates.sys, "frozen", True, raising=False)
    monkeypatch.setattr(updates.sys, "executable", str(exe))


def _launched(monkeypatch) -> dict:
    seen = {}
    monkeypatch.setattr(updates, "_detached", lambda argv: seen.update(argv=argv))
    return seen


# ---------------------------------------------------------------------------
# where the helper runs from
# ---------------------------------------------------------------------------

def test_a_frozen_windows_helper_runs_from_outside_the_build(tmp_path,
                                                            monkeypatch):
    app = tmp_path / "Programs" / "Operator's Console"
    exe = _frozen_build(app)
    _pretend_frozen(monkeypatch, exe)
    seen = _launched(monkeypatch)
    package = updates.staging_dir() / "setup.exe"
    package.write_bytes(b"installer")

    updates.launch_helper(package)

    helper = Path(seen["argv"][0])
    assert helper.name == "operators-console.exe"
    assert not helper.resolve().is_relative_to(app.resolve()), (
        "the helper runs from the folder the installer must overwrite")
    assert helper.resolve().is_relative_to(updates.staging_dir().resolve())
    assert helper.read_bytes() == b"bootloader"
    assert (helper.parent / "_internal" / "python314.dll").exists()
    # The target is still the real installation, not the copy.
    target = seen["argv"][seen["argv"].index("--target") + 1]
    assert Path(target).resolve() == app.resolve()


def test_the_helper_copy_leaves_qt_and_the_uninstaller_behind(tmp_path,
                                                             monkeypatch):
    exe = _frozen_build(tmp_path / "app")
    _pretend_frozen(monkeypatch, exe)
    seen = _launched(monkeypatch)
    updates.launch_helper(tmp_path / "setup.exe")

    copy = Path(seen["argv"][0]).parent
    assert not (copy / "_internal" / "PySide6").exists()
    assert not (copy / "_internal" / "shiboken6").exists()
    assert not (copy / "unins000.exe").exists()


def test_a_failed_copy_falls_back_to_running_in_place(tmp_path, monkeypatch):
    exe = _frozen_build(tmp_path / "app")
    _pretend_frozen(monkeypatch, exe)
    seen = _launched(monkeypatch)

    def refuse(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(updates.shutil, "copytree", refuse)
    updates.launch_helper(tmp_path / "setup.exe")
    assert seen["argv"][0] == str(exe)
    assert "could not copy the helper" in (
        updates.paths.data_dir() / "update.log").read_text(encoding="utf-8")


def test_running_from_source_starts_python_itself(tmp_path, monkeypatch):
    monkeypatch.delattr(updates.sys, "frozen", raising=False)
    seen = _launched(monkeypatch)
    updates.launch_helper(tmp_path / "pkg.zip")
    assert seen["argv"][:3] == [sys.executable, "-m", "operators_console"]


def test_old_helper_copies_are_cleared_and_a_fresh_one_is_kept():
    staging = updates.staging_dir()
    old = staging / (updates.HELPER_PREFIX + "111")
    fresh = staging / (updates.HELPER_PREFIX + "222")
    for folder in (old, fresh):
        (folder / "_internal").mkdir(parents=True)
        (folder / "operators-console.exe").write_bytes(b"x")
    an_hour_ago = time.time() - 3600
    os.utime(old, (an_hour_ago, an_hour_ago))

    updates.tidy_staging()

    assert not old.exists()
    assert fresh.exists(), "a helper that may still be running was deleted"


def test_the_helper_never_loads_qt(tmp_path):
    """The copy leaves Qt out, which is only safe while this stays true.

    Runs the real helper entry point in a clean interpreter against a real
    portable swap, then asks which modules it imported.
    """
    script = textwrap.dedent("""
        import hashlib, sys, zipfile
        from pathlib import Path
        from operators_console.core import updates
        import operators_console.__main__ as entry

        root = Path(sys.argv[1])
        app = root / "app"
        app.mkdir()
        (app / "operators-console.exe").write_bytes(b"old")
        package = root / "operators-console-9.9.9-windows-portable.zip"
        with zipfile.ZipFile(package, "w") as zf:
            zf.writestr("operators-console/operators-console.exe", "new")
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        updates._detached = lambda argv: None
        updates._wait_for_exit = lambda *a, **k: None
        code = entry.main([updates.APPLY_FLAG, str(package), "--pid", "1",
                           "--kind", "portable", "--target", str(app),
                           "--sha256", digest])
        assert code == 0, code
        assert (app / "operators-console.exe").read_text() == "new"
        qt = sorted(m for m in sys.modules
                    if m.split(".")[0] in ("PySide6", "shiboken6"))
        print("QT=" + ",".join(qt))
    """)
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"),
               OPERATORS_CONSOLE_HOME=str(tmp_path / "home"))
    result = subprocess.run([sys.executable, "-c", script, str(tmp_path)],
                            capture_output=True, text=True, env=env,
                            timeout=120)
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip() == "QT=", result.stdout


# ---------------------------------------------------------------------------
# the installer
# ---------------------------------------------------------------------------

def test_the_installer_runs_very_silently_and_logs(tmp_path, monkeypatch):
    seen = {}

    def fake_run(argv, **kwargs):
        seen["argv"] = argv
        seen["kwargs"] = kwargs
    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    updates._apply_windows_installer(tmp_path / "setup.exe", tmp_path)

    argv = seen["argv"]
    assert "/VERYSILENT" in argv
    assert "/SILENT" not in argv, "/SILENT shows Inno Setup's progress window"
    assert "/SUPPRESSMSGBOXES" in argv and "/NORESTART" in argv
    log = [a for a in argv if a.startswith("/LOG=")]
    assert log and Path(log[0][5:]).parent == updates.staging_dir()
    assert seen["kwargs"].get("check") is True


def _installer_script() -> str:
    return (ROOT / "packaging" / "windows" / "installer.iss").read_text(
        encoding="utf-8")


def _section(script: str, name: str) -> list[str]:
    """The non-comment lines of one [Section] of an Inno Setup script."""
    lines, inside = [], False
    for raw in script.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            inside = line.lower() == "[%s]" % name.lower()
            continue
        if inside and line and not line.startswith(";"):
            lines.append(line)
    return lines


def test_the_installer_relaunches_only_on_a_silent_run_without_norelaunch():
    """Exactly one launch after a silent run, and a 1.1.0 helper switches it off.

    Builds before 1.1.0 run the installer from their own executable, so the
    installer has to close them and then reopen the app itself. A 1.1.0 or
    later helper reopens the app on its own and passes /NORELAUNCH, so the two
    can never both start a copy.
    """
    script = _installer_script()
    run = _section(script, "Run")
    silent = [line for line in run if "skipifsilent" not in line]
    assert len(silent) == 1, run
    assert "Check: RelaunchAfterUpdate" in silent[0]
    assert "postinstall" not in silent[0], "a silent run never shows a wizard"
    # The ordinary finish-page tick box still exists for an interactive run.
    assert any("postinstall" in line and "skipifsilent" in line
               for line in run), run

    code = script.split("[Code]", 1)[1]
    body = code.split("function RelaunchAfterUpdate", 1)[1].split("end;", 1)[0]
    squeezed = " ".join(body.split())
    assert "Result := WizardSilent and not CmdLineHas('/NORELAUNCH');" \
        in squeezed, body


def test_the_in_app_helper_tells_the_installer_not_to_relaunch(tmp_path,
                                                              monkeypatch):
    seen = {}
    monkeypatch.setattr(updates.subprocess, "run",
                        lambda argv, **kwargs: seen.setdefault("argv", argv))
    updates._apply_windows_installer(tmp_path / "setup.exe", tmp_path)
    assert "/NORELAUNCH" in seen["argv"]


def test_the_installer_can_close_an_old_build_that_is_running_it():
    """What lets a 1.0.x build update at all: its helper holds the exe open.

    Proven on real installs with packaging/windows/check_old_build_update.py.
    Without "force" the Restart Manager asks nicely, the windowless helper
    never answers, and a silent run aborts with exit code 5.
    """
    setup = {}
    for line in _section(_installer_script(), "Setup"):
        name, _, value = line.partition("=")
        setup[name.strip().lower()] = value.strip()
    assert setup.get("closeapplications") == "force"
    patterns = [p.strip().lower()
                for p in setup.get("closeapplicationsfilter", "").split(",")]
    for pattern in ("*.exe", "*.dll", "*.pyd"):
        assert pattern in patterns, patterns
    # Windows must not reopen what it closed: the [Run] entry does that once.
    assert setup.get("restartapplications") == "no"
    assert setup.get("setuplogging") == "yes"


# ---------------------------------------------------------------------------
# coming back to the same page
# ---------------------------------------------------------------------------

def _new_window(ctx):
    from operators_console.ui.main_window import MainWindow
    return MainWindow(ctx)


def _destroy(qt_app, window):
    from PySide6.QtCore import QCoreApplication, QEvent
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qt_app.processEvents()


def test_the_restarted_app_opens_on_the_exercise_the_learner_had_open(
        qt_app, window, curriculum):
    exercise = curriculum.exercises[5]
    window.go("practice", exercise.id)
    pump(qt_app)
    window.remember_place()

    again = _new_window(window.ctx)
    try:
        assert again.current_key == "practice"
        assert again.views["practice"].current.id == exercise.id
        assert not window.ctx.store.setting("resume_after_update")
    finally:
        _destroy(qt_app, again)


def test_the_restarted_app_opens_on_the_phase_the_learner_was_reading(
        qt_app, window, curriculum):
    phase = curriculum.phases[3]
    window.go("phase", phase.id)
    pump(qt_app)
    window.remember_place()
    window.go("today")

    window._resume_after_update()
    assert window.current_key == "phase"
    assert window.views["phase"].current_id == phase.id


def test_the_bookmark_is_used_once(qt_app, window):
    window.go("stats")
    window.remember_place()
    window._resume_after_update()
    window.go("today")
    window._resume_after_update()
    assert window.current_key == "today"


def test_a_stale_bookmark_does_not_hijack_a_normal_launch(qt_app, window):
    window.ctx.store.set_setting("resume_after_update", {
        "key": "stats", "target": "", "at": time.time() - 3 * 3600})
    window._resume_after_update()
    assert window.current_key == "today"
    assert not window.ctx.store.setting("resume_after_update")


def test_a_garbled_bookmark_is_ignored(qt_app, window):
    for junk in ("stats", ["stats"], {"key": "nowhere", "at": time.time()},
                 {"key": "stats", "at": "yesterday"}):
        window.ctx.store.set_setting("resume_after_update", junk)
        window._resume_after_update()
        assert window.current_key == "today", junk


def test_pressing_update_remembers_the_page_before_quitting(qt_app, window,
                                                            monkeypatch):
    from operators_console.ui import updater

    quits = []

    class App:
        @staticmethod
        def instance():
            return App

        @staticmethod
        def quit():
            quits.append(1)

    monkeypatch.setattr(updater, "_hand_over", lambda package: None)
    monkeypatch.setattr(updater, "QApplication", App)
    window.go("roadmap")
    pump(qt_app)
    store = window.ctx.store
    remembered = {}
    real = store.set_setting

    def spy(key, value):
        if key == "resume_after_update":
            remembered.update(value or {})
        real(key, value)
    monkeypatch.setattr(store, "set_setting", spy)

    window.update_button.package = Path("setup.exe")
    window.update_button._restart()

    assert remembered.get("key") == "roadmap"
    assert quits == [1]


# ---------------------------------------------------------------------------
# the skeptic pass, 2026-09-22
# ---------------------------------------------------------------------------

def test_the_helper_copy_never_copies_the_data_folder(tmp_path, monkeypatch):
    """A portable install that keeps its data inside its own folder: the
    staging folder is inside the data folder, so copying it copied the copy
    until Python ran out of recursion."""
    app = tmp_path / "app"
    exe = _frozen_build(app)
    home = app / "data"
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))
    (home / "progress.db").parent.mkdir(parents=True, exist_ok=True)
    (home / "progress.db").write_bytes(b"the learner's work")
    helper = updates._stage_helper(app, exe.name)
    copy = helper.parent
    assert not (copy / "data").exists()
    assert not list(copy.rglob("progress.db"))


def test_a_portable_update_with_data_inside_says_why_before_quitting(
        tmp_path, monkeypatch):
    app = tmp_path / "app"
    exe = _frozen_build(app)
    (app / "unins000.exe").unlink()                 # portable, not installed
    _pretend_frozen(monkeypatch, exe)
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(app / "data"))
    seen = _launched(monkeypatch)
    with pytest.raises(OSError, match="inside the application folder"):
        updates.launch_helper(tmp_path / "pkg.zip")
    assert "argv" not in seen, "the app quit into a helper that would refuse"


def test_a_refused_package_waits_for_the_old_app_before_reopening_it(
        tmp_path, monkeypatch):
    order = []
    monkeypatch.setattr(updates, "_wait_for_exit",
                        lambda *a, **k: order.append("waited"))
    monkeypatch.setattr(updates, "_restart", lambda target: order.append("restarted"))
    package = tmp_path / "pkg.zip"
    package.write_bytes(b"tampered")
    code = updates.apply_update(package, 1, updates.PORTABLE, tmp_path, "0" * 64)
    assert code == 2
    assert order == ["waited", "restarted"]
    assert "checksum" in updates.take_failure()


def test_a_rolled_back_swap_removes_what_the_new_build_added(tmp_path,
                                                            monkeypatch):
    import zipfile
    target = tmp_path / "app"
    target.mkdir()
    (target / "a.txt").write_text("old a", encoding="utf-8")
    package = tmp_path / "update.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("a.txt", "new a")
        archive.writestr("b_added.txt", "only in the new build")
        archive.writestr("c.txt", "new c")
    real_move = updates.shutil.move

    def flaky(src, dst):
        if Path(dst).name == "c.txt":
            raise OSError("disk full half way through the swap")
        return real_move(src, dst)
    monkeypatch.setattr(updates.shutil, "move", flaky)
    with pytest.raises(OSError):
        updates._apply_archive(package, target)
    assert sorted(p.name for p in target.iterdir()) == ["a.txt"]
    assert (target / "a.txt").read_text(encoding="utf-8") == "old a"


def test_a_refused_rename_leaves_the_old_build_whole(tmp_path, monkeypatch):
    """Never copy-then-delete: a delete that cannot finish gutted _internal."""
    import zipfile
    target = tmp_path / "app"
    (target / "_internal").mkdir(parents=True)
    (target / "_internal" / "a.dll").write_bytes(b"old")
    (target / "operators-console.exe").write_bytes(b"old")
    package = tmp_path / "update.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("_internal/a.dll", "new")
        archive.writestr("operators-console.exe", "new")

    def refuse(src, dst):
        if Path(src).name == "_internal":
            raise PermissionError("a scanner holds a file in it")
        return real_replace(src, dst)
    real_replace = updates.os.replace
    monkeypatch.setattr(updates.os, "replace", refuse)
    monkeypatch.setattr(updates.time, "sleep", lambda s: None)
    with pytest.raises(OSError):
        updates._apply_archive(package, target)
    assert (target / "_internal" / "a.dll").read_bytes() == b"old"
    assert (target / "operators-console.exe").read_bytes() == b"old"


def test_a_redirect_off_https_means_no_offer_not_a_crash(monkeypatch):
    def redirected(url, timeout=None):
        raise updates.IntegrityError(updates.INSECURE_URL_MESSAGE % "http://x")
    monkeypatch.setattr(updates, "_request", redirected)
    assert updates.available() is None


def test_a_copy_of_the_offer_is_refused_in_words():
    with pytest.raises(ValueError, match="available"):
        updates._offered_asset({"asset": "operators-console-9.9.9.zip"})


# ---------------------------------------------------------------------------
# two copies reopened at once after an old build's update
# ---------------------------------------------------------------------------
#
# A 1.0.x build cannot pass /NORELAUNCH, so after it updates, the installer
# reopens the app and the old helper may reopen it too, milliseconds apart.
# Before the lock, both found nobody on the socket - the first copy did not
# listen until its window was built - and both opened on one database.

_CLAIMANT = textwrap.dedent("""
    import sys, time
    from pathlib import Path
    from PySide6.QtCore import QCoreApplication
    from operators_console import app

    key, lock, go, hold = sys.argv[1], sys.argv[2], Path(sys.argv[3]), float(sys.argv[4])
    qt = QCoreApplication([])
    deadline = time.monotonic() + 60
    while not go.exists() and time.monotonic() < deadline:
        time.sleep(0.002)
    raised = []
    claim = app.claim_instance(key, lock, lambda: raised.append(1))
    if claim is None:
        print("HANDED", flush=True)
        raise SystemExit(0)
    print("OWNER" if claim.lock is not None else "ALONE", flush=True)
    end = time.monotonic() + hold
    while time.monotonic() < end:
        qt.processEvents()
        time.sleep(0.01)
    claim.release()
    print("RAISED=%d" % len(raised), flush=True)
""")


def _claimant(tmp_path, go: Path, hold: float = 6.0):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"),
               OPERATORS_CONSOLE_HOME=str(tmp_path / "home"),
               QT_QPA_PLATFORM="offscreen")
    key = "operators-console-test-%d-%s" % (os.getpid(), tmp_path.name[-12:])
    return subprocess.Popen(
        [sys.executable, "-c", _CLAIMANT, key, str(tmp_path / "instance.lock"),
         str(go), str(hold)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


@pytest.mark.parametrize("gap", [0.0, 1.5])
def test_a_second_copy_started_with_the_first_hands_over(tmp_path, gap):
    """Released together, or seconds apart: one copy opens, the other leaves."""
    go_first, go_second = tmp_path / "go-1", tmp_path / "go-2"
    first = _claimant(tmp_path, go_first)
    second = _claimant(tmp_path, go_second)
    try:
        time.sleep(1.0)             # let both finish importing Qt
        go_first.touch()
        if gap:
            time.sleep(gap)
        go_second.touch()
        outputs = [p.communicate(timeout=60) for p in (first, second)]
    finally:
        for process in (first, second):
            if process.poll() is None:
                process.kill()
    said = [out.split() for out, _err in outputs]
    verdicts = sorted(words[0] for words in said if words)
    assert verdicts == ["HANDED", "OWNER"], outputs
    owner = next(words for words in said if words[0] == "OWNER")
    assert owner[-1] == "RAISED=1", "the copy that opened was not asked forward"


def test_the_lock_of_a_copy_that_crashed_does_not_block_the_next(tmp_path,
                                                                 qt_app):
    lock = tmp_path / "instance.lock"
    crashed = textwrap.dedent("""
        import os, sys
        from PySide6.QtCore import QLockFile
        held = QLockFile(sys.argv[1])
        held.setStaleLockTime(0)
        assert held.tryLock(0)
        os._exit(0)                 # no unlock: the file stays behind
    """)
    subprocess.run([sys.executable, "-c", crashed, str(lock)], check=True,
                   timeout=60)
    assert lock.exists()

    from operators_console import app
    key = "operators-console-test-crash-%d" % os.getpid()
    started = time.monotonic()
    claim = app.claim_instance(key, lock, lambda: None, wait_s=5)
    try:
        assert claim is not None and claim.lock is not None
        assert time.monotonic() - started < 3, "waited on a dead copy's lock"
    finally:
        if claim is not None:
            claim.release()

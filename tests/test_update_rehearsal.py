"""Updating, rehearsed end to end against real files.

The claim under test is the one the app makes to the learner on the update
button: "Your progress is untouched." These tests actually build an
installation, write a store into it with one version of the code, run the
swap, and reopen the store - rather than asserting that a path string looks
about right.

The three platform shapes are exercised where they can be: the archive swap
runs for real, the macOS bundle and the Windows installer hand-off run
against stand-ins, because attaching a disk image or running a setup binary
is not something a test can do on the wrong operating system.
"""
from __future__ import annotations

import hashlib
import json
import zipfile

import pytest

from operators_console.core import paths, updates
from operators_console.core.storage import Store


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_1_0_0_store(home):
    """A store written the way version 1.0.0 would have left it."""
    store = Store()
    store.set_checked("p01.s0.0", True)
    store.set_checked("p01.s0.1", True)
    store.set_setting("learner_name", "Sam")
    store.set_setting("track", "backend")
    store.set_rating("loops", 3)
    store.add_log("2026-01-01", "Generators", 2.5, "built", "stuck", "next")
    store.record_exercise_run("p01.001", "print('hi')", passed=True)
    store.set_project("p01.proj", status="in-progress")
    fingerprint = json.dumps(store.dump()["tables"], sort_keys=True)
    store.close()
    return fingerprint


def portable_build(folder, marker):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "operators-console").write_text(marker, encoding="utf-8")
    (folder / "PySide6").mkdir(exist_ok=True)
    (folder / "PySide6" / "QtCore.dll").write_text(marker, encoding="utf-8")
    return folder


def package_for(tmp_path, marker, name="update.zip"):
    package = tmp_path / name
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("operators-console/operators-console", marker)
        archive.writestr("operators-console/PySide6/QtCore.dll", marker)
        archive.writestr("operators-console/NEW-FILE.txt", marker)
    return package


# ---------------------------------------------------------------------------
# the promise
# ---------------------------------------------------------------------------

def test_a_portable_update_leaves_a_1_0_0_store_byte_for_byte(tmp_path,
                                                              monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))
    before = build_1_0_0_store(home)

    app = portable_build(tmp_path / "app", "1.0.0")
    stale = app / "OLD-FILE.txt"
    stale.write_text("left over", encoding="utf-8")

    updates._apply_archive(package_for(tmp_path, "1.1.0"), app)

    assert (app / "operators-console").read_text(encoding="utf-8") == "1.1.0"
    assert (app / "PySide6" / "QtCore.dll").read_text(encoding="utf-8") == "1.1.0"
    assert (app / "NEW-FILE.txt").exists()

    reopened = Store()
    try:
        after = json.dumps(reopened.dump()["tables"], sort_keys=True)
        assert after == before, "the update changed the learner's data"
        assert reopened.is_checked("p01.s0.0")
        assert reopened.setting("learner_name") == "Sam"
        assert reopened.total_hours() == 2.5
        assert reopened.project("p01.proj")["status"] == "in-progress"
    finally:
        reopened.close()


def test_updating_twice_in_a_row_is_still_safe(tmp_path, monkeypatch):
    """Re-running an install on a machine that already has it."""
    home = tmp_path / "home"
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))
    before = build_1_0_0_store(home)
    app = portable_build(tmp_path / "app", "1.0.0")

    for version in ("1.1.0", "1.2.0", "1.2.0"):
        updates._apply_archive(
            package_for(tmp_path, version, "u-%s.zip" % version), app)
        assert (app / "operators-console").read_text(encoding="utf-8") == version

    reopened = Store()
    try:
        assert json.dumps(reopened.dump()["tables"], sort_keys=True) == before
    finally:
        reopened.close()


def test_no_rollback_folder_is_left_behind(tmp_path, monkeypatch):
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    app = portable_build(tmp_path / "app", "1.0.0")
    updates._apply_archive(package_for(tmp_path, "1.1.0"), app)
    assert not (app / ".opcon-previous").exists()


def test_the_data_directory_is_never_inside_the_application_directory():
    """The structural reason an update is safe at all."""
    assert not paths.data_dir().resolve().is_relative_to(
        updates.app_root().resolve())


@pytest.mark.parametrize("home_inside", ["", "data", "nested/deeper"])
def test_progress_stored_inside_the_app_folder_stops_the_update(
        tmp_path, monkeypatch, home_inside):
    app = tmp_path / "app"
    app.mkdir()
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME",
                       str(app / home_inside) if home_inside else str(app))
    with pytest.raises(OSError, match="would delete your data"):
        updates._apply_archive(package_for(tmp_path, "1.1.0"), app)


# ---------------------------------------------------------------------------
# the handover, start to finish
# ---------------------------------------------------------------------------

def test_the_whole_handover_verifies_then_swaps_then_relaunches(
        tmp_path, monkeypatch):
    """available() -> download_update() -> apply_and_restart() -> helper."""
    home = tmp_path / "home"
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))
    before = build_1_0_0_store(home)
    app = portable_build(tmp_path / "app", "1.0.0")

    package = package_for(tmp_path, "2.0.0")
    body = package.read_bytes()
    asset = updates.Asset("operators-console-linux-portable.zip",
                          "https://example.invalid/u.zip", len(body),
                          digest(body))

    class Response:
        headers = {}

        def __init__(self, data):
            self.data = data
            self.at = 0

        def read(self, size=-1):
            chunk = self.data[self.at:] if size < 0 else \
                self.data[self.at:self.at + size]
            self.at += len(chunk)
            return chunk

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    monkeypatch.setattr(updates, "_request", lambda url, timeout=None:
                        Response(body))

    staged = updates.download_update({"_asset": asset})
    assert staged.exists()
    assert updates._remembered_digest(staged) == digest(body)

    handover = {}
    monkeypatch.setattr(updates, "_detached",
                        lambda argv: handover.setdefault("argv", argv))
    monkeypatch.setattr(updates, "app_root", lambda: app)
    monkeypatch.setattr(updates, "install_kind", lambda: updates.PORTABLE)
    updates.apply_and_restart(staged)

    argv = handover["argv"]
    assert updates.APPLY_FLAG in argv
    assert digest(body) in argv

    # Now run what the helper would run.
    relaunched = {}
    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_detached",
                        lambda a: relaunched.setdefault("argv", a))
    code = updates.apply_update(staged, 999_999, updates.PORTABLE, app,
                                digest(body))

    assert code == 0
    assert (app / "operators-console").read_text(encoding="utf-8") == "2.0.0"
    assert relaunched["argv"], "the helper did not start the new build"
    assert not staged.exists(), "the package was left in the staging folder"
    assert not updates._digest_sidecar(staged).exists()

    reopened = Store()
    try:
        assert json.dumps(reopened.dump()["tables"], sort_keys=True) == before
    finally:
        reopened.close()


def test_a_failed_swap_restarts_the_old_build_rather_than_nothing(
        tmp_path, monkeypatch):
    app = portable_build(tmp_path / "app", "1.0.0")
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    package = tmp_path / "broken.zip"
    package.write_bytes(b"not a zip at all")

    started = []
    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_detached", lambda argv: started.append(argv))

    code = updates.apply_update(package, 999_999, updates.PORTABLE, app,
                                digest(b"not a zip at all"))
    assert code == 1
    assert started, "the learner was left with nothing running"
    assert (app / "operators-console").read_text(encoding="utf-8") == "1.0.0"


# ---------------------------------------------------------------------------
# the other two platform shapes
# ---------------------------------------------------------------------------

def test_the_windows_installer_path_runs_the_setup_silently(tmp_path,
                                                            monkeypatch):
    """No console window, no prompts, no reboot."""
    package = tmp_path / "setup.exe"
    package.write_bytes(b"pretend installer")
    app = portable_build(tmp_path / "app", "1.0.0")
    seen = {}

    def fake_run(argv, **kwargs):
        seen["argv"] = argv
        seen["kwargs"] = kwargs

        class Done:
            returncode = 0
        return Done()

    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    updates._apply_windows_installer(package, app)
    assert seen["argv"][0] == str(package)
    # /VERYSILENT: /SILENT would still show Inno Setup's progress window.
    for flag in ("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"):
        assert flag in seen["argv"]
    assert "/SILENT" not in seen["argv"]
    assert seen["kwargs"].get("check") is True
    assert "creationflags" in seen["kwargs"]


def test_the_macos_bundle_is_staged_then_swapped(tmp_path, monkeypatch):
    """A half-copied .app must never become the installed one."""
    holder = tmp_path / "Applications"
    bundle = holder / "Operator's Console.app"
    (bundle / "Contents" / "MacOS").mkdir(parents=True)
    (bundle / "Contents" / "MacOS" / "operators-console").write_text(
        "1.0.0", encoding="utf-8")
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))

    mount = tmp_path / "mount"

    def fake_run(argv, **kwargs):
        if argv[0] == "hdiutil" and argv[1] == "attach":
            target = tmp_path / "mount"
            fresh = target / "Operator's Console.app"
            (fresh / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)
            (fresh / "Contents" / "MacOS" / "operators-console").write_text(
                "2.0.0", encoding="utf-8")

        class Done:
            returncode = 0
        return Done()

    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    monkeypatch.setattr(updates.tempfile, "mkdtemp",
                        lambda prefix="": str(mount))
    mount.mkdir(parents=True, exist_ok=True)

    package = tmp_path / "app.dmg"
    package.write_bytes(b"pretend image")
    executable = updates._apply_macos_dmg(package, bundle)

    assert executable.read_text(encoding="utf-8") == "2.0.0"
    assert not (holder / "Operator's Console.app.new").exists()
    assert not (holder / "Operator's Console.app.previous").exists()


def test_the_appimage_path_replaces_only_the_image(tmp_path, monkeypatch):
    program = tmp_path / "opt" / "operators-console"
    program.mkdir(parents=True)
    image = program / "operators-console.AppImage"
    image.write_bytes(b"1.0.0")

    store_dir = tmp_path / "share" / "operators-console"
    store_dir.mkdir(parents=True)
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(store_dir))
    monkeypatch.setenv("APPIMAGE", str(image))
    build_1_0_0_store(store_dir)
    kept = sorted(p.name for p in store_dir.iterdir())

    package = tmp_path / "new.AppImage"
    package.write_bytes(b"2.0.0")
    updates._apply_appimage(package, program)

    assert image.read_bytes() == b"2.0.0"
    assert sorted(p.name for p in store_dir.iterdir()) == kept
    assert not (program / "operators-console.AppImage.previous").exists()


# ---------------------------------------------------------------------------
# the exact call sequence the update button uses
# ---------------------------------------------------------------------------

def test_the_interfaces_own_call_sequence_works_unchanged(tmp_path,
                                                          monkeypatch):
    """available() -> pick_asset() -> download() -> apply_and_restart().

    The update button reads an offer as an object and downloads the asset
    itself rather than going through download_update(). That path has to
    verify and hand the digest on just as the packaged one does, or the
    helper refuses the package the button just checked.
    """
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    app = portable_build(tmp_path / "app", "1.0.0")
    package = package_for(tmp_path, "3.0.0")
    body = package.read_bytes()

    payload = {
        "tag_name": "v99.0.0",
        "name": "Release 99",
        "body": "What changed.",
        "html_url": "https://example.invalid/r",
        "assets": [
            {"name": "operators-console-99-linux-portable.zip",
             "browser_download_url": "https://example.invalid/u.zip",
             "size": len(body)},
            {"name": "SHA256SUMS",
             "browser_download_url": "https://example.invalid/SHA256SUMS",
             "size": 90},
        ],
    }
    sums = ("%s  operators-console-99-linux-portable.zip\n"
            % digest(body)).encode()

    class Response:
        headers = {}

        def __init__(self, data):
            self.data, self.at = data, 0

        def read(self, size=-1):
            chunk = (self.data[self.at:] if size < 0
                     else self.data[self.at:self.at + size])
            self.at += len(chunk)
            return chunk

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    served = {
        updates.API % updates.REPO: json.dumps(payload).encode(),
        "https://example.invalid/SHA256SUMS": sums,
        "https://example.invalid/u.zip": body,
    }
    monkeypatch.setattr(updates, "_request",
                        lambda url, timeout=None: Response(served[url]))
    monkeypatch.setattr(updates.sys, "platform", "linux")
    monkeypatch.setattr(updates, "install_kind", lambda: updates.PORTABLE)
    monkeypatch.setattr(updates, "app_root", lambda: app)

    offer = updates.available()
    assert offer is not None
    assert offer.label == "99.0.0"          # read as an object
    assert offer["verified"] is True        # read as a mapping

    asset = updates.pick_asset(offer)
    seen = []
    staged = updates.download(
        asset, updates.staging_dir() / asset.name,
        progress=lambda done, total: seen.append((done, total)))
    assert seen and seen[-1][0] == len(body)

    handover = {}
    monkeypatch.setattr(updates, "_detached",
                        lambda argv: handover.setdefault("argv", argv))
    updates.apply_and_restart(staged)
    assert digest(body) in handover["argv"], (
        "the digest did not survive the handover")

    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_detached", lambda a: None)
    assert updates.apply_update(staged, 999_999, updates.PORTABLE, app) == 0
    assert (app / "operators-console").read_text(encoding="utf-8") == "3.0.0"

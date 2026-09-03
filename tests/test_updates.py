"""Update checking, asset selection and the helper handover.

Nothing here touches the network: the release payload is synthetic, because the
logic worth testing is which file gets picked and when the button appears.
"""
from __future__ import annotations

import json

import pytest

from operators_console.core import updates
from operators_console.core.updates import Asset, Release, parse_version


def make_release(tag="v9.9.9", names=()):
    return Release(
        version=parse_version(tag), tag=tag, name="Release " + tag,
        notes="notes", url="https://example.invalid/r",
        assets=tuple(Asset(n, "https://example.invalid/" + n, 1024)
                     for n in names))


ALL_ASSETS = (
    "operators-console-1.0.0-windows-setup.exe",
    "operators-console-1.0.0-windows-portable.zip",
    "operators-console-1.0.0-macos-arm64.dmg",
    "operators-console-1.0.0-macos-arm64-portable.zip",
    "operators-console-1.0.0-macos-x86_64.dmg",
    "operators-console-1.0.0-macos-x86_64-portable.zip",
    "operators-console-1.0.0-x86_64.AppImage",
    "operators-console-1.0.0-linux-portable.zip",
    "operators-console_1.0.0_amd64.deb",
)


@pytest.mark.parametrize("text,expected", [
    ("1.0.0", (1, 0, 0)),
    ("v1.2.3", (1, 2, 3)),
    ("v10.0.1-beta", (10, 0, 1)),
    ("", (0,)),
    ("nonsense", (0,)),
])
def test_versions_parse_into_comparable_tuples(text, expected):
    assert parse_version(text) == expected


def test_version_ordering_is_numeric_not_alphabetical():
    assert parse_version("v1.0.10") > parse_version("v1.0.9")
    assert parse_version("v2.0.0") > parse_version("v1.99.99")


def test_a_newer_release_is_offered():
    assert updates.is_newer(make_release("v99.0.0", ALL_ASSETS))


def test_the_same_or_older_release_is_not_offered():
    from operators_console.version import __version__
    assert not updates.is_newer(make_release("v" + __version__, ALL_ASSETS))
    assert not updates.is_newer(make_release("v0.0.1", ALL_ASSETS))
    assert not updates.is_newer(None)


@pytest.mark.parametrize("platform,kind,expected", [
    ("win32", updates.INSTALLED, "windows-setup.exe"),
    ("win32", updates.PORTABLE, "windows-portable.zip"),
    ("linux", updates.APPIMAGE, "x86_64.AppImage"),
    ("linux", updates.PORTABLE, "linux-portable.zip"),
])
def test_each_install_shape_picks_its_own_download(monkeypatch, platform, kind,
                                                   expected):
    monkeypatch.setattr(updates.sys, "platform", platform)
    asset = updates.pick_asset(make_release("v9.0.0", ALL_ASSETS), kind)
    assert asset is not None and asset.name.endswith(expected)


@pytest.mark.parametrize("machine,expected", [
    ("arm64", "macos-arm64.dmg"),
    ("aarch64", "macos-arm64.dmg"),
    ("x86_64", "macos-x86_64.dmg"),
])
def test_macos_never_offers_the_wrong_architecture(monkeypatch, machine,
                                                   expected):
    monkeypatch.setattr(updates.sys, "platform", "darwin")
    monkeypatch.setattr(updates.platform, "machine", lambda: machine)
    asset = updates.pick_asset(make_release("v9.0.0", ALL_ASSETS),
                               updates.MACAPP)
    assert asset is not None and asset.name.endswith(expected)


def test_a_release_without_a_matching_build_picks_nothing(monkeypatch):
    monkeypatch.setattr(updates.sys, "platform", "win32")
    release = make_release("v9.0.0", ("operators-console-1.0.0-macos-arm64.dmg",))
    assert updates.pick_asset(release, updates.INSTALLED) is None


@pytest.mark.parametrize("payload", [{"draft": True}, {"prerelease": True}])
def test_a_draft_or_prerelease_is_ignored(monkeypatch, payload):
    monkeypatch.setattr(updates, "_request",
                        lambda *_a, **_k: _FakeResponse(payload))
    assert updates.fetch_latest() is None


def test_a_release_with_no_assets_is_ignored(monkeypatch):
    monkeypatch.setattr(updates, "_request",
                        lambda *_a, **_k: _FakeResponse(
                            {"tag_name": "v9.0.0", "assets": []}))
    assert updates.fetch_latest() is None


def test_a_network_failure_is_silent(monkeypatch):
    def explode(*_args, **_kwargs):
        raise OSError("no route to host")
    monkeypatch.setattr(updates, "_request", explode)
    assert updates.fetch_latest() is None


def test_unreadable_json_is_silent(monkeypatch):
    monkeypatch.setattr(updates, "_request",
                        lambda *_a, **_k: _FakeResponse(raw=b"not json"))
    assert updates.fetch_latest() is None


def test_a_good_payload_parses(monkeypatch):
    payload = {
        "tag_name": "v2.5.0",
        "name": "Release 2.5.0",
        "body": "Adds undo.",
        "html_url": "https://example.invalid/releases/v2.5.0",
        "assets": [{"name": "operators-console-2.5.0-windows-setup.exe",
                    "browser_download_url": "https://example.invalid/a.exe",
                    "size": 5}],
    }
    monkeypatch.setattr(updates, "_request",
                        lambda *_a, **_k: _FakeResponse(payload))
    release = updates.fetch_latest()
    assert release is not None
    assert release.version == (2, 5, 0)
    assert release.label == "2.5.0"
    assert len(release.assets) == 1


def test_running_from_source_does_not_self_update():
    assert updates.install_kind() == updates.SOURCE
    assert not updates.can_self_update()


class _FakeResponse:
    def __init__(self, payload=None, raw=None):
        self._raw = raw if raw is not None else json.dumps(payload).encode()
        self.headers = {}

    def read(self, *_args):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


# ---------------------------------------------------------------------------
# an update must never cost the learner their progress
# ---------------------------------------------------------------------------

def test_progress_lives_outside_the_application_folder():
    """The reason an update is safe: the two directories are unrelated."""
    from operators_console.core import paths

    app = updates.app_root().resolve()
    data = paths.data_dir().resolve()
    assert data != app
    assert not data.is_relative_to(app)


def test_replacing_a_portable_build_keeps_every_file_of_progress(tmp_path,
                                                                 monkeypatch):
    """Swap an app folder for a new one and prove the database survives."""
    import zipfile

    from operators_console.core.storage import Store

    home = tmp_path / "home"
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))

    store = Store()
    store.set_checked("p01.s0.0", True)
    store.set_setting("learner_name", "Sam")
    store.add_log("2026-01-01", "Generators", 2.5, "built", "stuck", "next")
    store.close()

    app = tmp_path / "app"
    app.mkdir()
    (app / "operators-console").write_text("old build", encoding="utf-8")
    (app / "stale.dll").write_text("remove me", encoding="utf-8")

    package = tmp_path / "new.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("operators-console/operators-console", "new build")
        archive.writestr("operators-console/fresh.dll", "keep me")

    updates._apply_archive(package, app)

    assert (app / "operators-console").read_text(encoding="utf-8") == "new build"
    assert (app / "fresh.dll").exists()

    reopened = Store()
    try:
        assert reopened.is_checked("p01.s0.0")
        assert reopened.setting("learner_name") == "Sam"
        assert reopened.total_hours() == 2.5
    finally:
        reopened.close()


def test_an_update_refuses_to_run_if_it_would_delete_your_data(tmp_path,
                                                               monkeypatch):
    """A portable install with its data inside the app folder is protected."""
    app = tmp_path / "app"
    app.mkdir()
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(app / "data"))

    with pytest.raises(OSError, match="would delete your data"):
        updates._guard_user_data(app)


def test_a_normal_layout_passes_the_guard(tmp_path, monkeypatch):
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    updates._guard_user_data(tmp_path / "app")

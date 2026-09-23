"""The update path treated as hostile input.

An updater downloads a file and then runs it. Everything it decides - which
URL, which bytes, whether to execute them - comes from a JSON document
fetched over the network, so every one of those decisions is an input to be
checked rather than a fact to be trusted.

The trust root is GitHub and the owner of the repository. The checksum proves
the bytes are the ones that release published; it does not prove who
published them. That limit is documented in docs/AUDIT-core.md.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile

import pytest

from operators_console.core import updates
from operators_console.core.updates import (
    Asset, IntegrityError, Release, parse_sums, parse_version, sha256_file,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeResponse(io.BytesIO):
    def __init__(self, data: bytes, headers=None):
        super().__init__(data)
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def serve(mapping):
    """A _request stand-in that answers from a {url: bytes} map."""
    def fake(url, timeout=None):
        if url not in mapping:
            raise OSError("404 %s" % url)
        return FakeResponse(mapping[url])
    return fake


# ---------------------------------------------------------------------------
# transport
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://attacker.example/setup.exe",
    "ftp://attacker.example/setup.exe",
    "file:///C:/Windows/System32/calc.exe",
    "//attacker.example/setup.exe",
    "",
])
def test_a_non_https_asset_url_is_refused(url):
    """The asset list is remote JSON, so its URLs are input.

    Without this the app would fetch an attacker-named URL over plain HTTP,
    or off the local filesystem, and then execute it.
    """
    with pytest.raises(IntegrityError, match="insecure"):
        updates.secure_url(url)


def test_a_redirect_off_https_is_refused():
    """GitHub redirects assets to its CDN, so redirects cannot be banned.

    urllib follows an https -> http redirect by default, which would hand the
    whole download to anyone on the path. Only the downgrade is refused.
    """
    handler = updates._HttpsOnlyRedirects()
    with pytest.raises(IntegrityError):
        handler.redirect_request(None, None, 302, "Found", {},
                                 "http://attacker.example/x.exe")


def test_a_https_redirect_is_allowed(monkeypatch):
    handler = updates._HttpsOnlyRedirects()
    monkeypatch.setattr(
        "urllib.request.HTTPRedirectHandler.redirect_request",
        lambda *a, **k: "allowed")
    assert handler.redirect_request(
        None, None, 302, "Found", {},
        "https://objects.githubusercontent.com/x.exe") == "allowed"


# ---------------------------------------------------------------------------
# the manifest
# ---------------------------------------------------------------------------

def test_a_sha256sums_file_parses_in_both_shapes():
    text = ("%s  plain.zip\n"
            "%s *binary.exe\n"
            "\n"
            "# a comment\n"
            "not a checksum line\n"
            "deadbeef  too-short.zip\n" % ("a" * 64, "b" * 64))
    assert parse_sums(text) == {"plain.zip": "a" * 64,
                                "binary.exe": "b" * 64}


def test_the_digest_of_a_file_is_the_real_sha256(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"operator")
    assert sha256_file(path) == digest(b"operator")


def test_a_release_stamps_each_asset_with_its_published_digest(monkeypatch):
    body = b"a real installer"
    payload = {
        "tag_name": "v9.9.9",
        "assets": [
            {"name": "operators-console-windows-setup.exe",
             "browser_download_url": "https://example.invalid/setup.exe",
             "size": len(body)},
            {"name": "SHA256SUMS",
             "browser_download_url": "https://example.invalid/SHA256SUMS",
             "size": 80},
        ],
    }
    sums = ("%s  operators-console-windows-setup.exe\n"
            % digest(body)).encode()
    monkeypatch.setattr(updates, "_request", serve({
        updates.API % updates.REPO: json.dumps(payload).encode(),
        "https://example.invalid/SHA256SUMS": sums,
    }))
    release = updates.fetch_latest()
    assert release.verified
    assert release.asset("operators-console-windows-setup.exe").sha256 \
        == digest(body)


def test_a_release_without_a_manifest_is_marked_unverified(monkeypatch):
    payload = {
        "tag_name": "v9.9.9",
        "assets": [{"name": "operators-console-windows-setup.exe",
                    "browser_download_url": "https://example.invalid/s.exe",
                    "size": 4}],
    }
    monkeypatch.setattr(updates, "_request", serve({
        updates.API % updates.REPO: json.dumps(payload).encode()}))
    release = updates.fetch_latest()
    assert release is not None and not release.verified


def test_the_manifest_is_never_offered_as_the_download(monkeypatch):
    monkeypatch.setattr(updates.sys, "platform", "linux")
    release = Release(
        version=(9, 0, 0), tag="v9.0.0", name="n", notes="", url="",
        assets=(Asset("SHA256SUMS", "https://example.invalid/SHA256SUMS", 80),))
    assert updates.pick_asset(release, updates.APPIMAGE) is None


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------

def test_a_tampered_download_is_refused_and_discarded(monkeypatch, tmp_path):
    """The bytes on the wire are not the bytes the release published."""
    swapped = b"MZ this is not the installer you asked for"
    good = b"the real installer"
    asset = Asset("setup.exe", "https://example.invalid/setup.exe",
                  len(swapped), digest(good))
    monkeypatch.setattr(updates, "_request",
                        serve({asset.url: swapped}))
    destination = tmp_path / "setup.exe"
    with pytest.raises(IntegrityError, match="does not match the checksum"):
        updates.download(asset, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob("*.part"))


def test_a_matching_download_is_kept_and_remembers_its_digest(monkeypatch,
                                                              tmp_path):
    """download() leaves the digest where the helper will look for it.

    The interface calls download() and then hands the path over. Nothing
    else carries the digest across that gap, so without the sidecar the
    helper would refuse the package it just verified.
    """
    body = b"the real installer"
    asset = Asset("setup.exe", "https://example.invalid/setup.exe",
                  len(body), digest(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    path = updates.download(asset, tmp_path / "setup.exe")
    assert path.read_bytes() == body
    assert updates._remembered_digest(path) == digest(body)


def test_a_release_with_no_checksum_stops_with_the_documented_words(
        monkeypatch, tmp_path):
    body = b"anything"
    asset = Asset("setup.exe", "https://example.invalid/setup.exe", len(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    with pytest.raises(IntegrityError) as caught:
        updates.download(asset, tmp_path / "setup.exe")
    assert str(caught.value) == updates.NO_SUMS_MESSAGE
    assert "SHA256SUMS" in updates.NO_SUMS_MESSAGE
    assert not (tmp_path / "setup.exe").exists()


def test_the_escape_hatch_allows_an_old_release(monkeypatch, tmp_path):
    body = b"an older release, published before checksums existed"
    asset = Asset("setup.exe", "https://example.invalid/setup.exe", len(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    monkeypatch.setenv(updates.SKIP_VERIFY_ENV, "1")
    assert updates.download(asset, tmp_path / "setup.exe").read_bytes() == body


def test_a_truncated_download_is_discarded(monkeypatch, tmp_path):
    body = b"half of it"
    asset = Asset("setup.exe", "https://example.invalid/setup.exe",
                  len(body) + 500, digest(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    with pytest.raises(OSError):
        updates.download(asset, tmp_path / "setup.exe")
    assert not (tmp_path / "setup.exe").exists()


def test_a_cancelled_download_leaves_nothing_behind(monkeypatch, tmp_path):
    body = b"x" * 600_000
    asset = Asset("setup.exe", "https://example.invalid/setup.exe",
                  len(body), digest(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    with pytest.raises(InterruptedError):
        updates.download(asset, tmp_path / "setup.exe",
                         cancelled=lambda: True)
    assert not (tmp_path / "setup.exe").exists()
    assert not list(tmp_path.glob("*.part"))


# ---------------------------------------------------------------------------
# the helper, which is where the file is finally executed
# ---------------------------------------------------------------------------

def test_the_helper_refuses_a_package_swapped_after_the_download(
        tmp_path, monkeypatch):
    """The window between staging and applying is where TOCTOU lives.

    The app quits before the helper runs. Anything able to write to the
    staging folder in that gap could replace the package the helper is about
    to execute, so the helper checks the bytes again itself.
    """
    package = tmp_path / "setup.zip"
    package.write_bytes(b"swapped after it was verified")
    applied = []
    monkeypatch.setattr(updates, "_apply_archive",
                        lambda *a: applied.append(a))
    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_restart", lambda *a: None)
    monkeypatch.setattr(updates, "_detached", lambda *a: None)

    code = updates.apply_update(package, 1, updates.PORTABLE, tmp_path / "app",
                                digest(b"what was actually downloaded"))
    assert code == 2
    assert not applied, "the helper applied a package that failed its check"
    assert not package.exists(), "the bad package was left on disk"


def test_the_helper_refuses_a_package_with_no_known_digest(tmp_path,
                                                           monkeypatch):
    package = tmp_path / "setup.zip"
    package.write_bytes(b"unknown provenance")
    applied = []
    monkeypatch.setattr(updates, "_apply_archive",
                        lambda *a: applied.append(a))
    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_restart", lambda *a: None)
    monkeypatch.setattr(updates, "_detached", lambda *a: None)
    monkeypatch.delenv(updates.SKIP_VERIFY_ENV, raising=False)

    assert updates.apply_update(package, 1, updates.PORTABLE,
                                tmp_path / "app") == 2
    assert not applied


def test_the_helper_applies_a_package_that_checks_out(tmp_path, monkeypatch):
    body = b"a genuine package"
    package = tmp_path / "setup.zip"
    package.write_bytes(body)
    applied = []
    monkeypatch.setattr(updates, "_apply_archive",
                        lambda pkg, target: applied.append(pkg) or target)
    monkeypatch.setattr(updates, "_wait_for_exit", lambda *a, **k: None)
    monkeypatch.setattr(updates, "_detached", lambda *a: None)

    assert updates.apply_update(package, 1, updates.PORTABLE,
                                tmp_path / "app", digest(body)) == 0
    assert applied == [package]


def test_the_digest_travels_with_the_handover(tmp_path, monkeypatch):
    package = tmp_path / "setup.zip"
    package.write_bytes(b"x")
    updates.remember_digest(package, digest(b"x"))
    seen = {}
    monkeypatch.setattr(updates, "_detached",
                        lambda argv: seen.update(argv=argv))
    updates.launch_helper(package)
    assert "--sha256" in seen["argv"]
    assert seen["argv"][seen["argv"].index("--sha256") + 1] == digest(b"x")


# ---------------------------------------------------------------------------
# the swap
# ---------------------------------------------------------------------------

def _archive(tmp_path, entries):
    package = tmp_path / "new.zip"
    with zipfile.ZipFile(package, "w") as zf:
        for name, body in entries.items():
            zf.writestr(name, body)
    return package


def test_a_failed_swap_puts_the_old_build_back(tmp_path, monkeypatch):
    """An interrupted update must not leave a half-replaced application."""
    app = tmp_path / "app"
    app.mkdir()
    (app / "operators-console").write_text("old build", encoding="utf-8")
    (app / "resources").mkdir()
    (app / "resources" / "data.bin").write_text("old data", encoding="utf-8")

    package = _archive(tmp_path, {
        "bundle/operators-console": "new build",
        "bundle/resources/data.bin": "new data",
    })

    real_move = updates.shutil.move
    calls = {"n": 0}

    def flaky_move(src, dst):
        # The old build is renamed aside (os.replace); shutil.move only moves
        # the new build in. Fail the second of those: half way through.
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("the disk filled up")
        return real_move(src, dst)

    monkeypatch.setattr(updates.shutil, "move", flaky_move)
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))

    with pytest.raises(OSError):
        updates._apply_archive(package, app)

    assert (app / "operators-console").read_text(encoding="utf-8") == "old build"
    assert (app / "resources" / "data.bin").read_text(encoding="utf-8") \
        == "old data"
    assert not (app / ".opcon-previous").exists()


def test_a_package_that_escapes_its_folder_is_refused(tmp_path, monkeypatch):
    """Archive member names are remote input too."""
    package = tmp_path / "evil.zip"
    with zipfile.ZipFile(package, "w") as zf:
        zf.writestr("../escaped.txt", "somewhere else entirely")
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    app = tmp_path / "app"
    app.mkdir()
    with pytest.raises(OSError, match="outside itself"):
        updates._apply_archive(package, app)
    assert not (tmp_path / "escaped.txt").exists()


def test_an_empty_package_replaces_nothing(tmp_path, monkeypatch):
    app = tmp_path / "app"
    app.mkdir()
    (app / "operators-console").write_text("old build", encoding="utf-8")
    package = tmp_path / "empty.zip"
    with zipfile.ZipFile(package, "w"):
        pass
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))
    with pytest.raises(OSError, match="empty"):
        updates._apply_archive(package, app)
    assert (app / "operators-console").read_text(encoding="utf-8") == "old build"


def test_an_appimage_swap_rolls_back(tmp_path, monkeypatch):
    current = tmp_path / "operators-console.AppImage"
    current.write_bytes(b"old image")
    package = tmp_path / "downloaded.AppImage"
    package.write_bytes(b"new image")
    monkeypatch.setenv("APPIMAGE", str(current))
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(tmp_path / "home"))

    def refuse(src, dst):
        raise OSError("read-only filesystem")

    real_move = updates.shutil.move
    moves = {"n": 0}

    def flaky(src, dst):
        moves["n"] += 1
        if moves["n"] == 2:
            return refuse(src, dst)
        return real_move(src, dst)

    monkeypatch.setattr(updates.shutil, "move", flaky)
    with pytest.raises(OSError):
        updates._apply_appimage(package, tmp_path)
    assert current.read_bytes() == b"old image"


def test_an_appimage_beside_the_database_is_refused(tmp_path, monkeypatch):
    """The Linux installer used to put both in the same folder."""
    home = tmp_path / "share" / "operators-console"
    home.mkdir(parents=True)
    monkeypatch.setenv("OPERATORS_CONSOLE_HOME", str(home))
    current = home / "operators-console.AppImage"
    current.write_bytes(b"old")
    monkeypatch.setenv("APPIMAGE", str(current))
    package = tmp_path / "new.AppImage"
    package.write_bytes(b"new")
    with pytest.raises(OSError, match="would delete your data"):
        updates._apply_appimage(package, home)


# ---------------------------------------------------------------------------
# the three calls the interface uses
# ---------------------------------------------------------------------------

def test_available_describes_the_offer(monkeypatch):
    body = b"a windows installer"
    payload = {
        "tag_name": "v99.0.0",
        "name": "Release 99",
        "body": "Notes go here.",
        "html_url": "https://example.invalid/r",
        "assets": [
            {"name": "operators-console-99-windows-setup.exe",
             "browser_download_url": "https://example.invalid/s.exe",
             "size": len(body)},
            {"name": "SHA256SUMS",
             "browser_download_url": "https://example.invalid/SHA256SUMS",
             "size": 80},
        ],
    }
    sums = ("%s  operators-console-99-windows-setup.exe\n"
            % digest(body)).encode()
    monkeypatch.setattr(updates, "_request", serve({
        updates.API % updates.REPO: json.dumps(payload).encode(),
        "https://example.invalid/SHA256SUMS": sums,
    }))
    monkeypatch.setattr(updates.sys, "platform", "win32")
    monkeypatch.setattr(updates, "install_kind", lambda: updates.INSTALLED)

    offer = updates.available()
    # Readable as a mapping, which is what the update button asks for.
    assert offer["version"] == "99.0.0"
    assert offer["notes"] == "Notes go here."
    assert offer["size"] == len(body)
    assert offer["verified"] is True
    assert offer["sha256"] == digest(body)
    # And as an object, which is what the dialog reaches for.
    assert offer.label == "99.0.0"
    assert offer.notes == "Notes go here."
    assert updates.pick_asset(offer).sha256 == digest(body)
    assert updates.is_newer(offer)


def test_available_is_none_when_there_is_nothing_newer(monkeypatch):
    monkeypatch.setattr(updates, "fetch_latest", lambda *a, **k: None)
    assert updates.available() is None


def test_download_update_verifies_and_remembers(monkeypatch, isolated_home):
    body = b"a windows installer"
    asset = Asset("setup.exe", "https://example.invalid/s.exe", len(body),
                  digest(body))
    monkeypatch.setattr(updates, "_request", serve({asset.url: body}))
    for offer in ({"_asset": asset}, asset):
        path = updates.download_update(offer)
        assert path.read_bytes() == body
        assert updates._remembered_digest(path) == digest(body)


def test_apply_and_restart_hands_over_with_the_digest(monkeypatch,
                                                      isolated_home, tmp_path):
    package = tmp_path / "setup.zip"
    package.write_bytes(b"x")
    seen = {}
    monkeypatch.setattr(updates, "_detached",
                        lambda argv: seen.update(argv=argv))
    updates.apply_and_restart(package, digest(b"x"))
    assert updates.APPLY_FLAG in seen["argv"]
    assert digest(b"x") in seen["argv"]


# ---------------------------------------------------------------------------
# version comparison, which decides whether any of this runs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag,expected", [
    ("v1.0.10", (1, 0, 10)),
    ("1.0.0", (1, 0, 0)),
    ("v2026.1.0", (2026, 1, 0)),
])
def test_tags_compare_numerically(tag, expected):
    assert parse_version(tag) == expected

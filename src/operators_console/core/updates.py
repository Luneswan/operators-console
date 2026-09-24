"""Checking for, downloading and applying a new version.

The whole feature is one promise: the learner sees a small button, clicks it,
and the app comes back running the new version. No terminal window, no manual
download, no instructions.

Applying an update cannot happen inside the running process, because on every
platform the files being replaced are the ones currently executing. So the app
relaunches itself with ``--apply-update``, that second process waits for the
first to exit, swaps the files, starts the new build and exits. The helper is
this same windowed executable, which is what keeps a console from flashing up.

Networking is stdlib only, so the app still has no third-party dependency
beyond Qt, and the check is a single request the user can turn off.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path

from . import paths
from ..version import __version__

REPO = os.environ.get("OPERATORS_CONSOLE_REPO", "Luneswan/operators-console")
API = "https://api.github.com/repos/%s/releases/latest"
USER_AGENT = "operators-console/%s" % __version__
TIMEOUT = 8

APPLY_FLAG = "--apply-update"

# The Windows portable zip is named so that builds before 1.1.0 cannot see it.
# Their picker looked for the literal "windows-portable.zip", and their
# portable swap deleted parts of the folder it was running from; given no
# match they say "no download for your platform" instead. The installer keeps
# its old name ("windows" ... "setup.exe"), which is how 1.0.x installed
# builds find it, and that path is safe.
WINDOWS_PORTABLE_SUFFIX = "windows-x64-portable.zip"

# The manifest the release workflow publishes beside the binaries: one
# "<sha256>  <filename>" line per artefact, the same shape sha256sum writes.
SUMS_NAME = "SHA256SUMS"
SKIP_VERIFY_ENV = "OPERATORS_CONSOLE_SKIP_VERIFY"

# Refusals are worded once, here, so the installers, the helper and the tests
# can all assert on the same sentence.
NO_SUMS_MESSAGE = (
    "This release does not publish a %s file, so the download cannot be "
    "verified. Refusing to install it." % SUMS_NAME)
MISMATCH_MESSAGE = (
    "The download does not match the checksum published with the release. "
    "It has been discarded and nothing was installed.")
INSECURE_URL_MESSAGE = (
    "Refusing to download over an insecure connection: %s")


class IntegrityError(Exception):
    """A download did not match the checksum published with the release."""


def skip_verification() -> bool:
    """The escape hatch, for a release published before checksums existed."""
    return os.environ.get(SKIP_VERIFY_ENV, "") not in ("", "0", "false", "no")


def secure_url(url: str) -> str:
    """Return *url* if it is plain HTTPS, otherwise refuse.

    The asset list arrives as JSON from the network, so its URLs are input,
    not configuration. Without this an answer that names ``http://`` or
    ``file://`` would be fetched and then executed.
    """
    parsed = urllib.parse.urlsplit(url or "")
    if parsed.scheme != "https" or not parsed.netloc:
        raise IntegrityError(INSECURE_URL_MESSAGE % (url or "(empty)"))
    return url


def sha256_file(path, chunk: int = 1024 * 1024) -> str:
    """Hex digest of a file, read in chunks so a 200 MB package is fine."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def parse_sums(text: str) -> dict:
    """Parse a sha256sum-style manifest into {filename: digest}."""
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, name = parts[0].strip().lower(), parts[1].strip()
        # sha256sum writes "*name" for a binary-mode file.
        name = name.lstrip("*").strip()
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
            out[name] = digest
    return out


def verify_file(path, expected: str) -> None:
    """Raise IntegrityError unless *path* hashes to *expected*."""
    if not expected:
        raise IntegrityError(NO_SUMS_MESSAGE)
    actual = sha256_file(path)
    if actual != expected.lower():
        raise IntegrityError(MISMATCH_MESSAGE)


@dataclass(frozen=True, slots=True)
class Asset:
    name: str
    url: str
    size: int
    sha256: str = ""       # filled in from the release's SHA256SUMS manifest


@dataclass(frozen=True, slots=True)
class Release:
    version: tuple
    tag: str
    name: str
    notes: str
    url: str
    assets: tuple
    verified: bool = False   # True when the release published SHA256SUMS

    @property
    def label(self) -> str:
        return ".".join(str(part) for part in self.version)

    def asset(self, name: str):
        for item in self.assets:
            if item.name == name:
                return item
        return None

    # The interface reads an offer either as an object (release.label,
    # release.notes) or as the mapping the update button was specified
    # against ({"version", "notes", "size"}). Supporting both costs six
    # lines here and saves the two halves having to land together.

    def summary(self) -> dict:
        chosen = pick_asset(self)
        return {
            "version": self.label,
            "tag": self.tag,
            "name": self.name,
            "notes": self.notes,
            "url": self.url,
            "asset": chosen.name if chosen else "",
            "size": chosen.size if chosen else 0,
            "sha256": chosen.sha256 if chosen else "",
            "verified": bool(self.verified and chosen and chosen.sha256),
        }

    def __getitem__(self, key: str):
        return self.summary()[key]

    def get(self, key: str, default=None):
        return self.summary().get(key, default)

    def keys(self):
        return self.summary().keys()


def parse_version(text: str) -> tuple:
    """Turn '1.2.3' or 'v1.2.3-beta' into a comparable tuple."""
    numbers = re.findall(r"\d+", text or "")
    if not numbers:
        return (0,)
    return tuple(int(n) for n in numbers[:4])


def current_version() -> tuple:
    return parse_version(__version__)


class _HttpsOnlyRedirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects, but never off HTTPS.

    urllib happily follows an https -> http redirect, which would hand a
    network attacker the whole download. GitHub redirects release assets to
    its CDN, so redirects cannot simply be refused; only downgrades can.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        secure_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_HttpsOnlyRedirects)


def _request(url: str, timeout: int = TIMEOUT, headers: dict | None = None):
    request = urllib.request.Request(
        secure_url(url), headers={"User-Agent": USER_AGENT,
                                  "Accept": "application/vnd.github+json",
                                  **(headers or {})})
    return _opener.open(request, timeout=timeout)


# The last answer about the latest release, and the ETag GitHub sent with
# it. Asking again with If-None-Match gets a 304 while nothing changed, and
# GitHub does not count a 304 against the 60-an-hour unauthenticated limit,
# so the app can look every few minutes without ever being rate limited.
_latest = {"etag": "", "release": None}


def fetch_latest(timeout: int = TIMEOUT) -> Release | None:
    """Ask GitHub for the newest release. Returns None on any failure.

    A failed check must never interrupt a study session, so every network and
    parsing error is swallowed: the button simply does not appear.
    """
    cached = {"If-None-Match": _latest["etag"]} if _latest["etag"] else {}
    try:
        with _request(API % REPO, timeout, headers=cached) as response:
            etag = (getattr(response, "headers", None) or {}).get("ETag") or ""
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and _latest["etag"]:
            return _latest["release"]       # unchanged since the last look
        return None
    except (urllib.error.URLError, OSError, ValueError,
            json.JSONDecodeError, IntegrityError):
        return None             # IntegrityError: redirected off https
    release = _release_from(payload, timeout)
    # Only a settled answer is worth reusing: a release whose checksums
    # could not be fetched this time is asked for in full next time.
    if release is None or release.verified:
        _latest.update(etag=etag, release=release)
    else:
        _latest.update(etag="", release=None)
    return release


def _release_from(payload: dict, timeout: int) -> Release | None:
    """The release a GitHub payload describes, or None if it offers none."""

    if payload.get("draft") or payload.get("prerelease"):
        return None

    tag = payload.get("tag_name") or ""
    assets = tuple(
        Asset(a.get("name", ""), a.get("browser_download_url", ""),
              int(a.get("size") or 0))
        for a in payload.get("assets", [])
        if a.get("browser_download_url"))
    if not assets:
        return None

    assets, verified = _attach_digests(assets, timeout)

    return Release(
        version=parse_version(tag),
        tag=tag,
        name=payload.get("name") or tag,
        notes=payload.get("body") or "",
        url=payload.get("html_url") or "",
        assets=assets,
        verified=verified,
    )


def fetch_sums(assets, timeout: int = TIMEOUT) -> dict:
    """Download and parse the release's SHA256SUMS. {} when there is none."""
    for asset in assets:
        if asset.name != SUMS_NAME:
            continue
        try:
            with _request(asset.url, timeout) as response:
                return parse_sums(response.read(1024 * 256).decode("utf-8",
                                                                   "replace"))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError,
                IntegrityError, ValueError):
            return {}
    return {}


def _attach_digests(assets, timeout: int = TIMEOUT):
    """Stamp each asset with its published digest. (assets, verified)."""
    sums = fetch_sums(assets, timeout)
    if not sums:
        return assets, False
    stamped = tuple(replace(a, sha256=sums.get(a.name, "")) for a in assets)
    # "Verified" means every downloadable artefact is covered, not just some.
    covered = all(a.sha256 for a in stamped if a.name != SUMS_NAME)
    return stamped, covered


def is_newer(release: Release | None) -> bool:
    return release is not None and release.version > current_version()


# ---------------------------------------------------------------------------
# working out which build this installation is
# ---------------------------------------------------------------------------

INSTALLED = "installed"
PORTABLE = "portable"
APPIMAGE = "appimage"
MACAPP = "macapp"
SOURCE = "source"


def app_root() -> Path:
    """The directory holding the running build."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def install_kind() -> str:
    """How this copy was installed, which decides how it is replaced."""
    if not getattr(sys, "frozen", False):
        return SOURCE
    if os.environ.get("APPIMAGE"):
        return APPIMAGE
    if sys.platform == "darwin":
        return MACAPP if ".app/Contents/" in str(sys.executable) else PORTABLE
    if sys.platform == "win32":
        # Inno Setup leaves its uninstaller beside the executable; a zip does not.
        if any(app_root().glob("unins*.exe")):
            return INSTALLED
        return PORTABLE
    return PORTABLE


def can_self_update() -> bool:
    """Running from source is updated with git, not by swapping files."""
    return install_kind() != SOURCE


def _mac_arch() -> str:
    machine = platform.machine().lower()
    return "arm64" if machine in ("arm64", "aarch64") else "x86_64"


def pick_asset(release: Release, kind: str | None = None) -> Asset | None:
    """Choose the download that matches this platform and install shape."""
    kind = kind or install_kind()

    def find(*needles: str) -> Asset | None:
        for asset in release.assets:
            if asset.name == SUMS_NAME:
                continue
            name = asset.name.lower()
            if all(needle.lower() in name for needle in needles):
                return asset
        return None

    if sys.platform == "win32":
        # "portable.zip" rather than the full suffix, so a release that still
        # uses the pre-1.1.0 name "windows-portable.zip" is found as well.
        if kind == INSTALLED:
            return (find("windows", "setup.exe")
                    or find("windows", "portable.zip"))
        return find("windows", "portable.zip")

    if sys.platform == "darwin":
        arch = _mac_arch()
        if kind == PORTABLE:
            return find("macos", arch, "portable.zip") or find("macos", arch, ".dmg")
        return find("macos", arch, ".dmg") or find("macos", arch, "portable.zip")

    if kind == APPIMAGE:
        return find(".appimage")
    return find("linux-portable.zip") or find("linux", ".tar.gz")


def download(asset: Asset, destination: Path, progress=None,
             cancelled=None, expect: str | None = None) -> Path:
    """Stream an asset to disk, then verify it before anyone can use it.

    ``progress(done, total)`` is called as the download proceeds and
    ``cancelled()`` is polled so the user can back out of a large download.

    The file is written to a ``.part`` beside the destination and only moved
    into place once its SHA-256 matches the digest the release published, so
    a caller that finds the destination knows it holds the right bytes and a
    half-finished or tampered download never occupies the name the updater
    will later execute.

    ``expect`` overrides ``asset.sha256``. A release that published no
    manifest leaves both empty, and that is refused unless the escape hatch
    OPERATORS_CONSOLE_SKIP_VERIFY is set.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = (expect if expect is not None else asset.sha256) or ""
    if not expected and not skip_verification():
        raise IntegrityError(NO_SUMS_MESSAGE)

    total = asset.size
    done = 0
    partial = destination.with_name(destination.name + ".part")
    partial.unlink(missing_ok=True)

    try:
        with _request(asset.url, timeout=30) as response:
            with partial.open("wb") as handle:
                if not total:
                    total = int(response.headers.get("Content-Length") or 0)
                while True:
                    if cancelled is not None and cancelled():
                        raise InterruptedError("The download was cancelled.")
                    chunk = response.read(262144)
                    if not chunk:
                        break
                    handle.write(chunk)
                    done += len(chunk)
                    if progress is not None:
                        progress(done, total)

        if total and partial.stat().st_size != total:
            raise OSError("The download finished early and was discarded.")
        if expected:
            verify_file(partial, expected)
        destination.unlink(missing_ok=True)
        partial.replace(destination)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    if expected:
        # The helper checks the package again just before it runs it, and it
        # only has the path to go on. Leave the digest where it can find it.
        remember_digest(destination, expected)
    return destination


def staging_dir() -> Path:
    folder = paths.root_dir() / "updates"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# ---------------------------------------------------------------------------
# handing over to the helper process
# ---------------------------------------------------------------------------

def _detached(argv: list) -> None:
    """Start a process that outlives this one and shows no console."""
    kwargs = {"close_fds": True}
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        flags |= getattr(subprocess, "DETACHED_PROCESS", 0)
        kwargs["creationflags"] = flags
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(argv, **kwargs)


HELPER_PREFIX = "helper-"
# Qt is most of a build's size and the helper never imports it.
_HELPER_SKIP = frozenset({"PySide6", "shiboken6", ".opcon-previous"})
# A helper copy younger than this may still be running; leave it alone.
_HELPER_GRACE_SECONDS = 60.0


def _helper_executable(keep=()) -> Path:
    """The program that will run the update helper.

    Windows lets a running program's files be renamed but never overwritten,
    and the installer overwrites in place. A helper started from the folder
    it is about to replace would therefore make its own update fail - and the
    installer's Restart Manager would try to close it half way through. So a
    frozen Windows build copies itself, minus Qt, into the staging folder and
    the helper runs from there. If the copy cannot be made the helper runs in
    place, which still works for the portable build: its swap only renames.
    """
    here = Path(sys.executable)
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return here
    try:
        return _stage_helper(app_root(), here.name, keep)
    except Exception as exc:        # RecursionError included, not just OSError
        _log("could not copy the helper out, running it in place: %s" % exc)
        return here


def _stage_helper(root: Path, exe_name: str, keep=()) -> Path:
    tidy_staging(keep)
    staging = staging_dir()
    folder = staging / ("%s%d" % (HELPER_PREFIX, os.getpid()))
    shutil.rmtree(folder, ignore_errors=True)
    root = Path(root)
    # A portable install may keep the learner's data inside its own folder,
    # and the staging folder lives in the data folder: copying either would
    # copy the copy, until Python ran out of recursion.
    avoid = {staging.resolve(), paths.root_dir().resolve()}

    def skip(directory, names):
        top = Path(directory) == root
        return [n for n in names if n in _HELPER_SKIP
                or (top and n.lower().startswith("unins"))
                or (Path(directory) / n).resolve() in avoid]

    shutil.copytree(root, folder, ignore=skip)
    os.utime(folder)            # copytree stamps the folder with the source's age
    exe = folder / exe_name
    if not exe.exists():
        raise OSError("the helper copy has no %s" % exe_name)
    return exe


def _is_log(path: Path) -> bool:
    return path.suffix.lower() == ".log"


def tidy_staging(keep=()) -> None:
    """Clear what earlier updates left in the staging folder. Never raises.

    The helper cannot delete the folder it runs from, so each update leaves
    one behind. A failed or abandoned update also leaves its package, a
    ``.part`` from a download that never finished and the ``.sha256``
    sidecar; a Windows package alone is over 20 MB. Anything older than the
    grace period goes, apart from the installer's log, which is the record of
    what happened. Paths in *keep*, and the folder the running process was
    started from, are never touched.
    """
    if isinstance(keep, (str, os.PathLike)):
        keep = (keep,)
    try:
        entries = list(staging_dir().iterdir())
    except OSError:
        return
    spared = set()
    for path in keep or ():
        try:
            path = Path(path).resolve()
        except OSError:
            continue
        spared.add(path)
        spared.add(_digest_sidecar(path))
    try:
        running = Path(sys.executable).resolve()
    except OSError:
        running = None
    now = time.time()
    for entry in entries:
        try:
            resolved = entry.resolve()
            if resolved in spared or _is_log(entry):
                continue
            if running is not None and running.is_relative_to(resolved):
                continue
            if now - entry.stat().st_mtime < _HELPER_GRACE_SECONDS:
                continue
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                entry.unlink(missing_ok=True)
        except OSError:
            continue


def launch_helper(package: Path, sha256: str = "") -> None:
    """Relaunch this executable as the updater, then the caller must quit.

    The digest travels with the handover so the helper can check the package
    again at the moment it is about to be executed. Between the download and
    the swap the application quits, which is exactly the window in which a
    staged file could be replaced.
    """
    package = Path(package)
    if getattr(sys, "frozen", False) and install_kind() == PORTABLE:
        # Raised here, while the app is still open to show it; the helper
        # would only have refused silently after the app had gone.
        _guard_user_data(app_root())
    if not sha256:
        sha256 = _remembered_digest(package)
    argv = [str(_helper_executable(keep=(package,)))]
    if not getattr(sys, "frozen", False):
        argv += ["-m", "operators_console"]
    argv += [APPLY_FLAG, str(package), "--pid", str(os.getpid()),
             "--kind", install_kind(), "--target", str(app_root())]
    if sha256:
        argv += ["--sha256", sha256]
    _detached(argv)


def _digest_sidecar(package: Path) -> Path:
    return Path(package).with_name(Path(package).name + ".sha256")


def remember_digest(package: Path, sha256: str) -> None:
    """Record the verified digest beside a staged package.

    ``launch_helper`` is called by the interface with only the path, so the
    digest has to survive somewhere between the two. The sidecar lives in the
    same per-user staging folder as the package; anyone able to rewrite it
    could rewrite the package too, so it adds no new exposure, and it means
    the default path still re-checks rather than trusting the file blindly.
    """
    try:
        _digest_sidecar(package).write_text(sha256.strip().lower(),
                                            encoding="ascii")
    except OSError:
        pass


def _remembered_digest(package: Path) -> str:
    try:
        text = _digest_sidecar(package).read_text(encoding="ascii").strip()
    except OSError:
        return ""
    return text.lower() if len(text) == 64 else ""


FAILURE_FILE = "update-failed.json"


def record_failure(reason: str) -> None:
    """Note why nothing was installed, for the next start of the app.

    The helper has no window, and the app it reopens is the old version: the
    learner would otherwise see the app close and come back unchanged, with
    no word and no button.
    """
    try:
        (paths.root_dir() / FAILURE_FILE).write_text(
            json.dumps({"reason": reason, "at": time.time()}),
            encoding="utf-8")
    except OSError:
        pass


def take_failure() -> str:
    """Why the last update did not install - once - or "" if it did."""
    note = paths.root_dir() / FAILURE_FILE
    try:
        data = json.loads(note.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    finally:
        try:
            note.unlink(missing_ok=True)
        except OSError:
            pass
    return str(data.get("reason") or "") if isinstance(data, dict) else ""


def _wait_for_exit(pid: int, timeout: float = 45.0) -> None:
    """Block until the parent has really gone, so its files are unlocked."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _alive(pid):
            # Windows releases handles slightly after the process disappears.
            time.sleep(1.5)
            return
        time.sleep(0.35)


def _alive(pid: int) -> bool:
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
            capture_output=True, text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return str(pid) in (result.stdout or "")
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _log(message: str) -> None:
    """The helper has no window, so leave a trail for when it goes wrong."""
    try:
        line = "%s  %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), message)
        (paths.root_dir() / "update.log").open("a", encoding="utf-8").write(line)
    except OSError:
        pass


def apply_update(package: Path, pid: int, kind: str, target: Path,
                 sha256: str = "") -> int:
    """Runs in the helper process: replace the build and start it again."""
    package, target = Path(package), Path(target)
    _log("helper started for %s (kind=%s, pid=%d)" % (package.name, kind, pid))
    # First, so that no path below - a refusal included - can start the old
    # build again while the old build is still closing.
    _wait_for_exit(pid)

    expected = sha256 or _remembered_digest(package)
    if expected:
        try:
            verify_file(package, expected)
        except (IntegrityError, OSError) as exc:
            _log("REFUSED: %s" % exc)
            record_failure("the download did not match the checksum "
                           "published with the release, so it was discarded")
            package.unlink(missing_ok=True)
            tidy_staging()
            _restart(target)
            return 2
        _log("checksum verified")
    elif not skip_verification():
        _log("REFUSED: %s" % NO_SUMS_MESSAGE)
        record_failure("the release publishes no checksums, so the download "
                       "could not be verified")
        package.unlink(missing_ok=True)
        tidy_staging()
        _restart(target)
        return 2

    try:
        if sys.platform == "win32" and package.suffix.lower() == ".exe":
            launched = _apply_windows_installer(package, target)
        elif package.suffix.lower() == ".dmg":
            launched = _apply_macos_dmg(package, target)
        elif package.suffix.lower() == ".appimage":
            launched = _apply_appimage(package, target)
        else:
            launched = _apply_archive(package, target)
    except Exception as exc:
        _log("FAILED: %s: %s" % (type(exc).__name__, exc))
        record_failure("%s (details in update.log)" % exc)
        # A failed update leaves the package behind; clear anything older
        # than the grace period now rather than at the next launch.
        tidy_staging()
        _restart(target)
        return 1

    _log("applied, relaunching %s" % launched)
    _detached([str(launched)])
    for leftover in (package, _digest_sidecar(package)):
        try:
            leftover.unlink(missing_ok=True)
        except OSError:
            pass
    return 0


def _executable_in(folder: Path) -> Path:
    """Find the application inside a build folder.

    Both spellings are tried on every platform. The restart after a failed
    swap has to find whatever is actually there, and "nothing matched the
    name I expected" would leave the learner staring at a closed app.
    """
    names = ("operators-console.exe", "operators-console")
    if sys.platform != "win32":
        names = tuple(reversed(names))
    for name in names:
        direct = folder / name
        if direct.exists():
            return direct
    for name in names:
        for candidate in folder.rglob(name):
            return candidate
    return folder / names[0]


def _restart(target: Path) -> None:
    """Best effort: get the learner back into the app even after a failure."""
    try:
        exe = _executable_in(target)
        if exe.exists():
            _detached([str(exe)])
    except OSError:
        pass


def _apply_windows_installer(package: Path, target: Path) -> Path:
    # /VERYSILENT, not /SILENT: a silent Inno Setup still shows its progress
    # window, and the promise is that nothing appears but the new version.
    # Errors are suppressed rather than shown, so the log is the only record.
    # /NORELAUNCH: this helper restarts the app itself below; without it the
    # installer would open a second copy (it reopens the app for builds
    # before 1.1.0, whose updater it has to close to replace the files).
    subprocess.run(
        [str(package), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
         "/NOCANCEL", "/SP-", "/NORELAUNCH",
         "/LOG=%s" % (staging_dir() / "setup.log")],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return _executable_in(target)


def _guard_user_data(target: Path) -> None:
    """Refuse to replace a folder that contains the learner's progress.

    An update swaps the application directory wholesale. Normally the database
    lives in the platform's data folder, far away from it, but a portable
    install with OPERATORS_CONSOLE_HOME pointed inside the app folder would
    otherwise have its progress deleted by the very act of updating.
    """
    data = paths.root_dir().resolve()
    target = Path(target).resolve()
    if data == target or data.is_relative_to(target):
        raise OSError(
            "Your progress is stored inside the application folder (%s), so "
            "replacing it would delete your data. Move the folder, or set "
            "OPERATORS_CONSOLE_HOME elsewhere, then update again." % data)


def _safe_extract(archive, members, unpacked: Path, name_of) -> None:
    """Extract only members that stay inside *unpacked*.

    A release built by the project's own workflow never contains ``..`` or an
    absolute path, but the archive arrives over the network, and an extractor
    that trusts member names writes wherever the archive says.
    """
    root = unpacked.resolve()
    for member in members:
        name = name_of(member)
        candidate = (unpacked / name).resolve()
        if candidate != root and not candidate.is_relative_to(root):
            raise OSError("The package contains a path outside itself: %s"
                          % name)
    archive.extractall(unpacked)


def _apply_archive(package: Path, target: Path) -> Path:
    """Replace a portable build with the contents of a zip or tarball.

    The old build is moved aside rather than deleted, so a swap that fails
    half way can be put back. Only once the new build is in place and its
    executable exists is the previous one discarded.
    """
    import tarfile
    import zipfile

    _guard_user_data(target)

    unpacked = Path(tempfile.mkdtemp(prefix="opcon-update-"))
    try:
        if package.suffix.lower() == ".zip":
            with zipfile.ZipFile(package) as archive:
                _safe_extract(archive, archive.infolist(), unpacked,
                              lambda m: m.filename)
        else:
            with tarfile.open(package) as archive:
                _safe_extract(archive, archive.getmembers(), unpacked,
                              lambda m: m.name)

        # Archives contain a single top-level folder; use it when present.
        entries = [p for p in unpacked.iterdir() if not p.name.startswith(".")]
        source = (entries[0] if len(entries) == 1 and entries[0].is_dir()
                  else unpacked)

        target = Path(target)
        target.mkdir(parents=True, exist_ok=True)
        keep = _rollback_dir(target)
        shutil.rmtree(keep, ignore_errors=True)
        keep.mkdir(parents=True, exist_ok=True)

        wanted = [item.name for item in source.iterdir()]
        if not wanted:
            raise OSError("The package is empty; nothing was replaced.")

        moved: list[tuple[Path, Path]] = []    # what was there, and where it went
        added: list[Path] = []                # what the new build brought
        try:
            for item in source.iterdir():
                destination = target / item.name
                if destination.exists():
                    aside = keep / item.name
                    _rename_or_refuse(destination, aside)
                    moved.append((aside, destination))
                else:
                    added.append(destination)
                shutil.move(str(item), str(destination))

            missing = [n for n in wanted if not (target / n).exists()]
            if missing:
                raise OSError(
                    "The new build is incomplete (%s); rolling back."
                    % ", ".join(missing[:3]))
        except Exception:
            _roll_back(moved, target, added)
            raise

        executable = _executable_in(target)
        if not executable.exists():
            _log("warning: no %s in the new build" % executable.name)
        elif sys.platform != "win32":
            executable.chmod(0o755)
        shutil.rmtree(keep, ignore_errors=True)
        return executable
    finally:
        shutil.rmtree(unpacked, ignore_errors=True)


def _rollback_dir(target: Path) -> Path:
    return Path(target) / ".opcon-previous"


def _rename_or_refuse(source: Path, destination: Path,
                      attempts: int = 6) -> None:
    """Rename, or raise with nothing touched.

    shutil.move falls back to copy-then-delete when a rename is refused, and
    a delete that cannot finish - a virus scanner holding one file for a
    moment - leaves half of the old build behind. A rename happens or it
    does not; the usual refusal is momentary, so it is retried briefly.
    """
    for attempt in range(attempts):
        try:
            os.replace(source, destination)
            return
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.25 * (attempt + 1))


def _roll_back(moved, target: Path, added=()) -> None:
    """Put the previous build back after a failed swap."""
    for path in added:              # files the new build brought, gone again
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
        except OSError as exc:
            _log("rollback could not remove %s: %s" % (path, exc))
    for aside, destination in reversed(moved):
        try:
            if destination.is_dir():
                shutil.rmtree(destination, ignore_errors=True)
            elif destination.exists():
                destination.unlink(missing_ok=True)
            shutil.move(str(aside), str(destination))
        except OSError as exc:
            _log("rollback could not restore %s: %s" % (destination, exc))
    shutil.rmtree(_rollback_dir(target), ignore_errors=True)
    _log("rolled back to the previous build")


def _apply_macos_dmg(package: Path, target: Path) -> Path:
    """Copy the .app out of a disk image, over the installed one."""
    # target points inside the bundle, so climb out to the folder holding it.
    bundle = Path(sys.executable)
    for parent in Path(target).parents:
        if parent.suffix == ".app":
            bundle = parent
            break
    else:
        bundle = Path(target)
    holder = bundle.parent

    _guard_user_data(bundle)

    mount = Path(tempfile.mkdtemp(prefix="opcon-dmg-"))
    subprocess.run(["hdiutil", "attach", str(package), "-nobrowse", "-quiet",
                    "-mountpoint", str(mount)], check=True)
    try:
        apps = [p for p in mount.iterdir() if p.suffix == ".app"]
        if not apps:
            raise OSError("no application inside the disk image")
        fresh = apps[0]
        destination = holder / fresh.name
        staged = holder / (fresh.name + ".new")
        previous = holder / (fresh.name + ".previous")
        shutil.rmtree(staged, ignore_errors=True)
        shutil.rmtree(previous, ignore_errors=True)
        shutil.copytree(fresh, staged, symlinks=True)
        had_previous = destination.exists()
        if had_previous:
            destination.rename(previous)
        try:
            staged.rename(destination)
        except OSError:
            if had_previous:
                previous.rename(destination)
                _log("rolled back the .app bundle")
            raise
        shutil.rmtree(previous, ignore_errors=True)
    finally:
        subprocess.run(["hdiutil", "detach", str(mount), "-quiet"], check=False)
        shutil.rmtree(mount, ignore_errors=True)

    subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(destination)],
                   check=False)
    return destination / "Contents" / "MacOS" / "operators-console"


def _apply_appimage(package: Path, target: Path) -> Path:
    """Swap the AppImage file this process was launched from.

    The old image is kept until the new one is in place, so a failed move
    does not leave the learner with no application at all.
    """
    current = Path(os.environ.get("APPIMAGE") or (target / "operators-console"))
    _guard_user_data(current.parent)
    backup = current.with_name(current.name + ".previous")
    had_backup = False
    if current.exists():
        backup.unlink(missing_ok=True)
        shutil.move(str(current), str(backup))
        had_backup = True
    try:
        shutil.move(str(package), str(current))
        current.chmod(0o755)
    except Exception:
        if had_backup:
            current.unlink(missing_ok=True)
            shutil.move(str(backup), str(current))
            _log("rolled back the AppImage")
        raise
    backup.unlink(missing_ok=True)
    return current


# ---------------------------------------------------------------------------
# the three calls the interface needs
# ---------------------------------------------------------------------------

def available(timeout: int = TIMEOUT) -> Release | None:
    """The newer release worth offering, or None. Never raises.

    The result reads as an object (``offer.label``, ``offer.notes``) and as a
    mapping (``offer["version"]``, ``offer["size"]``, ``offer["verified"]``),
    so whichever shape the interface reaches for is the right one.
    ``verified`` is False when the release published no checksum manifest,
    which is worth showing before offering to install anything.
    """
    release = fetch_latest(timeout)
    if not is_newer(release):
        return None
    if pick_asset(release) is None:
        return None
    return release


def _offered_asset(offer):
    """The Asset inside whatever ``available()`` handed back."""
    if isinstance(offer, Asset):
        return offer
    if isinstance(offer, Release):
        return pick_asset(offer)
    if isinstance(offer, dict):
        asset = offer.get("_asset") or offer.get("asset")
        if isinstance(asset, Asset):
            return asset
        # dict(offer) keeps only the asset's name: it is for reading.
        raise ValueError("Pass the offer that available() returned, not a "
                         "copy of its summary.")
    return getattr(offer, "asset", None)


def download_update(offer, progress=None, cancelled=None) -> Path:
    """Download the asset in an ``available()`` offer and verify it.

    Raises IntegrityError when the release published no checksum or the bytes
    do not match it, InterruptedError when ``cancelled()`` goes true.
    """
    asset = _offered_asset(offer)
    if asset is None:
        raise ValueError("That release has no download for this platform.")
    destination = staging_dir() / asset.name
    return download(asset, destination, progress=progress,
                    cancelled=cancelled)


def apply_and_restart(package: Path, sha256: str = "") -> None:
    """Hand the verified package to the helper. The caller must then quit.

    The helper waits for this process to exit, checks the package again,
    swaps the build with a rollback on failure, and starts the new version.
    """
    launch_helper(Path(package), sha256)


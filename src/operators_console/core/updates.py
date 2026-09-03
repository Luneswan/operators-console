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

import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from . import paths
from ..version import __version__

REPO = os.environ.get("OPERATORS_CONSOLE_REPO", "Luneswan/operators-console")
API = "https://api.github.com/repos/%s/releases/latest"
USER_AGENT = "operators-console/%s" % __version__
TIMEOUT = 8

APPLY_FLAG = "--apply-update"


@dataclass(frozen=True, slots=True)
class Asset:
    name: str
    url: str
    size: int


@dataclass(frozen=True, slots=True)
class Release:
    version: tuple
    tag: str
    name: str
    notes: str
    url: str
    assets: tuple

    @property
    def label(self) -> str:
        return ".".join(str(part) for part in self.version)


def parse_version(text: str) -> tuple:
    """Turn '1.2.3' or 'v1.2.3-beta' into a comparable tuple."""
    numbers = re.findall(r"\d+", text or "")
    if not numbers:
        return (0,)
    return tuple(int(n) for n in numbers[:4])


def current_version() -> tuple:
    return parse_version(__version__)


def _request(url: str, timeout: int = TIMEOUT):
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT,
                      "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(request, timeout=timeout)


def fetch_latest(timeout: int = TIMEOUT) -> Release | None:
    """Ask GitHub for the newest release. Returns None on any failure.

    A failed check must never interrupt a study session, so every network and
    parsing error is swallowed: the button simply does not appear.
    """
    try:
        with _request(API % REPO, timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError,
            ValueError, json.JSONDecodeError):
        return None

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

    return Release(
        version=parse_version(tag),
        tag=tag,
        name=payload.get("name") or tag,
        notes=payload.get("body") or "",
        url=payload.get("html_url") or "",
        assets=assets,
    )


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
            name = asset.name.lower()
            if all(needle.lower() in name for needle in needles):
                return asset
        return None

    if sys.platform == "win32":
        if kind == INSTALLED:
            return find("windows", "setup.exe") or find("windows-portable.zip")
        return find("windows-portable.zip")

    if sys.platform == "darwin":
        arch = _mac_arch()
        if kind == PORTABLE:
            return find("macos", arch, "portable.zip") or find("macos", arch, ".dmg")
        return find("macos", arch, ".dmg") or find("macos", arch, "portable.zip")

    if kind == APPIMAGE:
        return find(".appimage")
    return find("linux-portable.zip") or find("linux", ".tar.gz")


def download(asset: Asset, destination: Path, progress=None,
             cancelled=None) -> Path:
    """Stream an asset to disk, reporting progress in bytes.

    ``progress(done, total)`` is called as the download proceeds and
    ``cancelled()`` is polled so the user can back out of a large download.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    total = asset.size
    done = 0

    with _request(asset.url, timeout=30) as response, \
            destination.open("wb") as handle:
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

    if total and destination.stat().st_size != total:
        destination.unlink(missing_ok=True)
        raise OSError("The download finished early and was discarded.")
    return destination


def staging_dir() -> Path:
    folder = paths.data_dir() / "updates"
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


def launch_helper(package: Path) -> None:
    """Relaunch this executable as the updater, then the caller must quit."""
    argv = [sys.executable]
    if not getattr(sys, "frozen", False):
        argv += ["-m", "operators_console"]
    argv += [APPLY_FLAG, str(package), "--pid", str(os.getpid()),
             "--kind", install_kind(), "--target", str(app_root())]
    _detached(argv)


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
        (paths.data_dir() / "update.log").open("a", encoding="utf-8").write(line)
    except OSError:
        pass


def apply_update(package: Path, pid: int, kind: str, target: Path) -> int:
    """Runs in the helper process: replace the build and start it again."""
    package, target = Path(package), Path(target)
    _log("helper started for %s (kind=%s, pid=%d)" % (package.name, kind, pid))
    _wait_for_exit(pid)

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
        _restart(target)
        return 1

    _log("applied, relaunching %s" % launched)
    _detached([str(launched)])
    try:
        package.unlink(missing_ok=True)
    except OSError:
        pass
    return 0


def _executable_in(folder: Path) -> Path:
    name = "operators-console.exe" if sys.platform == "win32" \
        else "operators-console"
    direct = folder / name
    if direct.exists():
        return direct
    for candidate in folder.rglob(name):
        return candidate
    return direct


def _restart(target: Path) -> None:
    """Best effort: get the learner back into the app even after a failure."""
    try:
        exe = _executable_in(target)
        if exe.exists():
            _detached([str(exe)])
    except OSError:
        pass


def _apply_windows_installer(package: Path, target: Path) -> Path:
    subprocess.run(
        [str(package), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
         "/NOCANCEL"],
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
    data = paths.data_dir().resolve()
    target = Path(target).resolve()
    if data == target or data.is_relative_to(target):
        raise OSError(
            "Your progress is stored inside the application folder (%s), so "
            "replacing it would delete your data. Move the folder, or set "
            "OPERATORS_CONSOLE_HOME elsewhere, then update again." % data)


def _apply_archive(package: Path, target: Path) -> Path:
    """Replace a portable build with the contents of a zip or tarball."""
    import shutil
    import tarfile
    import zipfile

    _guard_user_data(target)

    unpacked = Path(tempfile.mkdtemp(prefix="opcon-update-"))
    if package.suffix.lower() == ".zip":
        with zipfile.ZipFile(package) as archive:
            archive.extractall(unpacked)
    else:
        with tarfile.open(package) as archive:
            archive.extractall(unpacked)

    # Archives contain a single top-level folder; use it when present.
    entries = [p for p in unpacked.iterdir() if not p.name.startswith(".")]
    source = entries[0] if len(entries) == 1 and entries[0].is_dir() else unpacked

    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if destination.is_dir():
            shutil.rmtree(destination, ignore_errors=True)
        elif destination.exists():
            destination.unlink(missing_ok=True)
        shutil.move(str(item), str(destination))
    shutil.rmtree(unpacked, ignore_errors=True)

    executable = _executable_in(target)
    if executable.exists() and sys.platform != "win32":
        executable.chmod(0o755)
    return executable


def _apply_macos_dmg(package: Path, target: Path) -> Path:
    """Copy the .app out of a disk image, over the installed one."""
    import shutil

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
        shutil.rmtree(staged, ignore_errors=True)
        shutil.copytree(fresh, staged, symlinks=True)
        shutil.rmtree(destination, ignore_errors=True)
        staged.rename(destination)
    finally:
        subprocess.run(["hdiutil", "detach", str(mount), "-quiet"], check=False)
        shutil.rmtree(mount, ignore_errors=True)

    subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(destination)],
                   check=False)
    return destination / "Contents" / "MacOS" / "operators-console"


def _apply_appimage(package: Path, target: Path) -> Path:
    """Swap the AppImage file this process was launched from."""
    import shutil

    current = Path(os.environ.get("APPIMAGE") or (target / "operators-console"))
    shutil.move(str(package), str(current))
    current.chmod(0o755)
    return current

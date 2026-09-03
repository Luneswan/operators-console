"""One command to produce an installable build on any platform.

    python packaging/build.py            freeze the app for this platform
    python packaging/build.py --installer  also produce the installer

Windows  -> dist/operators-console/ and an Inno Setup .exe if iscc is present
macOS    -> dist/Operator's Console.app and a .dmg via hdiutil
Linux    -> dist/operators-console/, a .tar.gz, and a .deb if dpkg-deb is there
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
BUILD = ROOT / "build"

sys.path.insert(0, str(SRC))
from operators_console.version import APP_ID, APP_NAME, __version__  # noqa: E402


def run(command, **kwargs) -> int:
    printable = " ".join(str(part) for part in command)
    print("->", printable)
    return subprocess.call(command, **kwargs)


def need(tool: str) -> str | None:
    return shutil.which(tool)


def make_icons() -> None:
    run([sys.executable, str(HERE / "make_icons.py")])
    if sys.platform == "darwin":
        iconset = HERE / "icons" / "operators-console.iconset"
        icns = HERE / "icons" / "operators-console.icns"
        if need("iconutil") and iconset.is_dir():
            run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)])


def _remove_tree(folder: Path, attempts: int = 8) -> None:
    """Delete a build folder that something else may still be holding.

    On Windows a just-exited process, an antivirus scan or a file-sync client
    can keep a handle open for several seconds. Renaming first almost always
    succeeds even when deleting does not, which unblocks the build; the stale
    directory is then removed at leisure.
    """
    import time
    import uuid

    if not folder.exists():
        return
    for attempt in range(attempts):
        try:
            shutil.rmtree(folder)
            return
        except (PermissionError, OSError):
            if attempt < 3:
                time.sleep(1.0 + attempt)
                continue
            stale = folder.with_name("%s.old-%s" % (folder.name, uuid.uuid4().hex[:8]))
            try:
                folder.rename(stale)
                shutil.rmtree(stale, ignore_errors=True)
                return
            except OSError:
                time.sleep(2.0)
    raise RuntimeError(
        "Could not clear %s. Close the application, pause any file-sync "
        "client, and try again." % folder)


def freeze() -> Path:
    if not need("pyinstaller"):
        print("PyInstaller is missing. Install it with:")
        print("    pip install pyinstaller")
        raise SystemExit(2)
    for folder in (BUILD, DIST):
        _remove_tree(folder)
    code = run(["pyinstaller", "--noconfirm", "--clean",
                "--distpath", str(DIST), "--workpath", str(BUILD),
                str(HERE / "operators-console.spec")])
    if code != 0:
        raise SystemExit(code)
    target = DIST / ("Operator's Console.app" if sys.platform == "darwin"
                     else "operators-console")
    print("built", target)
    return target


def find_iscc() -> str | None:
    """Inno Setup rarely puts itself on PATH, so look where it installs."""
    found = need("iscc") or need("ISCC")
    if found:
        return found
    for root in (os.environ.get("ProgramFiles(x86)"),
                 os.environ.get("ProgramFiles"),
                 "C:/Program Files (x86)", "C:/Program Files"):
        if not root:
            continue
        for version in ("6", "5", ""):
            candidate = Path(root) / ("Inno Setup %s" % version).strip() / "ISCC.exe"
            if candidate.exists():
                return str(candidate)
    return None


def portable_zip(folder: Path) -> Path:
    """A zip of the frozen folder: unzip anywhere, double-click, no install."""
    import zipfile

    system = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
    archive = DIST / ("%s-%s-%s-portable.zip" % (APP_ID, __version__, system))
    if archive.exists():
        archive.unlink()
    root = folder.parent
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root))
    print("built", archive)
    return archive


def windows_installer() -> None:
    iscc = find_iscc()
    script = HERE / "windows" / "installer.iss"
    if not iscc:
        print("Inno Setup (iscc) not found - skipping the .exe installer.")
        print("Install it from https://jrsoftware.org/isdl.php, then re-run.")
        return
    run([iscc, "/DAppVersion=" + __version__, str(script)])


def macos_installer(app: Path) -> None:
    if not need("hdiutil"):
        print("hdiutil not found - skipping the .dmg.")
        return
    dmg = DIST / ("%s-%s.dmg" % (APP_ID, __version__))
    staging = BUILD / "dmg"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    shutil.copytree(app, staging / app.name, symlinks=True)
    os.symlink("/Applications", staging / "Applications")
    if dmg.exists():
        dmg.unlink()
    run(["hdiutil", "create", "-volname", APP_NAME, "-srcfolder", str(staging),
         "-ov", "-format", "UDZO", str(dmg)])
    print("built", dmg)


def linux_tarball(folder: Path) -> Path:
    archive = DIST / ("%s-%s-linux-x86_64.tar.gz" % (APP_ID, __version__))
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(folder, arcname=folder.name)
    print("built", archive)
    return archive


def linux_deb(folder: Path) -> None:
    if not need("dpkg-deb"):
        print("dpkg-deb not found - skipping the .deb.")
        return
    stage = BUILD / "deb"
    if stage.exists():
        shutil.rmtree(stage)
    (stage / "DEBIAN").mkdir(parents=True)
    opt = stage / "opt" / APP_ID
    opt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(folder, opt)

    (stage / "usr" / "bin").mkdir(parents=True)
    launcher = stage / "usr" / "bin" / APP_ID
    launcher.write_text("#!/bin/sh\nexec /opt/%s/%s \"$@\"\n" % (APP_ID, APP_ID),
                        encoding="utf-8")
    launcher.chmod(0o755)

    apps = stage / "usr" / "share" / "applications"
    apps.mkdir(parents=True)
    shutil.copy(HERE / "linux" / (APP_ID + ".desktop"), apps)
    for size in (48, 128, 256, 512):
        icons = (stage / "usr" / "share" / "icons" / "hicolor"
                 / ("%dx%d" % (size, size)) / "apps")
        icons.mkdir(parents=True, exist_ok=True)
        shutil.copy(HERE / "icons" / ("operators-console-%d.png" % size),
                    icons / (APP_ID + ".png"))

    control = (
        "Package: %s\n"
        "Version: %s\n"
        "Section: education\n"
        "Priority: optional\n"
        "Architecture: amd64\n"
        "Depends: libgl1, libegl1, libxkbcommon0, libfontconfig1, libdbus-1-3\n"
        "Maintainer: Operator's Console <noreply@example.invalid>\n"
        "Description: A guided Python curriculum\n"
        " Graded exercises, projects, spaced review and progress tracking\n"
        " for learning Python from nothing to production engineering.\n"
    ) % (APP_ID, __version__)
    (stage / "DEBIAN" / "control").write_text(control, encoding="utf-8")

    deb = DIST / ("%s_%s_amd64.deb" % (APP_ID, __version__))
    run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(deb)])
    print("built", deb)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installer", action="store_true",
                        help="also build the platform installer")
    parser.add_argument("--skip-icons", action="store_true")
    args = parser.parse_args()

    if not args.skip_icons:
        make_icons()
    target = freeze()

    if args.installer:
        portable_zip(target)
        if sys.platform == "win32":
            windows_installer()
        elif sys.platform == "darwin":
            macos_installer(target)
        else:
            linux_tarball(target)
            linux_deb(target)
    print("\nDone. Output is in", DIST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

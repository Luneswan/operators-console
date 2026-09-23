"""Prove an installed build from before 1.1.0 can update itself - for real.

Builds throwaway installers from the SHIPPING installer.iss with only the
isolation fields changed (a fresh AppId, a scratch folder, no shortcuts),
installs the old build, and drives the old build's own updater exactly as
its launch_helper would. Nothing here may touch the real installation, and
the script checks that it did not.

    python packaging/windows/check_old_build_update.py
        <old_dist> <old_iss> <new_dist> <new_fixed_iss>
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ISCC = Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
REAL_DIR = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Operator's Console"
REAL_KEY = (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall"
            r"\{7C4B1E52-3D7A-4C1F-9B36-2E5F0A9D41C8}_is1")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TEST_GUID = "{%s}" % str(uuid.uuid4()).upper()
TEST_KEY = (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall"
            r"\%s_is1" % TEST_GUID)


def say(*parts):
    print(*parts, flush=True)


# -- the real installation must come out exactly as it went in ------------

def fingerprint_real():
    exe = REAL_DIR / "operators-console.exe"
    digest = hashlib.sha256(exe.read_bytes()).hexdigest() if exe.exists() else None
    key = subprocess.run(["reg", "query", REAL_KEY], capture_output=True,
                         text=True, creationflags=NO_WINDOW).stdout
    return digest, exe.stat().st_mtime if exe.exists() else None, key


# -- installers built from the shipping script -----------------------------

def sandbox_iss(source_iss: Path, dist: Path, version: str, install_dir: Path,
                out_dir: Path, name: str) -> Path:
    """The shipping script with only the isolation fields changed."""
    text = source_iss.read_text(encoding="utf-8")
    base = source_iss.parent
    text = re.sub(r"AppId=\{\{[0-9A-F-]+\}", "AppId={" + TEST_GUID, text)
    assert TEST_GUID in text, "AppId not replaced"
    text = text.replace('#define AppName "Operator\'s Console"',
                        '#define AppName "OpCon Update Sandbox"')
    icon = (base / ".." / "icons" / "operators-console.ico").resolve()
    licence = (base / ".." / ".." / "LICENSE").resolve()
    # Literal replacements: a Windows path is full of backslashes that a
    # regex template would read as escapes.
    for field, value in (("DefaultDirName", install_dir),
                         ("OutputDir", out_dir),
                         ("OutputBaseFilename", name),
                         ("SetupIconFile", icon),
                         ("LicenseFile", licence)):
        line = "%s=%s" % (field, value)
        text = re.sub(r"^%s=.*$" % field, lambda _m, _v=line: _v, text,
                      flags=re.M)
    source = '#define SourceDir "%s"' % dist
    text = re.sub(r"^#define SourceDir .*$", lambda _m, _v=source: _v, text,
                  flags=re.M)
    # No shortcuts anywhere on this machine.
    text = re.sub(r"^\[Icons\].*?(?=^\[)", "", text, flags=re.M | re.S)
    assert "[Icons]" not in text and "{autodesktop}" not in text
    # Evidence: every sandbox install writes a log to %TEMP%. Logging does not
    # change what Setup does.
    if "SetupLogging=" not in text:
        text = text.replace("[Setup]\n", "[Setup]\nSetupLogging=yes\n", 1)
    iss = out_dir / (name + ".iss")
    iss.write_text(text, encoding="utf-8")
    subprocess.run([str(ISCC), "/Q", "/DAppVersion=" + version, str(iss)],
                   check=True, creationflags=NO_WINDOW)
    setup = out_dir / (name + ".exe")
    assert setup.exists(), setup
    return setup


# -- probing an installed copy ---------------------------------------------

def installed_modules(install_dir: Path) -> set:
    listing = subprocess.run(
        [sys.executable, "-m", "PyInstaller.utils.cliutils.archive_viewer",
         "-l", "-r", str(install_dir / "operators-console.exe")],
        capture_output=True, text=True, creationflags=NO_WINDOW).stdout
    return set(re.findall(r"'(operators_console[\w.]*)'", listing))


def processes_in(install_dir: Path) -> list:
    """PIDs of any operators-console.exe running from this folder."""
    script = ("Get-Process operators-console -ErrorAction SilentlyContinue | "
              "Where-Object { $_.Path -like '%s*' } | "
              "ForEach-Object { $_.Id }" % str(install_dir).replace("'", "''"))
    out = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                         capture_output=True, text=True,
                         creationflags=NO_WINDOW).stdout
    return [int(x) for x in out.split() if x.isdigit()]


def kill_all(install_dir: Path) -> None:
    for pid in processes_in(install_dir):
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True, creationflags=NO_WINDOW)


def dead_pid() -> int:
    """A pid that belonged to a process which has already exited."""
    probe = subprocess.Popen([sys.executable, "-c", "pass"],
                             creationflags=NO_WINDOW)
    probe.wait()
    return probe.pid


def setup_logs() -> set:
    return set(Path(tempfile.gettempdir()).glob("Setup Log *.txt"))


def install(setup: Path, install_dir: Path, extra=()) -> None:
    subprocess.run([str(setup), "/VERYSILENT", "/SUPPRESSMSGBOXES",
                    "/NORESTART", "/SP-", "/DIR=%s" % install_dir, *extra],
                   check=True, creationflags=NO_WINDOW, timeout=300)


def uninstall(install_dir: Path) -> None:
    kill_all(install_dir)
    for uninst in sorted(install_dir.glob("unins*.exe")):
        subprocess.run([str(uninst), "/VERYSILENT", "/SUPPRESSMSGBOXES",
                        "/NORESTART"], creationflags=NO_WINDOW, timeout=300)
        break
    time.sleep(3)
    shutil.rmtree(install_dir, ignore_errors=True)


# -- one scenario: the old build's own updater, driven as it drives itself --

def old_build_updates(label: str, old_setup: Path, new_setup: Path,
                      root: Path) -> dict:
    say("\n=== %s ===" % label)
    install_dir = root / ("install-" + label)
    data_dir = root / ("data-" + label)
    shutil.rmtree(install_dir, ignore_errors=True)
    shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir(parents=True)
    install(old_setup, install_dir)
    before = installed_modules(install_dir)
    say("installed old build: has ui.focus =", "operators_console.ui.focus" in before)

    env = dict(os.environ, OPERATORS_CONSOLE_HOME=str(data_dir),
               QT_QPA_PLATFORM="offscreen")
    logs_before = setup_logs()
    # Exactly what the old launch_helper runs, but with a parent that is gone.
    argv = [str(install_dir / "operators-console.exe"), "--apply-update",
            str(new_setup), "--pid", str(dead_pid()), "--kind", "installed",
            "--target", str(install_dir)]
    say("helper:", " ".join(argv[1:]))
    helper = subprocess.Popen(argv, env=env, creationflags=NO_WINDOW)
    started = time.monotonic()
    try:
        code = helper.wait(timeout=240)
    except subprocess.TimeoutExpired:
        code = "timeout"
    took = time.monotonic() - started
    time.sleep(6)                               # a relaunch is nowait

    after = installed_modules(install_dir)
    relaunched = processes_in(install_dir)
    log = data_dir / "update.log"
    new_logs = sorted(setup_logs() - logs_before)
    result = {
        "helper_exit": code,
        "seconds": round(took, 1),
        "now_new_build": "operators_console.ui.focus" in after,
        "relaunched_pids": relaunched,
        "update_log": log.read_text(encoding="utf-8") if log.exists() else "",
        "setup_log_tail": "",
    }
    if new_logs:
        text = new_logs[-1].read_text(encoding="utf-8", errors="replace")
        keep = [ln for ln in text.splitlines()
                if re.search(r"Restart Manager|close|Closing|in use|Error|"
                             r"Abort|Installation process succeeded|"
                             r"Setup exit code|Need to restart|Filename:",
                             ln, re.I)]
        result["setup_log_tail"] = "\n".join(keep[-25:])
    for key, value in result.items():
        say("  %-16s %s" % (key, value if key != "setup_log_tail" else ""))
    if result["setup_log_tail"]:
        say("  --- setup log (filtered) ---")
        say("  " + result["setup_log_tail"].replace("\n", "\n  "))
    uninstall(install_dir)
    return result


def norelaunch_is_honoured(new_setup: Path, root: Path) -> dict:
    """The 1.1.0 updater passes /NORELAUNCH and restarts the app itself."""
    say("\n=== the installer's own relaunch ===")
    out = {}
    for flag in ([], ["/NORELAUNCH"]):
        install_dir = root / ("install-relaunch-%s" % ("no" if flag else "yes"))
        shutil.rmtree(install_dir, ignore_errors=True)
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen",
                   OPERATORS_CONSOLE_HOME=str(root / "data-relaunch"))
        subprocess.run([str(new_setup), "/VERYSILENT", "/SUPPRESSMSGBOXES",
                        "/NORESTART", "/SP-", "/DIR=%s" % install_dir, *flag],
                       check=True, creationflags=NO_WINDOW, env=env,
                       timeout=300)
        time.sleep(6)
        running = processes_in(install_dir)
        out["with /NORELAUNCH" if flag else "without"] = len(running)
        say("  %-18s app processes started: %d"
            % ("with /NORELAUNCH" if flag else "without flag", len(running)))
        uninstall(install_dir)
    return out


def main() -> int:
    old_dist, old_iss, new_dist, new_iss = (Path(a).resolve()
                                            for a in sys.argv[1:5])
    # A short root: PySide's nested plugin folders under the scratchpad path
    # overflow MAX_PATH, and Inno cannot compress what it cannot open.
    short = Path(tempfile.gettempdir()) / "ocsb"
    shutil.rmtree(short, ignore_errors=True)
    shutil.copytree(old_dist, short / "old")
    shutil.copytree(new_dist, short / "new")
    old_dist, new_dist = short / "old", short / "new"
    root = short / "run"
    root.mkdir(parents=True)
    say("test AppId:", TEST_GUID)
    real_before = fingerprint_real()
    say("real install fingerprint taken:", (real_before[0] or "none")[:16])

    results = {}
    try:
        old_setup = sandbox_iss(old_iss, old_dist, "1.0.2",
                                root / "install-default", root, "old-1.0.2-setup")
        asis_setup = sandbox_iss(old_iss, new_dist, "1.1.0",
                                 root / "install-default", root,
                                 "new-1.1.0-setup-shipping-script-before-fix")
        fixed_setup = sandbox_iss(new_iss, new_dist, "1.1.0",
                                  root / "install-default", root,
                                  "new-1.1.0-setup-fixed")
        results["before_fix"] = old_build_updates("before-fix", old_setup,
                                                  asis_setup, root)
        results["after_fix"] = old_build_updates("after-fix", old_setup,
                                                 fixed_setup, root)
        results["relaunch"] = norelaunch_is_honoured(fixed_setup, root)
    finally:
        for folder in root.glob("install-*"):
            uninstall(folder)
        leftover = subprocess.run(["reg", "query", TEST_KEY],
                                  capture_output=True, text=True,
                                  creationflags=NO_WINDOW).returncode == 0
        say("\ntest registry key left behind:", leftover)
        if leftover:
            subprocess.run(["reg", "delete", TEST_KEY, "/f"],
                           capture_output=True, creationflags=NO_WINDOW)
            say("  removed it")

    real_after = fingerprint_real()
    same = real_before == real_after
    say("real install untouched:", same)
    say("\nSUMMARY before-fix updated=%s  after-fix updated=%s  relaunch=%s"
        % (results.get("before_fix", {}).get("now_new_build"),
           results.get("after_fix", {}).get("now_new_build"),
           results.get("relaunch")))
    return 0 if same else 2


if __name__ == "__main__":
    sys.exit(main())

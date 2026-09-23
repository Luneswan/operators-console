"""The one-line installers and the workflow that feeds them.

`irm ... | iex` and `curl ... | sh` hand a stranger's script to a shell, and
the script then downloads a binary and runs it. None of that can be tested by
running it here, so these are structural checks: that the verification exists,
that it is not optional by accident, that the refusals say what the audit says
they say, and that the program directory can never be the progress directory.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from operators_console.core.updates import (
    MISMATCH_MESSAGE, NO_SUMS_MESSAGE, SUMS_NAME,
)

ROOT = Path(__file__).resolve().parent.parent
PS1 = (ROOT / "install.ps1").read_text(encoding="utf-8")
SH = (ROOT / "install.sh").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "build.yml").read_text(
    encoding="utf-8")


# ---------------------------------------------------------------------------
# the release publishes what the installers check against
# ---------------------------------------------------------------------------

def test_the_release_workflow_publishes_a_checksum_manifest():
    assert "sha256sum" in WORKFLOW
    assert SUMS_NAME in WORKFLOW
    # It has to be produced before the upload step, or it is not in the release.
    assert WORKFLOW.index("sha256sum") < WORKFLOW.index("action-gh-release")


def test_the_manifest_covers_every_artefact():
    """`sha256sum -- *` over the merged artefact folder, not a hand-written list."""
    assert re.search(r"sha256sum\s+--\s+\*\s*>\s*%s" % SUMS_NAME, WORKFLOW)


def test_the_release_uploads_the_manifest_with_the_binaries():
    assert "files: artifacts/*" in WORKFLOW


# ---------------------------------------------------------------------------
# install.ps1
# ---------------------------------------------------------------------------

def test_the_windows_installer_fetches_and_checks_the_manifest():
    assert "SHA256SUMS" in PS1
    assert "Get-FileHash" in PS1
    assert "-Algorithm SHA256" in PS1


def test_the_windows_installer_refuses_a_release_with_no_manifest():
    assert NO_SUMS_MESSAGE.split(",")[0] in PS1
    assert "Refusing to install it" in PS1


def test_the_windows_installer_refuses_a_tampered_download():
    assert MISMATCH_MESSAGE in PS1


def test_the_windows_installer_only_skips_verification_on_purpose():
    assert "[switch] $SkipVerify" in PS1
    # The skip has to be an explicit choice, not the fallback when a lookup
    # quietly fails.
    assert "if (-not $SkipVerify)" in PS1


def test_the_windows_installer_refuses_a_plain_http_url():
    assert "function Assert-Https" in PS1
    assert "https://" in PS1
    for call in ("Assert-Https $sumsAsset.browser_download_url",
                 "Assert-Https $asset.browser_download_url"):
        assert call in PS1


def test_the_windows_installer_stops_a_running_copy_before_replacing_it():
    assert "CloseMainWindow" in PS1
    assert "Stop-Process" in PS1
    # Ask first, force second.
    assert PS1.index("CloseMainWindow") < PS1.index("Stop-Process")


def test_the_windows_installer_never_expands_over_the_live_install():
    """Expand-Archive -Force must land in a staging folder, not the target."""
    expand = re.search(r"Expand-Archive[^\n]*", PS1).group(0)
    assert "$staging" in expand
    assert "$target" not in expand


def test_the_windows_installer_puts_the_old_build_back_on_failure():
    assert "$previous" in PS1
    assert "the previous version was put back" in PS1


def test_the_windows_program_directory_is_not_the_progress_directory():
    assert "LOCALAPPDATA" in PS1 and "Programs" in PS1
    assert "$env:APPDATA\\Operator's Console" in PS1
    # The program goes under LOCALAPPDATA, the progress under APPDATA.
    assert "Join-Path $env:APPDATA" not in PS1


def test_the_windows_installer_still_creates_the_shortcut():
    assert "CreateShortcut" in PS1
    assert "Operator's Console.lnk" in PS1


# ---------------------------------------------------------------------------
# install.sh
# ---------------------------------------------------------------------------

def test_the_unix_installer_fetches_and_checks_the_manifest():
    assert "SHA256SUMS" in SH
    assert "sha256_of" in SH
    assert "sha256sum" in SH and "shasum -a 256" in SH


def test_the_unix_installer_refuses_a_release_with_no_manifest():
    assert NO_SUMS_MESSAGE.split(",")[0] in SH
    assert "Refusing to install it" in SH


def test_the_unix_installer_refuses_a_tampered_download():
    assert MISMATCH_MESSAGE in SH


def test_the_unix_installer_only_skips_verification_on_purpose():
    assert "OPCON_SKIP_VERIFY" in SH
    assert '"${OPCON_SKIP_VERIFY:-0}" = "1"' in SH


def test_the_unix_installer_pins_https_on_the_redirect_too():
    """curl follows a redirect off https unless told not to."""
    assert "--proto =https" in SH
    assert "--proto-redir =https" in SH
    assert "https_only()" in SH
    # Every download goes through the guard.
    for line in SH.splitlines():
        if "$CURL" in line and "-o " in line:
            assert "https_only" in line or "$API" in line, line


def test_the_unix_installer_verifies_before_it_installs():
    """The checksum has to be checked before hdiutil or chmod +x."""
    assert SH.index('verify "$TMP/$NAME" "$NAME"') < SH.index("hdiutil attach")
    linux = SH[SH.index("Linux ----"):]
    assert linux.index('verify "$TMP/$NAME" "$NAME"') \
        < linux.index('chmod +x "$TMP/$NAME"')


def test_the_unix_installer_stops_a_running_copy():
    assert "stop_running" in SH
    assert "pkill" in SH


def test_the_linux_program_directory_is_not_the_progress_directory():
    """They used to be the same folder, with progress.db beside the AppImage.

    core/paths.py puts the store at $XDG_DATA_HOME/operators-console. An
    installer that unpacked the application into that same folder put the
    learner's only irreplaceable file one `rm -rf` from the program it was
    replacing.
    """
    assert 'APP_DIR="${OPCON_APP_DIR:-$HOME/.local/opt/$APP_ID}"' in SH
    assert 'STORE_DIR="$DATA_ROOT/$APP_ID"' in SH
    # And it refuses to run if someone points them at each other.
    assert 'case "$APP_DIR" in' in SH
    assert "is inside the progress directory" in SH


def test_the_linux_installer_migrates_an_old_layout_without_touching_the_store():
    """It removes the stale AppImage and nothing else in that folder."""
    assert 'OLD_IMAGE="$STORE_DIR/$APP_ID.AppImage"' in SH
    assert 'rm -f "$OLD_IMAGE"' in SH
    assert 'rm -rf "$STORE_DIR"' not in SH
    assert 'rm -rf "$OLD_IMAGE"' not in SH


def test_the_unix_installer_puts_the_old_build_back_on_failure():
    assert ".previous" in SH
    assert "the previous version was put back" in SH


def test_the_macos_roots_stay_separate():
    assert 'TARGET="$HOME/Applications"' in SH
    assert "Library/Application Support" in SH


def test_the_desktop_entry_points_at_the_new_location():
    assert "Exec=$TARGET_IMAGE" in SH


# ---------------------------------------------------------------------------
# what the one-liners actually promise
# ---------------------------------------------------------------------------

SCRIPTS = [pytest.param(PS1, "install.ps1", id="ps1"),
           pytest.param(SH, "install.sh", id="sh")]


@pytest.mark.parametrize("text,name", SCRIPTS)
def test_the_trust_root_is_stated_in_the_script(text, name):
    """A reader piping this into a shell deserves to know what they trust."""
    # Both files carry the note in a comment block, so drop the markers
    # before flattening or "# " lands in the middle of a sentence.
    flat = " ".join(
        " ".join(line.lstrip().lstrip("#").split())
        for line in text.lower().splitlines()).strip()
    flat = " ".join(flat.split())
    assert "trust root" in flat, name
    assert "does not prove who published" in flat, name


@pytest.mark.parametrize("text,name", SCRIPTS)
def test_the_scripts_say_the_progress_folder_is_never_touched(text, name):
    assert "never touch" in text.lower(), name


# ---------------------------------------------------------------------------
# what install.ps1 says matches what it does
# ---------------------------------------------------------------------------

def _ps1_installer_arguments() -> list[str]:
    match = re.search(r"\$arguments\s*=\s*@\(([^)]*)\)", PS1)
    assert match, "install.ps1 no longer builds an argument list"
    return re.findall(r"'([^']*)'", match.group(1))


def test_the_windows_installer_message_matches_the_relaunch():
    """A silent run reopens the app unless /NORELAUNCH is passed.

    The closing line must say whichever of the two is true.
    """
    arguments = _ps1_installer_arguments()
    assert "/SILENT" in arguments or "/VERYSILENT" in arguments
    done = [line for line in PS1.splitlines()
            if "Write-Step 'Done." in line and "Start menu" in line]
    assert len(done) == 1, done
    if "/NORELAUNCH" in arguments:
        assert "open" not in done[0].lower(), done[0]
    else:
        assert "opening now" in done[0], done[0]


def test_the_windows_portable_pattern_finds_both_spellings():
    """-Portable must find the 1.1.0 name and the name of older releases."""
    match = re.search(r"if \(\$Portable\) \{ '([^']+)' \}", PS1)
    assert match, "install.ps1 no longer picks the portable zip by pattern"
    pattern = match.group(1)
    # PowerShell -like: '*' is any run of characters, case-insensitive.
    regex = "^" + ".*".join(re.escape(p) for p in pattern.split("*")) + "$"
    for name in ("operators-console-1.1.0-windows-x64-portable.zip",
                 "operators-console-1.0.2-windows-portable.zip"):
        assert re.match(regex, name, re.IGNORECASE), (pattern, name)
    assert not re.match(regex, "operators-console-1.1.0-macos-arm64-portable.zip",
                        re.IGNORECASE)


def test_the_windows_installer_decodes_the_manifest_on_powershell_5():
    """GitHub serves SHA256SUMS as application/octet-stream, and Windows
    PowerShell 5.1 then returns Invoke-WebRequest content as bytes. Split as
    a string, the bytes never matched a line, and every install on 5.1 was
    refused with "This release does not publish a SHA256SUMS file"."""
    lookup = PS1[PS1.index("$sumsAsset = "):PS1.index("if (-not $expected)")]
    assert "-is [byte[]]" in lookup
    assert "[Text.Encoding]::UTF8.GetString($sums)" in lookup
    assert lookup.index("GetString") < lookup.index("-split")


def test_a_manifest_without_this_file_is_not_called_missing():
    assert "has no entry for $($asset.name)" in PS1

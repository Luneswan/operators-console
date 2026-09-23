"""The shape a release must have for every build out there to update.

Builds 1.0.0 to 1.0.2 (commit 7ad8750) are already on learners' machines and
cannot be changed. They find their download by looking for fixed text in the
file names, so the release is the only lever left. These tests pin that
recipe: the tag, the exact file names, the checksum manifest, and that the
Windows portable zip is invisible to the old picker - whose portable swap
damages the folder it runs from.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from operators_console.core import updates
from operators_console.core.updates import Asset, Release, parse_version
from operators_console.version import APP_ID, __version__

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = (ROOT / ".github" / "workflows" / "build.yml").read_text(
    encoding="utf-8")
ISS = (ROOT / "packaging" / "windows" / "installer.iss").read_text(
    encoding="utf-8")


def _load_build():
    spec = importlib.util.spec_from_file_location(
        "opcon_packaging_build", ROOT / "packaging" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = _load_build()
ASSETS = build.release_assets(__version__)
SETUP = "%s-%s-windows-setup.exe" % (APP_ID, __version__)
PORTABLE = "%s-%s-windows-x64-portable.zip" % (APP_ID, __version__)


def _release(names) -> Release:
    names = list(names) + [updates.SUMS_NAME]
    return Release(
        version=parse_version("v" + __version__), tag="v" + __version__,
        name="v" + __version__, notes="", url="https://example.invalid/r",
        assets=tuple(Asset(n, "https://example.invalid/" + n, 1)
                     for n in names))


def old_pick_asset(release: Release, kind: str, platform: str):
    """The picker shipped in 1.0.0-1.0.2, as it is in commit 7ad8750.

    Copied rather than imported: the point is that it can never change.
    (Its macOS branch is left out; nothing here depends on it.)
    """
    def find(*needles):
        for asset in release.assets:
            name = asset.name.lower()
            if all(needle.lower() in name for needle in needles):
                return asset
        return None

    if platform == "win32":
        if kind == "installed":
            return find("windows", "setup.exe") or find("windows-portable.zip")
        return find("windows-portable.zip")
    if kind == "appimage":
        return find(".appimage")
    return find("linux-portable.zip") or find("linux", ".tar.gz")


# -- the tag ----------------------------------------------------------------

def test_a_version_tag_triggers_the_release():
    assert re.search(r'tags:\s*\["v\*"\]', WORKFLOW)
    assert "startsWith(github.ref, 'refs/tags/v')" in WORKFLOW


def test_the_tag_must_match_version_py(tmp_path):
    for name in ASSETS:
        (tmp_path / name).write_bytes(b"x")
    assert build.check_release(tmp_path, "v" + __version__) == []
    problems = build.check_release(tmp_path, "v0.0.1")
    assert len(problems) == 1 and "does not match version.py" in problems[0]
    # Without the "v" the workflow never runs; the check agrees.
    assert build.check_release(tmp_path, __version__)


def test_the_release_job_runs_the_check_before_publishing():
    check = WORKFLOW.index("--check-release artifacts")
    assert '--tag "${GITHUB_REF_NAME}"' in WORKFLOW
    assert check < WORKFLOW.index("sha256sum -- *")
    assert check < WORKFLOW.index("action-gh-release")


def test_a_published_release_is_the_latest_and_not_a_draft():
    publish = WORKFLOW[WORKFLOW.index("action-gh-release"):]
    assert "draft: false" in publish
    assert "prerelease: false" in publish
    assert "fail_on_unmatched_files: true" in publish


# -- the names --------------------------------------------------------------

def test_the_windows_names_are_exact():
    assert SETUP in ASSETS
    assert PORTABLE in ASSETS
    assert build.windows_installer_name(__version__) == SETUP
    assert build.portable_zip_name("win32", __version__) == PORTABLE


def test_the_installer_script_produces_the_installer_name():
    match = re.search(r"^OutputBaseFilename=(.+)$", ISS, re.MULTILINE)
    produced = (match.group(1).strip()
                .replace("{#AppId}", APP_ID)
                .replace("{#AppVersion}", __version__)) + ".exe"
    assert produced == SETUP


def test_no_expected_name_is_one_the_old_portable_picker_takes():
    assert not any("windows-portable.zip" in n.lower() for n in ASSETS)


def test_a_missing_file_stops_the_release(tmp_path):
    for name in ASSETS:
        if name != SETUP:
            (tmp_path / name).write_bytes(b"x")
    assert build.check_release(tmp_path, "v" + __version__) == [
        "Missing: " + SETUP]


def test_an_old_style_portable_name_stops_the_release(tmp_path):
    for name in ASSETS:
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / ("%s-%s-windows-portable.zip" % (APP_ID, __version__))) \
        .write_bytes(b"x")
    problems = build.check_release(tmp_path, "v" + __version__)
    assert len(problems) == 1 and "before 1.1.0" in problems[0]


# -- what each build picks from this release ---------------------------------

def test_an_old_installed_windows_build_picks_the_installer():
    chosen = old_pick_asset(_release(ASSETS), "installed", "win32")
    assert chosen is not None and chosen.name == SETUP


def test_an_old_portable_windows_build_finds_nothing_to_install():
    """So it says "no download for your platform" instead of breaking."""
    assert old_pick_asset(_release(ASSETS), "portable", "win32") is None


@pytest.mark.parametrize("kind,expected", [
    (updates.INSTALLED, SETUP),
    (updates.PORTABLE, PORTABLE),
])
def test_the_current_windows_picker_finds_both(monkeypatch, kind, expected):
    monkeypatch.setattr(updates.sys, "platform", "win32")
    chosen = updates.pick_asset(_release(ASSETS), kind)
    assert chosen is not None and chosen.name == expected


@pytest.mark.parametrize("kind", ["appimage", "portable"])
def test_old_and_new_linux_builds_agree(monkeypatch, kind):
    monkeypatch.setattr(updates.sys, "platform", "linux")
    old = old_pick_asset(_release(ASSETS), kind, "linux")
    new = updates.pick_asset(_release(ASSETS), kind)
    assert old is not None and new is not None and old.name == new.name


@pytest.mark.parametrize("machine", ["arm64", "x86_64"])
def test_each_mac_finds_its_own_disk_image(monkeypatch, machine):
    monkeypatch.setattr(updates.sys, "platform", "darwin")
    monkeypatch.setattr(updates.platform, "machine", lambda: machine)
    chosen = updates.pick_asset(_release(ASSETS), updates.MACAPP)
    assert chosen.name == "%s-%s-macos-%s.dmg" % (APP_ID, __version__, machine)


# -- the checksum manifest ---------------------------------------------------

def test_the_release_publishes_sha256sums_over_every_file():
    assert "sha256sum -- * > SHA256SUMS" in WORKFLOW
    assert "sha256sum -c SHA256SUMS" in WORKFLOW
    assert WORKFLOW.index("sha256sum -- *") < WORKFLOW.index(
        "action-gh-release")


def test_the_current_build_needs_the_manifest_to_call_it_verified():
    release = _release(ASSETS)
    stamped = tuple(Asset(a.name, a.url, a.size, "a" * 64)
                    for a in release.assets if a.name != updates.SUMS_NAME)
    assert all(a.sha256 for a in stamped)
    assert updates.parse_sums("%s  %s\n" % ("a" * 64, SETUP)) == {
        SETUP: "a" * 64}


def test_the_release_notes_are_the_body_and_speak_to_old_builds_first():
    # softprops/action-gh-release reads body_path; body_file is ignored
    # silently, which is how 1.1.0 first shipped with no notes.
    assert "body_path: .github/RELEASE_NOTES.md" in WORKFLOW
    assert "body_file:" not in WORKFLOW
    notes = (ROOT / ".github" / "RELEASE_NOTES.md").read_text(
        encoding="utf-8")
    # The 1.0.x update dialog shows the first 700 characters of the body.
    assert "1.0" in notes[:700] and "windows-setup.exe" in notes[:700]
    assert "SHA256SUMS" in notes
    assert "no network calls" not in notes


# -- the README a downloader reads describes this release ---------------------

README = (ROOT / "README.md").read_text(encoding="utf-8")


def _readme_number(pattern: str) -> int:
    match = re.search(pattern, README)
    assert match, "README.md no longer says: %s" % pattern
    return int(match.group(1).replace(",", ""))


def test_the_readme_counts_match_the_shipped_content():
    """The numbers in "What is in it" are the ones the app ships.

    Content is added often; when this fails, update README.md, not the test.
    """
    from operators_console.core import curriculum
    course = curriculum.load()
    items = sum(len(p.items) for p in course.phases)
    gates = sum(len(p.gate.items) for p in course.phases if p.gate)
    expected = {
        r"\*\*(\d+) phases\*\*": len(course.phases),
        r"\*\*(\d+) tracked steps\*\*": items + gates,
        r"(\d+) study steps plus": items,
        r"plus (\d+) gate checks": gates,
        r"\*\*(\d+) graded exercises\*\*": len(course.exercises),
        r"\| ([\d,]+) individual checks": sum(len(e.tests)
                                             for e in course.exercises),
        r"\*\*(\d+) quiz questions\*\*": sum(len(q.questions)
                                             for q in course.quizzes),
        r"In (\d+) quizzes": len(course.quizzes),
        r"\*\*(\d+) projects\*\*": len(course.projects),
        r"(\d+) requirements between them": sum(len(p.requirements)
                                                for p in course.projects),
        r"\*\*(\d+) tracks\*\*": len(course.tracks),
        r"\*\*(\d+) fields,": len(course.fields),
        r"(\d+) certificates,": len(course.certs),
        r"(\d+) shelves\*\*": len(course.shelf),
    }
    wrong = {p: (_readme_number(p), n) for p, n in expected.items()
             if _readme_number(p) != n}
    assert not wrong, "README says / the app ships: %s" % wrong


def test_the_readme_names_the_screenshots_that_exist_in_the_release():
    shots = re.findall(r"docs/screenshots/([\w-]+\.png)", README)
    assert sorted(set(shots)) == sorted({
        "today-light.png", "today-dark.png", "roadmap-light.png",
        "practice-light.png", "practice-dark.png", "review-light.png"})


def test_the_readme_says_nothing_the_app_stopped_doing():
    for stale in ("no network calls", "120 tests", "the four things",
                  "windows-portable.zip", "192 grader runs"):
        assert stale not in README, stale

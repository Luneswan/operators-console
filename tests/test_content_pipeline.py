"""The shipped content bundles must match the sources they come from.

``src/operators_console/data/*.json`` are generated files: ``build_tools``
holds the authored material and the transform that produces them. Nothing
stopped someone editing a bundle by hand, and a hand-edit is destroyed the
next time anyone runs the pipeline - silently, because the app keeps working
until the missing field is the one a screen relies on.

This copies the pipeline into a temporary directory, runs it there and
compares. The date stamp is expected to move; nothing else is.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "build_tools"
DATA = ROOT / "src" / "operators_console" / "data"

# transform.py stamps the day it ran into the bundle.
VOLATILE = ("generated",)

BUILDERS = ("build_exercises.py", "build_projects.py", "transform.py")


def _without_volatile(bundle: dict) -> dict:
    return {k: v for k, v in bundle.items() if k not in VOLATILE}


def _run_pipeline(into: Path) -> Path:
    """Copy build_tools into `into` and run every builder there."""
    tools = into / "build_tools"
    tools.mkdir(parents=True)
    for source in list(TOOLS.glob("*.py")) + list(TOOLS.glob("*.json")):
        shutil.copy2(source, tools / source.name)
    shutil.copytree(TOOLS / "guides", tools / "guides")
    (into / "src" / "operators_console" / "data").mkdir(parents=True)

    for name in BUILDERS:
        script = tools / name
        if not script.exists():
            pytest.skip("%s is missing from build_tools" % name)
        done = subprocess.run(
            [sys.executable, name], cwd=str(tools), capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=600)
        assert done.returncode == 0, (
            "%s failed:\n%s" % (name, (done.stderr or done.stdout)[-2000:]))

    return into / "src" / "operators_console" / "data"


@pytest.fixture(scope="module")
def rebuilt(tmp_path_factory) -> Path:
    """The data directory the pipeline produces from today's sources."""
    if not TOOLS.is_dir():
        pytest.skip("build_tools is not part of this checkout")
    return _run_pipeline(tmp_path_factory.mktemp("pipeline"))


@pytest.mark.slow
@pytest.mark.parametrize("bundle", ["exercises.json", "projects.json"])
def test_the_bundle_is_exactly_what_its_sources_produce(rebuilt, bundle):
    shipped = json.loads((DATA / bundle).read_text(encoding="utf-8"))
    made = json.loads((rebuilt / bundle).read_text(encoding="utf-8"))
    assert shipped == made, (
        "%s no longer matches build_tools. Either it was edited by hand - put "
        "the change in build_tools instead, or the next run of the pipeline "
        "will delete it - or the pipeline changed and the bundle was not "
        "regenerated." % bundle)


@pytest.mark.slow
def test_the_curriculum_matches_its_sources_apart_from_the_date(rebuilt):
    shipped = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    made = json.loads((rebuilt / "curriculum.json").read_text(encoding="utf-8"))

    assert set(shipped) == set(made), (
        "the shipped curriculum has keys the pipeline does not produce: %s"
        % sorted(set(shipped) ^ set(made)))

    differing = [k for k in _without_volatile(shipped)
                 if shipped[k] != made.get(k)]
    assert not differing, (
        "curriculum.json differs from build_tools at %s. A hand-edit here is "
        "lost the next time transform.py runs: author it in build_tools "
        "(raw_curriculum.json or transform.py) and regenerate." % differing)


@pytest.mark.slow
def test_the_pipeline_is_deterministic(rebuilt, tmp_path):
    """Two runs of the same sources produce the same bundles."""
    again = _run_pipeline(tmp_path / "second")
    for bundle in ("exercises.json", "projects.json", "curriculum.json"):
        first = json.loads((rebuilt / bundle).read_text(encoding="utf-8"))
        repeat = json.loads((again / bundle).read_text(encoding="utf-8"))
        assert _without_volatile(first) == _without_volatile(repeat), (
            "%s is not deterministic: two runs of the same sources disagree, "
            "so a rebuild would show a spurious diff." % bundle)

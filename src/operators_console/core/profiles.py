"""Several people on one computer, each with their own progress.

A profile is a folder: its own progress.db, backups and exercise workspace.
The registry, profiles.json in the root data folder, lists them and records
which one is open. The first profile uses the root folder itself, so data
from before profiles existed becomes that profile without moving a file.

Removing a profile never deletes it: its folder moves to
root/removed-profiles, where it can be restored by hand.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass

from . import paths

DEFAULT_NAME = "Main profile"
NAME_LIMIT = 40


@dataclass(frozen=True, slots=True)
class Profile:
    id: str
    name: str
    created: str


def _registry_path():
    return paths.root_dir() / paths.PROFILES_FILE


def _load() -> dict:
    try:
        data = json.loads(_registry_path().read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError
    except (OSError, ValueError):
        data = {}
    entries = [p for p in data.get("profiles", [])
               if isinstance(p, dict) and p.get("id")]
    if not any(p["id"] == paths.DEFAULT_PROFILE for p in entries):
        entries.insert(0, {"id": paths.DEFAULT_PROFILE, "name": DEFAULT_NAME,
                           "created": ""})
    data["profiles"] = entries
    data.setdefault("active", paths.DEFAULT_PROFILE)
    return data


def _save(data: dict) -> None:
    target = _registry_path()
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                    encoding="utf-8")
    temp.replace(target)             # never a half-written registry


def clean_name(name: str) -> str:
    name = " ".join(str(name or "").split())[:NAME_LIMIT]
    if not name:
        raise ValueError("A profile needs a name.")
    return name


def profiles() -> list:
    return [Profile(p["id"], p.get("name") or DEFAULT_NAME,
                    p.get("created", "")) for p in _load()["profiles"]]


def active() -> Profile:
    current = paths.active_profile()
    for profile in profiles():
        if profile.id == current:
            return profile
    return profiles()[0]


def _slug(name: str, taken: set) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:24] or "profile"
    slug, n = base, 2
    while slug in taken or slug == paths.DEFAULT_PROFILE:
        slug = "%s-%d" % (base, n)
        n += 1
    return slug


def create(name: str) -> Profile:
    """A new, empty profile. It is not opened until switch() is called."""
    name = clean_name(name)
    data = _load()
    if any(p.get("name", "").casefold() == name.casefold()
           for p in data["profiles"]):
        raise ValueError("There is already a profile called %s." % name)
    pid = _slug(name, {p["id"] for p in data["profiles"]})
    paths.profile_dir(pid).mkdir(parents=True, exist_ok=True)
    entry = {"id": pid, "name": name,
             "created": time.strftime("%Y-%m-%d")}
    data["profiles"].append(entry)
    _save(data)
    return Profile(pid, name, entry["created"])


def rename(profile_id: str, name: str) -> None:
    name = clean_name(name)
    data = _load()
    for entry in data["profiles"]:
        if entry["id"] != profile_id and entry.get(
                "name", "").casefold() == name.casefold():
            raise ValueError("There is already a profile called %s." % name)
    for entry in data["profiles"]:
        if entry["id"] == profile_id:
            entry["name"] = name
            _save(data)
            return
    raise LookupError(profile_id)


def switch(profile_id: str) -> None:
    """Record `profile_id` as open. The caller reopens the database."""
    data = _load()
    if not any(p["id"] == profile_id for p in data["profiles"]):
        raise LookupError(profile_id)
    paths.profile_dir(profile_id).mkdir(parents=True, exist_ok=True)
    data["active"] = profile_id
    _save(data)
    paths.set_active_profile(profile_id)


def remove(profile_id: str) -> str:
    """Move a profile's folder aside and drop it from the list.

    The open profile and the main profile cannot be removed. Returns the
    folder the data was moved to.
    """
    if profile_id == paths.DEFAULT_PROFILE:
        raise ValueError("The main profile cannot be removed.")
    if profile_id == paths.active_profile():
        raise ValueError("Switch to another profile before removing this one.")
    data = _load()
    if not any(p["id"] == profile_id for p in data["profiles"]):
        raise LookupError(profile_id)
    source = paths.profile_dir(profile_id)
    parked = paths.root_dir() / "removed-profiles" / (
        "%s-%s" % (profile_id, time.strftime("%Y%m%d-%H%M%S")))
    if source.exists():
        parked.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(parked))
    data["profiles"] = [p for p in data["profiles"] if p["id"] != profile_id]
    _save(data)
    return str(parked)

"""Turn the extracted console data into the app's curriculum bundle.

Reads raw_curriculum.json (dumped straight out of the original HTML page) and
writes src/operators_console/data/curriculum.json with stable ids, estimated
effort, prerequisites and review-card seeds attached.
"""
from __future__ import annotations

import json
import re
import hashlib
from pathlib import Path
from datetime import date

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "src" / "operators_console" / "data"
DATA.mkdir(parents=True, exist_ok=True)

raw = json.loads((HERE / "raw_curriculum.json").read_text(encoding="utf-8"))


def slug(text: str, length: int = 8) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


# Effort estimates (hours) keyed by phase id. Derived from the "when" field of
# each phase at ~5 focused hours a day, six days a week.
WEEK_HOURS = 30
EST = {
    "ops": 1, "p00": 10, "p01": 120, "p02": 60, "p03": 30, "p04": 120,
    "p05": 60, "p06": 30, "p07": 60, "p08": 60, "p09": 60, "p10": 30,
    "p11": 30, "p12": 30, "p13": 30, "p14": 60, "p15": 120, "p16": 120,
    "p17": 90, "p18": 0, "p99": 0,
}

# Linear spine of the core path. Everything else is optional or parallel.
SPINE = ["p00", "p01", "p02", "p03", "p04", "p05", "p06", "p07", "p08",
         "p09", "p10", "p11", "p12", "p13", "p14", "p15", "p16"]

PREREQ = {}
for i, pid in enumerate(SPINE):
    PREREQ[pid] = [SPINE[i - 1]] if i else []
PREREQ["p17"] = ["p08", "p09"]
PREREQ["p18"] = ["p15"]
PREREQ["p99"] = ["p12"]
PREREQ["ops"] = []

# Topic tags let the adaptive planner rank phases against a learner's goals.
TAGS = {
    "ops": ["habits"],
    "p00": ["tooling", "git"],
    "p01": ["language", "fundamentals"],
    "p02": ["language", "advanced"],
    "p03": ["tooling", "packaging"],
    "p04": ["cs", "datastructures"],
    "p05": ["cs", "algorithms", "interview"],
    "p06": ["systems", "linux"],
    "p07": ["systems", "networking"],
    "p08": ["data", "sql", "backend"],
    "p09": ["backend", "web"],
    "p10": ["automation", "scraping", "web"],
    "p11": ["performance", "concurrency"],
    "p12": ["devops", "deployment"],
    "p13": ["security", "backend"],
    "p14": ["ai", "ml", "data"],
    "p15": ["architecture", "backend", "devops"],
    "p16": ["systems", "internals", "performance"],
    "p17": ["data", "engineering"],
    "p18": ["mastery"],
    "p99": ["mastery", "projects"],
}

# Difficulty band, used to sort a personalised roadmap gently.
LEVEL = {
    "ops": 0, "p00": 1, "p01": 1, "p02": 2, "p03": 2, "p04": 2, "p05": 3,
    "p06": 2, "p07": 3, "p08": 2, "p09": 3, "p10": 2, "p11": 4, "p12": 3,
    "p13": 4, "p14": 4, "p15": 5, "p16": 5, "p17": 4, "p18": 5, "p99": 5,
}


def plain(text: str) -> str:
    """Strip the page's <em> code markers for search and review-card text."""
    return re.sub(r"</?em>", "", text)


phases = []
for ph in raw["PHASES"]:
    pid = ph["id"]
    sections = []
    for si, sec in enumerate(ph["sections"]):
        items = []
        for ii, text in enumerate(sec["items"]):
            items.append({"id": f"{pid}.s{si}.{ii}", "text": text})
        sections.append({"id": f"{pid}.s{si}", "title": sec["h"], "items": items})

    gate = None
    if ph.get("gate"):
        gate = {
            "note": ph["gate"].get("note", ""),
            "items": [
                {"id": f"{pid}.g.{i}", "text": t}
                for i, t in enumerate(ph["gate"]["items"])
            ],
        }

    phases.append({
        "id": pid,
        "num": ph["num"],
        "name": ph["name"],
        "when": ph["when"],
        "aim": ph["aim"],
        "no_progress": bool(ph.get("noProgress")),
        "est_hours": EST.get(pid, 30),
        "level": LEVEL.get(pid, 3),
        "tags": TAGS.get(pid, []),
        "prereq": PREREQ.get(pid, []),
        "resources": [
            {"name": r["n"], "kind": r["k"], "why": r["w"], "url": r["u"]}
            for r in (ph.get("res") or [])
        ],
        "sections": sections,
        "snippet": ph.get("snippet") or "",
        "gate": gate,
    })

quizzes = []
for qz in raw["QUIZZES"]:
    questions = []
    for i, q in enumerate(qz["qs"]):
        questions.append({
            "id": f"{qz['id']}.{i}",
            "prompt": q["q"],
            "choices": q["a"],
            "correct": q["c"],
            "explain": q["e"],
        })
    quizzes.append({
        "id": qz["id"],
        "phase": qz["phase"],
        "name": qz["n"],
        "desc": qz["d"],
        "questions": questions,
    })

fields = []
for f in raw["FIELDS"]:
    fields.append({
        "id": f["id"],
        "group": f["g"],
        "name": f["n"],
        "blurb": f["blurb"],
        "build": f["build"],
        "libs": [{"name": n, "url": u} for n, u in f["libs"]],
    })

certs = [{
    "id": c["id"], "name": c["n"], "by": c["by"], "cost": c["cost"],
    "time": c["time"], "what": c["what"], "worth": c["worth"],
    "url": c.get("u", ""),
} for c in raw["CERTS"]]

channels = [{
    "group": c["g"],
    "items": [{"name": i["n"], "url": i["u"], "why": i["w"]} for i in c["items"]],
} for c in raw["CHANNELS"]]

shelf = [{"group": g, "items": [{"name": n, "url": u} for n, u in items]}
         for g, items in raw["SHELF"]]

matrix = [{"skill": s, "covers": c, "proof": p} for s, c, p in raw["MATRIX"]]

bundle = {
    "schema": 1,
    "generated": date.today().isoformat(),
    "phases": phases,
    "quizzes": quizzes,
    "fields": fields,
    "certs": certs,
    "channels": channels,
    "shelf": shelf,
    "matrix": matrix,
}

out = DATA / "curriculum.json"
out.write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"phases      {len(phases)}")
print(f"items       {sum(len(s['items']) for p in phases for s in p['sections'])}")
print(f"gate items  {sum(len(p['gate']['items']) for p in phases if p['gate'])}")
print(f"resources   {sum(len(p['resources']) for p in phases)}")
print(f"quizzes     {len(quizzes)} / {sum(len(q['questions']) for q in quizzes)} questions")
print(f"fields      {len(fields)}   certs {len(certs)}   shelf groups {len(shelf)}")
print(f"wrote       {out}  ({out.stat().st_size // 1024} KB)")

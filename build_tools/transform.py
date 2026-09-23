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
PICKS = json.loads((HERE / "resource_picks.json").read_text(encoding="utf-8"))

# A group of resources is "optional" when a learner only needs one of them to
# get started; the rest is study material the interface folds away. Which one
# leads is an editorial decision, so it is hand-authored in
# resource_picks.json rather than guessed from the data. A group with fewer
# than two entries is never folded and therefore never picked.
FOLD_MINIMUM = 2


class PickError(SystemExit):
    pass


def mark_group(kind: str, key: str, items: list) -> bool:
    """Flag the primary resource in one group. Returns whether it folds.

    Fails the build rather than shipping a group that folds the wrong thing:
    a missing pick, an unknown name, or a name matching two resources are all
    errors you want at generate time, not in front of a learner.
    """
    table = PICKS[kind]
    wanted = table.get(key)
    if len(items) < FOLD_MINIMUM:
        if wanted is not None:
            raise PickError(
                "resource_picks.json: %s %r has only %d resource(s) and is "
                "never folded, so it must not have a pick" % (kind, key,
                                                              len(items)))
        return False
    if wanted is None:
        raise PickError(
            "resource_picks.json: no primary chosen for %s %r (%d resources: "
            "%s)" % (kind, key, len(items),
                     ", ".join(i["name"] for i in items)))
    hits = [i for i in items if i["name"] == wanted]
    if len(hits) != 1:
        raise PickError(
            "resource_picks.json: %s %r picks %r, which matches %d of its "
            "resources" % (kind, key, wanted, len(hits)))
    hits[0]["primary"] = True
    return True


def check_every_pick_was_used(kind: str, used: set) -> None:
    extra = sorted(set(PICKS[kind]) - used)
    if extra:
        raise PickError(
            "resource_picks.json: %s has picks for groups that do not exist: "
            "%s" % (kind, ", ".join(extra)))


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


# Checklist sections that are stretch work rather than the phase itself.
# Everything else a phase lists is main: it is what the gate assumes you did.
# An optional section is folded behind an OPTIONAL pill, stays checkable, and
# never counts toward the phase's progress, so skipping it holds nothing
# back. Keyed by phase and the start of the section title; transform fails
# if a key matches nothing, so a renamed section cannot silently go main.
#   p05 Challenge ladder  - a way to push past the daily routine, not the
#                           routine itself.
#   p18 Leverage          - open source, talks, mentoring: career reach, not
#                           engineering skill the gate tests.
#   p18 Staying current   - a standing habit for after the course.
#   p99 Portfolio target  - a twelve-month outcome, not work you can tick
#                           off while climbing the ladder.
OPTIONAL_SECTIONS = {
    ("p05", "Challenge ladder"),
    ("p18", "Leverage"),
    ("p18", "Staying current"),
    ("p99", "Portfolio target"),
}


def plain(text: str) -> str:
    """Strip the page's <em> code markers for search and review-card text."""
    return re.sub(r"</?em>", "", text)


phases = []
picked_phases = set()
optional_used = set()
for ph in raw["PHASES"]:
    pid = ph["id"]
    sections = []
    for si, sec in enumerate(ph["sections"]):
        items = []
        for ii, text in enumerate(sec["items"]):
            items.append({"id": f"{pid}.s{si}.{ii}", "text": text})
        optional = [k for k in OPTIONAL_SECTIONS
                    if k[0] == pid and sec["h"].startswith(k[1])]
        optional_used.update(optional)
        sections.append({"id": f"{pid}.s{si}", "title": sec["h"],
                         "items": items, "optional": bool(optional)})

    gate = None
    if ph.get("gate"):
        gate = {
            "note": ph["gate"].get("note", ""),
            "items": [
                {"id": f"{pid}.g.{i}", "text": t}
                for i, t in enumerate(ph["gate"]["items"])
            ],
        }

    resources = [
        {"name": r["n"], "kind": r["k"], "why": r["w"], "url": r["u"]}
        for r in (ph.get("res") or [])
    ]
    resources_optional = mark_group("phase", pid, resources) if resources         else False
    if resources:
        picked_phases.add(pid)

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
        "resources": resources,
        "sections": sections,
        "snippet": ph.get("snippet") or "",
        "gate": gate,
        # Gates, sections and projects are the work itself and are never
        # folded; only this resource list can be.
        "resources_optional": resources_optional,
    })

check_every_pick_was_used("phase", picked_phases)
if OPTIONAL_SECTIONS - optional_used:
    raise PickError("OPTIONAL_SECTIONS names sections that do not exist: %s"
                    % sorted(OPTIONAL_SECTIONS - optional_used))

# -- quiz answer positions ----------------------------------------------------
# Authors write the correct choice wherever is convenient (usually first), so
# the authored order says nothing a learner should be able to use. The bundle
# places each correct answer by a fixed rule instead: a quiz's questions are
# taken four at a time, and each block of four gets its own ordering of the
# positions 0-3, so every position is used equally within a block. The
# distractors fill the other slots in an order derived from the question id.
# Everything is a hash of ids, never of the text or the clock, so the output
# is reproducible and fixing a typo never moves an answer.
#
# Question ids are positional ("q04.7" is the eighth question of q04) and
# learners' review history is keyed on them: questions are only ever edited
# in place or appended, never reordered or deleted.
BLOCK = 4


def _rank(*parts: object) -> str:
    return hashlib.sha1(":".join(map(str, parts)).encode("utf-8")).hexdigest()


def answer_slot(quiz_id: str, index: int, n_choices: int) -> int:
    """Where the correct answer of question `index` of `quiz_id` goes."""
    block, offset = divmod(index, BLOCK)
    order = sorted(range(BLOCK), key=lambda p: _rank(quiz_id, block, p))
    return order[offset] % n_choices


def place_answer(qid: str, slot: int, choices: list, correct: int,
                 explain_choice: list) -> tuple[list, int, list]:
    """Reorder choices (and their explanations, in lockstep) so the correct
    one sits at `slot`."""
    others = [i for i in range(len(choices)) if i != correct]
    others.sort(key=lambda i: _rank(qid, "distractor", i))
    order = others[:slot] + [correct] + others[slot:]
    return ([choices[i] for i in order], slot,
            [explain_choice[i] for i in order])


class QuizError(SystemExit):
    pass


KNOWN_ITEMS = {i["id"] for p in phases for s in p["sections"] for i in s["items"]}
KNOWN_ITEMS |= {g["id"] for p in phases if p["gate"] for g in p["gate"]["items"]}

# Where the raw bundle leaves a question without the line that teaches it,
# build_tools/quiz_teaches.json supplies one (see its _comment).
TEACHES = {k: v for k, v in json.loads(
    (Path(__file__).parent / "quiz_teaches.json").read_text(encoding="utf-8")
).items() if not k.startswith("_")}
teaches_used = set()

quizzes = []
for qz in raw["QUIZZES"]:
    questions = []
    for i, q in enumerate(qz["qs"]):
        qid = f"{qz['id']}.{i}"
        choices = list(q["a"])
        explain_choice = list(q.get("explain_choice") or [""] * len(choices))
        teaches = q.get("teaches", "")
        if not teaches and qid in TEACHES:
            teaches = TEACHES[qid]
            teaches_used.add(qid)
        if len(explain_choice) != len(choices):
            raise QuizError("%s: explain_choice has %d entries for %d choices"
                            % (qid, len(explain_choice), len(choices)))
        if not 0 <= q["c"] < len(choices):
            raise QuizError("%s: correct index %r is out of range" % (qid, q["c"]))
        if explain_choice[q["c"]]:
            raise QuizError("%s: the correct choice carries a 'why it is wrong' "
                            "note" % qid)
        if teaches and teaches not in KNOWN_ITEMS:
            raise QuizError("%s: teaches %r, which is not a checklist item"
                            % (qid, teaches))
        slot = answer_slot(qz["id"], i, len(choices))
        choices, correct, explain_choice = place_answer(
            qid, slot, choices, q["c"], explain_choice)
        questions.append({
            "id": qid,
            "prompt": q["q"],
            "choices": choices,
            "correct": correct,
            "explain": q["e"],
            # One note per choice, indexed like `choices`: why a learner who
            # picked it was wrong. The correct choice's entry is "".
            "explain_choice": explain_choice,
            # The checklist item this question checks, when there is one.
            "teaches": teaches,
        })
    quizzes.append({
        "id": qz["id"],
        "phase": qz["phase"],
        "name": qz["n"],
        "desc": qz["d"],
        "questions": questions,
    })

if set(TEACHES) - teaches_used:
    raise QuizError("quiz_teaches.json maps questions that are missing or "
                    "already mapped in the raw bundle: %s"
                    % sorted(set(TEACHES) - teaches_used))

fields = []
picked_fields = set()
for f in raw["FIELDS"]:
    libs = [{"name": n, "url": u} for n, u in f["libs"]]
    fields.append({
        "id": f["id"],
        "group": f["g"],
        "name": f["n"],
        "blurb": f["blurb"],
        "build": f["build"],
        "libs": libs,
        "libs_optional": mark_group("field", f["id"], libs),
    })
    if len(libs) >= FOLD_MINIMUM:
        picked_fields.add(f["id"])
check_every_pick_was_used("field", picked_fields)

certs = [{
    "id": c["id"], "name": c["n"], "by": c["by"], "cost": c["cost"],
    "time": c["time"], "what": c["what"], "worth": c["worth"],
    "url": c.get("u", ""),
} for c in raw["CERTS"]]

channels = []
for c in raw["CHANNELS"]:
    items = [{"name": i["n"], "url": i["u"], "why": i["w"]} for i in c["items"]]
    channels.append({
        "group": c["g"],
        "items": items,
        "optional": mark_group("channels", c["g"], items),
    })
check_every_pick_was_used("channels", {c["group"] for c in channels})

shelf = []
for group, entries in raw["SHELF"]:
    items = [{"name": n, "url": u} for n, u in entries]
    shelf.append({
        "group": group,
        "items": items,
        "optional": mark_group("shelf", group, items),
    })
check_every_pick_was_used("shelf", {g["group"] for g in shelf})

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
folded = (sum(1 for p in phases if p["resources_optional"])
          + sum(1 for f in fields if f["libs_optional"])
          + sum(1 for c in channels if c["optional"])
          + sum(1 for g in shelf if g["optional"]))
print(f"folded      {folded} optional groups, one primary each")
print(f"wrote       {out}  ({out.stat().st_size // 1024} KB)")

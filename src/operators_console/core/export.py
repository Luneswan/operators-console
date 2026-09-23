"""Getting progress out of the app.

Two shapes, for two different reasons: a JSON file that can be restored
verbatim on another machine, and a Markdown report that can be read by a human
or pasted into a CV, a standup or a mentor conversation.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .curriculum import Curriculum
from .progress import Progress
from .storage import Store


def export_backup(store: Store, target: Path) -> Path:
    target = Path(target)
    target.write_text(json.dumps(store.dump(), ensure_ascii=False, indent=1),
                      encoding="utf-8")
    return target


def import_backup(store: Store, source: Path) -> None:
    # utf-8-sig: Notepad and PowerShell 5 put a BOM in front of the JSON.
    payload = json.loads(Path(source).read_text(encoding="utf-8-sig"))
    store.restore(payload)


def export_report(curriculum: Curriculum, store: Store, progress: Progress,
                  target: Path) -> Path:
    """A readable Markdown summary of where the learner has got to."""
    overview = progress.overview()
    stats = progress.all_phases()
    plan = progress.active_phase_ids()
    track = curriculum.track(store.setting("track", "generalist"))
    current, longest = store.streak()

    lines = []
    add = lines.append
    name = store.setting("learner_name", "") or "Learner"
    add("# Python progress report")
    add("")
    add("**%s** - generated %s" % (name, date.today().isoformat()))
    add("")
    add("| Measure | Value |")
    add("| --- | --- |")
    add("| Track | %s |" % (track.name if track else "Custom"))
    add("| Curriculum complete | %d%% (%d of %d checks) |"
        % (overview.percent, overview.done, overview.total))
    add("| Phases proven | %d of %d |"
        % (overview.phases_complete, overview.phases_total))
    add("| Exercises passed | %d of %d |"
        % (overview.exercises_done, overview.exercises_total))
    revealed = store.revealed_exercise_ids()
    if revealed:
        # Worth knowing, and worth being honest about: these were solved
        # after reading the answer rather than from scratch.
        add("| Exercises whose answer was read | %d |" % len(revealed))
    add("| Projects shipped | %d of %d |"
        % (overview.projects_shipped, overview.projects_total))
    add("| Logged study hours | %.1f |" % overview.hours)
    add("| Current streak | %d days (best %d) |" % (current, longest))
    correct, total = store.review_accuracy(30)
    if total:
        add("| Review accuracy, 30 days | %d%% of %d |"
            % (round(correct / total * 100), total))
    add("")

    add("## Phases")
    add("")
    for pid in plan:
        phase = curriculum.phase(pid)
        st = stats.get(pid)
        if phase is None or st is None or not st.total:
            continue
        mark = "x" if st.is_complete else " "
        add("- [%s] **%s %s** - %d%% (%d/%d)%s"
            % (mark, phase.num, phase.name, st.percent, st.done, st.total,
               ", gate cleared" if st.gate_cleared else ""))
    add("")

    # The checklist above is the plan the learner is on; this is every phase
    # in the curriculum with the numbers behind it, including the ones the
    # chosen track leaves out.
    add("### Every phase in detail")
    add("")
    add("| Phase | Checks | Exercises | Gate | Best quiz | Projects |")
    add("| --- | --- | --- | --- | --- | --- |")
    for phase in curriculum.phases:
        st = stats.get(phase.id)
        if st is None:
            continue
        add("| %s %s | %d/%d (%d%%) | %d/%d | %s | %s | %d/%d |"
            % (phase.num, phase.name, st.done, st.total, st.percent,
               st.exercises_done, st.exercises_total,
               ("%d/%d" % (st.gate_done, st.gate_total)) if st.gate_total
               else "-",
               ("%d%%" % round(st.quiz_best * 100)) if st.quiz_best else "-",
               st.projects_shipped, st.projects_total))
    add("")

    shipped = [p for p in curriculum.projects
               if store.project(p.id)["status"] == "shipped"]
    if shipped:
        add("## Shipped projects")
        add("")
        for project in shipped:
            state = store.project(project.id)
            url = state["repo_url"]
            add("- **%s** - %s%s"
                % (project.title, project.brief,
                   (" (%s)" % url) if url else ""))
        add("")

    _add_notes(curriculum, store, add)

    logs = store.logs(limit=30)
    if logs:
        add("## Recent log")
        add("")
        for row in logs[:15]:
            focus = row["focus"] or "(no focus recorded)"
            add("- **%s** - %.1f h - %s" % (row["day"], row["hours"], focus))
            if row["built"]:
                add("  - Built: %s" % row["built"])
            if row["stuck"]:
                add("  - Stuck: %s" % row["stuck"])
        add("")

    target = Path(target)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def _add_notes(curriculum: Curriculum, store: Store, add) -> None:
    """Everything the learner typed for themselves, kept together.

    Notes were the one thing the report left behind entirely, so the file it
    produced could not stand in for the application - which is the whole
    point of being able to export it.
    """
    written = []
    for scope, body in sorted(store.all_notes().items()):
        body = (body or "").strip()
        if body:
            written.append((_note_heading(curriculum, scope), body))
    for project in curriculum.projects:
        body = (store.project(project.id)["notes"] or "").strip()
        if body:
            written.append(("Project: %s" % project.title, body))
    if not written:
        return
    add("## Notes")
    add("")
    for heading, body in written:
        add("### %s" % heading)
        add("")
        add(body)
        add("")


def _note_heading(curriculum: Curriculum, scope: str) -> str:
    """'phase:p01' reads as the phase it belongs to, not as a key."""
    kind, _, rest = scope.partition(":")
    if kind == "phase":
        phase = curriculum.phase(rest)
        if phase is not None:
            return "%s %s" % (phase.num, phase.name)
    return scope

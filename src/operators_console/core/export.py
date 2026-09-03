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
    payload = json.loads(Path(source).read_text(encoding="utf-8"))
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
    add("| Phases finished | %d of %d |"
        % (overview.phases_complete, overview.phases_total))
    add("| Exercises passed | %d of %d |"
        % (overview.exercises_done, overview.exercises_total))
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

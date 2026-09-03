"""The content itself has to be internally consistent, or the app lies."""
from __future__ import annotations

import re


URL = re.compile(r"^https?://")


def test_the_bundle_loads(curriculum):
    assert len(curriculum.phases) >= 20
    assert len(curriculum.exercises) >= 90
    assert len(curriculum.projects) >= 20
    assert len(curriculum.all_questions) >= 150


def test_every_id_is_unique(curriculum):
    for group in (curriculum.phases, curriculum.exercises, curriculum.projects,
                  curriculum.quizzes, curriculum.tracks, curriculum.certs,
                  curriculum.fields):
        ids = [item.id for item in group]
        assert len(ids) == len(set(ids)), ids


def test_every_check_id_is_unique_across_the_whole_course(curriculum):
    ids = []
    for phase in curriculum.phases:
        ids.extend(item.id for item in phase.items)
        if phase.gate:
            ids.extend(item.id for item in phase.gate.items)
    assert len(ids) == len(set(ids))


def test_exercises_and_projects_point_at_real_phases(curriculum):
    known = {phase.id for phase in curriculum.phases}
    for exercise in curriculum.exercises:
        assert exercise.phase in known, exercise.id
    for project in curriculum.projects:
        assert project.phase in known, project.id
    for quiz in curriculum.quizzes:
        assert quiz.phase in known, quiz.id


def test_prerequisites_point_at_real_phases(curriculum):
    known = {phase.id for phase in curriculum.phases}
    for phase in curriculum.phases:
        for prereq in phase.prereq:
            assert prereq in known, (phase.id, prereq)


def test_no_phase_depends_on_itself(curriculum):
    for phase in curriculum.phases:
        assert phase.id not in phase.prereq


def test_prerequisites_form_no_cycle(curriculum):
    seen = set()

    def visit(pid, trail):
        assert pid not in trail, "cycle through %s" % pid
        if pid in seen:
            return
        seen.add(pid)
        phase = curriculum.phase(pid)
        for prereq in phase.prereq:
            visit(prereq, trail | {pid})

    for phase in curriculum.phases:
        visit(phase.id, set())


def test_tracks_only_reference_real_phases(curriculum):
    known = {phase.id for phase in curriculum.phases}
    for track in curriculum.tracks:
        for pid in tuple(track.core) + tuple(track.optional):
            assert pid in known, (track.id, pid)
        assert not set(track.core) & set(track.optional), track.id


def test_every_track_starts_with_the_setup_phase(curriculum):
    for track in curriculum.tracks:
        assert "p00" in track.core, track.id


def test_quiz_answers_point_at_a_real_choice(curriculum):
    for quiz in curriculum.quizzes:
        for question in quiz.questions:
            assert 2 <= len(question.choices) <= 6, question.id
            assert 0 <= question.correct < len(question.choices), question.id
            assert question.explain.strip(), question.id


def test_quiz_choices_are_distinct(curriculum):
    for quiz in curriculum.quizzes:
        for question in quiz.questions:
            assert len(set(question.choices)) == len(question.choices), question.id


def test_exercises_are_well_formed(curriculum):
    for exercise in curriculum.exercises:
        assert exercise.prompt.strip(), exercise.id
        assert exercise.starter.strip(), exercise.id
        assert exercise.tests, exercise.id
        assert 1 <= exercise.difficulty <= 5, exercise.id
        assert exercise.solution.strip(), exercise.id
        names = [case.name for case in exercise.tests]
        assert len(names) == len(set(names)), exercise.id


def test_projects_carry_requirements_and_a_rubric(curriculum):
    for project in curriculum.projects:
        assert len(project.requirements) >= 3, project.id
        assert project.rubric, project.id
        assert len(set(project.requirement_ids)) == len(project.requirements)


def test_resource_links_look_like_links(curriculum):
    for phase in curriculum.phases:
        for resource in phase.resources:
            assert URL.match(resource.url), (phase.id, resource.url)
    for group in curriculum.shelf:
        for link in group.items:
            assert URL.match(link.url), link.url
    for group in curriculum.channels:
        for item in group.items:
            assert URL.match(item.url), item.url


def test_every_scored_phase_has_something_to_score(curriculum):
    for phase in curriculum.scored_phases:
        assert phase.trackable_ids, phase.id


def test_operating_rules_are_excluded_from_scoring(curriculum):
    ops = curriculum.phase("ops")
    assert ops is not None
    assert ops.no_progress
    assert ops.trackable_ids == ()

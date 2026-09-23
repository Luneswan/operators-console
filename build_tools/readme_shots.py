"""Render the README's screenshots with real fonts.

    python build_tools/readme_shots.py

build_tools/shots.py renders offscreen for layout review, where there are no
real fonts. The README needs what a learner sees, so this uses the native
platform with the window kept off the screen, a seeded learner partway
through the course, a failed practice run (so the grader's explanation is in
the picture) and a live review card. Writes docs/screenshots/*.png.
"""
import os
import sys
import tempfile
import time

HOME = tempfile.mkdtemp(prefix="opcon-readme-")
os.environ["OPERATORS_CONSOLE_HOME"] = HOME
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from PySide6.QtCore import Qt  # noqa: E402 - env first
from PySide6.QtWidgets import QApplication  # noqa: E402 - env first

app = QApplication(["readme-shots"] + (["-platform", "windows"]
                                        if sys.platform == "win32" else []))

from operators_console.core.storage import Store  # noqa: E402
from operators_console.ui.context import AppContext  # noqa: E402
from operators_console.ui.main_window import MainWindow  # noqa: E402

OUT = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)
SIZE = (1366, 820)


def pump(seconds=0.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.01)


def seed(store, curriculum):
    store.set_setting("onboarded", True)
    store.set_setting("guide_pointed", True)
    store.set_setting("learner_name", "Sam")
    store.set_setting("check_for_updates", False)
    for pid in ("p00", "p01"):
        phase = curriculum.phase(pid)
        items = list(phase.items)
        keep = items if pid == "p00" else items[:22]
        for item in keep:
            store.set_checked(item.id, True)
        if pid == "p00" and phase.gate:
            for item in phase.gate.items:
                store.set_checked(item.id, True)
    for exercise in curriculum.exercises_for("p01")[:9]:
        store.record_exercise_run(exercise.id, exercise.solution, True)
    today = time.strftime("%Y-%m-%d")
    store.add_log(today, "Generators and iterators", 2.5,
                  "A lazy file reader", "Closing over a loop variable",
                  "itertools.groupby")


def window_for(theme):
    store = Store()
    ctx = AppContext(store=store)
    if not store.setting("onboarded", False):
        seed(store, ctx.curriculum)
    store.set_setting("theme", theme)
    ctx.refresh_palette()
    win = MainWindow(ctx)
    win.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    win.resize(*SIZE)
    win.show()
    pump(1.0)
    return win


def shot(win, name):
    pump(0.6)
    path = os.path.join(OUT, name)
    win.grab().save(path)
    print("wrote", path)


def failed_practice(win):
    """A real wrong answer, graded, so the explanation is on screen."""
    exercises = win.ctx.curriculum.exercises_for("p01")
    exercise = exercises[min(9, len(exercises) - 1)]
    win.go("practice", exercise.id)
    pump()
    view = win.views["practice"]
    view.editor.set_code(exercise.starter)
    pump()
    view._run()
    deadline = time.monotonic() + 30
    while getattr(view, "_running", False) and time.monotonic() < deadline:
        pump(0.1)
    pump(0.8)


def quiz_results(win):
    """A finished attempt with three misses, one of them out of time."""
    win.go("quiz", "q00")
    pump()
    view = win.views["quiz"]
    for index in range(len(view.order)):
        question = view.quiz.questions[view.order[view.position]]
        if index == 1:
            view.question_started -= view.budget + 1
            view._on_tick()
        right = index >= 3 or index == 1
        chosen = question.correct if right else (
            question.correct + 1) % len(question.choices)
        view.group.button(chosen).setChecked(True)
        view._question_controls[1].click()
        pump(0.1)
        view._advance()
        pump(0.1)
    pump(0.6)


def main():
    for theme in ("light", "dark"):
        win = window_for(theme)
        win.go("today", "")
        shot(win, "today-%s.png" % theme)
        # Tall enough that the grader's explanation sits under the editor.
        win.resize(SIZE[0], 1180)
        failed_practice(win)
        view = win.views["practice"]
        view.scroller.verticalScrollBar().setValue(
            view.scroller.verticalScrollBar().maximum())
        shot(win, "practice-%s.png" % theme)
        win.resize(*SIZE)
        if theme == "dark":
            quiz_results(win)
            shot(win, "quiz-dark.png")
        if theme == "light":
            win.go("roadmap", "")
            shot(win, "roadmap-light.png")
            win.go("review", "")
            pump(0.5)
            shot(win, "review-light.png")
        win.close()
        pump(0.3)
    return 0


if __name__ == "__main__":
    sys.exit(main())

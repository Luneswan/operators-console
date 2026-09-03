"""Render each page to a PNG so the layout can be reviewed without a display."""
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HOME = os.environ.setdefault("OPERATORS_CONSOLE_HOME",
                             tempfile.mkdtemp(prefix="opcon-shot-"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from PySide6.QtWidgets import QApplication
from operators_console.core.storage import Store
from operators_console.ui.context import AppContext
from operators_console.ui.main_window import MainWindow

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build_tools", "shots")
os.makedirs(OUT, exist_ok=True)
THEME = sys.argv[2] if len(sys.argv) > 2 else "light"

app = QApplication([])
app.setStyle("Fusion")
store = Store()
store.set_setting("onboarded", True)
store.set_setting("learner_name", "Sam")
store.set_setting("theme", THEME)

# Seed enough state that the pages are not all empty.
curriculum_ids = []
ctx = AppContext(store=store)
phase = ctx.curriculum.phase("p00")
for item in phase.items:
    store.set_checked(item.id, True)
for item in phase.gate.items:
    store.set_checked(item.id, True)
p01 = ctx.curriculum.phase("p01")
for item in list(p01.items)[:14]:
    store.set_checked(item.id, True)
store.record_exercise_run("p01.001", "def greet(n):\n    return n\n", True)
store.record_exercise_run("p01.002", "x", False)
store.record_quiz("q00", 7, 8, 240)
store.add_log("2026-09-01", "Git recovery drills", 3.0, "Recovered a branch",
              "reflog output confused me", "Start phase 01")
store.add_log("2026-09-02", "Collections and slicing", 2.5, "Expense tracker",
              "Nested comprehensions", "Finish the CLI")
store.set_project("pj.p00.1", status="shipped",
                  repo_url="https://github.com/sam/git-training")
store.set_project("pj.p01.1", status="in-progress")
ctx.refresh_palette()

win = MainWindow(ctx)
win.resize(1320, 900)
win.show()
app.processEvents()

pages = ["today", "roadmap", "phase", "practice", "quiz", "review",
         "projects", "journal", "stats", "library", "settings"]
for key in pages:
    win.go(key, {"phase": "p01", "practice": "p01.003",
                 "quiet": ""}.get(key, ""))
    for _ in range(4):
        app.processEvents()
    path = os.path.join(OUT, "%s-%s.png" % (THEME, key))
    win.grab().save(path)
    print(path)

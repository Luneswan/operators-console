"""Take the screenshots that go in the report, on the real platform.

The walk itself runs offscreen, which renders correctly but is not what the
learner's machine draws. This module is launched as a separate process with
the native platform plugin and ``WA_DontShowOnScreen`` set on the window, so
the pictures come from the real style engine without anything appearing on
the user's desktop.

    python -m tests.walkthrough.shots <output directory>
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _grab(window, app, name: str, out: Path) -> str:
    for _ in range(4):
        app.processEvents()
    target = out / ("%s.png" % name)
    window.grab().save(str(target))
    return target.name


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[0]) if argv else Path.cwd()
    out.mkdir(parents=True, exist_ok=True)

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")

    from operators_console.core.storage import Store
    from operators_console.ui.context import AppContext
    from operators_console.ui.main_window import MainWindow, NAV

    store = Store()
    store.set_setting("onboarded", True)
    store.set_setting("learner_name", "Walker")
    ctx = AppContext(store=store)
    window = MainWindow(ctx)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.resize(1280, 900)
    window.show()
    for _ in range(6):
        app.processEvents()

    written = []
    for theme in ("light", "dark"):
        store.set_setting("theme", theme)
        ctx.refresh_palette()
        for _ in range(4):
            app.processEvents()
        for key, _text, _factory in NAV:
            window.go(key, "")
            for _ in range(4):
                app.processEvents()
            written.append(_grab(window, app,
                                 "%s-%s" % (key, theme), out))

    # The one page whose defect is worth a picture: a graded run whose
    # result panel is hidden again the moment it is drawn.
    store.set_setting("theme", "light")
    ctx.refresh_palette()
    exercise = ctx.curriculum.exercises[0]
    window.go("practice", exercise.id)
    for _ in range(4):
        app.processEvents()
    view = window.views["practice"]
    view.editor.set_code(exercise.solution)
    view._run()
    import time
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        app.processEvents()
        if view.run_button.isEnabled():
            break
        time.sleep(0.02)
    for _ in range(4):
        app.processEvents()
    written.append(_grab(window, app, "practice-after-a-passing-run", out))
    (out / "practice-after-a-passing-run.txt").write_text(
        "results panel hidden: %s\nrows rendered into it: %d\n"
        "hint label hidden: %s\n"
        % (view.results.isHidden(), view.results.box.count(),
           view.hint_label.isHidden()), encoding="utf-8")

    window.close()
    for name in written:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

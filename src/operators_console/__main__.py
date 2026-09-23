"""Command line entry point.

Two modes share one executable so that a frozen build needs no separate
interpreter:

    operators-console                    start the desktop application
    operators-console --exercise-runner  grade one exercise from stdin
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    # A multiprocessing worker in the frozen build is this executable again,
    # with --multiprocessing-fork. freeze_support() runs the worker and exits;
    # without it a learner's Pool would open a second copy of the app.
    # multiprocessing.freeze_support() only acts on Windows before 3.14, but
    # a frozen macOS build spawns its workers the same way, so call the
    # spawn-level helper directly: it runs the worker and exits on any
    # platform, and does nothing for an ordinary launch.
    if getattr(sys, "frozen", False):
        from multiprocessing import spawn
        spawn.freeze_support()

    argv = list(sys.argv[1:] if argv is None else argv)

    # Absolute imports: PyInstaller executes this file as a top-level
    # script, where a relative import has no parent package to resolve.
    from operators_console.core.runner import RUNNER_FLAG, child_main, exit_now
    if RUNNER_FLAG in argv:
        exit_now(child_main())

    from operators_console.core.updates import APPLY_FLAG, apply_update
    if APPLY_FLAG in argv:
        return _run_updater(argv, apply_update)

    if "--version" in argv or "-V" in argv:
        from operators_console.version import APP_NAME, __version__
        print("%s %s" % (APP_NAME, __version__))
        return 0

    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0

    from operators_console.app import run
    return run(argv)


def _run_updater(argv, apply_update) -> int:
    """Parse the helper invocation and swap the build over.

    This process has no window and no console. It exists only to outlive the
    application it is replacing.
    """
    import argparse
    from pathlib import Path

    from operators_console.core.updates import APPLY_FLAG

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(APPLY_FLAG, dest="package")
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--kind", default="")
    parser.add_argument("--target", required=True)
    parser.add_argument("--sha256", default="")
    options, _rest = parser.parse_known_args(argv)
    return apply_update(Path(options.package), options.pid, options.kind,
                        Path(options.target), options.sha256)


if __name__ == "__main__":
    raise SystemExit(main())

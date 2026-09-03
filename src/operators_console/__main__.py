"""Command line entry point.

Two modes share one executable so that a frozen build needs no separate
interpreter:

    operators-console                    start the desktop application
    operators-console --exercise-runner  grade one exercise from stdin
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # Absolute imports: PyInstaller executes this file as a top-level
    # script, where a relative import has no parent package to resolve.
    from operators_console.core.runner import RUNNER_FLAG, child_main
    if RUNNER_FLAG in argv:
        return child_main()

    if "--version" in argv or "-V" in argv:
        from operators_console.version import APP_NAME, __version__
        print("%s %s" % (APP_NAME, __version__))
        return 0

    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0

    from operators_console.app import run
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())

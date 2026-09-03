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
    options, _rest = parser.parse_known_args(argv)
    return apply_update(Path(options.package), options.pid, options.kind,
                        Path(options.target))


if __name__ == "__main__":
    raise SystemExit(main())

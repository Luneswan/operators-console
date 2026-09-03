"""Projects for the early phases."""
from proj_lib import pr


def build():
    pr("pj.p00.1", "p00", "Recover a repository you deliberately broke",
       "drill",
       "Create a repo, wreck it four different ways, and get it back each time.",
       "Version control is only useful if you trust it under pressure. The way "
       "to trust it is to break things on purpose while nothing is at stake.",
       ["Create a repo with at least eight commits across two branches.",
        "Cause a merge conflict and resolve it by hand, without a merge tool.",
        "Hard reset away a commit, then recover it using the reflog.",
        "Revert a commit that is already pushed, and explain why you did not reset.",
        "Rewrite the last three commit messages with an interactive rebase.",
        "Write a README section explaining, in your words, when each command is safe."],
       stretch=["Add a pre-commit hook that refuses a commit with a syntax error.",
                "Configure a .gitignore that survives adding a virtualenv by accident."],
       rubric=["You can perform every recovery from memory, with no cheat sheet open.",
               "You can say out loud what merge, revert, reset and rebase each do to history.",
               "Nothing in the repo was lost that you did not intend to lose."])

    pr("pj.p01.1", "p01", "A command-line expense tracker", "build",
       "A single-file CLI that records expenses, stores them, and reports totals.",
       "It exercises almost everything in the phase - input handling, data "
       "structures, files, errors - without needing any library at all.",
       ["Add, list and delete expenses from the command line.",
        "Persist to a JSON file so data survives restarts.",
        "Report totals by category and by month.",
        "Reject bad input with a clear message rather than a traceback.",
        "Handle a missing or corrupt data file without losing the good data.",
        "No third-party dependencies. Standard library only."],
       stretch=["Add a --since and --until date filter.",
                "Export a month to CSV.",
                "Add a simple text bar chart of spending per category."])

    pr("pj.p01.2", "p01", "A text-adventure engine", "build",
       "A small game engine where rooms, items and exits are data, not code.",
       "The moment the map moves out of if-statements and into a dictionary, "
       "you have understood the difference between data and logic.",
       ["Rooms, exits and items are defined in a data file, not hard-coded.",
        "The player can move, look, take, drop and check an inventory.",
        "Unknown commands produce a helpful message, never a crash.",
        "Game state can be saved and reloaded.",
        "Adding a new room requires editing data only, not the engine."],
       stretch=["Add locked doors that need a specific item.",
                "Add a scripted ending condition."])

    pr("pj.p02.1", "p02", "A log-processing pipeline that never loads the file",
       "build",
       "Process a multi-gigabyte log file with flat memory usage, and prove it.",
       "This is the exercise that makes generators click. You cannot fake it: "
       "either memory stays flat or it does not.",
       ["Generate a test log of at least 2 GB, or stream one you already have.",
        "Parse, filter, and aggregate it through chained generators.",
        "Peak memory stays roughly constant regardless of file size.",
        "Prove it with a memory profile, and put the numbers in the README.",
        "Provide a second, list-based implementation and compare the two.",
        "Include a context manager that guarantees the file handle closes."],
       stretch=["Add a --follow mode that tails a growing file.",
                "Parallelise the aggregation and measure whether it actually helps."])

    pr("pj.p02.2", "p02", "A small library with real protocols", "build",
       "A reusable package that implements the iterator, context manager and "
       "descriptor protocols rather than merely using them.",
       "Implementing a protocol is the fastest way to stop treating Python as "
       "magic and start reading the data model as an interface.",
       ["At least one custom iterator implemented without a generator.",
        "At least one context manager, both as a class and via contextlib.",
        "A decorator that preserves the wrapped signature and metadata.",
        "Full type hints that pass a type checker with no ignores.",
        "Docstrings on every public name, with a doctest that runs in CI."],
       stretch=["Add a descriptor that validates attribute assignment.",
                "Publish it to TestPyPI and install it in a fresh environment."])

    pr("pj.p03.1", "p03", "Package and publish a tool", "ship",
       "Take one script you have written and turn it into an installable, "
       "tested, documented package.",
       "The gap between a script that works on your machine and software other "
       "people can install is where most self-taught programmers stall.",
       ["A src-layout package with a pyproject.toml.",
        "A console entry point, so the tool runs by name after installation.",
        "Tests that run against the installed package, not the source folder.",
        "Linting and formatting enforced, not merely suggested.",
        "A README with installation, usage and one worked example.",
        "Published to TestPyPI and installed from there into a clean environment."],
       stretch=["Add a GitHub Actions workflow that publishes on a tag.",
                "Support Python 3.11 through the current release and prove it in CI."])

    pr("pj.p04.1", "p04", "A data-structures library, from scratch", "build",
       "Implement the core structures yourself, with tests and measured "
       "complexity.",
       "You will never argue confidently about a data structure you have not "
       "built at least once.",
       ["Dynamic array, linked list, stack, queue, hash map, binary search tree.",
        "A test suite that covers empty, single, duplicate and large inputs.",
        "A benchmark comparing each against the standard library equivalent.",
        "A README stating the complexity of every operation, with evidence.",
        "At least one structure where your version loses, and an honest explanation."],
       stretch=["Add a balanced tree and show the difference on sorted input.",
                "Add a trie and use it for autocomplete."])

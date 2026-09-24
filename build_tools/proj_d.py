"""Projects for the specialization phases (s01-s14)."""
from proj_lib import pr


def build():
    pr("pj.s01.1", "s01", "An analysis someone can check", "build",
       "Answer a question about a public dataset with a report generated "
       "entirely from code.",
       "A result counts only if someone else can rerun it and get the same "
       "numbers.",
       ["The question is written down before the data is explored.",
        "One script goes from the raw file to the finished report.",
        "Cleaning steps are listed, with how many rows each one changed.",
        "At least three charts, each with a one-line takeaway.",
        "A limitations section: sample, bias and missing data.",
        "Rerunning the script on a clean checkout reproduces every number."],
       stretch=["Add an interactive version with a dashboard library.",
                "Add a statistical test and explain whether it applies."])

    pr("pj.s02.1", "s02", "A desktop app with an installer", "ship",
       "Build a single-purpose desktop tool and ship it to a machine without "
       "Python.",
       "Packaging, threading and settings are where desktop apps fail.",
       ["A GUI with at least three screens or panels.",
        "Long operations run in a worker with progress and a cancel button.",
        "Settings and data stored in the platform's per-user folders.",
        "Logic tested without starting the GUI.",
        "A bundle or installer that runs on a clean machine.",
        "Keyboard navigation works for the main actions."],
       stretch=["Add an in-app update check against GitHub releases.",
                "Ship the same app for a second operating system."])

    pr("pj.s03.1", "s03", "A published command-line tool", "ship",
       "Write a CLI that solves a real task and publish it to PyPI or TestPyPI.",
       "A tool other people install forces you to handle input, errors and "
       "output properly.",
       ["At least two subcommands with complete help text.",
        "A --json output mode for scripts.",
        "Documented, tested exit codes.",
        "Configuration from flags, environment variables and a config file, in "
        "that order.",
        "Installable with pipx from a package index.",
        "A documentation site built in CI."],
       stretch=["Add shell completion.",
                "Add a plugin mechanism through entry points."])

    pr("pj.s04.1", "s04", "A finished 2D game", "build",
       "Build a complete game with a start screen, scoring and an ending, "
       "and package it.",
       "Finishing a game covers state, timing, input, assets and packaging.",
       ["A start screen, gameplay, pause and game-over states.",
        "Frame-rate-independent movement using delta time.",
        "Collision detection that stays correct at high speed.",
        "Sound effects and adjustable volume.",
        "Frame time measured and kept under 16 ms on your machine.",
        "A packaged build that runs without Python."],
       stretch=["Add a level editor that saves levels as JSON.",
                "Add controller support."])

    pr("pj.s05.1", "s05", "A validated simulation", "build",
       "Model a real system numerically and show the method is correct.",
       "A simulation is useful only if its error is known.",
       ["A written model of the system and its assumptions.",
        "The numerical method checked against an analytic or known case.",
        "An error study: error against step size or sample count.",
        "The hot loop optimized, with timings before and after.",
        "A pinned environment and one command that regenerates every figure."],
       stretch=["Fit the model's parameters to real data.",
                "Add an optimization that uses the simulation as its "
                "objective."])

    pr("pj.s06.1", "s06", "A backtester without lookahead", "build",
       "Backtest a simple strategy on historical data with realistic costs.",
       "Most backtests look good because of bias. This one must fail "
       "loudly if it cheats.",
       ["Data loading with adjustments for splits and dividends.",
        "Signals can only use data available at decision time, enforced by "
        "a test.",
        "Fees and slippage applied to every trade.",
        "Returns, volatility, Sharpe ratio and maximum drawdown reported.",
        "A buy-and-hold benchmark on the same period.",
        "Walk-forward results reported separately from in-sample ones."],
       stretch=["Add position sizing by volatility.",
                "Compare two strategies with a statistical test."])

    pr("pj.s07.1", "s07", "A vision model with error analysis", "build",
       "Fine-tune a pretrained vision model for a specific task and "
       "measure where it fails.",
       "The failure cases decide whether a model can be used.",
       ["A dataset with a documented source and split.",
        "A simple baseline, then a fine-tuned model that beats it.",
        "Per-class metrics and a confusion matrix.",
        "The worst errors reviewed and grouped by cause.",
        "An inference command for images or video."],
       stretch=["Export the model to ONNX and compare speed.",
                "Add test-time augmentation and measure its effect."])

    pr("pj.s08.1", "s08", "A text model with a baseline", "build",
       "Build a text classifier or search engine and compare it with a "
       "simple baseline.",
       "A transformer is justified only if it beats TF-IDF by a margin that "
       "matters.",
       ["A labelled dataset and a written labelling guide.",
        "A TF-IDF baseline and a transformer on the same test set.",
        "Precision, recall and F1 per class.",
        "Error analysis grouped by error type.",
        "A command or API that returns predictions with confidence."],
       stretch=["Add hybrid keyword and semantic search.",
                "Measure performance on a second domain."])

    pr("pj.s09.1", "s09", "A test strategy for a real codebase", "drill",
       "Write down the risks of an existing project and cover them with "
       "tests at the right level.",
       "More tests are not the goal. Tests that catch the likely defects are.",
       ["A written list of the project's risks.",
        "Unit, integration and end-to-end tests mapped to those risks.",
        "At least one property-based test.",
        "A mutation-testing run and the tests it made you add.",
        "Fast tests on every push; slow tests on a schedule."],
       stretch=["Add contract tests between two services.",
                "Add a load test with a pass or fail threshold."])

    pr("pj.s10.1", "s10", "A network change pipeline", "build",
       "Generate, dry-run, apply and verify configuration changes across a "
       "lab network.",
       "A network change without a diff and a rollback is a guess.",
       ["A lab with at least three virtual devices.",
        "Configuration rendered from templates and a source-of-truth file.",
        "A dry run that prints the diff for every device.",
        "Pre- and post-change checks that roll back on failure.",
        "A compliance report across the inventory.",
        "Credentials from the environment or a vault."],
       stretch=["Run the pipeline from CI on every change to the source of "
                "truth.",
                "Add NETCONF for at least one device type."])

    pr("pj.s11.1", "s11", "A connected sensor", "build",
       "Read a real sensor on a microcontroller and send the data to a "
       "service that stores it and alerts.",
       "Hardware projects fail on timing, memory and lost connections.",
       ["A sensor read on a schedule without blocking.",
        "Readings published over MQTT.",
        "A service that stores readings and alerts on a threshold.",
        "Readings buffered on the device when the network is down.",
        "A wiring diagram and parts list in the repository."],
       stretch=["Add deep sleep and measure battery life.",
                "Add over-the-air updates."])

    pr("pj.s12.1", "s12", "A security tool in CI", "build",
       "Build a tool that finds one class of security problem and run it "
       "against a real project.",
       "Writing a detector teaches you the vulnerability and its false "
       "positives.",
       ["One clearly defined detection target.",
        "Tests with known-bad and known-good samples.",
        "A measured false-positive rate on a real codebase.",
        "Output in SARIF or JSON.",
        "Documentation on scope, limits and safe use.",
        "Runs in CI and fails the build on a finding."],
       stretch=["Publish the rule set for others to use.",
                "Add a fix suggestion for each finding."])

    pr("pj.s13.1", "s13", "A bot in daily use", "ship",
       "Build a bot for a group you belong to and keep it running for a "
       "week.",
       "A bot that runs unattended must handle restarts, rate limits and "
       "bad input.",
       ["At least one command and one scheduled job.",
        "State that survives a restart.",
        "Rate limits handled and tested against a fake server.",
        "Secrets from the environment.",
        "Deployed with automatic restart and readable logs.",
        "One week of operation, with one bug found and fixed from the logs."],
       stretch=["Add a web dashboard for the bot's settings.",
                "Support a second platform."])

    pr("pj.s14.1", "s14", "A testnet event indexer", "build",
       "Index a contract's events into a database and handle chain "
       "reorganizations.",
       "Chain data is append-only until it is not; an indexer must handle "
       "both.",
       ["Events read from a testnet or local chain.",
        "Stored in SQLite or PostgreSQL without duplicates.",
        "Restarts resume from the last processed block.",
        "Reorganizations handled and tested.",
        "A report command over the indexed data.",
        "No mainnet keys or real funds in the project."],
       stretch=["Write and test a small contract with Ape.",
                "Add a GraphQL or REST API over the index."])

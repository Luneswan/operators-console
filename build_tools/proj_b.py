"""Projects for the middle phases."""
from proj_lib import pr


def build():
    pr("pj.p05.1", "p05", "A solved-problems repository with written reasoning",
       "drill",
       "Fifty problems solved, each with a note on why the approach works.",
       "Volume alone does not build problem-solving. The written reasoning is "
       "what transfers to a problem you have not seen.",
       ["At least fifty problems, spread across arrays, strings, graphs and DP.",
        "Every solution has a stated time and space complexity.",
        "Every solution has a short note on the insight that unlocked it.",
        "At least ten problems solved a second way, with a comparison.",
        "A tests file so a refactor cannot silently break an old solution."],
       stretch=["Solve one full Advent of Code year and write up the hardest day.",
                "Re-solve ten problems a month later, cold, and record the gap."])

    pr("pj.p06.1", "p06", "A system health reporter", "build",
       "A command-line tool that reports disk, memory, process and service "
       "state, and exits non-zero when something is wrong.",
       "Automation that cannot be trusted by a monitoring system is a toy. An "
       "exit code is the difference.",
       ["Reports disk usage, load, memory and the top processes.",
        "Thresholds are configurable, not hard-coded.",
        "Exits 0 when healthy and non-zero when a threshold is breached.",
        "Runs unattended from cron or a systemd timer.",
        "Logs to a file with rotation, and never grows without bound.",
        "Degrades gracefully when a metric is unavailable on this platform."],
       stretch=["Add a --json mode for machine consumption.",
                "Send an alert to a webhook, with retries and a rate limit."])

    pr("pj.p07.1", "p07", "An HTTP client and server, from sockets", "build",
       "Speak HTTP/1.1 over a raw TCP socket, both directions.",
       "Everything above this layer is easier once you have seen the bytes go "
       "across the wire yourself.",
       ["A server that parses a request line, headers and body from a socket.",
        "It serves at least GET and POST, with correct status codes.",
        "A client that builds a request by hand and parses the response.",
        "Correct handling of Content-Length and connection close.",
        "Concurrency for more than one client at a time.",
        "A packet capture or log showing a full exchange, explained in the README."],
       stretch=["Add chunked transfer encoding.",
                "Add TLS with the standard library ssl module."])

    pr("pj.p08.1", "p08", "A schema you designed, then optimised", "build",
       "Model a real domain in PostgreSQL, load real volume, then make the slow "
       "queries fast.",
       "Index tuning only teaches you something once there is enough data for "
       "the wrong plan to hurt.",
       ["A normalised schema with primary keys, foreign keys and constraints.",
        "At least 500,000 rows of realistic generated data.",
        "Five reporting queries, each with its EXPLAIN plan recorded.",
        "At least two queries made measurably faster by an index you chose.",
        "Before and after timings in the README, not guesses.",
        "A migration history, so the schema can be rebuilt from scratch."],
       stretch=["Add a window-function report and explain what it replaces.",
                "Demonstrate a deadlock between two transactions, then fix it."])

    pr("pj.p09.1", "p09", "A production-shaped API", "ship",
       "A tested, documented, authenticated HTTP service backed by a real "
       "database.",
       "This is the portfolio piece that most closely matches the job. It has "
       "to be complete, not impressive.",
       ["CRUD over at least two related resources, with validation at the edge.",
        "Authentication and authorisation, with a test proving a stranger is refused.",
        "Database access through migrations, never a hand-created schema.",
        "Generated OpenAPI documentation that matches the implementation.",
        "Structured logging with a request id that appears in every log line.",
        "Unit and integration tests, with the test database created and torn down.",
        "Pagination, filtering and sensible error responses."],
       stretch=["Add background jobs for the slow work.",
                "Add rate limiting and prove it with a load test."])

    pr("pj.p10.1", "p10", "An automation engine that survives failure", "build",
       "A task runner that scrapes, transforms and stores data, and can be "
       "killed at any moment without losing or duplicating work.",
       "Anyone can write a script that works. The engineering is in what "
       "happens when the network, the site or the machine misbehaves.",
       ["Reads a task list from configuration, not from code.",
        "Retries with exponential backoff and a cap.",
        "Handles 429 and 5xx distinctly from 4xx.",
        "Resumes after being killed mid-run, with no duplicated work.",
        "Respects robots.txt and a configurable request rate.",
        "Writes results to a database or structured files, atomically.",
        "A dry-run mode that shows what it would do."],
       stretch=["Add browser automation for one JavaScript-rendered source.",
                "Add a summary report emailed or posted at the end of a run."])

    pr("pj.p11.1", "p11", "A concurrency benchmark you can defend", "build",
       "The same workload implemented four ways, measured honestly.",
       "The point is not to find the fastest model. It is to be able to say "
       "which model suits which workload, and prove it.",
       ["One I/O-bound and one CPU-bound workload.",
        "Implementations with threads, processes, asyncio and plain sequential code.",
        "A benchmark harness that repeats runs and reports the spread, not one number.",
        "A results table in the README with the machine specification.",
        "A written explanation of why each model wins or loses where it does.",
        "A demonstration of cancellation that proves cleanup ran."],
       stretch=["Add a deliberate deadlock, show it, then fix it.",
                "Profile one implementation and make it 2x faster."])

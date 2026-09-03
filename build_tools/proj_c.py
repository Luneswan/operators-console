"""Projects for the later phases."""
from proj_lib import pr


def build():
    pr("pj.p12.1", "p12", "Reproducible from a bare machine", "ship",
       "Containerise a project you already have, and put a real pipeline in "
       "front of it.",
       "The test is not that it runs. The test is that someone who has never "
       "seen it runs it from the README alone.",
       ["A Dockerfile with a multi-stage build and a non-root user.",
        "A compose file bringing up the app and its database together.",
        "The image is smaller than the naive first attempt, and you can say why.",
        "CI runs tests, linting and type checks on every push.",
        "A deliberately broken test is caught by CI before it can merge.",
        "Deployed somewhere reachable, with the URL in the README.",
        "A documented rollback, tested at least once."],
       stretch=["Add a health check and a readiness probe.",
                "Add a staging environment promoted from the same image."])

    pr("pj.p13.1", "p13", "Break your own application", "drill",
       "Attack the API you built, find something real, fix it, and prove it "
       "stays fixed.",
       "Reading about injection teaches you the word. Finding one in your own "
       "code teaches you the habit.",
       ["A written threat model: what an attacker wants and how they might get it.",
        "At least one genuine vulnerability found in your own code.",
        "A regression test that fails before the fix and passes after.",
        "Password storage reviewed and justified at the algorithm level.",
        "Secrets removed from the repository and rotated.",
        "Dependency scan run, findings triaged, and the decisions recorded."],
       stretch=["Add security headers and prove them with a scanner.",
                "Complete an OWASP Top Ten review with a note per item."])

    pr("pj.p14.1", "p14", "A model with an evaluation you trust", "build",
       "Train something small, then spend most of the effort proving whether it "
       "actually works.",
       "The modelling is the easy half. Honest evaluation is what separates an "
       "engineer from a notebook.",
       ["A clean train, validation and test split, with no leakage.",
        "A baseline that is not machine learning at all, for comparison.",
        "Metrics chosen for the problem, and an explanation of why.",
        "An error analysis of the cases the model gets wrong.",
        "Reproducible results from a fixed seed and a recorded environment.",
        "A written statement of where the model should not be used."],
       stretch=["Serve it behind an API with input validation.",
                "Add monitoring for input drift."])

    pr("pj.p14.2", "p14", "A neural network from scratch", "build",
       "Implement forward and backward passes with no framework, then check "
       "your gradients.",
       "Autograd stops being magic the moment you have written the chain rule "
       "yourself and watched it agree with a numerical estimate.",
       ["A multi-layer network implemented in plain Python or NumPy.",
        "Backpropagation written by hand, not by a framework.",
        "Gradient checking against numerical differences, within tolerance.",
        "It learns a real task well enough to beat the baseline.",
        "A rewrite in PyTorch, with the two sets of results compared."],
       stretch=["Add a second optimiser and compare convergence.",
                "Write up what changed when you added normalisation."])

    pr("pj.p15.1", "p15", "A system with moving parts", "ship",
       "An API, a queue, a worker and a cache, wired together so that killing "
       "any one of them does not lose work.",
       "Architecture is only real when something fails. Until then it is a "
       "diagram.",
       ["An API that hands slow work to a queue and returns immediately.",
        "A worker that is safe to kill mid-job, with the job still completing.",
        "Idempotency, proven by running the same job twice with no double effect.",
        "Distributed tracing spanning API, queue and worker for one request.",
        "A cache with a stated invalidation strategy.",
        "An architecture decision record for every significant choice.",
        "A load test, and a named bottleneck it revealed."],
       stretch=["Add a dead-letter queue and a replay tool.",
                "Add a circuit breaker on an external dependency."])

    pr("pj.p16.1", "p16", "Make CPython show its work", "build",
       "Read the bytecode, measure the memory, and write a native extension "
       "that actually earns its complexity.",
       "The internals only matter when you can attach a number to them. This "
       "project is about producing those numbers.",
       ["Disassemble several functions and predict the bytecode before you look.",
        "Measure the memory layout of a list as it grows, and explain the jumps.",
        "Write one extension in C, Cython or Rust and benchmark it honestly.",
        "State the speedup and the maintenance cost you accepted for it.",
        "Profile a real bottleneck before optimising anything."],
       stretch=["Compare a free-threaded build against the default on your workload.",
                "Contribute a documentation fix upstream."])

    pr("pj.p17.1", "p17", "A pipeline that can be re-run safely", "build",
       "An orchestrated data pipeline with tests on the data itself.",
       "A pipeline nobody can re-run is a pipeline nobody can fix.",
       ["Extract, transform and load stages, each independently runnable.",
        "Re-running a stage produces the same result, not duplicates.",
        "Data quality tests that fail the run when an assumption breaks.",
        "Orchestration with retries, alerting and a visible run history.",
        "A backfill for a past date range, executed at least once.",
        "Schema changes handled by migration, not by hand."],
       stretch=["Add lineage documentation from source column to report.",
                "Add partitioning and show the query cost before and after."])

    pr("pj.p99.1", "p99", "Ship something a stranger relies on", "ship",
       "Build, release and maintain something other people actually use.",
       "Every earlier project had you as the only user. This one has a bug "
       "report from somebody you have never met.",
       ["Published where users can find and install it.",
        "A README good enough that nobody has to ask you how to start.",
        "At least one issue reported by someone else, and resolved.",
        "A versioned release history with a changelog.",
        "Tests and CI that let you accept a contribution without fear.",
        "A stated scope, including what the project deliberately will not do."],
       stretch=["Accept and review a pull request from a stranger.",
                "Write the post explaining what you learned building it."])

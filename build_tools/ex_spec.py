"""Exercises for the specialization phases, s01 to s14.

The grader runs submissions with the standard library only, so each
specialization is practised on the idea underneath its libraries: a pivot
table without pandas, IoU without a vision framework, a backtest that cannot
see the future. Clocks, senders and sleeps are passed in, so every check is
deterministic.
"""
from ex_lib import ex


def raises(call, exc="ValueError"):
    return ("try:\n"
            "    result = %s\n"
            "except %s:\n"
            "    pass\n"
            "else:\n"
            "    raise AssertionError('expected %s, but it returned %%r' %% (result,))"
            % (call, exc, exc))


def build():
    # -- s01 data analysis ---------------------------------------------------
    ex("s01.001", "s01", "Grouping", "Total by group", 2,
       """
       Write `group_totals(rows, key, value)` where `rows` is a list of dicts.
       Return a dict mapping each distinct `row[key]` to the sum of
       `row[value]` for that group. Skip rows where `row[value]` is `None`.

       `group_totals([{"k": "a", "v": 1}, {"k": "a", "v": 2}], "k", "v")`
       is `{"a": 3}`.
       """,
       """
       def group_totals(rows, key, value):
           pass
       """,
       [("one group", "assert group_totals([{'k': 'a', 'v': 1}, {'k': 'a', 'v': 2}], 'k', 'v') == {'a': 3}"),
        ("two groups", "assert group_totals([{'k': 'a', 'v': 1}, {'k': 'b', 'v': 5}], 'k', 'v') == {'a': 1, 'b': 5}"),
        ("skips missing values", "assert group_totals([{'k': 'a', 'v': None}, {'k': 'a', 'v': 4}], 'k', 'v') == {'a': 4}"),
        ("no rows", "assert group_totals([], 'k', 'v') == {}"),
        ("floats", "assert group_totals([{'k': 1, 'v': 0.5}, {'k': 1, 'v': 0.25}], 'k', 'v') == {1: 0.75}")],
       hints=["Walk the rows once and add each value to its group's running total.",
              "`out[g] = out.get(g, 0) + row[value]`, after `if row[value] is None: continue`."],
       solution="""
       def group_totals(rows, key, value):
           out = {}
           for row in rows:
               if row[value] is None:
                   continue
               group = row[key]
               out[group] = out.get(group, 0) + row[value]
           return out
       """)

    ex("s01.002", "s01", "Statistics", "Describe a column", 3,
       """
       Write `describe(values)` returning a dict with `count`, `mean`,
       `median` and `stdev` (the sample standard deviation) of the values,
       ignoring `None`. Raise `ValueError` if fewer than two values remain.

       The `statistics` module may be used.
       """,
       """
       def describe(values):
           pass
       """,
       [("basic", "d = describe([1, 2, 3, 4])\nassert (d['count'], d['mean'], d['median']) == (4, 2.5, 2.5)"),
        ("sample stdev", "assert round(describe([2, 4, 4, 4, 5, 5, 7, 9])['stdev'], 6) == 2.13809"),
        ("ignores None", "assert describe([None, 1, 3])['count'] == 2"),
        ("odd count median", "assert describe([5, 1, 3])['median'] == 3"),
        ("too few values", raises("describe([1, None])"))],
       hints=["Filter out `None` first, then check how many values are left.",
              "`statistics.mean`, `statistics.median` and `statistics.stdev` compute the three numbers."],
       solution="""
       import statistics


       def describe(values):
           data = [v for v in values if v is not None]
           if len(data) < 2:
               raise ValueError("need at least two values")
           return {"count": len(data), "mean": statistics.mean(data),
                   "median": statistics.median(data),
                   "stdev": statistics.stdev(data)}
       """)

    ex("s01.003", "s01", "Reshaping", "A pivot table", 4,
       """
       Write `pivot(rows, index, columns, values)` returning a dict of dicts:
       `{index_value: {column_value: total}}`, summing `row[values]` for each
       combination.

       Every inner dict must contain every column value that appears anywhere
       in the data, with `0` where a combination has no rows.
       """,
       """
       def pivot(rows, index, columns, values):
           pass
       """,
       [("simple", "rows = [{'r': 'x', 'c': 'a', 'v': 1}, {'r': 'x', 'c': 'b', 'v': 2}]\nassert pivot(rows, 'r', 'c', 'v') == {'x': {'a': 1, 'b': 2}}"),
        ("sums duplicates", "rows = [{'r': 'x', 'c': 'a', 'v': 1}, {'r': 'x', 'c': 'a', 'v': 4}]\nassert pivot(rows, 'r', 'c', 'v') == {'x': {'a': 5}}"),
        ("fills missing with zero", "rows = [{'r': 'x', 'c': 'a', 'v': 1}, {'r': 'y', 'c': 'b', 'v': 2}]\nassert pivot(rows, 'r', 'c', 'v') == {'x': {'a': 1, 'b': 0}, 'y': {'a': 0, 'b': 2}}"),
        ("empty", "assert pivot([], 'r', 'c', 'v') == {}")],
       hints=["Collect the set of column values first, then build each row's dict from it.",
              "Start every index value with `{col: 0 for col in all_columns}`, then add each row's value."],
       solution="""
       def pivot(rows, index, columns, values):
           cols = {row[columns] for row in rows}
           out = {}
           for row in rows:
               inner = out.setdefault(row[index], {c: 0 for c in cols})
               inner[row[columns]] += row[values]
           return out
       """)

    # -- s02 desktop apps ----------------------------------------------------
    ex("s02.001", "s02", "Settings", "Where settings live", 2,
       """
       Write `settings_dir(platform, home, env)` returning the folder where an
       app called `MyApp` should keep its settings, as a string with `/`
       separators:

       - `"win32"`: `env["APPDATA"] + "/MyApp"`
       - `"darwin"`: `home + "/Library/Application Support/MyApp"`
       - anything else: `env["XDG_CONFIG_HOME"] + "/MyApp"` if that variable
         is set and not empty, otherwise `home + "/.config/MyApp"`
       """,
       """
       def settings_dir(platform, home, env):
           pass
       """,
       [("windows", "assert settings_dir('win32', '/h', {'APPDATA': 'C:/Users/a/AppData/Roaming'}) == 'C:/Users/a/AppData/Roaming/MyApp'"),
        ("macos", "assert settings_dir('darwin', '/Users/a', {}) == '/Users/a/Library/Application Support/MyApp'"),
        ("linux default", "assert settings_dir('linux', '/home/a', {}) == '/home/a/.config/MyApp'"),
        ("linux with XDG", "assert settings_dir('linux', '/home/a', {'XDG_CONFIG_HOME': '/cfg'}) == '/cfg/MyApp'"),
        ("empty XDG is ignored", "assert settings_dir('linux', '/home/a', {'XDG_CONFIG_HOME': ''}) == '/home/a/.config/MyApp'")],
       hints=["Branch on the platform string first.",
              "`env.get(\"XDG_CONFIG_HOME\")` returns `None` when unset; an empty string is also falsy, so `if xdg:` covers both."],
       solution="""
       def settings_dir(platform, home, env):
           if platform == "win32":
               return env["APPDATA"] + "/MyApp"
           if platform == "darwin":
               return home + "/Library/Application Support/MyApp"
           xdg = env.get("XDG_CONFIG_HOME")
           if xdg:
               return xdg + "/MyApp"
           return home + "/.config/MyApp"
       """)

    ex("s02.002", "s02", "Worker threads", "A cancellable job", 3,
       """
       A GUI runs long work in a worker and lets the user cancel it. Write
       `run_job(items, work, cancelled, progress)`:

       - Before each item, call `cancelled()`. If it returns True, stop.
       - Otherwise call `work(item)`, then `progress(done, total)` with the
         number of items finished so far and the total.
       - Return `(done, was_cancelled)`.
       """,
       """
       def run_job(items, work, cancelled, progress):
           pass
       """,
       [("runs every item", "seen = []\nassert run_job([1, 2, 3], seen.append, lambda: False, lambda d, t: None) == (3, False)\nassert seen == [1, 2, 3]"),
        ("reports progress", "calls = []\nrun_job(['a', 'b'], lambda i: None, lambda: False, lambda d, t: calls.append((d, t)))\nassert calls == [(1, 2), (2, 2)]"),
        ("cancels before the next item", "state = {'n': 0}\ndef work(i):\n    state['n'] += 1\nassert run_job([1, 2, 3], work, lambda: state['n'] >= 2, lambda d, t: None) == (2, True)"),
        ("cancelled at once", "assert run_job([1], lambda i: None, lambda: True, lambda d, t: None) == (0, True)"),
        ("no items", "assert run_job([], lambda i: None, lambda: True, lambda d, t: None) == (0, False)")],
       hints=["Loop over the items and check `cancelled()` at the top of each iteration.",
              "Keep a `done` counter; return `(done, True)` from inside the loop when cancelled, and `(done, False)` after it."],
       solution="""
       def run_job(items, work, cancelled, progress):
           items = list(items)
           done = 0
           for item in items:
               if cancelled():
                   return done, True
               work(item)
               done += 1
               progress(done, len(items))
           return done, False
       """)

    ex("s02.003", "s02", "Model/view", "A table model", 4,
       """
       A view asks a model for rows instead of creating a widget per row.
       Write a class `TableModel(rows, columns)` where `rows` is a list of
       dicts and `columns` a list of keys, with:

       - `row_count()` and `column_count()` for the visible rows and columns
       - `data(r, c)`: the value at visible row `r`, column `c`, as a string
       - `sort(column, descending=False)`: stable sort by that column
       - `filter(text)`: show only rows where any column contains `text`,
         case-insensitively; `filter("")` shows all rows again
       """,
       """
       class TableModel:
           def __init__(self, rows, columns):
               pass
       """,
       [("counts", "m = TableModel([{'a': 1}, {'a': 2}], ['a'])\nassert (m.row_count(), m.column_count()) == (2, 1)"),
        ("data is text", "m = TableModel([{'a': 1, 'b': 'x'}], ['a', 'b'])\nassert m.data(0, 0) == '1'\nassert m.data(0, 1) == 'x'"),
        ("sorts", "m = TableModel([{'n': 3}, {'n': 1}, {'n': 2}], ['n'])\nm.sort('n', descending=True)\nassert [m.data(i, 0) for i in range(3)] == ['3', '2', '1']"),
        ("filters case-insensitively", "m = TableModel([{'n': 'Ada'}, {'n': 'Bob'}], ['n'])\nm.filter('ad')\nassert m.row_count() == 1\nassert m.data(0, 0) == 'Ada'"),
        ("clearing the filter", "m = TableModel([{'n': 'Ada'}, {'n': 'Bob'}], ['n'])\nm.filter('x')\nm.filter('')\nassert m.row_count() == 2")],
       hints=["Keep the full rows and a separate list of the visible ones.",
              "Sort the full list with `key=lambda r: r[column]`, then reapply the current filter to rebuild the visible list."],
       solution="""
       class TableModel:
           def __init__(self, rows, columns):
               self.rows = list(rows)
               self.columns = list(columns)
               self.text = ""
               self.visible = list(self.rows)

           def row_count(self):
               return len(self.visible)

           def column_count(self):
               return len(self.columns)

           def data(self, r, c):
               return str(self.visible[r][self.columns[c]])

           def sort(self, column, descending=False):
               self.rows.sort(key=lambda row: row[column], reverse=descending)
               self.filter(self.text)

           def filter(self, text):
               self.text = text
               needle = text.lower()
               self.visible = [row for row in self.rows
                               if not needle or any(needle in str(row[c]).lower()
                                                    for c in self.columns)]
       """)

    # -- s03 command-line tools ----------------------------------------------
    ex("s03.001", "s03", "Exit codes", "Usage errors and exit codes", 2,
       """
       Write `main(argv, stdout, stderr)` for a tool that prints how many
       words it was given.

       - With no arguments, write `usage: count WORD...` and a newline to
         `stderr` and return `2`.
       - Otherwise write the number of arguments and a newline to `stdout`
         and return `0`.

       `stdout` and `stderr` are file-like objects; use their `write` method.
       """,
       """
       def main(argv, stdout, stderr):
           pass
       """,
       [("counts words", "import io\nout, err = io.StringIO(), io.StringIO()\nassert main(['a', 'b'], out, err) == 0\nassert out.getvalue() == '2\\n'\nassert err.getvalue() == ''"),
        ("usage on stderr", "import io\nout, err = io.StringIO(), io.StringIO()\nassert main([], out, err) == 2\nassert err.getvalue() == 'usage: count WORD...\\n'\nassert out.getvalue() == ''"),
        ("one word", "import io\nout = io.StringIO()\nassert main(['x'], out, io.StringIO()) == 0\nassert out.getvalue() == '1\\n'"),
        ("returns an int", "import io\nassert isinstance(main([], io.StringIO(), io.StringIO()), int)")],
       hints=["Errors go to stderr and change the exit code; results go to stdout.",
              "`stderr.write(\"usage: count WORD...\\n\")` then `return 2`."],
       solution="""
       def main(argv, stdout, stderr):
           if not argv:
               stderr.write("usage: count WORD...\\n")
               return 2
           stdout.write("%d\\n" % len(argv))
           return 0
       """)

    ex("s03.002", "s03", "Configuration", "Settings precedence", 3,
       """
       Write `resolve(name, flags, env, config, default)` returning a setting
       from the first source that has it:

       1. `flags[name]`, if present and not `None`
       2. `env["APP_" + name.upper()]`, if present
       3. `config[name]`, if present
       4. `default`
       """,
       """
       def resolve(name, flags, env, config, default):
           pass
       """,
       [("flag wins", "assert resolve('port', {'port': 1}, {'APP_PORT': '2'}, {'port': 3}, 4) == 1"),
        ("env next", "assert resolve('port', {'port': None}, {'APP_PORT': '2'}, {'port': 3}, 4) == '2'"),
        ("config next", "assert resolve('port', {}, {}, {'port': 3}, 4) == 3"),
        ("default last", "assert resolve('port', {}, {}, {}, 4) == 4"),
        ("env name is prefixed and upper-case", "assert resolve('log_level', {}, {'APP_LOG_LEVEL': 'debug'}, {}, 'info') == 'debug'")],
       hints=["Check the sources in order and return as soon as one has the value.",
              "A flag set to `None` means \"not given\": test `flags.get(name) is not None`."],
       solution="""
       def resolve(name, flags, env, config, default):
           if flags.get(name) is not None:
               return flags[name]
           key = "APP_" + name.upper()
           if key in env:
               return env[key]
           if name in config:
               return config[name]
           return default
       """)

    ex("s03.003", "s03", "argparse", "Subcommands", 4,
       """
       Write `build_parser()` returning an `argparse.ArgumentParser` for a
       to-do tool with two subcommands, stored in `args.command`:

       - `add NAME [--priority N]`: `args.name`, and `args.priority` as an
         `int` defaulting to `1`
       - `list [--json]`: `args.json`, `False` unless the flag is given
       """,
       """
       import argparse


       def build_parser():
           pass
       """,
       [("add with default priority", "a = build_parser().parse_args(['add', 'milk'])\nassert (a.command, a.name, a.priority) == ('add', 'milk', 1)"),
        ("priority is an int", "a = build_parser().parse_args(['add', 'milk', '--priority', '3'])\nassert a.priority == 3"),
        ("list", "a = build_parser().parse_args(['list'])\nassert (a.command, a.json) == ('list', False)"),
        ("list json", "assert build_parser().parse_args(['list', '--json']).json is True"),
        ("bad priority exits", "try:\n    build_parser().parse_args(['add', 'x', '--priority', 'high'])\nexcept SystemExit as e:\n    assert e.code == 2\nelse:\n    raise AssertionError('expected SystemExit, but it parsed the arguments')")],
       hints=["`parser.add_subparsers(dest=\"command\")` creates the subcommands.",
              "`add.add_argument(\"--priority\", type=int, default=1)` and `lst.add_argument(\"--json\", action=\"store_true\")`."],
       solution="""
       import argparse


       def build_parser():
           parser = argparse.ArgumentParser(prog="todo")
           sub = parser.add_subparsers(dest="command", required=True)
           add = sub.add_parser("add")
           add.add_argument("name")
           add.add_argument("--priority", type=int, default=1)
           lst = sub.add_parser("list")
           lst.add_argument("--json", action="store_true")
           return parser
       """)

    # -- s04 games -----------------------------------------------------------
    ex("s04.001", "s04", "Game loop", "Move by delta time", 2,
       """
       Write `move(position, velocity, dt)` returning the new `(x, y)` after
       `dt` seconds, where `position` and `velocity` are `(x, y)` tuples in
       pixels and pixels per second.

       Moving for one second must give the same result whether it is done in
       60 steps of 1/60 s or 30 steps of 1/30 s.
       """,
       """
       def move(position, velocity, dt):
           pass
       """,
       [("one step", "assert move((0, 0), (10, 20), 0.5) == (5.0, 10.0)"),
        ("no time", "assert move((3, 4), (100, 100), 0) == (3, 4)"),
        ("negative velocity", "assert move((10, 10), (-10, 0), 1) == (0, 10)"),
        ("frame-rate independent", "p = q = (0.0, 0.0)\nfor _ in range(60):\n    p = move(p, (120, 0), 1 / 60)\nfor _ in range(30):\n    q = move(q, (120, 0), 1 / 30)\nassert round(p[0], 9) == round(q[0], 9)\nassert round(p[0], 9) == 120")],
       hints=["Distance is speed multiplied by time.",
              "`return (x + vx * dt, y + vy * dt)`."],
       solution="""
       def move(position, velocity, dt):
           x, y = position
           vx, vy = velocity
           return (x + vx * dt, y + vy * dt)
       """)

    ex("s04.002", "s04", "Collision", "Rectangles that collide", 3,
       """
       A rectangle is `(x, y, w, h)`. Write:

       - `overlaps(a, b)`: True when the rectangles share some area. Touching
         edges do not count.
       - `first_hit(mover, obstacles)`: the index of the first obstacle that
         overlaps `mover`, or `None`.
       """,
       """
       def overlaps(a, b):
           pass


       def first_hit(mover, obstacles):
           pass
       """,
       [("overlap", "assert overlaps((0, 0, 10, 10), (5, 5, 10, 10))"),
        ("apart", "assert not overlaps((0, 0, 10, 10), (20, 0, 5, 5))"),
        ("touching edges", "assert not overlaps((0, 0, 10, 10), (10, 0, 5, 5))"),
        ("contained", "assert overlaps((0, 0, 10, 10), (2, 2, 1, 1))"),
        ("first hit", "assert first_hit((0, 0, 4, 4), [(10, 10, 1, 1), (3, 3, 2, 2), (1, 1, 1, 1)]) == 1"),
        ("no hit", "assert first_hit((0, 0, 1, 1), [(5, 5, 1, 1)]) is None")],
       hints=["Two rectangles overlap when they overlap on the x axis and on the y axis.",
              "On x: `a.x < b.x + b.w and b.x < a.x + a.w`. Strict `<` makes touching edges not overlap."],
       solution="""
       def overlaps(a, b):
           ax, ay, aw, ah = a
           bx, by, bw, bh = b
           return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


       def first_hit(mover, obstacles):
           for i, obstacle in enumerate(obstacles):
               if overlaps(mover, obstacle):
                   return i
           return None
       """)

    ex("s04.003", "s04", "State machines", "A game state machine", 4,
       """
       Write a class `Game` that starts in state `"menu"` and has
       `handle(event)` with these transitions:

       - menu + `"start"` -> playing
       - playing + `"pause"` -> paused; paused + `"resume"` -> playing
       - playing + `"die"` -> game_over; game_over + `"restart"` -> menu

       Any other event raises `ValueError` and leaves the state unchanged.
       `game.state` is the current state and `game.history` lists every
       state entered, starting with `"menu"`.
       """,
       """
       class Game:
           pass
       """,
       [("starts in the menu", "g = Game()\nassert g.state == 'menu'\nassert g.history == ['menu']"),
        ("plays and pauses", "g = Game()\ng.handle('start'); g.handle('pause'); g.handle('resume')\nassert g.state == 'playing'"),
        ("full loop", "g = Game()\nfor e in ['start', 'die', 'restart']:\n    g.handle(e)\nassert g.history == ['menu', 'playing', 'game_over', 'menu']"),
        ("invalid event", "g = Game()\ntry:\n    g.handle('pause')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError, but it accepted pause in the menu')\nassert g.state == 'menu'")],
       hints=["Keep the transitions in a dict keyed by `(state, event)`.",
              "`TRANSITIONS = {(\"menu\", \"start\"): \"playing\", ...}`; look the pair up and raise `ValueError` when it is missing."],
       solution="""
       TRANSITIONS = {
           ("menu", "start"): "playing",
           ("playing", "pause"): "paused",
           ("paused", "resume"): "playing",
           ("playing", "die"): "game_over",
           ("game_over", "restart"): "menu",
       }


       class Game:
           def __init__(self):
               self.state = "menu"
               self.history = ["menu"]

           def handle(self, event):
               nxt = TRANSITIONS.get((self.state, event))
               if nxt is None:
                   raise ValueError("%s is not allowed in %s" % (event, self.state))
               self.state = nxt
               self.history.append(nxt)
       """)

    # -- s05 scientific computing --------------------------------------------
    ex("s05.001", "s05", "Integration", "The trapezoid rule", 2,
       """
       Write `trapezoid(f, a, b, n)` approximating the integral of `f` from
       `a` to `b` with `n` equal trapezoids. Raise `ValueError` if `n` is
       below 1.
       """,
       """
       def trapezoid(f, a, b, n):
           pass
       """,
       [("a straight line is exact", "assert round(trapezoid(lambda x: 2 * x, 0, 1, 1), 9) == 1"),
        ("x squared", "assert round(trapezoid(lambda x: x * x, 0, 1, 1000), 6) == round(1 / 3, 6)"),
        ("more steps, less error", "e1 = abs(trapezoid(lambda x: x ** 3, 0, 2, 10) - 4)\ne2 = abs(trapezoid(lambda x: x ** 3, 0, 2, 100) - 4)\nassert e2 < e1"),
        ("rejects zero steps", raises("trapezoid(lambda x: x, 0, 1, 0)"))],
       hints=["Each trapezoid has width `h = (b - a) / n` and area `h * (f(left) + f(right)) / 2`.",
              "Sum over `i` in `range(n)` with `left = a + i * h` and `right = left + h`."],
       solution="""
       def trapezoid(f, a, b, n):
           if n < 1:
               raise ValueError("n must be at least 1")
           h = (b - a) / n
           total = 0.0
           for i in range(n):
               left = a + i * h
               total += (f(left) + f(left + h)) * h / 2
           return total
       """)

    ex("s05.002", "s05", "Root finding", "Newton's method", 3,
       """
       Write `newton(f, df, x0, tol=1e-12, max_iter=50)` finding a root of `f`
       from the starting guess `x0`, where `df` is the derivative of `f`.

       Stop when a step changes x by less than `tol` and return x. Raise
       `ValueError` if the derivative is zero at some step, or if no
       convergence happens within `max_iter` steps.
       """,
       """
       def newton(f, df, x0, tol=1e-12, max_iter=50):
           pass
       """,
       [("square root of 2", "assert round(newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0), 12) == round(2 ** 0.5, 12)"),
        ("cube root", "assert round(newton(lambda x: x ** 3 - 27, lambda x: 3 * x * x, 5.0), 10) == 3"),
        ("zero derivative", raises("newton(lambda x: x * x + 1, lambda x: 2 * x, 0.0)")),
        ("does not converge", raises("newton(lambda x: x * x + 1, lambda x: 2 * x, 1.0, max_iter=20)"))],
       hints=["Each step is `x_new = x - f(x) / df(x)`.",
              "Loop `max_iter` times; check `df(x) == 0` before dividing, and return when `abs(x_new - x) < tol`."],
       solution="""
       def newton(f, df, x0, tol=1e-12, max_iter=50):
           x = x0
           for _ in range(max_iter):
               slope = df(x)
               if slope == 0:
                   raise ValueError("zero derivative")
               nxt = x - f(x) / slope
               if abs(nxt - x) < tol:
                   return nxt
               x = nxt
           raise ValueError("did not converge")
       """)

    ex("s05.003", "s05", "Simulation", "Euler steps for an ODE", 4,
       """
       Write `euler(f, y0, t0, t1, steps)` solving `dy/dt = f(t, y)` from
       `t0` to `t1` with the forward Euler method. Return a list of `(t, y)`
       pairs, `steps + 1` long, starting with `(t0, y0)`.
       """,
       """
       def euler(f, y0, t0, t1, steps):
           pass
       """,
       [("shape", "path = euler(lambda t, y: 0, 5, 0, 1, 4)\nassert len(path) == 5\nassert path[0] == (0, 5)\nassert path[-1][1] == 5"),
        ("constant slope", "path = euler(lambda t, y: 2, 0, 0, 3, 3)\nassert round(path[-1][1], 9) == 6"),
        ("ends at t1", "assert round(euler(lambda t, y: y, 1, 0, 1, 7)[-1][0], 9) == 1"),
        ("error shrinks with more steps", "import math\ne1 = abs(euler(lambda t, y: y, 1, 0, 1, 10)[-1][1] - math.e)\ne2 = abs(euler(lambda t, y: y, 1, 0, 1, 100)[-1][1] - math.e)\nassert e2 < e1 / 5")],
       hints=["Each step moves `h = (t1 - t0) / steps` forward in time.",
              "`y = y + h * f(t, y)`, then `t = t0 + (i + 1) * h`; append `(t, y)` each time."],
       solution="""
       def euler(f, y0, t0, t1, steps):
           h = (t1 - t0) / steps
           t, y = t0, y0
           path = [(t, y)]
           for i in range(steps):
               y = y + h * f(t, y)
               t = t0 + (i + 1) * h
               path.append((t, y))
           return path
       """)

    # -- s06 quantitative finance --------------------------------------------
    ex("s06.001", "s06", "Returns", "Returns from prices", 2,
       """
       Write:

       - `simple_returns(prices)`: the list of `p[i] / p[i - 1] - 1` for each
         price after the first
       - `growth(returns)`: the total growth of 1.0 invested through those
         returns, minus 1
       """,
       """
       def simple_returns(prices):
           pass


       def growth(returns):
           pass
       """,
       [("returns", "r = simple_returns([100, 110, 99])\nassert [round(x, 6) for x in r] == [0.1, -0.1]"),
        ("one price", "assert simple_returns([100]) == []"),
        ("growth compounds", "assert round(growth([0.1, -0.1]), 6) == -0.01"),
        ("round trip", "assert round(growth(simple_returns([50, 75, 60, 90])), 9) == 0.8")],
       hints=["Pair each price with the one before it.",
              "Growth multiplies `(1 + r)` for every return, then subtracts 1."],
       solution="""
       def simple_returns(prices):
           return [b / a - 1 for a, b in zip(prices, prices[1:])]


       def growth(returns):
           total = 1.0
           for r in returns:
               total *= 1 + r
           return total - 1
       """)

    ex("s06.002", "s06", "Risk", "Maximum drawdown", 3,
       """
       Write `max_drawdown(values)` returning the largest fall from a running
       peak as a positive fraction. For `[100, 120, 90, 130]` the peak 120
       falls to 90, a drawdown of 0.25. Return 0.0 if the values never fall.
       """,
       """
       def max_drawdown(values):
           pass
       """,
       [("example", "assert round(max_drawdown([100, 120, 90, 130]), 9) == 0.25"),
        ("never falls", "assert max_drawdown([1, 2, 3]) == 0.0"),
        ("worst of two", "assert round(max_drawdown([100, 80, 100, 50]), 9) == 0.5"),
        ("falls at the end", "assert round(max_drawdown([10, 12, 6]), 9) == 0.5"),
        ("single value", "assert max_drawdown([5]) == 0.0")],
       hints=["Track the highest value seen so far as you walk the list.",
              "At each value, the drawdown is `1 - value / peak`; keep the largest."],
       solution="""
       def max_drawdown(values):
           peak = values[0]
           worst = 0.0
           for value in values:
               peak = max(peak, value)
               worst = max(worst, 1 - value / peak)
           return worst
       """)

    ex("s06.003", "s06", "Backtesting", "A backtest that cannot see the future", 4,
       """
       Write `backtest(prices, signal, fee)` for daily closing prices.

       - At each day `t` except the last, call `signal(history)` with a tuple
         of the prices up to and including day `t`. It returns 1 (invested)
         or 0 (in cash).
       - The position chosen on day `t` earns the return from `t` to `t + 1`.
       - Each time the position changes, pay `fee` as a fraction of equity.
       - Start with equity 1.0 in cash and return the final equity.

       The signal must never receive a price from after day `t`.
       """,
       """
       def backtest(prices, signal, fee):
           pass
       """,
       [("always in", "assert round(backtest([100, 110, 121], lambda h: 1, 0), 9) == 1.21"),
        ("always out", "assert backtest([100, 50, 200], lambda h: 0, 0.01) == 1.0"),
        ("fee on entry", "assert round(backtest([100, 110], lambda h: 1, 0.01), 9) == round(0.99 * 1.1, 9)"),
        ("no future prices", "seen = []\ndef spy(h):\n    seen.append(len(h))\n    return 1\nbacktest([1, 2, 3, 4], spy, 0)\nassert seen == [1, 2, 3]"),
        ("history is read-only", "def s(h):\n    assert isinstance(h, tuple)\n    return 0\nbacktest([1, 2], s, 0)")],
       hints=["Loop `t` from 0 to `len(prices) - 2`; pass `tuple(prices[:t + 1])` to the signal.",
              "If the new position differs from the old one, multiply equity by `1 - fee`; if invested, multiply by `prices[t + 1] / prices[t]`."],
       solution="""
       def backtest(prices, signal, fee):
           equity = 1.0
           position = 0
           for t in range(len(prices) - 1):
               wanted = signal(tuple(prices[:t + 1]))
               if wanted != position:
                   equity *= 1 - fee
                   position = wanted
               if position:
                   equity *= prices[t + 1] / prices[t]
           return equity
       """)

    # -- s07 computer vision -------------------------------------------------
    ex("s07.001", "s07", "Pixels", "Grayscale an image", 2,
       """
       An image is a list of rows, each a list of `(r, g, b)` tuples with
       values 0-255. Write `to_gray(image)` returning the same shape with each
       pixel replaced by `round(0.299 * r + 0.587 * g + 0.114 * b)`.
       """,
       """
       def to_gray(image):
           pass
       """,
       [("white", "assert to_gray([[(255, 255, 255)]]) == [[255]]"),
        ("black", "assert to_gray([[(0, 0, 0)]]) == [[0]]"),
        ("pure red", "assert to_gray([[(255, 0, 0)]]) == [[76]]"),
        ("keeps the shape", "img = [[(10, 20, 30)] * 3] * 2\nout = to_gray(img)\nassert len(out) == 2\nassert [len(row) for row in out] == [3, 3]")],
       hints=["Transform every pixel and keep the row structure.",
              "`[[round(0.299 * r + 0.587 * g + 0.114 * b) for (r, g, b) in row] for row in image]`."],
       solution="""
       def to_gray(image):
           return [[round(0.299 * r + 0.587 * g + 0.114 * b) for (r, g, b) in row]
                   for row in image]
       """)

    ex("s07.002", "s07", "Detection metrics", "Intersection over union", 3,
       """
       A box is `(x1, y1, x2, y2)` with `x1 < x2` and `y1 < y2`. Write
       `iou(a, b)` returning the area of the intersection divided by the area
       of the union. Boxes that do not overlap give 0.0.
       """,
       """
       def iou(a, b):
           pass
       """,
       [("identical", "assert iou((0, 0, 2, 2), (0, 0, 2, 2)) == 1.0"),
        ("half overlap", "assert round(iou((0, 0, 2, 2), (1, 0, 3, 2)), 9) == round(1 / 3, 9)"),
        ("apart", "assert iou((0, 0, 1, 1), (2, 2, 3, 3)) == 0.0"),
        ("touching", "assert iou((0, 0, 1, 1), (1, 0, 2, 1)) == 0.0"),
        ("contained", "assert round(iou((0, 0, 4, 4), (1, 1, 3, 3)), 9) == 0.25")],
       hints=["The intersection box runs from the larger of the starts to the smaller of the ends.",
              "Width is `max(0, min(ax2, bx2) - max(ax1, bx1))`; union is area A + area B - intersection."],
       solution="""
       def iou(a, b):
           ax1, ay1, ax2, ay2 = a
           bx1, by1, bx2, by2 = b
           w = max(0, min(ax2, bx2) - max(ax1, bx1))
           h = max(0, min(ay2, by2) - max(ay1, by1))
           inter = w * h
           union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
           return inter / union if union else 0.0
       """)

    ex("s07.003", "s07", "Convolution", "A convolution layer's core", 4,
       """
       Write `convolve(image, kernel)` for 2D lists of numbers. Slide the
       kernel over every position where it fits entirely inside the image
       ("valid" mode) and, at each position, sum the element-wise products.
       Do not flip the kernel; this is what convolution layers compute.

       The output has `H - kh + 1` rows and `W - kw + 1` columns.
       """,
       """
       def convolve(image, kernel):
           pass
       """,
       [("identity kernel", "assert convolve([[1, 2], [3, 4]], [[1]]) == [[1, 2], [3, 4]]"),
        ("sum kernel", "assert convolve([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 1], [1, 1]]) == [[12, 16], [24, 28]]"),
        ("edge kernel", "assert convolve([[0, 0, 9, 9]], [[-1, 1]]) == [[0, 9, 0]]"),
        ("output shape", "out = convolve([[0] * 5 for _ in range(4)], [[1, 0, 0], [0, 1, 0]])\nassert len(out) == 3\nassert len(out[0]) == 3"),
        ("not flipped", "assert convolve([[1, 2]], [[1, 0]]) == [[1]]")],
       hints=["Four nested loops: output row, output column, kernel row, kernel column.",
              "`out[i][j] = sum(image[i + a][j + b] * kernel[a][b] for a in range(kh) for b in range(kw))`."],
       solution="""
       def convolve(image, kernel):
           kh, kw = len(kernel), len(kernel[0])
           h, w = len(image), len(image[0])
           return [[sum(image[i + a][j + b] * kernel[a][b]
                        for a in range(kh) for b in range(kw))
                    for j in range(w - kw + 1)]
                   for i in range(h - kh + 1)]
       """)

    # -- s08 NLP -------------------------------------------------------------
    ex("s08.001", "s08", "Tokenization", "Normalize and tokenize", 2,
       """
       Write `tokens(text)` that normalizes the text with Unicode NFKC,
       lowercases it, and returns the list of words: runs of letters, digits
       and apostrophes.
       """,
       """
       def tokens(text):
           pass
       """,
       [("basic", "assert tokens('Hello, World!') == ['hello', 'world']"),
        ("apostrophes", "assert tokens(\"Don't stop\") == [\"don't\", 'stop']"),
        ("numbers", "assert tokens('Route 66') == ['route', '66']"),
        ("NFKC", "assert tokens('ﬁne') == ['fine']"),
        ("empty", "assert tokens('...') == []")],
       hints=["`unicodedata.normalize(\"NFKC\", text)` turns the ligature `ﬁ` into `fi`; then call `.lower()`.",
              "`re.findall(r\"[^\\W_]+(?:'[^\\W_]+)*\", text)` matches letters and digits, with apostrophes inside a word."],
       solution="""
       import re
       import unicodedata


       def tokens(text):
           text = unicodedata.normalize("NFKC", text).lower()
           return re.findall(r"[^\\W_]+(?:'[^\\W_]+)*", text)
       """)

    ex("s08.002", "s08", "Weighting", "TF-IDF", 3,
       """
       `docs` is a list of documents, each a list of tokens. Write
       `tf_idf(docs)` returning one dict per document mapping each of its
       terms to `tf * idf`, where:

       - `tf` = the term's count in the document / the document's length
       - `idf` = `math.log(N / df)`, with `N` documents and `df` the number
         of documents that contain the term
       """,
       """
       def tf_idf(docs):
           pass
       """,
       [("a term in every document scores zero", "out = tf_idf([['a', 'b'], ['a']])\nassert out[0]['a'] == 0\nassert out[1]['a'] == 0"),
        ("rare term", "import math\nout = tf_idf([['a', 'b'], ['a']])\nassert round(out[0]['b'], 9) == round(0.5 * math.log(2), 9)"),
        ("repeats raise tf", "import math\nout = tf_idf([['x', 'x', 'y'], ['y']])\nassert round(out[0]['x'], 9) == round((2 / 3) * math.log(2), 9)"),
        ("one dict per document", "assert len(tf_idf([['a'], ['b'], ['c']])) == 3")],
       hints=["Count document frequency first: for each document, add 1 for each distinct term.",
              "Then for each document, `Counter(doc)` gives counts; divide by `len(doc)` and multiply by the idf."],
       solution="""
       import math
       from collections import Counter


       def tf_idf(docs):
           n = len(docs)
           df = Counter()
           for doc in docs:
               df.update(set(doc))
           out = []
           for doc in docs:
               counts = Counter(doc)
               out.append({term: (c / len(doc)) * math.log(n / df[term])
                           for term, c in counts.items()})
           return out
       """)

    ex("s08.003", "s08", "Evaluation", "Precision, recall and F1", 4,
       """
       Write `scores(true, pred, label)` for two equal-length lists of labels.
       Return `(precision, recall, f1)` for `label`. Any ratio with a zero
       denominator is 0.0.
       """,
       """
       def scores(true, pred, label):
           pass
       """,
       [("perfect", "assert scores(['a', 'b'], ['a', 'b'], 'a') == (1.0, 1.0, 1.0)"),
        ("mixed", "p, r, f = scores(['a', 'a', 'b', 'b'], ['a', 'b', 'a', 'a'], 'a')\nassert (round(p, 6), round(r, 6), round(f, 6)) == (0.333333, 0.5, 0.4)"),
        ("never predicted", "assert scores(['a'], ['b'], 'a') == (0.0, 0.0, 0.0)"),
        ("label absent", "assert scores(['b'], ['b'], 'a') == (0.0, 0.0, 0.0)"),
        ("lengths must match", raises("scores(['a'], [], 'a')"))],
       hints=["Count true positives, false positives and false negatives for the label.",
              "precision = tp / (tp + fp), recall = tp / (tp + fn), f1 = 2pr / (p + r); guard each division."],
       solution="""
       def scores(true, pred, label):
           if len(true) != len(pred):
               raise ValueError("lengths differ")
           tp = sum(1 for t, p in zip(true, pred) if t == label and p == label)
           fp = sum(1 for t, p in zip(true, pred) if t != label and p == label)
           fn = sum(1 for t, p in zip(true, pred) if t == label and p != label)
           precision = tp / (tp + fp) if tp + fp else 0.0
           recall = tp / (tp + fn) if tp + fn else 0.0
           f1 = (2 * precision * recall / (precision + recall)
                 if precision + recall else 0.0)
           return precision, recall, f1
       """)

    # -- s09 testing ---------------------------------------------------------
    ex("s09.001", "s09", "Test doubles", "A fake clock", 2,
       """
       Code that reads the real clock is hard to test. Write a class
       `FakeClock(start=0.0)` with `now()` and `advance(seconds)`, and a
       function `is_expired(created, ttl, clock)` that is True once
       `clock.now()` is at least `created + ttl`.
       """,
       """
       class FakeClock:
           pass


       def is_expired(created, ttl, clock):
           pass
       """,
       [("starts where told", "assert FakeClock(5).now() == 5"),
        ("advances", "c = FakeClock()\nc.advance(2.5)\nc.advance(1)\nassert c.now() == 3.5"),
        ("not yet expired", "c = FakeClock(10)\nassert not is_expired(5, 10, c)"),
        ("expires exactly at the ttl", "c = FakeClock(15)\nassert is_expired(5, 10, c)"),
        ("expires after advancing", "c = FakeClock(0)\nc.advance(60)\nassert is_expired(0, 30, c)")],
       hints=["The fake clock is just a number you control.",
              "`now()` returns it; `advance` adds to it; `is_expired` compares `clock.now() >= created + ttl`."],
       solution="""
       class FakeClock:
           def __init__(self, start=0.0):
               self.time = start

           def now(self):
               return self.time

           def advance(self, seconds):
               self.time += seconds


       def is_expired(created, ttl, clock):
           return clock.now() >= created + ttl
       """)

    ex("s09.002", "s09", "Shrinking", "Find the smallest failing input", 3,
       """
       Property-based testing tools shrink a failing input to the smallest one
       that still fails. Write `shrink(items, fails)`: repeatedly try removing
       one element at a time; whenever the shorter list still makes
       `fails(list)` return True, keep it and start over. Return the list when
       no single removal still fails.
       """,
       """
       def shrink(items, fails):
           pass
       """,
       [("finds the culprit", "assert shrink([1, 2, 3, 99, 4], lambda xs: 99 in xs) == [99]"),
        ("pair", "assert shrink([5, 1, 7, 3], lambda xs: 1 in xs and 3 in xs) == [1, 3]"),
        ("sum threshold", "out = shrink([1, 2, 3, 4], lambda xs: sum(xs) > 5)\nassert sum(out) > 5\nassert [x for x in out if sum(out) - x > 5] == []"),
        ("already minimal", "assert shrink([7], lambda xs: 7 in xs) == [7]"),
        ("keeps order", "assert shrink([3, 9, 1], lambda xs: len(xs) >= 2 and xs[0] > xs[-1]) in ([3, 1], [9, 1])")],
       hints=["Try each index; build the list without that element and test it.",
              "Use a `while` loop that restarts whenever a removal still fails, and stops when a full pass changes nothing."],
       solution="""
       def shrink(items, fails):
           current = list(items)
           changed = True
           while changed:
               changed = False
               for i in range(len(current)):
                   candidate = current[:i] + current[i + 1:]
                   if fails(candidate):
                       current = candidate
                       changed = True
                       break
           return current
       """)

    ex("s09.003", "s09", "Test runners", "A tiny test runner", 4,
       """
       Write `run_tests(namespace)` where `namespace` is a dict of names to
       objects. Run every callable whose name starts with `test_`, in sorted
       name order, and return a dict mapping each name to:

       - `"pass"` if it returns normally
       - `"fail"` if it raises `AssertionError`
       - `"error"` for any other exception
       """,
       """
       def run_tests(namespace):
           pass
       """,
       [("pass and fail", "def test_a():\n    return None\ndef test_b():\n    assert 1 == 2\nassert run_tests({'test_a': test_a, 'test_b': test_b}) == {'test_a': 'pass', 'test_b': 'fail'}"),
        ("error", "def test_c():\n    raise KeyError('x')\nassert run_tests({'test_c': test_c}) == {'test_c': 'error'}"),
        ("ignores other names", "assert run_tests({'helper': lambda: 1, 'test_x': 5}) == {}"),
        ("runs in sorted order", "order = []\nns = {'test_b': lambda: order.append('b'), 'test_a': lambda: order.append('a')}\nrun_tests(ns)\nassert order == ['a', 'b']")],
       hints=["Filter the names first: `name.startswith(\"test_\") and callable(obj)`.",
              "Wrap each call in `try`; catch `AssertionError` before `Exception`, since it is a subclass."],
       solution="""
       def run_tests(namespace):
           results = {}
           for name in sorted(namespace):
               test = namespace[name]
               if not name.startswith("test_") or not callable(test):
                   continue
               try:
                   test()
               except AssertionError:
                   results[name] = "fail"
               except Exception:
                   results[name] = "error"
               else:
                   results[name] = "pass"
           return results
       """)

    # -- s10 network automation ----------------------------------------------
    ex("s10.001", "s10", "Parsing output", "Parse interface status", 2,
       """
       Write `parse_brief(text)` for the output of `show ip interface brief`:

           Interface   IP-Address   OK? Method Status   Protocol
           Gi0/0       10.0.0.1     YES manual up       up
           Gi0/1       unassigned   YES unset  down     down

       Return a list of dicts with keys `name`, `ip`, `status` and
       `protocol`. Skip the header line and blank lines. Status values may be
       two words, such as `administratively down`.
       """,
       """
       def parse_brief(text):
           pass
       """,
       [("two interfaces", "t = 'Interface IP-Address OK? Method Status Protocol\\nGi0/0 10.0.0.1 YES manual up up\\nGi0/1 unassigned YES unset down down\\n'\nout = parse_brief(t)\nassert out[0] == {'name': 'Gi0/0', 'ip': '10.0.0.1', 'status': 'up', 'protocol': 'up'}\nassert out[1]['ip'] == 'unassigned'"),
        ("skips blank lines", "t = 'Interface IP-Address OK? Method Status Protocol\\n\\nGi0/0 1.1.1.1 YES manual up up\\n'\nassert len(parse_brief(t)) == 1"),
        ("two-word status", "t = 'Interface IP-Address OK? Method Status Protocol\\nGi0/2 unassigned YES unset administratively down down\\n'\nassert parse_brief(t)[0]['status'] == 'administratively down'"),
        ("header only", "assert parse_brief('Interface IP-Address OK? Method Status Protocol\\n') == []")],
       hints=["Split each line on whitespace: the first two fields and the last one are fixed.",
              "Fields 0 and 1 are name and ip, the last is protocol, and fields 4 up to the last one form the status."],
       solution="""
       def parse_brief(text):
           out = []
           for line in text.splitlines():
               parts = line.split()
               if not parts or parts[0] == "Interface":
                   continue
               out.append({"name": parts[0], "ip": parts[1],
                           "status": " ".join(parts[4:-1]),
                           "protocol": parts[-1]})
           return out
       """)

    ex("s10.002", "s10", "Templates", "Render a config", 3,
       """
       Write `render(template, data)` replacing every `{{ name }}` placeholder
       (spaces inside the braces optional) with `str(data[name])`. A
       placeholder whose name is missing from `data` raises `KeyError` naming
       it; nothing is silently left blank.
       """,
       """
       def render(template, data):
           pass
       """,
       [("one value", "assert render('hostname {{ host }}', {'host': 'r1'}) == 'hostname r1'"),
        ("no spaces", "assert render('vlan {{id}}', {'id': 10}) == 'vlan 10'"),
        ("several", "assert render('{{a}}-{{ b }}-{{a}}', {'a': 1, 'b': 2}) == '1-2-1'"),
        ("missing value", "try:\n    render('ip {{ ip }}', {})\nexcept KeyError as e:\n    assert 'ip' in str(e)\nelse:\n    raise AssertionError('expected KeyError, but it rendered the template')")],
       hints=["A regular expression finds the placeholders: `\\{\\{\\s*(\\w+)\\s*\\}\\}`.",
              "`re.sub` accepts a function; look the name up in `data` inside it, and a missing key raises `KeyError` by itself."],
       solution="""
       import re


       def render(template, data):
           return re.sub(r"\\{\\{\\s*(\\w+)\\s*\\}\\}",
                         lambda m: str(data[m.group(1)]), template)
       """)

    ex("s10.003", "s10", "Change control", "Diff a configuration", 4,
       """
       Write `config_diff(running, intended)` for two configurations given as
       text. Ignore blank lines and comment lines starting with `!`. Return a
       list of strings:

       - `"- line"` for each line in running but not in intended, in running
         order
       - then `"+ line"` for each line in intended but not in running, in
         intended order

       Compare lines after stripping surrounding whitespace.
       """,
       """
       def config_diff(running, intended):
           pass
       """,
       [("no change", "assert config_diff('a\\nb\\n', 'a\\nb\\n') == []"),
        ("add and remove", "assert config_diff('a\\nb\\n', 'a\\nc\\n') == ['- b', '+ c']"),
        ("ignores comments and blanks", "assert config_diff('! note\\na\\n\\n', 'a\\n') == []"),
        ("strips whitespace", "assert config_diff(' a \\n', 'a') == []"),
        ("keeps order", "assert config_diff('x\\ny\\n', 'z\\nw\\n') == ['- x', '- y', '+ z', '+ w']")],
       hints=["Clean both texts into lists of stripped lines, dropping blanks and `!` comments.",
              "Build a set of each for membership, but loop over the lists to keep the order."],
       solution="""
       def _lines(text):
           out = []
           for line in text.splitlines():
               line = line.strip()
               if line and not line.startswith("!"):
                   out.append(line)
           return out


       def config_diff(running, intended):
           run, want = _lines(running), _lines(intended)
           run_set, want_set = set(run), set(want)
           removed = ["- " + line for line in run if line not in want_set]
           added = ["+ " + line for line in want if line not in run_set]
           return removed + added
       """)

    # -- s11 embedded --------------------------------------------------------
    ex("s11.001", "s11", "GPIO", "Debounce a button", 2,
       """
       A mechanical button bounces between 0 and 1 for a few milliseconds.
       Write `debounce(samples, stable)`: `samples` is one reading per
       millisecond. The output state starts at `samples[0]` and changes only
       after `stable` identical readings in a row that differ from it. Return
       the list of output states, one per sample.
       """,
       """
       def debounce(samples, stable):
           pass
       """,
       [("clean press", "assert debounce([0, 1, 1, 1], 3) == [0, 0, 0, 1]"),
        ("bounce is ignored", "assert debounce([0, 1, 0, 1, 0, 0], 2) == [0, 0, 0, 0, 0, 0]"),
        ("press and release", "assert debounce([0, 1, 1, 0, 0], 2) == [0, 0, 1, 1, 0]"),
        ("stable of one", "assert debounce([0, 1, 0], 1) == [0, 1, 0]")],
       hints=["Keep the current output state and a count of consecutive readings that differ from it.",
              "When a reading equals the state, reset the count; when the count reaches `stable`, switch state and reset."],
       solution="""
       def debounce(samples, stable):
           state = samples[0]
           run = 0
           out = []
           for sample in samples:
               if sample == state:
                   run = 0
               else:
                   run += 1
                   if run >= stable:
                       state = sample
                       run = 0
               out.append(state)
           return out
       """)

    ex("s11.002", "s11", "Sensor data", "Decode a temperature reading", 3,
       """
       A temperature sensor returns two bytes over I2C. The temperature is
       the top 12 bits of `(msb << 8) | lsb`, as a two's complement number,
       in steps of 0.0625 degrees C.

       Write `temperature(msb, lsb)` returning degrees C as a float.
       `temperature(0x19, 0x00)` is 25.0 and `temperature(0xFF, 0xF0)` is
       -0.0625.
       """,
       """
       def temperature(msb, lsb):
           pass
       """,
       [("25 degrees", "assert temperature(0x19, 0x00) == 25.0"),
        ("zero", "assert temperature(0x00, 0x00) == 0.0"),
        ("just below zero", "assert temperature(0xFF, 0xF0) == -0.0625"),
        ("minus one", "assert temperature(0xFF, 0x00) == -1.0"),
        ("fraction", "assert temperature(0x19, 0x10) == 25.0625")],
       hints=["Combine the bytes, then shift right by 4 to keep the top 12 bits.",
              "If bit 11 is set (`raw & 0x800`), subtract `0x1000` to get the negative value; then multiply by 0.0625."],
       solution="""
       def temperature(msb, lsb):
           raw = ((msb << 8) | lsb) >> 4
           if raw & 0x800:
               raw -= 0x1000
           return raw * 0.0625
       """)

    ex("s11.003", "s11", "Connectivity", "Buffer readings while offline", 4,
       """
       Write a class `Outbox(capacity)`:

       - `add(reading)` stores a reading; when full, the oldest is dropped and
         `dropped` goes up by one
       - `flush(send)` calls `send(reading)` for each stored reading, oldest
         first, removing it when `send` returns True and stopping at the first
         False; it returns the number sent
       - `len(outbox)` is the number still stored
       """,
       """
       class Outbox:
           def __init__(self, capacity):
               pass
       """,
       [("sends in order", "o = Outbox(3)\nfor r in [1, 2]:\n    o.add(r)\nsent = []\ndef send(r):\n    sent.append(r)\n    return True\nassert o.flush(send) == 2\nassert sent == [1, 2]\nassert len(o) == 0"),
        ("drops the oldest", "o = Outbox(2)\nfor r in [1, 2, 3]:\n    o.add(r)\nsent = []\ndef send(r):\n    sent.append(r)\n    return True\no.flush(send)\nassert sent == [2, 3]\nassert o.dropped == 1"),
        ("stops at a failure", "o = Outbox(5)\nfor r in [1, 2, 3]:\n    o.add(r)\nassert o.flush(lambda r: r < 2) == 1\nassert len(o) == 2"),
        ("keeps unsent for later", "o = Outbox(5)\no.add('a')\no.flush(lambda r: False)\nassert o.flush(lambda r: True) == 1")],
       hints=["`collections.deque` with `maxlen` drops from the far end when full, but you must count drops yourself.",
              "Before appending, if `len(self.items) == capacity`, increment `dropped`. In `flush`, send `items[0]` and `popleft()` only on success."],
       solution="""
       from collections import deque


       class Outbox:
           def __init__(self, capacity):
               self.items = deque(maxlen=capacity)
               self.capacity = capacity
               self.dropped = 0

           def add(self, reading):
               if len(self.items) == self.capacity:
                   self.dropped += 1
               self.items.append(reading)

           def flush(self, send):
               sent = 0
               while self.items:
                   if not send(self.items[0]):
                       break
                   self.items.popleft()
                   sent += 1
               return sent

           def __len__(self):
               return len(self.items)
       """)

    # -- s12 security engineering --------------------------------------------
    ex("s12.001", "s12", "Secrets scanning", "Find leaked secrets", 2,
       """
       Write `find_secrets(text)` returning a list of `(line_number, kind)`
       tuples, line numbers starting at 1:

       - `"aws-key"` for `AKIA` followed by 16 upper-case letters or digits
       - `"private-key"` for a line containing `-----BEGIN` and
         `PRIVATE KEY-----`
       """,
       """
       def find_secrets(text):
           pass
       """,
       [("aws key", "assert find_secrets('x = \"AKIAABCDEFGHIJKLMNOP\"') == [(1, 'aws-key')]"),
        ("private key", "assert find_secrets('a\\n-----BEGIN RSA PRIVATE KEY-----\\n') == [(2, 'private-key')]"),
        ("too short", "assert find_secrets('AKIA123') == []"),
        ("clean text", "assert find_secrets('nothing here\\n') == []"),
        ("both", "t = 'AKIAZZZZZZZZZZZZZZZZ\\n-----BEGIN OPENSSH PRIVATE KEY-----'\nassert find_secrets(t) == [(1, 'aws-key'), (2, 'private-key')]")],
       hints=["Loop over `enumerate(text.splitlines(), start=1)` and test each line.",
              "`re.search(r\"AKIA[0-9A-Z]{16}\", line)` finds the key; the private key check is two substring tests."],
       solution="""
       import re


       def find_secrets(text):
           found = []
           for number, line in enumerate(text.splitlines(), start=1):
               if re.search(r"AKIA[0-9A-Z]{16}", line):
                   found.append((number, "aws-key"))
               if "-----BEGIN" in line and "PRIVATE KEY-----" in line:
                   found.append((number, "private-key"))
           return found
       """)

    ex("s12.002", "s12", "Message authentication", "Sign and verify messages", 3,
       """
       Write:

       - `sign(secret, message)`: the HMAC-SHA256 of `message` with key
         `secret` (both `bytes`), as a hex string
       - `verify(secret, message, signature)`: True when `signature` matches,
         compared in constant time
       """,
       """
       def sign(secret, message):
           pass


       def verify(secret, message, signature):
           pass
       """,
       [("known value", "assert sign(b'key', b'msg') == '2d93cbc1be167bcb1637a4a23cbff01a7878f0c50ee833954ea5221bb1b8c628'"),
        ("verifies", "assert verify(b'k', b'hello', sign(b'k', b'hello'))"),
        ("wrong message", "assert not verify(b'k', b'hello!', sign(b'k', b'hello'))"),
        ("wrong key", "assert not verify(b'x', b'hello', sign(b'k', b'hello'))"),
        ("constant time", "import ast, inspect\ntree = ast.parse(inspect.getsource(verify))\nnames = [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)]\nassert 'compare_digest' in names")],
       hints=["`hmac.new(secret, message, hashlib.sha256).hexdigest()` computes the signature.",
              "Compare with `hmac.compare_digest(a, b)`, never `==`, so timing does not leak how many characters matched."],
       solution="""
       import hashlib
       import hmac


       def sign(secret, message):
           return hmac.new(secret, message, hashlib.sha256).hexdigest()


       def verify(secret, message, signature):
           return hmac.compare_digest(sign(secret, message), signature)
       """)

    ex("s12.003", "s12", "Detection", "Detect brute-force logins", 4,
       """
       `events` is a list of `(timestamp, ip, ok)` tuples in time order.
       Write `detect(events, limit, window)` returning the set of IPs with
       more than `limit` failed logins within any period of `window` seconds
       (inclusive of both ends).
       """,
       """
       def detect(events, limit, window):
           pass
       """,
       [("burst", "ev = [(t, '1.1.1.1', False) for t in range(4)]\nassert detect(ev, 3, 10) == {'1.1.1.1'}"),
        ("spread out", "ev = [(t * 100, '1.1.1.1', False) for t in range(10)]\nassert detect(ev, 3, 10) == set()"),
        ("successes do not count", "ev = [(t, '2.2.2.2', True) for t in range(10)]\nassert detect(ev, 3, 10) == set()"),
        ("per ip", "ev = [(0, 'a', False), (1, 'b', False), (2, 'a', False), (3, 'a', False)]\nassert detect(ev, 2, 5) == {'a'}"),
        ("window edge is inclusive", "ev = [(0, 'a', False), (10, 'a', False), (20, 'a', False)]\nassert detect(ev, 1, 10) == {'a'}")],
       hints=["Keep, for each IP, a deque of its recent failure times.",
              "On each failure, append the time and pop from the left while the oldest is more than `window` seconds older; flag the IP when the deque is longer than `limit`."],
       solution="""
       from collections import defaultdict, deque


       def detect(events, limit, window):
           recent = defaultdict(deque)
           flagged = set()
           for timestamp, ip, ok in events:
               if ok:
                   continue
               times = recent[ip]
               times.append(timestamp)
               while timestamp - times[0] > window:
                   times.popleft()
               if len(times) > limit:
                   flagged.add(ip)
           return flagged
       """)

    # -- s13 bots ------------------------------------------------------------
    ex("s13.001", "s13", "Commands", "Parse a chat command", 2,
       """
       Write `parse_command(text, prefix="!")`. If `text` starts with the
       prefix, return `(name, args)`: the command name in lower case and the
       list of arguments, where quoted arguments may contain spaces. Otherwise
       return `None`. A prefix with no name after it is also `None`.
       """,
       """
       def parse_command(text, prefix="!"):
           pass
       """,
       [("simple", "assert parse_command('!ping') == ('ping', [])"),
        ("arguments", "assert parse_command('!Remind me 5') == ('remind', ['me', '5'])"),
        ("quotes", "assert parse_command('!say \"hello there\" now') == ('say', ['hello there', 'now'])"),
        ("not a command", "assert parse_command('hello') is None"),
        ("bare prefix", "assert parse_command('!') is None")],
       hints=["Check `text.startswith(prefix)` and strip the prefix.",
              "`shlex.split` handles the quoted arguments; the first item is the name."],
       solution="""
       import shlex


       def parse_command(text, prefix="!"):
           if not text.startswith(prefix):
               return None
           parts = shlex.split(text[len(prefix):])
           if not parts:
               return None
           return parts[0].lower(), parts[1:]
       """)

    ex("s13.002", "s13", "Webhooks", "Verify a webhook", 3,
       """
       A platform sends a header `t=<timestamp>,v1=<signature>` where the
       signature is the hex HMAC-SHA256 of `"<timestamp>.<body>"` with your
       secret. Write `verify_webhook(secret, body, header, now, max_age=300)`
       returning True only if the signature matches (constant-time compare)
       and the timestamp is no more than `max_age` seconds old. `secret` is
       bytes, `body` and `header` are strings, `now` is a number.
       """,
       """
       def verify_webhook(secret, body, header, now, max_age=300):
           pass
       """,
       [("valid", "import hmac, hashlib\nsig = hmac.new(b's', b'100.{}', hashlib.sha256).hexdigest()\nassert verify_webhook(b's', '{}', 't=100,v1=' + sig, 150)"),
        ("tampered body", "import hmac, hashlib\nsig = hmac.new(b's', b'100.{}', hashlib.sha256).hexdigest()\nassert not verify_webhook(b's', '{\"x\":1}', 't=100,v1=' + sig, 150)"),
        ("too old", "import hmac, hashlib\nsig = hmac.new(b's', b'100.{}', hashlib.sha256).hexdigest()\nassert not verify_webhook(b's', '{}', 't=100,v1=' + sig, 1000)"),
        ("malformed header", "assert not verify_webhook(b's', '{}', 'garbage', 100)"),
        ("wrong secret", "import hmac, hashlib\nsig = hmac.new(b's', b'100.{}', hashlib.sha256).hexdigest()\nassert not verify_webhook(b'other', '{}', 't=100,v1=' + sig, 150)")],
       hints=["Split the header on commas and then on `=` to get `t` and `v1`; return False if either is missing.",
              "Recompute the HMAC over `f\"{t}.{body}\".encode()` and compare with `hmac.compare_digest`; also check `now - int(t) <= max_age`."],
       solution="""
       import hashlib
       import hmac


       def verify_webhook(secret, body, header, now, max_age=300):
           fields = {}
           for part in header.split(","):
               key, _, value = part.partition("=")
               fields[key.strip()] = value.strip()
           if "t" not in fields or "v1" not in fields:
               return False
           try:
               stamp = int(fields["t"])
           except ValueError:
               return False
           if now - stamp > max_age:
               return False
           expected = hmac.new(secret, ("%s.%s" % (fields["t"], body)).encode(),
                               hashlib.sha256).hexdigest()
           return hmac.compare_digest(expected, fields["v1"])
       """)

    ex("s13.003", "s13", "Rate limits", "Respect rate limits", 4,
       """
       Write `send_all(messages, send, sleep)`. For each message, call
       `send(message)`, which returns `(status, retry_after)`:

       - status 200: sent; go to the next message
       - status 429: call `sleep(retry_after)` and send the same message again
       - after 3 attempts on one message without a 200, raise `RuntimeError`

       Any other status raises `RuntimeError` at once. Return the number of
       messages sent.
       """,
       """
       def send_all(messages, send, sleep):
           pass
       """,
       [("all sent", "assert send_all(['a', 'b'], lambda m: (200, 0), lambda s: None) == 2"),
        ("waits and retries", "calls = []\nstate = {'n': 0}\ndef send(m):\n    state['n'] += 1\n    return (429, 2) if state['n'] == 1 else (200, 0)\nassert send_all(['a'], send, calls.append) == 1\nassert calls == [2]"),
        ("gives up after three attempts", "try:\n    send_all(['a'], lambda m: (429, 1), lambda s: None)\nexcept RuntimeError:\n    pass\nelse:\n    raise AssertionError('expected RuntimeError, but it returned normally')"),
        ("other errors stop at once", "tries = []\ntry:\n    send_all(['a'], lambda m: tries.append(1) or (500, 0), lambda s: None)\nexcept RuntimeError:\n    pass\nassert tries == [1]"),
        ("no messages", "assert send_all([], lambda m: (200, 0), lambda s: None) == 0")],
       hints=["Use an inner loop over attempts for each message.",
              "`for attempt in range(3)`: on 200 break; on 429 sleep; otherwise raise. An `else` on the `for` runs when it never broke, which is where to raise."],
       solution="""
       def send_all(messages, send, sleep):
           sent = 0
           for message in messages:
               for _attempt in range(3):
                   status, retry_after = send(message)
                   if status == 200:
                       sent += 1
                       break
                   if status != 429:
                       raise RuntimeError("send failed with %s" % status)
                   sleep(retry_after)
               else:
                   raise RuntimeError("still rate-limited after 3 attempts")
           return sent
       """)

    # -- s14 blockchain ------------------------------------------------------
    ex("s14.001", "s14", "Units", "Wei, gwei and ether", 2,
       """
       Write `to_wei(amount, unit)` where `amount` is a string such as
       `"1.5"` and `unit` is `"ether"` (10**18 wei), `"gwei"` (10**9 wei) or
       `"wei"`. Return an exact `int`. Use `decimal.Decimal`, never float.
       Raise `ValueError` if the result is not a whole number of wei, or the
       unit is unknown.
       """,
       """
       def to_wei(amount, unit):
           pass
       """,
       [("one ether", "assert to_wei('1', 'ether') == 10 ** 18"),
        ("fraction of ether", "assert to_wei('1.5', 'ether') == 1_500_000_000_000_000_000"),
        ("gwei", "assert to_wei('30', 'gwei') == 30_000_000_000"),
        ("exact", "assert to_wei('0.1', 'ether') == 100_000_000_000_000_000"),
        ("fractional wei", raises("to_wei('0.5', 'wei')")),
        ("unknown unit", raises("to_wei('1', 'bitcoin')"))],
       hints=["Map each unit to its multiplier, then multiply `Decimal(amount)` by it.",
              "Check `value == value.to_integral_value()` before returning `int(value)`."],
       solution="""
       from decimal import Decimal

       UNITS = {"ether": 10 ** 18, "gwei": 10 ** 9, "wei": 1}


       def to_wei(amount, unit):
           if unit not in UNITS:
               raise ValueError("unknown unit %s" % unit)
           value = Decimal(amount) * UNITS[unit]
           if value != value.to_integral_value():
               raise ValueError("not a whole number of wei")
           return int(value)
       """)

    ex("s14.002", "s14", "Gas", "Transaction fee", 3,
       """
       Under EIP-1559 a transaction pays, per unit of gas, the smaller of
       `max_fee` and `base_fee + priority_fee`. Write
       `fee_wei(gas_used, base_fee, priority_fee, max_fee)` returning the
       total fee in wei. Raise `ValueError` if `max_fee` is below `base_fee`,
       since such a transaction cannot be included.
       """,
       """
       def fee_wei(gas_used, base_fee, priority_fee, max_fee):
           pass
       """,
       [("tip fits", "assert fee_wei(21000, 30, 2, 50) == 21000 * 32"),
        ("capped by max fee", "assert fee_wei(21000, 30, 25, 40) == 21000 * 40"),
        ("no tip", "assert fee_wei(100, 10, 0, 10) == 1000"),
        ("cannot be included", raises("fee_wei(21000, 30, 2, 20)"))],
       hints=["The price per gas is `min(max_fee, base_fee + priority_fee)`.",
              "Check `max_fee < base_fee` first and raise; otherwise multiply the price by `gas_used`."],
       solution="""
       def fee_wei(gas_used, base_fee, priority_fee, max_fee):
           if max_fee < base_fee:
               raise ValueError("max fee is below the base fee")
           return gas_used * min(max_fee, base_fee + priority_fee)
       """)

    ex("s14.003", "s14", "Indexing", "Handle a chain reorganization", 4,
       """
       Write a class `Indexer` that stores blocks and their events.
       `apply(block)` takes a dict with `number`, `hash`, `parent` and
       `events` (a list):

       - If `number` is at or below the current head, a reorganization has
         happened: drop the stored blocks from `number` upward first.
       - The block's `parent` must equal the stored hash of block
         `number - 1` (block 0 has no parent check); otherwise raise
         `ValueError`.
       - `head` is the highest stored block number, or `-1` when empty.
       - `events()` returns every stored event in block order.
       """,
       """
       class Indexer:
           pass
       """,
       [("appends", "ix = Indexer()\nix.apply({'number': 0, 'hash': 'a', 'parent': None, 'events': [1]})\nix.apply({'number': 1, 'hash': 'b', 'parent': 'a', 'events': [2]})\nassert ix.head == 1\nassert ix.events() == [1, 2]"),
        ("rejects a gap", "ix = Indexer()\nix.apply({'number': 0, 'hash': 'a', 'parent': None, 'events': []})\ntry:\n    ix.apply({'number': 1, 'hash': 'b', 'parent': 'zzz', 'events': []})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError, but it accepted the wrong parent')"),
        ("reorg replaces blocks", "ix = Indexer()\nix.apply({'number': 0, 'hash': 'a', 'parent': None, 'events': ['x']})\nix.apply({'number': 1, 'hash': 'b', 'parent': 'a', 'events': ['old']})\nix.apply({'number': 2, 'hash': 'c', 'parent': 'b', 'events': ['old2']})\nix.apply({'number': 1, 'hash': 'b2', 'parent': 'a', 'events': ['new']})\nassert ix.head == 1\nassert ix.events() == ['x', 'new']"),
        ("empty head", "assert Indexer().head == -1\nassert Indexer().events() == []")],
       hints=["Store blocks in a dict keyed by number, and compute `head` from its keys.",
              "In `apply`, delete every stored number `>= block[\"number\"]` first, then check the parent against `blocks[number - 1][\"hash\"]`."],
       solution="""
       class Indexer:
           def __init__(self):
               self.blocks = {}

           @property
           def head(self):
               return max(self.blocks) if self.blocks else -1

           def apply(self, block):
               number = block["number"]
               for n in [n for n in self.blocks if n >= number]:
                   del self.blocks[n]
               if number > 0:
                   previous = self.blocks.get(number - 1)
                   if previous is None or previous["hash"] != block["parent"]:
                       raise ValueError("parent does not match block %d" % (number - 1))
               self.blocks[number] = block

           def events(self):
               out = []
               for n in sorted(self.blocks):
                   out.extend(self.blocks[n]["events"])
               return out
       """)

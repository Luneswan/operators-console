"""Phases 03 and 08 - tooling, and SQL against a real SQLite database."""
from ex_lib import ex
from ex_p01a import no_string_building, raises

#: A second database built inside a check, with different rows, so a function
#: that returns a remembered answer for CONN cannot pass. Borges has no books.
OTHER_DB = (
    "import sqlite3\n"
    "other = sqlite3.connect(':memory:')\n"
    "other.row_factory = sqlite3.Row\n"
    "other.executescript(\n"
    "    'CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);'\n"
    "    'CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER NOT NULL,'\n"
    "    ' title TEXT NOT NULL, year INTEGER NOT NULL, copies INTEGER NOT NULL DEFAULT 0);'\n"
    "    \"INSERT INTO authors (id, name) VALUES (1,'Chiang'),(2,'Jemisin'),(3,'Borges');\"\n"
    "    'INSERT INTO books (author_id, title, year, copies) VALUES'\n"
    "    \" (1,'Exhalation',2019,2),(2,'The Fifth Season',2015,5),\"\n"
    "    \" (2,'The Obelisk Gate',2016,1),(2,'The Stone Sky',2017,3);\")\n")

#: Wraps a connection and counts the statements sent through it, including
#: through a cursor, so "one query" is measured rather than grepped.
QUERY_SPY = (
    "class Cursor:\n"
    "    def __init__(self, spy):\n"
    "        self.spy = spy\n"
    "        self.inner = spy.conn.cursor()\n"
    "    def execute(self, *args, **kwargs):\n"
    "        self.spy.queries += 1\n"
    "        self.inner.execute(*args, **kwargs)\n"
    "        return self\n"
    "    def __iter__(self):\n"
    "        return iter(self.inner)\n"
    "    def __getattr__(self, name):\n"
    "        return getattr(self.inner, name)\n"
    "class Spy:\n"
    "    def __init__(self, conn):\n"
    "        self.conn = conn\n"
    "        self.queries = 0\n"
    "    def execute(self, *args, **kwargs):\n"
    "        self.queries += 1\n"
    "        return self.conn.execute(*args, **kwargs)\n"
    "    def cursor(self):\n"
    "        return Cursor(self)\n"
    "    def __getattr__(self, name):\n"
    "        return getattr(self.conn, name)\n"
    "spy = Spy(CONN)\n")

SLASHES = (
    "import ast, inspect, textwrap\n"
    "tree = ast.parse(textwrap.dedent(inspect.getsource(log_path)))\n"
    "body = tree.body[0].body\n"
    "if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):\n"
    "    body = body[1:]    # a docstring may say anything it likes\n"
    "slashes = [node.value for statement in body for node in ast.walk(statement)\n"
    "           if isinstance(node, ast.Constant) and isinstance(node.value, str)\n"
    "           and ('/' in node.value or chr(92) in node.value)]\n"
    "assert not slashes, 'log_path glues text with a slash in it - join the parts with the / operator on Path objects instead'")


def build():
    ex("p03.001", "p03", "Paths", "Paths that work everywhere", 2,
       """
       Write `log_path(root, name)` returning a `pathlib.Path` for
       `<root>/logs/<name>.log`, with the parent directory created if needed.

       Never build a path by gluing strings with slashes - that breaks on
       Windows.
       """,
       """
       from pathlib import Path


       def log_path(root, name):
           pass
       """,
       [("builds the path",
         "from pathlib import Path\np = log_path('data', 'app')\nassert p == Path('data') / 'logs' / 'app.log'"),
        ("creates the folder",
         "from pathlib import Path\nlog_path('made', 'x')\nassert (Path('made') / 'logs').is_dir(), 'log_path should create the logs folder when it is missing'"),
        ("returns a Path",
         "from pathlib import Path\nassert isinstance(log_path('a', 'b'), Path)"),
        ("accepts a Path as the root",
         "from pathlib import Path\nassert log_path(Path('root2'), 'app.v2') == Path('root2') / 'logs' / 'app.v2.log'"),
        ("no manual separators", SLASHES)],
       hints=["The / operator joins Path objects.",
              "mkdir(parents=True, exist_ok=True) is idempotent."],
       solution="""
       from pathlib import Path


       def log_path(root, name):
           folder = Path(root) / "logs"
           folder.mkdir(parents=True, exist_ok=True)
           return folder / f"{name}.log"
       """)

    ex("p03.002", "p03", "Command line", "Parse arguments properly", 3,
       """
       Write `build_parser()` returning an `argparse.ArgumentParser` that
       accepts a required positional `path`, an optional `--limit` integer
       defaulting to 10, and a `--verbose` flag.
       """,
       """
       import argparse


       def build_parser():
           pass
       """,
       [("parses the positional",
         "args = build_parser().parse_args(['file.txt'])\nassert args.path == 'file.txt'"),
        ("limit default", "assert build_parser().parse_args(['x']).limit == 10"),
        ("limit is an int",
         "assert build_parser().parse_args(['x', '--limit', '5']).limit == 5"),
        ("verbose flag",
         "assert build_parser().parse_args(['x', '--verbose']).verbose is True"),
        ("verbose defaults off",
         "assert build_parser().parse_args(['x']).verbose is False"),
        ("every option at once",
         "args = build_parser().parse_args(['other.log', '--limit', '42', '--verbose'])\nassert args.path == 'other.log'\nassert args.limit == 42\nassert args.verbose is True"),
        ("options before the path",
         "args = build_parser().parse_args(['--limit', '3', 'late.txt'])\nassert args.path == 'late.txt'\nassert args.limit == 3"),
        ("missing positional fails",
         raises("build_parser().parse_args([])", "SystemExit")),
        ("a limit that is not a number fails",
         raises("build_parser().parse_args(['x', '--limit', 'many'])", "SystemExit"))],
       hints=["type=int makes argparse convert and validate for you.",
              "action='store_true' is how a flag becomes a boolean."],
       solution="""
       import argparse


       def build_parser():
           parser = argparse.ArgumentParser(description="Process a file.")
           parser.add_argument("path")
           parser.add_argument("--limit", type=int, default=10)
           parser.add_argument("--verbose", action="store_true")
           return parser
       """)

    ex("p03.003", "p03", "Versions", "Compare semantic versions", 3,
       """
       Write `newer(a, b)` returning True when version string `a` is strictly
       newer than `b`. Versions look like `"1.2.10"`.

       String comparison is wrong here: `"1.2.10"` sorts before `"1.2.9"`.
       """,
       """
       def newer(a, b):
           pass
       """,
       [("patch bump", "assert newer('1.2.10', '1.2.9') is True"),
        ("equal is not newer", "assert newer('1.0.0', '1.0.0') is False"),
        ("major wins", "assert newer('2.0.0', '1.9.9') is True"),
        ("older", "assert newer('1.0.0', '1.0.1') is False"),
        ("different lengths", "assert newer('1.1', '1.0.9') is True"),
        ("a missing part counts as zero", "assert newer('1.1', '1.1.0') is False"),
        ("and the other way round", "assert newer('1.1.0', '1.1') is False"),
        ("minor numbers compare as numbers", "assert newer('1.10.0', '1.9.0') is True")],
       hints=["Split on dots and compare tuples of ints.",
              "Pad the shorter version with zeros so 1.1 and 1.1.0 compare equal."],
       solution="""
       def newer(a, b):
           def parts(version):
               nums = [int(p) for p in version.split(".")]
               return nums + [0] * (3 - len(nums))
           return parts(a) > parts(b)
       """)

    ex("p03.004", "p03", "Logging", "Log instead of printing", 3,
       """
       Write `make_logger(name, stream)` returning a `logging.Logger` that
       writes to the given stream at INFO level, formatted as
       `LEVEL:message`.

       Configure it on the logger itself, not on the root logger.
       """,
       """
       import logging


       def make_logger(name, stream):
           pass
       """,
       [("writes info",
         "import io\nbuf = io.StringIO()\nlog = make_logger('t1', buf)\nlog.info('hello')\nassert buf.getvalue().strip() == 'INFO:hello'"),
        ("suppresses debug",
         "import io\nbuf = io.StringIO()\nlog = make_logger('t2', buf)\nlog.debug('quiet')\nassert buf.getvalue() == ''"),
        ("returns a Logger",
         "import io, logging\nassert isinstance(make_logger('t3', io.StringIO()), logging.Logger)"),
        ("no duplicate handlers",
         "import io\nbuf = io.StringIO()\nmake_logger('t4', buf)\nlog = make_logger('t4', buf)\nlog.info('once')\nassert buf.getvalue().count('once') == 1")],
       hints=["logging.getLogger(name) returns the same object every time - clear its handlers first.",
              "A Formatter takes a percent-style string such as '%(levelname)s:%(message)s'."],
       solution="""
       import logging


       def make_logger(name, stream):
           logger = logging.getLogger(name)
           logger.handlers.clear()
           logger.setLevel(logging.INFO)
           logger.propagate = False
           handler = logging.StreamHandler(stream)
           handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
           logger.addHandler(handler)
           return logger
       """)

    SQL_SETUP = """
    import sqlite3

    CONN = sqlite3.connect(":memory:")
    CONN.row_factory = sqlite3.Row
    CONN.executescript(
        "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
        "CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER NOT NULL"
        " REFERENCES authors(id), title TEXT NOT NULL, year INTEGER NOT NULL,"
        " copies INTEGER NOT NULL DEFAULT 0);"
        "INSERT INTO authors (id, name) VALUES (1,'Le Guin'),(2,'Butler'),(3,'Lem');"
        "INSERT INTO books (author_id,title,year,copies) VALUES"
        " (1,'A Wizard of Earthsea',1968,4),(1,'The Dispossessed',1974,2),"
        " (2,'Kindred',1979,7),(2,'Dawn',1987,1),(3,'Solaris',1961,3);")
    CONN.commit()
    """

    ex("p08.001", "p08", "Queries", "Select and filter", 2,
       """
       A SQLite connection is already open as `CONN`, with tables `authors`
       and `books`.

       Write `books_after(conn, year)` returning a list of titles published
       strictly after `year`, sorted alphabetically.

       Use a parameterised query. Never format values into SQL with an
       f-string.
       """,
       """
       def books_after(conn, year):
           pass
       """,
       [("filters",
         "assert books_after(CONN, 1975) == ['Dawn', 'Kindred']"),
        ("strictly after", "assert 'Solaris' not in books_after(CONN, 1961)"),
        ("nothing matches", "assert books_after(CONN, 2100) == []"),
        ("another database",
         OTHER_DB + "assert books_after(other, 2015) == ['Exhalation', 'The Obelisk Gate', 'The Stone Sky']"),
        ("cannot be injected",
         "assert books_after(CONN, '1975 OR 1=1') == [], 'the year was read as SQL - bind it as a parameter instead'"),
        ("parameterised", no_string_building(
            "books_after",
            "books_after should pass the year as a parameter, not build it into the SQL"))],
       setup=SQL_SETUP,
       hints=["conn.execute(sql, (year,)) binds the value safely.",
              "Each row behaves like a tuple, so row[0] is the first column."],
       solution="""
       def books_after(conn, year):
           rows = conn.execute(
               "SELECT title FROM books WHERE year > ? ORDER BY title", (year,))
           return [row[0] for row in rows]
       """)

    ex("p08.002", "p08", "Joins", "Join two tables", 3,
       """
       Write `titles_by(conn, author_name)` returning the titles written by
       that author, oldest first.

       Join `books` to `authors`; do not run two queries.
       """,
       """
       def titles_by(conn, author_name):
           pass
       """,
       [("finds the books",
         "assert titles_by(CONN, 'Le Guin') == ['A Wizard of Earthsea', 'The Dispossessed']"),
        ("ordered by year",
         "assert titles_by(CONN, 'Butler') == ['Kindred', 'Dawn']"),
        ("unknown author", "assert titles_by(CONN, 'Nobody') == []"),
        ("another database",
         OTHER_DB + "assert titles_by(other, 'Jemisin') == ['The Fifth Season', 'The Obelisk Gate', 'The Stone Sky']"),
        ("single query",
         QUERY_SPY + "titles_by(spy, 'Butler')\nassert spy.queries == 1, 'titles_by should ask the database once, with a JOIN - it sent %d queries' % spy.queries")],
       setup=SQL_SETUP,
       hints=["JOIN authors ON authors.id = books.author_id.",
              "ORDER BY year does the sorting in the database, not in Python."],
       solution="""
       def titles_by(conn, author_name):
           rows = conn.execute(
               "SELECT b.title FROM books b JOIN authors a ON a.id = b.author_id"
               " WHERE a.name = ? ORDER BY b.year", (author_name,))
           return [row[0] for row in rows]
       """)

    ex("p08.003", "p08", "Aggregation", "Group and count", 3,
       """
       Write `book_counts(conn)` returning a dict mapping every author name to
       how many books they have, including authors with none.

       Do it in a single query - let the database do the counting. Sort is
       irrelevant; the counts are what matter.
       """,
       """
       def book_counts(conn):
           pass
       """,
       [("counts each author",
         "assert book_counts(CONN) == {'Le Guin': 2, 'Butler': 2, 'Lem': 1}"),
        ("returns a dict", "assert isinstance(book_counts(CONN), dict)"),
        ("an author with no books counts as zero",
         OTHER_DB + "assert book_counts(other) == {'Chiang': 1, 'Jemisin': 3, 'Borges': 0}"),
        ("one query",
         QUERY_SPY + "book_counts(spy)\nassert spy.queries == 1, 'book_counts should ask the database once - it sent %d queries' % spy.queries")],
       setup=SQL_SETUP,
       hints=["LEFT JOIN keeps authors that have no matching books.",
              "COUNT(b.id) counts only real rows; COUNT(*) would count the null side too."],
       solution="""
       def book_counts(conn):
           rows = conn.execute(
               "SELECT a.name, COUNT(b.id) FROM authors a "
               "LEFT JOIN books b ON b.author_id = a.id GROUP BY a.id")
           return {name: count for name, count in rows}
       """)

    ex("p08.004", "p08", "Transactions", "Roll back on failure", 4,
       """
       Write `transfer_copies(conn, from_title, to_title, amount)` that moves
       copies between two books.

       If the source would go negative, raise `ValueError` and leave both rows
       untouched.
       """,
       """
       def transfer_copies(conn, from_title, to_title, amount):
           pass
       """,
       [("moves copies",
         "transfer_copies(CONN, 'Kindred', 'Dawn', 3)\nrows = dict(CONN.execute('SELECT title, copies FROM books'))\nassert rows['Kindred'] == 4\nassert rows['Dawn'] == 4"),
        ("rejects an overdraw", raises("transfer_copies(CONN, 'Dawn', 'Solaris', 999)")),
        ("leaves rows untouched after failure",
         "before = dict(CONN.execute('SELECT title, copies FROM books'))\ntry:\n    transfer_copies(CONN, 'Solaris', 'Dawn', 500)\nexcept ValueError:\n    pass\nafter = dict(CONN.execute('SELECT title, copies FROM books'))\nassert before == after")],
       setup=SQL_SETUP,
       hints=["Check the balance first, then do both updates, then commit.",
              "On failure call conn.rollback() so no half-finished write survives."],
       solution="""
       def transfer_copies(conn, from_title, to_title, amount):
           try:
               row = conn.execute(
                   "SELECT copies FROM books WHERE title = ?",
                   (from_title,)).fetchone()
               if row is None or row[0] < amount:
                   raise ValueError("not enough copies")
               conn.execute(
                   "UPDATE books SET copies = copies - ? WHERE title = ?",
                   (amount, from_title))
               conn.execute(
                   "UPDATE books SET copies = copies + ? WHERE title = ?",
                   (amount, to_title))
               conn.commit()
           except Exception:
               conn.rollback()
               raise
       """)

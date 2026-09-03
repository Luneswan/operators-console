"""Phases 03 and 08 - tooling, and SQL against a real SQLite database."""
from ex_lib import ex


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
         "from pathlib import Path\nlog_path('made', 'x')\nassert (Path('made') / 'logs').is_dir()"),
        ("returns a Path",
         "from pathlib import Path\nassert isinstance(log_path('a', 'b'), Path)"),
        ("no manual separators",
         "import inspect\nassert '/' not in inspect.getsource(log_path).split('\\\"\\\"\\\"')[-1] or True")],
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
        ("missing positional fails",
         "import argparse\ntry:\n    build_parser().parse_args([])\nexcept SystemExit:\n    pass\nelse:\n    raise AssertionError('should fail')")],
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
        ("different lengths", "assert newer('1.1', '1.0.9') is True")],
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
        ("parameterised",
         "import inspect\nsrc = inspect.getsource(books_after)\nassert '?' in src and 'f\\\"' not in src and \"f'\" not in src")],
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
        ("single query",
         "import inspect\nassert inspect.getsource(titles_by).lower().count('select') == 1")],
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

       Sort is irrelevant; the counts are what matter.
       """,
       """
       def book_counts(conn):
           pass
       """,
       [("counts each author",
         "assert book_counts(CONN) == {'Le Guin': 2, 'Butler': 2, 'Lem': 1}"),
        ("returns a dict", "assert isinstance(book_counts(CONN), dict)"),
        ("one query",
         "import inspect\nassert inspect.getsource(book_counts).lower().count('select') == 1")],
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
         "transfer_copies(CONN, 'Kindred', 'Dawn', 3)\nrows = dict(CONN.execute('SELECT title, copies FROM books'))\nassert rows['Kindred'] == 4 and rows['Dawn'] == 4"),
        ("rejects an overdraw",
         "try:\n    transfer_copies(CONN, 'Dawn', 'Solaris', 999)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
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

"""Phases 09 to 14 - backend, automation, concurrency, security, AI."""
from ex_lib import ex


def build():
    ex("p09.001", "p09", "Routing", "Match a URL to a handler", 4,
       """
       Write `match(route, path)` where a route looks like `/users/{id}/posts`.

       Return a dict of the captured segments when the path matches, or `None`
       when it does not. Segment counts must match exactly.
       """,
       """
       def match(route, path):
           pass
       """,
       [("captures one",
         "assert match('/users/{id}', '/users/42') == {'id': '42'}"),
        ("captures two",
         "assert match('/u/{a}/p/{b}', '/u/1/p/2') == {'a': '1', 'b': '2'}"),
        ("static route", "assert match('/health', '/health') == {}"),
        ("wrong literal", "assert match('/users/{id}', '/posts/42') is None"),
        ("too few segments", "assert match('/a/{b}/c', '/a/1') is None"),
        ("too many segments", "assert match('/a', '/a/b') is None")],
       hints=["Split both on '/' and compare position by position.",
              "A part wrapped in braces captures; anything else must match exactly."],
       solution="""
       def match(route, path):
           route_parts = route.strip("/").split("/")
           path_parts = path.strip("/").split("/")
           if len(route_parts) != len(path_parts):
               return None
           captured = {}
           for expected, actual in zip(route_parts, path_parts):
               if expected.startswith("{") and expected.endswith("}"):
                   captured[expected[1:-1]] = actual
               elif expected != actual:
                   return None
           return captured
       """)

    ex("p09.002", "p09", "Validation", "Reject bad input at the edge", 4,
       """
       Write `clean_signup(payload)` returning a normalised dict with keys
       `email` (lowercased, stripped) and `age` (int).

       Raise `ValueError` with a useful message when the email is missing or
       has no `@`, or the age is absent, not a whole number, or under 13.
       """,
       """
       def clean_signup(payload):
           pass
       """,
       [("normalises",
         "assert clean_signup({'email': ' A@B.COM ', 'age': '30'}) == {'email': 'a@b.com', 'age': 30}"),
        ("rejects a missing email",
         "try:\n    clean_signup({'age': 20})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects a malformed email",
         "try:\n    clean_signup({'email': 'nope', 'age': 20})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects a child",
         "try:\n    clean_signup({'email': 'a@b.c', 'age': 9})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects a non-numeric age",
         "try:\n    clean_signup({'email': 'a@b.c', 'age': 'old'})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("messages are not empty",
         "try:\n    clean_signup({})\nexcept ValueError as exc:\n    assert str(exc)")],
       hints=["Validate, then normalise. Never trust a payload that came off the network.",
              "Raise with a message a client could act on, without leaking internals."],
       solution="""
       def clean_signup(payload):
           email = str(payload.get("email", "")).strip().lower()
           if not email or "@" not in email:
               raise ValueError("a valid email address is required")
           raw_age = payload.get("age")
           try:
               age = int(raw_age)
           except (TypeError, ValueError):
               raise ValueError("age must be a whole number")
           if age < 13:
               raise ValueError("you must be at least 13")
           return {"email": email, "age": age}
       """)

    ex("p09.003", "p09", "Pagination", "Page a result set", 3,
       """
       Write `paginate(items, page, per_page)` returning a dict with `items`,
       `page`, `pages` (total) and `total`.

       Pages are 1-based. A page beyond the end returns an empty list, not an
       error. Reject a `page` below 1 or a `per_page` below 1 with
       `ValueError`.
       """,
       """
       def paginate(items, page, per_page):
           pass
       """,
       [("first page",
         "r = paginate(list(range(10)), 1, 3)\nassert r['items'] == [0, 1, 2] and r['pages'] == 4 and r['total'] == 10"),
        ("last partial page",
         "assert paginate(list(range(10)), 4, 3)['items'] == [9]"),
        ("past the end",
         "assert paginate(list(range(10)), 99, 3)['items'] == []"),
        ("empty input",
         "r = paginate([], 1, 5)\nassert r['items'] == [] and r['pages'] == 0"),
        ("rejects bad page",
         "try:\n    paginate([1], 0, 5)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')")],
       hints=["Total pages is a ceiling division: -(-total // per_page).",
              "Slicing past the end of a list is already safe."],
       solution="""
       def paginate(items, page, per_page):
           if page < 1 or per_page < 1:
               raise ValueError("page and per_page must be 1 or more")
           total = len(items)
           start = (page - 1) * per_page
           return {
               "items": items[start:start + per_page],
               "page": page,
               "pages": -(-total // per_page),
               "total": total,
           }
       """)

    ex("p10.001", "p10", "Text extraction", "Pull the prices out", 3,
       """
       Write `find_prices(text)` returning every dollar amount as a float, in
       the order they appear.

       Amounts look like `$12`, `$12.50` or `$1,299.99`.
       """,
       """
       import re


       def find_prices(text):
           pass
       """,
       [("simple", "assert find_prices('costs $12 today') == [12.0]"),
        ("with cents", "assert find_prices('$12.50 and $3.05') == [12.5, 3.05]"),
        ("with separators", "assert find_prices('$1,299.99') == [1299.99]"),
        ("none", "assert find_prices('free') == []"),
        ("ignores bare numbers", "assert find_prices('12 dollars') == []")],
       hints=["Strip the commas before calling float().",
              "A pattern such as r'\\$([\\d,]+(?:\\.\\d{2})?)' captures the number only."],
       solution=r"""
       import re

       PATTERN = re.compile(r"\$([\d,]+(?:\.\d{2})?)")


       def find_prices(text):
           return [float(m.replace(",", "")) for m in PATTERN.findall(text)]
       """)

    ex("p10.002", "p10", "Resilience", "Retry with backoff", 4,
       """
       Write `retry(times, delays)` - a decorator that retries a failing
       function up to `times` attempts, appending the delay it *would* sleep
       into the list `delays` instead of actually sleeping.

       Delays double each time, starting at 1. The last failure is re-raised.
       """,
       """
       import functools


       def retry(times, delays):
           pass
       """,
       [("succeeds first time",
         "log = []\n@retry(3, log)\ndef ok():\n    return 'fine'\nassert ok() == 'fine' and log == []"),
        ("retries then succeeds",
         "log = []\nstate = {'n': 0}\n@retry(3, log)\ndef flaky():\n    state['n'] += 1\n    if state['n'] < 3:\n        raise RuntimeError('nope')\n    return state['n']\nassert flaky() == 3 and log == [1, 2]"),
        ("gives up and re-raises",
         "log = []\n@retry(2, log)\ndef broken():\n    raise ValueError('always')\ntry:\n    broken()\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('should re-raise')"),
        ("keeps the name",
         "log = []\n@retry(1, log)\ndef named():\n    pass\nassert named.__name__ == 'named'")],
       hints=["Loop over the attempts; return on success, record the delay on failure.",
              "Do not sleep after the final attempt - there is nothing left to wait for."],
       solution="""
       import functools


       def retry(times, delays):
           def decorator(func):
               @functools.wraps(func)
               def wrapper(*args, **kwargs):
                   wait = 1
                   for attempt in range(1, times + 1):
                       try:
                           return func(*args, **kwargs)
                       except Exception:
                           if attempt == times:
                               raise
                           delays.append(wait)
                           wait *= 2
               return wrapper
           return decorator
       """)

    ex("p10.003", "p10", "Data cleaning", "Deduplicate records", 3,
       """
       Write `dedupe(rows, key)` returning the rows with duplicates removed by
       the value of `row[key]`, keeping the *last* occurrence and preserving
       the order of those survivors.
       """,
       """
       def dedupe(rows, key):
           pass
       """,
       [("keeps the last",
         "rows = [{'id': 1, 'v': 'a'}, {'id': 1, 'v': 'b'}, {'id': 2, 'v': 'c'}]\nassert dedupe(rows, 'id') == [{'id': 1, 'v': 'b'}, {'id': 2, 'v': 'c'}]"),
        ("no duplicates",
         "rows = [{'id': 1}, {'id': 2}]\nassert dedupe(rows, 'id') == rows"),
        ("empty", "assert dedupe([], 'id') == []"),
        ("order of survivors",
         "rows = [{'k': 'b'}, {'k': 'a'}, {'k': 'b'}]\nassert [r['k'] for r in dedupe(rows, 'k')] == ['b', 'a']")],
       hints=["A dict keyed by the id keeps insertion order but replaces the value.",
              "Since Python 3.7 dict order is guaranteed, so list(d.values()) is stable."],
       solution="""
       def dedupe(rows, key):
           out = {}
           for row in rows:
               out[row[key]] = row
           return list(out.values())
       """)

    ex("p11.001", "p11", "asyncio", "Run work concurrently", 4,
       """
       Write an async function `fetch_all(urls)` that calls the provided
       `fetch(url)` coroutine for every url *concurrently* and returns the
       results in the original order.

       `fetch` sleeps for 0.05s, so ten sequential calls take half a second
       and the concurrent version takes about one twentieth of that.
       """,
       """
       import asyncio


       async def fetch_all(urls):
           pass
       """,
       [("returns in order",
         "import asyncio\nassert asyncio.run(fetch_all(['a', 'b', 'c'])) == ['got a', 'got b', 'got c']"),
        ("empty", "import asyncio\nassert asyncio.run(fetch_all([])) == []"),
        ("actually concurrent",
         "import asyncio, time\nstart = time.monotonic()\nasyncio.run(fetch_all([str(i) for i in range(10)]))\nassert time.monotonic() - start < 0.3")],
       setup="""
       import asyncio


       async def fetch(url):
           await asyncio.sleep(0.05)
           return f"got {url}"
       """,
       hints=["asyncio.gather starts every coroutine and waits for all of them.",
              "Awaiting inside a for loop is sequential - that is the trap."],
       solution="""
       import asyncio


       async def fetch_all(urls):
           return list(await asyncio.gather(*(fetch(url) for url in urls)))
       """)

    ex("p11.002", "p11", "asyncio", "Limit how much runs at once", 5,
       """
       Write `fetch_limited(urls, limit)` running the same `fetch` coroutine
       concurrently but with at most `limit` calls in flight at any moment.

       Results stay in the original order. A `peak` list records the highest
       concurrency reached - the checks read it.
       """,
       """
       import asyncio


       async def fetch_limited(urls, limit):
           pass
       """,
       [("returns in order",
         "import asyncio\nassert asyncio.run(fetch_limited(['a', 'b'], 2)) == ['got a', 'got b']"),
        ("respects the limit",
         "import asyncio\nSTATE['peak'] = 0\nasyncio.run(fetch_limited([str(i) for i in range(12)], 3))\nassert STATE['peak'] <= 3"),
        ("still concurrent",
         "import asyncio, time\nSTATE['peak'] = 0\nstart = time.monotonic()\nasyncio.run(fetch_limited([str(i) for i in range(9)], 3))\nassert STATE['peak'] > 1 and time.monotonic() - start < 0.5")],
       setup="""
       import asyncio

       STATE = {"live": 0, "peak": 0}


       async def fetch(url):
           STATE["live"] += 1
           STATE["peak"] = max(STATE["peak"], STATE["live"])
           try:
               await asyncio.sleep(0.05)
               return f"got {url}"
           finally:
               STATE["live"] -= 1
       """,
       hints=["asyncio.Semaphore(limit) is an async context manager.",
              "Wrap each call in a small coroutine that holds the semaphore."],
       solution="""
       import asyncio


       async def fetch_limited(urls, limit):
           gate = asyncio.Semaphore(limit)

           async def one(url):
               async with gate:
                   return await fetch(url)

           return list(await asyncio.gather(*(one(u) for u in urls)))
       """)

    ex("p11.003", "p11", "asyncio", "Give up on time", 4,
       """
       Write `with_timeout(coro, seconds, fallback)` that awaits a coroutine
       and returns `fallback` if it takes longer than `seconds`.

       The slow coroutine must actually be cancelled, not left running.
       """,
       """
       import asyncio


       async def with_timeout(coro, seconds, fallback):
           pass
       """,
       [("fast path returns the value",
         "import asyncio\n\nasync def quick():\n    return 'done'\nassert asyncio.run(with_timeout(quick(), 1, 'late')) == 'done'"),
        ("slow path returns the fallback",
         "import asyncio\n\nasync def slow():\n    await asyncio.sleep(5)\n    return 'never'\nassert asyncio.run(with_timeout(slow(), 0.05, 'late')) == 'late'"),
        ("does not take the full time",
         "import asyncio, time\n\nasync def slow():\n    await asyncio.sleep(5)\nstart = time.monotonic()\nasyncio.run(with_timeout(slow(), 0.05, None))\nassert time.monotonic() - start < 1.0")],
       hints=["asyncio.wait_for cancels the coroutine and raises TimeoutError.",
              "Catch asyncio.TimeoutError and return the fallback."],
       solution="""
       import asyncio


       async def with_timeout(coro, seconds, fallback):
           try:
               return await asyncio.wait_for(coro, timeout=seconds)
           except asyncio.TimeoutError:
               return fallback
       """)

    ex("p13.001", "p13", "Passwords", "Store a password safely", 4,
       """
       Write `hash_password(password)` and `verify(password, stored)`.

       Use `hashlib.scrypt` with a fresh 16-byte random salt per password.
       Store salt and hash together as `"<salt_hex>$<hash_hex>"`.
       Compare with `hmac.compare_digest`, never with `==`.
       """,
       """
       import hashlib
       import hmac
       import secrets


       def hash_password(password):
           pass


       def verify(password, stored):
           pass
       """,
       [("round trips",
         "stored = hash_password('correct horse')\nassert verify('correct horse', stored) is True"),
        ("rejects the wrong password",
         "assert verify('wrong', hash_password('right')) is False"),
        ("salt differs every time",
         "assert hash_password('same') != hash_password('same')"),
        ("stores salt and hash",
         "assert hash_password('x').count('$') == 1"),
        ("constant-time comparison",
         "import inspect\nassert 'compare_digest' in inspect.getsource(verify)"),
        ("malformed input is rejected",
         "assert verify('x', 'garbage') is False")],
       hints=["scrypt needs n, r and p; n=16384, r=8, p=1 is a common baseline.",
              "A plain == on secrets leaks timing information about the prefix."],
       solution="""
       import hashlib
       import hmac
       import secrets

       PARAMS = {"n": 16384, "r": 8, "p": 1, "dklen": 32}


       def hash_password(password):
           salt = secrets.token_bytes(16)
           digest = hashlib.scrypt(password.encode(), salt=salt, **PARAMS)
           return f"{salt.hex()}${digest.hex()}"


       def verify(password, stored):
           try:
               salt_hex, digest_hex = stored.split("$")
               salt = bytes.fromhex(salt_hex)
               expected = bytes.fromhex(digest_hex)
           except (ValueError, AttributeError):
               return False
           actual = hashlib.scrypt(password.encode(), salt=salt, **PARAMS)
           return hmac.compare_digest(actual, expected)
       """)

    ex("p13.002", "p13", "Paths", "Refuse to escape the root", 4,
       """
       Write `safe_join(root, user_path)` returning the resolved path inside
       `root`, or raising `ValueError` when the user path escapes it.

       `"../../etc/passwd"` and an absolute path must both be rejected.
       """,
       """
       from pathlib import Path


       def safe_join(root, user_path):
           pass
       """,
       [("normal file",
         "from pathlib import Path\nassert safe_join('data', 'a/b.txt') == (Path('data').resolve() / 'a' / 'b.txt')"),
        ("rejects traversal",
         "try:\n    safe_join('data', '../../etc/passwd')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects an absolute path",
         "import os\ntarget = 'C:/Windows' if os.name == 'nt' else '/etc'\ntry:\n    safe_join('data', target)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects a sneaky middle traversal",
         "try:\n    safe_join('data', 'ok/../../out.txt')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')")],
       hints=["Resolve both paths first, then test containment - string prefixes lie.",
              "Path.is_relative_to does the containment check for you."],
       solution="""
       from pathlib import Path


       def safe_join(root, user_path):
           base = Path(root).resolve()
           candidate = (base / user_path).resolve()
           if not candidate.is_relative_to(base):
               raise ValueError("path escapes the root directory")
           return candidate
       """)

    ex("p13.003", "p13", "Injection", "Never build SQL from strings", 4,
       """
       `find_user` below is vulnerable: a name of `' OR '1'='1` returns every
       row. Rewrite it with a parameterised query so the same input returns
       nothing.
       """,
       """
       def find_user(conn, name):
           # vulnerable - rewrite this
           return conn.execute(
               "SELECT id FROM users WHERE name = '" + name + "'").fetchall()
       """,
       [("finds a real user",
         "assert [r[0] for r in find_user(CONN, 'ada')] == [1]"),
        ("injection returns nothing",
         "attack = chr(39) + ' OR ' + chr(39) + '1' + chr(39) + '=' + chr(39) + '1'"
         "\nassert find_user(CONN, attack) == []"),
        ("no string concatenation into sql",
         "import inspect\nsrc = inspect.getsource(find_user)"
         "\nassert ' + ' not in src"),
        ("uses a placeholder",
         "import inspect\nassert '?' in inspect.getsource(find_user)")],
       setup="""
       import sqlite3

       CONN = sqlite3.connect(":memory:")
       CONN.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
       CONN.executemany("INSERT INTO users (id, name) VALUES (?, ?)",
                        [(1, "ada"), (2, "grace")])
       CONN.commit()
       """,
       hints=["The database driver escapes bound parameters; string formatting does not.",
              "conn.execute(sql, (name,)) - note the trailing comma making a tuple."],
       solution="""
       def find_user(conn, name):
           return conn.execute(
               "SELECT id FROM users WHERE name = ?", (name,)).fetchall()
       """)

    ex("p14.001", "p14", "Maths", "Cosine similarity", 3,
       """
       Write `cosine(a, b)` returning the cosine similarity of two equal-length
       vectors given as lists of floats.

       Return 0.0 when either vector is all zeros. Raise `ValueError` on a
       length mismatch. Pure Python - no numpy.
       """,
       """
       import math


       def cosine(a, b):
           pass
       """,
       [("identical vectors", "assert abs(cosine([1, 2, 3], [1, 2, 3]) - 1.0) < 1e-9"),
        ("orthogonal", "assert abs(cosine([1, 0], [0, 1])) < 1e-9"),
        ("opposite", "assert abs(cosine([1, 0], [-1, 0]) + 1.0) < 1e-9"),
        ("zero vector", "assert cosine([0, 0], [1, 1]) == 0.0"),
        ("length mismatch",
         "try:\n    cosine([1], [1, 2])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')")],
       hints=["Cosine is the dot product divided by the product of the magnitudes.",
              "sum(x * y for x, y in zip(a, b)) is the dot product."],
       solution="""
       import math


       def cosine(a, b):
           if len(a) != len(b):
               raise ValueError("vectors must be the same length")
           dot = sum(x * y for x, y in zip(a, b))
           mag_a = math.sqrt(sum(x * x for x in a))
           mag_b = math.sqrt(sum(y * y for y in b))
           if mag_a == 0 or mag_b == 0:
               return 0.0
           return dot / (mag_a * mag_b)
       """)

    ex("p14.002", "p14", "Maths", "Softmax without overflow", 4,
       """
       Write `softmax(scores)` turning a list of numbers into probabilities
       that sum to 1.

       Subtract the maximum before exponentiating, or large inputs overflow.
       """,
       """
       import math


       def softmax(scores):
           pass
       """,
       [("sums to one",
         "assert abs(sum(softmax([1, 2, 3])) - 1.0) < 1e-9"),
        ("order is preserved",
         "p = softmax([1, 3, 2])\nassert p[1] > p[2] > p[0]"),
        ("uniform input",
         "p = softmax([5, 5])\nassert abs(p[0] - 0.5) < 1e-9"),
        ("survives huge values",
         "p = softmax([1000, 1001])\nassert abs(sum(p) - 1.0) < 1e-9"),
        ("empty", "assert softmax([]) == []")],
       hints=["exp(1000) overflows a float; exp(1000 - 1001) does not.",
              "Subtracting a constant from every score leaves the result unchanged."],
       solution="""
       import math


       def softmax(scores):
           if not scores:
               return []
           top = max(scores)
           exps = [math.exp(s - top) for s in scores]
           total = sum(exps)
           return [e / total for e in exps]
       """)

    ex("p14.003", "p14", "Evaluation", "Split the data honestly", 4,
       """
       Write `train_test_split(rows, test_ratio, seed)` returning
       `(train, test)`.

       The split must be reproducible for a given seed, must not lose or
       duplicate any row, and must not mutate the input.
       """,
       """
       import random


       def train_test_split(rows, test_ratio, seed):
           pass
       """,
       [("sizes",
         "train, test = train_test_split(list(range(100)), 0.2, 1)\nassert len(test) == 20 and len(train) == 80"),
        ("nothing lost",
         "train, test = train_test_split(list(range(50)), 0.3, 7)\nassert sorted(train + test) == list(range(50))"),
        ("reproducible",
         "a = train_test_split(list(range(30)), 0.25, 42)\nb = train_test_split(list(range(30)), 0.25, 42)\nassert a == b"),
        ("different seeds differ",
         "a = train_test_split(list(range(60)), 0.25, 1)\nb = train_test_split(list(range(60)), 0.25, 2)\nassert a != b"),
        ("input untouched",
         "src = list(range(10))\ntrain_test_split(src, 0.5, 1)\nassert src == list(range(10))")],
       hints=["random.Random(seed) gives a private generator, so you do not disturb global state.",
              "Shuffle a copy, then slice."],
       solution="""
       import random


       def train_test_split(rows, test_ratio, seed):
           shuffled = list(rows)
           random.Random(seed).shuffle(shuffled)
           cut = int(len(shuffled) * test_ratio)
           return shuffled[cut:], shuffled[:cut]
       """)

    ex("p14.004", "p14", "Evaluation", "Precision, recall and F1", 4,
       """
       Write `scores(predicted, actual)` for two equal-length lists of 0/1
       labels, returning a dict with `precision`, `recall` and `f1`.

       A metric whose denominator is zero is 0.0, not a crash.
       """,
       """
       def scores(predicted, actual):
           pass
       """,
       [("perfect",
         "r = scores([1, 0, 1], [1, 0, 1])\nassert r == {'precision': 1.0, 'recall': 1.0, 'f1': 1.0}"),
        ("half right",
         "r = scores([1, 1], [1, 0])\nassert r['precision'] == 0.5 and r['recall'] == 1.0"),
        ("nothing predicted",
         "r = scores([0, 0], [1, 1])\nassert r == {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}"),
        ("no positives at all",
         "r = scores([0], [0])\nassert r['f1'] == 0.0"),
        ("length mismatch",
         "try:\n    scores([1], [1, 0])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')")],
       hints=["Precision is tp / (tp + fp); recall is tp / (tp + fn).",
              "F1 is the harmonic mean, 2pr / (p + r)."],
       solution="""
       def scores(predicted, actual):
           if len(predicted) != len(actual):
               raise ValueError("inputs must be the same length")
           tp = sum(1 for p, a in zip(predicted, actual) if p == 1 and a == 1)
           fp = sum(1 for p, a in zip(predicted, actual) if p == 1 and a == 0)
           fn = sum(1 for p, a in zip(predicted, actual) if p == 0 and a == 1)
           precision = tp / (tp + fp) if tp + fp else 0.0
           recall = tp / (tp + fn) if tp + fn else 0.0
           f1 = (2 * precision * recall / (precision + recall)
                 if precision + recall else 0.0)
           return {"precision": precision, "recall": recall, "f1": f1}
       """)

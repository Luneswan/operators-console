"""Warm-ups for phase 04, and the back half of the course: phases 06, 07,
12, 15, 16 and 17.

Every exercise here is pure Python. The grader runs it in a subprocess with
no network and no external tools, so the systems topics are practised on the
text, bytes and dicts those systems hand you: a /proc file, an HTTP response,
a Dockerfile, a binary header. Clocks and randomness are injected, so every
check is deterministic.
"""
from ex_lib import ex


def raises(call, exc="ValueError"):
    """Check code asserting `call` raises `exc`, and saying what it did
    instead when it does not."""
    return ("try:\n"
            "    result = %s\n"
            "except %s:\n"
            "    pass\n"
            "else:\n"
            "    raise AssertionError('expected %s, but it returned %%r' %% (result,))"
            % (call, exc, exc))


def build_warmups():
    """Three level 2-3 warm-ups that list ahead of p04's own exercises, so
    the phase ramps 2-3-4-5 instead of opening at 3 and climbing to 5."""
    ex("p04.011", "p04", "Queues", "Where a ring buffer writes", 2,
       """
       A ring buffer is a fixed list of slots and a write position that wraps
       back to slot 0 after the last slot, overwriting whatever was there.

       Write `ring_slots(capacity, pushes)` that pushes the values
       `0, 1, 2, ... pushes - 1` one at a time into `capacity` slots and
       returns the slots as they are laid out in memory - a list of length
       `capacity`, with `None` in any slot never written.

       `ring_slots(3, 4)` is `[3, 1, 2]`: the value 3 wrapped round and
       overwrote 0. Raise `ValueError` when `capacity` is below 1.
       """,
       """
       def ring_slots(capacity, pushes):
           pass
       """,
       [("under capacity", "assert ring_slots(3, 2) == [0, 1, None]"),
        ("wraps and overwrites", "assert ring_slots(3, 4) == [3, 1, 2]"),
        ("wraps twice", "assert ring_slots(2, 5) == [4, 3]"),
        ("nothing pushed", "assert ring_slots(3, 0) == [None, None, None]"),
        ("one slot", "assert ring_slots(1, 3) == [2]"),
        ("rejects no slots", raises("ring_slots(0, 3)"))],
       hints=["Where the n-th value lands depends only on n and the capacity.",
              "Start from `[None] * capacity`; the slot for a value is "
              "`value % capacity`."],
       solution="""
       def ring_slots(capacity, pushes):
           if capacity < 1:
               raise ValueError("capacity must be at least 1")
           slots = [None] * capacity
           for value in range(pushes):
               slots[value % capacity] = value
           return slots
       """)

    ex("p04.012", "p04", "Hash tables", "Count the collisions", 2,
       """
       A toy hash table puts an integer key in bucket `key % buckets`.

       Write `count_collisions(keys, buckets)` returning how many keys landed
       in a bucket that already held a different key. A key seen before is
       the same entry being overwritten, not a collision, so repeats count
       nothing. Negative keys use Python's `%`, which always gives a bucket
       between 0 and `buckets - 1`.

       Raise `ValueError` when `buckets` is below 1.
       """,
       """
       def count_collisions(keys, buckets):
           pass
       """,
       [("no collisions", "assert count_collisions([1, 2, 3], 4) == 0"),
        ("all in one bucket", "assert count_collisions([1, 5, 9], 4) == 2"),
        ("repeats are not collisions",
         "assert count_collisions([1, 1, 1], 4) == 0"),
        ("two busy buckets",
         "assert count_collisions([0, 8, 16, 3, 11], 8) == 3"),
        ("negative keys", "assert count_collisions([-1, 3], 4) == 1"),
        ("rejects no buckets", raises("count_collisions([1], 0)"))],
       hints=["You need to remember two things as you go: which keys you have "
              "seen, and which buckets are already occupied.",
              "Two sets do it. Skip a key already in the first; otherwise a "
              "bucket already in the second is a collision."],
       solution="""
       def count_collisions(keys, buckets):
           if buckets < 1:
               raise ValueError("buckets must be at least 1")
           seen = set()
           used = set()
           collisions = 0
           for key in keys:
               if key in seen:
                   continue
               seen.add(key)
               bucket = key % buckets
               if bucket in used:
                   collisions += 1
               else:
                   used.add(bucket)
           return collisions
       """)

    ex("p04.013", "p04", "Heaps", "Check the heap property", 3,
       """
       A min-heap stored in a list keeps one rule: no item is smaller than its
       parent. The parent of index `i` is at index `(i - 1) // 2`.

       Write `heap_violation(values)` returning the index of the first item
       that is smaller than its parent, or `None` when the list is a valid
       min-heap. Equal values are allowed. An empty list and a one-item list
       are valid heaps.
       """,
       """
       def heap_violation(values):
           pass
       """,
       [("valid heap", "assert heap_violation([1, 3, 2, 7, 4]) is None"),
        ("empty and single", "assert heap_violation([]) is None\n"
                             "assert heap_violation([5]) is None"),
        ("child smaller than root", "assert heap_violation([5, 3]) == 1"),
        ("deep violation", "assert heap_violation([1, 3, 2, 0]) == 3"),
        ("equal values are fine", "assert heap_violation([1, 1, 1]) is None"),
        ("reports the first one",
         "assert heap_violation([2, 3, 4, 5, 6, 1, 0]) == 5")],
       hints=["Every item except the root has exactly one parent. Compare "
              "each item with its parent, once.",
              "Walk `i` from 1 to the end and compare `values[i]` with "
              "`values[(i - 1) // 2]`; return at the first failure."],
       solution="""
       def heap_violation(values):
           for i in range(1, len(values)):
               if values[i] < values[(i - 1) // 2]:
                   return i
           return None
       """)


def build():
    _p06()
    _p07()
    _p12()
    _p15()
    _p16()
    _p17()


def _p06():
    ex("p06.001", "p06", "Permissions", "Read an ls -l mode", 2,
       """
       `ls -l` shows a mode like `-rwxr-xr--`: one file-type character, then
       three groups of three for owner, group and others. In each group `r`
       is worth 4, `w` 2 and `x` 1, and `-` is worth nothing.

       Write `mode_to_octal(perm)` returning the three-digit string `chmod`
       would take, so `'-rwxr-xr--'` gives `'754'`. The first character can
       be anything (`-`, `d`, `l`...). Only `r`, `w`, `x` and `-` appear in
       the other nine. Raise `ValueError` when `perm` is not 10 characters.
       """,
       """
       def mode_to_octal(perm):
           pass
       """,
       [("a script", "assert mode_to_octal('-rwxr-xr--') == '754'"),
        ("a private directory", "assert mode_to_octal('drwx------') == '700'"),
        ("nothing allowed", "assert mode_to_octal('----------') == '000'"),
        ("world writable", "assert mode_to_octal('-rw-rw-rw-') == '666'"),
        ("rejects a short mode", raises("mode_to_octal('rwx')"))],
       hints=["Skip the first character, then treat the rest as three separate "
              "groups of three.",
              "For each group add 4, 2 and 1 for the positions that are not "
              "`-`, and turn the total into a digit with `str()`."],
       solution="""
       def mode_to_octal(perm):
           if len(perm) != 10:
               raise ValueError("a mode is 10 characters, like -rwxr-xr--")
           digits = []
           for start in (1, 4, 7):
               value = 0
               for char, bit in zip(perm[start:start + 3], (4, 2, 1)):
                   if char != "-":
                       value += bit
               digits.append(str(value))
           return "".join(digits)
       """)

    ex("p06.002", "p06", "Processes", "Parse a /proc file", 2,
       """
       Files under `/proc`, such as `/proc/<pid>/status` and `/proc/meminfo`,
       are lines of `Key: value`, often padded with tabs or spaces.

       Write `parse_status(text)` returning a dict of key to value, both with
       surrounding whitespace removed. Split each line on its first colon
       only, because values can contain colons. Skip blank lines and lines
       with no colon. Values stay strings.
       """,
       """
       def parse_status(text):
           pass
       """,
       [("a status file", r"""
         text = 'Name:\tpython3\nState:\tS (sleeping)\nPid:\t4242\n'
         assert parse_status(text) == {'Name': 'python3', 'State': 'S (sleeping)', 'Pid': '4242'}
         """),
        ("meminfo padding", r"""
         text = 'MemTotal:       16318412 kB\nMemFree:            1024 kB'
         assert parse_status(text) == {'MemTotal': '16318412 kB', 'MemFree': '1024 kB'}
         """),
        ("colon inside a value",
         """assert parse_status('Cmd: python -c "a:b"') == {'Cmd': 'python -c "a:b"'}"""),
        ("skips noise", r"""
         assert parse_status('\nNoColonHere\nUid:  1000\n\n') == {'Uid': '1000'}
         """),
        ("empty text", "assert parse_status('') == {}")],
       hints=["`str.splitlines()` gives you the lines; decide what to do with "
              "each one before splitting it.",
              "`line.partition(':')` splits on the first colon only and tells "
              "you whether there was one at all."],
       solution="""
       def parse_status(text):
           fields = {}
           for line in text.splitlines():
               key, colon, value = line.partition(":")
               if not colon:
                   continue
               fields[key.strip()] = value.strip()
           return fields
       """)

    ex("p06.003", "p06", "Exit codes", "Say why a process stopped", 3,
       """
       Write `describe_exit(code)` for a process's exit status:

       - `0` gives `'ok'`.
       - A negative code `-N` gives `'killed by signal N'`. This is what
         `subprocess` reports on Linux when a signal ended the child.
       - A shell reports a signal death as `128 + N`, so a code from 129 to
         192 inclusive gives `'killed by signal N'` too (137 is signal 9).
       - Any other positive code gives `'failed with code N'`.
       """,
       """
       def describe_exit(code):
           pass
       """,
       [("success", "assert describe_exit(0) == 'ok'"),
        ("a plain failure", "assert describe_exit(2) == 'failed with code 2'"),
        ("killed, as subprocess sees it",
         "assert describe_exit(-9) == 'killed by signal 9'"),
        ("killed, as a shell sees it",
         "assert describe_exit(137) == 'killed by signal 9'"),
        ("128 itself is a plain failure",
         "assert describe_exit(128) == 'failed with code 128'"),
        ("above the signal range",
         "assert describe_exit(255) == 'failed with code 255'")],
       hints=["Handle the cases in the order the prompt lists them, and watch "
              "both ends of the 129 to 192 range.",
              "`-code` turns -9 into 9, and `code - 128` turns 137 into 9. "
              "`129 <= code <= 192` is a single comparison in Python."],
       solution="""
       def describe_exit(code):
           if code == 0:
               return "ok"
           if code < 0:
               return "killed by signal %d" % -code
           if 129 <= code <= 192:
               return "killed by signal %d" % (code - 128)
           return "failed with code %d" % code
       """)

    ex("p06.004", "p06", "Filesystem", "Roll up sizes like du", 3,
       """
       A directory tree is given as a dict: a key is a name, an `int` value is
       a file's size in bytes, and a `dict` value is a subdirectory.

       Write `du(tree)` returning a dict from each directory's path to the
       total bytes beneath it, like `du` does. The top of the tree is `'.'`
       and a subdirectory's path joins names with `/`, so `'./src/lib'`.
       Every directory appears, including empty ones, which total 0.
       """,
       """
       def du(tree):
           pass
       """,
       [("a small project", """
         tree = {'a.txt': 100, 'src': {'main.py': 40, 'lib': {'x.py': 10}}, 'empty': {}}
         assert du(tree) == {'.': 150, './src': 50, './src/lib': 10, './empty': 0}
         """),
        ("an empty tree", "assert du({}) == {'.': 0}"),
        ("files only", "assert du({'f': 5, 'g': 7}) == {'.': 12}"),
        ("deep nesting", """
         tree = {'d': {'d': {'d': {'f': 1}}}}
         assert du(tree) == {'.': 1, './d': 1, './d/d': 1, './d/d/d': 1}
         """)],
       hints=["A directory's total is its own files plus the totals of its "
              "subdirectories - a recursive definition.",
              "Write an inner function `walk(node, path)` that returns the "
              "total and records it in a shared dict before returning."],
       solution="""
       def du(tree):
           totals = {}

           def walk(node, path):
               total = 0
               for name, child in node.items():
                   if isinstance(child, dict):
                       total += walk(child, path + "/" + name)
                   else:
                       total += child
               totals[path] = total
               return total

           walk(tree, ".")
           return totals
       """)


def _p07():
    ex("p07.001", "p07", "HTTP", "Read a status code", 2,
       """
       Write two functions.

       `classify_status(code)` returns `'informational'` for 100-199,
       `'success'` for 200-299, `'redirect'` for 300-399, `'client error'`
       for 400-499 and `'server error'` for 500-599. Raise `ValueError` for
       anything outside 100-599.

       `is_retryable(code)` returns True only for the codes where trying the
       same request again later can succeed: 408, 429, 502, 503 and 504.
       Everything else, including 500, returns False.
       """,
       """
       def classify_status(code):
           pass


       def is_retryable(code):
           pass
       """,
       [("success", "assert classify_status(200) == 'success'"),
        ("redirect and informational",
         "assert classify_status(301) == 'redirect'\n"
         "assert classify_status(101) == 'informational'"),
        ("errors", "assert classify_status(404) == 'client error'\n"
                   "assert classify_status(503) == 'server error'"),
        ("rejects a made-up code", raises("classify_status(600)")),
        ("rate limited is retryable", "assert is_retryable(429) == True"),
        ("not found is not", "assert is_retryable(404) == False")],
       hints=["The first digit of a status code is its class.",
              "`code // 100` gives the class; a set literal holds the "
              "retryable codes."],
       solution="""
       RETRYABLE = {408, 429, 502, 503, 504}
       CLASSES = {1: "informational", 2: "success", 3: "redirect",
                  4: "client error", 5: "server error"}


       def classify_status(code):
           if not 100 <= code <= 599:
               raise ValueError("not an HTTP status code: %r" % code)
           return CLASSES[code // 100]


       def is_retryable(code):
           return code in RETRYABLE
       """)

    ex("p07.002", "p07", "Addressing", "Check an address against an allowlist", 3,
       """
       Write `allowed(address, networks)` returning True when the IP address
       string `address` falls inside any of the CIDR blocks in `networks`
       (strings like `'10.0.0.0/8'`), and False otherwise.

       Use the standard `ipaddress` module. Both IPv4 and IPv6 must work. An
       address that does not parse is not allowed - return False rather than
       raising. An empty `networks` list allows nothing. The networks are
       always well-formed.
       """,
       """
       def allowed(address, networks):
           pass
       """,
       [("inside a /8", "assert allowed('10.1.2.3', ['10.0.0.0/8']) == True"),
        ("outside every block",
         "assert allowed('192.168.1.5', ['10.0.0.0/8', '172.16.0.0/12']) == False"),
        ("edge of a /12",
         "assert allowed('172.31.255.255', ['10.0.0.0/8', '172.16.0.0/12']) == True"),
        ("IPv6", "assert allowed('2001:db8::1', ['2001:db8::/32']) == True"),
        ("garbage is refused",
         "assert allowed('not-an-ip', ['0.0.0.0/0']) == False"),
        ("nothing listed", "assert allowed('10.0.0.1', []) == False")],
       hints=["Do not compare strings or split on dots: `ipaddress` knows what "
              "a network contains.",
              "`ipaddress.ip_address(a) in ipaddress.ip_network(n)` is the "
              "test; parsing a bad address raises `ValueError`."],
       solution="""
       import ipaddress


       def allowed(address, networks):
           try:
               ip = ipaddress.ip_address(address)
           except ValueError:
               return False
           return any(ip in ipaddress.ip_network(net) for net in networks)
       """)

    ex("p07.003", "p07", "Timeouts and retries", "A retry schedule with a budget", 3,
       """
       Write `backoff_schedule(base, cap, budget, rand, max_attempts=10)`
       returning the list of delays, in seconds, a client would wait between
       retries.

       Attempt `n` (counting from 0) waits `min(cap, base * 2 ** n) * rand()`.
       `rand` is a function with no arguments returning a number from 0 to 1;
       it is passed in so the jitter can be tested. Call it once per attempt.

       Stop before a delay would push the running total above `budget` (a
       total exactly equal to the budget is fine), or once the list holds
       `max_attempts` delays, whichever comes first.
       """,
       """
       def backoff_schedule(base, cap, budget, rand, max_attempts=10):
           pass
       """,
       [("doubles up to the cap",
         "assert backoff_schedule(1, 8, 20, lambda: 1.0) == [1, 2, 4, 8]"),
        ("jitter shrinks each delay",
         "assert backoff_schedule(1, 8, 20, lambda: 0.5) == "
         "[0.5, 1.0, 2.0, 4.0, 4.0, 4.0, 4.0]"),
        ("the budget can be spent exactly",
         "assert backoff_schedule(1, 8, 7, lambda: 1.0) == [1, 2, 4]"),
        ("a budget too small for one retry",
         "assert backoff_schedule(1, 8, 0.5, lambda: 1.0) == []"),
        ("max_attempts wins", """
         assert backoff_schedule(2, 100, 1000, lambda: 1.0, max_attempts=3) == [2, 4, 8]
         assert backoff_schedule(1, 8, 20, lambda: 0.0) == [0.0] * 10
         """),
        ("one rand() per attempt", """
         values = iter([1.0, 0.5, 0.25])
         assert backoff_schedule(4, 100, 100, lambda: next(values), max_attempts=3) == [4.0, 4.0, 4.0]
         """)],
       hints=["Keep a running total next to the list, and check it before you "
              "append, not after.",
              "Loop `for n in range(max_attempts)`, compute the delay, and "
              "`break` when `total + delay > budget`."],
       solution="""
       def backoff_schedule(base, cap, budget, rand, max_attempts=10):
           delays = []
           total = 0
           for n in range(max_attempts):
               delay = min(cap, base * 2 ** n) * rand()
               if total + delay > budget:
                   break
               delays.append(delay)
               total += delay
           return delays
       """)

    ex("p07.004", "p07", "HTTP", "Parse a raw HTTP response", 4,
       r"""
       Write `parse_response(raw)` taking the bytes of an HTTP/1.1 response
       and returning a tuple `(status, headers, body)`.

       - The head ends at the first `b'\r\n\r\n'`; everything after it is the
         body, returned as bytes exactly as sent (it may contain `\r\n\r\n`
         itself). If there is no blank line, raise `ValueError`.
       - Decode the head as `'latin-1'` and split it into lines on `'\r\n'`.
       - The first line is the status line, like `HTTP/1.1 200 OK`. The
         reason phrase may be missing (`HTTP/1.1 204`). `status` is the code
         as an int. Raise `ValueError` if the line does not start `HTTP/`.
       - Each other line is `Name: value`. Header names are case-insensitive,
         so store them lowercased; strip the values. A header sent more than
         once has its values joined with `', '` in the order they arrived.
       """,
       """
       def parse_response(raw):
           pass
       """,
       [("status code", r"""
         raw = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nhi'
         assert parse_response(raw)[0] == 200
         """),
        ("headers are lowercased", r"""
         raw = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length:  2 \r\n\r\nhi'
         assert parse_response(raw)[1] == {'content-type': 'text/plain', 'content-length': '2'}
         """),
        ("body kept verbatim", r"""
         raw = b'HTTP/1.1 200 OK\r\nX-Id: 1\r\n\r\nline1\r\n\r\nline2'
         assert parse_response(raw)[2] == b'line1\r\n\r\nline2'
         """),
        ("no reason phrase, no body", r"""
         assert parse_response(b'HTTP/1.1 204\r\n\r\n') == (204, {}, b'')
         """),
        ("repeated headers are joined", r"""
         raw = (b'HTTP/1.1 302 Found\r\nSet-Cookie: a=1\r\nset-cookie: b=2\r\n'
                b'Location: /home\r\n\r\n')
         assert parse_response(raw)[1] == {'set-cookie': 'a=1, b=2', 'location': '/home'}
         """),
        ("a truncated response",
         raises(r"parse_response(b'HTTP/1.1 200 OK\r\nContent-Type: text/plain')"))],
       hints=["Split the head from the body first, with the bytes still bytes. "
              "Only the head is text.",
              r"`raw.partition(b'\r\n\r\n')` gives head, separator and body "
              "in one call; the separator is empty when there was no blank "
              "line."],
       solution=r"""
       def parse_response(raw):
           head, blank, body = raw.partition(b"\r\n\r\n")
           if not blank:
               raise ValueError("no blank line ends the headers")
           lines = head.decode("latin-1").split("\r\n")
           status_line = lines[0]
           if not status_line.startswith("HTTP/"):
               raise ValueError("not an HTTP status line: %r" % status_line)
           status = int(status_line.split()[1])
           headers = {}
           for line in lines[1:]:
               name, _, value = line.partition(":")
               name = name.strip().lower()
               value = value.strip()
               if name in headers:
                   headers[name] += ", " + value
               else:
                   headers[name] = value
           return status, headers, body
       """)


def _p12():
    ex("p12.001", "p12", "Releases", "A semantic version gate", 2,
       """
       Write `bump_kind(old, new)` for two versions like `'1.4.2'`. Either may
       start with a `v` (`'v1.4.2'`).

       Return `'major'`, `'minor'` or `'patch'`: the most significant part
       that went up. Compare the parts as numbers, so `1.10.0` is newer than
       `1.9.0`. Raise `ValueError` when `new` is not newer than `old`, or when
       either is not three whole numbers separated by dots.
       """,
       """
       def bump_kind(old, new):
           pass
       """,
       [("a patch", "assert bump_kind('1.2.3', '1.2.4') == 'patch'"),
        ("a minor", "assert bump_kind('1.2.3', '1.3.0') == 'minor'"),
        ("numbers, not text", "assert bump_kind('1.9.0', '1.10.0') == 'minor'"),
        ("a major with a v prefix", "assert bump_kind('v0.9.9', '1.0.0') == 'major'"),
        ("the same version is refused", raises("bump_kind('1.2.3', '1.2.3')")),
        ("two parts are refused", raises("bump_kind('1.2', '1.3.0')"))],
       hints=["Turn each version into a tuple of three ints first; tuples "
              "compare part by part, which is exactly the rule.",
              "`s.removeprefix('v').split('.')`, check there are three parts "
              "that are all digits, then compare the tuples and find the "
              "first index where they differ."],
       solution="""
       def _parse(version):
           parts = version.removeprefix("v").split(".")
           if len(parts) != 3 or not all(p.isdigit() for p in parts):
               raise ValueError("not a MAJOR.MINOR.PATCH version: %r" % version)
           return tuple(int(p) for p in parts)


       def bump_kind(old, new):
           before, after = _parse(old), _parse(new)
           if after <= before:
               raise ValueError("%s is not newer than %s" % (new, old))
           for name, a, b in zip(("major", "minor", "patch"), before, after):
               if a != b:
                   return name
       """)

    ex("p12.002", "p12", "CI", "Validate a CI config", 3,
       """
       A CI config has been loaded into a dict shaped like a GitHub Actions
       workflow: `{'jobs': {name: job}}`, where a job has `'runs-on'`,
       `'steps'` (a list of dicts) and optionally `'needs'` (a list of job
       names, or a single name as a string).

       Write `ci_problems(config)` returning a sorted list of problem strings,
       or `[]` when the config is fine. Use exactly these messages:

       - `'no jobs'` when `jobs` is missing or empty (nothing else to check).
       - `'<job>: no runs-on'` when a job has no `runs-on`.
       - `'<job>: no steps'` when a job has no steps or an empty list.
       - `'<job>: step <n> needs exactly one of run or uses'` for a step with
         neither or both of those keys. `n` counts from 1.
       - `'<job>: needs unknown job <other>'` for each name in `needs` that
         is not a job.
       """,
       """
       def ci_problems(config):
           pass
       """,
       [("a good config", """
         config = {'jobs': {
             'test': {'runs-on': 'ubuntu-latest',
                      'steps': [{'uses': 'actions/checkout@v4'}, {'run': 'pytest'}]},
             'build': {'runs-on': 'ubuntu-latest', 'needs': ['test'],
                       'steps': [{'run': 'make'}]}}}
         assert ci_problems(config) == []
         """),
        ("no jobs at all", "assert ci_problems({}) == ['no jobs']\n"
                           "assert ci_problems({'jobs': {}}) == ['no jobs']"),
        ("a bare job", """
         assert ci_problems({'jobs': {'lint': {'steps': []}}}) == ['lint: no runs-on', 'lint: no steps']
         """),
        ("bad steps", """
         config = {'jobs': {'t': {'runs-on': 'x', 'steps': [
             {'run': 'a'}, {'name': 'oops'}, {'run': 'b', 'uses': 'c'}]}}}
         assert ci_problems(config) == [
             't: step 2 needs exactly one of run or uses',
             't: step 3 needs exactly one of run or uses']
         """),
        ("needs a job that is not there", """
         config = {'jobs': {'deploy': {'runs-on': 'x', 'steps': [{'run': 'go'}],
                                       'needs': 'tset'}}}
         assert ci_problems(config) == ['deploy: needs unknown job tset']
         """)],
       hints=["Collect problems into a list as you walk the jobs, and sort "
              "once at the end.",
              "`'run' in step` and `'uses' in step` are two booleans; the step "
              "is wrong when they are equal. Wrap a string `needs` in a list "
              "before looping over it."],
       solution="""
       def ci_problems(config):
           jobs = config.get("jobs") or {}
           if not jobs:
               return ["no jobs"]
           problems = []
           for name, job in jobs.items():
               if not job.get("runs-on"):
                   problems.append("%s: no runs-on" % name)
               steps = job.get("steps") or []
               if not steps:
                   problems.append("%s: no steps" % name)
               for number, step in enumerate(steps, 1):
                   if ("run" in step) == ("uses" in step):
                       problems.append("%s: step %d needs exactly one of run or uses"
                                       % (name, number))
               needs = job.get("needs") or []
               if isinstance(needs, str):
                   needs = [needs]
               for other in needs:
                   if other not in jobs:
                       problems.append("%s: needs unknown job %s" % (name, other))
           return sorted(problems)
       """)

    ex("p12.003", "p12", "Docker", "Spot a cache-busting Dockerfile", 4,
       r"""
       Docker caches each layer until something it depends on changes. Copying
       the whole project (`COPY . ...`) before `pip install` means every code
       change reinstalls every dependency.

       Write two functions.

       `layers(text)` returns a list of `(INSTRUCTION, arguments)` tuples, one
       per instruction, with the instruction uppercased (Docker accepts
       `run` as well as `RUN`) and the arguments stripped. Skip blank lines
       and comment lines (starting with `#`). A line ending in `\` continues
       on the next line: drop the backslash and join the pieces with a single
       space. Comments never appear inside a continued instruction.

       `cache_busting_lines(text)` returns the 1-based line numbers where
       each `RUN` containing `pip install` starts, when a `COPY` whose first
       source is `.` came earlier in the same stage. Arguments starting with
       `--` (like `--chown=app`) are options, not sources. A `FROM` starts a
       new stage and forgets any earlier `COPY`.
       """,
       """
       def layers(text):
           pass


       def cache_busting_lines(text):
           pass
       """,
       [("instructions in order", r"""
         text = ('FROM python:3.13-slim\nWORKDIR /app\nCOPY requirements.txt .\n'
                 'RUN pip install -r requirements.txt\nCOPY . .\nCMD ["python", "app.py"]\n')
         assert layers(text) == [('FROM', 'python:3.13-slim'), ('WORKDIR', '/app'),
                                 ('COPY', 'requirements.txt .'),
                                 ('RUN', 'pip install -r requirements.txt'),
                                 ('COPY', '. .'), ('CMD', '["python", "app.py"]')]
         """),
        ("the good order is clean", r"""
         text = ('FROM python:3.13-slim\nWORKDIR /app\nCOPY requirements.txt .\n'
                 'RUN pip install -r requirements.txt\nCOPY . .\n')
         assert cache_busting_lines(text) == []
         """),
        ("the bad order is flagged", r"""
         text = ('FROM python:3.13-slim\n# app code\nWORKDIR /app\nCOPY . .\n'
                 'RUN pip install -r requirements.txt\n')
         assert cache_busting_lines(text) == [5]
         """),
        ("continuations, options and lowercase", r"""
         text = ('FROM python:3.13\ncopy --chown=app . /app\nrun apt-get update && \\\n'
                 '    pip install -r /app/requirements.txt\n')
         assert layers(text)[2] == ('RUN', 'apt-get update && pip install -r /app/requirements.txt')
         assert cache_busting_lines(text) == [3]
         """),
        ("a new stage starts clean", r"""
         text = ('FROM python:3.13 AS build\nCOPY . /src\nRUN pip install build\n'
                 'FROM python:3.13-slim\nRUN pip install /wheels/app.whl\n')
         assert cache_busting_lines(text) == [3]
         """),
        ("only comments", r"assert layers('\n# nothing here\n\n') == []")],
       hints=["Write `layers` first, but have a helper also remember the line "
              "number each instruction started on; `cache_busting_lines` needs "
              "it.",
              "Keep a flag, 'copied everything', set by a matching COPY and "
              "cleared by FROM. For COPY, the first argument that does not "
              "start with `--` is the first source."],
       solution=r"""
       def _instructions(text):
           found = []
           pieces = None
           start = 0
           for number, line in enumerate(text.splitlines(), 1):
               stripped = line.strip()
               if pieces is None:
                   if not stripped or stripped.startswith("#"):
                       continue
                   pieces = []
                   start = number
               if stripped.endswith("\\"):
                   pieces.append(stripped[:-1].strip())
                   continue
               pieces.append(stripped)
               found.append((start, " ".join(p for p in pieces if p)))
               pieces = None
           if pieces:
               found.append((start, " ".join(p for p in pieces if p)))
           out = []
           for number, joined in found:
               word, _, rest = joined.partition(" ")
               out.append((number, word.upper(), rest.strip()))
           return out


       def layers(text):
           return [(word, args) for _, word, args in _instructions(text)]


       def cache_busting_lines(text):
           flagged = []
           copied_everything = False
           for number, word, args in _instructions(text):
               if word == "FROM":
                   copied_everything = False
               elif word == "COPY":
                   sources = [a for a in args.split() if not a.startswith("--")]
                   if sources and sources[0] == ".":
                       copied_everything = True
               elif word == "RUN" and copied_everything and "pip install" in args:
                   flagged.append(number)
           return flagged
       """)


def _p15():
    ex("p15.001", "p15", "Caching", "Cache-aside with a time to live", 3,
       """
       Write `TTLCache(loader, ttl, clock)` for the cache-aside pattern.
       `loader(key)` fetches the real value (think: a database query).
       `clock()` returns the current time in seconds; it is passed in so
       tests can move time by hand.

       - `get(key)` returns the cached value if it was loaded less than
         `ttl` seconds ago. Otherwise it calls `loader(key)`, stores the
         result with the current time, and returns it. An entry exactly
         `ttl` seconds old has expired.
       - If `loader` raises, the exception passes through and nothing is
         cached.
       - `invalidate(key)` forgets a key. Invalidating a key that is not
         cached does nothing.
       """,
       """
       class TTLCache:
           def __init__(self, loader, ttl, clock):
               pass

           def get(self, key):
               pass

           def invalidate(self, key):
               pass
       """,
       [("returns the loaded value", """
         cache = TTLCache(lambda key: key.upper(), 10, lambda: 0.0)
         assert cache.get('b') == 'B'
         """),
        ("loads once while fresh", """
         now, calls = [0.0], []
         def loader(key):
             calls.append(key)
             return key.upper()
         cache = TTLCache(loader, 10, lambda: now[0])
         cache.get('a')
         now[0] = 9.5
         cache.get('a')
         assert calls == ['a']
         """),
        ("expires at exactly ttl", """
         now, calls = [0.0], []
         def loader(key):
             calls.append(key)
             return key.upper()
         cache = TTLCache(loader, 10, lambda: now[0])
         cache.get('a')
         now[0] = 10.0
         cache.get('a')
         assert calls == ['a', 'a']
         """),
        ("invalidate forces a reload", """
         calls = []
         def loader(key):
             calls.append(key)
             return len(calls)
         cache = TTLCache(loader, 60, lambda: 0.0)
         cache.get('a')
         cache.invalidate('a')
         cache.invalidate('never-cached')
         assert cache.get('a') == 2
         """),
        ("a failure is not cached", """
         attempts = []
         def loader(key):
             attempts.append(key)
             if len(attempts) == 1:
                 raise ConnectionError('database down')
             return 'ok'
         cache = TTLCache(loader, 60, lambda: 0.0)
         try:
             cache.get('a')
         except ConnectionError:
             pass
         assert cache.get('a') == 'ok'
         """)],
       hints=["Store the value together with the time it was loaded, so `get` "
              "can decide whether it is still fresh.",
              "A dict of `key -> (value, loaded_at)`. Fresh means "
              "`clock() - loaded_at < ttl`; only write to the dict after "
              "`loader` has returned."],
       solution="""
       class TTLCache:
           def __init__(self, loader, ttl, clock):
               self.loader = loader
               self.ttl = ttl
               self.clock = clock
               self._entries = {}

           def get(self, key):
               now = self.clock()
               entry = self._entries.get(key)
               if entry is not None and now - entry[1] < self.ttl:
                   return entry[0]
               value = self.loader(key)
               self._entries[key] = (value, now)
               return value

           def invalidate(self, key):
               self._entries.pop(key, None)
       """)

    ex("p15.002", "p15", "Rate limiting", "A token bucket", 4,
       """
       Write `TokenBucket(rate, capacity, clock)`. The bucket starts full with
       `capacity` tokens and gains `rate` tokens per second, never holding
       more than `capacity`. `clock()` returns the current time in seconds.

       `allow(cost=1)` first adds the tokens earned since the last call, then
       returns True and spends `cost` tokens if there are at least that many.
       Otherwise it returns False and spends nothing, so a request bigger
       than the whole bucket is always refused but costs nothing.
       """,
       """
       class TokenBucket:
           def __init__(self, rate, capacity, clock):
               pass

           def allow(self, cost=1):
               pass
       """,
       [("a burst up to capacity", """
         bucket = TokenBucket(2, 4, lambda: 0.0)
         assert [bucket.allow() for _ in range(5)] == [True, True, True, True, False]
         """),
        ("refills with time", """
         now = [0.0]
         bucket = TokenBucket(2, 4, lambda: now[0])
         for _ in range(4):
             bucket.allow()
         now[0] = 0.5
         assert [bucket.allow(), bucket.allow()] == [True, False]
         """),
        ("never holds more than capacity", """
         now = [0.0]
         bucket = TokenBucket(2, 4, lambda: now[0])
         for _ in range(4):
             bucket.allow()
         now[0] = 100.0
         assert [bucket.allow() for _ in range(5)] == [True, True, True, True, False]
         """),
        ("costs", """
         bucket = TokenBucket(1, 4, lambda: 0.0)
         assert [bucket.allow(3), bucket.allow(2), bucket.allow(1)] == [True, False, True]
         """),
        ("a refusal spends nothing", """
         bucket = TokenBucket(1, 2, lambda: 0.0)
         assert [bucket.allow(3), bucket.allow(2)] == [False, True]
         """),
        ("a slow bucket", """
         now = [0.0]
         bucket = TokenBucket(0.25, 1, lambda: now[0])
         bucket.allow()
         now[0] = 2.0
         first = bucket.allow()
         now[0] = 4.0
         assert [first, bucket.allow()] == [False, True]
         """)],
       hints=["You only need two pieces of state besides the settings: how "
              "many tokens there are, and when you last looked.",
              "On each call: `tokens = min(capacity, tokens + (now - last) * "
              "rate)`, then `last = now`, then compare with `cost`."],
       solution="""
       class TokenBucket:
           def __init__(self, rate, capacity, clock):
               self.rate = rate
               self.capacity = capacity
               self.clock = clock
               self.tokens = capacity
               self.last = clock()

           def allow(self, cost=1):
               now = self.clock()
               earned = (now - self.last) * self.rate
               self.tokens = min(self.capacity, self.tokens + earned)
               self.last = now
               if self.tokens >= cost:
                   self.tokens -= cost
                   return True
               return False
       """)

    ex("p15.003", "p15", "Sharding", "A consistent hashing ring", 5,
       """
       Write `HashRing(nodes=(), replicas=100)` that decides which node owns a
       key, so that adding or removing a node moves as few keys as possible.

       Use the `position(text)` helper in the starter: never `hash()`, which
       changes between runs. Each node gets `replicas` virtual points on the
       ring, at `position(f"{node}#{i}")` for `i` in `range(replicas)`. A key
       sits at `position(key)`, and its owner is the node of the first
       virtual point at or after it, wrapping round to the lowest point when
       there is none.

       Support `add(node)`, `remove(node)` and `node_for(key)`. `node_for` on
       an empty ring raises `LookupError`. The order nodes were added in must
       not change any answer.
       """,
       """
       import hashlib


       def position(text):
           return int(hashlib.md5(text.encode()).hexdigest(), 16)


       class HashRing:
           def __init__(self, nodes=(), replicas=100):
               pass

           def add(self, node):
               pass

           def remove(self, node):
               pass

           def node_for(self, key):
               pass
       """,
       [("one node owns everything", """
         ring = HashRing(['a'])
         assert {ring.node_for('k%d' % i) for i in range(50)} == {'a'}
         """),
        ("an empty ring", raises("HashRing().node_for('k')", "LookupError")),
        ("order does not matter", """
         keys = ['user:%d' % i for i in range(300)]
         one, two = HashRing(['a', 'b', 'c']), HashRing(['c', 'a', 'b'])
         assert [one.node_for(k) for k in keys] == [two.node_for(k) for k in keys]
         """),
        ("adding moves keys only to the new node", """
         keys = ['user:%d' % i for i in range(1000)]
         ring = HashRing(['a', 'b', 'c'])
         before = {k: ring.node_for(k) for k in keys}
         ring.add('d')
         moved = {k for k in keys if ring.node_for(k) != before[k]}
         assert {ring.node_for(k) for k in moved} == {'d'}
         """),
        ("removing moves only that node's keys", """
         keys = ['user:%d' % i for i in range(1000)]
         ring = HashRing(['a', 'b', 'c'])
         before = {k: ring.node_for(k) for k in keys}
         ring.remove('b')
         moved = {k for k in keys if ring.node_for(k) != before[k]}
         assert moved == {k for k in keys if before[k] == 'b'}
         """),
        ("virtual nodes spread the load", """
         ring = HashRing(['a', 'b', 'c'])
         counts = {}
         for i in range(3000):
             owner = ring.node_for('user:%d' % i)
             counts[owner] = counts.get(owner, 0) + 1
         assert sorted(counts) == ['a', 'b', 'c']
         assert min(counts.values()) > 600
         """)],
       hints=["Keep every virtual point in one sorted list of positions, with "
              "a dict from position to node.",
              "`bisect.bisect_left(points, position(key))` finds the first "
              "point at or after the key; an index equal to `len(points)` "
              "wraps to 0."],
       solution="""
       import bisect
       import hashlib


       def position(text):
           return int(hashlib.md5(text.encode()).hexdigest(), 16)


       class HashRing:
           def __init__(self, nodes=(), replicas=100):
               self.replicas = replicas
               self._points = []
               self._owner = {}
               for node in nodes:
                   self.add(node)

           def add(self, node):
               for i in range(self.replicas):
                   point = position(f"{node}#{i}")
                   self._owner[point] = node
                   bisect.insort(self._points, point)

           def remove(self, node):
               for i in range(self.replicas):
                   point = position(f"{node}#{i}")
                   if self._owner.get(point) == node:
                       del self._owner[point]
                       self._points.remove(point)

           def node_for(self, key):
               if not self._points:
                   raise LookupError("the ring has no nodes")
               index = bisect.bisect_left(self._points, position(key))
               if index == len(self._points):
                   index = 0
               return self._owner[self._points[index]]
       """)


def _p16():
    ex("p16.001", "p16", "Binary data", "Unpack a binary header", 3,
       """
       A file format starts with a 12-byte header, all numbers little-endian:

       - bytes 0-3: the magic bytes `b'OPC1'`
       - bytes 4-5: `version`, an unsigned 16-bit integer
       - byte 6: `flags`, an unsigned 8-bit integer
       - byte 7: padding, ignored
       - bytes 8-11: `length`, an unsigned 32-bit integer

       Write `read_header(data)` returning `{'version': ..., 'flags': ...,
       'length': ...}`. Bytes after the header are the payload and are
       ignored. Raise `ValueError` when there are fewer than 12 bytes or the
       magic is wrong. Use the `struct` module.
       """,
       """
       def read_header(data):
           pass
       """,
       [("a header", r"""
         header = b'OPC1\x02\x00\x05\x00\x10\x00\x00\x00'
         assert read_header(header) == {'version': 2, 'flags': 5, 'length': 16}
         """),
        ("little-endian bytes", r"""
         header = b'OPC1\x02\x01\xff\x00\x00\x01\x00\x00'
         assert read_header(header) == {'version': 258, 'flags': 255, 'length': 256}
         """),
        ("the payload is ignored", r"""
         header = b'OPC1\x02\x00\x05\x00\x10\x00\x00\x00'
         assert read_header(header + b'payload') == {'version': 2, 'flags': 5, 'length': 16}
         """),
        ("too short", raises(r"read_header(b'OPC1\x02\x00\x05\x00\x10\x00\x00')")),
        ("wrong magic", raises(r"read_header(b'ELF!\x02\x00\x05\x00\x10\x00\x00\x00')"))],
       hints=["`struct` describes a layout with one format string: a byte "
              "order character, then one letter per field.",
              "`'<4sHBxI'` is little-endian: 4 bytes, unsigned short, unsigned "
              "char, one pad byte, unsigned int. `struct.unpack_from` ignores "
              "anything after the header."],
       solution="""
       import struct

       HEADER = struct.Struct("<4sHBxI")


       def read_header(data):
           if len(data) < HEADER.size:
               raise ValueError("a header is %d bytes, got %d" % (HEADER.size, len(data)))
           magic, version, flags, length = HEADER.unpack_from(data)
           if magic != b"OPC1":
               raise ValueError("wrong magic: %r" % magic)
           return {"version": version, "flags": flags, "length": length}
       """)

    ex("p16.002", "p16", "Memory", "Slice records without copying", 3,
       """
       Slicing `bytes` or a `bytearray` copies. Slicing a `memoryview` does
       not: it is a window onto the same memory.

       Write `split_records(buf, size)` returning a list of `memoryview`
       slices of `buf`, each `size` bytes long, in order. A trailing piece
       shorter than `size` is left out. Because nothing is copied, changing
       `buf` afterwards must show through the slices. Raise `ValueError` when
       `size` is below 1.
       """,
       """
       def split_records(buf, size):
           pass
       """,
       [("fixed-size records", """
         parts = split_records(bytearray(b'aaaabbbbcc'), 4)
         assert [bytes(p) for p in parts] == [b'aaaa', b'bbbb']
         """),
        ("an exact multiple", """
         parts = split_records(bytearray(b'abcdef'), 3)
         assert [bytes(p) for p in parts] == [b'abc', b'def']
         """),
        ("they are views", """
         parts = split_records(bytearray(b'abcdef'), 3)
         assert type(parts[0]).__name__ == 'memoryview'
         """),
        ("nothing was copied", """
         buf = bytearray(b'aaaabbbb')
         parts = split_records(buf, 4)
         buf[4:8] = b'ZZZZ'
         assert bytes(parts[1]) == b'ZZZZ', 'the slices must be views onto buf, not copies of it'
         """),
        ("an empty buffer", "assert split_records(bytearray(), 4) == []"),
        ("rejects a zero size", raises("split_records(bytearray(b'ab'), 0)"))],
       hints=["Make one `memoryview` of the whole buffer, then slice that, not "
              "the buffer.",
              "`view = memoryview(buf)`, then step `range(0, len(view) - size "
              "+ 1, size)` and take `view[i:i + size]`."],
       solution="""
       def split_records(buf, size):
           if size < 1:
               raise ValueError("size must be at least 1")
           view = memoryview(buf)
           return [view[i:i + size] for i in range(0, len(view) - size + 1, size)]
       """)

    ex("p16.003", "p16", "Buffers", "A byte ring that pushes back", 4,
       """
       Write `ByteRing(capacity)`, a fixed-size byte queue like a pipe's
       kernel buffer. Allocate one `bytearray(capacity)` in `__init__`, keep
       it in an attribute named `buffer`, and never replace it: the reads and
       writes wrap round inside it. Raise `ValueError` if `capacity` is
       below 1.

       - `write(data)` stores as many bytes of `data` as there is free room
         for and returns how many it took. It never overwrites unread bytes -
         a full ring takes 0, so the writer has to wait.
       - `read(n)` removes and returns up to `n` of the oldest bytes, as
         `bytes`. An empty ring returns `b''`.
       - `len(ring)` is the number of unread bytes.
       """,
       """
       class ByteRing:
           def __init__(self, capacity):
               pass

           def write(self, data):
               pass

           def read(self, n):
               pass

           def __len__(self):
               pass
       """,
       [("takes only what fits", "assert ByteRing(4).write(b'abcdef') == 4"),
        ("oldest bytes first", """
         ring = ByteRing(8)
         ring.write(b'abc')
         assert ring.read(2) == b'ab'
         """),
        ("wraps round", """
         ring = ByteRing(4)
         ring.write(b'abcd')
         ring.read(3)
         ring.write(b'xyz')
         assert ring.read(10) == b'dxyz'
         """),
        ("an empty read", "assert ByteRing(3).read(5) == b''"),
        ("counts unread bytes", """
         ring = ByteRing(4)
         ring.write(b'ab')
         ring.read(1)
         assert len(ring) == 1
         """),
        ("one buffer, reused", """
         ring = ByteRing(4)
         first = id(ring.buffer)
         for _ in range(3):
             ring.write(b'abc')
             ring.read(3)
         assert id(ring.buffer) == first, 'buffer must stay the one bytearray made in __init__'
         assert len(ring.buffer) == 4, 'buffer must stay capacity bytes long'
         """)],
       hints=["Track where the oldest unread byte is and how many unread bytes "
              "there are. Everything else follows from those two numbers.",
              "The next write goes at `(start + size) % capacity`; a read "
              "moves `start` forward with `% capacity` too."],
       solution="""
       class ByteRing:
           def __init__(self, capacity):
               if capacity < 1:
                   raise ValueError("capacity must be at least 1")
               self.buffer = bytearray(capacity)
               self._start = 0
               self._size = 0

           def __len__(self):
               return self._size

           def write(self, data):
               capacity = len(self.buffer)
               count = min(len(data), capacity - self._size)
               for i in range(count):
                   self.buffer[(self._start + self._size + i) % capacity] = data[i]
               self._size += count
               return count

           def read(self, n):
               capacity = len(self.buffer)
               count = min(n, self._size)
               out = bytes(self.buffer[(self._start + i) % capacity] for i in range(count))
               self._start = (self._start + count) % capacity
               self._size -= count
               return out
       """)


def _p17():
    ex("p17.001", "p17", "Data quality", "Typed rows with their errors", 3,
       """
       Write `load_rows(lines)` for CSV text given as a list of lines. Line 1
       is the header `id,name,amount`. Read it with the `csv` module, so a
       quoted field may contain a comma.

       Return `(rows, errors)`. Each good line becomes
       `{'id': int, 'name': str, 'amount': float}`, with the name stripped.
       A bad line is left out of `rows` and adds one `(line_number, field)`
       tuple to `errors`, naming the first field that failed in the order
       id, name, amount. A line with the wrong number of fields reports the
       field `'columns'`. A name that is empty after stripping fails. Blank
       lines are skipped but still counted. Line numbers count from 1, with
       the header as line 1. No lines at all gives `([], [])`.
       """,
       """
       def load_rows(lines):
           pass
       """,
       [("good rows", """
         lines = ['id,name,amount', '1,Ada,10.5', '2, Grace ,3']
         assert load_rows(lines) == ([{'id': 1, 'name': 'Ada', 'amount': 10.5},
                                      {'id': 2, 'name': 'Grace', 'amount': 3.0}], [])
         """),
        ("every error is kept", """
         lines = ['id,name,amount', 'x,Ada,1', '2,,1', '3,Bob,lots', '4,Cy,2']
         assert load_rows(lines)[1] == [(2, 'id'), (3, 'name'), (4, 'amount')]
         """),
        ("bad rows are left out", """
         lines = ['id,name,amount', 'x,Ada,1', '2,,1', '3,Bob,lots', '4,Cy,2']
         assert load_rows(lines)[0] == [{'id': 4, 'name': 'Cy', 'amount': 2.0}]
         """),
        ("quoted commas and wrong widths", """
         lines = ['id,name,amount', '5,"Hopper, G",7.25', '6,Too,1,extra', '7,Few']
         assert load_rows(lines) == ([{'id': 5, 'name': 'Hopper, G', 'amount': 7.25}],
                                     [(3, 'columns'), (4, 'columns')])
         """),
        ("blank lines still count", """
         lines = ['id,name,amount', '', '8,Eve,1', 'bad']
         assert load_rows(lines)[1] == [(4, 'columns')]
         """),
        ("nothing to read", "assert load_rows([]) == ([], [])\n"
                            "assert load_rows(['id,name,amount']) == ([], [])")],
       hints=["`csv.reader(lines)` accepts a list of strings and gives you each "
              "line as a list of fields; a blank line comes back as `[]`.",
              "Number the records with `enumerate(reader, 1)`, skip the first, "
              "and convert one field at a time inside its own `try`, so you "
              "know which one failed."],
       solution="""
       import csv


       def load_rows(lines):
           rows, errors = [], []
           for number, fields in enumerate(csv.reader(lines), 1):
               if number == 1 or not fields:
                   continue
               if len(fields) != 3:
                   errors.append((number, "columns"))
                   continue
               raw_id, raw_name, raw_amount = fields
               try:
                   row_id = int(raw_id)
               except ValueError:
                   errors.append((number, "id"))
                   continue
               name = raw_name.strip()
               if not name:
                   errors.append((number, "name"))
                   continue
               try:
                   amount = float(raw_amount)
               except ValueError:
                   errors.append((number, "amount"))
                   continue
               rows.append({"id": row_id, "name": name, "amount": amount})
           return rows, errors
       """)

    ex("p17.002", "p17", "Idempotency", "An upsert you can run twice", 3,
       """
       Write `upsert(table, incoming)`. Both are lists of dicts, and every
       dict has an `'id'`.

       Return a new list: for each incoming row, if a row with that id
       exists, merge the incoming fields into it (incoming values win, other
       fields are kept); otherwise append a copy. Existing rows keep their
       order and new rows follow in the order they arrived. If `incoming`
       repeats an id, the later row wins.

       Do not change `table` or the dicts inside it. Running the same upsert
       twice must give the same result as running it once. Raise
       `ValueError` for an incoming row with no `'id'`.
       """,
       """
       def upsert(table, incoming):
           pass
       """,
       [("updates merge fields", """
         table = [{'id': 1, 'name': 'a', 'n': 1}, {'id': 2, 'name': 'b', 'n': 2}]
         assert upsert(table, [{'id': 2, 'n': 5}]) == [{'id': 1, 'name': 'a', 'n': 1},
                                                      {'id': 2, 'name': 'b', 'n': 5}]
         """),
        ("inserts append", """
         table = [{'id': 1, 'name': 'a'}]
         assert upsert(table, [{'id': 3, 'name': 'c'}, {'id': 2, 'name': 'b'}]) == [
             {'id': 1, 'name': 'a'}, {'id': 3, 'name': 'c'}, {'id': 2, 'name': 'b'}]
         """),
        ("running it twice changes nothing", """
         table = [{'id': 1, 'n': 1}]
         batch = [{'id': 1, 'n': 2}, {'id': 9, 'n': 0}]
         once = upsert(table, batch)
         assert upsert(once, batch) == once
         """),
        ("the input is untouched", """
         import copy
         table = [{'id': 1, 'n': 1}]
         before = copy.deepcopy(table)
         upsert(table, [{'id': 1, 'n': 99}, {'id': 2, 'n': 2}])
         assert table == before
         """),
        ("the later duplicate wins", """
         assert upsert([], [{'id': 1, 'v': 1}, {'id': 1, 'v': 2}]) == [{'id': 1, 'v': 2}]
         """),
        ("rejects a row with no id", raises("upsert([], [{'name': 'x'}])"))],
       hints=["Copy each existing row before you change anything, and keep an "
              "index from id to position so you are not searching the list "
              "each time.",
              "`out = [dict(r) for r in table]` and `where = {r['id']: i for "
              "i, r in enumerate(out)}`; then `out[where[key]].update(row)` or "
              "append and record the new position."],
       solution="""
       def upsert(table, incoming):
           out = [dict(row) for row in table]
           where = {row["id"]: i for i, row in enumerate(out)}
           for row in incoming:
               if "id" not in row:
                   raise ValueError("every row needs an id: %r" % (row,))
               key = row["id"]
               if key in where:
                   out[where[key]].update(row)
               else:
                   where[key] = len(out)
                   out.append(dict(row))
           return out
       """)

    ex("p17.003", "p17", "Batch processing", "Aggregate in chunks", 4,
       """
       Data too big for memory is processed a chunk at a time. `rows` is any
       iterable of `(key, amount)` pairs, possibly a generator that can only
       be read once.

       Write `chunk_totals(rows, size)`, a generator that reads `size` rows at
       a time and yields one dict of `key -> sum of amounts` for each chunk.
       It must be lazy: taking the first chunk must read only the first
       `size` rows. The last chunk may be shorter.

       Write `grand_total(rows, size)` returning one dict of totals for all
       rows, built by merging the chunk dicts. Both raise `ValueError` when
       `size` is below 1 (for the generator, when it is first advanced).
       """,
       """
       def chunk_totals(rows, size):
           pass


       def grand_total(rows, size):
           pass
       """,
       [("one dict per chunk", """
         rows = [('a', 1), ('b', 2), ('a', 3), ('c', 4), ('a', 5)]
         assert list(chunk_totals(rows, 2)) == [{'a': 1, 'b': 2}, {'a': 3, 'c': 4}, {'a': 5}]
         """),
        ("grand totals", """
         rows = [('a', 1), ('b', 2), ('a', 3), ('c', 4), ('a', 5)]
         assert grand_total(rows, 2) == {'a': 9, 'b': 2, 'c': 4}
         """),
        ("a generator read once", """
         rows = [('a', 1), ('b', 2), ('a', 3), ('c', 4), ('a', 5)]
         assert grand_total(iter(rows), 4) == {'a': 9, 'b': 2, 'c': 4}
         """),
        ("it is lazy", """
         pulled = [0]
         def source():
             for _ in range(100_000):
                 pulled[0] += 1
                 yield ('k', 1)
         assert next(chunk_totals(source(), 3)) == {'k': 3}
         assert pulled[0] == 3, 'the first chunk should read 3 rows, not the whole input'
         """),
        ("no rows", "assert list(chunk_totals([], 3)) == []\n"
                    "assert grand_total([], 3) == {}"),
        ("rejects a zero size", raises("grand_total([('a', 1)], 0)"))],
       hints=["Take rows from one iterator in slices rather than looping over "
              "the whole input first. The standard library has a tool that "
              "hands you `size` items at a time.",
              "`it = iter(rows)`, then `chunk = list(itertools.islice(it, size))` "
              "until it comes back empty. (On Python 3.12+ `itertools.batched` "
              "does the same.) `grand_total` adds each chunk's values into one "
              "dict."],
       solution="""
       import itertools


       def chunk_totals(rows, size):
           if size < 1:
               raise ValueError("size must be at least 1")
           # itertools.batched does this on 3.12+; islice works on 3.11 too.
           it = iter(rows)
           while chunk := list(itertools.islice(it, size)):
               totals = {}
               for key, amount in chunk:
                   totals[key] = totals.get(key, 0) + amount
               yield totals


       def grand_total(rows, size):
           merged = {}
           for totals in chunk_totals(rows, size):
               for key, amount in totals.items():
                   merged[key] = merged.get(key, 0) + amount
           return merged
       """)

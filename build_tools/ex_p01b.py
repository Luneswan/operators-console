"""Phase 01 - part B: functions, errors, files, standard library."""
from ex_lib import ex


def build():
    ex("p01.019", "p01", "Sorting", "Top N by value", 3,
       """
       Write `top_n(scores, n)` where `scores` is a dict mapping names to
       numbers. Return a list of the `n` names with the highest scores,
       highest first. Break ties alphabetically by name.
       """,
       """
       def top_n(scores, n):
           pass
       """,
       [("picks the best two",
         "assert top_n({'a': 3, 'b': 9, 'c': 5}, 2) == ['b', 'c']"),
        ("ties are alphabetical",
         "assert top_n({'b': 5, 'a': 5}, 2) == ['a', 'b']"),
        ("n larger than the dict",
         "assert top_n({'a': 1}, 5) == ['a']"),
        ("n of zero", "assert top_n({'a': 1}, 0) == []")],
       hints=["Sort by a tuple key: negative score first, then the name.",
              "Slicing past the end of a list is safe - it just gives you what is there."],
       solution="""
       def top_n(scores, n):
           ordered = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
           return [name for name, _score in ordered[:n]]
       """)

    ex("p01.020", "p01", "Iteration", "Positions of a value", 2,
       """
       Write `positions(items, target)` returning a list of every index where
       `target` appears. Use `enumerate` rather than counting by hand.
       """,
       """
       def positions(items, target):
           pass
       """,
       [("several hits", "assert positions(['a', 'b', 'a'], 'a') == [0, 2]"),
        ("no hits", "assert positions([1, 2], 9) == []"),
        ("numbers", "assert positions([0, 0, 1], 0) == [0, 1]"),
        ("empty input", "assert positions([], 'x') == []")],
       solution="""
       def positions(items, target):
           return [i for i, item in enumerate(items) if item == target]
       """)

    ex("p01.021", "p01", "Iteration", "Pair two lists up", 2,
       """
       Write `pair_up(names, scores)` returning a dict built from two parallel
       lists. If one list is longer, ignore the extra entries.
       """,
       """
       def pair_up(names, scores):
           pass
       """,
       [("equal lengths",
         "assert pair_up(['a', 'b'], [1, 2]) == {'a': 1, 'b': 2}"),
        ("extra names ignored",
         "assert pair_up(['a', 'b', 'c'], [1, 2]) == {'a': 1, 'b': 2}"),
        ("empty", "assert pair_up([], []) == {}")],
       hints=["zip stops at the shorter of its inputs, which is exactly what you want here.",
              "dict() accepts an iterable of pairs."],
       solution="""
       def pair_up(names, scores):
           return dict(zip(names, scores))
       """)

    ex("p01.022", "p01", "Nested data", "Total by category", 3,
       """
       Given a list of dicts like
       `{"category": "food", "amount": 12.5}`, write `totals(rows)` returning a
       dict mapping each category to the sum of its amounts.
       """,
       """
       def totals(rows):
           pass
       """,
       [("groups and sums",
         "rows = [{'category': 'food', 'amount': 10}, {'category': 'rent', 'amount': 500}, {'category': 'food', 'amount': 5}]\nassert totals(rows) == {'food': 15, 'rent': 500}"),
        ("empty", "assert totals([]) == {}"),
        ("single row",
         "assert totals([{'category': 'x', 'amount': 1.5}]) == {'x': 1.5}")],
       hints=["Reach for dict.get(key, 0) again, or collections.defaultdict(float)."],
       solution="""
       def totals(rows):
           out = {}
           for row in rows:
               key = row["category"]
               out[key] = out.get(key, 0) + row["amount"]
           return out
       """)

    ex("p01.023", "p01", "Functions", "The mutable default trap", 4,
       """
       This function is broken. Every call shares the same list, so results
       leak between calls:

           def add_item(item, basket=[]):
               basket.append(item)
               return basket

       Fix `add_item` so that calling it with no basket always starts a fresh
       one, while still allowing a caller to pass their own list in.
       """,
       """
       def add_item(item, basket=None):
           pass
       """,
       [("fresh list every call",
         "assert add_item('a') == ['a']\nassert add_item('b') == ['b']"),
        ("accepts a caller's list",
         "mine = ['x']\nassert add_item('y', mine) == ['x', 'y']\nassert mine == ['x', 'y']"),
        ("no mutable default",
         "import inspect\nsig = inspect.signature(add_item)\nassert sig.parameters['basket'].default is None")],
       hints=["Default arguments are evaluated once, when the function is defined.",
              "Use None as a sentinel and build the real default inside the body."],
       solution="""
       def add_item(item, basket=None):
           if basket is None:
               basket = []
           basket.append(item)
           return basket
       """)

    ex("p01.024", "p01", "Functions", "Flexible arguments", 3,
       """
       Write `describe(*values, **options)` returning a string of the form
       `"3 values | sep=- upper=True"`.

       The count comes first, then a pipe with spaces around it, then each
       keyword option as `key=value`, sorted by key and separated by single
       spaces. With no options, return just `"3 values"`.
       """,
       """
       def describe(*values, **options):
           pass
       """,
       [("values only", "assert describe(1, 2, 3) == '3 values'"),
        ("with options",
         "assert describe(1, 2, 3, sep='-', upper=True) == '3 values | sep=- upper=True'"),
        ("no values at all", "assert describe() == '0 values'"),
        ("options are sorted",
         "assert describe(1, b=2, a=1) == '1 values | a=1 b=2'")],
       solution="""
       def describe(*values, **options):
           head = f"{len(values)} values"
           if not options:
               return head
           tail = " ".join(f"{k}={options[k]}" for k in sorted(options))
           return f"{head} | {tail}"
       """)

    ex("p01.025", "p01", "Recursion", "Factorial", 2,
       """
       Write `factorial(n)` recursively. `factorial(0)` is 1.
       Raise `ValueError` for negative input.
       """,
       """
       def factorial(n):
           pass
       """,
       [("zero", "assert factorial(0) == 1"),
        ("five", "assert factorial(5) == 120"),
        ("ten", "assert factorial(10) == 3628800"),
        ("rejects negatives",
         "try:\n    factorial(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('should raise ValueError')")],
       hints=["Write the base case first, then the recursive step.",
              "Without a base case you get a RecursionError, not a wrong answer."],
       solution="""
       def factorial(n):
           if n < 0:
               raise ValueError("factorial is undefined for negative numbers")
           if n <= 1:
               return 1
           return n * factorial(n - 1)
       """)

    ex("p01.026", "p01", "Exceptions", "Divide without crashing", 2,
       """
       Write `safe_div(a, b)` returning `a / b`, or `None` when `b` is zero.
       Catch the exception rather than testing for zero first, so you see how
       `try` reads.
       """,
       """
       def safe_div(a, b):
           pass
       """,
       [("normal division", "assert safe_div(10, 4) == 2.5"),
        ("division by zero", "assert safe_div(1, 0) is None"),
        ("zero numerator", "assert safe_div(0, 5) == 0"),
        ("uses try",
         "import inspect; assert 'try' in inspect.getsource(safe_div)")],
       hints=["Catch ZeroDivisionError specifically. A bare `except:` would swallow real bugs."],
       solution="""
       def safe_div(a, b):
           try:
               return a / b
           except ZeroDivisionError:
               return None
       """)

    ex("p01.027", "p01", "Exceptions", "Validate before you trust", 3,
       """
       Write `validate_age(value)` returning the age as an `int`.

       Raise `TypeError` if the value is not a string or a number.
       Raise `ValueError` if it cannot be read as a whole number, or is
       outside 0 to 130.
       """,
       """
       def validate_age(value):
           pass
       """,
       [("int passes through", "assert validate_age(30) == 30"),
        ("numeric string", "assert validate_age('42') == 42"),
        ("rejects nonsense",
         "try:\n    validate_age('old')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects out of range",
         "try:\n    validate_age(500)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects wrong type",
         "try:\n    validate_age([1])\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError('expected TypeError')")],
       hints=["int('old') raises ValueError; int([1]) raises TypeError.",
              "Check the type first, then the conversion, then the range."],
       solution="""
       def validate_age(value):
           if not isinstance(value, (str, int, float)) or isinstance(value, bool):
               raise TypeError("age must be a string or a number")
           try:
               age = int(value)
           except (TypeError, ValueError):
               raise ValueError("age must be a whole number")
           if not 0 <= age <= 130:
               raise ValueError("age must be between 0 and 130")
           return age
       """)

    ex("p01.028", "p01", "Exceptions", "Parse the numbers you can", 3,
       """
       Write `parse_ints(values)` returning a list of the entries that convert
       cleanly to `int`, skipping the ones that do not.

       `parse_ints(["1", "x", "3"])` returns `[1, 3]`.
       """,
       """
       def parse_ints(values):
           pass
       """,
       [("skips the bad ones",
         "assert parse_ints(['1', 'x', '3']) == [1, 3]"),
        ("all good", "assert parse_ints(['5', '6']) == [5, 6]"),
        ("all bad", "assert parse_ints(['a', 'b']) == []"),
        ("handles None entries", "assert parse_ints(['1', None]) == [1]"),
        ("empty", "assert parse_ints([]) == []")],
       hints=["Put the try inside the loop, around only the one line that can fail.",
              "None raises TypeError, not ValueError - catch both."],
       solution="""
       def parse_ints(values):
           out = []
           for value in values:
               try:
                   out.append(int(value))
               except (TypeError, ValueError):
                   continue
           return out
       """)

    ex("p01.029", "p01", "Files", "Count the non-empty lines", 3,
       """
       A file named `notes.txt` already exists in the working directory.
       Write `count_lines(path)` returning how many lines in it contain
       something other than whitespace.
       """,
       """
       def count_lines(path):
           pass
       """,
       [("counts the real lines", "assert count_lines('notes.txt') == 3"),
        ("uses a with block",
         "import inspect; assert 'with ' in inspect.getsource(count_lines)")],
       setup="""
       LINES = ["first", "", "  ", "second", "third"]
       with open("notes.txt", "w", encoding="utf-8") as fh:
           fh.write(chr(10).join(LINES) + chr(10))
       """,
       hints=["`with open(path) as fh:` closes the file even if something raises.",
              "A line of only spaces is not empty until you strip it."],
       solution="""
       def count_lines(path):
           total = 0
           with open(path, encoding="utf-8") as fh:
               for line in fh:
                   if line.strip():
                       total += 1
           return total
       """)

    ex("p01.030", "p01", "Files", "Round-trip through JSON", 3,
       """
       Write `save(path, data)` and `load(path)` that write a dict to a file as
       JSON and read it back. The value that comes back must equal the value
       that went in.
       """,
       """
       import json


       def save(path, data):
           pass


       def load(path):
           pass
       """,
       [("round trips",
         "payload = {'name': 'ada', 'years': [1815, 1852], 'ok': True}\nsave('out.json', payload)\nassert load('out.json') == payload"),
        ("really writes a file",
         "import os\nsave('check.json', {'a': 1})\nassert os.path.getsize('check.json') > 0"),
        ("writes valid json",
         "import json\nsave('valid.json', {'a': [1, 2]})\nassert json.load(open('valid.json', encoding='utf-8')) == {'a': [1, 2]}")],
       hints=["json.dump writes to a file object; json.dumps returns a string.",
              "Always pass encoding='utf-8' so the code behaves the same on every platform."],
       solution="""
       import json


       def save(path, data):
           with open(path, "w", encoding="utf-8") as fh:
               json.dump(data, fh)


       def load(path):
           with open(path, encoding="utf-8") as fh:
               return json.load(fh)
       """)

    ex("p01.031", "p01", "Standard library", "Days between two dates", 3,
       """
       Write `days_between(a, b)` taking two `YYYY-MM-DD` strings and returning
       the whole number of days between them. The result is never negative.
       """,
       """
       from datetime import date


       def days_between(a, b):
           pass
       """,
       [("forwards", "assert days_between('2026-01-01', '2026-01-31') == 30"),
        ("backwards is the same",
         "assert days_between('2026-01-31', '2026-01-01') == 30"),
        ("same day", "assert days_between('2026-05-05', '2026-05-05') == 0"),
        ("across a leap day",
         "assert days_between('2024-02-28', '2024-03-01') == 2")],
       hints=["date.fromisoformat parses the string for you.",
              "Subtracting two dates gives a timedelta; .days is the whole-day part."],
       solution="""
       from datetime import date


       def days_between(a, b):
           first = date.fromisoformat(a)
           second = date.fromisoformat(b)
           return abs((second - first).days)
       """)

    ex("p01.032", "p01", "Standard library", "Most common letter", 3,
       """
       Write `most_common_letter(text)` returning the letter that appears most
       often, ignoring case and anything that is not a letter.

       Ties are broken alphabetically. An input with no letters returns `None`.
       """,
       """
       from collections import Counter


       def most_common_letter(text):
           pass
       """,
       [("plain", "assert most_common_letter('aabbbc') == 'b'"),
        ("ignores case", "assert most_common_letter('AaB') == 'a'"),
        ("ignores punctuation", "assert most_common_letter('!!!zz!') == 'z'"),
        ("ties go alphabetical", "assert most_common_letter('ba') == 'a'"),
        ("no letters", "assert most_common_letter('123 !') is None")],
       hints=["str.isalpha() tells you whether a character is a letter.",
              "Counter.most_common does not break ties for you - sort by (-count, letter)."],
       solution="""
       from collections import Counter


       def most_common_letter(text):
           counts = Counter(ch for ch in text.lower() if ch.isalpha())
           if not counts:
               return None
           return min(counts, key=lambda ch: (-counts[ch], ch))
       """)

    ex("p01.033", "p01", "Built-ins", "any and all", 2,
       """
       Write two functions:

       `all_positive(numbers)` - True when every number is greater than zero.
       An empty list counts as True.

       `has_negative(numbers)` - True when at least one number is below zero.
       """,
       """
       def all_positive(numbers):
           pass


       def has_negative(numbers):
           pass
       """,
       [("all positive", "assert all_positive([1, 2, 3]) is True"),
        ("one zero fails", "assert all_positive([1, 0]) is False"),
        ("empty is vacuously true", "assert all_positive([]) is True"),
        ("finds a negative", "assert has_negative([1, -2]) is True"),
        ("none present", "assert has_negative([1, 2]) is False")],
       hints=["all() and any() short-circuit, so they stop at the first decisive value."],
       solution="""
       def all_positive(numbers):
           return all(n > 0 for n in numbers)


       def has_negative(numbers):
           return any(n < 0 for n in numbers)
       """)

    ex("p01.034", "p01", "Strings", "Palindrome check", 3,
       """
       Write `is_palindrome(text)` ignoring case, spaces and punctuation.

       `"A man, a plan, a canal: Panama"` is a palindrome.
       """,
       """
       def is_palindrome(text):
           pass
       """,
       [("classic",
         "assert is_palindrome('A man, a plan, a canal: Panama') is True"),
        ("not one", "assert is_palindrome('hello') is False"),
        ("empty is trivially one", "assert is_palindrome('') is True"),
        ("single character", "assert is_palindrome('x') is True"),
        ("digits count", "assert is_palindrome('12321') is True")],
       hints=["Build a cleaned string of only alphanumeric characters, lowercased.",
              "text[::-1] reverses a string."],
       solution="""
       def is_palindrome(text):
           cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
           return cleaned == cleaned[::-1]
       """)

    ex("p01.035", "p01", "Dictionaries", "Invert a mapping", 2,
       """
       Write `invert(mapping)` returning a new dict with keys and values
       swapped. If two keys share a value, the last one seen wins.
       """,
       """
       def invert(mapping):
           pass
       """,
       [("simple", "assert invert({'a': 1, 'b': 2}) == {1: 'a', 2: 'b'}"),
        ("last wins", "assert invert({'a': 1, 'b': 1}) == {1: 'b'}"),
        ("empty", "assert invert({}) == {}"),
        ("original untouched",
         "src = {'a': 1}\ninvert(src)\nassert src == {'a': 1}")],
       hints=["A dict comprehension reads {value: key for key, value in mapping.items()}."],
       solution="""
       def invert(mapping):
           return {value: key for key, value in mapping.items()}
       """)

    ex("p01.036", "p01", "Loops", "Running totals", 3,
       """
       Write `running_total(numbers)` returning a list where each position
       holds the sum of everything up to and including it.

       `[1, 2, 3]` becomes `[1, 3, 6]`.
       """,
       """
       def running_total(numbers):
           pass
       """,
       [("basic", "assert running_total([1, 2, 3]) == [1, 3, 6]"),
        ("negatives", "assert running_total([5, -5, 2]) == [5, 0, 2]"),
        ("empty", "assert running_total([]) == []"),
        ("single", "assert running_total([9]) == [9]")],
       hints=["Keep one accumulator outside the loop and append after each update.",
              "itertools.accumulate does this too - compare once yours works."],
       solution="""
       def running_total(numbers):
           out = []
           total = 0
           for number in numbers:
               total += number
               out.append(total)
           return out
       """)

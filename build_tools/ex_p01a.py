"""Phase 01 - Python foundations, part A: values, strings, conditionals."""
from ex_lib import ex


def build():
    ex("p01.001", "p01", "Values and printing", "Say hello", 1,
       """
       Write a function `greet(name)` that returns the string
       `Hello, <name>!` - so `greet("Ada")` returns `Hello, Ada!`.

       Return the string. Do not print it. Returning and printing are
       different things, and almost everything you write from here on
       returns.
       """,
       """
       def greet(name):
           # return the greeting instead of printing it
           pass
       """,
       [("greets Ada", "assert greet('Ada') == 'Hello, Ada!'"),
        ("greets Linus", "assert greet('Linus') == 'Hello, Linus!'"),
        ("handles an empty name", "assert greet('') == 'Hello, !'")],
       hints=["An f-string is the shortest route: f\"Hello, {name}!\"",
              "`return` hands a value back to the caller; `print` only writes to the screen."],
       solution="""
       def greet(name):
           return f"Hello, {name}!"
       """)

    ex("p01.002", "p01", "Arithmetic", "Celsius to Fahrenheit", 1,
       """
       Write `to_fahrenheit(celsius)` returning the temperature in
       Fahrenheit. The formula is `F = C x 9/5 + 32`.

       Return a float. 100 degrees Celsius is 212.0 Fahrenheit.
       """,
       """
       def to_fahrenheit(celsius):
           pass
       """,
       [("freezing", "assert to_fahrenheit(0) == 32"),
        ("boiling", "assert to_fahrenheit(100) == 212"),
        ("negative", "assert to_fahrenheit(-40) == -40"),
        ("fractions survive", "assert abs(to_fahrenheit(36.6) - 97.88) < 1e-9")],
       hints=["Use `9 / 5`, not `9 // 5`. Integer division would throw away the fraction."],
       solution="""
       def to_fahrenheit(celsius):
           return celsius * 9 / 5 + 32
       """)

    ex("p01.003", "p01", "Arithmetic", "Split seconds into h:m:s", 2,
       """
       Write `hms(total_seconds)` that turns a whole number of seconds into a
       tuple `(hours, minutes, seconds)`.

       `hms(3661)` is `(1, 1, 1)`. Every part must be a whole number.
       """,
       """
       def hms(total_seconds):
           pass
       """,
       [("one hour one minute one second", "assert hms(3661) == (1, 1, 1)"),
        ("under a minute", "assert hms(45) == (0, 0, 45)"),
        ("exact hours", "assert hms(7200) == (2, 0, 0)"),
        ("zero", "assert hms(0) == (0, 0, 0)"),
        ("all parts are ints",
         "assert all(isinstance(p, int) for p in hms(3661))")],
       hints=["`//` divides and throws away the remainder; `%` keeps only the remainder.",
              "divmod(a, b) gives you both at once."],
       solution="""
       def hms(total_seconds):
           minutes, seconds = divmod(total_seconds, 60)
           hours, minutes = divmod(minutes, 60)
           return hours, minutes, seconds
       """)

    ex("p01.004", "p01", "Strings", "Initials", 2,
       """
       Write `initials(full_name)` returning the uppercase initials of every
       word, separated by dots and ending with one.

       `initials("ada lovelace")` returns `"A.L."`.
       Extra spaces between words must not produce empty initials.
       """,
       """
       def initials(full_name):
           pass
       """,
       [("two names", "assert initials('ada lovelace') == 'A.L.'"),
        ("already capitalised", "assert initials('Grace Hopper') == 'G.H.'"),
        ("three names", "assert initials('john von neumann') == 'J.V.N.'"),
        ("collapses extra spaces", "assert initials('  ada   lovelace ') == 'A.L.'"),
        ("empty string", "assert initials('') == ''")],
       hints=["`text.split()` with no argument splits on any run of whitespace and drops empties.",
              "Build the pieces in a list, then `''.join(...)` them."],
       solution="""
       def initials(full_name):
           return "".join(word[0].upper() + "." for word in full_name.split())
       """)

    ex("p01.005", "p01", "Strings", "Format a price", 2,
       """
       Write `price(amount)` returning the amount as a string with a leading
       dollar sign, a thousands separator and exactly two decimals.

       `price(1234.5)` returns `"$1,234.50"`.
       """,
       """
       def price(amount):
           pass
       """,
       [("thousands", "assert price(1234.5) == '$1,234.50'"),
        ("small", "assert price(7) == '$7.00'"),
        ("millions", "assert price(1234567.891) == '$1,234,567.89'"),
        ("zero", "assert price(0) == '$0.00'")],
       hints=["Format specs compose: f\"{amount:,.2f}\" adds separators and fixes the decimals."],
       solution="""
       def price(amount):
           return f"${amount:,.2f}"
       """)

    ex("p01.006", "p01", "Conditionals", "Letter grade", 2,
       """
       Write `grade(score)` mapping a 0-100 score to a letter:
       90 and above `A`, 80-89 `B`, 70-79 `C`, 60-69 `D`, below 60 `F`.

       A score outside 0-100 must raise `ValueError`.
       """,
       """
       def grade(score):
           pass
       """,
       [("A", "assert grade(95) == 'A'"),
        ("boundary 90", "assert grade(90) == 'A'"),
        ("B", "assert grade(83) == 'B'"),
        ("boundary 60", "assert grade(60) == 'D'"),
        ("F", "assert grade(0) == 'F'"),
        ("rejects over 100",
         "try:\n    grade(101)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('should raise ValueError')"),
        ("rejects negative",
         "try:\n    grade(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('should raise ValueError')")],
       hints=["Check the invalid range first and raise, then the happy path reads top to bottom.",
              "Order your comparisons from highest to lowest so each `elif` only needs one bound."],
       solution="""
       def grade(score):
           if not 0 <= score <= 100:
               raise ValueError("score must be between 0 and 100")
           if score >= 90:
               return "A"
           if score >= 80:
               return "B"
           if score >= 70:
               return "C"
           if score >= 60:
               return "D"
           return "F"
       """)

    ex("p01.007", "p01", "Conditionals", "Leap years", 2,
       """
       Write `is_leap(year)` returning True for leap years in the Gregorian
       calendar.

       A year is a leap year if it is divisible by 4, except centuries, which
       must also be divisible by 400. 1900 was not a leap year. 2000 was.
       """,
       """
       def is_leap(year):
           pass
       """,
       [("ordinary leap year", "assert is_leap(2024) is True"),
        ("ordinary year", "assert is_leap(2023) is False"),
        ("century that is not", "assert is_leap(1900) is False"),
        ("century that is", "assert is_leap(2000) is True"),
        ("returns a real bool",
         "assert isinstance(is_leap(2024), bool)")],
       hints=["The whole rule fits in one boolean expression.",
              "Write it as: divisible by 4 AND (not divisible by 100 OR divisible by 400)."],
       solution="""
       def is_leap(year):
           return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
       """)

    ex("p01.008", "p01", "Loops", "Sum up to n", 1,
       """
       Write `sum_to(n)` returning the sum of every whole number from 1 to `n`
       inclusive. `sum_to(5)` is 15. `sum_to(0)` is 0.

       Write the loop yourself this time, even though a formula exists.
       """,
       """
       def sum_to(n):
           pass
       """,
       [("small", "assert sum_to(5) == 15"),
        ("one", "assert sum_to(1) == 1"),
        ("zero", "assert sum_to(0) == 0"),
        ("large", "assert sum_to(1000) == 500500")],
       hints=["`range(1, n + 1)` stops *before* the second argument, so add one.",
              "Start an accumulator at 0 before the loop, not inside it."],
       solution="""
       def sum_to(n):
           total = 0
           for value in range(1, n + 1):
               total += value
           return total
       """)

    ex("p01.009", "p01", "Loops", "FizzBuzz as a list", 2,
       """
       Write `fizzbuzz(n)` returning a list of length `n`. For each position
       from 1 to n: multiples of 15 become `"FizzBuzz"`, multiples of 3 become
       `"Fizz"`, multiples of 5 become `"Buzz"`, everything else is the number
       itself as an `int`.
       """,
       """
       def fizzbuzz(n):
           pass
       """,
       [("first five", "assert fizzbuzz(5) == [1, 2, 'Fizz', 4, 'Buzz']"),
        ("hits fifteen", "assert fizzbuzz(15)[14] == 'FizzBuzz'"),
        ("length", "assert len(fizzbuzz(100)) == 100"),
        ("numbers stay ints", "assert fizzbuzz(2) == [1, 2]"),
        ("zero length", "assert fizzbuzz(0) == []")],
       hints=["Test for 15 first. If you test 3 first, no number ever reaches the FizzBuzz branch."],
       solution="""
       def fizzbuzz(n):
           out = []
           for value in range(1, n + 1):
               if value % 15 == 0:
                   out.append("FizzBuzz")
               elif value % 3 == 0:
                   out.append("Fizz")
               elif value % 5 == 0:
                   out.append("Buzz")
               else:
                   out.append(value)
           return out
       """)

    ex("p01.010", "p01", "Lists", "Second largest", 3,
       """
       Write `second_largest(numbers)` returning the second largest *distinct*
       value in the list.

       `[5, 1, 5, 3]` gives 3, because both fives are the same value.
       If there is no second distinct value, return `None`.
       """,
       """
       def second_largest(numbers):
           pass
       """,
       [("plain case", "assert second_largest([1, 7, 3, 9]) == 7"),
        ("ignores duplicates", "assert second_largest([5, 1, 5, 3]) == 3"),
        ("all identical", "assert second_largest([4, 4, 4]) is None"),
        ("single value", "assert second_largest([2]) is None"),
        ("empty", "assert second_largest([]) is None"),
        ("negatives", "assert second_largest([-1, -5, -3]) == -3")],
       hints=["`set(numbers)` removes duplicates in one step.",
              "Sort the distinct values, then index from the end - but check the length first."],
       solution="""
       def second_largest(numbers):
           distinct = sorted(set(numbers))
           if len(distinct) < 2:
               return None
           return distinct[-2]
       """)

    ex("p01.011", "p01", "Comprehensions", "Squares of the even numbers", 2,
       """
       Write `even_squares(numbers)` returning a list containing the square of
       every even number in the input, in the original order.

       Use a single list comprehension.
       """,
       """
       def even_squares(numbers):
           pass
       """,
       [("mixed", "assert even_squares([1, 2, 3, 4]) == [4, 16]"),
        ("nothing even", "assert even_squares([1, 3, 5]) == []"),
        ("negatives count", "assert even_squares([-2, -3]) == [4]"),
        ("order preserved", "assert even_squares([4, 2]) == [16, 4]"),
        ("is a list", "assert isinstance(even_squares([2]), list)")],
       hints=["The shape is [expression for item in iterable if condition]."],
       solution="""
       def even_squares(numbers):
           return [n * n for n in numbers if n % 2 == 0]
       """)

    ex("p01.012", "p01", "Slicing", "Middle three characters", 3,
       """
       Write `middle_three(text)` returning the three characters in the middle
       of an odd-length string of length 3 or more.

       `middle_three("abcde")` returns `"bcd"`.
       Anything shorter than 3, or of even length, returns `""`.
       """,
       """
       def middle_three(text):
           pass
       """,
       [("five characters", "assert middle_three('abcde') == 'bcd'"),
        ("exactly three", "assert middle_three('xyz') == 'xyz'"),
        ("even length rejected", "assert middle_three('abcd') == ''"),
        ("too short", "assert middle_three('ab') == ''"),
        ("longer", "assert middle_three('abcdefg') == 'cde'")],
       hints=["The middle index is len(text) // 2.",
              "Slice from middle - 1 up to middle + 2."],
       solution="""
       def middle_three(text):
           if len(text) < 3 or len(text) % 2 == 0:
               return ""
           middle = len(text) // 2
           return text[middle - 1:middle + 2]
       """)

    ex("p01.013", "p01", "Strings", "Tidy up a name", 2,
       """
       Write `tidy(name)` that strips leading and trailing whitespace,
       collapses any internal run of whitespace to one space, and
       title-cases the result.

       `tidy("  ada   LOVELACE ")` returns `"Ada Lovelace"`.
       """,
       """
       def tidy(name):
           pass
       """,
       [("messy input", "assert tidy('  ada   LOVELACE ') == 'Ada Lovelace'"),
        ("already clean", "assert tidy('Grace Hopper') == 'Grace Hopper'"),
        ("single word", "assert tidy('  linus ') == 'Linus'"),
        ("empty", "assert tidy('   ') == ''")],
       hints=["split() then ' '.join() collapses whitespace in one move.",
              "str.title() capitalises each word."],
       solution="""
       def tidy(name):
           return " ".join(name.split()).title()
       """)

    ex("p01.014", "p01", "Strings", "Acronym", 2,
       """
       Write `acronym(phrase)` returning the uppercase first letter of each
       word joined together, with no separators.

       `acronym("portable network graphics")` returns `"PNG"`.
       """,
       """
       def acronym(phrase):
           pass
       """,
       [("three words", "assert acronym('portable network graphics') == 'PNG'"),
        ("mixed case", "assert acronym('Read The Manual') == 'RTM'"),
        ("one word", "assert acronym('python') == 'P'"),
        ("empty", "assert acronym('') == ''")],
       solution="""
       def acronym(phrase):
           return "".join(word[0].upper() for word in phrase.split())
       """)

    ex("p01.015", "p01", "Dictionaries", "Count the words", 3,
       """
       Write `word_count(text)` returning a dict mapping each lowercase word to
       how many times it appears. Split on whitespace and ignore case.

       `word_count("a A b")` returns `{"a": 2, "b": 1}`.
       """,
       """
       def word_count(text):
           pass
       """,
       [("case folded", "assert word_count('a A b') == {'a': 2, 'b': 1}"),
        ("empty text", "assert word_count('') == {}"),
        ("longer",
         "assert word_count('the cat the hat') == {'the': 2, 'cat': 1, 'hat': 1}"),
        ("returns a dict", "assert isinstance(word_count('x'), dict)")],
       hints=["dict.get(key, 0) gives you a default instead of a KeyError.",
              "collections.Counter does this in one line - try it after you have written the loop."],
       solution="""
       def word_count(text):
           counts = {}
           for word in text.lower().split():
               counts[word] = counts.get(word, 0) + 1
           return counts
       """)

    ex("p01.016", "p01", "Dictionaries", "Look up without crashing", 2,
       """
       Write `lookup(data, key, default=None)` returning `data[key]` when the
       key exists, and `default` when it does not. Do not use `dict.get`;
       write the branch yourself so you see what `get` is doing.
       """,
       """
       def lookup(data, key, default=None):
           pass
       """,
       [("present", "assert lookup({'a': 1}, 'a') == 1"),
        ("missing returns None", "assert lookup({'a': 1}, 'b') is None"),
        ("missing returns default", "assert lookup({}, 'x', 42) == 42"),
        ("falsy values survive", "assert lookup({'a': 0}, 'a', 9) == 0"),
        ("no get used", "import inspect; assert '.get(' not in inspect.getsource(lookup)")],
       hints=["`in` tests for a key, not a value.",
              "Beware of `if data[key]:` - that would treat 0 and '' as missing."],
       solution="""
       def lookup(data, key, default=None):
           if key in data:
               return data[key]
           return default
       """)

    ex("p01.017", "p01", "Sets", "Unique, order preserved", 3,
       """
       Write `unique(items)` returning a list with duplicates removed, keeping
       the first occurrence of each value in its original position.

       `unique([3, 1, 3, 2, 1])` returns `[3, 1, 2]`.
       A plain `set()` would lose the order, so you need both structures.
       """,
       """
       def unique(items):
           pass
       """,
       [("keeps order", "assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]"),
        ("already unique", "assert unique(['a', 'b']) == ['a', 'b']"),
        ("empty", "assert unique([]) == []"),
        ("all same", "assert unique([7, 7, 7]) == [7]")],
       hints=["Track what you have already emitted in a set, and append to a list.",
              "Membership testing in a set is constant time; in a list it is not."],
       solution="""
       def unique(items):
           seen = set()
           out = []
           for item in items:
               if item not in seen:
                   seen.add(item)
                   out.append(item)
           return out
       """)

    ex("p01.018", "p01", "Sorting", "Sort people by surname", 3,
       """
       Write `by_surname(names)` sorting a list of `"First Last"` strings by
       last name, then by first name. Return a new list; do not modify the
       input.
       """,
       """
       def by_surname(names):
           pass
       """,
       [("sorts by last name",
         "assert by_surname(['Ada Lovelace', 'Grace Hopper']) == ['Grace Hopper', 'Ada Lovelace']"),
        ("ties break on first name",
         "assert by_surname(['Bob Smith', 'Alice Smith']) == ['Alice Smith', 'Bob Smith']"),
        ("input untouched",
         "src = ['B X', 'A X']\nby_surname(src)\nassert src == ['B X', 'A X']"),
        ("empty", "assert by_surname([]) == []")],
       hints=["sorted() returns a new list; list.sort() changes the original.",
              "A key function returning a tuple sorts by the first element, then the second."],
       solution="""
       def by_surname(names):
           def key(name):
               first, _, last = name.rpartition(" ")
               return (last, first)
           return sorted(names, key=key)
       """)

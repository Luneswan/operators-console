"""Phase 02 - Python engineering: protocols, generators, decorators, classes."""
from ex_lib import ex


def build():
    ex("p02.001", "p02", "Iterator protocol", "Write an iterator by hand", 3,
       """
       Build a class `Countdown(n)` that iterates from `n` down to 1.

       Implement `__iter__` and `__next__` yourself. Do not use a generator -
       the point is to see what a generator is doing underneath.
       """,
       """
       class Countdown:
           def __init__(self, n):
               pass
       """,
       [("counts down", "assert list(Countdown(3)) == [3, 2, 1]"),
        ("zero yields nothing", "assert list(Countdown(0)) == []"),
        ("works in a for loop",
         "seen = []\nfor v in Countdown(2):\n    seen.append(v)\nassert seen == [2, 1]"),
        ("raises StopIteration",
         "it = iter(Countdown(1))\nnext(it)\ntry:\n    next(it)\nexcept StopIteration:\n    pass\nelse:\n    raise AssertionError('must raise StopIteration')")],
       hints=["__iter__ returns the thing that has __next__ - often self.",
              "__next__ raises StopIteration when there is nothing left."],
       solution="""
       class Countdown:
           def __init__(self, n):
               self.current = n

           def __iter__(self):
               return self

           def __next__(self):
               if self.current <= 0:
                   raise StopIteration
               self.current -= 1
               return self.current + 1
       """)

    ex("p02.002", "p02", "Generators", "Fibonacci, lazily", 3,
       """
       Write a generator function `fib()` yielding the Fibonacci sequence
       starting 0, 1, 1, 2, 3, 5 and never ending.

       Because it is lazy, an endless generator costs nothing until you take
       values from it.
       """,
       """
       def fib():
           pass
       """,
       [("first eight",
         "import itertools\nassert list(itertools.islice(fib(), 8)) == [0, 1, 1, 2, 3, 5, 8, 13]"),
        ("is a generator",
         "import inspect; assert inspect.isgeneratorfunction(fib)"),
        ("each call is independent",
         "a, b = fib(), fib()\nassert next(a) == next(b) == 0"),
        ("goes far without trouble",
         "import itertools\nassert len(str(next(itertools.islice(fib(), 300, 301)))) > 50")],
       hints=["A function containing `yield` returns a generator when called.",
              "Track two values and swap them: a, b = b, a + b."],
       solution="""
       def fib():
           a, b = 0, 1
           while True:
               yield a
               a, b = b, a + b
       """)

    ex("p02.003", "p02", "Generators", "Flatten nested lists", 4,
       """
       Write a generator `flatten(items)` yielding every non-list value from an
       arbitrarily nested list, left to right.

       `flatten([1, [2, [3, 4]], 5])` yields 1, 2, 3, 4, 5.
       Use `yield from` for the recursive step.
       """,
       """
       def flatten(items):
           pass
       """,
       [("nested", "assert list(flatten([1, [2, [3, 4]], 5])) == [1, 2, 3, 4, 5]"),
        ("flat already", "assert list(flatten([1, 2])) == [1, 2]"),
        ("deep", "assert list(flatten([[[[7]]]])) == [7]"),
        ("empty pockets", "assert list(flatten([1, [], [2, []]])) == [1, 2]"),
        ("strings are not exploded",
         "assert list(flatten(['ab', ['cd']])) == ['ab', 'cd']")],
       hints=["`yield from sub` forwards every value the inner generator produces.",
              "Check isinstance(item, list), not Iterable, or strings will unravel."],
       solution="""
       def flatten(items):
           for item in items:
               if isinstance(item, list):
                   yield from flatten(item)
               else:
                   yield item
       """)

    ex("p02.004", "p02", "Decorators", "Count the calls", 3,
       """
       Write a decorator `counted` that adds a `calls` attribute to the
       wrapped function, counting how many times it has run. The wrapped
       function must keep its own name and docstring.
       """,
       """
       import functools


       def counted(func):
           pass
       """,
       [("counts",
         "@counted\ndef f():\n    return 1\nf(); f(); f()\nassert f.calls == 3"),
        ("starts at zero",
         "@counted\ndef g():\n    pass\nassert g.calls == 0"),
        ("passes arguments through",
         "@counted\ndef add(a, b=0):\n    return a + b\nassert add(2, b=3) == 5"),
        ("keeps the name",
         "@counted\ndef named():\n    'doc here'\nassert named.__name__ == 'named'\nassert named.__doc__ == 'doc here'")],
       hints=["functools.wraps copies __name__, __doc__ and friends onto the wrapper.",
              "Attach the counter to the wrapper, then return the wrapper."],
       solution="""
       import functools


       def counted(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               wrapper.calls += 1
               return func(*args, **kwargs)
           wrapper.calls = 0
           return wrapper
       """)

    ex("p02.005", "p02", "Decorators", "A decorator that takes arguments", 4,
       """
       Write `repeat(times)` - a decorator factory. The decorated function runs
       `times` times and returns a list of every result.

           @repeat(3)
           def roll():
               return 4

           roll() == [4, 4, 4]
       """,
       """
       import functools


       def repeat(times):
           pass
       """,
       [("repeats three times",
         "@repeat(3)\ndef f():\n    return 4\nassert f() == [4, 4, 4]"),
        ("passes arguments",
         "@repeat(2)\ndef double(x):\n    return x * 2\nassert double(5) == [10, 10]"),
        ("zero repeats",
         "@repeat(0)\ndef n():\n    return 1\nassert n() == []"),
        ("keeps the name",
         "@repeat(1)\ndef named():\n    pass\nassert named.__name__ == 'named'")],
       hints=["Three nested functions: the factory, the decorator, then the wrapper.",
              "The factory takes the argument; the decorator takes the function."],
       solution="""
       import functools


       def repeat(times):
           def decorator(func):
               @functools.wraps(func)
               def wrapper(*args, **kwargs):
                   return [func(*args, **kwargs) for _ in range(times)]
               return wrapper
           return decorator
       """)

    ex("p02.006", "p02", "Context managers", "A context manager class", 3,
       """
       Write a class `Tag(name)` used as a context manager that appends
       `"<name>"` to a list when it enters and `"</name>"` when it leaves.

       The list must be reachable as `tag.parts`. The closing tag must still be
       written if the block raises, and the exception must still propagate.
       """,
       """
       class Tag:
           def __init__(self, name):
               pass
       """,
       [("wraps the block",
         "t = Tag('b')\nwith t:\n    t.parts.append('hi')\nassert t.parts == ['<b>', 'hi', '</b>']"),
        ("closes on error",
         "t = Tag('i')\ntry:\n    with t:\n        raise RuntimeError('boom')\nexcept RuntimeError:\n    pass\nassert t.parts == ['<i>', '</i>']"),
        ("does not swallow the error",
         "t = Tag('x')\ntry:\n    with t:\n        raise ValueError\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('exception must propagate')")],
       hints=["__exit__ runs whether or not the block raised.",
              "Returning a truthy value from __exit__ suppresses the exception - do not."],
       solution="""
       class Tag:
           def __init__(self, name):
               self.name = name
               self.parts = []

           def __enter__(self):
               self.parts.append(f"<{self.name}>")
               return self

           def __exit__(self, exc_type, exc, tb):
               self.parts.append(f"</{self.name}>")
               return False
       """)

    ex("p02.007", "p02", "Context managers", "contextlib version", 3,
       """
       Write `temporarily(mapping, key, value)` - a context manager built with
       `@contextlib.contextmanager` that sets `mapping[key] = value` on entry
       and restores the previous state on exit, including the case where the
       key did not exist before.
       """,
       """
       import contextlib


       @contextlib.contextmanager
       def temporarily(mapping, key, value):
           pass
       """,
       [("sets and restores",
         "d = {'a': 1}\nwith temporarily(d, 'a', 99):\n    assert d['a'] == 99\nassert d['a'] == 1"),
        ("removes a key that was absent",
         "d = {}\nwith temporarily(d, 'new', 5):\n    assert d['new'] == 5\nassert 'new' not in d"),
        ("restores after an error",
         "d = {'a': 1}\ntry:\n    with temporarily(d, 'a', 2):\n        raise RuntimeError\nexcept RuntimeError:\n    pass\nassert d['a'] == 1")],
       hints=["Everything before `yield` is the enter step; everything after is exit.",
              "Wrap the yield in try/finally so cleanup survives an exception."],
       solution="""
       import contextlib


       @contextlib.contextmanager
       def temporarily(mapping, key, value):
           missing = key not in mapping
           previous = mapping.get(key)
           mapping[key] = value
           try:
               yield mapping
           finally:
               if missing:
                   mapping.pop(key, None)
               else:
                   mapping[key] = previous
       """)

    ex("p02.008", "p02", "Dunder methods", "A vector type", 4,
       """
       Write a class `Vector(x, y)` supporting:

       * `v1 + v2` and `v1 - v2`
       * `v * 3` (scaling by a number)
       * `v1 == v2` by value
       * `repr(v)` returning `Vector(1, 2)`
       * `abs(v)` returning the length
       """,
       """
       import math


       class Vector:
           def __init__(self, x, y):
               self.x = x
               self.y = y
       """,
       [("adds", "assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)"),
        ("subtracts", "assert Vector(5, 5) - Vector(1, 2) == Vector(4, 3)"),
        ("scales", "assert Vector(1, 2) * 3 == Vector(3, 6)"),
        ("repr", "assert repr(Vector(1, 2)) == 'Vector(1, 2)'"),
        ("length", "assert abs(Vector(3, 4)) == 5"),
        ("unequal types",
         "assert (Vector(1, 1) == 'not a vector') is False")],
       hints=["__eq__ should return NotImplemented for unrelated types, not False.",
              "__repr__ is for developers; make it look like the call that builds the object."],
       solution="""
       import math


       class Vector:
           def __init__(self, x, y):
               self.x = x
               self.y = y

           def __add__(self, other):
               return Vector(self.x + other.x, self.y + other.y)

           def __sub__(self, other):
               return Vector(self.x - other.x, self.y - other.y)

           def __mul__(self, factor):
               return Vector(self.x * factor, self.y * factor)

           def __eq__(self, other):
               if not isinstance(other, Vector):
                   return NotImplemented
               return (self.x, self.y) == (other.x, other.y)

           def __repr__(self):
               return f"Vector({self.x}, {self.y})"

           def __abs__(self):
               return math.hypot(self.x, self.y)
       """)

    ex("p02.009", "p02", "Dunder methods", "A sequence of your own", 3,
       """
       Write `Deck()` holding the strings `"A"` through `"E"`. Support
       `len(deck)`, `deck[0]`, negative indexing, iteration and `"C" in deck`
       by implementing only `__len__` and `__getitem__`.
       """,
       """
       class Deck:
           def __init__(self):
               self.cards = ["A", "B", "C", "D", "E"]
       """,
       [("length", "assert len(Deck()) == 5"),
        ("indexing", "assert Deck()[0] == 'A'"),
        ("negative index", "assert Deck()[-1] == 'E'"),
        ("iterates", "assert list(Deck()) == ['A', 'B', 'C', 'D', 'E']"),
        ("membership", "assert ('C' in Deck()) is True"),
        ("slices", "assert Deck()[1:3] == ['B', 'C']")],
       hints=["Delegating to the underlying list gives you slicing for free.",
              "Python builds iteration and `in` out of __getitem__ when __iter__ is absent."],
       solution="""
       class Deck:
           def __init__(self):
               self.cards = ["A", "B", "C", "D", "E"]

           def __len__(self):
               return len(self.cards)

           def __getitem__(self, index):
               return self.cards[index]
       """)

    ex("p02.010", "p02", "Properties", "Validate on assignment", 3,
       """
       Write `Temperature` with a `celsius` property that rejects anything
       below absolute zero (-273.15) with `ValueError`, and a read-only
       `fahrenheit` property computed from it.
       """,
       """
       class Temperature:
           def __init__(self, celsius=0.0):
               self.celsius = celsius
       """,
       [("stores and reads",
         "t = Temperature(20)\nassert t.celsius == 20"),
        ("converts", "assert Temperature(100).fahrenheit == 212"),
        ("rejects impossible values",
         "try:\n    Temperature(-300)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("rejects on later assignment",
         "t = Temperature(0)\ntry:\n    t.celsius = -400\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("fahrenheit is read only",
         "t = Temperature(0)\ntry:\n    t.fahrenheit = 1\nexcept AttributeError:\n    pass\nelse:\n    raise AssertionError('should not be settable')")],
       hints=["The setter stores to a differently named attribute, usually _celsius.",
              "Assigning in __init__ goes through the setter, so validation happens there too."],
       solution="""
       class Temperature:
           def __init__(self, celsius=0.0):
               self.celsius = celsius

           @property
           def celsius(self):
               return self._celsius

           @celsius.setter
           def celsius(self, value):
               if value < -273.15:
                   raise ValueError("below absolute zero")
               self._celsius = value

           @property
           def fahrenheit(self):
               return self._celsius * 9 / 5 + 32
       """)

    ex("p02.011", "p02", "Classes", "Alternative constructors", 3,
       """
       Write `Event` with `year`, `month` and `day`, plus a classmethod
       `from_string("2026-01-31")` that builds one, and a staticmethod
       `is_valid_string(text)` returning whether a string has that shape.
       """,
       """
       class Event:
           def __init__(self, year, month, day):
               self.year = year
               self.month = month
               self.day = day
       """,
       [("builds from a string",
         "e = Event.from_string('2026-01-31')\nassert (e.year, e.month, e.day) == (2026, 1, 31)"),
        ("validates good input",
         "assert Event.is_valid_string('2026-01-31') is True"),
        ("rejects bad input",
         "assert Event.is_valid_string('31/01/2026') is False"),
        ("classmethod returns the right class",
         "assert isinstance(Event.from_string('2000-01-01'), Event)"),
        ("staticmethod needs no instance",
         "assert Event.is_valid_string('1999-12-31') is True")],
       hints=["A classmethod receives the class, so `cls(...)` also works for subclasses.",
              "A staticmethod is a plain function that happens to live on the class."],
       solution="""
       class Event:
           def __init__(self, year, month, day):
               self.year = year
               self.month = month
               self.day = day

           @classmethod
           def from_string(cls, text):
               year, month, day = text.split("-")
               return cls(int(year), int(month), int(day))

           @staticmethod
           def is_valid_string(text):
               parts = text.split("-")
               if len(parts) != 3:
                   return False
               widths = (4, 2, 2)
               return all(p.isdigit() and len(p) == w
                          for p, w in zip(parts, widths))
       """)

    ex("p02.012", "p02", "Dataclasses", "Less boilerplate", 3,
       """
       Rewrite a point type as a frozen, ordered dataclass `Point(x, y)`.

       It must be immutable, comparable, sortable and usable as a dict key.
       """,
       """
       from dataclasses import dataclass


       @dataclass
       class Point:
           x: int
           y: int
       """,
       [("equality by value", "assert Point(1, 2) == Point(1, 2)"),
        ("orders", "assert sorted([Point(2, 0), Point(1, 9)])[0] == Point(1, 9)"),
        ("hashable", "assert len({Point(1, 1), Point(1, 1)}) == 1"),
        ("immutable",
         "p = Point(1, 2)\ntry:\n    p.x = 5\nexcept Exception:\n    pass\nelse:\n    raise AssertionError('must be frozen')"),
        ("readable repr", "assert repr(Point(1, 2)) == 'Point(x=1, y=2)'")],
       hints=["@dataclass(frozen=True, order=True) gives you all of it.",
              "frozen=True is what makes instances hashable."],
       solution="""
       from dataclasses import dataclass


       @dataclass(frozen=True, order=True)
       class Point:
           x: int
           y: int
       """)

    ex("p02.013", "p02", "Inheritance", "Abstract base classes", 4,
       """
       Define an abstract base `Shape` with an abstract `area()` and a
       concrete `describe()` returning `"<ClassName> with area <area>"`.

       Then write `Rectangle(w, h)` and `Circle(r)`. Instantiating `Shape`
       directly must raise `TypeError`.
       """,
       """
       from abc import ABC, abstractmethod
       import math


       class Shape(ABC):
           pass
       """,
       [("rectangle area", "assert Rectangle(3, 4).area() == 12"),
        ("circle area", "assert abs(Circle(1).area() - math.pi) < 1e-9"),
        ("describe uses the subclass name",
         "assert Rectangle(2, 2).describe() == 'Rectangle with area 4'"),
        ("abstract cannot be built",
         "try:\n    Shape()\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError('Shape must be abstract')")],
       hints=["type(self).__name__ gives the real subclass name at runtime.",
              "A class with an unimplemented @abstractmethod cannot be instantiated."],
       solution="""
       from abc import ABC, abstractmethod
       import math


       class Shape(ABC):
           @abstractmethod
           def area(self):
               ...

           def describe(self):
               return f"{type(self).__name__} with area {self.area()}"


       class Rectangle(Shape):
           def __init__(self, w, h):
               self.w = w
               self.h = h

           def area(self):
               return self.w * self.h


       class Circle(Shape):
           def __init__(self, r):
               self.r = r

           def area(self):
               return math.pi * self.r ** 2
       """)

    ex("p02.014", "p02", "itertools", "Chunk an iterable", 4,
       """
       Write `chunks(iterable, size)` yielding lists of at most `size` items.
       It must work on a generator, not only a list, and must not read the
       whole input into memory first.
       """,
       """
       import itertools


       def chunks(iterable, size):
           pass
       """,
       [("even split", "assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]"),
        ("ragged tail",
         "assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]"),
        ("empty input", "assert list(chunks([], 3)) == []"),
        ("works on a generator",
         "assert list(chunks((n for n in range(5)), 2)) == [[0, 1], [2, 3], [4]]"),
        ("lazy",
         "import itertools\ninf = itertools.count()\nassert next(iter(chunks(inf, 3))) == [0, 1, 2]"),
        ("rejects a size of zero",
         "try:\n    list(chunks([1], 0))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')")],
       hints=["iter() on the input first, then islice repeatedly from that one iterator.",
              "islice on a fresh iter() each time would restart from the beginning."],
       solution="""
       import itertools


       def chunks(iterable, size):
           if size <= 0:
               raise ValueError("size must be positive")
           source = iter(iterable)
           while True:
               batch = list(itertools.islice(source, size))
               if not batch:
                   return
               yield batch
       """)

    ex("p02.015", "p02", "functools", "Memoise an expensive function", 3,
       """
       Write `slow_fib(n)` computed by naive recursion, then make it fast with
       caching. It must answer `slow_fib(35)` effectively instantly, and
       expose a `cache_info()` from the standard library.
       """,
       """
       import functools


       def slow_fib(n):
           pass
       """,
       [("correct", "assert slow_fib(10) == 55"),
        ("base cases", "assert slow_fib(0) == 0 and slow_fib(1) == 1"),
        ("fast enough to be cached",
         "import time\nstart = time.monotonic()\nslow_fib(35)\nassert time.monotonic() - start < 1.0"),
        ("exposes cache info", "assert slow_fib.cache_info().hits >= 0")],
       hints=["functools.lru_cache(maxsize=None), or functools.cache on 3.9 and later.",
              "The decorator caches by arguments, so the recursion hits the cache too."],
       solution="""
       import functools


       @functools.lru_cache(maxsize=None)
       def slow_fib(n):
           if n < 2:
               return n
           return slow_fib(n - 1) + slow_fib(n - 2)
       """)

    ex("p02.016", "p02", "Typing", "Type hints that mean something", 2,
       """
       Annotate `first_or_default` fully: it takes a list of strings and an
       optional default string, and returns a string.

       The body is written for you. Add the annotations so that
       `typing.get_type_hints` reports them.
       """,
       """
       def first_or_default(items, default="none"):
           return items[0] if items else default
       """,
       [("still works",
         "assert first_or_default(['a']) == 'a'\nassert first_or_default([]) == 'none'"),
        ("items is annotated",
         "import typing\nhints = typing.get_type_hints(first_or_default)\nassert 'items' in hints"),
        ("return is annotated",
         "import typing\nassert typing.get_type_hints(first_or_default)['return'] is str"),
        ("default is a string",
         "import typing\nassert typing.get_type_hints(first_or_default)['default'] is str")],
       hints=["list[str] works directly on modern Python; no typing import needed for it."],
       solution="""
       def first_or_default(items: list[str], default: str = "none") -> str:
           return items[0] if items else default
       """)

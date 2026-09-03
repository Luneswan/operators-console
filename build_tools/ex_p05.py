"""Phase 05 - algorithms and problem solving."""
from ex_lib import ex


def build():
    ex("p05.001", "p05", "Hashing", "Two sum", 3,
       """
       Write `two_sum(numbers, target)` returning the indices of the two values
       that add up to `target`, as a tuple in increasing order, or `None`.

       Solve it in one pass. The obvious nested loop is O(n^2); a dict makes it
       O(n).
       """,
       """
       def two_sum(numbers, target):
           pass
       """,
       [("basic", "assert two_sum([2, 7, 11, 15], 9) == (0, 1)"),
        ("later in the list", "assert two_sum([3, 2, 4], 6) == (1, 2)"),
        ("same value twice", "assert two_sum([3, 3], 6) == (0, 1)"),
        ("no answer", "assert two_sum([1, 2], 50) is None"),
        ("single pass",
         "import inspect\nsrc = inspect.getsource(two_sum)\nassert src.count('for ') <= 1")],
       hints=["As you walk the list, ask whether target minus this value has already been seen.",
              "Store value to index in a dict as you go."],
       solution="""
       def two_sum(numbers, target):
           seen = {}
           for index, value in enumerate(numbers):
               partner = target - value
               if partner in seen:
                   return (seen[partner], index)
               seen[value] = index
           return None
       """)

    ex("p05.002", "p05", "Intervals", "Merge overlapping intervals", 4,
       """
       Write `merge(intervals)` taking a list of `(start, end)` pairs and
       returning the merged, sorted list. Touching intervals such as `(1, 2)`
       and `(2, 3)` merge into `(1, 3)`.
       """,
       """
       def merge(intervals):
           pass
       """,
       [("overlaps",
         "assert merge([(1, 3), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]"),
        ("touching", "assert merge([(1, 2), (2, 3)]) == [(1, 3)]"),
        ("unsorted input", "assert merge([(5, 6), (1, 2)]) == [(1, 2), (5, 6)]"),
        ("fully contained", "assert merge([(1, 10), (2, 3)]) == [(1, 10)]"),
        ("empty", "assert merge([]) == []")],
       hints=["Sort by start first; then a single pass is enough.",
              "Extend the last interval when the next one starts at or before its end."],
       solution="""
       def merge(intervals):
           out = []
           for start, end in sorted(intervals):
               if out and start <= out[-1][1]:
                   out[-1] = (out[-1][0], max(out[-1][1], end))
               else:
                   out.append((start, end))
           return out
       """)

    ex("p05.003", "p05", "Dynamic programming", "Largest sum of a run", 4,
       """
       Write `max_subarray(numbers)` returning the largest sum of any
       contiguous run. For an empty list return 0.

       This is Kadane's algorithm: linear time, constant memory.
       """,
       """
       def max_subarray(numbers):
           pass
       """,
       [("classic",
         "assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6"),
        ("all positive", "assert max_subarray([1, 2, 3]) == 6"),
        ("all negative", "assert max_subarray([-3, -1, -7]) == -1"),
        ("single", "assert max_subarray([5]) == 5"),
        ("empty", "assert max_subarray([]) == 0")],
       hints=["At each step, either extend the run or start a new one at this value.",
              "current = max(value, current + value)."],
       solution="""
       def max_subarray(numbers):
           if not numbers:
               return 0
           best = current = numbers[0]
           for value in numbers[1:]:
               current = max(value, current + value)
               best = max(best, current)
           return best
       """)

    ex("p05.004", "p05", "Sorting", "Merge sort", 4,
       """
       Write `merge_sort(items)` returning a new sorted list. Implement the
       divide and merge yourself - no `sorted`, no `list.sort`.
       """,
       """
       def merge_sort(items):
           pass
       """,
       [("sorts", "assert merge_sort([5, 2, 9, 1]) == [1, 2, 5, 9]"),
        ("stable on duplicates", "assert merge_sort([3, 1, 3]) == [1, 3, 3]"),
        ("empty", "assert merge_sort([]) == []"),
        ("single", "assert merge_sort([1]) == [1]"),
        ("matches sorted for random data",
         "import random\nfor _ in range(50):\n    data = [random.randint(-50, 50) for _ in range(30)]\n    assert merge_sort(data) == sorted(data)"),
        ("does not use sorted",
         "import inspect\nsrc = inspect.getsource(merge_sort)\nassert 'sorted(' not in src and '.sort(' not in src")],
       hints=["Split in half, sort each half recursively, then merge two sorted lists.",
              "The merge step walks both halves with two indices."],
       solution="""
       def merge_sort(items):
           if len(items) <= 1:
               return list(items)
           middle = len(items) // 2
           left = merge_sort(items[:middle])
           right = merge_sort(items[middle:])
           out = []
           i = j = 0
           while i < len(left) and j < len(right):
               if right[j] < left[i]:
                   out.append(right[j])
                   j += 1
               else:
                   out.append(left[i])
                   i += 1
           out.extend(left[i:])
           out.extend(right[j:])
           return out
       """)

    ex("p05.005", "p05", "Dynamic programming", "Coin change", 5,
       """
       Write `fewest_coins(coins, amount)` returning the smallest number of
       coins that make `amount`, or `-1` when it cannot be made. Coins may be
       reused without limit.
       """,
       """
       def fewest_coins(coins, amount):
           pass
       """,
       [("classic", "assert fewest_coins([1, 5, 10, 25], 30) == 2"),
        ("impossible", "assert fewest_coins([5], 3) == -1"),
        ("zero amount", "assert fewest_coins([1], 0) == 0"),
        ("greedy would fail", "assert fewest_coins([1, 3, 4], 6) == 2"),
        ("no coins", "assert fewest_coins([], 5) == -1")],
       hints=["Build up an answer for every amount from 0 to the target.",
              "best[n] = 1 + min(best[n - coin]) over the coins that fit."],
       solution="""
       def fewest_coins(coins, amount):
           best = [0] + [float("inf")] * amount
           for value in range(1, amount + 1):
               for coin in coins:
                   if coin <= value and best[value - coin] + 1 < best[value]:
                       best[value] = best[value - coin] + 1
           return -1 if best[amount] == float("inf") else int(best[amount])
       """)

    ex("p05.006", "p05", "Strings", "Group anagrams", 4,
       """
       Write `group_anagrams(words)` returning a list of groups, each holding
       words that are anagrams of each other.

       Sort each group alphabetically, and sort the groups by their first word,
       so the answer is deterministic.
       """,
       """
       def group_anagrams(words):
           pass
       """,
       [("groups",
         "assert group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']) == [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]"),
        ("empty", "assert group_anagrams([]) == []"),
        ("no anagrams", "assert group_anagrams(['a', 'b']) == [['a'], ['b']]"),
        ("case sensitive", "assert group_anagrams(['Ab', 'ba']) == [['Ab'], ['ba']]")],
       hints=["The sorted letters of a word make a natural group key.",
              "collections.defaultdict(list) saves a membership test."],
       solution="""
       from collections import defaultdict


       def group_anagrams(words):
           buckets = defaultdict(list)
           for word in words:
               buckets["".join(sorted(word))].append(word)
           groups = [sorted(group) for group in buckets.values()]
           return sorted(groups, key=lambda group: group[0])
       """)

    ex("p05.007", "p05", "Two pointers", "Longest run without repeats", 4,
       """
       Write `longest_unique(text)` returning the length of the longest
       substring with no repeated character.

       `"abcabcbb"` gives 3, for `"abc"`.
       """,
       """
       def longest_unique(text):
           pass
       """,
       [("classic", "assert longest_unique('abcabcbb') == 3"),
        ("all same", "assert longest_unique('bbbb') == 1"),
        ("mixed", "assert longest_unique('pwwkew') == 3"),
        ("empty", "assert longest_unique('') == 0"),
        ("all distinct", "assert longest_unique('abcdef') == 6")],
       hints=["Keep a sliding window and the last index each character was seen at.",
              "When you meet a repeat inside the window, move the left edge past it."],
       solution="""
       def longest_unique(text):
           last_seen = {}
           best = start = 0
           for index, ch in enumerate(text):
               if ch in last_seen and last_seen[ch] >= start:
                   start = last_seen[ch] + 1
               last_seen[ch] = index
               best = max(best, index - start + 1)
           return best
       """)

    ex("p05.008", "p05", "Backtracking", "All subsets", 4,
       """
       Write `subsets(items)` returning every subset of a list of distinct
       values, as a list of lists, ordered by subset size then by contents.
       """,
       """
       def subsets(items):
           pass
       """,
       [("three items",
         "assert subsets([1, 2, 3]) == [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]"),
        ("empty", "assert subsets([]) == [[]]"),
        ("count is a power of two", "assert len(subsets([1, 2, 3, 4])) == 16")],
       hints=["itertools.combinations(items, k) gives every subset of size k.",
              "Loop k from 0 to len(items)."],
       solution="""
       import itertools


       def subsets(items):
           out = []
           for size in range(len(items) + 1):
               out.extend(list(combo)
                          for combo in itertools.combinations(items, size))
           return out
       """)

    ex("p05.009", "p05", "Graphs", "Cheapest route", 5,
       """
       Write `cheapest(graph, start, goal)` for a weighted graph given as
       `{node: {neighbour: cost}}`, returning the cost of the cheapest route,
       or `None` when unreachable. All costs are positive.
       """,
       """
       import heapq


       def cheapest(graph, start, goal):
           pass
       """,
       [("picks the cheap path",
         "g = {'a': {'b': 1, 'c': 4}, 'b': {'c': 1}, 'c': {}}\nassert cheapest(g, 'a', 'c') == 2"),
        ("start equals goal", "assert cheapest({'a': {}}, 'a', 'a') == 0"),
        ("unreachable", "assert cheapest({'a': {}, 'b': {}}, 'a', 'b') is None"),
        ("unknown node", "assert cheapest({}, 'x', 'y') is None")],
       hints=["A priority queue always expands the cheapest frontier node first.",
              "Skip a node you have already finalised - its first pop was optimal."],
       solution="""
       import heapq


       def cheapest(graph, start, goal):
           if start not in graph or goal not in graph:
               return None
           best = {start: 0}
           queue = [(0, start)]
           done = set()
           while queue:
               cost, node = heapq.heappop(queue)
               if node in done:
                   continue
               if node == goal:
                   return cost
               done.add(node)
               for neighbour, step in graph.get(node, {}).items():
                   candidate = cost + step
                   if candidate < best.get(neighbour, float("inf")):
                       best[neighbour] = candidate
                       heapq.heappush(queue, (candidate, neighbour))
           return None
       """)

    ex("p05.010", "p05", "Complexity", "Make it fast enough", 4,
       """
       `count_pairs(numbers, target)` counts how many unordered pairs sum to
       `target`. The naive version is O(n^2) and is too slow for the last
       check here.

       Write an O(n) version. Each pair counts once; the input may contain
       duplicates.
       """,
       """
       def count_pairs(numbers, target):
           pass
       """,
       [("small case", "assert count_pairs([1, 2, 3, 4], 5) == 2"),
        ("duplicates", "assert count_pairs([1, 1, 1], 2) == 3"),
        ("none", "assert count_pairs([1, 2], 99) == 0"),
        ("fast on a big input",
         "import time, random\ndata = [random.randint(0, 1000) for _ in range(60000)]\nstart = time.monotonic()\ncount_pairs(data, 500)\nassert time.monotonic() - start < 2.0")],
       hints=["Count how many of each value you have seen so far, then add the matches.",
              "Counting inside the same pass avoids double counting."],
       solution="""
       from collections import Counter


       def count_pairs(numbers, target):
           seen = Counter()
           total = 0
           for value in numbers:
               total += seen[target - value]
               seen[value] += 1
           return total
       """)

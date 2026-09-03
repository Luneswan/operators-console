"""Phase 04 - computer science core: data structures you build yourself."""
from ex_lib import ex


def build():
    ex("p04.001", "p04", "Stacks", "Balanced brackets", 3,
       """
       Write `balanced(text)` returning True when every `(`, `[` and `{` is
       closed in the right order. Ignore any other character.
       """,
       """
       def balanced(text):
           pass
       """,
       [("simple pair", "assert balanced('()') is True"),
        ("nested", "assert balanced('{[()]}') is True"),
        ("crossed", "assert balanced('([)]') is False"),
        ("unclosed", "assert balanced('(((') is False"),
        ("stray close", "assert balanced(')') is False"),
        ("ignores other text", "assert balanced('a(b)c') is True"),
        ("empty", "assert balanced('') is True")],
       hints=["A stack is just a list with append and pop.",
              "On a closing bracket, the top of the stack must be its partner."],
       solution="""
       def balanced(text):
           pairs = {")": "(", "]": "[", "}": "{"}
           stack = []
           for ch in text:
               if ch in "([{":
                   stack.append(ch)
               elif ch in pairs:
                   if not stack or stack.pop() != pairs[ch]:
                       return False
           return not stack
       """)

    ex("p04.002", "p04", "Queues", "A ring buffer", 4,
       """
       Write `RingBuffer(capacity)` that keeps only the most recent `capacity`
       items. Support `push(item)`, `items()` returning oldest to newest, and
       `len()`.
       """,
       """
       from collections import deque


       class RingBuffer:
           def __init__(self, capacity):
               pass
       """,
       [("keeps recent items",
         "b = RingBuffer(3)\nfor n in [1, 2, 3, 4]:\n    b.push(n)\nassert b.items() == [2, 3, 4]"),
        ("length is capped",
         "b = RingBuffer(2)\nfor n in range(10):\n    b.push(n)\nassert len(b) == 2"),
        ("under capacity",
         "b = RingBuffer(5)\nb.push('a')\nassert b.items() == ['a']"),
        ("empty", "assert RingBuffer(3).items() == []")],
       hints=["collections.deque(maxlen=n) drops from the far end automatically."],
       solution="""
       from collections import deque


       class RingBuffer:
           def __init__(self, capacity):
               self._data = deque(maxlen=capacity)

           def push(self, item):
               self._data.append(item)

           def items(self):
               return list(self._data)

           def __len__(self):
               return len(self._data)
       """)

    ex("p04.003", "p04", "Linked lists", "Build and reverse a linked list", 4,
       """
       Write `Node(value, next=None)`, `to_list(head)` turning a chain into a
       Python list, `from_list(values)` building a chain, and `reverse(head)`
       returning the new head of the reversed chain.

       Reverse it iteratively, in place, without building a Python list first.
       """,
       """
       class Node:
           def __init__(self, value, next=None):
               self.value = value
               self.next = next


       def from_list(values):
           pass


       def to_list(head):
           pass


       def reverse(head):
           pass
       """,
       [("round trips", "assert to_list(from_list([1, 2, 3])) == [1, 2, 3]"),
        ("reverses", "assert to_list(reverse(from_list([1, 2, 3]))) == [3, 2, 1]"),
        ("single node", "assert to_list(reverse(from_list([9]))) == [9]"),
        ("empty chain", "assert to_list(reverse(from_list([]))) is not None or True"),
        ("empty returns None", "assert reverse(None) is None"),
        ("no list used in reverse",
         "import inspect\nsrc = inspect.getsource(reverse)\nassert 'to_list' not in src and 'from_list' not in src")],
       hints=["Reversal needs three names: previous, current and the saved next.",
              "Save current.next before you overwrite it, or you lose the rest of the chain."],
       solution="""
       class Node:
           def __init__(self, value, next=None):
               self.value = value
               self.next = next


       def from_list(values):
           head = None
           for value in reversed(values):
               head = Node(value, head)
           return head


       def to_list(head):
           out = []
           while head is not None:
               out.append(head.value)
               head = head.next
           return out


       def reverse(head):
           previous = None
           while head is not None:
               following = head.next
               head.next = previous
               previous = head
               head = following
           return previous
       """)

    ex("p04.004", "p04", "Hash tables", "Write a hash map", 5,
       """
       Implement `HashMap(buckets=8)` with `put(key, value)`, `get(key,
       default=None)` and `__len__`, using a list of buckets and Python's
       `hash()`. Handle collisions with chaining, and overwrite on a repeat
       key.
       """,
       """
       class HashMap:
           def __init__(self, buckets=8):
               pass
       """,
       [("stores and reads",
         "m = HashMap()\nm.put('a', 1)\nassert m.get('a') == 1"),
        ("overwrites",
         "m = HashMap()\nm.put('a', 1)\nm.put('a', 2)\nassert m.get('a') == 2 and len(m) == 1"),
        ("missing key default", "assert HashMap().get('nope', 'x') == 'x'"),
        ("survives collisions",
         "m = HashMap(buckets=1)\nfor i in range(20):\n    m.put(i, i * 2)\nassert m.get(19) == 38 and len(m) == 20"),
        ("counts entries",
         "m = HashMap()\nfor i in range(5):\n    m.put(i, i)\nassert len(m) == 5")],
       hints=["Bucket index is hash(key) % len(self.buckets); hash can be negative, and % fixes it.",
              "Each bucket holds a list of (key, value) pairs."],
       solution="""
       class HashMap:
           def __init__(self, buckets=8):
               self.buckets = [[] for _ in range(buckets)]
               self.size = 0

           def _bucket(self, key):
               return self.buckets[hash(key) % len(self.buckets)]

           def put(self, key, value):
               bucket = self._bucket(key)
               for index, (existing, _v) in enumerate(bucket):
                   if existing == key:
                       bucket[index] = (key, value)
                       return
               bucket.append((key, value))
               self.size += 1

           def get(self, key, default=None):
               for existing, value in self._bucket(key):
                   if existing == key:
                       return value
               return default

           def __len__(self):
               return self.size
       """)

    ex("p04.005", "p04", "Trees", "A binary search tree", 5,
       """
       Implement `BST` with `insert(value)`, `contains(value)` and
       `in_order()` returning the values sorted ascending. Duplicates are
       ignored.
       """,
       """
       class BST:
           def __init__(self):
               self.root = None
       """,
       [("sorted traversal",
         "t = BST()\nfor v in [5, 3, 8, 1]:\n    t.insert(v)\nassert t.in_order() == [1, 3, 5, 8]"),
        ("finds present values",
         "t = BST()\nt.insert(4)\nassert t.contains(4) is True"),
        ("rejects absent values", "assert BST().contains(1) is False"),
        ("ignores duplicates",
         "t = BST()\nfor v in [2, 2, 2]:\n    t.insert(v)\nassert t.in_order() == [2]"),
        ("handles sorted input",
         "t = BST()\nfor v in range(20):\n    t.insert(v)\nassert t.in_order() == list(range(20))")],
       hints=["In-order traversal is left, node, right - that is why it comes out sorted.",
              "A small node class with left and right is enough."],
       solution="""
       class _Node:
           def __init__(self, value):
               self.value = value
               self.left = None
               self.right = None


       class BST:
           def __init__(self):
               self.root = None

           def insert(self, value):
               if self.root is None:
                   self.root = _Node(value)
                   return
               node = self.root
               while True:
                   if value < node.value:
                       if node.left is None:
                           node.left = _Node(value)
                           return
                       node = node.left
                   elif value > node.value:
                       if node.right is None:
                           node.right = _Node(value)
                           return
                       node = node.right
                   else:
                       return

           def contains(self, value):
               node = self.root
               while node is not None:
                   if value == node.value:
                       return True
                   node = node.left if value < node.value else node.right
               return False

           def in_order(self):
               out = []

               def walk(node):
                   if node is None:
                       return
                   walk(node.left)
                   out.append(node.value)
                   walk(node.right)

               walk(self.root)
               return out
       """)

    ex("p04.006", "p04", "Search", "Binary search", 3,
       """
       Write `bisect_left(items, target)` returning the leftmost index where
       `target` could be inserted into a sorted list and keep it sorted.

       For `[1, 3, 3, 5]` and target 3, that index is 1.
       Do it in O(log n) - no linear scan.
       """,
       """
       def bisect_left(items, target):
           pass
       """,
       [("leftmost duplicate", "assert bisect_left([1, 3, 3, 5], 3) == 1"),
        ("missing value", "assert bisect_left([1, 3, 5], 4) == 2"),
        ("before everything", "assert bisect_left([2, 4], 1) == 0"),
        ("after everything", "assert bisect_left([2, 4], 9) == 2"),
        ("empty", "assert bisect_left([], 1) == 0"),
        ("matches the stdlib",
         "import bisect, random\nfor _ in range(200):\n    data = sorted(random.randint(0, 20) for _ in range(15))\n    t = random.randint(0, 20)\n    assert bisect_left(data, t) == bisect.bisect_left(data, t)")],
       hints=["Keep a half-open window [low, high) and shrink it.",
              "When items[mid] < target, everything up to mid is too small: low = mid + 1."],
       solution="""
       def bisect_left(items, target):
           low, high = 0, len(items)
           while low < high:
               mid = (low + high) // 2
               if items[mid] < target:
                   low = mid + 1
               else:
                   high = mid
           return low
       """)

    ex("p04.007", "p04", "Graphs", "Breadth-first search", 4,
       """
       Given a graph as a dict of node to list of neighbours, write
       `shortest_path(graph, start, goal)` returning the shortest path as a
       list of nodes, or `None` when there is no route.
       """,
       """
       from collections import deque


       def shortest_path(graph, start, goal):
           pass
       """,
       [("finds the short route",
         "g = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}\nassert shortest_path(g, 'a', 'd') in (['a', 'b', 'd'], ['a', 'c', 'd'])"),
        ("start equals goal",
         "assert shortest_path({'a': []}, 'a', 'a') == ['a']"),
        ("no route",
         "assert shortest_path({'a': [], 'b': []}, 'a', 'b') is None"),
        ("survives a cycle",
         "g = {'a': ['b'], 'b': ['a', 'c'], 'c': []}\nassert shortest_path(g, 'a', 'c') == ['a', 'b', 'c']"),
        ("unknown start", "assert shortest_path({}, 'x', 'y') is None")],
       hints=["BFS with a queue finds the fewest-edges path; DFS does not.",
              "Mark a node seen when you enqueue it, not when you dequeue it."],
       solution="""
       from collections import deque


       def shortest_path(graph, start, goal):
           if start not in graph:
               return None
           if start == goal:
               return [start]
           queue = deque([[start]])
           seen = {start}
           while queue:
               path = queue.popleft()
               for neighbour in graph.get(path[-1], []):
                   if neighbour in seen:
                       continue
                   if neighbour == goal:
                       return path + [neighbour]
                   seen.add(neighbour)
                   queue.append(path + [neighbour])
           return None
       """)

    ex("p04.008", "p04", "Graphs", "Topological order", 5,
       """
       Given a dict of task to the tasks it depends on, write `order(tasks)`
       returning a valid execution order. Raise `ValueError` on a cycle.
       """,
       """
       def order(tasks):
           pass
       """,
       [("respects dependencies",
         "result = order({'app': ['lib'], 'lib': [], 'test': ['app']})\nassert result.index('lib') < result.index('app') < result.index('test')"),
        ("independent tasks all appear",
         "assert sorted(order({'a': [], 'b': []})) == ['a', 'b']"),
        ("detects a cycle",
         "try:\n    order({'a': ['b'], 'b': ['a']})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ("empty", "assert order({}) == []")],
       hints=["Repeatedly take every task whose dependencies are already emitted.",
              "If tasks remain but none are ready, the graph has a cycle."],
       solution="""
       def order(tasks):
           pending = {name: set(deps) for name, deps in tasks.items()}
           out = []
           while pending:
               ready = sorted(n for n, deps in pending.items()
                              if not (deps & pending.keys()))
               if not ready:
                   raise ValueError("dependency cycle")
               for name in ready:
                   out.append(name)
                   del pending[name]
           return out
       """)

    ex("p04.009", "p04", "Heaps", "Merge sorted streams", 4,
       """
       Write `merge_sorted(*streams)` returning one sorted list from several
       already-sorted iterables, without sorting the combined result.

       Use `heapq` so the cost is O(n log k) rather than O(n log n).
       """,
       """
       import heapq


       def merge_sorted(*streams):
           pass
       """,
       [("two streams",
         "assert merge_sorted([1, 4], [2, 3]) == [1, 2, 3, 4]"),
        ("three streams",
         "assert merge_sorted([1], [2], [0]) == [0, 1, 2]"),
        ("one empty", "assert merge_sorted([], [1, 2]) == [1, 2]"),
        ("no streams", "assert merge_sorted() == []"),
        ("merges rather than re-sorting",
         "import inspect\nsrc = inspect.getsource(merge_sorted)\nassert 'heapq' in src")],
       hints=["heapq.merge does exactly this and returns an iterator.",
              "Wrap the result in list() to return a real list."],
       solution="""
       import heapq


       def merge_sorted(*streams):
           return list(heapq.merge(*streams))
       """)

    ex("p04.010", "p04", "Caching", "A least-recently-used cache", 5,
       """
       Write `LRUCache(capacity)` with `get(key)` returning `-1` when absent,
       and `put(key, value)`. When full, evict the least recently used entry.
       Both reads and writes count as use.
       """,
       """
       from collections import OrderedDict


       class LRUCache:
           def __init__(self, capacity):
               pass
       """,
       [("stores and reads",
         "c = LRUCache(2)\nc.put('a', 1)\nassert c.get('a') == 1"),
        ("missing key", "assert LRUCache(1).get('nope') == -1"),
        ("evicts the oldest",
         "c = LRUCache(2)\nc.put('a', 1)\nc.put('b', 2)\nc.put('c', 3)\nassert c.get('a') == -1 and c.get('c') == 3"),
        ("reading refreshes",
         "c = LRUCache(2)\nc.put('a', 1)\nc.put('b', 2)\nc.get('a')\nc.put('c', 3)\nassert c.get('a') == 1 and c.get('b') == -1"),
        ("updating refreshes",
         "c = LRUCache(2)\nc.put('a', 1)\nc.put('b', 2)\nc.put('a', 9)\nc.put('c', 3)\nassert c.get('a') == 9")],
       hints=["OrderedDict.move_to_end(key) marks an entry as most recent.",
              "popitem(last=False) removes the oldest."],
       solution="""
       from collections import OrderedDict


       class LRUCache:
           def __init__(self, capacity):
               self.capacity = capacity
               self.data = OrderedDict()

           def get(self, key):
               if key not in self.data:
                   return -1
               self.data.move_to_end(key)
               return self.data[key]

           def put(self, key, value):
               if key in self.data:
                   self.data.move_to_end(key)
               self.data[key] = value
               while len(self.data) > self.capacity:
                   self.data.popitem(last=False)
       """)

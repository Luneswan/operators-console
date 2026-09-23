"""What an exercise wants, said the same way for all of them.

Prompts are hand-written and vary; what a beginner could not tell from them
was how the work is judged. People wrote `greet(anas)` under their function
because nothing said the checks call it for them, and read "returns the
string Hello, <name>!" without an example of the exact value. Everything
here is derived from data every exercise already has - the starter's `def`
lines, the checks' asserts, the solution's structure - so it is right for
all 119 exercises without rewriting any of them.
"""
from __future__ import annotations

import ast

EXAMPLE_LIMIT = 3
VALUE_LIMIT = 60


def entry_points(exercise) -> list[str]:
    """The functions and classes the starter asks for, in order."""
    try:
        tree = ast.parse(exercise.starter or "")
    except SyntaxError:
        return []
    return [node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef))]


def examples(exercise, limit: int = EXAMPLE_LIMIT) -> list[tuple[str, str]]:
    """(call, expected) pairs read from checks shaped `assert f(...) == v`.

    Only checks that call something the starter defines, with a short
    literal on the right, are used: those read as a worked example. Checks
    that inspect types, source or side effects are left for the grader.
    """
    names = set(entry_points(exercise))
    out: list[tuple[str, str]] = []
    for test in exercise.tests:
        pair = _example(getattr(test, "code", ""), names)
        if pair and pair not in out:
            out.append(pair)
        if len(out) >= limit:
            break
    return out


def _example(code: str, names: set) -> tuple[str, str] | None:
    try:
        tree = ast.parse(code.strip())
    except SyntaxError:
        return None
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assert):
        return None
    test = tree.body[0].test
    if not (isinstance(test, ast.Compare) and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)):
        return None
    left, right = test.left, test.comparators[0]
    if not (isinstance(left, ast.Call) and isinstance(left.func, ast.Name)
            and left.func.id in names):
        return None
    try:
        ast.literal_eval(right)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return None
    call, value = ast.unparse(left), ast.unparse(right)
    if len(call) > VALUE_LIMIT or len(value) > VALUE_LIMIT:
        return None
    return call, value


def how_checked(exercise) -> str:
    """One sentence on how the work is judged, naming the real function."""
    names = entry_points(exercise)
    if not names:
        return ("Write the code the task asks for. The checks run your file, "
                "then test what it defined.")
    shown = ", ".join("`%s`" % n for n in names[:3])
    return ("Write %s and leave it there: the checks use it themselves, with "
            "their own values, and compare what comes back. You do not need "
            "to call it, print it, or ask for input()."
            % (shown if len(names) == 1 else "these - " + shown))


# -- the shape of an answer ----------------------------------------------------


def skeleton(solution: str) -> str:
    """The solution's structure with every expression taken out.

    `def`, loops, branches, returns and the names being assigned stay; what
    they compute becomes `...`. It sits between the written hints and the
    full solution: enough to see how the answer is organised, nothing that
    can be typed in as it stands.
    """
    try:
        tree = ast.parse(solution or "")
    except SyntaxError:
        return ""
    lines: list[str] = []
    _walk(tree.body, 0, lines)
    out: list[str] = []
    for line in lines:
        if out and line.strip() == "..." and out[-1] == line:
            continue
        out.append(line)
    return "\n".join(out)


def _walk(body, depth: int, lines: list) -> None:
    pad = "    " * depth
    for node in body:
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            continue                                    # a docstring
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) \
                else "def"
            for deco in node.decorator_list:
                lines.append(pad + "@" + ast.unparse(deco))
            lines.append("%s%s %s(%s):" % (pad, prefix, node.name,
                                           ast.unparse(node.args)))
            _walk(node.body, depth + 1, lines)
        elif isinstance(node, ast.ClassDef):
            for deco in node.decorator_list:
                lines.append(pad + "@" + ast.unparse(deco))
            bases = ", ".join(ast.unparse(b) for b in node.bases)
            lines.append("%sclass %s%s:" % (pad, node.name,
                                            "(%s)" % bases if bases else ""))
            _walk(node.body, depth + 1, lines)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            lines.append("%sfor %s in ...:" % (pad, ast.unparse(node.target)))
            _walk(node.body, depth + 1, lines)
        elif isinstance(node, ast.While):
            lines.append(pad + "while ...:")
            _walk(node.body, depth + 1, lines)
        elif isinstance(node, ast.If):
            _if(node, depth, lines, "if")
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            names = [ast.unparse(i.optional_vars) for i in node.items
                     if i.optional_vars is not None]
            lines.append(pad + ("with ... as %s:" % ", ".join(names)
                                if names else "with ...:"))
            _walk(node.body, depth + 1, lines)
        elif isinstance(node, ast.Try):
            lines.append(pad + "try:")
            _walk(node.body, depth + 1, lines)
            for handler in node.handlers:
                kind = ast.unparse(handler.type) if handler.type else ""
                lines.append("%sexcept%s:" % (pad, " " + kind if kind else ""))
                _walk(handler.body, depth + 1, lines)
            if node.finalbody:
                lines.append(pad + "finally:")
                _walk(node.finalbody, depth + 1, lines)
        elif isinstance(node, ast.Return):
            lines.append(pad + ("return ..." if node.value is not None
                                else "return"))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            lines.append("%s%s = ..." % (pad, " = ".join(
                ast.unparse(t) for t in targets)))
        elif isinstance(node, ast.AugAssign):
            lines.append("%s%s %s= ..." % (pad, ast.unparse(node.target),
                                           _op(node.op)))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.append(pad + ast.unparse(node))
        elif isinstance(node, ast.Raise):
            lines.append(pad + "raise ...")
        elif isinstance(node, (ast.Pass, ast.Break, ast.Continue)):
            lines.append(pad + ast.unparse(node))
        elif isinstance(node, ast.Expr) and isinstance(
                node.value, (ast.Yield, ast.YieldFrom)):
            lines.append(pad + "yield ...")
        else:
            lines.append(pad + "...")


def _if(node: ast.If, depth: int, lines: list, word: str) -> None:
    pad = "    " * depth
    lines.append("%s%s ...:" % (pad, word))
    _walk(node.body, depth + 1, lines)
    if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
        _if(node.orelse[0], depth, lines, "elif")
    elif node.orelse:
        lines.append(pad + "else:")
        _walk(node.orelse, depth + 1, lines)


_OPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
        ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**", ast.BitOr: "|",
        ast.BitAnd: "&", ast.BitXor: "^", ast.LShift: "<<", ast.RShift: ">>",
        ast.MatMult: "@"}


def _op(op) -> str:
    return _OPS.get(type(op), "")

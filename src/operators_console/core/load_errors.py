"""Why a submission failed before any check could run, in plain words.

The grader runs the learner's file first and the checks after it. When the
file itself raises, every check is skipped and all the learner used to see
was Python's last line - `NameError: name 'anas' is not defined` - which
says what broke but not why, and never says the thing a beginner most needs
to hear: the checks call your function for you, so a call you added at the
bottom is both unnecessary and the reason nothing ran.

Pure and defensive: it reads the exception and the source text, and any
failure inside it degrades to "" rather than lose the run's result.
"""
from __future__ import annotations

import ast
import builtins
import difflib
import keyword

SUBMISSION_FILE = "your_code.py"


def explain_load_error(exc: BaseException, code: str) -> str:
    """A short paragraph for an error raised while loading the file."""
    try:
        return _explain(exc, code or "")
    except Exception:
        return ""


def _explain(exc: BaseException, code: str) -> str:
    if isinstance(exc, SyntaxError):
        return _syntax(exc, code)

    lines = code.splitlines()
    top, inner = _frames(exc)
    where = ""
    if top:
        source = lines[top - 1].strip() if 0 < top <= len(lines) else ""
        where = ("Line %d%s failed while the file was loading, so no checks "
                 "ran."
                 % (top, " (`%s`)" % source if source else ""))

    parts = []
    if isinstance(exc, NameError):
        parts.append(_name_error(exc, code, inside=bool(inner and inner != top)))
    if where:
        parts.append(where)
    call = _top_level_call(code, top)
    if call:
        parts.append(
            "Delete that line. The checks call `%s` themselves. Code outside "
            "your functions runs before any check, so an error there stops "
            "all of them." % call)
    # One paragraph per point: what is wrong, where, and what to do.
    return "\n\n".join(p for p in parts if p)


def _frames(exc: BaseException) -> tuple[int, int]:
    """(line in the file's top level, innermost line of the file)."""
    top = inner = 0
    tb = exc.__traceback__
    while tb is not None:
        frame_code = tb.tb_frame.f_code
        if frame_code.co_filename == SUBMISSION_FILE:
            if frame_code.co_name == "<module>" and not top:
                top = tb.tb_lineno
            inner = tb.tb_lineno
        tb = tb.tb_next
    return top, inner


def _top_level_call(code: str, line: int) -> str:
    """The function the learner called on `line` of the top level, if any."""
    if not line:
        return ""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ""
    defined = {n.name for n in tree.body
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef))}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Import, ast.ImportFrom)):
            continue
        if not node.lineno <= line <= getattr(node, "end_lineno", node.lineno):
            continue
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                    and sub.func.id in defined):
                return sub.func.id
    return ""


def _names_in(code: str) -> tuple[set, set]:
    """(every name the file binds anywhere, every function parameter)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set(), set()
    bound, params = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            bound.add(node.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.Lambda)):
            args = node.args
            for arg in (args.posonlyargs + args.args + args.kwonlyargs
                        + [a for a in (args.vararg, args.kwarg) if a]):
                params.add(arg.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        elif isinstance(node, ast.alias):
            bound.add((node.asname or node.name).split(".")[0])
    return bound, params


def _name_error(exc: NameError, code: str, inside: bool = False) -> str:
    name = getattr(exc, "name", "") or ""
    if not name:
        text = str(exc)
        start = text.find("'")
        end = text.find("'", start + 1)
        name = text[start + 1:end] if 0 <= start < end else ""
    if not name:
        return "Your file uses a name it never defines."
    bound, params = _names_in(code)
    known = bound | params | set(dir(builtins))

    # Inside a function its parameters are in reach, so `Name` for `name` is
    # a capital letter; at the top level a parameter is not what a bare word
    # was reaching for, and only names that exist out there count.
    reachable = bound | set(dir(builtins)) | (params if inside else set())
    same_but_case = [k for k in reachable
                     if k.lower() == name.lower() and k != name]
    if same_but_case:
        return ("`%s` is not defined. `%s` is. Python treats upper and lower "
                "case as different letters."
                % (name, same_but_case[0]))
    if name in params:
        return ("`%s` is a parameter. It only exists inside its function." % name)
    close = difflib.get_close_matches(name, sorted(known), n=1, cutoff=0.8)
    if close:
        return ("`%s` is not defined. Did you mean `%s`?"
                % (name, close[0]))
    if name.isidentifier() and not keyword.iskeyword(name):
        return ("`%s` has no quotes, so Python reads it as a variable, and no "
                "variable `%s` exists. If you meant the text %s, write "
                "`\"%s\"`." % (name, name, name, name))
    return "`%s` is used before it is given a value." % name


def _syntax(exc: SyntaxError, code: str) -> str:
    msg = (exc.msg or "").lower()
    line = exc.lineno or 0
    lines = code.splitlines()
    source = lines[line - 1].strip() if 0 < line <= len(lines) else ""
    at = "Line %d%s" % (line, " (`%s`)" % source if source else "")
    lead = ("%s is not valid Python, so the file did not run and no checks "
            "ran. " % at)
    if "expected ':'" in msg:
        return lead + ("Lines that start a block (`def`, `if`, `for`, "
                       "`while`, `class`) end with a colon.")
    if "indent" in msg:
        return lead + ("Every line in a block needs the same indent, usually "
                       "four spaces. An empty block needs `pass`.")
    if "never closed" in msg or "unmatched" in msg or "does not match" in msg:
        return lead + ("A bracket or quote is not closed, or is closed "
                       "without being opened. The mistake is often on the "
                       "line before.")
    if "unterminated string" in msg or "eol while scanning" in msg:
        return lead + ("A string is missing its closing quote.")
    if "forgot a comma" in msg:
        return lead + "Two values are missing a comma between them."
    if "'=' " in msg or "maybe you meant '=='" in msg or "cannot assign" in msg:
        return lead + ("`=` assigns. To compare, use `==`.")
    if "invalid character" in msg:
        return lead + ("It contains a character Python does not accept, often "
                       "a curly quote or dash pasted from a document. Retype "
                       "it.")
    return lead + "Python's message below says what it expected."

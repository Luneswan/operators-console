"""One way of deciding whether typed words match a piece of text.

Every search and filter box in the app goes through here, so they all agree:
Ctrl+K, the Practice and Journal filters, the Library filter and the Projects
filter. Before this they each did their own thing, and three boxes that look
identical behaved differently - two spaces broke one and not another, and
none of them found a title written with an en dash when a hyphen was typed.

The rules, applied to the text and to the query alike:

- Unicode is decomposed (NFKD) and combining marks are dropped, so "cafe"
  finds "café" and a non-breaking space is a space.
- Every dash and minus sign is a hyphen, and arrows are spelt the way they
  are typed: "->", "<-", "=>".
- Curly quotes are straight quotes.
- Case is folded (casefold, not lower: German "ß" matches "ss").
- The query is split on whitespace and every word has to appear, in any
  order. Nothing is a regular expression: "(", "*" and "[" are just
  characters.
"""
from __future__ import annotations

import re
import unicodedata

_DASHES = "‐‑‒–—―−﹘﹣－"

_TRANSLATE = {ord(ch): "-" for ch in _DASHES}
_TRANSLATE.update({
    ord("→"): "->", ord("⟶"): "->", ord("➔"): "->",
    ord("←"): "<-", ord("⟵"): "<-",
    ord("⇒"): "=>", ord("⟹"): "=>",
    ord("↔"): "<->",
    ord("‘"): "'", ord("’"): "'", ord("‚"): "'",
    ord("“"): '"', ord("”"): '"', ord("„"): '"',
    ord("­"): None,            # a soft hyphen is not a character
})


def fold(text) -> str:
    """Text reduced to what a search compares: see the module docstring."""
    decomposed = unicodedata.normalize("NFKD", str(text or ""))
    bare = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return bare.translate(_TRANSLATE).casefold()


def terms(query) -> tuple:
    """The words a query asks for, folded. Empty for a blank query."""
    return tuple(fold(query).split())


def haystack(*parts) -> str:
    """Several fields folded into one searchable string.

    The parts are joined with a newline, which no query word can contain,
    so a word can never match across the join between two fields.
    """
    return "\n".join(" ".join(fold(part).split()) for part in parts if part)


def contains(text: str, words) -> bool:
    """True when every word appears in an already folded `text`."""
    return all(word in text for word in words)


def matches(query, *parts) -> bool:
    """True when every word of `query` appears somewhere in `parts`.

    A blank query matches everything, as a cleared filter should.
    """
    words = terms(query)
    if not words:
        return True
    return contains(haystack(*parts), words)


def slug(text: str) -> str:
    """A name reduced to something stable enough to store it under.

    Shared by the Library, which files its read marks and its search targets
    under it, and by the search index, which has to name the same card.
    """
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-",
                                     str(text).lower())).strip("-")[:60]

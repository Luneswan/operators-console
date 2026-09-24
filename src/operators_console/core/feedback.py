"""Bug reports and requests, sent through GitHub by the learner.

The app never sends anything itself. It builds the text of an issue and a
link to GitHub's "new issue" page with that text filled in; the learner
reads it there and submits it from their own account, or copies the text
instead. System details are added only when the learner leaves the box
ticked, and they never include progress, notes or names.
"""
from __future__ import annotations

import platform
import sys
from urllib.parse import urlencode

from ..version import __version__

REPO = "Luneswan/operators-console"
NEW_ISSUE = "https://github.com/%s/issues/new" % REPO

#: (id, label, GitHub label, title prefix)
KINDS = (
    ("bug", "Report a bug", "bug", "Bug"),
    ("feature", "Request a feature", "enhancement", "Request"),
    ("content", "Report a mistake in the course", "content", "Content"),
    ("other", "Something else", "", "Feedback"),
)
#: Browsers and GitHub reject very long URLs; past this, the body is cut and
#: the learner is told to paste the full text from the clipboard.
URL_LIMIT = 7000


def system_details() -> str:
    return ("App version: %s\nOperating system: %s %s\nPython: %s"
            % (__version__, platform.system(), platform.release(),
               sys.version.split()[0]))


def issue_text(kind: str, title: str, details: str, include_system: bool,
               steps: str = "") -> tuple[str, str]:
    """(title, body) for the issue, in plain Markdown."""
    kinds = {k[0]: k for k in KINDS}
    if kind not in kinds:
        raise ValueError("unknown kind %r" % kind)
    title = " ".join((title or "").split())
    if not title:
        raise ValueError("Add a short title.")
    details = (details or "").strip()
    if not details:
        raise ValueError("Describe the problem or the request.")
    parts = ["## What happened" if kind == "bug" else "## Details", details]
    if kind == "bug" and steps.strip():
        parts += ["## Steps to reproduce", steps.strip()]
    if include_system:
        parts += ["## System", system_details()]
    return "%s: %s" % (kinds[kind][3], title), "\n\n".join(parts) + "\n"


def issue_url(kind: str, title: str, body: str) -> tuple[str, bool]:
    """GitHub's new-issue link with the text filled in.

    Returns (url, complete). When the body is too long for a URL, it is cut
    and `complete` is False: the learner pastes the full text instead.
    """
    label = {k[0]: k[2] for k in KINDS}.get(kind, "")

    def build(text):
        query = {"title": title, "body": text}
        if label:
            query["labels"] = label
        return NEW_ISSUE + "?" + urlencode(query)

    url = build(body)
    if len(url) <= URL_LIMIT:
        return url, True
    note = "\n\n(The rest is on the clipboard: paste it here.)\n"
    cut = len(body)
    while cut > 0 and len(build(body[:cut] + note)) > URL_LIMIT:
        cut -= max(1, (len(build(body[:cut] + note)) - URL_LIMIT) // 3)
    return build(body[:max(cut, 0)] + note), False

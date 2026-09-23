"""Every link the app ships: well-formed, and one name per destination.

The same page used to appear under two or three names across the Phase,
Library, Shelf and Field pages, so it looked like several resources; and the
older link test skipped certificate and field-library URLs entirely, while
the loader quietly turns a missing certificate URL into "".
"""
from __future__ import annotations

import re
from collections import defaultdict
from urllib.parse import urlsplit

import pytest

HOST = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


def _links(curriculum) -> list[tuple[str, str, str]]:
    """(where, name, url) for every link in the bundle."""
    out = []
    for phase in curriculum.phases:
        out += [("phase " + phase.id, r.name, r.url) for r in phase.resources]
    for group in curriculum.shelf:
        out += [("shelf " + group.group, i.name, i.url) for i in group.items]
    for group in curriculum.channels:
        out += [("channels " + group.group, i.name, i.url) for i in group.items]
    for field in curriculum.fields:
        out += [("field " + field.id, i.name, i.url) for i in field.libs]
    out += [("cert " + c.id, c.name, c.url) for c in curriculum.certs]
    return out


@pytest.fixture(scope="module")
def links(curriculum):
    return _links(curriculum)


def test_there_are_links_of_every_kind(links):
    kinds = {where.split()[0] for where, _name, _url in links}
    assert kinds == {"phase", "shelf", "channels", "field", "cert"}
    assert len(links) >= 300


def test_every_url_is_well_formed_https(links):
    for where, name, url in links:
        parts = urlsplit(url)
        assert parts.scheme == "https", (where, name, url)
        assert HOST.match(parts.hostname or ""), (where, name, url)
        assert not re.search(r"\s", url), (where, name, url)
        assert url == url.strip(), (where, name, url)


def test_every_link_has_a_name(links):
    for where, name, url in links:
        assert name.strip(), (where, url)
        assert name == name.strip(), (where, name)


def test_every_certificate_has_a_url(curriculum):
    for cert in curriculum.certs:
        assert cert.url.strip(), cert.id


def test_each_url_is_shown_under_exactly_one_name(links):
    names = defaultdict(set)
    for _where, name, url in links:
        names[url].add(name)
    clashes = {url: sorted(n) for url, n in names.items() if len(n) > 1}
    assert not clashes, clashes


def test_no_group_lists_the_same_page_twice(links):
    seen = defaultdict(list)
    for where, _name, url in links:
        seen[where].append(url)
    for where, urls in seen.items():
        assert len(urls) == len(set(urls)), where


def test_resource_blurbs_are_fragments_without_a_closing_full_stop(curriculum):
    """House style for phase resources: a headline fragment, no full stop."""
    for phase in curriculum.phases:
        for r in phase.resources:
            assert r.why.strip(), (phase.id, r.name)
            assert not r.why.rstrip().endswith("."), (phase.id, r.name, r.why)

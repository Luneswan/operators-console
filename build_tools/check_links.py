"""Check every link in the study guides answers.

    python build_tools/check_links.py            # guides only
    python build_tools/check_links.py --all      # plus phase resources

Network, so not part of the test suite. A link fails on a 404/410, a DNS
error or a timeout; 401/403/429 count as alive (sites that refuse robots).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALIVE = {200, 201, 202, 203, 204, 206, 301, 302, 303, 307, 308, 401, 403,
         405, 429}
AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def links(include_resources: bool) -> dict:
    found: dict = {}
    for file in sorted((HERE / "guides").glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        for item_id, guide in data.get("items", {}).items():
            for link in guide.get("where", ()):
                found.setdefault(link["url"], []).append(item_id)
    if include_resources:
        bundle = json.loads((HERE.parent / "src" / "operators_console" / "data"
                             / "curriculum.json").read_text(encoding="utf-8"))
        for phase in bundle["phases"]:
            for res in phase["resources"]:
                found.setdefault(res["url"], []).append(phase["id"])
    return found


def status(url: str) -> tuple:
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method,
                                         headers={"User-Agent": AGENT})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return url, response.status
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 404, 405, 501):
                continue            # some servers answer HEAD wrongly
            return url, exc.code
        except Exception as exc:    # report every failure
            if method == "HEAD":
                continue
            return url, type(exc).__name__
    return url, "no answer"


def main() -> int:
    found = links("--all" in sys.argv)
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(status, sorted(found)))
    bad = [(url, code) for url, code in results if code not in ALIVE]
    for url, code in bad:
        print("%s  %s  (%s)" % (code, url, ", ".join(found[url][:3])))
    print("%d links, %d bad" % (len(results), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

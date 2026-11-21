"""Every percent-encoded redirect source has its other-case twin.

Vercel matches the percent-encoded request path case-sensitively. WordPress
emits lowercase escapes (%e2%80%91) while browsers send uppercase (%E2%80%91),
so a rule written in one case 404s for the other. Measured on production
2026-11-21: five archive rules for Korean and U+2011 slugs had only the
lowercase form and their uppercase requests returned 404.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

VERCEL_CONFIG = Path(__file__).resolve().parents[2] / "vercel.json"
_PERCENT_ESCAPE = re.compile(r"%[0-9A-Fa-f]{2}")


def _with_case(source: str, case) -> str:
    return _PERCENT_ESCAPE.sub(lambda m: case(m.group(0)), source)


def test_encoded_sources_have_both_cases_with_the_same_destination():
    redirects = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))["redirects"]
    by_source = {rule["source"]: rule["destination"] for rule in redirects}
    missing = []
    for source, destination in by_source.items():
        if not _PERCENT_ESCAPE.search(source):
            continue
        for case in (str.lower, str.upper):
            twin = _with_case(source, case)
            if by_source.get(twin) != destination:
                missing.append(twin)
    assert not missing, sorted(set(missing))

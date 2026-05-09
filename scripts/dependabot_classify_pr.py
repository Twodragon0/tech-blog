#!/usr/bin/env python3
"""Fallback classifier for Dependabot PR titles.

Used by ``.github/workflows/dependabot-auto-merge.yml`` when
``dependabot/fetch-metadata`` returns ``update-type=null``. This happens
when the source requirement uses range syntax (``>=X.Y``) instead of a
pinned version, so dependabot can't determine semver classification on
its own.

Strategy: parse ``from <prev> to <new>`` from the PR title and compare
the major/minor/patch components. Strip leading version operators
(``>=``, ``~=``, ``==``, ``^``, ``~``).

Output (stdout): one of
- ``version-update:semver-patch``
- ``version-update:semver-minor``
- ``version-update:semver-major``
- empty string (cannot classify; treat as manual review)
"""

from __future__ import annotations

import re
import sys

_FROM_TO_RE = re.compile(
    r"from\s+([><=~!^]*[\d.]+[A-Za-z0-9.\-+]*)\s+to\s+([><=~!^]*[\d.]+[A-Za-z0-9.\-+]*)",
    re.IGNORECASE,
)
_OP_PREFIX_RE = re.compile(r"^[><=~!^]+")


def _parse_version(raw: str) -> tuple[int, ...]:
    """Strip leading operator and return numeric components.

    ``>=11.3.0`` -> (11, 3, 0)
    ``8.4.2`` -> (8, 4, 2)
    ``v1.2`` -> (1, 2)  (also handles a leading 'v')
    Non-numeric / pre-release suffixes are dropped: ``2.5.0rc1`` -> (2, 5, 0).
    """
    cleaned = _OP_PREFIX_RE.sub("", raw).lstrip("vV")
    parts: list[int] = []
    for part in cleaned.split(".")[:3]:
        m = re.match(r"\d+", part)
        if not m:
            break
        parts.append(int(m.group(0)))
    return tuple(parts)


def classify_pr_title(title: str) -> str:
    """Return semver classification or empty string when not classifiable."""
    if not title:
        return ""
    m = _FROM_TO_RE.search(title)
    if not m:
        return ""
    prev = _parse_version(m.group(1))
    new = _parse_version(m.group(2))
    if not prev or not new:
        return ""
    # Pad to 3 components for index-safe compare.
    prev = prev + (0,) * (3 - len(prev))
    new = new + (0,) * (3 - len(new))
    if new[0] != prev[0]:
        return "version-update:semver-major" if new[0] > prev[0] else ""
    if new[1] != prev[1]:
        return "version-update:semver-minor" if new[1] > prev[1] else ""
    if new[2] != prev[2]:
        return "version-update:semver-patch" if new[2] > prev[2] else ""
    return ""


def main(argv: list[str]) -> int:
    title = argv[1] if len(argv) > 1 else ""
    print(classify_pr_title(title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

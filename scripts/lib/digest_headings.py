#!/usr/bin/env python3
"""One definition of the digest reference heading, shared by producer and consumers.

The incident
------------
On 2026-09-19 `content_generator` started emitting a second spelling —
`## 관련 포스트 및 참고 자료` when cross-references exist, `## 참고 자료`
otherwise. Three consumers matched the old spelling as an exact string:

    scripts/enrich_digest_references.py        REFERENCE_HEADING = "## 참고 자료"
    scripts/backfill_digest_native_sections.py _REFS_HEADING     = "## 참고 자료"
    scripts/backfill_digest_structure.py       boundary regex alternation

The variant does NOT contain the old string as a substring, so all three went
blind to it. Measured the same day: 13 posts already carried the variant and
**all 13** lacked `## 참고 자료` entirely — `enrich_digest_references` reported
the section as absent on every one.

This is the failure CLAUDE.md names outright: *a content gate keyed to one exact
string is blind to the variant*. The fix is not "add the second string in three
places" — that is the same defect with a longer list. It is one definition that
the generator and every consumer read, so a third spelling cannot be introduced
on one side alone.

Usage
-----
Producers pick a spelling from :data:`REFERENCE_HEADINGS`. Consumers locate the
section with :func:`is_reference_heading` or :data:`REFERENCE_HEADING_RE`, never
with a literal.
"""

from __future__ import annotations

import re

__all__ = [
    "REFERENCE_HEADING",
    "REFERENCE_HEADING_WITH_POSTS",
    "REFERENCE_HEADINGS",
    "REFERENCE_HEADING_RE",
    "REFERENCE_HEADING_ALTERNATION",
    "is_reference_heading",
]

#: The plain spelling, used when a digest has no cross-references to sibling posts.
REFERENCE_HEADING = "## 참고 자료"

#: Used when `content_generator._get_recent_digest_links` found sibling digests.
REFERENCE_HEADING_WITH_POSTS = "## 관련 포스트 및 참고 자료"

#: Every spelling a digest may legitimately carry. Add here — and only here.
REFERENCE_HEADINGS = (REFERENCE_HEADING_WITH_POSTS, REFERENCE_HEADING)

#: The bare ``a|b`` fragment, for callers that splice it into a larger pattern.
#: The longer spelling is first so alternation prefers it — with the short one
#: first, ``## 관련 포스트 및 참고 자료`` would never match as a whole.
REFERENCE_HEADING_ALTERNATION = "|".join(re.escape(h) for h in REFERENCE_HEADINGS)

#: Anchored at line start so a mention inside prose or a table cell is not a
#: section header.
REFERENCE_HEADING_RE = re.compile(
    r"^(?:" + REFERENCE_HEADING_ALTERNATION + r")\s*$",
    re.M,
)


def is_reference_heading(line: str) -> bool:
    """True when `line` is a digest reference-section header, either spelling."""
    return line.strip() in REFERENCE_HEADINGS

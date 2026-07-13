#!/usr/bin/env python3
"""CSP inline-script sha256 regression gate.

Prep for CSP "Path B" (removing ``'unsafe-inline'`` from ``script-src``): once
that lands, the first-party inline ``<script>`` blocks in
``_includes/head.html`` are allow-listed by sha256 hash instead of the blanket
``'unsafe-inline'`` keyword. Any whitespace/content edit to those inline
scripts silently changes the hash the browser computes, which would break the
future Path B CSP without anyone noticing at review time.

This gate:

1. Parses ``_includes/head.html`` and extracts every first-party *executable*
   inline ``<script>`` — i.e. a ``<script>`` with an inline body and no
   ``src`` attribute. ``type="application/ld+json"`` data blocks and any
   external-``src`` scripts are excluded (CSP hashing only applies to
   executable script content).
2. Computes the base64 sha256 of each inline script's raw text-node content —
   exactly the bytes the browser hashes (no surrounding tag, no whitespace
   trimming).
3. Compares against the checked-in manifest ``scripts/dev/csp_inline_hashes.json``
   (label -> ``sha256-...``) and fails with a clear diff on any drift.

Extraction correctness is validated against two known-good hashes (see
``scripts/tests/test_csp_inline_hashes.py``):

- ``theme-init`` (the FOUC-prevention IIFE, ``<script id="theme-init">``)
  -> ``sha256-FiF+gbNVa7+4pSSr/iRRyau5vRAaG7O6j/jhduKyItE=``
- the deferred-CSS loader IIFE (no ``id`` attribute, second qualifying
  inline script in document order) -> ``sha256-bJASvghY1rpfB3ScKAFDDJoFiYeDK3Cu+aVj0ferf98=``

HTML comments are stripped before scanning for ``<script>`` tags: head.html
has a comment block that mentions ``<script async src="gtag/js?id=...">`` as
prose (documenting a script tag that was removed); without stripping
comments first, a naive regex scan misparses tag boundaries around that
comment. Stripping comments first was verified to reproduce both known-good
hashes exactly.

Usage:
    python3 scripts/dev/check_csp_inline_hashes.py            # check gate
    python3 scripts/dev/check_csp_inline_hashes.py --update   # regenerate manifest
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parent.parent.parent
DEFAULT_HEAD_HTML = REPO / "_includes" / "head.html"
DEFAULT_MANIFEST = REPO / "scripts" / "dev" / "csp_inline_hashes.json"

# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

import re

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
_SRC_ATTR_RE = re.compile(r"\bsrc\s*=", re.IGNORECASE)
_LDJSON_ATTR_RE = re.compile(
    r"""type\s*=\s*["']application/ld\+json["']""", re.IGNORECASE
)
_ID_ATTR_RE = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


class InlineScript(NamedTuple):
    label: str
    content: str


def extract_inline_scripts(html: str) -> list[InlineScript]:
    """Return every first-party executable inline ``<script>`` in *html*.

    Excludes scripts with a ``src`` attribute and ``application/ld+json``
    data blocks. HTML comments are stripped first so prose that merely
    *mentions* a ``<script ...>`` tag (e.g. inside a code-comment explaining
    a removed tag) is not mistaken for a real tag boundary.

    Label: the script's ``id`` attribute if present, otherwise
    ``inline-script-N`` where N is the 1-based ordinal among qualifying
    inline scripts in document order.
    """
    no_comments = _COMMENT_RE.sub("", html)
    results: list[InlineScript] = []
    ordinal = 0
    for match in _SCRIPT_RE.finditer(no_comments):
        attrs, body = match.group(1), match.group(2)
        if _SRC_ATTR_RE.search(attrs):
            continue
        if _LDJSON_ATTR_RE.search(attrs):
            continue
        ordinal += 1
        id_match = _ID_ATTR_RE.search(attrs)
        label = id_match.group(1) if id_match else f"inline-script-{ordinal}"
        results.append(InlineScript(label=label, content=body))
    return results


def compute_hash(content: str) -> str:
    """Return the CSP ``sha256-...`` token for *content* (utf-8, raw bytes)."""
    digest = hashlib.sha256(content.encode("utf-8")).digest()
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def compute_current_hashes(html: str) -> dict[str, str]:
    """Return ``{label: sha256-token}`` for every qualifying inline script."""
    return {s.label: compute_hash(s.content) for s in extract_inline_scripts(html)}


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------


def load_manifest(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.exists():
        return {}
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest_path: Path, hashes: dict[str, str]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")


# ---------------------------------------------------------------------------
# Diff / gate
# ---------------------------------------------------------------------------


def diff_hashes(
    current: dict[str, str], manifest: dict[str, str]
) -> list[str]:
    """Return a list of human-readable problem descriptions; empty = clean."""
    problems: list[str] = []

    for label, actual in sorted(current.items()):
        expected = manifest.get(label)
        if expected is None:
            problems.append(
                f"NEW inline script (not in manifest): {label}\n"
                f"    computed: {actual}\n"
                f"    Run with --update to add it to the manifest "
                f"(after reviewing the change)."
            )
        elif expected != actual:
            problems.append(
                f"MISMATCH: {label}\n"
                f"    expected: {expected}\n"
                f"    actual:   {actual}\n"
                f"    CSP token to paste: '{actual}'\n"
                f"    Run with --update to accept this change (after reviewing it)."
            )

    for label in sorted(set(manifest) - set(current)):
        problems.append(
            f"REMOVED: manifest entry no longer present in head.html: {label}\n"
            f"    was: {manifest[label]}\n"
            f"    Run with --update to remove it from the manifest."
        )

    return problems


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "CSP inline-script sha256 regression gate for _includes/head.html. "
            "Fails when a first-party inline <script> changes without the "
            "checked-in manifest being updated to match."
        )
    )
    parser.add_argument(
        "--head",
        type=Path,
        default=DEFAULT_HEAD_HTML,
        help="Path to head.html (default: _includes/head.html).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the hash manifest JSON (default: scripts/dev/csp_inline_hashes.json).",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Regenerate the manifest from the current head.html and exit 0.",
    )
    args = parser.parse_args(argv)

    if not args.head.exists():
        print(f"[csp-inline-hash] ERROR: {args.head} not found.", file=sys.stderr)
        return 2

    html = args.head.read_text(encoding="utf-8")
    current = compute_current_hashes(html)

    if args.update:
        save_manifest(args.manifest, current)
        print(f"[csp-inline-hash] Updated manifest: {args.manifest}")
        for label, token in sorted(current.items()):
            print(f"  {label}: {token}")
        return 0

    manifest = load_manifest(args.manifest)
    if not manifest:
        print(
            f"[csp-inline-hash] ERROR: manifest {args.manifest} missing or empty. "
            f"Run with --update to seed it after reviewing head.html.",
            file=sys.stderr,
        )
        return 1

    problems = diff_hashes(current, manifest)
    if problems:
        print(
            f"[csp-inline-hash] FAIL — {len(problems)} inline-script hash "
            f"drift issue(s) in {args.head}:\n",
            file=sys.stderr,
        )
        for p in problems:
            print(f"  - {p}\n", file=sys.stderr)
        return 1

    print(
        f"[csp-inline-hash] OK — {len(current)} inline script(s) match the "
        f"manifest ({args.manifest})."
    )
    for label, token in sorted(current.items()):
        print(f"  {label}: {token}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

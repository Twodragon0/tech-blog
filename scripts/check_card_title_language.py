#!/usr/bin/env python3
"""Require news-card `title=` values to be Korean, with an explicit allow-list.

This blog is Korean and its card titles are faithful translations of the source
headline with proper nouns left in English — e.g. "ToxicPanda Android 악성코드,
VPN 권한 악용해 Google Play 차단". Measured 2026-08-24 before this gate landed:
2261 Korean titles vs 51 English ones (2.2 %), so the English ones were drift,
not a citation convention. All 48 translatable ones were translated; the three
that remain are pure proper-noun strings with nothing to translate.

Why a dedicated gate instead of reusing check_digest_untranslated.py
-------------------------------------------------------------------
That script's `is_untranslated()` deliberately exempts cited English titles and
Title-Cased proper-noun runs, because it inspects *prose summaries* where an
embedded English article title is legitimate. Run over these 51 titles it
flagged **1**. It is the right heuristic for its own job and the wrong one here,
so this gate uses the opposite shape: deny by default, allow by exact string —
the same pattern check_digest_proper_nouns.py uses for entity spellings.

Every allow-list entry carries its reason. An entry without one is how a
deny-by-default list quietly becomes a deny-nothing list.

The `[클라우드]`-style bracket prefix is stripped before the check: those labels
are already Korean and would otherwise satisfy the Hangul test for a fully
English title.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

_TITLE_RE = re.compile(r'title="([^"]+)"')
_LABEL_RE = re.compile(r"^\[[^\]]*\]\s*")
_HANGUL_RE = re.compile(r"[가-힣]")

# Titles allowed to stay English, with the reason. Keep this list short: if it
# starts absorbing real headlines, the gate has stopped meaning anything.
ENGLISH_TITLE_ALLOW: Dict[str, str] = {
    "[클라우드] Google ADK + Datadog LLM Observability":
        "product names only (Google ADK, Datadog LLM Observability) — nothing to translate",
    "[DevOps] KubeCon Europe 2026 Open Source SecurityCon":
        "event names; KubeCon and Open Source SecurityCon are not translated in Korean coverage",
    "I/O 2026":
        "Google's conference name",
}


def normalize(text: str) -> str:
    """Whitespace/Unicode-normalized form used for allow-list lookup.

    RSS feeds deliver U+00A0 (and friends) that render identically to a space.
    One 2026-02-05 title carried two of them, which silently defeated exact
    string matching during the translation pass — so the allow-list is keyed on
    the normalized form rather than the raw bytes.
    """
    for ch in (" ", " ", " ", " "):
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


_ALLOW_NORMALIZED = {normalize(k): v for k, v in ENGLISH_TITLE_ALLOW.items()}


def offending_titles(text: str) -> List[str]:
    """Card titles with no Hangul that are not on the allow-list."""
    out = []
    for m in _TITLE_RE.finditer(text):
        raw = m.group(1)
        if normalize(raw) in _ALLOW_NORMALIZED:
            continue
        if not _HANGUL_RE.search(_LABEL_RE.sub("", raw)):
            out.append(raw)
    return out


def staged_posts() -> List[Path]:
    res = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "--", "_posts"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return [
        REPO_ROOT / line
        for line in res.stdout.split("\n")
        if line.strip().endswith(".md") and (REPO_ROOT / line).exists()
    ]


def scan(paths) -> Tuple[List[str], int]:
    violations, checked = [], 0
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        titles = _TITLE_RE.findall(text)
        if not titles:
            continue
        checked += len(titles)
        for bad in offending_titles(text):
            violations.append(f"{path.name}: {bad}")
    return violations, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true", help="scan every post (default)")
    scope.add_argument("--staged", action="store_true", help="scan staged posts only")
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    args = parser.parse_args()

    corpus = sorted(POSTS_DIR.glob("*.md"))
    if not corpus:
        print("[card-title-language] no posts found", file=sys.stderr)
        return 1

    scoped = staged_posts() if args.staged else corpus
    if args.staged and not scoped:
        print("[card-title-language] no staged posts — nothing to check.")
        return 0

    violations, checked = scan(scoped)

    if violations:
        print(
            "[card-title-language] FAIL — these card titles have no Korean text.\n"
            "Card titles are faithful translations of the source headline with\n"
            "proper nouns left in English. If a title is genuinely untranslatable\n"
            "(a pure product or event name), add it to ENGLISH_TITLE_ALLOW in\n"
            "scripts/check_card_title_language.py WITH ITS REASON.\n",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(f"\n{len(violations)} violation(s).", file=sys.stderr)
        return 1

    if not args.quiet:
        print(
            f"[card-title-language] OK — {checked} card title(s) across "
            f"{len(scoped)} post(s), {len(ENGLISH_TITLE_ALLOW)} allow-listed, "
            "0 violations."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

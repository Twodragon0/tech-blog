"""Restore the sentence-final period on already-published news-card summaries.

PR #511 fixed the generator (``_korean_brief_summary``'s ``.strip(" .")`` ate a
legitimate final period), but the 16 cards already in the corpus stayed
unterminated. This applies the SAME helper to existing ``summary="…"`` values —
importing it rather than re-implementing, so the corpus and the generator cannot
drift apart.

This edits inside a Liquid include, which is precisely where a context-blind
rewrite corrupted three cover images during PR #509. The contract is therefore
deliberately narrow and enforced at runtime: the ONLY change a file may receive
is a ``.`` appended to a ``summary`` value. Anything else aborts.

A summary that ends on a noun ("…취약점 탐지, 검증, 수정 제안") comes from a
headline-shaped source; the helper leaves it alone, because a period there would
be wrong Korean.

Usage:
    python3 scripts/backfill_card_summary_period.py --posts-glob '_posts/*Weekly_Digest*.md' --dry-run
    python3 scripts/backfill_card_summary_period.py _posts/2026-07-*.md
"""

import argparse
import glob
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.news.content_generator import _restore_sentence_period  # noqa: E402
from scripts.news_card_patterns import CARD_RE as _CARD_RE  # noqa: E402
from scripts.news_card_patterns import SUMMARY_RE as _SUMMARY_RE  # noqa: E402

restore = _restore_sentence_period

# Summaries at/over this length came from the pre-#506 hard 200-char cap and are
# cut mid-thought. Some end on a sentence-ending morpheme by coincidence, so the
# helper would happily punctuate them — making a truncation LOOK complete and
# hiding the very defect #506 fixed. Those 9 cards need a re-summary from the
# source article, not a period, so this backfill leaves them alone.
TRUNCATION_SUSPECT_LEN = 195


def _fix_card(card: str) -> str:
    def _sub(m):
        value = m.group(2)
        if len(value.strip()) >= TRUNCATION_SUSPECT_LEN:
            return m.group(0)
        return m.group(1) + restore(value) + m.group(3)

    return _SUMMARY_RE.sub(_sub, card)


def transform(text: str) -> str:
    return _CARD_RE.sub(lambda m: _fix_card(m.group(0)), text)


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def _violates_narrow_diff(old: str, new: str) -> bool:
    """True unless every difference is a '.' APPENDED to a summary value.

    Normalising both sides alone is not enough: it would also accept a period
    being REMOVED, since both collapse to the same text. The length check pins
    the direction — this transform may only add characters.
    """
    if len(new) < len(old):
        return True
    return new.replace('."', '"') != old.replace('."', '"')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Backfill card-summary periods.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    files = [f for f in files if _is_digest_post(f)]
    if not files:
        print("[backfill-period] no digest post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            continue
        if _violates_narrow_diff(original, new):
            print(f"ABORT {f}: change is not a bare appended period", file=sys.stderr)
            return 1
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[backfill-period] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

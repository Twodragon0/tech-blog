"""Rewind mid-sentence card summaries to their last complete sentence.

PR #506 fixed the generator's blind ``ko_summary[:200]`` slice, but the summaries
already published stayed cut mid-word ("…Java 바이트 스트림 역"). Measured
2026-08-07: 128 such summaries across 79 digests.

Chosen over re-summarising from the source article because rewinding is free of
the two costs that matter here — it makes no network call and invents no text.
The result is always a PREFIX of what was published, so there is nothing to
fact-check: 132 chars survive on average (66% of 200), and 126 of the 128 keep
at least one complete sentence. The other 2 have no sentence boundary at all and
are left exactly as they are; emptying them would be worse than a rough tail.

Only the trailing partial sentence is dropped, and the runtime contract enforces
that a file may only ever shrink — this edits inside a Liquid include, the same
place a context-blind rewrite corrupted cover images in PR #509.

Usage:
    python3 scripts/rewind_truncated_summaries.py --posts-glob '_posts/*Weekly_Digest*.md' --dry-run
    python3 scripts/rewind_truncated_summaries.py _posts/2026-04-*.md
"""
import argparse
import glob
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.news_card_patterns import CARD_RE as _CARD_RE  # noqa: E402
from scripts.news_card_patterns import SUMMARY_RE as _SUMMARY_RE  # noqa: E402

# Below this a summary was never near the old 200-char cap, so a missing final
# period is a headline-shaped source, not truncation — not this script's job.
TRUNCATION_SUSPECT_LEN = 195

_TERMINATED = (".", "!", "?")


def rewind(text: str) -> str:
    """Drop the trailing partial sentence. Returns a prefix, or text unchanged."""
    if not text or text.endswith(_TERMINATED):
        return text
    idx = text.rfind("다.")
    return text[: idx + 2] if idx > 0 else text


def _fix_card(card: str) -> str:
    def _sub(m):
        value = m.group(2)
        if len(value.strip()) < TRUNCATION_SUSPECT_LEN:
            return m.group(0)
        return m.group(1) + rewind(value.strip()) + m.group(3)

    return _SUMMARY_RE.sub(_sub, card)


def transform(text: str) -> str:
    return _CARD_RE.sub(lambda m: _fix_card(m.group(0)), text)


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def _violates_shrink_only(old: str, new: str) -> bool:
    """This transform may only remove characters, never add or rewrite."""
    return len(new) > len(old)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Rewind truncated card summaries.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    files = [f for f in files if _is_digest_post(f)]
    if not files:
        print("[rewind-summaries] no digest post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            continue
        if _violates_shrink_only(original, new):
            print(f"ABORT {f}: rewind grew the file", file=sys.stderr)
            return 1
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[rewind-summaries] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

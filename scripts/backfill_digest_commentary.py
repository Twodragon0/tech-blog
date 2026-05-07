#!/usr/bin/env python3
"""Backfill `## 분석가 시점` commentary into existing digest posts.

Iterates `_posts/*.md` files (filtered by date prefix and digest filename
pattern), parses headlines from the rendered news sections, then invokes
`_generate_unique_post_commentary` to produce a per-post 1-paragraph
analyst commentary. Inserts it between the `## 위험 스코어카드` block and
the next `## ` section (typically `## 1. 보안 뉴스`).

Idempotent: posts that already contain a `## 분석가 시점` section are
skipped.

Usage
-----
    # Dry-run on the most recent 5 digest posts (no writes, prints sample).
    python3 scripts/backfill_digest_commentary.py --dry-run --limit 5

    # Apply to posts newer than 60 days, up to 30 files.
    python3 scripts/backfill_digest_commentary.py --since 60 --limit 30

    # Use a fake commentary string instead of calling LLM (test/demo).
    python3 scripts/backfill_digest_commentary.py --no-llm --dry-run --limit 3

    # Target a specific glob.
    python3 scripts/backfill_digest_commentary.py \
        --posts-glob '_posts/2026-04-2*-Tech_Security_Weekly_Digest_*.md' \
        --dry-run

Exit codes
----------
    0  Completed (with or without changes).
    1  CLI error (invalid args, no matches, etc.).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- Path setup so we can import scripts.news.* ---
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger("backfill_digest_commentary")

# Default glob (only digest posts, not consolidation/index pages).
_DEFAULT_POSTS_GLOB = "_posts/*-Tech_Security_Weekly_Digest_*.md"

# Headline extraction regexes.
_H3_HEADLINE_RE = re.compile(r"^###\s+(?:\d+\.\d+\s+)?(.+?)\s*$", re.MULTILINE)
_LINK_TITLE_RE = re.compile(r"\*\*\[([^\]]+)\]\([^)]+\)\*\*")

# Commentary section anchor.
_COMMENTARY_HEADER = "## 분석가 시점"
_RISK_SCORECARD_HEADER = "## 위험 스코어카드"


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill analyst commentary into digest posts.",
    )
    parser.add_argument(
        "--since",
        type=int,
        default=60,
        help="Only consider posts whose date prefix is within N days of today (default: 60).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of posts to process (default: 100).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write changes; print previews to stdout.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Do not invoke any LLM. Use a deterministic fake commentary (testing).",
    )
    parser.add_argument(
        "--posts-glob",
        default=_DEFAULT_POSTS_GLOB,
        help=f"Glob pattern for post files (default: {_DEFAULT_POSTS_GLOB}).",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Apply changes (write files). If neither --commit nor --dry-run is set, "
        "behavior defaults to dry-run for safety.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging.",
    )
    return parser.parse_args(argv)


def _filter_by_date(paths: List[Path], since_days: int) -> List[Path]:
    """Keep posts whose YYYY-MM-DD prefix is within the last `since_days` days."""
    cutoff = _dt.date.today() - _dt.timedelta(days=since_days)
    out: List[Path] = []
    for p in paths:
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", p.name)
        if not m:
            continue
        try:
            post_date = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if post_date >= cutoff:
            out.append(p)
    return out


def _extract_frontmatter_and_body(text: str) -> Tuple[str, str]:
    """Split a Jekyll post into (front_matter_with_fences, body)."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    fm_block = text[: end + 4]  # include the closing '\n---'
    # Skip past the trailing newline if present.
    body_start = end + 4
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    return fm_block, text[body_start:]


def _has_commentary(body: str) -> bool:
    return bool(re.search(r"^## 분석가 시점\s*$", body, re.MULTILINE))


def _extract_headlines_from_body(body: str, max_n: int = 3) -> List[Dict[str, str]]:
    """Extract up to N headlines from a digest post body.

    Strategy:
      1. Try H3 headers under the news sections (### N.M Title format).
      2. Fall back to bold link titles in the body (**[Title](URL)**).
    """
    headlines: List[Dict[str, str]] = []

    # Strategy 1: H3 headlines that look like real news titles.
    for m in _H3_HEADLINE_RE.finditer(body):
        title = m.group(1).strip()
        # Skip standard sub-section headers.
        if not title or title in {
            "기술적 배경 및 위협 분석",
            "실무 영향 분석",
            "대응 체크리스트",
            "이번 주 하이라이트",
        }:
            continue
        if len(title) < 8:
            continue
        headlines.append({"title": title, "source": "", "category": "security"})
        if len(headlines) >= max_n:
            break

    if headlines:
        return headlines

    # Strategy 2: bold-link titles.
    for m in _LINK_TITLE_RE.finditer(body):
        title = m.group(1).strip()
        if len(title) < 8:
            continue
        headlines.append({"title": title, "source": "", "category": "security"})
        if len(headlines) >= max_n:
            break

    return headlines


def _build_fake_commentary(date_str: str, headlines: List[Dict[str, str]]) -> str:
    """Produce a deterministic fake commentary for --no-llm mode (test only)."""
    headline_phrase = "여러 보안 신호"
    if headlines:
        first = headlines[0]["title"][:40]
        headline_phrase = f"'{first}' 등 헤드라인"
    return (
        f"이번 분석 사이클에서 가장 먼저 눈에 띄는 신호는 {headline_phrase}이며, "
        "DevSecOps 실무자는 인터넷 노출 자산의 패치 SLA와 "
        "탐지 룰 우선순위를 같은 주기로 점검해야 한다. **노출 자산 인벤토리**를 "
        "기준으로 패치, SIEM 룰, 백업 무결성을 한 사이클 안에 회전시키는 운영 "
        "리듬이 이번 주기의 가장 실질적인 개선 레버리지가 된다."
    )


def _insert_commentary(body: str, commentary: str) -> str:
    """Insert the commentary section after `## 위험 스코어카드` block.

    The block extends until the next `## ` header (or `---`). We find the
    end of the scorecard block and inject the commentary section before
    the next H2.
    """
    # Find the position of the scorecard header.
    sc_match = re.search(r"^## 위험 스코어카드\s*$", body, re.MULTILINE)
    if not sc_match:
        # Fallback: insert before the first numbered news section.
        first_h2 = re.search(r"^## \d+\.\s+", body, re.MULTILINE)
        if not first_h2:
            return body  # no anchor found
        injection_pos = first_h2.start()
    else:
        # Find the next H2 after the scorecard header.
        sc_end = sc_match.end()
        next_h2 = re.search(r"^## ", body[sc_end:], re.MULTILINE)
        if not next_h2:
            # No following H2; append at end.
            injection_pos = len(body)
        else:
            injection_pos = sc_end + next_h2.start()

    block = f"{_COMMENTARY_HEADER}\n\n{commentary}\n\n"
    return body[:injection_pos] + block + body[injection_pos:]


def _update_last_modified_at(fm_block: str) -> str:
    """Set or insert `last_modified_at: <ISO timestamp>` in the front matter."""
    now_iso = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0900")
    if re.search(r"^last_modified_at:\s*", fm_block, re.MULTILINE):
        return re.sub(
            r"^last_modified_at:.*$",
            f"last_modified_at: {now_iso}",
            fm_block,
            count=1,
            flags=re.MULTILINE,
        )
    # Insert before the closing fence.
    closing = fm_block.rfind("\n---")
    if closing == -1:
        return fm_block
    return (
        fm_block[:closing]
        + f"\nlast_modified_at: {now_iso}"
        + fm_block[closing:]
    )


def _generate_commentary_for_post(
    post_path: Path,
    body: str,
    no_llm: bool,
) -> Optional[str]:
    """Produce a commentary string for a post, or None if not possible."""
    headlines = _extract_headlines_from_body(body, max_n=3)
    if not headlines:
        logger.warning("%s: no headlines extracted, skipping", post_path.name)
        return None

    # Date prefix from filename.
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-", post_path.name)
    date_str = m.group(1) if m else _dt.date.today().isoformat()

    if no_llm:
        return _build_fake_commentary(date_str, headlines)

    # Lazy import so --no-llm path doesn't trigger heavy imports.
    from scripts.news.content_generator import _generate_unique_post_commentary

    commentary = _generate_unique_post_commentary(
        headlines,
        date_str,
        mode="security",
        seed=date_str,
    )
    return commentary


def process_post(
    post_path: Path,
    *,
    dry_run: bool,
    no_llm: bool,
) -> Tuple[bool, str]:
    """Process a single post.

    Returns (changed, message). `changed` is True when a write would
    have occurred (or did occur, when not dry-run).
    """
    text = post_path.read_text(encoding="utf-8")
    fm_block, body = _extract_frontmatter_and_body(text)

    if _has_commentary(body):
        return False, "already has commentary"

    commentary = _generate_commentary_for_post(post_path, body, no_llm=no_llm)
    if not commentary:
        return False, "commentary generation failed"

    new_body = _insert_commentary(body, commentary)
    if new_body == body:
        return False, "no insertion anchor"

    new_fm = _update_last_modified_at(fm_block) if fm_block else fm_block
    new_text = (new_fm + "\n" + new_body) if new_fm else new_body

    if dry_run:
        return True, commentary

    post_path.write_text(new_text, encoding="utf-8")
    return True, "written"


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Default to dry-run when neither flag is given (safety).
    dry_run = args.dry_run or not args.commit
    if not args.dry_run and not args.commit:
        logger.warning(
            "Neither --dry-run nor --commit given; defaulting to dry-run."
        )

    matches = sorted(glob.glob(args.posts_glob), reverse=True)
    if not matches:
        logger.error("No posts matched glob: %s", args.posts_glob)
        return 1

    paths = [Path(p) for p in matches]
    paths = _filter_by_date(paths, args.since)
    if not paths:
        logger.warning(
            "No posts within %d days of today (glob=%s)",
            args.since,
            args.posts_glob,
        )
        return 0

    paths = paths[: args.limit]
    logger.info("Considering %d posts (limit=%d)", len(paths), args.limit)

    changed = 0
    skipped = 0
    failed = 0
    samples: List[Tuple[str, str]] = []

    for path in paths:
        try:
            did_change, message = process_post(
                path,
                dry_run=dry_run,
                no_llm=args.no_llm,
            )
        except Exception as e:
            logger.exception("%s: error during processing: %s", path.name, e)
            failed += 1
            continue

        if did_change:
            changed += 1
            samples.append((path.name, message))
            mode_word = "[DRY-RUN]" if dry_run else "[APPLIED]"
            logger.info("%s %s: %s", mode_word, path.name, message[:60] + "...")
        else:
            skipped += 1
            logger.debug("[SKIP] %s: %s", path.name, message)

    # Print samples for human review (dry-run mode only).
    if dry_run and samples:
        print("\n" + "=" * 78)
        print(f"  Sample commentary previews ({len(samples)} files)")
        print("=" * 78)
        for name, commentary in samples:
            print(f"\n--- {name} ---")
            print(commentary)
            print(f"({len(commentary)} chars)")
        print("\n" + "=" * 78)

    logger.info(
        "Summary: changed=%d skipped=%d failed=%d (dry_run=%s, no_llm=%s)",
        changed,
        skipped,
        failed,
        dry_run,
        args.no_llm,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

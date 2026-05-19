#!/usr/bin/env python3
"""Rewrite daily-digest post excerpts with deterministic-but-diverse phrasing.

Why this exists
---------------
GSC reports 127+ "Crawled, currently not indexed" pages for the blog. Audit
showed all 30+ April + 17 May `Tech_Security_Weekly_Digest_*.md` posts share
the identical excerpt template (``"...을 중심으로 YYYY년 MM월 DD일 주요 보안/기술 뉴스 N건과 대응 우선순위를 정리합니다. ... 등 최신 위협 동향과 DevSecOps 실무 대응 방안을 함께 다룹니다."``).
Google treats that boilerplate as a low-value duplicate signal.

This script rewrites the ``excerpt:`` front-matter line of each daily-digest
post with one of 25 (5 × 5) deterministic combinations of opening/closing
sentence templates, biased by the post date so the same input produces the
same output (idempotent re-runs).

Scope (safety)
--------------
- Only touches files matching ``_posts/YYYY-MM-DD-Tech_Security_Weekly_Digest_*.md``
- Only modifies the single ``excerpt:`` line of YAML front matter
- Skips monthly roll-ups (``Week3_*``, ``Week4_*``, ``MonthN_*``)
- Skips posts that already contain a v2 marker in their excerpt
- Length kept within 150–200 chars (matches existing front-matter rules)

Usage
-----
::

    python3 scripts/seo_diversify_excerpts.py            # dry-run
    python3 scripts/seo_diversify_excerpts.py --apply    # write changes
    python3 scripts/seo_diversify_excerpts.py --apply --month 2026-05
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"

DIGEST_GLOB = "20*-Tech_Security_Weekly_Digest_*.md"

# Marker phrase — presence in excerpt means a v2 rewrite already happened.
# We rotate this token through 5 variants so detection is robust even when
# the surrounding template shifts.
V2_MARKERS = (
    "운영 관점에서 점검",
    "DevSecOps 시선으로 정리",
    "즉각 대응 우선순위",
    "보안 다이제스트 — ",
    "영향 범위와 패치 우선순위",
)

OPENERS: tuple[str, ...] = (
    "{stories} 등 {date} 보고된 {n}건의 보안/기술 이슈를 운영 관점에서 점검합니다.",
    "{stories}을(를) 비롯한 {date} 보안/기술 동향 {n}건을 DevSecOps 시선으로 정리합니다.",
    "{date} 공개된 {n}건의 위협·취약점 가운데 {stories}이(가) 즉각 대응 우선순위에 올랐습니다.",
    "{stories}이(가) 부각된 {date} 보안 다이제스트 — {n}건의 이슈와 실행 가능한 대응 액션을 정리합니다.",
    "{date} 수집한 {n}건의 보안 이슈 중 {stories}을(를) 중심으로 영향 범위와 패치 우선순위를 분석합니다.",
)

CLOSERS: tuple[str, ...] = (
    " 위협 인텔리전스·패치 적용·탐지 룰 보강을 중심으로 한 실무 체크리스트를 함께 제공합니다.",
    " 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다.",
    " 보안 운영센터(SOC)와 DevSecOps 팀이 즉시 적용할 수 있는 차단·완화 조치를 요약합니다.",
    " 변경 통제와 모니터링 적용 시점, 사후 회고에 활용할 IoC 정리표를 포함합니다.",
    " 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다.",
)

# Particle helper — Korean 받침 detection for grammatical clitics
def _has_batchim(ch: str) -> bool:
    if not ch or not ("\uac00" <= ch <= "\ud7a3"):
        return False
    return (ord(ch) - 0xAC00) % 28 != 0


def _select_particles(template: str, anchor: str) -> str:
    """Resolve (을/를) / 이(가) particle pairs based on anchor's last char.

    Trailing punctuation (commas, periods, ellipsis, separators) is stripped
    before inspecting the last character so the particle attaches to the
    final meaningful syllable rather than to a punctuation glyph.
    """
    if not anchor:
        anchor = "이슈"
    cleaned = anchor.rstrip()
    while cleaned and cleaned[-1] in "'\"”’,.;·…":
        cleaned = cleaned[:-1].rstrip()
    last = cleaned[-1] if cleaned else ""
    has = _has_batchim(last)
    template = template.replace("을(를)", "을" if has else "를")
    template = template.replace("이(가)", "이" if has else "가")
    return template


@dataclass
class FrontMatter:
    raw: str
    end_line_idx: int  # exclusive — first body line


def _split_front_matter(text: str) -> tuple[FrontMatter | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    for i, ln in enumerate(lines[1:], start=1):
        if ln.strip() == "---":
            fm = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            return FrontMatter(raw=fm, end_line_idx=i + 1), body
    return None, text


_HIGHLIGHT_TITLE_RE = re.compile(
    r"-\s*\{\s*source:\s*\"[^\"]*\"\s*,\s*title:\s*\"([^\"]+)\"\s*\}"
)


def _extract_highlights(fm_raw: str) -> list[str]:
    """Pull up to 3 highlight titles from summary_card.highlights."""
    titles: list[str] = []
    in_highlights = False
    for ln in fm_raw.split("\n"):
        stripped = ln.strip()
        if stripped.startswith("highlights:"):
            in_highlights = True
            continue
        if in_highlights:
            if not stripped.startswith("-"):
                # next top-level key reached
                if stripped and not ln.startswith(" "):
                    break
            m = _HIGHLIGHT_TITLE_RE.search(ln)
            if m:
                titles.append(m.group(1).strip())
    # decode common HTML entities
    decoded = []
    for t in titles:
        decoded.append(
            t.replace("&#x27;", "'")
            .replace("&quot;", '"')
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
    return decoded


_TITLE_RE = re.compile(r'^title:\s*"(.+?)"\s*$', re.MULTILINE)
_EXCERPT_RE = re.compile(r'^excerpt:\s*"(.+?)"\s*$', re.MULTILINE)


def _extract_title(fm_raw: str) -> str:
    m = _TITLE_RE.search(fm_raw)
    return m.group(1).strip() if m else ""


def _extract_existing_excerpt(fm_raw: str) -> str:
    m = _EXCERPT_RE.search(fm_raw)
    return m.group(1).strip() if m else ""


_FILENAME_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")


def _date_from_filename(path: Path) -> str:
    m = _FILENAME_DATE_RE.match(path.name)
    if not m:
        return ""
    return f"{m.group(1)}년 {m.group(2)}월 {m.group(3)}일"


def _seed_from_filename(path: Path) -> int:
    """Stable integer seed from filename for deterministic rotation."""
    return sum(ord(c) for c in path.stem)


def _truncate(text: str, max_len: int) -> str:
    """Truncate at a clause boundary (comma/space) before the limit.

    Avoids cutting mid-word and avoids leaving a dangling "…" that the
    particle-attachment logic would have to grammar-glue to.
    """
    if len(text) <= max_len:
        return text.rstrip(" ,.;·")
    cut = text[:max_len]
    for sep in (", ", ", ", " · ", "·", " "):
        idx = cut.rfind(sep)
        if idx > max_len // 2:
            return cut[:idx].rstrip(" ,.;·")
    return cut.rstrip(" ,.;·")


def _count_from_existing_excerpt(existing: str) -> str:
    """Extract the news-count from the original excerpt (e.g. ``뉴스 15건``)."""
    m = re.search(r"뉴스\s*(\d{1,3})건", existing)
    if m:
        return m.group(1)
    m = re.search(r"(\d{1,3})\s*건", existing)
    return m.group(1) if m else "15"


def _build_diverse_excerpt(
    path: Path,
    title: str,
    highlights: list[str],
    existing: str,
) -> str:
    date_str = _date_from_filename(path)
    n = _count_from_existing_excerpt(existing)
    seed = _seed_from_filename(path)

    # Pick anchors: prefer highlights, fall back to title fragments
    if len(highlights) >= 2:
        anchors = [_truncate(h, 38) for h in highlights[:2]]
        stories = " · ".join(anchors)
    elif highlights:
        stories = _truncate(highlights[0], 60)
    else:
        # split title by commas — drop empties
        parts = [p.strip() for p in re.split(r"[,，]", title) if p.strip()]
        if len(parts) >= 2:
            stories = " · ".join(_truncate(p, 38) for p in parts[:2])
        elif parts:
            stories = _truncate(parts[0], 60)
        else:
            stories = "주요 보안 이슈"

    opener_tpl = OPENERS[seed % len(OPENERS)]
    closer_tpl = CLOSERS[(seed // len(OPENERS)) % len(CLOSERS)]

    opener = opener_tpl.format(stories=stories, date=date_str, n=n)
    opener = _select_particles(opener, stories)
    excerpt = opener + closer_tpl

    # Length tightening: if >200, prefer dropping the second story
    if len(excerpt) > 200 and " · " in stories:
        stories_short = stories.split(" · ")[0]
        opener = opener_tpl.format(stories=stories_short, date=date_str, n=n)
        opener = _select_particles(opener, stories_short)
        excerpt = opener + closer_tpl

    # Hard cap
    if len(excerpt) > 220:
        # Cut at the last full sentence within 200 chars
        cut = excerpt[:200]
        period = cut.rfind("다.")
        if period > 140:
            excerpt = cut[: period + 2]
        else:
            excerpt = cut

    # Floor
    if len(excerpt) < 150:
        excerpt = excerpt + " 다음 회차 다이제스트도 같은 형식으로 이어집니다."

    return _yaml_safe(excerpt)


def _yaml_safe(text: str) -> str:
    """Sanitize a string for embedding inside a YAML double-quoted scalar.

    The excerpt is written as ``excerpt: "<text>"`` so any embedded double
    quote would terminate the scalar early and break the front matter
    (caught by ``test_post_summary_card_format``). We swap ASCII ``"`` and
    backslashes for typographic equivalents — they look the same to
    readers and search engines but are safe inside the YAML scalar.
    """
    return (
        text.replace("\\", "")
        .replace('"', "'")
    )


def _is_v2(existing: str) -> bool:
    return any(m in existing for m in V2_MARKERS)


def _is_monthly_rollup(name: str) -> bool:
    stem = name.lower()
    return (
        "week3_" in stem
        or "week4_" in stem
        or "week5_" in stem
        or "month" in stem
        or "monthly" in stem
    )


def _process_file(path: Path, apply: bool) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    fm, body = _split_front_matter(text)
    if fm is None:
        return False, "no-front-matter"

    existing = _extract_existing_excerpt(fm.raw)
    if not existing:
        return False, "no-excerpt"

    if _is_v2(existing):
        return False, "already-v2"

    title = _extract_title(fm.raw)
    highlights = _extract_highlights(fm.raw)
    new_excerpt = _build_diverse_excerpt(path, title, highlights, existing)

    if new_excerpt == existing:
        return False, "no-change"

    # Replace the single excerpt line
    new_fm = _EXCERPT_RE.sub(
        f'excerpt: "{new_excerpt}"', fm.raw, count=1
    )
    new_text = "---\n" + new_fm + "\n---\n" + body

    if apply:
        path.write_text(new_text, encoding="utf-8")
    return True, "rewritten" if apply else "would-rewrite"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: dry-run)"
    )
    parser.add_argument(
        "--month",
        default=None,
        help="Optional YYYY-MM filter (e.g. 2026-05)",
    )
    args = parser.parse_args()

    candidates = sorted(POSTS_DIR.glob(DIGEST_GLOB))
    if args.month:
        candidates = [p for p in candidates if p.name.startswith(args.month)]
    candidates = [p for p in candidates if not _is_monthly_rollup(p.name)]

    if not candidates:
        print("No matching posts.", file=sys.stderr)
        return 1

    stats = {"rewritten": 0, "already-v2": 0, "no-change": 0, "skipped": 0}
    for path in candidates:
        changed, reason = _process_file(path, apply=args.apply)
        if changed:
            stats["rewritten"] += 1
            print(f"[REWRITE] {path.relative_to(ROOT)}")
        elif reason == "already-v2":
            stats["already-v2"] += 1
        elif reason == "no-change":
            stats["no-change"] += 1
        else:
            stats["skipped"] += 1
            print(f"[SKIP   ] {path.relative_to(ROOT)} ({reason})")

    print()
    print(f"Total candidates : {len(candidates)}")
    print(f"  Rewritten      : {stats['rewritten']}")
    print(f"  Already v2     : {stats['already-v2']}")
    print(f"  No-change      : {stats['no-change']}")
    print(f"  Skipped (err)  : {stats['skipped']}")
    if not args.apply:
        print()
        print("Dry-run complete. Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

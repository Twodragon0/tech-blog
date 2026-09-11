#!/usr/bin/env python3
"""Rewrite daily-digest post excerpts with deterministic-but-diverse phrasing.

Why this exists
---------------
GSC reports 127+ "Crawled, currently not indexed" pages for the blog. Audit
showed all 30+ April + 17 May `Tech_Security_Weekly_Digest_*.md` posts share
the identical excerpt template (``"...을 중심으로 YYYY년 MM월 DD일 주요 보안/기술 뉴스 N건과 대응 우선순위를 정리합니다. ... 등 최신 위협 동향과 DevSecOps 실무 대응 방안을 함께 다룹니다."``).
Google treats that boilerplate as a low-value duplicate signal.

This script rewrites the ``excerpt:`` front-matter line of each daily-digest
post by combining one of 5 opening sentences with a closing sentence, biased by
the post date so the same input produces the same output (idempotent re-runs).

The opener is chosen by a filename hash. The **closer is not** — each closer
promises something specific and is only used where the body delivers it. See
the ``CLOSERS`` block for the 129-post defect that produced that rule.

Scope (safety)
--------------
- Only touches files matching ``_posts/YYYY-MM-DD-Tech_Security_Weekly_Digest_*.md``
- Only modifies the single ``excerpt:`` line of YAML front matter
- Skips monthly roll-ups (``Week3_*``, ``Week4_*``, ``MonthN_*``)
- Skips posts that already contain a v2 marker in their excerpt, unless
  ``--repair-promises`` is passed — the marker sits in the OPENER, so a v2
  excerpt can still carry a closer whose promise the body never kept
- Length kept within 150–200 chars (matches existing front-matter rules)

Usage
-----
::

    python3 scripts/seo_diversify_excerpts.py            # dry-run
    python3 scripts/seo_diversify_excerpts.py --apply    # write changes
    python3 scripts/seo_diversify_excerpts.py --apply --month 2026-05
    python3 scripts/seo_diversify_excerpts.py --repair-promises          # dry-run
    python3 scripts/seo_diversify_excerpts.py --apply --repair-promises
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"

DIGEST_GLOB = "20*-Tech_Security_Weekly_Digest_*.md"

# Appended when the generated excerpt falls under the 150-char floor. Split off
# before closer matching, otherwise every padded excerpt reads as hand-written.
_LENGTH_FLOOR_SENTENCE = " 다음 회차 다이제스트도 같은 형식으로 이어집니다."

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

# --------------------------------------------------------------------------
# Closers — each one PROMISES something, so each one carries the predicate that
# decides whether this post can keep that promise.
#
# What was wrong
# --------------
# The closer used to be picked by ``(seed // 5) % 5`` — a hash of the filename,
# with no reference to the body at all. Measured 2026-09-10 over the 217
# non-rollup digests: only 88 (41%) landed on a closer the post actually
# delivered. The rest promised things that are simply not in the text —
# ``공격 경로`` appeared in 1 of the 42 posts whose excerpt promised it, ``SOC``
# in 8 of 42, ``SBOM`` in 21 of 50. The excerpt is what the listing pages, the
# RSS feed and the search result show, so this was 129 posts advertising
# content they do not contain.
#
# Not every clause was a lie, which is the part worth remembering: the
# checklist promise was kept by 35 of 35. The defect was the hash, not the
# phrasing.
#
# Why six and not five
# --------------------
# Filtering the original five to "only the eligible ones" makes every excerpt
# true but pushes 121 of 215 posts (56%) onto the single closer that always
# qualifies — recreating the duplicate-boilerplate signal this whole script was
# written to remove. Closers whose promises are true by construction for a
# digest (measured 206-215 / 215) were added alongside, so the eligible set is
# always several wide and the rotation still spreads: max share 28.4%.
#
# Two of the original five were then removed outright — see the note below the
# tuple. That is why the count went 5 -> 8 -> 6 rather than straight to 6.
#
# ``requires`` reads the BODY. Anything asserted here must be visible to a
# reader who opens the post, which is the same thing
# ``scripts/check_excerpt_promises.py`` enforces corpus-wide.
# --------------------------------------------------------------------------


_CHECKBOX_RE = re.compile(r"^\s*-\s*\[[ xX]\]", re.MULTILINE)
_LINK_RE = re.compile(r"\]\(https?://")
_FENCE_RE = re.compile(r"^```.*$", re.MULTILINE)

# Cell texts that make a column an IoC column. Matched whole-cell, because the
# bare substring finds a source-directory row like
# `| KISA | krcert.or.kr | 국내 보안 권고 및 IOC |` — a place that publishes
# IoCs, which is not the 정리표 the sentence promises.
_IOC_HEADINGS = frozenset({"IoC", "IOC", "IoC 유형", "IOC 유형", "지표", "침해지표"})
_SOURCE_HEADINGS = frozenset({"소스", "출처"})


def _fence_spans(body: str) -> list[tuple[int, int]]:
    """Character ranges inside ``` fences, which no predicate may inspect."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for m in _FENCE_RE.finditer(body):
        if start is None:
            start = m.start()
        else:
            spans.append((start, m.end()))
            start = None
    if start is not None:  # unterminated fence — treat the rest as fenced
        spans.append((start, len(body)))
    return spans


def _table_blocks(body: str) -> list[list[list[str]]]:
    """Contiguous runs of pipe rows, each row split into stripped cells.

    Blocks rather than a flat row list, because "소스와 영향도를 표로 정리해"
    claims ONE table carries both columns; two separate tables each carrying one
    would satisfy a flat ``any(...) and any(...)`` while making the sentence
    false. Fenced code is excluded — 14 digests contain pipe lines inside ```
    blocks, and a predicate must not read a code sample as evidence.
    """
    spans = _fence_spans(body)
    blocks: list[list[list[str]]] = []
    current: list[list[str]] = []
    pos = 0
    for line in body.split("\n"):
        fenced = any(a <= pos < b for a, b in spans)
        if line.strip().startswith("|") and not fenced:
            current.append([c.strip() for c in line.split("|")])
        elif current:
            blocks.append(current)
            current = []
        pos += len(line) + 1
    if current:
        blocks.append(current)
    return blocks


def _has_checklist(body: str) -> bool:
    return "## 실무 체크리스트" in body and len(_CHECKBOX_RE.findall(body)) >= 3


def _source_and_impact_in_one_table(body: str) -> bool:
    for block in _table_blocks(body):
        has_source = any(c in _SOURCE_HEADINGS for row in block for c in row)
        has_impact = any("영향" in c for row in block for c in row)
        if has_source and has_impact:
            return True
    return False


def _has_ioc_table(body: str) -> bool:
    return any(
        c in _IOC_HEADINGS
        for block in _table_blocks(body)
        for row in block
        for c in row
    )


@dataclass(frozen=True)
class Closer:
    """A closing sentence plus the body evidence that makes it true.

    ``why`` names the missing evidence in gate output, so a failure says what
    to add rather than only that something is absent.

    ``retired`` marks a sentence that is still RECOGNISED but never SELECTED.
    Deleting a closer outright looks tidier and is a trap: 84 published posts
    carried the two retired sentences, and once the entries were gone
    ``current_closer_index`` returned ``None`` for them, so the repair skipped
    them as hand-written and the gate — allow-by-default on unknown endings —
    stopped seeing them. They would have kept advertising a SOC discussion and
    an attack-path walkthrough, invisibly, which is the defect this file exists
    to remove. A retired closer's ``requires`` is always False, so every carrier
    is a violation until it rotates onto a live one.
    """

    text: str
    requires: "Callable[[str], bool]"
    why: str
    retired: bool = False


def _never(_body: str) -> bool:
    return False


CLOSERS: tuple[Closer, ...] = (
    # Index 0 is the guaranteed fallback: measured true for 217/217 digests, so
    # the eligible set is never empty and the rotation always has somewhere to
    # land. If a future template drops the checklist, add another unconditional
    # closer BEFORE weakening this predicate.
    Closer(
        " 본문 말미의 실무 체크리스트에 팀에서 바로 나눠 가질 점검 항목을 정리했습니다.",
        _has_checklist,
        "a '## 실무 체크리스트' section with 3+ checkbox items",
    ),
    Closer(
        " 위협 인텔리전스·패치 적용·탐지 룰 보강을 중심으로 한 실무 체크리스트를 함께 제공합니다.",
        lambda b: _has_checklist(b) and "탐지" in b and "패치" in b,
        "a checklist plus body mentions of 탐지 and 패치",
    ),
    Closer(
        " 사안별 소스와 영향도를 표로 정리해 우선순위 판단 근거를 남겼습니다.",
        _source_and_impact_in_one_table,
        "one table carrying both a 소스/출처 column and an 영향 column",
    ),
    Closer(
        " 각 항목의 원문 링크를 함께 실어 1차 출처에서 바로 확인할 수 있습니다.",
        lambda b: len(_LINK_RE.findall(b)) >= 3,
        "3+ external source links",
    ),
    Closer(
        " 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다.",
        lambda b: "SBOM" in b and "EDR" in b,
        "body mentions of both SBOM and EDR",
    ),
    Closer(
        " 변경 통제와 모니터링 적용 시점, 사후 회고에 활용할 IoC 정리표를 포함합니다.",
        _has_ioc_table,
        "a table with an IoC column",
    ),
    # --- retired 2026-09-11: recognised so carriers are repaired, never picked
    #
    # Both were caught in review, not by the gate, and both had passed a
    # word-presence check — the same shallow test the filename-hash defect is an
    # instance of. "Does the word appear" is not "is the sentence true".
    Closer(
        " 보안 운영센터(SOC)와 DevSecOps 팀이 즉시 적용할 수 있는 차단·완화 조치를 요약합니다.",
        _never,
        'a 보안 운영센터 discussion. `"SOC" in body` matched the SOC 1 / SOC 2 '
        "audit report, and on all 7 posts carrying this sentence that was the "
        "only sense present — one spells out `System and Organization "
        "Controls(SOC) 1 보고서`. Corpus-wide: 1 mention of 보안 운영센터, 2 of "
        "보안관제, so no predicate makes this sentence usable here",
        retired=True,
    ),
    Closer(
        " 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다.",
        _never,
        "a step-by-step treatment of all three promises. 운영 환경 검증 절차 was "
        "never checked at all, all 4 carriers had one incidental 공격 경로 "
        "clause, and requiring all three matches 0 of 215 posts",
        retired=True,
    ),
)

# Every closer, live or retired — what `current_closer_index` and the gate read.
CLOSER_TEXTS: tuple[str, ...] = tuple(c.text for c in CLOSERS)

# Used only when NO closer qualifies — 0 of 217 digests today, but a body that
# is empty or unlike a digest must not crash the cron publish and must not be
# handed a promise by default. This sentence claims nothing, so it is safe
# everywhere and deliberately dull enough that nobody reaches for it on purpose.
# It is not part of the rotation.
NEUTRAL_CLOSER = " 자세한 내용은 본문에서 확인할 수 있습니다."


def eligible_closers(body: str) -> list[int]:
    """Indices of the closers this body can honestly carry.

    Retired entries are excluded here but stay in :data:`CLOSER_TEXTS`, so a
    post still carrying one is recognised, flagged and repaired rather than
    silently reclassified as hand-written prose.

    May be empty; callers fall back to :data:`NEUTRAL_CLOSER`.
    """
    return [i for i, c in enumerate(CLOSERS) if not c.retired and c.requires(body)]


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


def choose_closer_text(
    path: Path, body: str, current: int | None = None, max_len: int | None = None
) -> str:
    """Pick this post's closing sentence, deterministically.

    ``current`` is the closer the excerpt already ends with, when it has one.
    A fulfilled promise is left alone — rewriting an excerpt that is already
    true would churn live, indexed pages for nothing. Only an unfulfilled one
    rotates, and it rotates within the eligible set so the replacement is true
    by construction.

    ``max_len`` keeps the replacement from being longer than the sentence it
    replaces. ``check_front_matter_growth.py --changed origin/main`` ratchets
    every existing post's front matter, and a repair that swapped in a longer
    closer grew it by 2-8 characters in 41 of the 150 posts — enough to fail the
    build. Exempting ``excerpt`` from that ratchet would have blinded it to real
    excerpt bloat, so the constraint belongs here instead. It costs nothing:
    measured 2026-09-10, all 150 repairs had a non-growing option, and honouring
    it actually spread the rotation better (max share 33% -> 26%) because the two
    shortest closers were being under-picked. When nothing fits, the eligible set
    is used unfiltered — a true excerpt beats a short one.
    """
    ok = eligible_closers(body)
    if not ok:
        return NEUTRAL_CLOSER
    if current is not None and current in ok:
        return CLOSER_TEXTS[current]
    if max_len is not None:
        fits = [i for i in ok if len(CLOSER_TEXTS[i]) <= max_len]
        if not fits:
            # Nothing fits — growth is unavoidable, so take the SHORTEST
            # eligible rather than rotating over all of them. Rotating here
            # would pick an arbitrarily long closer and grow the front matter
            # more than necessary, and the ratchet that rejects it is triggered
            # by the very command this gate prints as the fix.
            return CLOSER_TEXTS[min(ok, key=lambda i: len(CLOSER_TEXTS[i]))]
        ok = fits
    return CLOSER_TEXTS[ok[(_seed_from_filename(path) // len(CLOSERS)) % len(ok)]]


def _split_trailing_filler(excerpt: str) -> tuple[str, str]:
    """Separate the length-floor sentence so closer matching sees the real end."""
    if excerpt.endswith(_LENGTH_FLOOR_SENTENCE):
        return excerpt[: -len(_LENGTH_FLOOR_SENTENCE)], _LENGTH_FLOOR_SENTENCE
    return excerpt, ""


def current_closer_index(excerpt: str) -> int | None:
    """Which closer this excerpt ends with, or ``None`` if it is hand-written."""
    core, _ = _split_trailing_filler(excerpt)
    for i, text in enumerate(CLOSER_TEXTS):
        if core.endswith(text.strip()):
            return i
    return None


def _build_diverse_excerpt(
    path: Path,
    title: str,
    highlights: list[str],
    existing: str,
    body: str,
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
    # The closer is chosen from what the BODY can back up, not from the
    # filename hash. See the CLOSERS block for the 129-post defect that caused.
    closer_tpl = choose_closer_text(path, body)

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
        excerpt = excerpt + _LENGTH_FLOOR_SENTENCE

    return _yaml_safe(excerpt)


def _yaml_safe(text: str) -> str:
    """Sanitize a string for embedding inside a YAML double-quoted scalar.

    The excerpt is written as ``excerpt: "<text>"`` so any embedded double
    quote would terminate the scalar early and break the front matter
    (caught by ``test_post_summary_card_format``). We swap ASCII ``"`` and
    backslashes for typographic equivalents — they look the same to
    readers and search engines but are safe inside the YAML scalar.
    """
    return text.replace("\\", "").replace('"', "'")


def _replace_excerpt(fm_raw: str, excerpt: str) -> str:
    """Swap the excerpt line without letting ``re.sub`` read the replacement.

    A template string is interpreted for backslash escapes, so an excerpt
    containing ``C:\\temp\\x`` raised ``re.PatternError: bad escape \\x``. This
    was latent before the repair path existed: ``_yaml_safe`` used to strip
    every backslash from the whole excerpt, which hid it by accident. Making
    that pass surgical exposed it, and a function replacement removes the class
    of bug rather than the one character that happened to trigger it.
    """
    return _EXCERPT_RE.sub(lambda _m: f'excerpt: "{excerpt}"', fm_raw, count=1)


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


def _repair_promise(path: Path, body: str, existing: str) -> str | None:
    """Swap only the closing sentence when its promise is unmet.

    Deliberately surgical. Regenerating the whole excerpt would rebuild the
    opener from ``summary_card.highlights``, and those shift as the digest is
    edited — a repair pass would then silently rewrite the story names too. The
    closer is a known suffix, so replacing just that leaves everything a reader
    recognises about the excerpt intact.

    No length-floor pass here. A swapped-in closer can be a few characters
    shorter than the one it replaces: measured over the 150 repairs, 3 land at
    146-149 against the module's soft 150 target, and all 3 already carry the
    floor sentence, so there is nothing left to append. The enforced band is
    ``test_excerpt_quality.MIN_LEN``/``MAX_LEN`` (80-320) and all 150 sit well
    inside it; a second filler sentence to buy 4 characters would add duplicate
    boilerplate, which is the thing this script exists to remove.

    Returns the new excerpt, or ``None`` when nothing needs doing.
    """
    core, filler = _split_trailing_filler(existing)
    current = current_closer_index(existing)
    if current is None:
        return None  # hand-written ending — not ours to rewrite
    if CLOSERS[current].requires(body):
        return None  # promise already kept
    chosen = choose_closer_text(
        path, body, current=None, max_len=len(CLOSER_TEXTS[current])
    )
    core = core[: -len(CLOSER_TEXTS[current].strip())].rstrip()
    # `_yaml_safe` on the NEW text only. Applied to the whole excerpt it also
    # rewrites the opener — its `.replace("\\", "")` turned
    # `오늘 C:\temp\x 경로` into `오늘 C:tempx 경로` — which makes the
    # "surgical" contract above false. `core` came out of a parsed front matter
    # and is already safe inside the scalar it was read from.
    return core + _yaml_safe(chosen) + filler


def _process_file(
    path: Path, apply: bool, repair_promises: bool = False
) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    fm, body = _split_front_matter(text)
    if fm is None:
        return False, "no-front-matter"

    existing = _extract_existing_excerpt(fm.raw)
    if not existing:
        return False, "no-excerpt"

    if repair_promises:
        # Repair-only. Deliberately NOT combined with the v1 rewrite below: the
        # rewrite path rebuilds the excerpt from scratch, including the story
        # names in the opener, and a run asked to fix promises should not also
        # regenerate two unrelated v1 excerpts it happens to pass. The v2 marker
        # lives in the OPENER, so v2 posts reach this branch too — which is the
        # point, since that is where the 150 unfulfilled closers are.
        if current_closer_index(existing) is None:
            return False, "not-generated"
        repaired = _repair_promise(path, body, existing)
        if repaired is None:
            return False, "promise-kept"
        new_fm = _replace_excerpt(fm.raw, repaired)
        if apply:
            path.write_text("---\n" + new_fm + "\n---\n" + body, encoding="utf-8")
        return True, "repaired" if apply else "would-repair"

    if _is_v2(existing):
        return False, "already-v2"

    title = _extract_title(fm.raw)
    highlights = _extract_highlights(fm.raw)
    new_excerpt = _build_diverse_excerpt(path, title, highlights, existing, body)

    if new_excerpt == existing:
        return False, "no-change"

    # Replace the single excerpt line
    new_fm = _replace_excerpt(fm.raw, new_excerpt)
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
    parser.add_argument(
        "--repair-promises",
        action="store_true",
        help=(
            "Also revisit already-v2 excerpts and swap any closing sentence "
            "whose promise the body does not keep"
        ),
    )
    args = parser.parse_args()

    candidates = sorted(POSTS_DIR.glob(DIGEST_GLOB))
    if args.month:
        candidates = [p for p in candidates if p.name.startswith(args.month)]
    candidates = [p for p in candidates if not _is_monthly_rollup(p.name)]

    if not candidates:
        print("No matching posts.", file=sys.stderr)
        return 1

    stats = {
        "rewritten": 0,
        "repaired": 0,
        "already-v2": 0,
        "promise-kept": 0,
        "not-generated": 0,
        "no-change": 0,
        "skipped": 0,
    }
    for path in candidates:
        changed, reason = _process_file(
            path, apply=args.apply, repair_promises=args.repair_promises
        )
        if changed and reason in ("repaired", "would-repair"):
            stats["repaired"] += 1
            print(f"[PROMISE] {path.relative_to(ROOT)}")
        elif changed:
            stats["rewritten"] += 1
            print(f"[REWRITE] {path.relative_to(ROOT)}")
        elif reason in ("already-v2", "promise-kept", "not-generated", "no-change"):
            stats[reason] += 1
        else:
            stats["skipped"] += 1
            print(f"[SKIP   ] {path.relative_to(ROOT)} ({reason})")

    print()
    print(f"Total candidates : {len(candidates)}")
    print(f"  Rewritten      : {stats['rewritten']}")
    if args.repair_promises:
        print(f"  Promise fixed  : {stats['repaired']}")
        print(f"  Promise kept   : {stats['promise-kept']}")
        print(f"  Hand-written   : {stats['not-generated']}")
    else:
        print(f"  Already v2     : {stats['already-v2']}")
    print(f"  No-change      : {stats['no-change']}")
    print(f"  Skipped (err)  : {stats['skipped']}")
    if not args.apply:
        print()
        print("Dry-run complete. Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

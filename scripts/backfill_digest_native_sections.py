#!/usr/bin/env python3
"""Backfill the missing NATIVE house sections into legacy digest posts,
grounded 100% in each post's OWN existing content (Sub-project A follow-up).

The three native sections some early digests lack:
    ## 경영진 브리핑   (Executive Summary bullets)
    ## 위험 스코어카드  (risk scorecard table)
    ## 실무 체크리스트  (P0/P1/P2 checkbox items)

HONESTY IS THE TOP CONSTRAINT. Every value added is derived from the post's
own ``### 이번 주 하이라이트`` highlights table — the SAME table the cover and
summary_card already display. NO facts are invented, NO front matter is
touched, NO cover/SVG is regenerated.

To guarantee the prose matches the gold template exactly, this script REUSES
the canonical generators rather than re-implementing any wording:
    scripts.news.content_generator._generate_executive_and_risk_sections
    scripts.news.content_generator._generate_news_specific_checklist

Two grounding sources are supported, tried deterministically in order:

1. The anchored ``### 이번 주 하이라이트`` highlights table with header
   ``| 분야 | 소스 | 핵심 내용 | 영향도 |`` (parser pattern reused from
   scripts/backfill_placeholder_highlights.py, extended to also capture the
   분야/category and 영향도/severity columns). The row parser tolerates 4 OR
   MORE columns — a 5-column ``| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |``
   table reads the same first four fields and ignores trailing columns.
   Severity counts are tallied from the visible 영향도 emojis and passed as
   ``counts=`` so the briefing numbers match the evidence on the page.

2. (April rollup fallback, used only when no highlights table exists) the
   front-matter ``summary_card.highlights`` list (real headlines) combined
   with the ``## 주요 CVE 요약`` markdown table. Each highlight becomes a
   news_item; a highlight whose title names a CVE present in the CVE table
   takes that CVE's severity (numeric CVSS band ≥9.0 Critical / ≥7.0 High /
   ≥4.0 Medium / else Low, or a Korean severity word), non-CVE highlights map
   to Medium.

Fail-closed: a post with NEITHER a usable highlights table NOR
summary_card.highlights+CVE data is SKIPPED entirely (never fabricated).

Idempotent: exec/risk is guarded by ``"## 경영진 브리핑" not in body``; the
checklist ``- `` → ``- [ ]`` conversion is a no-op once the boxes exist.

Usage:
    python3 scripts/backfill_digest_native_sections.py --dry-run _posts/a.md _posts/b.md
    python3 scripts/backfill_digest_native_sections.py --stats  _posts/a.md
    python3 scripts/backfill_digest_native_sections.py          _posts/a.md   # apply (write)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- Path setup so we can import scripts.news.* (mirrors
# backfill_digest_enrichment.py's established pattern). ---
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.news import content_generator  # noqa: E402

# The highlights table opens with a (category, source) header — current
# "분야 | 소스 | …" or legacy "카테고리 | 출처 | …". Parsing is anchored to the
# contiguous rows after this header (mirrors backfill_placeholder_highlights)
# so secondary body tables (e.g. "| 분야 | 추진 현황 |") are never read.
_HEADER_RE = re.compile(r"^\|\s*(?:분야|카테고리)\s*\|\s*(?:소스|출처)\s*\|")
# A highlights row has 4 OR MORE columns. Always read the first four
# (분야/소스/핵심 내용/영향도); any trailing columns (e.g. a 5th 긴급도 cell)
# are matched by the tail ``\|.*$`` and ignored. The 4-column case still
# matches exactly (tail collapses to the closing ``|`` + optional spaces).
_ROW_RE = re.compile(r"^\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|.*$")
_SEP_CHARS = set("-: ")

# April rollup grounding: front-matter summary_card.highlights + CVE table.
_CVE_ID_RE = re.compile(r"CVE-\d{4}-\d+")
_CVE_HEADING = "## 주요 CVE 요약"

_EXEC_HEADING = "## 경영진 브리핑"
_CHECKLIST_HEADING = "## 실무 체크리스트"
_REFS_HEADING = "## 참고 자료"

# Convert a plain bullet ("- text") to a checkbox ("- [ ] text"); skip lines
# that are ALREADY a checkbox so the conversion is idempotent.
_BULLET_RE = re.compile(r"^(\s*)-\s+(?!\[[ xX]?\])(.+)$")


def _split_front_matter(text: str) -> Tuple[str, str]:
    """Return (front_matter_with_delimiters, body). Front matter is never
    modified by this script."""
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    return (m.group(1), m.group(2)) if m else ("", text)


def _category_from_cell(cell: str) -> str:
    """Map a 분야 cell (emoji + label) to a content_generator category.

    Emoji first (fast, exact), then a text-label fallback so real corpus
    variants like ``⛓️ **Blockchain**`` (not in the literal emoji spec) still
    ground correctly. Defaults to ``security`` only when nothing matches."""
    if "🔒" in cell:
        return "security"
    if "🤖" in cell:
        return "ai"
    if "☁" in cell:
        return "cloud"
    if "⚙" in cell:
        return "devops"
    if "💰" in cell or "🪙" in cell or "⛓" in cell:
        return "blockchain"
    low = cell.lower()
    if "blockchain" in low or "블록체인" in low or "crypto" in low or "bitcoin" in low:
        return "blockchain"
    if "kubernetes" in low or "쿠버네티스" in low or "k8s" in low:
        return "kubernetes"
    if "cloud" in low or "클라우드" in low:
        return "cloud"
    if "devops" in low or "devsecops" in low:
        return "devops"
    if "ai" in low or "ml" in low:
        return "ai"
    if "security" in low or "보안" in low:
        return "security"
    return "security"


def _severity_from_cell(cell: str) -> str:
    """Map a 영향도 cell (emoji or text) to Critical/High/Medium/Low."""
    if "🔴" in cell:
        return "Critical"
    if "🟠" in cell:
        return "High"
    if "🟡" in cell:
        return "Medium"
    if "🟢" in cell:
        return "Low"
    low = cell.lower()
    if "critical" in low:
        return "Critical"
    if "high" in low:
        return "High"
    if "medium" in low:
        return "Medium"
    if "low" in low:
        return "Low"
    return "Medium"


def parse_highlights(body: str) -> List[Dict]:
    """Parse the anchored ``### 이번 주 하이라이트`` table into news_items.

    Each item carries the exact keys the canonical generators consume:
    title (핵심 내용, raw Korean), summary (empty), category, source, severity.
    Skips the header/separator and any row missing a source/title."""
    items: List[Dict] = []
    in_table = False
    for line in body.splitlines():
        if not in_table:
            if _HEADER_RE.match(line):
                in_table = True
            continue
        m = _ROW_RE.match(line)
        if not m:
            break  # blank / non-table line ends the highlights table
        cat_cell, source, title, sev_cell = (c.strip() for c in m.groups())
        if set(cat_cell) <= _SEP_CHARS:  # |---|---| separator row
            continue
        if not source or not title:
            continue
        items.append(
            {
                "title": title,
                "summary": "",
                "category": _category_from_cell(cat_cell),
                "source": source,
                "severity": _severity_from_cell(sev_cell),
            }
        )
    return items


def _cvss_band_to_severity(score: float) -> str:
    """Map a numeric CVSS base score to a severity band."""
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"


def _severity_word_to_severity(cell: str) -> Optional[str]:
    """Map a Korean/English severity WORD (used in some CVE tables in place of
    a numeric CVSS score) to Critical/High/Medium/Low. Returns None when the
    cell is neither a recognized word nor parseable — the caller decides the
    fallback."""
    low = cell.lower()
    if "치명" in cell or "critical" in low:
        return "Critical"
    if "높음" in cell or "high" in low or "심각" in cell:
        return "High"
    if "중간" in cell or "medium" in low or "보통" in cell:
        return "Medium"
    if "낮음" in cell or "low" in low:
        return "Low"
    return None


def _parse_cve_table(body: str) -> Dict[str, str]:
    """Parse the ``## 주요 CVE 요약`` table into {CVE-ID: severity}.

    The 3rd column is a CVSS score which may be numeric (e.g. ``7.8``) or a
    Korean severity word (e.g. ``치명적``, ``높음``); both are supported. The
    header may label it ``CVSS`` or ``심각도``. Rows without a CVE ID are
    ignored."""
    mapping: Dict[str, str] = {}
    idx = body.find(_CVE_HEADING)
    if idx == -1:
        return mapping
    section = body[idx + len(_CVE_HEADING):]
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            break  # next section ends the CVE table
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        cve_match = _CVE_ID_RE.search(cells[0])
        if not cve_match:
            continue  # header / separator / non-CVE row
        score_cell = cells[2]
        num = re.search(r"\d+(?:\.\d+)?", score_cell)
        if num and _severity_word_to_severity(score_cell) is None:
            severity = _cvss_band_to_severity(float(num.group(0)))
        else:
            severity = _severity_word_to_severity(score_cell) or "High"
        mapping[cve_match.group(0).upper()] = severity
    return mapping


def _infer_category_from_title(title: str) -> str:
    """Best-effort category from a Korean headline sentence (April rollups
    carry no explicit 분야 column). Short English tokens (``ai``, ``ml``,
    ``k8s``) are matched on word boundaries so they do NOT fire inside larger
    words (e.g. ``ai`` inside ``Mirai``). Defaults to ``security``.

    Note: category only influences item SORTING inside the reused security-mode
    generator (severity/counts drive the actual copy), so a miss here does not
    alter the emitted 경영진 브리핑 / 위험 스코어카드 text."""
    low = title.lower()

    def has_word(*words: str) -> bool:
        return any(
            re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low) for w in words
        )

    if "쿠버네티스" in title or has_word("kubernetes", "k8s"):
        return "kubernetes"
    if "클라우드" in title or has_word("aws", "cloud", "azure", "gcp", "bedrock"):
        return "cloud"
    if has_word("docker", "devops", "ci/cd"):
        return "devops"
    if "에이전트" in title or has_word("ai", "llm", "agent", "ml"):
        return "ai"
    if any(k in title for k in ("암호화폐", "탈중앙", "블록체인")):
        return "blockchain"
    return "security"


def _extract_summary_card_highlights(front: str) -> List[Dict[str, str]]:
    """Read ``summary_card.highlights`` (list of {source, title}) from the YAML
    front matter. Returns [] when absent or malformed."""
    m = re.match(r"^---\n(.*?)\n---\n?$", front, re.DOTALL)
    fm_text = m.group(1) if m else front
    try:
        import yaml

        data = yaml.safe_load(fm_text) or {}
    except Exception:
        return []
    card = data.get("summary_card") if isinstance(data, dict) else None
    if not isinstance(card, dict):
        return []
    highlights = card.get("highlights")
    if not isinstance(highlights, list):
        return []
    out: List[Dict[str, str]] = []
    for h in highlights:
        if isinstance(h, dict):
            out.append(
                {
                    "source": str(h.get("source", "") or "").strip(),
                    "title": str(h.get("title", "") or "").strip(),
                }
            )
    return out


def parse_summary_card_cve(front: str, body: str) -> List[Dict]:
    """April rollup grounding: build news_items from summary_card.highlights,
    with severity from the ``## 주요 CVE 요약`` table.

    Requires BOTH a non-empty highlights list AND a non-empty CVE table
    (``summary_card.highlights+CVE data``); otherwise returns [] (SKIP)."""
    highlights = _extract_summary_card_highlights(front)
    if not highlights:
        return []
    cve_sev = _parse_cve_table(body)
    if not cve_sev:
        return []
    items: List[Dict] = []
    for h in highlights:
        title = h["title"]
        if not title:
            continue
        cves = _CVE_ID_RE.findall(title)
        if cves:
            severity = next(
                (cve_sev[c.upper()] for c in cves if c.upper() in cve_sev),
                "High",  # CVE-bearing but absent from table (fallback)
            )
        else:
            severity = "Medium"
        items.append(
            {
                "title": title,
                "summary": "",
                "category": _infer_category_from_title(title),
                "source": h["source"],
                "severity": severity,
            }
        )
    return items


def _derive_counts(items: List[Dict]) -> Dict[str, int]:
    """Severity tally from the visible 영향도 emojis (authoritative for the
    briefing numbers)."""
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for it in items:
        counts[it["severity"]] = counts.get(it["severity"], 0) + 1
    return counts


def _find_line(lines: List[str], needle: str) -> Optional[int]:
    for i, ln in enumerate(lines):
        if ln.startswith(needle):
            return i
    return None


def _insert_exec_risk(lines: List[str], block: str) -> Tuple[List[str], bool]:
    """Insert the exec/risk block right AFTER the highlights table's trailing
    ``---`` separator (and therefore before the first content section)."""
    hidx = next((i for i, ln in enumerate(lines) if _HEADER_RE.match(ln)), None)
    if hidx is None:
        return lines, False
    j = hidx + 1
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        j += 1
    # find the highlights table's trailing '---' separator
    while j < len(lines) and lines[j].strip() != "---":
        j += 1
    if j >= len(lines):
        return lines, False
    insert_at = j + 1  # right after the '---' line
    block_lines = [""] + block.rstrip("\n").split("\n")
    return lines[:insert_at] + block_lines + lines[insert_at:], True


def _insert_exec_risk_april(lines: List[str], block: str) -> Tuple[List[str], bool]:
    """Insert the exec/risk block for April rollups (which have NO highlights
    table) right AFTER the ``## 개요`` section's trailing ``---`` separator, so
    it sits between the overview and ``## 일별 다이제스트 인덱스``."""
    oidx = _find_line(lines, "## 개요")
    if oidx is None:
        return lines, False
    j = oidx + 1
    while j < len(lines) and lines[j].strip() != "---":
        j += 1
    if j >= len(lines):
        return lines, False
    insert_at = j + 1  # right after the overview's '---'
    block_lines = [""] + block.rstrip("\n").split("\n") + ["", "---"]
    return lines[:insert_at] + block_lines + lines[insert_at:], True


def _checklist_section_span(lines: List[str]) -> Optional[Tuple[int, int]]:
    """[start, end) line indices of the ## 실무 체크리스트 section (end = next
    ``## `` heading, or EOF)."""
    start = _find_line(lines, _CHECKLIST_HEADING)
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return (start, end)


def _count_checkboxes(lines: List[str]) -> int:
    return sum(1 for ln in lines if re.match(r"^\s*-\s*\[[ xX]?\]", ln))


def transform_text(
    text: str,
) -> Tuple[Optional[str], Dict[str, object]]:
    """Return (new_text_or_None, info). ``None`` means SKIP (no usable table).
    ``info`` carries the generated section text for --dry-run review."""
    front, body = _split_front_matter(text)
    # Try the highlights table first; fall back to the April
    # summary_card+CVE source only when no highlights table yields rows.
    items = parse_highlights(body)
    source = "highlights"
    if not items:
        items = parse_summary_card_cve(front, body)
        source = "summary_card_cve"
    info: Dict[str, object] = {"items": len(items), "source": source,
                               "exec_added": False, "checklist_action": "none",
                               "exec_block": "", "checklist_block": ""}
    if not items:
        info["skip"] = True
        return None, info

    counts = _derive_counts(items)
    info["counts"] = counts
    lines = body.split("\n")

    # --- Step 3: Executive + Risk (guarded) ---
    # Skip if the post ALREADY carries a briefing surface (## 경영진 브리핑 or
    # legacy ## 경영진 요약) OR a risk scorecard (any 스코어카드) — inserting the
    # combined block would duplicate an existing surface.
    has_briefing = any(m in body for m in (_EXEC_HEADING, "## 경영진 요약"))
    has_risk = "스코어카드" in body
    if not has_briefing and not has_risk:
        block = content_generator._generate_executive_and_risk_sections(
            items, "security", counts, honor_item_severity=True
        )
        if source == "highlights":
            lines, ok = _insert_exec_risk(lines, block)
        else:
            lines, ok = _insert_exec_risk_april(lines, block)
        if ok:
            info["exec_added"] = True
            info["exec_block"] = block.rstrip("\n")

    # --- Step 4: Checklist ---
    # Only the highlights source manages the checklist. April rollups already
    # carry a rich ``## 실무 우선순위 체크리스트`` (≥8 checkboxes); adding or
    # replacing it would double the surface, so leave it untouched.
    if source != "highlights":
        new_body = "\n".join(lines)
        new_text = front + new_body
        if new_text == text:
            info["nochange"] = True
            return text, info
        return new_text, info

    span = _checklist_section_span(lines)
    if span is not None:
        start, end = span
        # convert plain bullets to checkboxes in place
        converted = list(lines)
        for i in range(start, end):
            m = _BULLET_RE.match(converted[i])
            if m:
                converted[i] = f"{m.group(1)}- [ ] {m.group(2)}"
        n_boxes = _count_checkboxes(converted[start:end])
        if n_boxes >= 5:
            lines = converted
            info["checklist_action"] = f"converted ({n_boxes} boxes)"
            info["checklist_block"] = "\n".join(converted[start:end]).rstrip("\n")
        else:
            # regenerate from canonical generator (grounded in items)
            raw = content_generator._generate_news_specific_checklist(items, honor_item_severity=True)
            # strip the generator's leading '---\n\n' — the section is replaced
            # in place, keeping whatever precedes the existing heading.
            gen = re.sub(r"^---\n\n", "", raw)
            repl = gen.rstrip("\n").split("\n") + ["", "---", ""]
            lines = lines[:start] + repl + lines[end:]
            info["checklist_action"] = f"regenerated (was {n_boxes} boxes)"
            info["checklist_block"] = gen.rstrip("\n")
    else:
        # no ## 실무 체크리스트 yet → insert before ## 참고 자료 (or at EOF).
        # Emit the SAME normalized shape the regenerate branch would leave
        # (leading + trailing '---' separators, generator's own leading '---'
        # stripped) so a re-run — which now sees the heading and, when the
        # generated box count is <5, re-enters the regenerate branch — produces
        # byte-identical output (idempotent).
        raw = content_generator._generate_news_specific_checklist(items, honor_item_severity=True)
        gen = re.sub(r"^---\n\n", "", raw)
        refs = _find_line(lines, _REFS_HEADING)
        insert_at = len(lines) if refs is None else refs
        # Dedupe a leading separator: if the last non-blank line before the
        # insertion point is already '---', don't prepend another one
        # (avoids 2-3 consecutive horizontal rules).
        prev = next(
            (lines[i].strip() for i in range(insert_at - 1, -1, -1) if lines[i].strip()),
            "",
        )
        lead = [] if prev == "---" else ["---", ""]
        block_lines = lead + gen.rstrip("\n").split("\n") + ["", "---", ""]
        if refs is None:
            lines = lines + [""] + block_lines
        else:
            lines = lines[:refs] + block_lines + lines[refs:]
        info["checklist_action"] = "inserted"
        info["checklist_block"] = gen.rstrip("\n")

    new_body = "\n".join(lines)
    new_text = front + new_body
    if new_text == text:
        info["nochange"] = True
        return text, info
    return new_text, info


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", help="explicit digest post files to backfill")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print WOULD CHANGE + the generated sections; write nothing",
    )
    ap.add_argument("--stats", action="store_true", help="print per-file stats")
    args = ap.parse_args(argv)

    changed = 0
    for path in args.paths:
        try:
            original = open(path, encoding="utf-8").read()
        except OSError as exc:
            print(f"SKIP {path}: cannot read ({exc})", file=sys.stderr)
            continue

        new_text, info = transform_text(original)
        if new_text is None:
            print(f"SKIP {path}: no highlights table")
            continue

        if args.stats:
            print(
                f"{path}: items={info['items']} counts={info.get('counts')} "
                f"exec_added={info['exec_added']} checklist={info['checklist_action']}"
            )

        if new_text != original:
            changed += 1
            if args.dry_run:
                print(f"\nWOULD CHANGE {path}")
                if info["exec_added"]:
                    print("--- generated 경영진 브리핑 / 위험 스코어카드 ---")
                    print(info["exec_block"])
                if info["checklist_action"] != "none":
                    print(f"--- 실무 체크리스트 [{info['checklist_action']}] ---")
                    print(info["checklist_block"])
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new_text)
                print(f"CHANGED {path}")
        else:
            print(f"unchanged {path}")

    print(f"\n{changed}/{len(args.paths)} would change" if args.dry_run
          else f"\n{changed}/{len(args.paths)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Backfill Sub-project 0 structural normalization into existing digest posts.

Deterministic, in-place, idempotent. Applies the same heading normalization
and per-item-checklist removal the generator now does at build time
(_normalize_deep_analysis), so already-published posts get the fixed
structure without re-fetching news. Mirrors backfill_digest_commentary.py.

Usage:
    python3 scripts/backfill_digest_structure.py --dry-run \
        --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
    python3 scripts/backfill_digest_structure.py \
        --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
"""
import argparse
import glob
import re
import sys
from pathlib import Path

# --- Path setup so we can import scripts.news.* (mirrors
# backfill_digest_commentary.py's established pattern). ---
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.news.content_generator import _normalize_deep_analysis  # noqa: E402


def _split_front_matter(text: str):
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    return (m.group(1), m.group(2)) if m else ("", text)


# --- Finding 1: prose '#### 권장 조치' advisory preservation ---
#
# _normalize_deep_analysis treats ANY heading containing '권장 조치' as the
# start of a checklist to drop. That is correct for the LLM's per-item
# CHECKBOX checklist ('- [ ] ...'), but _generate_security_brief_template
# (content_generator.py) also emits a legitimate PROSE advisory under the
# exact same heading ('- text', no checkbox). Per project decision, only
# the checkbox form is the defect — prose must survive verbatim.
_ADVISORY_HEADING_RE = re.compile(r"^####\s+권장 조치\s*$")
_HEADING_ANY_RE = re.compile(r"^#{1,6}\s+")
_CHECKBOX_BULLET_RE = re.compile(r"^-\s*\[.\]")
_PROSE_BULLET_RE = re.compile(r"^-\s+(?!\[)")


def _split_preserved_segments(lines):
    """Partition an item-region buffer into segments, isolating any genuine
    prose '#### 권장 조치' advisory block (heading + non-checkbox bullet
    body) so it bypasses _normalize_deep_analysis verbatim instead of being
    silently dropped.

    Returns a list of (preserve: bool, chunk_lines) segments. Rejoining
    every chunk in order (verbatim if preserve else routed through
    _normalize_deep_analysis) reproduces the full buffer with only the
    intended heading demotion / checkbox-checklist strip applied.
    """
    segments = []
    current = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if _ADVISORY_HEADING_RE.match(line):
            j = i + 1
            while j < n and not _HEADING_ANY_RE.match(lines[j]):
                j += 1
            block = lines[i:j]
            body = [ln for ln in block[1:] if ln.strip()]
            has_checkbox = any(_CHECKBOX_BULLET_RE.match(ln.strip()) for ln in body)
            has_prose_bullet = any(_PROSE_BULLET_RE.match(ln.strip()) for ln in body)
            if has_prose_bullet and not has_checkbox:
                if current:
                    segments.append((False, current))
                    current = []
                segments.append((True, block))
                i = j
                continue
        current.append(line)
        i += 1
    if current:
        segments.append((False, current))
    return segments


# --- Finding 2: top-level section-boundary whitelist ---
#
# Any '## N. ...' heading that is neither a known section title nor an
# expected in-item collision (the LLM's own '## N. 기술적 배경 / 실무 영향
# 분석 / 대응 체크리스트' body headings _normalize_deep_analysis exists to
# fix) is suspicious: it may be an un-whitelisted section boundary that
# would otherwise get swept into item-region normalization. Warn (do not
# hard-fail) so corpus drift is caught by a human.
_GENERIC_TOP_RE = re.compile(r"^## \d+\.\s")
_IN_ITEM_COLLISION_MARKERS = ("기술적 배경", "실무 영향", "대응", "권장")


def transform_body(text: str, path: str = "<unknown>") -> str:
    """Apply heading normalization + per-item CHECKBOX-checklist strip to a post.

    Deep-analysis normalization (_normalize_deep_analysis: demote stray
    #/##/###/#### headings to #### and drop the LLM per-item checkbox
    checklist) applies ONLY inside item regions — the LLM-authored content
    that follows a '### N.M <item title>' heading. It never applies outside
    an item region: section intros (서론, 📊 빠른 참조 incl. its
    '### 이번 주 하이라이트' subheading, 경영진 브리핑, 위험 스코어카드,
    분석가 시점, 트렌드, 실무 체크리스트, 참고 자료) and all top-level
    '## N. ...' section headings are emitted verbatim.

    Region tracking:
    - A line matching '^### \\d+\\.\\d+' opens an item region (in_item=True).
      The item heading itself is emitted verbatim (it is the region
      delimiter, not part of the analysis body).
    - A line matching a genuine top-level section heading closes the item
      region (in_item=False) and is emitted verbatim. NOTE: a naive '^## '
      match is NOT sufficient here — the LLM-authored deep-analysis body
      inside an item region *itself* emits '## N. 기술적 배경 / 실무 영향
      분석 / 대응 체크리스트' (2-hash) headings, which is exactly the
      numbering collision _normalize_deep_analysis exists to fix. Ending
      the item region on any '## ' line would stop normalization dead on
      the first in-item heading. So the boundary is the fixed whitelist of
      real top-level section titles the generator emits (mirrors the
      previous 'protected' regex): '## 서론', '## 📊 빠른 참조', '## 경영진
      브리핑', '## 위험 스코어카드', '## 분석가 시점', '## N. <카테고리> 뉴스'
      / '## N. 트렌드 분석', '## N. GeekNews 하이라이트', '## N. Open Source',
      '## 실무 체크리스트', '## 참고 자료'. Any OTHER '## N. ...' heading that
      is not this whitelist and does not look like an in-item collision
      (기술적 배경 / 실무 영향 / 대응 / 권장) triggers a stderr WARNING (not a
      hard fail) naming the file + heading, so corpus drift in section
      titles is caught by a human rather than silently swept into
      normalization.
    - While in_item is True, lines are buffered and flushed through
      _normalize_deep_analysis, EXCEPT a genuine prose '#### 권장 조치'
      advisory block (heading + non-checkbox '- ' bullets, emitted by
      _generate_security_brief_template), which is preserved verbatim —
      see _split_preserved_segments. _normalize_deep_analysis would
      otherwise drop it, because it treats any heading containing
      '권장 조치' as the start of a checklist to skip; only the LLM's
      per-item CHECKBOX checklist ('- [ ] ...') is the actual defect. While
      in_item is False, lines are emitted verbatim — this is what preserves
      '### 이번 주 하이라이트' and everything else that precedes a section's
      first item heading.

    Idempotent.
    """
    front, body = _split_front_matter(text)
    item_heading_re = re.compile(r"^### \d+\.\d+")
    top_section_re = re.compile(
        r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드|"
        r"GeekNews|Open Source)|"
        r"## 실무 체크리스트|## 서론|## 분석가 시점|## 경영진 브리핑|"
        r"## 위험 스코어카드|## 참고 자료|## 📊)"
    )
    out = []
    buf = []
    in_item = False

    def flush():
        if not buf:
            return
        for preserve, chunk in _split_preserved_segments(buf):
            joined = "\n".join(chunk)
            out.append(joined if preserve else _normalize_deep_analysis(joined))
        buf.clear()

    for line in body.split("\n"):
        if item_heading_re.match(line):
            flush()
            in_item = True
            out.append(line)
        elif top_section_re.match(line):
            flush()
            in_item = False
            out.append(line)
        else:
            if _GENERIC_TOP_RE.match(line) and not any(
                marker in line for marker in _IN_ITEM_COLLISION_MARKERS
            ):
                print(
                    f"WARNING: {path}: unrecognized top-level section "
                    f"heading not in whitelist: {line!r}",
                    file=sys.stderr,
                )
            if in_item:
                buf.append(line)
            else:
                out.append(line)
    flush()
    return front + "\n".join(out)


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts-glob", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)
    files = sorted(glob.glob(args.posts_glob))
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("no files matched", file=sys.stderr)
        return 1
    changed = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        new = transform_body(original, path)
        if new != original:
            changed += 1
            if args.dry_run:
                print(f"WOULD CHANGE {path}")
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"CHANGED {path}")
        else:
            print(f"unchanged {path}")
    print(f"{changed}/{len(files)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

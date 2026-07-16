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


def transform_body(text: str) -> str:
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
      / '## N. 트렌드 분석', '## 실무 체크리스트', '## 참고 자료'.
    - While in_item is True, lines are buffered and flushed through
      _normalize_deep_analysis. While False, lines are emitted verbatim —
      this is what preserves '### 이번 주 하이라이트' and everything else
      that precedes a section's first item heading.

    Known limitation: an in-item prose '#### 권장 조치' advisory (from
    _generate_security_brief_template) WOULD be dropped by
    _normalize_deep_analysis, which treats any heading containing '권장 조치'
    as a checklist to skip. None of the 5 pilot posts contain this, so it
    does not affect this backfill. The forward-generation path is unaffected
    because that prose block is emitted by the brief template outside of
    the _normalize_deep_analysis() call, not through it.

    Idempotent.
    """
    front, body = _split_front_matter(text)
    item_heading_re = re.compile(r"^### \d+\.\d+")
    top_section_re = re.compile(
        r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드)|"
        r"## 실무 체크리스트|## 서론|## 분석가 시점|## 경영진 브리핑|"
        r"## 위험 스코어카드|## 참고 자료|## 📊)"
    )
    out = []
    buf = []
    in_item = False

    def flush():
        if buf:
            out.append(_normalize_deep_analysis("\n".join(buf)))
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
        elif in_item:
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
        new = transform_body(original)
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

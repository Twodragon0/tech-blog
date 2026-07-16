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

    Only the item deep-analysis regions are normalized: _normalize_deep_analysis
    demotes stray #/##/### headings to #### and drops the LLM per-item checkbox
    checklist (대응 체크리스트, `- [ ]`). The topic-specific PROSE advisory
    ('#### 권장 조치' + `- ` bullets) from _generate_security_brief_template is
    legitimate content and is PROTECTED (kept verbatim) — per the project
    decision that only checkbox per-item checklists are the defect. Top-level
    '## N.' section headings and the global '## 실무 체크리스트' are protected.
    Idempotent.
    """
    front, body = _split_front_matter(text)
    # Protect the true top-level section + global-checklist headings + prose
    # advisory headings; normalize everything else.
    protected = re.compile(
        r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드)|## 실무 체크리스트|## 서론|"
        r"## 분석가 시점|## 경영진 브리핑|## 위험 스코어카드|## 참고 자료|### P[012] |#### 요약|"
        r"#### 권장 조치|### \d+\.\d+|## 📊)"
    )
    out = []
    buf = []

    def flush():
        if buf:
            out.append(_normalize_deep_analysis("\n".join(buf)))
            buf.clear()

    for line in body.split("\n"):
        if protected.match(line):
            flush()
            out.append(line)
        else:
            buf.append(line)
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

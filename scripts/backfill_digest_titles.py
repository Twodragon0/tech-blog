#!/usr/bin/env python3
"""Backfill weekly-digest post titles to the new schema.

Rewrites the YAML `title:` field of every Weekly Digest post in `_posts/`
whose current title is a fragmented headline join (comma-separated noun
phrases — e.g. "Microsoft, AI 에이전트, 현대화된 Windows").

New schema:
    {date_str} {series_prefix}: {theme_phrase} ({total}건)

Inputs are reconstructed entirely from the post's own front matter and
body, so the script is idempotent and doesn't need historical news data.

Reference: .omc/research/gsc_disparity_analysis_2026_05_21.md
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

SERIES_PREFIX = {
    "security": "주간 보안 다이제스트",
    "tech-blog": "기술 블로그 주간 다이제스트",
}

# Canonical theme labels (mirrors _extract_digest_title_labels in
# scripts/news/content_generator.py — kept in sync deliberately).
SECURITY_LABEL_MAP = [
    (r"zero[- ]?day|0[- ]?day|제로데이|cve-", "제로데이"),
    (r"ransomware|랜섬웨어", "랜섬웨어"),
    (r"malware|악성코드", "악성코드"),
    (r"byovd|driver|edr", "BYOVD EDR"),
    (r"dns|exfil|data leak|유출", "DNS 유출"),
    (r"cisco|fmc", "Cisco FMC"),
    (r"dprk|north korea|북한", "북한 위협"),
    (r"ai[- ]?agent|agentic|llm|model|에이전트", "AI 에이전트"),
    (r"kubernetes|k8s|gke|cluster|쿠버네티스", "쿠버네티스"),
    (r"cloud|aws|azure|gcp|클라우드", "클라우드"),
    (r"patch|update|패치", "패치"),
    (r"vulnerabilit|취약점", "취약점"),
    (r"phishing|피싱", "피싱"),
    (r"supply[- ]?chain|공급망", "공급망 공격"),
    (r"botnet|봇넷", "봇넷"),
    (r"data breach|data leak|침해", "데이터 침해"),
]

TECH_LABEL_MAP = [
    (r"ai[- ]?agent|agentic|llm", "AI 에이전트"),
    (r"kubernetes|k8s|gke|쿠버네티스", "쿠버네티스"),
    (r"cloud|aws|azure|gcp|클라우드", "클라우드"),
    (r"docker|container|컨테이너", "컨테이너"),
    (r"rust|golang|go ", "시스템 언어"),
    (r"open[- ]?source|oss|github", "오픈소스"),
    (r"devops|gitops|cicd", "DevOps"),
    (r"finops|cost", "FinOps"),
]


def detect_mode(post_text: str, filename: str) -> str:
    """Return 'security' or 'tech-blog' based on filename + body cues."""
    if "Tech_Blog_Weekly_Digest" in filename:
        return "tech-blog"
    return "security"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) — caller handles serialisation."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text
    return fm, parts[2]


def extract_theme(fm: dict, body: str, mode: str) -> str:
    """Pick 1-2 canonical theme labels from tags + body content."""
    label_map = SECURITY_LABEL_MAP if mode == "security" else TECH_LABEL_MAP

    # Sources to scan for label matches (most specific first).
    haystack_parts = []
    sc = fm.get("summary_card") or {}
    for key in ("tags", "highlights"):
        val = sc.get(key)
        if isinstance(val, list):
            for entry in val:
                if isinstance(entry, str):
                    haystack_parts.append(entry)
                elif isinstance(entry, dict):
                    for v in entry.values():
                        if isinstance(v, str):
                            haystack_parts.append(v)
    for key in ("tags", "keywords", "title", "excerpt"):
        val = fm.get(key)
        if isinstance(val, list):
            haystack_parts.extend(str(x) for x in val)
        elif isinstance(val, str):
            haystack_parts.append(val)
    # Body — first 4 KB is enough to catch headline structure
    haystack_parts.append(body[:4000])

    haystack = " ".join(haystack_parts).lower()

    labels: list[str] = []
    seen: set[str] = set()
    for pattern, label in label_map:
        if re.search(pattern, haystack) and label not in seen:
            seen.add(label)
            labels.append(label)
            # 3 labels gives ~C(16,3) = 560 combinations vs 2-label's 120,
            # which is essential because most security digests trip the
            # generic "CVE-" pattern (= 제로데이) and need a richer mix
            # to avoid near-duplicate titles.
            if len(labels) >= 3:
                break

    if not labels:
        return "기술 동향" if mode == "tech-blog" else "보안 위협"
    return "·".join(labels)


def extract_total(fm: dict, body: str) -> int:
    """Count news-card includes; fall back to highlights or default 5."""
    count = body.count("{% include news-card.html")
    if count >= 1:
        return count
    sc = fm.get("summary_card") or {}
    highlights = sc.get("highlights")
    if isinstance(highlights, list) and highlights:
        return len(highlights)
    return 5


def format_date(fm: dict, filename: str) -> str:
    """Return 'YYYY년 MM월 DD일' from date frontmatter or filename."""
    raw = fm.get("date")
    if isinstance(raw, datetime):
        return raw.strftime("%Y년 %m월 %d일")
    if isinstance(raw, str):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", raw)
        if m:
            return f"{m.group(1)}년 {m.group(2)}월 {m.group(3)}일"
    # Fallback: parse from filename YYYY-MM-DD prefix
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-", filename)
    if m:
        return f"{m.group(1)}년 {m.group(2)}월 {m.group(3)}일"
    return ""


def is_already_new_schema(title: str) -> bool:
    return any(prefix in title for prefix in (
        "주간 보안 다이제스트:",
        "기술 블로그 주간 다이제스트:",
    )) and bool(re.search(r"\(\d+건\)", title))


def build_new_title(fm: dict, body: str, filename: str) -> str:
    mode = detect_mode(body, filename)
    date_str = format_date(fm, filename)
    theme = extract_theme(fm, body, mode)
    total = extract_total(fm, body)
    series = SERIES_PREFIX[mode]
    return f"{date_str} {series}: {theme} ({total}건)"


def update_title_line(text: str, new_title: str) -> str | None:
    """Rewrite the YAML `title:` line AND the nested `summary_card.title:`.

    Both fields ship to JSON-LD (BlogPosting.headline + sub-card display)
    so they must stay in lockstep — otherwise jekyll-seo-tag and the
    summary card include disagree on what the post is about.
    """
    title_re = re.compile(r'^(title:\s*)(["\']?)(.*?)\2\s*$', re.M)
    m = title_re.search(text)
    if not m:
        return None
    quote = m.group(2) or '"'
    safe = new_title.replace(quote, "'" if quote == '"' else '"')
    out = title_re.sub(f"{m.group(1)}{quote}{safe}{quote}", text, count=1)

    # Update nested summary_card.title (2-space indent, anchored under the
    # `summary_card:` block — match-once via DOTALL-bounded lookbehind).
    sc_title_re = re.compile(
        r'(^summary_card:\s*\n(?:[ \t].*\n)*?[ \t]+title:\s*)(["\']?)(.*?)\2(\s*$)',
        re.M,
    )
    m2 = sc_title_re.search(out)
    if m2:
        q2 = m2.group(2) or '"'
        safe2 = new_title.replace(q2, "'" if q2 == '"' else '"')
        out = sc_title_re.sub(
            f"{m2.group(1)}{q2}{safe2}{q2}{m2.group(4)}", out, count=1
        )
    return out


def process_file(path: Path, dry_run: bool, force: bool = False) -> tuple[str, str | None]:
    """Return (status, new_title_or_none) — status in {'updated','skip','error'}."""
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if not fm:
        return ("error", None)

    current_title = fm.get("title", "")
    if not force and is_already_new_schema(current_title):
        return ("skip", None)

    new_title = build_new_title(fm, body, path.name)
    if not new_title or current_title == new_title:
        return ("skip", None)

    if dry_run:
        return ("would-update", new_title)

    new_text = update_title_line(text, new_title)
    if new_text is None or new_text == text:
        return ("error", None)
    path.write_text(new_text, encoding="utf-8")
    return ("updated", new_title)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dry-run", action="store_true", help="print changes, don't write"
    )
    ap.add_argument(
        "--pattern",
        default="*Weekly_Digest*.md",
        help="glob inside _posts/ (default: %(default)s)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="rewrite titles even if they already match the new schema",
    )
    args = ap.parse_args()

    files = sorted(POSTS_DIR.glob(args.pattern))
    if not files:
        print(f"No files match {args.pattern} in {POSTS_DIR}", file=sys.stderr)
        return 1

    updated = 0
    skipped = 0
    errors = 0
    for p in files:
        status, new_title = process_file(p, args.dry_run, force=args.force)
        if status in ("updated", "would-update"):
            updated += 1
            marker = "[DRY]" if args.dry_run else "[OK] "
            print(f"  {marker} {p.name}\n       → {new_title}")
        elif status == "skip":
            skipped += 1
        else:
            errors += 1
            print(f"  [ERR] {p.name}")

    print()
    print(f"Scanned: {len(files)}  Updated: {updated}  Skipped: {skipped}  Errors: {errors}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())

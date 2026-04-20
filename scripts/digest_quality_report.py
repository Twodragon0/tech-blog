#!/usr/bin/env python3
"""Monthly Digest quality report — detects truncated summaries, English trend
headers, and summary fallback quality issues across all Digest posts.

Usage:
    python3 scripts/digest_quality_report.py                 # Current month
    python3 scripts/digest_quality_report.py --month 2026-03 # Specific month
    python3 scripts/digest_quality_report.py --all           # All Digest posts
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# Particles that indicate mid-sentence truncation when at end of table cell
_TRUNCATION_PARTICLES = re.compile(
    r"\s+(의|에|를|을|이|가|은|는|와|과|로|으로|에서|한|된|인|할|위한|하기|대한)\s*$"
)

# English-only trend header (no Korean chars)
_ENGLISH_HEADER = re.compile(r"^\*\*[A-Za-z0-9 /\-&.]+\*\*$")

# Acceptable English-only headers (industry standard terms)
_ALLOWED_ENGLISH_HEADERS = {
    "**AI/ML**",
    "**AI/LLM**",
    "**CVE ID**",
    "**Ransomware**",
    "**K8s**",
    "**Container/K8s**",
    "**DevOps**",
    "**DevSecOps**",
    "**FinOps**",
    "**CVSS**",
    "**MITRE ATT&CK**",
    "**IoC**",
    "**IoT/OT**",
}

# Proper Korean sentence endings
_KOREAN_ENDINGS = re.compile(
    r"(습니다|됩니다|했습니다|입니다|됨|임|다)\.\s*$|[.!?]\s*$"
)


def find_digest_posts(month: str = None) -> list:
    """Find Digest post files, optionally filtered by month (YYYY-MM)."""
    pattern = "*.md"
    posts = sorted(POSTS_DIR.glob(pattern))
    posts = [p for p in posts if "Digest" in p.name]
    if month:
        posts = [p for p in posts if p.name.startswith(month)]
    return posts


def analyze_post(filepath: Path) -> dict:
    """Analyze a single post for quality issues."""
    issues = {
        "truncated_cells": [],
        "english_headers": [],
        "incomplete_highlights": [],
        "summary_quality": "ok",
    }
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues["summary_quality"] = "encoding_error"
        return issues
    lines = content.split("\n")
    issues = {
        "truncated_cells": [],
        "english_headers": [],
        "incomplete_highlights": [],
        "summary_quality": "ok",
    }

    in_table = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect table rows
        if stripped.startswith("|") and "|" in stripped[1:]:
            in_table = True
            cells = [c.strip() for c in stripped.split("|")[1:-1]]

            # Check for truncated table cells (핵심 내용 / 주요 키워드)
            for cell in cells:
                if len(cell) > 30 and _TRUNCATION_PARTICLES.search(cell):
                    issues["truncated_cells"].append({"line": i, "text": cell[-60:]})

            # Check for English-only trend headers
            for cell in cells:
                if (
                    _ENGLISH_HEADER.match(cell)
                    and len(cell) > 6
                    and cell not in _ALLOWED_ENGLISH_HEADERS
                ):
                    issues["english_headers"].append({"line": i, "text": cell})
        elif in_table and not stripped.startswith("|"):
            in_table = False

        # Check highlights_html truncation
        if "highlights_html" in stripped:
            # Find <li> content that ends abruptly
            li_matches = re.findall(r"<li>.*?</li>", stripped)
            for li in li_matches:
                clean = re.sub(r"<[^>]+>", "", li)
                if len(clean) > 20 and not _KOREAN_ENDINGS.search(clean):
                    if _TRUNCATION_PARTICLES.search(clean):
                        issues["incomplete_highlights"].append(
                            {"line": i, "text": clean[-50:]}
                        )

    # Check summary fallback quality (generic template phrases)
    generic_patterns = [
        "상세 내용은 출처 링크를 참조하세요",
        "관련 보안 영향도 분석",
        "관련 보안 검토 및 모니터링",
    ]
    generic_count = sum(content.count(p) for p in generic_patterns)
    total_sections = content.count("### ")
    if total_sections > 0 and generic_count / max(total_sections, 1) > 0.5:
        issues["summary_quality"] = "generic_heavy"

    return issues


def generate_report(posts: list) -> dict:
    """Generate quality report across all posts."""
    report = {
        "total_posts": len(posts),
        "posts_with_issues": 0,
        "truncated_cells_total": 0,
        "english_headers_total": 0,
        "incomplete_highlights_total": 0,
        "generic_summaries": 0,
        "details": [],
    }

    for post in posts:
        issues = analyze_post(post)
        has_issues = (
            issues["truncated_cells"]
            or issues["english_headers"]
            or issues["incomplete_highlights"]
            or issues["summary_quality"] != "ok"
        )

        if has_issues:
            report["posts_with_issues"] += 1
            report["truncated_cells_total"] += len(issues["truncated_cells"])
            report["english_headers_total"] += len(issues["english_headers"])
            report["incomplete_highlights_total"] += len(
                issues["incomplete_highlights"]
            )
            if issues["summary_quality"] != "ok":
                report["generic_summaries"] += 1

            report["details"].append({"file": post.name, "issues": issues})

    return report


def print_report(report: dict):
    """Print formatted quality report."""
    print("=" * 60)
    print("  Digest Quality Report")
    print("=" * 60)
    print()
    print(f"  Total posts analyzed:    {report['total_posts']}")
    print(f"  Posts with issues:       {report['posts_with_issues']}")
    print()

    # Summary table
    print("  Issue Type                Count")
    print("  " + "-" * 40)
    print(f"  Truncated table cells:   {report['truncated_cells_total']}")
    print(f"  English trend headers:   {report['english_headers_total']}")
    print(f"  Incomplete highlights:   {report['incomplete_highlights_total']}")
    print(f"  Generic summaries:       {report['generic_summaries']}")
    print()

    clean = report["total_posts"] - report["posts_with_issues"]
    score = (clean / max(report["total_posts"], 1)) * 100
    print(f"  Quality Score: {score:.0f}% ({clean}/{report['total_posts']} clean)")
    print()

    if report["details"]:
        print("-" * 60)
        print("  Details")
        print("-" * 60)
        for detail in report["details"]:
            print(f"\n  {detail['file']}:")
            issues = detail["issues"]
            for tc in issues["truncated_cells"]:
                print(f"    L{tc['line']} TRUNCATED: ...{tc['text']}")
            for eh in issues["english_headers"]:
                print(f"    L{eh['line']} ENGLISH:   {eh['text']}")
            for ih in issues["incomplete_highlights"]:
                print(f"    L{ih['line']} HIGHLIGHT: ...{ih['text']}")
            if issues["summary_quality"] != "ok":
                print(f"    SUMMARY: {issues['summary_quality']}")
    else:
        print("  All posts pass quality checks!")

    print()
    print("=" * 60)
    return report["posts_with_issues"] == 0


def check_file(path: Path) -> list:
    """Check a single post file and return a list of human-readable issue strings.

    Returns an empty list when the file passes all quality checks.
    Designed to be imported by other scripts (e.g. auto_publish_news.py) so
    that a quality gate can run immediately after writing a new post.
    """
    issues = analyze_post(path)
    messages = []
    for tc in issues.get("truncated_cells", []):
        messages.append(f"L{tc['line']} TRUNCATED: ...{tc['text']}")
    for eh in issues.get("english_headers", []):
        messages.append(f"L{eh['line']} ENGLISH_HEADER: {eh['text']}")
    for ih in issues.get("incomplete_highlights", []):
        messages.append(f"L{ih['line']} INCOMPLETE_HIGHLIGHT: ...{ih['text']}")
    if issues.get("summary_quality") not in ("ok", None):
        messages.append(f"SUMMARY_QUALITY: {issues['summary_quality']}")
    return messages


def main():
    parser = argparse.ArgumentParser(description="Digest quality report")
    parser.add_argument("--month", help="Month to check (YYYY-MM)", default=None)
    parser.add_argument("--all", action="store_true", help="Check all Digest posts")
    parser.add_argument(
        "--ci", action="store_true", help="Exit with code 1 if issues found"
    )
    parser.add_argument(
        "--files", nargs="+", help="Check specific files instead of searching"
    )
    args = parser.parse_args()

    if args.files:
        posts = [Path(f) for f in args.files if Path(f).exists()]
    elif args.all:
        posts = find_digest_posts(None)
    elif args.month:
        posts = find_digest_posts(args.month)
    else:
        from datetime import datetime

        posts = find_digest_posts(datetime.now().strftime("%Y-%m"))

    if not posts:
        print("No Digest posts found")
        sys.exit(0)

    report = generate_report(posts)
    all_clean = print_report(report)

    if args.ci and not all_clean:
        sys.exit(1)


if __name__ == "__main__":
    main()

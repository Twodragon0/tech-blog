#!/usr/bin/env python3
"""
포스트 품질 검증 스크립트 (100점 만점)
"""

import argparse
import re
import sys
from pathlib import Path


def validate_front_matter(content: str) -> tuple[int, str]:
    """Front matter 완성도 (15점)

    Required fields (11점): title, date, categories, tags, excerpt,
        description, image, toc
    Bonus fields (4점): keywords, author, comments, image_alt

    Returns:
        (score, warning) where warning is an empty string if no issue.
    """
    fm_block = content[:1100]
    score: float = 0

    required = [
        "title:",
        "date:",
        "categories:",
        "tags:",
        "excerpt:",
        "description:",
        "image:",
        "toc:",
    ]
    for field in required:
        if field in fm_block:
            score += 11 / len(required)

    bonus = ["keywords:", "author:", "comments:", "image_alt:"]
    for field in bonus:
        if field in fm_block:
            score += 1

    # Check actual front matter block length
    warning = ""
    lines = content.splitlines()
    if len(lines) >= 2 and lines[0].strip() == "---":
        end_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = i
                break
        if end_idx is not None:
            fm_text = "\n".join(lines[1:end_idx])
            if len(fm_text) > 1000:
                warning = (
                    f"Front matter exceeds 1000 chars ({len(fm_text)} chars). "
                    "Fields beyond 1100 chars may not be scored."
                )

    return min(15, int(score)), warning


def validate_ai_summary(content: str) -> int:
    """AI Summary Card (10점)"""
    if "ai-summary-card" in content or "{% include ai-summary-card" in content:
        return 10
    return 0


def validate_executive_summary(content: str) -> int:
    """Executive Summary (10점)"""
    if "Executive Summary" in content or "경영진 브리핑" in content:
        return 10
    return 0


def validate_risk_scorecard(content: str) -> int:
    """위험 스코어카드 (10점)"""
    if "위험 스코어카드" in content or "위험도" in content:
        return 10
    return 0


def validate_sections(content: str) -> int:
    """섹션 구조 (15점)"""
    h2_count = len(re.findall(r"^## ", content, re.MULTILINE))
    h3_count = len(re.findall(r"^### ", content, re.MULTILINE))

    score = 0
    if h2_count >= 4:
        score += 7
    if h3_count >= 8:
        score += 8
    return score


def validate_checklists(content: str) -> int:
    """체크리스트 (10점)"""
    checkboxes = len(re.findall(r"- \[ \]", content))
    if checkboxes >= 5:
        return 10
    return int(checkboxes * 2)


def validate_tables(content: str) -> int:
    """표 활용 (10점)"""
    tables = len(re.findall(r"\|.*\|", content))
    if tables >= 15:  # 표 3개 ≈ 15줄
        return 10
    return int(tables / 1.5)


def validate_code_blocks(content: str) -> int:
    """코드 블록 (10점)"""
    score = 10
    in_block = False
    unlabeled_openings = 0

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("```"):
            continue

        fence_meta = stripped[3:].strip()
        if not in_block:
            if not fence_meta:
                unlabeled_openings += 1
            in_block = True
        else:
            in_block = False

    if unlabeled_openings > 0:
        score -= min(5, unlabeled_openings * 2)

    blocks = re.findall(r"```[a-zA-Z0-9_+\-]*\n(.*?)```", content, re.DOTALL)
    long_blocks = 0
    for block in blocks:
        if len(block.split("\n")) > 10:
            long_blocks += 1
    score -= min(4, long_blocks)

    return max(0, score)


def validate_cross_refs(content: str) -> int:
    """교차 참조 (5점)"""
    refs = len(re.findall(r"{%\s*post_url", content))
    return min(5, refs * 5)


def validate_length(content: str) -> int:
    """전체 길이 (5점)"""
    lines = len(content.split("\n"))
    if lines >= 500:
        return 5
    return int(lines / 100)


def validate_post(filepath: Path) -> dict[str, object]:
    """포스트 품질 검증"""
    content = filepath.read_text(encoding="utf-8")

    fm_score, fm_warning = validate_front_matter(content)

    scores = {
        "front_matter": fm_score,
        "ai_summary": validate_ai_summary(content),
        "executive_summary": validate_executive_summary(content),
        "risk_scorecard": validate_risk_scorecard(content),
        "sections": validate_sections(content),
        "checklists": validate_checklists(content),
        "tables": validate_tables(content),
        "code_blocks": validate_code_blocks(content),
        "cross_refs": validate_cross_refs(content),
        "length": validate_length(content),
    }

    total = sum(scores.values())

    return {
        "file": filepath.name,
        "total": total,
        "scores": scores,
        "lines": len(content.split("\n")),
        "warnings": [fm_warning] if fm_warning else [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="포스트 품질 검증 스크립트 (100점 만점)",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="검증할 포스트 파일 경로 (예: _posts/2026-03-11-*.md)",
    )
    parser.add_argument(
        "--fail-below",
        type=int,
        default=60,
        help="이 점수 미만이면 종료 코드 1 (기본값: 60)",
    )
    parser.add_argument(
        "--warn-below",
        type=int,
        default=80,
        help="이 점수 미만이면 경고 출력 (기본값: 80)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="통과한 포스트는 출력 생략 (fail/warn만 표시)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    has_error = False

    for filepath in args.files:
        result = validate_post(Path(filepath))
        raw_total = result.get("total", 0)
        total = raw_total if isinstance(raw_total, int) else 0
        file_name = str(result.get("file", filepath))
        raw_lines = result.get("lines", 0)
        lines = raw_lines if isinstance(raw_lines, int) else 0
        scores = result.get("scores", {})

        is_fail = total < args.fail_below
        is_warn = total < args.warn_below

        if args.quiet and not is_fail and not is_warn:
            continue

        print(f"\nPost Quality Score: {total}/100")
        print(f"File: {file_name} ({lines} lines)")
        print("\nBreakdown:")
        if isinstance(scores, dict):
            for key, score in scores.items():
                print(f"  {key}: {score}")

        raw_warnings = result.get("warnings", [])
        warnings = raw_warnings if isinstance(raw_warnings, list) else []
        for w in warnings:
            print(f"\n⚠️  WARNING: {w}")

        if is_fail:
            print(f"\n❌ ERROR: Score below {args.fail_below}")
            has_error = True
        elif is_warn:
            print(f"\n⚠️  WARNING: Score below {args.warn_below}")

    if has_error:
        sys.exit(1)

#!/usr/bin/env python3
"""
포스트 품질 검증 스크립트 (100점 만점)
"""

import argparse
import re
import sys
from pathlib import Path


def validate_front_matter(content: str) -> int:
    """Front matter 완성도 (15점)"""
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
        if field in content[:500]:  # Front matter는 처음 500자 이내
            score += 15 / len(required)
    return int(score)


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
    # 언어 태그 없는 코드 블록 감지
    if "```\n" in content:
        score -= 5
    # 10줄 초과 코드 블록 감지 (간단 검사)
    blocks = re.findall(r"```.*?\n(.*?)```", content, re.DOTALL)
    for block in blocks:
        if len(block.split("\n")) > 10:
            score -= 2
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

    scores = {
        "front_matter": validate_front_matter(content),
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

        print(f"\nPost Quality Score: {total}/100")
        print(f"File: {file_name} ({lines} lines)")
        print("\nBreakdown:")
        if isinstance(scores, dict):
            for key, score in scores.items():
                print(f"  {key}: {score}")

        if total < args.fail_below:
            print(f"\n❌ ERROR: Score below {args.fail_below}")
            has_error = True
        elif total < args.warn_below:
            print(f"\n⚠️  WARNING: Score below {args.warn_below}")

    if has_error:
        sys.exit(1)

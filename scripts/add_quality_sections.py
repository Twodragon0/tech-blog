#!/usr/bin/env python3
"""
포스트에 Executive Summary와 위험 스코어카드 섹션을 추가하는 스크립트.
80점 미만 포스트를 대상으로 누락된 섹션을 삽입합니다.

Usage:
    python3 scripts/add_quality_sections.py --dry-run _posts/2026-01-*.md
    python3 scripts/add_quality_sections.py --fix _posts/2026-01-*.md
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


# ──────────────────────────────────────────────
# Helper: front matter 파싱
# ──────────────────────────────────────────────

def parse_front_matter(content: str) -> dict:
    """YAML front matter에서 주요 필드를 추출합니다."""
    result = {}
    lines = content.splitlines()
    if len(lines) < 2 or lines[0].strip() != "---":
        return result

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return result

    fm_text = "\n".join(lines[1:end_idx])

    # excerpt (단일행 및 multiline block scalar)
    m = re.search(r'^excerpt:\s*["\']?(.+?)["\']?\s*$', fm_text, re.MULTILINE)
    if m:
        result["excerpt"] = m.group(1).strip().strip('"').strip("'")

    # description
    m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', fm_text, re.MULTILINE)
    if m:
        result["description"] = m.group(1).strip().strip('"').strip("'")

    # categories
    cat_m = re.search(r'^categories:\s*\n((?:^- .+\n?)+)', fm_text, re.MULTILINE)
    if cat_m:
        result["categories"] = re.findall(r"- (.+)", cat_m.group(1))

    # category (single-value field)
    m = re.search(r'^category:\s*\[?(.+?)\]?\s*$', fm_text, re.MULTILINE)
    if m:
        raw = m.group(1).strip()
        cats = [c.strip().strip('"').strip("'") for c in raw.split(",")]
        result.setdefault("categories", cats)

    return result


# ──────────────────────────────────────────────
# Helper: 포스트 타입 판별
# ──────────────────────────────────────────────

def classify_post(filepath: Path, fm: dict) -> str:
    """포스트 유형을 파일명과 카테고리에서 결정합니다."""
    name = filepath.name.lower()
    cats = [c.lower() for c in fm.get("categories", [])]

    if "postmortem" in name or "incident" in name:
        return "incident"
    if "cloud_security_course" in name or "8batch" in name:
        return "cloud_course"
    if "weekly_digest" in name or "security_vendor_blog" in name:
        return "weekly_digest"
    if "security" in cats or "devsecops" in cats:
        return "security_guide"
    return "general"


# ──────────────────────────────────────────────
# Helper: 위험도 텍스트 결정
# ──────────────────────────────────────────────

def risk_level_text(post_type: str) -> str:
    mapping = {
        "incident":       "🔴 높음 | 즉시 대응 및 패치 적용 필요",
        "cloud_course":   "🟢 낮음 | 교육 목적 실습 환경 중심",
        "weekly_digest":  "🟡 중간 | 주요 보안 위협 모니터링 및 패치 적용 필요",
        "security_guide": "🟡 중간 | 보안 설정 점검 및 강화 필요",
        "general":        "🟡 중간 | 보안 업데이트 및 모니터링 필요",
    }
    return mapping.get(post_type, mapping["general"])


# ──────────────────────────────────────────────
# Helper: 삽입 위치 탐색
# ──────────────────────────────────────────────

def find_insert_position(content: str) -> int:
    """
    삽입 위치 결정 규칙 (우선순위 순):
    1. ai-summary-card include 블록 끝(-%} 이후 줄)
    2. {% endcapture %} / {% capture %} Liquid 블록 이후
    3. 첫 번째 ## 헤딩 직전
    4. 파일 맨 끝
    """
    lines = content.splitlines(keepends=True)

    # 1. ai-summary-card 블록 탐색
    in_include = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 시작: {%- include ai-summary-card 또는 {% include ai-summary-card
        if re.search(r'\{%-?\s*include\s+ai-summary-card', stripped):
            in_include = True
        if in_include:
            # 블록 끝: -%} 또는 %} 로 끝나는 줄
            if re.search(r'-%\}', stripped) or (stripped.endswith('%}') and i > 0):
                # 다음 줄(빈 줄 포함)부터 삽입
                pos = sum(len(l) for l in lines[:i + 1])
                return pos

    # 2. {% endcapture %} 블록 탐색
    for i, line in enumerate(lines):
        if re.search(r'\{%-?\s*endcapture\s*-?%\}', line.strip()):
            pos = sum(len(l) for l in lines[:i + 1])
            return pos

    # 3. 첫 번째 ## 헤딩 직전
    for i, line in enumerate(lines):
        if re.match(r'^## ', line):
            pos = sum(len(l) for l in lines[:i])
            return pos

    # 4. 맨 끝
    return len(content)


# ──────────────────────────────────────────────
# Helper: 섹션 생성
# ──────────────────────────────────────────────

def make_executive_summary(summary_text: str) -> str:
    return f"\n## Executive Summary\n\n> **경영진 브리핑**: {summary_text}\n"


def make_risk_scorecard(risk_text: str) -> str:
    return (
        "\n### 위험도 평가\n\n"
        "| 항목 | 위험도 | 설명 |\n"
        "|------|--------|------|\n"
        f"| 전체 위험도 | {risk_text} |\n"
    )


# ──────────────────────────────────────────────
# 품질 점수 조회
# ──────────────────────────────────────────────

def get_quality_score(filepath: Path) -> tuple[int, dict]:
    """validate_post_quality.py 를 실행해 점수와 세부 항목을 반환합니다."""
    result = subprocess.run(
        [sys.executable, "scripts/validate_post_quality.py", str(filepath)],
        capture_output=True, text=True, cwd=filepath.parent.parent
    )
    output = result.stdout + result.stderr

    # 점수 파싱
    m = re.search(r"Post Quality Score:\s*(\d+)/100", output)
    score = int(m.group(1)) if m else -1

    # 세부 항목 파싱
    items = {}
    for line in output.splitlines():
        item_m = re.match(r"\s+(\w+):\s*(\d+)", line)
        if item_m:
            items[item_m.group(1)] = int(item_m.group(2))

    return score, items


# ──────────────────────────────────────────────
# 메인 처리 함수
# ──────────────────────────────────────────────

def process_file(filepath: Path, fix: bool) -> tuple[bool, str]:
    """
    파일을 분석하고 필요한 섹션을 삽입합니다.

    Returns:
        (changed, message)
    """
    content = filepath.read_text(encoding="utf-8")
    score, items = get_quality_score(filepath)

    if score < 0:
        return False, f"  점수 파싱 실패"

    if score >= 80:
        return False, f"  점수 {score}/100 — 수정 불필요"

    needs_exec = items.get("executive_summary", 0) == 0
    needs_risk = items.get("risk_scorecard", 0) == 0

    if not needs_exec and not needs_risk:
        return False, f"  점수 {score}/100 — 필요 섹션 이미 존재 (다른 이유로 낮음)"

    # front matter 분석
    fm = parse_front_matter(content)
    post_type = classify_post(filepath, fm)

    # 브리핑 텍스트 (excerpt 우선, 없으면 description 앞 100자)
    summary_text = (
        fm.get("excerpt")
        or (fm.get("description", "")[:120] + "...")
        or "보안 위협 분석 및 실무 대응 방안을 제공합니다."
    )
    # 너무 길면 자르기
    if len(summary_text) > 150:
        summary_text = summary_text[:147] + "..."

    risk_text = risk_level_text(post_type)

    # 삽입 위치 탐색
    insert_pos = find_insert_position(content)

    # 삽입할 텍스트 조합
    inject = ""
    if needs_exec:
        inject += make_executive_summary(summary_text)
    if needs_risk:
        inject += make_risk_scorecard(risk_text)

    new_content = content[:insert_pos] + inject + content[insert_pos:]

    missing = []
    if needs_exec:
        missing.append("executive_summary")
    if needs_risk:
        missing.append("risk_scorecard")

    if fix:
        filepath.write_text(new_content, encoding="utf-8")
        return True, (
            f"  [{score}/100] 섹션 추가: {', '.join(missing)}"
            f"  (타입={post_type})"
        )
    else:
        return True, (
            f"  [{score}/100] 추가 예정: {', '.join(missing)}"
            f"  (타입={post_type}) [dry-run]"
        )


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="80점 미만 포스트에 Executive Summary / 위험 스코어카드 섹션을 추가합니다."
    )
    parser.add_argument("files", nargs="+", help="처리할 포스트 파일 경로")
    parser.add_argument(
        "--fix", action="store_true",
        help="실제로 파일을 수정합니다 (없으면 dry-run)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="변경 내용만 출력하고 파일을 수정하지 않습니다 (기본)"
    )
    args = parser.parse_args()

    fix_mode = args.fix and not args.dry_run

    print(f"{'[FIX MODE]' if fix_mode else '[DRY-RUN]'} 포스트 품질 섹션 추가")
    print("=" * 60)

    changed = 0
    skipped = 0
    errors = 0

    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"파일 없음: {f}")
            errors += 1
            continue

        print(f"\n{path.name}")
        try:
            was_changed, msg = process_file(path, fix=fix_mode)
            print(msg)
            if was_changed:
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  오류: {e}")
            errors += 1

    print("\n" + "=" * 60)
    action = "수정됨" if fix_mode else "수정 예정"
    print(f"결과: {changed}개 {action}, {skipped}개 건너뜀, {errors}개 오류")
    if not fix_mode:
        print("실제 적용하려면 --fix 플래그를 사용하세요.")


if __name__ == "__main__":
    main()

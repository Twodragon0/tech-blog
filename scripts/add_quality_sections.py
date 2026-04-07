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
    cat_m = re.search(r"^categories:\s*\n((?:^- .+\n?)+)", fm_text, re.MULTILINE)
    if cat_m:
        result["categories"] = re.findall(r"- (.+)", cat_m.group(1))

    # category (single-value field)
    m = re.search(r"^category:\s*\[?(.+?)\]?\s*$", fm_text, re.MULTILINE)
    if m:
        raw = m.group(1).strip()
        cats = [c.strip().strip('"').strip("'") for c in raw.split(",")]
        result.setdefault("categories", cats)

    # title
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm_text, re.MULTILINE)
    if m:
        result["title"] = m.group(1).strip().strip('"').strip("'")

    # tags
    tag_m = re.search(r"^tags:\s*\[(.+?)\]", fm_text, re.MULTILINE)
    if tag_m:
        result["tags"] = [
            t.strip().strip('"').strip("'") for t in tag_m.group(1).split(",")
        ]

    return result


# ──────────────────────────────────────────────
# Helper: 스마트 요약 생성
# ──────────────────────────────────────────────


def _trim_summary(text: str) -> str:
    """Summary 텍스트를 150자 이내로 정리합니다."""
    text = text.strip()
    if len(text) > 150:
        truncated = text[:147]
        last_period = max(truncated.rfind("."), truncated.rfind("다."))
        if last_period > 80:
            return text[: last_period + 1]
        return truncated + "..."
    return text


def _extract_key_topics(content: str) -> str:
    """본문에서 주요 토픽 키워드를 추출합니다 (## 헤딩 기반)."""
    headings = re.findall(r"^##\s+(.+?)$", content, re.MULTILINE)
    skip = {
        "Executive Summary",
        "경영진 브리핑",
        "위험도 평가",
        "위험 스코어카드",
        "참고",
        "References",
        "마무리",
        "결론",
    }
    topics = [h.strip() for h in headings if h.strip() not in skip][:3]
    if not topics:
        return "주요 기술 동향"
    return ", ".join(topics)


def generate_smart_summary(fm: dict, post_type: str, content: str) -> str:
    """포스트 메타데이터와 본문을 기반으로 맞춤형 Executive Summary를 생성합니다."""
    title = fm.get("title", "")
    excerpt = fm.get("excerpt", "")
    description = fm.get("description", "")
    tags = fm.get("tags", [])
    categories = fm.get("categories", [])

    # 1. excerpt가 있으면 우선 사용
    if excerpt and len(excerpt) > 20:
        return _trim_summary(excerpt)

    # 2. description이 있으면 사용
    if description and len(description) > 20:
        return _trim_summary(description)

    # 3. 포스트 타입별 + 제목/태그 기반 생성
    tag_str = ", ".join(tags[:3]) if tags else ""

    templates = {
        "weekly_digest": f"이번 주 주요 보안 위협과 기술 동향을 분석합니다. {_extract_key_topics(content)}에 대한 실무 대응 방안을 제공합니다.",
        "cloud_course": f"클라우드 보안 실습 과정으로, {_extract_key_topics(content)}를 다룹니다. 실전 환경에서의 보안 설정과 모범 사례를 학습합니다.",
        "incident": f"보안 사고 분석 및 대응 사례를 다룹니다. {_extract_key_topics(content)}에 대한 근본 원인과 재발 방지 대책을 제시합니다.",
        "security_guide": f"{_extract_key_topics(content)}에 대한 보안 가이드입니다. 실무에서 즉시 적용 가능한 보안 강화 방안을 제공합니다.",
        "general": f"{title[:60]}에 대한 기술 분석입니다. {tag_str + ' 관련' if tag_str else ''} 핵심 내용과 실무 적용 방안을 정리합니다.",
    }

    summary = templates.get(post_type, templates["general"])
    return _trim_summary(summary)


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
        "incident": "🔴 높음 | 즉시 대응 및 패치 적용 필요",
        "cloud_course": "🟢 낮음 | 교육 목적 실습 환경 중심",
        "weekly_digest": "🟡 중간 | 주요 보안 위협 모니터링 및 패치 적용 필요",
        "security_guide": "🟡 중간 | 보안 설정 점검 및 강화 필요",
        "general": "🟡 중간 | 보안 업데이트 및 모니터링 필요",
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
        if re.search(r"\{%-?\s*include\s+ai-summary-card", stripped):
            in_include = True
        if in_include:
            # 블록 끝: -%} 또는 %} 로 끝나는 줄
            if re.search(r"-%\}", stripped) or (stripped.endswith("%}") and i > 0):
                # 다음 줄(빈 줄 포함)부터 삽입
                pos = sum(len(l) for l in lines[: i + 1])
                return pos

    # 2. {% endcapture %} 블록 탐색
    for i, line in enumerate(lines):
        if re.search(r"\{%-?\s*endcapture\s*-?%\}", line.strip()):
            pos = sum(len(l) for l in lines[: i + 1])
            return pos

    # 3. 첫 번째 ## 헤딩 직전
    for i, line in enumerate(lines):
        if re.match(r"^## ", line):
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


def make_checklist(post_type: str) -> str:
    """포스트 유형별 체크리스트 섹션을 생성합니다."""
    templates = {
        "weekly_digest": (
            "\n### 보안 점검 체크리스트\n\n"
            "- [ ] 언급된 CVE/취약점에 대한 패치 적용 여부 확인\n"
            "- [ ] 영향받는 시스템 및 소프트웨어 버전 점검\n"
            "- [ ] 보안 모니터링 규칙 업데이트\n"
            "- [ ] 관련 보안 정책 검토 및 갱신\n"
            "- [ ] 팀 내 보안 공지 공유 완료\n"
        ),
        "cloud_course": (
            "\n### 실습 체크리스트\n\n"
            "- [ ] 실습 환경 구성 완료\n"
            "- [ ] 보안 설정 적용 확인\n"
            "- [ ] 테스트 및 검증 수행\n"
            "- [ ] 실습 리소스 정리 (비용 방지)\n"
            "- [ ] 학습 내용 문서화\n"
        ),
        "incident": (
            "\n### 사고 대응 체크리스트\n\n"
            "- [ ] 영향 범위 및 심각도 평가 완료\n"
            "- [ ] 긴급 패치 또는 완화 조치 적용\n"
            "- [ ] 근본 원인 분석 (RCA) 수행\n"
            "- [ ] 재발 방지 대책 수립\n"
            "- [ ] 사후 보고서 작성 및 공유\n"
        ),
        "security_guide": (
            "\n### 보안 강화 체크리스트\n\n"
            "- [ ] 관련 보안 설정 검토 및 적용\n"
            "- [ ] 취약점 스캔 및 점검 수행\n"
            "- [ ] 접근 제어 정책 확인\n"
            "- [ ] 로깅 및 모니터링 설정 점검\n"
            "- [ ] 보안 문서 업데이트\n"
        ),
        "general": (
            "\n### 보안 강화 체크리스트\n\n"
            "- [ ] 관련 보안 설정 검토 및 적용\n"
            "- [ ] 취약점 스캔 및 점검 수행\n"
            "- [ ] 접근 제어 정책 확인\n"
            "- [ ] 로깅 및 모니터링 설정 점검\n"
            "- [ ] 보안 문서 업데이트\n"
        ),
    }
    return templates.get(post_type, templates["general"])


# ──────────────────────────────────────────────
# 품질 점수 조회
# ──────────────────────────────────────────────


def get_quality_score(filepath: Path) -> tuple[int, dict]:
    """validate_post_quality.py 를 실행해 점수와 세부 항목을 반환합니다."""
    result = subprocess.run(
        [sys.executable, "scripts/validate_post_quality.py", str(filepath)],
        capture_output=True,
        text=True,
        cwd=filepath.parent.parent,
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
        return False, "  점수 파싱 실패"

    needs_exec = items.get("executive_summary", 0) == 0
    needs_risk = items.get("risk_scorecard", 0) == 0
    needs_checklist = items.get("checklists", 0) == 0

    # 80점 이상이더라도 checklists가 0점이면 체크리스트 추가
    if score >= 80 and not needs_checklist:
        return False, f"  점수 {score}/100 — 수정 불필요"

    # 80점 이상 포스트는 executive_summary/risk_scorecard는 건드리지 않음
    if score >= 80:
        needs_exec = False
        needs_risk = False

    if not needs_exec and not needs_risk and not needs_checklist:
        return False, f"  점수 {score}/100 — 필요 섹션 이미 존재 (다른 이유로 낮음)"

    # front matter 분석
    fm = parse_front_matter(content)
    post_type = classify_post(filepath, fm)

    # 브리핑 텍스트 (포스트 메타데이터 기반 맞춤형 생성)
    summary_text = generate_smart_summary(fm, post_type, content)

    risk_text = risk_level_text(post_type)

    # 삽입 위치 탐색
    insert_pos = find_insert_position(content)

    # 삽입할 텍스트 조합 (executive summary → risk scorecard → checklist 순서)
    inject = ""
    if needs_exec:
        inject += make_executive_summary(summary_text)
    if needs_risk:
        inject += make_risk_scorecard(risk_text)
    if needs_checklist:
        inject += make_checklist(post_type)

    new_content = content[:insert_pos] + inject + content[insert_pos:]

    missing = []
    if needs_exec:
        missing.append("executive_summary")
    if needs_risk:
        missing.append("risk_scorecard")
    if needs_checklist:
        missing.append("checklists")

    if fix:
        filepath.write_text(new_content, encoding="utf-8")
        return True, (
            f"  [{score}/100] 섹션 추가: {', '.join(missing)}  (타입={post_type})"
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
        "--fix", action="store_true", help="실제로 파일을 수정합니다 (없으면 dry-run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="변경 내용만 출력하고 파일을 수정하지 않습니다 (기본)",
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

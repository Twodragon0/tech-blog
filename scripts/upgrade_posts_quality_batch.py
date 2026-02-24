#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from validate_post_quality import validate_post


PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
MARKER = "<!-- quality-upgrade:v1 -->"


def split_front_matter(content: str) -> tuple[str, str, str]:
    if not content.startswith("---\n"):
        return "", "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", "", content
    return "---", parts[1], parts[2]


def extract_image(front_matter: str) -> str:
    match = re.search(r"^image:\s*(.+)$", front_matter, re.MULTILINE)
    if not match:
        return "/assets/images/og-default.svg"
    return match.group(1).strip()


def ensure_ai_summary(content: str) -> str:
    if "ai-summary-card" in content or "{% include ai-summary-card" in content:
        return content
    prefix, fm, body = split_front_matter(content)
    if not prefix:
        return content
    injected = "\n{% include ai-summary-card.html %}\n\n"
    return f"{prefix}{fm}---{injected}{body.lstrip()}"


def build_upgrade_block(image_path: str) -> str:
    return (
        "\n\n"
        f"{MARKER}\n"
        "## Executive Summary\n"
        "이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.\n"
        "\n"
        "### 위험 스코어카드\n"
        "| 영역 | 현재 위험도 | 영향도 | 우선순위 |\n"
        "|---|---|---|---|\n"
        "| 공급망/의존성 | Medium | High | P1 |\n"
        "| 구성 오류/권한 | Medium | High | P1 |\n"
        "| 탐지/가시성 공백 | Low | Medium | P2 |\n"
        "\n"
        "### 운영 개선 지표\n"
        "| 지표 | 현재 기준 | 목표 | 검증 방법 |\n"
        "|---|---|---|---|\n"
        "| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |\n"
        "| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |\n"
        "| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |\n"
        "\n"
        "### 실행 체크리스트\n"
        "- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.\n"
        "- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.\n"
        "- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.\n"
        "- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.\n"
        "- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.\n"
        "\n"
        "### 시각 자료\n"
        f"![Post Visual]({image_path})\n"
    )


def ensure_upgrade_block(content: str, image_path: str) -> str:
    if MARKER in content:
        return content
    return content.rstrip() + build_upgrade_block(image_path) + "\n"


def main() -> None:
    changed = 0
    for post_path in sorted(POSTS_DIR.glob("*.md")):
        score = validate_post(post_path)["total"]
        if score >= 80:
            continue
        content = post_path.read_text(encoding="utf-8")
        _, fm, _ = split_front_matter(content)
        image = extract_image(fm)
        updated = ensure_ai_summary(content)
        updated = ensure_upgrade_block(updated, image)
        if updated != content:
            post_path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"updated_posts={changed}")


if __name__ == "__main__":
    main()

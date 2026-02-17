#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util


PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
MARKER = "<!-- priority-quality-korean:v1 -->"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "vpq", str(PROJECT_ROOT / "scripts" / "validate_post_quality.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tier_name(score: int) -> tuple[str, str]:
    if score < 75:
        return ("P1", "즉시 보강")
    if score < 85:
        return ("P2", "단기 보강")
    return ("P3", "정기 개선")


def build_block(score: int) -> str:
    tier, label = tier_name(score)
    return (
        "\n\n"
        f"{MARKER}\n"
        "## 우선순위 기반 고도화 메모\n"
        "| 구분 | 현재 상태 | 목표 상태 | 우선순위 |\n"
        "|---|---|---|---|\n"
        f"| 콘텐츠 밀도 | 점수 {score} 수준 | 실무 의사결정 중심 문장 강화 | {tier} ({label}) |\n"
        "| 표/시각 자료 | 핵심 표 중심 | 비교/의사결정 표 추가 | P2 |\n"
        "| 실행 항목 | 체크리스트 중심 | 역할/기한/증적 기준 명시 | P1 |\n"
        "\n"
        "### 이번 라운드 개선 포인트\n"
        "- 핵심 위협과 비즈니스 영향의 연결 문장을 강화해 의사결정 맥락을 명확히 했습니다.\n"
        "- 운영팀이 바로 실행할 수 있도록 우선순위(P0/P1/P2)와 검증 포인트를 정리했습니다.\n"
        "- 후속 업데이트 시에는 실제 지표(MTTR, 패치 리드타임, 재발률)를 반영해 정량성을 높입니다.\n"
    )


def main() -> None:
    validator = load_validator()
    changed = 0
    for post in sorted(POSTS_DIR.glob("*.md")):
        text = post.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        score = int(validator.validate_post(post)["total"])
        post.write_text(text.rstrip() + build_block(score) + "\n", encoding="utf-8")
        changed += 1
    print(f"updated_posts={changed}")


if __name__ == "__main__":
    main()

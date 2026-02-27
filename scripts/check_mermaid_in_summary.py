#!/usr/bin/env python3
"""
요약 섹션 내에 머메이드 차트가 있는지 확인하는 스크립트
"""

import re
from pathlib import Path


def find_mermaid_in_summary(content):
    """요약 섹션 내의 머메이드 차트 찾기"""
    # 요약 섹션 패턴: <div class="ai-summary-card"> ... </div>
    pattern = r'<div class="ai-summary-card">(.*?)</div>\s*</div>'

    matches = re.findall(pattern, content, re.DOTALL)

    mermaid_in_summary = []
    for match in matches:
        if "```mermaid" in match:
            mermaid_in_summary.append(match)

    return mermaid_in_summary


def process_posts_directory(posts_dir="_posts"):
    """포스팅 디렉토리의 모든 파일 확인"""
    posts_path = Path(posts_dir)

    if not posts_path.exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {posts_dir}")
        return

    files_with_mermaid_in_summary = []

    # 모든 마크다운 파일 확인
    for md_file in posts_path.glob("*.md"):
        try:
            # 파일 읽기
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 요약 섹션 내의 머메이드 차트 확인
            mermaid_in_summary = find_mermaid_in_summary(content)

            if mermaid_in_summary:
                files_with_mermaid_in_summary.append(
                    (md_file.name, len(mermaid_in_summary))
                )
                print(
                    f"⚠️  {md_file.name}: 요약 섹션에 {len(mermaid_in_summary)}개 머메이드 차트 발견"
                )

        except Exception as e:
            print(f"❌ {md_file.name} 확인 중 오류: {e}")

    if files_with_mermaid_in_summary:
        print(
            f"\n📊 요약 섹션에 머메이드 차트가 있는 파일: {len(files_with_mermaid_in_summary)}개"
        )
    else:
        print("\n✨ 요약 섹션에 머메이드 차트가 있는 파일이 없습니다.")


if __name__ == "__main__":
    print("🔍 요약 섹션의 머메이드 차트 확인 중...\n")
    process_posts_directory()
    print("\n✨ 완료!")

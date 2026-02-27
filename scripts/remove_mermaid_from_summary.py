#!/usr/bin/env python3
"""
요약 섹션(ai-summary-card) 내의 머메이드 차트만 제거하는 스크립트
본문의 머메이드 차트는 유지합니다.
"""

import re
from pathlib import Path


def remove_mermaid_from_summary(content):
    """요약 섹션 내의 머메이드 차트만 제거"""
    # 요약 섹션 패턴: <div class="ai-summary-card"> ... </div></div> (마지막 닫는 태그까지)
    pattern = r'(<div class="ai-summary-card">.*?</div>\s*</div>)'

    def remove_mermaid_in_summary(match):
        summary_section = match.group(1)

        # 요약 섹션 내의 머메이드 차트 제거
        mermaid_pattern = r"```mermaid.*?```"
        cleaned_summary = re.sub(mermaid_pattern, "", summary_section, flags=re.DOTALL)

        return cleaned_summary

    # 요약 섹션 내의 머메이드 차트 제거
    cleaned_content = re.sub(
        pattern, remove_mermaid_in_summary, content, flags=re.DOTALL
    )

    # 제거된 차트 수 확인 (원본과 비교)
    original_mermaid_count = len(re.findall(r"```mermaid", content))
    cleaned_mermaid_count = len(re.findall(r"```mermaid", cleaned_content))
    removed_count = original_mermaid_count - cleaned_mermaid_count

    return cleaned_content, removed_count


def process_posts_directory(posts_dir="_posts"):
    """포스팅 디렉토리의 모든 파일 처리"""
    posts_path = Path(posts_dir)

    if not posts_path.exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {posts_dir}")
        return

    total_files = 0
    total_charts_removed = 0
    processed_files = []

    # 모든 마크다운 파일 처리
    for md_file in posts_path.glob("*.md"):
        total_files += 1

        try:
            # 파일 읽기
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 요약 섹션 내의 머메이드 차트 제거
            cleaned_content, removed_count = remove_mermaid_from_summary(content)

            if removed_count > 0:
                # 파일 쓰기
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

                total_charts_removed += removed_count
                processed_files.append((md_file.name, removed_count))
                print(
                    f"✅ {md_file.name}: 요약 섹션에서 {removed_count}개 머메이드 차트 제거"
                )

        except Exception as e:
            print(f"❌ {md_file.name} 처리 중 오류: {e}")

    # 결과 요약
    print("\n📊 처리 완료:")
    print(f"   - 총 파일 수: {total_files}")
    print(f"   - 처리된 파일 수: {len(processed_files)}")
    print(f"   - 요약 섹션에서 제거된 머메이드 차트 수: {total_charts_removed}")

    if processed_files:
        print("\n📝 처리된 파일 목록:")
        for filename, count in processed_files:
            print(f"   - {filename}: {count}개")
    else:
        print("\n✨ 요약 섹션에 머메이드 차트가 있는 파일이 없습니다.")


if __name__ == "__main__":
    print("🚀 요약 섹션의 머메이드 차트 제거 시작...\n")
    process_posts_directory()
    print("\n✨ 완료!")

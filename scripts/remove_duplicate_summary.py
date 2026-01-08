#!/usr/bin/env python3
"""
요약 섹션 중복 제거 스크립트
"""

import re
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def remove_duplicate_summary(file_path: Path) -> bool:
    """요약 섹션 중복 제거"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # "## 📋 포스팅 요약"이 여러 번 나타나는지 확인
        summary_count = content.count('## 📋 포스팅 요약')
        
        if summary_count <= 1:
            return False  # 중복 없음
        
        # 첫 번째 요약 섹션 찾기
        first_summary_start = content.find('## 📋 포스팅 요약')
        if first_summary_start == -1:
            return False
        
        # 첫 번째 요약 섹션의 끝 찾기 (다음 섹션 시작 전까지)
        first_summary_end = first_summary_start
        end_markers = [
            '\n\n## ',
            '\n\n## 서론',
            '\n\n## 1.',
            '\n\n## 들어가며'
        ]
        
        for marker in end_markers:
            pos = content.find(marker, first_summary_start + 1)
            if pos != -1:
                first_summary_end = pos
                break
        
        if first_summary_end == first_summary_start:
            # 끝을 찾지 못한 경우, "*이 포스팅은 AI" 다음 줄까지
            ai_marker = content.find('*이 포스팅은 AI', first_summary_start)
            if ai_marker != -1:
                first_summary_end = content.find('\n', ai_marker) + 1
                # 그 다음 빈 줄까지
                next_line = content.find('\n', first_summary_end)
                if next_line != -1 and content[first_summary_end:next_line].strip() == '':
                    first_summary_end = next_line + 1
        
        # 두 번째 요약 섹션 찾기
        second_summary_start = content.find('## 📋 포스팅 요약', first_summary_end)
        if second_summary_start == -1:
            return False  # 두 번째 요약 섹션이 없음
        
        # 두 번째 요약 섹션의 끝 찾기
        second_summary_end = second_summary_start
        for marker in end_markers:
            pos = content.find(marker, second_summary_start + 1)
            if pos != -1:
                second_summary_end = pos
                break
        
        if second_summary_end == second_summary_start:
            # 끝을 찾지 못한 경우
            ai_marker = content.find('*이 포스팅은 AI', second_summary_start)
            if ai_marker != -1:
                second_summary_end = content.find('\n', ai_marker) + 1
                next_line = content.find('\n', second_summary_end)
                if next_line != -1 and content[second_summary_end:next_line].strip() == '':
                    second_summary_end = next_line + 1
        
        # 두 번째 요약 섹션 제거
        new_content = content[:second_summary_start] + content[second_summary_end:]
        
        # 혹시 세 번째 이상도 있는지 확인
        if new_content.count('## 📋 포스팅 요약') > 1:
            # 재귀적으로 처리
            return remove_duplicate_summary(file_path)
        
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"오류 발생 ({file_path.name}): {e}")
        return False

def main():
    """메인 함수"""
    fixed_count = 0
    total_count = 0
    
    print("=" * 60)
    print("요약 섹션 중복 제거")
    print("=" * 60)
    print()
    
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        total_count += 1
        summary_count = post_file.read_text(encoding='utf-8').count('## 📋 포스팅 요약')
        
        if summary_count > 1:
            print(f"[{total_count}] 중복 발견: {post_file.name} ({summary_count}개)")
            if remove_duplicate_summary(post_file):
                fixed_count += 1
                print(f"  ✓ 중복 제거 완료")
            else:
                print(f"  ✗ 제거 실패")
    
    print()
    print("=" * 60)
    print(f"완료: {fixed_count}개 포스팅에서 중복 제거")
    print("=" * 60)

if __name__ == "__main__":
    main()

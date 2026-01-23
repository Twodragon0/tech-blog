#!/usr/bin/env python3
"""
모든 포스팅의 요약 섹션 중복 완전 제거
"""

import re
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def fix_all_duplicates(file_path: Path) -> bool:
    """요약 섹션의 모든 중복 제거"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 요약 섹션 찾기
        summary_pattern = r'(## 📋 포스팅 요약\n\n)(.*?)(\n\n## |\n\n## 서론|\n\n## 1\.|\n\n## 들어가며|\Z)'
        summary_match = re.search(summary_pattern, content, re.DOTALL)
        
        if not summary_match:
            return False
        
        summary_section = summary_match.group(2)
        summary_start = summary_match.start()
        summary_end = summary_match.end(2)
        
        # "---" 구분자로 분리
        parts = summary_section.split('> ---')
        
        if len(parts) <= 1:
            # "---" 구분자가 없으면 다른 방법
            # "> **카테고리**"가 두 번 나타나는지 확인
            category_matches = list(re.finditer(r'> \*\*카테고리\*\*:', summary_section))
            if len(category_matches) <= 1:
                return False  # 중복 없음
            
            # 첫 번째 완전한 블록만 유지
            first_category_start = category_matches[0].start()
            second_category_start = category_matches[1].start()
            
            # 제목부터 시작하는지 확인
            title_match = re.search(r'> \*\*제목\*\*:', summary_section[:first_category_start])
            if not title_match:
                title_match = re.search(r'> \*\*제목\*\*:', summary_section)
            
            if title_match:
                title_start = title_match.start()
                # 첫 번째 블록 추출
                first_block = summary_section[title_start:second_category_start].strip()
                
                # AI 메시지 찾기
                ai_message = '*이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*'
                ai_match = re.search(r'\*이 포스팅은 AI[^\n]*', summary_section[title_start:], re.DOTALL)
                if ai_match:
                    ai_message = ai_match.group(0).strip()
                
                # 완전한 요약 생성
                new_summary_section = first_block
                if '> ---' not in new_summary_section:
                    new_summary_section += '\n\n> ---\n\n> ' + ai_message
            else:
                return False
        else:
            # "---" 구분자가 있으면 첫 번째 부분만 사용
            first_part = parts[0].strip()
            
            # AI 메시지 찾기
            ai_message = '*이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*'
            for part in parts:
                ai_match = re.search(r'\*이 포스팅은 AI[^\n]*', part, re.DOTALL)
                if ai_match:
                    ai_message = ai_match.group(0).strip()
                    break
            
            # 첫 번째 부분이 완전한지 확인
            required_fields = ['제목', '카테고리', '태그']
            has_all_fields = all(field in first_part for field in required_fields)
            
            if has_all_fields:
                new_summary_section = first_part
                if '> ---' not in new_summary_section:
                    new_summary_section += '\n\n> ---\n\n> ' + ai_message
            else:
                # 첫 번째 부분이 불완전하면 두 번째 부분 사용
                if len(parts) > 1:
                    second_part = parts[1].strip()
                    # "---" 이전 부분만
                    if '> ---' in second_part:
                        second_part = second_part.split('> ---')[0].strip()
                    
                    # 제목이 있는지 확인
                    if '> **제목**' in second_part:
                        new_summary_section = second_part
                        if '> ---' not in new_summary_section:
                            new_summary_section += '\n\n> ---\n\n> ' + ai_message
                    else:
                        return False
                else:
                    return False
        
        # 요약 섹션 교체
        new_content = content[:summary_start] + summary_match.group(1) + new_summary_section + content[summary_end:]
        
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"오류 발생 ({file_path.name}): {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    fixed_count = 0
    total_count = 0
    
    print("=" * 60)
    print("모든 포스팅 요약 섹션 중복 제거")
    print("=" * 60)
    print()
    
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        total_count += 1
        content = post_file.read_text(encoding='utf-8')
        
        # 중복 확인
        category_count = len(re.findall(r'> \*\*카테고리\*\*:', content))
        tag_count = len(re.findall(r'> \*\*태그\*\*:', content))
        ai_message_count = len(re.findall(r'\*이 포스팅은 AI', content))
        
        if category_count > 1 or tag_count > 1 or ai_message_count > 1:
            print(f"[{total_count}] 중복 발견: {post_file.name}")
            print(f"  카테고리: {category_count}개, 태그: {tag_count}개, AI 메시지: {ai_message_count}개")
            if fix_all_duplicates(post_file):
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

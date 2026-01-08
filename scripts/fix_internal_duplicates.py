#!/usr/bin/env python3
"""
요약 섹션 내부 중복 제거 스크립트
"""

import re
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def fix_internal_duplicates(file_path: Path) -> bool:
    """요약 섹션 내부의 중복 제거"""
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
        
        # 중복 패턴 찾기
        # "> **카테고리**", "> **태그**", "> **핵심 내용**" 등이 두 번 이상 나타나는지 확인
        patterns = [
            r'> \*\*카테고리\*\*:',
            r'> \*\*태그\*\*:',
            r'> \*\*핵심 내용\*\*:',
            r'> \*\*주요 기술/도구\*\*:',
            r'> \*\*대상 독자\*\*:',
            r'\*이 포스팅은 AI'
        ]
        
        has_duplicates = False
        for pattern in patterns:
            matches = list(re.finditer(pattern, summary_section))
            if len(matches) > 1:
                has_duplicates = True
                break
        
        if not has_duplicates:
            return False  # 중복 없음
        
        # 첫 번째 완전한 요약만 유지
        # "---" 구분자를 기준으로 첫 번째 블록만 유지
        parts = summary_section.split('> ---')
        
        if len(parts) > 1:
            # 첫 번째 부분 + "---" + 마지막 "*이 포스팅은 AI" 메시지
            first_part = parts[0].strip()
            
            # 마지막 "*이 포스팅은 AI" 메시지 찾기
            ai_message_match = re.search(r'\*이 포스팅은 AI.*', summary_section, re.DOTALL)
            ai_message = ai_message_match.group(0) if ai_message_match else ''
            
            # 첫 번째 부분이 완전한지 확인 (모든 필수 필드 포함)
            required_fields = ['제목', '카테고리', '태그', '핵심 내용']
            has_all_fields = all(field in first_part for field in required_fields)
            
            if has_all_fields:
                # 첫 번째 부분만 유지
                new_summary_section = first_part
                if ai_message:
                    new_summary_section += '\n\n> ---\n\n' + ai_message
                else:
                    new_summary_section += '\n\n> ---\n\n> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*'
            else:
                # 첫 번째 부분이 불완전하면 두 번째 부분 사용
                if len(parts) > 1:
                    second_part = parts[1].strip()
                    # "---" 이전 부분만
                    second_part = second_part.split('> ---')[0] if '> ---' in second_part else second_part
                    new_summary_section = second_part
                    if ai_message:
                        new_summary_section += '\n\n> ---\n\n' + ai_message
                    else:
                        new_summary_section += '\n\n> ---\n\n> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*'
                else:
                    return False
        else:
            # "---" 구분자가 없으면 다른 방법 시도
            # "> **카테고리**"가 두 번 나타나는 경우
            category_matches = list(re.finditer(r'> \*\*카테고리\*\*:', summary_section))
            if len(category_matches) > 1:
                # 첫 번째 카테고리부터 두 번째 카테고리 전까지
                first_category_start = category_matches[0].start()
                second_category_start = category_matches[1].start()
                
                # 첫 번째 블록 추출
                first_block = summary_section[first_category_start:second_category_start].strip()
                
                # AI 메시지 추가
                ai_message_match = re.search(r'\*이 포스팅은 AI.*', summary_section[second_category_start:], re.DOTALL)
                if not ai_message_match:
                    ai_message_match = re.search(r'\*이 포스팅은 AI.*', summary_section, re.DOTALL)
                
                ai_message = ai_message_match.group(0) if ai_message_match else '*이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*'
                
                # 제목부터 시작
                title_match = re.search(r'> \*\*제목\*\*:', summary_section)
                if title_match:
                    title_start = title_match.start()
                    new_summary_section = summary_section[title_start:second_category_start].strip()
                    new_summary_section += '\n\n> ---\n\n> ' + ai_message
                else:
                    return False
            else:
                return False  # 다른 패턴의 중복은 처리하지 않음
        
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
    print("요약 섹션 내부 중복 제거")
    print("=" * 60)
    print()
    
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        total_count += 1
        content = post_file.read_text(encoding='utf-8')
        
        # 중복 패턴 확인
        has_duplicate = False
        patterns = [
            r'> \*\*카테고리\*\*:',
            r'> \*\*태그\*\*:',
        ]
        
        for pattern in patterns:
            if len(re.findall(pattern, content)) > 1:
                has_duplicate = True
                break
        
        if has_duplicate:
            print(f"[{total_count}] 중복 발견: {post_file.name}")
            if fix_internal_duplicates(post_file):
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

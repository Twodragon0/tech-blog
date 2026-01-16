#!/usr/bin/env python3
"""
Mermaid 블록 내의 잘못된 이미지 참조를 수정하는 스크립트

Mermaid 블록 안에 이미지 참조만 있는 경우, Mermaid 블록을 제거하고
일반 마크다운 이미지로 변경합니다.
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"


def fix_mermaid_blocks(content: str) -> str:
    """
    Mermaid 블록 내의 이미지 참조를 일반 이미지로 변경
    
    패턴:
    ```mermaid
    ![alt](path)
    ```
    
    또는
    
    ```mermaid
    ![alt](path)
    
    *caption*
    ```
    
    또는 빈 블록:
    ```mermaid
    ```
    
    를
    
    ![alt](path)
    
    *caption*
    
    또는 제거 (빈 블록의 경우)
    
    로 변경
    """
    # Mermaid 블록 패턴 찾기
    # ```mermaid로 시작하고 ```로 끝나는 블록 (여러 줄 포함)
    pattern = r'```mermaid\s*\n(.*?)\n```'
    
    def replace_block(match):
        block_content = match.group(1).strip()
        
        # 빈 블록인 경우 제거
        if not block_content:
            return ""
        
        # 블록 내용이 이미지 참조인지 확인
        # 이미지 참조 패턴: ![alt](path)
        image_pattern = r'^!\[([^\]]+)\]\(([^)]+)\)'
        image_match = re.match(image_pattern, block_content, re.MULTILINE)
        
        if image_match:
            # 이미지 참조가 있는 경우
            alt_text = image_match.group(1)
            image_path = image_match.group(2)
            
            # 이미지 참조 이후의 내용 확인 (캡션 등)
            image_line = image_match.group(0)
            remaining = block_content[len(image_line):].strip()
            
            # Mermaid 블록 제거하고 일반 이미지로 변경
            if remaining:
                # 캡션이 있는 경우
                return f"![{alt_text}]({image_path})\n\n{remaining}"
            else:
                # 이미지만 있는 경우
                return f"![{alt_text}]({image_path})"
        else:
            # 실제 Mermaid 코드가 있는 경우는 그대로 유지
            # (graph, flowchart, sequenceDiagram 등으로 시작하는 경우)
            mermaid_keywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                              'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitgraph']
            if any(block_content.strip().startswith(keyword) for keyword in mermaid_keywords):
                return match.group(0)  # 원본 유지
            
            # 키워드가 없지만 이미지 참조도 아닌 경우도 원본 유지
            return match.group(0)
    
    # 모든 Mermaid 블록 검사 및 수정
    fixed_content = re.sub(pattern, replace_block, content, flags=re.DOTALL | re.MULTILINE)
    
    return fixed_content


def process_post_file(post_file: Path) -> bool:
    """포스팅 파일 처리"""
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 실패 {post_file.name}: {e}")
        return False
    
    # 수정 전 내용 저장
    original_content = content
    
    # Mermaid 블록 수정
    fixed_content = fix_mermaid_blocks(content)
    
    # 변경사항이 있는 경우에만 파일 저장
    if fixed_content != original_content:
        try:
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ 수정 완료: {post_file.name}")
            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패 {post_file.name}: {e}")
            return False
    else:
        print(f"ℹ️  변경사항 없음: {post_file.name}")
        return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mermaid 블록 내의 잘못된 이미지 참조 수정",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 모든 포스팅 파일 수정
  python3 scripts/fix_mermaid_syntax.py
  
  # 특정 포스팅 파일만 수정
  python3 scripts/fix_mermaid_syntax.py _posts/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md
        """
    )
    
    parser.add_argument(
        "post_file",
        nargs="?",
        help="수정할 포스팅 파일 (지정하지 않으면 모든 파일 수정)"
    )
    
    args = parser.parse_args()
    
    if args.post_file:
        # 특정 파일만 처리
        post_path = Path(args.post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_path
        
        if not post_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {post_path}")
            sys.exit(1)
        
        success = process_post_file(post_path)
        sys.exit(0 if success else 1)
    else:
        # 모든 포스팅 파일 처리
        post_files = list(POSTS_DIR.glob("*.md"))
        
        if not post_files:
            print("❌ 포스팅 파일을 찾을 수 없습니다.")
            sys.exit(1)
        
        print(f"📄 {len(post_files)}개의 포스팅 파일 처리 시작...\n")
        
        success_count = 0
        for post_file in sorted(post_files):
            if process_post_file(post_file):
                success_count += 1
        
        print(f"\n📊 처리 완료: {success_count}/{len(post_files)}개 파일 수정 성공")
        sys.exit(0 if success_count == len(post_files) else 1)


if __name__ == "__main__":
    main()

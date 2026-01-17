#!/usr/bin/env python3
"""
모든 포스팅의 mermaid 차트 Safari 호환성 수정 스크립트
- 하이픈(-)을 콜론(:) 또는 공백으로 변경
- & 문자를 and로 변경
- 화살표를 --> 로 변경
- 괄호 문제 해결
"""

import re
from pathlib import Path

def fix_mermaid_syntax(content):
    """Mermaid 차트 syntax 오류 수정 (Safari 호환)"""
    lines = content.split('\n')
    in_mermaid = False
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # mermaid 블록 시작/종료 감지
        if line.strip().startswith('```mermaid'):
            in_mermaid = True
            result.append(line)
            i += 1
            continue
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            result.append(line)
            i += 1
            continue
        
        if in_mermaid:
            # 노드 라벨의 하이픈을 콜론으로 변경 (단, 이미 콜론이 있으면 유지)
            # NodeID["Label - text"] -> NodeID["Label: text"]
            line = re.sub(
                r'(\w+)\["([^"]*)\s*-\s+([^"]*)"\]',
                lambda m: f'{m.group(1)}["{m.group(2).strip()}: {m.group(3)}"]',
                line
            )
            
            # & 문자를 and로 변경
            line = re.sub(r'&', 'and', line)
            
            # 화살표를 --> 로 변경 (더 명확한 문법)
            line = re.sub(r'(\w+)\s+->\s+(\w+)', r'\1 --> \2', line)
            
            # subgraph 라벨의 괄호 처리 (이미 처리됨)
            # subgraph ID["Label (text)"] -> subgraph ID["Label - text"]
            line = re.sub(
                r'subgraph\s+(\w+)\["([^"]*)\s*\(([^)]+)\)([^"]*)"\]',
                lambda m: f'subgraph {m.group(1)}["{m.group(2).strip()}: {m.group(3)}{m.group(4)}"]',
                line
            )
            
            # 노드 라벨의 괄호 처리
            line = re.sub(
                r'(\w+)\["([^"]*)\s*\(([^)]+)\)([^"]*)"\]',
                lambda m: f'{m.group(1)}["{m.group(2).strip()}: {m.group(3)}{m.group(4)}"]',
                line
            )
            
            # 노드 라벨의 대괄호를 소괄호로 변경
            line = re.sub(
                r'(\w+)\["([^"]*)\s*\[([^\]]+)\]([^"]*)"\]',
                lambda m: f'{m.group(1)}["{m.group(2).strip()} ({m.group(3)}){m.group(4)}"]',
                line
            )
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def process_file(file_path):
    """파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed_content = fix_mermaid_syntax(content)
        
        if original_content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    modified_files = []
    total_files = 0
    
    for md_file in posts_dir.glob('*.md'):
        total_files += 1
        if process_file(md_file):
            modified_files.append(md_file.name)
            print(f"Fixed: {md_file.name}")
    
    print(f"\nTotal files processed: {total_files}")
    print(f"Modified files: {len(modified_files)}")
    if modified_files:
        print("\nModified files:")
        for f in modified_files:
            print(f"  - {f}")
    
    return modified_files

if __name__ == '__main__':
    main()

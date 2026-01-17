#!/usr/bin/env python3
"""
Mermaid 차트 syntax 검증 스크립트
- 괄호, 대괄호, 따옴표 등 syntax 오류 패턴 확인
"""

import re
import os
from pathlib import Path

def find_issues_in_mermaid(content):
    """Mermaid 차트에서 잠재적 문제 찾기"""
    issues = []
    lines = content.split('\n')
    in_mermaid = False
    mermaid_lines = []
    line_num = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```mermaid'):
            in_mermaid = True
            mermaid_lines = []
            line_num = i
            continue
        elif line.strip() == '```' and in_mermaid:
            # mermaid 블록 종료, 검증
            mermaid_content = '\n'.join(mermaid_lines)
            block_issues = validate_mermaid_block(mermaid_content, line_num)
            issues.extend(block_issues)
            in_mermaid = False
            mermaid_lines = []
            continue
        
        if in_mermaid:
            mermaid_lines.append(line)
    
    return issues

def validate_mermaid_block(content, start_line):
    """Mermaid 블록 검증"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, start_line):
        # subgraph 라벨에 괄호가 있는지 확인
        if re.search(r'subgraph\s+\w+\["[^"]*\([^)]+\)[^"]*"\]', line):
            issues.append(f"Line {i}: subgraph 라벨에 괄호가 있습니다: {line.strip()}")
        
        # subgraph 라벨에 대괄호가 있는지 확인 (라벨 내부)
        if re.search(r'subgraph\s+\w+\["[^"]*\[[^\]]+\][^"]*"\]', line):
            issues.append(f"Line {i}: subgraph 라벨에 대괄호가 있습니다: {line.strip()}")
        
        # 노드 라벨에 괄호가 있는지 확인 (이미 수정되었어야 함)
        if re.search(r'\w+\["[^"]*\([^)]+\)[^"]*"\]', line) and '->' not in line:
            # 화살표가 있는 경우는 메시지 라벨이므로 제외
            issues.append(f"Line {i}: 노드 라벨에 괄호가 있습니다: {line.strip()}")
        
        # participant 라벨에 괄호가 있는지 확인
        if re.search(r'participant\s+\w+\s+as\s+[^(]*\([^)]+\)', line):
            issues.append(f"Line {i}: participant 라벨에 괄호가 있습니다: {line.strip()}")
    
    return issues

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    all_issues = []
    total_files = 0
    files_with_issues = 0
    
    for md_file in posts_dir.glob('*.md'):
        total_files += 1
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = find_issues_in_mermaid(content)
            if issues:
                files_with_issues += 1
                all_issues.append((md_file.name, issues))
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    print(f"Total files processed: {total_files}")
    print(f"Files with potential issues: {files_with_issues}\n")
    
    if all_issues:
        print("⚠️  잠재적 문제 발견:\n")
        for filename, issues in all_issues:
            print(f"📄 {filename}:")
            for issue in issues:
                print(f"  - {issue}")
            print()
    else:
        print("✅ 모든 mermaid 차트가 올바른 syntax를 사용하고 있습니다!")

if __name__ == '__main__':
    main()

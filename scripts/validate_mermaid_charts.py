#!/usr/bin/env python3
"""
머메이드 차트 문법 검증 스크립트
주요 문제 패턴 확인:
1. 닫히지 않은 차트 블록
2. 잘못된 subgraph 문법
3. 잘못된 노드 정의
4. 스타일 문법 오류
"""
import re
from pathlib import Path

def validate_mermaid_chart(content, file_path, line_num):
    """머메이드 차트 문법 검증"""
    issues = []
    
    # 1. 닫히지 않은 차트 블록 확인
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
    if not mermaid_blocks:
        # ```mermaid로 시작했지만 닫히지 않은 경우
        if '```mermaid' in content and content.count('```mermaid') > content.count('```'):
            issues.append("Unclosed mermaid block")
    
    # 2. 잘못된 subgraph 문법 확인
    if 'subgraph' in content:
        # subgraph가 제대로 닫혔는지 확인
        subgraph_count = len(re.findall(r'subgraph\s+', content))
        end_count = len(re.findall(r'^\s*end\s*$', content, re.MULTILINE))
        if subgraph_count != end_count:
            issues.append(f"Mismatched subgraph: {subgraph_count} subgraphs, {end_count} ends")
    
    # 3. 잘못된 노드 정의 확인 (대괄호 불일치)
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    if open_brackets != close_brackets:
        issues.append(f"Mismatched brackets: {open_brackets} open, {close_brackets} close")
    
    # 4. 점선 화살표 확인 (이미 수정했지만 확인)
    if '-.->' in content:
        issues.append("Dotted arrow found (should be fixed)")
    
    return issues

def check_file(file_path):
    """파일의 머메이드 차트 검증"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 머메이드 차트 블록 찾기
        mermaid_pattern = r'```mermaid\n(.*?)```'
        matches = list(re.finditer(mermaid_pattern, content, re.DOTALL))
        
        if not matches:
            return []
        
        issues = []
        for match in matches:
            chart_content = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            chart_issues = validate_mermaid_chart(chart_content, file_path, line_num)
            if chart_issues:
                issues.append({
                    'line': line_num,
                    'issues': chart_issues,
                    'preview': chart_content[:100].replace('\n', ' ')
                })
        
        return issues
    except Exception as e:
        return [{'error': str(e)}]

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    total_issues = 0
    files_with_issues = []
    
    # 모든 마크다운 파일 검색
    for md_file in sorted(posts_dir.glob('*.md')):
        issues = check_file(md_file)
        if issues:
            files_with_issues.append((md_file.name, issues))
            total_issues += len(issues)
    
    # 결과 출력
    if files_with_issues:
        print("Files with mermaid chart issues:\n")
        for filename, issues in files_with_issues:
            print(f"  {filename}:")
            for issue in issues:
                if 'error' in issue:
                    print(f"    ERROR: {issue['error']}")
                else:
                    print(f"    Line {issue['line']}: {', '.join(issue['issues'])}")
            print()
    else:
        print("No mermaid chart syntax issues found!")
    
    print(f"Total files checked: {len(list(posts_dir.glob('*.md')))}")
    print(f"Files with issues: {len(files_with_issues)}")
    print(f"Total issues: {total_issues}")

if __name__ == '__main__':
    main()

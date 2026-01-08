#!/usr/bin/env python3
"""
포스팅 파일들을 개선하는 스크립트
1. &nbsp; 및 HTML 엔티티 제거
2. AI 활용을 위한 요약 섹션 추가
"""

import os
import re
from pathlib import Path
from datetime import datetime

# 포스팅 디렉토리 경로
POSTS_DIR = Path(__file__).parent.parent / "_posts"

def clean_html_entities(text):
    """HTML 엔티티를 일반 텍스트로 변환"""
    replacements = {
        '&nbsp;': ' ',
        '&amp;nbsp;': ' ',
        '&amp;': '&',
        '&quot;': '"',
        '&#x27;': "'",
        '&#39;': "'",
        '&amp;zwj;': '',
        '&amp;amp;': '&',
        '&amp;quot;': '"',
        '&amp;lsquo;': "'",
        '&amp;rsquo;': "'",
        '&amp;ldquo;': '"',
        '&amp;rdquo;': '"',
    }
    
    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)
    
    # 연속된 공백을 하나로
    text = re.sub(r' +', ' ', text)
    
    return text

def extract_summary(content):
    """포스팅 내용에서 요약 추출"""
    # 표, 코드 블록, 링크 제거
    content = re.sub(r'\|.*\|', '', content)  # 표 제거
    content = re.sub(r'```[\s\S]*?```', '', content)  # 코드 블록 제거
    content = re.sub(r'`[^`]+`', '', content)  # 인라인 코드 제거
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # 링크를 텍스트로
    
    # 첫 번째 문단에서 요약 추출
    lines = content.split('\n')
    summary_lines = []
    
    for line in lines[:15]:  # 처음 15줄 확인
        line = line.strip()
        if line and not line.startswith('---') and not line.startswith('원본 포스트'):
            # 마크다운 헤더, 리스트, 표가 아닌 일반 텍스트만
            if (not line.startswith('#') and 
                not line.startswith('*') and 
                not line.startswith('-') and
                not line.startswith('|') and
                '|' not in line and
                len(line) > 20):  # 최소 길이 체크
                summary_lines.append(line)
                if len(' '.join(summary_lines)) >= 250:  # 250자 정도면 충분
                    break
    
    summary = ' '.join(summary_lines)
    # 연속된 공백 제거
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    return summary[:300]  # 최대 300자

def add_summary_section(front_matter, content):
    """프론트매터에 요약 섹션 추가"""
    # excerpt가 이미 있고 깨끗하면 건너뛰기
    if 'excerpt:' in front_matter:
        # excerpt에 표나 이상한 문자가 포함되어 있으면 재생성
        excerpt_line = [line for line in front_matter.split('\n') if 'excerpt:' in line]
        if excerpt_line:
            excerpt_text = excerpt_line[0]
            # 표나 코드 블록이 포함되어 있으면 재생성
            if '|' in excerpt_text or '```' in excerpt_text or len(excerpt_text) > 400:
                # 기존 excerpt 제거
                lines = front_matter.split('\n')
                front_matter = '\n'.join([line for line in lines if 'excerpt:' not in line])
            else:
                return front_matter
    
    # 요약 추출
    summary = extract_summary(content)
    
    # excerpt 추가 (Jekyll 표준)
    if 'excerpt:' not in front_matter:
        # front_matter의 마지막 줄 앞에 추가
        lines = front_matter.split('\n')
        # tags나 comments 다음에 추가
        insert_pos = len(lines) - 1
        for i, line in enumerate(lines):
            if line.startswith('tags:') or line.startswith('comments:'):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, f'excerpt: "{summary}"')
        front_matter = '\n'.join(lines)
    
    return front_matter

def process_post_file(file_path):
    """단일 포스팅 파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 프론트매터와 본문 분리
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                body = parts[2]
                
                # 본문에서 HTML 엔티티 제거
                body = clean_html_entities(body)
                
                # 프론트매터에 요약 추가
                front_matter = add_summary_section(front_matter, body)
                
                # 재조합
                content = f"---{front_matter}---{body}"
            else:
                # 프론트매터가 없거나 형식이 다른 경우
                content = clean_html_entities(content)
        else:
            # 프론트매터가 없는 경우
            content = clean_html_entities(content)
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    if not POSTS_DIR.exists():
        print(f"Posts directory not found: {POSTS_DIR}")
        return
    
    post_files = list(POSTS_DIR.glob("*.md"))
    print(f"Found {len(post_files)} post files")
    
    updated_count = 0
    for post_file in sorted(post_files):
        if process_post_file(post_file):
            print(f"✓ Updated: {post_file.name}")
            updated_count += 1
        else:
            print(f"- Skipped: {post_file.name}")
    
    print(f"\n✅ Processed {len(post_files)} files, updated {updated_count} files")

if __name__ == '__main__':
    main()

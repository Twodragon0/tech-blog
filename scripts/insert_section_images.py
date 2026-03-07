#!/usr/bin/env python3
"""Insert section banner images into digest posts for better UI/UX."""

import glob
import os
import re

POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_posts')

# Section header patterns and their corresponding banner images
# Pattern priority: specific numbered sections first, then keyword-based fallbacks
SECTION_BANNERS_NUMBERED = {
    r'^## \d+\.\s*보안\s*뉴스': 'security',
    r'^## \d+\.\s*AI/?ML\s*뉴스': 'ai-ml',
    r'^## \d+\.\s*클라우드': 'cloud',
    r'^## \d+\.\s*DevOps': 'devops',
    r'^## \d+\.\s*블록체인': 'blockchain',
}

# Keyword-based patterns for posts with different section structures
SECTION_BANNERS_KEYWORD = {
    r'^## (?:\d+\.\s*)?(?:위협\s*인텔리전스|보안|Security|CVE|Zero.?Day|취약점|공급망\s*보안|모바일.*보안|접근\s*제어)': 'security',
    r'^## (?:\d+\.\s*)?(?:AI/?ML\s*업데이트|AI\s*에이전트|LLM|인공지능)': 'ai-ml',
    r'^## (?:\d+\.\s*)?(?:클라우드.*인프라|클라우드|Cloud|AWS|GCP|Azure)': 'cloud',
    r'^## (?:\d+\.\s*)?(?:DevOps\s*뉴스|DevOps|CI/CD|컨테이너|플랫폼)': 'devops',
    r'^## (?:\d+\.\s*)?(?:블록체인\s*뉴스|블록체인|Blockchain|Bitcoin|DeFi|Web3)': 'blockchain',
}

BANNER_INFO = {
    'security': {
        'image': '/assets/images/section-security.svg',
        'alt': 'Security News Section Banner',
    },
    'ai-ml': {
        'image': '/assets/images/section-ai-ml.svg',
        'alt': 'AI ML News Section Banner',
    },
    'cloud': {
        'image': '/assets/images/section-cloud.svg',
        'alt': 'Cloud Infrastructure News Section Banner',
    },
    'devops': {
        'image': '/assets/images/section-devops.svg',
        'alt': 'DevOps Platform News Section Banner',
    },
    'blockchain': {
        'image': '/assets/images/section-blockchain.svg',
        'alt': 'Blockchain Web3 News Section Banner',
    },
}


def is_digest_post(filepath):
    """Check if a file is a weekly digest post."""
    basename = os.path.basename(filepath)
    return ('Weekly_Digest' in basename or 'Digest' in basename) and basename.endswith('.md')


def already_has_section_images(content):
    """Check if the post already has section banner images."""
    return 'section-security.svg' in content or 'section-ai-ml.svg' in content


def match_section(line):
    """Match a line against section banner patterns. Returns banner key or None."""
    # Skip non-h2 lines
    if not line.startswith('## '):
        return None
    # Skip common non-content sections
    skip_patterns = [
        r'^## 서론', r'^## 개요', r'^## 결론', r'^## 마무리',
        r'^## 참고', r'^## 실무\s*체크', r'^## 빠른\s*참조',
        r'^## 경영진', r'^## Executive', r'^## Checklist',
        r'^## 트렌드', r'^## 📊', r'^## 주요\s*하이라이트',
        r'^## 오늘의', r'^## 주요\s*이슈', r'^## 실무\s*액션',
        r'^## 영향\s*및', r'^## 원문', r'^## 기타\s*뉴스',
        r'^## 추가\s*뉴스',
    ]
    for sp in skip_patterns:
        if re.match(sp, line):
            return None

    # Try numbered patterns first
    for pattern, key in SECTION_BANNERS_NUMBERED.items():
        if re.match(pattern, line):
            return key
    # Then keyword patterns
    for pattern, key in SECTION_BANNERS_KEYWORD.items():
        if re.match(pattern, line, re.IGNORECASE):
            return key
    return None


def insert_banners(filepath):
    """Insert section banner images into a digest post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if already_has_section_images(content):
        return False

    lines = content.split('\n')
    new_lines = []
    inserted = 0
    used_banners = set()

    for line in lines:
        key = match_section(line)
        if key and key not in used_banners:
            banner = BANNER_INFO[key]
            new_lines.append(
                f'![{banner["alt"]}]({banner["image"]})'
            )
            new_lines.append('')
            new_lines.append(line)
            inserted += 1
            used_banners.add(key)
        else:
            new_lines.append(line)

    if inserted > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

    return inserted > 0


def main():
    """Process all digest posts."""
    posts = sorted(glob.glob(os.path.join(POSTS_DIR, '*.md')))
    digest_posts = [p for p in posts if is_digest_post(p)]

    print(f"Found {len(digest_posts)} digest posts")

    modified = 0
    for filepath in digest_posts:
        basename = os.path.basename(filepath)
        if insert_banners(filepath):
            modified += 1
            print(f"  [OK] {basename}")
        else:
            print(f"  [SKIP] {basename} (already has images or no sections found)")

    print(f"\nModified: {modified}/{len(digest_posts)} posts")


if __name__ == '__main__':
    main()

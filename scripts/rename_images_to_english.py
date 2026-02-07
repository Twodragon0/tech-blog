#!/usr/bin/env python3
"""
Rename image files with Korean characters to English
and update all references in post files.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import unicodedata

# Korean to English translation dictionary for common terms
KOREAN_TO_ENGLISH = {
    '클라우드': 'Cloud',
    '시큐리티': 'Security',
    '보안': 'Security',
    '과정': 'Course',
    '주차': 'Week',
    '기': 'Batch',
    '완벽': 'Complete',
    '가이드': 'Guide',
    '이메일': 'Email',
    '발송': 'Delivery',
    '신뢰도': 'Trust',
    '높이기': 'Improve',
    '설정': 'Setup',
    '공용': 'Public',
    'PC': 'PC',
    '안전하게': 'Safely',
    '패스키': 'Passkey',
    'OTP': 'OTP',
    '강력한': 'Strong',
    '암호': 'Password',
    '관리': 'Management',
    '활용법': 'Usage',
    '대응': 'Response',
    '이슈': 'Issue',
    '확인': 'Check',
    '교체': 'Replace',
    '중요성': 'Importance',
    '마스터': 'Master',
    '셋업': 'Setup',
    '규정': 'Regulation',
    '준수': 'Compliance',
    '올인원': 'All-in-One',
    '취약점': 'Vulnerability',
    '점검': 'Inspection',
    '인증': 'Certification',
    '대응': 'Response',
    '아키텍처': 'Architecture',
    '감사': 'Audit',
    '공략': 'Strategy',
    '거버넌스': 'Governance',
    '기반': 'Based',
    '통합': 'Integration',
    '인프라': 'Infrastructure',
    '본질': 'Essence',
    '미래': 'Future',
    '로드맵': 'Roadmap',
    '분석': 'Analysis',
    '장애': 'Incident',
    '해결기': 'Resolution',
    '데이터베이스': 'Database',
    '접근': 'Access',
    '게이트웨이': 'Gateway',
    '구축하기': 'Build',
    '노드': 'Node',
    '통합으로': 'Integration',
    '인한': 'Due to',
    '대규모': 'Large-scale',
    '회고': 'Review',
    '컨퍼런스': 'Conference',
    '미리': 'Preview',
    '보는': 'See',
    '공존': 'Coexistence',
    '블록체인': 'Blockchain',
    '암호화폐': 'Cryptocurrency',
    '관점에서': 'From Perspective',
    '본': 'View',
    '도구': 'Tools',
    '모범': 'Best',
    '사례': 'Practice',
    '자동차': 'Automotive',
    '바라보는': 'Viewing',
    '글로벌': 'Global',
    '대응': 'Response',
    '일지': 'Log',
    '무엇을': 'What',
    '배웠나': 'Learned',
    '안내': 'Guide',
    '실무형': 'Practical',
    '인재로': 'Talent',
    '도약하라': 'Leap',
    '핵심': 'Core',
    '정복': 'Conquer',
    '실전': 'Practical',
    '추가': 'Additional',
    '이미지': 'Image',
    '년': '',
    '월': '',
    '일': '',
    '년도': '',
    '에서도': 'Even in',
    '의': '',
    '와': 'and',
    '및': 'and',
    '부터': 'From',
    '까지': 'To',
    '로': 'with',
    '으로': 'with',
    '이': '',
    '가': '',
    '을': '',
    '를': '',
    '의': '',
    '에서': 'in',
    '로': '',
    '으로': '',
    '와': 'and',
    '과': 'and',
    '및': 'and',
    '그리고': 'and',
    '또는': 'or',
    '또한': 'also',
    '그러나': 'but',
    '하지만': 'but',
    '그래서': 'so',
    '따라서': 'therefore',
    '그런데': 'however',
    '그런': 'such',
    '이런': 'this',
    '저런': 'that',
    '어떤': 'what',
    '어떻게': 'how',
    '언제': 'when',
    '어디서': 'where',
    '누가': 'who',
    '무엇을': 'what',
    '왜': 'why',
    '어느': 'which',
    '몇': 'how many',
    '얼마나': 'how much',
    '어느': 'which',
    '어떤': 'what',
    '이런': 'this',
    '저런': 'that',
    '그런': 'such',
    '어떻게': 'how',
    '언제': 'when',
    '어디서': 'where',
    '누가': 'who',
    '무엇을': 'what',
    '왜': 'why',
    '어느': 'which',
    '몇': 'how many',
    '얼마나': 'how much',
    '어느': 'which',
    '어떤': 'what',
    '이런': 'this',
    '저런': 'that',
    '그런': 'such',
    '어떻게': 'how',
    '언제': 'when',
    '어디서': 'where',
    '누가': 'who',
    '무엇을': 'what',
    '왜': 'why',
    '어느': 'which',
    '몇': 'how many',
    '얼마나': 'how much',
}

def normalize_korean_text(text: str) -> str:
    """Normalize Korean text by removing special characters and normalizing."""
    # Remove special characters but keep underscores and hyphens
    text = re.sub(r'[^\w\s\-_]', '', text)
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    return text

def translate_korean_to_english(text: str) -> str:
    """Translate Korean text to English using dictionary and heuristics."""
    result = text
    
    # Try exact matches first (longest first)
    sorted_dict = sorted(KOREAN_TO_ENGLISH.items(), key=lambda x: len(x[0]), reverse=True)
    for korean, english in sorted_dict:
        if korean in result:
            result = result.replace(korean, english)
    
    # Remove remaining Korean characters
    result = re.sub(r'[가-힣]', '', result)
    
    # Clean up multiple spaces and underscores
    result = re.sub(r'[\s_]+', '_', result)
    result = re.sub(r'_+', '_', result)
    result = result.strip('_')
    
    return result

def get_post_image_mapping(blog_dir: Path) -> Dict[str, str]:
    """Get mapping from image filenames to post filenames for reference."""
    posts_dir = blog_dir / '_posts'
    mapping = {}
    
    if not posts_dir.exists():
        return mapping
    
    for post_file in posts_dir.glob('*.md'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract image path from frontmatter
            image_match = re.search(r'^image:\s*(.+)$', content, re.MULTILINE)
            if image_match:
                image_path = image_match.group(1).strip().strip('"\'')
                image_filename = Path(image_path).name
                
                # Extract date from post filename
                post_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', post_file.name)
                if post_match:
                    date, post_title = post_match.groups()
                    mapping[image_filename] = {
                        'date': date,
                        'post_title': post_title,
                        'post_file': post_file.name
                    }
        except Exception as e:
            print(f"  ⚠️  Error reading {post_file.name}: {e}")
    
    return mapping

def find_image_files_with_korean(images_dir: Path) -> List[Path]:
    """Find all image files with Korean characters in their names."""
    korean_files = []
    
    if not images_dir.exists():
        return korean_files
    
    for ext in ['*.svg', '*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif']:
        for img_file in images_dir.glob(ext):
            if re.search(r'[가-힣]', img_file.name):
                korean_files.append(img_file)
    
    return korean_files

def generate_english_filename(old_filename: str, post_mapping: Dict[str, dict]) -> str:
    """Generate English filename from Korean filename."""
    # Extract date and title
    match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+?)(_image)?\.(\w+)$', old_filename)
    if not match:
        return old_filename
    
    date, title_part, image_suffix, ext = match.groups()
    
    # Check if we have a matching post image reference
    if old_filename in post_mapping:
        post_info = post_mapping[old_filename]
        # Use post filename as base, but keep the image suffix if present
        post_title = post_info['post_title']
        # Remove Korean characters from post title
        english_title = translate_korean_to_english(post_title)
    else:
        # Translate Korean to English directly
        english_title = translate_korean_to_english(title_part)
    
    # Reconstruct filename
    if image_suffix:
        new_filename = f"{date}-{english_title}_image.{ext}"
    else:
        new_filename = f"{date}-{english_title}.{ext}"
    
    # Clean up the filename
    new_filename = re.sub(r'[^\w\.\-_]', '_', new_filename)
    new_filename = re.sub(r'_+', '_', new_filename)
    new_filename = new_filename.strip('_')
    
    return new_filename

def update_post_references(blog_dir: Path, old_path: str, new_path: str):
    """Update all references to image file in post files."""
    posts_dir = blog_dir / '_posts'
    old_filename = Path(old_path).name
    new_filename = Path(new_path).name
    
    if not posts_dir.exists():
        return
    
    updated_files = []
    
    for post_file in posts_dir.glob('*.md'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update image: field in frontmatter
            content = re.sub(
                rf'image:\s*(["\']?)/assets/images/{re.escape(old_filename)}(["\']?)',
                rf'image: \1/assets/images/{new_filename}\2',
                content
            )
            
            # Update img src tags
            content = re.sub(
                rf'<img[^>]+src=["\']{{[^}}]*[\'"]/assets/images/{re.escape(old_filename)}[\'"]',
                lambda m: m.group(0).replace(old_filename, new_filename),
                content
            )
            
            # Update markdown image links
            content = re.sub(
                rf'!\[([^\]]*)\]\(([^)]*)/assets/images/{re.escape(old_filename)}([^)]*)\)',
                lambda m: f"![{m.group(1)}]({m.group(2)}/assets/images/{new_filename}{m.group(3)})",
                content
            )
            
            # Update plain paths
            content = content.replace(f'/assets/images/{old_filename}', f'/assets/images/{new_filename}')
            content = content.replace(f'assets/images/{old_filename}', f'assets/images/{new_filename}')
            
            if content != original_content:
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(post_file.name)
        
        except Exception as e:
            print(f"  ⚠️  Error updating {post_file.name}: {e}")
    
    return updated_files

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rename image files with Korean to English')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    blog_dir = script_dir.parent
    images_dir = blog_dir / 'assets' / 'images'
    
    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}")
        sys.exit(1)
    
    print("=" * 80)
    print("Image Filename Translation: Korean to English")
    print("=" * 80)
    print()
    
    # Get post image mapping
    print("📋 Analyzing post files and image references...")
    post_mapping = get_post_image_mapping(blog_dir)
    print(f"   Found {len(post_mapping)} image references in post files")
    print()
    
    # Find all image files with Korean
    print("🔍 Finding image files with Korean characters...")
    korean_files = find_image_files_with_korean(images_dir)
    print(f"   Found {len(korean_files)} image files with Korean characters")
    print()
    
    if not korean_files:
        print("✅ No files to rename!")
        return
    
    # Generate rename mapping
    print("🔄 Generating English filenames...")
    rename_map = {}
    for img_file in korean_files:
        new_name = generate_english_filename(img_file.name, post_mapping)
        if new_name != img_file.name:
            rename_map[img_file] = new_name
            print(f"   {img_file.name}")
            print(f"   → {new_name}")
            print()
    
    if not rename_map:
        print("✅ No files need renaming!")
        return
    
    # Confirm before proceeding
    print(f"📝 Ready to rename {len(rename_map)} files")
    print("   This will also update all references in post files.")
    print()
    
    auto_yes = args.yes or os.environ.get("TECH_BLOG_AUTO_YES") or os.environ.get("CI")
    if not auto_yes:
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled.")
            return
    else:
        print("   Auto-confirmed (--yes / TECH_BLOG_AUTO_YES / CI)")
        print()
    
    # Perform renaming
    print()
    print("🔄 Renaming files and updating references...")
    print()
    
    renamed_count = 0
    updated_posts = set()
    
    for old_file, new_name in rename_map.items():
        try:
            new_file = old_file.parent / new_name
            
            # Check if target already exists
            if new_file.exists():
                print(f"  ⚠️  Target exists, skipping: {new_name}")
                continue
            
            # Rename file
            old_file.rename(new_file)
            print(f"  ✓ Renamed: {old_file.name} → {new_name}")
            
            # Update post references
            updated = update_post_references(blog_dir, str(old_file), str(new_file))
            if updated:
                updated_posts.update(updated)
                print(f"    Updated {len(updated)} post file(s)")
            
            renamed_count += 1
        
        except Exception as e:
            print(f"  ✗ Error renaming {old_file.name}: {e}")
    
    print()
    print("=" * 80)
    print(f"✅ Summary:")
    print(f"   - Renamed {renamed_count} image file(s)")
    print(f"   - Updated {len(updated_posts)} post file(s)")
    print("=" * 80)

if __name__ == '__main__':
    main()

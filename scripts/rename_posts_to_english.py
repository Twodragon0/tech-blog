#!/usr/bin/env python3
"""
Rename post files with Korean characters to English
and update all references in other post files and image files.
"""

import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import List

# Korean to English translation dictionary for common terms
KOREAN_TO_ENGLISH = {
    "클라우드": "Cloud",
    "시큐리티": "Security",
    "보안": "Security",
    "과정": "Course",
    "주차": "Week",
    "기": "Batch",
    "완벽": "Complete",
    "가이드": "Guide",
    "이메일": "Email",
    "발송": "Delivery",
    "신뢰도": "Trust",
    "높이기": "Improve",
    "설정": "Setup",
    "공용": "Public",
    "PC": "PC",
    "안전하게": "Safely",
    "패스키": "Passkey",
    "OTP": "OTP",
    "강력한": "Strong",
    "암호": "Password",
    "관리": "Management",
    "활용법": "Usage",
    "대응": "Response",
    "이슈": "Issue",
    "확인": "Check",
    "교체": "Replace",
    "중요성": "Importance",
    "마스터": "Master",
    "셋업": "Setup",
    "규정": "Regulation",
    "준수": "Compliance",
    "올인원": "All-in-One",
    "취약점": "Vulnerability",
    "점검": "Inspection",
    "인증": "Certification",
    "아키텍처": "Architecture",
    "감사": "Audit",
    "공략": "Strategy",
    "거버넌스": "Governance",
    "기반": "Based",
    "통합": "Integration",
    "인프라": "Infrastructure",
    "본질": "Essence",
    "미래": "Future",
    "로드맵": "Roadmap",
    "분석": "Analysis",
    "장애": "Incident",
    "해결기": "Resolution",
    "데이터베이스": "Database",
    "접근": "Access",
    "게이트웨이": "Gateway",
    "구축하기": "Build",
    "노드": "Node",
    "통합으로": "Integration",
    "인한": "Due_to",
    "대규모": "Large_scale",
    "회고": "Review",
    "컨퍼런스": "Conference",
    "미리": "Preview",
    "보는": "See",
    "공존": "Coexistence",
    "블록체인": "Blockchain",
    "암호화폐": "Cryptocurrency",
    "관점에서": "From_Perspective",
    "본": "View",
    "도구": "Tools",
    "모범": "Best",
    "사례": "Practice",
    "자동차": "Automotive",
    "바라보는": "Viewing",
    "글로벌": "Global",
    "일지": "Log",
    "무엇을": "What",
    "배웠나": "Learned",
    "안내": "Guide",
    "실무형": "Practical",
    "인재로": "Talent",
    "도약하라": "Leap",
    "핵심": "Core",
    "정복": "Conquer",
    "실전": "Practical",
    "실습": "Practice",
    "문제": "Problem",
    "해결부터": "From_Resolution",
    "테스트": "Test",
    "현재와": "Current_and",
    "에이전틱": "Agentic",
    "최신": "Latest",
    "업데이트": "Update",
    "환경에서": "In_Environment",
    "관리체계": "Management_System",
    "수립": "Establishment",
    "보호대책": "Protection_Measures",
    "구현": "Implementation",
    "자동화된": "Automated",
    "검증": "Verification",
    "컴플라이언스": "Compliance",
    "모니터링": "Monitoring",
    "부터": "From",
    "까지": "To",
    "및": "And",
    "와": "And",
    "그리고": "And",
    "년": "",
    "월": "",
    "일": "",
    "년도": "",
    "에서도": "Even_in",
    "의": "",
    "로": "",
    "으로": "",
    "이": "",
    "가": "",
    "을": "",
    "를": "",
    "에서": "In",
    "과": "And",
    "또는": "Or",
    "또한": "Also",
    "그러나": "But",
    "하지만": "But",
    "그래서": "So",
    "따라서": "Therefore",
    "그런데": "However",
    "그런": "Such",
    "이런": "This",
    "저런": "That",
    "어떤": "What",
    "어떻게": "How",
    "언제": "When",
    "어디서": "Where",
    "누가": "Who",
    "왜": "Why",
    "어느": "Which",
    "몇": "How_many",
    "얼마나": "How_much",
    "악성코드": "Malware",
    "감염": "Infection",
    "생태계": "Ecosystem",
    "다운로드": "Download",
    "패키지": "Package",
    "침해": "Breach",
    "자가": "Self",
    "복제": "Replication",
    "웜": "Worm",
    "공격": "Attack",
    "이상": "Above",
    "패키지": "Package",
    "공급망": "Supply_Chain",
    "완전": "Complete",
    "비서": "Secretary",
    "구멍": "Hole",
    "기업을": "For_Enterprise",
    "서비스": "Service",
    "SSL": "SSL",
    "검사": "Inspection",
    "샌드박스": "Sandbox",
    "광고": "Advertisement",
    "유해": "Harmful",
    "사이트": "Site",
    "차단": "Block",
    "OT": "OT",
    "인프라의": "Infrastructure",
    "아키텍처의": "Architecture",
    "VPC": "VPC",
    "GuardDuty": "GuardDuty",
    "FinOps": "FinOps",
    "ISMS-P": "ISMS-P",
    "Control": "Control",
    "Tower": "Tower",
    "SCP": "SCP",
    "SIEM": "SIEM",
    "WAF": "WAF",
    "CloudFront": "CloudFront",
    "DevSecOps": "DevSecOps",
    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
    "이해": "Understanding",
    "CICD": "CI/CD",
}


def normalize_korean_text(text: str) -> str:
    """Normalize Korean text by removing special characters and normalizing."""
    # Remove special characters but keep underscores and hyphens
    text = re.sub(r"[^\w\s\-_]", "", text)
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    return text


def translate_korean_to_english(text: str) -> str:
    """Translate Korean text to English using dictionary and heuristics."""
    result = text

    # Try exact matches first (longest first)
    sorted_dict = sorted(
        KOREAN_TO_ENGLISH.items(), key=lambda x: len(x[0]), reverse=True
    )
    for korean, english in sorted_dict:
        if korean in result:
            result = result.replace(korean, english)

    # Remove remaining Korean characters
    result = re.sub(r"[가-힣]", "", result)

    # Clean up multiple spaces and underscores
    result = re.sub(r"[\s_]+", "_", result)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_")

    return result


def find_post_files_with_korean(posts_dir: Path) -> List[Path]:
    """Find all post files with Korean characters in their names."""
    korean_files = []

    if not posts_dir.exists():
        return korean_files

    for post_file in posts_dir.glob("*.md"):
        if re.search(r"[가-힣]", post_file.name):
            korean_files.append(post_file)

    return korean_files


def generate_english_filename(old_filename: str) -> str:
    """Generate English filename from Korean filename."""
    # Extract date and title
    match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", old_filename)
    if not match:
        return old_filename

    date, title_part = match.groups()

    # Translate Korean to English
    english_title = translate_korean_to_english(title_part)

    # Reconstruct filename
    new_filename = f"{date}-{english_title}.md"

    # Clean up the filename
    new_filename = re.sub(r"[^\w\.\-_]", "_", new_filename)
    new_filename = re.sub(r"_+", "_", new_filename)
    new_filename = new_filename.strip("_")

    return new_filename


def update_post_references(blog_dir: Path, old_filename: str, new_filename: str):
    """Update all references to post file in other post files and image files."""
    posts_dir = blog_dir / "_posts"
    images_dir = blog_dir / "assets" / "images"

    updated_files = []

    # Update references in other post files
    if posts_dir.exists():
        for post_file in posts_dir.glob("*.md"):
            if post_file.name == old_filename:
                continue

            try:
                with open(post_file, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Update Jekyll post links: /posts/파일명 or /_posts/파일명
                content = re.sub(
                    rf"/posts/{re.escape(old_filename)}",
                    f"/posts/{new_filename}",
                    content,
                )
                content = re.sub(
                    rf"/_posts/{re.escape(old_filename)}",
                    f"/_posts/{new_filename}",
                    content,
                )

                # Update relative links: [text](파일명)
                content = re.sub(
                    rf"\[([^\]]+)\]\(([^)]*){re.escape(old_filename)}([^)]*)\)",
                    lambda m: f"[{m.group(1)}]({m.group(2)}{new_filename}{m.group(3)})",
                    content,
                )

                # Update plain filename references
                content = content.replace(old_filename, new_filename)

                if content != original_content:
                    with open(post_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_files.append(post_file.name)

            except Exception as e:
                print(f"  ⚠️  Error updating {post_file.name}: {e}")

    # Update image filenames that reference the post filename
    if images_dir.exists():
        old_base = old_filename.replace(".md", "")
        new_base = new_filename.replace(".md", "")

        for ext in ["*.svg", "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"]:
            for img_file in images_dir.glob(ext):
                if old_base in img_file.name:
                    try:
                        new_img_name = img_file.name.replace(old_base, new_base)
                        new_img_path = img_file.parent / new_img_name

                        if not new_img_path.exists():
                            img_file.rename(new_img_path)
                            print(
                                f"    Renamed image: {img_file.name} → {new_img_name}"
                            )

                            # Update image references in post files
                            update_image_references(
                                blog_dir, img_file.name, new_img_name
                            )

                    except Exception as e:
                        print(f"  ⚠️  Error renaming image {img_file.name}: {e}")

    return updated_files


def update_image_references(blog_dir: Path, old_img_name: str, new_img_name: str):
    """Update image references in post files."""
    posts_dir = blog_dir / "_posts"

    if not posts_dir.exists():
        return

    for post_file in posts_dir.glob("*.md"):
        try:
            with open(post_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Update image: field in frontmatter
            content = re.sub(
                rf'image:\s*(["\']?)/assets/images/{re.escape(old_img_name)}(["\']?)',
                rf"image: \1/assets/images/{new_img_name}\2",
                content,
            )

            # Update img src tags
            content = re.sub(
                rf'<img[^>]+src=["\']{{[^}}]*[\'"]/assets/images/{re.escape(old_img_name)}[\'"]',
                lambda m: m.group(0).replace(old_img_name, new_img_name),
                content,
            )

            # Update markdown image links
            content = re.sub(
                rf"!\[([^\]]*)\]\(([^)]*)/assets/images/{re.escape(old_img_name)}([^)]*)\)",
                lambda m: (
                    f"![{m.group(1)}]({m.group(2)}/assets/images/{new_img_name}{m.group(3)})"
                ),
                content,
            )

            # Update plain paths
            content = content.replace(
                f"/assets/images/{old_img_name}", f"/assets/images/{new_img_name}"
            )
            content = content.replace(
                f"assets/images/{old_img_name}", f"assets/images/{new_img_name}"
            )

            if content != original_content:
                with open(post_file, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"  ⚠️  Error updating image references in {post_file.name}: {e}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Rename post files with Korean to English"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    blog_dir = script_dir.parent
    posts_dir = blog_dir / "_posts"

    if not posts_dir.exists():
        print(f"Error: Posts directory not found: {posts_dir}")
        sys.exit(1)

    print("=" * 80)
    print("Post Filename Translation: Korean to English")
    print("=" * 80)
    print()

    # Find all post files with Korean
    print("🔍 Finding post files with Korean characters...")
    korean_files = find_post_files_with_korean(posts_dir)
    print(f"   Found {len(korean_files)} post files with Korean characters")
    print()

    if not korean_files:
        print("✅ No files to rename!")
        return

    # Generate rename mapping
    print("🔄 Generating English filenames...")
    rename_map = {}
    for post_file in korean_files:
        new_name = generate_english_filename(post_file.name)
        if new_name != post_file.name:
            rename_map[post_file] = new_name
            print(f"   {post_file.name}")
            print(f"   → {new_name}")
            print()

    if not rename_map:
        print("✅ No files need renaming!")
        return

    # Confirm before proceeding
    print(f"📝 Ready to rename {len(rename_map)} files")
    print("   This will also:")
    print("   - Update all references in other post files")
    print("   - Rename related image files")
    print("   - Update image references in post files")
    print()

    auto_yes = args.yes or os.environ.get("TECH_BLOG_AUTO_YES") or os.environ.get("CI")
    if not auto_yes:
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
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

            # Update references in other files
            updated = update_post_references(blog_dir, old_file.name, new_name)
            if updated:
                updated_posts.update(updated)
                print(f"    Updated {len(updated)} file(s)")

            renamed_count += 1

        except Exception as e:
            print(f"  ✗ Error renaming {old_file.name}: {e}")

    print()
    print("=" * 80)
    print("✅ Summary:")
    print(f"   - Renamed {renamed_count} post file(s)")
    print(f"   - Updated {len(updated_posts)} file(s)")
    print("=" * 80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Verify that all post file references and image links are correct after renaming.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lib.image_utils import check_image_exists, extract_image_paths, has_korean


def check_image_references(blog_dir: Path) -> List[Dict]:
    """Check if all image references in posts point to existing files."""
    posts_dir = blog_dir / "_posts"
    project_root = blog_dir
    images_dir = blog_dir / "assets" / "images"

    issues = []

    for post_file in sorted(posts_dir.glob("*.md")):
        try:
            content = post_file.read_text(encoding="utf-8")

            for rel in extract_image_paths(content):
                exists, _ = check_image_exists(
                    rel, project_root=project_root, images_dir=images_dir
                )
                if not exists:
                    issues.append(
                        {
                            "type": "image_not_found",
                            "post": post_file.name,
                            "image": rel,
                            "severity": "error",
                        }
                    )

        except Exception as e:
            issues.append(
                {
                    "type": "read_error",
                    "post": post_file.name,
                    "error": str(e),
                    "severity": "error",
                }
            )

    return issues


def check_post_urls(blog_dir: Path) -> List[Dict]:
    """Check if post URLs are properly formatted."""
    posts_dir = blog_dir / "_posts"
    issues = []

    for post_file in sorted(posts_dir.glob("*.md")):
        # Check filename format: YYYY-MM-DD-Title.md
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", post_file.name)
        if not match:
            issues.append(
                {
                    "type": "invalid_filename",
                    "post": post_file.name,
                    "severity": "error",
                }
            )
            continue

        year, month, day, title = match.groups()

        # Check for Korean characters in filename
        if has_korean(post_file.name):
            issues.append(
                {
                    "type": "korean_in_filename",
                    "post": post_file.name,
                    "severity": "warning",
                }
            )

        # Check for special characters that might cause URL issues
        if re.search(r"[^\w\-_.]", title):
            issues.append(
                {
                    "type": "special_chars_in_filename",
                    "post": post_file.name,
                    "severity": "warning",
                }
            )

    return issues


def check_cross_references(blog_dir: Path) -> List[Dict]:
    """Check for cross-references between posts."""
    posts_dir = blog_dir / "_posts"
    issues = []

    # Build post filename mapping
    post_files = {f.stem: f.name for f in posts_dir.glob("*.md")}

    for post_file in sorted(posts_dir.glob("*.md")):
        try:
            with open(post_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for markdown links to other posts
            # Pattern: [text](YYYY-MM-DD-title.md) or [text](/posts/...)
            md_link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            for match in re.finditer(md_link_pattern, content):
                link_path = match.group(2)

                # Check if it's a post file reference
                if link_path.endswith(".md"):
                    link_filename = Path(link_path).name
                    if link_filename not in post_files.values():
                        issues.append(
                            {
                                "type": "broken_post_link",
                                "post": post_file.name,
                                "link": link_filename,
                                "severity": "error",
                            }
                        )

        except Exception as e:
            issues.append(
                {
                    "type": "read_error",
                    "post": post_file.name,
                    "error": str(e),
                    "severity": "error",
                }
            )

    return issues


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    blog_dir = script_dir.parent

    print("=" * 80)
    print("Post Link Verification")
    print("=" * 80)
    print()

    all_issues = []

    # Check image references
    print("🔍 Checking image references...")
    image_issues = check_image_references(blog_dir)
    all_issues.extend(image_issues)
    if image_issues:
        print(f"   Found {len(image_issues)} image reference issue(s)")
        for issue in image_issues[:5]:
            print(f"   - {issue['post']}: {issue.get('image', 'N/A')}")
    else:
        print("   ✅ All image references are valid")
    print()

    # Check post URLs
    print("🔍 Checking post filenames...")
    url_issues = check_post_urls(blog_dir)
    all_issues.extend(url_issues)
    if url_issues:
        print(f"   Found {len(url_issues)} filename issue(s)")
        for issue in url_issues[:5]:
            print(f"   - {issue['post']}: {issue['type']}")
    else:
        print("   ✅ All post filenames are valid")
    print()

    # Check cross-references
    print("🔍 Checking cross-references...")
    crossref_issues = check_cross_references(blog_dir)
    all_issues.extend(crossref_issues)
    if crossref_issues:
        print(f"   Found {len(crossref_issues)} cross-reference issue(s)")
        for issue in crossref_issues[:5]:
            print(f"   - {issue['post']}: {issue.get('link', 'N/A')}")
    else:
        print("   ✅ All cross-references are valid")
    print()

    # Summary
    print("=" * 80)
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]

    print("Summary:")
    print(f"   - Errors: {len(errors)}")
    print(f"   - Warnings: {len(warnings)}")
    print("=" * 80)

    if errors:
        print("\n⚠️  Errors found - these need to be fixed:")
        for error in errors[:10]:
            print(f"   - {error['post']}: {error.get('type', 'unknown')}")

    if warnings:
        print("\nℹ️  Warnings (may be acceptable):")
        for warning in warnings[:10]:
            print(f"   - {warning['post']}: {warning.get('type', 'unknown')}")


if __name__ == "__main__":
    main()

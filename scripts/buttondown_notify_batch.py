#!/usr/bin/env python3
"""
Buttondown Batch Email Notification Script
Processes multiple blog posts and sends email notifications for each.
Can work with POSTS_JSON environment variable or detect posts via git diff.
Note: Only new posts trigger email notifications. Updated posts are excluded.
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

# .env 파일에서 환경 변수 로드
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Validate key is a valid identifier before setting
                if key.isidentifier():
                    os.environ[key] = value


def detect_posts_via_git_diff():
    """Detect only new posts via git diff (excludes modified posts)."""
    posts = []

    try:
        # Get only added posts (new posts)
        # Modified posts are excluded to prevent email notifications for updates
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=A",
                "HEAD~1",
                "HEAD",
                "--",
                "_posts/*.md",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            posts.extend(result.stdout.strip().split("\n"))

        # Remove duplicates and empty strings
        posts = list(set([p.strip() for p in posts if p.strip()]))

        if posts:
            print(f"📝 Detected {len(posts)} new post(s) (modified posts excluded)")

    except subprocess.TimeoutExpired:
        print("⚠️ Git diff command timed out")
    except Exception as e:
        print(f"⚠️ Error detecting posts via git diff: {e}")

    return posts


def main():
    """Process multiple posts from JSON array or git diff."""
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    # Debug logging
    print("🔍 Debug: Environment variables")
    print(f"   BUTTONDOWN_API_KEY: {'set' if api_key else 'not set'}")
    print(f"   SITE_URL: {site_url}")
    print("")

    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        sys.exit(1)

    # Try to get posts from POSTS_JSON first, then fall back to git diff
    posts_json = os.environ.get("POSTS_JSON", "[]")
    posts = []

    if posts_json and posts_json != "[]":
        print("📋 Using POSTS_JSON from environment variable")
        try:
            posts_encoded = json.loads(posts_json)
            for post_encoded in posts_encoded:
                if post_encoded:
                    try:
                        post_file = base64.b64decode(post_encoded).decode("utf-8")
                        posts.append(post_file)
                    except Exception as e:
                        print(f"⚠️ Failed to decode post file path: {e}")
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse POSTS_JSON: {e}")
            print("   Falling back to git diff detection")

    # If no posts from POSTS_JSON, detect via git diff
    if not posts:
        print("📋 Detecting posts via git diff...")
        posts = detect_posts_via_git_diff()

    # Filter out draft posts and validate
    valid_posts = []
    for post_file in posts:
        post_path = Path(post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_file

        if not post_path.exists():
            print(f"⚠️ Post file not found: {post_path}")
            continue

        # Check if draft (quick check without full parsing)
        try:
            with open(post_path, "r", encoding="utf-8") as f:
                content = f.read(1000)  # Read first 1000 chars
                if "draft: true" in content or "draft: True" in content:
                    print(f"⏭️ Skipping draft post: {post_file}")
                    continue
        except Exception as e:
            print(f"⚠️ Error checking draft status for {post_file}: {e}")

        valid_posts.append(str(post_path))

    if not valid_posts:
        print("❌ No valid post files found")
        print("   This might happen if:")
        print("   1. No new posts were detected (updated posts are excluded)")
        print("   2. All posts are marked as draft")
        print("   3. The post files don't exist")
        sys.exit(1)

    print(f"📧 Processing {len(valid_posts)} post(s)...")
    print("")

    success_count = 0
    fail_count = 0

    # Import the notification script function
    notify_script = PROJECT_ROOT / "scripts" / "buttondown_notify.py"

    for post_path in valid_posts:
        print(f"📄 Processing: {Path(post_path).name}")

        # 이메일 발송
        result = subprocess.run(
            [sys.executable, str(notify_script), post_path],
            env={**os.environ, "BUTTONDOWN_API_KEY": api_key, "SITE_URL": site_url},
            capture_output=True,
            text=True,
        )

        # 출력 표시
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"✅ Email sent successfully for: {Path(post_path).name}")
            success_count += 1
        else:
            print(f"❌ Failed to send email for: {Path(post_path).name}")
            fail_count += 1

        print("")

    # 결과 요약
    print("=" * 42)
    print("📊 Email Notification Summary")
    print("=" * 42)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📝 Total: {len(valid_posts)}")
    print("=" * 42)

    # 하나라도 성공하면 성공으로 처리
    if success_count > 0:
        print("✅ At least one email was sent successfully")
        sys.exit(0)
    else:
        print("❌ All email notifications failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

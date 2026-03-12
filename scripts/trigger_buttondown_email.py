#!/usr/bin/env python3
"""
Trigger ButtonDown Email for Existing Post
Simulates a new post by temporarily removing and re-adding the post file
to trigger GitHub Actions email notification.
"""

import os
import sys
from pathlib import Path

# .env 파일에서 환경 변수 로드
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Import functions from buttondown_notify.py
sys.path.insert(0, str(SCRIPT_DIR))
from buttondown_notify import (
    create_email_content,
    generate_post_url,
    get_post_content,
    parse_frontmatter,
    send_buttondown_email,
)


def trigger_email_for_post(post_path: str, dry_run: bool = False, yes: bool = False):
    """Trigger email for an existing post by sending it directly."""
    post_file = Path(post_path)

    if not post_file.exists():
        print(f"❌ Post file not found: {post_path}")
        sys.exit(1)

    if not post_file.is_absolute():
        post_file = PROJECT_ROOT / post_path

    # Get API key
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        print("")
        print("💡 To send email directly, you need to:")
        print(
            "   1. Get your ButtonDown API key from: https://buttondown.com/settings/api"
        )
        print("   2. Set it as an environment variable:")
        print("      export BUTTONDOWN_API_KEY='your-api-key'")
        print("")
        print("   Or add it to .env file:")
        print("      BUTTONDOWN_API_KEY=your-api-key")
        print("")
        print("⚠️  Alternatively, you can trigger GitHub Actions by:")
        print("   1. Temporarily removing the post file")
        print("   2. Committing the deletion")
        print("   3. Re-adding the post file")
        print("   4. Committing the addition")
        print("   5. Pushing to trigger GitHub Actions")
        sys.exit(1)

    # Get site URL
    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    print("=" * 70)
    print("📧 Trigger ButtonDown Email for Existing Post")
    print("=" * 70)
    print(f"📄 Post: {post_file.name}")
    print(
        f"🔧 Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will send email)'}"
    )
    print("")

    # Parse post metadata
    frontmatter = parse_frontmatter(str(post_file))
    if not frontmatter:
        print("⚠️ No frontmatter found in post")
        frontmatter = {"title": post_file.stem}

    # Check if draft
    if frontmatter.get("draft", False):
        print("⏭️ Skipping draft post")
        sys.exit(0)

    # Generate post URL
    post_url = generate_post_url(str(post_file), site_url)

    # Get post content
    post_content = get_post_content(str(post_file))
    filename = post_file.name

    # Create email content
    subject, body = create_email_content(frontmatter, post_url, post_content, filename)

    # Display preview
    print("=" * 70)
    print("📌 SUBJECT")
    print("=" * 70)
    print(subject)
    print("")

    print("=" * 70)
    print("📝 BODY (first 500 chars)")
    print("=" * 70)
    print(body[:500] + "..." if len(body) > 500 else body)
    print("")

    if dry_run:
        print("=" * 70)
        print("✅ DRY RUN: Email preview generated (not sent)")
        print("=" * 70)
        print("💡 To actually send the email, run without --dry-run flag")
        return True

    # Confirm before sending (skip if --yes or TECH_BLOG_AUTO_YES/CI)
    auto_yes = yes or os.environ.get("TECH_BLOG_AUTO_YES") or os.environ.get("CI")
    if not auto_yes:
        print("=" * 70)
        print("⚠️  WARNING: This will send an email to ALL subscribers!")
        print("=" * 70)
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("❌ Cancelled by user")
            return False
    else:
        print("   Auto-confirmed (--yes / TECH_BLOG_AUTO_YES / CI)")

    # Send email
    print("")
    print("📤 Sending email...")
    success = send_buttondown_email(subject, body, api_key)

    if success:
        print("")
        print("=" * 70)
        print("✅ Email sent successfully!")
        print("=" * 70)
        print("📧 Check your ButtonDown dashboard:")
        print("   https://buttondown.com/emails")
        return True
    else:
        print("")
        print("=" * 70)
        print("❌ Failed to send email")
        print("=" * 70)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Trigger ButtonDown email for an existing post",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview email (dry run)
  python trigger_buttondown_email.py _posts/2026-01-15-Example.md --dry-run

  # Actually send email (requires BUTTONDOWN_API_KEY)
  python trigger_buttondown_email.py _posts/2026-01-15-Example.md
        """,
    )
    parser.add_argument("post_path", help="Path to the blog post file")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview email without sending"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt (auto-yes for project/tmp)",
    )

    args = parser.parse_args()

    success = trigger_email_for_post(args.post_path, dry_run=args.dry_run, yes=args.yes)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

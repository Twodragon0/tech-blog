#!/usr/bin/env python3
"""
Test ButtonDown Email Sending
Sends a test email to verify the email template and API integration.
"""

import os
import sys
from pathlib import Path

# .env 파일에서 환경 변수 로드
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / '.env'

if ENV_FILE.exists():
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Import functions from buttondown_notify.py
sys.path.insert(0, str(SCRIPT_DIR))
from buttondown_notify import (
    parse_frontmatter,
    get_post_content,
    generate_post_url,
    create_email_content,
    send_buttondown_email
)


def test_email_send(post_path: str, dry_run: bool = False, yes: bool = False):
    """Test sending email for a post."""
    post_file = Path(post_path)
    
    if not post_file.exists():
        print(f"❌ Post file not found: {post_path}")
        sys.exit(1)
    
    if not post_file.is_absolute():
        post_file = PROJECT_ROOT / post_path
    
    # Get API key
    api_key = os.environ.get('BUTTONDOWN_API_KEY')
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        print("   Please set it in .env file or export it:")
        print("   export BUTTONDOWN_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Get site URL
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')
    
    print("=" * 70)
    print("🧪 ButtonDown Email Send Test")
    print("=" * 70)
    print(f"📄 Post: {post_file.name}")
    print(f"🔧 Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will send email)'}")
    print("")
    
    # Parse post metadata
    frontmatter = parse_frontmatter(str(post_file))
    if not frontmatter:
        print("⚠️ No frontmatter found in post")
        frontmatter = {'title': post_file.stem}
    
    # Check if draft
    if frontmatter.get('draft', False):
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
        print("⚠️  WARNING: This will send an email to all subscribers!")
        print("=" * 70)
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
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
        description='Test ButtonDown email sending',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview email (dry run)
  python test_buttondown_email_send.py _posts/2026-01-15-Example.md --dry-run
  
  # Actually send email
  python test_buttondown_email_send.py _posts/2026-01-15-Example.md
        """
    )
    parser.add_argument('post_path', help='Path to the blog post file')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview email without sending')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt (auto-yes for project/tmp)')
    
    args = parser.parse_args()
    
    success = test_email_send(args.post_path, dry_run=args.dry_run, yes=args.yes)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

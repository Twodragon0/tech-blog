#!/usr/bin/env python3
"""
Buttondown Batch Email Notification Script
Processes multiple blog posts and sends email notifications for each.
"""

import os
import sys
import json
import base64
import subprocess
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


def main():
    """Process multiple posts from JSON array."""
    # Get posts from environment variable (JSON array of base64-encoded paths)
    posts_json = os.environ.get('POSTS_JSON', '[]')
    api_key = os.environ.get('BUTTONDOWN_API_KEY')
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')
    
    # Debug logging
    print("🔍 Debug: Environment variables")
    print(f"   POSTS_JSON length: {len(posts_json)}")
    print(f"   POSTS_JSON (first 200 chars): {posts_json[:200]}...")
    print(f"   BUTTONDOWN_API_KEY: {'set' if api_key else 'not set'}")
    print(f"   SITE_URL: {site_url}")
    print("")
    
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        sys.exit(1)
    
    if not posts_json or posts_json == '[]':
        print("❌ No post files specified")
        print(f"   POSTS_JSON value: {posts_json}")
        print("   This might happen if:")
        print("   1. No new posts were added (only existing posts were modified)")
        print("   2. The workflow didn't detect any changes")
        print("   3. The POSTS_JSON environment variable wasn't set correctly")
        sys.exit(1)
    
    try:
        posts_encoded = json.loads(posts_json)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse posts JSON: {e}")
        sys.exit(1)
    
    if not posts_encoded:
        print("❌ No post files in JSON array")
        sys.exit(1)
    
    print(f"📧 Processing {len(posts_encoded)} new post(s)...")
    print("")
    
    success_count = 0
    fail_count = 0
    
    # Import the notification script function
    notify_script = PROJECT_ROOT / 'scripts' / 'buttondown_notify.py'
    
    for post_encoded in posts_encoded:
        if not post_encoded:
            continue
        
        # Base64 디코딩
        try:
            post_file = base64.b64decode(post_encoded).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Failed to decode post file path: {e}")
            fail_count += 1
            continue
        
        print(f"📄 Processing: {post_file}")
        
        # 파일 존재 확인
        post_path = Path(post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_file
        
        if not post_path.exists():
            print(f"⚠️ Post file not found: {post_path}")
            fail_count += 1
            continue
        
        # 이메일 발송
        result = subprocess.run(
            [sys.executable, str(notify_script), str(post_path)],
            env={**os.environ, 'BUTTONDOWN_API_KEY': api_key, 'SITE_URL': site_url},
            capture_output=True,
            text=True
        )
        
        # 출력 표시
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print(f"✅ Email sent successfully for: {post_file}")
            success_count += 1
        else:
            print(f"❌ Failed to send email for: {post_file}")
            fail_count += 1
        
        print("")
    
    # 결과 요약
    print("=" * 42)
    print("📊 Email Notification Summary")
    print("=" * 42)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📝 Total: {len(posts_encoded)}")
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

#!/usr/bin/env python3
"""
SNS Auto Share Script
Automatically shares new blog posts to Twitter/X, Facebook, and LinkedIn.
"""

import os
import sys
import re
import yaml
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# Optional imports - will be skipped if not configured
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def parse_frontmatter(file_path: str) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}


def generate_post_url(file_path: str, site_url: str) -> str:
    """Generate the URL for a blog post based on permalink structure."""
    filename = Path(file_path).stem

    # Parse date and title from filename (YYYY-MM-DD-title format)
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', filename)
    if not match:
        return f"{site_url}/posts/{filename}/"

    year, month, day, title = match.groups()
    # URL encode the title for Korean characters
    encoded_title = quote(title, safe='')

    return f"{site_url}/posts/{year}/{month}/{title}/"


def create_share_message(frontmatter: dict, post_url: str, platform: str) -> str:
    """Create a platform-specific share message."""
    title = frontmatter.get('title', 'New Post')
    excerpt = frontmatter.get('excerpt', frontmatter.get('description', ''))
    tags = frontmatter.get('tags', [])
    category = frontmatter.get('categories', frontmatter.get('category', ''))

    # Create hashtags from tags
    hashtags = ' '.join([f'#{tag.replace("-", "").replace(" ", "")}' for tag in tags[:5]])

    if platform == 'twitter':
        # Twitter has 280 character limit
        message = f"📝 {title}\n\n{post_url}\n\n{hashtags}"
        if len(message) > 280:
            message = f"📝 {title[:100]}...\n\n{post_url}"
        return message

    elif platform == 'facebook':
        message = f"""🚀 새 글이 올라왔습니다!

📝 {title}

{excerpt[:200] if excerpt else ''}

👉 자세히 보기: {post_url}

{hashtags}

#DevSecOps #CloudSecurity #TechBlog"""
        return message

    elif platform == 'linkedin':
        message = f"""🚀 새로운 기술 블로그 포스트를 공유합니다!

📝 {title}

{excerpt[:300] if excerpt else ''}

이 글에서는 실무에서 바로 적용할 수 있는 내용을 다룹니다.

👉 전체 글 읽기: {post_url}

{hashtags}

#DevSecOps #CloudSecurity #AWS #Kubernetes #TechBlog"""
        return message

    return f"{title}\n\n{post_url}"


def share_to_twitter(message: str) -> bool:
    """Share to Twitter/X using API v2."""
    if not TWITTER_AVAILABLE:
        print("Twitter: tweepy not installed, skipping")
        return False

    api_key = os.environ.get('TWITTER_API_KEY')
    api_secret = os.environ.get('TWITTER_API_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

    if not all([api_key, api_secret, access_token, access_secret]):
        print("Twitter: API credentials not configured, skipping")
        return False

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        response = client.create_tweet(text=message)
        print(f"Twitter: Successfully posted! Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Twitter: Error posting - {e}")
        return False


def share_to_facebook(message: str) -> bool:
    """Share to Facebook Page using Graph API."""
    if not REQUESTS_AVAILABLE:
        print("Facebook: requests not installed, skipping")
        return False

    page_id = os.environ.get('FACEBOOK_PAGE_ID')
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')

    if not all([page_id, access_token]):
        print("Facebook: API credentials not configured, skipping")
        return False

    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        payload = {
            'message': message,
            'access_token': access_token
        }

        response = requests.post(url, data=payload)
        result = response.json()

        if 'id' in result:
            print(f"Facebook: Successfully posted! Post ID: {result['id']}")
            return True
        else:
            print(f"Facebook: Error - {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Facebook: Error posting - {e}")
        return False


def share_to_linkedin(message: str) -> bool:
    """Share to LinkedIn using API."""
    if not REQUESTS_AVAILABLE:
        print("LinkedIn: requests not installed, skipping")
        return False

    access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')
    person_id = os.environ.get('LINKEDIN_PERSON_ID')

    if not all([access_token, person_id]):
        print("LinkedIn: API credentials not configured, skipping")
        return False

    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        payload = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            print(f"LinkedIn: Successfully posted!")
            return True
        else:
            print(f"LinkedIn: Error - {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"LinkedIn: Error posting - {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python share_sns.py <post_file_path>")
        sys.exit(1)

    post_path_arg = sys.argv[1]
    
    # Handle file path issues: decode if needed, resolve relative paths
    script_dir = Path(__file__).parent.parent
    posts_dir = script_dir / '_posts'
    
    # First, try to use the path as-is
    if os.path.isabs(post_path_arg):
        post_path = Path(post_path_arg)
    else:
        # Try relative to script directory first
        post_path = script_dir / post_path_arg
        if not post_path.exists():
            # Try relative to current working directory
            post_path = Path(post_path_arg).resolve()
    
    # If file doesn't exist, try to find it by date pattern or partial name
    if not post_path.exists() and posts_dir.exists():
        filename_arg = Path(post_path_arg).name
        
        # Extract date pattern (YYYY-MM-DD) if present
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename_arg)
        if date_match:
            date_str = date_match.group(1)
            # Find all files starting with that date
            matching_files = list(posts_dir.glob(f'{date_str}-*.md'))
            if len(matching_files) == 1:
                post_path = matching_files[0]
                print(f"Found file by date pattern: {post_path.name}")
            elif len(matching_files) > 1:
                # If multiple files, try to match by partial name
                # Remove non-ASCII characters and try to match
                filename_clean = re.sub(r'[^\w\-]', '', filename_arg.lower())
                for file in matching_files:
                    file_clean = re.sub(r'[^\w\-]', '', file.stem.lower())
                    if filename_clean in file_clean or file_clean in filename_clean:
                        post_path = file
                        print(f"Found file by partial match: {post_path.name}")
                        break
                else:
                    # Use the most recent file if no match
                    post_path = max(matching_files, key=lambda p: p.stat().st_mtime)
                    print(f"Multiple files found, using most recent: {post_path.name}")
        else:
            # No date pattern, try to find by partial name match
            filename_clean = re.sub(r'[^\w\-]', '', filename_arg.lower())
            for file in posts_dir.glob('*.md'):
                file_clean = re.sub(r'[^\w\-]', '', file.stem.lower())
                if filename_clean in file_clean or file_clean in filename_clean:
                    post_path = file
                    print(f"Found file by name match: {post_path.name}")
                    break
    
    # Convert to absolute path string
    post_path = str(post_path.resolve())
    
    if not os.path.exists(post_path):
        print(f"Error: File not found: {post_path}")
        print(f"Searched in: {posts_dir}")
        sys.exit(1)
    
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')

    print(f"Processing: {post_path}")

    # Parse frontmatter
    frontmatter = parse_frontmatter(post_path)
    if not frontmatter:
        print("Error: Could not parse frontmatter")
        sys.exit(1)

    print(f"Title: {frontmatter.get('title', 'Unknown')}")

    # Generate post URL
    post_url = generate_post_url(post_path, site_url)
    print(f"URL: {post_url}")

    # Share to each platform
    results = {}

    # Twitter/X
    twitter_msg = create_share_message(frontmatter, post_url, 'twitter')
    results['twitter'] = share_to_twitter(twitter_msg)

    # Facebook
    facebook_msg = create_share_message(frontmatter, post_url, 'facebook')
    results['facebook'] = share_to_facebook(facebook_msg)

    # LinkedIn
    linkedin_msg = create_share_message(frontmatter, post_url, 'linkedin')
    results['linkedin'] = share_to_linkedin(linkedin_msg)

    # Summary
    print("\n--- Summary ---")
    for platform, success in results.items():
        status = "✅ Success" if success else "⏭️ Skipped/Failed"
        print(f"{platform.capitalize()}: {status}")

    # Exit with success even if some platforms failed
    # (we don't want to fail the entire workflow)
    sys.exit(0)


if __name__ == '__main__':
    main()

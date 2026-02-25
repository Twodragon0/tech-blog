#!/usr/bin/env python3
"""
SNS Auto Share Script
Automatically shares new blog posts to Twitter/X, Facebook, and LinkedIn.
"""

import os
import sys
import re
import yaml
import importlib
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Any, cast

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

# Optional imports - will be skipped if not configured
try:
    tweepy = importlib.import_module("tweepy")
except ImportError:
    tweepy = None

try:
    requests = importlib.import_module("requests")
except ImportError:
    requests = None

TWITTER_AVAILABLE = tweepy is not None
REQUESTS_AVAILABLE = requests is not None


def parse_frontmatter(file_path: str) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
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
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)", filename)
    if not match:
        return f"{site_url}/posts/{filename}/"

    year, month, day, title = match.groups()
    # URL encode the title for Korean characters
    encoded_title = quote(title, safe="")

    return f"{site_url}/posts/{year}/{month}/{title}/"


def create_share_message(frontmatter: dict, post_url: str, platform: str) -> str:
    """Create a platform-specific share message."""
    title = frontmatter.get("title", "New Post")
    excerpt = frontmatter.get("excerpt", frontmatter.get("description", ""))
    tags = frontmatter.get("tags", [])
    category = frontmatter.get("categories", frontmatter.get("category", ""))

    summary = _build_summary(excerpt, max_length=220)
    hashtags = _build_hashtags(tags, max_count=5)

    investing_url = os.environ.get("INVESTING_SITE_URL", "https://investing.2twodragon.com")

    if platform == "twitter":
        return _build_twitter_message(title, summary, post_url, hashtags)

    elif platform == "facebook":
        message = f"""🚀 새 글이 올라왔습니다!

📝 {title}

{summary}

{hashtags}

#DevSecOps #CloudSecurity #TechBlog

📊 투자 블로그: {investing_url}"""
        return message

    elif platform == "linkedin":
        # LinkedIn은 메시지에 링크가 포함되면 자동으로 Open Graph를 크롤링하여 이미지 표시
        message = f"""🚀 새로운 기술 블로그 포스트를 공유합니다!

📝 {title}

{summary}

이 글에서는 실무에서 바로 적용할 수 있는 내용을 다룹니다.

👉 전체 글 읽기: {post_url}
📊 투자 블로그: {investing_url}

{hashtags}

#DevSecOps #CloudSecurity #AWS #Kubernetes #TechBlog"""
        return message

    return f"{title}\n\n{post_url}"


def _strip_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#>*_`]", "", text)
    return text


def _compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _truncate(text: str, max_length: int) -> str:
    if not text or len(text) <= max_length:
        return text
    truncated = text[:max_length].rstrip()
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.7:
        truncated = truncated[:last_space]
    return f"{truncated}..."


def _build_summary(text: str, max_length: int) -> str:
    cleaned = _compact_whitespace(_strip_markdown(text or ""))
    return _truncate(cleaned, max_length) if cleaned else ""


def _build_hashtags(tags: list, max_count: int = 5) -> str:
    if not tags:
        return ""
    clean_tags = []
    for tag in tags[:max_count]:
        tag_text = str(tag).replace("-", "").replace(" ", "")
        tag_text = re.sub(r"[^0-9a-zA-Z_가-힣]", "", tag_text)
        if tag_text:
            clean_tags.append(f"#{tag_text}")
    return " ".join(clean_tags)


def _build_twitter_message(
    title: str, summary: str, post_url: str, hashtags: str
) -> str:
    parts = [f"📝 {title}"]
    if summary:
        parts.append(summary)
    parts.append(post_url)
    if hashtags:
        parts.append(hashtags)

    message = "\n\n".join([part for part in parts if part])
    if len(message) <= 280:
        return message

    for limit in [160, 120, 90, 60, 0]:
        trimmed_summary = _truncate(summary, limit) if limit else ""
        trimmed_parts = [f"📝 {title}"]
        if trimmed_summary:
            trimmed_parts.append(trimmed_summary)
        trimmed_parts.append(post_url)
        if hashtags and limit >= 90:
            trimmed_parts.append(hashtags)
        message = "\n\n".join([part for part in trimmed_parts if part])
        if len(message) <= 280:
            return message

    return f"📝 {_truncate(title, 100)}\n\n{post_url}"


def share_to_twitter(message: str) -> bool:
    """Share to Twitter/X using API v2."""
    if not TWITTER_AVAILABLE:
        print("Twitter: tweepy not installed, skipping")
        return False

    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("Twitter: API credentials not configured, skipping")
        return False

    try:
        tweepy_client = cast(Any, tweepy)
        client = tweepy_client.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

        response = client.create_tweet(text=message)
        print(f"Twitter: Successfully posted! Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Twitter: Error posting - {e}")
        return False


def share_to_facebook(message: str, post_url: str) -> bool:
    """Share to Facebook Page using Graph API."""
    if not REQUESTS_AVAILABLE:
        print("Facebook: requests not installed, skipping")
        return False

    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")

    if not all([page_id, access_token]):
        print("Facebook: API credentials not configured, skipping")
        return False

    try:
        requests_client = cast(Any, requests)
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        payload = {"message": message, "link": post_url, "access_token": access_token}

        response = requests_client.post(url, data=payload, timeout=15)
        result = response.json()

        if "id" in result:
            print(f"Facebook: Successfully posted! Post ID: {result['id']}")
            return True
        else:
            print(
                f"Facebook: Error - {result.get('error', {}).get('message', 'Unknown error')}"
            )
            return False
    except Exception as e:
        print(f"Facebook: Error posting - {e}")
        return False


def decode_octal_path(path: str) -> str:
    """Decode octal escape sequences in file paths (e.g., \\355\\201\\264 -> actual characters)."""
    try:
        # Find all octal escape sequences and convert to bytes
        octal_pattern = r"\\(\d{1,3})"
        matches = list(re.finditer(octal_pattern, path))

        if not matches:
            return path

        # Build byte array: convert text parts and octal escapes to bytes
        byte_parts = []
        last_end = 0

        for match in matches:
            # Add any text before this match as UTF-8 bytes
            if match.start() > last_end:
                text_part = path[last_end : match.start()]
                byte_parts.append(text_part.encode("utf-8"))

            # Convert octal escape to byte
            octal_str = match.group(1)
            byte_val = int(octal_str, 8)
            byte_parts.append(bytes([byte_val]))

            last_end = match.end()

        # Add remaining text as UTF-8 bytes
        if last_end < len(path):
            text_part = path[last_end:]
            byte_parts.append(text_part.encode("utf-8"))

        # Join all bytes and decode as UTF-8
        decoded_bytes = b"".join(byte_parts)
        decoded = decoded_bytes.decode("utf-8", errors="replace")
        return decoded
    except Exception as e:
        # If decoding fails, try alternative: extract date and find file
        print(f"Warning: Failed to decode octal path: {e}")
        # Try to extract date pattern and find file by date
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path)
        if date_match:
            return path  # Will be handled by file finding logic later
        return path


def share_to_linkedin(
    message: str, post_url: Optional[str] = None, image_url: Optional[str] = None
) -> bool:
    """Share to LinkedIn using OAuth 2.0 Access Token with link preview (Open Graph image auto-included)."""
    if not REQUESTS_AVAILABLE:
        print("LinkedIn: requests not installed, skipping")
        return False

    # OAuth 2.0 Access Token 사용 (API key 불필요)
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    person_id = os.environ.get("LINKEDIN_PERSON_ID")

    if not all([access_token, person_id]):
        print("LinkedIn: OAuth 2.0 credentials not configured, skipping")
        print("   필요한 환경 변수: LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID")
        print("   OAuth 인증 실행: python scripts/linkedin_oauth.py")
        return False

    if not post_url:
        print("LinkedIn: Post URL is required for link preview")
        return False

    try:
        requests_client = cast(Any, requests)
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # 방법 1: ARTICLE 타입으로 링크 공유 (링크 미리보기와 이미지 자동 포함)
        # LinkedIn이 Open Graph 메타 태그를 크롤링하여 이미지와 미리보기 표시
        payload_article = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": message.split("\n\n")[1][:200]
                                if "\n\n" in message
                                else message[:200]
                            },
                            "originalUrl": post_url,
                            "title": {
                                "text": message.split("\n")[1].replace("📝 ", "")[:100]
                                if len(message.split("\n")) > 1
                                else message[:100]
                            },
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        response = requests_client.post(
            url, headers=headers, json=payload_article, timeout=15
        )

        if response.status_code == 201:
            print(f"LinkedIn: ✅ Successfully posted with link preview and image!")
            print(f"   LinkedIn이 Open Graph 이미지를 자동으로 크롤링합니다.")
            return True
        else:
            # 방법 2: 텍스트에 링크 포함 (LinkedIn이 자동으로 Open Graph 크롤링)
            print(
                f"LinkedIn: Article share failed ({response.status_code}), trying link-in-text share..."
            )

            # 메시지에 링크가 포함되어 있으면 LinkedIn이 자동으로 크롤링
            message_with_link = message
            if post_url not in message:
                message_with_link = f"{message}\n\n{post_url}"

            payload_text = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": message_with_link},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            response = requests_client.post(
                url, headers=headers, json=payload_text, timeout=15
            )

            if response.status_code == 201:
                print(f"LinkedIn: ✅ Successfully posted with link!")
                print(
                    f"   LinkedIn이 링크를 감지하여 Open Graph 이미지를 자동으로 크롤링합니다."
                )
                print(f"   ⏳ 이미지 표시까지 몇 분이 걸릴 수 있습니다.")
                return True
            else:
                print(f"LinkedIn: ❌ Error - {response.status_code}")
                print(f"   응답: {response.text}")
                return False
    except Exception as e:
        print(f"LinkedIn: ❌ Error posting - {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python share_sns.py <post_file_path>")
        sys.exit(1)

    post_path_arg = sys.argv[1]

    # Decode octal escape sequences if present (common in CI/CD environments)
    if "\\" in post_path_arg and re.search(r"\\\d{1,3}", post_path_arg):
        post_path_arg = decode_octal_path(post_path_arg)
        print(f"Decoded path: {post_path_arg}")

    # Handle file path issues: decode if needed, resolve relative paths
    script_dir = Path(__file__).parent.parent
    posts_dir = script_dir / "_posts"

    # First, try to use the path as-is
    post_path = None
    try:
        if os.path.isabs(post_path_arg):
            post_path = Path(post_path_arg)
        else:
            # Try relative to script directory first
            post_path = script_dir / post_path_arg
            if not post_path.exists():
                # Try relative to current working directory
                post_path = Path(post_path_arg).resolve()
    except (OSError, ValueError) as e:
        # Handle "File name too long" or other path errors
        # This often happens with octal-encoded paths
        print(f"Warning: Path error ({e}), will try to find file by date pattern")
        post_path = None

    # If file doesn't exist or path is invalid, try to find it by date pattern or partial name
    if (post_path is None or not post_path.exists()) and posts_dir.exists():
        # Extract filename from argument, handling octal-encoded paths
        try:
            filename_arg = Path(post_path_arg).name
        except (OSError, ValueError):
            # If Path() fails, try to extract filename manually
            filename_arg = (
                post_path_arg.split("/")[-1] if "/" in post_path_arg else post_path_arg
            )

        # Extract date pattern (YYYY-MM-DD) if present
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename_arg)
        if date_match:
            date_str = date_match.group(1)
            # Find all files starting with that date
            matching_files = list(posts_dir.glob(f"{date_str}-*.md"))
            if len(matching_files) == 1:
                post_path = matching_files[0]
                print(f"Found file by date pattern: {post_path.name}")
            elif len(matching_files) > 1:
                # If multiple files, try to match by partial name
                # Remove non-ASCII characters and try to match
                filename_clean = re.sub(r"[^\w\-]", "", filename_arg.lower())
                for file in matching_files:
                    file_clean = re.sub(r"[^\w\-]", "", file.stem.lower())
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
            filename_clean = re.sub(r"[^\w\-]", "", filename_arg.lower())
            for file in posts_dir.glob("*.md"):
                file_clean = re.sub(r"[^\w\-]", "", file.stem.lower())
                if filename_clean in file_clean or file_clean in filename_clean:
                    post_path = file
                    print(f"Found file by name match: {post_path.name}")
                    break

    # Validate that we found a file
    if post_path is None:
        print(f"Error: Could not resolve file path: {post_path_arg}")
        print(f"Searched in: {posts_dir}")
        sys.exit(1)

    # Convert to absolute path string
    try:
        post_path = str(post_path.resolve())
    except (OSError, ValueError) as e:
        print(f"Error: Invalid file path: {e}")
        print(f"Attempted path: {post_path}")
        sys.exit(1)

    if not os.path.exists(post_path):
        print(f"Error: File not found: {post_path}")
        print(f"Searched in: {posts_dir}")
        sys.exit(1)

    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

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
    twitter_msg = create_share_message(frontmatter, post_url, "twitter")
    results["twitter"] = share_to_twitter(twitter_msg)

    # Facebook
    facebook_msg = create_share_message(frontmatter, post_url, "facebook")
    results["facebook"] = share_to_facebook(facebook_msg, post_url)

    # LinkedIn (포스트 URL과 이미지 URL 전달)
    linkedin_msg = create_share_message(frontmatter, post_url, "linkedin")
    image_url = None
    image_path = frontmatter.get("image")
    if image_path:
        # 이미지 URL 생성 (절대 URL)
        site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")
        # SVG를 PNG로 변환 (LinkedIn은 SVG를 지원하지 않음)
        if image_path.endswith(".svg"):
            image_path = image_path.replace(".svg", ".png")
        image_url = f"{site_url}{image_path}"
    results["linkedin"] = share_to_linkedin(linkedin_msg, post_url, image_url)

    # Summary
    print("\n--- Summary ---")
    for platform, success in results.items():
        status = "✅ Success" if success else "⏭️ Skipped/Failed"
        print(f"{platform.capitalize()}: {status}")

    # Exit with success even if some platforms failed
    # (we don't want to fail the entire workflow)
    sys.exit(0)


if __name__ == "__main__":
    main()

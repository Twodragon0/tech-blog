#!/usr/bin/env python3
"""
Buttondown Email Notification Script
Automatically sends email to subscribers when new blog posts are published.
"""

import os
import sys
import re
import yaml
import requests
import hashlib
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

def mask_sensitive_info(text: str) -> str:
    """민감 정보 마스킹"""
    if not text:
        return text
    # API 키 마스킹
    masked = re.sub(r'Token\s+[a-zA-Z0-9_-]{20,}', 'Token ***MASKED***', text)
    masked = re.sub(r'[?&]key=[a-zA-Z0-9_-]+', '?key=***MASKED***', masked)
    # Buttondown API 키 마스킹
    buttondown_key = os.getenv("BUTTONDOWN_API_KEY", "")
    if buttondown_key and len(buttondown_key) > 10:
        masked = masked.replace(buttondown_key, '***BUTTONDOWN_API_KEY_MASKED***')
    return masked

def safe_print(message: str) -> None:
    """안전한 출력 (민감 정보 마스킹)"""
    safe_message = mask_sensitive_info(message)
    print(safe_message)

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


def get_post_content(file_path: str) -> str:
    """Get the main content of a markdown file (without frontmatter)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def generate_post_url(file_path: str, site_url: str) -> str:
    """Generate the URL for a blog post based on permalink structure."""
    filename = Path(file_path).stem

    # Parse date and title from filename (YYYY-MM-DD-title format)
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', filename)
    if not match:
        return f"{site_url}/posts/{filename}/"

    year, month, day, title = match.groups()

    return f"{site_url}/posts/{year}/{month}/{title}/"


def extract_excerpt_from_content(content: str, max_length: int = 250) -> str:
    """Extract excerpt from post content if excerpt is not available."""
    # Remove markdown links, images, code blocks
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)  # Remove images
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)  # Remove links (keep text)
    content = re.sub(r'```[\s\S]*?```', '', content)  # Remove code blocks
    content = re.sub(r'`[^`]+`', '', content)  # Remove inline code
    content = re.sub(r'#{1,6}\s+', '', content)  # Remove headers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*([^*]+)\*', r'\1', content)  # Remove italic
    content = re.sub(r'\n+', ' ', content)  # Replace newlines with space
    content = content.strip()
    
    if len(content) > max_length:
        # Try to cut at sentence boundary
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        last_sentence = max(last_period, last_exclamation, last_question)
        
        if last_sentence > max_length * 0.7:  # If we found a sentence boundary reasonably close
            content = truncated[:last_sentence + 1]
        else:
            content = truncated + '...'
    
    return content


def format_date_from_filename(filename: str) -> str:
    """Format date from filename (YYYY-MM-DD-title.md)."""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        # Convert to Korean date format
        months = ['1월', '2월', '3월', '4월', '5월', '6월', 
                  '7월', '8월', '9월', '10월', '11월', '12월']
        try:
            month_name = months[int(month) - 1]
            return f"{year}년 {month_name} {day}일"
        except (ValueError, IndexError):
            return f"{year}-{month}-{day}"
    return ""


def format_summary_for_email(description: str) -> str:
    """Format summary/excerpt for better readability in email with improved UI/UX."""
    if not description:
        return ""
    
    # Remove extra whitespace
    description = re.sub(r'\s+', ' ', description.strip())
    
    # If description is short (less than 150 chars), return as is
    if len(description) <= 150:
        return description
    
    # Pattern 1: Content with parentheses - most common pattern
    # e.g., "주제(설명), 주제2(설명2), 주제3(설명3)까지"
    if '(' in description and ')' in description:
        # Use regex to find all topic(content) patterns
        # Pattern matches: "topic(content)" where content can contain commas, slashes, etc.
        pattern = r'([^,()]+?)\(([^)]+?)\)'
        matches = re.finditer(pattern, description)
        
        formatted_parts = []
        last_end = 0
        
        for match in matches:
            # Check if there's text before this match (like "가이드: " prefix)
            if match.start() > last_end:
                prefix = description[last_end:match.start()].strip()
                # Remove trailing colons, commas, and common markers
                prefix = re.sub(r'[:,\s]+$', '', prefix)
                if prefix and not prefix.endswith('까지'):
                    # This might be an intro text
                    pass
            
            topic = match.group(1).strip()
            content = match.group(2).strip()
            
            # Clean up topic (remove trailing markers and colons)
            topic = re.sub(r'\s*(까지|및|그리고|,|:)$', '', topic).strip()
            
            # Format content - replace slashes with commas for better readability
            content = content.replace('/', ', ')
            # Clean up multiple spaces
            content = re.sub(r'\s+', ' ', content)
            
            # Add appropriate emoji based on topic keywords
            emoji = '📌'
            topic_lower = topic.lower()
            if any(kw in topic_lower for kw in ['즉시', '조치', '대응', 'action', 'response']):
                emoji = '⚡'
            elif any(kw in topic_lower for kw in ['위험', 'risk', 'threat', '공격', '스와핑', '복제']):
                emoji = '⚠️'
            elif any(kw in topic_lower for kw in ['확인', 'check', 'verify', '교체', 'imei', 'usim', 'esim']):
                emoji = '🔍'
            elif any(kw in topic_lower for kw in ['업데이트', 'update', '강화', '2025']):
                emoji = '🔄'
            elif any(kw in topic_lower for kw in ['시사점', 'implication', 'lesson', '기업', 'enterprise']):
                emoji = '💼'
            elif any(kw in topic_lower for kw in ['보안', 'security', 'mfa', 'otp']):
                emoji = '🔒'
            
            formatted_parts.append({
                'topic': topic,
                'content': content,
                'emoji': emoji
            })
            
            last_end = match.end()
        
        # If we found structured parts, format them nicely
        if formatted_parts:
            result_parts = []
            for part in formatted_parts[:8]:  # Limit to 8 items for readability
                result_parts.append(
                    f"{part['emoji']} **{part['topic']}**\n   {part['content']}"
                )
            
            # Check if there's trailing text after last match
            if last_end < len(description):
                trailing = description[last_end:].strip()
                trailing = re.sub(r'^\s*(까지|및|그리고|,)\s*', '', trailing)
                if trailing and len(trailing) > 5:
                    result_parts.append(f"💡 {trailing}")
            
            return "\n\n".join(result_parts)
    
    # Pattern 2: Content with colons (e.g., "주제: 내용, 주제2: 내용2")
    if ':' in description and ',' in description:
        # Split by comma and check if items contain colons
        parts = [p.strip() for p in description.split(',')]
        if len(parts) > 2 and any(':' in p for p in parts[:3]):
            formatted_parts = []
            for part in parts[:6]:  # Limit to 6 items
                if ':' in part:
                    # Split by colon
                    key_value = part.split(':', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        # Add emoji based on key content
                        emoji = '📌'
                        key_lower = key.lower()
                        if any(kw in key_lower for kw in ['주제', 'topic', 'subject']):
                            emoji = '📝'
                        elif any(kw in key_lower for kw in ['내용', 'content', 'summary']):
                            emoji = '📋'
                        elif any(kw in key_lower for kw in ['요약', 'summary']):
                            emoji = '✨'
                        formatted_parts.append(f"{emoji} **{key}:** {value}")
                    else:
                        formatted_parts.append(f"• {part}")
                else:
                    formatted_parts.append(f"• {part}")
            
            if formatted_parts:
                return "\n\n".join(formatted_parts)
    
    # Pattern 3: Long sentences - try to break into bullet points
    sentences = re.split(r'([.!?。！？]\s+)', description)
    if len(sentences) > 3:
        # Reconstruct sentences
        formatted_sentences = []
        current_sentence = ""
        for i, part in enumerate(sentences):
            current_sentence += part
            # Check if this is a complete sentence
            if part.strip() and part.strip()[-1] in '.!?。！？':
                sentence = current_sentence.strip()
                if sentence and len(sentence) > 20:  # Only format substantial sentences
                    # Check if sentence starts with common keywords
                    if any(sentence.startswith(kw) for kw in ['SKT', 'IMEI', 'USIM', 'MFA', '보안', '통신사']):
                        formatted_sentences.append(f"🔹 {sentence}")
                    else:
                        formatted_sentences.append(f"• {sentence}")
                current_sentence = ""
        
        if formatted_sentences:
            return "\n\n".join(formatted_sentences)
    
    # Pattern 4: If description contains common section markers
    if any(marker in description for marker in ['까지', '부터', '및', '그리고']):
        # Try to split by common delimiters
        parts = re.split(r'[,，]\s*(?=[가-힣A-Z])', description)
        if len(parts) > 3:
            formatted_parts = []
            for part in parts[:6]:  # Limit to 6 items for readability
                part = part.strip()
                if part:
                    # Remove trailing markers like "까지", "및" from individual items
                    part = re.sub(r'\s*(까지|및|그리고)$', '', part)
                    if part:
                        formatted_parts.append(f"• {part}")
            
            if formatted_parts:
                return "\n\n".join(formatted_parts)
    
    # Fallback: If description is very long, wrap it nicely
    if len(description) > 200:
        # Try to break at sentence boundaries
        sentences = re.split(r'([.!?。！？]\s+)', description)
        if len(sentences) > 2:
            # Take first few sentences and format nicely
            result = ""
            for i in range(0, min(4, len(sentences)), 2):
                if i + 1 < len(sentences):
                    sentence = (sentences[i] + sentences[i + 1]).strip()
                    if sentence:
                        result += f"{sentence}\n\n"
            return result.strip()
    
    # Default: return as is with some spacing improvements
    return description


def create_email_content(frontmatter: dict, post_url: str, post_content: str = None, filename: str = None) -> tuple:
    """Create email subject and body for Buttondown with improved UI/UX."""
    title = frontmatter.get('title', 'New Post')
    description = frontmatter.get('excerpt', frontmatter.get('description', ''))
    tags = frontmatter.get('tags', [])
    category = frontmatter.get('categories', frontmatter.get('category', ''))

    # Extract excerpt from content if not available
    if not description and post_content:
        description = extract_excerpt_from_content(post_content, max_length=250)

    # Format date
    date_str = ""
    date_short = ""
    if filename:
        date_str = format_date_from_filename(filename)
        # Extract short date (YYYY-MM-DD) for subject
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            date_short = match.group(0)  # YYYY-MM-DD format

    # Email subject with date and timestamp to avoid duplicate detection
    # Add date and timestamp to subject to make it unique
    clean_title = title
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    
    if date_short:
        # Include both post date and current timestamp for uniqueness
        subject = f"📢 새 글 ({date_short}) [{timestamp}]: {clean_title}"
    else:
        # Fallback: use timestamp only if date extraction fails
        subject = f"📢 새 글 [{timestamp}]: {clean_title}"

    # Email body (Markdown format with improved UI/UX)
    body_parts = [
        "---",
        "",
        f"# ✨ {title}",
        "",
    ]

    # Date
    if date_str:
        body_parts.extend([
            f"📅 **발행일:** {date_str}",
            "",
        ])

    # Category badge
    if category:
        if isinstance(category, list):
            category = category[0] if category else ''
        if category:
            # Category emoji mapping
            category_emoji = {
                'security': '🔒',
                'devsecops': '🛡️',
                'devops': '⚙️',
                'cloud': '☁️',
                'kubernetes': '☸️',
                'finops': '💰',
                'incident': '🚨',
            }
            emoji = category_emoji.get(category.lower(), '📝')
            body_parts.extend([
                f"{emoji} **카테고리:** `{category}`",
                "",
            ])

    # Tags
    if tags:
        tag_list = tags[:6]  # Limit to 6 tags
        tag_badges = ' '.join([f"`{tag}`" for tag in tag_list])
        body_parts.extend([
            f"🏷️ **태그:** {tag_badges}",
            "",
        ])

    # Description/Excerpt - formatted for better readability
    if description:
        formatted_description = format_summary_for_email(description)
        body_parts.extend([
            "---",
            "",
            "## 📋 요약",
            "",
            formatted_description,
            "",
            "---",
            "",
        ])

    # Call to action - more prominent
    body_parts.extend([
        "---",
        "",
        "### 🚀 전체 글 읽기",
        "",
        f"> **[👉 지금 바로 읽기 →]({post_url})**",
        "",
        "---",
        "",
    ])

    # Footer with timestamp and unique identifier to avoid duplicate detection
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Create a unique hash based on post URL and timestamp
    unique_id = hashlib.md5(f"{post_url}{current_time}".encode()).hexdigest()[:8]
    
    body_parts.extend([
        "---",
        "",
        "💌 **TwoDragon's Tech Blog**",
        "",
        "이 이메일은 [TwoDragon's Tech Blog](https://tech.2twodragon.com)의 새 글 알림입니다.",
        "",
        "📧 더 많은 기술 콘텐츠를 받아보려면 [블로그 구독하기](https://tech.2twodragon.com/support.html)",
        "",
        "---",
        "",
        f"<small>발송 시간: {current_time} | ID: {unique_id} | 구독 해지를 원하시면 이메일 하단의 링크를 클릭하세요.</small>",
    ])

    body = "\n".join(body_parts)

    return subject, body


def send_buttondown_email(subject: str, body: str, api_key: str) -> bool:
    """Send email via Buttondown API."""
    url = "https://api.buttondown.com/v1/emails"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    # Use "about_to_send" status to immediately send to all subscribers
    # Valid statuses: "draft", "about_to_send", "scheduled", "imported", "transactional"
    # Note: "sent" is not valid for newly created emails
    data = {
        "subject": subject,
        "body": body,
        "status": "about_to_send"  # Immediately send to all subscribers
    }

    try:
        print(f"📤 Sending email via Buttondown API...")
        print(f"   URL: {url}")
        print(f"   Subject: {subject[:50]}...")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)

        # Check response status
        if response.status_code in [200, 201]:
            result = response.json() if response.text else {}
            email_id = result.get('id', 'N/A')
            print(f"✅ Email sent successfully!")
            print(f"   Email ID: {email_id}")
            print(f"   Subject: {subject}")
            return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            print(f"   Please check your BUTTONDOWN_API_KEY")
            # Security: Mask API key in log output
            masked_key = f"Token {api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "Token ***MASKED***"
            safe_print(f"   API Key format: {masked_key}")
            return False
        elif response.status_code == 404:
            print(f"❌ Resource not found (404)")
            print(f"   This might indicate an invalid API endpoint or missing resource")
            print(f"   Response: {response.text[:200]}")
            return False
        else:
            print(f"❌ Failed to send email: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Error detail: {error_data['detail']}")
            except:
                pass
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout: API did not respond within 30 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print(f"   Please check your internet connection and API endpoint")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def find_post_file(post_path: str) -> Path:
    """Find post file with robust path handling for Unicode filenames."""
    post_path = post_path.strip()
    
    # Remove quotes if present
    if post_path.startswith('"') and post_path.endswith('"'):
        post_path = post_path[1:-1]
    if post_path.startswith("'") and post_path.endswith("'"):
        post_path = post_path[1:-1]

    project_root = Path(__file__).parent.parent
    posts_dir = project_root / '_posts'
    
    # Convert to Path object for better handling
    post_file = Path(post_path)
    
    # Try to resolve the path
    if not post_file.is_absolute():
        # If relative, try from project root
        post_file = project_root / post_path
    
    # Validate file exists
    if post_file.exists():
        return post_file
    
    # If file not found, try to find by filename pattern
    # Extract filename from path (handle both relative and absolute paths)
    filename = post_file.name
    
    # Try exact match first
    if posts_dir.exists():
        exact_match = posts_dir / filename
        if exact_match.exists():
            return exact_match
        
        # Try pattern matching (for cases where encoding is corrupted)
        # Extract date and partial title from filename
        match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', filename)
        if match:
            date_part = match.group(1)
            title_part = match.group(2)
            
            # Find files matching the date
            for f in posts_dir.glob(f'{date_part}-*.md'):
                # Check if the file matches (case-insensitive, partial match)
                if date_part in f.stem:
                    print(f"🔍 Found matching file by pattern: {f.name}")
                    return f
    
    # If still not found, return the original path for error reporting
    return post_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python buttondown_notify.py <post_file_path>")
        sys.exit(1)

    post_path = sys.argv[1]
    post_file = find_post_file(post_path)
    
    # Validate file exists
    if not post_file.exists():
        print(f"❌ Post file not found: {post_path}")
        print(f"   Resolved path: {post_file}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Available files in _posts/ (first 10):")
        posts_dir = Path(__file__).parent.parent / '_posts'
        if posts_dir.exists():
            for f in list(posts_dir.glob('*.md'))[:10]:
                print(f"     - {f.name}")
        sys.exit(1)
    
    # Use resolved path
    post_path = str(post_file)

    # Get API key from environment
    api_key = os.environ.get('BUTTONDOWN_API_KEY')
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        print("   Please set it in GitHub Secrets or .env file")
        sys.exit(1)
    
    # Validate API key format (should be UUID-like)
    if len(api_key) < 20:
        print("⚠️ Warning: API key seems too short. Please verify your BUTTONDOWN_API_KEY")
    
    # Test API connection (optional, can be disabled for faster execution)
    # This helps catch authentication issues early
    # Security: Mask API key in log output
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***MASKED***"
    safe_print(f"🔑 API Key: {masked_key}")

    # Get site URL
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')

    print(f"📧 Processing post: {post_path}")

    # Parse post metadata
    frontmatter = parse_frontmatter(post_path)
    if not frontmatter:
        print("⚠️ No frontmatter found in post")
        frontmatter = {'title': Path(post_path).stem}

    # Check if post should be published (not draft)
    if frontmatter.get('draft', False):
        print("⏭️ Skipping draft post")
        sys.exit(0)

    # Generate post URL
    post_url = generate_post_url(post_path, site_url)
    print(f"🔗 Post URL: {post_url}")

    # Get post content for excerpt extraction
    post_content = get_post_content(post_path)
    filename = Path(post_path).name

    # Create email content with improved UI/UX
    subject, body = create_email_content(frontmatter, post_url, post_content, filename)

    # Send email
    success = send_buttondown_email(subject, body, api_key)

    if success:
        print("✅ Buttondown notification complete!")
    else:
        print("❌ Failed to send Buttondown notification")
        sys.exit(1)


if __name__ == "__main__":
    main()

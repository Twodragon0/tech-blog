#!/usr/bin/env python3
"""
Buttondown Email Notification Script
Sends clean Markdown newsletter emails via Buttondown API.

Buttondown natively renders Markdown into responsive HTML emails
with its own template system, so we send Markdown directly.

Best practices (per Buttondown docs):
- 500-750 words for readable length
- Minimize links/images to avoid Gmail Promotions tab
- Use <!-- buttondown-editor-mode: fancy --> for explicit Markdown mode
- Buttondown handles responsive design, dark mode, unsubscribe
"""

import os
import re
import sys
from pathlib import Path

import requests
import yaml


def mask_sensitive_info(text: str) -> str:
    if not text:
        return text
    masked = re.sub(r"Token\s+[a-zA-Z0-9_-]{20,}", "Token ***MASKED***", text)
    buttondown_key = os.getenv("BUTTONDOWN_API_KEY", "")
    if buttondown_key and len(buttondown_key) > 10:
        masked = masked.replace(buttondown_key, "***MASKED***")
    return masked


def safe_print(message: str) -> None:
    print(mask_sensitive_info(message))


# Load .env
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value


def parse_frontmatter(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}


def get_post_content(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def generate_post_url(file_path: str, site_url: str) -> str:
    filename = Path(file_path).stem
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)", filename)
    if not match:
        return f"{site_url}/posts/{filename}/"
    year, month, day, title = match.groups()
    return f"{site_url}/posts/{year}/{month}/{title}/"


def extract_excerpt(content: str, max_length: int = 200) -> str:
    """Extract clean text excerpt from markdown content."""
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
    content = re.sub(r"\[([^\]]*)\]\(.*?\)", r"\1", content)
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"`[^`]+`", "", content)
    content = re.sub(r"#{1,6}\s+", "", content)
    content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)
    content = re.sub(r"\*([^*]+)\*", r"\1", content)
    content = re.sub(r">\s*", "", content)
    content = re.sub(r"\|[^\n]+\|", "", content)
    content = re.sub(r"-{3,}", "", content)
    content = re.sub(r"\n+", " ", content)
    content = content.strip()

    if len(content) > max_length:
        truncated = content[:max_length]
        last_sentence = max(
            truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?")
        )
        if last_sentence > max_length * 0.6:
            content = truncated[: last_sentence + 1]
        else:
            last_space = truncated.rfind(" ")
            content = (truncated[:last_space] + "...") if last_space > 0 else (truncated + "...")
    return content


def extract_toc_items(content: str, max_items: int = 5) -> list:
    """Extract top-level headings for table of contents."""
    headings = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    items = []
    for h in headings[:max_items]:
        h = re.sub(r"\*\*([^*]+)\*\*", r"\1", h)
        h = re.sub(r"\[([^\]]*)\]\(.*?\)", r"\1", h)
        # Remove emoji and leading numbering (e.g. "📊 ", "1. ")
        h = re.sub(r"^[\U0001F300-\U0001FAD6\u2600-\u27BF\u2700-\u27BF]+\s*", "", h)
        h = re.sub(r"^\d+\.\s+", "", h)
        h = h.strip()
        if h and not h.lower().startswith(("목차", "table of", "toc")):
            items.append(h)
    return items


def get_image_url(frontmatter: dict, site_url: str) -> str:
    """Get OG PNG image URL (email clients don't support SVG)."""
    image = frontmatter.get("image", "")
    if not image:
        return ""
    image = str(image)
    if image.endswith(".svg"):
        og_png = image.replace(".svg", "_og.png")
        if os.path.exists(og_png.lstrip("/")):
            image = og_png
        else:
            png = image.replace(".svg", ".png")
            if os.path.exists(png.lstrip("/")):
                image = png
            else:
                return ""
    if image.startswith(("http://", "https://")):
        return image
    return f"{site_url}{image}" if image.startswith("/") else f"{site_url}/{image}"


def format_date(filename: str) -> str:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
    if match:
        year, month, day = match.groups()
        return f"{year}.{month}.{day}"
    return ""


CATEGORY_LABELS = {
    "security": "Security",
    "devsecops": "DevSecOps",
    "devops": "DevOps",
    "cloud": "Cloud",
    "kubernetes": "Kubernetes",
    "finops": "FinOps",
    "incident": "Incident",
}


def build_markdown_email(
    title: str,
    excerpt: str,
    post_url: str,
    image_url: str,
    date_str: str,
    category: str,
    tags: list,
    toc_items: list,
    site_url: str,
) -> str:
    """Build a clean Markdown email body.

    Buttondown renders Markdown into its own responsive HTML template.
    Keep it simple: Buttondown handles styling, responsive, dark mode.
    """
    cat_key = str(category).lower() if category else ""
    cat_label = CATEGORY_LABELS.get(cat_key, str(category).title() if category else "Tech")

    parts = []

    # Explicit Markdown mode for Buttondown
    parts.append("<!-- buttondown-editor-mode: fancy -->")
    parts.append("")

    # Header: category + date
    meta_line = f"**{cat_label}**"
    if date_str:
        meta_line += f" | {date_str}"
    parts.append(meta_line)
    parts.append("")

    # Title
    parts.append(f"# {title}")
    parts.append("")

    # Hero image (OG PNG, not SVG)
    if image_url:
        parts.append(f"[![{title}]({image_url})]({post_url})")
        parts.append("")

    # Excerpt
    if excerpt:
        parts.append(excerpt)
        parts.append("")

    # Tags
    if tags:
        tag_str = " ".join([f"`{tag}`" for tag in tags[:5]])
        parts.append(tag_str)
        parts.append("")

    # Table of contents
    if toc_items:
        parts.append("---")
        parts.append("")
        parts.append("**In This Post**")
        parts.append("")
        for i, item in enumerate(toc_items, 1):
            parts.append(f"{i}. {item}")
        parts.append("")

    # CTA
    parts.append("---")
    parts.append("")
    parts.append(f"**[Read Full Post &rarr;]({post_url})**")
    parts.append("")

    # Footer
    parts.append("---")
    parts.append("")
    parts.append(
        f"[TwoDragon Tech Blog]({site_url}) | "
        f"[Archive]({site_url}/archive/) | "
        f"[Support]({site_url}/support/)"
    )

    return "\n".join(parts)


def create_email_content(
    frontmatter: dict,
    post_url: str,
    post_content: "str | None" = None,
    filename: "str | None" = None,
) -> tuple:
    """Create email subject and Markdown body."""
    title = frontmatter.get("title", "New Post")
    excerpt = frontmatter.get("excerpt", frontmatter.get("description", ""))
    tags = frontmatter.get("tags", [])
    category = frontmatter.get("categories", frontmatter.get("category", ""))
    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    if isinstance(category, list) and category:
        category = category[0]

    if not excerpt and post_content:
        excerpt = extract_excerpt(post_content, max_length=200)

    date_str = format_date(filename) if filename else ""
    image_url = get_image_url(frontmatter, site_url)
    toc_items = extract_toc_items(post_content) if post_content else []

    # Subject line: clean, descriptive
    date_short = ""
    if filename:
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
        if m:
            date_short = m.group(0)

    subject = f"[TwoDragon] {title}"
    if date_short:
        subject = f"[{date_short}] {title}"

    body = build_markdown_email(
        title=title,
        excerpt=excerpt,
        post_url=post_url,
        image_url=image_url,
        date_str=date_str,
        category=category,
        tags=tags,
        toc_items=toc_items,
        site_url=site_url,
    )

    return subject, body


def send_buttondown_email(subject: str, body: str, api_key: str) -> bool:
    """Send Markdown email via Buttondown API."""
    url = "https://api.buttondown.com/v1/emails"
    headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

    data = {
        "subject": subject,
        "body": body,
        "status": "about_to_send",
    }

    try:
        print("Sending email via Buttondown API...")
        print(f"  Subject: {subject[:80]}")

        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            result = response.json() if response.text else {}
            email_id = result.get("id", "N/A")
            print(f"  Sent successfully (ID: {email_id})")
            return True
        elif response.status_code == 401:
            print("  Auth failed (401). Check BUTTONDOWN_API_KEY.")
            safe_print(f"  API Key length: {len(api_key)}")
            return False
        else:
            print(f"  Failed: {response.status_code}")
            print(f"  Response: {response.text[:300]}")
            return False

    except requests.exceptions.Timeout:
        print("  Timeout: API did not respond within 30s")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  Connection error: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  Request error: {e}")
        return False


def find_post_file(post_path: str) -> Path:
    post_path = post_path.strip().strip("'\"")
    project_root = Path(__file__).parent.parent
    posts_dir = project_root / "_posts"
    post_file = Path(post_path)

    if not post_file.is_absolute():
        post_file = project_root / post_path

    if post_file.exists():
        return post_file

    if posts_dir.exists():
        exact_match = posts_dir / post_file.name
        if exact_match.exists():
            return exact_match

        match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md", post_file.name)
        if match:
            date_part = match.group(1)
            for f in posts_dir.glob(f"{date_part}-*.md"):
                if date_part in f.stem:
                    return f

    return post_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python buttondown_notify.py <post_file_path>")
        sys.exit(1)

    post_path = sys.argv[1]
    post_file = find_post_file(post_path)

    if not post_file.exists():
        print(f"Post file not found: {post_path}")
        sys.exit(1)

    post_path = str(post_file)

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("BUTTONDOWN_API_KEY not set")
        sys.exit(1)

    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    print(f"Processing: {Path(post_path).name}")

    frontmatter = parse_frontmatter(post_path)
    if not frontmatter:
        frontmatter = {"title": Path(post_path).stem}

    if frontmatter.get("draft", False):
        print("Skipping draft post")
        sys.exit(0)

    post_url = generate_post_url(post_path, site_url)
    post_content = get_post_content(post_path)
    filename = Path(post_path).name

    subject, body = create_email_content(frontmatter, post_url, post_content, filename)

    success = send_buttondown_email(subject, body, api_key)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

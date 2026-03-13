#!/usr/bin/env python3
"""
Fetch Open Graph images from article URLs in news-card includes
and add them as image= parameters.

Usage:
    python3 scripts/fetch_og_images.py [--dry-run] [--file FILENAME]

Options:
    --dry-run    Show what would be changed without modifying files
    --file       Process only a specific file (basename, e.g. 2026-03-07-...)
"""

import argparse
import logging
import os
import re
import ssl
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
POSTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts"
)
MAX_WORKERS = 3
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 0.5  # seconds between requests to same domain
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Suppress InsecureRequestWarning when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter per domain
# ---------------------------------------------------------------------------
_domain_locks: dict[str, Lock] = defaultdict(Lock)
_domain_last_request: dict[str, float] = {}
_global_lock = Lock()


def _rate_limit(domain: str) -> None:
    """Ensure at least RATE_LIMIT_DELAY seconds between requests to the same domain."""
    with _global_lock:
        lock = _domain_locks[domain]
    with lock:
        last = _domain_last_request.get(domain, 0.0)
        elapsed = time.time() - last
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        _domain_last_request[domain] = time.time()


# ---------------------------------------------------------------------------
# OG image fetching
# ---------------------------------------------------------------------------
def fetch_og_image(url: str) -> str | None:
    """Fetch the og:image (or twitter:image fallback) from a URL."""
    domain = urlparse(url).netloc
    _rate_limit(domain)

    try:
        # Try with SSL verification first, fall back to no-verify
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
        except requests.exceptions.SSLError:
            resp = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                verify=False,
            )
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("  HTTP error for %s: %s", url, exc)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try og:image first, then twitter:image
    for prop in ("og:image", "twitter:image"):
        meta = soup.find("meta", attrs={"property": prop, "content": True})
        if not meta:
            meta = soup.find("meta", attrs={"name": prop, "content": True})
        if meta:
            img_url = meta["content"].strip()
            if not img_url or img_url.startswith("data:"):
                continue
            # Convert relative URLs to absolute
            if not img_url.startswith(("http://", "https://")):
                img_url = urljoin(url, img_url)
            return img_url

    log.warning("  No og:image found for %s", url)
    return None


# ---------------------------------------------------------------------------
# Parsing news-card includes
# ---------------------------------------------------------------------------
# Match an entire news-card include block
NEWS_CARD_RE = re.compile(
    r"(\{%-?\s*include\s+news-card\.html\s*\n)"  # opening tag
    r'((?:\s+\w+="[^"]*"\n)*)'  # parameters (each on own line)
    r"(\s*-?%\})",  # closing tag
    re.MULTILINE,
)

URL_PARAM_RE = re.compile(r'\n( +url="([^"]*)")\n')
IMAGE_PARAM_RE = re.compile(r'\s+image="[^"]*"')


def process_file(filepath: str, dry_run: bool = False) -> tuple[int, int, int]:
    """
    Process a single markdown file.
    Returns (total_cards, images_added, errors).
    """
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    total_cards = 0
    images_added = 0
    errors = 0
    modified = False

    # We need to process matches in reverse order so that insertions
    # don't shift positions for subsequent matches.
    matches = list(NEWS_CARD_RE.finditer(content))

    # Collect (url, match) pairs to fetch
    tasks: list[tuple[str, re.Match]] = []
    for m in matches:
        total_cards += 1
        params_block = m.group(2)

        # Skip if already has image parameter
        if IMAGE_PARAM_RE.search(params_block):
            log.info("  [%s] Already has image, skipping", filename)
            continue

        url_match = URL_PARAM_RE.search(params_block)
        if not url_match:
            log.warning("  [%s] No url= found in news-card block", filename)
            errors += 1
            continue

        url = url_match.group(2)
        tasks.append((url, m))

    if not tasks:
        return total_cards, 0, errors

    log.info("[%s] Found %d cards needing images", filename, len(tasks))

    # Fetch OG images (we do it sequentially per file to keep replacements simple,
    # but the outer loop runs files in parallel)
    replacements: list[tuple[re.Match, str]] = []  # (match, image_url)
    for url, m in tasks:
        log.info("  Fetching: %s", url)
        img_url = fetch_og_image(url)
        if img_url:
            # Escape double quotes in URL (very unlikely but be safe)
            img_url = img_url.replace('"', "&quot;")
            replacements.append((m, img_url))
            images_added += 1
            log.info("  ✓ Found image: %s", img_url[:80])
        else:
            errors += 1

    if not replacements:
        return total_cards, 0, errors

    # Apply replacements in reverse order of position
    replacements.sort(key=lambda x: x[0].start(), reverse=True)
    for m, img_url in replacements:
        params_block = m.group(2)
        # Insert image= line right after the url= line
        url_line_match = URL_PARAM_RE.search(params_block)
        if url_line_match:
            url_line = url_line_match.group(1)  # e.g. '  url="https://..."'
            # Determine indentation from url line
            indent_match = re.match(r"^(\s+)", url_line)
            indent = indent_match.group(1) if indent_match else "  "
            image_line = f'{indent}image="{img_url}"'
            # Insert after url line + newline
            insert_pos = url_line_match.end()  # position after the newline
            new_params = (
                params_block[:insert_pos]
                + image_line
                + "\n"
                + params_block[insert_pos:]
            )
            # Reconstruct the full match
            new_block = m.group(1) + new_params + m.group(3)
            content = content[: m.start()] + new_block + content[m.end() :]
            modified = True

    if modified and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        log.info("[%s] Saved with %d new images", filename, images_added)
    elif modified and dry_run:
        log.info("[%s] DRY RUN: would add %d images", filename, images_added)

    return total_cards, images_added, errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch OG images for news-card includes"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files")
    parser.add_argument(
        "--file", type=str, help="Process only this file (basename pattern)"
    )
    args = parser.parse_args()

    if not os.path.isdir(POSTS_DIR):
        log.error("Posts directory not found: %s", POSTS_DIR)
        sys.exit(1)

    # Collect markdown files
    md_files = sorted(
        os.path.join(POSTS_DIR, f) for f in os.listdir(POSTS_DIR) if f.endswith(".md")
    )

    if args.file:
        md_files = [f for f in md_files if args.file in os.path.basename(f)]

    log.info("Processing %d files from %s", len(md_files), POSTS_DIR)
    if args.dry_run:
        log.info("DRY RUN mode - no files will be modified")

    total_cards = 0
    total_added = 0
    total_errors = 0

    # Process files with thread pool - each file is independent
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {
            executor.submit(process_file, fp, args.dry_run): fp for fp in md_files
        }
        for future in as_completed(future_to_file):
            fp = future_to_file[future]
            try:
                cards, added, errs = future.result()
                total_cards += cards
                total_added += added
                total_errors += errs
            except Exception:
                log.exception("Error processing %s", fp)
                total_errors += 1

    # Summary
    log.info("=" * 60)
    log.info("SUMMARY")
    log.info("  Total news-card includes: %d", total_cards)
    log.info("  Images successfully added: %d", total_added)
    log.info("  Errors/skipped:            %d", total_errors)
    log.info(
        "  Already had images:        %d", total_cards - total_added - total_errors
    )
    log.info("=" * 60)


if __name__ == "__main__":
    main()

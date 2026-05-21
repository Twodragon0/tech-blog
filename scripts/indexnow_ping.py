#!/usr/bin/env python3
"""IndexNow ping script for Bing and Yandex search engine notifications.

Submits URLs from sitemap.xml (or a custom list) to IndexNow endpoints so that
Bing, Yandex, and other participating search engines are notified immediately
of content changes.

Google does NOT participate in IndexNow; use GSC for Google indexing.

Usage:
    # Submit all URLs from sitemap.xml
    python3 scripts/indexnow_ping.py

    # Submit specific URLs only
    python3 scripts/indexnow_ping.py --urls https://tech.2twodragon.com/post1 https://tech.2twodragon.com/post2

    # Dry-run: print payload without sending
    python3 scripts/indexnow_ping.py --dry-run

Environment:
    INDEXNOW_KEY  - Override key (takes precedence over _config.yml)
"""

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/IndexNow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]

HOST = "tech.2twodragon.com"
CONFIG_PATH = Path(__file__).parent.parent / "_config.yml"
PRODUCTION_SITEMAP_URL = f"https://{HOST}/sitemap.xml"

# IndexNow limit per submission
URL_LIMIT = 10_000

# Retry settings for 429 rate limit
MAX_RETRIES = 1
RETRY_BACKOFF = 30  # seconds

# Sitemap fetch timeout (production XML download)
SITEMAP_FETCH_TIMEOUT = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def mask_key(key: str) -> str:
    """Return a safe masked version of the key (first 4 + last 4 chars)."""
    if len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def mask_key_location(key_location: str, key: str) -> str:
    """Replace raw key in a keyLocation URL with its masked form."""
    return key_location.replace(key, mask_key(key))


def read_key_from_config() -> Optional[str]:
    """Parse indexnow_key from _config.yml (simple regex-free YAML read)."""
    if not CONFIG_PATH.exists():
        return None
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("indexnow_key:"):
                value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                return value if value else None
    return None


def resolve_key() -> str:
    """Resolve IndexNow key: env var INDEXNOW_KEY > _config.yml."""
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    if key:
        return key
    key = read_key_from_config()
    if key:
        return key
    print(
        "ERROR: INDEXNOW_KEY not set and indexnow_key not found in _config.yml",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_sitemap_urls(sitemap_url: str = PRODUCTION_SITEMAP_URL) -> list[str]:
    """Fetch sitemap.xml from `sitemap_url` and return all <loc> URLs.

    Production-only source: the deployed sitemap is the ground truth for what
    is publicly crawlable. If the fetch or parse fails, the caller treats it
    as a hard failure — local files are not consulted because pinging URLs
    that aren't live yet would be useless.
    """
    req = Request(sitemap_url, headers={"User-Agent": "TechBlog-IndexNow/1.0"})
    try:
        with urlopen(req, timeout=SITEMAP_FETCH_TIMEOUT) as resp:
            if resp.status != 200:
                print(
                    f"ERROR: Sitemap fetch returned HTTP {resp.status} from {sitemap_url}",
                    file=sys.stderr,
                )
                return []
            xml_text = resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as exc:
        print(
            f"ERROR: Failed to fetch sitemap from {sitemap_url}: {exc}",
            file=sys.stderr,
        )
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(
            f"ERROR: Failed to parse sitemap fetched from {sitemap_url}: {exc}",
            file=sys.stderr,
        )
        return []

    ns = root.tag.split("}")[0] + "}" if "{" in root.tag else ""
    urls = []
    for url_elem in root.findall(f"{ns}url"):
        loc = url_elem.find(f"{ns}loc")
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


def build_payload(key: str, urls: list[str]) -> dict:
    """Build the IndexNow JSON payload."""
    key_location = f"https://{HOST}/{key}.txt"
    return {
        "host": HOST,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }


def post_to_endpoint(
    endpoint: str, payload: dict, dry_run: bool = False
) -> tuple[bool, int, str]:
    """
    POST payload to a single IndexNow endpoint.

    Returns (success: bool, status_code: int, message: str).
    200 and 202 are treated as success (202 = received but key not verified yet).
    """
    if dry_run:
        return True, 0, "dry-run"

    body = json.dumps(payload).encode("utf-8")
    req = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "TechBlog-IndexNow/1.0",
        },
        method="POST",
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=30) as resp:
                status = resp.status
                if status in (200, 202):
                    return True, status, "OK" if status == 200 else "Accepted (202 - key verification pending)"
                return False, status, f"Unexpected status {status}"
        except HTTPError as exc:
            status = exc.code
            if status == 429 and attempt < MAX_RETRIES:
                print(
                    f"  Rate limited (429). Retrying in {RETRY_BACKOFF}s...",
                    file=sys.stderr,
                )
                time.sleep(RETRY_BACKOFF)
                continue
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            return False, status, f"HTTP {status}: {body_text}"
        except URLError as exc:
            return False, 0, f"Connection error: {exc.reason}"

    return False, 429, "Rate limited after retry"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Submit URLs to IndexNow endpoints (Bing, Yandex, api.indexnow.org)"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        metavar="URL",
        help="Specific URLs to submit (default: all URLs from sitemap)",
    )
    parser.add_argument(
        "--sitemap-url",
        default=PRODUCTION_SITEMAP_URL,
        help=f"Sitemap source URL (default: {PRODUCTION_SITEMAP_URL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload without sending any requests",
    )
    args = parser.parse_args()

    key = resolve_key()
    print(f"IndexNow key: {mask_key(key)}")

    # Resolve URL list
    if args.urls:
        urls = args.urls
        print(f"Custom URL list: {len(urls)} URL(s)")
    else:
        print(f"Sitemap source: {args.sitemap_url}")
        urls = parse_sitemap_urls(args.sitemap_url)
        print(f"Sitemap URLs parsed: {len(urls)}")

    if not urls:
        print(
            "ERROR: No URLs to submit — sitemap returned 0 URLs (hard fail).",
            file=sys.stderr,
        )
        return 1

    # Enforce IndexNow limit
    if len(urls) > URL_LIMIT:
        print(
            f"WARNING: URL list ({len(urls)}) exceeds IndexNow limit ({URL_LIMIT}). "
            f"Truncating to first {URL_LIMIT} URLs."
        )
        urls = urls[:URL_LIMIT]

    # Validate all URLs belong to expected host
    invalid = [u for u in urls if urlparse(u).netloc not in (HOST, "")]
    if invalid:
        print(
            f"WARNING: {len(invalid)} URL(s) have unexpected host (expected {HOST}). "
            "They will be included but may be rejected by IndexNow."
        )

    payload = build_payload(key, urls)

    if args.dry_run:
        print("\n--- DRY RUN PAYLOAD ---")
        # Mask key and keyLocation in dry-run output
        display_payload = dict(payload)
        display_payload["key"] = mask_key(key)
        display_payload["keyLocation"] = mask_key_location(payload["keyLocation"], key)
        print(json.dumps(display_payload, indent=2, ensure_ascii=False))
        print(f"\nTotal URLs: {len(urls)}")
        print("--- END DRY RUN (no requests sent) ---")
        return 0

    # Submit to all endpoints
    print(f"\nSubmitting {len(urls)} URL(s) to {len(INDEXNOW_ENDPOINTS)} endpoint(s)...")
    all_success = True

    for endpoint in INDEXNOW_ENDPOINTS:
        success, status, message = post_to_endpoint(endpoint, payload)
        status_str = f"[{status}]" if status else ""
        icon = "OK" if success else "FAIL"
        print(f"  {icon} {endpoint} {status_str} {message}")
        if not success:
            all_success = False

    if all_success:
        print("\nAll endpoints accepted the submission.")
        return 0
    else:
        print("\nOne or more endpoints failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

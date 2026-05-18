#!/usr/bin/env python3
"""GSC URL Inspection logger — read-only observability for indexing status.

Polls Google Search Console URL Inspection API (`urlInspection.index.inspect`)
for each URL in the sitemap and writes a snapshot of per-URL index status to a
state JSON file. PR-1 foundation: observability only, no recrawl trigger.

Usage:
    python3 scripts/gsc_inspect.py [--sitemap-url URL] [--state-file PATH]
                                   [--limit N] [--daily-budget N]

Env:
    GSC_SERVICE_ACCOUNT_JSON  Required. Path to a service-account JSON key,
                              or the raw JSON content of the key.
    GSC_SITE_URL              Optional. Default: https://tech.2twodragon.com.
                              Domain Property form: sc-domain:example.com.

See docs/seo/GSC_RECRAWL_SETUP.md for setup. Exits non-zero on auth or
sitemap-fetch failure; per-URL failures are logged but do not abort the run.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Constants

DEFAULT_SITE_URL = "https://tech.2twodragon.com"
DEFAULT_SITEMAP_URL = f"{DEFAULT_SITE_URL}/sitemap.xml"
DEFAULT_STATE_FILE = Path(".omc/state/gsc-queue.json")

GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"

# Per Google quotas: 2000 QPD + 600 QPM per site. Self-cap conservatively.
DAILY_BUDGET_DEFAULT = 500  # leaves 75 % headroom
PER_REQUEST_SLEEP_SEC = 0.15  # ~400 QPM well under 600 QPM cap

# Exponential backoff on 429 / 5xx
MAX_RETRIES = 5
BASE_BACKOFF_SEC = 1.0


# Sitemap parsing


def fetch_sitemap(sitemap_url: str, timeout: int = 30) -> str:
    """Fetch the sitemap XML body."""
    req = Request(sitemap_url, headers={"User-Agent": "gsc-inspect/1.0"})
    with urlopen(req, timeout=timeout) as resp:  # nosec: B310 — trusted URL
        return resp.read().decode("utf-8", errors="replace")


def parse_sitemap_urls(xml_text: str) -> List[str]:
    """Extract <loc> URLs from a sitemap XML body."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"ERROR: sitemap parse failed: {exc}", file=sys.stderr)
        return []

    ns = ""
    if "{" in root.tag:
        ns = root.tag.split("}")[0] + "}"

    urls: List[str] = []
    for url_elem in root.findall(f"{ns}url"):
        loc = url_elem.find(f"{ns}loc")
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


# Authentication


def load_service_account_info(env_value: str) -> Dict[str, Any]:
    """Load service account credentials from env value (path or raw JSON)."""
    stripped = env_value.strip()
    if not stripped:
        raise ValueError("GSC_SERVICE_ACCOUNT_JSON is empty")

    # If the value looks like a JSON object, parse directly
    if stripped.startswith("{"):
        return json.loads(stripped)

    # Otherwise treat as a path
    path = Path(stripped).expanduser()
    if not path.exists():
        raise FileNotFoundError(
            f"GSC_SERVICE_ACCOUNT_JSON path does not exist: {path}"
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_search_console_client(service_account_info: Dict[str, Any]):
    """Build an authenticated searchconsole v1 API client (lazy import)."""
    from google.oauth2 import service_account  # type: ignore[import-not-found]
    from googleapiclient.discovery import build  # type: ignore[import-not-found]

    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=[GSC_SCOPE]
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


# URL Inspection


def _extract_index_status(inspection_result: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the index status fields we care about from the API response."""
    index_status = inspection_result.get("indexStatusResult", {}) or {}
    return {
        "verdict": index_status.get("verdict"),
        "coverage_state": index_status.get("coverageState"),
        "indexing_state": index_status.get("indexingState"),
        "last_crawl_time": index_status.get("lastCrawlTime"),
        "robots_txt_state": index_status.get("robotsTxtState"),
        "page_fetch_state": index_status.get("pageFetchState"),
        "google_canonical": index_status.get("googleCanonical"),
        "user_canonical": index_status.get("userCanonical"),
    }


def inspect_url(client: Any, url: str, site_url: str) -> Dict[str, Any]:
    """Call urlInspection.index.inspect with exponential backoff on 429/5xx."""
    body = {"inspectionUrl": url, "siteUrl": site_url}

    for attempt in range(MAX_RETRIES):
        try:
            response = (
                client.urlInspection().index().inspect(body=body).execute()
            )
            return response.get("inspectionResult", {}) or {}
        except Exception as exc:  # broad: googleapiclient.HttpError + transient
            status = getattr(exc, "resp", None)
            status_code = getattr(status, "status", None) if status else None
            try:
                status_code = int(status_code) if status_code else None
            except (TypeError, ValueError):
                status_code = None

            is_retryable = status_code in (429, 500, 502, 503, 504)
            if not is_retryable or attempt == MAX_RETRIES - 1:
                raise

            wait = BASE_BACKOFF_SEC * (2 ** attempt) + random.uniform(0, 0.5)
            print(
                f"  retry {attempt + 1}/{MAX_RETRIES} after {wait:.1f}s "
                f"(status={status_code})",
                file=sys.stderr,
            )
            time.sleep(wait)

    return {}


# State file IO


def utc_now_iso() -> str:
    """RFC3339 UTC timestamp suitable for JSON state files."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_state(state_file: Path, payload: Dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# Main runner


def categorise(coverage_state: Optional[str]) -> str:
    """Bucket a coverageState string: indexed | discovered | crawled | other."""
    if not coverage_state:
        return "other"
    cs = coverage_state.lower()
    if "submitted and indexed" in cs or "indexed, not submitted" in cs:
        return "indexed"
    if "discovered" in cs:
        return "discovered"
    if "crawled" in cs:
        return "crawled"
    return "other"


def run_inspection(
    urls: Iterable[str],
    client: Any,
    site_url: str,
    daily_budget: int,
    per_request_sleep: float = PER_REQUEST_SLEEP_SEC,
) -> Dict[str, Any]:
    """Iterate URLs, inspect each, return aggregated state dict."""
    results: List[Dict[str, Any]] = []
    totals = {
        "inspected": 0,
        "indexed": 0,
        "discovered_not_indexed": 0,
        "crawled_not_indexed": 0,
        "errors": 0,
    }

    for index, url in enumerate(urls):
        if totals["inspected"] >= daily_budget:
            print(
                f"  daily budget {daily_budget} reached at url #{index}; "
                "stopping early",
                file=sys.stderr,
            )
            break

        entry: Dict[str, Any] = {"url": url, "inspected_at": utc_now_iso()}
        try:
            inspection = inspect_url(client, url, site_url)
            index_status = _extract_index_status(inspection)
            entry.update(index_status)
            totals["inspected"] += 1
            bucket = categorise(index_status.get("coverage_state"))
            if bucket == "indexed":
                totals["indexed"] += 1
            elif bucket == "discovered":
                totals["discovered_not_indexed"] += 1
            elif bucket == "crawled":
                totals["crawled_not_indexed"] += 1
        except Exception as exc:
            entry["error"] = str(exc)[:240]
            totals["errors"] += 1
            print(f"  ERROR inspecting {url}: {exc}", file=sys.stderr)

        results.append(entry)
        if per_request_sleep > 0:
            time.sleep(per_request_sleep)

    return {
        "schema_version": 1,
        "generated_at": utc_now_iso(),
        "site_url": site_url,
        "totals": totals,
        "urls": results,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sitemap-url", default=DEFAULT_SITEMAP_URL,
                        help=f"sitemap URL (default: {DEFAULT_SITEMAP_URL})")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE), type=Path,
                        help=f"output state path (default: {DEFAULT_STATE_FILE})")
    parser.add_argument("--site-url",
                        default=os.environ.get("GSC_SITE_URL", DEFAULT_SITE_URL),
                        help="GSC siteUrl (URL or sc-domain:example.com form)")
    parser.add_argument("--limit", type=int, default=0,
                        help="cap inspected URLs (0 = no cap)")
    parser.add_argument("--daily-budget", type=int, default=DAILY_BUDGET_DEFAULT,
                        help=f"self-cap per day (default: {DAILY_BUDGET_DEFAULT}, "
                             f"GSC cap: 2000)")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    env_creds = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not env_creds:
        print(
            "ERROR: GSC_SERVICE_ACCOUNT_JSON env var not set. "
            "Provide either a path to a service-account key JSON file or the "
            "raw JSON content. See docs/seo/GSC_RECRAWL_SETUP.md.",
            file=sys.stderr,
        )
        return 1

    try:
        sa_info = load_service_account_info(env_creds)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: failed to load service account credentials: {exc}",
              file=sys.stderr)
        return 1

    try:
        client = build_search_console_client(sa_info)
    except Exception as exc:
        print(f"ERROR: failed to build Search Console client: {exc}",
              file=sys.stderr)
        return 1

    try:
        sitemap_xml = fetch_sitemap(args.sitemap_url)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"ERROR: failed to fetch sitemap {args.sitemap_url}: {exc}",
              file=sys.stderr)
        return 1

    urls = parse_sitemap_urls(sitemap_xml)
    if args.limit and args.limit > 0:
        urls = urls[: args.limit]

    if not urls:
        print(f"ERROR: no URLs found in sitemap {args.sitemap_url}",
              file=sys.stderr)
        return 1

    print(f"inspecting {len(urls)} URLs (site={args.site_url}, "
          f"budget={args.daily_budget})", file=sys.stderr)

    state = run_inspection(
        urls=urls,
        client=client,
        site_url=args.site_url,
        daily_budget=args.daily_budget,
    )

    write_state(args.state_file, state)
    t = state["totals"]
    summary = (
        f"inspected={t['inspected']} indexed={t['indexed']} "
        f"discovered={t['discovered_not_indexed']} "
        f"crawled={t['crawled_not_indexed']} errors={t['errors']}"
    )
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Normalize BlogWatcher payload into collected_news.json format."""

import argparse
import ipaddress
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests


def _allowed_hosts() -> List[str]:
    """Optional strict host allowlist from BLOGWATCHER_ALLOWED_HOSTS (comma-sep).

    Empty → no host restriction (only the unconditional private-IP block below
    applies). Set it in the workflow to the blogwatcher feed's host to add
    feed-poisoning defense-in-depth.
    """
    raw = os.getenv("BLOGWATCHER_ALLOWED_HOSTS", "")
    return [h.strip().lower() for h in raw.split(",") if h.strip()]


def _resolves_to_public(host: str) -> bool:
    """True only if EVERY resolved address for *host* is a public IP.

    Blocks SSRF to loopback / private / link-local (169.254.169.254 metadata) /
    reserved / multicast targets. Numeric IP hosts resolve without a DNS query.
    """
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    addrs = {info[4][0] for info in infos}
    if not addrs:
        return False
    for addr in addrs:
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False
    return True


def validate_fetch_url(url: str, allowed_hosts: Optional[List[str]] = None):
    """Validate a payload URL before fetching it (SSRF / feed-poisoning guard).

    - scheme must be http/https (blocks file://, gopher://, etc.)
    - if an allowlist is provided, host must match it (exact or subdomain)
    - host must resolve only to public IPs (blocks internal/metadata SSRF)

    Returns the parsed URL on success; raises ValueError otherwise.
    """
    allowed = allowed_hosts if allowed_hosts is not None else _allowed_hosts()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Refusing non-http(s) payload URL scheme: {parsed.scheme!r}")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("Payload URL has no host")
    if allowed and not any(host == h or host.endswith("." + h) for h in allowed):
        raise ValueError(
            f"Payload URL host {host!r} not in BLOGWATCHER_ALLOWED_HOSTS allowlist"
        )
    if not _resolves_to_public(host):
        raise ValueError(
            f"Refusing payload URL that resolves to a non-public address: {host!r}"
        )
    return parsed


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json_string(value: str) -> Optional[Any]:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _extract_candidate(payload: Any) -> Optional[Dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return payload

        for key in (
            "collected_news",
            "collected_news_json",
            "payload",
            "data",
            "blogwatcher",
            "news",
        ):
            if key in payload:
                candidate = payload[key]
                if isinstance(candidate, str):
                    candidate = _load_json_string(candidate)
                result = _extract_candidate(candidate)
                if result:
                    return result

    if isinstance(payload, list):
        return {"items": payload}

    return None


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = payload.get("items", []) if isinstance(payload.get("items"), list) else []
    normalized = dict(payload)
    normalized["items"] = items
    if "total_items" not in normalized:
        normalized["total_items"] = len(items)
    if "collected_at" not in normalized:
        normalized["collected_at"] = _now_iso()
    return normalized


def _load_payload(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        return json.loads(input_path.read_text(encoding="utf-8"))

    if args.payload_json:
        payload = _load_json_string(args.payload_json)
        if payload is None:
            raise ValueError("Invalid payload JSON")
        return payload

    if args.payload_url:
        validate_fetch_url(args.payload_url)
        # allow_redirects=False so a public URL cannot 3xx-redirect into an
        # internal target after the host check (redirect-based SSRF).
        response = requests.get(args.payload_url, timeout=30, allow_redirects=False)
        if response.is_redirect or response.is_permanent_redirect:
            raise ValueError(
                "Payload URL returned a redirect; refusing to follow (SSRF guard). "
                "Point BLOGWATCHER_NEWS_URL at the final URL."
            )
        response.raise_for_status()
        return response.json()

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize BlogWatcher payload to collected_news.json"
    )
    parser.add_argument("--input", help="Input JSON file")
    parser.add_argument("--output", default="_data/collected_news.json")
    parser.add_argument(
        "--payload-json",
        default=os.getenv("BLOGWATCHER_PAYLOAD", "").strip(),
    )
    parser.add_argument(
        "--payload-url",
        default=os.getenv("BLOGWATCHER_NEWS_URL", "").strip(),
    )

    args = parser.parse_args()

    payload = _load_payload(args)
    if payload is None:
        print("No BlogWatcher payload provided")
        return 0

    candidate = _extract_candidate(payload)
    if candidate is None:
        raise ValueError("Unsupported BlogWatcher payload format")

    normalized = _normalize_payload(candidate)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Normalized BlogWatcher payload -> {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}")
        raise

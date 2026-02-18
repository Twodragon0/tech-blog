#!/usr/bin/env python3
"""Normalize BlogWatcher payload into collected_news.json format."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests


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
        response = requests.get(args.payload_url, timeout=30)
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

#!/usr/bin/env python3
"""Convert the 12 pinned L22 digest covers (4-29, 4-30, 5-01..5-10) to L20.

Same logic as scripts/convert_feb_digest_to_l20.py but with a fixed date list.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DIGEST_DIR = REPO / "_data" / "digest_covers"
L20_DIR = REPO / "_data" / "l20_covers"

TARGETS = [
    "2026-04-29",
    "2026-04-30",
    "2026-05-01",
    "2026-05-02",
    "2026-05-03",
    "2026-05-04",
    "2026-05-05",
    "2026-05-06",
    "2026-05-07",
    "2026-05-08",
    "2026-05-09",
    "2026-05-10",
]

VISUAL_MAP = {
    "lock_cve": "cve_chain",
    "kernel_lpe": "cve_chain",
    "network_nodes": "hub_spoke",
    "shield": "hub_spoke",
    "senate_columns": "hub_spoke",
    "router_mesh": "hub_spoke",
    "botnet_p2p": "hub_spoke",
    "hub_spoke": "hub_spoke",
    "cloud_k8s": "container_escape",
    "code_bars": "code_injection",
    "browser_cve": "code_injection",
    "bar_graph": "data_exfil",
    "wallet_forensic": "data_exfil",
    "price_chart": "data_exfil",
    "ad_fraud": "data_exfil",
    "data_exfil": "data_exfil",
    "supply_chain": "supply_chain_pipe",
}

THEME_MAP = {
    "red": "red",
    "amber": "amber",
    "yellow": "amber",
    "orange": "amber",
    "blue": "blue",
    "purple": "blue",
    "violet": "blue",
    "pink": "blue",
    "green": "blue",
    "teal": "blue",
    "cyan": "blue",
}


def pick_visual(band: dict) -> str:
    kind = (band.get("visual") or {}).get("kind", "")
    headline = (band.get("headline") or "").lower()
    label = (band.get("label") or "").lower()
    metric = (band.get("metric") or "").lower()
    primary = " ".join([headline, label])
    full = " ".join([headline, label, metric])

    if any(k in primary for k in ("cve-", "rce", "0-day", "zero-day", "zero day", "kernel lpe", "auth bypass")):
        return "cve_chain"
    if any(k in primary for k in ("ransomware", "wiper", "lockbit", "ransom note")):
        return "ransomware_lock"
    if any(k in primary for k in ("supply chain", "npm", "pypi", "pkg.go.dev", "package", "hijack", "site hijack")):
        return "supply_chain_pipe"
    if any(k in primary for k in ("ai agent", "agentic", "llm", "claude code", "gpt", "model context", "ai phishing", "ai threat")):
        return "ai_agent_funnel"
    if any(k in primary for k in ("k8s", "kubernetes", "container", "docker", "azure", "aws", "cloud")):
        return "container_escape"
    if any(k in primary for k in ("data breach", "data exfil", "exfil", "data theft", "leak", "trojan", "stealer", "credential")):
        return "data_exfil"
    if any(k in primary for k in ("injection", "xss", "sqli", "backdoor", "rat", "worm", "botnet")):
        return "code_injection"
    if "ransomware" in full:
        return "ransomware_lock"
    if "supply chain" in full:
        return "supply_chain_pipe"

    return VISUAL_MAP.get(kind, "hub_spoke")


def theme_of(band: dict) -> str:
    t = (band.get("theme") or "").lower().strip()
    return THEME_MAP.get(t, "blue")


def band_to_l20_block(band: dict, index: str, is_hero: bool) -> dict:
    badge = band.get("badge") or {}
    headline = band.get("headline") or band.get("label") or "Security Update"
    label = band.get("label") or ""
    metric = (band.get("metric") or "").strip()
    detail = (band.get("detail") or "").strip()
    metric_b = (band.get("metric_b") or "").strip()

    raw_sub = detail or metric or headline
    parts = [p.strip() for p in raw_sub.split(":") if p.strip()]
    if parts:
        candidates = [p for p in parts if len(p) > 18]
        subheadline = (candidates[0] if candidates else parts[0]).strip()
    else:
        subheadline = headline
    subheadline = subheadline.replace(" : ", " - ").strip()
    if len(subheadline) > 78:
        subheadline = subheadline[:75].rstrip(" ,;:") + "..."

    block = {
        "tag": label.upper()[:24] if label else "HIGH",
        "index": index,
        "theme": theme_of(band),
        "visual": pick_visual(band),
        "headline": headline,
        "subheadline": subheadline,
        "kpi_value": str(badge.get("value", "")) or "VULN",
        "kpi_label": str(badge.get("label", "")) or "DETECT",
        "kpi_sub": str(badge.get("sub", "")) or "patch",
    }

    if is_hero:
        action = metric_b or "PATCH + ROTATE CREDENTIALS"
        if len(action) > 48:
            first = action.split(":")[0].strip()
            action = first[:45].rstrip(" ,;") + "..."
        block["action"] = action.upper()
    return block


def convert(date: str) -> tuple[Path, dict] | None:
    spec_path = DIGEST_DIR / f"{date}.yml"
    if not spec_path.exists():
        print(f"[skip] no spec for {date}")
        return None
    with spec_path.open() as f:
        src = yaml.safe_load(f)
    bands = src.get("bands") or []
    if len(bands) < 3:
        print(f"[skip] {date}: needs 3 bands")
        return None

    slug = str(src.get("slug", "")).strip()
    if not slug:
        print(f"[skip] {date}: missing slug")
        return None

    title = src.get("title") or f"Weekly digest {date}"

    year, month, day = date.split("-")
    date_str = f"{year}.{month}.{day}"
    url = f"https://tech.2twodragon.com/posts/{year}/{month}/{day}/{slug}/"

    l20 = {
        "date": date,
        "slug": slug,
        "date_str": date_str,
        "post_title": title,
        "url": url,
        "hero": band_to_l20_block(bands[0], "01", is_hero=True),
        "top_right": band_to_l20_block(bands[1], "02", is_hero=False),
        "bottom_right": band_to_l20_block(bands[2], "03", is_hero=False),
    }
    target = L20_DIR / f"{date}-{slug}.yml"
    return target, l20


def main():
    written = 0
    for date in TARGETS:
        result = convert(date)
        if not result:
            continue
        target, l20 = result
        if target.exists():
            print(f"[overwrite] {target.name}")
        with target.open("w") as f:
            yaml.safe_dump(l20, f, sort_keys=False, default_flow_style=False, allow_unicode=False, width=120)
        print(f"[ok] wrote {target.name}")
        written += 1
    print(f"\n[done] {written}/{len(TARGETS)} specs written")


if __name__ == "__main__":
    main()

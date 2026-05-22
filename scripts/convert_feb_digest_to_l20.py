#!/usr/bin/env python3
"""Convert 2026-02 _data/digest_covers/*.yml (L22 Stacked Bands) to L20 Hero+2-Card.

Mapping:
  band[0] -> hero (with action)
  band[1] -> top_right
  band[2] -> bottom_right

Visual kind L22 -> L20:
  lock_cve, kernel_lpe                  -> cve_chain
  network_nodes, shield, senate_columns,
  router_mesh, botnet_p2p, hub_spoke    -> hub_spoke
  cloud_k8s                             -> container_escape
  code_bars, browser_cve                -> code_injection
  bar_graph, wallet_forensic,
  price_chart, ad_fraud, data_exfil     -> data_exfil
  supply_chain                          -> supply_chain_pipe
  (ransomware band heuristic)           -> ransomware_lock
  (ai/llm/agent band heuristic)         -> ai_agent_funnel

Theme remapping (drop unsupported L22 themes):
  green/teal/cyan      -> blue
  purple/violet/pink   -> blue
  red, amber, blue     -> kept
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parent.parent
DIGEST_DIR = REPO / "_data" / "digest_covers"
L20_DIR = REPO / "_data" / "l20_covers"
POSTS_DIR = REPO / "_posts"


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
    """Pick L20 hero visual.

    Priority: prefer matching on headline/label (specific) over detail (generic).
    """
    kind = (band.get("visual") or {}).get("kind", "")
    headline = (band.get("headline") or "").lower()
    label = (band.get("label") or "").lower()
    metric = (band.get("metric") or "").lower()
    primary = " ".join([headline, label])
    full = " ".join([headline, label, metric])

    # CVE/RCE/kernel takes priority over ransomware mention in detail
    if any(k in primary for k in ("cve-", "rce", "0-day", "zero-day", "zero day", "kernel lpe")):
        return "cve_chain"
    if any(k in primary for k in ("ransomware", "lockbit", "ransom note")):
        return "ransomware_lock"
    if any(k in primary for k in ("supply chain", "go.sum", "pypi", "npm", "pkg.go.dev", "package backdoor", "dependency")):
        return "supply_chain_pipe"
    if any(k in primary for k in ("ai agent", "agentic", "llm", "claude code", "gpt", "model context", "owasp llm")):
        return "ai_agent_funnel"
    if any(k in primary for k in ("k8s", "kubernetes", "container", "docker", "pod escape", "namespace")):
        return "container_escape"
    if any(k in primary for k in ("data exfil", "exfil", "data leak", "data theft", "wallet", "btc", "usdt", "blockchain")):
        return "data_exfil"
    if any(k in primary for k in ("injection", "xss", "sqli", "backdoor", "rat")):
        return "code_injection"
    # secondary pass on full text
    if "ransomware" in full and "cve" not in primary:
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

    # Subheadline: prefer detail (most descriptive), strip colon-separated tags.
    # The renderer caps at ~54 chars (top_right/bottom_right) or 62 (hero), so we trim conservatively.
    raw_sub = detail or metric or headline
    # remove leading "Term : " tags repeated from metric, keep the descriptive clause
    parts = [p.strip() for p in raw_sub.split(":") if p.strip()]
    if parts:
        # pick the longest descriptive clause that isn't just keywords
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
        # short to fit hero action slug
        if len(action) > 48:
            # take first clause before " : "
            first = action.split(":")[0].strip()
            action = first[:45].rstrip(" ,;") + "..."
        block["action"] = action.upper()
    return block


def find_post_file(date: str, slug: str) -> Path | None:
    target = f"{date}-{slug}.md"
    p = POSTS_DIR / target
    if p.exists():
        return p
    # fallback fuzzy match
    matches = list(POSTS_DIR.glob(f"{date}-*.md"))
    for m in matches:
        if slug.lower() in m.name.lower():
            return m
    return None


def post_title(post: Path | None, fallback: str, date: str) -> str:
    """Use the digest_cover's English title (English only). Renderer strips Hangul anyway."""
    return fallback or f"Weekly digest {date}"


def convert(spec_path: Path) -> tuple[Path, dict] | None:
    with spec_path.open() as f:
        src = yaml.safe_load(f)
    bands = src.get("bands") or []
    if len(bands) < 3:
        print(f"[skip] {spec_path.name}: needs 3 bands, got {len(bands)}")
        return None

    date = str(src.get("date", "")).strip()
    slug = str(src.get("slug", "")).strip()
    if not (date and slug):
        print(f"[skip] {spec_path.name}: missing date/slug")
        return None

    post = find_post_file(date, slug)
    title = post_title(post, src.get("title", f"Weekly digest {date}"), date)

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
    targets = sorted(DIGEST_DIR.glob("2026-02-*.yml"))
    if not targets:
        print("[error] no 2026-02 digest covers found")
        sys.exit(1)

    written = 0
    for src in targets:
        result = convert(src)
        if not result:
            continue
        target, l20 = result
        if target.exists():
            print(f"[skip] exists: {target.name}")
            continue
        with target.open("w") as f:
            yaml.safe_dump(l20, f, sort_keys=False, default_flow_style=False, allow_unicode=False, width=120)
        print(f"[ok] wrote {target.name}")
        written += 1
    print(f"\n[done] converted {written}/{len(targets)} specs")


if __name__ == "__main__":
    main()

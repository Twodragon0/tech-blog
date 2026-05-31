#!/usr/bin/env python3
"""Track A — regenerate 14 covers across 6 target dates as L22 stacked-bands.

Bypasses ``_is_digest_post()`` so non-digest standalone posts (KARA, KISA,
Cloud Trends, etc.) still get the rich 3-band cover the user requested.

For each target post:
  1. Read frontmatter (title, filename, excerpt, content)
  2. Call ``generate_l22_digest_svg`` directly (forced L22 path)
  3. Build 5 raster variants (og.png/webp/avif + card.webp/avif)

Usage:
    python3 scripts/regen_track_a_covers.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.generate_post_images import generate_l22_digest_svg  # noqa: E402

ASSETS = REPO / "assets" / "images"
OG_W, OG_H = 1200, 630
CARD_W, CARD_H = 525, 295

TARGETS = [
    "2026-01-22-AWS_GCP_Cloud_Updates_January_2026_EC2_G7e_X8i_Bangkok_Region_European_Sovereign_Cloud",
    "2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide",
    "2026-01-22-Cloud_Security_Trends_January_2026_Kubernetes_82_Percent_Production_VS_Code_Threats_CNCF_Survey",
    "2026-01-22-KARA_Ransomware_Trends_Report_2025_Q3_Analysis_SK_Shieldus_EQST",
    "2026-01-22-KISA_Security_Advisory_Ransomware_Prevention_Linux_Rootkit_Detection_Guide_Analysis",
    "2026-01-22-Security_Vendor_Blog_Weekly_Review",
    "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin",
    "2026-02-09-Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic",
    "2026-02-10-AI_Cloud_Digest_Meta_Prometheus_Google_OTLP_AWS",
    "2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin",
    "2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack",
    "2026-02-16-Daily_Tech_Digest_RSS_Roundup",
    "2026-02-25-Claude_Code_OpenCode_Best_Practices",
    "2026-02-25-Tech_Security_Weekly_Digest_AI_Malware_Ransomware_LLM",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)
TITLE_RE = re.compile(r"^title:\s*(.+?)$", re.M)
EXCERPT_RE = re.compile(r"^excerpt:\s*(.+?)$", re.M)
IMAGE_RE = re.compile(r"^image:\s*(.+?)$", re.M)


def read_post(slug: str) -> dict:
    """Read post frontmatter + body. Returns dict for generate_l22_digest_svg."""
    path = REPO / "_posts" / f"{slug}.md"
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"no frontmatter: {slug}")
    fm, body = m.group(1), m.group(2)

    def _grab(rx: re.Pattern[str]) -> str:
        match = rx.search(fm)
        if not match:
            return ""
        return match.group(1).strip().strip('"').strip("'")

    image = _grab(IMAGE_RE)
    return {
        "title": _grab(TITLE_RE),
        "excerpt": _grab(EXCERPT_RE),
        "filename": f"{slug}.md",
        "category": "security",
        "tags": ["security"],
        "content": body,
        "image": image,
    }


def build_rasters(svg: Path) -> None:
    from PIL import Image  # type: ignore

    base = svg.with_suffix("").name
    og_png = ASSETS / f"{base}_og.png"
    subprocess.run(
        ["rsvg-convert", "-w", str(OG_W), "-h", str(OG_H), "-o", str(og_png), str(svg)],
        check=True,
        capture_output=True,
    )
    with Image.open(og_png) as og:
        og.load()
        og.save(ASSETS / f"{base}_og.webp", "WEBP", quality=80)
        og.save(ASSETS / f"{base}_og.avif", "AVIF", quality=60)
        card = og.resize((CARD_W, CARD_H), Image.LANCZOS)
        card.save(ASSETS / f"{base}_card.webp", "WEBP", quality=80)
        card.save(ASSETS / f"{base}_card.avif", "AVIF", quality=60)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ok = fail = 0
    for slug in TARGETS:
        post_info = read_post(slug)
        # Resolve output SVG from image: frontmatter field; fall back to slug.svg
        img = post_info.get("image", "") or ""
        if img.startswith("/assets/images/"):
            svg_path = REPO / img.lstrip("/")
        else:
            svg_path = ASSETS / f"{slug}.svg"

        if args.dry_run:
            print(f"WOULD regen {svg_path.name}  ({post_info['title'][:60]})")
            ok += 1
            continue

        try:
            generated = generate_l22_digest_svg(post_info, svg_path)
            if not generated:
                print(f"[fail-gen] {slug}")
                fail += 1
                continue
            build_rasters(svg_path)
            print(f"[ok] {svg_path.name}")
            ok += 1
        except Exception as exc:
            print(f"[fail] {slug}: {exc}")
            fail += 1

    print(f"\n[done] {ok}/{len(TARGETS)} ({fail} failed)")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

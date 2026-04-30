#!/usr/bin/env python3
"""Hand-curate 2026-02-25 weekly-digest SVG with full English content.

Replaces the bulk-generated L22 ultra SVG (which had Korean topic strings
and ``...`` truncation) with explicit, hand-written English bands so the
cover matches the design language used by other Tech Security Weekly
Digest posts.

Top items selected from the post body:
  red   - GitHub Codespaces RoguePilot: Copilot abuse leaks GITHUB_TOKEN
          (The Hacker News, Critical)
  amber - UAC-0050 phishing: RMS malware against EU financial-sector
          legal counsel (The Hacker News, High)
  green - Malicious Next.js repo C2 supply-chain attack on developers
          (Microsoft Security Blog, Critical -> normalised to green/info)

Usage::

    python3 scripts/upgrade_2026_02_25_to_ultra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"


def cfg_2026_02_25() -> dict:
    """Feb 25: Codespaces RoguePilot, UAC-0050 RMS phishing, Next.js C2 chain."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="FE25",
        aria="GitHub Codespaces RoguePilot Copilot token leak, UAC-0050 RMS malware against EU financial legal counsel, malicious Next.js repository C2 supply chain attack",
        title="2026-02-25: Codespaces RoguePilot, UAC-0050 RMS, Next.js C2 chain",
        url="https://tech.2twodragon.com/security/2026/02/25/Tech_Security_Weekly_Digest_AI_Malware_Ransomware_LLM.html",
        bands=[
            dict(
                theme="red",
                label="COPILOT TOKEN LEAK",
                headline="Codespaces RoguePilot",
                metric="GITHUB_TOKEN exfil : prompt-injection",
                detail="Hidden instruction in repo : Copilot resolves and leaks env GITHUB_TOKEN : full repo read-write",
                metric_b="OWASP A06 LLM injection : least-privilege scope on Copilot",
                detail_b="Disable shared instructions : token rotation : CSP egress allowlist for Codespaces sessions",
                badge_value="RCE", badge_label="IMPACT", badge_sub="token exfil",
                mini_value="GH", mini_label="VENDOR", mini_sub="Codespaces",
                mini2_value="LLM", mini2_label="VECTOR", mini2_sub="prompt inj",
                visual=l22.v_browser_cve(500, 105, red["accent"], red["soft"], label="COPILOT"),
            ),
            dict(
                theme="amber",
                label="FIN SECTOR PHISHING",
                headline="UAC-0050 RMS Malware",
                metric="EU legal counsel : RMS RAT drop",
                detail="Spear-phish to financial-sector lawyers : RMS remote-management trojan : credential + session theft",
                metric_b="MITRE T1566.001 spear-phishing attachment + T1219 remote access tool",
                detail_b="Block RMS hashes : EDR rule for RemoteUtilities CLI : MFA on legal mailbox enforce",
                badge_value="UAC", badge_label="ACTOR", badge_sub="0050 group",
                mini_value="RMS", mini_label="MALWARE", mini_sub="RAT",
                mini2_value="EU", mini2_label="REGION", mini2_sub="finance",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="PHISH"),
            ),
            dict(
                theme="green",
                label="DEV SUPPLY CHAIN",
                headline="Next.js Repo C2",
                metric="Malicious Next.js repo : devs targeted",
                detail="Microsoft Security flags fake Next.js GitHub repo : install-time script reaches C2 : workstation foothold",
                metric_b="Pre-clone scan : npm audit signature : SBOM provenance verify",
                detail_b="Block install scripts in npm config : repo allowlist : pin commit SHA in CI/CD : SLSA L3 target",
                badge_value="C2", badge_label="STAGE", badge_sub="post-clone",
                mini_value="NX", mini_label="LURE", mini_sub="Next.js",
                mini2_value="MSF", mini2_label="REPORT", mini2_sub="Microsoft",
                visual=l22.v_code_bars(500, 525, green["accent"], green["soft"], caption="DEV CHAIN"),
            ),
        ],
    )


SPECS = [
    ("2026-02-25-Tech_Security_Weekly_Digest_AI_Malware_Ransomware_LLM.svg", cfg_2026_02_25),
]


def main() -> None:
    for filename, cfg_fn in SPECS:
        cfg = cfg_fn()
        svg = l22.render_bands_svg(
            sfx=cfg["sfx"],
            aria=cfg["aria"],
            title=cfg["title"],
            url=cfg["url"],
            bands_cfg=cfg["bands"],
            tier="ultra",
        )
        out = ASSETS / filename
        out.write_text(svg, encoding="utf-8")
        size_kb = out.stat().st_size / 1024
        line_count = svg.count("\n") + 1
        print(f"  wrote {filename}: {line_count} lines / {size_kb:.1f} KB")


if __name__ == "__main__":
    main()

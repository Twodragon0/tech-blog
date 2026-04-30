#!/usr/bin/env python3
"""Upgrade 2026-04-26 weekly-digest SVG to L22 ultra tier.

Mirrors the structure of upgrade_2026_04_27_29_to_ultra.py.
Each band is hand-curated from the post's top headlines so the design
stays consistent with the rest of the late-April family.

Top items selected for the cover (per the 2026-04-26 post body):
  red   - 'fast16' pre-Stuxnet Lua malware targeting engineering software
          (The Hacker News, High severity)
  amber - 'Snow' malware distributed via Microsoft Teams
          (BleepingComputer, High severity)
  green - Anthropic Mythos forces crypto industry to rethink AI security
          (CoinDesk, Medium - AI x blockchain pivot)

Usage::

    python3 scripts/upgrade_2026_04_26_to_ultra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"


def cfg_2026_04_26() -> dict:
    """Apr 26: fast16 pre-Stuxnet Lua, MS Teams Snow malware, Anthropic Mythos."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="AP26",
        aria="fast16 pre-Stuxnet Lua malware on engineering software, Snow malware via Microsoft Teams, Anthropic Mythos AI forcing crypto security rethink",
        title="2026-04-26: fast16 Lua malware, Teams Snow, Anthropic Mythos",
        url="https://tech.2twodragon.com/security/2026/04/26/Tech_Security_Weekly_Digest_Malware_Threat_AWS_Go.html",
        bands=[
            dict(
                theme="red",
                label="OT SABOTAGE FRAMEWORK",
                headline="fast16 Pre-Stuxnet Lua",
                metric="2005 origin : engineering CAE/CAD",
                detail="Lua plugin tampering : numeric calc poisoning : OT logic-bomb : SentinelOne attribution",
                metric_b="DevSecOps risk : Lua scripts in CI/CD + Nginx + Redis automation",
                detail_b="Sign + hash all build scripts : SBOM Lua deps : runtime calc range checks for OT",
                badge_value="2005", badge_label="ORIGIN", badge_sub="pre-Stuxnet",
                mini_value="Lua", mini_label="VECTOR", mini_sub="plugin",
                mini2_value="OT", mini2_label="TARGET", mini2_sub="engineering",
                visual=l22.v_code_bars(500, 105, red["accent"], red["soft"], caption="LUA TAMPER"),
            ),
            dict(
                theme="amber",
                label="COLLAB PLATFORM ABUSE",
                headline="Teams Snow Malware",
                metric="Microsoft Teams : delivery vector",
                detail="Threat actor abuses Teams chat : Snow loader drop : EDR-blind collab channel",
                metric_b="OWASP A06 : risky 3rd-party trust : Teams external federation",
                detail_b="Disable external Teams chat by default : EDR Teams cache rules : message-link sandbox",
                badge_value="Teams", badge_label="VECTOR", badge_sub="collab",
                mini_value="Snow", mini_label="LOADER", mini_sub="stage1",
                mini2_value="EDR", mini2_label="GAP", mini2_sub="collab blind",
                visual=l22.v_browser_cve(500, 315, amber["accent"], amber["soft"], label="TEAMS"),
            ),
            dict(
                theme="green",
                label="AI x CRYPTO SECURITY",
                headline="Anthropic Mythos Pivot",
                metric="Crypto industry : security rethink",
                detail="Mythos model challenges Web3 trust assumptions : AI-aided audit + adversarial prompt safety",
                metric_b="Prompt-injection defense + signed model artefacts : SLSA-style provenance",
                detail_b="AI-assisted Solidity SAST : pre-commit secret scan : LLM red-team gate before deploy",
                badge_value="MTH", badge_label="MODEL", badge_sub="Mythos",
                mini_value="Web3", mini_label="SCOPE", mini_sub="audit AI",
                mini2_value="ANT", mini2_label="VENDOR", mini2_sub="Anthropic",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="AI SEC"),
            ),
        ],
    )


SPECS = [
    ("2026-04-26-Tech_Security_Weekly_Digest_Malware_Threat_AWS_Go.svg", cfg_2026_04_26),
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

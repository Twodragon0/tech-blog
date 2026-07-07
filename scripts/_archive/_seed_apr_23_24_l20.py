#!/usr/bin/env python3
"""Seed L20 specs for 2026-04-23 + 2026-04-24 weekly digests."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-04-23", "Tech_Security_Weekly_Digest_AI_Docker_Go_API",
     "Weekly digest 2026-04-23: malicious KICS Docker image + VS Code ext, self-prop npm worm, BYOVD",
     {"tag":"KICS IMG","theme":"red","visual":"supply_chain_pipe","headline":"Malicious KICS Docker",
      "subheadline":"Malicious KICS Docker image and VS Code extension distribute developer-token theft",
      "kpi_value":"KICS","kpi_label":"IMG","kpi_sub":"mal",
      "action":"BLOCK IMG + AUDIT EXT REGISTRY"},
     {"tag":"NPM WORM","theme":"amber","visual":"code_injection","headline":"Self-Prop npm Worm",
      "subheadline":"Self-propagating supply-chain worm hijacks npm packages to steal dev tokens",
      "kpi_value":"WORM","kpi_label":"NPM","kpi_sub":"tok"},
     {"tag":"BYOVD","theme":"blue","visual":"cve_chain","headline":"BYOVD EDR Bypass",
      "subheadline":"BYOVD families abuse signed drivers to disable EDR telemetry sensors",
      "kpi_value":"BYO","kpi_label":"VD","kpi_sub":"EDR"}),

    ("2026-04-24", "Tech_Security_Weekly_Digest_Malware_AI_Go_Threat",
     "Weekly digest 2026-04-24: UNC6692 Teams campaign, Bitwarden CLI Checkmarx supply, BYOVD",
     {"tag":"UNC6692","theme":"red","visual":"data_exfil","headline":"UNC6692 Teams Targeted",
      "subheadline":"UNC6692 targets IT staff via Microsoft Teams for initial-access payloads",
      "kpi_value":"UNC","kpi_label":"6692","kpi_sub":"MS",
      "action":"HARDEN TEAMS + AUDIT INBOUND"},
     {"tag":"BITWARDEN CLI","theme":"amber","visual":"supply_chain_pipe","headline":"Bitwarden CLI Supply Hit",
      "subheadline":"Bitwarden CLI compromised in Checkmarx supply-chain campaign vector",
      "kpi_value":"BW","kpi_label":"CLI","kpi_sub":"sup"},
     {"tag":"BYOVD","theme":"blue","visual":"cve_chain","headline":"BYOVD Driver Sideload",
      "subheadline":"BYOVD vulnerable-driver sideload campaigns continue across enterprises",
      "kpi_value":"BYO","kpi_label":"VD","kpi_sub":"side"}),
]


def emit() -> None:
    for date, slug, title, hero, tr, br in SPECS:
        hero = {**hero, "index": "01"}
        tr = {**tr, "index": "02"}
        br = {**br, "index": "03"}
        year, month, day = date.split("-")
        block = {
            "date": date,
            "slug": slug,
            "date_str": f"{year}.{month}.{day}",
            "post_title": title,
            "url": f"https://tech.2twodragon.com/posts/{year}/{month}/{day}/{slug}/",
            "hero": hero,
            "top_right": tr,
            "bottom_right": br,
        }
        target = OUT / f"{date}-{slug}.yml"
        with target.open("w") as f:
            yaml.safe_dump(block, f, sort_keys=False, default_flow_style=False, allow_unicode=False, width=120)
        print(f"[ok] {target.name}")


if __name__ == "__main__":
    emit()

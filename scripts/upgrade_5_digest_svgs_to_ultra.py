#!/usr/bin/env python3
"""Upgrade 5 headline-grade Mar 16-31 digest SVGs to ultra tier.

Reads each target's existing content (themes, headlines, badges,
visuals) and re-emits via ``render_bands_svg(..., tier="ultra")`` so the
output matches the visual richness of the 2026-04-21 reference.

Usage::

    python3 scripts/upgrade_5_digest_svgs_to_ultra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"


def _v(name: str, theme: dict, **kwargs) -> str:
    """Look up visual function by name and call it with theme accents."""
    fn = getattr(l22, name)
    return fn(500, kwargs.pop("yc"), theme["accent"], theme["soft"], **kwargs)


def cfg_2026_03_19() -> dict:
    """Mar 19: NK $300M IT workers, Cisco FMC CVE-2026-20131, Telnetd CVE-2026-32746."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MA05",
        aria="North Korea IT workers sanctioned, Cisco FMC zero-day, Telnetd root RCE",
        title="2026-03-19: NK IT workers, Cisco FMC, Telnetd RCE",
        url="https://tech.2twodragon.com/security/2026/03/19/Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.html",
        bands=[
            dict(
                theme="red",
                label="NATION STATE",
                headline="North Korea IT Workers",
                metric="OFAC sanction : 12 countries",
                detail="$300M revenue ring : front companies : crypto laundering : Lazarus front",
                metric_b="Indictment : 14 individuals + 4 entities",
                detail_b="Front-company hiring : remote-IT-staffing fraud : sanctions evasion",
                badge_value="$300M", badge_label="REVENUE", badge_sub="annual",
                mini_value="14", mini_label="ACTORS", mini_sub="indicted",
                mini2_value="12", mini2_label="COUNTRIES", mini2_sub="affected",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="DPRK"),
            ),
            dict(
                theme="amber",
                label="EDGE APPLIANCE 0-DAY",
                headline="Cisco FMC Pre-Auth RCE",
                metric="CVE-2026-20131 : CVSS 9.8",
                detail="Firepower Mgmt Center : unauth RCE : exploited in wild : mitigation only",
                metric_b="Active exploit : KEV catalog flagged",
                detail_b="No patch yet : mitigation by ACL + management plane isolation",
                badge_value="9.8", badge_label="CVSS", badge_sub="pre-auth",
                mini_value="KEV", mini_label="STATUS", mini_sub="active",
                mini2_value="0d", mini2_label="PATCH ETA", mini2_sub="mitigate",
                visual=l22.v_lock_cve(500, 315, amber["accent"], amber["soft"], cvss="9.8"),
            ),
            dict(
                theme="green",
                label="PATCH ADVISORY",
                headline="Telnetd Root RCE",
                metric="CVE-2026-32746 : 23 vendors",
                detail="BusyBox telnetd root shell : crafted packet : IoT/OT scope : CERT advisory",
                metric_b="IoT/OT scope : embedded BusyBox stacks",
                detail_b="Crafted packet : root RCE : 23 vendor advisories : firmware refresh path",
                badge_value="23", badge_label="VENDORS", badge_sub="patched",
                mini_value="IoT", mini_label="SCOPE", mini_sub="OT/edge",
                mini2_value="ROOT", mini2_label="IMPACT", mini2_sub="shell",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="PATCH"),
            ),
        ],
    )


def cfg_2026_03_22() -> dict:
    """Mar 22: Signal phishing, Oracle IdM CVE-2026-31201, Apple iOS 18.4 7 zero-days."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MA08",
        aria="Signal phishing, Oracle Identity Manager RCE, Apple iOS KEV 7 zero-days",
        title="2026-03-22: Signal phishing, Oracle IdM RCE, Apple KEV",
        url="https://tech.2twodragon.com/security/2026/03/22/Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.html",
        bands=[
            dict(
                theme="red",
                label="MESSENGER PHISHING",
                headline="Signal + WhatsApp Targeted",
                metric="State-sponsored : journalists",
                detail="Linked-device QR phishing : session hijack : Citizen Lab attribution",
                metric_b="Citizen Lab : nation-state attribution",
                detail_b="QR linked-device abuse : full session hijack : journalists + dissidents",
                badge_value="QR", badge_label="VECTOR", badge_sub="link-device",
                mini_value="C-Lab", mini_label="ATTRIB", mini_sub="report",
                mini2_value="HIJACK", mini2_label="SESSION", mini2_sub="device",
                visual=l22.v_browser_cve(500, 105, red["accent"], red["soft"], label="PHISH"),
            ),
            dict(
                theme="amber",
                label="ORACLE CRITICAL",
                headline="Oracle Identity Mgr RCE",
                metric="CVE-2026-31201 : CVSS 9.8",
                detail="Pre-auth RCE : enterprise IAM : Mar 2026 Critical Patch Update : 6.2K instances",
                metric_b="6.2K exposed instances : Shodan census",
                detail_b="Mar 2026 CPU : enterprise IAM : auth-bypass + deserialization chain",
                badge_value="9.8", badge_label="CVSS", badge_sub="OIM",
                mini_value="6.2K", mini_label="EXPOSED", mini_sub="instances",
                mini2_value="CPU", mini2_label="ORACLE", mini2_sub="Mar26",
                visual=l22.v_lock_cve(500, 315, amber["accent"], amber["soft"], cvss="9.8"),
            ),
            dict(
                theme="green",
                label="APPLE KEV",
                headline="iOS 18.4 Emergency",
                metric="7 zero-days : active exploit",
                detail="WebKit Safari + Kernel LPE : Pegasus-linked : also macOS 14.6 Sonoma",
                metric_b="WebKit + Kernel chain : LPE to root",
                detail_b="Pegasus-linked exploitation : iOS 18.4 + macOS 14.6 Sonoma : KEV catalog",
                badge_value="7", badge_label="0-DAYS", badge_sub="patched",
                mini_value="WK", mini_label="WEBKIT", mini_sub="RCE",
                mini2_value="LPE", mini2_label="KERNEL", mini2_sub="root",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="iOS 18.4"),
            ),
        ],
    )


def cfg_2026_03_23() -> dict:
    """Mar 23: The Gentlemen 1570 victims, Zero Trust visibility, EQST Q1 report."""
    red = l22.THEMES["red"]
    blue = l22.THEMES["blue"]
    amber = l22.THEMES["amber"]
    return dict(
        sfx="MA09",
        aria="The Gentlemen ransomware 1,570 victims, Zero Trust east-west visibility, EQST Q1 2026 report",
        title="2026-03-23: Gentlemen RW, Zero Trust visibility, EQST Q1",
        url="https://tech.2twodragon.com/security/2026/03/23/Tech_Security_Weekly_Digest_Ransomware.html",
        bands=[
            dict(
                theme="red",
                label="RANSOMWARE GROUP",
                headline="The Gentlemen",
                metric="1,570+ victims : SystemBC",
                detail="SOCKS5 tunnel C2 : double extortion : RaaS since Jul 2025 : Q1 top 3",
                metric_b="Top-3 RaaS Q1 2026 : SystemBC SOCKS5 C2",
                detail_b="Double extortion : healthcare + manufacturing : Jul-2025 first sighting",
                badge_value="1570", badge_label="VICTIMS", badge_sub="The Gentlemen",
                mini_value="RaaS", mini_label="MODEL", mini_sub="affiliate",
                mini2_value="SBC", mini2_label="C2", mini2_sub="SOCKS5",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="RAAS"),
            ),
            dict(
                theme="blue",
                label="ZERO TRUST",
                headline="Network Visibility",
                metric="East-west flow inspection",
                detail="Service mesh telemetry : eBPF flow logs : behavior baselining : NDR uplift",
                metric_b="eBPF flow logs : service-mesh telemetry",
                detail_b="Behavior baselining : NDR uplift : lateral-movement detection focus",
                badge_value="E-W", badge_label="VISIBILITY", badge_sub="ZT",
                mini_value="eBPF", mini_label="SOURCE", mini_sub="kernel",
                mini2_value="NDR", mini2_label="DETECT", mini2_sub="lateral",
                visual=l22.v_shield(500, 315, blue["accent"], blue["soft"], label="ZERO TRUST"),
            ),
            dict(
                theme="amber",
                label="THREAT INSIGHT",
                headline="SK Shieldus EQST",
                metric="Q1 2026 threat report",
                detail="Korean enterprise targeting : ransomware + APT crossover : MITRE ATT and CK mapping",
                metric_b="Korean enterprise focus : APT + RaaS overlap",
                detail_b="MITRE ATT and CK mapping : sector heatmap : top techniques + IOCs",
                badge_value="Q1", badge_label="EQST", badge_sub="2026 report",
                mini_value="KOR", mini_label="REGION", mini_sub="targeted",
                mini2_value="APT", mini2_label="OVERLAP", mini2_sub="RaaS",
                visual=l22.v_bar_graph(500, 525, amber["accent"], amber["soft"], caption="Q1 TREND"),
            ),
        ],
    )


def cfg_2026_03_29() -> dict:
    """Mar 29: RW + AI automation, LLM jailbreak CVE-2026-3291, Helm + Next.js CVE-2026-29927."""
    red = l22.THEMES["red"]
    purple = l22.THEMES["purple"]
    amber = l22.THEMES["amber"]
    return dict(
        sfx="MA15",
        aria="Ransomware AI automation, LLM multi-step jailbreak CVE-2026-3291, Kubernetes Helm + Next.js CVE-2026-29927",
        title="2026-03-29: RW AI, LLM jailbreak CVE-2026-3291, Helm, Next.js",
        url="https://tech.2twodragon.com/security/2026/03/29/Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.html",
        bands=[
            dict(
                theme="red",
                label="RANSOMWARE + AI",
                headline="Attack Automation",
                metric="Recon + lateral via LLM",
                detail="ChatGPT-4 driven recon : auto-tailored phish : PowerShell synthesis : EDR evasion",
                metric_b="EDR evasion : LLM-synthesised PowerShell",
                detail_b="Auto-tailored phish : per-victim payload tuning : 4x faster recon",
                badge_value="AI", badge_label="AUTO", badge_sub="recon",
                mini_value="4x", mini_label="SPEED", mini_sub="recon",
                mini2_value="EDR", mini2_label="EVASION", mini2_sub="bypass",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="LLM-RW"),
            ),
            dict(
                theme="purple",
                label="LLM JAILBREAK",
                headline="Multi-Step CVE-2026-3291",
                metric="7-step chain : MCP loop",
                detail="Tool reflection cycle : safety eval drift : patched in Claude Opus 4.7",
                metric_b="Tool reflection cycle : safety-eval drift",
                detail_b="MCP loop abuse : patched Claude Opus 4.7 : Anthropic responsible disclosure",
                badge_value="7", badge_label="STEPS", badge_sub="jailbreak",
                mini_value="MCP", mini_label="LOOP", mini_sub="abuse",
                mini2_value="4.7", mini2_label="OPUS", mini2_sub="patched",
                visual=l22.v_code_bars(500, 315, purple["accent"], purple["soft"], caption="LLM CHAIN"),
            ),
            dict(
                theme="amber",
                label="HELM + NEXT.JS",
                headline="K8s Helm + Auth Bypass",
                metric="Chart sig + Next.js CVE",
                detail="Helm provenance gap : Next.js middleware auth bypass CVE-2026-29927",
                metric_b="Next.js CVE-2026-29927 : middleware auth bypass",
                detail_b="Helm provenance/SBOM gap : sigstore enforcement : 2 stacks affected",
                badge_value="2", badge_label="STACKS", badge_sub="affected",
                mini_value="SIG", mini_label="HELM", mini_sub="prov gap",
                mini2_value="MW", mini2_label="NEXT.JS", mini2_sub="bypass",
                visual=l22.v_cloud_k8s(500, 525, amber["accent"], amber["soft"]),
            ),
        ],
    )


def cfg_2026_03_31() -> dict:
    """Mar 31: ChatGPT cache leak, DeepLoad 120K samples, ClickFix Q1 23 campaigns."""
    purple = l22.THEMES["purple"]
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    return dict(
        sfx="MA17",
        aria="ChatGPT cache cross-tenant leak, DeepLoad 120K malware samples, ClickFix Q1 23 campaigns",
        title="2026-03-31: ChatGPT leak, DeepLoad, ClickFix",
        url="https://tech.2twodragon.com/security/2026/03/31/Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.html",
        bands=[
            dict(
                theme="purple",
                label="OPENAI INCIDENT",
                headline="ChatGPT Data Leak",
                metric="Cache cross-tenant exposure",
                detail="Conversation cache miss : metadata leak : disclosed by Promptfoo : patched same day",
                metric_b="Promptfoo disclosure : patched same day",
                detail_b="Cache key collision : cross-tenant metadata leak : titles + first turn exposed",
                badge_value="OAI", badge_label="LEAK", badge_sub="cache",
                mini_value="X-T", mini_label="SCOPE", mini_sub="tenants",
                mini2_value="0d", mini2_label="DWELL", mini2_sub="patched",
                visual=l22.v_code_bars(500, 105, purple["accent"], purple["soft"], caption="GPT CACHE"),
            ),
            dict(
                theme="red",
                label="MALWARE DOWNLOADER",
                headline="DeepLoad Campaign",
                metric="120K samples : malvertising",
                detail="Google Ads vector : signed installer : DanaBot successor : Stealer + RAT chain",
                metric_b="DanaBot lineage : signed-installer abuse",
                detail_b="Google Ads vector : Stealer to RAT chain : 120K unique samples observed",
                badge_value="120K", badge_label="SAMPLES", badge_sub="DeepLoad",
                mini_value="ADS", mini_label="VECTOR", mini_sub="malvert",
                mini2_value="RAT", mini2_label="STAGE2", mini2_sub="payload",
                visual=l22.v_network_nodes(500, 315, red["accent"], red["soft"], label="LOADER"),
            ),
            dict(
                theme="amber",
                label="SOCIAL ENGINEERING",
                headline="ClickFix Pattern",
                metric="Fake CAPTCHA : PowerShell",
                detail="Verify-you-are-human lure : clipboard PowerShell : 23 campaigns Q1 2026",
                metric_b="Clipboard-injection PowerShell : LOLBin chain",
                detail_b="Verify-you-are-human lure : 23 distinct Q1 campaigns : SOC playbook needed",
                badge_value="23", badge_label="CAMPAIGNS", badge_sub="ClickFix Q1",
                mini_value="PS1", mini_label="STAGER", mini_sub="clipboard",
                mini2_value="LOL", mini2_label="LIVING", mini2_sub="off-land",
                visual=l22.v_browser_cve(500, 525, amber["accent"], amber["soft"], label="CLICKFIX"),
            ),
        ],
    )


SPECS = [
    ("2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.svg", cfg_2026_03_19),
    ("2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg", cfg_2026_03_22),
    ("2026-03-23-Tech_Security_Weekly_Digest_Ransomware.svg", cfg_2026_03_23),
    ("2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.svg", cfg_2026_03_29),
    ("2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.svg", cfg_2026_03_31),
]


def main() -> None:
    for filename, cfg_fn in SPECS:
        cfg = cfg_fn()
        # Re-aim each visual at the correct band y_center (105 / 315 / 525).
        # cfg_*() above already passes the right y values for each band.
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
        line_count = svg.count("\n") + 1
        print(f"  wrote {filename}: {line_count} lines")


if __name__ == "__main__":
    main()

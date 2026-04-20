#!/usr/bin/env python3
"""Regenerate cover SVGs (and derivative formats) for Phase A (2026-04-09..2026-04-19).

The template is derived from the reference file
``assets/images/2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet.svg``.
Each post is rendered as a 1200x630 dark-navy/indigo digest card with
three issue cards that use a palette picked to match the severity and
topic of the highlight.

Run from the repo root::

    DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib \
      python3 scripts/regenerate_phase_a_svgs.py

The script is intentionally one-off (no external API calls, no CLI flags).
English-only SVG text content is required by project policy; the card
payload below was hand-written from each post's ``highlights_html`` block.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "images"

# Keep the reference file untouched - it is the style anchor.
REFERENCE_BASENAME = "2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet"


@dataclass(frozen=True)
class Palette:
    """A named palette keyed to the reference SVG gradients."""

    key: str  # "red" | "blue" | "green"
    accent_id: str  # linearGradient id (accentRed / accentBlue / accentGreen)
    stroke_rgba: str  # rgba(...) used for card border
    pill_rgba: str  # rgba(...) used for the label pill background
    label_color: str  # hex color used for label + accent text
    tag_color: str  # hex color used for the CVE/tag line
    icon_name: str  # "botnet" | "identity" | "stack" | "shield" | "alert" | "patch"


RED = Palette(
    key="red",
    accent_id="accentRed",
    stroke_rgba="rgba(255,62,108,0.35)",
    pill_rgba="rgba(255,62,108,0.18)",
    label_color="#ff3e6c",
    tag_color="#ff7a4a",
    icon_name="botnet",
)
BLUE = Palette(
    key="blue",
    accent_id="accentBlue",
    stroke_rgba="rgba(91,163,255,0.35)",
    pill_rgba="rgba(91,163,255,0.18)",
    label_color="#5ba3ff",
    tag_color="#9d6fff",
    icon_name="identity",
)
GREEN = Palette(
    key="green",
    accent_id="accentGreen",
    stroke_rgba="rgba(0,255,136,0.35)",
    pill_rgba="rgba(0,255,136,0.18)",
    label_color="#00ff88",
    tag_color="#00d4b2",
    icon_name="stack",
)


@dataclass(frozen=True)
class CardData:
    """Payload for a single issue card."""

    label: str  # one-word pill label, uppercase (CRITICAL, IDENTITY, etc.)
    headline_1: str
    headline_2: str
    tag: str  # CVE number or vendor label
    desc_1: str
    desc_2: str
    palette: Palette
    icon: str = ""  # override icon - defaults to palette.icon_name


# ---------------------------------------------------------------------------
# Icon library - minimal geometric SVG glyphs per icon family.
# Each icon is drawn inside a transform translate(cx, 92) in the card group.
# Using distinct icons per issue helps differentiate cards visually.


def _icon_botnet(accent: str) -> str:
    """Nodes + links icon: used for botnet/malware/exploit (red)."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2">
      <circle cx="0" cy="0" r="8" fill="url(#{accent})"/>
      <circle cx="-52" cy="30" r="5" fill="url(#{accent})" fill-opacity="0.5"/>
      <circle cx="52" cy="30" r="5" fill="url(#{accent})" fill-opacity="0.5"/>
      <circle cx="-62" cy="-22" r="5" fill="url(#{accent})" fill-opacity="0.5"/>
      <circle cx="62" cy="-22" r="5" fill="url(#{accent})" fill-opacity="0.5"/>
      <circle cx="0" cy="52" r="5" fill="url(#{accent})" fill-opacity="0.5"/>
      <line x1="0" y1="0" x2="-52" y2="30"/>
      <line x1="0" y1="0" x2="52" y2="30"/>
      <line x1="0" y1="0" x2="-62" y2="-22"/>
      <line x1="0" y1="0" x2="62" y2="-22"/>
      <line x1="0" y1="0" x2="0" y2="52"/>
      <line x1="-52" y1="30" x2="52" y2="30" stroke-dasharray="3 3"/>
    </g>"""


def _icon_identity(accent: str) -> str:
    """Shield with slash: identity / impersonation / phishing."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <path d="M-44,-22 L0,-44 L44,-22 L44,12 Q44,38 0,50 Q-44,38 -44,12 Z"/>
      <line x1="-22" y1="-20" x2="22" y2="24" stroke="#ff3e6c" stroke-width="3"/>
      <circle cx="18" cy="20" r="4" fill="#ff3e6c" stroke="none"/>
    </g>"""


def _icon_stack(accent: str) -> str:
    """Layered stack with one highlighted: finance / supply / resource."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <rect x="-52" y="12" width="32" height="32" rx="3"/>
      <rect x="-16" y="-8" width="32" height="32" rx="3"/>
      <rect x="20" y="12" width="32" height="32" rx="3" stroke="#ff3e6c" stroke-dasharray="4 3"/>
      <path d="M-34,12 L-34,-16 L34,-16" stroke-opacity="0.5"/>
      <polyline points="30,-20 36,-14 30,-8" stroke-opacity="0.5"/>
    </g>"""


def _icon_cloud(accent: str) -> str:
    """Cloud with arrow down: cloud exposure / data leak."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M-42,8 Q-58,8 -58,-8 Q-58,-26 -38,-26 Q-32,-42 -12,-42 Q12,-42 18,-24 Q42,-24 42,-4 Q42,14 22,14 L-38,14 Q-42,14 -42,8 Z"/>
      <line x1="0" y1="18" x2="0" y2="48"/>
      <polyline points="-10,38 0,50 10,38"/>
    </g>"""


def _icon_alert(accent: str) -> str:
    """Warning triangle with exclamation: zero-day / critical alert."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M0,-44 L50,40 L-50,40 Z"/>
      <line x1="0" y1="-16" x2="0" y2="16" stroke-width="3.5"/>
      <circle cx="0" cy="30" r="3.5" fill="url(#{accent})" stroke="none"/>
    </g>"""


def _icon_patch(accent: str) -> str:
    """Shield with check: patch / compliance / policy."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M-40,-22 L0,-40 L40,-22 L40,10 Q40,36 0,48 Q-40,36 -40,10 Z"/>
      <polyline points="-18,4 -4,18 20,-8" stroke-width="3"/>
    </g>"""


def _icon_chip(accent: str) -> str:
    """Chip/CPU icon: hardware / firmware / silicon."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round">
      <rect x="-28" y="-28" width="56" height="56" rx="6"/>
      <rect x="-14" y="-14" width="28" height="28" rx="3"/>
      <line x1="-36" y1="-14" x2="-28" y2="-14"/>
      <line x1="-36" y1="0" x2="-28" y2="0"/>
      <line x1="-36" y1="14" x2="-28" y2="14"/>
      <line x1="28" y1="-14" x2="36" y2="-14"/>
      <line x1="28" y1="0" x2="36" y2="0"/>
      <line x1="28" y1="14" x2="36" y2="14"/>
      <line x1="-14" y1="-36" x2="-14" y2="-28"/>
      <line x1="0" y1="-36" x2="0" y2="-28"/>
      <line x1="14" y1="-36" x2="14" y2="-28"/>
      <line x1="-14" y1="28" x2="-14" y2="36"/>
      <line x1="0" y1="28" x2="0" y2="36"/>
      <line x1="14" y1="28" x2="14" y2="36"/>
    </g>"""


def _icon_bot(accent: str) -> str:
    """Bug/bot icon: generic malware / worm."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round">
      <ellipse cx="0" cy="6" rx="24" ry="28"/>
      <circle cx="-8" cy="-2" r="3" fill="url(#{accent})" stroke="none"/>
      <circle cx="8" cy="-2" r="3" fill="url(#{accent})" stroke="none"/>
      <line x1="0" y1="-22" x2="-12" y2="-40"/>
      <line x1="0" y1="-22" x2="12" y2="-40"/>
      <line x1="-24" y1="-4" x2="-42" y2="-12"/>
      <line x1="-24" y1="6" x2="-44" y2="6"/>
      <line x1="-24" y1="16" x2="-42" y2="24"/>
      <line x1="24" y1="-4" x2="42" y2="-12"/>
      <line x1="24" y1="6" x2="44" y2="6"/>
      <line x1="24" y1="16" x2="42" y2="24"/>
    </g>"""


def _icon_code(accent: str) -> str:
    """Code brackets with slash: supply chain / source / dev tooling."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="-14,-24 -40,0 -14,24"/>
      <polyline points="14,-24 40,0 14,24"/>
      <line x1="-4" y1="30" x2="4" y2="-30" stroke-width="2"/>
    </g>"""


def _icon_globe(accent: str) -> str:
    """Globe: geopolitical / international / campaign."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <circle cx="0" cy="0" r="36"/>
      <ellipse cx="0" cy="0" rx="14" ry="36"/>
      <line x1="-36" y1="0" x2="36" y2="0"/>
      <line x1="-32" y1="-18" x2="32" y2="-18"/>
      <line x1="-32" y1="18" x2="32" y2="18"/>
    </g>"""


def _icon_lock(accent: str) -> str:
    """Lock icon: credentials / session / auth."""
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round">
      <rect x="-24" y="0" width="48" height="36" rx="4"/>
      <path d="M-14,0 L-14,-16 Q-14,-32 0,-32 Q14,-32 14,-16 L14,0"/>
      <circle cx="0" cy="18" r="5" fill="url(#{accent})" stroke="none"/>
    </g>"""


ICON_FUNCS = {
    "botnet": _icon_botnet,
    "identity": _icon_identity,
    "stack": _icon_stack,
    "cloud": _icon_cloud,
    "alert": _icon_alert,
    "patch": _icon_patch,
    "chip": _icon_chip,
    "bot": _icon_bot,
    "code": _icon_code,
    "globe": _icon_globe,
    "lock": _icon_lock,
}


# ---------------------------------------------------------------------------
# Per-post card data.  Keys are post basenames (without extension).
# Each value is a 3-tuple of CardData (left, middle, right card).

POSTS: dict[str, tuple[str, tuple[CardData, CardData, CardData]]] = {
    # 2026-04-09  Chaos cloud variant / Masjesu IoT / APT28 PRISMEX
    "2026-04-09-Tech_Security_Weekly_Digest_Cloud_Botnet_AI_Malware": (
        "2026-04-09",
        (
            CardData(
                label="CLOUD",
                headline_1="Chaos Variant",
                headline_2="Hits Cloud",
                tag="SOCKS proxy added",
                desc_1="Misconfigured cloud",
                desc_2="workloads targeted",
                palette=RED,
                icon="cloud",
            ),
            CardData(
                label="BOTNET",
                headline_1="Masjesu IoT",
                headline_2="DDoS for Hire",
                tag="Telegram marketplace",
                desc_1="Global routers and",
                desc_2="gateways recruited",
                palette=BLUE,
                icon="bot",
            ),
            CardData(
                label="APT",
                headline_1="APT28 Drops",
                headline_2="PRISMEX Malware",
                tag="Ukraine and NATO",
                desc_1="Steganography plus",
                desc_2="COM hijacking C2",
                palette=GREEN,
                icon="globe",
            ),
        ),
    ),
    # 2026-04-10 EngageLab SDK / UAT-10362 LucidRook / Agentic SOC
    "2026-04-10-Tech_Security_Weekly_Digest_AI_Malware_Go_Agent": (
        "2026-04-10",
        (
            CardData(
                label="SDK LEAK",
                headline_1="EngageLab SDK",
                headline_2="50M Exposed",
                tag="30M crypto wallets",
                desc_1="Sandbox bypass on",
                desc_2="Android devices",
                palette=RED,
                icon="alert",
            ),
            CardData(
                label="APT",
                headline_1="UAT-10362",
                headline_2="LucidRook Stager",
                tag="Taiwan NGOs hit",
                desc_1="Lua plus Rust DLL",
                desc_2="embedded dropper",
                palette=BLUE,
                icon="code",
            ),
            CardData(
                label="SECOPS",
                headline_1="Agentic SOC",
                headline_2="Redefines SecOps",
                tag="Microsoft blueprint",
                desc_1="Autonomous triage",
                desc_2="at machine speed",
                palette=GREEN,
                icon="patch",
            ),
        ),
    ),
    # 2026-04-11 GlassWorm Zig / Chrome DBSC / browser ext AI
    "2026-04-11-Tech_Security_Weekly_Digest_AI_Go_CVE_Update": (
        "2026-04-11",
        (
            CardData(
                label="SUPPLY",
                headline_1="GlassWorm Zig",
                headline_2="Dropper Spreads",
                tag="Fake WakaTime ext",
                desc_1="Open VSX extension",
                desc_2="infects all IDEs",
                palette=RED,
                icon="code",
            ),
            CardData(
                label="AI RISK",
                headline_1="Browser Ext",
                headline_2="AI Blind Spot",
                tag="LayerX research",
                desc_1="Shadow AI pipes",
                desc_2="leaking enterprise data",
                palette=BLUE,
                icon="bot",
            ),
            CardData(
                label="IDENTITY",
                headline_1="Chrome 146",
                headline_2="Ships DBSC",
                tag="Windows session bind",
                desc_1="Cookie theft blocked",
                desc_2="by device binding",
                palette=GREEN,
                icon="lock",
            ),
        ),
    ),
    # 2026-04-12 Citizen Lab Webloc / Crypto scam ops / ChatGPT Pro
    "2026-04-12-Tech_Security_Weekly_Digest_Data_GPT_Cloud_AI": (
        "2026-04-12",
        (
            CardData(
                label="PRIVACY",
                headline_1="Webloc Tracks",
                headline_2="500M Devices",
                tag="Citizen Lab report",
                desc_1="Ad data abused by",
                desc_2="law enforcement",
                palette=RED,
                icon="globe",
            ),
            CardData(
                label="FRAUD",
                headline_1="Crypto Scam",
                headline_2="20K Victims Found",
                tag="International takedown",
                desc_1="Pig butchering ring",
                desc_2="dismantled globally",
                palette=BLUE,
                icon="stack",
            ),
            CardData(
                label="AI",
                headline_1="ChatGPT Pro",
                headline_2="Rivals Claude",
                tag="100 USD per month",
                desc_1="OpenAI targets",
                desc_2="Anthropic tier",
                palette=GREEN,
                icon="bot",
            ),
        ),
    ),
    # 2026-04-13 CPU-Z trojan / Marimo RCE / Adobe Acrobat
    "2026-04-13-Tech_Security_Weekly_Digest_CVE_Patch_Zero-Day_Rust": (
        "2026-04-13",
        (
            CardData(
                label="SUPPLY",
                headline_1="CPUID Breach",
                headline_2="CPU-Z Trojanized",
                tag="STX RAT delivered",
                desc_1="HWMonitor downloads",
                desc_2="altered at source",
                palette=RED,
                icon="chip",
            ),
            CardData(
                label="CRITICAL",
                headline_1="Marimo RCE",
                headline_2="Under Exploit",
                tag="CVE-2026-39987",
                desc_1="Pre-auth remote code",
                desc_2="executed in the wild",
                palette=BLUE,
                icon="alert",
            ),
            CardData(
                label="PATCH",
                headline_1="Adobe Acrobat",
                headline_2="Patches Zero-Day",
                tag="CVE-2026-34621",
                desc_1="Active exploitation",
                desc_2="against PDF readers",
                palette=GREEN,
                icon="patch",
            ),
        ),
    ),
    # 2026-04-14 March ransomware report / JanelaRAT / W3LL takedown
    "2026-04-14-Tech_Security_Weekly_Digest_Malware_Vulnerability_AI_Data": (
        "2026-04-14",
        (
            CardData(
                label="REPORT",
                headline_1="March 2026",
                headline_2="Ransomware Trends",
                tag="AhnLab ASEC brief",
                desc_1="Volume and TTP",
                desc_2="shifts tracked",
                palette=RED,
                icon="alert",
            ),
            CardData(
                label="BANKING",
                headline_1="JanelaRAT Hits",
                headline_2="LatAm Banks",
                tag="14,739 attacks in Brazil",
                desc_1="Financial data theft",
                desc_2="across 2025 campaign",
                palette=BLUE,
                icon="bot",
            ),
            CardData(
                label="TAKEDOWN",
                headline_1="W3LL Phishing",
                headline_2="Network Dismantled",
                tag="20M USD fraud foiled",
                desc_1="FBI and Indonesia",
                desc_2="police coordinate",
                palette=GREEN,
                icon="globe",
            ),
        ),
    ),
    # 2026-04-15 MCP AWS agents / PHP Composer / Pixel Rust DNS
    "2026-04-15-Tech_Security_Weekly_Digest_AI_AWS_Agent_Patch": (
        "2026-04-15",
        (
            CardData(
                label="AI AGENT",
                headline_1="MCP Patterns",
                headline_2="Secure AWS Agents",
                tag="AWS Security Blog",
                desc_1="Model Context Protocol",
                desc_2="guardrails outlined",
                palette=BLUE,
                icon="patch",
            ),
            CardData(
                label="SUPPLY",
                headline_1="PHP Composer",
                headline_2="RCE Flaw Patched",
                tag="Arbitrary commands",
                desc_1="Dependency resolver",
                desc_2="abused by attackers",
                palette=RED,
                icon="code",
            ),
            CardData(
                label="HARDEN",
                headline_1="Pixel 10 Modem",
                headline_2="Gets Rust DNS",
                tag="Google memory safety",
                desc_1="Baseband parser",
                desc_2="rewritten in Rust",
                palette=GREEN,
                icon="chip",
            ),
        ),
    ),
    # 2026-04-16 n8n webhooks / Nginx UI bypass / nginx-ui CVE
    "2026-04-16-Tech_Security_Weekly_Digest_AI_Malware_CVE_Patch": (
        "2026-04-16",
        (
            CardData(
                label="ABUSE",
                headline_1="n8n Webhooks",
                headline_2="Phish Delivery",
                tag="Active since Oct 2025",
                desc_1="Automation platform",
                desc_2="weaponized by actors",
                palette=RED,
                icon="bot",
            ),
            CardData(
                label="CRITICAL",
                headline_1="Nginx UI",
                headline_2="Auth Bypass",
                tag="CVE-2026-33032",
                desc_1="Full server takeover",
                desc_2="under active exploit",
                palette=BLUE,
                icon="alert",
            ),
            CardData(
                label="CISO",
                headline_1="Cloud CISO",
                headline_2="Resilience Q and A",
                tag="Google Cloud brief",
                desc_1="Technical and cultural",
                desc_2="resilience guidance",
                palette=GREEN,
                icon="patch",
            ),
        ),
    ),
    # 2026-04-17 PowMix botnet / Defender 0-day / Operation PowerOFF
    "2026-04-17-Tech_Security_Weekly_Digest_Botnet_Threat_AI_Malware": (
        "2026-04-17",
        (
            CardData(
                label="BOTNET",
                headline_1="PowMix Botnet",
                headline_2="Hits Czech Staff",
                tag="Randomized C2",
                desc_1="Obfuscated beacons",
                desc_2="evade detection",
                palette=RED,
                icon="botnet",
            ),
            CardData(
                label="ZERO-DAY",
                headline_1="Defender",
                headline_2="Zero-Day Active",
                tag="SonicWall brute force",
                desc_1="Multiple vendors face",
                desc_2="in-the-wild abuse",
                palette=BLUE,
                icon="alert",
            ),
            CardData(
                label="TAKEDOWN",
                headline_1="Operation",
                headline_2="PowerOFF Strikes",
                tag="75K DDoS users ID",
                desc_1="53 booter domains",
                desc_2="seized worldwide",
                palette=GREEN,
                icon="globe",
            ),
        ),
    ),
    # 2026-04-18 Defender 3 0-days / OCSF ETL / Google ads + Android 17
    "2026-04-18-Tech_Security_Weekly_Digest_Zero-Day_Patch_Security_Go": (
        "2026-04-18",
        (
            CardData(
                label="ZERO-DAY",
                headline_1="Defender",
                headline_2="3 Zero-Days Hit",
                tag="2 still unpatched",
                desc_1="Microsoft endpoint",
                desc_2="agent under attack",
                palette=RED,
                icon="alert",
            ),
            CardData(
                label="PIPELINE",
                headline_1="OCSF ETL",
                headline_2="Normalizes Logs",
                tag="AWS reference build",
                desc_1="Config driven schema",
                desc_2="across security tools",
                palette=BLUE,
                icon="stack",
            ),
            CardData(
                label="POLICY",
                headline_1="Google Blocks",
                headline_2="8.3B Bad Ads",
                tag="Android 17 privacy",
                desc_1="2025 enforcement and",
                desc_2="new OS safeguards",
                palette=GREEN,
                icon="patch",
            ),
        ),
    ),
}


# ---------------------------------------------------------------------------
# SVG rendering


_HEADER = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>Security Weekly Digest - {date}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0a0e27"/>
      <stop offset="1" stop-color="#1a1f3a"/>
    </linearGradient>
    <linearGradient id="accentRed" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ff3e6c"/>
      <stop offset="1" stop-color="#ff7a4a"/>
    </linearGradient>
    <linearGradient id="accentBlue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5ba3ff"/>
      <stop offset="1" stop-color="#9d6fff"/>
    </linearGradient>
    <linearGradient id="accentGreen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#00ff88"/>
      <stop offset="1" stop-color="#00d4b2"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#5ba3ff" stop-opacity="0.25"/>
      <stop offset="1" stop-color="#5ba3ff" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="200" cy="150" r="300" fill="url(#glow)"/>
  <circle cx="1000" cy="500" r="260" fill="url(#glow)" opacity="0.6"/>

  <g opacity="0.08" stroke="#ffffff" stroke-width="1">
    <line x1="60" y1="95" x2="1140" y2="95"/>
    <line x1="60" y1="555" x2="1140" y2="555"/>
  </g>

  <text x="60" y="55" font-family="system-ui, -apple-system, sans-serif" font-size="17" font-weight="700" fill="#00ff88" letter-spacing="4">TECH SECURITY WEEKLY DIGEST</text>
  <text x="1140" y="55" text-anchor="end" font-family="system-ui, -apple-system, sans-serif" font-size="17" font-weight="500" fill="#8b95b0" letter-spacing="2">{date}</text>
"""

_FOOTER = """  <text x="60" y="595" font-family="system-ui, sans-serif" font-size="14" font-weight="600" fill="#5ba3ff">tech.2twodragon.com</text>

  <g transform="translate(950, 578)">
    <rect x="0" y="0" width="82" height="26" rx="13" fill="rgba(0,255,136,0.14)" stroke="rgba(0,255,136,0.4)"/>
    <text x="41" y="18" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="#00ff88" letter-spacing="2">SECURITY</text>
    <rect x="92" y="0" width="96" height="26" rx="13" fill="rgba(91,163,255,0.14)" stroke="rgba(91,163,255,0.4)"/>
    <text x="140" y="18" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="#5ba3ff" letter-spacing="2">DEVSECOPS</text>
  </g>
</svg>
"""


# Per-card layout: (translate_x, card_width)
_CARD_LAYOUT = [
    (60, 345),
    (427, 346),
    (795, 345),
]


def _pill_width(label: str) -> int:
    """Width of the label pill, roughly scaled to label length."""
    # 11pt letter-spacing:3 makes each glyph ~10-11 px wide; add 24 px padding.
    return max(80, 8 * len(label) + 32)


def _render_card(translate_x: int, width: int, card: CardData) -> str:
    cx = width // 2
    icon_name = card.icon or card.palette.icon_name
    icon_func = ICON_FUNCS[icon_name]
    icon_svg = icon_func(card.palette.accent_id).format(cx=cx)
    pill_w = _pill_width(card.label)
    pill_x = cx - pill_w // 2
    return f"""  <g transform="translate({translate_x}, 125)">
    <rect width="{width}" height="410" rx="18" fill="rgba(255,255,255,0.04)" stroke="{card.palette.stroke_rgba}" stroke-width="1.5"/>
{icon_svg}
    <rect x="{pill_x}" y="210" width="{pill_w}" height="24" rx="12" fill="{card.palette.pill_rgba}"/>
    <text x="{cx}" y="227" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{card.palette.label_color}" letter-spacing="3">{card.label}</text>
    <text x="{cx}" y="272" text-anchor="middle" font-family="system-ui, sans-serif" font-size="23" font-weight="700" fill="#f0f4f8">{card.headline_1}</text>
    <text x="{cx}" y="300" text-anchor="middle" font-family="system-ui, sans-serif" font-size="23" font-weight="700" fill="#f0f4f8">{card.headline_2}</text>
    <text x="{cx}" y="335" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600" fill="{card.palette.tag_color}" letter-spacing="1">{card.tag}</text>
    <text x="{cx}" y="365" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13" fill="#8b95b0">{card.desc_1}</text>
    <text x="{cx}" y="384" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13" fill="#8b95b0">{card.desc_2}</text>
  </g>
"""


def render_svg(date: str, cards: Sequence[CardData]) -> str:
    assert len(cards) == 3, "exactly three cards required"
    parts = [_HEADER.format(date=date), "\n"]
    for (tx, w), card in zip(_CARD_LAYOUT, cards):
        parts.append(_render_card(tx, w, card))
    parts.append("\n")
    parts.append(_FOOTER)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Validators - fail fast on Korean or forbidden punctuation.

_FORBIDDEN_CHARS = "\u00b7\u2022\u2014\u201c\u201d\u2018\u2019"  # · • — " " ' '


def _validate_text(text: str, where: str) -> None:
    for ch in text:
        if "\uac00" <= ch <= "\ud7a3":
            raise ValueError(f"Korean character found in {where}: {text!r}")
        if ch in _FORBIDDEN_CHARS:
            raise ValueError(f"Forbidden char {ch!r} in {where}: {text!r}")


def _validate_card(basename: str, card: CardData) -> None:
    for field in (card.label, card.headline_1, card.headline_2, card.tag, card.desc_1, card.desc_2):
        _validate_text(field, f"{basename}")


# ---------------------------------------------------------------------------
# Derivative formats (og.{png,webp,avif}, card.{webp,avif})


def _regenerate_derivatives(basename: str) -> None:
    # Lazy imports so the SVG-only path works without graphics libs installed.
    import cairosvg  # type: ignore
    from PIL import Image  # type: ignore

    svg_path = ASSETS_DIR / f"{basename}.svg"
    og_png = ASSETS_DIR / f"{basename}_og.png"
    cairosvg.svg2png(url=str(svg_path), output_width=1200, output_height=630, write_to=str(og_png))
    with Image.open(og_png) as og:
        og.load()
        og.save(ASSETS_DIR / f"{basename}_og.webp", "WEBP", quality=88)
        og.save(ASSETS_DIR / f"{basename}_og.avif", "AVIF", quality=72)

    card_png = ASSETS_DIR / f"{basename}_card.png"
    cairosvg.svg2png(url=str(svg_path), output_width=525, output_height=275, write_to=str(card_png))
    try:
        with Image.open(card_png) as card:
            card.load()
            card.save(ASSETS_DIR / f"{basename}_card.webp", "WEBP", quality=88)
            card.save(ASSETS_DIR / f"{basename}_card.avif", "AVIF", quality=72)
    finally:
        if card_png.exists():
            card_png.unlink()


# ---------------------------------------------------------------------------
# Main


def main() -> None:
    # Write 10 SVGs (the reference 04-19 stays untouched).
    for basename, (date, cards) in POSTS.items():
        for c in cards:
            _validate_card(basename, c)
        svg = render_svg(date, cards)
        _validate_text(svg, basename)
        out = ASSETS_DIR / f"{basename}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"svg:  {out.name}")

    # Plus derivatives for all 11 dates (04-09 through 04-19) -- the reference
    # was already rewritten, and its derivatives must also be regenerated.
    all_bases = list(POSTS.keys()) + [REFERENCE_BASENAME]
    for base in all_bases:
        _regenerate_derivatives(base)
        print(f"derv: {base}")


if __name__ == "__main__":
    main()

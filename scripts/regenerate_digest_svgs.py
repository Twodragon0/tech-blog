#!/usr/bin/env python3
"""Regenerate cover SVGs (and derivative formats) for the weekly digest series.

This is the generalised successor to ``regenerate_phase_a_svgs.py``.  It keeps
the same visual language (dark navy gradient, three issue cards, per-card
palette) but spans multiple waves of posts.  Phase A (2026-04-09..2026-04-19)
and Phase B (2026-03-08..2026-04-05) are both maintained here so one script can
rebuild every digest cover without external API calls.

Run from the repo root::

    DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib \
      python3 scripts/regenerate_digest_svgs.py

English-only SVG text content is required by project policy; the card
payload below was hand-written from each post's ``highlights_html`` block
(or in the case of the monthly index, from the digest table of contents).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "images"

# Reference file - the visual anchor for both phases.
REFERENCE_BASENAME = "2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet"


@dataclass(frozen=True)
class Palette:
    key: str  # "red" | "blue" | "green"
    accent_id: str
    stroke_rgba: str
    pill_rgba: str
    label_color: str
    tag_color: str
    icon_name: str


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
    label: str
    headline_1: str
    headline_2: str
    tag: str
    desc_1: str
    desc_2: str
    palette: Palette
    icon: str = ""


# ---------------------------------------------------------------------------
# Icon library - unchanged from Phase A.


def _icon_botnet(accent: str) -> str:
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
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <path d="M-44,-22 L0,-44 L44,-22 L44,12 Q44,38 0,50 Q-44,38 -44,12 Z"/>
      <line x1="-22" y1="-20" x2="22" y2="24" stroke="#ff3e6c" stroke-width="3"/>
      <circle cx="18" cy="20" r="4" fill="#ff3e6c" stroke="none"/>
    </g>"""


def _icon_stack(accent: str) -> str:
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <rect x="-52" y="12" width="32" height="32" rx="3"/>
      <rect x="-16" y="-8" width="32" height="32" rx="3"/>
      <rect x="20" y="12" width="32" height="32" rx="3" stroke="#ff3e6c" stroke-dasharray="4 3"/>
      <path d="M-34,12 L-34,-16 L34,-16" stroke-opacity="0.5"/>
      <polyline points="30,-20 36,-14 30,-8" stroke-opacity="0.5"/>
    </g>"""


def _icon_cloud(accent: str) -> str:
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M-42,8 Q-58,8 -58,-8 Q-58,-26 -38,-26 Q-32,-42 -12,-42 Q12,-42 18,-24 Q42,-24 42,-4 Q42,14 22,14 L-38,14 Q-42,14 -42,8 Z"/>
      <line x1="0" y1="18" x2="0" y2="48"/>
      <polyline points="-10,38 0,50 10,38"/>
    </g>"""


def _icon_alert(accent: str) -> str:
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M0,-44 L50,40 L-50,40 Z"/>
      <line x1="0" y1="-16" x2="0" y2="16" stroke-width="3.5"/>
      <circle cx="0" cy="30" r="3.5" fill="url(#{accent})" stroke="none"/>
    </g>"""


def _icon_patch(accent: str) -> str:
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M-40,-22 L0,-40 L40,-22 L40,10 Q40,36 0,48 Q-40,36 -40,10 Z"/>
      <polyline points="-18,4 -4,18 20,-8" stroke-width="3"/>
    </g>"""


def _icon_chip(accent: str) -> str:
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
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="-14,-24 -40,0 -14,24"/>
      <polyline points="14,-24 40,0 14,24"/>
      <line x1="-4" y1="30" x2="4" y2="-30" stroke-width="2"/>
    </g>"""


def _icon_globe(accent: str) -> str:
    return f"""    <g transform="translate({{cx}}, 92)" fill="none" stroke="url(#{accent})" stroke-width="2.5">
      <circle cx="0" cy="0" r="36"/>
      <ellipse cx="0" cy="0" rx="14" ry="36"/>
      <line x1="-36" y1="0" x2="36" y2="0"/>
      <line x1="-32" y1="-18" x2="32" y2="-18"/>
      <line x1="-32" y1="18" x2="32" y2="18"/>
    </g>"""


def _icon_lock(accent: str) -> str:
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
# Phase A payload (preserved verbatim so a single run refreshes everything).

PHASE_A: dict[str, tuple[str, tuple[CardData, CardData, CardData]]] = {
    "2026-04-09-Tech_Security_Weekly_Digest_Cloud_Botnet_AI_Malware": (
        "2026-04-09",
        (
            CardData("CLOUD", "Chaos Variant", "Hits Cloud", "SOCKS proxy added",
                     "Misconfigured cloud", "workloads targeted", RED, "cloud"),
            CardData("BOTNET", "Masjesu IoT", "DDoS for Hire", "Telegram marketplace",
                     "Global routers and", "gateways recruited", BLUE, "bot"),
            CardData("APT", "APT28 Drops", "PRISMEX Malware", "Ukraine and NATO",
                     "Steganography plus", "COM hijacking C2", GREEN, "globe"),
        ),
    ),
    "2026-04-10-Tech_Security_Weekly_Digest_AI_Malware_Go_Agent": (
        "2026-04-10",
        (
            CardData("SDK LEAK", "EngageLab SDK", "50M Exposed", "30M crypto wallets",
                     "Sandbox bypass on", "Android devices", RED, "alert"),
            CardData("APT", "UAT-10362", "LucidRook Stager", "Taiwan NGOs hit",
                     "Lua plus Rust DLL", "embedded dropper", BLUE, "code"),
            CardData("SECOPS", "Agentic SOC", "Redefines SecOps", "Microsoft blueprint",
                     "Autonomous triage", "at machine speed", GREEN, "patch"),
        ),
    ),
    "2026-04-11-Tech_Security_Weekly_Digest_AI_Go_CVE_Update": (
        "2026-04-11",
        (
            CardData("SUPPLY", "GlassWorm Zig", "Dropper Spreads", "Fake WakaTime ext",
                     "Open VSX extension", "infects all IDEs", RED, "code"),
            CardData("AI RISK", "Browser Ext", "AI Blind Spot", "LayerX research",
                     "Shadow AI pipes", "leaking enterprise data", BLUE, "bot"),
            CardData("IDENTITY", "Chrome 146", "Ships DBSC", "Windows session bind",
                     "Cookie theft blocked", "by device binding", GREEN, "lock"),
        ),
    ),
    "2026-04-12-Tech_Security_Weekly_Digest_Data_GPT_Cloud_AI": (
        "2026-04-12",
        (
            CardData("PRIVACY", "Webloc Tracks", "500M Devices", "Citizen Lab report",
                     "Ad data abused by", "law enforcement", RED, "globe"),
            CardData("FRAUD", "Crypto Scam", "20K Victims Found", "International takedown",
                     "Pig butchering ring", "dismantled globally", BLUE, "stack"),
            CardData("AI", "ChatGPT Pro", "Rivals Claude", "100 USD per month",
                     "OpenAI targets", "Anthropic tier", GREEN, "bot"),
        ),
    ),
    "2026-04-13-Tech_Security_Weekly_Digest_CVE_Patch_Zero-Day_Rust": (
        "2026-04-13",
        (
            CardData("SUPPLY", "CPUID Breach", "CPU-Z Trojanized", "STX RAT delivered",
                     "HWMonitor downloads", "altered at source", RED, "chip"),
            CardData("CRITICAL", "Marimo RCE", "Under Exploit", "CVE-2026-39987",
                     "Pre-auth remote code", "executed in the wild", BLUE, "alert"),
            CardData("PATCH", "Adobe Acrobat", "Patches Zero-Day", "CVE-2026-34621",
                     "Active exploitation", "against PDF readers", GREEN, "patch"),
        ),
    ),
    "2026-04-14-Tech_Security_Weekly_Digest_Malware_Vulnerability_AI_Data": (
        "2026-04-14",
        (
            CardData("REPORT", "March 2026", "Ransomware Trends", "AhnLab ASEC brief",
                     "Volume and TTP", "shifts tracked", RED, "alert"),
            CardData("BANKING", "JanelaRAT Hits", "LatAm Banks", "14,739 attacks in Brazil",
                     "Financial data theft", "across 2025 campaign", BLUE, "bot"),
            CardData("TAKEDOWN", "W3LL Phishing", "Network Dismantled", "20M USD fraud foiled",
                     "FBI and Indonesia", "police coordinate", GREEN, "globe"),
        ),
    ),
    "2026-04-15-Tech_Security_Weekly_Digest_AI_AWS_Agent_Patch": (
        "2026-04-15",
        (
            CardData("AI AGENT", "MCP Patterns", "Secure AWS Agents", "AWS Security Blog",
                     "Model Context Protocol", "guardrails outlined", BLUE, "patch"),
            CardData("SUPPLY", "PHP Composer", "RCE Flaw Patched", "Arbitrary commands",
                     "Dependency resolver", "abused by attackers", RED, "code"),
            CardData("HARDEN", "Pixel 10 Modem", "Gets Rust DNS", "Google memory safety",
                     "Baseband parser", "rewritten in Rust", GREEN, "chip"),
        ),
    ),
    "2026-04-16-Tech_Security_Weekly_Digest_AI_Malware_CVE_Patch": (
        "2026-04-16",
        (
            CardData("ABUSE", "n8n Webhooks", "Phish Delivery", "Active since Oct 2025",
                     "Automation platform", "weaponized by actors", RED, "bot"),
            CardData("CRITICAL", "Nginx UI", "Auth Bypass", "CVE-2026-33032",
                     "Full server takeover", "under active exploit", BLUE, "alert"),
            CardData("CISO", "Cloud CISO", "Resilience Q and A", "Google Cloud brief",
                     "Technical and cultural", "resilience guidance", GREEN, "patch"),
        ),
    ),
    "2026-04-17-Tech_Security_Weekly_Digest_Botnet_Threat_AI_Malware": (
        "2026-04-17",
        (
            CardData("BOTNET", "PowMix Botnet", "Hits Czech Staff", "Randomized C2",
                     "Obfuscated beacons", "evade detection", RED, "botnet"),
            CardData("ZERO-DAY", "Defender", "Zero-Day Active", "SonicWall brute force",
                     "Multiple vendors face", "in-the-wild abuse", BLUE, "alert"),
            CardData("TAKEDOWN", "Operation", "PowerOFF Strikes", "75K DDoS users ID",
                     "53 booter domains", "seized worldwide", GREEN, "globe"),
        ),
    ),
    "2026-04-18-Tech_Security_Weekly_Digest_Zero-Day_Patch_Security_Go": (
        "2026-04-18",
        (
            CardData("ZERO-DAY", "Defender", "3 Zero-Days Hit", "2 still unpatched",
                     "Microsoft endpoint", "agent under attack", RED, "alert"),
            CardData("PIPELINE", "OCSF ETL", "Normalizes Logs", "AWS reference build",
                     "Config driven schema", "across security tools", BLUE, "stack"),
            CardData("POLICY", "Google Blocks", "8.3B Bad Ads", "Android 17 privacy",
                     "2025 enforcement and", "new OS safeguards", GREEN, "patch"),
        ),
    ),
}


# ---------------------------------------------------------------------------
# Phase B payload (2026-03-08..2026-04-05).  Headlines compressed from each
# post's highlights_html block.  The monthly index on 03-30 keeps the same
# three-card layout but pivots to the month's top themes.

PHASE_B: dict[str, tuple[str, tuple[CardData, CardData, CardData]]] = {
    "2026-03-08-Tech_Security_Weekly_Digest_AI_Security": (
        "2026-03-08",
        (
            CardData("AI SCAN", "Codex Security", "Finds 10K Bugs", "1.2M commits scanned",
                     "OpenAI automation", "flags CVEs at scale", BLUE, "bot"),
            CardData("AI HUNT", "Claude Audits", "Firefox Code", "22 flaws reported",
                     "Anthropic agents", "triage real sources", GREEN, "patch"),
            CardData("FINANCE", "USDC Transfers", "Cross 1.8T USD", "Go UUID proposal",
                     "Stablecoin volume", "rewrites rail charts", RED, "stack"),
        ),
    ),
    "2026-03-09-Tech_Security_Weekly_Digest_AI_Security_Go_Bitcoin": (
        "2026-03-09",
        (
            CardData("AI AGENT", "Agent Attack", "Surface Mapped", "Krebs deep dive",
                     "Prompt injection", "and supply chain risks", RED, "bot"),
            CardData("POLICY", "CLARITY Act", "Splits SEC CFTC", "Bank compliance hit",
                     "Crypto rulebook", "reshapes controls", BLUE, "stack"),
            CardData("SANDBOX", "Agent Safehouse", "Ships for macOS", "Native isolation",
                     "AI agents pinned", "to OS sandbox", GREEN, "lock"),
        ),
    ),
    "2026-03-10-Tech_Security_Weekly_Digest_AI_Malware_Security_Data": (
        "2026-03-10",
        (
            CardData("DPRK", "UNC4899 Hits", "Crypto Firms", "Trojan AirDrop files",
                     "North Korean op", "lures developers", RED, "globe"),
            CardData("ZERO-DAY", "Qualcomm 0-Day", "And iOS Chain", "AirSnitch active",
                     "Mobile exploit", "chain in the wild", BLUE, "alert"),
            CardData("POLICY", "Coinbase Rolls", "EU Futures Live", "Nasdaq-Kraken deal",
                     "Tokenized equities", "move onshore", GREEN, "patch"),
        ),
    ),
    "2026-03-11-Tech_Security_Weekly_Digest_AI_Agent_Data_Malware": (
        "2026-03-11",
        (
            CardData("EXPOSURE", "Cloudflare ASI", "Maps Attack Face", "Surface intel brief",
                     "External assets", "audited continuously", RED, "globe"),
            CardData("HARDEN", "Wallet Access", "Needs Rule Audit", "Detection tuning",
                     "Internet-facing", "services re-hardened", BLUE, "lock"),
            CardData("GOVERN", "AI Infra Spend", "Shifts Controls", "Local-first tools",
                     "Governance gaps", "widen in fast stacks", GREEN, "stack"),
        ),
    ),
    "2026-03-12-Tech_Security_Weekly_Digest_AI_Malware_AWS_Patch": (
        "2026-03-12",
        (
            CardData("STRATEGY", "Vertical AI", "Meets Policy", "Chain market signals",
                     "Product and risk", "moves in lockstep", BLUE, "stack"),
            CardData("HARDEN", "Wallet Guard", "3P Dep Checks", "Policy monitoring",
                     "Supply-chain audits", "for every quarter", RED, "code"),
            CardData("SIGNAL", "Tech News Maps", "Ops Governance", "Leading indicator",
                     "Model choices tied", "to control plane", GREEN, "patch"),
        ),
    ),
    "2026-03-15-Tech_Security_Weekly_Digest_AWS_AI_Bitcoin": (
        "2026-03-15",
        (
            CardData("SUPPLY", "GlassWorm Hits", "72 VSX Exts", "Open VSX registry",
                     "Dev tool chain", "turned hostile", RED, "code"),
            CardData("AI RISK", "Agent Prompt", "Injection Leak", "Data theft paths",
                     "Internal LLMs", "need input guards", BLUE, "bot"),
            CardData("IDENTITY", "AWS IAM IDC", "Goes Multi-Region", "Central access plane",
                     "Federated policy", "spans every region", GREEN, "lock"),
        ),
    ),
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update": (
        "2026-03-16",
        (
            CardData("RED TEAM", "Agent Playbook", "Goes Open Source", "Show HN launch",
                     "Exploit code ships", "for AI agent labs", RED, "bot"),
            CardData("BUILDERS", "Bedrock Agents", "On Serverless", "Claude Agent SDK",
                     "AWS shows multi", "agent blueprints", BLUE, "patch"),
            CardData("PRACTICE", "Agent Harness", "Needs Guardrails", "Prompt boundaries",
                     "Tool scopes pinned", "for every workflow", GREEN, "stack"),
        ),
    ),
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin": (
        "2026-03-16",
        (
            CardData("FRAUD", "Libra Token", "5M USD Trail", "Argentina probe",
                     "Forensics exposes", "pump-and-dump ring", RED, "stack"),
            CardData("POLICY", "Stablecoin Rule", "Hits Banks Hard", "Regulatory limbo",
                     "Lenders feel it", "more than crypto", BLUE, "globe"),
            CardData("TOOLING", "MCP Revived", "For AI Eng", "CLI trend reset",
                     "Model Context", "returns to org stacks", GREEN, "code"),
        ),
    ),
    "2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet": (
        "2026-03-17",
        (
            CardData("SUPPLY", "GlassWorm Pivots", "To Python Repos", "Stolen GitHub tokens",
                     "Malicious pushes", "into PyPI sources", RED, "code"),
            CardData("WEEKLY", "Chrome 0-Day", "Router Botnet", "AWS breach watch",
                     "Malicious agents", "span every vector", BLUE, "alert"),
            CardData("VALIDATE", "Security Tests", "Go Agentic", "Autonomous QA",
                     "Runtime probes", "replace scanners", GREEN, "bot"),
        ),
    ),
    "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware": (
        "2026-03-18",
        (
            CardData("AI FLAW", "Bedrock Leak", "LangSmith RCE", "SGLang bug chain",
                     "LLM pipelines", "leak data and code", RED, "alert"),
            CardData("RANSOM", "LeakNet Ships", "Deno Loader", "ClickFix lure",
                     "Compromised sites", "deliver in-memory", BLUE, "bot"),
            CardData("SCALE", "Multi-Cluster", "GKE Inference", "Global AI routing",
                     "Workloads scale", "across regions", GREEN, "stack"),
        ),
    ),
    "2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch": (
        "2026-03-19",
        (
            CardData("SANCTION", "OFAC Targets", "DPRK IT Workers", "WMD funding ring",
                     "Remote dev jobs", "fund weapons program", BLUE, "globe"),
            CardData("RANSOM", "Interlock Hits", "Cisco FMC Root", "CVE-2026-20131",
                     "Zero-day grants", "full admin shell", RED, "alert"),
            CardData("CRITICAL", "Telnetd Flaw", "Pre-Auth RCE", "CVE-2026-32746",
                     "Unauthenticated", "root still unpatched", GREEN, "patch"),
        ),
    ),
    "2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat": (
        "2026-03-20",
        (
            CardData("BREACH", "Speagle Spills", "DocGuard Data", "Supply chain leak",
                     "Cobra tool abused", "to exfiltrate logs", RED, "stack"),
            CardData("EDR KILL", "54 Killers Ship", "With BYOVD Kit", "34 signed drivers",
                     "EDR products", "disabled at scale", BLUE, "alert"),
            CardData("WEEKLY", "FortiGate RaaS", "Citrix Exploits", "MCP abuse trend",
                     "Threat roundup", "across daily brief", GREEN, "globe"),
        ),
    ),
    "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware": (
        "2026-03-21",
        (
            CardData("SUPPLY", "Trivy Actions", "75 Tags Stolen", "CI secret leak",
                     "GitHub Actions", "breach leaks pipelines", RED, "code"),
            CardData("CRITICAL", "Langflow Flaw", "Hit in 20 Hrs", "CVE-2026-33017",
                     "Exploits landed", "hours after disclosure", BLUE, "alert"),
            CardData("POLICY", "Android Adds", "24H Sideload Wait", "Scam prevention",
                     "Unverified apps", "face cooldown gate", GREEN, "patch"),
        ),
    ),
    "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple": (
        "2026-03-22",
        (
            CardData("PHISH", "Russian Actors", "Hit Signal WA", "FBI advisory",
                     "Messaging apps", "face mass phishing", RED, "identity"),
            CardData("CRITICAL", "Oracle IdM", "Unauth RCE Fix", "CVE-2026-21992",
                     "Identity manager", "patched under fire", BLUE, "alert"),
            CardData("SUPPLY", "CanisterWorm", "Hits 47 NPM Pkgs", "Self-spreading worm",
                     "Trivy-linked loot", "infects registries", GREEN, "code"),
        ),
    ),
    "2026-03-23-Tech_Security_Weekly_Digest_Ransomware": (
        "2026-03-23",
        (
            CardData("RANSOM", "Gentlemen Ring", "Keeps Growing", "SK Shieldus brief",
                     "December waves", "target APAC orgs", RED, "alert"),
            CardData("STRATEGY", "Zero Trust Lens", "On Visibility", "Special report",
                     "Analytics stack", "gets modernized", BLUE, "lock"),
            CardData("INSIGHT", "EQST Digest", "Ships December", "Unified insight",
                     "Threat analytics", "for security ops", GREEN, "stack"),
        ),
    ),
    "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI": (
        "2026-03-24",
        (
            CardData("DPRK", "StoatWaffle Hits", "Via VS Code", "Auto-run tasks",
                     "Developer IDEs", "turn into droppers", RED, "code"),
            CardData("IDENTITY", "IAM Policies", "When to Apply", "AWS playbook",
                     "Policy types", "mapped to use cases", BLUE, "lock"),
            CardData("WEEKLY", "CI/CD Backdoor", "FBI Geo Buys", "WhatsApp wipe",
                     "Headline threats", "span this week", GREEN, "globe"),
        ),
    ),
    "2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent": (
        "2026-03-25",
        (
            CardData("GUIDE", "Trivy Breach", "Detect Defend", "Microsoft brief",
                     "IR playbook for", "supply chain hit", BLUE, "patch"),
            CardData("SUPPLY", "TeamPCP Drops", "LiteLLM Backdoor", "v1.82.7 tainted",
                     "LLM gateway", "shipped poisoned build", RED, "code"),
            CardData("ADS", "Tax Scam Ads", "Bring Huawei Drv", "ScreenConnect RAT",
                     "Signed drivers", "disable endpoint EDR", GREEN, "chip"),
        ),
    ),
    "2026-03-26-Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI": (
        "2026-03-26",
        (
            CardData("K8S", "RBAC Bypass", "Hits Clusters", "CVE-2026-0421",
                     "Cilium and eBPF", "tighten policy", RED, "alert"),
            CardData("SUPPLY", "SLSA v1.1", "Plus SBOM Flow", "Hands-on recipe",
                     "End to end signed", "builds in practice", BLUE, "code"),
            CardData("AI RISK", "Agent Prompt", "New Attack Plays", "Defense in depth",
                     "Injection chains", "evolve weekly", GREEN, "bot"),
        ),
    ),
    "2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps": (
        "2026-03-27",
        (
            CardData("ZERO TRUST", "AWS IDC + SCP", "Reference Build", "Zero Trust guide",
                     "Identity center", "plus guardrails", BLUE, "lock"),
            CardData("FINOPS", "Spot Graviton", "Cut Cloud Bills", "Workload right-size",
                     "Elastic fleets", "pay off at scale", GREEN, "stack"),
            CardData("IAC", "Terraform Stacks", "Meet tfsec", "Scan automation",
                     "Policy as code", "locks deploys", RED, "patch"),
        ),
    ),
    "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day": (
        "2026-03-28",
        (
            CardData("AI FLAW", "Agent Framework", "Privilege Escape", "Microsoft analysis",
                     "Escalation path", "through agent hops", BLUE, "bot"),
            CardData("ZERO-DAY", "AWS ECS Hit", "Container Escape", "Host takeover risk",
                     "Runtime isolation", "fails for tenants", RED, "alert"),
            CardData("SUPPLY", "Harbor Images", "Poisoned Push", "Registry campaign",
                     "Malicious builds", "hit shared tags", GREEN, "code"),
        ),
    ),
    "2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain": (
        "2026-03-29",
        (
            CardData("RANSOM", "Ransom Gangs", "Go AI-Driven", "CISA advisory",
                     "Automated intrusion", "scales threat volume", RED, "bot"),
            CardData("LLM", "Jailbreak CVE", "Bypasses Safety", "CVE-2026-3291",
                     "Top models lose", "guardrail coverage", BLUE, "alert"),
            CardData("SUPPLY", "Helm Charts", "Poisoned Repo", "K8s deploy risk",
                     "Chart tampering", "hits cluster builds", GREEN, "code"),
        ),
    ),
    "2026-03-30-March_2026_Security_Digest_Monthly_Index": (
        "2026-03-30",
        (
            CardData("MARCH 2026", "Monthly Index", "Top Threat Map", "30+ digests linked",
                     "Headline CVEs", "and campaign waves", BLUE, "stack"),
            CardData("TRENDS", "Ransomware", "Supply Chain AI", "Three mega-themes",
                     "Agents weaponized", "across sectors", RED, "alert"),
            CardData("OPS", "CVE Patch Plan", "Cloud and K8s", "Priority ladder",
                     "Runbook ready", "for next wave", GREEN, "patch"),
        ),
    ),
    "2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT": (
        "2026-03-31",
        (
            CardData("AI FIX", "ChatGPT Leak", "Codex Token Bug", "OpenAI patches",
                     "Data exposure", "and token reuse", RED, "patch"),
            CardData("MALWARE", "DeepLoad Ships", "ClickFix WMI", "Browser creds gone",
                     "Persistence via", "WMI subscriptions", BLUE, "bot"),
            CardData("WEEKLY", "Telco Sleepers", "LLM Jailbreaks", "UK age gate fight",
                     "Week in review", "across policy and AI", GREEN, "globe"),
        ),
    ),
    "2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS": (
        "2026-04-01",
        (
            CardData("POLICY", "Android Dev ID", "Verify Rollout", "September deadline",
                     "Staged launch", "for signed builds", BLUE, "patch"),
            CardData("ZERO-DAY", "TrueConf Hit", "SEA Gov Targets", "In-the-wild chain",
                     "State networks", "breached via 0-day", RED, "alert"),
            CardData("COMPLY", "AWS Refresh", "ISO 27001 Guide", "2022 edition out",
                     "Compliance kit", "for cloud tenants", GREEN, "patch"),
        ),
    ),
    "2026-04-02-Tech_Security_Weekly_Digest_AI_Malware": (
        "2026-04-02",
        (
            CardData("CAMPAIGN", "CERT-UA Lure", "1M Email Blast", "AGEWHEEZE payload",
                     "State defender", "impersonated widely", RED, "globe"),
            CardData("SUPPLY", "Axios NPM Hit", "Microsoft Guide", "Incident cleanup",
                     "HTTP client", "compromised in JS ecosystem", BLUE, "code"),
            CardData("WIN", "WhatsApp VBS", "UAC Bypass Drop", "Microsoft warning",
                     "Messaging trick", "takes over Windows", GREEN, "bot"),
        ),
    ),
    "2026-04-03-Tech_Security_Weekly_Digest_CVE_Patch_AWS_AI": (
        "2026-04-03",
        (
            CardData("CRITICAL", "Next.js 766 Hit", "Creds Stolen", "CVE-2025-55182",
                     "Deploy vector", "breached at scale", RED, "alert"),
            CardData("PATCH", "Cisco IMC SSM", "9.8 CVSS Fix", "Remote takeover",
                     "Mgmt consoles", "patched in hurry", BLUE, "patch"),
            CardData("AI SEC", "AWS Agent Lab", "4 Core Principles", "Security playbook",
                     "Agentic AI apps", "hardened by design", GREEN, "lock"),
        ),
    ),
    "2026-04-04-Tech_Security_Weekly_Digest_Go_AI_Data_Security": (
        "2026-04-04",
        (
            CardData("APT", "TA416 Phish", "PlugX And OAuth", "EU gov targets",
                     "China-linked ops", "harvest tokens", RED, "globe"),
            CardData("LINUX", "Cron PHP Shell", "Cookie Control", "Microsoft brief",
                     "Persistence via", "Linux job queue", BLUE, "code"),
            CardData("PRIVACY", "LinkedIn Scrapes", "6K Chrome Exts", "Silent harvest",
                     "Extension telemetry", "hits pro network", GREEN, "stack"),
        ),
    ),
    "2026-04-05-Tech_Security_Weekly_Digest_AWS_AI_Security_Malware": (
        "2026-04-05",
        (
            CardData("COMPLY", "AWS LZA Kit", "Compliance Book", "Landing Zone ref",
                     "Universal config", "for audited stacks", GREEN, "patch"),
            CardData("SUPPLY", "Axios Takeover", "Fake Teams Fix", "Maintainer hijack",
                     "Bait message", "grants repo access", RED, "code"),
            CardData("PHISH", "Device Code", "Attacks 37x Up", "New kit surge",
                     "OAuth flows", "weaponized at scale", BLUE, "identity"),
        ),
    ),
}


POSTS: dict[str, tuple[str, tuple[CardData, CardData, CardData]]] = {
    **PHASE_A,
    **PHASE_B,
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

_CARD_LAYOUT = [
    (60, 345),
    (427, 346),
    (795, 345),
]


def _pill_width(label: str) -> int:
    return max(80, 8 * len(label) + 32)


def _render_card(translate_x: int, width: int, card: CardData) -> str:
    cx = width // 2
    icon_name = card.icon or card.palette.icon_name
    icon_svg = ICON_FUNCS[icon_name](card.palette.accent_id).format(cx=cx)
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


_FORBIDDEN_CHARS = "\u00b7\u2022\u2014\u201c\u201d\u2018\u2019"


def _validate_text(text: str, where: str) -> None:
    for ch in text:
        if "\uac00" <= ch <= "\ud7a3":
            raise ValueError(f"Korean character found in {where}: {text!r}")
        if ch in _FORBIDDEN_CHARS:
            raise ValueError(f"Forbidden char {ch!r} in {where}: {text!r}")


def _validate_card(basename: str, card: CardData) -> None:
    for field in (card.label, card.headline_1, card.headline_2, card.tag, card.desc_1, card.desc_2):
        _validate_text(field, basename)


def _regenerate_derivatives(basename: str) -> None:
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


def _iter_targets(phase: str) -> Iterable[str]:
    if phase == "a":
        return PHASE_A.keys()
    if phase == "b":
        return PHASE_B.keys()
    return POSTS.keys()


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate digest cover SVGs + derivatives.")
    parser.add_argument("--phase", choices=("a", "b", "all"), default="all",
                        help="Which wave of posts to refresh (default: all).")
    parser.add_argument("--skip-derivatives", action="store_true",
                        help="Only rewrite SVGs, skip og/card raster outputs.")
    args = parser.parse_args()

    targets = list(_iter_targets(args.phase))

    for basename in targets:
        date, cards = POSTS[basename]
        for c in cards:
            _validate_card(basename, c)
        svg = render_svg(date, cards)
        _validate_text(svg, basename)
        out = ASSETS_DIR / f"{basename}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"svg:  {out.name}")

    if args.skip_derivatives:
        return

    # Also refresh the reference derivatives if Phase A (or all) was rebuilt.
    derivative_targets = list(targets)
    if args.phase in ("a", "all") and REFERENCE_BASENAME not in derivative_targets:
        derivative_targets.append(REFERENCE_BASENAME)

    for base in derivative_targets:
        _regenerate_derivatives(base)
        print(f"derv: {base}")


if __name__ == "__main__":
    main()

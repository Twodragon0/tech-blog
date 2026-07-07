#!/usr/bin/env python3
"""Regenerate 15 weekly-digest SVG covers (Jan/Feb 2026) at L20 Hero+2-Card quality.

Reference visual style: ``assets/images/2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg``
and the 16 March covers built by ``scripts/upgrade_2026_03_16_31_to_l20_hero.py``.

Each cover has:
  - HERO LEFT panel: most-critical story with embedded visual + action tag.
  - TOP RIGHT panel: HIGH/02 story with visual + KPI card.
  - BOTTOM RIGHT panel: HIGH/03 story with visual + KPI card.
  - Real QR code bottom-right linking to the post URL.

Topics are hand-curated English headlines/subheadlines derived from each post's
title, excerpt, and H3 highlights. NO Korean characters and NO ellipsis.

Usage::

    python3 scripts/upgrade_2026_01_02_to_l20_hero.py

Writes SVG files to ``assets/images/`` and prints a summary.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.svg_l20_hero import render_l20_hero  # noqa: E402

ASSETS_DIR = REPO_ROOT / "assets" / "images"
URL_BASE = "https://tech.2twodragon.com/posts"


def _post_url(date_str_iso: str, slug: str) -> str:
    """Build canonical post URL: posts/YYYY/MM/DD/<slug>/."""
    y, m, d = date_str_iso.split("-")
    return f"{URL_BASE}/{y}/{m}/{d}/{slug}/"


# --- 15 configs ---
def cfg_2026_02_22() -> Dict:
    return {
        "filename": "2026-02-22-Tech_Security_Weekly_Digest_AI_Threat_Vulnerability_Security.svg",
        "date_str": "2026.02.22",
        "post_title": "Weekly digest 2026-02-22: AI threat actors hit FortiGate, Roundcube KEV, Claude Code Security",
        "url": _post_url("2026-02-22", "Tech_Security_Weekly_Digest_AI_Threat_Vulnerability_Security"),
        "hero": {
            "tag": "NATION STATE", "index": "01", "theme": "red", "visual": "hub_spoke",
            "headline": "FortiGate Mass Compromise",
            "subheadline": "AI-driven threat actor breaches 600+ devices across 55 countries",
            "kpi_value": "600+", "kpi_label": "DEVICES", "kpi_sub": "55 countries hit",
            "action": "ROTATE CREDS - HUNT IOCS NOW",
        },
        "top_right": {
            "tag": "KEV URGENT", "index": "02", "theme": "blue", "visual": "cve_chain",
            "headline": "Roundcube CISA KEV Add",
            "subheadline": "Two webmail flaws actively exploited / pre-auth chain",
            "kpi_value": "2", "kpi_label": "CVES", "kpi_sub": "added to KEV",
        },
        "bottom_right": {
            "tag": "DEFENSE", "index": "03", "theme": "amber", "visual": "code_injection",
            "headline": "Claude Code Security",
            "subheadline": "Anthropic launches AI-driven repo vulnerability scanner",
            "kpi_value": "GA", "kpi_label": "RELEASE", "kpi_sub": "agentic scanner",
        },
    }


def cfg_2026_02_21() -> Dict:
    return {
        "filename": "2026-02-21-Tech_Security_Weekly_Digest_Data_Rust_AI_Threat.svg",
        "date_str": "2026.02.21",
        "post_title": "Weekly digest 2026-02-21: Claude Code Security, Roundcube KEV, EC-Council AI certs",
        "url": _post_url("2026-02-21", "Tech_Security_Weekly_Digest_Data_Rust_AI_Threat"),
        "hero": {
            "tag": "AI DEFENSE", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "Claude Code Security GA",
            "subheadline": "Anthropic agent scans repos for CVEs and supply-chain risk",
            "kpi_value": "GA", "kpi_label": "LAUNCH", "kpi_sub": "agentic scanner",
            "action": "PILOT - GATE CI WITH AI SCAN",
        },
        "top_right": {
            "tag": "KEV URGENT", "index": "02", "theme": "blue", "visual": "cve_chain",
            "headline": "CISA Roundcube KEV",
            "subheadline": "Active exploitation in wild forces emergency patch order",
            "kpi_value": "2", "kpi_label": "CVES", "kpi_sub": "Roundcube KEV",
        },
        "bottom_right": {
            "tag": "WORKFORCE", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "EC-Council AI Cert Push",
            "subheadline": "Expanded AI-security cert track readies US security workforce",
            "kpi_value": "AI", "kpi_label": "CERT", "kpi_sub": "portfolio expand",
        },
    }


def cfg_2026_02_20() -> Dict:
    return {
        "filename": "2026-02-20-Tech_Security_Weekly_Digest_Gemini_AI_Supply_Chain_Kubernetes.svg",
        "date_str": "2026.02.20",
        "post_title": "Weekly digest 2026-02-20: PromptSpy Android, INTERPOL Red Card 2.0, Windows Admin Center",
        "url": _post_url("2026-02-20", "Tech_Security_Weekly_Digest_Gemini_AI_Supply_Chain_Kubernetes"),
        "hero": {
            "tag": "AI ABUSE", "index": "01", "theme": "red", "visual": "ai_agent_funnel",
            "headline": "PromptSpy Android Malware",
            "subheadline": "Abuses Gemini API to automate persistence on victim devices",
            "kpi_value": "GMNI", "kpi_label": "ABUSED", "kpi_sub": "AI persistence",
            "action": "BLOCK PROMPTSPY C2 NOW",
        },
        "top_right": {
            "tag": "LAW ENF", "index": "02", "theme": "blue", "visual": "hub_spoke",
            "headline": "INTERPOL Red Card 2.0",
            "subheadline": "Africa cybercrime takedown nets 651 arrests in joint op",
            "kpi_value": "651", "kpi_label": "ARRESTS", "kpi_sub": "Africa op",
        },
        "bottom_right": {
            "tag": "CRITICAL CVE", "index": "03", "theme": "amber", "visual": "cve_chain",
            "headline": "WAC CVE-2026-26119",
            "subheadline": "Windows Admin Center privilege escalation patched by MS",
            "kpi_value": "EoP", "kpi_label": "PATCH", "kpi_sub": "WAC fix",
        },
    }


def cfg_2026_02_17() -> Dict:
    return {
        "filename": "2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.svg",
        "date_str": "2026.02.17",
        "post_title": "Weekly digest 2026-02-17: Infostealer AI agent theft, password manager attacks, AWS defense",
        "url": _post_url("2026-02-17", "Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security"),
        "hero": {
            "tag": "INFOSTEALER", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "AI Agent Token Theft",
            "subheadline": "Infostealer drops target agent config files and gateway tokens",
            "kpi_value": "AI", "kpi_label": "TARGET", "kpi_sub": "agent gateways",
            "action": "ROTATE AGENT TOKENS NOW",
        },
        "top_right": {
            "tag": "HIGH", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "Password Manager Flaws",
            "subheadline": "25 recovery attacks hit Bitwarden, Dashlane, LastPass clouds",
            "kpi_value": "25", "kpi_label": "ATTACKS", "kpi_sub": "3 vendors hit",
        },
        "bottom_right": {
            "tag": "DEFENSE", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "AWS Serverless Defense",
            "subheadline": "AI-driven defense-in-depth pattern for serverless microservices",
            "kpi_value": "DiD", "kpi_label": "PATTERN", "kpi_sub": "AWS reference",
        },
    }


def cfg_2026_02_13() -> Dict:
    return {
        "filename": "2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg",
        "date_str": "2026.02.13",
        "post_title": "Weekly digest 2026-02-13: Gemini abuse recon, Lazarus npm/PyPI, Copilot Studio risks",
        "url": _post_url("2026-02-13", "Tech_Security_Weekly_Digest_AI_Go_Security_Agent"),
        "hero": {
            "tag": "NATION STATE", "index": "01", "theme": "red", "visual": "ai_agent_funnel",
            "headline": "Gemini Abuse Recon Ops",
            "subheadline": "Nation-state actors weaponize Gemini for recon and code-gen",
            "kpi_value": "APT", "kpi_label": "ACTOR", "kpi_sub": "Gemini abuse",
            "action": "MONITOR AI EGRESS NOW",
        },
        "top_right": {
            "tag": "SUPPLY CHAIN", "index": "02", "theme": "blue", "visual": "supply_chain_pipe",
            "headline": "Lazarus npm + PyPI",
            "subheadline": "DPRK-linked malicious packages target dev wallets and CI",
            "kpi_value": "DPRK", "kpi_label": "ACTOR", "kpi_sub": "npm + PyPI hit",
        },
        "bottom_right": {
            "tag": "AGENT RISK", "index": "03", "theme": "amber", "visual": "code_injection",
            "headline": "Copilot Studio Top 10",
            "subheadline": "Agent security risks ranked from prompt-inject to data leak",
            "kpi_value": "10", "kpi_label": "RISKS", "kpi_sub": "Copilot Studio",
        },
    }


def cfg_2026_02_12() -> Dict:
    return {
        "filename": "2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent.svg",
        "date_str": "2026.02.12",
        "post_title": "Weekly digest 2026-02-12: Outlook addin creds, APT36 SideCopy RAT, 60+ vendor patches",
        "url": _post_url("2026-02-12", "Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent"),
        "hero": {
            "tag": "CRED THEFT", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "Outlook Add-In Theft",
            "subheadline": "Malicious Outlook addin steals creds via session token hook",
            "kpi_value": "M365", "kpi_label": "TARGET", "kpi_sub": "Outlook addin",
            "action": "BLOCK ADDIN INSTALLS",
        },
        "top_right": {
            "tag": "APT", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "APT36 SideCopy RAT",
            "subheadline": "Cross-platform RAT campaign targets Windows, Linux, macOS",
            "kpi_value": "3 OS", "kpi_label": "PLATFORM", "kpi_sub": "RAT campaign",
        },
        "bottom_right": {
            "tag": "PATCH WAVE", "index": "03", "theme": "amber", "visual": "cve_chain",
            "headline": "60+ Vendor Patch Tuesday",
            "subheadline": "Largest synchronized patch wave hits OS and infra vendors",
            "kpi_value": "60+", "kpi_label": "VENDORS", "kpi_sub": "patch wave",
        },
    }


def cfg_2026_02_11() -> Dict:
    return {
        "filename": "2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg",
        "date_str": "2026.02.11",
        "post_title": "Weekly digest 2026-02-11: NK LinkedIn infiltration, Reynolds ransomware, Fortinet CVE",
        "url": _post_url("2026-02-11", "Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI"),
        "hero": {
            "tag": "RANSOMWARE", "index": "01", "theme": "red", "visual": "ransomware_lock",
            "headline": "Reynolds BYOVD Ransomware",
            "subheadline": "Embedded vulnerable driver disables EDR before encryption",
            "kpi_value": "BYOVD", "kpi_label": "BYPASS", "kpi_sub": "EDR killed",
            "action": "BLOCK SIGNED VULN DRIVERS",
        },
        "top_right": {
            "tag": "NATION STATE", "index": "02", "theme": "blue", "visual": "data_exfil",
            "headline": "DPRK LinkedIn Lure",
            "subheadline": "Fake recruiters infiltrate firms posing as senior IT pros",
            "kpi_value": "DPRK", "kpi_label": "ACTOR", "kpi_sub": "LinkedIn lure",
        },
        "bottom_right": {
            "tag": "CRITICAL CVE", "index": "03", "theme": "amber", "visual": "cve_chain",
            "headline": "Fortinet CVE-2026-21643",
            "subheadline": "Critical SQLi in FortiOS gets emergency vendor patch",
            "kpi_value": "SQLi", "kpi_label": "CVE", "kpi_sub": "FortiOS critical",
        },
    }


def cfg_2026_02_08() -> Dict:
    return {
        "filename": "2026-02-08-Tech_Security_Weekly_Digest_AI_Ransomware_Data.svg",
        "date_str": "2026.02.08",
        "post_title": "Weekly digest 2026-02-08: Russia Signal phishing, BlackField ransomware, zero-trust data",
        "url": _post_url("2026-02-08", "Tech_Security_Weekly_Digest_AI_Ransomware_Data"),
        "hero": {
            "tag": "NATION STATE", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "Russia Signal Phishing",
            "subheadline": "BfV and BSI warn on targeted phishing of officials and press",
            "kpi_value": "BSI", "kpi_label": "ALERT", "kpi_sub": "Signal lure",
            "action": "ENABLE SIGNAL VERIFY PIN",
        },
        "top_right": {
            "tag": "RANSOMWARE", "index": "02", "theme": "blue", "visual": "ransomware_lock",
            "headline": "BlackField Code Reuse",
            "subheadline": "LockBit and Conti leaked code recycled into new variant",
            "kpi_value": "2", "kpi_label": "FAMILIES", "kpi_sub": "code recycled",
        },
        "bottom_right": {
            "tag": "ARCHITECTURE", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "Zero-Trust Data Strategy",
            "subheadline": "Data-centric controls beat perimeter for ransomware blast",
            "kpi_value": "ZT", "kpi_label": "DATA", "kpi_sub": "ABAC + crypto",
        },
    }


def cfg_2026_02_07() -> Dict:
    return {
        "filename": "2026-02-07-Tech_Security_Weekly_Digest_AI_Malware_Go_Security.svg",
        "date_str": "2026.02.07",
        "post_title": "Weekly digest 2026-02-07: TGR-STA-1030 APT, DKnife AitM, dYdX npm/PyPI supply chain",
        "url": _post_url("2026-02-07", "Tech_Security_Weekly_Digest_AI_Malware_Go_Security"),
        "hero": {
            "tag": "APT", "index": "01", "theme": "red", "visual": "hub_spoke",
            "headline": "TGR-STA-1030 APT Sweep",
            "subheadline": "Asian state-backed group breaches 70+ orgs across 37 nations",
            "kpi_value": "37", "kpi_label": "COUNTRIES", "kpi_sub": "70+ orgs hit",
            "action": "PATCH VPN - HUNT IOCS NOW",
        },
        "top_right": {
            "tag": "AITM", "index": "02", "theme": "blue", "visual": "data_exfil",
            "headline": "DKnife AitM Framework",
            "subheadline": "China-linked toolkit hijacks TLS at edge router layer",
            "kpi_value": "TLS", "kpi_label": "HIJACK", "kpi_sub": "router AitM",
        },
        "bottom_right": {
            "tag": "SUPPLY CHAIN", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "dYdX npm + PyPI Drop",
            "subheadline": "Malicious packages exfil dev wallets and CI build secrets",
            "kpi_value": "2", "kpi_label": "REGISTRIES", "kpi_sub": "npm + PyPI",
        },
    }


def cfg_2026_02_05() -> Dict:
    return {
        "filename": "2026-02-05-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.svg",
        "date_str": "2026.02.05",
        "post_title": "Weekly digest 2026-02-05: n8n CVE-2026-25049, NGINX hijack, AsyncRAT IPFS",
        "url": _post_url("2026-02-05", "Tech_Security_Weekly_Digest_CVE_AI_Malware_Go"),
        "hero": {
            "tag": "CRITICAL CVE", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "n8n CVE-2026-25049",
            "subheadline": "Malicious workflows execute system commands on n8n hosts",
            "kpi_value": "RCE", "kpi_label": "STATUS", "kpi_sub": "system commands",
            "action": "P0 - PATCH n8n NOW",
        },
        "top_right": {
            "tag": "TRAFFIC HIJACK", "index": "02", "theme": "blue", "visual": "hub_spoke",
            "headline": "NGINX Config Hijack",
            "subheadline": "Tampered NGINX configs hijack web traffic at large scale",
            "kpi_value": "NGINX", "kpi_label": "TARGET", "kpi_sub": "config tamper",
        },
        "bottom_right": {
            "tag": "RAT CAMPAIGN", "index": "03", "theme": "amber", "visual": "data_exfil",
            "headline": "AsyncRAT via IPFS",
            "subheadline": "DEAD#VAX phishing chains ride IPFS to deliver AsyncRAT",
            "kpi_value": "IPFS", "kpi_label": "VECTOR", "kpi_sub": "AsyncRAT chain",
        },
    }


def cfg_2026_02_04() -> Dict:
    return {
        "filename": "2026-02-04-Tech_Security_Weekly_Digest_AI_Docker_Data_Go.svg",
        "date_str": "2026.02.04",
        "post_title": "Weekly digest 2026-02-04: Metro4Shell RCE, AWS IdC multi-region, Docker 3Cs framework",
        "url": _post_url("2026-02-04", "Tech_Security_Weekly_Digest_AI_Docker_Data_Go"),
        "hero": {
            "tag": "CRITICAL CVE", "index": "01", "theme": "red", "visual": "cve_chain",
            "headline": "Metro4Shell RCE 9.8",
            "subheadline": "React Native CLI Metro server allows pre-auth RCE in wild",
            "kpi_value": "9.8", "kpi_label": "CVSS", "kpi_sub": "Metro RCE",
            "action": "P0 - PATCH METRO CLI NOW",
        },
        "top_right": {
            "tag": "IDENTITY", "index": "02", "theme": "blue", "visual": "supply_chain_pipe",
            "headline": "AWS IdC Multi-Region",
            "subheadline": "Identity Center adds replication for DR and data sovereignty",
            "kpi_value": "Multi", "kpi_label": "REGION", "kpi_sub": "IdC replication",
        },
        "bottom_right": {
            "tag": "FRAMEWORK", "index": "03", "theme": "amber", "visual": "ai_agent_funnel",
            "headline": "Docker 3Cs AI Agents",
            "subheadline": "Container, Credential, Code: Docker AI agent guardrails",
            "kpi_value": "3Cs", "kpi_label": "MODEL", "kpi_sub": "Docker agents",
        },
    }


def cfg_2026_02_01() -> Dict:
    return {
        "filename": "2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.svg",
        "date_str": "2026.02.01",
        "post_title": "Weekly digest 2026-02-01: AISLE OpenSSL 12 zero-days, OWASP Agentic AI, Fortinet SSO",
        "url": _post_url("2026-02-01", "Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet"),
        "hero": {
            "tag": "HISTORIC FIRST", "index": "01", "theme": "red", "visual": "cve_chain",
            "headline": "AISLE Finds 12 OpenSSL 0-Days",
            "subheadline": "AI system discovers all 12 fresh OpenSSL flaws / first-ever",
            "kpi_value": "12", "kpi_label": "ZERO-DAY", "kpi_sub": "AISLE coverage",
            "action": "PATCH OPENSSL ASAP",
        },
        "top_right": {
            "tag": "FRAMEWORK", "index": "02", "theme": "blue", "visual": "ai_agent_funnel",
            "headline": "OWASP Agentic AI",
            "subheadline": "OWASP ships Top 10 risk framework for autonomous agents",
            "kpi_value": "Top 10", "kpi_label": "OWASP", "kpi_sub": "Agentic AI",
        },
        "bottom_right": {
            "tag": "ZERO-DAY", "index": "03", "theme": "amber", "visual": "data_exfil",
            "headline": "Fortinet FortiCloud SSO",
            "subheadline": "Zero-day SSO bypass leaks tenant tokens / patch shipped",
            "kpi_value": "SSO", "kpi_label": "BYPASS", "kpi_sub": "FortiCloud 0day",
        },
    }


def cfg_2026_01_29() -> Dict:
    return {
        "filename": "2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.svg",
        "date_str": "2026.01.29",
        "post_title": "Weekly digest 2026-01-29: n8n RCE 9.9, D-Link zero-day, Kubernetes AI agent security",
        "url": _post_url("2026-01-29", "Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent"),
        "hero": {
            "tag": "CRITICAL RCE", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "n8n CVE-2026-1470",
            "subheadline": "JS AST sandbox escape via Function constructor enables RCE",
            "kpi_value": "9.9", "kpi_label": "CVSS", "kpi_sub": "sandbox escape",
            "action": "P0 - PATCH n8n NOW",
        },
        "top_right": {
            "tag": "ZERO-DAY", "index": "02", "theme": "blue", "visual": "hub_spoke",
            "headline": "D-Link CVE-2026-0625",
            "subheadline": "End-of-life routers exploited in wild / no vendor patch",
            "kpi_value": "EoL", "kpi_label": "DEVICES", "kpi_sub": "D-Link 0day",
        },
        "bottom_right": {
            "tag": "AGENT RISK", "index": "03", "theme": "amber", "visual": "ai_agent_funnel",
            "headline": "K8s AI Agent Threats",
            "subheadline": "AI agent tooling expands K8s attack surface and policy gaps",
            "kpi_value": "K8s", "kpi_label": "SCOPE", "kpi_sub": "agent attack surf",
        },
    }


def cfg_2026_01_25() -> Dict:
    return {
        "filename": "2026-01-25-Tech_Security_Weekly_Digest_VMware_vCenter_Fortinet_SSO_Sandworm_DynoWiper_AI_Agents.svg",
        "date_str": "2026.01.25",
        "post_title": "Weekly digest 2026-01-25: VMware vCenter KEV, Fortinet SSO bypass, Sandworm DynoWiper",
        "url": _post_url("2026-01-25", "Tech_Security_Weekly_Digest_VMware_vCenter_Fortinet_SSO_Sandworm_DynoWiper_AI_Agents"),
        "hero": {
            "tag": "KEV URGENT", "index": "01", "theme": "red", "visual": "cve_chain",
            "headline": "VMware vCenter CVE-2024-37079",
            "subheadline": "CISA KEV add confirms active exploitation of vCenter RCE",
            "kpi_value": "KEV", "kpi_label": "STATUS", "kpi_sub": "active exploit",
            "action": "P0 - PATCH vCENTER NOW",
        },
        "top_right": {
            "tag": "ZERO-DAY", "index": "02", "theme": "blue", "visual": "data_exfil",
            "headline": "Fortinet SSO Bypass",
            "subheadline": "Patched FortiGate fleets still leak tokens via SSO 0-day",
            "kpi_value": "SSO", "kpi_label": "BYPASS", "kpi_sub": "FortiCloud",
        },
        "bottom_right": {
            "tag": "WIPER", "index": "03", "theme": "amber", "visual": "ransomware_lock",
            "headline": "Sandworm DynoWiper",
            "subheadline": "Russia GRU APT hits Polish power grid with destructive wiper",
            "kpi_value": "GRU", "kpi_label": "ACTOR", "kpi_sub": "Poland grid",
        },
    }


def cfg_2026_01_23() -> Dict:
    return {
        "filename": "2026-01-23-Tech_Security_Weekly_Digest_Microsoft_AitM_Phishing_Agentic_AI_Zero_Trust_OpenAI_PostgreSQL.svg",
        "date_str": "2026.01.23",
        "post_title": "Weekly digest 2026-01-23: Microsoft AitM phishing, Agentic AI Zero Trust, OpenAI Postgres",
        "url": _post_url("2026-01-23", "Tech_Security_Weekly_Digest_Microsoft_AitM_Phishing_Agentic_AI_Zero_Trust_OpenAI_PostgreSQL"),
        "hero": {
            "tag": "AITM PHISH", "index": "01", "theme": "red", "visual": "hub_spoke",
            "headline": "MS AitM Energy Phish",
            "subheadline": "Multi-stage AitM and BEC abuse SharePoint to hit energy firms",
            "kpi_value": "AitM", "kpi_label": "VECTOR", "kpi_sub": "BEC + SharePoint",
            "action": "FORCE FIDO2 - REVOKE TOKENS",
        },
        "top_right": {
            "tag": "ZERO TRUST", "index": "02", "theme": "blue", "visual": "ai_agent_funnel",
            "headline": "Agentic AI Zero Trust",
            "subheadline": "HashiCorp NHI strategy scopes per-call agent identity",
            "kpi_value": "NHI", "kpi_label": "MODEL", "kpi_sub": "agent identity",
        },
        "bottom_right": {
            "tag": "SCALE", "index": "03", "theme": "amber", "visual": "data_exfil",
            "headline": "OpenAI Postgres 800M",
            "subheadline": "ChatGPT serves 800M users on a tuned PostgreSQL backbone",
            "kpi_value": "800M", "kpi_label": "USERS", "kpi_sub": "Postgres scale",
        },
    }


CONFIGS: List[Callable[[], Dict]] = [
    cfg_2026_02_22,
    cfg_2026_02_21,
    cfg_2026_02_20,
    cfg_2026_02_17,
    cfg_2026_02_13,
    cfg_2026_02_12,
    cfg_2026_02_11,
    cfg_2026_02_08,
    cfg_2026_02_07,
    cfg_2026_02_05,
    cfg_2026_02_04,
    cfg_2026_02_01,
    cfg_2026_01_29,
    cfg_2026_01_25,
    cfg_2026_01_23,
]


def _validate(svg_path: Path) -> Tuple[bool, str]:
    """Parse the SVG and check no Korean / no ellipsis."""
    try:
        ET.parse(svg_path)
    except ET.ParseError as e:
        return False, f"XML parse error: {e}"
    raw = svg_path.read_text(encoding="utf-8")
    for ch in raw:
        if "\uAC00" <= ch <= "\uD7A3":
            return False, "contains Korean characters"
    if "..." in raw or "\u2026" in raw:
        return False, "contains ellipsis"
    return True, "ok"


def main() -> int:
    rows = []
    for fn in CONFIGS:
        cfg = fn()
        svg = render_l20_hero(
            date_str=cfg["date_str"],
            hero=cfg["hero"],
            top_right=cfg["top_right"],
            bottom_right=cfg["bottom_right"],
            url=cfg["url"],
            post_title=cfg["post_title"],
        )
        out = ASSETS_DIR / cfg["filename"]
        out.write_text(svg, encoding="utf-8")
        ok, msg = _validate(out)
        size_kb = out.stat().st_size / 1024
        line_count = svg.count("\n") + 1
        rows.append((cfg["filename"], size_kb, line_count, ok, msg))

    print("=" * 100)
    print(f"{'filename':<82} {'KB':>6} {'lines':>6} {'status':>6}")
    print("-" * 100)
    all_ok = True
    for name, kb, lines, ok, msg in rows:
        status = "OK" if ok else "FAIL"
        print(f"{name:<82} {kb:>6.1f} {lines:>6} {status:>6}")
        if not ok:
            print(f"  -> {msg}")
            all_ok = False
    print("=" * 100)
    print(f"Total: {len(rows)} files  /  validation: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

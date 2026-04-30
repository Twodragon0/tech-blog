#!/usr/bin/env python3
"""Regenerate 16 weekly-digest SVG covers (2026-03-16..2026-03-31) at L20 quality.

Reference visual style: ``assets/images/2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg``.
Each cover has:
  - HERO LEFT panel: most-critical story with embedded visual + action tag.
  - TOP RIGHT panel: HIGH/02 story with visual + KPI card.
  - BOTTOM RIGHT panel: HIGH/03 story with visual + KPI card.
  - Real QR code bottom-right linking to the post URL.

Usage::

    python3 scripts/upgrade_2026_03_16_31_to_l20_hero.py

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


# --- 16 configs ---
def cfg_2026_03_16_a() -> Dict:
    return {
        "filename": "2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.svg",
        "date_str": "2026.03.16",
        "post_title": "Weekly digest 2026-03-16: AI red-team OSS, Bedrock multi-agent, Aave Shield",
        "url": _post_url("2026-03-16", "Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update"),
        "hero": {
            "tag": "OSS RELEASE", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "AI Agent Red-Team OSS",
            "subheadline": "Open-source toolkit for LLM jailbreak and prompt-injection tests",
            "kpi_value": "v1.0", "kpi_label": "RELEASE", "kpi_sub": "MIT licensed",
            "action": "ADOPT - HARDEN AI AGENTS NOW",
        },
        "top_right": {
            "tag": "HIGH", "index": "02", "theme": "blue", "visual": "hub_spoke",
            "headline": "AWS Bedrock Multi-Agent",
            "subheadline": "Coordinated agent runtime ships with isolation guardrails",
            "kpi_value": "GA", "kpi_label": "STATUS", "kpi_sub": "us-east + eu-west",
        },
        "bottom_right": {
            "tag": "MEDIUM", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "Aave Shield DeFi Launch",
            "subheadline": "On-chain insurance covers smart-contract exploits",
            "kpi_value": "$50M", "kpi_label": "TVL", "kpi_sub": "first 24h",
        },
    }


def cfg_2026_03_16_b() -> Dict:
    return {
        "filename": "2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin.svg",
        "date_str": "2026.03.16",
        "post_title": "Weekly digest 2026-03-16: LIBRA forensic, stablecoin rules, crypto trends",
        "url": _post_url("2026-03-16", "Tech_Security_Weekly_Digest_AI_Bitcoin"),
        "hero": {
            "tag": "FORENSIC", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "Argentina LIBRA Forensic",
            "subheadline": "On-chain trail maps insider rug-pull wallet flow",
            "kpi_value": "$87M", "kpi_label": "DRAINED", "kpi_sub": "in 4 hours",
            "action": "FREEZE SUSPECT WALLETS",
        },
        "top_right": {
            "tag": "HIGH", "index": "02", "theme": "blue", "visual": "supply_chain_pipe",
            "headline": "Stablecoin Regulation",
            "subheadline": "US Senate moves bill mandating reserve attestation",
            "kpi_value": "60d", "kpi_label": "DEADLINE", "kpi_sub": "issuer audit",
        },
        "bottom_right": {
            "tag": "MEDIUM", "index": "03", "theme": "amber", "visual": "hub_spoke",
            "headline": "Crypto Market Trends",
            "subheadline": "BTC ETF inflows hit record while alt-coin volatility cools",
            "kpi_value": "$3.2B", "kpi_label": "INFLOW", "kpi_sub": "weekly net",
        },
    }


def cfg_2026_03_17() -> Dict:
    return {
        "filename": "2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet.svg",
        "date_str": "2026.03.17",
        "post_title": "Weekly digest 2026-03-17: GlassWorm GitHub theft, Chrome 0-day, router botnet",
        "url": _post_url("2026-03-17", "Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet"),
        "hero": {
            "tag": "TOKEN THEFT", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "GlassWorm Token Theft",
            "subheadline": "Malicious npm package siphons GitHub PATs from CI runners",
            "kpi_value": "12k+", "kpi_label": "AFFECTED", "kpi_sub": "repos compromised",
            "action": "ROTATE TOKENS - AUDIT CI",
        },
        "top_right": {
            "tag": "ZERO-DAY", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "Chrome Zero-Day Patch",
            "subheadline": "V8 type-confusion exploited in the wild  /  CVSS 8.8",
            "kpi_value": "8.8", "kpi_label": "CVSS", "kpi_sub": "patch upstream",
        },
        "bottom_right": {
            "tag": "BOTNET", "index": "03", "theme": "amber", "visual": "hub_spoke",
            "headline": "Router Botnet Threats",
            "subheadline": "SOHO router malware fleet rents DDoS to highest bidder",
            "kpi_value": "85k", "kpi_label": "NODES", "kpi_sub": "global mesh",
        },
    }


def cfg_2026_03_18() -> Dict:
    return {
        "filename": "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.svg",
        "date_str": "2026.03.18",
        "post_title": "Weekly digest 2026-03-18: Bedrock DNS leak, LeakNet ClickFix, GKE inference",
        "url": _post_url("2026-03-18", "Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware"),
        "hero": {
            "tag": "DATA LEAK", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "Bedrock LangSmith DNS Leak",
            "subheadline": "Inference traffic egresses outside VPC private DNS scope",
            "kpi_value": "3", "kpi_label": "PRODUCTS", "kpi_sub": "Bedrock LangSmith SGLang",
            "action": "PATCH PRIVATE DNS NOW",
        },
        "top_right": {
            "tag": "RANSOMWARE", "index": "02", "theme": "blue", "visual": "ransomware_lock",
            "headline": "LeakNet ClickFix Deno",
            "subheadline": "ClickFix lure delivers Deno-based loader to Windows hosts",
            "kpi_value": "Deno", "kpi_label": "LOADER", "kpi_sub": "TS runtime abuse",
        },
        "bottom_right": {
            "tag": "INFRA", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "GKE Inference Gateway",
            "subheadline": "Multi-cluster inference gateway adds tenant key scoping",
            "kpi_value": "GA", "kpi_label": "STATUS", "kpi_sub": "1.31+ clusters",
        },
    }


def cfg_2026_03_19() -> Dict:
    return {
        "filename": "2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.svg",
        "date_str": "2026.03.19",
        "post_title": "Weekly digest 2026-03-19: NK $300M sanction, Cisco FMC 9.8, telnetd RCE",
        "url": _post_url("2026-03-19", "Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch"),
        "hero": {
            "tag": "CRITICAL PATCH", "index": "01", "theme": "red", "visual": "cve_chain",
            "headline": "Cisco FMC CVE-2026-20131",
            "subheadline": "Auth bypass in Firepower Management Center  /  CVSS 9.8",
            "kpi_value": "9.8", "kpi_label": "CVSS", "kpi_sub": "auth bypass",
            "action": "P0 - PATCH FMC NOW",
        },
        "top_right": {
            "tag": "HIGH", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "Telnetd CVE-2026-32746",
            "subheadline": "Root RCE in inetutils telnetd  /  affects 23 vendor builds",
            "kpi_value": "23", "kpi_label": "VENDORS", "kpi_sub": "root RCE chain",
        },
        "bottom_right": {
            "tag": "SANCTION", "index": "03", "theme": "amber", "visual": "data_exfil",
            "headline": "NK IT Workers Sanctioned",
            "subheadline": "Treasury hits 6 fronts laundering remote-dev paychecks",
            "kpi_value": "$300M", "kpi_label": "SEIZED", "kpi_sub": "OFAC action",
        },
    }


def cfg_2026_03_20() -> Dict:
    return {
        "filename": "2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat.svg",
        "date_str": "2026.03.20",
        "post_title": "Weekly digest 2026-03-20: Speagle infostealer, BYOVD EDR killer, Kyverno",
        "url": _post_url("2026-03-20", "Tech_Security_Weekly_Digest_Malware_Data_Security_Threat"),
        "hero": {
            "tag": "INFOSTEALER", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "Speagle Infostealer",
            "subheadline": "Targets browser cookies, MFA seeds, and crypto wallets",
            "kpi_value": "47", "kpi_label": "BROWSERS", "kpi_sub": "cookie targets",
            "action": "BLOCK C2 - HUNT IOCS NOW",
        },
        "top_right": {
            "tag": "EDR BYPASS", "index": "02", "theme": "blue", "visual": "container_escape",
            "headline": "BYOVD EDR Killer",
            "subheadline": "Signed driver loaded to disable EDR before deployment",
            "kpi_value": "5+", "kpi_label": "VENDORS", "kpi_sub": "EDR products hit",
        },
        "bottom_right": {
            "tag": "TOOLING", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "Kyverno AI Coding Agent",
            "subheadline": "Policy guardrails monitor AI-generated K8s manifests",
            "kpi_value": "v1.13", "kpi_label": "RELEASE", "kpi_sub": "AI mode opt-in",
        },
    }


def cfg_2026_03_21() -> Dict:
    return {
        "filename": "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.svg",
        "date_str": "2026.03.21",
        "post_title": "Weekly digest 2026-03-21: Trivy CI compromise, Langflow RCE, Android sideload",
        "url": _post_url("2026-03-21", "Tech_Security_Weekly_Digest_Security_CVE_AI_Malware"),
        "hero": {
            "tag": "SUPPLY CHAIN", "index": "01", "theme": "red", "visual": "supply_chain_pipe",
            "headline": "Trivy CI/CD Compromise",
            "subheadline": "Tampered scanner image leaks repo secrets to attacker C2",
            "kpi_value": "1.55", "kpi_label": "VERSION", "kpi_sub": "tagged poisoned",
            "action": "PIN IMAGES - VERIFY DIGESTS",
        },
        "top_right": {
            "tag": "CRITICAL RCE", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "Langflow Critical RCE",
            "subheadline": "Unauthenticated RCE via /api/v1/validate code-eval path",
            "kpi_value": "9.8", "kpi_label": "CVSS", "kpi_sub": "no auth required",
        },
        "bottom_right": {
            "tag": "DEFENSE", "index": "03", "theme": "amber", "visual": "container_escape",
            "headline": "Android Sideload Guard",
            "subheadline": "Play Protect blocks sideloaded apps without verified publisher",
            "kpi_value": "16+", "kpi_label": "ANDROID", "kpi_sub": "default-on",
        },
    }


def cfg_2026_03_22() -> Dict:
    return {
        "filename": "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg",
        "date_str": "2026.03.22",
        "post_title": "Weekly digest 2026-03-22: Signal phishing, Oracle IdM 9.8, Trivy + Apple KEV",
        "url": _post_url("2026-03-22", "Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple"),
        "hero": {
            "tag": "CRITICAL PATCH", "index": "01", "theme": "red", "visual": "cve_chain",
            "headline": "Oracle IdM CVE-2026-31201",
            "subheadline": "Pre-auth RCE in Identity Manager  /  CVSS 9.8",
            "kpi_value": "9.8", "kpi_label": "CVSS", "kpi_sub": "pre-auth RCE",
            "action": "P0 - PATCH ORACLE IDM",
        },
        "top_right": {
            "tag": "PHISHING", "index": "02", "theme": "blue", "visual": "data_exfil",
            "headline": "Signal WhatsApp Phish",
            "subheadline": "Spear-phishing kits hijack secure-chat session pairing",
            "kpi_value": "2", "kpi_label": "TARGETS", "kpi_sub": "Signal + WhatsApp",
        },
        "bottom_right": {
            "tag": "KEV", "index": "03", "theme": "amber", "visual": "code_injection",
            "headline": "Trivy + Apple KEV",
            "subheadline": "CanisterWorm worm joins CISA KEV with Apple webkit chain",
            "kpi_value": "3", "kpi_label": "CVES", "kpi_sub": "added to KEV",
        },
    }


def cfg_2026_03_23() -> Dict:
    return {
        "filename": "2026-03-23-Tech_Security_Weekly_Digest_Ransomware.svg",
        "date_str": "2026.03.23",
        "post_title": "Weekly digest 2026-03-23: Gentlemen ransomware, zero-trust visibility, EQST",
        "url": _post_url("2026-03-23", "Tech_Security_Weekly_Digest_Ransomware"),
        "hero": {
            "tag": "RANSOMWARE", "index": "01", "theme": "red", "visual": "ransomware_lock",
            "headline": "Gentlemen Ransomware",
            "subheadline": "Spread via Veeam backup creds harvested from prior breach",
            "kpi_value": "32", "kpi_label": "VICTIMS", "kpi_sub": "in 7 days",
            "action": "PATCH VEEAM - ROTATE CREDS",
        },
        "top_right": {
            "tag": "ZERO TRUST", "index": "02", "theme": "blue", "visual": "hub_spoke",
            "headline": "Network Visibility Gap",
            "subheadline": "Telemetry blind spots delay ransomware containment by days",
            "kpi_value": "73%", "kpi_label": "BLINDSPOT", "kpi_sub": "east-west traffic",
        },
        "bottom_right": {
            "tag": "INTEL", "index": "03", "theme": "amber", "visual": "data_exfil",
            "headline": "EQST Threat Intelligence",
            "subheadline": "Quarterly report flags Korea-targeted lateral-movement TTPs",
            "kpi_value": "Q1", "kpi_label": "REPORT", "kpi_sub": "EQST 2026",
        },
    }


def cfg_2026_03_24() -> Dict:
    return {
        "filename": "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg",
        "date_str": "2026.03.24",
        "post_title": "Weekly digest 2026-03-24: NK VS Code malware, AWS IAM design, Bedrock SecOps",
        "url": _post_url("2026-03-24", "Tech_Security_Weekly_Digest_Malware_Data_AWS_AI"),
        "hero": {
            "tag": "NATION STATE", "index": "01", "theme": "red", "visual": "code_injection",
            "headline": "NK VS Code Malware",
            "subheadline": "Tasks.json runs payload via launch.json on devs opening repo",
            "kpi_value": "DPRK", "kpi_label": "ACTOR", "kpi_sub": "Lazarus tooling",
            "action": "AUDIT REPO TASK FILES",
        },
        "top_right": {
            "tag": "DESIGN", "index": "02", "theme": "blue", "visual": "supply_chain_pipe",
            "headline": "AWS IAM Policy Design",
            "subheadline": "Org-wide SCP boundaries plus session tag deny pattern",
            "kpi_value": "SCP", "kpi_label": "PATTERN", "kpi_sub": "deny by default",
        },
        "bottom_right": {
            "tag": "AUTOMATION", "index": "03", "theme": "amber", "visual": "ai_agent_funnel",
            "headline": "Bedrock SecOps Agent",
            "subheadline": "Routine triage automated by guarded Bedrock agent runtime",
            "kpi_value": "60%", "kpi_label": "TRIAGE", "kpi_sub": "auto-handled",
        },
    }


def cfg_2026_03_25() -> Dict:
    return {
        "filename": "2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent.svg",
        "date_str": "2026.03.25",
        "post_title": "Weekly digest 2026-03-25: Trivy supply breach, LiteLLM backdoor, EDR-bypass",
        "url": _post_url("2026-03-25", "Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent"),
        "hero": {
            "tag": "SUPPLY CHAIN", "index": "01", "theme": "red", "visual": "supply_chain_pipe",
            "headline": "Trivy Supply-Chain Breach",
            "subheadline": "Maintainer pipeline hijack signs malicious release tags",
            "kpi_value": "2", "kpi_label": "TAGS", "kpi_sub": "1.55-1.55.1",
            "action": "PIN DIGEST - REVOKE KEYS",
        },
        "top_right": {
            "tag": "BACKDOOR", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "LiteLLM 1.82.7-8 Backdoor",
            "subheadline": "Rogue maintainer commit exfils keys via telemetry hook",
            "kpi_value": "1.82", "kpi_label": "VERSION", "kpi_sub": ".7 and .8 hot",
        },
        "bottom_right": {
            "tag": "EDR BYPASS", "index": "03", "theme": "amber", "visual": "container_escape",
            "headline": "EDR-bypass ScreenConnect",
            "subheadline": "Signed RMM tool used to deploy payload past Defender",
            "kpi_value": "RMM", "kpi_label": "VECTOR", "kpi_sub": "ScreenConnect abused",
        },
    }


def cfg_2026_03_26() -> Dict:
    return {
        "filename": "2026-03-26-Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI.svg",
        "date_str": "2026.03.26",
        "post_title": "Weekly digest 2026-03-26: K8s RBAC bypass, SLSA SBOM, AI prompt-injection",
        "url": _post_url("2026-03-26", "Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI"),
        "hero": {
            "tag": "K8S BYPASS", "index": "01", "theme": "red", "visual": "container_escape",
            "headline": "K8s RBAC Bypass + Cilium",
            "subheadline": "eBPF policy gap lets sidecar escalate to node uid 0",
            "kpi_value": "1.31", "kpi_label": "VERSIONS", "kpi_sub": "1.30-1.31 hit",
            "action": "UPGRADE - DENY RAW ESCAPE",
        },
        "top_right": {
            "tag": "SUPPLY CHAIN", "index": "02", "theme": "blue", "visual": "supply_chain_pipe",
            "headline": "SLSA SBOM Adoption",
            "subheadline": "L3 attestation now required by major Linux distro mirrors",
            "kpi_value": "L3", "kpi_label": "SLSA", "kpi_sub": "tier required",
        },
        "bottom_right": {
            "tag": "DEFENSE", "index": "03", "theme": "amber", "visual": "ai_agent_funnel",
            "headline": "AI Prompt-Injection Defense",
            "subheadline": "Pattern library blocks indirect injections from web context",
            "kpi_value": "94%", "kpi_label": "BLOCK", "kpi_sub": "inj test set",
        },
    }


def cfg_2026_03_27() -> Dict:
    return {
        "filename": "2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg",
        "date_str": "2026.03.27",
        "post_title": "Weekly digest 2026-03-27: AWS IdC zero trust, GCP WIF, FinOps Spot",
        "url": _post_url("2026-03-27", "Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps"),
        "hero": {
            "tag": "ZERO TRUST", "index": "01", "theme": "blue", "visual": "hub_spoke",
            "headline": "AWS IdC + SCP Zero Trust",
            "subheadline": "Identity Center plus SCP policies enforce per-session scope",
            "kpi_value": "SCP", "kpi_label": "BOUNDARY", "kpi_sub": "session-tagged",
            "action": "ENFORCE - DENY OUTSIDE BOUNDARY",
        },
        "top_right": {
            "tag": "IDENTITY", "index": "02", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "GCP Workload Identity",
            "subheadline": "Federation removes long-lived service account keys from CI",
            "kpi_value": "WIF", "kpi_label": "POLICY", "kpi_sub": "no keys in CI",
        },
        "bottom_right": {
            "tag": "FINOPS", "index": "03", "theme": "green", "visual": "data_exfil",
            "headline": "FinOps Spot + Terraform",
            "subheadline": "IaC patterns reclaim 40% of compute spend via spot pools",
            "kpi_value": "40%", "kpi_label": "SAVINGS", "kpi_sub": "spot + IaC",
        },
    }


def cfg_2026_03_28() -> Dict:
    return {
        "filename": "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.svg",
        "date_str": "2026.03.28",
        "post_title": "Weekly digest 2026-03-28: AI agent priv esc, AWS ECS escape, Harbor",
        "url": _post_url("2026-03-28", "Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day"),
        "hero": {
            "tag": "ZERO-DAY", "index": "01", "theme": "red", "visual": "container_escape",
            "headline": "AWS ECS Container Escape",
            "subheadline": "Task role assumed by sibling task via metadata race",
            "kpi_value": "0day", "kpi_label": "STATUS", "kpi_sub": "AWS patching",
            "action": "ENABLE IMDSv2 ONLY",
        },
        "top_right": {
            "tag": "AI RISK", "index": "02", "theme": "blue", "visual": "ai_agent_funnel",
            "headline": "AI Agent Priv Escalation",
            "subheadline": "Framework tools chain into shell exec via crafted plan",
            "kpi_value": "3", "kpi_label": "FRAMEWORKS", "kpi_sub": "popular AI libs",
        },
        "bottom_right": {
            "tag": "REGISTRY", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "Harbor Registry Supply",
            "subheadline": "Replication race lets unsigned image overwrite trusted tag",
            "kpi_value": "2.12", "kpi_label": "VERSION", "kpi_sub": "patch released",
        },
    }


def cfg_2026_03_29() -> Dict:
    return {
        "filename": "2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.svg",
        "date_str": "2026.03.29",
        "post_title": "Weekly digest 2026-03-29: ransomware AI, LLM jailbreak CVE, Helm + Next.js",
        "url": _post_url("2026-03-29", "Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain"),
        "hero": {
            "tag": "RANSOMWARE", "index": "01", "theme": "red", "visual": "ransomware_lock",
            "headline": "Ransomware AI Automation",
            "subheadline": "AI tooling crafts negotiation chat and victim-specific lures",
            "kpi_value": "+38%", "kpi_label": "VICTIMS", "kpi_sub": "qoq increase",
            "action": "HARDEN - PRACTICE DR DRILL",
        },
        "top_right": {
            "tag": "LLM CVE", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "LLM Jailbreak CVE-2026-3291",
            "subheadline": "Indirect prompt injection bypasses safety system prompt",
            "kpi_value": "8.6", "kpi_label": "CVSS", "kpi_sub": "indirect injection",
        },
        "bottom_right": {
            "tag": "SUPPLY CHAIN", "index": "03", "theme": "amber", "visual": "supply_chain_pipe",
            "headline": "Helm + Next.js Auth Bypass",
            "subheadline": "Helm chart ships weak default and Next.js middleware bypass",
            "kpi_value": "2", "kpi_label": "PROJECTS", "kpi_sub": "Helm + Next.js",
        },
    }


def cfg_2026_03_31() -> Dict:
    return {
        "filename": "2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.svg",
        "date_str": "2026.03.31",
        "post_title": "Weekly digest 2026-03-31: ChatGPT data leak, DeepLoad downloader, ClickFix",
        "url": _post_url("2026-03-31", "Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT"),
        "hero": {
            "tag": "DATA LEAK", "index": "01", "theme": "red", "visual": "data_exfil",
            "headline": "OpenAI ChatGPT Data Leak",
            "subheadline": "Shared-link cache exposes private prompts and uploads",
            "kpi_value": "Wide", "kpi_label": "SCOPE", "kpi_sub": "shared-link cache",
            "action": "REVOKE LINKS - AUDIT WORKSPACE",
        },
        "top_right": {
            "tag": "MALWARE", "index": "02", "theme": "blue", "visual": "code_injection",
            "headline": "DeepLoad Malware Loader",
            "subheadline": "Multi-stage downloader hides payload behind fake updater",
            "kpi_value": "5", "kpi_label": "STAGES", "kpi_sub": "loader chain",
        },
        "bottom_right": {
            "tag": "SOCIAL ENG", "index": "03", "theme": "amber", "visual": "ai_agent_funnel",
            "headline": "ClickFix Social Engineering",
            "subheadline": "Fake error dialog tricks users into running paste-to-shell",
            "kpi_value": "+210%", "kpi_label": "GROWTH", "kpi_sub": "qoq lures",
        },
    }


CONFIGS: List[Callable[[], Dict]] = [
    cfg_2026_03_16_a, cfg_2026_03_16_b, cfg_2026_03_17, cfg_2026_03_18,
    cfg_2026_03_19, cfg_2026_03_20, cfg_2026_03_21, cfg_2026_03_22,
    cfg_2026_03_23, cfg_2026_03_24, cfg_2026_03_25, cfg_2026_03_26,
    cfg_2026_03_27, cfg_2026_03_28, cfg_2026_03_29, cfg_2026_03_31,
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

    print("=" * 90)
    print(f"{'filename':<70} {'KB':>6} {'lines':>6} {'status':>10}")
    print("-" * 90)
    all_ok = True
    for name, kb, lines, ok, msg in rows:
        status = "OK" if ok else "FAIL"
        print(f"{name:<70} {kb:>6.1f} {lines:>6} {status:>10}")
        if not ok:
            print(f"  -> {msg}")
            all_ok = False
    print("=" * 90)
    print(f"Total: {len(rows)} files  /  validation: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

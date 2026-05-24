#!/usr/bin/env python3
"""Seed L20 specs for 4 orphan April covers (21, 26, 27, 28)."""
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"


SPECS = [
    (
        "2026-04-21",
        "Tech_Security_Weekly_Digest_CVE_Apple_AI_Agent",
        "Weekly digest 2026-04-21: SGLang CVE-2026-5760 critical RCE, Vercel breach, Push fraud",
        {
            "tag": "SGLANG RCE",
            "theme": "red",
            "visual": "cve_chain",
            "headline": "SGLang CVE-2026-5760 RCE",
            "subheadline": "SGLang LLM serving stack hit by CVE-2026-5760 with CVSS 9.8 remote-code-exec",
            "kpi_value": "9.8",
            "kpi_label": "CVSS",
            "kpi_sub": "SGLang",
            "action": "PATCH SGLANG + RESTRICT INFERENCE INGRESS",
        },
        {
            "tag": "VERCEL BREACH",
            "theme": "amber",
            "visual": "hub_spoke",
            "headline": "Vercel Hack Disclosure",
            "subheadline": "Vercel discloses platform compromise impacting customer build secrets",
            "kpi_value": "VER",
            "kpi_label": "BREACH",
            "kpi_sub": "platform",
        },
        {
            "tag": "PUSH FRAUD",
            "theme": "blue",
            "visual": "code_injection",
            "headline": "Push Notification Scam",
            "subheadline": "Push-notification phishing wave bypasses MFA via consent fatigue prompts",
            "kpi_value": "MFA",
            "kpi_label": "PUSH",
            "kpi_sub": "fatigue",
        },
    ),
    (
        "2026-04-26",
        "Tech_Security_Weekly_Digest_Malware_Threat_AWS_Go",
        "Weekly digest 2026-04-26: fast16 Lua OT malware, Teams Snow delivery, Anthropic Mythos",
        {
            "tag": "OT SABOTAGE",
            "theme": "red",
            "visual": "code_injection",
            "headline": "fast16 Pre-Stuxnet Lua",
            "subheadline": "fast16 Lua malware framework predates Stuxnet, targets CAE-CAD OT engineering",
            "kpi_value": "OT",
            "kpi_label": "FAST",
            "kpi_sub": "Lua",
            "action": "AUDIT OT ENGINEERING WORKSTATIONS",
        },
        {
            "tag": "TEAMS ABUSE",
            "theme": "amber",
            "visual": "data_exfil",
            "headline": "Teams Snow Malware Delivery",
            "subheadline": "Microsoft Teams used as Snow malware delivery vector via external collab links",
            "kpi_value": "MS",
            "kpi_label": "TEAMS",
            "kpi_sub": "Snow",
        },
        {
            "tag": "AI X CRYPTO",
            "theme": "blue",
            "visual": "ai_agent_funnel",
            "headline": "Anthropic Mythos Pivot",
            "subheadline": "Anthropic Mythos sparks crypto-industry security rethink for AI agent risk",
            "kpi_value": "AI",
            "kpi_label": "CRYPTO",
            "kpi_sub": "Mythos",
        },
    ),
    (
        "2026-04-27",
        "Tech_Security_Weekly_Digest_AI_Agent",
        "Weekly digest 2026-04-27: Itron utility breach, AWS Bedrock AgentCore, DeepMind Korea",
        {
            "tag": "UTILITY BREACH",
            "theme": "red",
            "visual": "data_exfil",
            "headline": "Itron IT Network Breach",
            "subheadline": "Itron utility-meter vendor files SEC 8-K disclosure with OT-adjacent risk",
            "kpi_value": "8-K",
            "kpi_label": "ITRON",
            "kpi_sub": "utility",
            "action": "AUDIT METERING SUPPLIER ACCESS + IR PLAN",
        },
        {
            "tag": "CLOUD AI LAUNCH",
            "theme": "amber",
            "visual": "ai_agent_funnel",
            "headline": "AWS Bedrock AgentCore",
            "subheadline": "AWS launches AgentCore for orchestrating expert-team agentic AI simulations",
            "kpi_value": "AWS",
            "kpi_label": "AGENT",
            "kpi_sub": "Bedrock",
        },
        {
            "tag": "AI ECOSYSTEM",
            "theme": "blue",
            "visual": "hub_spoke",
            "headline": "DeepMind + OpenAI Korea",
            "subheadline": "DeepMind and OpenAI announce Korea AI partnership programs and joint research",
            "kpi_value": "KR",
            "kpi_label": "DM+OAI",
            "kpi_sub": "partner",
        },
    ),
    (
        "2026-04-28",
        "Tech_Security_Weekly_Digest_Data_AI_Malware_AWS",
        "Weekly digest 2026-04-28: Checkmarx data leak, Robinhood email phish, fast16 BigQuery AI",
        {
            "tag": "SUPPLY CHAIN LEAK",
            "theme": "red",
            "visual": "supply_chain_pipe",
            "headline": "Checkmarx Dark Web Post",
            "subheadline": "Checkmarx GitHub repository data surfaces on dark-web criminal forum",
            "kpi_value": "GH",
            "kpi_label": "REPO",
            "kpi_sub": "leaked",
            "action": "ROTATE REPO TOKENS + AUDIT BUILD SECRETS",
        },
        {
            "tag": "PHISH EXPLOIT",
            "theme": "amber",
            "visual": "code_injection",
            "headline": "Robinhood Email Abuse",
            "subheadline": "Robinhood account-creation flaw weaponized to send phishing from trusted domain",
            "kpi_value": "RH",
            "kpi_label": "PHISH",
            "kpi_sub": "domain",
        },
        {
            "tag": "MALVERTISING",
            "theme": "blue",
            "visual": "data_exfil",
            "headline": "fast16 + BigQuery AI",
            "subheadline": "Malvertising distributes signed fast16 installers, BigQuery AI data theft path",
            "kpi_value": "ADS",
            "kpi_label": "FAST",
            "kpi_sub": "signed",
        },
    ),
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

#!/usr/bin/env python3
"""Upgrade 3 weekly-digest SVGs (2026-04-27, 2026-04-28, 2026-04-29) to L22 ultra tier.

Mirrors the structure of upgrade_5_digest_svgs_to_ultra.py.
Each post gets three themed bands (red / amber / green) with hand-curated
content drawn from the post's top headlines.

Usage::

    python3 scripts/upgrade_2026_04_27_29_to_ultra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"


# ---------------------------------------------------------------------------
# 2026-04-27  AI Agent digest
# Top items:
#   red   - Itron utility internal-IT breach (security)
#   amber - AWS Bedrock AgentCore agentic AI launch (cloud-AI)
#   green - Google DeepMind Korea partnership + OpenAI principles (AI/ecosystem)
# ---------------------------------------------------------------------------
def cfg_2026_04_27() -> dict:
    """Apr 27: Itron IT breach, AWS Bedrock AgentCore, Google DeepMind Korea."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="AP27",
        aria="Itron utility internal-IT breach, AWS Bedrock AgentCore agentic AI, Google DeepMind Korea partnership",
        title="2026-04-27: Itron breach, AWS AgentCore, DeepMind Korea",
        url="https://tech.2twodragon.com/security/2026/04/27/Tech_Security_Weekly_Digest_AI_Agent.html",
        bands=[
            dict(
                theme="red",
                label="UTILITY BREACH",
                headline="Itron IT Network Hit",
                metric="SEC 8-K : OT-adjacent risk",
                detail="Smart meter vendor : internal IT compromised : lateral OT risk : credential rotation required",
                metric_b="Supply chain : firmware pipeline integrity check",
                detail_b="CI/CD artefact re-sign : API key rotation : NERC CIP audit trail update",
                badge_value="8-K", badge_label="SEC FILING", badge_sub="disclosed",
                mini_value="OT", mini_label="RISK", mini_sub="adjacent",
                mini2_value="ITR", mini2_label="VENDOR", mini2_sub="utility",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="BREACH"),
            ),
            dict(
                theme="amber",
                label="CLOUD AI LAUNCH",
                headline="AWS Bedrock AgentCore",
                metric="Agentic AI : expert team sim",
                detail="Multi-agent orchestration : RAG access control : FedRAMP readiness : tool-use whitelist",
                metric_b="Human-in-the-loop gate : least privilege agent scope",
                detail_b="Bedrock AgentCore CLI : Anthropic + Meta partnership : Lambda S3 Files integration",
                badge_value="AWS", badge_label="BEDROCK", badge_sub="AgentCore",
                mini_value="MAS", mini_label="MULTI", mini_sub="agent",
                mini2_value="IAM", mini2_label="ACCESS", mini2_sub="control",
                visual=l22.v_cloud_k8s(500, 315, amber["accent"], amber["soft"]),
            ),
            dict(
                theme="green",
                label="AI ECOSYSTEM",
                headline="DeepMind + OpenAI",
                metric="Korea AI partnership",
                detail="Google DeepMind x Korea scientific AI acceleration : OpenAI AGI principles : 5-pillar safety",
                metric_b="AGI benefit : safety-first governance : prompt injection defense",
                detail_b="SAST gate for AI-generated code : pre-commit secret scan : bias + safety eval metrics",
                badge_value="AGI", badge_label="POLICY", badge_sub="principles",
                mini_value="5", mini_label="PILLARS", mini_sub="OpenAI",
                mini2_value="KOR", mini2_label="PARTNER", mini2_sub="DeepMind",
                visual=l22.v_bar_graph(500, 525, green["accent"], green["soft"], caption="AI GROWTH"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-04-28  Data / AI / Malware / AWS digest
# Top items:
#   red   - Checkmarx GitHub repo data on dark web (supply chain / security)
#   amber - Robinhood account-creation flaw exploited for phishing
#   green - Fast16 malware + BigQuery + Google Earth AI (data/AI/malware)
# ---------------------------------------------------------------------------
def cfg_2026_04_28() -> dict:
    """Apr 28: Checkmarx dark-web leak, Robinhood phishing flaw, Fast16 + BigQuery AI."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="AP28",
        aria="Checkmarx GitHub repo data on dark web, Robinhood account flaw phishing, Fast16 malware BigQuery Earth AI",
        title="2026-04-28: Checkmarx leak, Robinhood phish, Fast16 malware",
        url="https://tech.2twodragon.com/security/2026/04/28/Tech_Security_Weekly_Digest_Data_AI_Malware_AWS.html",
        bands=[
            dict(
                theme="red",
                label="SUPPLY CHAIN LEAK",
                headline="Checkmarx Dark Web",
                metric="GitHub repo data : dark web post",
                detail="Mar 23 supply-chain attack : SAST vendor breached : customer CI/CD tokens at risk",
                metric_b="PAT + API key rotation : SBOM re-validation required",
                detail_b="Custom SAST rules exposed : bypass path risk : pipeline integrity re-verify urgently",
                badge_value="SAST", badge_label="VENDOR", badge_sub="breached",
                mini_value="PAT", mini_label="ROTATE", mini_sub="tokens",
                mini2_value="DW", mini2_label="DARK WEB", mini2_sub="posted",
                visual=l22.v_router_mesh(500, 105, red["accent"], red["soft"]),
            ),
            dict(
                theme="amber",
                label="PHISHING EXPLOIT",
                headline="Robinhood Email Abuse",
                metric="Account creation flaw : trusted domain",
                detail="Input injection into legit Robinhood email : SPF/DKIM/DMARC bypass : OWASP A03 Injection",
                metric_b="Allowlist input validation : context-aware output encoding",
                detail_b="Business logic fuzz testing in CI/CD : real-time account-creation anomaly detection",
                badge_value="A03", badge_label="OWASP", badge_sub="injection",
                mini_value="SPF", mini_label="BYPASS", mini_sub="trusted",
                mini2_value="RH", mini2_label="BROKER", mini2_sub="abused",
                visual=l22.v_browser_cve(500, 315, amber["accent"], amber["soft"], label="PHISH"),
            ),
            dict(
                theme="green",
                label="MALWARE + DATA AI",
                headline="Fast16 + BigQuery AI",
                metric="Malvertising : signed installer",
                detail="Fast16 malware via Google Ads : DanaBot successor : Stealer + RAT chain : 120K samples",
                metric_b="BigQuery + Google Earth AI : geospatial analytics launch",
                detail_b="authorized view access control : data lake path injection prevention : SBOM for deps",
                badge_value="F16", badge_label="MALWARE", badge_sub="Fast16",
                mini_value="BQ", mini_label="BIGQUERY", mini_sub="Earth AI",
                mini2_value="RAT", mini2_label="STAGE2", mini2_sub="payload",
                visual=l22.v_code_bars(500, 525, green["accent"], green["soft"], caption="THREAT DATA"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-04-29  CVE / AI / Ransomware / Update digest
# Top items:
#   red   - GitHub CVE-2026-3854 single-git-push RCE (critical CVE)
#   amber - LofyGang LofyStealer Minecraft 3-year return (malware/stealer)
#   green - VECT 2.0 ransomware wiper >131KB on Win/Linux/ESXi
# ---------------------------------------------------------------------------
def cfg_2026_04_29() -> dict:
    """Apr 29: GitHub CVE-2026-3854 RCE, LofyGang LofyStealer, VECT 2.0 wiper ransomware."""
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="AP29",
        aria="GitHub CVE-2026-3854 single git push RCE, LofyGang LofyStealer Minecraft return, VECT 2.0 wiper ransomware",
        title="2026-04-29: GitHub RCE CVE-2026-3854, LofyGang, VECT 2.0 wiper",
        url="https://tech.2twodragon.com/security/2026/04/29/Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update.html",
        bands=[
            dict(
                theme="red",
                label="CRITICAL CVE",
                headline="GitHub RCE CVE-2026-3854",
                metric="CVE-2026-3854 : CVSS 8.7",
                detail="Single git push RCE : command injection : push-access required : GHES on-prem critical",
                metric_b="GitHub Actions token rotation : push ACL lockdown",
                detail_b="Audit git push events for shell metachar in branch names : network egress monitor",
                badge_value="8.7", badge_label="CVSS", badge_sub="git push RCE",
                mini_value="RCE", mini_label="IMPACT", mini_sub="unauth cmd",
                mini2_value="GH", mini2_label="GITHUB", mini2_sub="+ GHES",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="8.7"),
            ),
            dict(
                theme="amber",
                label="STEALER RETURN",
                headline="LofyGang LofyStealer",
                metric="3-year gap : Minecraft lure",
                detail="Brazilian LofyGang resurfaces : GrabBot stealer : fake Slinky hack tool : cred + wallet theft",
                metric_b="Dev workstation risk : CI/CD contamination via infected dev machine",
                detail_b="Game binary EDR block : IoC pre-load : secret rotation 90-day enforce : UEBA deploy",
                badge_value="3yr", badge_label="DORMANT", badge_sub="resurfaced",
                mini_value="BRA", mini_label="ORIGIN", mini_sub="LofyGang",
                mini2_value="MC", mini2_label="LURE", mini2_sub="Minecraft",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="STEALER"),
            ),
            dict(
                theme="green",
                label="WIPER RANSOMWARE",
                headline="VECT 2.0 Destroys >131KB",
                metric="Win + Linux + ESXi : wiper",
                detail="VECT 2.0 : 131KB+ files irreversibly destroyed : crypto flaw : ransom payment useless",
                metric_b="Air-gap + WORM backup urgent : FIM on large artefacts",
                detail_b="ESXi SSH lockdown + MFA : Falco/osquery FIM rules : immutable backup rehearsal now",
                badge_value="131K", badge_label="THRESHOLD", badge_sub="bytes",
                mini_value="ESXi", mini_label="SCOPE", mini_sub="Win/Linux",
                mini2_value="WIPE", mini2_label="ACTION", mini2_sub="no recovery",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="WIPER"),
            ),
        ],
    )


SPECS = [
    ("2026-04-27-Tech_Security_Weekly_Digest_AI_Agent.svg", cfg_2026_04_27),
    ("2026-04-28-Tech_Security_Weekly_Digest_Data_AI_Malware_AWS.svg", cfg_2026_04_28),
    ("2026-04-29-Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update.svg", cfg_2026_04_29),
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

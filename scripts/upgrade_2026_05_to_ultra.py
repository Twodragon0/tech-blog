#!/usr/bin/env python3
"""Upgrade 10 weekly-digest SVGs (2026-05-01 ~ 2026-05-10) to L22 ultra tier.

Mirrors the structure of upgrade_2026_04_27_29_to_ultra.py — each post
gets three themed bands (red / amber / green) with English-only,
hand-curated content drawn from the post's top headlines. The QR code
encodes the canonical Jekyll permalink (underscore-preserved) so
mobile scans land on a 200 OK URL.

This script replaces the auto-generated L20 hero covers (which carry
only 3 short title segments and a smaller visual) with the richer
L22 ultra layout — title, headline, metric, detail, badge, KPI,
secondary metric/detail row, and a thematic visual per band — while
keeping the cover ASCII-only per the project's English-only-SVG rule.

Usage::

    python3 scripts/upgrade_2026_05_to_ultra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"


def _url(date: str, slug: str) -> str:
    """Canonical Jekyll permalink (underscore-preserved)."""
    yyyy, mm, dd = date.split("-")
    return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug}/"


# ---------------------------------------------------------------------------
# 2026-05-01  PyTorch Lightning supply chain + Python backdoor + Cloud CISO
# ---------------------------------------------------------------------------
def cfg_2026_05_01() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY01",
        aria=(
            "PyTorch Lightning supply chain credential theft, Python tunneling backdoor "
            "browser and cloud credential exfiltration, multicloud multi-AI strategy"
        ),
        title="2026-05-01: PyTorch supply chain, Python backdoor, multi-AI",
        url=_url("2026-05-01", "Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud"),
        bands=[
            dict(
                theme="red",
                label="SUPPLY CHAIN ATTACK",
                headline="PyTorch Lightning Hijack",
                metric="ML pipeline : credential theft",
                detail=(
                    "PyTorch Lightning + Intercom-client compromised : "
                    "developer tokens exfiltrated : ML CI/CD pipeline at risk"
                ),
                metric_b="Pin lockfiles + signature verify on ML deps",
                detail_b=(
                    "Re-issue tokens : audit pip install logs : "
                    "block uncommon registries : run npm audit and pip-audit"
                ),
                badge_value="ML", badge_label="ECOSYSTEM", badge_sub="poisoned",
                mini_value="PIP", mini_label="VECTOR", mini_sub="package",
                mini2_value="DEV", mini2_label="EXPOSED", mini2_sub="creds",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="HIJACK"),
            ),
            dict(
                theme="amber",
                label="PYTHON BACKDOOR",
                headline="Tunneling Steals Cloud Creds",
                metric="Browser + cloud credential drain",
                detail=(
                    "Python backdoor uses tunneling services to exfiltrate "
                    "browser auth tokens, AWS keys, Azure session cookies"
                ),
                metric_b="EDR rule : detect outbound ngrok-style tunnels",
                detail_b=(
                    "Tunnel egress block + DNS sinkhole : "
                    "rotate cloud keys : enforce hardware-bound MFA"
                ),
                badge_value="3K", badge_label="VICTIMS", badge_sub="reported",
                mini_value="AWS", mini_label="TARGET", mini_sub="keys",
                mini2_value="AZ", mini2_label="ALSO", mini2_sub="cookies",
                visual=l22.v_browser_cve(500, 315, amber["accent"], amber["soft"], label="STEAL"),
            ),
            dict(
                theme="green",
                label="MULTI CLOUD STRATEGY",
                headline="CISO Picks Multi AI",
                metric="Google Cloud Next 26 keynote",
                detail=(
                    "Cloud CISO playbook : multi-cloud + multi-model AI "
                    "to avoid lock-in and concentrate risk per workload"
                ),
                metric_b="Vendor portability + AI provider diversification",
                detail_b=(
                    "IAM federation across providers : "
                    "data residency mapping : cost + safety tier per model"
                ),
                badge_value="3+", badge_label="CLOUDS", badge_sub="federated",
                mini_value="AI", mini_label="MULTI", mini_sub="model",
                mini2_value="GCP", mini2_label="HOST", mini2_sub="primary",
                visual=l22.v_cloud_k8s(500, 525, green["accent"], green["soft"]),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-02  Facebook 30K phishing + AWS AI security + Microsoft Run dialog
# ---------------------------------------------------------------------------
def cfg_2026_05_02() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY02",
        aria=(
            "30000 Facebook accounts phished via Google AppSheet, "
            "AWS posture management for AI workloads, Microsoft Windows Run dialog redesign"
        ),
        title="2026-05-02: 30K Facebook phish, AWS AI posture, Win Run",
        url=_url("2026-05-02", "Tech_Security_Weekly_Digest_AI_Go_Security_AWS"),
        bands=[
            dict(
                theme="red",
                label="MASS PHISHING",
                headline="30K Facebook Accounts",
                metric="Google AppSheet abuse",
                detail=(
                    "Phishing campaign abuses Google AppSheet to bulk-send "
                    "credential-harvesting emails impersonating Meta security"
                ),
                metric_b="Block AppSheet outbound when impersonation detected",
                detail_b=(
                    "Mail gateway DKIM/DMARC enforcement : "
                    "user training + simulated phishing baseline"
                ),
                badge_value="30K", badge_label="ACCOUNTS", badge_sub="harvested",
                mini_value="GAS", mini_label="ABUSE", mini_sub="AppSheet",
                mini2_value="FB", mini2_label="LURE", mini2_sub="Meta",
                visual=l22.v_browser_cve(500, 105, red["accent"], red["soft"], label="PHISH"),
            ),
            dict(
                theme="amber",
                label="CLOUD AI POSTURE",
                headline="AWS AI Security Guide",
                metric="Posture management : AI era",
                detail=(
                    "AWS publishes AI posture management guidance : "
                    "model registry, prompt injection defense, agent scope"
                ),
                metric_b="GuardDuty + Inspector for AI workloads",
                detail_b=(
                    "Enable Bedrock guardrails : "
                    "tag inference workloads for cost + risk attribution"
                ),
                badge_value="AWS", badge_label="POSTURE", badge_sub="AI guide",
                mini_value="GD", mini_label="GUARD", mini_sub="duty",
                mini2_value="IAM", mini2_label="SCOPE", mini2_sub="agent",
                visual=l22.v_shield(500, 315, amber["accent"], amber["soft"], label="POSTURE"),
            ),
            dict(
                theme="green",
                label="WINDOWS PRODUCTIVITY",
                headline="Modernized Run Dialog",
                metric="Faster than legacy Win Run",
                detail=(
                    "Microsoft tests redesigned Run with command palette UX : "
                    "history search + alias + quick actions"
                ),
                metric_b="Enterprise rollout : Group Policy controllable",
                detail_b=(
                    "AppLocker + WDAC compatibility check : "
                    "audit shell history exposure for sensitive commands"
                ),
                badge_value="WIN", badge_label="REFRESH", badge_sub="Run UX",
                mini_value="CMD", mini_label="PALETTE", mini_sub="modern",
                mini2_value="GPO", mini2_label="CONTROL", mini2_sub="enterprise",
                visual=l22.v_code_bars(500, 525, green["accent"], green["soft"], caption="RUN"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-03  cPanel Sorry ransomware + Trellix source leak + ConsentFix v3
# ---------------------------------------------------------------------------
def cfg_2026_05_03() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY03",
        aria=(
            "cPanel critical vulnerability mass-exploited by Sorry ransomware, "
            "Trellix unauthorized repo access source code leak, "
            "ConsentFix v3 attack automated OAuth abuse against Azure"
        ),
        title="2026-05-03: cPanel Sorry ransomware, Trellix leak, ConsentFix",
        url=_url("2026-05-03", "Tech_Security_Weekly_Digest_Ransomware_Azure_CVE_Vulnerability"),
        bands=[
            dict(
                theme="red",
                label="MASS EXPLOIT",
                headline="cPanel + Sorry Ransomware",
                metric="Critical CVE : web hosting",
                detail=(
                    "cPanel vulnerability mass-exploited by Sorry ransomware : "
                    "shared-hosting blast radius : tenant isolation broken"
                ),
                metric_b="Patch cPanel WHM : audit running cron + perl tasks",
                detail_b=(
                    "Tenant snapshot restore plan : "
                    "WAF rule for cPanel admin URLs : full forensic image"
                ),
                badge_value="MASS", badge_label="EXPLOIT", badge_sub="hosting",
                mini_value="WHM", mini_label="ADMIN", mini_sub="path",
                mini2_value="LE", mini2_label="LET'S", mini2_sub="shared host",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="9.1"),
            ),
            dict(
                theme="amber",
                label="SOURCE CODE LEAK",
                headline="Trellix Repo Breach",
                metric="Unauthorized SCM access",
                detail=(
                    "Trellix confirms unauthorized repo access : "
                    "source code exposure : security vendor brand impact"
                ),
                metric_b="Token rotation + commit signing across all repos",
                detail_b=(
                    "Audit OAuth app permissions : "
                    "branch protection + required reviewers : SBOM regeneration"
                ),
                badge_value="SCM", badge_label="LEAK", badge_sub="vendor src",
                mini_value="OAUTH", mini_label="VECTOR", mini_sub="app token",
                mini2_value="GH", mini2_label="HOST", mini2_sub="GitHub",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="LEAK"),
            ),
            dict(
                theme="green",
                label="OAUTH ABUSE",
                headline="ConsentFix v3 vs Azure",
                metric="Automated consent phishing",
                detail=(
                    "ConsentFix v3 automates OAuth consent abuse against Azure AD : "
                    "low-friction tenant takeover via legit app trust"
                ),
                metric_b="Restrict user app consent + enable admin review",
                detail_b=(
                    "Conditional Access for risky apps : "
                    "Entra ID app governance + token revocation runbook"
                ),
                badge_value="V3", badge_label="VARIANT", badge_sub="auto OAuth",
                mini_value="AZ", mini_label="TARGET", mini_sub="Entra ID",
                mini2_value="MS", mini2_label="ALERT", mini2_sub="Microsoft",
                visual=l22.v_cloud_k8s(500, 525, green["accent"], green["soft"]),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-04  Instructure breach + DigiCert MS Defender + CVE-2026-31431 KEV
# ---------------------------------------------------------------------------
def cfg_2026_05_04() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY04",
        aria=(
            "Instructure data breach confirmed ShinyHunters claim, "
            "Microsoft Defender flags DigiCert certificates, "
            "CISA adds Linux root CVE-2026-31431 to KEV"
        ),
        title="2026-05-04: Instructure breach, Defender DigiCert, KEV CVE",
        url=_url("2026-05-04", "Tech_Security_Weekly_Digest_AI_Data_CVE_Malware"),
        bands=[
            dict(
                theme="red",
                label="EDU DATA BREACH",
                headline="Instructure Hit by ShinyHunters",
                metric="Edu PII : confirmed exposure",
                detail=(
                    "Instructure (Canvas LMS) confirms data breach : "
                    "ShinyHunters claim student + faculty PII for sale"
                ),
                metric_b="FERPA notification + credential reset waves",
                detail_b=(
                    "Audit OAuth grants on Canvas : "
                    "MFA enforcement for institutional accounts : DLP review"
                ),
                badge_value="EDU", badge_label="SECTOR", badge_sub="K-12 + HE",
                mini_value="SH", mini_label="ACTOR", mini_sub="ShinyHunters",
                mini2_value="LMS", mini2_label="SCOPE", mini2_sub="Canvas",
                visual=l22.v_network_nodes(500, 105, red["accent"], red["soft"], label="LEAK"),
            ),
            dict(
                theme="amber",
                label="CERT TRUST CHAIN",
                headline="Defender vs DigiCert",
                metric="False-positive cascade",
                detail=(
                    "Microsoft Defender flags DigiCert-signed binaries : "
                    "patch tooling + EDR + auto-update chains affected"
                ),
                metric_b="Allowlist DigiCert intermediate CA in Defender ASR",
                detail_b=(
                    "Validate code-signing pipeline : "
                    "stage rollback : runbook for Defender flag escalation"
                ),
                badge_value="CA", badge_label="TRUST", badge_sub="DigiCert",
                mini_value="MD", mini_label="DEFEND", mini_sub="alert",
                mini2_value="ASR", mini2_label="RULE", mini2_sub="cert",
                visual=l22.v_shield(500, 315, amber["accent"], amber["soft"], label="TRUST"),
            ),
            dict(
                theme="green",
                label="KEV ADDITION",
                headline="Linux Root CVE-2026-31431",
                metric="CISA KEV : actively exploited",
                detail=(
                    "CISA adds Linux root-access CVE-2026-31431 to KEV : "
                    "FCEB 21-day patch deadline triggered"
                ),
                metric_b="Inventory affected kernel + glibc range : SLA tracker",
                detail_b=(
                    "Auto-patch pipeline + reboot orchestration : "
                    "compensating control if patch deferred : audit log retention"
                ),
                badge_value="KEV", badge_label="CISA", badge_sub="21-day SLA",
                mini_value="ROOT", mini_label="IMPACT", mini_sub="privilege",
                mini2_value="LX", mini2_label="OS", mini2_sub="Linux",
                visual=l22.v_lock_cve(500, 525, green["accent"], green["soft"], cvss="7.8"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-05  SimpleHelp/RMM phishing + MOVEit auth bypass + AI summary
# ---------------------------------------------------------------------------
def cfg_2026_05_05() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY05",
        aria=(
            "SimpleHelp ScreenConnect RMM phishing campaign hits 80 organizations, "
            "Progress patches critical MOVEit Automation auth bypass, "
            "weekly AI threat summary with Android spy tooling"
        ),
        title="2026-05-05: SimpleHelp RMM phish, MOVEit auth bypass, AI weekly",
        url=_url("2026-05-05", "Tech_Security_Weekly_Digest_AI_Patch_AWS"),
        bands=[
            dict(
                theme="red",
                label="RMM ABUSE",
                headline="SimpleHelp + ScreenConnect",
                metric="80+ orgs : phishing-led RMM",
                detail=(
                    "Phishing campaign delivers SimpleHelp and ScreenConnect "
                    "RMM agents to 80+ organizations for hands-on intrusion"
                ),
                metric_b="Block unsolicited RMM installers at MAR + EDR",
                detail_b=(
                    "AppLocker rule for known-good RMM only : "
                    "DNS sinkhole RMM C2 domains : tabletop incident drill"
                ),
                badge_value="80+", badge_label="ORGS", badge_sub="targeted",
                mini_value="RMM", mini_label="VECTOR", mini_sub="installer",
                mini2_value="ML", mini2_label="LANG", mini2_sub="multi-locale",
                visual=l22.v_browser_cve(500, 105, red["accent"], red["soft"], label="RMM"),
            ),
            dict(
                theme="amber",
                label="CRITICAL PATCH",
                headline="MOVEit Auth Bypass",
                metric="Progress critical : patch now",
                detail=(
                    "Progress patches MOVEit Automation auth bypass : "
                    "unauthenticated RCE risk on file-transfer servers"
                ),
                metric_b="Network ACL : restrict MOVEit admin to bastion",
                detail_b=(
                    "Apply patch within 24h : audit transfer logs : "
                    "rotate API + service-account credentials"
                ),
                badge_value="9.8", badge_label="CVSS", badge_sub="auth bypass",
                mini_value="MFT", mini_label="CLASS", mini_sub="file xfer",
                mini2_value="PROG", mini2_label="VENDOR", mini2_sub="Progress",
                visual=l22.v_lock_cve(500, 315, amber["accent"], amber["soft"], cvss="9.8"),
            ),
            dict(
                theme="green",
                label="AI THREAT WEEKLY",
                headline="AI Phishing + Android Spy",
                metric="Cross-platform threat roundup",
                detail=(
                    "Weekly summary : AI-generated phishing, Android spy tools, "
                    "Linux exploits, GitHub-hosted RCE chains"
                ),
                metric_b="Mobile EDR + GitHub Advanced Security gates",
                detail_b=(
                    "Block known-bad GH actions + scripts in CI : "
                    "Android MDM compliance : prompt injection eval"
                ),
                badge_value="WK", badge_label="DIGEST", badge_sub="weekly AI",
                mini_value="AND", mini_label="MOBILE", mini_sub="spy",
                mini2_value="GH", mini2_label="HOST", mini2_sub="GitHub",
                visual=l22.v_bar_graph(500, 525, green["accent"], green["soft"], caption="THREATS"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-06  Apache HTTP/2 CVE-2026-23918 + DAEMON Tools + UAT-8302 APT
# ---------------------------------------------------------------------------
def cfg_2026_05_06() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY06",
        aria=(
            "Apache HTTP/2 critical CVE-2026-23918 DoS and potential RCE, "
            "DAEMON Tools supply chain official installer malware, "
            "China-linked UAT-8302 APT cross-region malware government targeting"
        ),
        title="2026-05-06: Apache HTTP/2 CVE, DAEMON supply chain, UAT-8302",
        url=_url("2026-05-06", "Tech_Security_Weekly_Digest_CVE_AI_Malware_Go"),
        bands=[
            dict(
                theme="red",
                label="CRITICAL CVE",
                headline="Apache HTTP/2 CVE-2026-23918",
                metric="DoS + potential RCE",
                detail=(
                    "Apache HTTP/2 critical : malformed frame triggers DoS "
                    "with potential RCE via memory corruption pathway"
                ),
                metric_b="Patch httpd : fall back to HTTP/1.1 if patch deferred",
                detail_b=(
                    "WAF anti-DoS rule : monitor connection-reset spikes : "
                    "container image rebuild + redeploy in waves"
                ),
                badge_value="9.4", badge_label="CVSS", badge_sub="DoS+RCE",
                mini_value="H2", mini_label="PROTO", mini_sub="HTTP/2",
                mini2_value="APA", mini2_label="VENDOR", mini2_sub="Apache",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="9.4"),
            ),
            dict(
                theme="amber",
                label="SUPPLY CHAIN",
                headline="DAEMON Tools Installer",
                metric="Official site : trojanized",
                detail=(
                    "DAEMON Tools official installer trojanized : "
                    "millions of users at risk via legitimate download path"
                ),
                metric_b="Hash + signature verify on third-party installers",
                detail_b=(
                    "EDR block + revoke trust on compromised certificate : "
                    "user notification + clean reinstall guidance"
                ),
                badge_value="OFC", badge_label="VENDOR", badge_sub="official",
                mini_value="WIN", mini_label="OS", mini_sub="Windows",
                mini2_value="ISO", mini2_label="USECASE", mini2_sub="virtual",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="TROJAN"),
            ),
            dict(
                theme="green",
                label="APT CAMPAIGN",
                headline="UAT-8302 vs Government",
                metric="China-linked : cross-region",
                detail=(
                    "UAT-8302 APT : cross-region shared malware family "
                    "targeting government agencies across multiple geographies"
                ),
                metric_b="MITRE ATT and CK mapping + threat-hunt queries",
                detail_b=(
                    "IOC ingest into SIEM + EDR : "
                    "geo-baseline anomaly detection : threat-intel sharing partner"
                ),
                badge_value="APT", badge_label="ACTOR", badge_sub="UAT-8302",
                mini_value="GOV", mini_label="TARGET", mini_sub="agencies",
                mini2_value="CN", mini2_label="ORIGIN", mini2_sub="linked",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="APT"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-07  Mirai xlabs_v1 botnet + AWS ISO 42001 + MuddyWater Teams
# ---------------------------------------------------------------------------
def cfg_2026_05_07() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY07",
        aria=(
            "Mirai-based xlabs_v1 botnet exploits ADB to commandeer IoT for DDoS, "
            "AWS publishes ISO/IEC 42001:2023 AI compliance guidance, "
            "MuddyWater fake ransomware campaign abuses Microsoft Teams"
        ),
        title="2026-05-07: Mirai xlabs_v1, AWS ISO 42001, MuddyWater Teams",
        url=_url("2026-05-07", "Tech_Security_Weekly_Digest_AI_Botnet_AWS_Ransomware"),
        bands=[
            dict(
                theme="red",
                label="IOT BOTNET",
                headline="Mirai xlabs_v1 via ADB",
                metric="Android Debug Bridge abuse",
                detail=(
                    "Mirai-based xlabs_v1 exploits exposed ADB to enslave "
                    "IoT and Android devices for DDoS-as-a-service"
                ),
                metric_b="Block ADB ports + audit IoT firmware update channels",
                detail_b=(
                    "Egress filter UDP/SSDP amplification ports : "
                    "DDoS playbook drill : provider scrubbing service tested"
                ),
                badge_value="IoT", badge_label="VECTOR", badge_sub="ADB exposed",
                mini_value="DDoS", mini_label="USE", mini_sub="rented",
                mini2_value="AND", mini2_label="OS", mini2_sub="Android",
                visual=l22.v_router_mesh(500, 105, red["accent"], red["soft"]),
            ),
            dict(
                theme="amber",
                label="AI COMPLIANCE",
                headline="AWS ISO/IEC 42001",
                metric="Cloud AI governance",
                detail=(
                    "AWS publishes ISO/IEC 42001:2023 compliance guidance : "
                    "AI management system controls for cloud workloads"
                ),
                metric_b="Map controls to NIST AI RMF + EU AI Act tiers",
                detail_b=(
                    "Inventory AI workloads + risk classify : "
                    "model card lifecycle : bias + safety eval cadence"
                ),
                badge_value="42001", badge_label="ISO", badge_sub="AI MS",
                mini_value="AWS", mini_label="HOST", mini_sub="cloud",
                mini2_value="GOV", mini2_label="FRAME", mini2_sub="AI",
                visual=l22.v_shield(500, 315, amber["accent"], amber["soft"], label="ISO"),
            ),
            dict(
                theme="green",
                label="APT TEAMS ABUSE",
                headline="MuddyWater Fake Ransomware",
                metric="Teams + cred theft",
                detail=(
                    "MuddyWater fake ransomware leverages Microsoft Teams "
                    "external chat for credential theft and lateral movement"
                ),
                metric_b="Block external Teams chat by default + admin allowlist",
                detail_b=(
                    "Defender for Office 365 anti-phishing tuning : "
                    "Teams audit log + SIEM rule for atypical external invites"
                ),
                badge_value="MW", badge_label="ACTOR", badge_sub="MuddyWater",
                mini_value="MS", mini_label="VECTOR", mini_sub="Teams",
                mini2_value="CRED", mini2_label="GOAL", mini2_sub="theft",
                visual=l22.v_network_nodes(500, 525, green["accent"], green["soft"], label="MUDDY"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-08  Ivanti EPMM CVE-2026-6973 + PCPJack worm + AI prompt RCE
# ---------------------------------------------------------------------------
def cfg_2026_05_08() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY08",
        aria=(
            "Ivanti EPMM CVE-2026-6973 actively exploited admin RCE, "
            "PCPJack credential stealer worm chains 5 CVEs across cloud, "
            "Microsoft warns AI agent framework prompts can become shells"
        ),
        title="2026-05-08: Ivanti EPMM RCE, PCPJack 5-CVE worm, prompt RCE",
        url=_url("2026-05-08", "Tech_Security_Weekly_Digest_CVE_Cloud_AI_Agent"),
        bands=[
            dict(
                theme="red",
                label="ADMIN RCE",
                headline="Ivanti EPMM CVE-2026-6973",
                metric="Active exploit : admin access",
                detail=(
                    "Ivanti EPMM CVE-2026-6973 RCE exploited in the wild : "
                    "yields admin-tier mobile management access"
                ),
                metric_b="Patch immediately + isolate EPMM admin plane",
                detail_b=(
                    "Restrict EPMM admin URL to bastion subnet : "
                    "rotate API keys : audit MDM enrollment for foreign devices"
                ),
                badge_value="9.8", badge_label="CVSS", badge_sub="admin RCE",
                mini_value="MDM", mini_label="CLASS", mini_sub="mobile",
                mini2_value="IVT", mini2_label="VENDOR", mini2_sub="Ivanti",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="9.8"),
            ),
            dict(
                theme="amber",
                label="WORM CHAIN",
                headline="PCPJack 5 CVE Spread",
                metric="Cred-stealer : worm-like",
                detail=(
                    "PCPJack worm chains five CVEs across cloud workloads "
                    "for credential theft and self-propagation"
                ),
                metric_b="VPC segmentation + east-west network policy",
                detail_b=(
                    "Block lateral SSH + Kubernetes internal API : "
                    "rotate IAM/service-account creds : runtime EDR sensors"
                ),
                badge_value="5", badge_label="CVES", badge_sub="chained",
                mini_value="WORM", mini_label="MODE", mini_sub="self-spread",
                mini2_value="CLD", mini2_label="SCOPE", mini2_sub="multi-cloud",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="WORM"),
            ),
            dict(
                theme="green",
                label="AI AGENT RCE",
                headline="When Prompts Become Shells",
                metric="Agent framework RCE class",
                detail=(
                    "Microsoft details RCE in AI agent frameworks : "
                    "untrusted prompts route to tool-call shell execution"
                ),
                metric_b="Whitelist agent tool calls + human-in-the-loop gate",
                detail_b=(
                    "Sandbox tool execution : prompt-injection eval CI : "
                    "audit agent transcripts for prompt-derived shell exits"
                ),
                badge_value="RCE", badge_label="CLASS", badge_sub="prompt-led",
                mini_value="AI", mini_label="AGENT", mini_sub="framework",
                mini2_value="MS", mini2_label="ALERT", mini2_sub="Microsoft",
                visual=l22.v_code_bars(500, 525, green["accent"], green["soft"], caption="AGENT"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-09  TCLBANKER worm + 7.3M Play Store fake call app + Dirty Frag Linux
# ---------------------------------------------------------------------------
def cfg_2026_05_09() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY09",
        aria=(
            "TCLBANKER banking trojan worms via WhatsApp and Outlook to target "
            "financial platforms, fake call-history Android app racks 7.3M Play "
            "Store downloads exfiltrating payment data, Dirty Frag Linux flaw "
            "actively exploited for post-compromise privilege expansion"
        ),
        title="2026-05-09: TCLBANKER worm, 7.3M fake-call app, Dirty Frag Linux",
        url=_url("2026-05-09", "Tech_Security_Weekly_Digest_Vulnerability_AI_Threat"),
        bands=[
            dict(
                theme="red",
                label="BANKING TROJAN",
                headline="TCLBANKER WhatsApp Worm",
                metric="Banking + worm via chat",
                detail=(
                    "TCLBANKER banking trojan self-propagates through "
                    "WhatsApp and Outlook to hit financial-platform credentials"
                ),
                metric_b="Block Outlook + WhatsApp executable attachments",
                detail_b=(
                    "EDR rule for clipboard-injection patterns : "
                    "user-training drill on chat-borne malware lures"
                ),
                badge_value="BANK", badge_label="TARGET", badge_sub="financial",
                mini_value="WORM", mini_label="MODE", mini_sub="self-spread",
                mini2_value="CHAT", mini2_label="VECTOR", mini2_sub="WhatsApp",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="HIGH"),
            ),
            dict(
                theme="amber",
                label="MOBILE SUPPLY",
                headline="7.3M Fake Call-History App",
                metric="Play Store data theft",
                detail=(
                    "Android fake call-history app reaches 7.3M Play Store "
                    "installs while exfiltrating user payment information"
                ),
                metric_b="MDM allowlist + Play Protect re-scan policy",
                detail_b=(
                    "Audit installed apps against Play Store reputation : "
                    "block sideload + restrict accessibility-service grants"
                ),
                badge_value="7.3M", badge_label="INSTALLS", badge_sub="Play Store",
                mini_value="AND", mini_label="OS", mini_sub="Android",
                mini2_value="PAY", mini2_label="EXFIL", mini2_sub="payment",
                visual=l22.v_network_nodes(500, 315, amber["accent"], amber["soft"], label="INSTALL"),
            ),
            dict(
                theme="green",
                label="LINUX KERNEL",
                headline="Dirty Frag Active Exploit",
                metric="Post-compromise privesc",
                detail=(
                    "Dirty Frag Linux flaw actively exploited to expand "
                    "post-compromise foothold into root-tier access"
                ),
                metric_b="Apply kernel patch + restrict containers caps",
                detail_b=(
                    "Drop SYS_PTRACE / SYS_ADMIN where unneeded : "
                    "audit unprivileged user namespace + sysctl hardening"
                ),
                badge_value="ROOT", badge_label="IMPACT", badge_sub="privesc",
                mini_value="LIN", mini_label="OS", mini_sub="kernel",
                mini2_value="ACT", mini2_label="STATE", mini2_sub="active",
                visual=l22.v_shield(500, 525, green["accent"], green["soft"], label="KERNEL"),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 2026-05-10  JDownloader RAT + cPanel/WHM 3 patches + HuggingFace fake OpenAI
# ---------------------------------------------------------------------------
def cfg_2026_05_10() -> dict:
    red = l22.THEMES["red"]
    amber = l22.THEMES["amber"]
    green = l22.THEMES["green"]
    return dict(
        sfx="MY10",
        aria=(
            "JDownloader official site compromise replaces installer with a "
            "Python RAT, cPanel and WHM ship three new vulnerability patches "
            "that operators must apply now, Hugging Face fake OpenAI repository "
            "distributes information-stealing malware to ML developers"
        ),
        title="2026-05-10: JDownloader RAT, cPanel triple patch, HF fake OpenAI",
        url=_url("2026-05-10", "Tech_Security_Weekly_Digest_Malware_Patch_AI_Agent"),
        bands=[
            dict(
                theme="red",
                label="SUPPLY CHAIN",
                headline="JDownloader Site Hijack",
                metric="Installer to Python RAT",
                detail=(
                    "JDownloader official download site compromised : "
                    "installer swapped for a Python RAT seeded across users"
                ),
                metric_b="SBOM + checksum gate for any third-party installer",
                detail_b=(
                    "Block JDownloader install + force fresh re-download : "
                    "EDR sweep for python.exe spawning suspicious child shells"
                ),
                badge_value="RAT", badge_label="PAYLOAD", badge_sub="Python",
                mini_value="DL", mini_label="VECTOR", mini_sub="installer",
                mini2_value="JD", mini2_label="VENDOR", mini2_sub="JDownloader",
                visual=l22.v_lock_cve(500, 105, red["accent"], red["soft"], cvss="HIGH"),
            ),
            dict(
                theme="amber",
                label="HOSTING PANEL",
                headline="cPanel + WHM Triple CVE",
                metric="3 fixes : patch now",
                detail=(
                    "cPanel and WHM publish three new CVE patches affecting "
                    "shared hosting control planes : exploit pressure imminent"
                ),
                metric_b="Stage cPanel update on canary host then fleet-wide",
                detail_b=(
                    "Audit reseller + admin sessions for anomalies : "
                    "rotate API tokens : restrict WHM admin port to bastion"
                ),
                badge_value="3", badge_label="CVES", badge_sub="cPanel/WHM",
                mini_value="HOST", mini_label="SCOPE", mini_sub="shared",
                mini2_value="PATCH", mini2_label="STATE", mini2_sub="now",
                visual=l22.v_shield(500, 315, amber["accent"], amber["soft"], label="cPanel"),
            ),
            dict(
                theme="green",
                label="ML SUPPLY CHAIN",
                headline="Hugging Face Fake OpenAI",
                metric="Stealer in ML registry",
                detail=(
                    "Hugging Face fake OpenAI repository distributes "
                    "information-stealing malware aimed at ML developers"
                ),
                metric_b="Pin model repos by org + signed-release verification",
                detail_b=(
                    "Add HF org allowlist to ML CI : pip + transformers SBOM : "
                    "EDR rule for pickle deserialization spawning new processes"
                ),
                badge_value="HF", badge_label="REGISTRY", badge_sub="model hub",
                mini_value="ML", mini_label="TARGET", mini_sub="developers",
                mini2_value="FAKE", mini2_label="ACTOR", mini2_sub="impersonate",
                visual=l22.v_code_bars(500, 525, green["accent"], green["soft"], caption="MODEL"),
            ),
        ],
    )


SPECS = [
    ("2026-05-01-Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud.svg", cfg_2026_05_01),
    ("2026-05-02-Tech_Security_Weekly_Digest_AI_Go_Security_AWS.svg", cfg_2026_05_02),
    ("2026-05-03-Tech_Security_Weekly_Digest_Ransomware_Azure_CVE_Vulnerability.svg", cfg_2026_05_03),
    ("2026-05-04-Tech_Security_Weekly_Digest_AI_Data_CVE_Malware.svg", cfg_2026_05_04),
    ("2026-05-05-Tech_Security_Weekly_Digest_AI_Patch_AWS.svg", cfg_2026_05_05),
    ("2026-05-06-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.svg", cfg_2026_05_06),
    ("2026-05-07-Tech_Security_Weekly_Digest_AI_Botnet_AWS_Ransomware.svg", cfg_2026_05_07),
    ("2026-05-08-Tech_Security_Weekly_Digest_CVE_Cloud_AI_Agent.svg", cfg_2026_05_08),
    ("2026-05-09-Tech_Security_Weekly_Digest_Vulnerability_AI_Threat.svg", cfg_2026_05_09),
    ("2026-05-10-Tech_Security_Weekly_Digest_Malware_Patch_AI_Agent.svg", cfg_2026_05_10),
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

#!/usr/bin/env python3
"""Seed L20 specs for 2026-05-23..26 weekly digests."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-05-23", "Tech_Security_Weekly_Digest_K8s_RBAC_AI_Prompt_R2_Misconfig",
     "Weekly digest 2026-05-23: K8s RBAC escalation, AI prompt injection, Cloudflare R2 leak",
     {"tag":"K8S RBAC","theme":"red","visual":"cve_chain","headline":"K8s RBAC Privilege Escalation",
      "subheadline":"Kubernetes RBAC evaluation flaw enables cluster-admin escalation via aggregation",
      "kpi_value":"RBAC","kpi_label":"K8s","kpi_sub":"esc",
      "action":"PATCH + AUDIT CLUSTERROLEBINDING"},
     {"tag":"AI INJECT","theme":"amber","visual":"ai_agent_funnel","headline":"AI Prompt Injection Wave",
      "subheadline":"Cross-domain prompt injection campaign abuses RAG context boundaries",
      "kpi_value":"AI","kpi_label":"PI","kpi_sub":"RAG"},
     {"tag":"R2 LEAK","theme":"blue","visual":"data_exfil","headline":"Cloudflare R2 Public Leak",
      "subheadline":"Misconfigured R2 bucket exposes build artifacts via default public flag",
      "kpi_value":"R2","kpi_label":"CF","kpi_sub":"open"}),

    ("2026-05-24", "Tech_Security_Weekly_Digest_Ransomware_Pivot_IAM_Center_OSS_Supply",
     "Weekly digest 2026-05-24: ransomware data-theft pivot, AWS IAM Identity Center, OSS supply chain",
     {"tag":"RANSOM PIVOT","theme":"red","visual":"ransomware_lock","headline":"Ransomware Data-Theft Pivot",
      "subheadline":"Operators drop encryption and pivot to data-theft-only extortion models",
      "kpi_value":"RAN","kpi_label":"PIV","kpi_sub":"theft",
      "action":"DLP RULES + DATA INVENTORY"},
     {"tag":"IAM CENTER","theme":"amber","visual":"cve_chain","headline":"AWS IAM Identity Center Flaw",
      "subheadline":"AWS Identity Center delegation evaluation flaw exceeds intended scopes",
      "kpi_value":"IDC","kpi_label":"AWS","kpi_sub":"deleg"},
     {"tag":"OSS SUPPLY","theme":"blue","visual":"supply_chain_pipe","headline":"OSS Maintainer Takeover",
      "subheadline":"npm and PyPI maintainer accounts targeted via weak OTP backup codes",
      "kpi_value":"OSS","kpi_label":"MAINT","kpi_sub":"ATO"}),

    ("2026-05-25", "Tech_Security_Weekly_Digest_Patch_Tuesday_AI_Jailbreak_Container_Runtime",
     "Weekly digest 2026-05-25: June Patch Tuesday preview, AI agent jailbreak, containerd runtime",
     {"tag":"PATCH TUE","theme":"red","visual":"cve_chain","headline":"June Patch Tuesday Critical 6",
      "subheadline":"Microsoft pre-advisory flags six Critical fixes including active-exploit cases",
      "kpi_value":"6","kpi_label":"CRIT","kpi_sub":"MSFT",
      "action":"FREEZE CAB + KEV MAPPING"},
     {"tag":"AI JAILBREAK","theme":"amber","visual":"ai_agent_funnel","headline":"AI Agent Tool Jailbreak",
      "subheadline":"Multi-step tool-call chain bypasses AI agent system prompt alignment",
      "kpi_value":"AI","kpi_label":"JB","kpi_sub":"tool"},
     {"tag":"CONTAINERD","theme":"blue","visual":"container_escape","headline":"containerd Runtime Exploit",
      "subheadline":"containerd flaw enables host access without user-namespaces enforcement",
      "kpi_value":"CTRD","kpi_label":"RT","kpi_sub":"esc"}),

    ("2026-05-26", "Tech_Security_Weekly_Digest_CVE_2026_Zero_Trust_FinOps_Security",
     "Weekly digest 2026-05-26: new CVE-2026 critical, multi-cloud Zero Trust, FinOps x security",
     {"tag":"CVE-2026","theme":"red","visual":"cve_chain","headline":"New CVE-2026 Critical Active",
      "subheadline":"New CVE-2026 critical advisory with auth bypass to remote code execution",
      "kpi_value":"CRIT","kpi_label":"CVE","kpi_sub":"2026",
      "action":"PATCH CARAVAN + WAF RULES"},
     {"tag":"ZERO TRUST","theme":"amber","visual":"hub_spoke","headline":"Multi-Cloud ZTA Pattern",
      "subheadline":"Multi-cloud Zero Trust deployment pattern unifies identity device session axes",
      "kpi_value":"ZTA","kpi_label":"MC","kpi_sub":"3-ax"},
     {"tag":"FINOPS x SEC","theme":"blue","visual":"data_exfil","headline":"FinOps x Security Telemetry",
      "subheadline":"Cost observability and security telemetry unified for early threat signal",
      "kpi_value":"FIN","kpi_label":"SEC","kpi_sub":"unif"}),
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

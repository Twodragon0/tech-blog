#!/usr/bin/env python3
"""Seed L20 specs for Jan batch C (22b-e, 28, 31)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-01-22", "Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide",
     "Cloud Security 8/8: CI/CD pipeline security, K8s NetworkPolicy, AI DevSecOps",
     {"tag":"CI/CD","theme":"red","visual":"supply_chain_pipe","headline":"Trivy Snyk Vault Stack",
      "subheadline":"CI/CD pipeline security with Trivy Snyk and HashiCorp Vault integration",
      "kpi_value":"CI","kpi_label":"GATE","kpi_sub":"scan",
      "action":"BLOCK ON HIGH SEVERITY"},
     {"tag":"K8S NETPOL","theme":"amber","visual":"hub_spoke","headline":"NetworkPolicy + RBAC",
      "subheadline":"Kubernetes network policy and RBAC patterns for tenant isolation",
      "kpi_value":"NP","kpi_label":"RBAC","kpi_sub":"k8s"},
     {"tag":"AI DSO","theme":"blue","visual":"ai_agent_funnel","headline":"AI-Driven DevSecOps",
      "subheadline":"Cursor and Claude integration for AI-assisted DevSecOps reviews",
      "kpi_value":"AI","kpi_label":"DSO","kpi_sub":"asst"}),

    ("2026-01-22", "Cloud_Security_Trends_January_2026_Kubernetes_82_Percent_Production_VS_Code_Threats_CNCF_Survey",
     "Cloud Security Jan 2026: K8s 82% prod, VS Code tunnel abuse, CRI-O audit",
     {"tag":"K8S 82","theme":"red","visual":"container_escape","headline":"K8s 82% Production",
      "subheadline":"CNCF survey shows Kubernetes hits 82 percent production adoption",
      "kpi_value":"82","kpi_label":"K8s","kpi_sub":"prod",
      "action":"AUDIT POD SECURITY POSTURE"},
     {"tag":"VS CODE","theme":"amber","visual":"code_injection","headline":"VS Code Tunnel Abuse",
      "subheadline":"VS Code remote tunnel feature abused as a covert command and control",
      "kpi_value":"VSC","kpi_label":"C2","kpi_sub":"tun"},
     {"tag":"NTLMv1","theme":"blue","visual":"cve_chain","headline":"NTLMv1 Rainbow Tables",
      "subheadline":"Net-NTLMv1 rainbow tables published and CRI-O audit findings released",
      "kpi_value":"NTLM","kpi_label":"v1","kpi_sub":"rbow"}),

    ("2026-01-22", "KARA_Ransomware_Trends_Report_2025_Q3_Analysis_SK_Shieldus_EQST",
     "KARA Q3 2025 ransomware: LockBit 5.0, Akira, INC ransom, Zero Trust",
     {"tag":"RANSOM Q3","theme":"red","visual":"ransomware_lock","headline":"LockBit 5.0 + Akira",
      "subheadline":"LockBit 5.0 Akira and INC Ransomware lead Q3 2025 attack volume",
      "kpi_value":"Q3","kpi_label":"2025","kpi_sub":"rep",
      "action":"REFRESH IR + BACKUP DRILL"},
     {"tag":"TTPs","theme":"amber","visual":"data_exfil","headline":"Updated TTPs",
      "subheadline":"Updated YARA Sigma detection rules and TTP coverage analysis",
      "kpi_value":"TTP","kpi_label":"YARA","kpi_sub":"sigma"},
     {"tag":"ZERO TRUST","theme":"blue","visual":"hub_spoke","headline":"Zero Trust Defense",
      "subheadline":"Zero Trust defense and incident response checklist for enterprises",
      "kpi_value":"ZT","kpi_label":"IR","kpi_sub":"chk"}),

    ("2026-01-22", "KISA_Security_Advisory_Ransomware_Prevention_Linux_Rootkit_Detection_Guide_Analysis",
     "KISA advisory: 3-2-1 backup, Linux rootkit detection, smishing alerts",
     {"tag":"3-2-1 BACKUP","theme":"red","visual":"ransomware_lock","headline":"3-2-1 Backup Strategy",
      "subheadline":"3-2-1 backup strategy for ransomware containment with offline copies",
      "kpi_value":"3-2-1","kpi_label":"BKUP","kpi_sub":"off",
      "action":"VERIFY OFFLINE RESTORE"},
     {"tag":"ROOTKIT","theme":"amber","visual":"code_injection","headline":"chkrootkit + rkhunter",
      "subheadline":"Linux kernel rootkit detection via chkrootkit and rkhunter workflows",
      "kpi_value":"RKT","kpi_label":"LIN","kpi_sub":"scan"},
     {"tag":"SMISHING","theme":"blue","visual":"data_exfil","headline":"Smishing + Phishing Alert",
      "subheadline":"E-commerce breach driving wave of smishing and phishing campaigns",
      "kpi_value":"SMS","kpi_label":"PHISH","kpi_sub":"wave"}),

    ("2026-01-22", "Security_Vendor_Blog_Weekly_Review",
     "Vendor blog weekly: VS Code tunnel, ACME cert flaw, AI Agent NHI, HashiCorp",
     {"tag":"VS CODE","theme":"red","visual":"code_injection","headline":"VS Code Tunnel Wave",
      "subheadline":"VS Code remote tunnel abuse spreads to additional vendor advisories",
      "kpi_value":"VSC","kpi_label":"TUN","kpi_sub":"wave",
      "action":"DISABLE UNUSED TUNNELS"},
     {"tag":"ACME","theme":"amber","visual":"cve_chain","headline":"ACME Certificate Flaw",
      "subheadline":"ACME certificate-issuance vulnerability affects automation workflows",
      "kpi_value":"ACME","kpi_label":"CERT","kpi_sub":"vuln"},
     {"tag":"NHI","theme":"blue","visual":"ai_agent_funnel","headline":"AI Agent Zero Trust NHI",
      "subheadline":"AI agent Zero Trust non-human identity management strategy guidance",
      "kpi_value":"NHI","kpi_label":"ZT","kpi_sub":"AI"}),

    ("2026-01-28", "Claude_MD_Security_Guide",
     "CLAUDE.md security guide: AI agent project security, never hardcode secrets",
     {"tag":"CLAUDE.MD","theme":"red","visual":"ai_agent_funnel","headline":"CLAUDE.md Drafting",
      "subheadline":"CLAUDE.md drafting patterns enforce secret hygiene across AI agents",
      "kpi_value":"CMD","kpi_label":"SEC","kpi_sub":"baseline",
      "action":"REVIEW + COMMIT CLAUDE.MD"},
     {"tag":"NO HARDCODE","theme":"amber","visual":"code_injection","headline":"Never Hardcode Secrets",
      "subheadline":"Never-hardcode-secrets principle with environment variable patterns",
      "kpi_value":"ENV","kpi_label":"NO","kpi_sub":"hard"},
     {"tag":"PRE-COMMIT","theme":"blue","visual":"supply_chain_pipe","headline":"Pre-commit Automation",
      "subheadline":"Log masking input validation and pre-commit automation workflows",
      "kpi_value":"PRE","kpi_label":"HOOK","kpi_sub":"auto"}),

    ("2026-01-31", "January_2026_Security_Digest_Monthly_Index",
     "January 2026 monthly index: AitM phishing, VMware KEV, AI agent threats, OT",
     {"tag":"MONTH BRIEF","theme":"red","visual":"hub_spoke","headline":"January 2026 Index",
      "subheadline":"Monthly index aggregates nine weekly digests of CVE cloud AI threats",
      "kpi_value":"JAN","kpi_label":"IDX","kpi_sub":"month",
      "action":"REVIEW KEV + PATCH GAPS"},
     {"tag":"TOP CVE","theme":"amber","visual":"cve_chain","headline":"VMware KEV + Microsoft AitM",
      "subheadline":"VMware KEV adds plus Microsoft AitM phishing campaign at scale",
      "kpi_value":"KEV","kpi_label":"CVE","kpi_sub":"jan"},
     {"tag":"AI + OT","theme":"blue","visual":"ai_agent_funnel","headline":"AI Agent + OT Attacks",
      "subheadline":"AI agent threats join the OT attack wave shaping January coverage",
      "kpi_value":"AI","kpi_label":"OT","kpi_sub":"jan"}),
]

def emit():
    for date, slug, title, hero, tr, br in SPECS:
        hero = {**hero, "index": "01"}
        tr = {**tr, "index": "02"}
        br = {**br, "index": "03"}
        year, month, day = date.split("-")
        block = {
            "date": date, "slug": slug,
            "date_str": f"{year}.{month}.{day}", "post_title": title,
            "url": f"https://tech.2twodragon.com/posts/{year}/{month}/{day}/{slug}/",
            "hero": hero, "top_right": tr, "bottom_right": br,
        }
        target = OUT / f"{date}-{slug}.yml"
        with target.open("w") as f:
            yaml.safe_dump(block, f, sort_keys=False, default_flow_style=False, allow_unicode=False, width=120)
        print(f"[ok] {target.name}")

if __name__ == "__main__":
    emit()

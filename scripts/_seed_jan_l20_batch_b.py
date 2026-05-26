#!/usr/bin/env python3
"""Seed L20 specs for Jan batch B (14x4, 15, 16, 17, 22a)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-01-14", "2025_ISMS-P_Certification_Complete_Guide_AWS_In_Environment_Management_System_Establishment_And_Protection_Measures_Implementation",
     "ISMS-P certification guide: 101 controls, AWS environment, NIST CSF 2.0 + AI",
     {"tag":"ISMS-P 2025","theme":"red","visual":"hub_spoke","headline":"ISMS-P 101 Controls",
      "subheadline":"Revised ISMS-P 101-control framework mapped to AWS environment baselines",
      "kpi_value":"101","kpi_label":"CTRL","kpi_sub":"new",
      "action":"MAP CONTROLS + SCHEDULE AUDIT"},
     {"tag":"NIST CSF","theme":"amber","visual":"cve_chain","headline":"NIST CSF 2.0 Linkage",
      "subheadline":"NIST CSF 2.0 alignment strategy and CIS Benchmark compliance program",
      "kpi_value":"CSF","kpi_label":"2.0","kpi_sub":"link"},
     {"tag":"AI SECURITY","theme":"blue","visual":"ai_agent_funnel","headline":"AI Security Reqs",
      "subheadline":"AI security requirements integrate with traditional control families",
      "kpi_value":"AI","kpi_label":"REQ","kpi_sub":"map"}),

    ("2026-01-14", "AWS_Cloud_Security_Complete_Guide_IAMFrom_EKSTo_Security_Architecture",
     "AWS cloud security guide: IAM to EKS, defense in depth, least privilege",
     {"tag":"IAM CORE","theme":"red","visual":"hub_spoke","headline":"IAM Least Privilege",
      "subheadline":"IAM least-privilege baseline anchors VPC S3 RDS EKS hardening",
      "kpi_value":"IAM","kpi_label":"CORE","kpi_sub":"min",
      "action":"ROTATE KEYS + ENFORCE SCP"},
     {"tag":"EKS","theme":"amber","visual":"container_escape","headline":"EKS Hardening",
      "subheadline":"EKS pod security and runtime defense with namespace isolation",
      "kpi_value":"EKS","kpi_label":"POD","kpi_sub":"sec"},
     {"tag":"DEFENSE","theme":"blue","visual":"data_exfil","headline":"Defense In Depth",
      "subheadline":"Encryption logging and monitoring layered across AWS workloads",
      "kpi_value":"DiD","kpi_label":"LAYER","kpi_sub":"log"}),

    ("2026-01-14", "CSPM_DataDog_AWS_Security_Guide_Automated_Security_Setup_Verification_And_Compliance_Monitoring",
     "CSPM with DataDog: AWS misconfig detection, CIS ISMS-P PCI-DSS monitoring",
     {"tag":"CSPM","theme":"red","visual":"cve_chain","headline":"Misconfig Auto-Detect",
      "subheadline":"DataDog CSPM detects AWS misconfigurations across hundreds of accounts",
      "kpi_value":"DD","kpi_label":"CSPM","kpi_sub":"auto",
      "action":"WIRE FINDINGS TO SIEM"},
     {"tag":"COMPLIANCE","theme":"amber","visual":"hub_spoke","headline":"CIS + PCI Monitor",
      "subheadline":"CIS Benchmark ISMS-P and PCI-DSS continuous compliance monitoring",
      "kpi_value":"CIS","kpi_label":"PCI","kpi_sub":"mon"},
     {"tag":"RESPONSE","theme":"blue","visual":"data_exfil","headline":"Real-time Threat",
      "subheadline":"Real-time threat detection feeds automated remediation workflows",
      "kpi_value":"RT","kpi_label":"AUTO","kpi_sub":"resp"}),

    ("2026-01-14", "GCP_Cloud_Security_Complete_Guide_IAMFrom_GKETo_Security_Architecture",
     "GCP cloud security guide: IAM to GKE, Pod Security, Security Command Center",
     {"tag":"GCP IAM","theme":"red","visual":"hub_spoke","headline":"IAM + VPC Isolation",
      "subheadline":"GCP IAM least privilege with VPC network segmentation patterns",
      "kpi_value":"IAM","kpi_label":"VPC","kpi_sub":"min",
      "action":"REVIEW SCC FINDINGS"},
     {"tag":"GKE","theme":"amber","visual":"container_escape","headline":"GKE Pod Security",
      "subheadline":"GKE Pod Security Standards baseline and runtime hardening guidance",
      "kpi_value":"GKE","kpi_label":"POD","kpi_sub":"std"},
     {"tag":"SCC","theme":"blue","visual":"data_exfil","headline":"Security Command Center",
      "subheadline":"Security Command Center central findings and KMS encryption controls",
      "kpi_value":"SCC","kpi_label":"FIND","kpi_sub":"kms"}),

    ("2026-01-15", "Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide",
     "Cloud Security 8/7: Docker image scan, K8s PSS user-ns, Network Policies",
     {"tag":"DOCKER","theme":"red","visual":"container_escape","headline":"Image Scan Secrets",
      "subheadline":"Container image scanning secret management and non-root execution",
      "kpi_value":"DKR","kpi_label":"SCAN","kpi_sub":"sec",
      "action":"BLOCK ROOT + ROTATE SECRETS"},
     {"tag":"K8S PSS","theme":"amber","visual":"cve_chain","headline":"Pod Security + UserNS",
      "subheadline":"Kubernetes Pod Security Standards plus user namespaces and RBAC",
      "kpi_value":"PSS","kpi_label":"K8s","kpi_sub":"rbac"},
     {"tag":"NETPOL","theme":"blue","visual":"hub_spoke","headline":"Network Policies",
      "subheadline":"Kubernetes network policy designs for east-west segmentation",
      "kpi_value":"NP","kpi_label":"K8s","kpi_sub":"seg"}),

    ("2026-01-16", "Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis",
     "Postmortem: Next.js SSR error, Cloudflare WAF block, ALB 5XX cascade",
     {"tag":"SSR ERROR","theme":"red","visual":"code_injection","headline":"Next.js Location Ref",
      "subheadline":"Next.js SSR ReferenceError on location object triggers ALB 5XX cascade",
      "kpi_value":"SSR","kpi_label":"REF","kpi_sub":"err",
      "action":"ADD WINDOW GUARDS + CANARY"},
     {"tag":"CF WAF","theme":"amber","visual":"data_exfil","headline":"Cloudflare IP Block",
      "subheadline":"Cloudflare WAF IP ban policy compounded the broken health checks",
      "kpi_value":"CF","kpi_label":"WAF","kpi_sub":"ban"},
     {"tag":"ALB 5XX","theme":"blue","visual":"hub_spoke","headline":"ALB Health-Check Fail",
      "subheadline":"ALB target group health checks fail leading to multi-stage outage",
      "kpi_value":"5XX","kpi_label":"ALB","kpi_sub":"down"}),

    ("2026-01-17", "AI_Coding_Assistants_Comparison_Gemini_Claude_Code_ChatGPT_OpenCode_2025_2026_Research_Analysis",
     "AI coding assistants compared: Gemini, Claude Code, ChatGPT, OpenCode, DeepSeek",
     {"tag":"BENCHMARKS","theme":"red","visual":"ai_agent_funnel","headline":"SWE-Bench HumanEval",
      "subheadline":"SWE-Bench and HumanEval results compared across five AI coding tools",
      "kpi_value":"SWE","kpi_label":"BENCH","kpi_sub":"hu-e",
      "action":"PILOT WITH GUARDRAILS"},
     {"tag":"REPRODUCIBLE","theme":"amber","visual":"code_injection","headline":"Reproducibility Gap",
      "subheadline":"Reproducibility issues across releases and multilingual coverage gaps",
      "kpi_value":"REPRO","kpi_label":"GAP","kpi_sub":"lang"},
     {"tag":"FIELD GUIDE","theme":"blue","visual":"hub_spoke","headline":"Practical Field Guide",
      "subheadline":"Practical adoption guide weighing latency cost and review workflow",
      "kpi_value":"GUIDE","kpi_label":"OPS","kpi_sub":"cost"}),

    ("2026-01-22", "AWS_GCP_Cloud_Updates_January_2026_EC2_G7e_X8i_Bangkok_Region_European_Sovereign_Cloud",
     "AWS GCP Jan 2026: EC2 G7e Blackwell, X8i SAP, Bangkok, Sovereign Cloud, Gemini 3",
     {"tag":"EC2 G7e","theme":"red","visual":"hub_spoke","headline":"G7e Blackwell GPU",
      "subheadline":"AWS EC2 G7e launches NVIDIA Blackwell GPU acceleration tier",
      "kpi_value":"G7e","kpi_label":"GPU","kpi_sub":"BLW",
      "action":"BUDGET + CAPACITY RESERVE"},
     {"tag":"BANGKOK","theme":"amber","visual":"data_exfil","headline":"GCP Bangkok Region",
      "subheadline":"GCP opens Bangkok region adding ASEAN data-residency coverage",
      "kpi_value":"GCP","kpi_label":"BKK","kpi_sub":"asean"},
     {"tag":"SOVEREIGN","theme":"blue","visual":"supply_chain_pipe","headline":"EU Sovereign Cloud",
      "subheadline":"European sovereign cloud lifts data-sovereignty guarantees for EU customers",
      "kpi_value":"EU","kpi_label":"SOV","kpi_sub":"data"}),
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

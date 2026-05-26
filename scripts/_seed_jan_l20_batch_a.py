#!/usr/bin/env python3
"""Seed L20 specs for Jan batch A (01, 03, 06, 08x2, 10, 11)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-01-01", "Tesla_FSD_2026_Complete_Guide_Model_Y_Juniper_Security_DevSecOps",
     "Tesla FSD 2026 guide: Model Y Juniper, HW4 500+ TOPS, OTA security, DevSecOps",
     {"tag":"TESLA FSD 2026","theme":"red","visual":"hub_spoke","headline":"FSD v14.2.1 Release",
      "subheadline":"Emergency vehicle handling, speed profiles, Model Y Juniper from $49,990",
      "kpi_value":"v14","kpi_label":"FSD","kpi_sub":"2.1",
      "action":"REVIEW OTA + SECURE BOOT PIPELINE"},
     {"tag":"HW4","theme":"amber","visual":"cve_chain","headline":"Hardware 4 500+ TOPS",
      "subheadline":"HW4 doubles inference throughput, 4680 battery, 357-mile range",
      "kpi_value":"500","kpi_label":"TOPS","kpi_sub":"HW4"},
     {"tag":"DEVSECOPS","theme":"blue","visual":"supply_chain_pipe","headline":"OTA + SBOM Chain",
      "subheadline":"Over-the-air update integrity, SBOM tracking, Secure Boot enforcement",
      "kpi_value":"OTA","kpi_label":"SBOM","kpi_sub":"sign"}),

    ("2026-01-03", "OWASP_2025_Latest_Update_Complete_Guide_Top_10_Agentic_AI_Security",
     "OWASP 2025 update: Top 10 supply chain + crypto, Agentic AI threats, PQC",
     {"tag":"OWASP TOP 10","theme":"red","visual":"supply_chain_pipe","headline":"OWASP Top 10:2025",
      "subheadline":"Software Supply Chain + Cryptographic Failures newly added to Top 10",
      "kpi_value":"T10","kpi_label":"2025","kpi_sub":"new",
      "action":"AUDIT DEPS + ROTATE CRYPTO"},
     {"tag":"AGENTIC AI","theme":"amber","visual":"ai_agent_funnel","headline":"Agentic AI Top 10",
      "subheadline":"Top 10 agentic AI threats covers tool poisoning and memory exfiltration",
      "kpi_value":"AI","kpi_label":"AGENT","kpi_sub":"top10"},
     {"tag":"POST-QUANTUM","theme":"blue","visual":"cve_chain","headline":"PQC + SecureCode v2",
      "subheadline":"Post-quantum migration guidance pairs with SecureCode v2.0 release",
      "kpi_value":"PQC","kpi_label":"v2.0","kpi_sub":"shift"}),

    ("2026-01-06", "DevSecOps_Viewing_Automotive_Security_Complete_Guide",
     "DevSecOps automotive security: SDV architecture, ISO 21434, UN R155/R156",
     {"tag":"SDV ARCHITECTURE","theme":"red","visual":"hub_spoke","headline":"SDV Security Stack",
      "subheadline":"Software-defined vehicle security across network, physical, and supply chain",
      "kpi_value":"SDV","kpi_label":"ARCH","kpi_sub":"layers",
      "action":"INTEGRATE TARA + CYBER PATCH"},
     {"tag":"ISO 21434","theme":"amber","visual":"cve_chain","headline":"ISO 21434 + R155",
      "subheadline":"Regulatory compliance under ISO 21434 and UN R155/R156 lifecycle",
      "kpi_value":"ISO","kpi_label":"21434","kpi_sub":"R155"},
     {"tag":"TOOL STACK","theme":"blue","visual":"supply_chain_pipe","headline":"SAST DAST SBOM",
      "subheadline":"Integrated SAST DAST SBOM tooling across the automotive DevSecOps pipeline",
      "kpi_value":"DSO","kpi_label":"STACK","kpi_sub":"sast"}),

    ("2026-01-08", "Blockchain_Cryptocurrency_Security_Complete_Guide_DevSecOps_From_Perspective_View_GitHub_Security_Tools_And_Best_Practice",
     "Blockchain crypto security: $3.4B losses, smart-contract tools, CI/CD",
     {"tag":"CRYPTO LOSS","theme":"red","visual":"data_exfil","headline":"3.4B USD Lost 2024-25",
      "subheadline":"3.4 billion USD lost including Bybit 1.5 billion USD heist analysis",
      "kpi_value":"3.4B","kpi_label":"USD","kpi_sub":"loss",
      "action":"AUDIT SMART CONTRACTS + KMS"},
     {"tag":"CONTRACT TOOLS","theme":"amber","visual":"code_injection","headline":"Slither Mythril Securify",
      "subheadline":"Smart contract security with Slither Mythril Securify static analysis",
      "kpi_value":"3","kpi_label":"TOOL","kpi_sub":"sast"},
     {"tag":"CI/CD","theme":"blue","visual":"supply_chain_pipe","headline":"CI/CD Pipeline Gates",
      "subheadline":"CI/CD pipeline integration blocks reentrancy and 51 percent attack vectors",
      "kpi_value":"CI","kpi_label":"GATE","kpi_sub":"audit"}),

    ("2026-01-08", "Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_And_GitHub_DevSecOps_Practical",
     "Cloud Security course 8/6: AWS WAF CloudFront, GitHub DevSecOps practical",
     {"tag":"AWS WAF","theme":"red","visual":"hub_spoke","headline":"WAF + CloudFront OAC",
      "subheadline":"AWS WAF and CloudFront OAI OAC rules with geo-blocking patterns",
      "kpi_value":"WAF","kpi_label":"CF","kpi_sub":"OAC",
      "action":"ENFORCE OAC + GEO BLOCK"},
     {"tag":"GITHUB DSO","theme":"amber","visual":"supply_chain_pipe","headline":"CodeQL Dependabot",
      "subheadline":"GitHub DevSecOps stack with CodeQL Dependabot and secret scanning",
      "kpi_value":"GH","kpi_label":"DSO","kpi_sub":"stack"},
     {"tag":"DATA MASK","theme":"blue","visual":"code_injection","headline":"SSRF + Data Masking",
      "subheadline":"SSRF patches and data masking for Jekyll-based security blogs",
      "kpi_value":"SSRF","kpi_label":"MASK","kpi_sub":"jekyll"}),

    ("2026-01-10", "2026_DevSecOps_Roadmap_Complete_Guide_Analysis",
     "2026 DevSecOps roadmap: 93 items, OWASP 2025, NIST CSF 2.0, GHAS",
     {"tag":"ROADMAP","theme":"red","visual":"hub_spoke","headline":"93 Learning Items",
      "subheadline":"roadmap.sh 2026 DevSecOps roadmap maps 93 items across the lifecycle",
      "kpi_value":"93","kpi_label":"ITEM","kpi_sub":"plan",
      "action":"PRIORITIZE OWASP + NIST"},
     {"tag":"FRAMEWORKS","theme":"amber","visual":"cve_chain","headline":"OWASP + NIST CSF 2",
      "subheadline":"OWASP Top 10:2025 ties into NIST CSF 2.0 and GHAS integration",
      "kpi_value":"CSF","kpi_label":"2.0","kpi_sub":"map"},
     {"tag":"AI / ML","theme":"blue","visual":"ai_agent_funnel","headline":"AI ML Security Automation",
      "subheadline":"AI ML security automation with SAST DAST IAST plus SBOM tooling",
      "kpi_value":"AI","kpi_label":"ML","kpi_sub":"auto"}),

    ("2026-01-11", "AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective",
     "AI music video gen guide: Suno V5, Veo 3, Midjourney V1, Zero-Trust",
     {"tag":"SUNO V5","theme":"red","visual":"ai_agent_funnel","headline":"Suno V5 MIDI Export",
      "subheadline":"Suno V5 MIDI export pairs with Veo 3 multishot 1080p generation",
      "kpi_value":"V5","kpi_label":"SUNO","kpi_sub":"midi",
      "action":"GATE API KEYS + REVIEW EULA"},
     {"tag":"VEO 3","theme":"amber","visual":"data_exfil","headline":"Veo 3 + Midjourney V1",
      "subheadline":"Veo 3 1080p multi-shot pipeline with Midjourney Video V1 workflows",
      "kpi_value":"VEO","kpi_label":"3","kpi_sub":"1080p"},
     {"tag":"ZERO TRUST","theme":"blue","visual":"hub_spoke","headline":"Zero-Trust API Key",
      "subheadline":"Zero-trust API key management with data privacy controls for gen-AI",
      "kpi_value":"ZTA","kpi_label":"KEYS","kpi_sub":"vault"}),
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

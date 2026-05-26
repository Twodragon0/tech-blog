#!/usr/bin/env python3
"""Seed L20 specs for Feb batch E (14, 16, 20, 25, 28x2)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-02-14", "Weekly_Security_Digest_Microsoft_Zero_Day_Apple_Ivanti_EPMM",
     "2026 W7 security: MS 6 zero-days, Apple CVE-2026-20700, Ivanti EPMM, SAP 9.9",
     {"tag":"MS 0-DAY x6","theme":"red","visual":"cve_chain","headline":"MS 6 Zero-Days",
      "subheadline":"Microsoft Patch Tuesday ships six zero-day fixes for active exploitation",
      "kpi_value":"6","kpi_label":"0DAY","kpi_sub":"MSFT",
      "action":"PATCH NOW + AUDIT LOGS"},
     {"tag":"APPLE 20700","theme":"amber","visual":"code_injection","headline":"Apple CVE-2026-20700",
      "subheadline":"Apple CVE-2026-20700 targeted attack chain affects mobile and macOS",
      "kpi_value":"20700","kpi_label":"CVE","kpi_sub":"APPL"},
     {"tag":"IVANTI EPMM","theme":"blue","visual":"data_exfil","headline":"Ivanti EPMM Mass Exploit",
      "subheadline":"Ivanti EPMM mass exploitation plus SAP CVSS 9.9 SQL injection wave",
      "kpi_value":"9.9","kpi_label":"SAP","kpi_sub":"SQLi"}),

    ("2026-02-16", "Daily_Tech_Digest_RSS_Roundup",
     "Daily tech 2026-02-16: LLM inference, Windows native dev, crypto trends, smart home",
     {"tag":"LLM INFER","theme":"red","visual":"ai_agent_funnel","headline":"LLM Inference Tune",
      "subheadline":"LLM inference optimization strategies for low-latency production serving",
      "kpi_value":"LLM","kpi_label":"OPT","kpi_sub":"infer",
      "action":"BENCHMARK QUANT + KV CACHE"},
     {"tag":"WIN NATIVE","theme":"amber","visual":"hub_spoke","headline":"Windows Native Dev",
      "subheadline":"Windows native development pipeline improvements and tooling refresh",
      "kpi_value":"WIN","kpi_label":"NAT","kpi_sub":"dev"},
     {"tag":"CRYPTO + UI","theme":"blue","visual":"data_exfil","headline":"Crypto + Light UI Libs",
      "subheadline":"Crypto market trends plus ultra-light UI libraries and subscription shifts",
      "kpi_value":"UI","kpi_label":"LITE","kpi_sub":"libs"}),

    ("2026-02-20", "Tech_Blog_Weekly_Digest_AI_Data_Cloud",
     "Tech blog 2026-02-20: AI alignment, EKS Flyte, Docker security, cloud-native",
     {"tag":"AI ALIGN","theme":"red","visual":"ai_agent_funnel","headline":"AI Alignment Research",
      "subheadline":"AI alignment research updates with EKS Flyte workflow patterns",
      "kpi_value":"ALN","kpi_label":"AI","kpi_sub":"res",
      "action":"REVIEW WORKFLOW ISOLATION"},
     {"tag":"EKS FLYTE","theme":"amber","visual":"container_escape","headline":"EKS Flyte Workflow",
      "subheadline":"EKS Flyte workflow integration spans multi-tenant ML platform teams",
      "kpi_value":"EKS","kpi_label":"FLY","kpi_sub":"wf"},
     {"tag":"CLOUD-NATIVE","theme":"blue","visual":"hub_spoke","headline":"Docker + Cloud-Native",
      "subheadline":"Docker security guidance and cloud-native ecosystem trend roundup",
      "kpi_value":"DKR","kpi_label":"CN","kpi_sub":"sec"}),

    ("2026-02-25", "Claude_Code_OpenCode_Best_Practices",
     "Claude Code + OpenCode best practices: 38 patterns, CLAUDE.md, agent teams",
     {"tag":"38 PATTERNS","theme":"red","visual":"ai_agent_funnel","headline":"38 Best Practices",
      "subheadline":"38 best practices spanning Claude Code and OpenCode adoption guidance",
      "kpi_value":"38","kpi_label":"BP","kpi_sub":"AI",
      "action":"ADOPT + REVIEW QUARTERLY"},
     {"tag":"CONTEXT WIN","theme":"amber","visual":"hub_spoke","headline":"Context + CLAUDE.md",
      "subheadline":"Context window optimization paired with CLAUDE.md authoring patterns",
      "kpi_value":"CTX","kpi_label":"WIN","kpi_sub":"opt"},
     {"tag":"AGENT TEAMS","theme":"blue","visual":"supply_chain_pipe","headline":"Agent Teams + Hooks",
      "subheadline":"Agent team orchestration with hooks skills and prompting techniques",
      "kpi_value":"TEAM","kpi_label":"HOOK","kpi_sub":"sk"}),

    ("2026-02-28", "AI_Agent_Security_Architecture_Design_Guide",
     "AI Agent security architecture: Stateful Runtime, AgentCore, Continuous Eval",
     {"tag":"STATEFUL RT","theme":"red","visual":"ai_agent_funnel","headline":"Stateful Runtime",
      "subheadline":"OpenAI Stateful Runtime patterns for long-running secure AI agents",
      "kpi_value":"OAI","kpi_label":"RT","kpi_sub":"state",
      "action":"DESIGN STATE + AUDIT TRAIL"},
     {"tag":"AGENTCORE","theme":"amber","visual":"hub_spoke","headline":"Bedrock AgentCore",
      "subheadline":"Amazon Bedrock AgentCore orchestration with strict isolation boundaries",
      "kpi_value":"AWS","kpi_label":"CORE","kpi_sub":"AI"},
     {"tag":"CONT EVAL","theme":"blue","visual":"cve_chain","headline":"Google Continuous Eval",
      "subheadline":"Google Continuous Evaluation aligned with OWASP Agentic Top 10",
      "kpi_value":"CE","kpi_label":"GCP","kpi_sub":"owasp"}),

    ("2026-02-28", "February_2026_Security_Digest_Monthly_Index",
     "Feb 2026 monthly index: OpenSSL AI, ransomware evolution, APT28 Lazarus UAC-0050",
     {"tag":"MONTH BRIEF","theme":"red","visual":"hub_spoke","headline":"February 2026 Index",
      "subheadline":"Monthly index aggregates 22 weekly digests of February 2026 threats",
      "kpi_value":"22","kpi_label":"FEB","kpi_sub":"month",
      "action":"REVIEW MONTHLY KEV + IR"},
     {"tag":"OPENSSL AI","theme":"amber","visual":"cve_chain","headline":"OpenSSL AI Detect",
      "subheadline":"OpenSSL AI auto-detection supply-chain attacks ransomware evolution",
      "kpi_value":"SSL","kpi_label":"AI","kpi_sub":"feb"},
     {"tag":"APT GROUPS","theme":"blue","visual":"data_exfil","headline":"APT28 Lazarus UAC-0050",
      "subheadline":"APT28 Lazarus and UAC-0050 threat actor activity dominates February",
      "kpi_value":"APT","kpi_label":"3","kpi_sub":"feb"}),
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

#!/usr/bin/env python3
"""Seed L20 specs for Feb batch D (01, 02x2, 03, 04, 05, 09x2, 10x3)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

SPECS = [
    ("2026-02-01", "Agentic_AI_Security_2026_Attack_Vectors_Defense_Architecture",
     "Agentic AI Security 2026: tool poisoning, prompt injection, defense architecture",
     {"tag":"TOOL POISON","theme":"red","visual":"ai_agent_funnel","headline":"Tool Poisoning Chain",
      "subheadline":"Agentic AI tool poisoning and tool-chain attacks target connected tools",
      "kpi_value":"TP","kpi_label":"CHAIN","kpi_sub":"AI",
      "action":"AUDIT AGENT TOOL SCOPES"},
     {"tag":"PROMPT INJECT","theme":"amber","visual":"code_injection","headline":"Prompt Injection",
      "subheadline":"Prompt injection paired with JWT signing-key leakage incidents",
      "kpi_value":"PI","kpi_label":"JWT","kpi_sub":"AI"},
     {"tag":"DEFENSE","theme":"blue","visual":"hub_spoke","headline":"Chrome + CrowdStrike",
      "subheadline":"Google Chrome and CrowdStrike Falcon agentic AI defense architecture",
      "kpi_value":"DEF","kpi_label":"ARCH","kpi_sub":"AI"}),

    ("2026-02-02", "Weekly_Security_Threat_Intelligence_Digest",
     "Threat intel 2026-02-02: Notepad++ supply chain, SK Shieldus, HashiCorp Boundary",
     {"tag":"SUPPLY CHAIN","theme":"red","visual":"supply_chain_pipe","headline":"Notepad++ Supply Hit",
      "subheadline":"Notepad++ nation-state supply chain attack mapped to MITRE T1195",
      "kpi_value":"NPP","kpi_label":"T1195","kpi_sub":"nat",
      "action":"PATCH NPP + AUDIT WIN HOSTS"},
     {"tag":"SK SHIELDUS","theme":"amber","visual":"ransomware_lock","headline":"SK Shieldus Nov-Jan",
      "subheadline":"SK Shieldus brief covers Vertical AI BlackField Sinobi Gentlemen ransom",
      "kpi_value":"SKS","kpi_label":"BRF","kpi_sub":"3mo"},
     {"tag":"HASHICORP","theme":"blue","visual":"hub_spoke","headline":"Boundary 0.21 RDP",
      "subheadline":"HashiCorp Boundary 0.21 ships passwordless RDP for privileged access",
      "kpi_value":"HC","kpi_label":"B0.21","kpi_sub":"rdp"}),

    ("2026-02-02", "Weekly_Tech_AI_Blockchain_Digest",
     "Tech AI Blockchain 2026-02-02: Apple MLX, Bitcoin crash $19B, DeFi security",
     {"tag":"APPLE MLX","theme":"red","visual":"ai_agent_funnel","headline":"A18 Neural MLX Bug",
      "subheadline":"Apple A18 Pro Neural Engine MLX bug surfaces in inference workloads",
      "kpi_value":"A18","kpi_label":"MLX","kpi_sub":"bug",
      "action":"PIN MLX VERSION + RETEST"},
     {"tag":"BTC CRASH","theme":"amber","visual":"data_exfil","headline":"Bitcoin Crash 19B",
      "subheadline":"Bitcoin weekend crash drives 19 billion USD in cascade liquidations",
      "kpi_value":"19B","kpi_label":"BTC","kpi_sub":"liq"},
     {"tag":"DEFI","theme":"blue","visual":"code_injection","headline":"DeFi Security Incident",
      "subheadline":"DeFi security incident with Claude Code tips and FOSDEM 2026 recap",
      "kpi_value":"DEFI","kpi_label":"HIT","kpi_sub":"recap"}),

    ("2026-02-03", "Weekly_Security_DevOps_Digest",
     "Security DevOps 2026-02-03: Clawdbot RCE, ClawHavoc 335 Atomic, MDM, VS Code",
     {"tag":"AI AGENT RCE","theme":"red","visual":"ai_agent_funnel","headline":"Clawdbot 1-Click RCE",
      "subheadline":"AI Agent Clawdbot Moltbot CVE-2026-25253 one-click remote code exec",
      "kpi_value":"25253","kpi_label":"CVE","kpi_sub":"AI",
      "action":"PATCH AGENT + WAF RULE"},
     {"tag":"CLAWHAVOC","theme":"amber","visual":"supply_chain_pipe","headline":"ClawHavoc 335 Stealer",
      "subheadline":"ClawHavoc campaign delivers 335 Atomic Stealer payloads via fake updates",
      "kpi_value":"335","kpi_label":"ATM","kpi_sub":"steal"},
     {"tag":"MDM + VSCODE","theme":"blue","visual":"code_injection","headline":"MDM + Fake VSCode",
      "subheadline":"MDM application-control strategy and fake VS Code extension wave",
      "kpi_value":"MDM","kpi_label":"VSC","kpi_sub":"fake"}),

    ("2026-02-04", "AI_vs_Claude_Code_AI_Coding_Assistant_Comparison",
     "AI vs Claude Code: CVE-2026-25253 RCE, 400+ malicious skills, SOC 2 certified",
     {"tag":"CVE-2026-25253","theme":"red","visual":"cve_chain","headline":"AI Agent RCE Detail",
      "subheadline":"CVE-2026-25253 RCE vulnerability deep-dive across AI coding agents",
      "kpi_value":"25253","kpi_label":"CVE","kpi_sub":"RCE",
      "action":"PIN AGENT + LIMIT MCP"},
     {"tag":"MALICIOUS SKILLS","theme":"amber","visual":"ai_agent_funnel","headline":"400+ Malicious Skills",
      "subheadline":"400 plus malicious skills campaign distributed across agent stores",
      "kpi_value":"400","kpi_label":"SKILL","kpi_sub":"mal"},
     {"tag":"SOC 2","theme":"blue","visual":"hub_spoke","headline":"SOC 2 + DevSecOps",
      "subheadline":"SOC 2 Type II certification with DevSecOps CI/CD and FinOps ROI",
      "kpi_value":"SOC2","kpi_label":"DSO","kpi_sub":"finops"}),

    ("2026-02-05", "AI_Content_Creator_Workflow_2026_Blog_Video_Music_Animation",
     "AI content creator 2026: Claude 4.5, Qwen3-TTS, Suno, Runway, D-ID, Python pipeline",
     {"tag":"BLOG GEN","theme":"red","visual":"ai_agent_funnel","headline":"Claude 4.5 Blog Gen",
      "subheadline":"Claude Opus 4.5 blog generation with Qwen3-TTS open-source voice",
      "kpi_value":"4.5","kpi_label":"BLOG","kpi_sub":"gen",
      "action":"PILOT + AUDIT API KEYS"},
     {"tag":"VIDEO + MUSIC","theme":"amber","visual":"data_exfil","headline":"Suno + Runway + D-ID",
      "subheadline":"Suno music Runway Gen-3 video and D-ID animation in one stack",
      "kpi_value":"SUN","kpi_label":"RUN","kpi_sub":"DID"},
     {"tag":"PIPELINE","theme":"blue","visual":"supply_chain_pipe","headline":"Python E2E Pipeline",
      "subheadline":"Python end-to-end pipeline and three case studies across the workflow",
      "kpi_value":"E2E","kpi_label":"PY","kpi_sub":"case"}),

    ("2026-02-09", "Blockchain_Tech_Digest_Bithumb_Bitcoin",
     "Blockchain 2026-02-09: Bithumb $4.4B misdirected, Bitcoin $71K, GBA shaders",
     {"tag":"BITHUMB","theme":"red","visual":"data_exfil","headline":"4.4B USD Misdirected",
      "subheadline":"Bithumb 4.4 billion USD bitcoin misdirected transaction operational fail",
      "kpi_value":"4.4B","kpi_label":"BTC","kpi_sub":"mis",
      "action":"REVIEW TX SIGN-OFF + 4 EYES"},
     {"tag":"BTC 71K","theme":"amber","visual":"hub_spoke","headline":"Bitcoin $71K Recovery",
      "subheadline":"Bitcoin recovers to 71K USD on institutional buying after weekend rout",
      "kpi_value":"71K","kpi_label":"BTC","kpi_sub":"inst"},
     {"tag":"GBA SHADERS","theme":"blue","visual":"code_injection","headline":"GameBoy 3D Shaders",
      "subheadline":"Game Boy 3D shader implementation case study and 2026 UX outlook",
      "kpi_value":"GBA","kpi_label":"3D","kpi_sub":"shad"}),

    ("2026-02-09", "Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic",
     "Security 2026-02-09: VirusTotal AI supply chain, SK Shieldus BlackField, AWS Agentic",
     {"tag":"VT AI","theme":"red","visual":"ai_agent_funnel","headline":"AI VirusTotal Supply",
      "subheadline":"AI VirusTotal integration hardens agent supply-chain telemetry",
      "kpi_value":"VT","kpi_label":"AI","kpi_sub":"supply",
      "action":"ENABLE VT FEED IN PIPELINE"},
     {"tag":"BLACKFIELD","theme":"amber","visual":"ransomware_lock","headline":"BlackField Ransom Rpt",
      "subheadline":"SK Shieldus BlackField ransomware analysis covers TTPs and IOCs",
      "kpi_value":"BLK","kpi_label":"FLD","kpi_sub":"rep"},
     {"tag":"AWS AGENTIC","theme":"blue","visual":"hub_spoke","headline":"AWS Agentic AI Case",
      "subheadline":"AWS Agentic AI delivered by two engineers in seven weeks case study",
      "kpi_value":"2x7","kpi_label":"AWS","kpi_sub":"agent"}),

    ("2026-02-10", "AI_Cloud_Digest_Meta_Prometheus_Google_OTLP_AWS",
     "AI Cloud 2026-02-10: Meta Prometheus GW cluster, Google OTLP, AWS Claude 4.6 Bedrock",
     {"tag":"META PROM","theme":"red","visual":"hub_spoke","headline":"Meta Prometheus GW",
      "subheadline":"Meta Prometheus gigawatt-class AI cluster powers next-gen training",
      "kpi_value":"GW","kpi_label":"META","kpi_sub":"AI",
      "action":"REVIEW CAPACITY + CARBON"},
     {"tag":"OTLP","theme":"amber","visual":"supply_chain_pipe","headline":"Google Cloud OTLP",
      "subheadline":"Google Cloud native OTLP telemetry support arrives across services",
      "kpi_value":"OTLP","kpi_label":"GCP","kpi_sub":"obs"},
     {"tag":"BEDROCK","theme":"blue","visual":"ai_agent_funnel","headline":"AWS Claude 4.6 Bedrock",
      "subheadline":"AWS Bedrock adds Claude Opus 4.6 and ChatGPT GenAI.mil platform",
      "kpi_value":"4.6","kpi_label":"BDR","kpi_sub":"gov"}),

    ("2026-02-10", "DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin",
     "DevOps Blockchain 2026-02-10: CNCF Velocity, Cluster API v1.12, Hexagate, BTC 70K",
     {"tag":"CNCF VELOCITY","theme":"red","visual":"hub_spoke","headline":"CNCF Project Velocity",
      "subheadline":"CNCF Project Velocity 2025 outlines cloud-native maturity outlook",
      "kpi_value":"CNCF","kpi_label":"VEL","kpi_sub":"2025",
      "action":"REVIEW PROJECT GRADUATIONS"},
     {"tag":"CAPI v1.12","theme":"amber","visual":"container_escape","headline":"Cluster API v1.12",
      "subheadline":"Cluster API v1.12 ships in-place upgrade flow for managed control planes",
      "kpi_value":"v1.12","kpi_label":"CAPI","kpi_sub":"inpl"},
     {"tag":"HEXAGATE","theme":"blue","visual":"data_exfil","headline":"Hexagate + BTC 70K",
      "subheadline":"Chainalysis Hexagate MegaETH integration with Bitcoin 70K recovery",
      "kpi_value":"HEX","kpi_label":"MET","kpi_sub":"btc"}),

    ("2026-02-10", "Security_Digest_SolarWinds_UNC3886_LLM_Attack",
     "Security 2026-02-10: SolarWinds RCE, UNC3886 Singapore telco, LLM GRPO, UNC1069 deepfake",
     {"tag":"SOLARWINDS RCE","theme":"red","visual":"cve_chain","headline":"SolarWinds WHD RCE",
      "subheadline":"SolarWinds WHD multi-stage RCE chain tracked as CVE-2025-40551",
      "kpi_value":"40551","kpi_label":"CVE","kpi_sub":"WHD",
      "action":"PATCH WHD + ROTATE CREDS"},
     {"tag":"UNC3886","theme":"amber","visual":"data_exfil","headline":"UNC3886 SG Telco",
      "subheadline":"Chinese UNC3886 espionage targets Singapore telecommunications providers",
      "kpi_value":"UNC","kpi_label":"3886","kpi_sub":"SG"},
     {"tag":"LLM GRPO","theme":"blue","visual":"ai_agent_funnel","headline":"LLM GRPO Bypass",
      "subheadline":"LLM safety alignment GRPO neutralized plus UNC1069 deepfake crypto attacks",
      "kpi_value":"GRPO","kpi_label":"LLM","kpi_sub":"bypass"}),
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

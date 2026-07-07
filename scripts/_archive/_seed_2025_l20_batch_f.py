#!/usr/bin/env python3
"""Seed L20 specs for 2025 batch F (Apr-Jun, 13 posts)."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_data" / "l20_covers"

# (date, slug_for_filename, post_title, hero, top_right, bottom_right)
# slug_for_filename must match each post's `image:` short-name (case-sensitive).
SPECS = [
    ("2025-04-29", "SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_and_MFA_Importance",
     "SKT USIM breach response: IMEI check, USIM eSIM replace, MFA importance",
     {"tag":"USIM BREACH","theme":"red","visual":"data_exfil","headline":"SKT USIM Leak Response",
      "subheadline":"SKT USIM data leak triggers SIM-swap risk for millions of subscribers",
      "kpi_value":"USIM","kpi_label":"LEAK","kpi_sub":"SKT",
      "action":"REPLACE USIM + ENABLE MFA NOW"},
     {"tag":"IMEI CHECK","theme":"amber","visual":"cve_chain","headline":"IMEI Verification",
      "subheadline":"IMEI verification procedure with carrier-side validation steps",
      "kpi_value":"IMEI","kpi_label":"CHK","kpi_sub":"sim"},
     {"tag":"MFA","theme":"blue","visual":"hub_spoke","headline":"MFA + Banking Lockdown",
      "subheadline":"Enable MFA across banking accounts and carrier security services",
      "kpi_value":"MFA","kpi_label":"BANK","kpi_sub":"lock"}),

    ("2025-04-30", "Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage",
     "Public PC safety: FIDO2 passkey, OTP, strong password manager, AI phishing",
     {"tag":"PASSKEY","theme":"red","visual":"hub_spoke","headline":"FIDO2 Passkey + WebAuthn",
      "subheadline":"FIDO2 passkey WebAuthn authentication for safe public PC use",
      "kpi_value":"FIDO","kpi_label":"PASS","kpi_sub":"key",
      "action":"ENROLL PASSKEY + DISABLE PWD"},
     {"tag":"OTP","theme":"amber","visual":"cve_chain","headline":"OTP 2-Factor Strength",
      "subheadline":"OTP two-factor authentication strengthens session protection",
      "kpi_value":"OTP","kpi_label":"2FA","kpi_sub":"step"},
     {"tag":"AI PHISH","theme":"blue","visual":"ai_agent_funnel","headline":"AI Phishing Defense",
      "subheadline":"AI phishing defense strategy and password manager best practices",
      "kpi_value":"AI","kpi_label":"PHISH","kpi_sub":"def"}),

    ("2025-05-02", "Cloud_Security_Course_7Batch_-_3Week_AWS_Security_and_Finops",
     "Cloud Security 7/3: AWS security services, FinOps framework, Well-Architected",
     {"tag":"AWS SECURITY","theme":"red","visual":"hub_spoke","headline":"IAM Org CloudTrail",
      "subheadline":"AWS IAM Organizations CloudTrail GuardDuty Security Hub structure",
      "kpi_value":"IAM","kpi_label":"AWS","kpi_sub":"core",
      "action":"MAP ACCOUNTS + ENABLE GUARD"},
     {"tag":"FINOPS","theme":"amber","visual":"data_exfil","headline":"FinOps Framework",
      "subheadline":"FinOps framework with cost optimization and budget control patterns",
      "kpi_value":"FIN","kpi_label":"OPS","kpi_sub":"cost"},
     {"tag":"WELL-ARCH","theme":"blue","visual":"cve_chain","headline":"Well-Architected Pillars",
      "subheadline":"AWS Well-Architected Framework applied to cloud security baselines",
      "kpi_value":"WA","kpi_label":"PIL","kpi_sub":"5"}),

    ("2025-05-02", "Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide",
     "Kandji macOS: MDM policies, FIDO2, Zero Trust, AI threat detection",
     {"tag":"KANDJI MDM","theme":"red","visual":"hub_spoke","headline":"Kandji macOS MDM",
      "subheadline":"Kandji-based macOS endpoint management with MDM policy enforcement",
      "kpi_value":"MDM","kpi_label":"KANDJI","kpi_sub":"mac",
      "action":"ENROLL DEVICES + APPLY BASELINE"},
     {"tag":"FIDO2","theme":"amber","visual":"cve_chain","headline":"FIDO2 + WebAuthn",
      "subheadline":"Passkey-based FIDO2 WebAuthn authentication integrated with Kandji",
      "kpi_value":"FIDO","kpi_label":"AUTH","kpi_sub":"key"},
     {"tag":"ZERO TRUST","theme":"blue","visual":"ai_agent_funnel","headline":"Zero Trust + AI",
      "subheadline":"Zero Trust architecture with AI-driven threat detection on endpoints",
      "kpi_value":"ZT","kpi_label":"AI","kpi_sub":"det"}),

    ("2025-05-09", "Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_and_ISMS_Response_Guide",
     "Cloud Security 7/4: Inspector, Security Hub, GuardDuty, ISMS-P response",
     {"tag":"INSPECTOR","theme":"red","visual":"cve_chain","headline":"AWS Inspector",
      "subheadline":"AWS Inspector vulnerability scanning for EC2 ECR and Lambda functions",
      "kpi_value":"INSP","kpi_label":"AWS","kpi_sub":"scan",
      "action":"SCHEDULE SCAN + TRIAGE"},
     {"tag":"SEC HUB","theme":"amber","visual":"hub_spoke","headline":"Security Hub + GuardDuty",
      "subheadline":"Security Hub centralizes findings from GuardDuty Macie and Config",
      "kpi_value":"HUB","kpi_label":"AWS","kpi_sub":"agg"},
     {"tag":"ISMS-P","theme":"blue","visual":"data_exfil","headline":"ISMS-P Response",
      "subheadline":"ISMS-P certification response strategy with re:Invent updates",
      "kpi_value":"ISMS","kpi_label":"P","kpi_sub":"audit"}),

    ("2025-05-16", "Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA",
     "Cloud Security 7/5: AWS Control Tower Landing Zone, ZTNA",
     {"tag":"CONTROL TWR","theme":"red","visual":"hub_spoke","headline":"AWS Control Tower",
      "subheadline":"AWS Control Tower Landing Zone Guardrails and SCP-based multi-account",
      "kpi_value":"CT","kpi_label":"AWS","kpi_sub":"land",
      "action":"SET LANDING ZONE + SCPs"},
     {"tag":"ZTNA","theme":"amber","visual":"data_exfil","headline":"Zero Trust Network",
      "subheadline":"ZTNA Zero Trust Network Access concept and AWS implementation patterns",
      "kpi_value":"ZTNA","kpi_label":"NET","kpi_sub":"AWS"},
     {"tag":"GOVERNANCE","theme":"blue","visual":"cve_chain","headline":"2025 Governance",
      "subheadline":"2025 AWS governance updates affecting enterprise account strategies",
      "kpi_value":"GOV","kpi_label":"2025","kpi_sub":"AWS"}),

    ("2025-05-23", "Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security",
     "Cloud Security 7/6: AWS WAF, Cloudflare DDoS, GitHub Dependabot CodeQL",
     {"tag":"AWS WAF","theme":"red","visual":"hub_spoke","headline":"AWS WAF + Managed Rules",
      "subheadline":"AWS WAF rule design with managed rule group composition patterns",
      "kpi_value":"WAF","kpi_label":"AWS","kpi_sub":"rule",
      "action":"DEPLOY MANAGED RULES"},
     {"tag":"CLOUDFLARE","theme":"amber","visual":"data_exfil","headline":"Cloudflare DDoS",
      "subheadline":"Cloudflare DDoS and WAF security policies for edge protection",
      "kpi_value":"CF","kpi_label":"DDoS","kpi_sub":"edge"},
     {"tag":"GITHUB","theme":"blue","visual":"supply_chain_pipe","headline":"Dependabot + CodeQL",
      "subheadline":"GitHub Dependabot CodeQL and secret scanning DevSecOps automation",
      "kpi_value":"GH","kpi_label":"DSO","kpi_sub":"auto"}),

    ("2025-05-24", "Amazon_Q_Developerand_GitHub_Advanced_Security_Security_and_AWS",
     "Amazon Q Developer + GHAS: AI code review, SAST SCA, AWS cost optimize",
     {"tag":"AMAZON Q","theme":"red","visual":"ai_agent_funnel","headline":"Amazon Q Developer",
      "subheadline":"Amazon Q Developer AI-powered code generation and review",
      "kpi_value":"AmQ","kpi_label":"DEV","kpi_sub":"AI",
      "action":"PILOT + AUDIT AI CODE"},
     {"tag":"GHAS","theme":"amber","visual":"supply_chain_pipe","headline":"GitHub Advanced Sec",
      "subheadline":"GitHub Advanced Security SAST SCA secret scanning enforcement",
      "kpi_value":"GHAS","kpi_label":"SAST","kpi_sub":"sca"},
     {"tag":"COST OPT","theme":"blue","visual":"data_exfil","headline":"AWS Cost Optimize",
      "subheadline":"AWS cost optimization recommendations from Q Developer integrated",
      "kpi_value":"COST","kpi_label":"AWS","kpi_sub":"AmQ"}),

    ("2025-05-30", "Cloud_Security_Course_7Batch_-_7Week_Docker_and_Kubernetes",
     "Cloud Security 7/7: Docker basics, K8s architecture, Trivy Falco runtime",
     {"tag":"DOCKER","theme":"red","visual":"container_escape","headline":"Docker Fundamentals",
      "subheadline":"Docker image container Dockerfile fundamentals and security patterns",
      "kpi_value":"DKR","kpi_label":"BASE","kpi_sub":"fund",
      "action":"SCAN IMAGES + PIN BASE"},
     {"tag":"K8S","theme":"amber","visual":"hub_spoke","headline":"K8s Control Plane Node Pod",
      "subheadline":"Kubernetes Control Plane Node Pod architecture overview",
      "kpi_value":"K8s","kpi_label":"ARCH","kpi_sub":"node"},
     {"tag":"RUNTIME","theme":"blue","visual":"code_injection","headline":"Trivy + Falco Runtime",
      "subheadline":"Container runtime security with Trivy image scan and Falco threats",
      "kpi_value":"TRV","kpi_label":"FAL","kpi_sub":"rt"}),

    ("2025-05-30", "Kubernetes_Minikube_and_K9s_Practice_Guide",
     "Kubernetes practical: Minikube 1.37, K9s UI, User Namespaces, troubleshoot",
     {"tag":"MINIKUBE","theme":"red","visual":"container_escape","headline":"Minikube 1.37 Setup",
      "subheadline":"Minikube 1.37 install and configuration for local Kubernetes labs",
      "kpi_value":"1.37","kpi_label":"MINI","kpi_sub":"k8s",
      "action":"PIN VERSION + DRIVER CHECK"},
     {"tag":"K9S","theme":"amber","visual":"hub_spoke","headline":"K9s Terminal UI",
      "subheadline":"K9s terminal UI workflow for managing Kubernetes resources quickly",
      "kpi_value":"K9s","kpi_label":"UI","kpi_sub":"tui"},
     {"tag":"USER NS","theme":"blue","visual":"cve_chain","headline":"User Namespaces 2024-25",
      "subheadline":"K8s 2024-2025 security hardening User Namespaces and bound tokens",
      "kpi_value":"NS","kpi_label":"K8s","kpi_sub":"sec"}),

    ("2025-06-05", "Email_Delivery_Trust_Improve_SendGrid_SPF_DKIM_DMARC_Setup_Complete_Guide",
     "Email trust: SendGrid SPF DKIM DMARC, deliverability, DNS records",
     {"tag":"SPF","theme":"red","visual":"hub_spoke","headline":"SPF Sender Auth",
      "subheadline":"SPF record verifies authorized sending servers for the domain",
      "kpi_value":"SPF","kpi_label":"DNS","kpi_sub":"auth",
      "action":"PUBLISH SPF + ALIGN DOMAIN"},
     {"tag":"DKIM","theme":"amber","visual":"code_injection","headline":"DKIM Signing",
      "subheadline":"DKIM signature ensures email content integrity across hops",
      "kpi_value":"DKIM","kpi_label":"SIGN","kpi_sub":"key"},
     {"tag":"DMARC","theme":"blue","visual":"cve_chain","headline":"DMARC Policy + Report",
      "subheadline":"DMARC policy enforcement with aggregate and forensic reporting",
      "kpi_value":"DMARC","kpi_label":"POL","kpi_sub":"rep"}),

    ("2025-06-06", "Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide",
     "Cloud Security 7/8: CI/CD pipeline security, K8s RBAC PSS, image signing",
     {"tag":"CI/CD","theme":"red","visual":"supply_chain_pipe","headline":"CI/CD Security Stack",
      "subheadline":"CI/CD pipeline security with GitHub Actions SAST DAST secret scanning",
      "kpi_value":"CI","kpi_label":"DSO","kpi_sub":"stack",
      "action":"GATE ON HIGH SEVERITY"},
     {"tag":"K8S RBAC","theme":"amber","visual":"hub_spoke","headline":"RBAC + PSS + NetPol",
      "subheadline":"Kubernetes RBAC Pod Security Standards and Network Policy patterns",
      "kpi_value":"RBAC","kpi_label":"PSS","kpi_sub":"k8s"},
     {"tag":"IMG SIGN","theme":"blue","visual":"code_injection","headline":"Container Image Signing",
      "subheadline":"Container image signing and runtime security verification flow",
      "kpi_value":"IMG","kpi_label":"SIGN","kpi_sub":"rt"}),

    ("2025-06-13", "Cloud_Security_Course_7Batch_-_9Week_DevSecOps_Integration",
     "Cloud Security 7/9: DevSecOps pipeline architecture, maturity model, checklist",
     {"tag":"DSO PIPELINE","theme":"red","visual":"supply_chain_pipe","headline":"DevSecOps Pipeline",
      "subheadline":"DevSecOps pipeline architecture mapping security tools to lifecycle stages",
      "kpi_value":"DSO","kpi_label":"FULL","kpi_sub":"arch",
      "action":"MAP TOOLS + INTEGRATE"},
     {"tag":"MATURITY","theme":"amber","visual":"hub_spoke","headline":"Maturity Model",
      "subheadline":"DevSecOps maturity model and AWS security service integration strategy",
      "kpi_value":"MAT","kpi_label":"MOD","kpi_sub":"DSO"},
     {"tag":"CHECKLIST","theme":"blue","visual":"cve_chain","headline":"Field Checklist",
      "subheadline":"Practical adoption checklist for DevSecOps rollout across teams",
      "kpi_value":"CHK","kpi_label":"DSO","kpi_sub":"ops"}),
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
        target = (Path(__file__).resolve().parent.parent / "_data" / "l20_covers" / f"{date}-{slug}.yml")
        with target.open("w") as f:
            yaml.safe_dump(block, f, sort_keys=False, default_flow_style=False, allow_unicode=False, width=120)
        print(f"[ok] {target.name}")

if __name__ == "__main__":
    emit()

---
layout: post
title: "AI Agent Token Theft, Password Manager Vulnerability, Serverless Defense"
date: 2026-02-17 12:35:29 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI-Agent, Password-Manager, Serverless]
excerpt: "2026년 02월 17일 주요 보안/기술 뉴스 18건 - Infostealer의 AI 에이전트 토큰 탈취, 클라우드 패스워드 매니저 25개 취약점, AWS 서버리스 Defense-in-Depth"
description: "Infostealer 악성코드의 AI 에이전트 설정/토큰 탈취 신규 벡터, Bitwarden/Dashlane/LastPass 25개 패스워드 복구 공격, AWS AI 기반 서버리스 방어 심층 아키텍처 등 18건 분석."
keywords: [Security-Weekly, DevSecOps, AI-Agent, Password-Manager, Serverless, Cloud-Security, 2026]
author: Twodragon
comments: true
image: /assets/images/2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.svg
image_alt: "Tech Security Weekly Digest February 17 2026 AI Agent Cloud Security"
toc: true
---

{% include ai-summary-card.html
  title='AI Agent Token Theft / Password Manager / Serverless Defense (2026.02.17)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">AI-Agent-Security</span>
      <span class="tag">Password-Manager</span>
      <span class="tag">Serverless</span>
      <span class="tag">0-Day</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>Infostealer evolution</strong>: AI agent config files and gateway tokens now targeted - single token compromise grants access to all connected systems</li>
      <li><strong>Password Manager 25 attacks</strong>: Bitwarden, Dashlane, LastPass recovery mechanisms expose full vault compromise paths</li>
      <li><strong>AWS Serverless DiD</strong>: AI-powered defense-in-depth architecture for serverless microservices - GuardDuty, Security Hub integration</li>
      <li><strong>Weekly Recap</strong>: Outlook Add-Ins hijack, multiple 0-Day patches requiring immediate action</li>'
  period='2026.02.17 (24h)'
  audience='Security Engineers, DevSecOps, SRE, Cloud Architects'
%}

---

## Introduction

Hello, this is **Twodragon**.

Here is the in-depth analysis of major tech and security news from the past 24 hours as of February 17, 2026.

> Previous digest: [SolarWinds RCE, UNC3886, LLM Attack (2026.02.10)]({{ site.baseurl }}/security/2026/02/10/Security_Digest_SolarWinds_UNC3886_LLM_Attack.html)

**Collection stats:**
- **Total**: 18 articles
- **Security**: 5
- **AI/ML**: 10
- **Cloud**: 3
- **Blockchain**: 5

---

## Quick Reference

| Category | Source | Key Finding | Impact |
|----------|--------|-------------|--------|
| **Security** | The Hacker News | Infostealer targets AI agent config files + gateway tokens | HIGH |
| **Security** | The Hacker News | 25 password recovery attacks in Bitwarden/Dashlane/LastPass | HIGH |
| **Security** | AWS Security Blog | AI-powered defense-in-depth for serverless microservices | MEDIUM |
| **Security** | The Hacker News | Weekly Recap: Outlook Add-Ins hijack, 0-Day patches | HIGH |
| **Security** | The Hacker News | Lithuania's e-Society security framework analysis | LOW |
| **Cloud** | AWS Blog | EC2 Hpc8a with 5th Gen AMD EPYC - 40% performance boost | MEDIUM |
| **Cloud** | AWS Blog | SageMaker Inference for custom Amazon Nova models | MEDIUM |

---

## 1. Security News

### 1.1 Infostealer Targets AI Agent Configuration Files and Gateway Tokens

Cybersecurity researchers have discovered infostealer malware actively stealing AI agent configuration files and gateway tokens. This represents a critical evolution in the infostealer threat landscape - from targeting browser credentials to harvesting AI agent identities and access configurations.

**Why this matters:**

A single compromised AI agent token can grant attackers access to every system the agent connects to. As enterprises deploy AI agents with broad system access (databases, APIs, cloud services), these tokens become high-value targets.

**Attack chain:**

```
1. Infostealer infects developer/operator workstation
2. Scans for AI agent config files (e.g., .env, config.yaml, agent.json)
3. Extracts OAuth tokens, API keys, gateway credentials
4. Exfiltrates to C2 - attacker impersonates the AI agent
5. Accesses all systems the agent was authorized to use
```

**MITRE ATT&CK Mapping:**

| Technique | ID | Description |
|-----------|------|-------------|
| Credentials from Files | T1552.001 | AI agent config file harvesting |
| Steal Application Access Token | T1528 | Gateway token extraction |
| Valid Accounts: Cloud | T1078.004 | Impersonation via stolen tokens |

**Recommended actions:**
- Store AI agent credentials in Secrets Manager / HashiCorp Vault, never in local config files
- Implement short-lived, auto-rotating tokens for AI agent authentication
- Add EDR rules to detect access to AI agent configuration directories
- Monitor for anomalous API calls from agent service accounts (unusual hours, IPs, request patterns)

> **Source**: [The Hacker News](https://thehackernews.com/2026/02/infostealer-steals-ai-agent-configuration-files-and-gateway-tokens.html)

---

### 1.2 25 Password Recovery Attacks in Major Cloud Password Managers

A research team (Scarlata, Torrisi, Backendal, Paterson) discovered 25 distinct password recovery attack vectors in major cloud password managers including Bitwarden, Dashlane, and LastPass. Attack severity ranges from integrity violations to complete compromise of all organizational vaults.

**Attack categories identified:**

| Category | Affected | Severity | Description |
|----------|----------|----------|-------------|
| Recovery key interception | All three | Critical | Intercepting recovery keys during setup/reset flows |
| Admin recovery abuse | Bitwarden, LastPass | High | Enterprise admin recovery mechanisms exploitable |
| Email-based recovery bypass | Dashlane, LastPass | High | Email verification weaknesses in recovery chains |
| Vault integrity violations | All three | Medium | Modifying encrypted vault contents without detection |

**Recommended actions:**
- Audit password recovery settings in your organization's password manager
- Disable password recovery mechanisms where possible, enforce MFA instead
- Monitor abnormal vault access patterns (bulk exports, unusual geolocations)
- Rotate master passwords for admin/privileged accounts immediately
- Evaluate hardware key (FIDO2) enforcement for vault access

> **Source**: [The Hacker News](https://thehackernews.com/2026/02/study-uncovers-25-password-recovery.html)

---

### 1.3 AWS AI-Powered Defense-in-Depth for Serverless Microservices

AWS Security Blog published a comprehensive guide on building AI-powered defense-in-depth architecture for serverless microservices. The guide addresses the challenge of AI-enhanced threats that can identify vulnerabilities, automate attacks, and evade detection at machine speed - rendering traditional perimeter-based security insufficient.

**Key architecture layers:**

| Layer | AWS Service | Purpose |
|-------|-------------|---------|
| Edge protection | WAF + Shield Advanced | DDoS mitigation, bot management |
| Runtime protection | GuardDuty + Lambda Insights | Anomaly detection in function execution |
| Data protection | KMS + Macie | Encryption, sensitive data detection |
| Identity | IAM + Cognito | Least privilege, fine-grained access control |
| Monitoring | Security Hub + CloudTrail | Centralized findings, audit trail |
| Response | EventBridge + Step Functions | Automated remediation workflows |

**Recommended actions:**
- Audit Lambda execution role permissions - most are over-privileged
- Enable GuardDuty Lambda Protection for runtime threat detection
- Implement function-level network policies (VPC endpoints, security groups)
- Add automated remediation via EventBridge for common security findings

> **Source**: [AWS Security Blog](https://aws.amazon.com/blogs/security/building-an-ai-powered-defense-in-depth-security-architecture-for-serverless-microservices/)

---

### 1.4 Weekly Recap: Outlook Add-Ins Hijack, 0-Day Patches

The Hacker News weekly security recap highlights critical threats requiring immediate attention:

- **Outlook Add-Ins Hijack**: Attackers exploit Outlook add-in sideloading to achieve persistence and data exfiltration via legitimate email client
- **Multiple 0-Day Patches**: Several actively exploited zero-day vulnerabilities patched this week across major platforms

**Recommended actions:**
- Review Outlook add-in policies - restrict sideloading to IT-approved add-ins only
- Deploy 0-day patches immediately per vendor advisories
- Monitor for unauthorized Outlook add-in installations via endpoint telemetry

> **Source**: [The Hacker News](https://thehackernews.com/2026/02/weekly-recap.html)

---

## 2. Cloud & Infrastructure

### 2.1 Amazon EC2 Hpc8a: 5th Gen AMD EPYC with 40% Performance Boost

AWS launched EC2 Hpc8a instances powered by 5th Gen AMD EPYC processors, delivering up to 40% higher performance, increased memory bandwidth, and 300 Gbps Elastic Fabric Adapter (EFA) networking for compute-intensive HPC workloads.

**Practical considerations:**
- Profile current HPC bottlenecks (CFD, FEA, molecular simulations) before migration
- EFA 300Gbps requires proper MPI configuration and placement group setup
- Validate existing HPC cluster scripts compatibility before production transition

> **Source**: [AWS Blog](https://aws.amazon.com/blogs/aws/amazon-ec2-hpc8a-instances-powered-by-5th-gen-amd-epyc-processors-are-now-available/)

---

### 2.2 SageMaker Inference for Custom Amazon Nova Models

AWS announced SageMaker Inference support for custom Amazon Nova models with configurable instance types, auto-scaling policies, and concurrency settings.

**Security considerations:**
- Scope IAM roles per endpoint to follow least privilege
- Route inference traffic through VPC endpoints (avoid public internet)
- Apply SSE-KMS encryption to S3 buckets storing model artifacts

> **Source**: [AWS Blog](https://aws.amazon.com/blogs/aws/announcing-amazon-sagemaker-inference-for-custom-amazon-nova-models/)

---

## 3. Blockchain News

### 3.1 Bitcoin Bears: $71,800 Resistance Holds, Downside Risk Persists

Bitcoin failed to break the $71,800 resistance level, with key support at $65,650. A break below opens $63,000, then Fibonacci level $57,800. Upside remains capped at the $71,800-$74,500 range.

**Security implication**: Market uncertainty increases phishing/scam activity targeting crypto investors. Monitor for fake exchange sites and investment scam campaigns.

> **Source**: [Bitcoin Magazine](https://bitcoinmagazine.com/markets/bitcoin-bears-dominate-failure-to-break-71800-keeps-downside-risk-alive)

---

### 3.2 Payjoin Foundation Gains 501(c)(3) Status

The Payjoin Foundation, the nonprofit behind the Payjoin Dev Kit, secured 501(c)(3) tax-exempt status from the IRS. This enables tax-deductible donations for privacy-enhancing Bitcoin protocol development, accelerating adoption of Payjoin transactions that improve both privacy and fee efficiency.

> **Source**: [Bitcoin Magazine](https://bitcoinmagazine.com/business/payjoin-foundation-gains-501c3-status-enabling-tax-deductible-donations-for-bitcoin-privacy-development)

---

## 4. Other Notable News

| Title | Source | Summary |
|-------|--------|---------|
| [AWS Weekly Roundup: EC2 M8azn, Bedrock open weights models](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-amazon-ec2-m8azn-instances-new-open-weights-models-in-amazon-bedrock-and-more-february-16-2026/) | AWS Blog | M8azn for network-intensive workloads, new open weights models in Bedrock. Check license terms for compliance |
| [Lithuania's Safe and Inclusive e-Society](https://thehackernews.com/2026/02/safe-and-inclusive-e-society.html) | The Hacker News | Lithuania's cybersecurity framework for digital society - reference for national-level security policy |

---

## 5. Trend Analysis

| Trend | Articles | Key Insight |
|-------|----------|-------------|
| **AI agent security** | 3 | AI agents create new attack surface - config files, tokens, and execution environments are high-value targets |
| **Authentication infrastructure** | 3 | Password manager vulnerabilities + 0-day exploits targeting auth systems highlight identity as the new perimeter |
| **Serverless security** | 2 | AI-powered defense-in-depth becoming essential as threats automate at machine speed |
| **Cloud infrastructure** | 3 | AMD EPYC HPC + SageMaker Nova + Bedrock open weights expand cloud AI capabilities |

The dominant trend this period is **AI agent security becoming a critical concern**. As AI agents proliferate in enterprise environments with broad system access, the attack surface shifts from traditional credentials to agent configuration files and gateway tokens. Organizations must treat AI agent credentials with the same rigor as privileged service accounts.

---

## Action Checklist

### P0 (Immediate)

- [ ] **Outlook Add-In sideloading**: Restrict to IT-approved add-ins only, deploy 0-day patches
- [ ] **AI agent credentials**: Verify all AI agent tokens/config files are stored in Secrets Manager/Vault, not in local files or git repos
- [ ] **Password manager recovery**: Audit recovery mechanism settings in Bitwarden/Dashlane/LastPass, disable where possible

### P1 (Within 7 days)

- [ ] Implement EDR detection rules for access to AI agent configuration directories
- [ ] Review password manager MFA enforcement for all organizational vaults
- [ ] Audit Lambda execution role permissions for least privilege compliance

### P2 (Within 30 days)

- [ ] Implement AI-powered defense-in-depth for serverless environments (GuardDuty Lambda Protection)
- [ ] Evaluate short-lived, auto-rotating token strategy for AI agent authentication
- [ ] Review HPC workload migration opportunities with Hpc8a instances

---

## References

| Resource | Link |
|----------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| AWS Security Blog | [aws.amazon.com/blogs/security](https://aws.amazon.com/blogs/security/) |

---

**Author**: Twodragon

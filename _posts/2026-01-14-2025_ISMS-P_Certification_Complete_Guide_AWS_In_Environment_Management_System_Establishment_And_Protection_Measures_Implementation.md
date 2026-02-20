---
layout: post
title: "2025년 ISMS-P 인증 완벽 가이드: AWS 환경에서 관리체계 수립 및 보호대책 구현"
date: 2026-01-14 10:00:00 +0900
categories: [security, cloud]
tags: [ISMS-P, AWS, Security, Compliance, ISMS, NIST-CSF, AI-Security]
excerpt: "2025년 ISMS-P 인증 AWS 환경 완벽 가이드"
description: "2025년 개정된 ISMS-P 인증 기준(101개 항목) 완벽 분석. AWS 환경에서 관리체계 수립 방법, 보호대책 구현, NIST CSF 2.0 연계, AI 보안 요구사항, CIS Benchmark 준수까지 단계별 실무 가이드 제공."
keywords: [ISMS-P, AWS, 정보보호 관리체계, 개인정보보호, Compliance, NIST CSF 2.0, AI Security, Cloud Security, ISO 27001, CIS Benchmark, PCI-DSS, 보안 컴플라이언스]
author: Twodragon
comments: true
image: /assets/images/2026-01-14-2025_ISMS-P_Certification_Complete_Guide_AWS_Environment_Management_System_Establishment_and_Protection_Measures_Implementation.svg
image_alt: "2025 ISMS-P Certification Complete Guide: AWS Environment Management System Establishment and Protection Measures Implementation"
toc: true
schema_type: Article
certifications: [isms-p]
---

## 📋 포스팅 요약

> **제목**: 2025년 ISMS-P 인증 완벽 가이드: AWS 환경에서 관리체계 수립 및 보호대책 구현

> **카테고리**: security, cloud

> **태그**: ISMS-P, AWS, Security, Compliance, ISMS, NIST-CSF, AI-Security

> **핵심 내용**: 
> - 2025년 ISMS-P 인증 AWS 환경 완벽 가이드

> **주요 기술/도구**: AWS, Security, Security, security, cloud

> **대상 독자**: 기업 보안 담당자, 보안 엔지니어, CISO

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">2025년 ISMS-P 인증 완벽 가이드: AWS 환경에서 관리체계 수립 및 보호대책 구현</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">ISMS-P</span>
      <span class="tag">AWS</span>
      <span class="tag">Security</span>
      <span class="tag">Compliance</span>
      <span class="tag">ISMS</span>
      <span class="tag">NIST-CSF</span>
      <span class="tag">AI-Security</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>2025년 ISMS-P 개정 기준 반영</strong>: 101개 기준 상세 설명 (관리체계 수립 16개, 보호대책 64개, 개인정보 처리 21개), NIST CSF 2.0 연계 방안, AI 보안 요구사항 추가</li>
      <li><strong>AWS 환경 ISMS-P 인증 전략</strong>: 클라우드 환경 특화 요구사항, AWS 서비스 기반 컴플라이언스 구현, Defense in Depth 보안 아키텍처 설계</li>
      <li><strong>관리체계 수립 실무 가이드</strong>: 정보보안 정책 수립, 조직 구성 및 역할 정의, 위험 관리 체계 구축, 지속적 개선 프로세스</li>
      <li><strong>보호대책 구현 상세 가이드</strong>: 접근 통제 (IAM, Security Group, NACL), 암호화 (전송/저장 데이터), 로그 관리 및 모니터링 (CloudTrail, CloudWatch), 네트워크 보안 (VPC, Subnet)</li>
      <li><strong>개인정보 처리 단계별 요구사항</strong>: 수집, 이용, 제공, 파기 단계별 보안 요구사항 및 AWS 서비스 활용 방법</li>
      <li><strong>실무 적용 사례</strong>: AWS 기반 ISMS-P 인증 사례, 보안 감사 대응 방법, 문제 해결 사례</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">ISMS-P, AWS (IAM, VPC, S3, RDS, CloudTrail, CloudWatch, KMS, Security Hub), NIST CSF 2.0, AI Security, Compliance Tools</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">ISMS-P 인증 준비자, 보안 엔지니어, 클라우드 보안 전문가, CISO, 컴플라이언스 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## Executive Summary: ISMS-P 인증 준비도 평가

### 인증 준비도 자가 진단

| 평가 영역 | 현황 점검 항목 | 준비 단계 | 예상 소요 기간 |
|---------|-------------|---------|-------------|
| **관리체계 수립** | 정보보안 정책 수립, 조직 구성, 경영진 승인 | ⬜ 미착수 ⬜ 진행중 ⬜ 완료 | 2-3개월 |
| **보호대책 구현** | 접근통제, 암호화, 로그관리, 네트워크 보안 | ⬜ 미착수 ⬜ 진행중 ⬜ 완료 | 3-4개월 |
| **개인정보 처리** | 수집·이용·제공·파기 단계별 보안 조치 | ⬜ 미착수 ⬜ 진행중 ⬜ 완료 | 1-2개월 |
| **AWS 인프라** | VPC, IAM, KMS, CloudTrail, Security Hub 설정 | ⬜ 미착수 ⬜ 진행중 ⬜ 완료 | 2-3개월 |
| **문서화** | 정책서, 절차서, 매뉴얼, 증적자료 | ⬜ 미착수 ⬜ 진행중 ⬜ 완료 | 2개월 |

### 인증 로드맵 (총 8-12개월)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> Phase 1: 준비 (1-2개월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> Phase 1: 준비 (1-2개월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
Phase 1: 준비 (1-2개월)
└─ Gap Analysis → 현황 분석 → 인증 범위 정의

Phase 2: 관리체계 수립 (2-3개월)
└─ 정책 수립 → 조직 구성 → 위험 관리 체계

Phase 3: 보호대책 구현 (3-4개월)
└─ AWS 보안 설정 → 암호화 구현 → 모니터링 체계

Phase 4: 심사 준비 (1-2개월)
└─ 문서 정비 → 모의 심사 → 개선 조치

Phase 5: 인증 심사 (1개월)
└─ 서면 심사 → 현장 심사 → 보완 조치 → 인증 획득


```
-->
-->

### 비용 예측 (중견기업 기준)

| 항목 | 예상 비용 | 비고 |
|-----|---------|------|
| **컨설팅** | 3,000만원 ~ 5,000만원 | 외부 전문가 활용 시 |
| **인증 심사 비용** | 1,500만원 ~ 2,500만원 | KISA 인증 수수료 |
| **AWS 인프라** | 월 500만원 ~ 1,000만원 | Security Hub, GuardDuty 등 포함 |
| **보안 솔루션** | 2,000만원 ~ 4,000만원 | SIEM, DLP, 취약점 스캐너 등 |
| **내부 인력** | 3-5명 × 8-12개월 | 전담 TF 구성 |

### 주요 위험 요소 및 대응 방안

| 위험 요소 | 영향도 | 대응 방안 |
|---------|-------|---------|
| **경영진 지원 부족** | 🔴 높음 | 경영진 보고 및 예산 확보 사전 진행 |
| **AWS 보안 설정 미비** | 🔴 높음 | AWS Well-Architected Review 선행 실시 |
| **문서화 지연** | 🟡 중간 | 프로젝트 초기부터 문서 템플릿 준비 |
| **조직 변화 저항** | 🟡 중간 | 교육 및 인식 제고 프로그램 운영 |
| **외부 심사 지적** | 🟢 낮음 | 모의 심사를 통한 사전 점검 |

## 서론

안녕하세요, **Twodragon**입니다.

2025년 개정된 ISMS-P(정보보호 및 개인정보보호 관리체계) 인증 기준은 클라우드 환경에서의 보안 요구사항을 더욱 강화하고, NIST CSF 2.0과의 연계, AI 보안 요구사항 등 최신 보안 트렌드를 반영하고 있습니다.

이 포스팅은 **SK Shieldus의 2025년 ISMS-P 운영 가이드**를 기반으로, AWS 환경에서 ISMS-P 인증을 받기 위한 실무 중심의 완벽 가이드를 제공합니다. 101개 기준을 상세히 설명하고, AWS 서비스를 활용한 컴플라이언스 구현 방법을 단계별로 제시합니다.

ISMS-P 인증 프로세스는 체계적인 단계를 통해 진행됩니다:

## 📊 빠른 참조

### ISMS-P 인증 기준 개요

| 항목 | 내용 |
|------|------|
| **총 기준 수** | 101개 |
| **관리체계 수립 및 운영** | 16개 항목 |
| **보호대책 요구사항** | 64개 항목 |
| **개인정보 처리 단계별 요구사항** | 21개 항목 |
| **인증 유효기간** | 3년 |
| **인증 기관** | 한국인터넷진흥원 (KISA) |

### 2025년 주요 변경사항

| 변경사항 | 설명 |
|---------|------|
| **NIST CSF 2.0 연계** | 거버넌스 함수 추가, ISMS-P 기준과의 매핑 강화 |
| **AI 보안 요구사항** | AI 서비스 기업을 위한 보안 요구사항 추가 |
| **클라우드 보안 강화** | 클라우드 환경 특화 요구사항 명확화 |
| **암호화 요구사항 강화** | 전송/저장 데이터 암호화 의무화 |

---

## MITRE ATT&CK 매핑: ISMS-P 통제와 공격 기법 연계

### ISMS-P 보호대책과 MITRE ATT&CK 전술 매핑

| ISMS-P 통제 | MITRE ATT&CK 전술 | 방어 기법 | AWS 구현 |
|------------|------------------|---------|---------|
| **접근 통제 (3.1)** | Initial Access (TA0001) | MFA, IAM Policies | IAM MFA, Cognito |
| **접근 통제 (3.1)** | Privilege Escalation (TA0004) | Least Privilege | IAM Policies, SCPs |
| **암호화 (3.2)** | Collection (TA0009) | Data Encryption | KMS, S3 Encryption |
| **암호화 (3.2)** | Exfiltration (TA0010) | TLS/SSL | ALB, CloudFront |
| **로그 관리 (3.3)** | Defense Evasion (TA0005) | Centralized Logging | CloudTrail, CloudWatch |
| **네트워크 보안** | Lateral Movement (TA0008) | Network Segmentation | VPC, Security Groups |
| **침해사고 대응** | Impact (TA0040) | Incident Response | Security Hub, GuardDuty |

### 주요 공격 시나리오별 ISMS-P 통제 매핑

#### 시나리오 1: 자격 증명 탈취 공격

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1078 (Valid Accounts)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1078 (Valid Accounts)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
MITRE ATT&CK: T1078 (Valid Accounts)
├─ ISMS-P 통제
│  ├─ 3.1.1 사용자 계정 관리
│  ├─ 3.1.3 사용자 인증
│  └─ 3.1.5 원격 접근 통제
│
└─ AWS 방어 조치
   ├─ IAM MFA 강제 활성화
   ├─ AWS SSO 통합 인증
   ├─ CloudTrail 로그인 실패 모니터링
   └─ GuardDuty 이상 행위 탐지


```
-->
-->

<!--
# SIEM Detection Query: IAM 비정상 로그인 탐지

## Splunk SPL
index=aws sourcetype=aws:cloudtrail eventName=ConsoleLogin errorCode=Failed
| stats count by userIdentity.principalId src_ip
| where count > 5
| table _time userIdentity.principalId src_ip count
| eval severity="HIGH"

## Azure Sentinel KQL
AWSCloudTrail
| where EventName == "ConsoleLogin" and ErrorCode == "Failed"
| summarize FailedAttempts=count() by UserIdentityPrincipalId, SourceIpAddress, bin(TimeGenerated, 5m)
| where FailedAttempts > 5
| project TimeGenerated, UserIdentityPrincipalId, SourceIpAddress, FailedAttempts
| extend Severity = "High"
-->

#### 시나리오 2: 데이터 유출 (Data Exfiltration)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1567 (Exfiltration Over Web Service)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1567 (Exfiltration Over Web Service)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
MITRE ATT&CK: T1567 (Exfiltration Over Web Service)
├─ ISMS-P 통제
│  ├─ 3.2.1 암호화 적용
│  ├─ 3.3.2 로그 기록 및 보존
│  └─ 4.2.2 개인정보 이용 제한
│
└─ AWS 방어 조치
   ├─ S3 Block Public Access
   ├─ KMS 암호화 강제
   ├─ VPC Endpoint로 인터넷 우회 차단
   └─ CloudWatch Logs 대용량 데이터 전송 알람


```
-->
-->

<!--
# SIEM Detection Query: S3 대량 다운로드 탐지

## Splunk SPL
index=aws sourcetype=aws:cloudtrail eventName=GetObject
| stats sum(requestParameters.bytesTransferred) as total_bytes by userIdentity.principalId, requestParameters.bucketName
| where total_bytes > 10737418240
| eval total_gb=round(total_bytes/1073741824, 2)
| table _time userIdentity.principalId requestParameters.bucketName total_gb
| eval severity="CRITICAL"

## Azure Sentinel KQL
AWSCloudTrail
| where EventName == "GetObject"
| extend BytesTransferred = toint(RequestParameters.bytesTransferred)
| summarize TotalBytes=sum(BytesTransferred) by UserIdentityPrincipalId, BucketName=tostring(RequestParameters.bucketName), bin(TimeGenerated, 1h)
| where TotalBytes > 10737418240
| extend TotalGB = round(TotalBytes / 1073741824.0, 2)
| project TimeGenerated, UserIdentityPrincipalId, BucketName, TotalGB
| extend Severity = "Critical"
-->

#### 시나리오 3: 권한 상승 (Privilege Escalation)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1548 (Abuse Elevation Control Mechanism)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> MITRE ATT&CK: T1548 (Abuse Elevation Control Mechanism)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
MITRE ATT&CK: T1548 (Abuse Elevation Control Mechanism)
├─ ISMS-P 통제
│  ├─ 3.1.2 사용자 식별
│  ├─ 3.1.6 관리자 계정 및 권한 관리
│  └─ 3.3.1 로그 수집 및 관리
│
└─ AWS 방어 조치
   ├─ IAM Access Analyzer로 과도한 권한 탐지
   ├─ SCPs로 조직 수준 권한 제한
   ├─ CloudTrail IAM 정책 변경 모니터링
   └─ EventBridge 자동 알람 및 차단


```
-->
-->

<!--
# SIEM Detection Query: IAM 정책 변경 탐지

## Splunk SPL
index=aws sourcetype=aws:cloudtrail (eventName=PutUserPolicy OR eventName=PutRolePolicy OR eventName=AttachUserPolicy OR eventName=AttachRolePolicy)
| eval policy_change=if(eventName=="PutUserPolicy" OR eventName=="PutRolePolicy", "Inline Policy Modified", "Managed Policy Attached")
| table _time userIdentity.principalId eventName requestParameters.userName requestParameters.roleName policy_change
| eval severity="HIGH"

## Azure Sentinel KQL
AWSCloudTrail
| where EventName in ("PutUserPolicy", "PutRolePolicy", "AttachUserPolicy", "AttachRolePolicy")
| extend PolicyChange = iff(EventName in ("PutUserPolicy", "PutRolePolicy"), "Inline Policy Modified", "Managed Policy Attached")
| extend TargetIdentity = coalesce(tostring(RequestParameters.userName), tostring(RequestParameters.roleName))
| project TimeGenerated, UserIdentityPrincipalId, EventName, TargetIdentity, PolicyChange
| extend Severity = "High"
-->

### ISMS-P 통제 효과성 측정 (MITRE ATT&CK 기반)

| 전술 (Tactic) | 탐지율 | 차단율 | ISMS-P 통제 개선 우선순위 |
|--------------|-------|-------|------------------------|
| Initial Access | 85% | 70% | 🟡 MFA 적용 확대 |
| Execution | 60% | 40% | 🔴 응용프로그램 실행 제어 강화 |
| Persistence | 75% | 60% | 🟡 IAM 역할 정기 검토 |
| Privilege Escalation | 80% | 65% | 🟡 SCPs 정책 강화 |
| Defense Evasion | 50% | 30% | 🔴 CloudTrail 로그 무결성 검증 |
| Credential Access | 90% | 80% | 🟢 현재 수준 유지 |
| Discovery | 70% | 50% | 🟡 GuardDuty 룰 최적화 |
| Lateral Movement | 85% | 75% | 🟢 현재 수준 유지 |
| Collection | 80% | 70% | 🟡 DLP 솔루션 도입 검토 |
| Exfiltration | 75% | 60% | 🟡 VPC Endpoint 활용 확대 |
| Impact | 90% | 85% | 🟢 현재 수준 유지 |

---

## 1. ISMS-P 인증 개요

### 1.1 ISMS-P 인증이란?

ISMS-P(Information Security Management System - Personal Information)는 정보보호와 개인정보보호를 위한 관리체계를 수립하고 운영하는 기관·기업에 대해 한국인터넷진흥원(KISA)이 인증을 부여하는 제도입니다.

#### 인증 목적

| 목적 | 설명 |
|------|------|
| **정보보호 체계 구축** | 체계적인 정보보호 관리체계 수립 및 운영 |
| **개인정보보호 강화** | 개인정보 처리 단계별 보안 요구사항 준수 |
| **신뢰성 확보** | 고객 및 이해관계자에 대한 신뢰도 향상 |
| **규정 준수** | 개인정보보호법, 정보통신망법 등 법규 준수 |

### 1.2 2025년 개정 기준 주요 특징

#### 101개 기준 구조

| 영역 | 기준 수 | 주요 내용 |
|------|--------|----------|
| **관리체계 수립 및 운영** | 16개 | 정보보안 정책, 조직 구성, 위험 관리, 지속적 개선 |
| **보호대책 요구사항** | 64개 | 접근 통제, 암호화, 물리적 보안, 운영 보안, 침해사고 대응 |
| **개인정보 처리 단계별 요구사항** | 21개 | 수집, 이용, 제공, 파기 단계별 보안 요구사항 |

#### NIST CSF 2.0 연계

2025년 개정 기준은 NIST Cybersecurity Framework 2.0과의 연계를 강화했습니다:

| NIST CSF 2.0 함수 | ISMS-P 영역 | 설명 |
|------------------|------------|------|
| **Govern (거버넌스)** | 관리체계 수립 | 정보보안 정책, 조직 구성, 위험 관리 |
| **Identify (식별)** | 자산 관리 | 정보자산 분류 및 관리 |
| **Protect (보호)** | 보호대책 | 접근 통제, 암호화, 물리적 보안 |
| **Detect (탐지)** | 모니터링 | 로그 관리, 이상 탐지 |
| **Respond (대응)** | 침해사고 대응 | 사고 대응 체계, 복구 계획 |
| **Recover (복구)** | 비즈니스 연속성 | 백업 및 복구, 재해 복구 |

#### AI 보안 요구사항

ISMS-P 보호대책은 Defense in Depth 전략을 통해 다층 보안을 구현합니다:

AI 서비스 기업을 위한 추가 보안 요구사항이 포함되었습니다:

- **AI 모델 보안**: 모델 학습 데이터 보호, 모델 무결성 검증
- **데이터 보호**: 학습 데이터 암호화, 접근 제어
- **프라이버시 보호**: 개인정보 포함 데이터 처리 시 추가 보호 조치

### 1.3 한국 법규 상세 매핑: 개인정보보호법 및 정보통신망법

#### 개인정보보호법 조항별 ISMS-P 기준 매핑

| 법 조항 | 내용 | ISMS-P 기준 | AWS 구현 방법 |
|--------|------|------------|-------------|
| **제15조** | 개인정보의 수집·이용 | 4.1.1 개인정보 수집 시 동의 | Cognito, Lambda 동의 관리 |
| **제17조** | 개인정보의 제공 | 4.3.1 개인정보 제공 시 동의 | API Gateway, Lambda 제공 내역 기록 |
| **제21조** | 개인정보의 파기 | 4.4.1 개인정보 파기 | S3 Lifecycle Policy, Lambda |
| **제24조** | 고유식별정보 처리 제한 | 4.1.2 고유식별정보 처리 | KMS 암호화, 접근 제어 |
| **제29조** | 안전조치의무 | 3.2.1 암호화 적용 | KMS, TLS/SSL |
| **제34조** | 개인정보 유출 통지 | 5.1.1 침해사고 대응 | SNS, EventBridge 자동 알림 |
| **제39조의3** | 개인정보 처리방침 공개 | 2.1.1 정보보안 정책 수립 | S3 정적 웹사이트 호스팅 |

#### 정보통신망법 조항별 ISMS-P 기준 매핑

| 법 조항 | 내용 | ISMS-P 기준 | AWS 구현 방법 |
|--------|------|------------|-------------|
| **제28조** | 개인정보의 보호조치 | 3.2.1 암호화 적용 | KMS, S3 암호화 |
| **제45조** | 정보통신망 침해사고 대응 | 5.1.1 침해사고 대응 | Security Hub, GuardDuty |
| **제45조의3** | 침해사고 통지 | 5.1.2 침해사고 통지 | SNS, SES 자동 통지 |
| **제47조** | 정보보호 최고책임자 지정 | 2.2.1 조직 구성 | IAM 역할 정의 |
| **제47조의2** | 정보보호 관리체계 인증 | 전체 기준 | ISMS-P 인증 |

#### 과태료 및 형사처벌 기준 (2025년 개정 기준)

| 위반 내용 | 법적 근거 | 과태료/벌금 | ISMS-P 예방 통제 |
|----------|---------|-----------|----------------|
| **개인정보 유출 미통지** | 개인정보보호법 제34조 | 3천만원 이하 과태료 | 자동 통지 시스템 (EventBridge) |
| **암호화 미적용** | 정보통신망법 제28조 | 3천만원 이하 과태료 | KMS 강제 암호화 정책 |
| **개인정보 불법 제공** | 개인정보보호법 제17조 | 5년 이하 징역, 5천만원 이하 벌금 | Lambda 동의 검증 로직 |
| **안전조치 미이행** | 개인정보보호법 제29조 | 2년 이하 징역, 2천만원 이하 벌금 | Security Hub 컴플라이언스 자동 검증 |
| **CISO 미지정** | 정보통신망법 제47조 | 3천만원 이하 과태료 | 조직도 명시 |

#### 규제 기관별 감독 및 처분 현황 (2024년 기준)

| 규제 기관 | 주요 감독 대상 | 2024년 처분 건수 | 주요 위반 사항 |
|----------|-------------|---------------|-------------|
| **개인정보보호위원회** | 전체 사업자 | 1,247건 | 개인정보 유출 미통지 (42%), 암호화 미적용 (28%) |
| **방송통신위원회** | 정보통신서비스 제공자 | 389건 | CISO 미지정 (35%), 침해사고 대응 미비 (31%) |
| **과학기술정보통신부** | ISMS-P 인증 의무 대상 | 127건 | 관리체계 미운영 (48%), 문서 미비 (29%) |

### 1.4 AWS 환경에서의 ISMS-P 인증

클라우드 환경에서 ISMS-P 인증을 받기 위해서는 다음을 고려해야 합니다:

#### 클라우드 환경 특화 요구사항

| 요구사항 | AWS 구현 방법 | 설명 |
|---------|-------------|------|
| **공유 책임 모델** | AWS와 고객의 책임 분리 명확화 | 인프라 보안은 AWS, 데이터 보안은 고객 책임 |
| **다중 테넌시** | VPC 격리, 리소스 태깅 | 논리적 격리 및 리소스 관리 |
| **동적 리소스** | 자동화된 보안 정책 적용 | CloudFormation, Terraform을 통한 IaC |
| **지리적 분산** | 리전별 데이터 보호 정책 | 데이터 레지던시 요구사항 준수 |

#### AWS 서비스 기반 컴플라이언스 구현

| ISMS-P 요구사항 | AWS 서비스 | 구현 방법 |
|----------------|-----------|----------|
| **접근 통제** | IAM, Security Group, NACL | 역할 기반 접근 제어, 최소 권한 원칙 |
| **암호화** | KMS, S3, RDS | 전송/저장 데이터 암호화 |
| **로그 관리** | CloudTrail, CloudWatch | 모든 활동 로깅 및 모니터링 |
| **네트워크 보안** | VPC, Subnet, NAT Gateway | 네트워크 분리 및 접근 제어 |
| **백업 및 복구** | S3, EBS Snapshot, RDS Backup | 자동화된 백업 및 복구 |

---

## AWS ISMS-P 컴플라이언스 아키텍처 다이어그램

### 전체 보안 아키텍처 (Defense in Depth)

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────────────────────────────────────────────────────────────┐
│                         CloudFront (CDN)                             │
│                    TLS 1.3, WAF, Shield Standard                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                      Application Load Balancer                       │
│              TLS 1.2+, ACM 인증서, Security Policy                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │             VPC (10.0.0.0/16)                 │
         │  ┌──────────────────────────────────────────┐ │
         │  │   Public Subnet (10.0.1.0/24)            │ │
         │  │   ├─ NAT Gateway                         │ │
         │  │   └─ Bastion Host (MFA 필수)             │ │
         │  └──────────────────┬───────────────────────┘ │
         │                     │                          │
         │  ┌──────────────────┴───────────────────────┐ │
         │  │   Private Subnet (10.0.2.0/24)           │ │
         │  │   ├─ ECS Fargate (애플리케이션)          │ │
         │  │   ├─ Lambda (비즈니스 로직)              │ │
         │  │   └─ Security Group (최소 권한)          │ │
         │  └──────────────────┬───────────────────────┘ │
         │                     │                          │
         │  ┌──────────────────┴───────────────────────┐ │
         │  │   Data Subnet (10.0.3.0/24)              │ │
         │  │   ├─ RDS (Multi-AZ, 암호화)              │ │
         │  │   ├─ ElastiCache (암호화)                │ │
         │  │   └─ No Internet Access                  │ │
         │  └──────────────────────────────────────────┘ │
         └──────────────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                 │
┌────────┴─────────┐           ┌──────────┴──────────┐
│   S3 (암호화)     │           │   KMS (CMK)         │
│   ├─ 개인정보     │           │   ├─ 키 로테이션    │
│   ├─ 로그         │           │   └─ 접근 정책      │
│   └─ 백업         │           └─────────────────────┘
└──────────────────┘
         │
┌────────┴─────────────────────────────────────────────┐
│            보안 모니터링 및 로깅                       │
│  ┌──────────────┬──────────────┬─────────────────┐   │
│  │ CloudTrail   │ CloudWatch   │ Security Hub    │   │
│  │ (모든 API)   │ (메트릭)     │ (통합 대시보드) │   │
│  └──────┬───────┴──────┬───────┴─────┬───────────┘   │
│         │              │              │               │
│  ┌──────┴──────┬───────┴──────┬──────┴──────┐        │
│  │ GuardDuty   │ Config       │ Inspector   │        │
│  │ (위협탐지)  │ (규정준수)   │ (취약점)    │        │
│  └─────────────┴──────────────┴─────────────┘        │
└──────────────────────────────────────────────────────┘


```
-->
-->

### IAM 권한 모델 (최소 권한 원칙)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌─────────────────────────────────────────────────────┐
│              AWS Organizations (Root)                │
│                                                       │
│  Service Control Policies (SCPs)                     │
│  ├─ 모든 계정에 기본 보안 정책 강제                 │
│  ├─ 특정 리전 외 리소스 생성 차단                   │
│  └─ CloudTrail 비활성화 차단                        │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┬───────────────────┐
        │                       │                   │
┌───────┴────────┐   ┌──────────┴──────┐   ┌────────┴────────┐
│  Production    │   │  Development    │   │  Security       │
│  Account       │   │  Account        │   │  Account        │
└───────┬────────┘   └──────────┬──────┘   └────────┬────────┘
        │                       │                   │
        │                       │                   │
┌───────┴─────────────────┐     │     ┌─────────────┴──────┐
│  IAM 역할 (Role)        │     │     │  보안 감사 역할    │
│  ├─ Developer           │     │     │  (ReadOnly)        │
│  │  (읽기, 배포)        │     │     └────────────────────┘
│  ├─ SecurityManager     │     │
│  │  (보안 설정, 감사)   │     │
│  └─ DataEngineer        │     │
│     (데이터 처리)       │     │
└─────────────────────────┘     │
                                │
                    ┌───────────┴────────────┐
                    │  IAM 사용자            │
                    │  (MFA 필수)            │
                    │  ├─ 임시 자격 증명     │
                    │  └─ 정기 권한 검토     │
                    └────────────────────────┘


```
-->
-->

### 개인정보 처리 흐름 및 보안 통제

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────┐
│  사용자     │
└──────┬──────┘
       │ HTTPS (TLS 1.3)
       ▼
┌──────────────────────────────────────────────┐
│        API Gateway (인증/인가)                │
│  ├─ Lambda Authorizer (JWT 검증)             │
│  ├─ WAF (SQL Injection, XSS 차단)            │
│  └─ Rate Limiting (DDoS 방어)                │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Lambda (비즈니스 로직)                       │
│  ├─ 개인정보 수집 동의 검증                  │
│  ├─ 데이터 유효성 검사 (Input Validation)    │
│  └─ 민감정보 마스킹 (로그)                   │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  KMS (암호화 키 관리)                         │
│  ├─ CMK로 데이터 암호화                      │
│  ├─ 키 로테이션 (연 1회)                     │
│  └─ IAM 정책으로 접근 제어                   │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  RDS (개인정보 저장)                          │
│  ├─ 암호화 저장 (AES-256)                    │
│  ├─ Multi-AZ (가용성)                        │
│  ├─ 자동 백업 (암호화)                       │
│  └─ 접근 제어 (Security Group)               │
└──────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  CloudTrail + CloudWatch Logs                 │
│  ├─ 모든 접근 로그 기록                      │
│  ├─ 7년 보관 (법적 요구사항)                 │
│  ├─ 로그 암호화 (KMS)                        │
│  └─ 이상 탐지 알람 (CloudWatch Alarms)       │
└──────────────────────────────────────────────┘


```
-->
-->

### 데이터 라이프사이클 및 파기 프로세스

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────────────────────────────────────────────┐
│              개인정보 라이프사이클                   │
└─────────────────────────────────────────────────────┘

수집 → 저장 → 이용 → 제공 → 파기
 │      │      │      │      │
 ▼      ▼      ▼      ▼      ▼
┌────┐┌────┐┌────┐┌────┐┌────────┐
│동의││암호││접근││동의││자동파기│
│확인││화  ││제어││재확││(7일전  │
│    ││    ││로깅││인  ││알림)   │
└────┘└────┘└────┘└────┘└────────┘

┌─────────────────────────────────────────────────────┐
│          S3 Lifecycle Policy (자동 파기)             │
│                                                       │
│  0일: 수집 (Standard)                                │
│  │                                                    │
│  90일: Infrequent Access (IA)                        │
│  │                                                    │
│  365일: Glacier (장기 보관)                          │
│  │                                                    │
│  1095일 (3년): 파기 전 알림 (SNS → Lambda)          │
│  │                                                    │
│  1102일 (3년 7일): 영구 삭제 (Delete)                │
│                                                       │
│  파기 증적: CloudTrail DeleteObject 이벤트           │
└─────────────────────────────────────────────────────┘


```
-->
-->

---

## 경영진 보고 형식: ISMS-P 인증 현황 대시보드

### 월간 보안 KPI 리포트 (Board Reporting)

#### 1. 인증 진행 현황 (Traffic Light)

| 영역 | 상태 | 진행률 | 주요 이슈 | 조치 계획 |
|-----|------|-------|----------|----------|
| **관리체계 수립** | 🟢 완료 | 100% | 없음 | 유지 관리 |
| **보호대책 구현** | 🟡 진행중 | 75% | 암호화 키 로테이션 미설정 | 2주 내 완료 |
| **개인정보 처리** | 🟡 진행중 | 80% | 파기 프로세스 자동화 필요 | Lambda 함수 개발 중 |
| **문서화** | 🟢 완료 | 95% | 일부 절차서 업데이트 필요 | 1주 내 완료 |
| **모의 심사** | 🔴 예정 | 0% | 외부 컨설턴트 선정 필요 | 다음 분기 예산 확보 |

#### 2. 보안 위험 지표 (Risk Dashboard)

| 위험 등급 | 건수 | 전월 대비 | 주요 위험 |
|---------|------|----------|----------|
| 🔴 Critical | 2 | ▼ -3 | IAM 과도한 권한 2건 |
| 🟠 High | 15 | ▲ +5 | 암호화 미적용 S3 버킷 15개 |
| 🟡 Medium | 47 | ─ 0 | 패치 지연 EC2 인스턴스 47개 |
| 🟢 Low | 128 | ▼ -12 | 로그 보관 기간 미준수 등 |

#### 3. 컴플라이언스 준수율 (Compliance Score)

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
전체 준수율: 87% (목표: 95%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

관리체계 수립 (16개 기준)
████████████████████████████████████████ 100% (16/16)

보호대책 요구사항 (64개 기준)
███████████████████████████████░░░░░ 84% (54/64)
└─ 미준수: 암호화 5개, 접근제어 3개, 로그관리 2개

개인정보 처리 (21개 기준)
████████████████████████████████░░░ 81% (17/21)
└─ 미준수: 파기 프로세스 2개, 동의 관리 2개


```
-->
-->

#### 4. AWS 보안 서비스 현황

| 서비스 | 활성화 | 탐지 건수 | 조치율 | 비용 (월) |
|--------|-------|----------|-------|----------|
| **Security Hub** | 🟢 ON | 234건 | 89% | $45 |
| **GuardDuty** | 🟢 ON | 18건 | 100% | $120 |
| **Config** | 🟢 ON | 127건 규칙 | 92% | $78 |
| **CloudTrail** | 🟢 ON | 15M 이벤트 | N/A | $150 |
| **Inspector** | 🟡 부분 | 42건 취약점 | 67% | $89 |
| **Macie** | 🔴 OFF | - | - | $0 |

#### 5. 인증 일정 및 예산

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌────────────────────────────────────────────────────┐
│  ISMS-P 인증 타임라인                               │
└────────────────────────────────────────────────────┘

2026 Q1          Q2          Q3          Q4
  │              │           │           │
  ├─ Gap Analysis (완료)
  │              │
  ├──────────────┤
  └─ 보호대책 구현 (진행중, 75%)
                 │
                 ├──────────┤
                 └─ 문서화 및 모의심사
                            │
                            ├──────────┤
                            └─ 인증 심사 및 획득 (목표)

예산 집행 현황:
총 예산: 1억 2천만원
집행액: 6천만원 (50%)
잔여액: 6천만원


```
-->
-->

#### 6. 주요 리스크 및 의사결정 사항

| 구분 | 내용 | 영향도 | 의사결정 필요 |
|-----|------|-------|-------------|
| **기술** | Macie 미활성화로 개인정보 자동 탐지 불가 | 🔴 높음 | 예산 승인 필요 ($500/월) |
| **조직** | 정보보호 전담 인력 1명 추가 필요 | 🟡 중간 | 인력 충원 검토 |
| **프로세스** | 침해사고 대응 절차 테스트 미실시 | 🟡 중간 | 분기별 모의 훈련 실시 |
| **재정** | 외부 컨설팅 예산 초과 우려 | 🟡 중간 | 예산 추가 확보 또는 일정 조정 |

---

## 2. 관리체계 수립

### 2.1 정보보안 정책 수립

정보보안 정책은 ISMS-P 인증의 기반이 되는 최상위 문서입니다.

#### 정책 수립 원칙

| 원칙 | 설명 |
|------|------|
| **최고 경영진 승인** | 최고 경영진의 명시적 승인 및 지지 |
| **법규 준수** | 개인정보보호법, 정보통신망법 등 법규 반영 |
| **조직 특성 반영** | 조직의 업무 특성, 규모, 위험 수준 반영 |
| **지속적 개선** | 정기적인 검토 및 개선 프로세스 |

#### 정책 구성 요소

```markdown
1. 정보보안 목표 및 범위
2. 정보보안 조직 구성 및 역할
3. 정보보안 위험 관리 절차
4. 보호대책 요구사항
5. 개인정보 처리 원칙
6. 침해사고 대응 절차
7. 지속적 개선 프로세스
```

> **참고**: 정보보안 정책 수립 가이드는 [KISA ISMS-P 공식 사이트](https://isms.kisa.or.kr/) 및 [SK Shieldus 2025년 ISMS-P 운영 가이드](https://www.skshieldus.com/download/files/download.do?o_fname=%2725%EB%85%84%20%EC%A0%95%EB%B3%B4%EB%B3%B4%ED%98%B8%20%EB%B0%8F%20%EA%B0%9C%EC%9D%B8%EC%A0%95%EB%B3%B4%ED%98%B8%20%EA%B4%80%EB%A6%AC%EC%B2%B4%EA%B3%84(ISMS-P)%20%EC%9A%B4%EC%98%81%20%EA%B0%80%EC%9D%B4%EB%93%9C_%EA%B0%9C%EC%A0%95%ED%8C%90.pdf&r_fname=20251230170658586.pdf)를 참조하세요.

### 2.2 조직 구성 및 역할 정의

#### 정보보안 조직 구성

| 역할 | 책임 | AWS 환경 적용 |
|------|------|--------------|
| **최고 경영진** | 정보보안 정책 승인, 예산 배정 | AWS 계정 관리, 예산 승인 |
| **정보보안 책임자** | 정보보안 관리체계 전반 관리 | AWS 보안 아키텍처 설계, 컴플라이언스 관리 |
| **정보보안 관리자** | 일상적 정보보안 업무 수행 | AWS 보안 설정, 모니터링, 대응 |
| **개인정보보호 책임자** | 개인정보 처리 감독 | 개인정보 포함 데이터 보호 정책 수립 |
| **부서별 정보보안 담당자** | 부서별 정보보안 업무 수행 | 부서별 AWS 리소스 보안 관리 |

#### AWS 환경에서의 역할 정의

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS IAM 역할 기반 정보보안 조직 구성 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS IAM 역할 기반 정보보안 조직 구성 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AWS IAM 역할 기반 정보보안 조직 구성 예시
Resources:
  SecurityManagerRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: ISMS-Security-Manager
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !GetAtt SecurityManagerUser.Arn
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/SecurityAudit
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: ISMSCompliancePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - securityhub:*
                  - config:*
                  - cloudtrail:*
                Resource: '*'


```
-->
-->

### 2.3 위험 관리 체계

#### 위험 관리 프로세스

| 단계 | 프로세스 | 설명 | AWS 활용 |
|------|---------|------|---------|
| 1 | **위험 식별** | 정보자산별 위협 및 취약점 식별 | AWS Security Hub, AWS Config |
| 2 | **위험 분석** | 위험의 발생 가능성 및 영향도 평가 | AWS Security Hub 인사이트 |
| 3 | **위험 평가** | 위험 수준 결정 및 우선순위 설정 | 위험 매트릭스 활용 |
| 4 | **위험 대응** | 위험 감소 조치 수립 및 실행 | AWS 보안 서비스 활용 |
| 5 | **위험 모니터링** | 지속적인 위험 모니터링 및 재평가 | CloudWatch, Security Hub |

#### AWS 기반 위험 관리

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```yaml
# AWS Security Hub를 통한 위험 관리 설정
Resources:
  SecurityHubAccount:
    Type: AWS::SecurityHub::Hub
    Properties:
      EnableDefaultStandards: true
      StandardsSubscriptionArns:
        - arn:aws:securityhub:ap-northeast-2::standards/cis-aws-foundations-benchmark/v/1.2.0
        - arn:aws:securityhub:ap-northeast-2::standards/pci-dss/v/3.2.1
```

---

## 컴플라이언스 자동화: Terraform 및 CloudFormation 스니펫

### Terraform: ISMS-P 준수 VPC 구성

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # ISMS-P 요구사항: 네트워크 분리 및 접근 제어...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # ISMS-P 요구사항: 네트워크 분리 및 접근 제어...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# ISMS-P 요구사항: 네트워크 분리 및 접근 제어
# Terraform으로 3-Tier 아키텍처 구성

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC 생성
resource "aws_vpc" "isms_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name       = "ISMS-P-Compliant-VPC"
    Compliance = "ISMS-P"
    ManagedBy  = "Terraform"
  }
}

# Public Subnet (NAT Gateway, Bastion Host)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.isms_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "ISMS-Public-Subnet-${count.index + 1}"
    Tier = "Public"
  }
}

# Private Subnet (Application)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.isms_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "ISMS-Private-Subnet-${count.index + 1}"
    Tier = "Private"
  }
}

# Data Subnet (Database)
resource "aws_subnet" "data" {
  count             = 2
  vpc_id            = aws_vpc.isms_vpc.id
  cidr_block        = "10.0.${count.index + 20}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "ISMS-Data-Subnet-${count.index + 1}"
    Tier = "Data"
  }
}

# Security Group: Web Tier (HTTPS Only)
resource "aws_security_group" "web_tier" {
  name        = "isms-web-tier-sg"
  description = "ISMS-P Compliant Web Tier Security Group"
  vpc_id      = aws_vpc.isms_vpc.id

  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name       = "ISMS-Web-Tier-SG"
    Compliance = "ISMS-P"
  }
}

# CloudTrail: 모든 API 호출 로깅
resource "aws_cloudtrail" "isms_audit" {
  name                          = "isms-p-audit-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true
  kms_key_id                    = aws_kms_key.cloudtrail.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/"]
    }
  }

  tags = {
    Name       = "ISMS-P-CloudTrail"
    Compliance = "ISMS-P"
  }
}

# KMS Key: CloudTrail 로그 암호화
resource "aws_kms_key" "cloudtrail" {
  description             = "KMS key for CloudTrail logs encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudTrail to encrypt logs"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = [
          "kms:GenerateDataKey*",
          "kms:DecryptDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name       = "ISMS-P-CloudTrail-KMS"
    Compliance = "ISMS-P"
  }
}

# S3 Bucket: 개인정보 저장 (암호화 강제)
resource "aws_s3_bucket" "personal_data" {
  bucket = "isms-p-personal-data-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name       = "ISMS-P-Personal-Data"
    Compliance = "ISMS-P"
    DataType   = "PersonalInformation"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "personal_data" {
  bucket = aws_s3_bucket.personal_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_encryption.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "personal_data" {
  bucket = aws_s3_bucket.personal_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Lifecycle Policy: 개인정보 자동 파기
resource "aws_s3_bucket_lifecycle_configuration" "personal_data" {
  bucket = aws_s3_bucket.personal_data.id

  rule {
    id     = "auto-delete-personal-data"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 365
      storage_class = "GLACIER"
    }

    expiration {
      days = 1095  # 3년 후 자동 삭제
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Security Hub: 컴플라이언스 자동 검증
resource "aws_securityhub_account" "main" {
  enable_default_standards = true
}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:ap-northeast-2::standards/cis-aws-foundations-benchmark/v/1.2.0"
}

resource "aws_securityhub_standards_subscription" "pci_dss" {
  standards_arn = "arn:aws:securityhub:ap-northeast-2::standards/pci-dss/v/3.2.1"
}

# GuardDuty: 위협 탐지
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name       = "ISMS-P-GuardDuty"
    Compliance = "ISMS-P"
  }
}

# EventBridge Rule: 보안 이벤트 자동 알림
resource "aws_cloudwatch_event_rule" "security_alerts" {
  name        = "isms-p-security-alerts"
  description = "ISMS-P Security Event Alerts"

  event_pattern = jsonencode({
    source = ["aws.guardduty", "aws.securityhub"]
    detail-type = [
      "GuardDuty Finding",
      "Security Hub Findings - Imported"
    ]
    detail = {
      severity = ["HIGH", "CRITICAL"]
    }
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.security_alerts.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.security_alerts.arn
}

resource "aws_sns_topic" "security_alerts" {
  name              = "isms-p-security-alerts"
  kms_master_key_id = aws_kms_key.sns.id

  tags = {
    Name       = "ISMS-P-Security-Alerts"
    Compliance = "ISMS-P"
  }
}


```
-->
-->

### CloudFormation: IAM 역할 및 정책 (최소 권한 원칙)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 접근 통제 및 최소 권한 원칙...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 접근 통제 및 최소 권한 원칙...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# ISMS-P 요구사항: 접근 통제 및 최소 권한 원칙
# CloudFormation Template

AWSTemplateFormatVersion: '2010-09-09'
Description: 'ISMS-P Compliant IAM Roles and Policies'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - production
      - development
    Description: Environment name

Resources:
  # 보안 관리자 역할
  SecurityManagerRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'ISMS-Security-Manager-${Environment}'
      Description: 'ISMS-P Security Manager Role with audit and security configuration permissions'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'sts:AssumeRole'
            Condition:
              Bool:
                'aws:MultiFactorAuthPresent': 'true'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/SecurityAudit'
        - 'arn:aws:iam::aws:policy/ReadOnlyAccess'
      Policies:
        - PolicyName: ISMSComplianceManagement
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: SecurityHubFullAccess
                Effect: Allow
                Action:
                  - 'securityhub:*'
                Resource: '*'
              - Sid: ConfigFullAccess
                Effect: Allow
                Action:
                  - 'config:*'
                Resource: '*'
              - Sid: CloudTrailReadAccess
                Effect: Allow
                Action:
                  - 'cloudtrail:LookupEvents'
                  - 'cloudtrail:GetTrailStatus'
                  - 'cloudtrail:DescribeTrails'
                Resource: '*'
              - Sid: GuardDutyReadAccess
                Effect: Allow
                Action:
                  - 'guardduty:Get*'
                  - 'guardduty:List*'
                Resource: '*'
      Tags:
        - Key: Compliance
          Value: ISMS-P
        - Key: Role
          Value: SecurityManager

  # 개발자 역할 (읽기 전용 + 배포 권한)
  DeveloperRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'ISMS-Developer-${Environment}'
      Description: 'ISMS-P Developer Role with limited deployment permissions'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'sts:AssumeRole'
            Condition:
              Bool:
                'aws:MultiFactorAuthPresent': 'true'
      Policies:
        - PolicyName: DeveloperLimitedAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: ReadOnlyAccess
                Effect: Allow
                Action:
                  - 's3:GetObject'
                  - 's3:ListBucket'
                  - 'ec2:Describe*'
                  - 'rds:Describe*'
                  - 'lambda:Get*'
                  - 'lambda:List*'
                Resource: '*'
              - Sid: LambdaDeployment
                Effect: Allow
                Action:
                  - 'lambda:UpdateFunctionCode'
                  - 'lambda:UpdateFunctionConfiguration'
                Resource: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function/*'
                Condition:
                  StringEquals:
                    'aws:RequestedRegion': !Ref 'AWS::Region'
              - Sid: DenySecurityChanges
                Effect: Deny
                Action:
                  - 'iam:*'
                  - 'kms:*'
                  - 'securityhub:*'
                  - 'guardduty:*'
                Resource: '*'
      Tags:
        - Key: Compliance
          Value: ISMS-P
        - Key: Role
          Value: Developer

  # 데이터 엔지니어 역할 (개인정보 처리)
  DataEngineerRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'ISMS-DataEngineer-${Environment}'
      Description: 'ISMS-P Data Engineer Role with personal data processing permissions'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'sts:AssumeRole'
            Condition:
              Bool:
                'aws:MultiFactorAuthPresent': 'true'
              IpAddress:
                'aws:SourceIp':
                  - '10.0.0.0/8'  # 사내 네트워크만 허용
      Policies:
        - PolicyName: PersonalDataProcessing
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: S3PersonalDataAccess
                Effect: Allow
                Action:
                  - 's3:GetObject'
                  - 's3:PutObject'
                  - 's3:DeleteObject'
                Resource: !Sub 'arn:aws:s3:::isms-p-personal-data-${AWS::AccountId}/*'
                Condition:
                  StringEquals:
                    's3:x-amz-server-side-encryption': 'aws:kms'
              - Sid: KMSDecryptEncrypt
                Effect: Allow
                Action:
                  - 'kms:Decrypt'
                  - 'kms:DescribeKey'
                  - 'kms:Encrypt'
                  - 'kms:GenerateDataKey'
                Resource: !GetAtt PersonalDataKMSKey.Arn
              - Sid: CloudWatchLogsWrite
                Effect: Allow
                Action:
                  - 'logs:CreateLogGroup'
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                Resource: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/isms-p/*'
      Tags:
        - Key: Compliance
          Value: ISMS-P
        - Key: Role
          Value: DataEngineer
        - Key: DataAccess
          Value: PersonalInformation

  # KMS Key: 개인정보 암호화
  PersonalDataKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: 'KMS key for personal data encryption (ISMS-P)'
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow use of the key for encryption
            Effect: Allow
            Principal:
              AWS: !GetAtt DataEngineerRole.Arn
            Action:
              - 'kms:Encrypt'
              - 'kms:Decrypt'
              - 'kms:GenerateDataKey'
              - 'kms:DescribeKey'
            Resource: '*'
          - Sid: Allow CloudWatch Logs
            Effect: Allow
            Principal:
              Service: !Sub 'logs.${AWS::Region}.amazonaws.com'
            Action:
              - 'kms:Encrypt'
              - 'kms:Decrypt'
              - 'kms:GenerateDataKey'
            Resource: '*'
            Condition:
              ArnLike:
                'kms:EncryptionContext:aws:logs:arn': !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:*'
      Tags:
        - Key: Compliance
          Value: ISMS-P
        - Key: Purpose
          Value: PersonalDataEncryption

  PersonalDataKMSKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub 'alias/isms-p-personal-data-${Environment}'
      TargetKeyId: !Ref PersonalDataKMSKey

  # CloudWatch Alarms: IAM 정책 변경 모니터링
  IAMPolicyChangeAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: ISMS-P-IAM-Policy-Change
      AlarmDescription: 'Alert when IAM policy is modified'
      MetricName: IAMPolicyEventCount
      Namespace: CloudTrailMetrics
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref SecurityAlertsTopic

  # SNS Topic: 보안 알림
  SecurityAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub 'ISMS-P-Security-Alerts-${Environment}'
      DisplayName: 'ISMS-P Security Alerts'
      KmsMasterKeyId: !GetAtt SNSKMSKey.Arn
      Tags:
        - Key: Compliance
          Value: ISMS-P

  SNSKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: 'KMS key for SNS topic encryption'
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow SNS to use the key
            Effect: Allow
            Principal:
              Service: sns.amazonaws.com
            Action:
              - 'kms:Decrypt'
              - 'kms:GenerateDataKey'
            Resource: '*'

Outputs:
  SecurityManagerRoleArn:
    Description: ARN of Security Manager Role
    Value: !GetAtt SecurityManagerRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-SecurityManagerRole'

  DeveloperRoleArn:
    Description: ARN of Developer Role
    Value: !GetAtt DeveloperRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-DeveloperRole'

  DataEngineerRoleArn:
    Description: ARN of Data Engineer Role
    Value: !GetAtt DataEngineerRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-DataEngineerRole'

  PersonalDataKMSKeyId:
    Description: KMS Key ID for Personal Data Encryption
    Value: !Ref PersonalDataKMSKey
    Export:
      Name: !Sub '${AWS::StackName}-PersonalDataKMSKey'


```
-->
-->

<!--
# SIEM Detection Query: Terraform/CloudFormation 배포 추적

## Splunk SPL
index=aws sourcetype=aws:cloudtrail (eventName=CreateStack OR eventName=UpdateStack OR eventName=DeleteStack OR eventName=ExecuteChangeSet)
| eval stack_operation=case(
    eventName=="CreateStack", "Stack Created",
    eventName=="UpdateStack", "Stack Updated",
    eventName=="DeleteStack", "Stack Deleted",
    eventName=="ExecuteChangeSet", "ChangeSet Executed"
  )
| table _time userIdentity.principalId eventName requestParameters.stackName stack_operation
| eval severity="MEDIUM"

## Azure Sentinel KQL
AWSCloudTrail
| where EventName in ("CreateStack", "UpdateStack", "DeleteStack", "ExecuteChangeSet")
| extend StackOperation = case(
    EventName == "CreateStack", "Stack Created",
    EventName == "UpdateStack", "Stack Updated",
    EventName == "DeleteStack", "Stack Deleted",
    EventName == "ExecuteChangeSet", "ChangeSet Executed",
    "Unknown"
  )
| extend StackName = tostring(RequestParameters.stackName)
| project TimeGenerated, UserIdentityPrincipalId, EventName, StackName, StackOperation
| extend Severity = "Medium"
-->

---

## 3. 보호대책 구현

### 3.1 접근 통제

ISMS-P 요구사항에 따라 Defense in Depth 전략을 적용한 다층 접근 통제를 구현해야 합니다.

#### AWS IAM 기반 접근 통제

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 최소 권한 원칙 적용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 최소 권한 원칙 적용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# ISMS-P 요구사항: 최소 권한 원칙 적용
# AWS IAM 정책 예시
Version: '2012-10-17'
Statement:
  - Effect: Allow
    Action:
      - s3:GetObject
      - s3:PutObject
    Resource: 'arn:aws:s3:::secure-bucket/*'
    Condition:
      StringEquals:
        's3:x-amz-server-side-encryption': 'AES256'
      IpAddress:
        'aws:SourceIp':
          - '10.0.0.0/8'  # 사내 네트워크만 허용


```
-->
-->

#### Security Group 및 NACL 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Security Group 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Security Group 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AWS Security Group 예시
# ISMS-P 요구사항: 네트워크 접근 제어
Resources:
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: web-server-sg
      GroupDescription: Security group for web servers
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS from internet
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: Allow all outbound traffic
      Tags:
        - Key: Compliance
          Value: ISMS-P


```
-->
-->

> **참고**: 전체 Security Group 설정 예시는 [AWS Security Groups 모범 사례](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html) 및 [AWS VPC 보안 모범 사례](https://aws.amazon.com/security/security-resources/)를 참조하세요.

### 3.2 암호화

#### 전송 중 암호화 (TLS/SSL)

| AWS 서비스 | 암호화 방법 | 설명 |
|-----------|------------|------|
| **ALB/NLB** | TLS 1.2 이상 | 로드 밸런서에서 TLS 종료 |
| **CloudFront** | TLS 1.2 이상, Perfect Forward Secrecy | CDN 레벨 암호화 |
| **API Gateway** | TLS 1.2 이상 | API 통신 암호화 |
| **RDS** | SSL/TLS 연결 | 데이터베이스 연결 암호화 |

#### 저장 데이터 암호화 (KMS)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # S3 버킷 암호화 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # S3 버킷 암호화 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# S3 버킷 암호화 설정
# ISMS-P 요구사항: 저장 데이터 암호화
Resources:
  SecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: secure-data-bucket
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref KMSKey
            BucketKeyEnabled: true


```
-->
-->

#### CloudTrail 로그 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 로그 관리 및 모니터링...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # ISMS-P 요구사항: 로그 관리 및 모니터링...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# ISMS-P 요구사항: 로그 관리 및 모니터링
# CloudTrail 설정 예시
Resources:
  CloudTrailLogs:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: isms-p-audit-trail
      S3BucketName: !Ref AuditLogsBucket
      IncludeGlobalServiceEvents: true
      IsLogging: true
      EventSelectors:
        - ReadWriteType: All
          IncludeManagementEvents: true
      KMSKeyId: !Ref CloudTrailKMSKey
      CloudWatchLogsLogGroupArn: !GetAtt CloudWatchLogGroup.Arn
      CloudWatchLogsRoleArn: !GetAtt CloudWatchLogsRole.Arn


```
-->
-->

### 3.3 로그 관리 및 모니터링

#### CloudWatch 로그 수집

| 로그 유형 | AWS 서비스 | 수집 방법 |
|----------|-----------|----------|
| **API 호출 로그** | CloudTrail | 자동 수집 |
| **VPC 네트워크 로그** | VPC Flow Logs | CloudWatch Logs로 전송 |
| **애플리케이션 로그** | CloudWatch Logs | 애플리케이션에서 직접 전송 |
| **보안 이벤트** | Security Hub | 통합 보안 이벤트 수집 |

#### 보안 모범 사례

| 보안 영역 | ISMS-P 요구사항 | AWS 구현 방법 | 모범 사례 |
|----------|---------------|-------------|----------|
| **접근 통제** | 최소 권한 원칙 | IAM 정책, Security Group | 역할 기반 접근 제어 (RBAC) |
| **암호화** | 전송/저장 데이터 암호화 | KMS, TLS/SSL | AES-256 암호화, 키 로테이션 |
| **로그 관리** | 보안 이벤트 로깅 | CloudTrail, CloudWatch | 중앙화된 로그 수집, 실시간 모니터링 |
| **네트워크 보안** | 네트워크 분리 | VPC, Subnet, NACL | Private Subnet 활용, NAT Gateway |
| **백업 및 복구** | 데이터 백업 | S3, EBS Snapshot | 자동화된 백업, 암호화된 백업 |

---

## 4. 개인정보 처리 단계별 요구사항

### 4.1 수집 단계

| 요구사항 | AWS 구현 방법 | 설명 |
|---------|-------------|------|
| **수집 목적 명시** | S3 버킷 태깅, 메타데이터 | 데이터 수집 목적 명확화 |
| **최소 수집 원칙** | 데이터 분류 및 태깅 | 필요한 최소한의 정보만 수집 |
| **암호화 저장** | S3 암호화, KMS | 수집 즉시 암호화 저장 |
| **접근 제어** | IAM 정책, 버킷 정책 | 수집 데이터 접근 제한 |

### 4.2 이용 단계

| 요구사항 | AWS 구현 방법 | 설명 |
|---------|-------------|------|
| **이용 목적 준수** | IAM 정책 조건 | 수집 목적 범위 내에서만 이용 |
| **접근 로그 기록** | CloudTrail, S3 Access Logs | 모든 접근 활동 로깅 |
| **데이터 무결성** | S3 버전 관리, 체크섬 | 데이터 변조 방지 |
| **암호화 전송** | TLS/SSL | 데이터 전송 시 암호화 |

### 4.3 제공 단계

| 요구사항 | AWS 구현 방법 | 설명 |
|---------|-------------|------|
| **제공 동의 확인** | Lambda 함수, DynamoDB | 제공 동의 여부 확인 |
| **제공 내역 기록** | CloudTrail, S3 Access Logs | 제공 내역 상세 기록 |
| **안전한 전송** | API Gateway, TLS | 암호화된 채널로 전송 |
| **제공 후 관리** | S3 라이프사이클 정책 | 제공 후 데이터 관리 |

### 4.4 파기 단계

| 요구사항 | AWS 구현 방법 | 설명 |
|---------|-------------|------|
| **파기 시점 준수** | S3 라이프사이클 정책 | 보유 기간 만료 시 자동 파기 |
| **완전 삭제** | S3 영구 삭제, Glacier 삭제 | 복구 불가능한 완전 삭제 |
| **파기 내역 기록** | CloudTrail, S3 Access Logs | 파기 내역 상세 기록 |
| **검증** | S3 버전 관리 확인 | 삭제 완료 검증 |

---

## 5. 실무 적용 사례

### 5.1 AWS 기반 ISMS-P 인증 사례

#### 사례 1: 전자상거래 플랫폼

| 영역 | 구현 내용 | AWS 서비스 |
|------|----------|-----------|
| **접근 통제** | 역할 기반 접근 제어, MFA 필수 | IAM, MFA |
| **암호화** | 전송/저장 데이터 암호화 | KMS, S3, RDS |
| **로그 관리** | 모든 활동 로깅 및 모니터링 | CloudTrail, CloudWatch |
| **네트워크 보안** | VPC 격리, Private Subnet 활용 | VPC, Subnet, NAT Gateway |
| **백업 및 복구** | 일일 자동 백업, 암호화된 백업 | S3, RDS Snapshot |

#### 사례 2: 핀테크 서비스

| 영역 | 구현 내용 | AWS 서비스 |
|------|----------|-----------|
| **접근 통제** | 최소 권한 원칙, 정기적 권한 검토 | IAM, Access Analyzer |
| **암호화** | 고객 관리 키(CMK) 사용 | KMS CMK |
| **로그 관리** | 실시간 보안 모니터링 | Security Hub, GuardDuty |
| **컴플라이언스** | PCI-DSS 준수 | Security Hub PCI-DSS 표준 |

### 5.2 보안 감사 대응

#### 감사 전 준비사항

| 준비 항목 | 설명 | AWS 활용 |
|----------|------|---------|
| **문서 준비** | 정보보안 정책, 절차서, 매뉴얼 | 문서화된 AWS 아키텍처 |
| **증적 자료** | 로그, 설정 파일, 정책 문서 | CloudTrail 로그, CloudFormation 템플릿 |
| **인프라 점검** | 보안 설정 검증 | AWS Config, Security Hub |
| **취약점 보완** | 발견된 취약점 사전 보완 | Security Hub 권장사항 적용 |

#### 감사 중 대응

| 단계 | 대응 방법 | AWS 활용 |
|------|---------|---------|
| **질의 응답** | 명확한 답변 및 증적 제시 | CloudTrail 로그, Config 규칙 |
| **시연** | 실제 보안 설정 시연 | AWS Console, CLI 명령어 |
| **설명** | AWS 아키텍처 및 보안 설계 설명 | 아키텍처 다이어그램, 문서 |

---

## 6. 2025년 이후 최신 업데이트

### 6.1 NIST CSF 2.0 AI 보안 요구사항

2025년 8월 21일, 한국인터넷진흥원(KISA)은 AI 서비스 기업이 고려해야 할 보안 요구사항을 발표하였으며, 이는 NIST CSF 2.0의 최신 보안 요구사항을 반영한 것입니다.

#### AI 시스템 보안 통제 강화

| 보안 통제 | 설명 | AWS 구현 방법 |
|----------|------|-------------|
| **AI 모델 학습 데이터 보호** | 학습 데이터 암호화 및 접근 제어 | S3 암호화, IAM 정책 |
| **모델 무결성 검증** | 모델 변조 방지 및 검증 | S3 버전 관리, 체크섬 검증 |
| **AI 시스템 오남용 방지** | 악의적 사용 방지 및 모니터링 | CloudWatch, GuardDuty |

#### 위협 인텔리전스 및 공격 표면 관리

| 기능 | 설명 | AWS 구현 방법 |
|------|------|-------------|
| **AI 기반 위협 인텔리전스** | AI 기반 위협 탐지 및 분석 | GuardDuty, Security Hub |
| **공격 표면 관리 (ASM)** | AI 서비스의 보안 취약점 식별 | Security Hub, Config |
| **자동화된 대응** | 위협 탐지 시 자동 대응 | EventBridge, Lambda |

### 6.2 AI 서비스 개인정보 보호 강화

#### 개인정보 처리 과정 보안 조치

| 처리 단계 | 보안 요구사항 | AWS 구현 방법 |
|----------|-------------|-------------|
| **수집** | 최소 수집 원칙, 암호화 저장 | S3 암호화, 데이터 분류 |
| **저장** | 암호화 저장, 접근 제어 | KMS, IAM 정책 |
| **처리** | 처리 과정 로깅, 무결성 검증 | CloudTrail, S3 버전 관리 |
| **파기** | 완전 삭제, 파기 내역 기록 | S3 라이프사이클 정책, CloudTrail |

### 6.3 NIST CSF 2.0 사이버 AI 프로파일

NIST는 AI 시스템의 안전한 도입을 위한 사이버보안 프레임워크 초안인 '사이버 AI 프로파일'을 공개하였습니다.

#### 주요 내용

| 영역 | 설명 | ISMS-P 연계 |
|------|------|------------|
| **AI 시스템 식별** | AI 자산 분류 및 관리 | 자산 관리 요구사항 |
| **AI 위협 보호** | AI 특유의 위협 요소 대응 | 보호대책 요구사항 |
| **AI 위협 탐지** | AI 기반 위협 탐지 | 모니터링 요구사항 |
| **AI 위협 대응** | AI 위협 대응 체계 | 침해사고 대응 요구사항 |

---

## 결론

2025년 개정된 ISMS-P 인증 기준은 클라우드 환경에서의 보안 요구사항을 더욱 강화하고, NIST CSF 2.0 연계, AI 보안 요구사항 등 최신 보안 트렌드를 반영하고 있습니다.

AWS 환경에서 ISMS-P 인증을 받기 위해서는:

1. **체계적인 관리체계 수립**: 정보보안 정책, 조직 구성, 위험 관리 체계 구축
2. **다층 보안 방어 구현**: Defense in Depth 전략을 통한 접근 통제, 암호화, 모니터링
3. **지속적인 모니터링**: CloudTrail, CloudWatch, Security Hub를 통한 실시간 보안 모니터링
4. **규정 준수 자동화**: AWS Config, Security Hub를 통한 컴플라이언스 자동 검증

이 가이드를 참고하여 AWS 환경에서 ISMS-P 인증을 성공적으로 준비하시기 바랍니다.

### 관련 자료

#### 공식 인증 기관 및 법규

| 구분 | 자료명 | URL | 설명 |
|-----|-------|-----|------|
| **KISA** | ISMS-P 인증 공식 사이트 | [https://isms.kisa.or.kr/](https://isms.kisa.or.kr/) | 인증 기준, 신청 절차, Q&A |
| **KISA** | 2025년 ISMS-P 인증 기준 해설서 | [https://isms.kisa.or.kr/main/ispims/notice/?boardId=bbs_0000000000000045&mode=view&cntId=97](https://isms.kisa.or.kr/main/ispims/notice/?boardId=bbs_0000000000000045&mode=view&cntId=97) | 101개 기준 상세 해설 |
| **개인정보보호위원회** | 개인정보보호법 | [https://www.pipc.go.kr/](https://www.pipc.go.kr/) | 법령, 가이드라인, 판례 |
| **방송통신위원회** | 정보통신망법 | [https://www.kcc.go.kr/](https://www.kcc.go.kr/) | 정보통신서비스 제공자 의무사항 |
| **국가법령정보센터** | 개인정보보호법 전문 | [https://www.law.go.kr/법령/개인정보보호법](https://www.law.go.kr/%EB%B2%95%EB%A0%B9/%EA%B0%9C%EC%9D%B8%EC%A0%95%EB%B3%B4%EB%B3%B4%ED%98%B8%EB%B2%95) | 법령 조문 및 개정 이력 |

#### 업계 가이드 및 백서

| 구분 | 자료명 | URL | 설명 |
|-----|-------|-----|------|
| **SK Shieldus** | 2025년 ISMS-P 운영 가이드 (개정판) | [PDF 다운로드](https://www.skshieldus.com/download/files/download.do?o_fname=%2725%EB%85%84%20%EC%A0%95%EB%B3%B4%EB%B3%B4%ED%98%B8%20%EB%B0%8F%20%EA%B0%9C%EC%9D%B8%EC%A0%95%EB%B3%B4%ED%98%B8%20%EA%B4%80%EB%A6%AC%EC%B2%B4%EA%B3%84(ISMS-P)%20%EC%9A%B4%EC%98%81%20%EA%B0%80%EC%9D%B4%EB%93%9C_%EA%B0%9C%EC%A0%95%ED%8C%90.pdf&r_fname=20251230170658586.pdf) | NIST CSF 2.0 연계, AI 보안 포함 |
| **AWS** | AWS 보안 모범 사례 | [https://docs.aws.amazon.com/security/](https://docs.aws.amazon.com/security/) | IAM, VPC, KMS, CloudTrail 등 |
| **AWS** | AWS Well-Architected Framework (보안 Pillar) | [https://aws.amazon.com/architecture/well-architected/](https://aws.amazon.com/architecture/well-architected/) | 클라우드 보안 아키텍처 설계 |
| **AWS** | AWS Compliance Programs | [https://aws.amazon.com/compliance/programs/](https://aws.amazon.com/compliance/programs/) | SOC, ISO 27001, PCI-DSS 등 |
| **AWS** | AWS Security Blog | [https://aws.amazon.com/blogs/security/](https://aws.amazon.com/blogs/security/) | 최신 보안 기술 및 사례 |

#### 국제 표준 및 프레임워크

| 구분 | 자료명 | URL | 설명 |
|-----|-------|-----|------|
| **NIST** | Cybersecurity Framework 2.0 | [https://www.nist.gov/cyberframework](https://www.nist.gov/cyberframework) | ISMS-P 연계 가능 |
| **NIST** | AI Risk Management Framework | [https://www.nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) | AI 보안 요구사항 |
| **ISO** | ISO/IEC 27001:2022 | [https://www.iso.org/standard/27001](https://www.iso.org/standard/27001) | 정보보안 관리체계 국제 표준 |
| **ISO** | ISO/IEC 27701:2019 | [https://www.iso.org/standard/71670.html](https://www.iso.org/standard/71670.html) | 개인정보 관리체계 확장 |
| **MITRE** | ATT&CK Framework | [https://attack.mitre.org/](https://attack.mitre.org/) | 공격 전술 및 기법 데이터베이스 |
| **CIS** | CIS AWS Foundations Benchmark | [https://www.cisecurity.org/benchmark/amazon_web_services](https://www.cisecurity.org/benchmark/amazon_web_services) | AWS 보안 설정 가이드 |

#### AWS 서비스별 문서

| 서비스 | 문서 | URL | ISMS-P 연계 |
|--------|------|-----|------------|
| **IAM** | Identity and Access Management | [https://docs.aws.amazon.com/iam/](https://docs.aws.amazon.com/iam/) | 접근 통제 (3.1) |
| **KMS** | Key Management Service | [https://docs.aws.amazon.com/kms/](https://docs.aws.amazon.com/kms/) | 암호화 (3.2) |
| **CloudTrail** | AWS CloudTrail | [https://docs.aws.amazon.com/cloudtrail/](https://docs.aws.amazon.com/cloudtrail/) | 로그 관리 (3.3) |
| **Security Hub** | AWS Security Hub | [https://docs.aws.amazon.com/securityhub/](https://docs.aws.amazon.com/securityhub/) | 컴플라이언스 자동 검증 |
| **GuardDuty** | Amazon GuardDuty | [https://docs.aws.amazon.com/guardduty/](https://docs.aws.amazon.com/guardduty/) | 위협 탐지 |
| **Config** | AWS Config | [https://docs.aws.amazon.com/config/](https://docs.aws.amazon.com/config/) | 규정 준수 모니터링 |
| **VPC** | Virtual Private Cloud | [https://docs.aws.amazon.com/vpc/](https://docs.aws.amazon.com/vpc/) | 네트워크 보안 |
| **Macie** | Amazon Macie | [https://docs.aws.amazon.com/macie/](https://docs.aws.amazon.com/macie/) | 개인정보 자동 탐지 |

#### 교육 및 인증 과정

| 구분 | 과정명 | URL | 대상 |
|-----|-------|-----|------|
| **KISA** | ISMS-P 인증심사원 양성 과정 | [https://edu.kisa.or.kr/](https://edu.kisa.or.kr/) | 심사원, 컨설턴트 |
| **AWS** | AWS Certified Security - Specialty | [https://aws.amazon.com/certification/certified-security-specialty/](https://aws.amazon.com/certification/certified-security-specialty/) | 보안 엔지니어 |
| **AWS** | AWS Security Fundamentals | [https://aws.amazon.com/training/](https://aws.amazon.com/training/) | 초급자 |
| **Tech Blog** | ISMS-P 인증 페이지 | [/certifications/isms-p/](/certifications/isms-p/) | 인증 준비자 |
| **Tech Blog** | 온라인 강의 | [https://edu.2twodragon.com/courses/isms-p](https://edu.2twodragon.com/courses/isms-p) | 실무자 |

#### 커뮤니티 및 Q&A

| 구분 | 플랫폼 | URL | 설명 |
|-----|-------|-----|------|
| **AWS re:Post** | AWS 공식 Q&A | [https://repost.aws/](https://repost.aws/) | AWS 전문가 답변 |
| **GitHub** | aws-samples/security | [https://github.com/aws-samples](https://github.com/aws-samples) | AWS 보안 샘플 코드 |
| **Reddit** | r/aws | [https://www.reddit.com/r/aws/](https://www.reddit.com/r/aws/) | AWS 커뮤니티 |
| **Stack Overflow** | aws tag | [https://stackoverflow.com/questions/tagged/aws](https://stackoverflow.com/questions/tagged/aws) | 기술 Q&A |

#### 관련 블로그 포스트 (Tech Blog)

| 제목 | 카테고리 | 링크 |
|-----|---------|------|
| AWS Security Hub 완벽 가이드 | Security | /posts/aws-security-hub-guide/ |
| IAM 최소 권한 원칙 구현 | Security | /posts/iam-least-privilege/ |
| KMS 암호화 키 관리 전략 | Security | /posts/kms-key-management/ |
| CloudTrail 로그 분석 및 위협 탐지 | Security | /posts/cloudtrail-log-analysis/ |
| Terraform으로 AWS 보안 자동화 | DevOps | /posts/terraform-aws-security-automation/ |

#### 보안 도구 및 오픈소스

| 도구 | 용도 | URL | ISMS-P 활용 |
|-----|------|-----|------------|
| **Prowler** | AWS 보안 감사 | [https://github.com/prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | 컴플라이언스 자동 점검 |
| **ScoutSuite** | 멀티 클라우드 보안 감사 | [https://github.com/nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | 취약점 스캐닝 |
| **CloudMapper** | AWS 네트워크 시각화 | [https://github.com/duo-labs/cloudmapper](https://github.com/duo-labs/cloudmapper) | 네트워크 구조 분석 |
| **CloudSploit** | AWS 보안 스캐너 | [https://github.com/aquasecurity/cloudsploit](https://github.com/aquasecurity/cloudsploit) | 보안 설정 검증 |
| **Pacu** | AWS 모의 해킹 도구 | [https://github.com/RhinoSecurityLabs/pacu](https://github.com/RhinoSecurityLabs/pacu) | 보안 테스트 |

#### 법률 및 컨설팅

| 구분 | 기관 | URL | 서비스 |
|-----|------|-----|--------|
| **법률** | 법무법인 광장 | [https://www.leeko.com/](https://www.leeko.com/) | 개인정보보호법 자문 |
| **법률** | 법무법인 율촌 | [https://www.yulchon.com/](https://www.yulchon.com/) | 정보보호 법률 자문 |
| **컨설팅** | SK Shieldus | [https://www.skshieldus.com/](https://www.skshieldus.com/) | ISMS-P 인증 컨설팅 |
| **컨설팅** | 이글루시큐리티 | [https://www.igloosec.co.kr/](https://www.igloosec.co.kr/) | 보안 컨설팅 |
| **컨설팅** | 안랩 | [https://www.ahnlab.com/](https://www.ahnlab.com/) | 종합 보안 솔루션 |

---

## 추가 학습 자료

### ISMS-P 체크리스트 (Self-Assessment)

인증 준비를 위한 자가 점검 체크리스트는 다음 링크에서 다운로드할 수 있습니다:

- [KISA ISMS-P 자가 점검표](https://isms.kisa.or.kr/main/ispims/intro/?boardId=bbs_0000000000000045)
- [AWS Well-Architected Security Pillar 체크리스트](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

### 샘플 정책 및 절차서

- [정보보호 정책 샘플](https://isms.kisa.or.kr/download/ISMS-P_Policy_Sample.docx)
- [개인정보 처리방침 샘플](https://www.privacy.go.kr/a3sc/per/inf/perInfStep03.do)
- [침해사고 대응 절차서 샘플](https://isms.kisa.or.kr/download/ISMS-P_Incident_Response.pdf)

### 실습 환경

- [AWS Free Tier](https://aws.amazon.com/free/) - 무료로 AWS 서비스 실습
- [AWS Workshops](https://workshops.aws/) - 실습 중심 워크샵
- [AWS Solutions Library](https://aws.amazon.com/solutions/) - 검증된 아키텍처 템플릿

---

**마지막 업데이트**: 2026-01-14
**작성 기준**: SK Shieldus 2025년 ISMS-P 운영 가이드 (개정판)
**검증 기준**: KISA 2025년 ISMS-P 인증 기준 (101개 항목)
**AWS 서비스 버전**: 2026년 1월 기준 최신 버전
**법규 기준**: 개인정보보호법 (2025년 개정), 정보통신망법 (2025년 개정)

---

**면책 조항**: 이 포스팅은 정보 제공 목적으로 작성되었으며, 법률 자문이나 공식 인증 가이드를 대체하지 않습니다. ISMS-P 인증 신청 전에 반드시 KISA 공식 문서와 전문 컨설턴트의 조언을 참고하시기 바랍니다.

---

**저작권**: 이 포스팅의 코드 예제와 아키텍처 다이어그램은 [MIT 라이선스](https://opensource.org/licenses/MIT)를 따릅니다. 자유롭게 사용 및 수정 가능하며, 출처 표기를 권장합니다.

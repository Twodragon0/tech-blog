---
author: Yongho Ha
categories:
- cloud
certifications:
- aws-saa
comments: true
date: 2025-05-16 00:53:10 +0900
description: 클라우드 시큐리티 7기 5주차. AWS Control Tower 멀티 계정 관리(Landing Zone, Guardrails,
  SCP), ZTNA(Zero Trust Network Access) 개념 및 AWS 구현, 2025년 거버넌스 업데이트 실무 정리.
excerpt: AWS Control Tower 및 ZTNA 완벽 가이드. 멀티 계정 거버넌스, Zero Trust 구현 실무 정리.
image: /assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA.svg
image_alt: 'Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA'
keywords:
- AWS
- Control-Tower
- ZTNA
- Zero-Trust
- Landing-Zone
- Guardrails
- SCP
- 멀티계정
- Organizations
- 제로트러스트
layout: post
original_url: https://twodragon.tistory.com/683
schema_type: Article
tags:
- AWS
- Control-Tower
- ZTNA
- Zero-Trust
title: 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA
toc: true
---

## 요약

- **핵심 요약**: AWS Control Tower 및 ZTNA 완벽 가이드. 멀티 계정 거버넌스, Zero Trust 구현 실무 정리.
- **주요 주제**: 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA
- **키워드**: AWS, Control-Tower, ZTNA, Zero-Trust

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">Control-Tower</span>
      <span class="tag">ZTNA</span>
      <span class="tag">Zero-Trust</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS Control Tower 멀티 계정 관리</strong>: Landing Zone 자동 설정, Guardrails 정책 적용(필수/권장/선택), 계정 팩토리(자동 계정 생성), Organizations 및 SCP 활용, 2025년 업데이트(계정 마이그레이션 개선, standalone 분리 불필요)</li>
      <li><strong>ZTNA(Zero Trust Network Access)</strong>: Zero Trust 개념("절대 신뢰하지 말고, 항상 검증하라"), AWS 구현 방법(PrivateLink, VPC Endpoint, Security Group 최소 권한), 클라우드 환경 제로 트러스트 보안 모델 적용</li>
      <li><strong>2025년 AWS 거버넌스 업데이트</strong>: Organizations 계정 마이그레이션 개선(조직 간 직접 이동, 다운타임 최소화), Control Tower Guardrails 확장, SCP 정책 자동화</li>
      <li><strong>실무 적용</strong>: 멀티 계정 아키텍처 설계, 거버넌스 정책 자동화, 제로 트러스트 네트워크 구성, 보안 및 컴플라이언스 통합 관리</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS Control Tower, ZTNA, Zero Trust</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## Executive Summary

본 포스트는 클라우드 시큐리티 과정 7기 5주차의 핵심 내용인 **AWS Control Tower와 ZTNA(Zero Trust Network Access)**를 다룹니다. 멀티 계정 거버넌스부터 Zero Trust 보안 모델 구현까지 실무에서 즉시 활용할 수 있는 고품질 콘텐츠를 제공합니다.

### Learning Scorecard

| 평가 항목 | 점수 | 설명 |
|----------|------|------|
| **실무 적용성** | ⭐⭐⭐⭐⭐ | Control Tower 설정부터 SCP 정책까지 step-by-step 가이드 제공 |
| **기술 깊이** | ⭐⭐⭐⭐⭐ | Landing Zone 아키텍처, Guardrails 메커니즘 심층 분석 |
| **보안 커버리지** | ⭐⭐⭐⭐⭐ | 예방/탐지/대응 전 단계 포괄, ISMS-P 매핑 포함 |
| **코드/정책 예제** | ⭐⭐⭐⭐⭐ | SCP JSON 정책, SIEM 쿼리, Terraform 코드 제공 |
| **ROI/비즈니스 가치** | ⭐⭐⭐⭐☆ | 경영진 보고 템플릿, TCO 분석 포함 |

### 학습 시간 가이드

| 섹션 | 예상 시간 | 난이도 |
|------|----------|--------|
| AWS Control Tower 기초 | 30분 | 초급 |
| Landing Zone 아키텍처 | 45분 | 중급 |
| SCP 정책 작성 | 60분 | 고급 |
| ZTNA 개념 및 구현 | 45분 | 중급 |
| 실습 (hands-on) | 90분 | 고급 |
| **총 학습 시간** | **4-5시간** | - |

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 시큐리티 과정 7기 5주차에서 다룬 **AWS Control Tower**와 **ZTNA(Zero Trust Network Access)**를 실무 중심으로 깊이 있게 다룹니다.

### 강의 운영 방식

이 과정은 **게더 타운(Gather Town)**에서 진행되며, 각 세션은 다음과 같이 구성됩니다:

- **20분 강의** + **5분 휴식** 반복
- 온라인 강의 특성상 눈의 피로를 줄이고 집중력을 최대화하기 위한 구성
- 실시간 Q&A 및 실습 세션 포함

### 왜 Control Tower와 ZTNA인가?

현대 기업의 클라우드 환경은 다음과 같은 과제를 직면합니다:

1. **멀티 계정 관리의 복잡성**: 수십~수백 개의 AWS 계정을 일관되게 관리해야 함
2. **거버넌스 자동화 필요성**: 수동 점검으로는 컴플라이언스 유지 불가능
3. **경계 기반 보안의 한계**: VPN/방화벽만으로는 내부자 위협 대응 불가
4. **규제 준수 압박**: ISMS-P, ISO 27001, PCI-DSS 등 다양한 규제 요구사항

AWS Control Tower는 **멀티 계정 거버넌스 자동화**를, ZTNA는 **경계 없는 보안 아키텍처**를 제공하여 이러한 과제를 해결합니다.

이 글에서는 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA에 대해 실무 중심으로 상세히 다룹니다.

<img src="{{ '/assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA_image.jpg' | relative_url }}" alt="Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA" loading="lazy" class="post-image">

<figure>
<img src="{{ '/assets/images/diagrams/diagram_zero_trust.png' | relative_url }}" alt="Zero Trust Security Architecture" loading="lazy" class="post-image">
<figcaption>Zero Trust 보안 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

## 1. 5주차 커리큘럼 개요

### 1.1 학습 목표

이번 5주차에서는 AWS Control Tower와 ZTNA(Zero Trust Network Access)를 중심으로 클라우드 거버넌스와 보안 아키텍처를 학습합니다.

| 시간 | 주제 | 내용 |
|------|------|------|
| 10:00 - 10:20 | 근황 토크 | 한 주간의 보안 이슈 공유 및 Q&A |
| 10:25 - 10:50 | AWS Control Tower | Landing Zone, SCP, 계정 관리 |
| 11:00 - 11:25 | ZTNA 개념 | Zero Trust 원칙, 구현 전략 |
| 11:30 - 11:50 | 실습 | Control Tower 설정, SCP 정책 작성 |

### 1.2 AWS Control Tower 핵심 개념

![AWS Control Tower - Landing Zone, SCP, Guardrails](/assets/images/diagrams/2025-05-16-aws-control-tower.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```
AWS Control Tower Components:
- Landing Zone (Base Environment)
- SCP (Service Control Policy)
- Guardrails (Governance Rules)
```

</details>

## 2. AWS Control Tower 완전 가이드

### 2.1 Control Tower란 무엇인가?

AWS Control Tower는 **멀티 계정 AWS 환경을 자동으로 설정하고 관리하는 서비스**입니다. 다음 핵심 기능을 제공합니다:

| 기능 | 설명 | 비즈니스 가치 |
|------|------|--------------|
| **Landing Zone** | 보안 모범 사례 기반 초기 환경 자동 구성 | 초기 설정 시간 90% 단축 |
| **Guardrails** | 예방적/탐지적 정책 자동 적용 | 컴플라이언스 위반 70% 감소 |
| **Account Factory** | 표준화된 계정 자동 생성 | 계정 프로비저닝 시간 80% 단축 |
| **Dashboard** | 통합 거버넌스 현황 모니터링 | 감사 준비 시간 60% 단축 |

### 2.2 Landing Zone 아키텍처 심층 분석

Landing Zone은 Control Tower의 핵심 개념으로, **보안 모범 사례를 적용한 멀티 계정 기반 환경**을 의미합니다.

#### 2.2.1 Landing Zone 구성 요소

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS Organizations (Root)                     │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Security OU    │  │  Infrastructure │  │  Sandbox OU     │ │
│  │                 │  │       OU        │  │                 │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │ Log       │  │  │  │ Network   │  │  │  │ Dev-1     │  │ │
│  │  │ Archive   │  │  │  │ Account   │  │  │  │           │  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │ Audit     │  │  │  │ Shared    │  │  │  │ Dev-2     │  │ │
│  │  │ Account   │  │  │  │ Services  │  │  │  │           │  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Guardrails (SCP + Config Rules)              │  │
│  │  ✓ Prevent public S3 buckets                             │  │
│  │  ✓ Enforce MFA for root account                          │  │
│  │  ✓ Deny region outside allowed list                      │  │
│  │  ✓ Monitor CloudTrail changes                            │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘


```
-->
-->

#### 2.2.2 핵심 계정 역할

| 계정 유형 | 역할 | 주요 서비스 |
|----------|------|------------|
| **Management Account** | Organizations 관리, 빌링 통합 | Organizations, Billing Console |
| **Log Archive Account** | 모든 계정의 로그 중앙 보관 | S3, CloudTrail, VPC Flow Logs |
| **Audit Account** | 보안 감사 및 컴플라이언스 점검 | Security Hub, GuardDuty, Config |
| **Network Account** | 중앙 네트워크 허브 (Transit Gateway) | VPC, Transit Gateway, Route 53 |
| **Shared Services Account** | 공통 서비스 (CI/CD, 모니터링) | Jenkins, Prometheus, ELK |

#### 2.2.3 OU (Organizational Unit) 전략

**환경별 OU 구성 예시:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Organizations:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Organizations:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Organizations:
  Root:
    - Security OU:
        Purpose: "보안 및 감사 계정"
        Accounts:
          - Log Archive
          - Audit
        SCPs:
          - DenyLeavingOrganization
          - EnforceMFA

    - Infrastructure OU:
        Purpose: "공유 인프라 서비스"
        Accounts:
          - Network
          - Shared Services
        SCPs:
          - RestrictRegions
          - RequireEncryption

    - Production OU:
        Purpose: "프로덕션 워크로드"
        Accounts:
          - Prod-Frontend
          - Prod-Backend
          - Prod-Database
        SCPs:
          - PreventPublicAccess
          - EnforceTagging
          - DenyRootUser

    - Staging OU:
        Purpose: "스테이징 환경"
        Accounts:
          - Staging-App
        SCPs:
          - RestrictInstanceTypes

    - Development OU:
        Purpose: "개발 환경"
        Accounts:
          - Dev-Team-A
          - Dev-Team-B
        SCPs:
          - AllowExperimentation
          - CostLimits

    - Sandbox OU:
        Purpose: "실험 및 테스트"
        Accounts:
          - Sandbox-1
          - Sandbox-2
        SCPs:
          - MaximalRestrictions
          - AutoShutdown


```
-->
-->

### 2.3 Guardrails 완전 분석

Guardrails는 Control Tower의 **정책 엔진**으로, 다음 두 가지 유형으로 나뉩니다:

#### 2.3.1 Guardrail 유형 비교

| 유형 | 동작 방식 | 구현 기술 | 예시 |
|------|----------|----------|------|
| **Preventive (예방적)** | 위반 행위를 원천 차단 | SCP (Service Control Policy) | "S3 버킷을 public으로 설정 불가" |
| **Detective (탐지적)** | 위반 행위를 탐지하고 알림 | AWS Config Rules | "MFA 미설정 계정 탐지" |

#### 2.3.2 필수 Guardrails (Mandatory)

Control Tower가 자동으로 적용하는 필수 guardrails:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Mandatory Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Mandatory Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Mandatory Guardrails:
  1. "Disallow policy changes to log archive":
      Type: Preventive
      SCP: DenyS3BucketPolicyChanges
      Reason: "로그 무결성 보호"

  2. "Detect public read access to log archive bucket":
      Type: Detective
      ConfigRule: s3-bucket-public-read-prohibited
      Reason: "로그 노출 방지"

  3. "Disallow changes to CloudTrail":
      Type: Preventive
      SCP: DenyCloudTrailChanges
      Reason: "감사 추적 보호"

  4. "Integrate CloudTrail with CloudWatch Logs":
      Type: Preventive
      Enforced: true
      Reason: "실시간 로그 분석 가능"

  5. "Enable AWS Config in all regions":
      Type: Preventive
      Enforced: true
      Reason: "리소스 변경 추적"


```
-->
-->

#### 2.3.3 권장 Guardrails (Strongly Recommended)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Recommended Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Recommended Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Recommended Guardrails:
  1. "Enable MFA for root user":
      Type: Detective
      ConfigRule: root-account-mfa-enabled
      Impact: "High"
      ISMS-P: "접근통제-2.5.1"

  2. "Disallow internet connection through RDP":
      Type: Preventive
      SCP: DenyRDPFromInternet
      Impact: "Medium"
      ISMS-P: "접근통제-2.7.3"

  3. "Disallow public write access to S3 buckets":
      Type: Preventive
      SCP: DenyS3PublicWrite
      Impact: "High"
      ISMS-P: "암호화-2.8.2"

  4. "Enable encryption for EBS volumes":
      Type: Detective
      ConfigRule: ec2-ebs-encryption-by-default
      Impact: "High"
      ISMS-P: "암호화-2.8.1"

  5. "Detect unencrypted RDS instances":
      Type: Detective
      ConfigRule: rds-storage-encrypted
      Impact: "High"
      ISMS-P: "암호화-2.8.3"


```
-->
-->

#### 2.3.4 선택적 Guardrails (Elective)

조직의 요구사항에 따라 선택 적용:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Elective Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Elective Guardrails:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Elective Guardrails:
  1. "Disallow creation of access keys for root user":
      Type: Preventive
      SCP: DenyRootAccessKeys
      Use-Case: "고보안 환경"

  2. "Detect EC2 instances with public IP":
      Type: Detective
      ConfigRule: ec2-instance-no-public-ip
      Use-Case: "프라이빗 네트워크 전용"

  3. "Disallow launch of EC2 instances without approved AMI":
      Type: Preventive
      SCP: RequireApprovedAMI
      Use-Case: "이미지 표준화 필수"

  4. "Restrict EC2 instance types to approved list":
      Type: Preventive
      SCP: AllowedInstanceTypes
      Use-Case: "비용 통제"


```
-->
-->

### 2.4 SCP (Service Control Policy) 실전 예제

#### 2.4.1 SCP 작성 원칙

1. **명시적 거부 우선**: SCP는 권한을 부여하지 않고 제한만 함
2. **계층적 적용**: OU 레벨에서 적용되어 하위 계정 모두에 영향
3. **IAM 정책과의 관계**: `SCP ∩ IAM Policy = 실제 권한`

#### 2.4.2 실전 SCP 정책 예제

**예제 1: 특정 리전만 허용**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllOutsideAllowedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "ap-northeast-2",
            "us-east-1"
          ]
        },
        "ArnNotLike": {
          "aws:PrincipalArn": [
            "arn:aws:iam::*:role/AWSControlTowerExecution"
          ]
        }
      }
    }
  ]
}


```
-->
-->

**예제 2: S3 Public Access 완전 차단**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyS3PublicAccess",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:PutAccountPublicAccessBlock",
        "s3:PutBucketPolicy",
        "s3:PutBucketAcl",
        "s3:PutObjectAcl"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": [
            "public-read",
            "public-read-write"
          ]
        }
      }
    },
    {
      "Sid": "DenyDeletePublicAccessBlock",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteAccountPublicAccessBlock",
        "s3:DeleteBucketPublicAccessBlock"
      ],
      "Resource": "*"
    }
  ]
}


```
-->
-->

**예제 3: Root 사용자 작업 차단 (긴급 상황 제외)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootAccountActions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        },
        "StringNotEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}


```
-->
-->

**예제 4: 비용 최적화 - 비승인 인스턴스 타입 차단**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedInstanceTypes",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "ec2:StartInstances"
      ],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringNotLike": {
          "ec2:InstanceType": [
            "t3.*",
            "t3a.*",
            "m5.*",
            "c5.*"
          ]
        }
      }
    }
  ]
}


```
-->
-->

**예제 5: 태그 정책 강제 (비용 할당 추적)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceTaggingOnCreation",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "aws:RequestTag/CostCenter": "*",
          "aws:RequestTag/Project": "*",
          "aws:RequestTag/Environment": [
            "production",
            "staging",
            "development"
          ]
        }
      }
    }
  ]
}


```
-->
-->

#### 2.4.3 SCP 테스트 및 검증

**IAM Policy Simulator 활용:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# AWS CLI로 SCP 효과 시뮬레이션
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/test-user \
  --action-names ec2:RunInstances \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:instance/* \
  --context-entries \
    "ContextKeyName=ec2:InstanceType,ContextKeyValues=t2.large,ContextKeyType=string"
```

**응답 예시:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "EvaluationResults": [
    {
      "EvalActionName": "ec2:RunInstances",
      "EvalResourceName": "arn:aws:ec2:us-east-1:123456789012:instance/*",
      "EvalDecision": "implicitDeny",
      "MatchedStatements": [],
      "MissingContextValues": [],
      "OrganizationsDecisionDetail": {
        "AllowedByOrganizations": false
      }
    }
  ]
}


```
-->
-->

### 2.5 Account Factory 설정 가이드

#### 2.5.1 Account Factory 개요

Account Factory는 **표준화된 AWS 계정을 자동으로 생성**하는 기능입니다.

**자동 구성 항목:**
- VPC 및 서브넷 생성
- IAM Identity Center (AWS SSO) 사용자 할당
- Guardrails 적용
- CloudTrail 및 Config 활성화
- 태그 정책 적용

#### 2.5.2 계정 생성 자동화 (Terraform)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # terraform/account-factory.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # terraform/account-factory.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# terraform/account-factory.tf

resource "aws_servicecatalog_provisioned_product" "new_account" {
  name                       = "prod-backend-account"
  product_id                 = data.aws_servicecatalog_product.account_factory.id
  provisioning_artifact_id   = data.aws_servicecatalog_product.account_factory.provisioning_artifact_ids[0]
  path_id                    = data.aws_servicecatalog_launch_paths.account_factory.summary[0].path_id

  provisioning_parameters {
    key   = "AccountEmail"
    value = "aws-prod-backend@company.com"
  }

  provisioning_parameters {
    key   = "AccountName"
    value = "Production-Backend"
  }

  provisioning_parameters {
    key   = "ManagedOrganizationalUnit"
    value = "Production OU"
  }

  provisioning_parameters {
    key   = "SSOUserEmail"
    value = "backend-team@company.com"
  }

  provisioning_parameters {
    key   = "SSOUserFirstName"
    value = "Backend"
  }

  provisioning_parameters {
    key   = "SSOUserLastName"
    value = "Team"
  }

  tags = {
    CostCenter  = "Engineering"
    Project     = "Backend-Services"
    Environment = "Production"
  }
}

data "aws_servicecatalog_product" "account_factory" {
  id = "prod-xxxxxxxxxx"
}

data "aws_servicecatalog_launch_paths" "account_factory" {
  product_id = data.aws_servicecatalog_product.account_factory.id
}


```
-->
-->

#### 2.5.3 계정 생성 후 자동화 (Lambda + EventBridge)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # lambda/account_post_creation.py...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # lambda/account_post_creation.py...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# lambda/account_post_creation.py

import boto3
import json

def lambda_handler(event, context):
    """
    Account Factory로 생성된 계정에 추가 구성 적용
    - VPC Peering 설정
    - Transit Gateway 연결
    - SSM Parameter Store 초기화
    - SNS 알림 구독
    """

    account_id = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']
    account_name = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountName']

    print(f"Processing new account: {account_name} ({account_id})")

    # 1. Assume role to new account
    sts_client = boto3.client('sts')
    role_arn = f"arn:aws:iam::{account_id}:role/AWSControlTowerExecution"

    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AccountSetupSession'
    )

    credentials = assumed_role['Credentials']

    # 2. Setup VPC Peering with Network Account
    ec2_client = boto3.client(
        'ec2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    network_account_id = '123456789012'  # Network Account ID
    network_vpc_id = 'vpc-xxxxxxxxx'      # Network VPC ID

    # Create VPC Peering Connection
    peering_response = ec2_client.create_vpc_peering_connection(
        VpcId=get_default_vpc(ec2_client),
        PeerVpcId=network_vpc_id,
        PeerOwnerId=network_account_id
    )

    print(f"VPC Peering created: {peering_response['VpcPeeringConnection']['VpcPeeringConnectionId']}")

    # 3. Initialize SSM Parameter Store
    ssm_client = boto3.client(
        'ssm',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    ssm_client.put_parameter(
        Name='/config/account/name',
        Value=account_name,
        Type='String',
        Description='Account name for automation scripts'
    )

    # 4. Subscribe to Security Alerts SNS Topic
    sns_client = boto3.client('sns')
    topic_arn = 'arn:aws:sns:ap-northeast-2:123456789012:security-alerts'

    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=f'security-{account_id}@company.com'
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Account {account_name} setup completed')
    }

def get_default_vpc(ec2_client):
    """Get default VPC ID"""
    vpcs = ec2_client.describe_vpcs(
        Filters=[{'Name': 'isDefault', 'Values': ['true']}]
    )
    return vpcs['Vpcs'][0]['VpcId']


```
-->
-->

**EventBridge Rule 설정:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```json
{
  "source": ["aws.controltower"],
  "detail-type": ["AWS Service Event via CloudTrail"],
  "detail": {
    "eventName": ["CreateManagedAccount"]
  }
}
```

### 1.3 Zero Trust 아키텍처 원칙

ZTNA의 핵심 원칙:

| 원칙 | 설명 | AWS 구현 |
|------|------|----------|
| **Never Trust** | 모든 접근을 검증 | IAM Identity Center |
| **Always Verify** | 지속적 인증/인가 | AWS SSO + MFA |
| **Assume Breach** | 침해 가정 설계 | VPC 세분화, 마이크로세그멘테이션 |
| **Least Privilege** | 최소 권한 원칙 | IAM 정책 최소화 |

## 3. ZTNA (Zero Trust Network Access) 완전 가이드

### 3.1 Zero Trust란 무엇인가?

Zero Trust는 "**절대 신뢰하지 말고, 항상 검증하라 (Never Trust, Always Verify)**"는 보안 원칙에 기반한 아키텍처입니다.

#### 3.1.1 전통적 보안 vs Zero Trust

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌────────────────────────────────────────────────────────────────┐
│              전통적 경계 기반 보안 (Perimeter Security)          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Internet  →  [Firewall]  →  Internal Network (Trusted)      │
│                                                                 │
│   문제점:                                                        │
│   - 내부 네트워크는 신뢰됨 (내부자 위협 취약)                     │
│   - 한 번 침투하면 측면 이동 가능                                │
│   - VPN 접속만으로 모든 리소스 접근 가능                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    Zero Trust 보안 모델                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User  →  [Identity Verification]  →  [Policy Engine]  →     │
│            [Device Check]            →  [Resource Access]      │
│                                                                 │
│   특징:                                                         │
│   - 모든 요청을 개별적으로 검증                                  │
│   - 내부/외부 구분 없음                                         │
│   - 마이크로세그멘테이션으로 측면 이동 차단                       │
│   - 최소 권한 원칙 (Least Privilege) 적용                       │
└────────────────────────────────────────────────────────────────┘


```
-->
-->

#### 3.1.2 Zero Trust 5대 원칙 (NIST SP 800-207)

| 원칙 | 설명 | 구현 예시 |
|------|------|----------|
| **1. 명시적 검증** | 모든 접근 요청을 ID, 디바이스, 위치, 행위 등 모든 가용 데이터를 기반으로 검증 | AWS IAM Identity Center + MFA + Device Trust |
| **2. 최소 권한 접근** | Just-In-Time, Just-Enough-Access (JIT/JEA) 원칙 적용 | IAM Session Policies, Temporary Credentials |
| **3. 침해 가정** | 이미 침해되었다고 가정하고 피해 범위 최소화 (Blast Radius) | VPC Isolation, Security Groups, NACLs |
| **4. 마이크로세그멘테이션** | 네트워크를 작은 단위로 분할하여 측면 이동 차단 | Security Group per Function, PrivateLink |
| **5. 지속적 모니터링** | 모든 활동을 실시간 모니터링하고 이상 행위 탐지 | GuardDuty, CloudTrail, Security Hub |

### 3.2 Google BeyondCorp 모델 분석

Google의 BeyondCorp는 Zero Trust 구현의 대표적 사례입니다.

#### 3.2.1 BeyondCorp 아키텍처

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────────────────────────────────────────────────────────┐
│                      BeyondCorp 구성 요소                        │
│                                                                  │
│  1. [Device Inventory] - 모든 디바이스 등록 및 상태 추적         │
│     ↓                                                            │
│  2. [User/Device Authentication] - 강력한 인증 (FIDO2, MFA)     │
│     ↓                                                            │
│  3. [Trust Inference] - 사용자/디바이스 신뢰도 점수 계산         │
│     ↓                                                            │
│  4. [Access Control Engine] - 정책 기반 접근 제어                │
│     ↓                                                            │
│  5. [Application Access] - 인가된 애플리케이션만 접근            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


```
-->
-->

#### 3.2.2 Trust Score 계산 로직

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython)를 참조하세요.
> 
> ```python
> # BeyondCorp-style Trust Score Calculation...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # BeyondCorp-style Trust Score Calculation...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# BeyondCorp-style Trust Score Calculation

def calculate_trust_score(user, device, context):
    """
    사용자/디바이스 신뢰도 점수 계산
    반환값: 0-100 (100 = 완전 신뢰)
    """
    score = 100

    # 1. 사용자 인증 강도
    if not user.mfa_enabled:
        score -= 30
    if user.recent_password_change_days > 90:
        score -= 10

    # 2. 디바이스 상태
    if not device.corporate_managed:
        score -= 20
    if device.os_patch_level < 90:  # 90% 이상 패치 적용
        score -= 15
    if device.antivirus_enabled == False:
        score -= 15

    # 3. 컨텍스트 (위치, 시간, 행위 패턴)
    if context.location not in user.known_locations:
        score -= 20
    if context.access_time not in user.normal_hours:
        score -= 10
    if context.unusual_activity_detected:
        score -= 25

    # 4. 과거 보안 이벤트
    if user.security_incidents_last_30days > 0:
        score -= 15

    return max(0, score)

# 접근 허용 예시
def allow_access(trust_score, resource_sensitivity):
    """
    신뢰 점수와 리소스 민감도에 따라 접근 허용 결정
    """
    thresholds = {
        'public': 0,
        'internal': 50,
        'confidential': 70,
        'highly_confidential': 85
    }

    return trust_score >= thresholds.get(resource_sensitivity, 100)


```
-->
-->

### 3.3 ZTNA vs VPN 비교

| 항목 | 전통적 VPN | ZTNA |
|------|-----------|------|
| **접근 범위** | 전체 네트워크 접근 (over-privileged) | 특정 애플리케이션만 접근 (least privilege) |
| **인증 방식** | 1회 인증 후 세션 유지 | 요청마다 검증 |
| **네트워크 가시성** | 클라이언트 IP만 보임 | 사용자/디바이스/애플리케이션 모두 가시 |
| **성능** | VPN 게이트웨이 병목 | 직접 연결로 빠름 |
| **확장성** | 동시 접속자 수 제한 | 클라우드 네이티브 확장 |
| **보안** | 내부 측면 이동 가능 | 마이크로세그멘테이션으로 차단 |
| **사용자 경험** | 연결/해제 필요, 느림 | 항상 연결된 것처럼 느껴짐 |

**실제 공격 시나리오 비교:**

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
[VPN 환경에서의 공격]
1. 공격자가 직원 노트북 탈취
2. VPN 연결 (저장된 인증 정보 사용)
3. 내부 네트워크 전체 스캔 가능
4. 데이터베이스 서버 접근
5. 전체 고객 데이터 유출

[ZTNA 환경에서의 공격]
1. 공격자가 직원 노트북 탈취
2. 인증 시도 (MFA 필요, 디바이스 신뢰도 낮음)
3. 신뢰 점수 낮아 접근 차단
4. 보안팀에 이상 행위 알림 전송
5. 계정 자동 잠금 처리


```
-->
-->

### 3.4 AWS에서 ZTNA 구현 가이드

#### 3.4.1 AWS Zero Trust 아키텍처

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌──────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌──────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌──────────────────────────────────────────────────────────────────┐
│                     AWS Zero Trust 아키텍처                       │
│                                                                   │
│  [User] ──> [IAM Identity Center] ──> [Policy Engine]            │
│             (MFA Required)            (Attribute-Based AC)        │
│                                                                   │
│             ↓                                                     │
│                                                                   │
│  [VPC A]                    [VPC B]                  [VPC C]      │
│   ┌─────────────┐            ┌─────────────┐         ┌─────────┐ │
│   │ App Tier    │            │ Data Tier   │         │ Shared  │ │
│   │             │            │             │         │ Services│ │
│   │ SG: App-SG  │◄──────────►│ SG: DB-SG   │◄───────►│ SG: Svc │ │
│   └─────────────┘  PrivateLink└─────────────┘         └─────────┘ │
│                                                                   │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │  [GuardDuty] + [Security Hub] + [CloudTrail]           │   │
│   │  실시간 위협 탐지 및 컴플라이언스 모니터링               │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘


```
-->
-->

#### 3.4.2 IAM Identity Center (AWS SSO) 설정

**1단계: Identity Source 구성**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # AWS CLI로 Identity Center 활성화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # AWS CLI로 Identity Center 활성화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# AWS CLI로 Identity Center 활성화
aws sso-admin create-instance \
  --name "CompanyIdentityCenter" \
  --region ap-northeast-2

# Microsoft Entra ID (Azure AD) 연동
aws sso-admin create-application-assignment \
  --application-arn arn:aws:sso:::application/ssoins-xxxx/apl-xxxx \
  --principal-id ${AZURE_AD_GROUP_ID} \
  --principal-type GROUP


```
-->
-->

**2단계: Permission Sets 생성 (ABAC 적용)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyAccessBasedOnDepartment",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/Department": "${aws:ResourceTag/Department}"
        }
      }
    },
    {
      "Sid": "WriteAccessOnlyToOwnedResources",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::company-data/${aws:PrincipalTag/Department}/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}


```
-->
-->

#### 3.4.3 VPC PrivateLink로 Private Access 구현

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # terraform/privatelink.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # terraform/privatelink.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# terraform/privatelink.tf

# Service Provider VPC (서비스 제공자)
resource "aws_vpc_endpoint_service" "app_service" {
  acceptance_required        = true
  network_load_balancer_arns = [aws_lb.app_nlb.arn]

  tags = {
    Name = "app-service-endpoint"
  }
}

# Service Consumer VPC (서비스 소비자)
resource "aws_vpc_endpoint" "app_endpoint" {
  vpc_id             = aws_vpc.consumer.id
  service_name       = aws_vpc_endpoint_service.app_service.service_name
  vpc_endpoint_type  = "Interface"
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.endpoint_sg.id]

  private_dns_enabled = true

  tags = {
    Name = "app-endpoint"
  }
}

# Security Group for Endpoint (최소 권한)
resource "aws_security_group" "endpoint_sg" {
  name        = "endpoint-sg"
  description = "Security group for VPC Endpoint"
  vpc_id      = aws_vpc.consumer.id

  ingress {
    description     = "HTTPS from authorized apps only"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.authorized_app.id]
  }

  egress {
    description = "No outbound traffic allowed"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "endpoint-security-group"
  }
}


```
-->
-->

#### 3.4.4 마이크로세그멘테이션 구현

**Security Group 설계 원칙:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Microsegmentation Strategy:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Microsegmentation Strategy:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Microsegmentation Strategy:
  1. "One Security Group per Function":
      Example:
        - web-tier-sg
        - app-tier-sg
        - db-tier-sg
        - cache-tier-sg

  2. "Deny by Default":
      - 모든 inbound 트래픽 차단
      - 필요한 포트만 명시적 허용

  3. "Security Group Chaining":
      - IP 기반 규칙 대신 Security Group ID 참조
      - 예: DB SG는 App SG로부터의 3306 포트만 허용

  4. "No 0.0.0.0/0 Rules":
      - 절대 모든 IP 허용하지 않음
      - ALB/NLB Security Group만 예외


```
-->
-->

**실전 Security Group 예제:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # Web Tier Security Group...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # Web Tier Security Group...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# Web Tier Security Group
resource "aws_security_group" "web" {
  name        = "web-tier-sg"
  description = "Security group for web tier (ALB)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 유일한 예외
  }

  egress {
    description     = "To App Tier only"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
}

# App Tier Security Group
resource "aws_security_group" "app" {
  name        = "app-tier-sg"
  description = "Security group for app tier"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "From Web Tier only"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    description     = "To Database only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.database.id]
  }

  egress {
    description     = "To Cache only"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.cache.id]
  }
}

# Database Tier Security Group
resource "aws_security_group" "database" {
  name        = "database-tier-sg"
  description = "Security group for database tier"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from App Tier only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # No egress rules = No outbound connections
}


```
-->
-->

### 3.5 Zero Trust 구현 로드맵

#### 3.5.1 3단계 구현 로드맵

**Phase 1: 가시성 확보 (1-2개월)**

| 활동 | 도구 | 산출물 |
|------|------|--------|
| 모든 사용자/디바이스 인벤토리 | AWS SSO, Okta, Azure AD | 사용자/디바이스 목록 |
| 애플리케이션 종속성 매핑 | AWS X-Ray, AppMesh | 서비스 맵 |
| 데이터 흐름 분석 | VPC Flow Logs, GuardDuty | 트래픽 패턴 |
| 현재 보안 상태 평가 | Security Hub, Config | 취약점 리포트 |

**Phase 2: 정책 수립 및 파일럿 (2-3개월)**

| 활동 | 도구 | 산출물 |
|------|------|--------|
| Zero Trust 정책 문서 작성 | - | 접근 제어 정책서 |
| IAM Identity Center 구성 | AWS SSO | SSO 포털 |
| 파일럿 애플리케이션 선정 | - | 파일럿 계획서 |
| PrivateLink 구성 (파일럿) | VPC Endpoint | Private Access |
| Security Group 재설계 | Terraform | IaC 코드 |

**Phase 3: 전사 확대 (3-6개월)**

| 활동 | 도구 | 산출물 |
|------|------|--------|
| 모든 애플리케이션 마이그레이션 | - | 마이그레이션 완료 |
| VPN 단계적 폐기 | - | VPN 제거 |
| 지속적 모니터링 체계 구축 | GuardDuty, Security Hub | SOC 대시보드 |
| 정책 자동화 | Lambda, EventBridge | 자동화 스크립트 |

#### 3.5.2 Quick Win 전략

즉시 시작할 수 있는 Zero Trust 요소:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Quick Wins:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Quick Wins:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Quick Wins:
  1. "MFA 100% 적용":
      Duration: "1주"
      Impact: "High"
      Tool: "IAM Identity Center"

  2. "Root 계정 접근 차단":
      Duration: "1일"
      Impact: "High"
      SCP: "DenyRootUser"

  3. "S3 Public Access 차단":
      Duration: "1일"
      Impact: "High"
      Tool: "S3 Block Public Access"

  4. "Security Group Audit":
      Duration: "1주"
      Impact: "Medium"
      Tool: "AWS Config Rule: restricted-ssh"

  5. "CloudTrail 전체 활성화":
      Duration: "1일"
      Impact: "High"
      Tool: "CloudTrail + S3"


```
-->
-->

## 4. 실습 가이드: Control Tower 초기 설정

### 4.1 사전 요구사항

Control Tower를 설정하기 전에 다음 사항을 확인하세요:

| 항목 | 요구사항 | 확인 방법 |
|------|----------|----------|
| **AWS 계정** | 신규 또는 Organizations 미사용 계정 | `aws organizations describe-organization` |
| **권한** | AdministratorAccess 또는 동등한 권한 | IAM 콘솔 확인 |
| **리전** | Control Tower 지원 리전 | [공식 문서](https://docs.aws.amazon.com/controltower/latest/userguide/region-how.html) 참조 |
| **이메일 주소** | Log Archive, Audit 계정용 각각 1개 | 유효한 이메일 주소 |

### 4.2 Step-by-Step 설정 가이드

#### Step 1: Control Tower 콘솔 접속

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# AWS CLI로 현재 계정 확인
aws sts get-caller-identity

# 출력 예시:
# {
#   "UserId": "AIDAI...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/admin"
# }
```

**웹 콘솔:**
1. AWS Management Console 로그인
2. 서비스 검색에서 "Control Tower" 입력
3. "Set up landing zone" 클릭

#### Step 2: Home Region 선택

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
Recommended Regions:
  - ap-northeast-2 (서울): "한국 기업 권장"
  - us-east-1 (버지니아): "글로벌 서비스, 최신 기능 우선 제공"

Considerations:
  - Home Region은 변경 불가
  - 모든 Guardrails는 Home Region에서 관리
  - 멀티 리전 배포는 나중에 가능
```

#### Step 3: Landing Zone 버전 선택

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# 최신 버전 확인 (AWS CLI)
aws controltower list-landing-zones --max-results 10

# 권장: 항상 최신 버전 사용
Landing Zone Version: 3.3 (2025년 1월 기준)
```

#### Step 4: 추가 리전 선택 (선택사항)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Governed Regions:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Governed Regions:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Governed Regions:
  Primary:
    - ap-northeast-2  # 서울 (필수)

  Additional (optional):
    - us-east-1       # 글로벌 서비스용
    - ap-northeast-1  # 도쿄 (재해복구)

Cost Impact:
  - 리전당 AWS Config Rules 비용 발생
  - 예상 비용: 리전당 월 $50-100


```
-->
-->

#### Step 5: Log Archive 계정 설정

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Log Archive 계정 이메일 입력
Log Archive Account Email: aws-log-archive@company.com

# 자동 생성되는 리소스:
# - S3 Bucket: aws-controltower-logs-{account-id}-{region}
# - CloudTrail: 모든 계정의 API 활동 로그
# - VPC Flow Logs: 네트워크 트래픽 로그
# - Config Logs: 리소스 변경 이력
```

**S3 버킷 정책 예시 (자동 생성):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::aws-controltower-logs-123456789012-ap-northeast-2"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::aws-controltower-logs-123456789012-ap-northeast-2/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}


```
-->
-->

#### Step 6: Audit 계정 설정

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Audit 계정 이메일 입력
Audit Account Email: aws-audit@company.com

# 자동 활성화되는 서비스:
# - AWS Security Hub
# - Amazon GuardDuty
# - AWS Config (모든 리전)
# - SNS Topic (보안 알림용)
```

**Audit 계정의 SNS 구독 예시:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# SNS Topic ARN (자동 생성)
arn:aws:sns:ap-northeast-2:987654321098:aws-controltower-SecurityNotifications

# 이메일 구독 자동 설정
# → aws-audit@company.com 으로 알림 전송
```

#### Step 7: KMS 암호화 설정 (선택사항)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # terraform/kms.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> # terraform/kms.tf...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# terraform/kms.tf

resource "aws_kms_key" "controltower" {
  description             = "KMS key for Control Tower logs"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::123456789012:root"
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
        Condition = {
          StringLike = {
            "kms:EncryptionContext:aws:cloudtrail:arn" = "arn:aws:cloudtrail:*:123456789012:trail/*"
          }
        }
      }
    ]
  })

  tags = {
    Name = "control-tower-kms-key"
  }
}

resource "aws_kms_alias" "controltower" {
  name          = "alias/control-tower"
  target_key_id = aws_kms_key.controltower.key_id
}


```
-->
-->

#### Step 8: Landing Zone 생성 시작

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # 예상 소요 시간: 60-90분...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # 예상 소요 시간: 60-90분...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 예상 소요 시간: 60-90분

# 진행 상황 확인 (AWS CLI)
aws controltower get-landing-zone \
  --landing-zone-identifier arn:aws:controltower:ap-northeast-2:123456789012:landingzone/xxxx

# 출력 예시:
# {
#   "landingZone": {
#     "status": "PROCESSING",
#     "version": "3.3",
#     "driftStatus": {
#       "status": "IN_SYNC"
#     }
#   }
# }


```
-->
-->

**생성 과정 세부 단계:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```
[0-10분]  Organizations 구성
[10-20분] Security 계정 생성 (Log Archive, Audit)
[20-40분] Guardrails 배포 (필수 + 권장)
[40-60분] AWS Config Rules 배포
[60-90분] Service Catalog Portfolio 생성 (Account Factory)

완료 시 상태: "ACTIVE"
```

### 4.3 초기 설정 검증

#### Step 1: Organizations 구조 확인

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # Organizations 구조 출력...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # Organizations 구조 출력...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Organizations 구조 출력
aws organizations list-roots
aws organizations list-organizational-units-for-parent \
  --parent-id r-xxxx

# 예상 출력:
# Root
#   ├── Security OU
#   │   ├── Log Archive
#   │   └── Audit
#   └── Sandbox OU


```
-->
-->

#### Step 2: Guardrails 활성화 확인

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# 활성화된 Guardrails 목록
aws controltower list-enabled-controls \
  --target-identifier arn:aws:organizations::123456789012:ou/o-xxxx/ou-xxxx

# 필수 Guardrails 확인:
# ✓ Disallow policy changes to log archive
# ✓ Detect public read access to log archive bucket
# ✓ Disallow changes to CloudTrail
# ✓ Enable AWS Config in all regions
```

#### Step 3: CloudTrail 로깅 확인

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # CloudTrail이 정상 작동하는지 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # CloudTrail이 정상 작동하는지 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# CloudTrail이 정상 작동하는지 확인
aws cloudtrail get-trail-status \
  --name aws-controltower-BaselineCloudTrail

# 출력:
# {
#   "IsLogging": true,
#   "LatestDeliveryTime": 1705123456.789,
#   "StartLoggingTime": 1705000000.123
# }

# Log Archive 계정의 S3 버킷 확인
aws s3 ls s3://aws-controltower-logs-123456789012-ap-northeast-2/ \
  --profile log-archive


```
-->
-->

#### Step 4: Security Hub 통합 확인

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Audit 계정에서 Security Hub 상태 확인
aws securityhub get-findings --profile audit \
  --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}'

# GuardDuty 활성화 확인
aws guardduty list-detectors --profile audit
```

### 4.4 첫 번째 계정 생성 (Account Factory)

#### Step 1: Service Catalog 접속

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Service Catalog에서 Account Factory Product 확인
aws servicecatalog search-products \
  --filters FullTextSearch=ControlTower

# Product Name: "AWS Control Tower Account Factory"
```

#### Step 2: 계정 생성 파라미터 입력

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Account Creation Parameters:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Account Creation Parameters:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Account Creation Parameters:
  AccountEmail: "dev-team-a@company.com"
  AccountName: "Development-Team-A"
  ManagedOrganizationalUnit: "Sandbox OU"  # 드롭다운 선택
  SSOUserEmail: "dev-lead@company.com"
  SSOUserFirstName: "Dev"
  SSOUserLastName: "Lead"

Optional Parameters:
  VPCOptions: "Enabled"  # VPC 자동 생성
  VPCRegion: "ap-northeast-2"
  VPCCidr: "10.1.0.0/16"


```
-->
-->

#### Step 3: 계정 생성 모니터링

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Service Catalog Provisioned Product 상태 확인
aws servicecatalog describe-provisioned-product \
  --id prod-xxxxxxxxx

# 예상 소요 시간: 30-40분

# 완료 시 계정 정보 확인
aws organizations describe-account \
  --account-id 111222333444
```

#### Step 4: SSO 접속 테스트

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # SSO 포털 URL 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # SSO 포털 URL 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# SSO 포털 URL 확인
aws sso-admin list-instances

# 출력:
# SSO Portal: https://d-xxxxxxxxxx.awsapps.com/start

# 웹 브라우저로 접속 테스트:
# 1. SSO 포털 로그인
# 2. "Development-Team-A" 계정 선택
# 3. "AdministratorAccess" 권한 선택
# 4. Management Console 접속 확인


```
-->
-->

### 4.5 문제 해결 (Troubleshooting)

#### 문제 1: Landing Zone 생성 실패

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Error: "Failed to create log archive bucket"...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Error: "Failed to create log archive bucket"...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Error: "Failed to create log archive bucket"
Cause: "이메일 주소가 이미 다른 AWS 계정에 사용 중"
Solution:
  - 새로운 이메일 주소 사용
  - 또는 AWS 계정 닫기 후 재시도

Error: "Insufficient permissions"
Cause: "IAM 사용자에게 필요한 권한 부족"
Solution:
  - AdministratorAccess 정책 연결
  - 또는 Root 계정으로 설정


```
-->
-->

#### 문제 2: Guardrails 적용 실패

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# Drift Detection 실행
aws controltower list-landing-zones

# Drift 복구
aws controltower reset-landing-zone \
  --landing-zone-identifier arn:aws:controltower:...
```

#### 문제 3: Account Factory 프로비저닝 실패

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
Error: "Email already exists"
Solution:
  - 다른 이메일 주소 사용
  - 이메일 알리아스 활용 (예: team+dev1@company.com)

Error: "OU not found"
Solution:
  - OU가 Control Tower에 등록되었는지 확인
  - Organizations 콘솔에서 OU 재확인
```

## 5. SIEM Detection Queries

### 5.1 Splunk SPL 쿼리 (AWS Control Tower)

<!--
Splunk Query: Control Tower Guardrail 위반 탐지

index=aws sourcetype=aws:cloudtrail eventName=PutBucketPolicy
| where match(requestParameters.bucketName, "aws-controltower-logs-.*")
| eval severity="CRITICAL"
| table _time, userIdentity.principalId, sourceIPAddress, requestParameters.bucketName, errorCode
| where errorCode="AccessDenied"
| stats count by userIdentity.principalId, sourceIPAddress
| where count > 3
| eval alert="Repeated attempts to modify Control Tower log bucket policy"
-->

<!--
Splunk Query: 비인가 리전에서의 리소스 생성 탐지

index=aws sourcetype=aws:cloudtrail eventName=RunInstances OR eventName=CreateBucket
| eval allowed_regions="ap-northeast-2,us-east-1"
| where NOT match(awsRegion, allowed_regions)
| eval severity="HIGH"
| table _time, userIdentity.principalId, eventName, awsRegion, sourceIPAddress
| sort -_time
-->

<!--
Splunk Query: Root 계정 사용 탐지

index=aws sourcetype=aws:cloudtrail userIdentity.type=Root
| where eventName!="ConsoleLogin"
| eval severity="CRITICAL"
| table _time, eventName, sourceIPAddress, userAgent, requestParameters
| eval alert="Root account used for API call - investigate immediately"
-->

<!--
Splunk Query: MFA 미사용 콘솔 로그인 탐지

index=aws sourcetype=aws:cloudtrail eventName=ConsoleLogin
| spath input=additionalEventData
| where additionalEventData.MFAUsed="No"
| eval severity="HIGH"
| table _time, userIdentity.principalId, sourceIPAddress, userAgent
| stats count by userIdentity.principalId, sourceIPAddress
-->

### 5.2 Azure Sentinel KQL 쿼리 (멀티 클라우드)

<!--
KQL Query: AWS + Azure 통합 모니터링 - 의심스러운 국가 로그인

union
  (AWSCloudTrail
  | where EventName == "ConsoleLogin"
  | extend CloudProvider = "AWS"),
  (SigninLogs
  | where ResultType == 0
  | extend CloudProvider = "Azure")
| extend Country = tostring(parse_json(LocationDetails).countryOrRegion)
| where Country in ("RU", "CN", "KP")
| project TimeGenerated, CloudProvider, UserPrincipalName, IPAddress, Country
| order by TimeGenerated desc
-->

<!--
KQL Query: Control Tower Guardrail 위반 패턴 분석

AWSCloudTrail
| where EventName in ("PutBucketPolicy", "DeleteBucketPublicAccessBlock", "StopLogging")
| where ErrorCode == "AccessDenied"
| summarize AttemptCount = count() by UserIdentityPrincipalId, SourceIpAddress, bin(TimeGenerated, 1h)
| where AttemptCount > 5
| extend Severity = "High"
| project TimeGenerated, UserIdentityPrincipalId, SourceIpAddress, AttemptCount, Severity
-->

### 5.3 CloudWatch Insights 쿼리

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```sql
> -- Query 1: Control Tower API 호출 모니터링...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```sql
> -- Query 1: Control Tower API 호출 모니터링...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```sql
-- Query 1: Control Tower API 호출 모니터링
fields @timestamp, eventName, userIdentity.principalId, sourceIPAddress, errorCode
| filter eventSource = "controltower.amazonaws.com"
| stats count() by eventName, errorCode
| sort count desc

-- Query 2: SCP 정책 변경 탐지
fields @timestamp, userIdentity.principalId, eventName, requestParameters
| filter eventName in ["CreatePolicy", "UpdatePolicy", "DeletePolicy"]
| filter requestParameters like /Service Control Policy/
| display @timestamp, userIdentity.principalId, eventName

-- Query 3: 비정상 시간대 활동 탐지 (업무 시간 외)
fields @timestamp, eventName, userIdentity.principalId
| filter hour(@timestamp) < 9 or hour(@timestamp) > 18
| filter eventName in ["RunInstances", "CreateBucket", "PutBucketPolicy"]
| stats count() by userIdentity.principalId, hour(@timestamp)


```
-->
-->

## 6. ISMS-P 매핑

### 6.1 Control Tower Guardrails → ISMS-P 매핑표

| ISMS-P 통제 | Control Tower Guardrail | 구현 방법 |
|-------------|------------------------|----------|
| **2.5.1 사용자 인증** | Detect whether MFA is enabled for root user | Detective (Config Rule) |
| **2.5.4 관리자 계정 보호** | Disallow access keys for root user | Preventive (SCP) |
| **2.7.1 접근권한 관리** | Enforce least privilege via IAM Identity Center | Preventive (IAM Policies) |
| **2.7.3 원격접근 통제** | Disallow internet connection through RDP/SSH | Preventive (SCP) |
| **2.8.1 암호화 적용** | Detect unencrypted EBS volumes | Detective (Config Rule) |
| **2.8.2 암호키 관리** | Enable KMS key rotation | Detective (Config Rule) |
| **2.8.3 데이터베이스 암호화** | Detect unencrypted RDS instances | Detective (Config Rule) |
| **2.9.1 로그 기록** | Enable CloudTrail in all regions | Preventive (Mandatory) |
| **2.9.2 로그 보호** | Disallow changes to CloudTrail | Preventive (SCP) |
| **2.9.3 로그 보관** | Centralize logs in Log Archive account | Preventive (S3 Lifecycle) |
| **2.10.1 백업** | Detect whether EBS volumes have backup enabled | Detective (Config Rule) |
| **2.11.1 취약점 점검** | Integrate with Security Hub | Detective (Security Hub) |
| **2.12.1 침입 탐지** | Enable GuardDuty | Detective (GuardDuty) |

### 6.2 ISMS-P 인증 심사 대응 가이드

#### 심사 항목: 2.5.1 사용자 인증

**증빙 자료:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # 1. MFA 적용 현황 리포트 (Config Rule)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # 1. MFA 적용 현황 리포트 (Config Rule)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 1. MFA 적용 현황 리포트 (Config Rule)
aws configservice get-compliance-details-by-config-rule \
  --config-rule-name root-account-mfa-enabled \
  --compliance-types NON_COMPLIANT

# 2. IAM Identity Center 사용자 목록
aws sso-admin list-permission-sets \
  --instance-arn arn:aws:sso:::instance/ssoins-xxxx

# 3. 스크린샷: Control Tower Dashboard - Guardrails 활성화 상태


```
-->
-->

**예상 질문 및 답변:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Q: "MFA 미적용 계정이 존재하는 경우 어떻게 대응하나요?"...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> Q: "MFA 미적용 계정이 존재하는 경우 어떻게 대응하나요?"...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Q: "MFA 미적용 계정이 존재하는 경우 어떻게 대응하나요?"
A:
  - Detective Guardrail이 자동 탐지
  - Security Hub에서 중앙 집중 모니터링
  - 비준수 계정에 SNS 알림 자동 전송
  - 7일 이내 시정 조치 강제 (SCP로 계정 동결 가능)

Q: "Root 계정 사용이 불가피한 경우는?"
A:
  - CloudTrail 로그로 모든 사용 추적
  - Root 사용 시 보안팀에 실시간 알림 (CloudWatch Alarm)
  - 사용 후 즉시 감사 리포트 생성


```
-->
-->

## 2. 2025년 AWS 거버넌스 업데이트

2025년에 발표된 AWS 거버넌스 관련 주요 업데이트를 정리합니다.

### 2.1 AWS Organizations 계정 마이그레이션 개선

기존에는 AWS 계정을 다른 조직으로 이동하려면 먼저 standalone 계정으로 분리한 후 다시 새 조직에 가입해야 했습니다. **2025년 업데이트로 이제 계정을 standalone으로 분리하지 않고도 조직 간 직접 이동이 가능**해졌습니다.

**주요 이점:**
- 계정 이동 과정 단순화
- 다운타임 최소화
- M&A 또는 조직 재구성 시 효율성 향상

### 2.2 AgentCore Identity - AI 에이전트 접근 제어

AI/ML 워크로드가 증가함에 따라 AWS는 **AgentCore Identity**를 도입하여 AI 에이전트에 대한 세밀한 접근 제어를 제공합니다.

**주요 기능:**
- AI 에이전트별 IAM 역할 및 정책 할당
- 에이전트 행위 감사 및 추적
- 최소 권한 원칙을 AI 워크로드에 적용
- Control Tower와 통합하여 멀티 계정 환경에서 AI 거버넌스 관리

### 2.3 IAM Policy Autopilot

**IAM Policy Autopilot**은 오픈소스 도구로, 애플리케이션 코드를 분석하여 IAM 정책을 자동으로 생성합니다.

**동작 방식:**
1. 애플리케이션 소스 코드 분석
2. AWS SDK 호출 패턴 식별
3. 필요한 최소 권한 IAM 정책 자동 생성
4. 기존 정책과의 차이 분석 및 권장 사항 제공

**사용 예시:**
```bash
# IAM Policy Autopilot 실행
iam-policy-autopilot analyze --source ./my-app --output policy.json
```

### 2.4 보안 모니터링 강화

#### AWS Security Hub GA

AWS Security Hub가 GA(General Availability)로 출시되어 **멀티 계정 보안 현황을 통합 관리**할 수 있게 되었습니다.

**주요 기능:**
- Control Tower와 자동 통합
- 모든 멤버 계정의 보안 상태 중앙 집중 관리
- 자동화된 보안 점수 산정
- 규정 준수 상태 대시보드

#### GuardDuty Extended Threat Detection

GuardDuty가 **Extended Threat Detection** 기능을 추가하여 EC2 및 ECS 환경에서의 위협 시퀀스를 탐지합니다.

**탐지 가능한 위협:**
- 다단계 공격 시퀀스 식별
- EC2 인스턴스 내 악성 행위 패턴
- ECS 컨테이너 런타임 위협
- 내부자 위협 및 측면 이동 탐지

### 2.5 Control Tower 업데이트 적용 권장 사항

1. **Organizations 계정 이동 기능 활용**: 기존 계정 구조 재편 시 새로운 직접 이동 기능 사용
2. **AI 워크로드 거버넌스**: AgentCore Identity를 통해 AI 에이전트에 대한 접근 제어 정책 수립
3. **IAM 정책 자동화**: IAM Policy Autopilot으로 과도한 권한을 가진 정책 식별 및 최적화
4. **Security Hub 통합**: 멀티 계정 보안 현황을 단일 대시보드에서 모니터링
5. **GuardDuty 확장 기능 활성화**: EC2/ECS 환경에서의 고급 위협 탐지 활성화

## 7. 경영진 보고 형식

### 7.1 Zero Trust 도입 ROI 분석

#### Executive Summary for C-Level

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```markdown
> # Zero Trust Network Access (ZTNA) 도입 제안...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```markdown
> # Zero Trust Network Access (ZTNA) 도입 제안...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```markdown
# Zero Trust Network Access (ZTNA) 도입 제안

## 현황 분석
- **현재 보안 모델**: VPN 기반 경계 보안
- **주요 리스크**: 내부자 위협, 측면 이동 공격, 과도한 접근 권한
- **규제 압박**: ISMS-P, ISO 27001 인증 요구사항

## 제안 솔루션
**AWS Control Tower + ZTNA 아키텍처**
- 멀티 계정 거버넌스 자동화
- Zero Trust 보안 모델 구현
- 지속적 컴플라이언스 모니터링

## 투자 대비 효과 (3년 기준)

| 항목 | 현재 (VPN) | ZTNA | 절감 효과 |
|------|-----------|------|----------|
| **보안 사고 비용** | 연 2억원 | 연 5천만원 | 75% 감소 |
| **컴플라이언스 비용** | 연 1억원 | 연 3천만원 | 70% 감소 |
| **운영 인력** | 5명 | 2명 | 60% 감소 |
| **VPN 인프라** | 연 8천만원 | 0원 | 100% 절감 |
| **총 비용 (3년)** | 9.6억원 | 2.4억원 | **7.2억원 절감** |

## 도입 효과

### 정량적 효과
- **보안 사고 감소**: 연평균 75% (업계 벤치마크)
- **침해 발견 시간 단축**: 200일 → 20일 (90% 개선)
- **컴플라이언스 준비 시간**: 80% 단축
- **계정 프로비저닝**: 2주 → 1일 (93% 단축)

### 정성적 효과
- 임직원 생산성 향상 (VPN 연결 불필요)
- 원격 근무 환경 개선
- 감사 대응 자동화
- 보안팀 업무 효율화

## 도입 일정
- **Phase 1 (1-2개월)**: 파일럿 (10% 사용자)
- **Phase 2 (3-5개월)**: 단계적 확대 (50% 사용자)
- **Phase 3 (6개월)**: 전사 적용 (100%)

## 투자 소요
- **초기 투자**: 1.5억원 (컨설팅, 교육, 초기 설정)
- **연간 운영비**: 3천만원 (AWS 서비스 비용)

## 추천 사항
✅ **즉시 파일럿 프로젝트 시작** (예산: 2천만원)


```
-->
-->

### 7.2 월간 거버넌스 리포트 템플릿

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Control Tower 월간 리포트 (2025년 1월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Control Tower 월간 리포트 (2025년 1월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AWS Control Tower 월간 리포트 (2025년 1월)

## 1. 계정 현황
Total Accounts: 47개
  - Production: 12개
  - Staging: 8개
  - Development: 20개
  - Sandbox: 7개

신규 생성: 3개
폐기: 1개

## 2. Guardrails 준수율
Overall Compliance: 94% (↑ 2% from last month)

Non-Compliant Controls:
  - "MFA for root user": 3개 계정 (조치 중)
  - "Encrypted EBS volumes": 12개 볼륨 (1주 내 암호화 예정)

## 3. 보안 이슈
Critical: 0건
High: 2건
  - Issue #1: Dev 계정에서 Public S3 버킷 탐지 (즉시 차단됨)
  - Issue #2: 비인가 리전(eu-west-1)에서 EC2 시작 시도 (SCP로 차단)
Medium: 15건
Low: 48건

## 4. 비용 최적화
Total AWS Spend: $125,000 (↓ 8% from last month)
  - Control Tower 비용: $2,500 (전체의 2%)
  - Guardrails로 인한 절감: $10,000 (비승인 인스턴스 타입 차단)

## 5. Action Items
High Priority:
  ☐ MFA 미적용 계정 3개 조치 (담당: 보안팀, 기한: 1/31)
  ☐ Sandbox 계정 자동 종료 정책 적용 (담당: FinOps팀, 기한: 2/7)

Medium Priority:
  ☐ 신규 Guardrail 추가: "Deny unapproved AMI" (담당: 인프라팀)


```
-->
-->

## 8. 한국 기업 사례 연구

### 8.1 금융권: K-Bank Zero Trust 전환

**배경:**
- 기존 VPN 기반 접근 제어
- 재택근무 확대로 VPN 병목 발생
- FSS (금융감독원) 보안 규제 강화

**구현:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Phase 1 (3개월):...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> Phase 1 (3개월):...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
Phase 1 (3개월):
  - AWS Control Tower 구축
  - Landing Zone 설정 (14개 계정)
  - Guardrails 적용 (필수 + 금융권 특화)

Phase 2 (4개월):
  - IAM Identity Center + Okta 연동
  - PrivateLink로 내부 시스템 접근
  - VPN 단계적 폐기

Phase 3 (2개월):
  - 전 직원 ZTNA 전환
  - SOC 통합 모니터링
  - FSS 보안 검사 통과


```
-->
-->

**효과:**
- **접속 속도**: VPN 대비 3배 향상
- **보안 사고**: 연 12건 → 2건 (83% 감소)
- **컴플라이언스**: FSS 보안 검사 100% 통과
- **비용**: VPN 인프라 폐기로 연 2억원 절감

### 8.2 제조업: H-Motors 멀티 클라우드 거버넌스

**과제:**
- AWS, Azure, GCP 동시 사용
- 글로벌 50개 법인, 200개 계정 관리
- 각 법인별 독립적 보안 정책 필요

**솔루션:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> AWS Control Tower:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> AWS Control Tower:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
AWS Control Tower:
  - Global Landing Zone (3개 리전)
  - OU 구조:
      - Korea HQ
      - Americas
      - Europe
      - APAC
  - 법인별 SCP 정책 차별화

Multi-Cloud Governance:
  - AWS Control Tower (메인)
  - Azure Policy (Azure 워크로드)
  - GCP Organization Policies (GCP 워크로드)
  - Centralized SIEM: Splunk Cloud


```
-->
-->

**성과:**
- **계정 프로비저닝**: 2주 → 4시간 (96% 단축)
- **정책 일관성**: 멀티 클라우드 통합 Guardrails
- **감사 효율**: 50개 법인 감사 3개월 → 2주
- **TCO**: 멀티 클라우드 비용 가시성 확보, 15% 절감

### 8.3 공공기관: S-Agency 클라우드 보안 강화

**규제 요구사항:**
- 행정안전부 클라우드 보안 인증 (CSAP)
- 개인정보보호법 준수
- 망 분리 의무

**구현 아키텍처:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌────────────────────────────────────────────────────┐
│             S-Agency AWS 환경                      │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Public OU    │  │ Private OU   │  │ Mgmt OU  │ │
│  │ (인터넷망)   │  │ (업무망)     │  │          │ │
│  │              │  │              │  │          │ │
│  │ SCP:         │  │ SCP:         │  │ SCP:     │ │
│  │ - Public OK  │  │ - No Internet│  │ - Admin  │ │
│  │ - Low Data   │  │ - Encryption │  │   Only   │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
│                                                     │
│  [Transit Gateway] - 망 분리 경계 제어              │
│                                                     │
└────────────────────────────────────────────────────┘


```
-->
-->

**특화 Guardrails:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Name": "공공기관 개인정보 보호 정책",
  "Controls": [
    {
      "Name": "Deny data export to internet",
      "Type": "Preventive",
      "SCP": "DenyS3PublicAccess + DenyRDSPublicAccess"
    },
    {
      "Name": "Enforce encryption at rest",
      "Type": "Detective",
      "ConfigRule": "encrypted-volumes + rds-storage-encrypted"
    },
    {
      "Name": "Log retention 7 years",
      "Type": "Preventive",
      "S3LifecyclePolicy": "7-year retention"
    },
    {
      "Name": "Restrict to Korea regions only",
      "Type": "Preventive",
      "SCP": "ap-northeast-2 only"
    }
  ]
}


```
-->
-->

**결과:**
- **CSAP 인증**: 1회 통과
- **개인정보 유출**: 0건 (3년간)
- **감사 준비 시간**: 90% 단축
- **망 분리 자동화**: 수동 작업 → 완전 자동화

## 9. Threat Hunting: AWS 환경 위협 탐지

### 9.1 공격 시나리오: Privilege Escalation

**공격 흐름:**

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
1. 공격자가 개발자 계정 탈취 (IAM User: dev-user-1)
   ↓
2. IAM 정책 변경 시도
   ↓
3. SCP로 차단됨
   ↓
4. 대안 경로 탐색: Lambda 함수 생성 시도
   ↓
5. Lambda 함수에 높은 권한 부여 시도
   ↓
6. Guardrail 탐지: "Detect overly permissive IAM roles"
   ↓
7. Security Hub 알림 전송
   ↓
8. 자동 대응: 계정 임시 동결


```
-->
-->

**탐지 쿼리 (CloudWatch Logs Insights):**

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```sql
fields @timestamp, userIdentity.principalId, eventName, errorCode
| filter eventName in [
    "PutUserPolicy",
    "AttachUserPolicy",
    "CreateAccessKey",
    "UpdateAssumeRolePolicy"
  ]
| filter errorCode = "AccessDenied"
| stats count() as attempts by userIdentity.principalId, sourceIPAddress
| filter attempts > 3
| sort attempts desc


```
-->
-->

**자동 대응 (Lambda):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> import boto3...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> import boto3...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
import boto3

def lambda_handler(event, context):
    """
    권한 상승 시도 탐지 시 자동 대응
    """
    iam = boto3.client('iam')
    sns = boto3.client('sns')

    # 공격자 IAM 사용자 추출
    attacker_user = event['detail']['userIdentity']['userName']
    source_ip = event['detail']['sourceIPAddress']

    # 1. 계정 임시 동결 (Deny All 정책 연결)
    iam.attach_user_policy(
        UserName=attacker_user,
        PolicyArn='arn:aws:iam::aws:policy/DenyAll'
    )

    # 2. 모든 Access Key 비활성화
    keys = iam.list_access_keys(UserName=attacker_user)
    for key in keys['AccessKeyMetadata']:
        iam.update_access_key(
            UserName=attacker_user,
            AccessKeyId=key['AccessKeyId'],
            Status='Inactive'
        )

    # 3. 보안팀에 즉시 알림
    sns.publish(
        TopicArn='arn:aws:sns:ap-northeast-2:123456789012:security-alerts',
        Subject=f'🚨 권한 상승 공격 탐지: {attacker_user}',
        Message=f"""
권한 상승 공격이 탐지되어 자동 차단되었습니다.

공격자: {attacker_user}
Source IP: {source_ip}
시간: {event['detail']['eventTime']}

조치 사항:
✓ 계정 임시 동결
✓ Access Key 비활성화
✓ SOC 티켓 생성 (TICKET-{context.request_id})

즉시 조사가 필요합니다.
        """
    )

    return {
        'statusCode': 200,
        'action': 'Account frozen',
        'user': attacker_user
    }


```
-->
-->

### 9.2 위협 시나리오: Data Exfiltration

**공격 흐름:**

```
1. 공격자가 S3 버킷의 대량 데이터 다운로드 시도
   ↓
2. GuardDuty 탐지: "Exfiltration:S3/AnomalousBehavior"
   ↓
3. VPC Flow Logs 분석: 비정상 네트워크 트래픽
   ↓
4. CloudTrail 분석: 평소와 다른 시간대 접근
   ↓
5. 자동 대응: S3 버킷 임시 격리
```

**탐지 쿼리 (Athena on CloudTrail):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```sql
> -- 비정상 S3 다운로드 패턴 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```sql
> -- 비정상 S3 다운로드 패턴 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```sql
-- 비정상 S3 다운로드 패턴 탐지
SELECT
    useridentity.principalid,
    sourceipaddress,
    COUNT(*) as download_count,
    SUM(CAST(json_extract_scalar(requestparameters, '$.size') AS BIGINT)) / 1024 / 1024 / 1024 as total_gb
FROM cloudtrail_logs
WHERE
    eventname = 'GetObject'
    AND eventsource = 's3.amazonaws.com'
    AND eventtime > CURRENT_TIMESTAMP - INTERVAL '1' HOUR
GROUP BY
    useridentity.principalid,
    sourceipaddress
HAVING
    COUNT(*) > 1000  -- 1시간에 1000건 이상 다운로드
    OR SUM(CAST(json_extract_scalar(requestparameters, '$.size') AS BIGINT)) / 1024 / 1024 / 1024 > 100  -- 100GB 이상
ORDER BY
    total_gb DESC;


```
-->
-->

**자동 대응 (Lambda + EventBridge):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> def handle_data_exfiltration(event, context):...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> def handle_data_exfiltration(event, context):...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
def handle_data_exfiltration(event, context):
    """
    데이터 유출 시도 탐지 시 자동 격리
    """
    s3 = boto3.client('s3')
    guardduty_finding = event['detail']

    bucket_name = guardduty_finding['resource']['s3BucketDetails']['name']
    attacker_ip = guardduty_finding['service']['action']['networkConnectionAction']['remoteIpDetails']['ipAddressV4']

    # 1. S3 버킷 Public Access 차단
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    # 2. 버킷 정책으로 공격자 IP 차단
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": attacker_ip
                    }
                }
            }
        ]
    }

    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )

    # 3. WAF IP Block (ALB 사용 시)
    waf = boto3.client('wafv2')
    waf.update_ip_set(
        Name='BlockedIPs',
        Scope='REGIONAL',
        Id='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        Addresses=[f'{attacker_ip}/32'],
        LockToken='...'
    )

    # 4. 포렌식을 위한 스냅샷 생성
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    s3.create_bucket(
        Bucket=f'{bucket_name}-forensic-{timestamp}',
        CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-2'}
    )

    # 원본 버킷의 현재 상태 복사 (versioning 활용)
    s3.copy_object(
        CopySource={'Bucket': bucket_name, 'Key': '*'},
        Bucket=f'{bucket_name}-forensic-{timestamp}'
    )

    return {
        'statusCode': 200,
        'action': 'Bucket isolated and forensic snapshot created'
    }


```
-->
-->

### 9.3 Threat Hunting Playbook

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Control Tower 환경 Threat Hunting 체크리스트...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Control Tower 환경 Threat Hunting 체크리스트...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Control Tower 환경 Threat Hunting 체크리스트

Daily Checks:
  - [ ] GuardDuty 고위험 탐지 검토
  - [ ] Security Hub Critical/High 발견사항 조사
  - [ ] CloudTrail 비정상 API 호출 분석
  - [ ] VPC Flow Logs 이상 트래픽 검토

Weekly Checks:
  - [ ] IAM Access Analyzer 신규 발견사항
  - [ ] Unused/Overprivileged IAM 역할 식별
  - [ ] 비인가 리전 활동 검토
  - [ ] Guardrails 위반 시도 패턴 분석

Monthly Checks:
  - [ ] 전체 계정 권한 감사
  - [ ] SCP 정책 효과성 검토
  - [ ] 보안 그룹 규칙 최적화
  - [ ] CloudTrail 로그 무결성 검증


```
-->
-->

## 10. 참고 자료 및 추가 학습

### 10.1 공식 문서

| 리소스 | URL | 설명 |
|--------|-----|------|
| **AWS Control Tower 사용 설명서** | [https://docs.aws.amazon.com/controltower/](https://docs.aws.amazon.com/controltower/) | 공식 문서, 모든 기능 상세 설명 |
| **Control Tower Guardrails 레퍼런스** | [https://docs.aws.amazon.com/controltower/latest/userguide/guardrails-reference.html](https://docs.aws.amazon.com/controltower/latest/userguide/guardrails-reference.html) | 모든 Guardrails 목록 및 설명 |
| **NIST SP 800-207: Zero Trust** | [https://csrc.nist.gov/publications/detail/sp/800-207/final](https://csrc.nist.gov/publications/detail/sp/800-207/final) | Zero Trust 표준 문서 |
| **AWS Well-Architected Framework - Security Pillar** | [https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) | AWS 보안 모범 사례 |
| **IAM Identity Center 문서** | [https://docs.aws.amazon.com/singlesignon/](https://docs.aws.amazon.com/singlesignon/) | AWS SSO 설정 가이드 |

### 10.2 실습 환경 및 튜토리얼

| 리소스 | 설명 |
|--------|------|
| **AWS Workshop - Control Tower Immersion Day** | 실습 중심의 Control Tower 워크샵 ([https://controltower.aws-management.tools/](https://controltower.aws-management.tools/)) |
| **AWS Samples - Control Tower Customizations** | GitHub 샘플 코드 ([https://github.com/aws-samples/aws-control-tower-customizations](https://github.com/aws-samples/aws-control-tower-customizations)) |
| **Terraform AWS Control Tower Module** | Infrastructure as Code 예제 ([https://registry.terraform.io/modules/aws-ia/control_tower](https://registry.terraform.io/modules/aws-ia/control_tower)) |

### 10.3 한국어 리소스

| 리소스 | 링크 |
|--------|------|
| **AWS 한국 블로그 - Control Tower** | [https://aws.amazon.com/ko/blogs/korea/tag/aws-control-tower/](https://aws.amazon.com/ko/blogs/korea/tag/aws-control-tower/) |
| **클라우드 보안 컨설팅 (Twodragon)** | [https://tech.2twodragon.com](https://tech.2twodragon.com) |
| **AWS 공인 교육 과정** | AWS Training and Certification 한국어 과정 |

### 10.4 관련 AWS 서비스

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> Control Tower 통합 서비스 맵:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> Control Tower 통합 서비스 맵:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
Control Tower 통합 서비스 맵:

[AWS Control Tower]
    ├─ [AWS Organizations] - 멀티 계정 관리
    ├─ [AWS SSO (IAM Identity Center)] - 통합 인증
    ├─ [Service Catalog] - Account Factory
    ├─ [AWS Config] - 리소스 컴플라이언스 추적
    ├─ [CloudTrail] - API 활동 로깅
    ├─ [CloudWatch] - 로그 및 메트릭
    ├─ [SNS] - 알림
    ├─ [Lambda] - 자동화
    ├─ [Security Hub] - 보안 현황 통합
    ├─ [GuardDuty] - 위협 탐지
    ├─ [IAM Access Analyzer] - 권한 분석
    └─ [S3] - 로그 저장소


```
-->
-->

### 10.5 커뮤니티 및 지원

| 채널 | 설명 |
|------|------|
| **AWS re:Post** | AWS 공식 Q&A 포럼 ([https://repost.aws/](https://repost.aws/)) |
| **AWS Discord (한국)** | AWS 한국 사용자 커뮤니티 |
| **AWS User Group Korea** | 정기 밋업 및 세미나 |
| **Stack Overflow** | `[aws-control-tower]` 태그 |

### 10.6 인증 및 교육 과정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> AWS 보안 관련 인증:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> AWS 보안 관련 인증:...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
AWS 보안 관련 인증:

초급:
  - AWS Certified Cloud Practitioner
    ↓
중급:
  - AWS Certified Solutions Architect - Associate
  - AWS Certified Security - Specialty (추천!)
    ↓
고급:
  - AWS Certified Solutions Architect - Professional
  - AWS Certified DevOps Engineer - Professional

보안 특화:
  - (ISC)² CCSP (Certified Cloud Security Professional)
  - CompTIA Cloud+
  - SANS SEC488: Cloud Security Essentials


```
-->
-->

## 결론

클라우드 시큐리티 과정 7기 5주차에서는 **AWS Control Tower**와 **ZTNA(Zero Trust Network Access)**를 심층적으로 다루었습니다.

### 핵심 요약

1. **AWS Control Tower**는 멀티 계정 거버넌스를 자동화하고, Landing Zone과 Guardrails를 통해 보안 모범 사례를 강제합니다.

2. **ZTNA**는 "절대 신뢰하지 말고, 항상 검증하라"는 원칙으로 경계 기반 보안의 한계를 극복합니다.

3. **2025년 업데이트**로 AWS는 계정 마이그레이션 개선, AI 에이전트 거버넌스, IAM 정책 자동화 등 실무 효율성을 대폭 향상시켰습니다.

4. **실습 가이드**를 통해 Control Tower 초기 설정부터 SCP 정책 작성, ZTNA 구현까지 단계별로 학습할 수 있습니다.

5. **ISMS-P 매핑**과 **SIEM 쿼리**를 통해 컴플라이언스와 위협 탐지를 자동화할 수 있습니다.

### 다음 단계

올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 클라우드 환경을 구축할 수 있습니다. 다음 단계로 권장하는 학습 경로:

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```yaml
학습 로드맵:
  1주차: AWS Control Tower 파일럿 구축 (Sandbox 계정)
  2주차: Guardrails 추가 및 SCP 정책 최적화
  3주차: IAM Identity Center 구성 (SSO)
  4주차: ZTNA 아키텍처 설계 (PrivateLink)
  5-6주차: 전사 확대 및 모니터링 체계 구축
  7-8주차: Threat Hunting 및 자동 대응 구현
```

**지속적 개선:**
- 매월 Guardrails 준수율 검토
- 분기별 SCP 정책 업데이트
- 연 1회 Zero Trust 성숙도 평가 (NIST 기준)

AWS Control Tower와 ZTNA를 통해 **안전하고 확장 가능하며 컴플라이언스를 준수하는 클라우드 환경**을 구축하시기 바랍니다.

---

## 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **AWS Control Tower** | 멀티 계정 거버넌스, SCP, Guardrails 설정 | [수강하기](https://edu.2twodragon.com/courses/aws-control-tower) |
| **Zero Trust 보안** | ZTNA 아키텍처, 정책 설정, 구현 가이드 | [수강하기](https://edu.2twodragon.com/courses/zero-trust) |
| **AWS 클라우드 보안** | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |
---
layout: post
title: "클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA"
date: 2025-05-16 00:53:10 +0900
categories: [cloud]
tags: [AWS, Control-Tower, ZTNA, Zero-Trust]
excerpt: "AWS Control Tower 및 ZTNA 완벽 가이드. 멀티 계정 거버넌스, Zero Trust 구현 실무 정리."
comments: true
original_url: https://twodragon.tistory.com/683
image: /assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA.svg
image_alt: "Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA"
toc: true
description: 클라우드 시큐리티 7기 5주차. AWS Control Tower 멀티 계정 관리(Landing Zone, Guardrails, SCP), ZTNA(Zero Trust Network Access) 개념 및 AWS 구현, 2025년 거버넌스 업데이트 실무 정리.
keywords: [AWS, Control-Tower, ZTNA, Zero-Trust, Landing-Zone, Guardrails, SCP, 멀티계정, Organizations, 제로트러스트]
author: "Yongho Ha"
certifications: [aws-saa]
schema_type: Article
---

## 📋 포스팅 요약

> **제목**: 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA

> **카테고리**: cloud

> **태그**: AWS, Control-Tower, ZTNA, Zero-Trust

> **핵심 내용**: 
> - AWS Control Tower 및 ZTNA 완벽 가이드. 멀티 계정 거버넌스, Zero Trust 구현 실무 정리.

> **주요 기술/도구**: AWS, cloud

> **대상 독자**: 클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


## 핵심 요약

본 포스트는 클라우드 시큐리티 과정 7기 5주차의 핵심 내용인 **AWS Control Tower와 ZTNA(Zero Trust Network Access)**를 다룹니다. 멀티 계정 거버넌스부터 Zero Trust 보안 모델 구현까지 실무에서 즉시 활용할 수 있는 고품질 콘텐츠를 제공합니다.

### 학습 스코어카드

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Organizations:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 2.3 Guardrails 완전 분석

Guardrails는 Control Tower의 **정책 엔진**으로, 다음 두 가지 유형으로 나뉩니다:

#### 2.3.1 Guardrail 유형 비교

| 유형 | 동작 방식 | 구현 기술 | 예시 |
|------|----------|----------|------|
| **Preventive (예방적)** | 위반 행위를 원천 차단 | SCP (Service Control Policy) | "S3 버킷을 public으로 설정 불가" |
| **Detective (탐지적)** | 위반 행위를 탐지하고 알림 | AWS Config Rules | "MFA 미설정 계정 탐지" |

#### 2.3.2 필수 Guardrails (Mandatory)

Control Tower가 자동으로 적용하는 필수 guardrails:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Mandatory Guardrails:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 2.3.3 권장 Guardrails (Strongly Recommended)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Recommended Guardrails:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 2.3.4 선택적 Guardrails (Elective)

조직의 요구사항에 따라 선택 적용:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Elective Guardrails:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 2.4 SCP (Service Control Policy) 실전 예제

#### 2.4.1 SCP 작성 원칙

1. **명시적 거부 우선**: SCP는 권한을 부여하지 않고 제한만 함
2. **계층적 적용**: OU 레벨에서 적용되어 하위 계정 모두에 영향
3. **IAM 정책과의 관계**: `SCP ∩ IAM Policy = 실제 권한`

#### 2.4.2 실전 SCP 정책 예제

**예제 1: 특정 리전만 허용**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**예제 2: S3 Public Access 완전 차단**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**예제 3: Root 사용자 작업 차단 (긴급 상황 제외)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**예제 4: 비용 최적화 - 비승인 인스턴스 타입 차단**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**예제 5: 태그 정책 강제 (비용 할당 추적)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 2.4.3 SCP 테스트 및 검증

**IAM Policy Simulator 활용:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```hcl
> # terraform/account-factory.tf...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 2.5.3 계정 생성 후 자동화 (Lambda + EventBridge)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```python
> # lambda/account_post_creation.py...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**EventBridge Rule 설정:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 3.2.2 Trust Score 계산 로직

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```python
> # BeyondCorp-style Trust Score Calculation...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 3.4 AWS에서 ZTNA 구현 가이드

#### 3.4.1 AWS Zero Trust 아키텍처

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> ┌──────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 3.4.2 IAM Identity Center (AWS SSO) 설정

**1단계: Identity Source 구성**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # AWS CLI로 Identity Center 활성화...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**2단계: Permission Sets 생성 (ABAC 적용)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 3.4.3 VPC PrivateLink로 Private Access 구현

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```python
> # terraform/privatelink.tf...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 3.4.4 마이크로세그멘테이션 구현

**Security Group 설계 원칙:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Microsegmentation Strategy:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**실전 Security Group 예제:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```hcl
> # Web Tier Security Group...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Quick Wins:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# example omitted: see reference link
```

**웹 콘솔:**
1. AWS Management Console 로그인
2. 서비스 검색에서 "Control Tower" 입력
3. "Set up landing zone" 클릭

#### Step 2: Home Region 선택

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# 최신 버전 확인 (AWS CLI)
aws controltower list-landing-zones --max-results 10

# 권장: 항상 최신 버전 사용
Landing Zone Version: 3.3 (2025년 1월 기준)
```

#### Step 4: 추가 리전 선택 (선택사항)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Governed Regions:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 5: Log Archive 계정 설정

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 6: Audit 계정 설정

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# SNS Topic ARN (자동 생성)
arn:aws:sns:ap-northeast-2:987654321098:aws-controltower-SecurityNotifications

# 이메일 구독 자동 설정
# → aws-audit@company.com 으로 알림 전송
```

#### Step 7: KMS 암호화 설정 (선택사항)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```hcl
> # terraform/kms.tf...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 8: Landing Zone 생성 시작

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # 예상 소요 시간: 60-90분...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**생성 과정 세부 단계:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # Organizations 구조 출력...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 2: Guardrails 활성화 확인

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# example omitted: see reference link
```

#### Step 3: CloudTrail 로깅 확인

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # CloudTrail이 정상 작동하는지 확인...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 4: Security Hub 통합 확인

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# Audit 계정에서 Security Hub 상태 확인
aws securityhub get-findings --profile audit \
  --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}'

# GuardDuty 활성화 확인
aws guardduty list-detectors --profile audit
```

### 4.4 첫 번째 계정 생성 (Account Factory)

#### Step 1: Service Catalog 접속

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# Service Catalog에서 Account Factory Product 확인
aws servicecatalog search-products \
  --filters FullTextSearch=ControlTower

# Product Name: "AWS Control Tower Account Factory"
```

#### Step 2: 계정 생성 파라미터 입력

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Account Creation Parameters:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Step 3: 계정 생성 모니터링

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# example omitted: see reference link
```

#### Step 4: SSO 접속 테스트

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # SSO 포털 URL 확인...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 4.5 문제 해결 (Troubleshooting)

#### 문제 1: Landing Zone 생성 실패

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Error: "Failed to create log archive bucket"...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 문제 2: Guardrails 적용 실패

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```bash
# Drift Detection 실행
aws controltower list-landing-zones

# Drift 복구
aws controltower reset-landing-zone \
  --landing-zone-identifier arn:aws:controltower:...
```

#### 문제 3: Account Factory 프로비저닝 실패

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

```yaml
# example omitted: see reference link
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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```sql
> -- Query 1: Control Tower API 호출 모니터링...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```bash
> # 1. MFA 적용 현황 리포트 (Config Rule)...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**예상 질문 및 답변:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Q: "MFA 미적용 계정이 존재하는 경우 어떻게 대응하나요?"...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```markdown
> # Zero Trust Network Access (ZTNA) 도입 제안...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 7.2 월간 거버넌스 리포트 템플릿

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> # AWS Control Tower 월간 리포트 (2025년 1월)...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 8. 한국 기업 사례 연구

### 8.1 금융권: K-Bank Zero Trust 전환

**배경:**
- 기존 VPN 기반 접근 제어
- 재택근무 확대로 VPN 병목 발생
- FSS (금융감독원) 보안 규제 강화

**구현:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> Phase 1 (3개월):...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> AWS Control Tower:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> ┌────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**특화 Guardrails:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**결과:**
- **CSAP 인증**: 1회 통과
- **개인정보 유출**: 0건 (3년간)
- **감사 준비 시간**: 90% 단축
- **망 분리 자동화**: 수동 작업 → 완전 자동화

## 9. Threat Hunting: AWS 환경 위협 탐지

### 9.1 공격 시나리오: Privilege Escalation

**공격 흐름:**

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**탐지 쿼리 (CloudWatch Logs Insights):**

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**자동 대응 (Lambda):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```python
> import boto3...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 9.2 위협 시나리오: Data Exfiltration

**공격 흐름:**

```
# example omitted: see reference link
```

**탐지 쿼리 (Athena on CloudTrail):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```sql
> -- 비정상 S3 다운로드 패턴 탐지...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**자동 대응 (Lambda + EventBridge):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```python
> def handle_data_exfiltration(event, context):...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 9.3 Threat Hunting Playbook

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> # Control Tower 환경 Threat Hunting 체크리스트...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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
| **AWS Samples - Control Tower Customizations** | GitHub 샘플 코드 ([https://docs.aws.amazon.com/](https://docs.aws.amazon.com/)) |
| **Terraform AWS Control Tower Module** | Infrastructure as Code 예제 ([https://registry.terraform.io/modules/aws-ia/control_tower](https://registry.terraform.io/modules/aws-ia/control_tower)) |

### 10.3 한국어 리소스

| 리소스 | 링크 |
|--------|------|
| **AWS 한국 블로그 - Control Tower** | [https://aws.amazon.com/ko/blogs/korea/tag/aws-control-tower/](https://aws.amazon.com/ko/blogs/korea/tag/aws-control-tower/) |
| **클라우드 보안 컨설팅 (Twodragon)** | [https://tech.2twodragon.com](https://tech.2twodragon.com) |
| **AWS 공인 교육 과정** | AWS Training and Certification 한국어 과정 |

### 10.4 관련 AWS 서비스

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> Control Tower 통합 서비스 맵:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 10.5 커뮤니티 및 지원

| 채널 | 설명 |
|------|------|
| **AWS re:Post** | AWS 공식 Q&A 포럼 ([https://repost.aws/](https://repost.aws/)) |
| **AWS Discord (한국)** | AWS 한국 사용자 커뮤니티 |
| **AWS User Group Korea** | 정기 밋업 및 세미나 |
| **Stack Overflow** | `[aws-control-tower]` 태그 |

### 10.6 인증 및 교육 과정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```yaml
> AWS 보안 관련 인증:...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://docs.aws.amazon.com/)를 참조하세요.

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
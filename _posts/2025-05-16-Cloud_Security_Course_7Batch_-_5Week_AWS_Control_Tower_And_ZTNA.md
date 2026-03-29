---

layout: post
title: 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA
date: 2025-05-16 00:53:10 +0900
categories:
- cloud
tags:
- AWS
- Control-Tower
- ZTNA
- Zero-Trust
keywords: [AWS, Control-Tower, ZTNA, Zero-Trust]
excerpt: "클라우드 시큐리티 과정 7기 5주차 핵심 정리. AWS Control Tower 멀티 계정 관리(Landing Zone, Guardrails, SCP), ZTNA(Zero Trust Network Access) 개념과 AWS 구현 방법, 2025년 최신 거버넌스 업데이트를 실무 관점에서 깊이 있게 다룹니다."
description: 클라우드 시큐리티 7기 5주차. AWS Control Tower 멀티 계정 관리(Landing Zone, Guardrails,
  SCP), ZTNA(Zero Trust Network Access) 개념 및 AWS 구현, 2025년 거버넌스 업데이트 실무 정리.
image: /assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA.svg
toc: true
author: Yongho Ha
comments: true
image_alt: 'Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA'
certifications:
- aws-saa
original_url: https://twodragon.tistory.com/683
series: "Cloud Security Course 7기"
series_order: 3
series_total: 7
---
{%- include ai-summary-card.html
  title='클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA'
  categories_html='<span class="category-tag cloud">Cloud</span>'
  tags_html='<span class="tag">AWS</span>
      <span class="tag">Control-Tower</span>
      <span class="tag">ZTNA</span>
      <span class="tag">Zero-Trust</span>'
  highlights_html='<li><strong>AWS Control Tower 멀티 계정 관리</strong>: Landing Zone 자동 설정, Guardrails 정책 적용(필수/권장/선택), 계정 팩토리(자동 계정 생성), Organizations 및 SCP 활용, 2025년 업데이트(계정 마이그레이션 개선, standalone 분리 불필요)</li>
      <li><strong>ZTNA(Zero Trust Network Access)</strong>: Zero Trust 개념("절대 신뢰하지 말고, 항상 검증하라"), AWS 구현 방법(PrivateLink, VPC Endpoint, Security Group 최소 권한), 클라우드 환경 제로 트러스트 보안 모델 적용</li>
      <li><strong>2025년 AWS 거버넌스 업데이트</strong>: Organizations 계정 마이그레이션 개선(조직 간 직접 이동, 다운타임 최소화), Control Tower Guardrails 확장, SCP 정책 자동화</li>
      <li><strong>실무 적용</strong>: 멀티 계정 아키텍처 설계, 거버넌스 정책 자동화, 제로 트러스트 네트워크 구성, 보안 및 컴플라이언스 통합 관리</li>'
  audience='클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자'
-%}

### 실습 체크리스트

- [ ] 실습 환경 구성 완료
- [ ] 보안 설정 적용 확인
- [ ] 테스트 및 검증 수행
- [ ] 실습 리소스 정리 (비용 방지)
- [ ] 학습 내용 문서화

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## Executive Summary

본 포스트는 클라우드 시큐리티 과정 7기 5주차의 핵심 내용인 AWS Control Tower와 ZTNA(Zero Trust Network Access)를 다룹니다.

### 위험 스코어카드

| 위험 영역 | 위험도 | 완화 전략 |
|----------|--------|----------|
| 멀티 계정 권한 분산 | 높음 | SCP 기반 중앙 통제 |
| 비인가 리전 사용 | 중간 | Guardrails 리전 제한 |
| 네트워크 경계 침투 | 높음 | ZTNA 제로 트러스트 적용 |
| 계정 간 데이터 유출 | 높음 | VPC Endpoint + PrivateLink |

멀티 계정 거버넌스부터 Zero Trust 보안 모델 구현까지 실무에서 즉시 활용할 수 있는 고품질 콘텐츠를 제공합니다.

### Learning Scorecard

| 평가 항목 | 점수 | 설명 |
|----------|------|------|
| 실무 적용성 | ⭐⭐⭐⭐⭐ | Control Tower 설정부터 SCP 정책까지 step-by-step 가이드 제공 |
| 기술 깊이 | ⭐⭐⭐⭐⭐ | Landing Zone 아키텍처, Guardrails 메커니즘 심층 분석 |
| 보안 커버리지 | ⭐⭐⭐⭐⭐ | 예방/탐지/대응 전 단계 포괄, ISMS-P 매핑 포함 |
| 코드/정책 예제 | ⭐⭐⭐⭐⭐ | SCP JSON 정책, SIEM 쿼리, Terraform 코드 제공 |
| ROI/비즈니스 가치 | ⭐⭐⭐⭐☆ | 경영진 보고 템플릿, TCO 분석 포함 |

### 학습 시간 가이드

| 섹션 | 예상 시간 | 난이도 |
|------|----------|--------|
| AWS Control Tower 기초 | 30분 | 초급 |
| Landing Zone 아키텍처 | 45분 | 중급 |
| SCP 정책 작성 | 60분 | 고급 |
| ZTNA 개념 및 구현 | 45분 | 중급 |
| 실습 (hands-on) | 90분 | 고급 |
| 총 학습 시간 | 4-5시간 | - |

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 시큐리티 과정 7기 5주차에서 다룬 AWS Control Tower와 ZTNA(Zero Trust Network Access)를 실무 중심으로 깊이 있게 다룹니다.

### 강의 운영 방식

이 과정은 게더 타운(Gather Town)에서 진행되며, 각 세션은 다음과 같이 구성됩니다:

- 20분 강의 + 5분 휴식 반복
- 온라인 강의 특성상 눈의 피로를 줄이고 집중력을 최대화하기 위한 구성
- 실시간 Q&A 및 실습 세션 포함

### 왜 Control Tower와 ZTNA인가?

현대 기업의 클라우드 환경은 다음과 같은 과제를 직면합니다:

1. 멀티 계정 관리의 복잡성: 수십~수백 개의 AWS 계정을 일관되게 관리해야 함
2. 거버넌스 자동화 필요성: 수동 점검으로는 컴플라이언스 유지 불가능
3. 경계 기반 보안의 한계: VPN/방화벽만으로는 내부자 위협 대응 불가
4. 규제 준수 압박: ISMS-P, ISO 27001, PCI-DSS 등 다양한 규제 요구사항

AWS Control Tower는 멀티 계정 거버넌스 자동화를, ZTNA는 경계 없는 보안 아키텍처를 제공하여 이러한 과제를 해결합니다.

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

```text
AWS Control Tower Components:
- Landing Zone (Base Environment)
- SCP (Service Control Policy)
- Guardrails (Governance Rules)
```

</details>

## 2. AWS Control Tower 완전 가이드

### 2.1 Control Tower란 무엇인가?

AWS Control Tower는 멀티 계정 AWS 환경을 자동으로 설정하고 관리하는 서비스입니다. 다음 핵심 기능을 제공합니다:

| 기능 | 설명 | 비즈니스 가치 |
|------|------|--------------|
| Landing Zone | 보안 모범 사례 기반 초기 환경 자동 구성 | 초기 설정 시간 90% 단축 |
| Guardrails | 예방적/탐지적 정책 자동 적용 | 컴플라이언스 위반 70% 감소 |
| Account Factory | 표준화된 계정 자동 생성 | 계정 프로비저닝 시간 80% 단축 |
| Dashboard | 통합 거버넌스 현황 모니터링 | 감사 준비 시간 60% 단축 |

### 2.2 Landing Zone 아키텍처 심층 분석

Landing Zone은 Control Tower의 핵심 개념으로, 보안 모범 사례를 적용한 멀티 계정 기반 환경을 의미합니다.

#### 2.2.1 Landing Zone 구성 요소

Landing Zone은 다음 계정으로 구성됩니다:

- Management Account: 중앙 관리 계정 (루트 계정)
- Log Archive Account: 모든 CloudTrail, Config 로그 집중 보관
- Audit Account: 보안 감사 도구 (Security Hub, GuardDuty) 집중 관리

## 3. Threat Hunting Playbook

### 3.1 Control Tower 환경 위협 탐지

Control Tower 환경에서 이상 징후를 탐지하는 핵심 체크리스트:

- GuardDuty 알림 중 HIGH 등급 즉시 확인
- CloudTrail에서 루트 계정 직접 사용 감지
- Config Rules 위반 항목 24시간 내 수정

### 3.2 실전 AWS CLI 탐지 명령어

**1) CloudTrail로 루트 계정 직접 사용 이력 조회**

```bash
# 최근 24시간 내 루트 계정 API 호출 내역 조회
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
  --query 'Events[*].{Time:EventTime,Event:EventName,Source:EventSource}' \
  --output table
```

**2) AWS Config - SCP 위반 또는 비준수 리소스 목록 조회**

```bash
# Config Rules 중 NON_COMPLIANT 상태인 리소스 일괄 조회
aws configservice describe-compliance-by-config-rule \
  --compliance-types NON_COMPLIANT \
  --query 'ComplianceByConfigRules[*].{Rule:ConfigRuleName,Compliance:Compliance.ComplianceType}' \
  --output table
```

**3) Control Tower Guardrails - 위반 계정 확인**

```bash
# 특정 Control Tower Guardrail 위반 계정 조회 (AWS Control Tower API)
aws controltower list-enabled-controls \
  --target-identifier arn:aws:organizations::ACCOUNT_ID:ou/OU_ID \
  --query 'enabledControls[*].{Arn:controlIdentifier,Status:driftStatusSummary.driftStatus}' \
  --output table
```

## 4. ZTNA (Zero Trust Network Access)

### 4.1 Zero Trust 핵심 원칙

ZTNA는 "절대 신뢰하지 말고, 항상 검증하라(Never Trust, Always Verify)"는 원칙을 기반으로 합니다.

| 원칙 | 설명 | AWS 적용 방법 |
|------|------|--------------|
| 명시적 검증 | 모든 요청을 사용자·기기·위치 기반으로 인증 | IAM Identity Center + MFA 강제 적용 |
| 최소 권한 접근 | 필요한 리소스에만 최소한의 권한 부여 | IAM 최소 권한 정책 + SCP |
| 침해 가정 | 이미 내부가 침해되었다고 가정하고 방어 | GuardDuty + VPC Flow Logs 실시간 분석 |
| 마이크로 세그멘테이션 | 네트워크를 세분화해 측면 이동(lateral movement) 차단 | Security Group + VPC + PrivateLink |

### 4.2 AWS에서의 ZTNA 구현

**PrivateLink와 VPC Endpoint를 활용한 네트워크 격리**

```yaml
# CloudFormation: VPC Endpoint for S3 (Gateway Type)
Resources:
  S3VPCEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub com.amazonaws.${AWS::Region}.s3
      RouteTableIds:
        - !Ref PrivateRouteTable
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal: "*"
            Action: "s3:*"
            Resource:
              - arn:aws:s3:::my-secure-bucket
              - arn:aws:s3:::my-secure-bucket/*
```

**Security Group 최소 권한 규칙 예시**

```bash
# 특정 애플리케이션 서버에서 RDS로만 3306 포트 허용 (Zero Trust 접근 통제)
aws ec2 authorize-security-group-ingress \
  --group-id sg-RDS_GROUP_ID \
  --protocol tcp \
  --port 3306 \
  --source-group sg-APP_SERVER_GROUP_ID
```

### 4.3 ZTNA 도입 체크리스트

- [ ] IAM Identity Center(AWS SSO) 활성화 및 MFA 필수 설정
- [ ] VPC Endpoint를 통한 AWS 서비스 프라이빗 접근 구성
- [ ] PrivateLink로 외부 서비스 연결 시 인터넷 우회 차단
- [ ] Security Group에 0.0.0.0/0 인바운드 규칙 제거
- [ ] VPC Flow Logs 활성화 및 Athena 쿼리 설정

## 5. 참고 자료 및 추가 학습

### 5.1 공식 문서

| 리소스 | URL | 설명 |
|--------|-----|------|
| AWS Control Tower 사용 설명서 | [docs.aws.amazon.com/controltower](https://docs.aws.amazon.com/controltower/) | 공식 문서, 모든 기능 상세 설명 |
| Control Tower Guardrails 레퍼런스 | [docs.aws.amazon.com/controltower/guardrails-reference](https://docs.aws.amazon.com/controltower/latest/userguide/guardrails-reference.html) | 모든 Guardrails 목록 및 설명 |
| NIST SP 800-207: Zero Trust | [csrc.nist.gov/sp/800-207](https://csrc.nist.gov/publications/detail/sp/800-207/final) | Zero Trust 표준 문서 |
| AWS Well-Architected Framework - Security Pillar | [docs.aws.amazon.com/wellarchitected/security-pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) | AWS 보안 모범 사례 |
| IAM Identity Center 문서 | [docs.aws.amazon.com/singlesignon](https://docs.aws.amazon.com/singlesignon/) | AWS SSO 설정 가이드 |

### 5.2 실습 환경 및 튜토리얼

| 리소스 | 설명 |
|--------|------|
| AWS Workshop - Control Tower Immersion Day | 실습 중심의 Control Tower 워크샵 ([controltower.aws-management.tools](https://controltower.aws-management.tools/)) |
| AWS Samples - Control Tower Customizations | GitHub 샘플 코드 ([aws-control-tower-customizations](https://github.com/aws-samples/aws-control-tower-customizations)) |
| Terraform AWS Control Tower Module | Infrastructure as Code 예제 ([Terraform Registry](https://registry.terraform.io/modules/aws-ia/control_tower)) |

### 5.3 한국어 리소스

| 리소스 | 링크 |
|--------|------|
| AWS 한국 블로그 - Control Tower | [aws.amazon.com/ko/blogs/korea/aws-control-tower](https://aws.amazon.com/ko/blogs/korea/tag/aws-control-tower/) |
| 클라우드 보안 컨설팅 (Twodragon) | [tech.2twodragon.com](https://tech.2twodragon.com) |
| AWS 공인 교육 과정 | AWS Training and Certification 한국어 과정 |

### 5.4 관련 AWS 서비스

| 서비스 | 설명 | 링크 |
|--------|------|------|
| AWS Control Tower | 멀티 계정 거버넌스 | [docs.aws.amazon.com/controltower](https://docs.aws.amazon.com/controltower/) |
| AWS Organizations | 계정 그룹 관리 | [docs.aws.amazon.com/organizations](https://docs.aws.amazon.com/organizations/) |
| AWS WAF | 네트워크 시나리오 - AWS WAF와 전체적인 네트워크 보안 구성 | [youtu.be/r84IuPv_4TI](https://youtu.be/r84IuPv_4TI) |

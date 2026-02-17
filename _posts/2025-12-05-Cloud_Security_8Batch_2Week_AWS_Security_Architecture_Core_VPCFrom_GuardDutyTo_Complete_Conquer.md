---
author: Twodragon
categories:
- cloud
category: cloud
certifications:
- aws-saa
comments: true
date: 2025-12-05 17:07:53 +0900
description: VPC, IAM, S3, GuardDuty 등 AWS 보안 아키텍처 핵심 구성요소와 2025년 re:Invent 신규 보안
  서비스를 실무 중심으로 완벽 정복하세요.
excerpt: VPC, IAM, S3, GuardDuty 등 AWS 보안 아키텍처와 2025년 신규 서비스 실무 완벽 정복
image: /assets/images/2025-12-05-Cloud_Security_8Batch_2Week_AWS_Security_Architecture_Core_VPCFrom_GuardDutyTo_Complete_Conquer.svg
image_alt: 'Cloud Security 8Batch 2Week: Complete Mastery of AWS Security Architecture
  Core from VPC to GuardDuty'
keywords:
- AWS
- VPC
- IAM
- GuardDuty
- Security-Architecture
- S3
- AWS보안
- 보안아키텍처
- IAM Policy
layout: post
original_url: https://twodragon.tistory.com/702
tags:
- AWS
- VPC
- GuardDuty
- Security-Architecture
title: '클라우드 시큐리티 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지 완벽 정복!'
toc: true
---

## 요약

- **핵심 요약**: VPC, IAM, S3, GuardDuty 등 AWS 보안 아키텍처와 2025년 신규 서비스 실무 완벽 정복
- **주요 주제**: 클라우드 시큐리티 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지 완벽 정복!
- **키워드**: AWS, VPC, GuardDuty, Security-Architecture

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지 완벽 정복!</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">VPC</span>
      <span class="tag">GuardDuty</span>
      <span class="tag">Security-Architecture</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>AWS 보안 아키텍처 핵심 구성요소: VPC 네트워크 격리, IAM 접근 제어, S3 데이터 보호, GuardDuty 위협 탐지</li>
      <li>2025년 AWS re:Invent 보안 발표: GuardDuty Extended Threat Detection, Security Hub 강화, IAM Policy Autopilot</li>
      <li>실무 보안 모범 사례 및 적용 전략</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS VPC, IAM, S3, GuardDuty</span>
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

## Executive Summary (경영진 요약)

### 보안 위험 스코어카드

| 보안 영역 | 현재 리스크 | 투자 우선순위 | 예상 ROI |
|---------|-----------|------------|---------|
| **네트워크 격리 (VPC)** | 🔴 높음 | 최우선 | 공격 표면 60% 축소 |
| **접근 제어 (IAM)** | 🟠 중간 | 높음 | 권한 오용 사고 75% 감소 |
| **데이터 보호 (S3)** | 🔴 높음 | 최우선 | 데이터 유출 위험 90% 감소 |
| **위협 탐지 (GuardDuty)** | 🟠 중간 | 높음 | 평균 탐지 시간 80% 단축 |

### 투자 효과 분석

| 항목 | 투자 비용 (월) | 예상 절감액 (연) | ROI |
|------|-------------|--------------|-----|
| VPC 네트워크 재설계 | ₩5,000,000 | ₩120,000,000 | 2,400% |
| IAM 정책 자동화 | ₩3,000,000 | ₩80,000,000 | 2,667% |
| S3 보안 강화 | ₩2,000,000 | ₩150,000,000 | 7,500% |
| GuardDuty 활성화 | ₩1,500,000 | ₩100,000,000 | 6,667% |

> **경영진 권고사항**: VPC 네트워크 격리와 S3 Public Access 차단을 최우선으로 진행하여 데이터 유출 위험을 90% 이상 감소시킬 것을 권고합니다.

## 서론

안녕하세요, Twodragon입니다. 클라우드 시큐리티 과정 8기 2주차에서는 AWS 보안 아키텍처의 핵심 구성요소인 **VPC, IAM, S3, GuardDuty**를 다뤘습니다. 네트워크 격리, 접근 제어, 데이터 보호, 위협 탐지까지 실무에 바로 적용 가능한 내용을 중심으로 진행되었습니다.

이번 주차에서는 각 서비스의 보안 모범 사례와 실무 적용 전략을 중심으로 다뤘으며, 2025년 AWS re:Invent에서 발표된 최신 보안 기능들도 함께 살펴봤습니다.

본 포스팅에서는 AWS 보안 아키텍처의 핵심 구성요소와 2025년 최신 보안 기능을 실무 중심으로 상세히 다룹니다.

<img src="{% raw %}{{ '/assets/images/2025-12-05-Cloud_Security_8Batch_2Week_AWS_Security_Architecture_Core_VPCFrom_GuardDutyTo_Complete_Conquer_image.png' | relative_url }}{% endraw %}" alt="Cloud Security 8Batch 2Week: Complete Mastery of AWS Security Architecture Core from VPC to GuardDuty" loading="lazy" class="post-image">

> **📌 핵심 요약**
>
> - **VPC**: 네트워크 격리 및 보안 설계를 통한 방어의 깊이 구현
> - **IAM**: 최소 권한 원칙과 역할 기반 접근 제어를 통한 세밀한 권한 관리
> - **S3**: 데이터 암호화 및 접근 제어를 통한 데이터 보호
> - **GuardDuty**: 지속적인 위협 탐지 및 자동 대응을 통한 보안 강화

<figure>
<img src="{% raw %}{{ '/assets/images/diagrams/diagram_vpc_security.png' | relative_url }}{% endraw %}" alt="AWS VPC Security Architecture Diagram" loading="lazy" class="post-image">
<figcaption>AWS VPC 보안 아키텍처 다이어그램 - Python diagrams로 생성</figcaption>
</figure>

## MITRE ATT&CK 매핑

### AWS 보안 서비스별 MITRE ATT&CK 커버리지

| MITRE ATT&CK Tactic | VPC | IAM | S3 | GuardDuty | 탐지/차단 |
|---------------------|-----|-----|----|-----------| ---------|
| **Initial Access** | ✓ | ✓ | - | ✓ | 탐지+차단 |
| **Persistence** | - | ✓ | - | ✓ | 탐지 |
| **Privilege Escalation** | - | ✓ | - | ✓ | 탐지 |
| **Defense Evasion** | ✓ | ✓ | - | ✓ | 탐지 |
| **Credential Access** | - | ✓ | - | ✓ | 탐지 |
| **Discovery** | ✓ | - | - | ✓ | 탐지 |
| **Lateral Movement** | ✓ | - | - | ✓ | 탐지+차단 |
| **Collection** | - | - | ✓ | ✓ | 탐지 |
| **Exfiltration** | ✓ | - | ✓ | ✓ | 탐지+차단 |
| **Impact** | ✓ | ✓ | ✓ | ✓ | 탐지 |

### 주요 공격 기법별 대응 전략

| MITRE ATT&CK 기법 | AWS 서비스 | 탐지 방법 | 대응 방안 |
|------------------|----------|---------|---------|
| **T1078 - Valid Accounts** | IAM, GuardDuty | CloudTrail + GuardDuty | MFA 강제, 이상 로그인 패턴 탐지 |
| **T1110 - Brute Force** | GuardDuty | GuardDuty UnauthorizedAccess | IP 기반 차단, WAF 룰 적용 |
| **T1190 - Exploit Public-Facing Application** | VPC, WAF | GuardDuty, WAF | Security Group 최소화, WAF 룰 |
| **T1530 - Data from Cloud Storage** | S3, GuardDuty | S3 Access Logs, GuardDuty | Public Access Block, 암호화 |
| **T1562 - Impair Defenses** | CloudTrail, Config | CloudTrail 로그 | 로그 무결성 검증, 삭제 방지 |

## 1. AWS 보안 아키텍처 핵심 구성요소

AWS 보안 아키텍처는 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다.

### 1.1 VPC: 네트워크 격리 및 보안 설계

<img src="{% raw %}{{ '/assets/images/diagrams/2025-12-05-Cloud_Security_8Batch_2Week_AWS_Security_Architecture_Core_VPCFrom_GuardDutyTo_Complete_Conquer/2025-12-05-Cloud_Security_8Batch_2Week_AWS_Security_Architecture_Core_VPCFrom_GuardDutyTo_Complete_Conquer_mermaid_chart_1.png' | relative_url }}{% endraw %}" alt="mermaid_chart_1" loading="lazy" class="post-image">

VPC(Virtual Private Cloud)는 AWS 리소스를 격리된 가상 네트워크에서 실행할 수 있게 해주는 핵심 서비스입니다.

#### 네트워크 분리 전략

| 서브넷 유형 | 설명 | 배치 리소스 | 보안 고려사항 |
|-----------|------|-----------|------------|
| **Public 서브넷** | 인터넷 게이트웨이를 통한 외부 접근 허용 | 웹 서버, 로드 밸런서 | 최소한의 포트만 개방, WAF 적용 |
| **Private 서브넷** | NAT 게이트웨이를 통한 아웃바운드만 허용 | 애플리케이션 서버, 데이터베이스 | 인바운드 트래픽 차단, VPC Endpoint 활용 |
| **Isolated 서브넷** | 인터넷 접근 완전 차단 | 데이터베이스, 백업 저장소 | 완전 격리, VPC Peering 또는 VPN만 허용 |

```bash
# VPC 생성 및 서브넷 구성 예시
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=security-vpc}]'

# Public 서브넷 생성
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1}]'

# Private 서브넷 생성
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.10.0/24 --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1}]'

# Security Group 생성 (최소 권한 원칙)
aws ec2 create-security-group --group-name web-sg --description "Web Server Security Group" --vpc-id vpc-xxx
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# GuardDuty 활성화
aws guardduty create-detector --enable
```

#### 보안 그룹 및 NACL 비교

| 항목 | Security Group | NACL |
|------|---------------|------|
| **작동 레벨** | 인스턴스 레벨 | 서브넷 레벨 |
| **상태 관리** | Stateful (연결 추적) | Stateless (연결 추적 없음) |
| **규칙 평가** | 허용 규칙만 평가 | 허용 및 거부 규칙 모두 평가 |
| **우선순위** | 모든 규칙 평가 | 규칙 번호 순서대로 평가 |
| **권장 사용** | 기본 방화벽으로 사용 | 추가 보안 레이어로 사용 |

> **💡 실무 팁**
>
> VPC 보안 설계 시 주의사항:
> - **최소 권한 원칙**: 필요한 포트만 개방하고 기본적으로 모든 트래픽 차단
> - **다중 AZ 배치**: 가용성을 위해 여러 가용 영역에 리소스 분산 배치
> - **VPC Flow Logs**: 네트워크 트래픽 로깅을 통한 보안 모니터링
> - **VPC Endpoint**: 인터넷을 거치지 않고 AWS 서비스 접근 (비용 및 보안 강화)

#### VPC 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │
              ┌──────────▼──────────┐
              │  Internet Gateway   │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │          VPC (10.0.0.0/16)    │
         │                               │
         │  ┌─────────────────────────┐  │
         │  │  Public Subnet          │  │
         │  │  (10.0.1.0/24)          │  │
         │  │  ┌─────────────────┐    │  │
         │  │  │   Web Tier      │    │  │
         │  │  │   (ELB, WAF)    │    │  │
         │  │  └─────────────────┘    │  │
         │  └─────────┬───────────────┘  │
         │            │                  │
         │  ┌─────────▼───────────────┐  │
         │  │  Private Subnet         │  │
         │  │  (10.0.10.0/24)         │  │
         │  │  ┌─────────────────┐    │  │
         │  │  │   App Tier      │    │  │
         │  │  │   (EC2, ECS)    │    │  │
         │  │  └─────────────────┘    │  │
         │  └─────────┬───────────────┘  │
         │            │                  │
         │  ┌─────────▼───────────────┐  │
         │  │  Isolated Subnet        │  │
         │  │  (10.0.20.0/24)         │  │
         │  │  ┌─────────────────┐    │  │
         │  │  │   Data Tier     │    │  │
         │  │  │   (RDS, DynamoDB)│   │  │
         │  │  └─────────────────┘    │  │
         │  └─────────────────────────┘  │
         └───────────────────────────────┘
```

### 1.2 IAM: 접근 제어 및 권한 관리

IAM(Identity and Access Management)은 AWS 리소스에 대한 접근을 제어하는 핵심 서비스입니다.

#### IAM 핵심 원칙

| 원칙 | 설명 | 실무 적용 |
|------|------|----------|
| **최소 권한 원칙** | 필요한 최소한의 권한만 부여 | IAM Policy Autopilot 활용 |
| **역할 기반 접근 제어** | 사용자 대신 역할(Role) 사용 권장 | EC2 Instance Profile 활용 |
| **MFA 강제** | 루트 계정 및 관리자 계정에 MFA 필수 적용 | IAM Policy에서 MFA 조건 추가 |
| **정기적 권한 검토** | 미사용 권한 정리 및 권한 검토 | Access Analyzer 활용 |

#### IAM 모범 사례

| 모범 사례 | 설명 | 구현 방법 |
|----------|------|----------|
| **루트 계정 보호** | 루트 계정은 일상 작업에 사용 금지 | 루트 계정 MFA 활성화, Access Key 삭제 |
| **IAM Policy 버전 관리** | Policy 변경 이력 추적 | IAM Policy 버전 관리 활성화 |
| **권한 검토 자동화** | 정기적인 권한 검토 자동화 | Access Analyzer, IAM Access Analyzer 활용 |
| **교차 계정 역할** | 다른 계정 접근 시 역할 사용 | AssumeRole을 통한 임시 권한 부여 |

> **참고**: IAM Policy Autopilot 관련 자세한 내용은 [AWS IAM Policy Autopilot 문서](https://docs.aws.amazon.com/IAM/latest/UserGuide/)를 참조하세요.

#### IAM Policy 예제: MFA 강제 정책

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllExceptListedIfNoMFA",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:GetUser",
        "iam:ListMFADevices",
        "iam:ListVirtualMFADevices",
        "iam:ResyncMFADevice",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### 1.3 S3: 데이터 보호 및 접근 제어

S3(Simple Storage Service)는 객체 스토리지 서비스로, 데이터 보호가 중요한 서비스입니다.

#### S3 보안 설정

| 보안 기능 | 설명 | 적용 방법 |
|----------|------|----------|
| **버킷 정책** | 버킷 레벨 접근 제어 | JSON 형식의 정책 문서 작성 |
| **객체 ACL** | 개별 객체 접근 제어 | 객체별 ACL 설정 (권장하지 않음) |
| **버전 관리** | 실수로 삭제된 데이터 복구 가능 | 버킷 버전 관리 활성화 |
| **암호화** | 저장 시 암호화(SSE-S3, SSE-KMS) 및 전송 시 암호화(TLS) | 버킷 기본 암호화 설정 |

#### S3 암호화 옵션 비교

| 암호화 유형 | 설명 | 사용 시나리오 |
|------------|------|-------------|
| **SSE-S3** | AWS가 관리하는 암호화 키 사용 | 일반적인 데이터 암호화 |
| **SSE-KMS** | AWS KMS를 통한 암호화 키 관리 | 규정 준수 요구사항, 감사 추적 필요 |
| **SSE-C** | 고객이 제공하는 암호화 키 사용 | 고객이 키를 완전히 제어해야 하는 경우 |
| **클라이언트 측 암호화** | 업로드 전 클라이언트에서 암호화 | 최고 수준의 보안 요구사항 |

#### Public 접근 차단 전략

| 설정 항목 | 설명 | 권장 설정 |
|----------|------|----------|
| **Block Public Access** | 버킷의 Public Access 완전 차단 | 모든 옵션 활성화 |
| **버킷 정책** | Public 접근을 명시적으로 거부 | Deny 정책 추가 |
| **객체 ACL** | Public 읽기/쓰기 차단 | 버킷 정책에서 제어 |

> **⚠️ 보안 주의사항**
>
> S3 보안 설정 시 주의사항:
> - **Public Access Block**: 모든 버킷에 Public Access Block 활성화
> - **버킷 정책 검토**: 버킷 정책을 정기적으로 검토하여 Public 접근 확인
> - **암호화 필수**: 민감한 데이터는 반드시 암호화하여 저장
> - **접근 로그**: CloudTrail 및 S3 접근 로그를 통한 접근 모니터링

#### S3 버킷 정책 예제: Public Access 완전 차단

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-secure-bucket",
        "arn:aws:s3:::my-secure-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalOrgID": "o-xxxxxxxxxx"
        }
      }
    }
  ]
}
```

### 1.4 GuardDuty: 위협 탐지 및 대응

GuardDuty는 AWS 계정 및 워크로드에서 악의적 활동과 무단 동작을 지속적으로 모니터링하는 위협 탐지 서비스입니다.

#### GuardDuty 탐지 기능

| 탐지 영역 | 설명 | 주요 기능 |
|---------|------|----------|
| **악의적 IP 주소** | 알려진 악성 IP와의 통신 탐지 | C2 통신, 악성 IP 접근 탐지 |
| **비정상적인 API 호출** | 의심스러운 API 활동 탐지 | 권한 에스컬레이션, 비정상적인 리소스 생성 |
| **인스턴스 침해** | EC2 인스턴스의 악성코드 감염 탐지 | 악성코드 스캔, 이상 행위 탐지 |
| **데이터 유출 시도** | 대량 데이터 전송 패턴 탐지 | S3 대량 다운로드, 데이터 유출 시도 탐지 |

#### GuardDuty 활용 전략

| 전략 | 설명 | 구현 방법 |
|------|------|----------|
| **전 리전 활성화** | 모든 리전에서 GuardDuty 활성화 | 멀티 리전 배포 시 필수 |
| **Security Hub 통합** | Security Hub와 통합하여 중앙 집중식 관리 | Security Hub에서 GuardDuty 결과 확인 |
| **자동 대응** | CloudWatch Events를 통한 자동 대응 워크플로우 구성 | Lambda 함수를 통한 자동 격리 |
| **알림 설정** | 중요한 발견 사항에 대한 즉시 알림 | SNS, Slack 등 알림 채널 설정 |

> **💡 실무 팁**
>
> GuardDuty 활용 시 주의사항:
> - **False Positive 관리**: 알림 규칙을 최적화하여 False Positive 최소화
> - **비용 관리**: GuardDuty는 데이터 처리량 기반 과금이므로 모니터링 필요
> - **정기적 리뷰**: GuardDuty 발견 사항을 정기적으로 리뷰하고 대응 프로세스 개선

#### GuardDuty 자동 대응 Lambda 예제

```python
import boto3
import json

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    # GuardDuty 이벤트에서 인스턴스 ID 추출
    finding = event['detail']
    instance_id = finding['resource']['instanceDetails']['instanceId']
    severity = finding['severity']

    # High 심각도 이상일 경우 자동 격리
    if severity >= 7.0:
        # Security Group 변경으로 네트워크 격리
        response = ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=['sg-isolated']  # 격리용 Security Group
        )

        # 관리자에게 알림
        sns.publish(
            TopicArn='arn:aws:sns:region:account-id:security-alerts',
            Subject=f'GuardDuty Alert: Instance {instance_id} Isolated',
            Message=json.dumps(finding, indent=2)
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'Instance {instance_id} isolated successfully')
        }
```

## 2. 2025년 AWS re:Invent 보안 발표

2025년 AWS re:Invent에서 발표된 최신 보안 기능들을 정리합니다. VPC, IAM, GuardDuty 등 이번 주차에서 다룬 서비스들의 주요 업데이트가 포함되어 있습니다.

### 2.1 GuardDuty 주요 업데이트

#### GuardDuty Extended Threat Detection

기존 GuardDuty의 위협 탐지 기능이 대폭 강화되었습니다.

| 기능 | 기존 | 신규 |
|------|------|------|
| **탐지 방식** | 개별 이벤트 단위 분석 | 공격 시퀀스 탐지 (Attack Sequence) |
| **탐지 대상** | EC2, S3, IAM | EC2, ECS, S3, IAM, Lambda |
| **공격 패턴** | 단일 이벤트 기반 | 복합 공격 패턴 자동 연결 |
| **오탐률** | 상대적으로 높음 | 공격 시퀀스 분석으로 오탐 감소 |
| **시각화** | 개별 알림 | 공격 체인 시각화 |

#### GuardDuty Malware Protection for AWS Backup

| 기능 | 설명 | 비용 최적화 |
|------|------|-----------|
| **백업 데이터 스캔** | EC2, EBS, S3 백업 데이터에서 악성코드 자동 스캔 | 증분 스캔 지원 |
| **복원 전 검증** | 백업 복원 전 악성코드 감염 여부 확인 | 사전 차단으로 복구 시간 단축 |
| **스캔 최적화** | 증분 스캔 지원으로 스캔 시간 및 비용 최적화 | 변경된 데이터만 스캔 |

### 2.2 Security Hub 강화

#### AWS Security Hub GA 업데이트

Security Hub가 더욱 강력한 중앙 보안 관리 플랫폼으로 발전했습니다.

| 신규 기능 | 설명 | 활용 시나리오 |
|----------|------|-------------|
| **보안 위험 중앙 집중화** | 모든 보안 서비스 통합 | 단일 대시보드 관리 |
| **히스토리 트렌드** | 시간별 보안 상태 추적 | 보안 개선 효과 측정 |
| **노출 요약** | 취약점 현황 요약 | 경영진 리포트 |
| **커스텀 위젯** | 맞춤형 대시보드 | 팀별 보안 현황 |
| **자동화된 컴플라이언스** | CIS, PCI-DSS 등 표준 준수 상태 자동 확인 | 규정 준수 자동화 |

### 2.3 IAM 보안 자동화

#### IAM Policy Autopilot

AI 기반 IAM 정책 자동 생성 도구입니다.

| 기능 | 설명 | 실무 활용 |
|------|------|----------|
| **정책 자동 생성** | 실제 사용 패턴 분석하여 최소 권한 정책 생성 | 신규 사용자 온보딩 시 자동 정책 생성 |
| **정책 최적화** | 기존 정책의 사용되지 않는 권한 제거 | 과도한 권한 제거, 보안 강화 |
| **권한 추천** | 필요한 권한을 자동으로 추천 | 개발 생산성 향상 및 보안 강화 균형 |
| **컴플라이언스 검증** | 최소 권한 원칙 준수 여부 자동 검증 | 보안 감사 자동화 |

> **참고**: IAM Policy Autopilot 관련 자세한 내용은 [AWS IAM Policy Autopilot 문서](https://docs.aws.amazon.com/IAM/latest/UserGuide/)를 참조하세요.

#### aws login 명령어

새로운 CLI 인증 방식으로 브라우저 세션 기반 자격증명을 획득합니다.

| 기능 | 설명 | 보안 이점 |
|------|------|----------|
| **SSO 연동** | AWS IAM Identity Center와 연동 | 중앙 집중식 인증 관리 |
| **임시 자격증명** | 임시 자격증명 자동 관리 | 장기 Access Key 사용 감소 |
| **브라우저 기반** | 브라우저를 통한 인증 | MFA 자동 적용 |

> **참고**: AWS CLI 인증 관련 내용은 [AWS CLI 공식 문서](https://docs.aws.amazon.com/cli/latest/userguide/) 및 [AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/)를 참조하세요.

### 2.4 AI 보안 솔루션

#### AWS Security Agent (Preview)

개발 전 과정에서 보안을 자동화하는 에이전트입니다.

| 기능 | 설명 | 활용 시나리오 |
|------|------|-------------|
| **자동화된 보안 리뷰** | 애플리케이션 보안 자동 리뷰 | 코드 리뷰 프로세스 통합 |
| **컨텍스트 인식 침투 테스트** | 애플리케이션 컨텍스트를 이해한 침투 테스트 | 개발 단계 보안 테스트 |
| **DevSecOps 통합** | CI/CD 파이프라인에 자동 통합 | Shift-Left Security 실현 |


#### AgentCore Identity

AI 에이전트를 위한 전용 신원 관리 시스템입니다.

| 기능 | 설명 | 활용 시나리오 |
|------|------|-------------|
| **에이전트 신원 관리** | AI 에이전트에 대한 고유 신원 부여 | AI 기반 자동화 워크로드 관리 |
| **권한 관리** | 에이전트별 세분화된 권한 제어 | 최소 권한 원칙 적용 |
| **감사 추적** | 에이전트의 모든 행위에 대한 감사 로그 | 보안 감사 및 컴플라이언스 |

### 2.5 조직 관리 개선

#### AWS Organizations Account Migration

| 기능 | 설명 | 보안 이점 |
|------|------|----------|
| **조직 간 이동** | 계정을 standalone으로 변환하지 않고 조직 간 직접 이동 | 보안 정책 연속성 유지 |
| **SCP 자동 재적용** | Service Control Policy 자동 재적용 | 거버넌스 정책 유지 |
| **보안 정책 연속성** | 계정 이동 시 보안 정책 자동 유지 | 보안 공백 방지 |

### 2.6 Third-party 보안 통합

2025년 re:Invent에서 발표된 주요 Third-party 보안 파트너십:

| 파트너 | 통합 내용 | 핵심 가치 |
|--------|----------|----------|
| **SentinelOne** | Singularity + Security Hub/CloudWatch | Purple AI MCP Server로 AI 기반 위협 분석 |
| **Salt Security** | Ask Pepper AI (Bedrock 기반) | API 보안 자동화 및 취약점 탐지 |
| **HiddenLayer** | Bedrock, SageMaker 네이티브 | AI/ML 모델 보안 및 적대적 공격 방어 |

## 3. 한국 기업 환경 분석 (Korean Impact Analysis)

### 3.1 국내 기업의 AWS 보안 현황

| 산업군 | 주요 보안 과제 | AWS 서비스 활용 | 규제 준수 |
|--------|-------------|---------------|----------|
| **금융** | 개인정보보호, 금융거래 보안 | VPC 격리, KMS 암호화 | 전자금융감독규정, ISMS-P |
| **공공** | 행정정보 보호, 개인정보 보안 | Private Subnet, VPN | 정보보호 지침, 개인정보보호법 |
| **이커머스** | 결제정보 보호, 고객정보 보안 | S3 암호화, GuardDuty | PCI-DSS, 개인정보보호법 |
| **헬스케어** | 의료정보 보호, 환자정보 보안 | Private VPC, HIPAA 준수 | 의료법, 개인정보보호법 |

### 3.2 국내 규제 준수 전략

| 규제/법률 | 요구사항 | AWS 대응 방안 | 구현 방법 |
|----------|---------|-------------|----------|
| **개인정보보호법** | 개인정보 암호화, 접근 제어 | S3 SSE-KMS, IAM Policy | 민감정보 KMS 암호화, 최소 권한 |
| **ISMS-P** | 정보보호관리체계 인증 | Security Hub, Config | 통합 모니터링, 자동 감사 |
| **전자금융감독규정** | 전자금융거래 보안 | VPC 격리, MFA 강제 | Private Subnet, IAM MFA |
| **클라우드컴퓨팅법** | 클라우드 이용 보고 | CloudTrail, Config | 로그 수집, 변경 추적 |

### 3.3 한국 기업의 AWS 도입 시 주요 고려사항

| 고려사항 | 설명 | AWS 솔루션 |
|---------|------|-----------|
| **데이터 주권** | 한국 내 데이터 저장 요구 | ap-northeast-2 리전 사용 |
| **망분리** | 개발/운영 망 분리 | VPC Peering, Transit Gateway |
| **접근 통제** | 내부 IP 기반 접근 제어 | Security Group, NACL |
| **로그 관리** | 최소 1년 이상 로그 보관 | CloudTrail, S3 버킷 정책 |
| **백업/복구** | 재해복구 계획 수립 | AWS Backup, Cross-Region 복제 |

## 4. 경영진 보고 형식 (Board Reporting Format)

### 4.1 월간 보안 현황 리포트

#### 보안 지표 요약

| 지표 | 이번 달 | 지난 달 | 증감 | 목표 |
|------|--------|--------|------|------|
| **보안 사고** | 2건 | 5건 | ⬇️ 60% | 0건 |
| **GuardDuty 탐지** | 127건 | 98건 | ⬆️ 30% | 모니터링 중 |
| **평균 대응 시간** | 15분 | 45분 | ⬇️ 67% | 10분 |
| **컴플라이언스 점수** | 92% | 85% | ⬆️ 7% | 95% |

#### 주요 보안 투자 및 효과

| 투자 항목 | 투자 금액 | 예상 효과 | ROI |
|----------|---------|----------|-----|
| **VPC 재설계** | ₩5,000,000 | 공격 표면 60% 축소 | 2,400% |
| **IAM 정책 자동화** | ₩3,000,000 | 권한 오용 75% 감소 | 2,667% |
| **GuardDuty 활성화** | ₩1,500,000 | 탐지 시간 80% 단축 | 6,667% |

### 4.2 분기별 보안 전략 리포트

#### 전략적 목표 및 달성도

| 전략적 목표 | Q1 목표 | 현재 달성도 | 액션 플랜 |
|-----------|--------|-----------|----------|
| **Zero Trust 아키텍처 구현** | 50% | 45% | VPC Endpoint 확대 |
| **자동화된 위협 대응** | 80% | 75% | Lambda 함수 고도화 |
| **컴플라이언스 자동화** | 100% | 92% | Config Rules 추가 |

#### 보안 위험 히트맵

| 위험 영역 | 리스크 레벨 | 영향도 | 대응 우선순위 |
|---------|-----------|--------|------------|
| **네트워크 노출** | 🔴 높음 | 매우 높음 | 1순위 |
| **권한 과다 부여** | 🟠 중간 | 높음 | 2순위 |
| **로그 미수집** | 🟡 낮음 | 중간 | 3순위 |

## 5. SIEM 탐지 쿼리 (Detection Queries)

<!--
### Splunk SPL 쿼리

#### GuardDuty 고위험 알림 모니터링
```spl
index=aws sourcetype=aws:cloudwatch:guardduty
| where severity >= 7.0
| stats count by type, severity, resource.instanceDetails.instanceId
| sort -severity
```

#### IAM 비정상 API 호출 탐지
```spl
index=aws sourcetype=aws:cloudtrail
| where eventName IN ("CreateAccessKey", "CreateUser", "AttachUserPolicy")
  AND userAgent!="console.amazonaws.com"
| stats count by userIdentity.arn, eventName, sourceIPAddress
| where count > 10
```

#### S3 Public Access 변경 탐지
```spl
index=aws sourcetype=aws:cloudtrail eventName IN ("PutBucketAcl", "PutBucketPolicy")
| eval isPublic=if(match(requestParameters, "AllUsers|AuthenticatedUsers"), "true", "false")
| where isPublic="true"
| table _time, userIdentity.arn, eventName, requestParameters.bucketName
```

### Azure Sentinel KQL 쿼리

#### GuardDuty 위협 탐지 분석
```kql
AWSGuardDuty
| where Severity >= 7.0
| where TimeGenerated > ago(24h)
| summarize Count=count() by Type, Severity, ResourceId
| order by Severity desc
```

#### IAM 권한 에스컬레이션 탐지
```kql
AWSCloudTrail
| where EventName in ("PutUserPolicy", "AttachUserPolicy", "CreateAccessKey")
| where UserAgent !contains "console.amazonaws.com"
| summarize Count=count() by UserIdentityArn, EventName, SourceIpAddress
| where Count > 5
```

#### S3 대량 다운로드 탐지 (데이터 유출)
```kql
AWSCloudTrail
| where EventName == "GetObject"
| where TimeGenerated > ago(1h)
| summarize TotalRequests=count(), UniqueObjects=dcount(RequestParameters) by UserIdentityArn, SourceIpAddress
| where TotalRequests > 1000
| order by TotalRequests desc
```
-->

## 6. Threat Hunting 쿼리

### 6.1 공격 시나리오별 헌팅 쿼리

#### 시나리오 1: 크리덴셜 침해 후 권한 에스컬레이션

```bash
# CloudTrail 로그에서 비정상적인 API 호출 패턴 탐지
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole \
  --start-time 2025-01-01T00:00:00Z \
  --max-results 50 \
  | jq '.Events[] | select(.Username | test("i-[0-9a-f]+") | not)'
```

#### 시나리오 2: 내부자 위협 - 대량 데이터 접근

```bash
# S3 접근 로그 분석 - 단기간 대량 다운로드
aws s3api list-objects-v2 \
  --bucket security-logs \
  --prefix cloudtrail/ \
  | jq '.Contents[] | select(.Key | contains("GetObject"))'
```

#### 시나리오 3: 암호화폐 채굴 인스턴스 탐지

```bash
# CloudWatch 메트릭으로 CPU 사용량 이상 탐지
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxxxxxx \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-07T23:59:59Z \
  --period 3600 \
  --statistics Average \
  | jq '.Datapoints[] | select(.Average > 90)'
```

### 6.2 고급 위협 헌팅 전략

| 헌팅 대상 | 탐지 방법 | 사용 도구 | 대응 방안 |
|---------|---------|---------|----------|
| **Lateral Movement** | VPC Flow Logs 분석 | Athena, Elasticsearch | Security Group 격리 |
| **Data Exfiltration** | S3 접근 패턴 분석 | CloudTrail, GuardDuty | S3 버킷 정책 강화 |
| **Privilege Escalation** | IAM API 호출 분석 | CloudTrail, IAM Access Analyzer | 권한 회수, MFA 강제 |
| **Persistence** | Launch Configuration 변경 탐지 | Config, CloudTrail | 자동 롤백, 알림 |

## 7. 실무 적용 방안

### 7.1 즉시 적용 가능한 보안 강화 방안

| 항목 | 적용 방법 | 예상 효과 | 우선순위 |
|------|---------|----------|---------|
| **VPC 네트워크 분리** | Public/Private/Isolated 서브넷 구성 | 공격 표면 축소 | 높음 |
| **IAM 정책 최적화** | IAM Policy Autopilot 활용 | 과도한 권한 제거 | 높음 |
| **S3 Public Access 차단** | 모든 버킷에 Public Access Block 활성화 | 데이터 유출 위험 감소 | 높음 |
| **GuardDuty 활성화** | 모든 리전에서 GuardDuty 활성화 | 위협 조기 탐지 | 높음 |
| **Security Hub 통합** | Security Hub 활성화 및 통합 | 중앙 집중식 보안 관리 | 중간 |

### 7.2 보안 모범 사례 체크리스트

| 보안 영역 | 체크리스트 항목 | 설명 |
|----------|---------------|------|
| **네트워크 보안** | VPC 네트워크 분리 | Public/Private/Isolated 서브넷 구성 |
| | Security Group 최소 권한 원칙 | 필요한 포트만 개방 |
| | VPC Flow Logs 활성화 | 네트워크 트래픽 로깅 |
| **접근 제어** | IAM 최소 권한 원칙 | 필요한 최소한의 권한만 부여 |
| | MFA 강제 적용 | 루트 계정 및 관리자 계정 |
| | 정기적 권한 검토 | 미사용 권한 정리 |
| **데이터 보안** | S3 암호화 활성화 | 저장 시 암호화 필수 |
| | S3 Public Access 차단 | 모든 버킷에 Public Access Block |
| | 버전 관리 활성화 | 실수로 삭제된 데이터 복구 |
| **위협 탐지** | GuardDuty 활성화 | 모든 리전에서 활성화 |
| | Security Hub 통합 | 중앙 집중식 보안 관리 |
| | 자동 대응 설정 | CloudWatch Events를 통한 자동 대응 |

### 7.3 공격 흐름도 (Attack Flow Diagram)

```
[1단계: 초기 침투 (Initial Access)]
         |
         v
[정찰 (Reconnaissance)]
    - Port Scanning
    - Service Enumeration
    - Vulnerability Scanning
         |
         v
[2단계: 실행 (Execution)]
    - Exploit Public-Facing Application
    - Phishing
    - Valid Accounts
         |
         v
[3단계: 지속성 확보 (Persistence)]
    - Create Account
    - Valid Accounts
    - Modify Cloud Compute Infrastructure
         |
         v
[4단계: 권한 상승 (Privilege Escalation)]
    - IAM Policy Manipulation
    - Valid Accounts
    - Exploitation for Privilege Escalation
         |
         v
[5단계: 방어 회피 (Defense Evasion)]
    - Disable Cloud Logs
    - Impair Defenses
    - Valid Accounts
         |
         v
[6단계: 크리덴셜 접근 (Credential Access)]
    - Unsecured Credentials
    - Steal Application Access Token
         |
         v
[7단계: 탐색 (Discovery)]
    - Cloud Infrastructure Discovery
    - Account Discovery
    - Permission Groups Discovery
         |
         v
[8단계: 측면 이동 (Lateral Movement)]
    - Use Alternate Authentication Material
    - Remote Services
         |
         v
[9단계: 수집 (Collection)]
    - Data from Cloud Storage Object
    - Data from Information Repositories
         |
         v
[10단계: 유출 (Exfiltration)]
    - Transfer Data to Cloud Account
    - Exfiltration Over Web Service
         |
         v
[11단계: 영향 (Impact)]
    - Resource Hijacking
    - Data Destruction
    - Service Stop

┌────────────────────────────────────────────────────────────┐
│  AWS 보안 서비스별 방어 레이어                                  │
├────────────────────────────────────────────────────────────┤
│  [VPC + Security Group]  → 1, 2, 7, 8단계 차단               │
│  [IAM + MFA]             → 3, 4, 6단계 차단                  │
│  [CloudTrail + Config]   → 5단계 탐지                        │
│  [GuardDuty]             → 전 단계 탐지                       │
│  [S3 Block Public Access]→ 9, 10단계 차단                    │
└────────────────────────────────────────────────────────────┘
```

### 7.4 단계별 구현 로드맵

#### Phase 1: 기본 보안 설정 (1-2주)

```
Week 1: 네트워크 기반 강화
├── VPC 네트워크 재설계 (Public/Private/Isolated)
├── Security Group 최소 권한 원칙 적용
├── VPC Flow Logs 활성화
└── Network ACL 구성

Week 2: 접근 제어 강화
├── IAM Policy 최소 권한 원칙 적용
├── MFA 강제 적용 (루트 계정 + 관리자)
├── IAM Access Analyzer 활성화
└── 교차 계정 역할 설정
```

#### Phase 2: 데이터 보호 (2-3주)

```
Week 3: S3 보안 강화
├── S3 Public Access Block 활성화 (전체 버킷)
├── S3 버킷 암호화 설정 (SSE-KMS)
├── S3 버전 관리 활성화
└── S3 접근 로그 활성화

Week 4: 암호화 및 키 관리
├── KMS 키 생성 및 관리
├── CloudTrail 암호화
├── EBS 볼륨 암호화
└── RDS 암호화 설정
```

#### Phase 3: 위협 탐지 및 대응 (3-4주)

```
Week 5: GuardDuty 및 Security Hub 설정
├── GuardDuty 전 리전 활성화
├── Security Hub 활성화
├── CloudWatch Events 연동
└── SNS 알림 설정

Week 6: 자동 대응 구성
├── Lambda 함수 작성 (자동 격리)
├── CloudWatch Events 규칙 생성
├── 자동 복구 워크플로우 구성
└── Playbook 작성
```

## 8. 참고 자료 (Comprehensive References)

### 8.1 AWS 공식 문서

| 서비스 | 문서 URL | 설명 |
|--------|---------|------|
| **VPC** | [AWS VPC 공식 문서](https://docs.aws.amazon.com/vpc/) | VPC 네트워크 설계 및 보안 |
| **IAM** | [AWS IAM 공식 문서](https://docs.aws.amazon.com/IAM/) | IAM 정책 및 역할 관리 |
| **S3** | [AWS S3 공식 문서](https://docs.aws.amazon.com/s3/) | S3 보안 및 암호화 |
| **GuardDuty** | [AWS GuardDuty 공식 문서](https://docs.aws.amazon.com/guardduty/) | GuardDuty 위협 탐지 |
| **Security Hub** | [AWS Security Hub 공식 문서](https://docs.aws.amazon.com/securityhub/) | Security Hub 통합 관리 |
| **CloudTrail** | [AWS CloudTrail 공식 문서](https://docs.aws.amazon.com/cloudtrail/) | CloudTrail 로그 관리 |

### 8.2 보안 프레임워크

| 프레임워크 | URL | 설명 |
|----------|-----|------|
| **MITRE ATT&CK** | [attack.mitre.org](https://attack.mitre.org/) | 공격 기법 매트릭스 |
| **CIS Benchmarks** | [cisecurity.org](https://www.cisecurity.org/cis-benchmarks/) | AWS 보안 기준 |
| **NIST Cybersecurity Framework** | [nist.gov/cyberframework](https://www.nist.gov/cyberframework) | 사이버보안 프레임워크 |
| **AWS Well-Architected Framework** | [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/) | AWS 아키텍처 모범 사례 |

### 8.3 한국어 보안 자료

| 자료 | URL | 설명 |
|------|-----|------|
| **KISA 클라우드 보안 가이드** | [kisa.or.kr](https://www.kisa.or.kr/) | 한국인터넷진흥원 보안 가이드 |
| **금융보안원 클라우드 보안 가이드** | [fsec.or.kr](https://www.fsec.or.kr/) | 금융권 클라우드 보안 |
| **AWS 한국 블로그** | [aws.amazon.com/ko/blogs/](https://aws.amazon.com/ko/blogs/) | AWS 한국 공식 블로그 |
| **AWS 한국 보안 웨비나** | [aws.amazon.com/ko/events/](https://aws.amazon.com/ko/events/) | AWS 보안 웨비나 자료 |

### 8.4 보안 도구 및 스크립트

| 도구 | GitHub URL | 설명 |
|------|-----------|------|
| **Prowler** | [github.com/prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | AWS 보안 감사 도구 |
| **ScoutSuite** | [github.com/nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | 멀티 클라우드 보안 감사 |
| **CloudSploit** | [github.com/aquasecurity/cloudsploit](https://github.com/aquasecurity/cloudsploit) | 클라우드 보안 스캐너 |
| **CloudMapper** | [github.com/duo-labs/cloudmapper](https://github.com/duo-labs/cloudmapper) | AWS 네트워크 시각화 |

### 8.5 학습 리소스

| 리소스 | URL | 설명 |
|--------|-----|------|
| **AWS Skill Builder** | [skillbuilder.aws](https://skillbuilder.aws/) | AWS 공식 교육 플랫폼 |
| **AWS Security Blog** | [aws.amazon.com/blogs/security/](https://aws.amazon.com/blogs/security/) | AWS 보안 블로그 |
| **AWS re:Invent Security Sessions** | [youtube.com/@AWSEventsChannel](https://www.youtube.com/@AWSEventsChannel) | re:Invent 보안 세션 영상 |
| **AWS Security Workshops** | [workshops.aws/categories/Security](https://workshops.aws/categories/Security) | AWS 보안 실습 워크샵 |

### 8.6 인증 및 자격증

| 인증 | URL | 설명 |
|------|-----|------|
| **AWS Certified Security - Specialty** | [aws.amazon.com/certification/certified-security-specialty/](https://aws.amazon.com/certification/certified-security-specialty/) | AWS 보안 전문가 인증 |
| **AWS Certified Solutions Architect** | [aws.amazon.com/certification/certified-solutions-architect-associate/](https://aws.amazon.com/certification/certified-solutions-architect-associate/) | AWS 솔루션 아키텍트 인증 |
| **CISSP** | [isc2.org/certifications/cissp](https://www.isc2.org/certifications/cissp) | 국제 정보보안 전문가 |

## 결론

클라우드 시큐리티 8기 2주차에서는 **AWS 보안 아키텍처의 핵심 구성요소**를 다뤘습니다.

**AWS 보안 아키텍처 핵심 구성요소**에서는 VPC를 통한 네트워크 격리, IAM을 통한 접근 제어, S3를 통한 데이터 보호, GuardDuty를 통한 위협 탐지까지 실무에 바로 적용 가능한 내용을 살펴봤습니다. 각 서비스의 보안 모범 사례와 실무 적용 전략을 중심으로 다뤘으며, 표 형식으로 정리하여 가독성을 높였습니다.

**2025년 AWS re:Invent 보안 발표**에서는 최신 보안 기능들을 정리했습니다:

| 서비스 | 주요 업데이트 | 실무 활용 |
|--------|-------------|----------|
| **GuardDuty Extended Threat Detection** | 공격 시퀀스 탐지로 복합 공격 패턴 자동 연결 | 공격 체인 추적 및 시각화 |
| **Security Hub 강화** | 중앙 집중식 보안 관리 플랫폼으로 발전 | 단일 대시보드에서 모든 보안 상태 확인 |
| **IAM Policy Autopilot** | AI 기반 IAM 정책 자동 생성 | 최소 권한 정책 자동 생성 및 최적화 |
| **AWS Security Agent** | 개발 전 과정 보안 자동화 | Shift-Left Security 실현 |
| **Third-party 보안 통합** | SentinelOne, Salt Security, HiddenLayer 등 파트너십 강화 | AI 기반 위협 분석 및 API 보안 강화 |

**실무 적용 방안**에서는 즉시 적용 가능한 보안 강화 방안과 보안 모범 사례 체크리스트를 제공했습니다. VPC 네트워크 분리, IAM 정책 최적화, S3 Public Access 차단, GuardDuty 활성화 등 실무에 바로 적용할 수 있는 구체적인 방안을 정리했습니다.

AWS 보안 아키텍처는 단순한 서비스 구성이 아닌, 각 구성요소 간의 시너지를 고려한 전략적 설계가 필요합니다. 올바른 네트워크 분리, 세밀한 접근 제어, 지속적인 위협 탐지를 통해 안전하고 효율적인 클라우드 환경을 구축할 수 있습니다. 특히 2025년에는 AI 기반 보안 자동화 도구들이 실무에서 즉시 활용 가능한 수준에 도달했으며, 이러한 도구들을 적극 활용하여 보안을 강화하는 것이 핵심입니다.

## 실무 체크리스트

### AWS 보안 아키텍처 점검 체크리스트

- [ ] VPC 네트워크가 Public/Private/Isolated로 올바르게 분리되어 있는지 확인
- [ ] Security Group이 최소 권한 원칙을 따르는지 점검
- [ ] VPC Flow Logs가 활성화되어 있는지 확인
- [ ] IAM 정책이 최소 권한 원칙을 따르는지 검토
- [ ] 모든 관리자 계정에 MFA가 적용되어 있는지 확인
- [ ] S3 버킷에 Public Access Block이 설정되어 있는지 점검
- [ ] S3 암호화(SSE-S3 또는 SSE-KMS)가 활성화되어 있는지 확인
- [ ] GuardDuty가 모든 리전에서 활성화되어 있는지 확인
- [ ] Security Hub가 활성화되고 CIS Benchmark가 적용되어 있는지 점검
- [ ] CloudTrail이 모든 리전에서 활성화되어 있는지 확인

---

**원본 포스트**: [클라우드 시큐리티 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지 완벽 정복!](https://twodragon.tistory.com/702)
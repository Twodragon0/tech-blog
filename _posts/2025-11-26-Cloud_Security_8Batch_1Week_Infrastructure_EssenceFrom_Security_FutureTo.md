---
layout: post
title: "클라우드 시큐리티 8기 1주차: 인프라의 본질부터 보안의 미래까지"
date: 2025-11-26 19:36:52 +0900
category: cloud
categories: [cloud]
tags: [Infrastructure, Cloud-Security, AWS]
excerpt: "클라우드 인프라 본질부터 2025년 AI 보안, Zero Trust, Post-quantum 암호화까지 실무 중심 학습"
comments: true
original_url: https://twodragon.tistory.com/701
image: /assets/images/2025-11-26-Cloud_Security_8Batch_1Week_Infrastructure_EssenceFrom_Security_FutureTo.svg
image_alt: "Cloud Security 8Batch 1Week: From Infrastructure Essence to Security Future"
toc: true
description: "클라우드 인프라 본질부터 2025년 보안 트렌드까지. AI 보안, Zero Trust, Post-quantum 암호화 등 최신 보안 기술을 실무 중심으로 학습하세요."
keywords: [Infrastructure, Cloud-Security, AWS, Zero Trust, AI보안, Post-quantum, 네트워크보안, 클라우드인프라]
author: Twodragon
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 8기 1주차: 인프라의 본질부터 보안의 미래까지</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Infrastructure</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AWS</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>클라우드 인프라의 본질: 네트워크, 컴퓨팅, 스토리지의 보안 관점</li>
      <li>2025년 클라우드 보안 트렌드: AI 보안, Zero Trust, 클라우드 네이티브 보안</li>
      <li>실무 인프라 보안 이슈 및 대응 방안</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS, Cloud Infrastructure, Security</span>
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

### 리스크 스코어카드

| 리스크 영역 | 현재 위험도 | 잠재적 영향 | 우선순위 | 예상 대응 비용 |
|-----------|-----------|------------|---------|--------------|
| **Shadow AI 사용** | 🔴 높음 | 데이터 유출, IP 손실 | 긴급 | 중간 (정책 수립 및 모니터링) |
| **과도한 IAM 권한** | 🔴 높음 | 내부자 위협, 권한 남용 | 긴급 | 낮음 (정책 재설계) |
| **암호화 미적용** | 🟡 중간 | 규제 위반, 데이터 유출 | 높음 | 낮음 (기본 암호화 활성화) |
| **네트워크 노출** | 🔴 높음 | 외부 공격, 데이터 탈취 | 긴급 | 중간 (아키텍처 재설계) |
| **모니터링 부재** | 🟡 중간 | 침해 탐지 지연 | 높음 | 낮음 (AWS 기본 서비스 활용) |
| **컴플라이언스 미준수** | 🟡 중간 | 법적 제재, 평판 손실 | 높음 | 높음 (인증 및 감사) |

### 핵심 권장사항 (Top 3)

1. **즉시 조치**: Shadow AI 사용 정책 수립 및 모니터링 시스템 구축
2. **3개월 내**: Zero Trust 아키텍처 기반 접근 제어 재설계
3. **6개월 내**: AI 기반 위협 탐지 시스템 도입 (GuardDuty Extended Threat Detection)

### 비즈니스 영향 분석

| 지표 | 현재 상태 | 목표 상태 | ROI |
|------|----------|----------|-----|
| **평균 침해 탐지 시간** | 45일 | 24시간 이내 | 보안 사고 비용 70% 감소 |
| **컴플라이언스 위반 건수** | 연 8건 | 0건 | 법적 리스크 100% 제거 |
| **보안 운영 비용** | 월 $50K | 월 $35K | 30% 비용 절감 (자동화) |
| **사고 대응 시간** | 평균 72시간 | 평균 4시간 | 다운타임 95% 감소 |

## 서론

안녕하세요, Twodragon입니다. 드디어 기다리던 클라우드 시큐리티 과정 8기가 힘차게 닻을 올렸습니다! 이번 8기는 온라인미팅에서, '20분 강의 + 5분 휴식'이라는 뇌과학적으로 가장 효율적인 학습 루틴으로 진행됩니다. 단순한 이론 주입식 교육이 아닌, 실무의 고민을 함께 나누는 시간이었습니다. 1주차 핵심 내용을 블로그를 통해 정리해 드립니다.

이 글에서는 클라우드 시큐리티 8기 1주차: 인프라의 본질부터 보안의 미래까지에 대해 실무 중심으로 상세히 다룹니다.

<img src="{% raw %}{{ '/assets/images/2025-11-26-Cloud_Security_8Batch_1Week_Infrastructure_EssenceFrom_Security_FutureTo_image.jpg' | relative_url }}{% endraw %}" alt="Cloud Security 8Batch 1Week: From Infrastructure Essence to Security Future" loading="lazy" class="post-image">

<figure>
<img src="{% raw %}{{ '/assets/images/diagrams/diagram_aws_security_services.png' | relative_url }}{% endraw %}" alt="AWS Security Services Overview" loading="lazy" class="post-image">
<figcaption>AWS 보안 서비스 개요 - Python diagrams로 생성</figcaption>
</figure>


## 1. 클라우드 인프라의 본질

### 1.1 인프라의 기본 구성 요소

클라우드 보안을 이해하기 위해서는 먼저 클라우드 인프라의 본질을 파악해야 합니다. 클라우드 인프라는 크게 세 가지 핵심 요소로 구성됩니다:

#### 네트워크 (Network)
- **가상 네트워크**: VPC, 서브넷, 라우팅 테이블을 통한 논리적 네트워크 분리
- **네트워크 보안**: Security Group, NACL, 방화벽을 통한 트래픽 제어
- **연결성**: 인터넷 게이트웨이, NAT 게이트웨이, VPN, Direct Connect

#### 컴퓨팅 (Compute)
- **가상 서버**: EC2, Lambda, 컨테이너 등 다양한 컴퓨팅 옵션
- **리소스 관리**: 오토스케일링, 로드 밸런싱을 통한 가용성 확보
- **보안**: IAM 역할, 인스턴스 프로파일을 통한 접근 제어

```bash
# 클라우드 인프라 보안 기본 설정 예시

# IAM 역할 생성 (최소 권한 원칙)
aws iam create-role --role-name EC2-Minimal-Role \
  --assume-role-policy-document file://trust-policy.json

# S3 버킷 암호화 활성화
aws s3api put-bucket-encryption --bucket my-secure-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/my-key"
      }
    }]
  }'

# CloudTrail 활성화 (모든 리전)
aws cloudtrail create-trail --name security-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail \
  --enable-log-file-validation

# Security Hub 활성화
aws securityhub enable-security-hub --enable-default-standards
```

#### 스토리지 (Storage)
- **데이터 저장**: S3, EBS, EFS 등 다양한 스토리지 옵션
- **데이터 보호**: 암호화, 버전 관리, 백업 및 복구
- **접근 제어**: 버킷 정책, 객체 ACL을 통한 세밀한 권한 관리

### 1.2 보안 관점에서 본 인프라

보안은 인프라의 모든 계층에 걸쳐 적용되어야 합니다:

**방어의 깊이 (Defense in Depth)**
- 네트워크 계층: 네트워크 분리 및 트래픽 필터링
- 애플리케이션 계층: WAF, API 게이트웨이 보안
- 데이터 계층: 암호화, 접근 제어, 데이터 분류

**최소 권한 원칙 (Principle of Least Privilege)**
- 사용자 및 서비스에 필요한 최소한의 권한만 부여
- 정기적인 권한 검토 및 정리
- IAM 정책을 통한 세밀한 접근 제어

**모니터링 및 감사 (Monitoring & Auditing)**
- CloudTrail을 통한 API 호출 로깅
- CloudWatch를 통한 리소스 모니터링
- GuardDuty를 통한 위협 탐지

### 1.3 실무에서 자주 발생하는 인프라 보안 이슈

| 보안 영역 | 주요 이슈 | 위험도 | 대응 방안 |
|----------|---------|-------|----------|
| **네트워크 보안** | Public 서브넷에 데이터베이스 배치 | 높음 | Private 서브넷으로 이동, Security Group 최소 권한 원칙 |
| | 과도하게 개방된 Security Group 규칙 | 높음 | 필요한 포트만 개방, 정기적 검토 |
| | 인터넷 게이트웨이를 통한 불필요한 외부 접근 | 중간 | VPC Endpoint 활용, NAT Gateway 최적화 |
| **접근 제어** | 루트 계정의 일상적 사용 | 높음 | IAM 사용자/역할 사용, 루트 계정 MFA 강제 |
| | 과도한 권한을 가진 IAM 사용자/역할 | 높음 | 최소 권한 원칙 적용, IAM Policy Autopilot 활용 |
| | 하드코딩된 자격 증명 | 높음 | Secrets Manager, 환경 변수 활용 |
| **데이터 보호** | 암호화되지 않은 민감 데이터 저장 | 높음 | S3, EBS 기본 암호화 활성화 |
| | Public 버킷에 민감 정보 노출 | 높음 | Public Access Block 활성화, 버킷 정책 검토 |
| | 백업 및 복구 계획 부재 | 중간 | AWS Backup 자동화, 정기적 복구 테스트 |

### 1.4 클라우드 인프라 아키텍처 패턴

#### 3-Tier 아키텍처 보안 설계

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet Gateway                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Public Subnet (Web Tier)                                        │
│  - Application Load Balancer                                     │
│  - WAF (Web Application Firewall)                                │
│  - Security Group: Allow 443 from 0.0.0.0/0                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Private Subnet (Application Tier)                               │
│  - EC2 Instances / ECS Tasks                                     │
│  - Security Group: Allow 8080 from Web Tier SG only              │
│  - No direct internet access                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Private Subnet (Data Tier)                                      │
│  - RDS Database (Encrypted)                                      │
│  - Security Group: Allow 3306 from App Tier SG only              │
│  - Automated backups enabled                                     │
│  - No internet connectivity                                      │
└─────────────────────────────────────────────────────────────────┘
```

#### 보안 계층별 방어 메커니즘

| 계층 | 방어 메커니즘 | 구현 도구 | 목적 |
|------|-------------|----------|------|
| **엣지** | DDoS 방어, CDN | CloudFront, Shield, Route53 | 트래픽 분산 및 공격 완화 |
| **네트워크** | 방화벽, 침입 차단 | WAF, Security Groups, NACL | 악성 트래픽 차단 |
| **애플리케이션** | 입력 검증, 인증 | API Gateway, Cognito, IAM | 무단 접근 방지 |
| **데이터** | 암호화, 접근 제어 | KMS, Secrets Manager, S3 Encryption | 데이터 보호 |
| **감사** | 로깅, 모니터링 | CloudTrail, CloudWatch, GuardDuty | 위협 탐지 및 추적 |

## 2. 2025년 클라우드 보안의 핵심 트렌드

### 2.1 AI 보안 위협과 대응

2025년 클라우드 보안에서 AI는 양날의 검이 되었습니다:

#### AI 기반 보안 위협

| 위협 유형 | 설명 | 위험도 | 대응 방안 |
|----------|------|-------|----------|
| **Shadow AI** | 승인되지 않은 AI 도구 사용 | 높음 | AI 사용 정책 수립, 네트워크 트래픽 모니터링, 승인된 AI 도구 화이트리스트 |
| **Deepfakes** | AI 생성 가짜 콘텐츠를 통한 사기 | 높음 | 다중 인증, 대역 외 확인, 음성/영상 인증 강화 |
| **AI 기반 공격** | AI를 활용한 자동화된 공격 | 높음 | 행위 기반 탐지, Rate Limiting, 이상 탐지 시스템 |
| | 지능형 자격 증명 스터핑 | 중간 | 다중 인증, CAPTCHA, 로그인 시도 제한 |
| | 적응형 피싱 | 높음 | AI 탐지 도구, 사용자 교육, 이메일 필터링 강화 |
| | 자율적 취약점 악용 | 높음 | 취약점 스캔 자동화, 패치 관리, 위협 인텔리전스 |

> **참고**: AI 보안 위협 관련 내용은 [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) 및 [MITRE ATLAS](https://atlas.mitre.org/)를 참조하세요.

#### AI 기반 보안 방어

| 방어 도구 | 설명 | 활용 시나리오 |
|----------|------|-------------|
| **AWS Security Agent (Preview)** | AI 기반 보안 자동화 | 개발 전 과정 보안 자동화 |
| **Amazon GuardDuty Extended Threat Detection** | 공격 시퀀스 탐지 | 복합 공격 패턴 자동 연결 |
| **Copilot Autofix** | 코드 취약점 자동 수정 | 개발 단계 취약점 자동 수정 |
| **IAM Policy Autopilot** | AI 기반 IAM 정책 자동 생성 | 최소 권한 정책 자동 생성 |

#### Shadow AI 탐지 및 대응 전략

```python
# Shadow AI 탐지를 위한 네트워크 트래픽 분석 (개념 코드)

import boto3
from datetime import datetime, timedelta

def detect_shadow_ai_usage():
    """
    VPC Flow Logs를 분석하여 승인되지 않은 AI 서비스 사용 탐지
    """
    # 승인된 AI 서비스 엔드포인트
    approved_ai_endpoints = [
        'api.openai.com',
        'bedrock.amazonaws.com',
        'sagemaker.amazonaws.com'
    ]

    # 의심스러운 AI 서비스 패턴
    suspicious_patterns = [
        'claude.ai',
        'chat.openai.com',
        'bard.google.com',
        'copilot.microsoft.com'
    ]

    # VPC Flow Logs에서 외부 AI 서비스 접근 탐지
    cloudwatch = boto3.client('logs')

    # 지난 24시간 로그 조회
    start_time = datetime.now() - timedelta(days=1)

    # 탐지 결과 보고
    incidents = []
    for pattern in suspicious_patterns:
        # 로그 분석 로직 (실제 구현 필요)
        pass

    return incidents

# 참고: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
```

### 2.2 Zero Trust 아키텍처 진화

2025년 Zero Trust는 단순한 네트워크 분할을 넘어섰습니다:

**Zero Trust 인증 및 접근 제어 프로세스**:

| 단계 | 프로세스 | 설명 | 결과 |
|------|---------|------|------|
| 1 | 사용자 요청 | 사용자가 리소스 접근 요청 | - |
| 2 | Identity Verification | 사용자 신원 확인 | 인증 성공/실패 |
| 3 | Device Trust Assessment | 디바이스 신뢰성 평가 | 디바이스 상태 확인 |
| 4 | Context Analysis | 컨텍스트 분석 (위치, 시간, 행동 패턴) | 위험도 평가 |
| 5 | Risk Score 계산 | 종합 위험도 점수 계산 | Low/Medium/High |
| 6 | 접근 제어 결정 | 위험도에 따른 접근 권한 부여 | Full/Limited/Block |

**위험도별 접근 제어 정책**:

| 위험도 | 접근 권한 | 추가 조치 | 설명 |
|--------|----------|----------|------|
| **Low** | Full Access | 없음 | 신뢰할 수 있는 사용자/디바이스 |
| **Medium** | Limited Access | MFA 필수 | 부분적 신뢰, 제한적 접근 |
| **High** | Block + Alert | 보안 팀 알림 | 의심스러운 활동, 접근 차단 |

**지속적 모니터링**:

| 모니터링 대상 | 설명 | 목적 |
|-------------|------|------|
| **Identity Verification** | 사용자 인증 상태 지속 확인 | 세션 하이재킹 방지 |
| **Device Trust Assessment** | 디바이스 상태 실시간 모니터링 | 디바이스 변조 탐지 |
| **Context Analysis** | 사용자 행동 패턴 분석 | 이상 행위 탐지 |

#### Zero Trust 2025 핵심 원칙
1. **지속적 검증**: 세션 내 지속적인 신뢰도 평가
2. **최소 권한의 동적 적용**: 상황에 따른 권한 조정
3. **마이크로 세그멘테이션**: 워크로드 수준의 네트워크 분리
4. **AI 기반 이상 탐지**: 행동 분석을 통한 위협 식별

#### Zero Trust 구현 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                     Identity Provider (IdP)                    │
│                  (AWS IAM Identity Center)                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│            Policy Decision Point (PDP)                         │
│  ┌──────────────┬──────────────┬──────────────────────┐      │
│  │ User Context │ Device State │ Risk Score Calculator│      │
│  └──────────────┴──────────────┴──────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Allow Access   │ │ Limited Access  │ │  Block Access   │
│  + Full Perms   │ │  + MFA Required │ │  + Alert SOC    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2.3 클라우드 네이티브 보안

#### 컨테이너 보안

컨테이너 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다.

| 보안 영역 | 기능 | 설명 |
|----------|------|------|
| **이미지 스캔** | 빌드 시점 취약점 탐지 | CI/CD 파이프라인에 이미지 스캔 통합 |
| **런타임 보호** | 컨테이너 런타임 보안 | Falco, Aqua Security 등 런타임 보안 도구 |
| **네트워크 정책** | Pod 간 통신 제어 | Kubernetes Network Policies를 통한 마이크로 세그멘테이션 |

#### Kubernetes 보안 (1.32+)

| 기능 | 설명 | 보안 이점 |
|------|------|----------|
| **Fine-grained Kubelet API Authorization** | Kubelet API에 대한 세밀한 권한 제어 | 최소 권한 원칙 적용 |
| **Credential Tracking** | 자격 증명 추적 및 관리 | 자격 증명 유출 탐지 |
| **User Namespaces** | Pod 사용자 네임스페이스 격리 | 컨테이너 탈출 위험 감소 |
| **Pod Certificates for mTLS** | Pod 간 상호 TLS 인증 | 네트워크 트래픽 암호화 |

#### Kubernetes 보안 체크리스트

```yaml
# Kubernetes 보안 강화 설정 예시

apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  # Security Context 설정
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:
  - name: app
    image: myapp:latest

    # 컨테이너 보안 설정
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL

    # 리소스 제한
    resources:
      limits:
        cpu: "1"
        memory: "512Mi"
      requests:
        cpu: "100m"
        memory: "128Mi"

    # 환경 변수 (Secrets 사용)
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password

# 참고: https://kubernetes.io/docs/concepts/security/pod-security-standards/
```

#### 서버리스 보안

| 보안 기능 | 설명 | 구현 방법 |
|----------|------|----------|
| **Function Permission Boundaries** | Lambda 함수 권한 경계 설정 | 최소 권한 원칙 적용 |
| **Event Source Validation** | 이벤트 소스 검증 | 무단 이벤트 차단 |
| **Execution Environment Isolation** | 실행 환경 격리 | 함수 간 격리 강화 |

> **참고**: 클라우드 네이티브 보안 관련 내용은 [CNCF Security Whitepaper](https://github.com/cncf/tag-security) 및 [Kubernetes 보안 체크리스트](https://kubernetes.io/docs/concepts/security/security-checklist/)를 참조하세요.

### 2.4 규제 및 컴플라이언스 동향

2025년 주요 규제 변화:

| 규제 | 주요 변경사항 | 대응 방안 |
|------|--------------|----------|
| **ISMS-P** | AI 보안 요구사항 강화 | AI 거버넌스 프레임워크 수립 |
| **개인정보보호법** | 국외 이전 규정 강화 | 데이터 지역화 검토 |
| **금융보안** | 클라우드 보안 가이드 개정 | 망분리 예외 요건 확인 |
| **EU AI Act** | 고위험 AI 시스템 규제 | AI 리스크 평가 체계 구축 |

### 2.5 FinOps와 보안의 융합

#### 비용 인식 보안 (Cost-Aware Security)

| 전략 | 설명 | 실무 적용 |
|------|------|----------|
| **보안 도구 비용 최적화** | 보안 도구의 비용 효율성 고려 | Security Hub, GuardDuty 비용 모니터링 |
| **리스크 기반 리소스 할당** | 위험도에 따른 보안 투자 우선순위 설정 | 중요도 높은 리소스에 우선 투자 |
| **컴플라이언스 비용 추적** | 규정 준수 비용 관리 | ISMS-P 등 인증 유지 비용 추적 |

#### 보안 인식 FinOps (Security-Aware FinOps)

| 전략 | 설명 | 실무 적용 |
|------|------|----------|
| **데이터 분류 기반 티어링** | 데이터 중요도에 따른 스토리지 티어 선택 | 민감 데이터는 고성능 티어 사용 |
| **암호화 오버헤드 계획** | 암호화로 인한 성능 및 비용 영향 고려 | 암호화 방식 선택 시 비용 고려 |
| **보안 사고 비용 영향** | 보안 사고로 인한 비용 영향 분석 | 사고 대응 비용 추적 및 예산 계획 |

#### 공유 메트릭

| 메트릭 | 설명 | 활용 방법 |
|--------|------|----------|
| **Cost per Protected Asset** | 보호된 자산당 비용 | 보안 투자 효율성 측정 |
| **Security Investment ROI** | 보안 투자 ROI | 보안 투자의 비즈니스 가치 정량화 |
| **Compliance Cost Efficiency** | 컴플라이언스 비용 효율성 | 규정 준수 비용 최적화 |

> **참고**: FinOps와 보안 통합 관련 내용은 [FinOps Foundation](https://www.finops.org/) 및 [AWS Cost Management](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/)를 참조하세요.

### 2.6 Post-Quantum 암호화 준비

#### 양자 컴퓨팅 위협 시나리오

| 위협 | 현재 암호화 | 양자 컴퓨터 영향 | 대응 방안 |
|------|-----------|----------------|----------|
| **RSA 암호 해독** | RSA-2048, RSA-4096 | Shor 알고리즘으로 해독 가능 | NIST PQC 표준 알고리즘으로 전환 |
| **ECC 공격** | ECDSA, ECDH | 타원 곡선 이산 로그 문제 해결 | Lattice 기반 암호화 |
| **Harvest Now, Decrypt Later** | 현재 암호화된 데이터 수집 | 미래 양자 컴퓨터로 해독 | 즉시 PQC 전환 필요 |

#### NIST Post-Quantum Cryptography (PQC) 표준

| 알고리즘 | 유형 | 용도 | AWS 지원 |
|---------|------|------|---------|
| **CRYSTALS-Kyber** | Key Encapsulation | 키 교환 | 2025년 KMS 지원 예정 |
| **CRYSTALS-Dilithium** | Digital Signature | 디지털 서명 | 2025년 지원 예정 |
| **SPHINCS+** | Stateless Hash-Based | 디지털 서명 | 평가 중 |

#### PQC 전환 로드맵

```
Phase 1 (2025 Q1-Q2): 평가 및 계획
┌────────────────────────────────────────┐
│ - 현재 암호화 인벤토리 수집             │
│ - 양자 위협 리스크 평가                 │
│ - PQC 전환 우선순위 결정                │
└────────────────────────────────────────┘
                 │
                 ▼
Phase 2 (2025 Q3-Q4): 파일럿 구현
┌────────────────────────────────────────┐
│ - 비프로덕션 환경 PQC 테스트            │
│ - 성능 및 호환성 검증                   │
│ - 하이브리드 암호화 방식 구현           │
└────────────────────────────────────────┘
                 │
                 ▼
Phase 3 (2026 Q1-Q2): 점진적 롤아웃
┌────────────────────────────────────────┐
│ - 중요 시스템부터 PQC 전환              │
│ - 레거시 시스템 호환성 유지             │
│ - 지속적 모니터링 및 최적화             │
└────────────────────────────────────────┘
```

## 3. MITRE ATT&CK 매핑

### 클라우드 환경 공격 기법 및 대응 방안

| Tactic | Technique | Sub-Technique | 클라우드 시나리오 | 탐지 방법 | 대응 조치 |
|--------|-----------|---------------|----------------|----------|----------|
| **Initial Access** | T1078: Valid Accounts | .004 Cloud Accounts | 탈취된 IAM 자격 증명 사용 | CloudTrail 이상 로그인 패턴 | MFA 강제, IP 화이트리스트 |
| | T1190: Exploit Public-Facing Application | - | 공개 API Gateway 취약점 악용 | WAF 로그, API Gateway 로그 | 입력 검증, Rate Limiting |
| **Execution** | T1059: Command and Scripting Interpreter | .009 Cloud API | 악의적 Lambda 함수 실행 | CloudTrail API 호출 로깅 | Lambda 권한 최소화 |
| **Persistence** | T1136: Create Account | .003 Cloud Account | 무단 IAM 사용자 생성 | CloudTrail `CreateUser` 이벤트 | IAM 생성 권한 제한, SCPs |
| | T1098: Account Manipulation | .001 Additional Cloud Credentials | IAM 키 추가 생성 | CloudTrail `CreateAccessKey` | IAM 키 정기 로테이션 |
| **Privilege Escalation** | T1548: Abuse Elevation Control Mechanism | .005 Temporary Elevated Cloud Access | AssumeRole 남용 | CloudTrail `AssumeRole` 패턴 분석 | 역할 신뢰 정책 강화 |
| **Defense Evasion** | T1562: Impair Defenses | .008 Disable Cloud Logs | CloudTrail 비활성화 | CloudWatch 로깅 중단 알람 | CloudTrail 변경 알림 |
| | T1070: Indicator Removal | .001 Clear Logs | S3 로그 버킷 삭제 | S3 버킷 삭제 이벤트 | 로그 버킷 MFA Delete |
| **Credential Access** | T1110: Brute Force | .001 Password Guessing | IAM 사용자 비밀번호 무차별 대입 | 연속 로그인 실패 탐지 | 계정 잠금 정책, MFA |
| | T1555: Credentials from Password Stores | .006 Cloud Secrets Management Stores | Secrets Manager 무단 접근 | Secrets Manager 접근 로그 | 최소 권한, VPC Endpoint |
| **Discovery** | T1580: Cloud Infrastructure Discovery | - | EC2 인스턴스 메타데이터 서비스 악용 | IMDSv2 미사용 탐지 | IMDSv2 강제 |
| | T1087: Account Discovery | .004 Cloud Account | IAM 사용자/역할 열거 | 대량 IAM API 호출 탐지 | Rate Limiting, 알람 |
| **Lateral Movement** | T1550: Use Alternate Authentication Material | .001 Application Access Token | 탈취된 STS 토큰 사용 | 비정상 위치/IP에서 토큰 사용 | 토큰 유효 기간 단축 |
| **Collection** | T1530: Data from Cloud Storage | - | S3 버킷 대량 다운로드 | S3 접근 로그, CloudTrail | 버킷 정책, VPC Endpoint |
| **Exfiltration** | T1537: Transfer Data to Cloud Account | - | 외부 계정으로 데이터 전송 | 교차 계정 접근 탐지 | SCPs로 외부 전송 차단 |
| **Impact** | T1485: Data Destruction | - | S3 버킷/EBS 볼륨 삭제 | 리소스 삭제 이벤트 알람 | 백업, MFA Delete |
| | T1486: Data Encrypted for Impact | - | 랜섬웨어로 EBS 암호화 | 비정상 암호화 활동 탐지 | 백업, 스냅샷 보호 |

### MITRE ATT&CK 공격 흐름도

```
Initial Access → Execution → Persistence → Privilege Escalation
     │              │            │                  │
     ▼              ▼            ▼                  ▼
[Stolen IAM]   [Lambda]    [New IAM]          [AssumeRole]
[Credentials]  [Function]  [User Created]     [Abuse]
     │              │            │                  │
     └──────────────┴────────────┴──────────────────┘
                         │
                         ▼
              Defense Evasion + Discovery
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    [Disable]      [Enumerate]    [IMDSv1]
    [CloudTrail]   [Resources]    [Abuse]
          │              │              │
          └──────────────┴──────────────┘
                         │
                         ▼
              Lateral Movement + Collection
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    [Use STS]      [Access S3]    [Download]
    [Token]        [Buckets]      [Data]
          │              │              │
          └──────────────┴──────────────┘
                         │
                         ▼
            Exfiltration + Impact
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    [Transfer to]  [Delete]       [Encrypt]
    [External]     [Resources]    [Data]
    [Account]
```

## 4. SIEM 탐지 쿼리

<!--
Splunk SPL Query: 무단 IAM 사용자 생성 탐지
index=cloudtrail eventName="CreateUser"
| stats count by userIdentity.principalId, requestParameters.userName, sourceIPAddress, userAgent
| where count > 3
| eval severity="HIGH"
| table _time, userIdentity.principalId, requestParameters.userName, sourceIPAddress, count, severity
-->

<!--
Azure Sentinel KQL Query: 무단 IAM 사용자 생성 탐지
AWSCloudTrail
| where EventName == "CreateUser"
| summarize Count=count() by UserIdentityPrincipalId, RequestParametersUserName, SourceIpAddress, UserAgent
| where Count > 3
| extend Severity = "HIGH"
| project TimeGenerated, UserIdentityPrincipalId, RequestParametersUserName, SourceIpAddress, Count, Severity
-->

<!--
Splunk SPL Query: CloudTrail 비활성화 탐지
index=cloudtrail eventName IN ("StopLogging", "DeleteTrail", "UpdateTrail")
| eval severity=case(
    eventName="DeleteTrail", "CRITICAL",
    eventName="StopLogging", "HIGH",
    eventName="UpdateTrail", "MEDIUM"
)
| table _time, eventName, userIdentity.principalId, sourceIPAddress, severity
| where severity IN ("HIGH", "CRITICAL")
-->

<!--
Azure Sentinel KQL Query: CloudTrail 비활성화 탐지
AWSCloudTrail
| where EventName in ("StopLogging", "DeleteTrail", "UpdateTrail")
| extend Severity = case(
    EventName == "DeleteTrail", "CRITICAL",
    EventName == "StopLogging", "HIGH",
    EventName == "UpdateTrail", "MEDIUM",
    "LOW"
)
| where Severity in ("HIGH", "CRITICAL")
| project TimeGenerated, EventName, UserIdentityPrincipalId, SourceIpAddress, Severity
-->

<!--
Splunk SPL Query: S3 버킷 퍼블릭 노출 탐지
index=cloudtrail eventName IN ("PutBucketAcl", "PutBucketPolicy", "PutBucketPublicAccessBlock")
| where requestParameters.AccessControlList.Grant{}.Grantee.URI="http://acs.amazonaws.com/groups/global/AllUsers"
    OR requestParameters.PublicAccessBlockConfiguration.BlockPublicAcls="false"
| table _time, eventName, requestParameters.bucketName, userIdentity.principalId, sourceIPAddress
| eval severity="CRITICAL"
-->

<!--
Azure Sentinel KQL Query: S3 버킷 퍼블릭 노출 탐지
AWSCloudTrail
| where EventName in ("PutBucketAcl", "PutBucketPolicy", "PutBucketPublicAccessBlock")
| where RequestParameters contains "AllUsers" or RequestParameters contains "BlockPublicAcls=false"
| extend Severity = "CRITICAL"
| project TimeGenerated, EventName, RequestParametersBucketName, UserIdentityPrincipalId, SourceIpAddress, Severity
-->

<!--
Splunk SPL Query: 비정상 시간대 관리자 활동 탐지
index=cloudtrail userIdentity.type="Root" OR userIdentity.principalId="*:admin*"
| eval hour=strftime(_time, "%H")
| where (hour >= 0 AND hour < 6) OR (hour >= 22 AND hour <= 23)
| stats count by userIdentity.principalId, sourceIPAddress, eventName, hour
| eval severity="HIGH"
| table _time, userIdentity.principalId, eventName, sourceIPAddress, hour, count, severity
-->

<!--
Azure Sentinel KQL Query: 비정상 시간대 관리자 활동 탐지
AWSCloudTrail
| where UserIdentityType == "Root" or UserIdentityPrincipalId contains ":admin"
| extend Hour = datetime_part("hour", TimeGenerated)
| where (Hour >= 0 and Hour < 6) or (Hour >= 22 and Hour <= 23)
| summarize Count=count() by UserIdentityPrincipalId, SourceIpAddress, EventName, Hour
| extend Severity = "HIGH"
| project TimeGenerated, UserIdentityPrincipalId, EventName, SourceIpAddress, Hour, Count, Severity
-->

<!--
Splunk SPL Query: 대량 EC2 인스턴스 종료 탐지
index=cloudtrail eventName="TerminateInstances"
| stats count by userIdentity.principalId, sourceIPAddress, userAgent
| where count > 5
| eval severity="HIGH"
| table _time, userIdentity.principalId, sourceIPAddress, count, severity
-->

<!--
Azure Sentinel KQL Query: 대량 EC2 인스턴스 종료 탐지
AWSCloudTrail
| where EventName == "TerminateInstances"
| summarize Count=count() by UserIdentityPrincipalId, SourceIpAddress, UserAgent
| where Count > 5
| extend Severity = "HIGH"
| project TimeGenerated, UserIdentityPrincipalId, SourceIpAddress, Count, Severity
-->

## 5. Threat Hunting 쿼리

### 위협 헌팅 시나리오 1: Shadow Admin 탐지

**목적**: 과도한 권한을 가진 숨겨진 관리자 계정 탐지

```python
# AWS CLI를 사용한 Shadow Admin 탐지

import boto3
import json

def find_shadow_admins():
    """
    AdministratorAccess 또는 PowerUserAccess를 가진
    모든 IAM 사용자/역할 탐지
    """
    iam = boto3.client('iam')

    # 모든 IAM 사용자 조회
    users = iam.list_users()['Users']
    shadow_admins = []

    for user in users:
        username = user['UserName']

        # 직접 연결된 정책 확인
        attached_policies = iam.list_attached_user_policies(
            UserName=username
        )['AttachedPolicies']

        for policy in attached_policies:
            if 'Administrator' in policy['PolicyName'] or \
               'PowerUser' in policy['PolicyName']:
                shadow_admins.append({
                    'Type': 'User',
                    'Name': username,
                    'Policy': policy['PolicyName'],
                    'LastUsed': iam.get_user(UserName=username)['User'].get('PasswordLastUsed', 'Never')
                })

    return shadow_admins

# 참고: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html
```

### 위협 헌팅 시나리오 2: 외부 계정으로의 데이터 전송

**목적**: S3 버킷에서 외부 AWS 계정으로 데이터 전송 탐지

```bash
# CloudTrail 로그에서 교차 계정 접근 탐지

# Athena 쿼리
SELECT
  eventtime,
  useridentity.principalid,
  useridentity.accountid AS source_account,
  requestparameters,
  resources[1].accountid AS target_account,
  sourceipaddress
FROM cloudtrail_logs
WHERE
  eventname IN ('PutObject', 'CopyObject', 'UploadPart')
  AND useridentity.accountid != resources[1].accountid
  AND year = '2025'
  AND month = '02'
ORDER BY eventtime DESC
LIMIT 100;

# 참고: https://docs.aws.amazon.com/athena/latest/ug/cloudtrail-logs.html
```

### 위협 헌팅 시나리오 3: 암호화 키 무단 사용

**목적**: KMS 키를 사용한 비정상적인 복호화 활동 탐지

```python
# KMS 키 사용 패턴 분석

import boto3
from datetime import datetime, timedelta
from collections import defaultdict

def detect_abnormal_kms_usage():
    """
    KMS Decrypt 호출 패턴 분석하여 이상 징후 탐지
    """
    cloudtrail = boto3.client('cloudtrail')

    # 지난 7일간 KMS Decrypt 이벤트 조회
    start_time = datetime.now() - timedelta(days=7)

    response = cloudtrail.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'Decrypt'
            }
        ],
        StartTime=start_time
    )

    # 사용자별 Decrypt 횟수 집계
    decrypt_counts = defaultdict(int)
    for event in response.get('Events', []):
        principal_id = event.get('Username', 'Unknown')
        decrypt_counts[principal_id] += 1

    # 평균 + 2 표준편차 이상이면 이상 징후
    avg = sum(decrypt_counts.values()) / len(decrypt_counts)
    anomalies = [
        (principal, count)
        for principal, count in decrypt_counts.items()
        if count > avg * 3
    ]

    return anomalies

# 참고: https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html
```

## 6. 한국 기업 환경 분석

### 6.1 국내 클라우드 보안 현황

| 구분 | 현황 | 과제 | 권장 사항 |
|------|------|------|----------|
| **클라우드 도입률** | 대기업 85%, 중소기업 62% | 보안 우려로 인한 도입 지연 | 클라우드 보안 교육, PoC 지원 |
| **보안 인력** | CISO 배치 기업 45% | 전문 인력 부족 | 외부 MSP 활용, 교육 프로그램 |
| **규제 준수** | ISMS-P 인증 기업 12% | 인증 비용 및 시간 소요 | 자동화 도구 활용, 컨설팅 |
| **망분리** | 금융권 100% 적용 | 클라우드 전환 시 망분리 예외 필요 | 가상 망분리, VDI 솔루션 |

### 6.2 한국형 클라우드 보안 참조 모델

```
┌────────────────────────────────────────────────────────────────┐
│              Compliance Layer (규제 준수 계층)                  │
│  ISMS-P │ 개인정보보호법 │ 금융보안 가이드 │ 전자금융거래법   │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│            Identity & Access (인증 및 접근 제어)                │
│  통합인증 (SSO) │ MFA 필수 │ 망분리 (물리/가상) │ 접근 로그    │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│              Data Protection (데이터 보호)                      │
│  개인정보 암호화 │ DLP │ 데이터 분류 │ 국내 데이터 보관 필수  │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│          Network Security (네트워크 보안)                       │
│  방화벽 │ IDS/IPS │ DDoS 방어 │ VPN │ 전용선 (Direct Connect)│
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│        Monitoring & Incident Response (모니터링 및 대응)        │
│  24/7 모니터링 │ 침해사고 대응 체계 │ CERT 연계 │ 로그 3년 보관│
└────────────────────────────────────────────────────────────────┘
```

### 6.3 금융권 클라우드 보안 요구사항

| 요구사항 | 설명 | AWS 구현 방안 | 주의사항 |
|---------|------|-------------|---------|
| **망분리** | 인터넷망과 업무망 물리적 분리 | AWS Outposts, VDI (WorkSpaces) | 예외 승인 필요 |
| **데이터 지역화** | 고객 금융정보는 국내 보관 | ap-northeast-2 (서울) 리전 전용 | 백업도 국내 보관 |
| **접근 통제** | 강화된 인증 (공인인증서, OTP) | IAM + MFA, Cognito | 금융보안원 가이드 준수 |
| **암호화** | 주요정보 암호화 (전송, 저장) | TLS 1.2+, KMS, S3/EBS 암호화 | 암호화 키 관리 정책 |
| **로그 보관** | 3년 이상 접근 로그 보관 | CloudTrail, S3 Glacier | 로그 위변조 방지 |
| **재해복구** | RTO 4시간, RPO 1시간 | 멀티 AZ, 백업, DR 사이트 | 정기 DR 훈련 |

### 6.4 ISMS-P 인증을 위한 클라우드 보안 체크리스트

| 통제항목 | 요구사항 | AWS 구현 | 증적 |
|---------|---------|---------|-----|
| **1.1.1 정보보호 정책 수립** | 클라우드 보안 정책 문서화 | 정책 문서 + SCPs | 정책 승인 문서 |
| **2.1.1 사용자 계정 관리** | 최소 권한 원칙, 정기 검토 | IAM 정책, Access Analyzer | IAM 검토 보고서 |
| **2.2.1 사용자 인증** | 강화된 인증 (MFA) | IAM MFA, Cognito MFA | MFA 활성화 현황 |
| **2.3.1 사용자 접근 통제** | 역할 기반 접근 제어 | IAM 역할, 정책 | 역할 매트릭스 |
| **2.4.1 네트워크 접근 통제** | IP 기반 접근 제어 | Security Groups, NACL | 네트워크 정책 |
| **2.5.1 응용 프로그램 접근 통제** | API 접근 제어 | API Gateway, WAF | API 정책 |
| **2.6.1 데이터베이스 접근 통제** | DB 접근 로그, 암호화 | RDS 감사 로그, 암호화 | 접근 로그 |
| **2.7.1 물리적 접근 통제** | 데이터센터 물리 보안 | AWS 인증서 (ISO 27001) | AWS 인증서 사본 |
| **2.8.1 모바일 기기 보안** | MDM, 데이터 암호화 | WorkSpaces, AppStream | MDM 정책 |
| **2.9.1 무선 네트워크 보안** | 암호화, 인증 | Client VPN, WPA3 | 무선 정책 |
| **2.10.1 원격 접근 보안** | VPN, MFA | Client VPN, IAM MFA | VPN 접속 로그 |

## 7. Board Reporting Format (경영진 보고 형식)

### 월간 클라우드 보안 현황 보고서

#### 1. 요약 (Executive Summary)

```
보고 기간: 2025년 2월 1일 - 2월 28일
보고 부서: 정보보안팀
보고 대상: 이사회, 경영진
```

| 지표 | 현재 | 전월 대비 | 목표 | 상태 |
|------|------|----------|------|------|
| **보안 사고 건수** | 2건 | ▼ 1건 | 0건 | 🟡 주의 |
| **평균 탐지 시간** | 4시간 | ▼ 20시간 | <24시간 | ✅ 양호 |
| **평균 대응 시간** | 12시간 | ▼ 36시간 | <48시간 | ✅ 양호 |
| **취약점 해결률** | 92% | ▲ 5% | >90% | ✅ 양호 |
| **컴플라이언스 준수율** | 98% | - | 100% | ✅ 양호 |

#### 2. 주요 보안 사고 (Security Incidents)

| 일자 | 유형 | 심각도 | 설명 | 영향 | 조치 사항 | 상태 |
|------|------|--------|------|------|----------|------|
| 2/5 | 무단 접근 시도 | 중간 | 외부 IP에서 SSH 브루트포스 공격 | 접근 실패 | IP 차단, 알림 | ✅ 해결 |
| 2/18 | 내부자 위협 | 높음 | 퇴사 직원 계정으로 S3 접근 시도 | 접근 차단 | 계정 비활성화, 조사 중 | 🔄 진행 중 |

#### 3. 위협 동향 (Threat Landscape)

```
이번 달 주요 위협:
1. Shadow AI 사용 증가 (전월 대비 40% 증가)
   - 승인되지 않은 ChatGPT, Claude 사용 탐지
   - 대응: AI 사용 정책 수립, 네트워크 모니터링 강화

2. 피싱 공격 증가 (전월 대비 25% 증가)
   - CEO 사칭 이메일 탐지
   - 대응: 이메일 필터링 강화, 전 직원 보안 교육

3. 클라우드 설정 오류
   - S3 버킷 퍼블릭 노출 1건 탐지 및 즉시 차단
   - 대응: 자동화된 S3 Public Access Block 적용
```

#### 4. 투자 권고 (Investment Recommendations)

| 항목 | 우선순위 | 예상 비용 | ROI | 권고 사항 |
|------|---------|----------|-----|----------|
| **AI 기반 위협 탐지** | 높음 | $50K/년 | 침해 사고 70% 감소 | 즉시 도입 권고 |
| **Zero Trust 아키텍처** | 높음 | $100K (초기) | 내부자 위협 90% 감소 | 6개월 내 구축 |
| **보안 교육 프로그램** | 중간 | $30K/년 | 피싱 피해 80% 감소 | 분기별 실시 |
| **PQC 전환 준비** | 낮음 | $200K (2026년) | 미래 양자 위협 대응 | 2026년 계획 수립 |

#### 5. 규제 준수 현황 (Compliance Status)

| 규제 | 준수 현황 | 미흡 사항 | 조치 계획 | 완료 예정일 |
|------|----------|----------|----------|------------|
| **ISMS-P** | 98% | 로그 보관 정책 미비 | 3년 보관 정책 수립 | 2025-03-15 |
| **개인정보보호법** | 100% | - | - | - |
| **금융보안 가이드** | 95% | 망분리 예외 승인 대기 | 금융보안원 승인 신청 | 2025-04-30 |

## 클라우드 인프라 보안 점검 체크리스트

### 네트워크 보안

- [ ] VPC 서브넷이 Public/Private으로 적절히 분리되어 있는가?
- [ ] 데이터베이스, 애플리케이션 서버가 Private 서브넷에 배치되어 있는가?
- [ ] Security Group 규칙이 최소 권한 원칙을 따르는가?
- [ ] 불필요한 인바운드 포트(0.0.0.0/0)가 개방되어 있지 않은가?
- [ ] VPC Flow Logs가 활성화되어 있는가?

### 접근 제어

- [ ] 루트 계정에 MFA가 활성화되어 있는가?
- [ ] 일상 업무에 IAM 사용자/역할을 사용하고 있는가?
- [ ] IAM 정책이 최소 권한 원칙을 따르는가?
- [ ] 하드코딩된 자격 증명이 코드에 포함되어 있지 않은가?
- [ ] Secrets Manager 또는 Parameter Store를 사용하고 있는가?

### 데이터 보호

- [ ] S3 버킷 기본 암호화가 활성화되어 있는가?
- [ ] S3 Public Access Block이 활성화되어 있는가?
- [ ] EBS 볼륨 암호화가 활성화되어 있는가?
- [ ] RDS 암호화가 활성화되어 있는가?
- [ ] 정기적인 백업 및 복구 테스트가 수행되고 있는가?

### 모니터링 및 감사

- [ ] CloudTrail이 모든 리전에서 활성화되어 있는가?
- [ ] CloudWatch 알람이 주요 지표에 설정되어 있는가?
- [ ] GuardDuty가 활성화되어 있는가?
- [ ] Security Hub가 활성화되어 있는가?
- [ ] 보안 이벤트에 대한 알림이 구성되어 있는가?

## 8. 실무 시나리오 및 트러블슈팅

### 시나리오 1: 대규모 DDoS 공격 대응

**상황**: 웹 애플리케이션에 대한 대규모 DDoS 공격 발생

**증상**:
- CloudWatch에서 비정상적인 트래픽 증가 감지
- 애플리케이션 응답 시간 급증
- 정상 사용자 접속 불가

**대응 절차**:

```bash
# 1. Shield Advanced 활성화 (아직 미활성화된 경우)
aws shield create-subscription

# 2. CloudFront 배포 확인 및 설정
aws cloudfront get-distribution --id DISTRIBUTION_ID

# 3. WAF 웹 ACL에 Rate Limiting 규칙 추가
aws wafv2 create-web-acl --name ddos-protection \
  --scope CLOUDFRONT \
  --default-action Block={} \
  --rules file://rate-limit-rules.json

# 4. Route53 Health Check 및 Failover 설정
aws route53 create-health-check --health-check-config \
  IPAddress=YOUR_IP,Port=443,Type=HTTPS,ResourcePath=/health

# 5. Shield Response Team (SRT) 연락 (Enterprise Support 계획)
# AWS Support Console에서 케이스 오픈
```

**예방 조치**:
- CloudFront + Shield Standard (기본 활성화)
- WAF Rate Limiting 규칙 사전 설정
- Auto Scaling 그룹 최대 용량 증가
- Route53 Health Check 및 Failover 라우팅

**참고**: [AWS Shield](https://aws.amazon.com/shield/)

### 시나리오 2: S3 버킷 데이터 유출 사고

**상황**: 실수로 S3 버킷이 퍼블릭으로 노출되어 민감 데이터 유출

**증상**:
- GuardDuty에서 "Exfiltration:S3/ObjectRead.Unusual" 알람
- CloudTrail에서 비정상적인 GetObject 호출 급증
- 외부 IP에서 대량 다운로드 탐지

**대응 절차**:

```bash
# 1. 즉시 버킷 퍼블릭 액세스 차단
aws s3api put-public-access-block \
  --bucket BUCKET_NAME \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# 2. 버킷 정책에서 퍼블릭 액세스 제거
aws s3api delete-bucket-policy --bucket BUCKET_NAME

# 3. CloudTrail 로그 분석 (누가, 언제, 무엇을 접근했는지)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=BUCKET_NAME \
  --start-time 2025-02-01T00:00:00Z

# 4. 접근한 IP 차단 (Security Group, NACL)
aws ec2 create-network-acl-entry --network-acl-id ACL_ID \
  --rule-number 100 --protocol -1 --rule-action deny \
  --cidr-block MALICIOUS_IP/32

# 5. 사고 보고서 작성 (개인정보 유출 시 72시간 내 개인정보보호위원회 신고)
```

**예방 조치**:
- S3 Public Access Block 기본 활성화 (계정 수준)
- S3 버킷 정책에서 퍼블릭 액세스 금지
- AWS Config 규칙으로 퍼블릭 버킷 자동 탐지
- Macie를 사용한 민감 데이터 자동 탐지

**참고**: [S3 보안 모범 사례](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

### 시나리오 3: 내부자 위협 - 퇴사 직원의 무단 접근

**상황**: 퇴사 직원의 계정으로 민감 데이터 접근 시도

**증상**:
- CloudTrail에서 비활성화된 직원 계정의 API 호출 탐지
- 비정상 시간대(새벽 2시)에 S3, RDS 접근
- 평소와 다른 IP(해외)에서 접근

**대응 절차**:

```bash
# 1. 즉시 계정 비활성화
aws iam delete-login-profile --user-name FORMER_EMPLOYEE

# 2. 모든 액세스 키 비활성화
aws iam list-access-keys --user-name FORMER_EMPLOYEE
aws iam delete-access-key --user-name FORMER_EMPLOYEE --access-key-id KEY_ID

# 3. 현재 세션 강제 종료
aws iam update-user --user-name FORMER_EMPLOYEE --no-password-reset-required

# 4. 접근한 리소스 확인 (CloudTrail 로그 분석)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=FORMER_EMPLOYEE \
  --start-time 2025-02-01T00:00:00Z

# 5. 접근한 데이터 검토 (S3 접근 로그)
aws s3api get-bucket-logging --bucket BUCKET_NAME

# 6. 필요 시 자격 증명 로테이션 (Secrets Manager)
aws secretsmanager rotate-secret --secret-id DATABASE_CREDENTIALS
```

**예방 조치**:
- 퇴사 시 자동화된 계정 비활성화 프로세스 (HR 시스템 연동)
- IAM 계정 정기 검토 (90일 미사용 계정 자동 비활성화)
- CloudWatch 알람 설정 (비활성 계정 접근 시도)
- 직무 분리 (Separation of Duties) 원칙 적용

### 시나리오 4: 컨테이너 이미지 취약점 악용

**상황**: 취약점이 있는 컨테이너 이미지가 프로덕션 환경에 배포됨

**증상**:
- ECR 이미지 스캔에서 Critical 취약점 탐지
- GuardDuty에서 "CryptoCurrency:EC2/BitcoinTool.B!DNS" 알람
- 비정상적인 아웃바운드 트래픽 급증

**대응 절차**:

```bash
# 1. 영향받는 컨테이너 식별
aws ecr describe-image-scan-findings \
  --repository-name APP_REPO \
  --image-id imageTag=VULNERABLE_TAG

# 2. 영향받는 ECS 태스크 중지
aws ecs stop-task --cluster CLUSTER_NAME --task TASK_ARN

# 3. 새로운 패치된 이미지 빌드 및 배포
docker build -t APP_REPO:PATCHED_TAG .
docker push APP_REPO:PATCHED_TAG

# 4. ECS 서비스 업데이트
aws ecs update-service --cluster CLUSTER_NAME \
  --service SERVICE_NAME \
  --force-new-deployment

# 5. 컨테이너 로그 분석 (침해 여부 확인)
aws logs filter-log-events --log-group-name /ecs/APP \
  --start-time TIMESTAMP --filter-pattern "crypto"
```

**예방 조치**:
- ECR 이미지 스캔 자동화 (푸시 시 스캔)
- CI/CD 파이프라인에 이미지 스캔 통합 (취약점 발견 시 빌드 실패)
- 정기적인 베이스 이미지 업데이트
- 불필요한 패키지 제거 (최소 이미지 원칙)

**참고**: [ECR 이미지 스캔](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html)

## 9. 자동화 및 IaC (Infrastructure as Code)

### Terraform을 사용한 보안 강화 인프라 구축

```hcl
# AWS 클라우드 보안 강화 인프라 (Terraform)

# VPC 생성 (Private/Public 서브넷 분리)
resource "aws_vpc" "secure_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "secure-vpc"
  }
}

# Private 서브넷 (데이터베이스, 애플리케이션)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.secure_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-subnet-${count.index + 1}"
  }
}

# Security Hub 활성화
resource "aws_securityhub_account" "main" {}

# GuardDuty 활성화
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
  }
}

# CloudTrail 활성화 (모든 리전)
resource "aws_cloudtrail" "main" {
  name                          = "security-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
}

# S3 버킷 (암호화 강제)
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"

  tags = {
    Name = "secure-bucket"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# S3 Public Access Block (계정 수준)
resource "aws_s3_account_public_access_block" "main" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM 정책 (최소 권한)
resource "aws_iam_policy" "least_privilege" {
  name        = "least-privilege-policy"
  description = "Least privilege policy for EC2"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.secure_bucket.arn}/*"
      }
    ]
  })
}

# 참고: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
```

### AWS Config 규칙으로 컴플라이언스 자동화

```python
# AWS Config 사용자 정의 규칙 (Lambda)
# S3 버킷 퍼블릭 액세스 자동 차단

import boto3
import json

def lambda_handler(event, context):
    """
    S3 버킷이 퍼블릭으로 설정되면 자동으로 차단
    """
    s3 = boto3.client('s3')
    config = boto3.client('config')

    # Config에서 전달받은 이벤트 파싱
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event['configurationItem']

    if configuration_item['resourceType'] != 'AWS::S3::Bucket':
        return

    bucket_name = configuration_item['resourceName']

    # 버킷 ACL 확인
    try:
        acl = s3.get_bucket_acl(Bucket=bucket_name)

        # 퍼블릭 액세스 여부 확인
        is_public = any(
            grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
            for grant in acl['Grants']
        )

        if is_public:
            # 자동으로 Public Access Block 적용
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )

            # Config에 NON_COMPLIANT 보고
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType': 'AWS::S3::Bucket',
                        'ComplianceResourceId': bucket_name,
                        'ComplianceType': 'NON_COMPLIANT',
                        'Annotation': f'Bucket {bucket_name} was public. Auto-remediated.',
                        'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
                    }
                ],
                ResultToken=event['resultToken']
            )

    except Exception as e:
        print(f"Error: {str(e)}")

# 참고: https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules.html
```

## 10. 참고 자료 (Comprehensive References)

### 공식 문서

| 자료 | 링크 | 설명 |
|------|------|------|
| **AWS 보안 모범 사례** | [https://aws.amazon.com/security/best-practices/](https://aws.amazon.com/security/best-practices/) | AWS 보안 공식 가이드 |
| **AWS Well-Architected Framework - Security Pillar** | [https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) | 보안 설계 원칙 |
| **CIS AWS Foundations Benchmark** | [https://www.cisecurity.org/benchmark/amazon_web_services](https://www.cisecurity.org/benchmark/amazon_web_services) | AWS 보안 기준 |
| **NIST Cybersecurity Framework** | [https://www.nist.gov/cyberframework](https://www.nist.gov/cyberframework) | 사이버보안 프레임워크 |

### 보안 표준 및 프레임워크

| 표준/프레임워크 | 링크 | 설명 |
|---------------|------|------|
| **MITRE ATT&CK for Cloud** | [https://attack.mitre.org/matrices/enterprise/cloud/](https://attack.mitre.org/matrices/enterprise/cloud/) | 클라우드 공격 기법 |
| **MITRE ATLAS** | [https://atlas.mitre.org/](https://atlas.mitre.org/) | AI/ML 보안 위협 |
| **OWASP Top 10** | [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/) | 웹 애플리케이션 보안 |
| **OWASP Top 10 for LLM** | [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | LLM 보안 위협 |
| **CNCF Security Whitepaper** | [https://github.com/cncf/tag-security](https://github.com/cncf/tag-security) | 클라우드 네이티브 보안 |
| **Zero Trust Architecture (NIST SP 800-207)** | [https://csrc.nist.gov/publications/detail/sp/800-207/final](https://csrc.nist.gov/publications/detail/sp/800-207/final) | Zero Trust 표준 |

### 한국 규제 및 가이드

| 규제/가이드 | 링크 | 설명 |
|-----------|------|------|
| **ISMS-P 인증 기준** | [https://isms.kisa.or.kr/](https://isms.kisa.or.kr/) | 정보보호 및 개인정보보호 관리체계 |
| **개인정보보호법** | [https://www.privacy.go.kr/](https://www.privacy.go.kr/) | 개인정보 보호 관련 법령 |
| **금융분야 클라우드컴퓨팅서비스 이용 가이드** | [https://www.fss.or.kr/](https://www.fss.or.kr/) | 금융권 클라우드 보안 |
| **전자금융거래법** | [https://www.law.go.kr/](https://www.law.go.kr/) | 전자금융 보안 규정 |

### AWS 보안 서비스

| 서비스 | 링크 | 설명 |
|--------|------|------|
| **AWS CloudTrail** | [https://docs.aws.amazon.com/cloudtrail/](https://docs.aws.amazon.com/cloudtrail/) | API 호출 로깅 및 감사 |
| **AWS GuardDuty** | [https://docs.aws.amazon.com/guardduty/](https://docs.aws.amazon.com/guardduty/) | 지능형 위협 탐지 |
| **AWS Security Hub** | [https://docs.aws.amazon.com/securityhub/](https://docs.aws.amazon.com/securityhub/) | 보안 태세 통합 관리 |
| **AWS Secrets Manager** | [https://docs.aws.amazon.com/secretsmanager/](https://docs.aws.amazon.com/secretsmanager/) | 자격 증명 관리 |
| **AWS KMS** | [https://docs.aws.amazon.com/kms/](https://docs.aws.amazon.com/kms/) | 암호화 키 관리 |
| **AWS IAM Identity Center** | [https://docs.aws.amazon.com/singlesignon/](https://docs.aws.amazon.com/singlesignon/) | 통합 인증 및 접근 관리 |
| **AWS Shield** | [https://docs.aws.amazon.com/shield/](https://docs.aws.amazon.com/shield/) | DDoS 방어 |
| **AWS WAF** | [https://docs.aws.amazon.com/waf/](https://docs.aws.amazon.com/waf/) | 웹 애플리케이션 방화벽 |

### 블로그 및 커뮤니티

| 자료 | 링크 | 설명 |
|------|------|------|
| **AWS Security Blog** | [https://aws.amazon.com/blogs/security/](https://aws.amazon.com/blogs/security/) | AWS 보안 공식 블로그 |
| **AWS re:Inforce** | [https://reinforce.awsevents.com/](https://reinforce.awsevents.com/) | AWS 보안 컨퍼런스 |
| **Kubernetes Security Best Practices** | [https://kubernetes.io/docs/concepts/security/](https://kubernetes.io/docs/concepts/security/) | Kubernetes 보안 |
| **SANS Cloud Security** | [https://www.sans.org/cloud-security/](https://www.sans.org/cloud-security/) | 클라우드 보안 교육 |

### 도구 및 오픈소스

| 도구 | 링크 | 설명 |
|------|------|------|
| **Prowler** | [https://github.com/prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | AWS 보안 평가 도구 |
| **ScoutSuite** | [https://github.com/nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | 멀티 클라우드 보안 감사 |
| **CloudSploit** | [https://github.com/aquasecurity/cloudsploit](https://github.com/aquasecurity/cloudsploit) | 클라우드 보안 스캐너 |
| **Falco** | [https://falco.org/](https://falco.org/) | 런타임 보안 모니터링 |
| **Trivy** | [https://github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) | 컨테이너 이미지 스캐너 |
| **Terraform AWS Modules** | [https://registry.terraform.io/modules/terraform-aws-modules/](https://registry.terraform.io/modules/terraform-aws-modules/) | AWS 인프라 IaC 모듈 |

### 인증 및 교육

| 인증/교육 | 링크 | 설명 |
|---------|------|------|
| **AWS Certified Security - Specialty** | [https://aws.amazon.com/certification/certified-security-specialty/](https://aws.amazon.com/certification/certified-security-specialty/) | AWS 보안 전문가 인증 |
| **CISSP** | [https://www.isc2.org/Certifications/CISSP](https://www.isc2.org/Certifications/CISSP) | 정보보안 전문가 인증 |
| **CCSP** | [https://www.isc2.org/Certifications/CCSP](https://www.isc2.org/Certifications/CCSP) | 클라우드 보안 전문가 인증 |
| **AWS Skill Builder** | [https://skillbuilder.aws/](https://skillbuilder.aws/) | AWS 무료 교육 플랫폼 |

## 결론

클라우드 시큐리티 8기 1주차에서는 **인프라의 본질부터 보안의 미래까지** 다뤘습니다.

**인프라의 본질**에서는 클라우드 인프라의 핵심 구성 요소(네트워크, 컴퓨팅, 스토리지)와 보안 관점에서의 인프라 설계 원칙을 살펴봤습니다. 방어의 깊이, 최소 권한 원칙, 모니터링 및 감사가 클라우드 보안의 기초가 됩니다.

**보안의 미래**에서는 2025년 클라우드 보안의 핵심 트렌드를 다뤘습니다:

| 트렌드 | 주요 내용 | 실무 적용 포인트 |
|--------|----------|----------------|
| **AI 보안** | AI 기반 위협과 방어 도구의 진화 | Shadow AI 모니터링, AI 탐지 도구 도입 |
| **Zero Trust** | 지속적 검증과 동적 권한 관리 | 위험도 기반 접근 제어, 지속적 모니터링 |
| **클라우드 네이티브 보안** | 컨테이너와 Kubernetes 보안의 고도화 | 이미지 스캔, 네트워크 정책, 런타임 보호 |
| **규제 및 컴플라이언스** | AI Act, ISMS-P 등 새로운 규제 대응 | AI 거버넌스 프레임워크, 데이터 지역화 검토 |
| **FinOps와 보안의 융합** | 비용 효율적인 보안 운영 | 보안 투자 ROI 측정, 비용 인식 보안 |
| **Post-Quantum 암호화** | 양자 컴퓨팅 위협 대응 | NIST PQC 표준 알고리즘 전환 준비 |

**실무에서 자주 발생하는 인프라 보안 이슈**에서는 네트워크 보안, 접근 제어, 데이터 보호 영역의 주요 이슈와 대응 방안을 표 형식으로 정리했습니다. 이러한 이슈들을 사전에 인지하고 대응하는 것이 중요합니다.

**MITRE ATT&CK 매핑**을 통해 클라우드 환경의 실제 공격 기법과 탐지 방법, 대응 조치를 구체적으로 이해할 수 있었습니다. 공격자의 관점에서 방어 전략을 수립하는 것이 효과적입니다.

**한국 기업 환경 분석**에서는 국내 특유의 규제 환경(ISMS-P, 금융보안 가이드, 망분리)과 대응 방안을 다뤘습니다. 글로벌 표준과 함께 국내 규제를 준수하는 것이 중요합니다.

클라우드 보안은 단순한 기술 구현이 아닌, 인프라의 본질을 이해하고 미래 트렌드를 선제적으로 대응하는 전략적 접근이 필요합니다. 올바른 인프라 설계와 지속적인 보안 모니터링을 통해 안전하고 효율적인 클라우드 환경을 구축할 수 있습니다. 특히 2025년에는 AI 보안, Zero Trust 아키텍처, Post-Quantum 암호화가 핵심 트렌드로 부상했으며, 이러한 트렌드를 선제적으로 대응하는 것이 핵심입니다.

---

**원본 포스트**: [클라우드 시큐리티 8기 1주차: 인프라의 본질부터 보안의 미래까지](https://twodragon.tistory.com/701)

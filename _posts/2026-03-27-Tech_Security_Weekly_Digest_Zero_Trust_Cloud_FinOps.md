---
layout: post
title: "AWS IAM Zero Trust 구현, GCP Workload Identity 보안, FinOps 비용 최적화 - 보안 주간 다이제스트"
date: 2026-03-27 10:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Trust, Cloud, FinOps]
excerpt: "AWS IAM Identity Center + SCP 기반 Zero Trust 구현, GCP Workload Identity Federation 보안, FinOps Spot/Graviton 비용 최적화, Terraform Stacks IaC 보안 스캔, CloudTrail + GuardDuty 통합 위협 탐지 등 2026년 03월 27일 주요 보안/기술 뉴스의 위협 분석과 DevSecOps 대응 우선순위를 정리합니다."
description: "2026년 03월 27일 보안 뉴스 요약. Zero Trust 아키텍처, 클라우드 보안 설계, FinOps 비용 최적화, Terraform IaC 보안, CloudTrail/GuardDuty 위협 탐지 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Trust, Cloud, FinOps]
author: Twodragon
comments: true
image: /assets/images/2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg
image_alt: "AWS IAM Zero Trust, GCP Workload Identity security, FinOps cost optimization digest"
toc: true
---

{% include ai-summary-card.html
  title='AWS IAM Zero Trust 구현, GCP Workload Identity 보안, FinOps 비용 최적화'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">Cloud</span>
      <span class="tag">FinOps</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>AWS Security</strong>: IAM Identity Center + SCP 기반 Zero Trust 아키텍처 구현 가이드</li>
      <li><strong>GCP Security</strong>: Workload Identity Federation 보안 베스트 프랙티스와 키 없는 인증</li>
      <li><strong>FinOps</strong>: Spot/Graviton 인스턴스 비용 최적화 전략과 실무 사례</li>
      <li><strong>IaC Security</strong>: Terraform Stacks와 tfsec/checkov 기반 보안 스캔 자동화</li>'
  period='2026년 03월 27일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 03월 27일 기준, Zero Trust 아키텍처, 클라우드 보안 설계, FinOps 비용 최적화를 중심으로 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 24개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 6개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 4개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | AWS Security Blog | IAM Identity Center + SCP 기반 Zero Trust 아키텍처 구현 | 🔴 Critical |
| ☁️ **Cloud** | Google Cloud Blog | Workload Identity Federation 보안 베스트 프랙티스 | 🟠 High |
| 💰 **FinOps** | AWS Blog | Spot/Graviton 인스턴스 비용 최적화 전략 | 🟠 High |
| 🔒 **Security** | HashiCorp Blog | Terraform Stacks와 IaC 보안 스캔(tfsec, checkov) | 🟠 High |
| 🔒 **Security** | AWS Security Blog | CloudTrail + GuardDuty 통합 위협 탐지 아키텍처 | 🟠 High |
| ⚙️ **DevOps** | Terraform Blog | Terraform 1.10 신규 기능과 보안 개선 사항 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: AWS IAM 장기 액세스 키를 사용하는 조직은 IAM Identity Center 기반 Zero Trust 아키텍처로의 전환이 시급합니다. 2026년 4월부터 AWS가 장기 액세스 키에 대한 보안 경고를 강화합니다.
- **주요 모니터링 대상**: GCP Workload Identity Federation 미적용 워크로드의 서비스 계정 키 노출 위험이 증가하고 있으며, CloudTrail과 GuardDuty의 통합 설정을 검토하여 위협 탐지 범위를 확대해야 합니다.
- FinOps 관점에서 Spot/Graviton 인스턴스 전환을 통해 연간 클라우드 비용의 30~60% 절감이 가능하며, 보안 수준을 유지하면서 비용을 최적화하는 전략이 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| IAM/인증 | Critical | 장기 액세스 키 사용 현황 점검 및 Identity Center 전환 |
| 클라우드 보안 | High | Workload Identity Federation 적용 및 키 없는 인증 전환 |
| IaC 보안 | High | Terraform 코드 보안 스캔 파이프라인 구축 |
| 위협 탐지 | Medium | CloudTrail + GuardDuty 통합 설정 및 경보 체계 구축 |

---

## 1. Zero Trust 아키텍처

### 1.1 AWS IAM Identity Center + SCP 기반 Zero Trust 구현

> 🔴 **심각도**: Critical

## 1. 기술적 배경 및 위협 분석
AWS는 2026년 4월부터 장기 IAM 액세스 키에 대한 보안 경고를 강화하며, IAM Identity Center(구 AWS SSO) 기반의 단기 자격 증명(Short-lived credentials) 사용을 강력히 권고하고 있습니다. Zero Trust 모델에서 "절대 신뢰하지 말고, 항상 검증하라"는 원칙은 AWS 환경에서 **IAM Identity Center + SCP(Service Control Policies) + VPC 엔드포인트 정책**의 조합으로 구현됩니다.

핵심 위협은 장기 액세스 키의 유출입니다. GitHub 공개 저장소에서 노출된 AWS 액세스 키를 통한 무단 접근 사례가 2026년 1분기에만 전년 대비 45% 증가했습니다. SCP를 활용한 조직 수준의 권한 경계 설정은 개별 계정의 보안 설정 오류를 보완하는 안전망 역할을 합니다.

## 2. 실무 영향 분석
IAM Identity Center로의 전환은 단순한 인증 방식 변경이 아닌, 조직의 전체 접근 제어 아키텍처를 재설계하는 작업입니다. 특히 멀티 어카운트 환경에서 SCP를 통한 가드레일 설정은 개발팀의 자율성을 보장하면서도 보안 경계를 유지하는 데 필수적입니다. 기존에 프로그래밍 방식으로 장기 키를 사용하던 워크로드는 IAM Roles Anywhere 또는 OIDC Federation으로의 전환이 필요합니다.

## 3. 대응 체크리스트
- [ ] **장기 IAM 액세스 키 인벤토리 생성**: `aws iam list-access-keys`로 모든 사용자의 액세스 키 목록을 생성하고, 90일 이상 사용된 키를 식별합니다.
- [ ] **IAM Identity Center 활성화 및 설정**: 조직의 AWS Organizations에서 IAM Identity Center를 활성화하고, IdP(Identity Provider)를 연동합니다.
- [ ] **SCP 기반 가드레일 배포**: 루트 사용자 사용 금지, 특정 리전 외 서비스 사용 금지, CloudTrail 비활성화 금지 등의 SCP를 배포합니다.
- [ ] **VPC 엔드포인트 정책 구성**: S3, DynamoDB 등 주요 서비스에 대해 VPC 엔드포인트를 통한 접근만 허용하는 정책을 구성합니다.
- [ ] **조건부 접근 정책 구현**: IP 기반, MFA 기반, 시간 기반 조건부 접근 정책을 IAM 정책에 적용합니다.

```json
// SCP 예시: 주요 보안 서비스 비활성화 방지
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PreventCloudTrailDisable",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail",
        "guardduty:DeleteDetector",
        "guardduty:DisassociateFromMasterAccount",
        "config:StopConfigurationRecorder",
        "config:DeleteConfigurationRecorder"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalArn": [
            "arn:aws:iam::*:role/SecurityAdmin"
          ]
        }
      }
    },
    {
      "Sid": "DenyLongTermAccessKeys",
      "Effect": "Deny",
      "Action": "iam:CreateAccessKey",
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalArn": [
            "arn:aws:iam::*:role/EmergencyAccess"
          ]
        }
      }
    }
  ]
}
```

---

### 1.2 조건부 접근 정책과 세션 기반 인증

> 🟠 **심각도**: High

#### 요약

Zero Trust 아키텍처의 핵심은 "모든 요청을 검증"하는 것이며, AWS 환경에서 이를 구현하는 가장 효과적인 방법은 조건부 접근 정책입니다. IAM 정책의 Condition 블록을 활용하여 IP 주소, MFA 상태, 요청 시간, 소스 VPC 등 다양한 조건을 기반으로 접근을 제어할 수 있습니다.

**실무 포인트**: 프로덕션 환경 접근 시 반드시 MFA를 요구하고, 세션 기간을 최소화(최대 4시간)하는 정책을 적용하세요.

#### 실무 적용 포인트

- IAM 정책 Condition 블록으로 MFA, IP, VPC, 시간 기반 접근 제어 구현
- STS AssumeRole 세션 기간을 워크로드 특성에 맞게 최소화
- AWS Config Rules로 과도한 권한을 가진 IAM 엔티티 자동 탐지

```json
// 프로덕션 환경 MFA 강제 정책 예시
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireMFAForProduction",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-2"
        },
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        },
        "StringLike": {
          "aws:PrincipalTag/Environment": "production"
        }
      }
    }
  ]
}
```

---

## 2. 클라우드 보안 설계

### 2.1 GCP Workload Identity Federation 보안 베스트 프랙티스

> 🟠 **심각도**: High

## 1. 기술적 배경 및 위협 분석
GCP Workload Identity Federation은 외부 워크로드(AWS, Azure, GitHub Actions, Kubernetes)가 서비스 계정 키 없이 GCP 리소스에 접근할 수 있도록 하는 키 없는 인증(Keyless Authentication) 메커니즘입니다. 서비스 계정 키는 유출 시 장기간 악용이 가능한 고위험 자격 증명으로, 2025년 Google Cloud의 보안 보고서에 따르면 클라우드 보안 사고의 35%가 유출된 서비스 계정 키에서 시작되었습니다.

## 2. 실무 영향 분석
Workload Identity Federation을 적용하면 서비스 계정 키 관리 부담이 완전히 제거되며, 자격 증명 유출 위험이 원천적으로 차단됩니다. 특히 CI/CD 파이프라인(GitHub Actions, GitLab CI)에서 GCP 리소스에 접근할 때, OIDC 토큰 기반 인증으로 전환하면 파이프라인 보안이 대폭 강화됩니다.

## 3. 대응 체크리스트
- [ ] **서비스 계정 키 인벤토리 생성**: `gcloud iam service-accounts keys list`로 모든 서비스 계정의 키 목록을 생성하고, 90일 이상 사용된 키를 식별합니다.
- [ ] **Workload Identity Pool 생성**: 외부 ID 공급자(AWS, Azure AD, OIDC)에 대한 Workload Identity Pool을 생성합니다.
- [ ] **Attribute Mapping 구성**: 외부 토큰의 클레임을 GCP IAM 속성에 매핑하여 세밀한 접근 제어를 구현합니다.
- [ ] **Attribute Condition 설정**: 특정 조건(리포지토리, 브랜치, 환경)을 충족하는 요청만 인증되도록 조건을 설정합니다.
- [ ] **서비스 계정 키 순환 및 폐기 계획 수립**: Workload Identity Federation 전환 후 기존 키를 순차적으로 폐기합니다.

```yaml
# GitHub Actions에서 GCP Workload Identity Federation 사용 예시
name: Deploy to GCP
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'deploy-sa@my-project.iam.gserviceaccount.com'

      - name: Deploy to GKE
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: my-service
          region: asia-northeast3
          image: gcr.io/my-project/my-app:${{ github.sha }}
```

---

### 2.2 CloudTrail + GuardDuty 통합 위협 탐지 아키텍처

> 🟠 **심각도**: High

#### 요약

AWS CloudTrail과 GuardDuty를 통합하여 클라우드 환경의 위협을 실시간으로 탐지하는 아키텍처가 2026년 AWS 보안 모범 사례로 재정립되었습니다. GuardDuty는 CloudTrail 관리 이벤트, VPC Flow Logs, DNS 로그를 분석하여 비정상적인 API 호출, 암호화폐 채굴, 자격 증명 탈취 시도 등을 탐지합니다.

**실무 포인트**: 모든 리전에서 GuardDuty를 활성화하고, S3 Protection/EKS Protection/Malware Protection 기능을 추가로 활성화하세요.

#### 위협 분석

| 항목 | 내용 |
|------|------|
| **위협 유형** | 클라우드 자격 증명 탈취, 내부 위협, 암호화폐 채굴 |
| **심각도** | High |
| **대응 우선순위** | P1 - 7일 이내 구축 권장 |

#### 권장 조치

- [ ] 모든 AWS 리전에서 GuardDuty 활성화
- [ ] S3 Protection, EKS Audit Log Monitoring, Malware Protection 추가 활성화
- [ ] GuardDuty 결과를 Security Hub로 집약하여 중앙 관리
- [ ] 고위험 결과(Severity 7.0+)에 대한 자동 대응 Lambda 함수 구성
- [ ] EventBridge 규칙으로 Slack/PagerDuty 실시간 알림 설정

```python
# GuardDuty 고위험 결과 자동 대응 Lambda 예시
import json
import boto3
import os

iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

ALERT_TOPIC_ARN = os.environ['ALERT_TOPIC_ARN']

def lambda_handler(event, context):
    """GuardDuty finding auto-response handler."""
    detail = event.get('detail', {})
    finding_type = detail.get('type', '')
    severity = detail.get('severity', 0)

    # High severity finding auto-response
    if severity >= 7.0:
        resource = detail.get('resource', {})

        # Compromised IAM credentials - disable access key
        if 'UnauthorizedAccess:IAMUser' in finding_type:
            access_key_id = (
                resource.get('accessKeyDetails', {})
                .get('accessKeyId', '')
            )
            if access_key_id:
                user_name = (
                    resource.get('accessKeyDetails', {})
                    .get('userName', '')
                )
                iam_client.update_access_key(
                    UserName=user_name,
                    AccessKeyId=access_key_id,
                    Status='Inactive'
                )

        # Crypto mining - isolate EC2 instance
        if 'CryptoCurrency' in finding_type:
            instance_id = (
                resource.get('instanceDetails', {})
                .get('instanceId', '')
            )
            if instance_id:
                ec2_client.modify_instance_attribute(
                    InstanceId=instance_id,
                    Groups=['sg-isolation']  # Isolation SG
                )

        # Send alert notification
        sns_client.publish(
            TopicArn=ALERT_TOPIC_ARN,
            Subject=f'GuardDuty Alert: {finding_type}',
            Message=json.dumps(detail, indent=2, default=str)
        )

    return {'statusCode': 200}
```

---

## 3. FinOps 비용 최적화

### 3.1 Spot/Graviton 인스턴스 비용 최적화 전략

> 🟠 **심각도**: High

## 1. 기술적 배경 및 분석
FinOps(Financial Operations) 관점에서 클라우드 비용 최적화는 단순한 비용 절감이 아닌, **보안 수준을 유지하면서 비용 효율성을 극대화**하는 전략입니다. AWS Spot 인스턴스는 온디맨드 대비 최대 90% 할인된 가격으로 제공되며, Graviton3/4 프로세서 기반 인스턴스는 x86 대비 40% 향상된 가성비를 제공합니다.

2026년 기준 AWS의 Spot 인스턴스 중단율은 평균 5% 미만으로 안정화되었으며, Karpenter(Kubernetes 노드 오토스케일러)와의 조합을 통해 Spot 중단에 대한 자동 복구가 가능해졌습니다.

## 2. 실무 영향 분석
보안 워크로드에서도 Spot 인스턴스의 활용이 확대되고 있습니다. SIEM 로그 처리, 취약점 스캔, 침투 테스트 환경 등 일시적 중단이 허용되는 보안 워크로드에 Spot을 적용하면 상당한 비용 절감이 가능합니다. Graviton 인스턴스는 동일 성능 대비 에너지 소비가 60% 적어 ESG(Environmental, Social, Governance) 목표 달성에도 기여합니다.

## 3. 비용 최적화 체크리스트
- [ ] **현재 인스턴스 유형별 비용 분석**: AWS Cost Explorer에서 인스턴스 유형별 비용을 분석하고, Graviton 전환 대상을 식별합니다.
- [ ] **Spot 적합 워크로드 식별**: 스테이트리스 웹 서버, 배치 처리, CI/CD 러너, 로그 처리 등 Spot 적합 워크로드를 식별합니다.
- [ ] **Karpenter 기반 Spot 관리 구성**: Kubernetes 환경에서 Karpenter를 통해 Spot/On-Demand 혼합 전략을 자동화합니다.
- [ ] **Graviton 마이그레이션 계획 수립**: ARM64 호환성 테스트를 수행하고, 단계적 마이그레이션 계획을 수립합니다.
- [ ] **비용 경보 및 예산 설정**: AWS Budgets로 월별 비용 경보를 설정하고, 이상 비용 발생 시 자동 알림을 구성합니다.

```yaml
# Karpenter NodePool - Spot/Graviton 혼합 전략 예시
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: cost-optimized
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: kubernetes.io/arch
          operator: In
          values: ["arm64", "amd64"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values:
            - m7g.large      # Graviton3
            - m7g.xlarge
            - c7g.large      # Graviton3 Compute
            - c7g.xlarge
            - m6i.large      # x86 fallback
            - c6i.large
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
  limits:
    cpu: "100"
    memory: 400Gi
  weight: 50
```

---

### 3.2 FinOps 대시보드와 비용 거버넌스

> 🟡 **심각도**: Medium

#### 요약

FinOps Foundation의 2026 State of FinOps 보고서에 따르면, 클라우드 비용 최적화를 체계적으로 수행하는 조직은 그렇지 않은 조직 대비 평균 35% 낮은 클라우드 비용을 유지합니다. 핵심은 비용 가시성(Visibility), 최적화(Optimization), 거버넌스(Governance)의 세 축을 균형 있게 운영하는 것입니다.

**실무 포인트**: 팀별 비용 할당 태그를 강제화하고, 월별 비용 리뷰 프로세스를 수립하세요.

#### 실무 적용 포인트

- AWS Cost Allocation Tags 강제화 (SCP로 태그 미부착 리소스 생성 차단)
- Kubecost를 활용한 Kubernetes 네임스페이스별 비용 추적
- Reserved Instances/Savings Plans 커버리지 최적화 (80% 이상 목표)
- 미사용 리소스(Idle EBS, Unused EIP, Stopped EC2) 자동 정리

---

## 4. IaC 보안

### 4.1 Terraform Stacks와 tfsec/checkov 기반 IaC 보안 스캔

> 🟠 **심각도**: High

## 1. 기술적 배경 및 위협 분석
Terraform Stacks는 HashiCorp가 2026년 초 정식 출시한 멀티 환경(dev/staging/prod) 배포 관리 기능입니다. 기존 Terraform Workspaces의 한계를 극복하여, 단일 구성으로 여러 환경과 리전에 일관된 인프라를 배포할 수 있습니다. 그러나 IaC 코드의 보안 결함은 인프라 전체에 즉시 전파되므로, **배포 전 보안 스캔이 필수**입니다.

tfsec과 checkov는 Terraform 코드의 보안 취약점을 정적 분석하는 대표적인 도구입니다. 공개 S3 버킷, 암호화되지 않은 RDS, 과도한 보안 그룹 규칙 등 일반적인 클라우드 보안 설정 오류를 CI/CD 파이프라인에서 자동으로 탐지합니다.

## 2. 실무 영향 분석
IaC 보안 스캔을 CI/CD에 통합하면 인프라 배포 전 보안 문제를 사전에 차단할 수 있습니다. 특히 Terraform Stacks 환경에서는 하나의 보안 결함이 모든 환경에 전파될 수 있으므로, PR 단계에서의 자동 스캔이 더욱 중요합니다.

## 3. 대응 체크리스트
- [ ] **tfsec/checkov CI/CD 통합**: GitHub Actions/GitLab CI에서 Terraform 코드 변경 시 자동으로 보안 스캔을 실행합니다.
- [ ] **커스텀 정책 작성**: 조직 특화 보안 요구사항(예: 특정 태그 필수, 특정 리전만 허용)에 대한 커스텀 정책을 작성합니다.
- [ ] **Severity 기반 차단 정책**: High/Critical 취약점 발견 시 PR 머지를 자동 차단하는 정책을 구성합니다.
- [ ] **정기적 전체 스캔 실행**: 주간 단위로 전체 Terraform 코드베이스에 대한 보안 스캔을 실행합니다.

```yaml
# GitHub Actions - Terraform 보안 스캔 파이프라인
name: Terraform Security Scan
on:
  pull_request:
    paths:
      - 'terraform/**'

jobs:
  tfsec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: tfsec scan
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: terraform/
          soft_fail: false  # High/Critical 발견 시 실패

  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: checkov scan
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          check: CKV_AWS_18,CKV_AWS_19,CKV_AWS_145  # S3 encryption, logging
          soft_fail: false
```

---

## 5. DevOps & 자동화

### 5.1 Terraform 1.10 보안 개선 사항

> 🟡 **심각도**: Medium

#### 요약

Terraform 1.10이 릴리스되면서 보안 관련 주요 개선 사항이 포함되었습니다. Ephemeral Values 기능이 정식 지원되어 민감 데이터가 State 파일에 저장되지 않도록 제어할 수 있으며, Provider 설치 시 서명 검증이 강화되었습니다.

**실무 포인트**: Terraform 1.10으로 업그레이드하고, 민감 변수에 ephemeral 플래그를 적용하여 State 파일의 보안을 강화하세요.

#### 실무 적용 포인트

- Ephemeral Values로 패스워드, API 키 등 민감 데이터의 State 저장 방지
- Provider Lock File(`.terraform.lock.hcl`) 기반 공급망 보안 강화
- State 파일 암호화 및 접근 제어 정책 점검

---

### 5.2 OPA/Conftest 기반 정책 코드화(Policy as Code)

> 🟡 **심각도**: Medium

#### 요약

OPA(Open Policy Agent)와 Conftest를 활용한 정책 코드화가 IaC 보안의 핵심 프랙티스로 자리잡고 있습니다. Terraform Plan 출력을 Conftest로 검증하여, 보안 정책 위반 여부를 배포 전에 자동으로 확인할 수 있습니다.

**실무 포인트**: Rego 언어로 조직 보안 정책을 코드화하고, CI/CD 파이프라인에 Conftest 검증 단계를 추가하세요.

#### 실무 적용 포인트

- Rego 기반 보안 정책 라이브러리 구축 (리소스 태깅, 암호화, 네트워크 격리)
- Terraform Plan JSON 출력에 대한 Conftest 검증 자동화
- 정책 위반 사항의 Jira/Slack 자동 알림 연동

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| AWS Config Conformance Packs 업데이트 | AWS Blog | CIS Benchmark, NIST 800-53 등 컴플라이언스 팩이 최신 표준에 맞게 업데이트 |
| Infracost로 Terraform 비용 예측 자동화 | Infracost Blog | PR 단계에서 인프라 변경에 따른 비용 영향을 자동 코멘트로 제공 |
| OpenTofu 1.9 릴리스 | OpenTofu Blog | Terraform 포크인 OpenTofu가 State 암호화와 Provider 미러링 기능 추가 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **Zero Trust** | 5건 | IAM Identity Center, SCP, 조건부 접근, MFA |
| **클라우드 보안** | 5건 | Workload Identity, CloudTrail, GuardDuty, VPC |
| **FinOps** | 4건 | Spot, Graviton, Karpenter, Cost Allocation |
| **IaC 보안** | 3건 | Terraform, tfsec, checkov, Policy as Code |
| **위협 탐지** | 2건 | GuardDuty, Security Hub, EventBridge |

이번 주기의 핵심 트렌드는 **Zero Trust**(5건)와 **클라우드 보안**(5건)입니다. AWS IAM Identity Center 기반 Zero Trust 구현과 GCP Workload Identity Federation이 주요 이슈입니다. **FinOps** 분야에서는 Spot/Graviton 인스턴스 전환을 통한 비용 최적화가 실무 사례와 함께 주목받고 있으며, **IaC 보안** 분야에서는 Terraform Stacks와 보안 스캔 자동화가 핵심 과제입니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **AWS 장기 IAM 액세스 키 인벤토리** 생성 및 IAM Identity Center 전환 계획 수립
- [ ] **GCP 서비스 계정 키 사용 현황** 점검 및 Workload Identity Federation 적용

### P1 (7일 내)

- [ ] **CloudTrail + GuardDuty 통합** 설정 및 고위험 결과 자동 대응 구성
- [ ] **Terraform 보안 스캔 파이프라인** 구축 (tfsec/checkov CI/CD 통합)
- [ ] **Spot/Graviton 적합 워크로드 식별** 및 비용 최적화 PoC 수행
- [ ] **SCP 기반 가드레일** 배포 (CloudTrail 비활성화 방지, 리전 제한)

### P2 (30일 내)

- [ ] **FinOps 대시보드 구축** 및 팀별 비용 할당 태그 강제화
- [ ] **OPA/Conftest 기반 Policy as Code** 라이브러리 구축
- [ ] 클라우드 인프라 보안 설정 정기 감사

## 요약 및 다음 단계

### 이번 주 핵심 정리

- **Zero Trust 아키텍처 전환 가속화**: AWS IAM Identity Center + SCP 기반 Zero Trust 구현이 필수가 되었으며, 장기 액세스 키에서 단기 자격 증명으로의 전환이 시급합니다.
- **키 없는 인증의 확산**: GCP Workload Identity Federation을 통한 서비스 계정 키 제거가 클라우드 보안의 핵심 과제로, CI/CD 파이프라인부터 적용을 시작해야 합니다.
- **FinOps와 보안의 균형**: Spot/Graviton 인스턴스 전환으로 비용을 최적화하면서도 Karpenter를 통한 가용성 확보와 보안 워크로드 적합성 검증이 필요합니다.

### 다음 주 주목 사항

- AWS IAM 장기 액세스 키 보안 경고 강화 정책 시행(2026년 4월)
- GCP Workload Identity Federation의 Azure AD 통합 업데이트 예상
- Terraform 1.10 Ephemeral Values의 프로덕션 적용 사례 발표

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| AWS IAM Identity Center | [docs.aws.amazon.com/singlesignon](https://docs.aws.amazon.com/singlesignon/) |
| GCP Workload Identity | [cloud.google.com/iam/docs/workload-identity-federation](https://cloud.google.com/iam/docs/workload-identity-federation) |
| FinOps Foundation | [finops.org](https://www.finops.org/) |

---

**작성자**: Twodragon
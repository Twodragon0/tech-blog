---
layout: post
title: "AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처"
date: 2026-01-14 11:00:00 +0900
categories: [security, cloud]
tags: [AWS, Security, IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security-Hub]
excerpt: "AWS IAM, VPC, S3, RDS, EKS 보안 아키텍처. Defense in Depth 전략과 실무 체크리스트 제공."
description: "AWS 클라우드 환경에서의 보안 아키텍처 설계 및 구현 가이드. IAM, VPC, S3, RDS, EKS 등 주요 서비스별 보안 모범 사례, Defense in Depth 전략, 최소 권한 원칙, 암호화, 로그 관리 및 모니터링까지 실무 중심 가이드."
keywords: "AWS 보안, IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security Hub, GuardDuty, KMS, Defense in Depth, 최소 권한 원칙, AWS-SAA"
author: Twodragon
comments: true
image: /assets/images/2026-01-14-AWS_Cloud_Security_Complete_Guide_IAM_to_EKS_Practical_Security_Architecture.svg
image_alt: "AWS Cloud Security Complete Guide: IAM to EKS Practical Security Architecture"
toc: true
schema_type: Article
certifications: [aws-saa]
---

## 🎯 Executive Summary

### AWS/EKS 보안 태세 평가

| 보안 영역 | 현재 위협 수준 | 주요 공격 벡터 | 권장 우선순위 |
|----------|-------------|-------------|-------------|
| **IAM/인증** | 🔴 **HIGH** | Credential stuffing, 권한 에스컬레이션 | 1순위 |
| **EKS/Container** | 🔴 **HIGH** | Escape to Host, 특권 컨테이너 실행 | 2순위 |
| **VPC/네트워크** | 🟡 **MEDIUM** | Lateral movement, 무단 네트워크 접근 | 3순위 |
| **S3/데이터** | 🟡 **MEDIUM** | Public bucket 노출, 암호화 미적용 | 4순위 |
| **RDS/데이터베이스** | 🟢 **LOW** | SQL injection, 암호화되지 않은 백업 | 5순위 |

**핵심 권장사항:**
1. **즉시 조치**: 모든 루트 계정에 MFA 활성화 + IAM Access Analyzer 실행
2. **1주 내**: EKS Pod Security Standards 적용 + Network Policy 구성
3. **1개월 내**: Security Hub + GuardDuty 활성화 + 자동화된 위협 대응 워크플로 구축

**투자 대비 효과 (ROI):**
- **보안 사고 감소**: 평균 67% (CIS AWS Foundations Benchmark 적용 시)
- **컴플라이언스 비용 절감**: 30-40% (ISMS-P, CSAP 자동 감사)
- **평균 복구 시간 (MTTR)**: 4시간 → 45분 (GuardDuty + Lambda 자동 대응)

---

## 서론

안녕하세요, **Twodragon**입니다.

AWS 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 EKS까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다. 이 포스팅은 **SK Shieldus의 2024년 AWS 클라우드 보안 가이드**를 기반으로, 실무에서 즉시 활용 가능한 AWS 보안 아키텍처 설계 및 구현 가이드를 제공합니다.

주요 AWS 서비스별 보안 모범 사례와 코드 예제, 보안 체크리스트를 포함하여 실무 중심의 보안 구축 방법을 제시합니다.

## 📊 빠른 참조

### AWS 보안 서비스 개요

| 서비스 | 용도 | 주요 기능 |
|--------|------|----------|
| **IAM** | 접근 제어 | 사용자, 역할, 정책 관리 |
| **VPC** | 네트워크 보안 | 네트워크 격리, 접근 제어 |
| **Security Hub** | 통합 보안 관리 | 보안 상태 통합 대시보드 |
| **CloudTrail** | 감사 및 컴플라이언스 | API 호출 로깅 |
| **CloudWatch** | 모니터링 | 메트릭, 로그, 알람 |
| **GuardDuty** | 위협 탐지 | 이상 활동 탐지 |
| **KMS** | 암호화 | 키 관리 서비스 |
| **Config** | 설정 관리 | 리소스 설정 모니터링 |

---

## 🛡️ MITRE ATT&CK 매핑: AWS/EKS 위협 모델링

### 컨테이너 및 Kubernetes 주요 공격 기법

| MITRE Technique | 공격 설명 | AWS/EKS 대응 방안 |
|----------------|----------|------------------|
| **T1610: Deploy Container** | 악성 컨테이너 배포 | ECR Image Scanning + Admission Controller |
| **T1611: Escape to Host** | 컨테이너 탈출 → 호스트 권한 획득 | Pod Security Standards (restricted) + seccomp/AppArmor |
| **T1078.004: Cloud Accounts** | 탈취된 클라우드 자격 증명 악용 | IAM Access Analyzer + CloudTrail 이상 탐지 |
| **T1552.001: Credentials in Files** | 하드코딩된 시크릿 탈취 | AWS Secrets Manager + IRSA (IAM Roles for Service Accounts) |
| **T1613: Container & Resource Discovery** | 컨테이너 환경 정찰 | Network Policy + VPC Flow Logs |
| **T1204: User Execution** | 사용자 유도 악성 실행 | GuardDuty Runtime Monitoring + Falco |
| **T1053.003: Cron** | 예약 작업을 통한 지속성 확보 | Pod Security Admission + ReadOnlyRootFilesystem |
| **T1486: Data Encrypted for Impact** | 랜섬웨어 공격 | S3 Versioning + Object Lock + EBS Snapshot 정책 |

### AWS 특화 공격 체인 예시

```
[Initial Access]           [Execution]              [Persistence]           [Defense Evasion]
T1078.004                  T1610                    T1053.003               T1562.001
└─ IAM 자격증명 탈취  →  악성 컨테이너 배포  →  CronJob 등록     →  CloudTrail 로그 삭제

[Lateral Movement]         [Collection]             [Exfiltration]
T1613                      T1552.001                T1567.002
└─ Cluster 정찰       →  시크릿 탈취        →  S3 버킷으로 데이터 유출
```

<!--
SIEM 탐지 쿼리:

1. Splunk SPL - 컨테이너 탈출 시도 (T1611)
index=kubernetes source="audit" verb IN (create, update)
objectRef.resource="pods"
| where like(requestObject.spec.containers{}.securityContext.privileged, "true")
   OR like(requestObject.spec.hostPID, "true")
   OR like(requestObject.spec.hostNetwork, "true")
| stats count by user.username objectRef.namespace objectRef.name
| where count > 3

2. Azure Sentinel KQL - IAM 권한 에스컬레이션 (T1078.004)
AWSCloudTrail
| where EventName in ("PutUserPolicy", "AttachUserPolicy", "CreateAccessKey", "PutRolePolicy")
| where ErrorCode == "" // 성공한 호출만
| extend PolicyDocument = tostring(parse_json(RequestParameters).policyDocument)
| where PolicyDocument contains "*" and PolicyDocument contains "Resource"
| summarize count() by UserIdentityArn, EventName, SourceIpAddress, bin(TimeGenerated, 5m)
| where count_ > 2

3. AWS CloudWatch Insights - EKS 의심스러운 Pod 실행
fields @timestamp, requestURI, user.username, objectRef.namespace, objectRef.name
| filter objectRef.resource="pods" and verb="create"
| filter requestObject.spec.containers.0.image !~ /^123456789012\.dkr\.ecr\./
| stats count() by user.username, requestObject.spec.containers.0.image
| sort count desc

4. Splunk SPL - S3 Public Access 설정 변경 (T1530)
index=cloudtrail sourcetype=aws:cloudtrail eventName IN ("PutBucketAcl", "PutBucketPolicy", "DeletePublicAccessBlock")
| eval isPubAccess=if(match(requestParameters, "AllUsers|AuthenticatedUsers"), "yes", "no")
| where isPubAccess="yes"
| table _time userName sourceIPAddress bucketName requestParameters
-->

---

## 1. AWS 보안 아키텍처 개요

### 1.1 Defense in Depth 전략

Defense in Depth는 여러 보안 레이어를 중첩하여 보안을 강화하는 전략입니다.

#### AWS 보안 아키텍처 다이어그램

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. + Shield (DDoS Protection)        │      │  ← 1계층: 경계 방어
│  │ CloudFront (CDN + Geo-blocking)       │      │
│  └───────────────────────────────────────┘      │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────── Network Layer ───────────────────┐
│  ┌─────────────────────────────────────────┐    │
│  │ VPC: 10.0.0.0/16                        │    │  ← 2계층: 네트워크 격리
│  │  ├─ Public Subnet (NAT, ALB)            │    │
│  │  ├─ Private Subnet (EKS Workers)        │    │
│  │  └─ DB Subnet (RDS)                     │    │
│  │                                          │    │
│  │ Security Groups + NACL                  │    │
│  │ VPC Flow Logs → CloudWatch              │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────── Identity Layer ──────────────────┐
│  ┌─────────────────────────────────────────┐    │
│  │ IAM + MFA                               │    │  ← 3계층: 인증/인가
│  │ AWS SSO / SAML Federation               │    │
│  │ IAM Access Analyzer                     │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────── Compute Layer ───────────────────┐
│  ┌───────────────────────────────────────────┐  │
│  │ EKS Cluster                               │  │  ← 4계층: 워크로드 격리
│  │  ├─ Pod Security Standards (restricted)  │  │
│  │  ├─ Network Policy (Calico/Cilium)       │  │
│  │  ├─ RBAC (Role-Based Access Control)     │  │
│  │  └─ IRSA (IAM Roles for Service Accounts)│  │
│  └───────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────── Data Layer ──────────────────────┐
│  ┌─────────────────────────────────────────┐    │
│  │ S3 (Encryption at Rest + KMS)           │    │  ← 5계층: 데이터 보호
│  │ RDS (TDE + Backup Encryption)           │    │
│  │ EBS (Encrypted Volumes)                 │    │
│  │ Secrets Manager (Credential Rotation)   │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────── Monitoring Layer ────────────────┐
│  ┌─────────────────────────────────────────┐    │
│  │ CloudTrail (Audit Logs)                 │    │  ← 6계층: 탐지/대응
│  │ GuardDuty (Threat Detection)            │    │
│  │ Security Hub (Unified Dashboard)        │    │
│  │ EventBridge → Lambda (Auto-remediation) │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘

```
-->
-->

#### 다층 보안 방어 구조

| 레이어 | AWS 서비스 | 보안 기능 |
|--------|-----------|----------|
| **네트워크 레이어** | VPC, Security Group, NACL | 네트워크 분리, 트래픽 필터링 |
| **인증/인가 레이어** | IAM, MFA | 사용자 인증, 권한 관리 |
| **애플리케이션 레이어** | WAF, Shield | 웹 애플리케이션 보호 |
| **데이터 레이어** | KMS, S3, RDS | 데이터 암호화 |
| **모니터링 레이어** | CloudTrail, CloudWatch, GuardDuty | 로깅, 모니터링, 위협 탐지 |

### 1.2 보안 모범 사례

| 원칙 | 설명 | AWS 구현 |
|------|------|---------|
| **최소 권한 원칙** | 필요한 최소한의 권한만 부여 | IAM 정책, Security Group 규칙 |
| **암호화** | 전송 중/저장 데이터 암호화 | TLS/SSL, KMS, S3 암호화 |
| **로그 관리** | 모든 활동 로깅 및 모니터링 | CloudTrail, CloudWatch |
| **정기적 검토** | 보안 설정 정기적 검토 및 개선 | Config, Security Hub |

---

## 2. IAM 보안

### 2.1 IAM 정책 작성

#### 최소 권한 원칙 적용

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.는 다른 AWS 계정의 VPC 리소스를 오리진으로 설정할 수 있도록 지원합니다.

**주요 활용 사례:**
- 멀티 계정 아키텍처에서 공통 프런트 도메인 구성
- 각 계정별 백엔드 VPC 패턴 구성
- 보안 격리 유지하면서 리소스 공유

### 8.3 S3 보안 강화

#### S3 Express One Zone IPv6 지원 및 테이블 태깅

2025년 11월, S3 Express One Zone은 IPv6를 지원하며, S3 테이블에 대한 태깅 기능이 추가되었습니다.

**주요 기능:**
- IPv6 네트워크 지원으로 보안 강화
- 테이블 태깅을 통한 리소스 관리 및 보안 정책 적용
- 비용 최적화 및 성능 향상

### 8.4 RDS 보안 강화

#### AWS Backup을 통한 Amazon EKS 지원

2025년 11월, AWS Backup은 Amazon EKS 클러스터, 네임스페이스, 볼륨 등 Kubernetes 워크로드를 직접 백업 및 복구할 수 있도록 지원합니다.

**주요 기능:**
- 컨테이너 환경의 재해 복구 표준화
- EKS 클러스터 자동 백업
- 네임스페이스 및 볼륨 레벨 백업

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Backup EKS 백업 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # AWS Backup EKS 백업 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AWS Backup EKS 백업 설정 예시
Resources:
  EKSBackupPlan:
    Type: AWS::Backup::BackupPlan
    Properties:
      BackupPlan:
        BackupPlanName: eks-backup-plan
        Rules:
          - RuleName: eks-daily-backup
            TargetBackupVault: !Ref BackupVault
            ScheduleExpression: cron(0 3 * * ? *)
            Lifecycle:
              DeleteAfterDays: 30
            CopyActions:
              - DestinationBackupVaultArn: !GetAtt BackupVault.Arn
                Lifecycle:
                  DeleteAfterDays: 90

```
-->
-->

### 8.5 EKS 보안 강화

#### 향상된 네트워크 보안 정책

2025년 12월, Amazon EKS는 Kubernetes 워크로드에 대한 네트워크 보안 태세와 클러스터 외부 대상과의 통합을 개선하기 위해 향상된 네트워크 정책 기능을 발표했습니다.

**주요 기능:**
- 전체 클러스터에 걸친 네트워크 액세스 필터 중앙 적용
- DNS 기반 정책을 활용한 클러스터 환경의 송신 트래픽 보호
- 네트워크 보안 정책의 중앙 관리

#### EKS Cluster Insights 정책

2025년, EKS는 클러스터 인사이트를 사용한 Kubernetes 버전 업그레이드 준비 및 잘못된 구성 문제 해결을 위해 `AmazonEKSClusterInsightsPolicy`를 도입했습니다.

**주요 기능:**
- 클러스터 노드의 상태 정보 읽기
- kube-proxy 구성에 대한 읽기 액세스
- 클러스터의 보안과 안정성 향상

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # EKS Cluster Insights Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # EKS Cluster Insights Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# EKS Cluster Insights Policy 예시
Resources:
  EKSClusterInsightsRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: EKSClusterInsightsRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: eks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonEKSClusterInsightsPolicy

```
-->
-->

---

## 🔬 실전 시나리오: EKS 보안 사고 대응 플레이북

### 시나리오 1: 컨테이너 탈출 시도 감지 (T1611)

**1단계: 탐지 (Detection)**
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.

```bash
# GuardDuty Finding 트리거
Finding Type: Execution:Container/PrivilegeEscalation
Severity: HIGH
Resource: EKS Cluster - production-cluster
```

**2단계: 격리 (Containment)**
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 의심 Pod 즉시 삭제...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 의심 Pod 즉시 삭제...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 의심 Pod 즉시 삭제
kubectl delete pod suspicious-pod -n production --grace-period=0

# 해당 노드 격리 (cordon)
kubectl cordon ip-10-0-1-123.ap-northeast-2.compute.internal

# Network Policy로 트래픽 차단
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF

```
-->
-->

**3단계: 증거 수집 (Evidence Collection)**
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # Pod 로그 백업...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # Pod 로그 백업...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Pod 로그 백업
kubectl logs suspicious-pod -n production --previous > /tmp/incident-logs.txt

# 노드 포렌식 스냅샷
aws ec2 create-snapshot --volume-id vol-xxxxxxxxx \
  --description "Forensic snapshot - incident-2026-01-14"

# CloudTrail 이벤트 추출
aws cloudtrail lookup-events --lookup-attributes \
  AttributeKey=ResourceName,AttributeValue=suspicious-pod \
  --start-time 2026-01-14T00:00:00Z

```
-->
-->

**4단계: 근본 원인 분석 (Root Cause Analysis)**
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# 취약한 이미지 식별
kubectl get pod suspicious-pod -n production -o jsonpath='{.spec.containers[*].image}'
# 출력: nginx:1.14.0  # ← 알려진 CVE-2021-23017 존재

# ECR 이미지 스캔 결과 확인
aws ecr describe-image-scan-findings \
  --repository-name production-app \
  --image-id imageTag=v1.14.0
```

**5단계: 복구 및 재발 방지 (Recovery & Prevention)**
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Admission Controller 배포 (Gatekeeper)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Admission Controller 배포 (Gatekeeper)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Admission Controller 배포 (Gatekeeper)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sBlockPrivileged
metadata:
  name: block-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    exemptImages:
      - "gcr.io/google-containers/pause"  # 시스템 Pod 제외

```
-->
-->

### 시나리오 2: IAM 자격증명 노출 대응

**탐지 Alert:**
> **참고**: 관련 예제는 [공식 문서](https://www.json.org/json-en.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.json.org/json-en.html)를 참조하세요.

```json
{
  "GuardDutyFinding": {
    "Type": "UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration",
    "Severity": 8.0,
    "Description": "IAM credentials from EC2 instance i-0abc123 used from IP 198.51.100.42"
  }
}
```

**즉시 대응 Lambda 함수:**
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
    iam = boto3.client('iam')
    ec2 = boto3.client('ec2')

    # 1. 해당 인스턴스 격리
    instance_id = event['detail']['resource']['instanceDetails']['instanceId']
    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=['sg-quarantine']  # 모든 트래픽 차단하는 SG
    )

    # 2. IAM Role 임시 정책 추가 (모든 권한 거부)
    role_name = event['detail']['resource']['accessKeyDetails']['userName']
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName='EmergencyDenyAll',
        PolicyDocument=json.dumps({
            'Version': '2012-10-17',
            'Statement': [{
                'Effect': 'Deny',
                'Action': '*',
                'Resource': '*'
            }]
        })
    )

    # 3. SNS 알림
    sns = boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:ap-northeast-2:123456789012:security-alerts',
        Subject='CRITICAL: IAM Credential Compromise',
        Message=f'Instance {instance_id} credentials compromised. Auto-quarantined.'
    )

    return {'statusCode': 200}

```
-->
-->

---

## 결론

AWS 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 EKS까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다.

주요 보안 원칙:

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **암호화**: 전송 중/저장 데이터 암호화
3. **로그 관리**: 모든 활동 로깅 및 모니터링
4. **정기적 검토**: 보안 설정 정기적 검토 및 개선
5. **자동화된 대응**: GuardDuty + EventBridge + Lambda를 통한 즉시 대응 체계 구축

### 핵심 실무 체크리스트

**즉시 적용 (오늘 내):**
- [ ] 모든 루트 계정 MFA 활성화
- [ ] S3 Public Access Block 전체 활성화
- [ ] CloudTrail 로깅 활성화 (모든 리전)

**1주일 내 적용:**
- [ ] Security Hub + GuardDuty 활성화
- [ ] EKS Pod Security Standards 적용
- [ ] IAM Access Analyzer 실행 및 결과 검토

**1개월 내 적용:**
- [ ] 자동화된 보안 사고 대응 워크플로 구축
- [ ] CSAP/ISMS-P 컴플라이언스 점검 자동화
- [ ] 정기 보안 교육 프로그램 시작

이 가이드를 참고하여 AWS 환경에서 강력한 보안 아키텍처를 구축하시기 바랍니다.

---

## 📚 참고 자료

### 공식 문서 및 가이드

1. **AWS 공식 보안 문서**
   - [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
   - [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
   - [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
   - [Amazon EKS Security Best Practices](https://aws.github.io/aws-eks-best-practices/security/docs/)

2. **컴플라이언스 및 규제**
   - [SK Shieldus 2024년 AWS 클라우드 보안 가이드](https://www.skshieldus.com/download/files/download.do?o_fname=2024%20%ED%81%AC%EB%9D%BC%EC%9A%B0%EB%93%9C%20%EB%B3%B4%EC%95%88%EA%B0%80%EC%9D%B4%EB%93%9C(AWS).pdf&r_fname=20240703112722479.pdf)
   - [CSAP (Cloud Security Assurance Program) 인증 기준](https://www.kisa.or.kr/2060301)
   - [ISMS-P 인증 기준 해설서](https://www.kisa.or.kr/2060204)
   - [CIS AWS Foundations Benchmark v1.5.0](https://www.cisecurity.org/benchmark/amazon_web_services)

3. **MITRE ATT&CK 프레임워크**
   - [MITRE ATT&CK: Containers](https://attack.mitre.org/matrices/enterprise/containers/)
   - [MITRE ATT&CK: Cloud (IaaS)](https://attack.mitre.org/matrices/enterprise/cloud/iaas/)
   - [AWS 보안 사고 대응 가이드](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)

### 보안 도구 및 서비스

4. **AWS 보안 서비스 문서**
   - [AWS Security Hub User Guide](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)
   - [Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html)
   - [AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
   - [AWS Config Developer Guide](https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html)
   - [Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html)

5. **Kubernetes 보안**
   - [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
   - [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
   - [Calico Network Policy Tutorial](https://docs.tigera.io/calico/latest/network-policy/get-started/kubernetes-policy/kubernetes-policy-basic)
   - [Falco Runtime Security](https://falco.org/docs/)

### 커뮤니티 및 학습 자료

6. **보안 블로그 및 연구**
   - [AWS Security Blog](https://aws.amazon.com/blogs/security/)
   - [AWS re:Inforce 2025 세션 자료](https://reinforce.awsevents.com/)
   - [Cloud Security Alliance (CSA)](https://cloudsecurityalliance.org/)
   - [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)

7. **실습 및 교육**
   - [AWS Security Workshops](https://workshops.aws/categories/Security)
   - [AWS Skill Builder - Security Learning Plan](https://explore.skillbuilder.aws/learn/public/learning_plan/view/91/security-learning-plan)
   - [AWS-SAA 인증 페이지](/certifications/aws-saa/)
   - [온라인 강의 (2twodragon.com)](https://edu.2twodragon.com/courses/aws-saa)

### 오픈소스 보안 도구

8. **Infrastructure as Code (IaC) 보안 스캐닝**
   - [Checkov - Terraform/CloudFormation 보안 스캔](https://www.checkov.io/)
   - [tfsec - Terraform 정적 분석](https://github.com/aquasecurity/tfsec)
   - [Prowler - AWS 보안 베스트 프랙티스 점검](https://github.com/prowler-cloud/prowler)

9. **컨테이너 보안**
   - [Trivy - 컨테이너 이미지 취약점 스캐너](https://github.com/aquasecurity/trivy)
   - [Anchore - 컨테이너 보안 플랫폼](https://anchore.com/)
   - [Kube-bench - CIS Kubernetes Benchmark 점검](https://github.com/aquasecurity/kube-bench)

10. **보안 자동화**
    - [AWS Lambda Security Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)
    - [AWS Systems Manager - 보안 자동화](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
    - [Terraform AWS Security Modules](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest)

### 사고 대응 및 포렌식

11. **AWS 보안 사고 대응**
    - [AWS Security Incident Response Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)
    - [AWS Systems Manager Incident Manager](https://docs.aws.amazon.com/incident-manager/latest/userguide/what-is-incident-manager.html)
    - [CloudTrail 로그 분석 가이드](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html)

12. **관련 인증 및 자격증**
    - [AWS Certified Security - Specialty](https://aws.amazon.com/certification/certified-security-specialty/)
    - [Certified Kubernetes Security Specialist (CKS)](https://www.cncf.io/certification/cks/)
    - [CISSP (Certified Information Systems Security Professional)](https://www.isc2.org/Certifications/CISSP)

---

**마지막 업데이트**: 2026-01-14
**작성 기준**: SK Shieldus 2024년 AWS 클라우드 보안 가이드, MITRE ATT&CK v14, CIS AWS Foundations Benchmark v1.5.0

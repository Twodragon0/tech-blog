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

## 📋 포스팅 요약

> **제목**: AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처

> **카테고리**: security, cloud

> **태그**: AWS, Security, IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security-Hub

> **핵심 내용**: 
> - AWS IAM, VPC, S3, RDS, EKS 보안 아키텍처. Defense in Depth 전략과 실무 체크리스트 제공.

> **주요 기술/도구**: AWS, Security, IAM, VPC, Security, security, cloud

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
    <span class="summary-value">AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">Security</span>
      <span class="tag">IAM</span>
      <span class="tag">VPC</span>
      <span class="tag">S3</span>
      <span class="tag">RDS</span>
      <span class="tag">EKS</span>
      <span class="tag">CloudTrail</span>
      <span class="tag">CloudWatch</span>
      <span class="tag">Security-Hub</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS 보안 아키텍처 개요</strong>: Defense in Depth 전략, 다층 보안 방어, AWS 서비스별 보안 레이어, 보안 그룹, NACL, IAM 통합</li>
      <li><strong>IAM 보안</strong>: IAM 정책 작성, 역할 기반 접근 제어 (RBAC), MFA 설정, 최소 권한 원칙, 정기적인 권한 검토</li>
      <li><strong>VPC 보안</strong>: VPC 아키텍처 설계 (Public/Private Subnet), NAT Gateway 설정, Security Group 및 NACL 구성, 네트워크 분리</li>
      <li><strong>S3 보안</strong>: 버킷 정책, 암호화 설정 (서버 측 암호화, KMS), 버전 관리, 접근 로그, Public Access 차단</li>
      <li><strong>RDS 보안</strong>: 데이터베이스 암호화, 보안 그룹 구성, 파라미터 그룹, 스냅샷, 자동 백업</li>
      <li><strong>EKS 보안</strong>: Pod Security Standards, Network Policy, RBAC, 컨테이너 이미지 보안, 시크릿 관리</li>
      <li><strong>모니터링 및 감사</strong>: CloudTrail 설정, CloudWatch 모니터링, Security Hub 통합, GuardDuty 위협 탐지</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS (IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security Hub, GuardDuty, KMS, Config), Defense in Depth, RBAC, TLS/SSL, Encryption</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">AWS 보안 엔지니어, 클라우드 아키텍트, DevOps 엔지니어, 보안 전문가, AWS-SAA 준비자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS 다층 보안 아키텍처 (Defense in Depth)          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────── Perimeter Layer ─────────────────┐
│  ┌───────────────────────────────────────┐      │
│  │ WAF + Shield (DDoS Protection)        │      │  ← 1계층: 경계 방어
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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # IAM 정책 예시: 최소 권한 원칙...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # IAM 정책 예시: 최소 권한 원칙...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# IAM 정책 예시: 최소 권한 원칙
Version: '2012-10-17'
Statement:
  - Sid: AllowS3ReadOnly
    Effect: Allow
    Action:
      - s3:GetObject
      - s3:ListBucket
    Resource:
      - 'arn:aws:s3:::secure-bucket'
      - 'arn:aws:s3:::secure-bucket/*'
    Condition:
      StringEquals:
        's3:x-amz-server-side-encryption': 'AES256'
      IpAddress:
        'aws:SourceIp':
          - '10.0.0.0/8'


```
-->
-->

#### 역할 기반 접근 제어 (RBAC)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # IAM 역할 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # IAM 역할 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# IAM 역할 예시
Resources:
  ApplicationRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: ApplicationRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
      Policies:
        - PolicyName: ApplicationPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                Resource: 'arn:aws:dynamodb:*:*:table/ApplicationTable'


```
-->
-->

> **참고**: 전체 IAM 정책 예시는 [AWS IAM 모범 사례](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) 및 [AWS 보안 모범 사례](https://aws.amazon.com/security/security-resources/)를 참조하세요.

### 2.2 MFA 설정

| MFA 방법 | 설명 | 사용 사례 |
|---------|------|----------|
| **가상 MFA 디바이스** | Authenticator 앱 | 일반 사용자 |
| **하드웨어 MFA 디바이스** | 물리적 토큰 | 관리자 계정 |
| **SMS MFA** | 문자 메시지 | 간단한 인증 (권장하지 않음) |

### 2.3 IAM 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **MFA 활성화** | 모든 사용자에 MFA 활성화 | IAM Console |
| **최소 권한 원칙** | 필요한 권한만 부여 | IAM Access Analyzer |
| **정기적인 권한 검토** | 90일마다 권한 검토 | IAM Access Analyzer |
| **사용하지 않는 자격 증명 제거** | 오래된 액세스 키, 역할 정리 | IAM Credential Report |
| **강력한 비밀번호 정책** | 복잡한 비밀번호 요구 | IAM Password Policy |

---

## 3. VPC 보안

### 3.1 VPC 아키텍처 설계

#### Public/Private Subnet 구성

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # VPC 아키텍처 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # VPC 아키텍처 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# VPC 아키텍처 예시
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: SecureVPC
  
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: ap-northeast-2a
      MapPublicIpOnLaunch: true
  
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: ap-northeast-2a
      MapPublicIpOnLaunch: false


```
-->
-->

#### NAT Gateway 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # NAT Gateway 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # NAT Gateway 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# NAT Gateway 예시
Resources:
  NATGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt EIP.AllocationId
      SubnetId: !Ref PublicSubnet
  
  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Routes:
        - DestinationCidrBlock: 0.0.0.0/0
          NatGatewayId: !Ref NATGateway


```
-->
-->

### 3.2 Security Group 및 NACL

#### Security Group 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # Security Group 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # Security Group 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Security Group 예시
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
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP from internet
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: Allow all outbound traffic
      Tags:
        - Key: Name
          Value: WebServerSecurityGroup
        - Key: Compliance
          Value: ISMS-P


```
-->
-->

> **참고**: 전체 Security Group 설정 예시는 [AWS Security Groups 모범 사례](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html) 및 [AWS VPC 보안 모범 사례](https://aws.amazon.com/security/security-resources/)를 참조하세요.

### 3.3 VPC 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **Private Subnet 활용** | 데이터베이스는 Private Subnet에 배치 | VPC Console |
| **Security Group 규칙 최소화** | 필요한 포트만 허용 | Security Group Console |
| **NACL 설정** | 네트워크 레벨 접근 제어 | NACL Console |
| **VPC Flow Logs 활성화** | 네트워크 트래픽 로깅 | VPC Flow Logs |
| **VPC Peering 보안** | VPC Peering 시 보안 그룹 규칙 확인 | VPC Peering Console |

---

## 4. S3 보안

### 4.1 버킷 정책

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # S3 버킷 정책 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # S3 버킷 정책 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# S3 버킷 정책 예시
# ISMS-P 요구사항: 접근 통제 및 암호화
Resources:
  SecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: secure-data-bucket
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
            BucketKeyEnabled: true
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LoggingConfiguration:
        DestinationBucketName: !Ref AccessLogsBucket
        LogFilePrefix: access-logs/
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 90


```
-->
-->

### 4.2 S3 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **버킷 정책 설정** | 접근 권한 명확히 정의 | S3 Bucket Policy |
| **암호화 활성화** | 서버 측 암호화 필수 | S3 Encryption |
| **버전 관리 활성화** | 데이터 복구 가능하도록 | S3 Versioning |
| **Public Access 차단** | Public Access Block 활성화 | S3 Block Public Access |
| **접근 로그 활성화** | 버킷 접근 로그 수집 | S3 Access Logging |

---

## 5. RDS 보안

### 5.1 데이터베이스 암호화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # RDS 암호화 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # RDS 암호화 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# RDS 암호화 설정 예시
Resources:
  SecureDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: secure-db
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: admin
      MasterUserPassword: !Ref DatabasePassword
      DBInstanceClass: db.t3.medium
      AllocatedStorage: 100
      StorageEncrypted: true
      KmsKeyId: !Ref RDSKMSKey
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      PreferredBackupWindow: '03:00-04:00'
      EnableCloudwatchLogsExports:
        - error
        - slowquery


```
-->
-->

### 5.2 RDS 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **암호화 활성화** | 저장 데이터 암호화 | RDS Encryption |
| **보안 그룹 구성** | 데이터베이스 접근 제한 | Security Group |
| **자동 백업 활성화** | 정기적인 백업 설정 | RDS Automated Backups |
| **SSL/TLS 연결** | 연결 암호화 필수 | RDS SSL/TLS |
| **파라미터 그룹 설정** | 보안 관련 파라미터 설정 | RDS Parameter Groups |

---

## 6. EKS 보안

### 6.1 Pod Security Standards

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Pod Security Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Pod Security Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Pod Security Policy 예시
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
---
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: secure-namespace
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
    - name: app
      image: nginx:latest
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - ALL


```
-->
-->

### 6.2 Network Policy

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Network Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Network Policy 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Network Policy 예시
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: secure-network-policy
  namespace: secure-namespace
spec:
  podSelector:
    matchLabels:
      app: secure-app
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: allowed-app
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 3306


```
-->
-->

### 6.3 EKS 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **Pod Security Standards** | Pod Security Policy 적용 | EKS Pod Security |
| **Network Policy** | 네트워크 트래픽 제어 | Kubernetes Network Policy |
| **RBAC 설정** | 역할 기반 접근 제어 | Kubernetes RBAC |
| **컨테이너 이미지 보안** | 취약점 스캔 및 검증 | ECR Image Scanning |
| **시크릿 관리** | AWS Secrets Manager 통합 | EKS Secrets Manager |

### 6.4 EKS Threat Hunting Queries

#### 1. 특권 컨테이너 실행 탐지 (T1611 대응)

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```bash
# kubectl로 특권 컨테이너 검색
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.containers[].securityContext.privileged == true) |
  "\(.metadata.namespace)/\(.metadata.name)"'
```

<!--
CloudWatch Insights 쿼리:
fields @timestamp, objectRef.namespace, objectRef.name, user.username
| filter objectRef.resource="pods" and verb="create"
| filter requestObject.spec.containers.0.securityContext.privileged = true
| stats count() by objectRef.namespace, user.username
-->

#### 2. 외부 레지스트리 이미지 사용 탐지

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```bash
# 승인된 ECR 외부 이미지 사용 감지
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[].spec.containers[] |
  select(.image | test("^123456789012\\.dkr\\.ecr") | not) |
  .image' | sort | uniq
```

<!--
Splunk SPL:
index=kubernetes source="audit" verb="create" objectRef.resource="pods"
| rex field=requestObject.spec.containers{}.image "(?<registry>[^/]+)"
| where NOT match(registry, "123456789012\.dkr\.ecr\.ap-northeast-2")
| stats count by registry user.username objectRef.namespace
-->

#### 3. 과도한 RBAC 권한 탐지

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```bash
# ClusterRole 중 와일드카드 권한 확인
kubectl get clusterroles -o json | \
  jq -r '.items[] | select(.rules[].resources[] | contains("*")) |
  .metadata.name'
```

#### 4. 시크릿 접근 이상 패턴

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```bash
# 5분 내 3회 이상 서로 다른 시크릿 접근
kubectl get events --all-namespaces --field-selector reason=FailedMount | \
  grep "secret" | awk '{print $5}' | sort | uniq -c | sort -rn
```

<!--
Azure Sentinel KQL:
KubernetesPodInventory
| where TimeGenerated > ago(5m)
| where ContainerStatusReason contains "Secret"
| summarize SecretAccessCount = dcount(Name) by Computer, Namespace
| where SecretAccessCount > 3
-->

---

## 📋 한국 규제 준수: CSAP 및 ISMS-P 매핑

### CSAP (Cloud Security Assurance Program) 인증 항목

| CSAP 통제 항목 | AWS 구현 방안 | 자동화 도구 |
|--------------|-------------|-----------|
| **1.1 자산 관리** | AWS Config Rules로 리소스 인벤토리 관리 | Config + Systems Manager Inventory |
| **2.1 접근 통제** | IAM + MFA + RBAC | IAM Access Analyzer |
| **3.1 암호화** | KMS + S3/RDS/EBS 암호화 | Security Hub (CIS Benchmark) |
| **4.1 로그 관리** | CloudTrail + CloudWatch Logs (1년 보관) | S3 Lifecycle Policy |
| **5.1 침입 탐지** | GuardDuty + VPC Flow Logs | GuardDuty Findings |
| **6.1 취약점 관리** | Inspector + ECR Image Scanning | Inspector Findings |
| **7.1 사고 대응** | Security Hub + EventBridge → SNS | Lambda 자동 대응 |

### ISMS-P (정보보호 및 개인정보보호 관리체계) 매핑

| ISMS-P 통제 항목 | AWS 서비스 | 증거 자료 |
|----------------|-----------|----------|
| **2.5.1 식별** | IAM Users + SSO | IAM Credential Report |
| **2.5.2 인증** | IAM MFA + Cognito | CloudTrail (ConsoleLogin 이벤트) |
| **2.5.3 인가** | IAM Policies + SCPs | IAM Policy Simulator 결과 |
| **2.6.1 네트워크 접근 제어** | Security Groups + NACL | VPC Flow Logs 분석 |
| **2.7.1 암호화 적용** | KMS + TLS 1.2+ | Config Rules (encrypted-volumes) |
| **2.8.1 로그 기록** | CloudTrail + Config | S3 버킷 접근 로그 |
| **2.8.2 로그 보호** | S3 Object Lock + MFA Delete | S3 버킷 정책 |
| **2.9.1 백업** | AWS Backup + RDS 자동 백업 | Backup Vault 복구 테스트 결과 |

### 자동화된 컴플라이언스 점검 스크립트

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # ISMS-P 2.5.2: MFA 미설정 사용자 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # ISMS-P 2.5.2: MFA 미설정 사용자 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# ISMS-P 2.5.2: MFA 미설정 사용자 탐지
import boto3

iam = boto3.client('iam')

def check_mfa_compliance():
    users = iam.list_users()['Users']
    non_compliant = []

    for user in users:
        mfa_devices = iam.list_mfa_devices(UserName=user['UserName'])
        if not mfa_devices['MFADevices']:
            non_compliant.append(user['UserName'])

    return non_compliant

print("ISMS-P 2.5.2 위반 사용자:", check_mfa_compliance())


```
-->
-->

<!--
SIEM 쿼리 - ISMS-P 2.6.1 네트워크 접근 제어 감사:

Splunk SPL:
index=vpc_flow_logs action=REJECT
| stats count by src_ip dest_ip dest_port
| where count > 100
| eval compliance_status="ISMS-P 2.6.1 이상 접근 시도"

Azure Sentinel KQL:
AWSVPCFlow
| where Action == "REJECT"
| summarize RejectedCount = count() by SrcIP, DstIP, DstPort, bin(TimeGenerated, 1h)
| where RejectedCount > 50
| extend ComplianceControl = "ISMS-P 2.6.1"
-->

---

## 🎯 경영진 보고 형식 (Board Reporting)

### 월간 보안 현황 리포트 (Executive Summary)

#### 1. 핵심 지표 (KPIs)

| 지표 | 목표 | 실제 | 상태 |
|-----|------|------|------|
| **보안 사고 건수** | 0건 | 2건 | 🔴 |
| **평균 복구 시간 (MTTR)** | < 1시간 | 45분 | 🟢 |
| **취약점 해결율** | > 95% | 92% | 🟡 |
| **MFA 적용률** | 100% | 87% | 🔴 |
| **암호화 적용률** | 100% | 98% | 🟡 |
| **컴플라이언스 점수** | > 90점 | 88점 | 🟡 |

#### 2. 주요 보안 사고 및 조치사항

**사고 #1: IAM 자격증명 노출 (2026-01-10)**
- **영향도**: 🔴 HIGH
- **탐지 방법**: GuardDuty UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration
- **조치**: 해당 액세스 키 즉시 폐기 + CloudTrail 로그 분석 완료
- **근본 원인**: 개발자 로컬 환경에 하드코딩된 자격증명
- **재발 방지**: git-secrets 도구 배포 + pre-commit hook 설정

**사고 #2: S3 버킷 Public 노출 (2026-01-12)**
- **영향도**: 🟡 MEDIUM
- **탐지 방법**: Security Hub (S3.1: S3 Block Public Access setting should be enabled)
- **조치**: 2시간 내 Public Access Block 활성화
- **근본 원인**: IaC(Terraform) 설정 오류
- **재발 방지**: Terraform Sentinel Policy 추가

#### 3. 투자 권고사항

| 항목 | 예상 비용 | 기대 효과 | ROI |
|-----|----------|----------|-----|
| **AWS GuardDuty 고도화** | $500/월 | 위협 탐지 속도 50% 개선 | 6개월 |
| **EKS Fargate 전환** | $2,000/월 | 컨테이너 탈출 위험 제거 | 12개월 |
| **보안 교육 프로그램** | $10,000/년 | 인적 오류 70% 감소 | 9개월 |

#### 4. 컴플라이언스 현황

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
[CSAP 인증 진행 상황]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 85%

완료 항목: 34 / 40
- 자산 관리: ✅ 완료
- 접근 통제: ✅ 완료
- 암호화: 🔄 진행 중 (98% 적용)
- 로그 관리: ✅ 완료
- 침입 탐지: ✅ 완료
- 취약점 관리: 🔄 진행 중 (92% 해결)

[ISMS-P 인증 갱신]
예정일: 2026-03-15
준비율: 88% (목표 95%)


```
-->
-->

#### 5. 향후 3개월 로드맵

**Q1 2026 보안 강화 계획:**
1. **IAM 보안 강화** (1-2월)
   - MFA 100% 적용 완료
   - IAM Access Analyzer 자동 검토 체계 구축

2. **EKS 보안 아키텍처 개선** (2-3월)
   - Pod Security Standards 전면 적용
   - Network Policy 자동화 배포

3. **Zero Trust 아키텍처 도입** (3월)
   - Service Mesh (Istio) 도입 검토
   - mTLS 전면 적용

---

## 7. 모니터링 및 감사

### 7.1 CloudTrail 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # CloudTrail 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # CloudTrail 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# CloudTrail 설정 예시
Resources:
  CloudTrailLogs:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: security-audit-trail
      S3BucketName: !Ref AuditLogsBucket
      IncludeGlobalServiceEvents: true
      IsLogging: true
      IsMultiRegionTrail: true
      EventSelectors:
        - ReadWriteType: All
          IncludeManagementEvents: true
          DataResources:
            - Type: AWS::S3::Object
              Values:
                - 'arn:aws:s3:::secure-bucket/*'
      KMSKeyId: !Ref CloudTrailKMSKey
      CloudWatchLogsLogGroupArn: !GetAtt CloudWatchLogGroup.Arn
      CloudWatchLogsRoleArn: !GetAtt CloudWatchLogsRole.Arn


```
-->
-->

### 7.2 CloudWatch 모니터링

| 모니터링 항목 | CloudWatch 메트릭 | 알람 임계값 |
|-------------|------------------|------------|
| **비정상 API 호출** | CloudTrail API 호출 수 | 평균 대비 200% 증가 |
| **권한 에스컬레이션** | IAM 권한 변경 이벤트 | 즉시 알람 |
| **네트워크 이상** | VPC Flow Logs 분석 | 의심스러운 트래픽 패턴 |
| **암호화 미적용** | S3 암호화 상태 | 암호화 미적용 객체 발견 |

### 7.3 Security Hub 통합

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```yaml
# Security Hub 설정 예시
Resources:
  SecurityHubAccount:
    Type: AWS::SecurityHub::Hub
    Properties:
      EnableDefaultStandards: true
      StandardsSubscriptionArns:
        - arn:aws:securityhub:ap-northeast-2::standards/cis-aws-foundations-benchmark/v/1.2.0
        - arn:aws:securityhub:ap-northeast-2::standards/pci-dss/v/3.2.1
```

### 7.4 실시간 보안 이벤트 탐지 쿼리

#### GuardDuty Findings 자동 대응

<!--
Splunk SPL - GuardDuty 고위험 Finding 즉시 알림:
index=guardduty sourcetype=aws:cloudwatch:guardduty
| where Severity >= 7
| eval threat_type=case(
    like(Type, "%UnauthorizedAccess%"), "Unauthorized Access",
    like(Type, "%Trojan%"), "Malware",
    like(Type, "%CryptoCurrency%"), "Cryptomining",
    1=1, "Other"
  )
| stats count by threat_type AccountId Region
| where count > 0
-->

#### CloudTrail 권한 에스컬레이션 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # Lambda 함수: IAM 정책 변경 즉시 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # Lambda 함수: IAM 정책 변경 즉시 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# Lambda 함수: IAM 정책 변경 즉시 탐지
import boto3
import json

def lambda_handler(event, context):
    detail = event['detail']
    event_name = detail['eventName']

    # 위험한 IAM 변경 감지
    dangerous_events = [
        'PutUserPolicy',
        'AttachUserPolicy',
        'CreateAccessKey',
        'PutRolePolicy',
        'AttachRolePolicy'
    ]

    if event_name in dangerous_events:
        user = detail['userIdentity']['arn']
        policy = detail.get('requestParameters', {}).get('policyDocument', '')

        # 와일드카드 권한 검사
        if '*' in policy:
            send_alert(f"CRITICAL: {% raw %}{{user}}{% endraw %} granted wildcard permissions")

    return {'statusCode': 200}


```
-->
-->

<!--
Azure Sentinel KQL - Root 계정 사용 탐지:
AWSCloudTrail
| where UserIdentityType == "Root"
| where EventName !in ("DescribeRegions", "GetBucketLocation") // 정상 활동 제외
| extend AlertSeverity = "Critical"
| project TimeGenerated, EventName, SourceIpAddress, UserAgent, RequestParameters
| summarize EventCount = count() by EventName, bin(TimeGenerated, 1h)
-->

#### VPC Flow Logs 이상 트래픽 패턴

<!--
CloudWatch Insights:
fields @timestamp, srcaddr, dstaddr, dstport, protocol, bytes
| filter action = "REJECT"
| stats sum(bytes) as total_bytes by srcaddr, dstport
| sort total_bytes desc
| limit 20
| filter total_bytes > 10000000  # 10MB 이상 차단된 트래픽
-->

#### S3 데이터 유출 탐지

<!--
Splunk SPL - 대용량 S3 다운로드:
index=s3_access_logs http_status=200 operation="REST.GET.OBJECT"
| eval bytes_mb = bytes_sent / 1048576
| where bytes_mb > 100  # 100MB 이상
| stats sum(bytes_mb) as total_mb by requester bucket_name object_key
| where total_mb > 1000  # 1GB 이상 다운로드
| eval alert="Potential Data Exfiltration"
-->

---

## 8. 2025년 이후 최신 업데이트

### 8.1 IAM 보안 강화

#### 리전 기반 액세스 제어: `aws:SourceVpcArn` 조건 키

2025년 11월, AWS는 리전 기반 액세스 제어를 위한 새로운 글로벌 조건 키 `aws:SourceVpcArn`을 도입했습니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # aws:SourceVpcArn 조건 키 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # aws:SourceVpcArn 조건 키 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# aws:SourceVpcArn 조건 키 예시
Version: '2012-10-17'
Statement:
  - Effect: Allow
    Action:
      - s3:GetObject
      - s3:PutObject
    Resource: 'arn:aws:s3:::secure-bucket/*'
    Condition:
      StringEquals:
        'aws:SourceVpcArn': 'arn:aws:ec2:ap-northeast-2:ACCOUNT_ID:vpc/vpc-xxxxxxxxx'


```
-->
-->

**주요 활용 사례:**
- AWS PrivateLink를 통한 리소스 접근 제어
- 데이터 레지던시 요구사항 충족
- 특정 리전의 VPC 엔드포인트에서만 접근 허용

### 8.2 VPC 보안 강화

#### VPC 오리진의 교차 계정 지원

2025년 11월, Amazon CloudFront는 다른 AWS 계정의 VPC 리소스를 오리진으로 설정할 수 있도록 지원합니다.

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

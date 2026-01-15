---
layout: post
title: "AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처"
date: 2026-01-14 11:00:00 +0900
categories: [security, cloud]
tags: [AWS, Security, IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security-Hub]
excerpt: "AWS 클라우드 환경에서의 보안 아키텍처 설계 및 구현 가이드. IAM, VPC, S3, RDS, EKS 등 주요 서비스별 보안 모범 사례와 실무 적용 사례 제공. Defense in Depth 전략, 최소 권한 원칙, 암호화, 로그 관리 및 모니터링까지 실무 중심 가이드."
comments: true
certifications: [aws-saa]
image: /assets/images/2026-01-14-AWS_Cloud_Security_Complete_Guide_IAM_to_EKS_Practical_Security_Architecture.svg
image_alt: "AWS Cloud Security Complete Guide: IAM to EKS Practical Security Architecture"
toc: true
---

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

## 1. AWS 보안 아키텍처 개요

### 1.1 Defense in Depth 전략

Defense in Depth는 여러 보안 레이어를 중첩하여 보안을 강화하는 전략입니다.

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

#### 역할 기반 접근 제어 (RBAC)

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

#### NAT Gateway 설정

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

### 3.2 Security Group 및 NACL

#### Security Group 설정

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

### 6.2 Network Policy

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

### 6.3 EKS 보안 체크리스트

| 체크리스트 항목 | 설명 | AWS 도구 |
|---------------|------|---------|
| **Pod Security Standards** | Pod Security Policy 적용 | EKS Pod Security |
| **Network Policy** | 네트워크 트래픽 제어 | Kubernetes Network Policy |
| **RBAC 설정** | 역할 기반 접근 제어 | Kubernetes RBAC |
| **컨테이너 이미지 보안** | 취약점 스캔 및 검증 | ECR Image Scanning |
| **시크릿 관리** | AWS Secrets Manager 통합 | EKS Secrets Manager |

---

## 7. 모니터링 및 감사

### 7.1 CloudTrail 설정

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

### 7.2 CloudWatch 모니터링

| 모니터링 항목 | CloudWatch 메트릭 | 알람 임계값 |
|-------------|------------------|------------|
| **비정상 API 호출** | CloudTrail API 호출 수 | 평균 대비 200% 증가 |
| **권한 에스컬레이션** | IAM 권한 변경 이벤트 | 즉시 알람 |
| **네트워크 이상** | VPC Flow Logs 분석 | 의심스러운 트래픽 패턴 |
| **암호화 미적용** | S3 암호화 상태 | 암호화 미적용 객체 발견 |

### 7.3 Security Hub 통합

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

---

## 결론

AWS 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 EKS까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다.

주요 보안 원칙:

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **암호화**: 전송 중/저장 데이터 암호화
3. **로그 관리**: 모든 활동 로깅 및 모니터링
4. **정기적 검토**: 보안 설정 정기적 검토 및 개선

이 가이드를 참고하여 AWS 환경에서 강력한 보안 아키텍처를 구축하시기 바랍니다.

### 관련 자료

- [AWS-SAA 인증 페이지](/certifications/aws-saa/)
- [온라인 강의](https://edu.2twodragon.com/courses/aws-saa)
- [SK Shieldus 2024년 AWS 클라우드 보안 가이드](https://www.skshieldus.com/download/files/download.do?o_fname=2024%20%ED%81%AC%EB%9D%BC%EC%9A%B0%EB%93%9C%20%EB%B3%B4%EC%95%88%EA%B0%80%EC%9D%B4%EB%93%9C(AWS).pdf&r_fname=20240703112722479.pdf)
- [AWS 보안 모범 사례](https://aws.amazon.com/security/security-resources/)

---

**마지막 업데이트**: 2026-01-14
**작성 기준**: SK Shieldus 2024년 AWS 클라우드 보안 가이드

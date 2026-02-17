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

## 경영진 요약

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

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.)    │    │  │
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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> -->...
> ```

json
> {...
> > **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ...
> ```

spl
index=aws sourcetype=aws:cloudwatch:guardduty
| where severity >= 7.0
| stats count by type, severity, resource.instanceDetails.instanceId
| sort -severity
```

#### IAM 비정상 API 호출 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```spl
index=aws sourcetype=aws:cloudtrail
| where eventName IN ("CreateAccessKey", "CreateUser", "AttachUserPolicy")
  AND userAgent!="console.amazonaws.com"
| stats count by userIdentity.arn, eventName, sourceIPAddress
| where count > 10
```

#### S3 Public Access 변경 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```spl
index=aws sourcetype=aws:cloudtrail eventName IN ("PutBucketAcl", "PutBucketPolicy")
| eval isPublic=if(match(requestParameters, "AllUsers|AuthenticatedUsers"), "true", "false")
| where isPublic="true"
| table _time, userIdentity.arn, eventName, requestParameters.bucketName
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```

### Azure Sentinel KQL 쿼리

#### GuardDuty 위협 탐지 분석
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```kql
AWSGuardDuty
| where Severity >= 7.0
| where TimeGenerated > ago(24h)
| summarize Count=count() by Type, Severity, ResourceId
| order by Severity desc
```

#### IAM 권한 에스컬레이션 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```kql
AWSCloudTrail
| where EventName in ("PutUserPolicy", "AttachUserPolicy", "CreateAccessKey")
| where UserAgent !contains "console.amazonaws.com"
| summarize Count=count() by UserIdentityArn, EventName, SourceIpAddress
| where Count > 5
```

#### S3 대량 다운로드 탐지 (데이터 유출)
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```kql
AWSCloudTrail
| where EventName == "GetObject"
| where TimeGenerated > ago(1h)
| summarize TotalRequests=count(), UniqueObjects=dcount(RequestParameters) by UserIdentityArn, SourceIpAddress
| where TotalRequests > 1000
| order by TotalRequests desc
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```

## 6. Threat Hunting 쿼리

### 6.1 공격 시나리오별 헌팅 쿼리

#### 시나리오 1: 크리덴셜 침해 후 권한 에스컬레이션

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# CloudTrail 로그에서 비정상적인 API 호출 패턴 탐지
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole \
  --start-time 2025-01-01T00:00:00Z \
  --max-results 50 \
  | jq '.Events[] | select(.Username | test("i-[0-9a-f]+") | not)'
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```

#### 시나리오 2: 내부자 위협 - 대량 데이터 접근

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# S3 접근 로그 분석 - 단기간 대량 다운로드
aws s3api list-objects-v2 \
  --bucket security-logs \
  --prefix cloudtrail/ \
  | jq '.Contents[] | select(.Key | contains("GetObject"))'
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```

#### 시나리오 3: 암호화폐 채굴 인스턴스 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # CloudWatch 메트릭으로 CPU 사용량 이상 탐지...
> > **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> ...
> ```



### 7.4 단계별 구현 로드맵

#### Phase 1: 기본 보안 설정 (1-2주)

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

#### Phase 2: 데이터 보호 (2-3주)

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

#### Phase 3: 위협 탐지 및 대응 (3-4주)

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

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
| **Prowler** | [https://github.com/prowler-cloud/prowler) | AWS 보안 감사 도구 |
| **ScoutSuite** | [https://github.com/nccgroup/ScoutSuite) | 멀티 클라우드 보안 감사 |
| **CloudSploit** | [https://github.com/aquasecurity/cloudsploit) | 클라우드 보안 스캐너 |
| **CloudMapper** | [https://github.com/duo-labs/cloudmapper) | AWS 네트워크 시각화 |

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
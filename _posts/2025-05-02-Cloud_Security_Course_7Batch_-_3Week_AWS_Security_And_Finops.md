---
author: Yongho Ha
categories:
- cloud
certifications:
- aws-saa
comments: true
date: 2025-05-02 00:41:54 +0900
description: 클라우드 시큐리티 7기 3주차. AWS 보안 서비스 전체 구조(IAM, Organizations, CloudTrail, GuardDuty,
  Security Hub), FinOps 프레임워크, 비용 최적화 전략, AWS Well-Architected Framework 실무 적용.
excerpt: AWS 보안 및 FinOps 완벽 가이드. GuardDuty, Security Hub, IAM 보안 설정 및 비용 최적화 전략 실무
  정리.
image: /assets/images/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_and_Finops.svg
image_alt: 'Cloud Security Course 7Batch 3Week: AWS Security and FinOps'
keywords:
- AWS
- FinOps
- GuardDuty
- Security-Hub
- IAM
- CloudTrail
- Cost-Optimization
- Well-Architected
- 비용최적화
- 클라우드보안
layout: post
original_url: https://twodragon.tistory.com/679
schema_type: Article
tags:
- AWS
- FinOps
- Cloud-Security
- Cost-Optimization
- Well-Architected
title: '클라우드 시큐리티 과정 7기 - 3주차: AWS 보안 및 FinOps'
toc: true
---

## 요약

- **핵심 요약**: AWS 보안 및 FinOps 완벽 가이드. GuardDuty, Security Hub, IAM 보안 설정 및 비용 최적화 전략 실무 정리.
- **주요 주제**: 클라우드 시큐리티 과정 7기 - 3주차: AWS 보안 및 FinOps
- **키워드**: AWS, FinOps, Cloud-Security, Cost-Optimization, Well-Architected

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 3주차: AWS 보안 및 FinOps</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">FinOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">Cost-Optimization</span>
      <span class="tag">Well-Architected</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS 보안 서비스 구조</strong>: IAM(Identity Center), Organizations(SCP), CloudTrail(감사), Config(규칙), Security Hub(중앙 집중 보안), GuardDuty(위협 탐지), Inspector(취약점), Macie(데이터), Detective(포렌식), WAF, Shield, Firewall Manager, KMS, Secrets Manager</li>
      <li><strong>IAM 보안 모범 사례</strong>: 최소 권한 원칙, IP 기반 접근 제어, MFA 필수, 조건부 정책, VPC 보안 구성(Security Group, NACL, Flow Logs), GuardDuty 자동 대응(Lambda 기반 격리, SNS 알림)</li>
      <li><strong>FinOps 프레임워크</strong>: Inform(가시성 확보), Optimize(비용 최적화), Operate(운영 관리), Capabilities(비용 할당/태깅, 예산/예측, 이상 탐지, Reserved Instance/Savings Plans, Right Sizing)</li>
      <li><strong>비용 최적화 전략</strong>: 일관된 리소스 태깅 전략(Environment, Project, Owner, CostCenter), AWS Cost Explorer API 활용, 월간 비용 분석 및 이상 탐지, Reserved Instance/Savings Plans 최적화</li>
      <li><strong>AWS Well-Architected Framework</strong>: 보안 및 비용 최적화 관점에서의 아키텍처 설계, 보안과 비용의 균형, 실무 적용 가능한 FinOps 전략</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS, FinOps, GuardDuty, Security Hub</span>
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

<img src="{% raw %}{{ '/assets/images/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_and_Finops_image.png' | relative_url }}{% endraw %}" alt="Cloud Security Course 7Batch 3Week: AWS Security and FinOps" loading="lazy" class="post-image">

## Executive Summary

본 가이드는 AWS 보안 서비스와 FinOps 전략의 실무 통합을 다룹니다. 2025년 현재 AWS는 Security Hub GA 출시, GuardDuty Extended Threat Detection, AI 기반 보안 자동화 등 혁신적인 기능을 제공하며, 이를 통해 보안과 비용 최적화를 동시에 달성할 수 있습니다.

**핵심 결과물:**
- 13개 AWS 보안 서비스 통합 아키텍처
- FinOps 프레임워크 기반 비용 최적화 전략
- GuardDuty 자동화 대응 시스템 구축
- 태깅 전략 및 비용 할당 자동화
- Well-Architected Framework 적용 가이드

**측정 가능한 목표:**
- RI/SP 커버리지 70% 이상
- 태깅 준수율 95% 이상
- 보안 위협 대응 시간 5분 이내
- 비용 낭비율 5% 미만

**이 가이드는 클라우드 아키텍트, DevOps 엔지니어, FinOps 실무자를 대상으로 하며, 실무에 즉시 적용 가능한 코드와 설정을 제공합니다.**

## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 클라우드 시큐리티 과정 7기 3주차에서 다룬 **AWS 보안 및 FinOps**에 대해 실무 중심으로 정리합니다.

2025년 AWS는 보안 서비스와 비용 최적화 도구를 지속적으로 개선하고 있으며, 특히 **AWS Security Hub의 GA 출시**, **GuardDuty Extended Threat Detection**, **Cost Optimization Hub** 등 최신 기능들이 실무에 큰 도움을 주고 있습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- AWS 보안 서비스 전체 구조 및 각 서비스의 역할
- IAM 보안 모범 사례 및 VPC 보안 구성
- FinOps 프레임워크와 비용 최적화 전략
- AWS Well-Architected Framework 관점에서의 보안과 비용 균형

## 1. AWS 보안 아키텍처

<img src="{% raw %}{{ '/assets/images/diagrams/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_And_Finops/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_And_Finops_mermaid_chart_1.png' | relative_url }}{% endraw %}" alt="mermaid_chart_1" loading="lazy" class="post-image">

### 1.1 AWS 보안 서비스 전체 구조

AWS 보안 서비스는 계층화된 방어 전략(Defense in Depth)을 구현합니다. 각 서비스는 특정 보안 영역을 담당하며, Security Hub를 통해 통합 관리됩니다.

#### 1.1.1 Identity & Access Management 계층

**IAM Identity Center (AWS SSO)**
- 중앙 집중식 사용자 인증 및 권한 관리
- 다중 계정 환경에서 SSO 제공
- SAML 2.0 기반 외부 IdP 연동

**IAM (Identity and Access Management)**
- 세밀한 권한 제어 (Fine-grained Access Control)
- 정책 기반 권한 관리 (Policy-based Authorization)
- 임시 자격증명 발급 (STS - Security Token Service)

**AWS Organizations**
- 계정 그룹화 및 계층 구조 관리
- SCP (Service Control Policies)를 통한 계정 수준 권한 제어
- 통합 결제 및 리소스 공유

#### 1.1.2 Threat Detection & Response 계층

**Amazon GuardDuty**
- 지능형 위협 탐지 서비스
- VPC Flow Logs, CloudTrail, DNS 로그 분석
- 머신러닝 기반 이상 행위 탐지
- 2025년 신규: Extended Threat Detection (공격 시퀀스 탐지)

**Amazon Detective**
- 보안 이벤트 근본 원인 분석
- 시각화된 조사 도구 제공
- GuardDuty, Security Hub와 연동

**AWS Security Hub**
- 중앙 집중식 보안 관리 콘솔
- 모든 보안 서비스의 결과 통합
- 규정 준수 체크 (CIS, PCI-DSS, NIST 등)
- 2025년 신규: 커스텀 위젯, 히스토리 트렌드

#### 1.1.3 Vulnerability & Compliance 계층

**Amazon Inspector**
- EC2, ECR, Lambda 취약점 스캔
- CVSS 기반 위험도 평가
- 자동 패치 권장사항 제공

**AWS Config**
- 리소스 설정 변경 추적
- 규정 준수 규칙 평가
- 자동 수정 (Auto Remediation)

**Amazon Macie**
- S3 데이터 보안 및 개인정보 탐지
- 민감 데이터 자동 분류
- 데이터 유출 위험 평가

#### 1.1.4 Infrastructure Protection 계층

**AWS WAF (Web Application Firewall)**
- 웹 애플리케이션 보호
- OWASP Top 10 방어
- 관리형 규칙 그룹 제공
- Rate limiting 및 Geo-blocking

**AWS Shield**
- DDoS 방어 서비스
- Standard: 자동 보호 (무료)
- Advanced: 전담 지원 + 비용 보호

**AWS Network Firewall**
- 스테이트풀 네트워크 방화벽
- IDS/IPS 기능
- 도메인 필터링

**AWS Firewall Manager**
- 다중 계정 방화벽 정책 관리
- WAF, Shield, Network Firewall 통합 관리

#### 1.1.5 Data Protection 계층

**AWS KMS (Key Management Service)**
- 암호화 키 생성 및 관리
- 자동 키 로테이션
- CloudHSM 통합

**AWS Secrets Manager**
- 자격증명 자동 로테이션
- RDS, Redshift 등 AWS 서비스 네이티브 통합
- 세밀한 접근 제어

**AWS Certificate Manager**
- SSL/TLS 인증서 자동 갱신
- ALB, CloudFront 통합

#### 1.1.6 Audit & Compliance 계층

**AWS CloudTrail**
- API 호출 기록 (Audit Log)
- 계정 활동 추적 및 규정 준수
- S3, CloudWatch Logs 통합
- 변조 방지 (Log File Integrity Validation)

**AWS Audit Manager**
- 감사 준비 자동화
- 규정 준수 프레임워크 템플릿
- 증거 자동 수집

### 1.1.7 보안 서비스 통합 아키텍처



#### 1.2.2 조건부 정책 (Conditional Policies)

IP, MFA, 시간 등 조건 기반 접근 제어를 적용합니다.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
>
> ```json
> {...
> ```



#### 1.2.3 역할 기반 접근 제어 (RBAC)

사용자 대신 역할을 사용하여 임시 자격증명으로 작업합니다.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



#### 1.2.4 IAM Access Analyzer

IAM Access Analyzer는 외부에 노출된 리소스를 자동으로 탐지합니다.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. | 비정상적인 로그인, 브루트포스 공격 탐지 |
| **Execution (실행)** | Inspector, Config | 취약한 코드 실행, 악성 스크립트 탐지 |
| **Persistence (지속성)** | CloudTrail, Config | IAM 변경, 백도어 계정 생성 탐지 |
| **Privilege Escalation (권한 상승)** | IAM Access Analyzer, CloudTrail | 권한 변경, 정책 수정 탐지 |
| **Defense Evasion (방어 회피)** | GuardDuty, Detective | 로그 삭제, CloudTrail 비활성화 탐지 |
| **Credential Access (자격증명 탈취)** | GuardDuty, Macie | 키 유출, 자격증명 노출 탐지 |
| **Discovery (탐색)** | VPC Flow Logs, GuardDuty | 포트 스캔, 네트워크 탐색 탐지 |
| **Lateral Movement (측면 이동)** | GuardDuty, Detective | 비정상 네트워크 트래픽 탐지 |
| **Collection (수집)** | Macie, CloudTrail | 민감 데이터 접근 탐지 |
| **Exfiltration (유출)** | GuardDuty, Macie | 대용량 데이터 전송 탐지 |
| **Impact (영향)** | GuardDuty, Config | 리소스 삭제, 서비스 중단 탐지 |

### 7.2 GuardDuty 탐지와 MITRE ATT&CK

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython)를 참조하세요.
> 
> ```python
> # GuardDuty Finding을 MITRE ATT&CK 전술로 매핑...
> ```



## 8. 보안 운영 시나리오

### 8.1 침해 대응 플레이북

#### 8.1.1 인스턴스 침해 의심 시

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

#### 8.1.2 자동화된 포렌식 스냅샷

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요."]
        WAF["WAF"]
        Shield["Shield"]
    end

    subgraph "Network Layer"
        IGW["Internet Gateway"]
        ALB["Application Load Balancer"]
        NAT["NAT Gateway"]
        VPC["VPC"]
    end

    subgraph "Compute Layer"
        ASG["Auto Scaling Group"]
        EC2["EC2 Instances"]
    end

    subgraph "Data Layer"
        RDS["RDS"]
        S3["S3"]
    end

    subgraph "Security Services"
        GD["GuardDuty"]
        SH["Security Hub"]
        CT["CloudTrail"]
        CFG["Config"]
        INS["Inspector"]
        MAC["Macie"]
    end

    User --> CF
    Attacker -.->|Blocked| WAF
    CF --> WAF
    WAF --> Shield
    Shield --> IGW
    IGW --> ALB
    ALB --> ASG
    ASG --> EC2
    EC2 --> RDS
    EC2 --> S3

    VPC --> GD
    CT --> GD
    GD --> SH
    CFG --> SH
    INS --> SH
    MAC --> SH

    style WAF fill:#ff6b6b
    style GD fill:#4ecdc4
    style SH fill:#95e1d3


```

### 11.2 FinOps 데이터 플로우

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

---

📚 **외부 참고 자료:**
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [FinOps Foundation](https://www.finops.org/)

<!-- quality-upgrade:v1 -->
## Executive Summary
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | Medium | High | P1 |
| 구성 오류/권한 | Medium | High | P1 |
| 탐지/가시성 공백 | Low | Medium | P2 |

### 운영 개선 지표
| 지표 | 현재 기준 | 목표 | 검증 방법 |
|---|---|---|---|
| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |
| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |
| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |

### 실행 체크리스트
- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.
- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.
- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.
- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.
- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.

### 시각 자료
![Post Visual](/assets/images/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_and_Finops.svg)


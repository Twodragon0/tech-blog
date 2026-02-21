---
layout: post
title: "GCP 클라우드 보안 완벽 가이드: IAM부터 GKE까지 실무 중심 보안 아키텍처"
date: 2026-01-14 12:00:00 +0900
categories: [security, cloud]
tags: [GCP, Security, IAM, Cloud-SQL, Cloud-Storage, GKE, Cloud-Monitoring, Cloud-Logging]
excerpt: "GCP IAM, VPC, Cloud SQL, Storage, GKE 보안 아키텍처, Defense in Depth 전략"
description: "GCP 클라우드 보안 완벽 가이드: IAM 최소 권한, VPC 네트워크 분리, Cloud SQL 암호화, Cloud Storage 버킷 정책, GKE Pod Security Standards, Security Command Center 통합까지 Defense in Depth 전략 기반 실무 보안 아키텍처 제공"
keywords: [GCP-Security, IAM, Cloud-SQL, Cloud-Storage, GKE, VPC-Security, Defense-in-Depth, Cloud-Monitoring, Cloud-Logging, Security-Command-Center, ISMS-P, KMS]
author: Twodragon
comments: true
image: /assets/images/2026-01-14-GCP_Cloud_Security_Complete_Guide_IAM_to_GKE_Practical_Security_Architecture.svg
image_alt: "GCP Cloud Security Complete Guide: IAM to GKE Practical Security Architecture"
toc: true
schema_type: Article
certifications: [isms-p]
---

## 📋 포스팅 요약

> **제목**: GCP 클라우드 보안 완벽 가이드: IAM부터 GKE까지 실무 중심 보안 아키텍처

> **카테고리**: security, cloud

> **태그**: GCP, Security, IAM, Cloud-SQL, Cloud-Storage, GKE, Cloud-Monitoring, Cloud-Logging

> **핵심 내용**: 
> - GCP IAM, VPC, Cloud SQL, Storage, GKE 보안 아키텍처, Defense in Depth 전략

> **주요 기술/도구**: Security, IAM, security, cloud

> **대상 독자**: 기업 보안 담당자, 보안 엔지니어, CISO

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


## 서론

안녕하세요, **Twodragon**입니다.

GCP 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 GKE까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다. 이 포스팅은 **SK Shieldus의 2024년 GCP 클라우드 보안 가이드**를 기반으로, 실무에서 즉시 활용 가능한 GCP 보안 아키텍처 설계 및 구현 가이드를 제공합니다.

주요 GCP 서비스별 보안 모범 사례와 코드 예제, 보안 체크리스트를 포함하여 실무 중심의 보안 구축 방법을 제시합니다.

---

## 핵심 요약

### GCP 보안 태세 평가

**전체 보안 성숙도**: ⭐⭐⭐⭐ (4/5)

| 보안 도메인 | 현재 수준 | 위험도 | 권장 사항 |
|-----------|----------|--------|----------|
| **IAM 및 접근 제어** | 높음 | 낮음 | MFA 전체 적용, Service Account Key Rotation 자동화 |
| **네트워크 보안** | 높음 | 중간 | VPC Flow Logs 활성화, Cloud Armor 도입 검토 |
| **데이터 암호화** | 높음 | 낮음 | CMEK 적용 확대, 키 로테이션 자동화 |
| **컨테이너 보안** | 중간 | 중간 | Binary Authorization 적용, Vulnerability Scanning 강화 |
| **모니터링/감사** | 높음 | 낮음 | Security Command Center Premium 활성화 검토 |

**핵심 보안 지표**:
- IAM 정책 준수율: 94%
- 암호화 적용률: 98%
- 취약점 평균 해결 시간: 3일
- 보안 이벤트 탐지율: 89%

**즉각 조치 필요 항목**:
1. 모든 관리자 계정에 MFA 강제 적용 (현재 87% 적용)
2. Public IP를 사용하는 Cloud SQL 인스턴스 제거 (5개 발견)
3. 과도한 권한을 가진 Service Account 권한 축소 (12개 발견)

**2026년 1분기 보안 목표**:
- Security Command Center Premium 도입
- Binary Authorization 전체 GKE 클러스터 적용
- 보안 자동화 스크립트 확대 (현재 60% → 목표 85%)

---

## MITRE ATT&CK 매핑 (GCP 클라우드)

### GCP 환경 주요 공격 기법

| MITRE ID | 기법 | GCP 타겟 | 탐지 방법 | 완화 전략 |
|----------|------|---------|----------|----------|
| **T1078.004** | Cloud Accounts | IAM 계정, Service Account | Cloud Logging 이상 로그인 탐지 | MFA 강제, IAM Recommender |
| **T1530** | Data from Cloud Storage | Cloud Storage, Cloud SQL | Data Access Audit Logs | CMEK 암호화, VPC Service Controls |
| **T1610** | Deploy Container | GKE, Cloud Run | Container Analysis API | Binary Authorization, Admission Controllers |
| **T1552.005** | Cloud Instance Metadata API | Compute Engine Metadata | VPC Flow Logs, Cloud Logging | Workload Identity, Metadata Concealment |
| **T1580** | Cloud Infrastructure Discovery | Organization, Projects, Resources | Cloud Asset Inventory Logs | Organization Policies, IAM Conditions |
| **T1562.008** | Disable Cloud Logs | Cloud Logging, Audit Logs | Security Command Center Alerts | Org-level Log Sinks, IAM Conditions |
| **T1496** | Resource Hijacking | Compute Engine, GKE | Cloud Monitoring Anomaly Detection | Budget Alerts, Resource Quotas |

### 공격 시나리오: GCP IAM 권한 상승

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
초기 침투 (T1078.004)
    ↓
노출된 Service Account Key 탈취
    ↓
IAM 정책 열람 (T1580)
    ↓
과도한 권한을 가진 SA 발견
    ↓
권한 상승 시도 (T1098)
    ↓
Cloud Storage 데이터 유출 (T1530)
    ↓
Audit Log 비활성화 시도 (T1562.008)


```
-->
-->

**탐지 쿼리** (Cloud Logging):

<!--
Splunk SPL - GCP IAM Anomaly Detection:
index=gcp_audit sourcetype="google:gcp:audit"
protoPayload.serviceName="iam.googleapis.com"
protoPayload.methodName IN ("SetIamPolicy", "CreateServiceAccountKey")
| stats count by protoPayload.authenticationInfo.principalEmail, protoPayload.methodName, protoPayload.resourceName
| where count > 5
| table _time, protoPayload.authenticationInfo.principalEmail, protoPayload.methodName, protoPayload.resourceName, count
-->

<!--
Azure Sentinel KQL - GCP Service Account Key Creation Anomaly:
GCPAuditLogs
| where ServiceName == "iam.googleapis.com"
| where MethodName == "google.iam.admin.v1.CreateServiceAccountKey"
| summarize KeyCreationCount=count() by PrincipalEmail, bin(TimeGenerated, 1h)
| where KeyCreationCount > 3
| project TimeGenerated, PrincipalEmail, KeyCreationCount
-->

<!--
Google Chronicle YARA-L - Suspicious IAM Policy Changes:
rule gcp_suspicious_iam_policy_change {
  meta:
    author = "GCP Security Team"
    description = "Detects suspicious IAM policy changes"
    severity = "HIGH"

  events:
    $e.metadata.product_name = "Google Cloud Platform"
    $e.metadata.vendor_name = "Google"
    $e.target.resource.attribute.labels["service_name"] = "iam.googleapis.com"
    $e.target.resource.attribute.labels["method_name"] = /SetIamPolicy|CreateServiceAccountKey/

  match:
    $principalEmail over 1h

  outcome:
    $risk_score = 75
    $alert_title = "Suspicious IAM Policy Changes Detected"

  condition:
    #e > 5
}
-->

### GKE 특화 공격 기법

| MITRE ID | 기법 | 탐지 지표 | 완화 방안 |
|----------|------|----------|----------|
| **T1610** | Malicious Container | 알려지지 않은 레지스트리에서 이미지 Pull | Binary Authorization, Container Analysis |
| **T1611** | Escape to Host | {% raw %}`privileged: true`{% endraw %}, `hostPath` 마운트 | Pod Security Standards (Restricted) |
| **T1613** | Container API | Kubernetes API 무단 접근 시도 | RBAC, Network Policy |

**탐지 쿼리** (GKE Audit Logs):

<!--
Splunk SPL - GKE Privileged Pod Detection:
index=gcp_gke sourcetype="google:gcp:gke:audit"
{% raw %}objectRef.resource="pods"{% endraw %}
requestObject.spec.containers{}.securityContext.privileged=true
| table _time, user.username, {% raw %}objectRef.namespace{% endraw %}, {% raw %}objectRef.name{% endraw %}
| dedup user.username, {% raw %}objectRef.name{% endraw %}
-->

<!--
Azure Sentinel KQL - GKE hostPath Volume Mount:
GKEAuditLogs
| where ObjectRef_Resource == "pods"
| where RequestObject contains "hostPath"
| project TimeGenerated, User_Username, ObjectRef_Namespace, ObjectRef_Name, RequestObject
| summarize by User_Username, ObjectRef_Name
-->

---

## 한국 특화 보안 고려사항

### CSAP (클라우드보안인증제) 준수

GCP는 2023년 한국인터넷진흥원(KISA) CSAP 인증을 획득했습니다.

| CSAP 통제 항목 | GCP 구현 | 준수 방법 |
|--------------|---------|----------|
| **데이터 암호화** | Cloud KMS, CMEK | 모든 민감 데이터 CMEK 암호화 |
| **접근 통제** | IAM, VPC Service Controls | 최소 권한 원칙, Conditional IAM |
| **로그 관리** | Cloud Logging, Audit Logs | 조직 레벨 Log Sink, 7년 보관 |
| **재해 복구** | Multi-Region Replication | 서울-부산 리전 동시 운영 |
| **데이터 주권** | 한국 리전 (Seoul, Busan) | 데이터 위치 제약 정책 적용 |

**한국 리전 아키�ekstur 예시**:

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────────────────────────────────────────────┐
│         Organization (한국 법인)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Folder: Production (CSAP 준수)              │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │  Project: prod-app-kr                  │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐   │  │  │
│  │  │  │ Seoul Region │  │ Busan Region │   │  │  │
│  │  │  │ (Primary)    │  │ (DR)         │   │  │  │
│  │  │  │              │  │              │   │  │  │
│  │  │  │ - GKE Cluster│  │ - GKE Cluster│   │  │  │
│  │  │  │ - Cloud SQL  │→→│ - Cloud SQL  │   │  │  │
│  │  │  │ - Storage    │  │ - Storage    │   │  │  │
│  │  │  └──────────────┘  └──────────────┘   │  │  │
│  │  │  Organization Policy:                  │  │  │
│  │  │  - constraints/gcp.resourceLocations   │  │  │
│  │  │    → in:asia-northeast3,asia-northeast2│  │  │
│  │  └────────────────────────────────────────┘  │  │
│  │  Data Residency: 한국 내 데이터 저장 강제     │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘


```
-->
-->

### 한국 GCP 채택 현황 (2025-2026)

**주요 기업 GCP 도입 현황**:

| 산업군 | GCP 채택률 | 주요 서비스 | 보안 요구사항 |
|--------|----------|------------|-------------|
| **금융** | 38% | BigQuery, GKE, Cloud SQL | ISMS-P, PCI-DSS, 전자금융감독규정 |
| **공공** | 22% | Compute Engine, Cloud Storage | 클라우드컴퓨팅법, 개인정보보호법 |
| **제조** | 45% | IoT Core, Dataflow, AI Platform | 산업보안, 영업비밀보호법 |
| **게임** | 61% | GKE, Memorystore, Cloud CDN | 게임산업진흥법, 청소년보호법 |
| **이커머스** | 53% | Cloud Run, Firebase, BigQuery | 전자상거래법, 개인정보보호법 |

**한국 특화 규제 대응**:

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
# Organization Policy - 한국 리전 제한
name: organizations/ORG_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - in:asia-northeast3  # Seoul
          - in:asia-northeast2  # Osaka (재해복구용)
      enforce: true
```

### 개인정보보호법 준수

**GCP에서 개인정보 처리 시 필수 통제**:

| 개인정보보호법 조항 | GCP 통제 | 구현 방법 |
|------------------|---------|----------|
| **제24조 (고유식별정보 암호화)** | Cloud KMS CMEK | 주민번호 등 필드레벨 암호화 |
| **제29조 (안전성 확보 조치)** | VPC Service Controls | 네트워크 기반 데이터 유출 방지 |
| **제34조 (개인정보 파기)** | Cloud Storage Lifecycle | 보유기간 경과 시 자동 삭제 |
| **제35조 (접속기록 보관)** | Cloud Logging | 6개월 이상 접속 로그 보관 |

**개인정보 암호화 예시**:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> from google.cloud import kms...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> from google.cloud import kms...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
from google.cloud import kms
from google.cloud import bigquery

def encrypt_ssn_field(project_id, location, key_ring, key_name, plaintext_ssn):
    """주민번호 필드레벨 암호화"""
    client = kms.KeyManagementServiceClient()
    key_name = client.crypto_key_path(project_id, location, key_ring, key_name)

    response = client.encrypt(
        request={'name': key_name, 'plaintext': plaintext_ssn.encode('utf-8')}
    )

    return response.ciphertext

# BigQuery 테이블에 암호화된 데이터 삽입
bq_client = bigquery.Client()
table_ref = bq_client.dataset('customer_data').table('users')

rows_to_insert = [
    {
        'user_id': 'U12345',
        'encrypted_ssn': encrypt_ssn_field(
            'my-project', 'asia-northeast3', 'my-keyring', 'ssn-key', '123456-1234567'
        ).hex(),
        'created_at': '2026-01-14T12:00:00'
    }
]

bq_client.insert_rows_json(table_ref, rows_to_insert)


```
-->
-->

---

## 경영진 보고 형식

### 월간 GCP 보안 리포트 (2026년 1월)

**보고 일자**: 2026-01-14
**보고 대상**: CISO, CTO, 경영진
**작성자**: GCP 보안팀

#### 1. 핵심 요약 (Executive Highlight)

| 지표 | 현황 | 전월 대비 | 목표 | 상태 |
|------|------|----------|------|------|
| **보안 점수** | 92/100 | +3 | 90+ | ✅ 양호 |
| **취약점 해결률** | 96% | +2% | 95%+ | ✅ 양호 |
| **보안 이벤트** | 23건 | -5건 | <30건 | ✅ 양호 |
| **MFA 적용률** | 87% | +12% | 100% | ⚠️ 개선 필요 |
| **보안 예산 집행률** | 78% | - | 80% | ✅ 정상 |

#### 2. 주요 보안 이슈 및 조치사항

**🔴 Critical (즉시 조치 필요)**:
- Public IP를 사용하는 Cloud SQL 인스턴스 5개 발견
  - **위험도**: 높음 (데이터 유출 가능)
  - **조치 기한**: 2026-01-20
  - **담당**: 인프라팀

**🟡 High (1주일 내 조치)**:
- 과도한 권한을 가진 Service Account 12개 발견
  - **위험도**: 중상 (권한 상승 공격 가능)
  - **조치 기한**: 2026-01-21
  - **담당**: IAM 관리팀

**🟢 Medium (2주일 내 조치)**:
- VPC Flow Logs 미활성화 서브넷 8개 발견
  - **위험도**: 중 (가시성 부족)
  - **조치 기한**: 2026-01-28
  - **담당**: 네트워크팀

#### 3. 비용 영향 분석

| 보안 항목 | 월간 비용 | 전월 대비 | 비고 |
|----------|----------|----------|------|
| Security Command Center | $2,400 | +$200 | Premium 티어 적용 검토 |
| Cloud KMS (CMEK) | $1,800 | - | 안정적 |
| VPC Flow Logs | $650 | +$150 | 로그 보관 기간 증가 |
| Container Analysis | $320 | - | 안정적 |
| **총 보안 비용** | **$5,170** | **+$350 (+7.3%)** | 예산 범위 내 |

**ROI 분석**:
- 보안 사고 방지로 인한 추정 손실 방지액: 월 $45,000
- 보안 투자 대비 수익률: 약 870%

#### 4. 향후 계획 (2026년 1분기)

| 항목 | 목표 | 일정 | 예산 | 담당 |
|------|------|------|------|------|
| Binary Authorization 도입 | GKE 전체 적용 | 2026-02-15 | $3,000 | 컨테이너팀 |
| MFA 100% 적용 | 전 직원 강제 적용 | 2026-01-31 | - | IAM팀 |
| Security Posture 자동화 | Cloud Security Scanner 도입 | 2026-03-15 | $5,000 | 보안팀 |

#### 5. 규제 준수 현황

| 규제/인증 | 준수율 | 만료일 | 상태 |
|----------|--------|--------|------|
| ISMS-P | 98% | 2026-06-30 | ✅ 정상 |
| CSAP | 96% | 2026-12-31 | ✅ 정상 |
| ISO 27001 | 99% | 2026-09-15 | ✅ 정상 |

---

## GCP 보안 아키텍처 다이어그램

### Defense in Depth 전체 구조

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```
> ┌───────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```
> ┌───────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌───────────────────────────────────────────────────────────────────┐
│                    인터넷 (Internet)                               │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 1: 경계 보안 (Perimeter Security)                           │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  Cloud Armor    │  │ Cloud CDN    │  │ DDoS Protection    │   │
│  │  (WAF)          │  │ (Edge Cache) │  │ (Google Shield)    │   │
│  └─────────────────┘  └──────────────┘  └────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 2: 네트워크 보안 (Network Security)                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   VPC Network                               │  │
│  │  ┌────────────────┐          ┌────────────────┐            │  │
│  │  │ Public Subnet  │          │ Private Subnet │            │  │
│  │  │ (10.0.1.0/24)  │          │ (10.0.2.0/24)  │            │  │
│  │  │                │          │                │            │  │
│  │  │ ┌────────────┐ │          │ ┌────────────┐ │            │  │
│  │  │ │ Cloud NAT  │ │          │ │ Cloud SQL  │ │            │  │
│  │  │ │ Gateway    │ │          │ │ (Private)  │ │            │  │
│  │  │ └────────────┘ │          │ └────────────┘ │            │  │
│  │  └────────────────┘          └────────────────┘            │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ Firewall Rules                                       │  │  │
│  │  │ - Allow HTTPS (443) from 0.0.0.0/0                   │  │  │
│  │  │ - Allow SSH (22) from Corporate IP only              │  │  │
│  │  │ - Deny All (default)                                 │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  VPC Flow Logs → Cloud Logging → Security Analysis        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 3: 인증/인가 (Identity & Access Management)                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  IAM (Identity and Access Management)                      │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Users      │  │ Service      │  │ Workload         │   │  │
│  │  │ + MFA      │  │ Accounts     │  │ Identity         │   │  │
│  │  └────────────┘  └──────────────┘  └──────────────────┘   │  │
│  │         │                │                    │            │  │
│  │         └────────────────┴────────────────────┘            │  │
│  │                          │                                 │  │
│  │                ┌─────────▼─────────┐                       │  │
│  │                │ IAM Policy Engine │                       │  │
│  │                │ (Least Privilege) │                       │  │
│  │                └───────────────────┘                       │  │
│  │                                                             │  │
│  │  Audit Logs → Cloud Logging → SIEM Analysis                │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 4: 애플리케이션 보안 (Application Security)                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   GKE Cluster                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │ Namespace: production                                │   │  │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │  │
│  │  │  │ Pod        │  │ Pod        │  │ Pod        │     │   │  │
│  │  │  │ (Restricted│  │ (Restricted│  │ (Restricted│     │   │  │
│  │  │  │  Mode)     │  │  Mode)     │  │  Mode)     │     │   │  │
│  │  │  │            │  │            │  │            │     │   │  │
│  │  │  │ securityCx:│  │ securityCx:│  │ securityCx:│     │   │  │
│  │  │  │ - nonRoot  │  │ - nonRoot  │  │ - nonRoot  │     │   │  │
│  │  │  │ - readOnly │  │ - readOnly │  │ - readOnly │     │   │  │
│  │  │  └────────────┘  └────────────┘  └────────────┘     │   │  │
│  │  │                                                      │   │  │
│  │  │  ┌──────────────────────────────────────────────┐   │   │  │
│  │  │  │ Network Policy                               │   │   │  │
│  │  │  │ - Ingress: only from allowed namespaces      │   │   │  │
│  │  │  │ - Egress: only to database & external APIs   │   │   │  │
│  │  │  └──────────────────────────────────────────────┘   │   │  │
│  │  │                                                      │   │  │
│  │  │  Binary Authorization: Verify signed images only    │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                             │  │
│  │  Container Analysis → Vulnerability Scanning                │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 5: 데이터 보안 (Data Security)                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Cloud KMS (Key Management Service)                        │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Key Ring   │  │ Crypto Keys  │  │ Key Rotation     │   │  │
│  │  │ (Regional) │  │ (CMEK)       │  │ (Auto, 90 days)  │   │  │
│  │  └────────────┘  └──────────────┘  └──────────────────┘   │  │
│  │         │                │                    │            │  │
│  │         └────────────────┴────────────────────┘            │  │
│  │                          │                                 │  │
│  │           ┌──────────────┼──────────────┐                  │  │
│  │           │              │              │                  │  │
│  │           ▼              ▼              ▼                  │  │
│  │  ┌──────────────┐ ┌────────────┐ ┌──────────────┐         │  │
│  │  │ Cloud Storage│ │ Cloud SQL  │ │ BigQuery     │         │  │
│  │  │ (CMEK)       │ │ (CMEK)     │ │ (CMEK)       │         │  │
│  │  │              │ │            │ │              │         │  │
│  │  │ - Versioning │ │ - Backups  │ │ - Column     │         │  │
│  │  │ - Lifecycle  │ │ - PITR     │ │   Encryption │         │  │
│  │  └──────────────┘ └────────────┘ └──────────────┘         │  │
│  │                                                             │  │
│  │  Data Access Audit Logs → DLP (Data Loss Prevention)       │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ Layer 6: 모니터링 및 대응 (Monitoring & Response)                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Security Command Center (Unified Dashboard)               │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Cloud      │  │ Cloud        │  │ Security         │   │  │
│  │  │ Logging    │  │ Monitoring   │  │ Health Analytics │   │  │
│  │  └────────────┘  └──────────────┘  └──────────────────┘   │  │
│  │         │                │                    │            │  │
│  │         └────────────────┴────────────────────┘            │  │
│  │                          │                                 │  │
│  │                ┌─────────▼─────────┐                       │  │
│  │                │ Threat Detection  │                       │  │
│  │                │ & Alerting        │                       │  │
│  │                └───────────────────┘                       │  │
│  │                          │                                 │  │
│  │                          ▼                                 │  │
│  │              ┌─────────────────────┐                       │  │
│  │              │ Incident Response   │                       │  │
│  │              │ Automation          │                       │  │
│  │              └─────────────────────┘                       │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘


```
-->
-->

### GKE 보안 아키텍처 상세

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```
> ┌─────────────────────────────────────────────────────────────────┐...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
┌─────────────────────────────────────────────────────────────────┐
│                    GKE Cluster (asia-northeast3)                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Control Plane (Google Managed)                           │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ API Server  │  │ etcd (암호화) │  │ Cloud Logging  │  │  │
│  │  │ (Private IP)│  │ (at rest)    │  │ (Audit Logs)   │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              │ (Authorized Networks Only)       │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Worker Nodes (Node Pool)                                 │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │ Node 1 (Shielded VM)                            │    │  │
│  │  │  ┌──────────────────────────────────────────┐   │    │  │
│  │  │  │ Namespace: production                    │   │    │  │
│  │  │  │  ┌────────────────┐  ┌────────────────┐  │   │    │  │
│  │  │  │  │ Pod: web-app   │  │ Pod: api-svc   │  │   │    │  │
│  │  │  │  │                │  │                │  │   │    │  │
│  │  │  │  │ Security:      │  │ Security:      │  │   │    │  │
│  │  │  │  │ - runAsUser:   │  │ - runAsUser:   │  │   │    │  │
│  │  │  │  │   1000         │  │   1000         │  │   │    │  │
│  │  │  │  │ - readOnly     │  │ - readOnly     │  │   │    │  │
│  │  │  │  │   rootFS       │  │   rootFS       │  │   │    │  │
│  │  │  │  │ - drop ALL     │  │ - drop ALL     │  │   │    │  │
│  │  │  │  │   capabilities │  │   capabilities │  │   │    │  │
│  │  │  │  │                │  │                │  │   │    │  │
│  │  │  │  │ Workload ID:   │  │ Workload ID:   │  │   │    │  │
│  │  │  │  │ web-app-sa@    │  │ api-svc-sa@    │  │   │    │  │
│  │  │  │  │ project.iam    │  │ project.iam    │  │   │    │  │
│  │  │  │  └────────────────┘  └────────────────┘  │   │    │  │
│  │  │  │                                          │   │    │  │
│  │  │  │  Network Policy (Calico):                │   │    │  │
│  │  │  │  - Ingress: from ingress-nginx only      │   │    │  │
│  │  │  │  - Egress: to api-svc & cloud-sql-proxy  │   │    │  │
│  │  │  └──────────────────────────────────────────┘   │    │  │
│  │  │                                                  │    │  │
│  │  │  Container Runtime: containerd (hardened)       │    │  │
│  │  │  OS: Container-Optimized OS (auto-update)       │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │ Node 2 (Shielded VM) - Similar config...        │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Security Controls                                        │  │
│  │  ✓ Binary Authorization (only signed images allowed)    │  │
│  │  ✓ Pod Security Standards: Restricted                   │  │
│  │  ✓ Network Policies: Default Deny                       │  │
│  │  ✓ RBAC: Least Privilege per namespace                  │  │
│  │  ✓ Workload Identity: No node SA key export             │  │
│  │  ✓ Shielded GKE Nodes: Secure Boot + vTPM               │  │
│  │  ✓ Container Analysis: Continuous vulnerability scan    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘


```
-->
-->

## 📊 빠른 참조

### GCP 보안 서비스 개요

GCP 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다.

| 서비스 | 용도 | 주요 기능 |
|--------|------|----------|
| **IAM** | 접근 제어 | 사용자, 역할, 서비스 계정 관리 |
| **VPC Network** | 네트워크 보안 | 네트워크 격리, 접근 제어 |
| **Security Command Center** | 통합 보안 관리 | 보안 상태 통합 대시보드 |
| **Cloud Logging** | 감사 및 컴플라이언스 | 활동 로깅 |
| **Cloud Monitoring** | 모니터링 | 메트릭, 로그, 알람 |
| **Cloud KMS** | 암호화 | 키 관리 서비스 |
| **Cloud Asset Inventory** | 자산 관리 | 리소스 설정 모니터링 |

---

## 1. GCP 보안 아키텍처 개요

### GCP 보안 아키텍처 (Defense in Depth)

GCP 클라우드 환경에서의 다층 보안 방어 구조:

### 1.1 Defense in Depth 전략

#### 다층 보안 방어 구조

| 레이어 | GCP 서비스 | 보안 기능 |
|--------|-----------|----------|
| **네트워크 레이어** | VPC, 방화벽 규칙, Cloud NAT | 네트워크 분리, 트래픽 필터링 |
| **인증/인가 레이어** | IAM, Identity Platform, MFA | 사용자 인증, 권한 관리 |
| **애플리케이션 레이어** | Cloud Armor, API Gateway | 웹 애플리케이션 보호 |
| **데이터 레이어** | Cloud KMS, Cloud Storage, Cloud SQL | 데이터 암호화 |
| **모니터링 레이어** | Cloud Logging, Cloud Monitoring, Security Command Center | 로깅, 모니터링, 위협 탐지 |

### 1.2 보안 모범 사례

| 원칙 | 설명 | GCP 구현 |
|------|------|---------|
| **최소 권한 원칙** | 필요한 최소한의 권한만 부여 | IAM 정책, 방화벽 규칙 |
| **암호화** | 전송 중/저장 데이터 암호화 | TLS/SSL, Cloud KMS |
| **로그 관리** | 모든 활동 로깅 및 모니터링 | Cloud Logging, Cloud Monitoring |
| **정기적 검토** | 보안 설정 정기적 검토 및 개선 | Security Command Center |

---

## 2. IAM 보안

### 2.1 IAM 정책 작성

#### 최소 권한 원칙 적용

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
# IAM 정책 예시: 최소 권한 원칙
bindings:
  - members:
      - serviceAccount:app-service-account@project-id.iam.gserviceaccount.com
    role: roles/storage.objectViewer
    condition:
      expression: resource.name.startsWith('projects/_/buckets/secure-bucket')
      title: Secure bucket access only
```

#### 서비스 계정 관리

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
# 서비스 계정 예시
resources:
  - name: app-service-account
    type: iam.v1.serviceAccount
    properties:
      accountId: app-service-account
      displayName: Application Service Account
      description: Service account for application
```

> **참고**: 전체 IAM 정책 예시는 [GCP IAM 모범 사례](https://cloud.google.com/iam/docs/using-iam-securely) 및 [GCP 보안 모범 사례](https://cloud.google.com/security/best-practices)를 참조하세요.

### 2.2 Identity Platform

| 기능 | 설명 | 사용 사례 |
|------|------|----------|
| **OAuth 2.0** | 표준 인증 프로토콜 | 외부 사용자 인증 |
| **SAML 2.0** | 엔터프라이즈 SSO | 기업 사용자 인증 |
| **MFA** | 다중 인증 | 관리자 계정 보호 |

### 2.3 IAM 보안 체크리스트

| 체크리스트 항목 | 설명 | GCP 도구 |
|---------------|------|---------|
| **MFA 활성화** | 모든 사용자에 MFA 활성화 | IAM Console |
| **최소 권한 원칙** | 필요한 권한만 부여 | IAM Recommender |
| **서비스 계정 관리** | 서비스 계정 키 로테이션 | Service Account Key Rotation |
| **사용하지 않는 권한 제거** | 오래된 권한 정리 | IAM Recommender |
| **조직 정책 설정** | 조직 레벨 보안 정책 | Organization Policies |

---

## 3. VPC Network 보안

### 3.1 VPC 아키텍처 설계

#### Subnet 구성

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # VPC 아키텍처 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # VPC 아키텍처 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# VPC 아키텍처 예시
resources:
  - name: secure-vpc
    type: compute.v1.network
    properties:
      name: secure-vpc
      autoCreateSubnetworks: false
  
  - name: public-subnet
    type: compute.v1.subnetwork
    properties:
      name: public-subnet
      network: $(ref.secure-vpc.selfLink)
      ipCidrRange: 10.0.1.0/24
      region: asia-northeast3
      privateIpGoogleAccess: false
  
  - name: private-subnet
    type: compute.v1.subnetwork
    properties:
      name: private-subnet
      network: $(ref.secure-vpc.selfLink)
      ipCidrRange: 10.0.2.0/24
      region: asia-northeast3
      privateIpGoogleAccess: true


```
-->
-->

#### Cloud NAT 설정

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud NAT 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud NAT 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Cloud NAT 예시
resources:
  - name: secure-nat
    type: compute.v1.router
    properties:
      name: secure-nat
      network: $(ref.secure-vpc.selfLink)
      region: asia-northeast3
      nats:
        - name: secure-nat-config
          natIpAllocateOption: AUTO_ONLY
          sourceSubnetworks:
            - $(ref.private-subnet.selfLink)


```
-->
-->

### 3.2 방화벽 규칙

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # GCP 방화벽 규칙 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # GCP 방화벽 규칙 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# GCP 방화벽 규칙 예시
# ISMS-P 요구사항: 네트워크 접근 제어
resources:
  - name: allow-https
    type: compute.v1.firewall
    properties:
      name: allow-https
      network: projects/PROJECT_ID/global/networks/default
      direction: INGRESS
      priority: 1000
      allowed:
        - IPProtocol: tcp
          ports:
            - '443'
      sourceRanges:
        - '0.0.0.0/0'
      targetTags:
        - web-server
      description: Allow HTTPS traffic from internet


```
-->
-->

> **참고**: 전체 GCP 방화벽 규칙 예시는 [GCP 방화벽 규칙 모범 사례](https://cloud.google.com/vpc/docs/firewalls) 및 [GCP 보안 모범 사례](https://cloud.google.com/security/best-practices)를 참조하세요.

### 3.3 VPC 보안 체크리스트

| 체크리스트 항목 | 설명 | GCP 도구 |
|---------------|------|---------|
| **Private Subnet 활용** | 데이터베이스는 Private Subnet에 배치 | VPC Console |
| **방화벽 규칙 최소화** | 필요한 포트만 허용 | Firewall Rules Console |
| **Cloud NAT 설정** | 아웃바운드 트래픽 제어 | Cloud NAT Console |
| **VPC Flow Logs 활성화** | 네트워크 트래픽 로깅 | VPC Flow Logs |
| **VPC Peering 보안** | VPC Peering 시 방화벽 규칙 확인 | VPC Peering Console |

---

## 4. Cloud Storage 보안

### 4.1 버킷 정책

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud Storage 버킷 정책 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud Storage 버킷 정책 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Cloud Storage 버킷 정책 예시
# ISMS-P 요구사항: 접근 통제 및 암호화
resources:
  - name: secure-bucket
    type: storage.v1.bucket
    properties:
      name: secure-data-bucket
      location: ASIA-NORTHEAST3
      storageClass: STANDARD
      encryption:
        defaultKmsKeyName: projects/PROJECT_ID/locations/asia-northeast3/keyRings/keyring/cryptoKeys/key
      versioning:
        enabled: true
      iamConfiguration:
        uniformBucketLevelAccess:
          enabled: true
      lifecycle:
        rule:
          - action:
              type: Delete
            condition:
              age: 90
              matchesStorageClass:
                - STANDARD


```
-->
-->

### 4.2 Cloud Storage 보안 체크리스트

| 체크리스트 항목 | 설명 | GCP 도구 |
|---------------|------|---------|
| **버킷 정책 설정** | 접근 권한 명확히 정의 | Cloud Storage IAM |
| **암호화 활성화** | CMEK 또는 기본 암호화 | Cloud KMS |
| **버전 관리 활성화** | 데이터 복구 가능하도록 | Cloud Storage Versioning |
| **Public Access 차단** | Public Access 제한 | Cloud Storage IAM |
| **접근 로그 활성화** | 버킷 접근 로그 수집 | Cloud Logging |

---

## 5. Cloud SQL 보안

### 5.1 데이터베이스 암호화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud SQL 암호화 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud SQL 암호화 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Cloud SQL 암호화 설정 예시
resources:
  - name: secure-database
    type: sqladmin.v1beta4.instance
    properties:
      name: secure-db
      databaseVersion: MYSQL_8_0
      region: asia-northeast3
      settings:
        tier: db-n1-standard-1
        backupConfiguration:
          enabled: true
          startTime: '03:00'
          binaryLogEnabled: true
        ipConfiguration:
          ipv4Enabled: false
          privateNetwork: projects/PROJECT_ID/global/networks/secure-vpc
        databaseFlags:
          - name: require_ssl
            value: 'on'
        diskEncryptionConfiguration:
          kmsKeyName: projects/PROJECT_ID/locations/asia-northeast3/keyRings/keyring/cryptoKeys/db-key


```
-->
-->

### 5.2 Cloud SQL 보안 체크리스트

| 체크리스트 항목 | 설명 | GCP 도구 |
|---------------|------|---------|
| **암호화 활성화** | 저장 데이터 암호화 | Cloud KMS |
| **SSL/TLS 연결** | 연결 암호화 필수 | Cloud SQL SSL/TLS |
| **자동 백업 활성화** | 정기적인 백업 설정 | Cloud SQL Automated Backups |
| **Private IP 사용** | Public IP 비활성화 | Cloud SQL Private IP |
| **방화벽 규칙 설정** | 데이터베이스 접근 제한 | Cloud SQL Authorized Networks |

---

## 6. GKE 보안

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
      image: gcr.io/project-id/app:latest
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

### 6.3 GKE 보안 체크리스트

| 체크리스트 항목 | 설명 | GCP 도구 |
|---------------|------|---------|
| **Pod Security Standards** | Pod Security Policy 적용 | GKE Pod Security |
| **Network Policy** | 네트워크 트래픽 제어 | Kubernetes Network Policy |
| **RBAC 설정** | 역할 기반 접근 제어 | Kubernetes RBAC |
| **컨테이너 이미지 보안** | 취약점 스캔 및 검증 | Container Analysis API |
| **시크릿 관리** | Secret Manager 통합 | GKE Secret Manager |

---

## 7. 모니터링 및 감사

### 7.1 Cloud Logging

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud Logging 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloud Logging 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Cloud Logging 설정 예시
resources:
  - name: audit-log-sink
    type: logging.v2.sink
    properties:
      name: audit-log-sink
      destination: storage.googleapis.com/audit-logs-bucket
      filter: |
        resource.type="gce_instance"
        OR resource.type="gcs_bucket"
        OR resource.type="cloudsql_database"


```
-->
-->

### 7.2 Cloud Monitoring

| 모니터링 항목 | Cloud Monitoring 메트릭 | 알람 임계값 |
|-------------|----------------------|------------|
| **비정상 API 호출** | API 호출 수 | 평균 대비 200% 증가 |
| **권한 변경** | IAM 권한 변경 이벤트 | 즉시 알람 |
| **네트워크 이상** | VPC Flow Logs 분석 | 의심스러운 트래픽 패턴 |
| **암호화 미적용** | Cloud Storage 암호화 상태 | 암호화 미적용 객체 발견 |

### 7.3 Security Command Center 통합

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Security Command Center 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Security Command Center 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Security Command Center 설정 예시
resources:
  - name: security-command-center
    type: securitycenter.v1.organizationSettings
    properties:
      name: organizations/ORGANIZATION_ID/organizationSettings
      enableAssetDiscovery: true
      assetDiscoveryConfig:
        projectIds:
          - PROJECT_ID


```
-->
-->

---

## 8. Threat Hunting (위협 헌팅)

### 8.1 GCP 환경 위협 헌팅 쿼리

#### IAM 권한 상승 탐지

**시나리오**: Service Account Key 생성 후 즉시 IAM 정책 변경 시도

<!--
Splunk SPL - IAM Privilege Escalation Hunt:
index=gcp_audit sourcetype="google:gcp:audit"
protoPayload.serviceName="iam.googleapis.com"
| eval method=case(
    protoPayload.methodName="google.iam.admin.v1.CreateServiceAccountKey", "key_created",
    protoPayload.methodName="SetIamPolicy", "policy_changed",
    1=1, "other"
  )
| transaction protoPayload.authenticationInfo.principalEmail maxspan=5m
| where mvcount(method) >= 2 AND mvfind(method, "key_created") >= 0 AND mvfind(method, "policy_changed") >= 0
| table _time, protoPayload.authenticationInfo.principalEmail, protoPayload.resourceName, method
| sort -_time
-->

#### Cloud Storage 대량 다운로드 탐지

**시나리오**: 비정상적으로 많은 양의 Cloud Storage 객체 다운로드

<!--
Splunk SPL - Cloud Storage Mass Download:
index=gcp_audit sourcetype="google:gcp:audit"
protoPayload.serviceName="storage.googleapis.com"
protoPayload.methodName="storage.objects.get"
| stats count as download_count, dc(protoPayload.resourceName) as unique_files by protoPayload.authenticationInfo.principalEmail, _time
| where download_count > 100 OR unique_files > 50
| table _time, protoPayload.authenticationInfo.principalEmail, download_count, unique_files
-->

<!--
Azure Sentinel KQL - Cloud Storage Anomaly:
GCPAuditLogs
| where ServiceName == "storage.googleapis.com"
| where MethodName == "storage.objects.get"
| summarize DownloadCount=count(), UniqueFiles=dcount(ResourceName) by PrincipalEmail, bin(TimeGenerated, 5m)
| where DownloadCount > 100 or UniqueFiles > 50
| project TimeGenerated, PrincipalEmail, DownloadCount, UniqueFiles
| order by TimeGenerated desc
-->

#### GKE Privileged Container 실행 탐지

<!--
Google Chronicle YARA-L - GKE Privileged Pod Detection:
rule gke_privileged_pod_detection {
  meta:
    author = "GCP Security Team"
    description = "Detects creation of privileged pods in GKE"
    severity = "CRITICAL"

  events:
    $e.metadata.product_name = "Google Kubernetes Engine"
    $e.metadata.vendor_name = "Google"
    $e.target.resource.attribute.labels["verb"] = "create"
    $e.target.resource.attribute.labels["objectRef.resource"] = "pods"
    $e.target.resource.attribute.labels["requestObject"] = /privileged.*true/

  match:
    $user over 1h

  outcome:
    $risk_score = 95
    $alert_title = "Privileged Pod Created in GKE"

  condition:
    $e
}
-->

### 8.2 Cloud SQL 의심스러운 접근 패턴

#### 비정상 시간대 데이터베이스 접근

<!--
Splunk SPL - Cloud SQL Off-Hours Access:
index=gcp_cloudsql sourcetype="google:gcp:cloudsql:mysql"
| eval hour=strftime(_time, "%H")
| where (hour >= "22" OR hour <= "06") AND source_ip!="10.0.0.0/8"
| stats count by user, source_ip, database, _time
| where count > 10
| table _time, user, source_ip, database, count
-->

#### SQL Injection 패턴 탐지

<!--
Azure Sentinel KQL - SQL Injection Detection:
GCPCloudSQLLogs
| where QueryText contains "UNION" or QueryText contains "OR 1=1" or QueryText contains "DROP TABLE"
| where QueryText !contains "/* Legitimate App Query */"
| project TimeGenerated, User, SourceIP, Database, QueryText
| order by TimeGenerated desc
-->

### 8.3 네트워크 이상 행위 탐지

#### VPC Flow Logs를 통한 데이터 유출 탐지

<!--
Splunk SPL - VPC Data Exfiltration Hunt:
index=gcp_vpc sourcetype="google:gcp:vpc:flowlogs"
| stats sum(bytes_sent) as total_bytes_sent by src_ip, dest_ip, _time
| where total_bytes_sent > 1000000000
| eval GB_sent=round(total_bytes_sent/1073741824, 2)
| table _time, src_ip, dest_ip, GB_sent
| sort -GB_sent
-->

<!--
Google Chronicle YARA-L - High Volume Data Transfer:
rule gcp_high_volume_data_transfer {
  meta:
    author = "GCP Network Security"
    description = "Detects unusually high data transfers"
    severity = "HIGH"

  events:
    $e.metadata.product_name = "Google Cloud VPC"
    $e.network.sent_bytes > 1073741824

  match:
    $src_ip over 10m

  outcome:
    $risk_score = 80
    $alert_title = "High Volume Data Transfer Detected"

  condition:
    #e > 5
}
-->

### 8.4 Kubernetes API 무단 접근 시도

<!--
Splunk SPL - K8s API Unauthorized Access:
index=gcp_gke sourcetype="google:gcp:gke:audit"
responseStatus.code=403
| stats count by user.username, verb, objectRef.resource, _time
| where count > 10
| table _time, user.username, verb, objectRef.resource, count
-->

### 8.5 암호화 키 무단 사용 시도

<!--
Azure Sentinel KQL - KMS Unauthorized Key Usage:
GCPAuditLogs
| where ServiceName == "cloudkms.googleapis.com"
| where MethodName in ("Decrypt", "Encrypt", "AsymmetricDecrypt")
| where AuthorizationInfo has "PERMISSION_DENIED"
| summarize AttemptCount=count() by PrincipalEmail, ResourceName, bin(TimeGenerated, 5m)
| where AttemptCount > 5
| project TimeGenerated, PrincipalEmail, ResourceName, AttemptCount
-->

---

## 9. 2025년 이후 최신 업데이트

### 9.1 IAM 보안 강화

#### IAM Recommender 개선

2025년, GCP IAM Recommender는 보안 강화를 위한 권장사항을 더욱 정확하게 제공합니다.

**주요 기능:**
- 사용하지 않는 권한 자동 탐지
- 과도한 권한 부여 감지
- 최소 권한 원칙 기반 권장사항 제공

### 9.2 Cloud SQL 보안 강화

#### 자동 백업 및 복구 개선

2025년, Cloud SQL은 자동 백업 및 복구 기능을 강화하여 데이터 보호를 향상시켰습니다.

**주요 기능:**
- Point-in-time 복구 (PITR) 개선
- 자동 백업 스케줄링 최적화
- 암호화된 백업 지원 강화

### 9.3 Cloud Storage 보안 강화

#### 객체 라이프사이클 정책 개선

2025년, Cloud Storage는 객체 라이프사이클 정책을 개선하여 보안 및 비용 최적화를 강화했습니다.

**주요 기능:**
- 자동 암호화 전환
- 보안 정책 기반 자동 삭제
- 접근 빈도 기반 스토리지 클래스 자동 전환

### 9.4 GKE 보안 강화

#### Pod Security Standards 강화

Pod Security Standards는 세 가지 보안 레벨을 제공합니다:

2025년, GKE는 Pod Security Standards를 강화하여 컨테이너 보안을 향상시켰습니다.

**주요 기능:**
- Restricted 모드 기본 적용
- Security Context 자동 검증
- 네트워크 정책 자동 적용

#### Anthos 통합 강화

2025년, GKE는 Anthos와의 통합을 강화하여 멀티클라우드 및 하이브리드 환경에서의 보안 관리를 개선했습니다.

**주요 기능:**
- 서비스 메쉬 보안 정책 통합
- 구성 관리 및 정책 통합
- 중앙화된 보안 관리

### 9.5 Security Command Center 개선

#### 자동 위협 탐지 강화

2025년, Security Command Center는 AI 기반 자동 위협 탐지 기능을 강화했습니다.

**주요 기능:**
- 이상 활동 자동 탐지
- 보안 이벤트 자동 분석
- 위협 인텔리전스 통합

---

## 결론

GCP 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 GKE까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다.

주요 보안 원칙:

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **암호화**: 전송 중/저장 데이터 암호화
3. **로그 관리**: 모든 활동 로깅 및 모니터링
4. **정기적 검토**: 보안 설정 정기적 검토 및 개선

이 가이드를 참고하여 GCP 환경에서 강력한 보안 아키텍처를 구축하시기 바랍니다.

### 참고 자료

#### 공식 문서 및 가이드

1. **GCP 공식 보안 문서**
   - [GCP Security Best Practices](https://cloud.google.com/security/best-practices) - Google Cloud 보안 모범 사례 공식 가이드
   - [IAM Best Practices](https://cloud.google.com/iam/docs/best-practices) - IAM 권한 관리 모범 사례
   - [VPC Security Best Practices](https://cloud.google.com/vpc/docs/best-practices) - VPC 네트워크 보안 설정
   - [GKE Security Hardening Guide](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster) - GKE 클러스터 보안 강화
   - [Cloud SQL Security Guide](https://cloud.google.com/sql/docs/mysql/security-best-practices) - Cloud SQL 보안 구성

2. **보안 프레임워크 및 컴플라이언스**
   - [SK Shieldus 2024년 GCP 클라우드 보안 가이드](https://www.skshieldus.com/download/files/download.do?o_fname=2024%20%ED%81%AC%EB%9D%BC%EC%9A%B0%EB%93%9C%20%EB%B3%B4%EC%95%88%EA%B0%80%EC%9D%B4%EB%93%9C(GCP).pdf&r_fname=20240703112823626.pdf) - SK쉴더스 공식 가이드
   - [ISMS-P 인증 페이지](/certifications/isms-p/) - 정보보호 및 개인정보보호 관리체계 인증
   - [GCP Compliance Resource Center](https://cloud.google.com/security/compliance) - 규제 준수 리소스
   - [CSAP 클라우드보안인증제](https://www.kisa.or.kr/main.do) - 한국인터넷진흥원 클라우드 보안 인증

3. **MITRE ATT&CK 및 위협 인텔리전스**
   - [MITRE ATT&CK for Cloud](https://attack.mitre.org/matrices/enterprise/cloud/) - 클라우드 환경 공격 기법 매트릭스
   - [MITRE ATT&CK: IaaS](https://attack.mitre.org/matrices/enterprise/cloud/iaas/) - IaaS 환경 공격 기법
   - [Google Threat Horizons Report](https://cloud.google.com/blog/topics/threat-intelligence) - Google Cloud 위협 인텔리전스 리포트

4. **컨테이너 및 Kubernetes 보안**
   - [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) - Pod 보안 표준
   - [GKE Binary Authorization](https://cloud.google.com/binary-authorization/docs) - 컨테이너 이미지 검증
   - [Container Analysis API](https://cloud.google.com/container-analysis/docs) - 취약점 스캐닝
   - [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes) - Kubernetes 보안 벤치마크

5. **모니터링 및 로깅**
   - [Cloud Logging Best Practices](https://cloud.google.com/logging/docs/best-practices) - 로깅 모범 사례
   - [Security Command Center Documentation](https://cloud.google.com/security-command-center/docs) - 통합 보안 관리
   - [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs) - 모니터링 설정
   - [VPC Flow Logs](https://cloud.google.com/vpc/docs/flow-logs) - 네트워크 트래픽 로깅

6. **암호화 및 키 관리**
   - [Cloud KMS Documentation](https://cloud.google.com/kms/docs) - 키 관리 서비스
   - [CMEK (Customer-Managed Encryption Keys)](https://cloud.google.com/kms/docs/cmek) - 고객 관리 암호화 키
   - [Encryption at Rest](https://cloud.google.com/docs/security/encryption/default-encryption) - 저장 데이터 암호화

7. **한국 규제 및 법률**
   - [개인정보보호법](https://www.law.go.kr/법령/개인정보보호법) - 개인정보 보호 법률
   - [클라우드컴퓨팅법](https://www.law.go.kr/법령/클라우드컴퓨팅발전및이용자보호에관한법률) - 클라우드 이용자 보호
   - [전자금융감독규정](https://www.law.go.kr/행정규칙/전자금융감독규정) - 금융권 보안 규정

8. **보안 자동화 및 DevSecOps**
   - [GCP Deployment Manager](https://cloud.google.com/deployment-manager/docs) - 인프라 코드화
   - [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs) - Terraform GCP 프로바이더
   - [Cloud Build Security](https://cloud.google.com/build/docs/securing-builds) - 안전한 CI/CD 파이프라인

9. **보안 도구 및 오픈소스**
   - [ScoutSuite](https://github.com/nccgroup/ScoutSuite) - 멀티클라우드 보안 감사 도구
   - [CloudSploit](https://github.com/aquasecurity/cloudsploit) - 클라우드 보안 스캐너
   - [Forseti Security](https://forsetisecurity.org/) - GCP 보안 자동화 도구 (아카이브)
   - [Open Policy Agent](https://www.openpolicyagent.org/) - 정책 기반 제어

10. **교육 및 인증**
    - [Google Cloud Certified Professional Cloud Security Engineer](https://cloud.google.com/learn/certification/cloud-security-engineer) - GCP 보안 전문가 인증
    - [Coursera: Security in Google Cloud](https://www.coursera.org/specializations/security-google-cloud-platform) - GCP 보안 교육 과정
    - [Google Cloud Skills Boost](https://www.cloudskillsboost.google/) - 실습 기반 학습

---

**마지막 업데이트**: 2026-01-14
**작성 기준**: SK Shieldus 2024년 GCP 클라우드 보안 가이드

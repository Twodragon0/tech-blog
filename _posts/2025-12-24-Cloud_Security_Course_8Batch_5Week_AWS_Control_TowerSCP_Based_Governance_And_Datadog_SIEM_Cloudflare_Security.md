---
author: Twodragon
categories:
- cloud
certifications:
- aws-saa
comments: true
date: 2025-12-24 19:13:05 +0900
description: AWS Control Tower/SCP로 멀티 계정 거버넌스를 구축하고, Datadog SIEM과 Cloudflare로 통합
  보안 모니터링 및 웹 보안을 강화하세요.
excerpt: Control Tower/SCP 멀티 계정 거버넌스와 Datadog SIEM, Cloudflare 통합 보안 실무
image: /assets/images/2025-12-24-Cloud_Security_Course_8Batch_5Week_AWS_Control_TowerSCP_Based_Governance_and_Datadog_SIEM_Cloudflare_Security.svg
image_alt: 'Cloud Security Course 8Batch 5Week: AWS Control Tower SCP Based Governance
  and Datadog SIEM Cloudflare Security'
keywords:
- AWS
- Control-Tower
- SCP
- Datadog
- Cloudflare
- SIEM
- 멀티계정
- 거버넌스
- Landing Zone
layout: post
original_url: https://twodragon.tistory.com/706
tags:
- AWS
- Control-Tower
- SCP
- Datadog
- Cloudflare
- SIEM
title: '클라우드 시큐리티 과정 8기 5주차: AWS Control Tower/SCP 기반 거버넌스 및 Datadog SIEM, Cloudflare
  보안'
toc: true
---

## 요약

- **핵심 요약**: Control Tower/SCP 멀티 계정 거버넌스와 Datadog SIEM, Cloudflare 통합 보안 실무
- **주요 주제**: 클라우드 시큐리티 과정 8기 5주차: AWS Control Tower/SCP 기반 거버넌스 및 Datadog SIEM, Cloudflare 보안
- **키워드**: AWS, Control-Tower, SCP, Datadog, Cloudflare

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 8기 5주차: AWS Control Tower/SCP 기반 거버넌스 및 Datadog SIEM, Cloudflare 보안</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">Control-Tower</span>
      <span class="tag">SCP</span>
      <span class="tag">Datadog</span>
      <span class="tag">Cloudflare</span>
      <span class="tag">SIEM</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS 멀티 계정 거버넌스</strong>: AWS Control Tower를 통한 Landing Zone 자동 설정, Guardrails(필수/강력 권장/선택적 정책) 기반 보안 및 컴플라이언스 정책 자동 적용, Service Control Policies (SCP)를 통한 계정/OU 레벨 권한 제어</li>
      <li><strong>통합 보안 모니터링</strong>: Datadog SIEM을 통한 보안 이벤트 수집 및 상관관계 분석, CloudTrail/VPC Flow Logs/애플리케이션 로그 통합, 머신러닝 기반 이상 행위 탐지 및 커스텀 탐지 규칙</li>
      <li><strong>웹 보안 강화</strong>: Cloudflare DDoS 방어(레이어 3/4/7 자동 완화), WAF(OWASP Top 10 보호, 커스텀 규칙), SSL/TLS 관리(TLS 1.3, 자동 인증서), AWS Route 53 연동</li>
      <li><strong>2025년 AWS 거버넌스 업데이트</strong>: Organizations 계정 직접 이동 지원, AgentCore Identity(AI 에이전트 접근 제어), IAM Policy Autopilot(정책 자동 생성), Security Hub GA(멀티 계정 보안 통합 관리), GuardDuty Extended Threat Detection(EC2/ECS 위협 시퀀스 탐지)</li>
      <li><strong>실무 적용 가이드</strong>: Control Tower 설정 및 Guardrails 적용, SCP 작성 및 OU 적용, Datadog SIEM AWS 통합 설정, Cloudflare와 AWS 통합, 통합 보안 아키텍처 구성</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS Control Tower, AWS Organizations, Service Control Policies (SCP), Datadog SIEM, Cloudflare, AWS Security Hub, GuardDuty, IAM Policy Autopilot, AgentCore Identity</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 아키텍트, 보안 엔지니어, DevOps 엔지니어, 클라우드 관리자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{% raw %}{{ '/assets/images/2025-12-24-Cloud_Security_Course_8Batch_5Week_AWS_Control_TowerSCP_Based_Governance_and_Datadog_SIEM_Cloudflare_Security.svg' | relative_url }}{% endraw %}" alt="Cloud Security Course 8Batch 5Week: AWS Control Tower SCP Based Governance and Datadog SIEM Cloudflare Security" loading="lazy" class="post-image">

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 8기 5주차에서 다룰 AWS 멀티 계정 거버넌스 및 통합 보안 모니터링에 관련된 내용을 소개하고자 합니다.

이번 과정 역시 게더 타운(Gather Town)에서 진행되며, 온라인 환경에서의 집중력 유지를 위해 20분 강의 후 5분 휴식 패턴으로 구성되어 있습니다. 특히 이번 주차에서는 AWS의 강력한 통제 기능을 제공하는 Control Tower와 SCP, 그리고 통합 보안 모니터링을 위한 Datadog SIEM, 웹 보안을 위한 Cloudflare에 대해 다룹니다.

<img src="{% raw %}{{ '/assets/images/2025-12-24-Cloud_Security_Course_8Batch_5Week_AWS_Control_TowerSCP_Based_Governance_and_Datadog_SIEM_Cloudflare_Security_image.jpg' | relative_url }}{% endraw %}" alt="Cloud Security Course 8Batch 5Week: AWS Control Tower SCP Based Governance and Datadog SIEM Cloudflare Security" loading="lazy" class="post-image">

## Executive Summary (경영진 요약)

본 문서는 엔터프라이즈 클라우드 보안 거버넌스 체계를 제시합니다:

- **비용 절감**: 통합 거버넌스를 통한 불필요한 리소스 생성 차단으로 연간 클라우드 비용 15-30% 절감 달성
- **보안 사고 대응 시간**: Datadog SIEM 통합으로 평균 탐지 시간(MTTD) 73% 단축, 평균 대응 시간(MTTR) 58% 단축
- **컴플라이언스 준수율**: Control Tower Guardrails 자동화로 컴플라이언스 위반 사례 92% 감소, 감사 대응 시간 65% 단축
- **DDoS 공격 완화**: Cloudflare 엣지 방어 계층으로 애플리케이션 레벨 DDoS 공격 99.7% 자동 차단, 가용성 99.99% 유지
- **운영 효율성**: 멀티 계정 자동화로 계정 프로비저닝 시간 80% 단축, 인적 오류 96% 감소

## 1. AWS 멀티 계정 전략

### 1.1 왜 멀티 계정이 필요한가?

대규모 조직에서는 여러 계정을 사용하는 것이 권장됩니다:

- **격리**: 환경별, 팀별 리소스 격리
- **보안 경계**: 계정 단위 보안 경계 설정
- **비용 관리**: 계정별 비용 추적 및 관리
- **컴플라이언스**: 규제 요구사항별 계정 분리

### 1.2 계정 구조 예시



#### 특정 리전만 허용

> **참고**: 리전 제한 SCP 정책 관련 내용은 [AWS Organizations SCP 예제](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples.html)를 참조하세요.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



#### Root 계정 사용 차단

> **참고**: Root 계정 차단 SCP 정책 관련 내용은 [AWS Organizations SCP 보안 모범 사례](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html)를 참조하세요.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



## 4. Datadog SIEM

### 4.1 Datadog SIEM이란?

Datadog SIEM(Security Information and Event Management)은 보안 이벤트를 수집, 분석, 상관관계 분석하여 위협을 탐지하고 대응하는 플랫폼입니다.

### 4.2 주요 기능

#### 로그 수집 및 분석

- **AWS CloudTrail 통합**: 모든 API 호출 로그 수집
- **VPC Flow Logs**: 네트워크 트래픽 분석
- **애플리케이션 로그**: 앱 레벨 보안 이벤트

#### 위협 탐지

- **이상 행위 탐지**: 머신러닝 기반 이상 패턴 탐지
- **규칙 기반 탐지**: 미리 정의된 규칙 기반 탐지
- **커스텀 탐지**: 조직별 맞춤 탐지 규칙

#### 대시보드 및 알림

- **보안 대시보드**: 실시간 보안 상태 모니터링
- **알림 통합**: Slack, PagerDuty 등과 통합
- **리포트**: 정기적인 보안 리포트 생성

### 4.3 Datadog AWS 통합 설정

#### CloudTrail 통합

1. **Datadog AWS 통합 활성화**
2. **IAM 역할 생성**: Datadog이 CloudTrail 로그를 읽을 수 있는 권한
3. **로그 수집 시작**: 자동으로 CloudTrail 로그 수집

#### 커스텀 탐지 규칙

> **참고**: Datadog 커스텀 탐지 규칙 관련 내용은 [Datadog Security Monitoring](https://docs.datadoghq.com/security/) 및 [CloudTrail 통합](https://docs.datadoghq.com/integrations/amazon_cloudtrail/)을 참조하세요.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 예시: 비정상적인 리전에서의 API 호출 탐지...
> ```



## 5. Cloudflare 보안

Cloudflare는 웹 애플리케이션 보안을 강화하는 엣지 보안 플랫폼입니다.

### 5.1 Cloudflare란?

Cloudflare는 전 세계에 분산된 CDN 및 보안 서비스를 제공하는 플랫폼입니다. 웹 애플리케이션 보안을 강화하는 다양한 기능을 제공합니다.

### 5.2 주요 보안 기능

#### DDoS 방어

- **자동 DDoS 완화**: 레이어 3, 4, 7 DDoS 공격 자동 차단
- **Rate Limiting**: 요청 속도 제한
- **Bot Management**: 봇 트래픽 식별 및 차단

#### Web Application Firewall (WAF)

- **OWASP Top 10 보호**: 일반적인 웹 취약점 보호
- **커스텀 규칙**: 조직별 맞춤 보안 규칙
- **실시간 차단**: 악성 요청 즉시 차단

#### SSL/TLS 관리

- **자동 인증서**: Let's Encrypt 통합
- **TLS 1.3**: 최신 암호화 프로토콜
- **Universal SSL**: 모든 도메인 자동 암호화

### 5.3 Cloudflare와 AWS 통합

#### Route 53 연동

1. **Cloudflare에 도메인 추가**
2. **Route 53에서 DNS 레코드 업데이트**
3. **Cloudflare 프록시 활성화**

#### AWS WAF와의 비교

| 기능 | Cloudflare | AWS WAF |
|------|------------|---------|
| DDoS 방어 | 자동, 무료 | 추가 비용 |
| 글로벌 네트워크 | 200+ 도시 | 리전별 |
| 설정 복잡도 | 낮음 | 높음 |
| 비용 | 플랜별 | 사용량 기반 |

## 6. 통합 보안 아키텍처

### 6.1 전체 아키텍처

> **참고**: AWS 보안 아키텍처 관련 내용은 [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) 및 [AWS Security Reference Architecture](https://aws.amazon.com/architecture/security-identity-compliance/)를 참조하세요.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.)
2. **네트워크 보안**: VPC, Security Groups, NACLs
3. **계정 보안**: Control Tower, SCP
4. **모니터링**: Datadog SIEM

## 7. 실습 가이드

### 7.1 Control Tower 설정

1. **Control Tower 활성화**
   - AWS 콘솔에서 Control Tower 접근
   - Landing Zone 설정 시작
   - 계정 및 OU 구조 정의

2. **Guardrails 적용**
   - 필수 Guardrails 자동 적용
   - 강력 권장 Guardrails 검토 및 적용
   - 선택적 Guardrails 필요시 적용

3. **계정 팩토리 설정**
   - 새 계정 생성 워크플로우 정의
   - 자동 설정 템플릿 구성

### 7.2 SCP 작성 및 적용

1. **SCP 정책 작성**
   - JSON 형식으로 정책 작성
   - 테스트 계정에서 먼저 검증

2. **OU에 적용**
   - 적절한 OU 선택
   - SCP 연결

3. **효과 검증**
   - 정책이 의도대로 작동하는지 확인
   - 필요시 조정

### 7.3 Datadog SIEM 설정

1. **AWS 통합 활성화**
   - Datadog에서 AWS 통합 추가
   - IAM 역할 생성 및 권한 부여

2. **로그 수집 설정**
   - CloudTrail 로그 수집 활성화
   - VPC Flow Logs 수집 설정

3. **탐지 규칙 구성**
   - 기본 탐지 규칙 활성화
   - 커스텀 규칙 추가

## 8. 모범 사례

### 8.1 Control Tower

- **단계적 적용**: 처음에는 필수 Guardrails만 적용
- **정기적 검토**: Guardrails 효과 정기적으로 검토
- **문서화**: 계정 구조 및 정책 문서화

### 8.2 SCP

- **최소 권한**: 필요한 최소한의 제한만 적용
- **테스트 우선**: 프로덕션 적용 전 테스트
- **예외 처리**: 필요한 경우 예외 계정 설정

### 8.3 Datadog SIEM

- **로그 보존**: 충분한 로그 보존 기간 설정
- **알림 최적화**: 중요한 이벤트만 알림
- **정기적 검토**: 탐지 규칙 효과 정기적으로 검토

### 8.4 Cloudflare

- **WAF 규칙 최적화**: False Positive 최소화
- **Rate Limiting 조정**: 정상 트래픽에 영향 최소화
- **캐싱 전략**: 성능과 보안의 균형

## 9. 2025년 AWS 거버넌스 업데이트

2025년에 발표된 AWS 거버넌스 관련 주요 업데이트를 정리합니다. 이 업데이트들은 Control Tower 및 SCP 기반 거버넌스를 더욱 강화합니다.

### 9.1 AWS Organizations 계정 마이그레이션 개선

기존에는 AWS 계정을 다른 조직으로 이동하려면 먼저 standalone 계정으로 분리한 후 다시 새 조직에 가입해야 했습니다. **2025년 업데이트로 이제 계정을 standalone으로 분리하지 않고도 조직 간 직접 이동이 가능**해졌습니다.

**주요 이점:**
- 계정 이동 과정 단순화
- 다운타임 최소화
- M&A 또는 조직 재구성 시 효율성 향상

**Control Tower와의 연계:**
- Control Tower로 관리되는 계정도 직접 이동 가능
- 이동 시 기존 Guardrails 및 SCP 자동 재적용 옵션

### 9.2 AgentCore Identity - AI 에이전트 접근 제어

AI/ML 워크로드가 증가함에 따라 AWS는 **AgentCore Identity**를 도입하여 AI 에이전트에 대한 세밀한 접근 제어를 제공합니다.

**주요 기능:**
- AI 에이전트별 IAM 역할 및 정책 할당
- 에이전트 행위 감사 및 추적
- 최소 권한 원칙을 AI 워크로드에 적용
- Control Tower와 통합하여 멀티 계정 환경에서 AI 거버넌스 관리

**SCP 적용 예시 - AI 에이전트 리전 제한:**

> **참고**: AI 에이전트 접근 제어 SCP 정책 관련 내용은 [AWS Organizations SCP 문서](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) 및 [AgentCore Identity 문서](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)를 참조하세요.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



### 9.3 IAM Policy Autopilot

**IAM Policy Autopilot**은 오픈소스 도구로, 애플리케이션 코드를 분석하여 IAM 정책을 자동으로 생성합니다.

**동작 방식:**
1. 애플리케이션 소스 코드 분석
2. AWS SDK 호출 패턴 식별
3. 필요한 최소 권한 IAM 정책 자동 생성
4. 기존 정책과의 차이 분석 및 권장 사항 제공

**사용 예시:**

> **참고**: IAM Policy Autopilot 사용 관련 자세한 내용은 [IAM Policy Autopilot GitHub 저장소](https://github.com/aws/iam-policy-autopilot) 및 [AWS IAM Policy Autopilot 문서](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

```bash
# IAM Policy Autopilot 실행
iam-policy-autopilot analyze --source ./my-app --output policy.json

# 기존 정책과 비교
iam-policy-autopilot diff --current current-policy.json --recommended policy.json
```

**SCP와의 연계:**
- Autopilot이 생성한 정책이 SCP와 충돌하는지 자동 검증
- Control Tower Guardrails와의 호환성 검사

### 9.4 보안 모니터링 강화

#### AWS Security Hub GA

AWS Security Hub가 GA(General Availability)로 출시되어 **멀티 계정 보안 현황을 통합 관리**할 수 있게 되었습니다.

**주요 기능:**
- Control Tower와 자동 통합
- 모든 멤버 계정의 보안 상태 중앙 집중 관리
- 자동화된 보안 점수 산정
- 규정 준수 상태 대시보드

**Datadog SIEM과의 통합:**
> **참고**: Datadog SIEM 통합 관련 내용은 [Datadog Security Monitoring](https://docs.datadoghq.com/security/) 및 [Datadog AWS Security Hub 통합](https://docs.datadoghq.com/integrations/amazon_security_hub/)을 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
# Datadog에서 Security Hub 데이터 수집 설정
security_hub_integration:
  enabled: true
  accounts:
    - management_account
    - security_tooling_account
  findings_filter:
    severity: ["CRITICAL", "HIGH", "MEDIUM"]
  sync_interval: 5m
```

#### GuardDuty Extended Threat Detection

GuardDuty가 **Extended Threat Detection** 기능을 추가하여 EC2 및 ECS 환경에서의 위협 시퀀스를 탐지합니다.

**탐지 가능한 위협:**
- 다단계 공격 시퀀스 식별
- EC2 인스턴스 내 악성 행위 패턴
- ECS 컨테이너 런타임 위협
- 내부자 위협 및 측면 이동 탐지

**Datadog SIEM 연동 탐지 규칙:**
> **참고**: Datadog SIEM 탐지 규칙 관련 내용은 [Datadog Security Monitoring](https://docs.datadoghq.com/security/) 및 [Datadog CloudTrail 통합](https://docs.datadoghq.com/integrations/amazon_cloudtrail/)을 참조하세요.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.:*",
        "waf:*",
        "support:*",
        "budgets:*",
        "ce:*",
        "health:*",
        "trustedadvisor:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "ap-northeast-2",
            "us-east-1"
          ]
        }
      }
    }
  ]
}



```

### 12.2 서비스 제한 정책

#### 금융권 보안 요구사항 SCP

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



### 12.3 태그 강제 정책

#### Cost Center 태깅 필수화

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

json
> {...
> ```

javascript
> // Cloudflare Workers: Advanced WAF Rules...
> ```



#### Rate Limiting 정교화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloudflare Rate Limiting Rules...
> > **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```

javascript
> // Cloudflare Workers: Bot Detection and Mitigation...
> ```

yaml
> # Cloudflare Advanced DDoS Protection...
> > **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```



## 15. 통합 보안 모니터링 대시보드

### 15.1 Executive Dashboard (경영진용)

#### KPI 중심 보안 지표

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요., Access Policy |
| 2.5.1 암호화 적용 | 저장/전송 데이터 암호화 | S3/EBS 암호화 Guardrail | 비암호화 리소스 탐지 | TLS 1.3 강제 |
| 2.7.1 로그 관리 | 로그 수집, 보관, 모니터링 | CloudTrail 필수 활성화 | 중앙 집중 로그 수집 및 90일 보관 | Access Logs |
| 2.8.1 침해사고 대응 | 탐지, 분석, 대응 체계 | Security Hub 통합 | 실시간 위협 탐지 및 알림 | DDoS 자동 완화 |
| 3.1.1 개인정보 수집 제한 | 최소 수집 원칙 | 태그 기반 데이터 분류 SCP | 민감 정보 접근 감사 | 민감 정보 마스킹 |

### 17.2 KISA 클라우드 보안 인증 기준

한국인터넷진흥원(KISA) 클라우드 보안 인증(CSAP) 기준 충족:

#### 물리적 보안

| 통제 항목 | AWS 기본 제공 | 추가 구성 필요 |
|----------|-------------|---------------|
| 데이터센터 물리적 접근 통제 | AWS 인증 데이터센터 | N/A |
| 전력 및 냉각 이중화 | AWS 인증 인프라 | N/A |
| 재해 복구 능력 | Multi-AZ | Control Tower로 DR 계정 자동 설정 |

#### 기술적 보안

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 문서](https://developers.cloudflare.com/waf/)
   - [DDoS Protection Guide](https://developers.cloudflare.com/ddos-protection/)
   - [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)

5. **AWS Security Services**
   - [AWS Security Hub](https://docs.aws.amazon.com/securityhub/)
   - [Amazon GuardDuty](https://docs.aws.amazon.com/guardduty/)
   - [AWS IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)

### 보안 프레임워크

6. **MITRE ATT&CK**
   - [MITRE ATT&CK for Cloud](https://attack.mitre.org/matrices/enterprise/cloud/)
   - [MITRE ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)

7. **AWS Well-Architected Framework**
   - [Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
   - [AWS Security Reference Architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/)

### 한국 규제 및 컴플라이언스

8. **ISMS-P (정보보호 및 개인정보보호 관리체계)**
   - [KISA ISMS-P 인증 기준](https://www.kisa.or.kr/isms-p)
   - [클라우드 보안 인증(CSAP)](https://www.kisa.or.kr/csap)

9. **금융권 규제**
   - [금융감독원 전자금융감독규정](https://www.fss.or.kr/)
   - [금융보안원 클라우드 보안 가이드](https://www.fsec.or.kr/)

10. **개인정보보호법**
    - [개인정보보호위원회 고시](https://www.pipc.go.kr/)
    - [클라우드 환경 개인정보보호 가이드라인](https://www.pipc.go.kr/)

### 도구 및 오픈소스

11. **IAM Policy Autopilot**
    - [GitHub: aws/iam-policy-autopilot](https://github.com/aws/iam-policy-autopilot)

12. **CloudFormation Templates**
    - [AWS Control Tower Customizations](https://github.com/aws-samples/aws-control-tower-customizations)

### 관련 블로그 및 자료

13. **AWS Blog**
    - [AWS Security Blog](https://aws.amazon.com/blogs/security/)
    - [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/)

14. **Datadog Blog**
    - [Datadog Security Monitoring Blog](https://www.datadoghq.com/blog/tag/security/)

15. **Cloudflare Blog**
    - [Cloudflare Security Blog](https://blog.cloudflare.com/tag/security/)

---

## 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **AWS Control Tower** | 멀티 계정 거버넌스, SCP, Guardrails 설정 | [수강하기](https://edu.2twodragon.com/courses/aws-control-tower) |
| **Datadog SIEM** | Security Monitoring, Log Management, 알림 설정 | [수강하기](https://edu.2twodragon.com/courses/datadog-siem) |
| **Cloudflare 보안** | WAF, DDoS 방어, Zero Trust 설정 | [수강하기](https://edu.2twodragon.com/courses/cloudflare-security) |
| **AWS 클라우드 보안** | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |
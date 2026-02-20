---
layout: post
title: "클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안"
date: 2025-05-23 01:07:48 +0900
category: security
categories: [security, devsecops]
tags: [AWS, CDN, Cloudflare, GitHub, SAST, WAF, 보안, 보안-아키텍처, 애플리케이션-보안, 코드-보안]
excerpt: "AWS WAF, Cloudflare, GitHub 보안 완벽 가이드. DDoS 방어, 코드 스캔, 취약점 자동화 실무 정리."
comments: true
original_url: https://twodragon.tistory.com/684
image: /assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security.svg
image_alt: "Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security"
toc: true
description: 클라우드 시큐리티 7기 6주차. AWS WAF 보안 강화(웹 ACL, Rate Limiting), Cloudflare 종합 보안(DDoS, WAF, SSL/TLS), GitHub 보안 자동화(Dependabot, CodeQL, Secret Scanning) 실무 정리.
keywords: [AWS, WAF, Cloudflare, DDoS, CDN, GitHub, CodeQL, Dependabot, SAST, Secret-Scanning, 웹보안, 코드보안]
author: "Yongho Ha"
schema_type: Article
---

## 📋 포스팅 요약

> **제목**: 클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안

> **카테고리**: security, devsecops

> **태그**: AWS, CDN, Cloudflare, GitHub, SAST, WAF, 보안, 보안-아키텍처, 애플리케이션-보안, 코드-보안

> **핵심 내용**: 
> - AWS WAF, Cloudflare, GitHub 보안 완벽 가이드. DDoS 방어, 코드 스캔, 취약점 자동화 실무 정리.

> **주요 기술/도구**: AWS, Cloudflare, GitHub, WAF, security, devsecops

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
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">CDN</span>
      <span class="tag">Cloudflare</span>
      <span class="tag">GitHub</span>
      <span class="tag">SAST</span>
      <span class="tag">WAF</span>
      <span class="tag">보안</span>
      <span class="tag">보안-아키텍처</span>
      <span class="tag">애플리케이션-보안</span>
      <span class="tag">코드-보안</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS WAF 보안 강화</strong>: 웹 ACL 규칙 설정(SQL Injection, XSS, Rate Limiting), IP 기반 접근 제어, Geo-blocking, 커스텀 규칙 로직, CloudWatch 연동 모니터링</li>
      <li><strong>Cloudflare 종합 보안</strong>: DDoS 보호(자동 완화, Rate Limiting), WAF 규칙 관리(OWASP Core Rule Set), SSL/TLS 설정(TLS 1.3, HSTS), CDN 최적화, Bot Management, Page Rules</li>
      <li><strong>GitHub 보안 자동화</strong>: Dependabot 의존성 취약점 스캔 및 자동 PR 생성, Code Scanning(CodeQL) 정적 분석, Secret Scanning 민감 정보 탐지, Security Advisories 관리</li>
      <li><strong>실무 보안 실습</strong>: DVWA(Damn Vulnerable Web Application)를 활용한 취약점 실습, AWS WAF 규칙 테스트, Cloudflare 보안 설정 실습, GitHub 보안 기능 통합</li>
      <li><strong>보안 모범 사례</strong>: Defense in Depth 전략, 다층 보안 방어, 자동화된 보안 검사, 실시간 모니터링 및 알림</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS WAF, CloudFront, Cloudflare, DDoS Protection, WAF, SSL/TLS, CDN, Bot Management, GitHub Advanced Security, Dependabot, CodeQL, Code Scanning, Secret Scanning, DVWA, CloudWatch, OWASP Core Rule Set</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 엔지니어, DevSecOps 엔지니어, 클라우드 보안 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{% raw %}{{ '/assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security_image.png' | relative_url }}{% endraw %}" alt="Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security" loading="lazy" class="post-image">

## 경영진 요약 (Executive Summary)

이 문서는 웹 애플리케이션 보안을 위한 3단계 방어 전략을 제시합니다: AWS WAF를 통한 기본 웹 보안, Cloudflare를 통한 DDoS 및 글로벌 보안 강화, GitHub 보안 자동화를 통한 소스 코드 보안입니다.

### 보안 위험 스코어카드

| 보안 영역 | 구현 전 위험도 | 구현 후 위험도 | 비즈니스 영향 |
|---------|-------------|-------------|------------|
| **웹 애플리케이션 공격** | CRITICAL (9.5) | LOW (2.0) | 데이터 유출 방지, 서비스 연속성 확보 |
| **DDoS 공격** | CRITICAL (9.0) | LOW (1.5) | 가용성 99.99% 달성, 매출 손실 방지 |
| **의존성 취약점** | HIGH (7.5) | LOW (2.5) | 공급망 공격 방지, 규제 준수 |
| **코드 보안 취약점** | HIGH (8.0) | MEDIUM (3.0) | 제로데이 공격 사전 차단 |
| **시크릿 노출** | CRITICAL (9.8) | LOW (1.0) | 계정 탈취 방지, 규정 위반 예방 |

### 주요 달성 지표 (KPI)

| 지표 | 목표 | 측정 방법 |
|-----|-----|---------|
| **공격 차단율** | 99.5% 이상 | AWS WAF + Cloudflare 메트릭 |
| **취약점 수정 시간** | 24시간 이내 | GitHub Security Advisory MTTR |
| **의존성 업데이트** | 주 1회 자동 | Dependabot PR 통계 |
| **거짓 양성율** | 5% 미만 | 보안 알림 분석 |
| **서비스 가용성** | 99.99% | Cloudflare Uptime 모니터링 |

### 투자 대비 효과 (ROI)

| 항목 | 비용 | 효과 | ROI |
|-----|-----|-----|-----|
| **AWS WAF** | $월 100-500 | 데이터 유출 방지 ($수백만) | 1,000% 이상 |
| **Cloudflare Pro** | $월 20-200 | DDoS 방어, CDN 최적화 | 500% 이상 |
| **GitHub Advanced Security** | $월 49/사용자 | 공급망 공격 방지 | 800% 이상 |

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 Application 보안 및 Cloudflare 및 GitHub 활용을 다루고자 합니다. 이 과정은 게더 타운에서 진행되며, 각 세션은 20분 강의 후 5분 휴식으로 구성되어 있습니다. 이러한 구성은 온라인 강의의 특성 상 눈의 피로를 줄이고, 멘티 분들의 집중력을 최대화하기 위함입니다. 여러분들과 함께 다양한 AWS 보안 모니터링 및 대응 관련 주제를 깊이 있게 다루어 보고자 합니다.

이 글에서는 클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안에 대해 실무 중심으로 상세히 다룹니다.

## 1. 강의 일정 및 구성

### 1.1 세션 구성

이번 6주차 강의는 다음과 같은 일정으로 진행됩니다:

**10:00 - 10:20**: 근황 토크 & 과제 피드백
- 한 주간의 근황 공유 및 토론
- 영상 & 과제 피드백: 어려웠던 점, 개선점 공유
- 보안 이슈 논의

**10:25 - 10:50**: AWS WAF & Cloudflare
- AWS WAF 기본 개념 및 실습
- Cloudflare 보안 기능 소개

**11:00 - 11:30**: Cloudflare 및 GitHub 보안
- Cloudflare 고급 보안 설정
- GitHub 보안 기능 활용

**11:40 - 12:00**: 필수적인 실습을 통한 이론 정리
- 실습 환경 구축 및 테스트
- 보안 모범 사례 적용

### 1.2 최신 보안 업데이트 권고사항

> **⚠️ 보안 주의사항**
>
> 최신 보안 업데이트를 지속적으로 확인하고 적용해야 합니다. 특히 BPF(Berkeley Packet Filter) 관련 취약점 점검 가이드를 참고하시기 바랍니다.
>
> - **BPF 점검 가이드**: [KISA 보호나라&KrCERT/CC](https://www.krcert.or.kr/kr/bbs/view.do?searchCnd=&bbsId=B0000133&searchWrd=&menuNo=205020&pageIndex=1&categoryCode=&nttId=71754)

## 2. AWS WAF (Web Application Firewall)

### 2.1 AWS WAF 개요

AWS WAF는 웹 애플리케이션을 보호하는 데 중요한 도구입니다. 이 서비스는 SQL 인젝션, 크로스 사이트 스크립팅(XSS) 등 다양한 웹 기반 공격으로부터 보호하며, 사용자 정의 규칙을 설정하여 트래픽을 제어할 수 있습니다.

#### 주요 기능

| 기능 | 설명 | 사용 사례 |
|------|------|----------|
| **SQL Injection 방어** | SQL 인젝션 공격 자동 탐지 및 차단 | 데이터베이스 보호, 데이터 유출 방지 |
| **XSS 방어** | 크로스 사이트 스크립팅 공격 차단 | 사용자 세션 탈취 방지 |
| **Rate Limiting** | 트래픽 제한을 통한 DDoS 공격 완화 | API 남용 방지, 서비스 안정성 확보 |
| **Geo-blocking** | 특정 지역의 트래픽 차단 | 규정 준수, 리스크 감소 |
| **Custom Rules** | 사용자 정의 규칙을 통한 세밀한 제어 | 비즈니스 로직 보호 |

### 2.2 AWS WAF 실습

AWS WAF는 [AWS WAF Workshop](https://sessin.github.io/awswafhol/)을 통해 실습할 수 있으며, DVWA(Damn Vulnerable Web Application)를 활용한 공격 및 방어 실습이 가능합니다.

#### 실습 환경 구성

> **참고**: DVWA 실습 환경 관련 내용은 [DVWA GitHub 저장소](https://github.com/digininja/DVWA) 및 [OWASP WebGoat](https://github.com/WebGoat/WebGoat)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```bash
# DVWA 컨테이너 실행 예시
docker run --rm -it -p 80:80 vulnerables/web-dvwa

# AWS WAF 설정 테스트
# AWS Console에서 WAF 규칙 생성 및 테스트
```

#### 실습 시나리오

1. **SQL Injection 공격 시뮬레이션**
   - DVWA를 통한 SQL Injection 공격 테스트
   - AWS WAF 규칙 생성 및 적용
   - 공격 차단 확인

2. **XSS 공격 방어**
   - 크로스 사이트 스크립팅 공격 테스트
   - WAF 규칙을 통한 자동 차단

3. **Rate Limiting 설정**
   - 트래픽 제한 규칙 설정
   - DDoS 공격 시뮬레이션 및 방어

> **💡 실무 팁**
>
> AWS WAF와 전체적인 네트워크 시나리오에 대한 상세한 설명은 [YouTube 영상](https://youtu.be/r84IuPv_4TI?si=lUbhpD3TqEbbk2ud)을 참고하시기 바랍니다.

### 2.3 AWS WAF 고급 규칙 설계

#### 2.3.1 커스텀 규칙 예제

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Name": "BlockSuspiciousUserAgents",
  "Priority": 10,
  "Statement": {
    "ByteMatchStatement": {
      "SearchString": "sqlmap",
      "FieldToMatch": {
        "SingleHeader": {
          "Name": "user-agent"
        }
      },
      "TextTransformations": [
        {
          "Priority": 0,
          "Type": "LOWERCASE"
        }
      ],
      "PositionalConstraint": "CONTAINS"
    }
  },
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "BlockSuspiciousUserAgents"
  }
}


```
-->
-->

#### 2.3.2 Rate Limiting 전략

| 시나리오 | Rate Limit | 측정 기간 | 차단 시간 |
|---------|-----------|---------|---------|
| **API 엔드포인트** | 100 requests | 5분 | 30분 |
| **로그인 페이지** | 5 requests | 1분 | 60분 |
| **검색 기능** | 50 requests | 5분 | 10분 |
| **파일 업로드** | 10 requests | 5분 | 30분 |

#### 2.3.3 Geo-blocking 전략

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # AWS WAF Geo-blocking 설정 예제 (Terraform)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # AWS WAF Geo-blocking 설정 예제 (Terraform)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# AWS WAF Geo-blocking 설정 예제 (Terraform)
resource "aws_wafv2_web_acl" "main" {
  name  = "geo-blocking-acl"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "BlockHighRiskCountries"
    priority = 1

    action {
      block {}
    }

    statement {
      geo_match_statement {
        country_codes = ["KP", "IR", "SY"]  # 북한, 이란, 시리아
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockHighRiskCountries"
      sampled_requests_enabled   = true
    }
  }
}


```
-->
-->

### 2.4 AWS WAF 모니터링 및 대응

#### 2.4.1 CloudWatch 메트릭

주요 모니터링 지표:

| 메트릭 | 임계값 | 알림 조건 |
|-------|-------|---------|
| **BlockedRequests** | >100/분 | 5분 연속 |
| **AllowedRequests** | <50/분 | 정상 트래픽 급감 |
| **CountedRequests** | >1000/분 | 공격 가능성 |
| **SampledRequests** | 비정상 패턴 | 수동 분석 필요 |

#### 2.4.2 자동화된 대응 워크플로우

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # EventBridge Rule for WAF automation...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # EventBridge Rule for WAF automation...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# EventBridge Rule for WAF automation
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  WAFSecurityAutomation:
    Type: AWS::Events::Rule
    Properties:
      Name: WAF-Security-Automation
      Description: Automatically respond to WAF threats
      EventPattern:
        source:
          - aws.wafv2
        detail-type:
          - AWS API Call via CloudTrail
        detail:
          eventName:
            - CreateWebACL
            - UpdateWebACL
      State: ENABLED
      Targets:
        - Arn: !GetAtt SecurityLambda.Arn
          Id: SecurityAutomation


```
-->
-->

## 3. Cloudflare

### 3.1 Cloudflare 개요

Cloudflare는 웹사이트의 성능과 보안을 강화하기 위한 다양한 기능을 제공합니다. 전 세계에 분산된 네트워크를 통해 DDoS 공격 방어, WAF, CDN 등 종합적인 보안 및 성능 최적화 서비스를 제공합니다.

### 3.2 주요 보안 기능

| 보안 기능 | 설명 | 핵심 특징 |
|----------|------|----------|
| **DDoS 보호** | 대규모 트래픽 공격 자동 차단 | Layer 3/4/7 공격 방어, 실시간 위협 탐지 |
| **WAF** | 웹 애플리케이션 방화벽 | SQL Injection/XSS 차단, OWASP Top 10 대응 |
| **SSL/TLS** | 데이터 암호화 통신 | 자동 인증서 관리, TLS 1.3 지원 |
| **DNS 보안** | 안전한 DNS 서비스 | DNSSEC 지원, Anycast 고가용성 |
| **봇 관리** | 악성 봇 탐지 및 차단 | AI 기반 봇 탐지, 정상 크롤러 허용 |
| **CDN** | 콘텐츠 전송 네트워크 | 전 세계 에지 서버, 캐싱 최적화 |

#### CDN (콘텐츠 전송 네트워크)
- 전 세계에 분산된 서버를 통해 콘텐츠를 빠르게 전달
- 캐싱을 통한 성능 최적화
- 대역폭 비용 절감

#### 페이지 규칙 및 리디렉션
- 특정 페이지에 대한 규칙 설정과 URL 리디렉션을 관리
- 캐싱 정책 세밀한 제어
- 보안 헤더 자동 추가

### 3.3 Cloudflare 보안 아키텍처

Cloudflare의 보안 아키텍처에 대한 상세한 정보는 [Cloudflare Security Architecture](https://developers.cloudflare.com/reference-architecture/architectures/security/) 문서를 참고하시기 바랍니다.

이 문서는 다음 내용을 다룹니다:
- 네트워크 및 플랫폼의 보안 아키텍처
- 운영 보안 모범 사례
- 기업의 보안 요구사항 대응 방법

### 3.4 Cloudflare, CDN 구성

Cloudflare와 AWS CloudFront, S3의 통합 CORS 구성 및 보안 최적화에 대한 상세한 가이드는 [이전 포스팅](https://twodragon.tistory.com/664)을 참고하시기 바랍니다.

> **💡 실무 팁**
>
> 이러한 기능을 적절히 조합하여 웹사이트의 보안을 강화하고 성능을 최적화할 수 있습니다. 사용자의 특정 요구사항과 인프라에 맞게 Cloudflare 설정을 조정하는 것이 중요합니다.

### 3.5 Cloudflare DDoS 방어 전략

#### 3.5.1 DDoS 공격 유형 및 방어

| 공격 유형 | OSI Layer | Cloudflare 방어 방법 | 차단 시간 |
|---------|----------|-------------------|---------|
| **Volumetric Attack** | Layer 3/4 | Anycast 네트워크 분산 | <3초 |
| **Protocol Attack** | Layer 4 | SYN Flood 필터링 | <3초 |
| **Application Attack** | Layer 7 | Rate Limiting, WAF | <10초 |
| **DNS Amplification** | Layer 3/4 | DNS 요청 필터링 | <3초 |
| **HTTP Flood** | Layer 7 | Challenge Page, JS Verification | <10초 |

#### 3.5.2 DDoS 공격 흐름도

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> 인터넷...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> 인터넷...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
                                    인터넷
                                      |
                                      v
                        +----------------------------+
                        |  Cloudflare Edge Network   |
                        |  (전 세계 300+ 데이터센터)   |
                        +----------------------------+
                                      |
                    +-----------------+-----------------+
                    |                                   |
                    v                                   v
          +------------------+              +------------------+
          | DDoS Mitigation  |              |   정상 트래픽    |
          | - Volumetric     |              | - 사용자 검증     |
          | - Protocol       |              | - Rate Limit 통과|
          | - Application    |              +------------------+
          +------------------+                        |
                    |                                 |
                    v                                 v
          [차단 및 로깅]                    +------------------+
                                           |  오리진 서버      |
                                           | (AWS/GCP/Azure)  |
                                           +------------------+


```
-->
-->

### 3.6 Cloudflare WAF 규칙 최적화

#### 3.6.1 OWASP Core Rule Set

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/nodejs/node/tree/main/doc)를 참조하세요.
> 
> ```javascript
> // Cloudflare WAF 규칙 예제 (Workers 스크립트)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/nodejs/node/tree/main/doc)를 참조하세요.
> 
> ```javascript
> // Cloudflare WAF 규칙 예제 (Workers 스크립트)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```javascript
// Cloudflare WAF 규칙 예제 (Workers 스크립트)
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // SQL Injection 탐지
  const sqlPattern = /(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDROP\b)/gi
  if (sqlPattern.test(url.search)) {
    return new Response('Blocked: SQL Injection detected', {
      status: 403,
      headers: { 'X-Block-Reason': 'SQL-Injection' }
    })
  }

  // XSS 탐지
  const xssPattern = /<script|javascript:|onerror=|onload=/gi
  if (xssPattern.test(url.search)) {
    return new Response('Blocked: XSS detected', {
      status: 403,
      headers: { 'X-Block-Reason': 'XSS' }
    })
  }

  return fetch(request)
}


```
-->
-->

#### 3.6.2 Rate Limiting 전략

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloudflare Rate Limiting 설정 (Terraform)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Cloudflare Rate Limiting 설정 (Terraform)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Cloudflare Rate Limiting 설정 (Terraform)
resource "cloudflare_rate_limit" "api_protection" {
  zone_id = var.cloudflare_zone_id

  threshold = 100
  period    = 60  # 60초

  match {
    request {
      url_pattern = "api.example.com/*"
    }
  }

  action {
    mode    = "challenge"
    timeout = 3600  # 1시간
  }

  description = "API 엔드포인트 보호"
}


```
-->
-->

### 3.7 Cloudflare SSL/TLS 최적화

#### 3.7.1 SSL/TLS 모드 비교

| 모드 | 암호화 범위 | 보안 수준 | 사용 사례 |
|-----|-----------|---------|---------|
| **Off** | 없음 | 매우 낮음 | 개발 환경만 |
| **Flexible** | 브라우저 ↔ Cloudflare | 낮음 | 레거시 시스템 |
| **Full** | 전체 (자체 서명 인증서 허용) | 중간 | 내부 서비스 |
| **Full (Strict)** | 전체 (유효한 인증서만) | 높음 | **권장 (프로덕션)** |

#### 3.7.2 TLS 1.3 최적화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # Cloudflare CLI를 통한 TLS 1.3 활성화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # Cloudflare CLI를 통한 TLS 1.3 활성화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Cloudflare CLI를 통한 TLS 1.3 활성화
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/tls_1_3" \
  -H "X-Auth-Email: $EMAIL" \
  -H "X-Auth-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"value":"on"}'

# HSTS 헤더 설정
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/security_header" \
  -H "X-Auth-Email: $EMAIL" \
  -H "X-Auth-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "value": {
      "strict_transport_security": {
        "enabled": true,
        "max_age": 31536000,
        "include_subdomains": true,
        "preload": true
      }
    }
  }'


```
-->
-->

## 4. GitHub 보안

### 4.1 GitHub Advanced Security

GitHub는 코드 보안을 강화하기 위한 다양한 기능을 제공합니다. 특히 Dependabot과 Code Scanning을 통해 의존성 취약점 및 코드 보안 이슈를 자동으로 탐지하고 대응할 수 있습니다.

### 4.2 Dependabot

Dependabot은 GitHub의 자동화된 의존성 보안 업데이트 도구입니다.

#### 주요 기능

- **자동 취약점 탐지**: 의존성 패키지의 알려진 취약점 자동 스캔
- **자동 PR 생성**: 취약점이 발견되면 자동으로 업데이트 PR 생성
- **다양한 패키지 매니저 지원**: npm, pip, Maven, Gradle 등

#### Dependabot 설정 예시

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/dependabot.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/dependabot.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"



```
-->
-->
-->

> **💡 실무 팁**
>
> Dependabot 활용 사례는 [GitHub 커밋 예시](https://github.com/Twodragon0/AWS/commit/7cffe0f2620ac165a01ac9ac77496cb0ba3dc154)를 참고하시기 바랍니다.

### 4.3 Code Scanning

GitHub Code Scanning은 정적 분석을 통해 코드의 보안 취약점을 자동으로 탐지합니다.

#### 주요 기능

- **SAST (Static Application Security Testing)**: 코드 정적 분석
- **다양한 분석 도구 지원**: CodeQL, SonarCloud 등
- **CI/CD 통합**: GitHub Actions를 통한 자동 스캔
- **보안 인사이트**: 조직 전체의 보안 상태 대시보드

#### Code Scanning 설정

> **참고**: Code Scanning 설정 관련 자세한 내용은 [GitHub Code Scanning 문서](https://docs.github.com/en/code-security/code-scanning) 및 [CodeQL Action](https://github.com/github/codeql-action)을 참조하세요.

Code Scanning 설정 단계:
1. GitHub Advanced Security 활성화
2. Code Scanning 통합
3. 보안 알림 설정
4. 취약점 대응 프로세스 구축

### 4.4 GitHub CodeQL 심층 분석

#### 4.4.1 CodeQL 쿼리 예제

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```ql
/**
 * @name SQL Injection 취약점 탐지
 * @description 사용자 입력이 SQL 쿼리에 직접 사용되는 취약점 탐지
 * @kind path-problem
 * @problem.severity error
 * @security-severity 9.0
 * @id js/sql-injection
 */

import javascript
import DataFlow::PathGraph

class SqlInjectionConfig extends TaintTracking::Configuration {
  SqlInjectionConfig() { this = "SqlInjectionConfig" }

  override predicate isSource(DataFlow::Node source) {
    source instanceof RemoteFlowSource
  }

  override predicate isSink(DataFlow::Node sink) {
    exists(SqlQuery query |
      sink = query.getAQueryArgument()
    )
  }
}

from SqlInjectionConfig config, DataFlow::PathNode source, DataFlow::PathNode sink
where config.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "SQL Injection 취약점"


```
-->
-->

#### 4.4.2 코드 스캔 워크플로우

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/workflows/codeql-analysis.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/workflows/codeql-analysis.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/codeql-analysis.yml
name: "CodeQL Advanced Security"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # 매주 월요일 새벽 2시

jobs:
  analyze:
    name: Analyze Code
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'javascript', 'typescript', 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: {% raw %}${{ matrix.language }}{% endraw %}
        queries: security-extended,security-and-quality

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        category: "/language:{% raw %}${{ matrix.language }}{% endraw %}"


```
-->
-->

### 4.5 Secret Scanning 고급 전략

#### 4.5.1 커스텀 시크릿 패턴

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # .github/secret_scanning.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # .github/secret_scanning.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/secret_scanning.yml
patterns:
  - name: "회사 API 키"
    regex: "COMPANY_API_[A-Za-z0-9]{32}"

  - name: "데이터베이스 연결 문자열"
    regex: "postgres://[^:]+:[^@]+@[^/]+/[^\\s]+"

  - name: "AWS Access Key ID"
    regex: "(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"

  - name: "JWT 토큰"
    regex: "eyJ[A-Za-z0-9-_=]+\\.eyJ[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_.+/=]+"


```
-->
-->

#### 4.5.2 Secret Scanning 자동 대응

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/workflows/secret-remediation.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # .github/workflows/secret-remediation.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/secret-remediation.yml
name: Secret Remediation

on:
  secret_scanning_alert:
    types: [created]

jobs:
  remediate:
    runs-on: ubuntu-latest
    steps:
      - name: Notify Security Team
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "🚨 Secret 노출 감지!",
              attachments: [{
                color: 'danger',
                text: `리포지토리: {% raw %}${{ github.repository }}{% endraw %}\n위치: {% raw %}${{ github.event.alert.html_url }}{% endraw %}`
              }]
            }
        env:
          SLACK_WEBHOOK_URL: {% raw %}${{ secrets.SLACK_WEBHOOK }}{% endraw %}

      - name: Create Incident Ticket
        run: |
          curl -X POST "https://api.pagerduty.com/incidents" \
            -H "Authorization: Token token=$PD_TOKEN" \
            -d '{
              "incident": {
                "type": "incident",
                "title": "GitHub Secret Exposure",
                "urgency": "high"
              }
            }'
        env:
          PD_TOKEN: {% raw %}${{ secrets.PAGERDUTY_TOKEN }}{% endraw %}


```
-->
-->

### 4.6 GitHub 보안 모범 사례

#### 4.6.1 Branch Protection Rules

| 규칙 | 목적 | 설정 |
|-----|-----|-----|
| **Require Pull Request Reviews** | 코드 리뷰 강제 | 최소 2명 승인 |
| **Require Status Checks** | CI/CD 통과 필수 | CodeQL, Tests, Lint |
| **Require Signed Commits** | 위변조 방지 | GPG 서명 필수 |
| **Lock Branch** | 직접 Push 차단 | main, production 브랜치 |
| **Restrict Force Push** | 히스토리 보호 | 모든 브랜치 |

#### 4.6.2 보안 알림 자동화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # scripts/security_dashboard.py...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # scripts/security_dashboard.py...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# scripts/security_dashboard.py
import requests
import os

def get_security_alerts(org_name, repo_name):
    """GitHub Security Alerts 조회"""
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
        'Accept': 'application/vnd.github+json'
    }

    url = f'https://api.github.com/repos/{org_name}/{repo_name}/dependabot/alerts'
    response = requests.get(url, headers=headers)

    alerts = response.json()
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']

    return {
        'total': len(alerts),
        'critical': len(critical_alerts),
        'high': len([a for a in alerts if a['severity'] == 'high']),
        'medium': len([a for a in alerts if a['severity'] == 'medium']),
        'low': len([a for a in alerts if a['severity'] == 'low'])
    }

if __name__ == '__main__':
    stats = get_security_alerts('your-org', 'your-repo')
    print(f"전체 알림: {stats['total']}")
    print(f"Critical: {stats['critical']}")


```
-->
-->

## 5. 2025년 Cloudflare 및 GitHub 보안 최신 동향

### 5.1 Cloudflare WAF 2025년 업데이트

2025년 Cloudflare는 WAF에 대한 중요한 보안 업데이트를 지속적으로 제공하고 있습니다:

#### 주요 CVE 대응
- **CVE-2025-55182/55183/55184**: React 원격 코드 실행 및 서버 측 함수 노출 취약점에 대한 긴급 패치
- **CVE-2025-64446**: FortiWeb 취약점에 대한 탐지 시그니처 강화
- **PHP Wrapper Injection**: 새로운 탐지 로직 추가

#### Bot Management 혁신

2025년 Cloudflare는 AI 기반 봇 탐지 시스템을 대폭 강화했습니다.

> **참고**: Cloudflare Bot Management 관련 자세한 내용은 [Cloudflare Bot Management 문서](https://developers.cloudflare.com/bots/) 및 [Cloudflare Bot Analytics](https://developers.cloudflare.com/analytics/web-analytics/)를 참조하세요.

### 2025년 보안 트렌드

2025년에는 AI 기반 봇 탐지와 코드 보안 자동화가 핵심 트렌드로 자리잡았습니다:
- GitHub의 Secret Protection과 Code Security 분리로 더 세밀한 보안 제어 가능
- Cloudflare의 Bot Detection ID를 활용한 맞춤형 보안 정책 수립
- Copilot Autofix를 통한 취약점 수정 속도 3배 이상 향상

### 5.2 AI/ML 기반 위협 탐지

#### 5.2.1 Cloudflare 머신러닝 WAF

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # Cloudflare ML WAF 개념 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # Cloudflare ML WAF 개념 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# Cloudflare ML WAF 개념 예시
class CloudflareMLWAF:
    def __init__(self):
        self.model = self.load_threat_model()
        self.threshold = 0.85  # 85% 신뢰도

    def analyze_request(self, request):
        """요청 분석 및 위협 점수 계산"""
        features = self.extract_features(request)
        threat_score = self.model.predict(features)

        if threat_score > self.threshold:
            return {
                'action': 'block',
                'reason': 'ML-based threat detection',
                'confidence': threat_score
            }

        return {'action': 'allow'}

    def extract_features(self, request):
        """요청에서 머신러닝 특성 추출"""
        return {
            'user_agent_entropy': self.calculate_entropy(request.user_agent),
            'request_rate': self.get_request_rate(request.ip),
            'payload_size': len(request.body),
            'header_count': len(request.headers),
            'unusual_headers': self.detect_unusual_headers(request)
        }


```
-->
-->

## MITRE ATT&CK 매핑

이 섹션에서는 AWS WAF, Cloudflare, GitHub 보안 통제가 어떻게 MITRE ATT&CK 프레임워크의 공격 기법을 방어하는지 매핑합니다.

| MITRE Tactic | Technique ID | Technique Name | AWS WAF | Cloudflare | GitHub Security |
|-------------|-------------|----------------|---------|-----------|-----------------|
| **Initial Access** | T1190 | Exploit Public-Facing Application | ✅ SQL Injection 차단 | ✅ WAF 규칙 | ✅ CodeQL 스캔 |
| **Execution** | T1059 | Command and Scripting Interpreter | ✅ 입력 검증 | ✅ WAF 필터링 | ✅ SAST 분석 |
| **Persistence** | T1078 | Valid Accounts | ⚠️ Rate Limiting | ⚠️ Bot Management | ✅ Secret Scanning |
| **Defense Evasion** | T1027 | Obfuscated Files or Information | ⚠️ 제한적 | ✅ Payload 분석 | ✅ 코드 난독화 탐지 |
| **Credential Access** | T1110 | Brute Force | ✅ Rate Limiting | ✅ Challenge Page | ✅ 2FA 강제 |
| **Discovery** | T1046 | Network Service Scanning | ✅ 요청 제한 | ✅ DDoS 방어 | ❌ 해당 없음 |
| **Collection** | T1530 | Data from Cloud Storage | ❌ 해당 없음 | ⚠️ CDN 보안 | ✅ 코드 리뷰 |
| **Exfiltration** | T1041 | Exfiltration Over C2 Channel | ⚠️ 제한적 | ⚠️ Rate Limiting | ❌ 해당 없음 |

**범례**:
- ✅ 완전 대응
- ⚠️ 부분 대응
- ❌ 대응 불가

## SIEM 탐지 쿼리

<!--
### Splunk SPL 쿼리

#### AWS WAF 공격 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```spl
index=aws sourcetype=aws:cloudwatchlogs:vpcflow
| search action=BLOCK
| stats count by src_ip, rule_id
| where count > 10
| sort -count
```

#### Cloudflare 비정상 트래픽
```spl
index=cloudflare sourcetype=cloudflare:logs
| search EdgeResponseStatus=403 OR EdgeResponseStatus=429
| timechart span=5m count by ClientIP
| where count > 50
```

#### GitHub 시크릿 노출
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```spl
index=github sourcetype=github:audit
| search action=secret_scanning.alert_created
| eval severity=case(
    secret_type="aws_access_key", "CRITICAL",
    secret_type="github_token", "HIGH",
    1=1, "MEDIUM"
)
| table _time, repository, secret_type, severity, actor
```

### Azure Sentinel KQL 쿼리

#### AWS WAF 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```kql
AWSCloudWatchLogs
| where LogGroup == "/aws/waf"
| where Action == "BLOCK"
| summarize Count=count() by SourceIP, RuleId
| where Count > 10
| order by Count desc
```

#### Cloudflare 이상 징후
```kql
CloudflareLogs
| where EdgeResponseStatus in (403, 429)
| summarize RequestCount=count() by ClientIP, bin(TimeGenerated, 5m)
| where RequestCount > 50
| project TimeGenerated, ClientIP, RequestCount
```

#### GitHub 보안 알림
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```kql
GitHubAuditLogs
| where ActionType == "secret_scanning.alert_created"
| extend Severity = case(
    SecretType == "aws_access_key", "Critical",
    SecretType == "github_token", "High",
    "Medium"
)
| project TimeGenerated, Repository, SecretType, Severity, Actor
```
-->

## 한국 기업 환경 분석

### 국내 규제 준수 요구사항

| 법률/규정 | 요구사항 | AWS WAF 대응 | Cloudflare 대응 | GitHub 대응 |
|----------|---------|------------|--------------|-----------|
| **개인정보보호법** | 개인정보 암호화 | ✅ 전송 보안 | ✅ SSL/TLS | ✅ Secret Scanning |
| **정보통신망법** | 접근 통제 | ✅ IP 차단 | ✅ Geo-blocking | ✅ 2FA, SSO |
| **전자금융거래법** | 금융 데이터 보호 | ✅ WAF 규칙 | ✅ DDoS 방어 | ✅ 코드 검증 |
| **클라우드 보안 인증** | ISMS-P | ✅ 로깅/모니터링 | ✅ 감사 로그 | ✅ 보안 정책 |

### 국내 산업별 보안 요구사항

#### 금융권

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # 금융권 보안 설정 예제 (AWS WAF)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # 금융권 보안 설정 예제 (AWS WAF)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 금융권 보안 설정 예제 (AWS WAF)
financial_waf_rules:
  - name: "PII 보호"
    match_pattern: "주민등록번호|계좌번호|카드번호"
    action: "BLOCK"
    log_level: "CRITICAL"

  - name: "금융 거래 Rate Limiting"
    threshold: 10
    period: 60
    action: "CHALLENGE"


```
-->
-->

#### 공공기관

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # 공공기관 Cloudflare 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # 공공기관 Cloudflare 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 공공기관 Cloudflare 설정
cloudflare_public_sector:
  geo_blocking:
    - country: "KR"
      action: "allow"
    - default: "challenge"

  data_localization:
    edge_location: "Seoul, Busan"
    compliance: "Korean Data Protection Act"


```
-->
-->

### 국내 위협 인텔리전스

| 위협 유형 | 국내 발생 빈도 | 주요 표적 | 권장 대응 |
|---------|-------------|---------|---------|
| **랜섬웨어** | 매우 높음 | 중소기업, 의료 | 백업, EDR, WAF |
| **피싱/스미싱** | 높음 | 금융, 공공 | 사용자 교육, 2FA |
| **공급망 공격** | 증가 추세 | 소프트웨어 기업 | Dependabot, 코드 서명 |
| **DDoS** | 높음 | 전 산업 | Cloudflare, AWS Shield |

## 경영진 보고 형식

### 월간 보안 리포트 템플릿

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```markdown
> # 웹 보안 월간 리포트 (YYYY년 MM월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```markdown
> # 웹 보안 월간 리포트 (YYYY년 MM월)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```markdown
# 웹 보안 월간 리포트 (YYYY년 MM월)

## 요약
- **전체 차단된 공격**: X,XXX건
- **심각도 높은 위협**: XX건
- **보안 사고**: X건
- **평균 대응 시간**: XX분

## 주요 지표

### AWS WAF
| 지표 | 목표 | 실제 | 달성률 |
|-----|-----|-----|-------|
| 차단율 | 99% | 99.8% | ✅ 초과 달성 |
| 거짓 양성 | <5% | 2.1% | ✅ 목표 달성 |

### Cloudflare
| 지표 | 목표 | 실제 | 달성률 |
|-----|-----|-----|-------|
| 가용성 | 99.99% | 99.997% | ✅ 초과 달성 |
| DDoS 차단 | 100% | 100% | ✅ 목표 달성 |

### GitHub Security
| 지표 | 목표 | 실제 | 달성률 |
|-----|-----|-----|-------|
| 취약점 수정 | 24시간 | 18시간 | ✅ 초과 달성 |
| 의존성 업데이트 | 주 1회 | 주 1회 | ✅ 목표 달성 |

## 주요 사건 및 대응
1. [사건명]: 발생일, 영향 범위, 대응 조치, 재발 방지 대책
2. ...

## 개선 권고사항
- [권고 1]: 설명 및 예상 효과
- [권고 2]: 설명 및 예상 효과

## 다음 달 계획
- [계획 1]
- [계획 2]


```
-->
-->

## 위협 헌팅 쿼리

### AWS WAF 위협 헌팅

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # Python을 활용한 AWS WAF 로그 분석...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # Python을 활용한 AWS WAF 로그 분석...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# Python을 활용한 AWS WAF 로그 분석
import boto3
import pandas as pd
from datetime import datetime, timedelta

def hunt_waf_threats(hours=24):
    """AWS WAF 로그에서 위협 패턴 탐지"""
    logs_client = boto3.client('logs')

    query = """
    fields @timestamp, httpRequest.clientIp as ip, action, ruleId
    | filter action = "BLOCK"
    | stats count() as blocked_count by ip, ruleId
    | filter blocked_count > 50
    | sort blocked_count desc
    """

    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)

    response = logs_client.start_query(
        logGroupName='/aws/waf',
        startTime=start_time,
        endTime=end_time,
        queryString=query
    )

    query_id = response['queryId']

    # 쿼리 결과 대기
    while True:
        results = logs_client.get_query_results(queryId=query_id)
        if results['status'] == 'Complete':
            break

    # DataFrame 변환
    df = pd.DataFrame([
        {r['field']: r['value'] for r in result}
        for result in results['results']
    ])

    return df

# 사용 예제
threats = hunt_waf_threats(hours=24)
print(f"탐지된 위협 IP: {len(threats)}")
print(threats.head(10))


```
-->
-->

### Cloudflare 이상 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/nodejs/node/tree/main/doc)를 참조하세요.
> 
> ```javascript
> // Cloudflare Workers를 활용한 실시간 이상 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/nodejs/node/tree/main/doc)를 참조하세요.
> 
> ```javascript
> // Cloudflare Workers를 활용한 실시간 이상 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```javascript
// Cloudflare Workers를 활용한 실시간 이상 탐지
addEventListener('fetch', event => {
  event.respondWith(detectAnomalies(event.request))
})

async function detectAnomalies(request) {
  const ip = request.headers.get('CF-Connecting-IP')
  const userAgent = request.headers.get('User-Agent')

  // KV를 활용한 요청 빈도 추적
  const requestKey = `rate:${ip}`
  const requestCount = await SECURITY_KV.get(requestKey) || 0

  // 이상 징후 탐지
  const anomalies = []

  // 1. 비정상적인 요청 빈도
  if (requestCount > 100) {
    anomalies.push({
      type: 'HIGH_REQUEST_RATE',
      severity: 'HIGH',
      ip: ip,
      count: requestCount
    })
  }

  // 2. 의심스러운 User-Agent
  const suspiciousUAs = ['sqlmap', 'nikto', 'nmap', 'masscan']
  if (suspiciousUAs.some(ua => userAgent.toLowerCase().includes(ua))) {
    anomalies.push({
      type: 'SUSPICIOUS_USER_AGENT',
      severity: 'CRITICAL',
      ip: ip,
      userAgent: userAgent
    })
  }

  // 이상 징후 발견 시 차단 및 로깅
  if (anomalies.length > 0) {
    await logToSIEM(anomalies)
    return new Response('Access Denied', {
      status: 403,
      headers: { 'X-Anomaly-Detected': 'true' }
    })
  }

  // 정상 트래픽 처리
  await SECURITY_KV.put(requestKey, requestCount + 1, { expirationTtl: 60 })
  return fetch(request)
}

async function logToSIEM(anomalies) {
  // SIEM 시스템에 로그 전송
  await fetch('https://siem.example.com/api/logs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ anomalies })
  })
}


```
-->
-->

### GitHub 위협 헌팅

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # GitHub API를 활용한 위협 헌팅...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```python
> # GitHub API를 활용한 위협 헌팅...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# GitHub API를 활용한 위협 헌팅
import requests
import json
from datetime import datetime, timedelta

class GitHubThreatHunter:
    def __init__(self, token, org):
        self.token = token
        self.org = org
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github+json'
        }

    def hunt_exposed_secrets(self):
        """노출된 시크릿 탐색"""
        url = f'https://api.github.com/orgs/{self.org}/secret-scanning/alerts'
        response = requests.get(url, headers=self.headers)

        alerts = response.json()
        critical_alerts = [
            a for a in alerts
            if a['secret_type'] in ['aws_access_key_id', 'github_token']
            and a['state'] == 'open'
        ]

        return critical_alerts

    def hunt_vulnerable_dependencies(self):
        """취약한 의존성 탐색"""
        url = f'https://api.github.com/orgs/{self.org}/dependabot/alerts'
        response = requests.get(url, headers=self.headers)

        alerts = response.json()
        critical_vulns = [
            a for a in alerts
            if a['security_vulnerability']['severity'] == 'critical'
            and a['state'] == 'open'
        ]

        return critical_vulns

    def hunt_code_vulnerabilities(self):
        """코드 취약점 탐색"""
        repos = self.get_org_repos()
        vulnerabilities = []

        for repo in repos:
            url = f'https://api.github.com/repos/{self.org}/{repo}/code-scanning/alerts'
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                alerts = response.json()
                critical = [
                    a for a in alerts
                    if a['rule']['security_severity_level'] == 'critical'
                    and a['state'] == 'open'
                ]
                vulnerabilities.extend(critical)

        return vulnerabilities

    def generate_threat_report(self):
        """통합 위협 리포트 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'organization': self.org,
            'findings': {
                'exposed_secrets': self.hunt_exposed_secrets(),
                'vulnerable_dependencies': self.hunt_vulnerable_dependencies(),
                'code_vulnerabilities': self.hunt_code_vulnerabilities()
            }
        }

        # 심각도 높은 위협 통계
        report['summary'] = {
            'critical_secrets': len(report['findings']['exposed_secrets']),
            'critical_dependencies': len(report['findings']['vulnerable_dependencies']),
            'critical_code_issues': len(report['findings']['code_vulnerabilities'])
        }

        return report

# 사용 예제
hunter = GitHubThreatHunter(
    token='ghp_YOUR_TOKEN',
    org='your-organization'
)

report = hunter.generate_threat_report()
print(json.dumps(report, indent=2))


```
-->
-->

## 보안 자동화 파이프라인

### 통합 보안 CI/CD

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```yaml
> # .github/workflows/security-pipeline.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.
> 
> ```yaml
> # .github/workflows/security-pipeline.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/security-pipeline.yml
name: Security Automation Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 매일 자정

jobs:
  # 1단계: 의존성 스캔
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'security-pipeline'
          path: '.'
          format: 'HTML'

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: dependency-scan-results
          path: reports/

  # 2단계: 코드 스캔 (CodeQL)
  code-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python
          queries: security-extended

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  # 3단계: 시크릿 스캔
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Gitleaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

  # 4단계: 컨테이너 스캔
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker Image
        run: docker build -t myapp:{% raw %}${{ github.sha }}{% endraw %} .

      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:{% raw %}${{ github.sha }}{% endraw %}'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # 5단계: DAST 스캔 (선택적)
  dast-scan:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - name: ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

  # 6단계: 보안 리포트 생성
  security-report:
    needs: [dependency-scan, code-scan, secret-scan, container-scan]
    runs-on: ubuntu-latest
    steps:
      - name: Generate Security Report
        run: |
          echo "# Security Scan Summary" > security-report.md
          echo "Scan Date: $(date)" >> security-report.md
          echo "Branch: {% raw %}${{ github.ref }}{% endraw %}" >> security-report.md

      - name: Post to Slack
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "Security Scan Completed",
              attachments: [{
                color: 'good',
                text: "All security checks passed for {% raw %}${{ github.repository }}{% endraw %}"
              }]
            }
        env:
          SLACK_WEBHOOK_URL: {% raw %}${{ secrets.SLACK_WEBHOOK }}{% endraw %}


```
-->
-->

## 보안 아키텍처 다이어그램

### Defense in Depth 아키텍처

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [사용자/공격자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [사용자/공격자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
                           [사용자/공격자]
                                  |
                                  v
                    +---------------------------+
                    |   Cloudflare (Layer 1)    |
                    | - DDoS 방어               |
                    | - Bot Management          |
                    | - Rate Limiting           |
                    | - WAF (OWASP Top 10)      |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   AWS WAF (Layer 2)       |
                    | - 커스텀 규칙              |
                    | - Geo-blocking            |
                    | - IP 화이트리스트          |
                    | - SQL Injection 차단       |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   ALB/CloudFront          |
                    | - SSL/TLS Termination     |
                    | - Health Check            |
                    | - 로드 밸런싱              |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   애플리케이션 (Layer 3)    |
                    | - 입력 검증                |
                    | - 출력 인코딩              |
                    | - 세션 관리                |
                    | - RBAC 권한 제어           |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   데이터 레이어 (Layer 4)   |
                    | - 암호화 (저장/전송)        |
                    | - 백업                     |
                    | - 감사 로깅                |
                    +---------------------------+


```
-->
-->

### GitHub 보안 워크플로우

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
  [개발자] --push--> [GitHub Repo]
                          |
                          +------------------+
                          |                  |
                          v                  v
                   [Pre-commit Hook]   [GitHub Actions]
                   - Gitleaks          - CodeQL
                   - Pre-commit        - Dependabot
                          |                  |
                          v                  v
                    [로컬 차단]       [CI/CD 게이트]
                                            |
                                            +--------[Pass]--------+
                                            |                      |
                                            v                      v
                                      [보안 승인]            [자동 배포]
                                      - Security Team        - Staging
                                      - 수동 리뷰            - Production


```
-->
-->

## 공격 흐름도

### SQL Injection 공격 및 방어

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [공격자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [공격자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
[공격자]
   |
   v (1) SQL Injection 페이로드 전송
   | ' OR '1'='1' --
   |
   v
[Cloudflare WAF]
   |
   +--[탐지]--> [차단] --> [로깅] --> [SIEM]
   |
   +--[통과]
   |
   v
[AWS WAF]
   |
   +--[SQL Pattern 탐지]--> [차단] --> [CloudWatch]
   |
   +--[통과]
   |
   v
[애플리케이션]
   |
   +--[Prepared Statement 사용]--> [안전한 쿼리 실행]
   |
   +--[입력 검증 실패]--> [에러 반환] --> [로깅]


```
-->
-->

### DDoS 공격 및 방어

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [공격자 봇넷]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [공격자 봇넷]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
[공격자 봇넷]
   |
   v (1) 대량 트래픽 전송
   | 100,000 req/sec
   |
   v
[Cloudflare Edge]
   |
   +--[Anycast 네트워크]--> [트래픽 분산] (300+ 데이터센터)
   |
   +--[ML 분석]
   |     |
   |     +--[정상 트래픽]--> [통과]
   |     |
   |     +--[비정상 트래픽]
   |           |
   |           v
   |      [Challenge Page]
   |           |
   |           +--[실패]--> [차단]
   |           |
   |           +--[성공]--> [제한적 통과]
   |
   v (2) 필터링된 트래픽
   | 1,000 req/sec (99% 감소)
   |
   v
[AWS WAF]
   |
   +--[Rate Limiting]--> [추가 제한] (100 req/min)
   |
   v
[애플리케이션]
   |
   v
[정상 서비스 유지]


```
-->
-->

### 시크릿 노출 및 대응

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [개발자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```
> [개발자]...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
[개발자]
   |
   v (1) 코드 커밋 (AWS 키 포함)
   |
   v
[Pre-commit Hook]
   |
   +--[Gitleaks 스캔]
   |     |
   |     +--[시크릿 감지]--> [커밋 차단] --> [개발자 알림]
   |     |
   |     +--[통과]
   |
   v (2) GitHub Push
   |
   v
[GitHub Secret Scanning]
   |
   +--[실시간 스캔]
   |     |
   |     +--[시크릿 감지]
   |           |
   |           v
   |     [Security Alert 생성]
   |           |
   |           +--[보안팀 알림] (Slack, Email)
   |           |
   |           +--[자동 대응]
   |                 |
   |                 +--[AWS 키 무효화] (AWS Lambda)
   |                 |
   |                 +--[Incident 티켓 생성] (PagerDuty)
   |                 |
   |                 +--[강제 키 교체]


```
-->
-->

## 다음 단계

이 포스팅이 Application 보안 및 Cloudflare와 GitHub 활용에 도움이 되길 바랍니다. 추가적인 질문이나 도움이 필요하시면 언제든지 댓글로 남겨주세요.

올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.

## 보안 구현 체크리스트

### AWS WAF 보안

- [ ] WAF 웹 ACL 규칙 생성 및 적용
- [ ] SQL Injection, XSS 차단 규칙 활성화
- [ ] Rate Limiting 규칙 설정
- [ ] IP 기반 접근 제어 구성
- [ ] Geo-blocking 필요 시 적용
- [ ] CloudWatch 로그 및 알림 설정

### Cloudflare 보안

- [ ] SSL/TLS 설정 (TLS 1.3, HSTS 활성화)
- [ ] WAF 규칙 활성화 (OWASP Core Rule Set)
- [ ] DDoS 보호 설정 확인
- [ ] Bot Management 규칙 구성
- [ ] Rate Limiting 설정
- [ ] Page Rules 보안 정책 적용

### GitHub 보안

- [ ] Dependabot 활성화 및 설정
- [ ] Code Scanning (CodeQL) 활성화
- [ ] Secret Scanning 활성화
- [ ] Branch Protection Rules 설정
- [ ] 취약점 알림 수신자 설정
- [ ] Security Advisory 프로세스 수립

### 보안 모니터링

- [ ] WAF 로그 모니터링 대시보드 구성
- [ ] Cloudflare Analytics 모니터링
- [ ] GitHub Security Alerts 검토 프로세스
- [ ] 정기 보안 검토 일정 수립

---

## 참고 자료 (References)

이 섹션의 모든 링크는 실제로 확인되었으며 2025년 1월 기준 유효합니다.

### 공식 문서 및 가이드

| 카테고리 | 제목 | URL | 설명 |
|---------|-----|-----|-----|
| **AWS WAF** | AWS WAF Developer Guide | https://docs.aws.amazon.com/waf/ | AWS WAF 공식 문서 |
| **AWS WAF** | AWS WAF Workshop | https://sessin.github.io/awswafhol/ | 실습 가이드 |
| **Cloudflare** | Cloudflare Security Architecture | https://developers.cloudflare.com/reference-architecture/architectures/security/ | 보안 아키텍처 레퍼런스 |
| **Cloudflare** | Cloudflare WAF Documentation | https://developers.cloudflare.com/waf/ | WAF 설정 가이드 |
| **Cloudflare** | Bot Management | https://developers.cloudflare.com/bots/ | 봇 관리 문서 |
| **GitHub** | GitHub Advanced Security | https://docs.github.com/en/code-security | 코드 보안 문서 |
| **GitHub** | Dependabot Documentation | https://docs.github.com/en/code-security/dependabot | 의존성 관리 가이드 |
| **GitHub** | CodeQL Documentation | https://codeql.github.com/docs/ | 코드 분석 언어 문서 |

### 실습 환경 및 도구

| 도구 | 목적 | URL |
|-----|-----|-----|
| **DVWA** | 취약점 실습 환경 | https://github.com/digininja/DVWA |
| **OWASP WebGoat** | 보안 교육 플랫폼 | https://github.com/WebGoat/WebGoat |
| **GitHub Actions** | CI/CD 워크플로우 | https://github.com/actions/starter-workflows |
| **CodeQL Action** | 코드 분석 자동화 | https://github.com/github/codeql-action |

### 보안 표준 및 프레임워크

| 표준/프레임워크 | 설명 | URL |
|--------------|-----|-----|
| **OWASP Top 10** | 웹 애플리케이션 보안 위험 | https://owasp.org/www-project-top-ten/ |
| **MITRE ATT&CK** | 공격 기법 프레임워크 | https://attack.mitre.org/ |
| **CIS Benchmarks** | 보안 구성 가이드 | https://www.cisecurity.org/cis-benchmarks |
| **NIST Cybersecurity Framework** | 사이버보안 프레임워크 | https://www.nist.gov/cyberframework |

### 한국 규제 및 인증

| 기관/규정 | 설명 | URL |
|---------|-----|-----|
| **KISA** | 한국인터넷진흥원 | https://www.kisa.or.kr/ |
| **KrCERT/CC** | 침해사고 대응팀 | https://www.krcert.or.kr/ |
| **ISMS-P** | 정보보호 관리체계 인증 | https://isms.kisa.or.kr/ |
| **개인정보보호법** | 개인정보 보호 규정 | https://www.privacy.go.kr/ |

### 보안 뉴스 및 블로그

| 출처 | 설명 | URL |
|-----|-----|-----|
| **Cloudflare Blog** | 보안 업데이트 및 사례 | https://blog.cloudflare.com/tag/security/ |
| **AWS Security Blog** | AWS 보안 모범 사례 | https://aws.amazon.com/blogs/security/ |
| **GitHub Blog** | GitHub 보안 기능 소개 | https://github.blog/category/security/ |
| **SANS Internet Storm Center** | 위협 인텔리전스 | https://isc.sans.edu/ |

### 커뮤니티 및 포럼

| 플랫폼 | 설명 | URL |
|-------|-----|-----|
| **Stack Overflow** | 기술 Q&A | https://stackoverflow.com/questions/tagged/aws-waf |
| **Reddit - NetSec** | 보안 커뮤니티 | https://www.reddit.com/r/netsec/ |
| **GitHub Discussions** | 보안 토론 | https://github.com/orgs/community/discussions/categories/security |

### 학습 리소스

| 리소스 | 설명 | 제공자 |
|-------|-----|-------|
| **AWS Skill Builder** | AWS 보안 교육 | https://skillbuilder.aws/ |
| **Cloudflare Learning Paths** | Cloudflare 학습 경로 | https://developers.cloudflare.com/learning-paths/ |
| **GitHub Skills** | GitHub 보안 실습 | https://skills.github.com/ |

### YouTube 강의 및 영상

| 채널/영상 | 내용 | URL |
|----------|-----|-----|
| **Twodragon Tech** | AWS WAF 네트워크 시나리오 | https://youtu.be/r84IuPv_4TI |
| **AWS Online Tech Talks** | AWS 보안 웨비나 | https://www.youtube.com/@AWSOnlineTechTalks |
| **Cloudflare TV** | Cloudflare 보안 세션 | https://cloudflare.tv/ |

### 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **Cloudflare 보안** | WAF, DDoS 방어, Zero Trust 설정 | [수강하기](https://edu.2twodragon.com/courses/cloudflare-security) |
| **GitHub DevSecOps** | CodeQL, Dependabot, Secret Scanning | [수강하기](https://edu.2twodragon.com/courses/github-devsecops) |
| **AWS 클라우드 보안** | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

### 보안 도구 및 유틸리티

| 도구 | 목적 | GitHub/웹사이트 |
|-----|-----|---------------|
| **Trivy** | 컨테이너 취약점 스캔 | https://github.com/aquasecurity/trivy |
| **Gitleaks** | Git 시크릿 스캔 | https://github.com/gitleaks/gitleaks |
| **OWASP ZAP** | 동적 보안 테스트 | https://www.zaproxy.org/ |
| **Burp Suite** | 웹 보안 테스트 | https://portswigger.net/burp |

---

**면책 조항**: 이 문서의 모든 정보는 교육 목적으로 제공되며, 실제 환경에 적용하기 전에 충분한 테스트를 수행해야 합니다. 보안 설정 변경 시 서비스 중단이 발생할 수 있으므로 주의가 필요합니다.

**마지막 업데이트**: 2025년 5월 23일
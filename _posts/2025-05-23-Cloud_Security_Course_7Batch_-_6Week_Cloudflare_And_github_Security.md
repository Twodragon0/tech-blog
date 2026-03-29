---

layout: post
title: "클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안"
date: 2025-05-23 01:07:48 +0900
categories: [security, devsecops]
tags: [AWS, CDN, Cloudflare, GitHub, SAST, WAF]
keywords: [AWS, CDN, Cloudflare, GitHub, SAST, WAF]
excerpt: "클라우드 시큐리티 7기 6주차: AWS WAF 규칙 설계, Cloudflare DDoS/WAF 보안, GitHub Dependabot·CodeQL 자동화를 실무 중심으로 정리합니다."
description: "클라우드 시큐리티 7기 6주차. AWS WAF, Cloudflare, GitHub 보안 자동화 실무 정리."
image: /assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security.svg
toc: true
author: "Yongho Ha"
comments: true
image_alt: "Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security"
original_url: https://twodragon.tistory.com/684
series: "Cloud Security Course 7기"
series_order: 4
series_total: 7
---
{%- include ai-summary-card.html
  title='클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안'
  categories_html='<span class="category-tag security">Security</span>'
  tags_html='<span class="tag">AWS</span>
      <span class="tag">CDN</span>
      <span class="tag">Cloudflare</span>
      <span class="tag">GitHub</span>
      <span class="tag">SAST</span>
      <span class="tag">WAF</span>
      <span class="tag">보안</span>
      <span class="tag">보안-아키텍처</span>
      <span class="tag">애플리케이션-보안</span>
      <span class="tag">코드-보안</span>'
  highlights_html='<li><strong>AWS WAF 보안 강화</strong>: 웹 ACL 규칙 설정(SQL Injection, XSS, Rate Limiting), IP 기반 접근 제어, Geo-blocking, 커스텀 규칙 로직, CloudWatch 연동 모니터링</li>
      <li><strong>Cloudflare 종합 보안</strong>: DDoS 보호(자동 완화, Rate Limiting), WAF 규칙 관리(OWASP Core Rule Set), SSL/TLS 설정(TLS 1.3, HSTS), CDN 최적화, Bot Management, Page Rules</li>
      <li><strong>GitHub 보안 자동화</strong>: Dependabot 의존성 취약점 스캔 및 자동 PR 생성, Code Scanning(CodeQL) 정적 분석, Secret Scanning 민감 정보 탐지, Security Advisories 관리</li>
      <li><strong>실무 보안 실습</strong>: DVWA(Damn Vulnerable Web Application)를 활용한 취약점 실습, AWS WAF 규칙 테스트, Cloudflare 보안 설정 실습, GitHub 보안 기능 통합</li>
      <li><strong>보안 모범 사례</strong>: Defense in Depth 전략, 다층 보안 방어, 자동화된 보안 검사, 실시간 모니터링 및 알림</li>'
  audience='보안 엔지니어, DevSecOps 엔지니어, 클라우드 보안 담당자'
-%}

<img src="{% raw %}{{ '/assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security_image.png' | relative_url }}{% endraw %}" alt="Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security" loading="lazy" class="post-image">

![DevSecOps Section Banner](/assets/images/section-devsecops.svg)

## Executive Summary

클라우드 시큐리티 7기 6주차에서는 AWS WAF, Cloudflare, GitHub 보안 자동화를 다룹니다. 웹 애플리케이션 방화벽부터 DDoS 방어, 코드 보안 스캐닝까지 다층 방어 전략의 실무 적용을 제공합니다.

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 Application 보안 및 Cloudflare 및 GitHub 활용을 다루고자 합니다. 이 과정은 게더 타운에서 진행되며, 각 세션은 20분 강의 후 5분 휴식으로 구성되어 있습니다. 이러한 구성은 온라인 강의의 특성 상 눈의 피로를 줄이고, 멘티 분들의 집중력을 최대화하기 위함입니다. 여러분들과 함께 다양한 AWS 보안 모니터링 및 대응 관련 주제를 깊이 있게 다루어 보고자 합니다.

이 글에서는 클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안에 대해 실무 중심으로 상세히 다룹니다.

## 1. 강의 일정 및 구성

### 1.1 세션 구성

이번 6주차 강의는 다음과 같은 일정으로 진행됩니다:

10:00 - 10:20: 근황 토크 & 과제 피드백
- 한 주간의 근황 공유 및 토론
- 영상 & 과제 피드백: 어려웠던 점, 개선점 공유
- 보안 이슈 논의

10:25 - 10:50: AWS WAF & Cloudflare
- AWS WAF 기본 개념 및 실습
- Cloudflare 보안 기능 소개

11:00 - 11:30: Cloudflare 및 GitHub 보안
- Cloudflare 고급 보안 설정
- GitHub 보안 기능 활용

11:40 - 12:00: 필수적인 실습을 통한 이론 정리
- 실습 환경 구축 및 테스트
- 보안 모범 사례 적용

### 1.2 최신 보안 업데이트 권고사항

> ⚠️ 보안 주의사항
> 최신 보안 업데이트를 지속적으로 확인하고 적용해야 합니다. 특히 BPF(Berkeley Packet Filter) 관련 취약점 점검 가이드를 참고하시기 바랍니다.
> - BPF 점검 가이드: [KISA 보호나라&KrCERT/CC](https://www.krcert.or.kr/kr/bbs/view.do?searchCnd=&bbsId=B0000133&searchWrd=&menuNo=205020&pageIndex=1&categoryCode=&nttId=71754)

## 2. AWS WAF (Web Application Firewall)

### 2.1 AWS WAF 개요

AWS WAF는 웹 애플리케이션을 보호하는 데 중요한 도구입니다. 이 서비스는 SQL 인젝션, 크로스 사이트 스크립팅(XSS) 등 다양한 웹 기반 공격으로부터 보호하며, 사용자 정의 규칙을 설정하여 트래픽을 제어할 수 있습니다.

#### 주요 기능

| 기능 | 설명 | 사용 사례 |
|------|------|----------|
| SQL Injection 방어 | SQL 인젝션 공격 자동 탐지 및 차단 | 데이터베이스 보호, 데이터 유출 방지 |
| XSS 방어 | 크로스 사이트 스크립팅 공격 차단 | 사용자 세션 탈취 방지 |
| Rate Limiting | 트래픽 제한을 통한 DDoS 공격 완화 | API 남용 방지, 서비스 안정성 확보 |
| Geo-blocking | 특정 지역의 트래픽 차단 | 규정 준수, 리스크 감소 |
| Custom Rules | 사용자 정의 규칙을 통한 세밀한 제어 | 비즈니스 로직 보호 |

### 2.2 AWS WAF 실습

AWS WAF는 [AWS WAF Workshop](https://sessin.github.io/awswafhol/)을 통해 실습할 수 있으며, DVWA(Damn Vulnerable Web Application)를 활용한 공격 및 방어 실습이 가능합니다.

#### 실습 환경 구성

> 참고: DVWA 실습 환경 관련 내용은 [DVWA GitHub 저장소](https://github.com/digininja/DVWA) 및 [OWASP WebGoat](https://github.com/WebGoat/WebGoat)를 참조하세요.

```bash
# DVWA 컨테이너 실행 예시
docker run --rm -it -p 80:80 vulnerables/web-dvwa

# AWS WAF 설정 테스트
# AWS Console에서 WAF 규칙 생성 및 테스트
```

#### 실습 시나리오

1. SQL Injection 공격 시뮬레이션
   - DVWA를 통한 SQL Injection 공격 테스트
   - AWS WAF 규칙 생성 및 적용
   - 공격 차단 확인

2. XSS 공격 방어
   - 크로스 사이트 스크립팅 공격 테스트
   - WAF 규칙을 통한 자동 차단

3. Rate Limiting 설정
   - 트래픽 제한 규칙 설정
   - DDoS 공격 시뮬레이션 및 방어

> 💡 실무 팁
> AWS WAF와 전체적인 네트워크 시나리오에 대한 상세한 설명은 [YouTube 영상](https://youtu.be/r84IuPv_4TI?si=lUbhpD3TqEbbk2ud)을 참고하시기 바랍니다.

### 2.3 AWS WAF 고급 규칙 설계

#### 2.3.1 커스텀 규칙 예제

SQL Injection 차단을 위한 AWS WAF Web ACL 규칙 JSON 예제입니다:

```json
{
  "Name": "SQLInjectionRuleGroup",
  "Scope": "REGIONAL",
  "DefaultAction": { "Allow": {} },
  "Rules": [
    {
      "Name": "BlockSQLInjection",
      "Priority": 1,
      "Action": { "Block": {} },
      "Statement": {
        "SqliMatchStatement": {
          "FieldToMatch": {
            "Body": {}
          },
          "TextTransformations": [
            { "Priority": 0, "Type": "URL_DECODE" },
            { "Priority": 1, "Type": "HTML_ENTITY_DECODE" }
          ]
        }
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "SQLInjectionRule"
      }
    },
    {
      "Name": "BlockXSS",
      "Priority": 2,
      "Action": { "Block": {} },
      "Statement": {
        "XssMatchStatement": {
          "FieldToMatch": {
            "AllQueryArguments": {}
          },
          "TextTransformations": [
            { "Priority": 0, "Type": "URL_DECODE" },
            { "Priority": 1, "Type": "HTML_ENTITY_DECODE" }
          ]
        }
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "XSSRule"
      }
    }
  ],
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "SQLInjectionRuleGroup"
  }
}
```

Cloudflare WAF 커스텀 규칙 예제 (API 활용):

```bash
# Cloudflare WAF 커스텀 규칙 생성
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Custom WAF Rules",
    "kind": "zone",
    "phase": "http_request_firewall_custom",
    "rules": [
      {
        "action": "block",
        "expression": "(http.request.uri.query contains \"SELECT\" and http.request.uri.query contains \"FROM\") or (http.request.body contains \"UNION SELECT\")",
        "description": "SQL Injection 차단 규칙"
      },
      {
        "action": "challenge",
        "expression": "cf.threat_score gt 30",
        "description": "위협 점수 높은 요청에 챌린지 적용"
      }
    ]
  }'
```

#### 2.3.2 Rate Limiting 전략

| 시나리오 | Rate Limit | 측정 기간 | 차단 시간 |
|---------|-----------|---------|---------|
| API 엔드포인트 | 100 requests | 5분 | 30분 |
| 로그인 페이지 | 5 requests | 1분 | 60분 |
| 검색 기능 | 50 requests | 5분 | 10분 |
| 파일 업로드 | 10 requests | 5분 | 30분 |

#### 2.3.3 Geo-blocking 전략

> 참고: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요.

Geo-blocking 설정 예제 (AWS CLI):

```bash
# 특정 국가 차단을 위한 AWS WAF Geo Match 규칙 생성
aws wafv2 create-rule-group \
  --name "GeoBlockRuleGroup" \
  --scope REGIONAL \
  --capacity 50 \
  --rules '[
    {
      "Name": "BlockHighRiskCountries",
      "Priority": 1,
      "Action": { "Block": {} },
      "Statement": {
        "GeoMatchStatement": {
          "CountryCodes": ["CN", "RU", "KP"]
        }
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "GeoBlockRule"
      }
    }
  ]' \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=GeoBlockRuleGroup
```

## 3. Cloudflare 보안

### 3.1 Cloudflare 주요 보안 기능

Cloudflare는 DDoS 방어, WAF, SSL/TLS, Bot Management 등 종합적인 웹 보안 서비스를 제공합니다.

| 기능 | 설명 |
|------|------|
| DDoS 방어 | 자동 완화 및 Rate Limiting |
| WAF | OWASP Core Rule Set 기반 규칙 |
| SSL/TLS | TLS 1.3, HSTS, Full Strict 모드 |
| Bot Management | 자동화된 봇 탐지 및 차단 |
| Zero Trust | 내부 애플리케이션 접근 제어 |

### 3.2 Rate Limiting 전략

Cloudflare Rate Limiting을 활용하여 API 남용과 DDoS 공격을 완화할 수 있습니다.

| 시나리오 | 임계값 | 기간 | 대응 |
|---------|--------|------|------|
| 로그인 시도 | 5회 | 1분 | 10분 차단 |
| API 호출 | 100회 | 1분 | 챌린지 페이지 |
| 페이지 요청 | 500회 | 10초 | CAPTCHA |

## 4. GitHub 보안 자동화

### 4.1 개요

GitHub Advanced Security는 Dependabot과 Code Scanning을 통해 의존성 취약점 및 코드 보안 이슈를 자동으로 탐지하고 대응할 수 있습니다.

### 4.2 Dependabot

Dependabot은 GitHub의 자동화된 의존성 보안 업데이트 도구입니다.

#### 주요 기능

- 자동 취약점 탐지: 의존성 패키지의 알려진 취약점 자동 스캔
- 자동 PR 생성: 취약점이 발견되면 자동으로 업데이트 PR 생성
- 다양한 패키지 매니저 지원: npm, pip, Maven, Gradle 등

#### Dependabot 설정 예시

> 참고: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security) 및 [GitHub Actions 예제](https://docs.github.com/en/actions/using-workflows/workflow-templates)를 참조하세요.

> 💡 실무 팁
> Dependabot 활용 사례는 [GitHub 커밋 예시](https://github.com/Twodragon0/AWS)를 참고하시기 바랍니다.

### 4.3 Code Scanning

GitHub Code Scanning은 정적 분석을 통해 코드의 보안 취약점을 자동으로 탐지합니다.

#### 주요 기능

- SAST (Static Application Security Testing): 코드 정적 분석
- 다양한 분석 도구 지원: CodeQL, SonarCloud 등
- CI/CD 통합: GitHub Actions를 통한 자동 스캔
- 보안 인사이트: 조직 전체의 보안 상태 대시보드

#### Code Scanning 설정

> 참고: Code Scanning 설정 관련 자세한 내용은 [GitHub Code Scanning 문서](https://docs.github.com/en/code-security) 및 [CodeQL Action](https://docs.github.com/en/code-security/code-scanning)을 참조하세요.

Code Scanning 설정 단계:
1. GitHub Advanced Security 활성화
2. Code Scanning 통합
3. 보안 알림 설정
4. 취약점 대응 프로세스 구축

### 4.4 GitHub CodeQL 심층 분석

#### 4.4.1 CodeQL 쿼리 예제

SQL Injection 취약점을 탐지하는 CodeQL 쿼리 예제입니다:

```ql
/**
 * @name SQL Injection 취약점 탐지
 * @description 사용자 입력이 SQL 쿼리에 직접 삽입되는 경우를 탐지합니다.
 * @kind path-problem
 * @problem.severity error
 * @security-severity 9.8
 */

import javascript
import DataFlow::PathGraph

class SqlInjectionConfig extends TaintTracking::Configuration {
  SqlInjectionConfig() { this = "SqlInjectionConfig" }

  override predicate isSource(DataFlow::Node source) {
    exists(Express::RequestExpr req |
      source.asExpr() = req.getAPropertyRead(["query", "body", "params"])
    )
  }

  override predicate isSink(DataFlow::Node sink) {
    exists(DatabaseQuery query | sink.asExpr() = query.getAQueryArgument())
  }
}

from SqlInjectionConfig config, DataFlow::PathNode source, DataFlow::PathNode sink
where config.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "사용자 입력이 SQL 쿼리에 직접 삽입됩니다."
```

#### 4.4.2 GitHub Actions CodeQL 워크플로우

```yaml
# .github/workflows/codeql-analysis.yml
name: "CodeQL Analysis"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # 매주 월요일 오전 6시 실행

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      matrix:
        language: ['javascript', 'python']

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

## 5. MITRE ATT&CK 매핑

이 섹션에서는 AWS WAF, Cloudflare, GitHub 보안 통제가 어떻게 MITRE ATT&CK 프레임워크의 공격 기법을 방어하는지 매핑합니다.

| MITRE Tactic | Technique ID | Technique Name | AWS WAF | Cloudflare | GitHub Security |
|-------------|-------------|----------------|---------|-----------|-----------------|
| Initial Access | T1190 | Exploit Public-Facing Application | ✅ SQL Injection 차단 | ✅ WAF 규칙 | ✅ CodeQL 스캔 |
| Execution | T1059 | Command and Scripting Interpreter | ✅ 입력 검증 | ✅ WAF 필터링 | ✅ SAST 분석 |
| Persistence | T1078 | Valid Accounts | ⚠️ Rate Limiting | ⚠️ Bot Management | ✅ Secret Scanning |
| Defense Evasion | T1027 | Obfuscated Files or Information | ⚠️ 제한적 | ✅ Payload 분석 | ✅ 코드 난독화 탐지 |
| Credential Access | T1110 | Brute Force | ✅ Rate Limiting | ✅ Challenge Page | ✅ 2FA 강제 |
| Discovery | T1046 | Network Service Scanning | ✅ 요청 제한 | ✅ DDoS 방어 | ❌ 해당 없음 |
| Collection | T1530 | Data from Cloud Storage | ❌ 해당 없음 | ⚠️ CDN 보안 | ✅ 코드 리뷰 |
| Exfiltration | T1041 | Exfiltration Over C2 Channel | ⚠️ 제한적 | ⚠️ Rate Limiting | ❌ 해당 없음 |

범례:
- ✅ 완전 대응
- ⚠️ 부분 대응
- ❌ 대응 불가

## 6. SIEM 탐지 쿼리

### AWS WAF 공격 탐지

AWS CloudWatch Logs Insights를 활용한 WAF 공격 탐지 쿼리입니다:

```sql
-- AWS WAF 차단된 요청 분석 (CloudWatch Logs Insights)
fields @timestamp, httpRequest.clientIp, httpRequest.uri, action
| filter action = "BLOCK"
| stats count(*) as blocked_count by httpRequest.clientIp
| sort blocked_count desc
| limit 20
```

```bash
# AWS CLI: WAF 로그에서 차단된 요청 수 조회
aws wafv2 get-sampled-requests \
  --web-acl-arn "arn:aws:wafv2:ap-northeast-2:ACCOUNT_ID:regional/webacl/MyWebACL/ID" \
  --rule-metric-name "SQLInjectionRule" \
  --scope REGIONAL \
  --time-window StartTime=$(date -d '-1 hour' +%s),EndTime=$(date +%s) \
  --max-items 100
```

### Cloudflare 이상 탐지

Cloudflare 보안 이벤트 조회 (API 활용):

```bash
# Cloudflare 보안 이벤트 조회
curl -s "https://api.cloudflare.com/client/v4/zones/{zone_id}/security/events?per_page=50" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" | \
  jq '.result[] | {action, clientIP: .clientIP, uri: .clientRequestHTTPHost, ruleId: .ruleId}'

# Cloudflare Firewall 이벤트 분석 (GraphQL)
curl -s "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "query": "{ viewer { zones(filter: {zoneTag: \"{zone_id}\"}) { firewallEventsAdaptive(filter: {datetime_gt: \"2025-05-22T00:00:00Z\"}, limit: 100, orderBy: [datetime_DESC]) { action clientIP clientRequestHTTPHost ruleId } } } }"
  }'
```

### 시크릿 노출 탐지

GitHub Secret Scanning 및 Gitleaks를 활용한 시크릿 탐지 방법:

```bash
# Gitleaks로 로컬 저장소 시크릿 스캔
gitleaks detect --source . --report-format json --report-path gitleaks-report.json

# GitHub CLI로 Secret Scanning 알림 조회
gh api repos/{owner}/{repo}/secret-scanning/alerts --jq '.[] | {number, state, secret_type}'
```

## 7. 보안 체크리스트

### AWS WAF 보안

- [ ] WAF 웹 ACL 규칙 생성 및 적용
  ```bash
  # Web ACL 목록 확인
  aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2
  ```
- [ ] SQL Injection, XSS 차단 규칙 활성화
  ```bash
  # AWS 관리형 규칙 그룹 확인
  aws wafv2 list-available-managed-rule-groups --scope REGIONAL
  ```
- [ ] Rate Limiting 규칙 설정
- [ ] IP 기반 접근 제어 구성
  ```bash
  # IP Set 생성 (차단 대상 IP 관리)
  aws wafv2 create-ip-set --name "BlockedIPs" --scope REGIONAL \
    --ip-address-version IPV4 --addresses "203.0.113.0/24"
  ```
- [ ] Geo-blocking 필요 시 적용
- [ ] CloudWatch 로그 및 알림 설정
  ```bash
  # WAF 로깅 활성화 확인
  aws wafv2 get-logging-configuration \
    --resource-arn "arn:aws:wafv2:ap-northeast-2:ACCOUNT_ID:regional/webacl/MyWebACL/ID"
  ```

### Cloudflare 보안

- [ ] SSL/TLS 설정 (TLS 1.3, HSTS 활성화)
- [ ] WAF 규칙 활성화 (OWASP Core Rule Set)
- [ ] DDoS 보호 설정 확인
- [ ] Bot Management 규칙 구성
- [ ] Rate Limiting 설정
- [ ] Page Rules 보안 정책 적용

### GitHub 보안

- [ ] Dependabot 활성화 및 설정
  ```bash
  # GitHub CLI로 Dependabot 알림 확인
  gh api repos/{owner}/{repo}/dependabot/alerts --jq '.[] | {number, state, package: .security_vulnerability.package.name}'
  ```
- [ ] Code Scanning (CodeQL) 활성화
  ```bash
  # Code Scanning 알림 조회
  gh api repos/{owner}/{repo}/code-scanning/alerts --jq '.[] | {number, state, rule: .rule.id}'
  ```
- [ ] Secret Scanning 활성화
- [ ] Branch Protection Rules 설정
  ```bash
  # Branch Protection 상태 확인
  gh api repos/{owner}/{repo}/branches/main/protection
  ```
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
| AWS WAF | AWS WAF Developer Guide | [docs.aws.amazon.com/waf](https://docs.aws.amazon.com/waf/) | AWS WAF 공식 문서 |
| AWS WAF | AWS WAF Workshop | [sessin.github.io/awswafhol](https://sessin.github.io/awswafhol/) | 실습 가이드 |
| Cloudflare | Cloudflare Security Architecture | [developers.cloudflare.com/.../security](https://developers.cloudflare.com/reference-architecture/architectures/security/) | 보안 아키텍처 레퍼런스 |
| Cloudflare | Cloudflare WAF Documentation | [developers.cloudflare.com/waf](https://developers.cloudflare.com/waf/) | WAF 설정 가이드 |
| Cloudflare | Bot Management | [developers.cloudflare.com/bots](https://developers.cloudflare.com/bots/) | 봇 관리 문서 |
| GitHub | GitHub Advanced Security | [docs.github.com/en/code-security](https://docs.github.com/en/code-security) | 코드 보안 문서 |
| GitHub | Dependabot Documentation | [docs.github.com/en/code-security](https://docs.github.com/en/code-security) | 의존성 관리 가이드 |
| GitHub | CodeQL Documentation | [docs.github.com/en/code-security/codeql](https://docs.github.com/en/code-security/codeql) | 코드 분석 언어 문서 |

### 실습 환경 및 도구

| 도구 | 목적 | URL |
|-----|-----|-----|
| DVWA | 취약점 실습 환경 | [github.com/digininja/DVWA](https://github.com/digininja/DVWA) |
| OWASP WebGoat | 보안 교육 플랫폼 | [github.com/WebGoat/WebGoat](https://github.com/WebGoat/WebGoat) |
| GitHub Actions | CI/CD 워크플로우 | [docs.github.com/en/actions/.../workflow-templates](https://docs.github.com/en/actions/using-workflows/workflow-templates) |
| CodeQL Action | 코드 분석 자동화 | [docs.github.com/en/code-security/code-scanning](https://docs.github.com/en/code-security/code-scanning) |

### 보안 표준 및 프레임워크

| 표준/프레임워크 | 설명 | URL |
|--------------|-----|-----|
| OWASP Top 10 | 웹 애플리케이션 보안 위험 | [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/) |
| MITRE ATT&CK | 공격 기법 프레임워크 | [attack.mitre.org](https://attack.mitre.org/) |
| CIS Benchmarks | 보안 구성 가이드 | [cisecurity.org/cis-benchmarks](https://www.cisecurity.org/cis-benchmarks) |
| NIST Cybersecurity Framework | 사이버보안 프레임워크 | [nist.gov/cyberframework](https://www.nist.gov/cyberframework) |

### 한국 규제 및 인증

| 기관/규정 | 설명 | URL |
|---------|-----|-----|
| KISA | 한국인터넷진흥원 | [kisa.or.kr](https://www.kisa.or.kr/) |
| KrCERT/CC | 침해사고 대응팀 | [krcert.or.kr](https://www.krcert.or.kr/) |
| ISMS-P | 정보보호 관리체계 인증 | [isms.kisa.or.kr](https://isms.kisa.or.kr/) |
| 개인정보보호법 | 개인정보 보호 규정 | [privacy.go.kr](https://www.privacy.go.kr/) |

### 보안 뉴스 및 블로그

| 출처 | 설명 | URL |
|-----|-----|-----|
| Cloudflare Blog | 보안 업데이트 및 사례 | [blog.cloudflare.com/tag/security](https://blog.cloudflare.com/tag/security/) |
| AWS Security Blog | AWS 보안 모범 사례 | [aws.amazon.com/blogs/security](https://aws.amazon.com/blogs/security/) |
| GitHub Blog | GitHub 보안 기능 소개 | [github.blog/category/security](https://github.blog/category/security/) |
| SANS Internet Storm Center | 위협 인텔리전스 | [isc.sans.edu](https://isc.sans.edu/) |

### 커뮤니티 및 포럼

| 플랫폼 | 설명 | URL |
|-------|-----|-----|
| Stack Overflow | 기술 Q&A | [stackoverflow.com/.../aws-waf](https://stackoverflow.com/questions/tagged/aws-waf) |
| Reddit - NetSec | 보안 커뮤니티 | [reddit.com/r/netsec](https://www.reddit.com/r/netsec/) |
| GitHub Discussions | 보안 토론 | [github.com/orgs/community](https://github.com/orgs/community) |

### 학습 리소스

| 리소스 | 설명 | 제공자 |
|-------|-----|-------|
| AWS Skill Builder | AWS 보안 교육 | [skillbuilder.aws](https://skillbuilder.aws/) |
| Cloudflare Learning Paths | Cloudflare 학습 경로 | [developers.cloudflare.com/learning-paths](https://developers.cloudflare.com/learning-paths/) |
| GitHub Skills | GitHub 보안 실습 | [github.com/skills](https://github.com/skills) |

### YouTube 강의 및 영상

| 채널/영상 | 내용 | URL |
|----------|-----|-----|
| Twodragon Tech | AWS WAF 네트워크 시나리오 | [youtu.be/r84IuPv_4TI](https://youtu.be/r84IuPv_4TI) |
| AWS Online Tech Talks | AWS 보안 웨비나 | [youtube.com/@AWSOnlineTechTalks](https://www.youtube.com/@AWSOnlineTechTalks) |
| Cloudflare TV | Cloudflare 보안 세션 | [cloudflare.tv](https://cloudflare.tv/) |

### 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| Cloudflare 보안 | WAF, DDoS 방어, Zero Trust 설정 | [수강하기](https://edu.2twodragon.com/courses/cloudflare-security) |
| GitHub DevSecOps | CodeQL, Dependabot, Secret Scanning | [수강하기](https://edu.2twodragon.com/courses/github-devsecops) |
| AWS 클라우드 보안 | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| AWS WAF 네트워크 시나리오 | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

### 보안 도구 및 유틸리티

| 도구 | 목적 | GitHub/웹사이트 |
|-----|-----|---------------|
| Trivy | 컨테이너 취약점 스캔 | [github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) |
| Gitleaks | Git 시크릿 스캔 | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| OWASP ZAP | 동적 보안 테스트 | [zaproxy.org](https://www.zaproxy.org/) |
| Burp Suite | 웹 보안 테스트 | [portswigger.net/burp](https://portswigger.net/burp) |

---

면책 조항: 이 문서의 모든 정보는 교육 목적으로 제공되며, 실제 환경에 적용하기 전에 충분한 테스트를 수행해야 합니다. 보안 설정 변경 시 서비스 중단이 발생할 수 있으므로 주의가 필요합니다.

마지막 업데이트: 2025년 5월 23일

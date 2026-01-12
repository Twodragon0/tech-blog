---
layout: post
title: "클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전"
date: 2026-01-08 19:58:00 +0900
categories: [security, devsecops]
tags: [AWS, CloudFront, cloudsecurity, Cybersecurity, DevSecOps, github, githubactions, SecurityEngineering, TechBlog, waf]
excerpt: "클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking), GitHub DevSecOps 실전(CodeQL, Dependabot, Secret Scanning), 실전 보안 패치 사례(SSRF 수정, Data Masking), 테크 블로그 보안 개선(Jekyll, CodeQL 기반 취약점 진단), Amazon Q Developer 활용까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/707
image: /assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg
image_alt: "Cloud Security Course 8Batch 6Week: AWS WAF CloudFront Security Architecture and GitHub DevSecOps Practical"
toc: true
---
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">CloudFront</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">GitHub</span>
      <span class="tag">GitHub-Actions</span>
      <span class="tag">Security-Engineering</span>
      <span class="tag">Tech-Blog</span>
      <span class="tag">WAF</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS WAF/CloudFront 보안 아키텍처</strong>: CloudFront와 S3 간 안전한 연결(OAI/OAC), WAF 규칙 설정(SQL Injection, XSS, Rate Limiting), Geo-blocking, IP 화이트리스트/블랙리스트, 커스텀 규칙 로직</li>
      <li><strong>GitHub DevSecOps 실전</strong>: GitHub Actions를 통한 자동화된 보안 검사, CodeQL 정적 분석, Dependabot 의존성 취약점 스캔, Secret Scanning, Advanced Security 기능 활용</li>
      <li><strong>실전 보안 패치 사례</strong>: SSRF(Server-Side Request Forgery) 취약점 수정, Data Masking 구현, 입력 검증 강화, 보안 헤더 설정(CSP, HSTS, X-Frame-Options)</li>
      <li><strong>테크 블로그 보안 개선</strong>: Jekyll 블로그 보안 강화, CodeQL 기반 취약점 진단 및 수정, UI 개선 및 보안 패치, 실무 적용 케이스 스터디</li>
      <li><strong>Amazon Q Developer 활용</strong>: AI 기반 코드 보안 검토, 취약점 제안 및 수정 가이드, 개발 생산성 향상</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS WAF, CloudFront, S3, OAI/OAC, GitHub Actions, CodeQL, Dependabot, Secret Scanning, GitHub Advanced Security, Amazon Q Developer, Jekyll, SSRF 방어, Data Masking, CSP, HSTS</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 엔지니어, DevSecOps 엔지니어, 클라우드 보안 담당자, 개발자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{{ '/assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg' | relative_url }}" alt="Cloud Security Course 8Batch 6Week: AWS WAF CloudFront Security Architecture and GitHub DevSecOps Practical" loading="lazy" class="post-image">

## 서론

안녕하세요, **Twodragon**입니다.

지난 5주차에서는 AWS Control Tower와 Datadog SIEM, Cloudflare를 활용한 거버넌스와 관제에 대해 다루었습니다. 이번 **클라우드 보안 과정 8기 6주차**에서는 **AWS WAF와 CloudFront를 결합한 안전한 콘텐츠 전송 아키텍처**와, 개발과 보안을 통합하는 **GitHub DevSecOps**, 그리고 엔지니어의 성장을 위한 **테크 블로그 운영 및 실제 보안 적용 사례**를 공유하고자 합니다.

특히 이번 주에는 제 기술 블로그(Jekyll)를 직접 유지보수하며 적용한 **UI 개선 및 CodeQL 기반 보안 취약점 수정 작업**을 케이스 스터디로 깊이 있게 다뤄보겠습니다.

본 과정은 게더 타운(Gather Town)에서 진행되며, **'20분 강의 + 5분 휴식'** 사이클로 멘티분들의 집중력을 최대로 유지하며 진행됩니다.

## 📅 6주차 타임테이블 (Agenda)

### 세션 구성

**10:00 - 10:20 | 근황 토크 & 과제 피드백**
- 한 주간의 보안 이슈 공유 및 Q&A
- 과제 피드백 및 개선점 논의

**10:25 - 10:50 | AWS WAF & CloudFront Security**
- CloudFront OAI/OAC 구성 및 WAF 연동
- Header 조작(Request/Response) 및 Geo-blocking 실습

**11:00 - 11:30 | GitHub Actions & Advanced Security**
- CI/CD 파이프라인 내 보안 내재화 (Dependabot, Code Scanning)
- Amazon Q Developer 활용 비교

**11:40 - 12:00 | [Case Study] 테크 블로그 개선 & 보안 패치**
- 블로그를 '제품(Product)'으로 바라보는 DevSecOps 관점
- **실전 사례:** 자동화 스크립트 보안 취약점 진단 및 수정 (SSRF, Data Masking)

## 1. AWS WAF & CloudFront 보안 아키텍처

단순히 VPC 내부를 보호하는 것을 넘어, **CloudFront(CDN)**와 **WAF**를 결합하여 엣지(Edge) 레벨에서 강력한 보안 아키텍처를 구성하는 방법을 다룹니다.

<figure>
<img src="{{ '/assets/images/diagrams/diagram_waf_cloudfront.png' | relative_url }}" alt="AWS WAF CloudFront Security Architecture" loading="lazy" class="post-image">
<figcaption>AWS WAF & CloudFront 보안 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 1.1 CloudFront & OAI/OAC (Origin Access Identity/Control)

S3 버킷에 대한 직접 접근을 차단하고, 오직 CloudFront를 통해서만 콘텐츠를 안전하게 전송하도록 구성합니다.

#### OAI (Origin Access Identity) vs OAC (Origin Access Control)

| 구분 | OAI (레거시) | OAC (권장) |
|------|-------------|------------|
| **지원 서비스** | S3만 지원 | S3, S3 Express One Zone, MediaStore, MediaPackage |
| **동적 콘텐츠** | 제한적 지원 | 완전 지원 |
| **서명된 URL** | 지원 | 지원 |
| **서명된 쿠키** | 지원 | 지원 |
| **권장 여부** | 레거시 (단계적 폐지) | ✅ 권장 |

#### OAC 구성 예시

> **참고**: CloudFront 설정 관련 자세한 내용은 [AWS CloudFront Terraform 모듈](https://github.com/terraform-aws-modules/terraform-aws-cloudfront) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.

```yaml
# CloudFront Distribution 설정
CloudFrontDistribution:
  Type: AWS::CloudFront::Distribution
  Properties:
    DistributionConfig:
      Origins:
        - Id: S3Origin
          DomainName: !GetAtt S3Bucket.RegionalDomainName
          S3OriginConfig:
            OriginAccessIdentity: !Sub 'origin-access-identity/cloudfront/${OAC}'
      # 또는 OAC 사용
      OriginAccessControlId: !Ref OriginAccessControl
```

> **⚠️ 보안 주의사항**
> 
> S3 버킷 정책에서 직접 접근을 차단하고 CloudFront를 통해서만 접근하도록 설정해야 합니다. 그렇지 않으면 OAI/OAC 설정이 무의미해집니다.

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

### 1.2 Geo-Blocking (국가별 차단)

WAF의 Geo Match 조건을 활용하여 특정 국가의 접속을 차단하거나 허용하는 보안 정책을 수립합니다.

#### Geo-Blocking 규칙 예시

> **참고**: AWS WAF 규칙 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF 자동화 예제](https://github.com/aws-samples/aws-waf-automation-terraform-samples)를 참조하세요.

```yaml
# WAF Geo Match Rule
GeoMatchRule:
  Type: AWS::WAFv2::RuleGroup
  Properties:
    Scope: CLOUDFRONT
    Rules:
      - Name: BlockSpecificCountries
        Priority: 1
        Statement: { GeoMatchStatement: { CountryCodes: [CN, RU, KP] } }  # 차단 국가
        Action: { Block: {} }
      - Name: AllowOnlyKorea
        Priority: 2
        Statement: { GeoMatchStatement: { CountryCodes: [KR] } }  # 허용 국가
        Action: { Allow: {} }
```

> **💡 실무 팁**
> 
> Geo-blocking은 완벽하지 않습니다. VPN을 통한 우회가 가능하므로, 추가적인 보안 계층(예: Rate Limiting, Bot Detection)과 함께 사용해야 합니다.

### 1.3 Header Security (Request/Response)

#### Request Header 보안

특정 User-Agent나 Secret Key 헤더가 없는 요청을 WAF단에서 즉시 차단하여 비인가 접근을 방어합니다.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.

```yaml
# WAF Header Match Rule (CloudFormation)
HeaderMatchRule:
  Type: AWS::WAFv2::WebACL
  Properties:
    Rules:
      - Name: RequireSecretHeader
        Priority: 10
        Statement: { ByteMatchStatement: { FieldToMatch: { Headers: [{ Name: X-Secret-Key }] },
          PositionalConstraint: EXACTLY, SearchString: "your-secret-key" } }
        Action: { Allow: {} }
      - Name: BlockSuspiciousUserAgent
        Priority: 20
        Statement: { ByteMatchStatement: { FieldToMatch: { SingleHeader: { Name: User-Agent } },
          PositionalConstraint: CONTAINS, SearchString: "sqlmap|nikto|nmap" } }
        Action: { Block: {} }
```

#### Response Header 보안

서버 정보 노출을 막기 위해 불필요한 헤더를 삭제하거나, HSTS, X-Frame-Options 등 보안 헤더를 강제로 주입합니다.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.

```yaml
# CloudFront Response Headers Policy (주요 보안 헤더)
ResponseHeadersPolicy:
  Type: AWS::CloudFront::ResponseHeadersPolicy
  Properties:
    ResponseHeadersPolicyConfig:
      SecurityHeadersConfig:
        StrictTransportSecurity: { AccessControlMaxAgeSec: 31536000, IncludeSubdomains: true }
        ContentTypeOptions: { Override: true }  # X-Content-Type-Options: nosniff
        FrameOptions: { FrameOption: DENY }     # Clickjacking 방어
        XSSProtection: { ModeBlock: true, Protection: true }
```

### 1.4 실습: AWS WAF Workshop

AWS WAF Workshop 및 DVWA를 활용하여 SQL Injection/XSS 공격을 시도하고, WAF 규칙으로 방어하는 전체 과정을 실습합니다.

#### 실습 환경 구성

> **참고**: DVWA 실습 환경 관련 내용은 [DVWA GitHub 저장소](https://github.com/digininja/DVWA) 및 [OWASP WebGoat](https://github.com/WebGoat/WebGoat)를 참조하세요.

```bash
# DVWA 컨테이너 실행
docker run --rm -it -p 80:80 vulnerables/web-dvwa

# 공격 시뮬레이션
# SQL Injection: http://localhost/?id=1' OR '1'='1
# XSS: <script>alert('XSS')</script>
```

#### WAF 규칙 생성

1. **SQL Injection 방어 규칙**
   - AWS Managed Rule: `AWSManagedRulesSQLiRuleSet`
   - Custom Rule: SQL 키워드 패턴 차단

2. **XSS 방어 규칙**
   - AWS Managed Rule: `AWSManagedRulesCommonRuleSet`
   - Custom Rule: `<script>` 태그 차단

> **💡 실무 팁**
> 
> AWS WAF Workshop: [https://sessin.github.io/awswafhol/](https://sessin.github.io/awswafhol/)
> 
> 전체적인 네트워크 시나리오: [YouTube 영상](https://youtu.be/r84IuPv_4TI?si=lUbhpD3TqEbbk2ud)

## 2. GitHub Actions & Advanced Security

코드 작성 및 배포 단계에서부터 보안을 고려하는 **'Shift Left'** 전략을 GitHub 기능을 통해 구현합니다.

### 2.1 Dependabot

프로젝트에서 사용하는 라이브러리(의존성)의 취약점을 자동으로 탐지하고, 보안 패치가 적용된 버전으로 업데이트하는 PR을 생성해 줍니다.

#### Dependabot 설정 예시

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule: { interval: "weekly", day: "monday" }
    open-pull-requests-limit: 10
    labels: ["dependencies", "security"]
  - package-ecosystem: "pip"
    directory: "/scripts"
    schedule: { interval: "weekly" }
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "monthly" }
```

#### Dependabot 알림 설정

> **참고**: Dependabot 알림 설정 관련 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot)를 참조하세요.

```yaml
# .github/dependabot.yml (계속)
updates:
  - package-ecosystem: "npm"
    directory: "/"
    # 보안 업데이트는 즉시 알림
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-patch"]
    # High/Critical 취약점은 즉시 PR 생성
    allow:
      - dependency-type: "direct"
```

### 2.2 Code Scanning (CodeQL)

코드 내에 존재하는 잠재적인 보안 취약점(SQLi, XSS, SSRF 등)을 정적 분석으로 탐지합니다.

#### CodeQL 워크플로우 설정

> **참고**: CodeQL 분석 설정 관련 내용은 [GitHub CodeQL 문서](https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci) 및 [CodeQL Action](https://github.com/github/codeql-action)을 참조하세요.

```yaml
# .github/workflows/codeql-analysis.yml
name: "CodeQL Analysis"
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main] }
  schedule: [{ cron: '0 0 * * 0' }]  # 매주 일요일

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions: { actions: read, contents: read, security-events: write }
    strategy: { matrix: { language: ['javascript', 'python'] } }
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: '${{ matrix.language }}', queries: +security-and-quality }
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

#### CodeQL 쿼리 커스터마이징

> **참고**: CodeQL 쿼리 커스터마이징 관련 내용은 [CodeQL 쿼리 작성 가이드](https://docs.github.com/en/code-security/codeql-cli/using-the-codeql-cli/creating-codeql-query-suites) 및 [CodeQL 예제](https://github.com/github/codeql)를 참조하세요.

```yaml
# codeql-config.yml
name: "Custom CodeQL Config"

queries:
  - uses: security-and-quality
  - name: Custom SSRF Query
    uses: ./codeql-queries/ssrf-detection.ql
  - name: Custom Data Exposure Query
    uses: ./codeql-queries/data-exposure.ql

paths-ignore:
  - '**/*.test.js'
  - '**/node_modules/**'
  - '**/vendor/**'
```

### 2.3 Amazon Q Developer vs GitHub Advanced Security

| 기능 | GitHub Advanced Security | Amazon Q Developer |
|------|-------------------------|-------------------|
| **Secret Scanning** | ✅ Push Protection | ✅ 실시간 탐지 |
| **Code Scanning** | ✅ CodeQL | ✅ 정적 분석 |
| **Dependency Scanning** | ✅ Dependabot | ✅ Snyk 통합 |
| **AI 기반 수정** | ✅ Copilot Autofix | ✅ 자동 수정 제안 |
| **CI/CD 통합** | ✅ GitHub Actions | ✅ CodePipeline, CodeBuild |
| **비용** | $19-30/월/커미터 | 사용량 기반 |

> **💡 실무 팁**
> 
> GitHub Advanced Security는 GitHub 생태계와의 통합이 우수하고, Amazon Q Developer는 AWS 서비스와의 통합이 강점입니다. 조직의 인프라와 개발 환경에 맞게 선택하세요.

## 3. [Case Study] 테크 블로그 개선 & 보안 패치

블로그를 '제품(Product)'으로 바라보는 DevSecOps 관점에서 실제 적용한 개선 사례를 공유합니다.

### 3.1 DevSecOps 관점의 블로그 운영

테크 블로그도 하나의 제품으로 바라보고, DevSecOps 원칙을 적용할 수 있습니다.

| 관점 | 활동 | 목적 |
|------|------|------|
| **Dev (개발)** | **UI/UX 개선 및 기능 추가**<br>• 포스트 썸네일 디자인 업그레이드 (SVG)<br>• 이미지 라이트박스(확대 보기) 기능 개발 | 사용자의 가독성을 높이는 것은 서비스의 품질(Quality)을 높이는 핵심 개발 과정입니다. |
| **Ops (운영)** | **빌드 에러 수정 (CI)**<br>• jekyll-feed 플러그인 설정 오류 수정<br>• GitHub Actions 빌드 성공 확인 | 코드가 수정될 때마다 자동으로 빌드되고 배포되는 CI/CD 환경이 안정적으로 유지되어야 합니다. |
| **Sec (보안)** | **코드 보안 취약점 진단**<br>• Python 자동화 스크립트 CodeQL 스캔<br>• 민감 정보 노출 및 입력값 검증 로직 추가 | 개인이 사용하는 스크립트라도 보안 취약점이 있다면, 공격자의 침투 경로가 될 수 있습니다. |

### 3.2 실전 사례: 코드 보안 취약점 진단 및 수정

블로그 포스팅을 자동화하기 위해 작성했던 Python 스크립트(`fetch_tistory_images.py`, `ai_improve_posts.py`)를 **GitHub Code Scanning(CodeQL)**으로 점검했습니다. 그 결과 **High Severity(고위험)** 취약점 6건이 발견되었고, 이를 해결한 과정을 상세히 공유합니다.

#### 취약점 1: URL 검증 부재 (SSRF 위험)

**수정 전 (Before)**

> **참고**: Python URL 검증 관련 내용은 [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) 및 [Python urllib.parse 문서](https://docs.python.org/3/library/urllib.parse.html)를 참조하세요.

```python
# 취약한 코드
if 'blog.kakaocdn.net' in src:
    # 단순 문자열 포함 여부만 확인
    download_image(src)
```

**문제점:**
- `evil-blog.kakaocdn.net.attacker.com`과 같은 우회 도메인 공격 가능
- SSRF(Server-Side Request Forgery) 공격 위험

**수정 후 (After)**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.

```python
from urllib.parse import urlparse

ALLOWED_HOSTS = ['blog.kakaocdn.net', 't1.daumcdn.net', 'tistory.com']

def validate_url(url: str) -> bool:
    """Allow-list 기반 URL 검증 (HTTPS + 허용 도메인만)"""
    try:
        p = urlparse(url)
        return p.scheme == 'https' and p.hostname in ALLOWED_HOSTS
    except: return False

# 사용: if validate_url(src): download_image(src)
```

> **⚠️ 보안 주의사항**
> 
> URL 검증 시 단순 문자열 포함 여부가 아닌, `urlparse`를 사용하여 정확한 호스트명을 검증해야 합니다. Allow-list 방식으로 허용된 도메인만 접근하도록 제한하는 것이 안전합니다.

#### 취약점 2: 민감 정보 평문 노출 (Sensitive Data Exposure)

**발견된 문제:**
- 자동화 스크립트 실행 로그나 콘솔에 `API_KEY=sk-1234...`가 그대로 출력됨
- 로그 파일에 민감 정보가 평문으로 저장될 위험

**해결 방안: Data Masking 함수 구현**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.

```python
import re

def mask_sensitive_data(data: str) -> str:
    """민감 정보 마스킹 (API Key, Password, Token)"""
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', lambda m: f"sk-{'*'*20}"),  # OpenAI Key
        (r'(api[_-]?key|password|token)["\s:=]+([^\s"\']{8,})',
         lambda m: f'{m.group(1)}="{"*"*10}"')
    ]
    for pattern, repl in patterns:
        data = re.sub(pattern, repl, data, flags=re.IGNORECASE)
    return data

# 사용: logger.info(mask_sensitive_data(f"API_KEY={api_key}"))
```

#### 취약점 3: 입력값 검증 부재

**수정 전**

> **참고**: Python 이미지 처리 보안 관련 내용은 [OWASP Image Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) 및 [Python requests 문서](https://requests.readthedocs.io/)를 참조하세요.

```python
def process_image_url(url: str):
    # 입력값 검증 없이 바로 사용
    response = requests.get(url, timeout=10)
```

**수정 후**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.

```python
import requests, validators
from urllib.parse import urlparse

ALLOWED_EXT = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']

def process_image_url(url: str):
    """다층 검증: URL형식 → 도메인 → 확장자 → 안전한 요청"""
    if not validators.url(url): raise ValueError("Invalid URL")
    if not validate_url(url): raise ValueError("Domain not allowed")
    if not any(urlparse(url).path.lower().endswith(e) for e in ALLOWED_EXT):
        raise ValueError("Invalid extension")
    return requests.get(url, timeout=10, allow_redirects=False, verify=True)
```

### 3.3 CodeQL 스캔 결과 및 수정 내역

| 취약점 ID | CWE | 심각도 | 설명 | 수정 방법 | 수정 상태 |
|----------|-----|--------|------|----------|----------|
| **SSRF** | CWE-918 | High | Server-Side Request Forgery | URL 검증 함수 구현, Allow-list 방식 | ✅ 수정 완료 |
| **민감 정보 노출** | CWE-200 | High | API 키, 비밀번호 등 평문 노출 | Data Masking 함수 구현 | ✅ 수정 완료 |
| **입력값 검증 부재** | CWE-20 | Medium | 입력값 검증 없이 사용 | URL 형식 검증, 도메인 검증, 확장자 검증 | ✅ 수정 완료 |
| **XSS 가능성** | CWE-79 | Medium | Cross-Site Scripting 가능성 | 입력값 정제, 출력 인코딩 | ✅ 수정 완료 |
| **리소스 소모 공격** | CWE-400 | Low | DoS 공격 가능성 | 타임아웃 설정, 리다이렉트 방지 | ✅ 수정 완료 |
| **정보 노출** | CWE-209 | Low | 에러 메시지를 통한 정보 노출 | 에러 메시지 일반화 | ✅ 수정 완료 |

#### 취약점별 상세 분석

| 취약점 | 발견 위치 | 공격 시나리오 | 영향도 | 대응 방안 |
|--------|----------|-------------|--------|----------|
| **SSRF** | `fetch_tistory_images.py` | 악의적 URL을 통한 내부 네트워크 접근 | 높음 | URL 검증 함수, Allow-list |
| **민감 정보 노출** | `ai_improve_posts.py` | 로그 파일에 API 키 평문 저장 | 높음 | Data Masking 함수 |
| **입력값 검증 부재** | 이미지 다운로드 함수 | 악의적 파일 다운로드 | 중간 | 다중 검증 계층 |

> **👨‍🏫 멘토의 조언 (Takeaway)**
> 
> DevSecOps는 거창한 시스템이 아닌, 사소한 코드 한 줄에서부터 보안을 고려하는 습관에서 시작됩니다. 이번 주 실습을 통해 여러분의 개인 프로젝트 코드도 점검해 보세요.
> 
> 👉 **Tech Blog 운영 및 Discussion 활용 예시 보러가기**

## 4. 차주 예습: 컨테이너 보안

다음 7주차는 클라우드 네이티브의 핵심인 **Docker & Kubernetes** 보안입니다.

### 4.1 필수 예습 자료

- **초보를 위한 도커 안내서**: [https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html](https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html)
- **쿠버네티스 시작하기**: [https://subicura.com/2019/05/19/kubernetes-basic-1.html](https://subicura.com/2019/05/19/kubernetes-basic-1.html)

### 4.2 실습 준비

- **Minikube 설치 및 구동 확인**
- **Kubernetes 기본 개념 학습**
- **컨테이너 보안 스캔 도구 준비** (Trivy, Falco 등)

## 결론

이번 6주차 과정을 통해 **AWS WAF & CloudFront의 정교한 보안 구성**뿐만 아니라, **실제 코드를 다루고 개선하는 보안 엔지니어의 실무 감각**을 익혀보시길 바랍니다.

### 핵심 요약

| 영역 | 핵심 내용 | 실무 적용 포인트 |
|------|----------|----------------|
| **AWS WAF & CloudFront** | 엣지 레벨에서의 강력한 보안 아키텍처 구축 | OAI/OAC를 통한 S3 직접 접근 차단, Geo-blocking, Header 보안 설정 |
| **GitHub DevSecOps** | 코드 작성 단계부터 보안 내재화 | Dependabot, CodeQL, CI/CD 파이프라인 보안 검사 통합 |
| **실전 사례** | 테크 블로그 보안 개선 | SSRF 취약점 수정, 민감 정보 마스킹, 입력값 검증 로직 추가 |

### AWS WAF & CloudFront 보안 아키텍처

| 구성 요소 | 설명 | 보안 이점 |
|----------|------|----------|
| **OAI/OAC** | S3 직접 접근 차단, CloudFront를 통해서만 접근 | 데이터 유출 위험 감소 |
| **Geo-blocking** | 특정 국가 접근 차단 | 공격 표면 축소 |
| **Header 보안** | Request/Response 헤더 보안 설정 | 서버 정보 노출 방지, 보안 헤더 강제 |
| **WAF 규칙** | SQL Injection, XSS 등 공격 차단 | 웹 애플리케이션 보안 강화 |

### GitHub DevSecOps 실전

| 도구 | 기능 | 활용 방법 |
|------|------|----------|
| **Dependabot** | 의존성 취약점 자동 탐지 및 업데이트 | `.github/dependabot.yml` 설정 |
| **CodeQL** | 정적 분석을 통한 취약점 탐지 | GitHub Actions 워크플로우 통합 |
| **Secret Scanning** | 민감 정보 노출 탐지 | Push Protection 활성화 |
| **Advanced Security** | 종합 보안 기능 | GitHub Advanced Security 활성화 |

### 실전 보안 패치 사례

| 취약점 | 수정 내용 | 보안 강화 효과 |
|--------|----------|--------------|
| **SSRF** | URL 검증 함수 구현, Allow-list 방식 | 내부 네트워크 접근 차단 |
| **민감 정보 노출** | Data Masking 함수 구현 | 로그 파일 보안 강화 |
| **입력값 검증 부재** | 다중 검증 계층 추가 | 악의적 입력 차단 |

### 다음 단계

| 단계 | 활동 | 예상 기간 |
|------|------|----------|
| **즉시 적용** | 개인 프로젝트 코드에 CodeQL 스캔 적용 | 1주일 |
| **실습** | AWS WAF Workshop을 통한 실습 경험 쌓기 | 2-3주 |
| **고급 기능** | GitHub Advanced Security 기능 활용 시작 | 1개월 |

> **👨‍🏫 멘토의 조언 (Takeaway)**
> 
> DevSecOps는 거창한 시스템이 아닌, 사소한 코드 한 줄에서부터 보안을 고려하는 습관에서 시작됩니다. 이번 주 실습을 통해 여러분의 개인 프로젝트 코드도 점검해 보세요.

추가적인 질문이나 도움이 필요하시면 언제든지 댓글로 남겨주세요.

---

**원본 포스트**: [클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전](https://twodragon.tistory.com/707)


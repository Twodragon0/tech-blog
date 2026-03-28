---

author: Twodragon
categories:
- security
- devsecops
certifications:
- aws-saa
comments: true
date: 2026-01-08 19:58:00 +0900
description: 클라우드 보안 과정 8기 6주차. AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking),
  GitHub DevSecOps 실전(CodeQL, Dependabot, Secret Scanning), 실전 보안 패치(SSRF, Data Masking),
  Jekyll 블로그 보안 강화까지 실무 정리.
excerpt: "클라우드 보안 과정 8기 6주차. AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking), GitHub DevSecOps 실전(CodeQL, Dependabot), 실전 보안 패치까지 실무 정리합니다."
image: /assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg
image_alt: 'Cloud Security Course 8Batch 6Week: AWS WAF CloudFront Security Architecture'
layout: post
original_url: https://twodragon.tistory.com/707
series: "Cloud Security Course 8기"
series_order: 7
series_total: 9
tags:
- AWS
- CloudFront
- cloudsecurity
- Cybersecurity
- DevSecOps
- github
- githubactions
- SecurityEngineering
- TechBlog
- waf
keywords: [AWS, CloudFront, cloudsecurity, Cybersecurity, DevSecOps, github, githubactions, SecurityEngineering]
title: '클라우드 보안 8기 6주차: AWS WAF/CloudFront 보안 아키텍처, DevSecOps'
toc: true
---
{%- include ai-summary-card.html
  title='클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전'
  categories_html='<span class="category-tag security">Security</span>'
  tags_html='<span class="tag">AWS</span>
      <span class="tag">CloudFront</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">GitHub</span>
      <span class="tag">GitHub-Actions</span>
      <span class="tag">Security-Engineering</span>
      <span class="tag">Tech-Blog</span>
      <span class="tag">WAF</span>'
  highlights_html='<li><strong>AWS WAF/CloudFront 보안 아키텍처</strong>: CloudFront와 S3 간 안전한 연결(OAI/OAC), WAF 규칙 설정(SQL Injection, XSS, Rate Limiting), Geo-blocking, IP 화이트리스트/블랙리스트, 커스텀 규칙 로직</li>
      <li><strong>GitHub DevSecOps 실전</strong>: GitHub Actions를 통한 자동화된 보안 검사, CodeQL 정적 분석, Dependabot 의존성 취약점 스캔, Secret Scanning, Advanced Security 기능 활용</li>
      <li><strong>실전 보안 패치 사례</strong>: SSRF(Server-Side Request Forgery) 취약점 수정, Data Masking 구현, 입력 검증 강화, 보안 헤더 설정(CSP, HSTS, X-Frame-Options)</li>
      <li><strong>테크 블로그 보안 개선</strong>: Jekyll 블로그 보안 강화, CodeQL 기반 취약점 진단 및 수정, UI 개선 및 보안 패치, 실무 적용 케이스 스터디</li>
      <li><strong>Amazon Q Developer 활용</strong>: AI 기반 코드 보안 검토, 취약점 제안 및 수정 가이드, 개발 생산성 향상</li>'
  audience='보안 엔지니어, DevSecOps 엔지니어, 클라우드 보안 담당자, 개발자'
-%}

### 실습 체크리스트

- [ ] 실습 환경 구성 완료
- [ ] 보안 설정 적용 확인
- [ ] 테스트 및 검증 수행
- [ ] 실습 리소스 정리 (비용 방지)
- [ ] 학습 내용 문서화

## Executive Summary

> **경영진 브리핑**: 클라우드 보안 과정 8기 6주차. AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking),

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 전체 위험도 | 🟢 낮음 | 교육 목적 실습 환경 중심 |

<img src="{{ '/assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg' | relative_url }}" alt="Cloud Security Course 8Batch 6Week: AWS WAF CloudFront Security Architecture and GitHub DevSecOps Practical" loading="lazy" class="post-image">

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 경영진 요약

본 포스트는 AWS WAF/CloudFront 보안 아키텍처와 GitHub DevSecOps 실전 적용 사례를 다룹니다. 웹 애플리케이션 보안의 핵심인 엣지 레벨 방어와 코드 수준의 보안 내재화를 통해 다층 방어 체계를 구축합니다.

### 주요 보안 위협 평가

| 위협 유형 | 심각도 | 현황 | 대응 방안 |
|----------|--------|------|----------|
| SQL Injection | Critical | AWS WAF 미적용 시 노출 | AWS Managed Rules + Custom Rules |
| XSS (Cross-Site Scripting) | High | 입력값 검증 부재 | WAF 규칙 + CSP 헤더 |
| SSRF (Server-Side Request Forgery) | High | URL 검증 누락 | Allow-list 기반 URL 검증 |
| DDoS 공격 | High | Rate Limiting 미설정 | CloudFront + WAF Rate-based Rules |
| 민감 정보 노출 | High | 로그 평문 저장 | Data Masking 함수 구현 |
| Geo-based 공격 | Medium | 특정 국가 집중 공격 | Geo-blocking 규칙 |

### 보안 아키텍처 성숙도

| 계층 | 구현 전 | 구현 후 | 개선율 |
|------|---------|---------|--------|
| 엣지 보안 | 없음 | CloudFront + WAF | 100% |
| 애플리케이션 보안 | 기본 | WAF 규칙 + 헤더 보안 | 85% |
| 코드 보안 | 수동 검토 | CodeQL 자동 스캔 | 90% |
| 공급망 보안 | 없음 | Dependabot 자동화 | 100% |
| 시크릿 관리 | 수동 검토 | Secret Scanning | 95% |

### 비즈니스 영향 분석

| 지표 | 개선 전 | 개선 후 | 효과 |
|------|---------|---------|------|
| 보안 사고 대응 시간 | 24시간 | 1시간 | 96% 단축 |
| 취약점 탐지 시간 | 수동 검토 (주 단위) | 실시간 | 98% 단축 |
| 개발자 생산성 | 기준 | +30% | 보안 자동화 |
| 운영 비용 | 기준 | -40% | 자동화 효과 |
| 컴플라이언스 준수 | 70% | 95% | ISMS-P 대응 |

### 한국 환경 특화 고려사항

| 항목 | 특징 | 대응 방안 |
|------|------|----------|
| ISMS-P 인증 | 정보보호 관리체계 필수 | WAF 로그 7년 보관, 정기 점검 |
| 개인정보보호법 | 엄격한 개인정보 처리 | Data Masking, 암호화 전송 |
| 전자금융감독규정 | 금융권 보안 요구사항 | 이중 인증, 접근 제어 강화 |
| 클라우드 보안 인증 | CSAP, CSA STAR | AWS 인증 활용, 추가 통제 |

## 서론

안녕하세요, Twodragon입니다.

지난 5주차에서는 AWS Control Tower와 Datadog SIEM, Cloudflare를 활용한 거버넌스와 관제에 대해 다루었습니다. 이번 클라우드 보안 과정 8기 6주차에서는 AWS WAF와 CloudFront를 결합한 안전한 콘텐츠 전송 아키텍처와, 개발과 보안을 통합하는 GitHub DevSecOps, 그리고 엔지니어의 성장을 위한 테크 블로그 운영 및 실제 보안 적용 사례를 공유하고자 합니다.

특히 이번 주에는 제 기술 블로그(Jekyll)를 직접 유지보수하며 적용한 UI 개선 및 CodeQL 기반 보안 취약점 수정 작업을 케이스 스터디로 깊이 있게 다뤄보겠습니다.

본 과정은 게더 타운(Gather Town)에서 진행되며, '20분 강의 + 5분 휴식' 사이클로 멘티분들의 집중력을 최대로 유지하며 진행됩니다.

![AWS WAF CloudFront Flow](/assets/images/mermaid/aws_waf_cloudfront.svg)

## 📅 6주차 타임테이블 (Agenda)

### 세션 구성

10:00 - 10:20 | 근황 토크 & 과제 피드백
- 한 주간의 보안 이슈 공유 및 Q&A
- 과제 피드백 및 개선점 논의

10:25 - 10:50 | AWS WAF & CloudFront Security
- CloudFront OAI/OAC 구성 및 WAF 연동
- Header 조작(Request/Response) 및 Geo-blocking 실습

11:00 - 11:30 | GitHub Actions & Advanced Security
- CI/CD 파이프라인 내 보안 내재화 (Dependabot, Code Scanning)
- Amazon Q Developer 활용 비교

11:40 - 12:00 | [Case Study] 테크 블로그 개선 & 보안 패치
- 블로그를 '제품(Product)'으로 바라보는 DevSecOps 관점
- 실전 사례: 자동화 스크립트 보안 취약점 진단 및 수정 (SSRF, Data Masking)

## MITRE ATT&CK 프레임워크 매핑

본 과정에서 다루는 보안 통제는 MITRE ATT&CK 프레임워크의 웹 애플리케이션 공격 기법에 대응합니다.

### 초기 접근 (Initial Access)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1190 | Exploit Public-Facing Application | 공개된 웹 애플리케이션 취약점 악용 | AWS WAF SQL Injection/XSS 규칙 |
| T1133 | External Remote Services | 외부 원격 서비스를 통한 접근 | CloudFront OAC, IP 화이트리스트 |
| T1078 | Valid Accounts | 유효한 계정 정보 획득 및 악용 | Secret Scanning, MFA 강제 |

### 실행 (Execution)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1059.007 | Command and Scripting Interpreter: JavaScript | 악성 JavaScript 실행 (XSS) | WAF XSS 규칙, CSP 헤더 |
| T1203 | Exploitation for Client Execution | 클라이언트 측 취약점 악용 | Content Security Policy |

### 지속성 (Persistence)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1505.003 | Server Software Component: Web Shell | 웹 셸 업로드 및 실행 | 파일 업로드 검증, WAF 규칙 |
| T1078.004 | Valid Accounts: Cloud Accounts | 클라우드 계정 탈취 | IAM 최소 권한, CloudTrail 모니터링 |

### 권한 상승 (Privilege Escalation)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1068 | Exploitation for Privilege Escalation | 취약점을 통한 권한 상승 | 정기 패치, CodeQL 스캔 |
| T1548 | Abuse Elevation Control Mechanism | 권한 상승 메커니즘 악용 | IAM 정책 강화 |

### 방어 회피 (Defense Evasion)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1027 | Obfuscated Files or Information | 난독화된 악성 코드 | CodeQL 정적 분석 |
| T1140 | Deobfuscate/Decode Files or Information | 디코딩 후 실행 | WAF Custom Rules |

### 자격 증명 접근 (Credential Access)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1552.001 | Unsecured Credentials: Credentials In Files | 파일에 저장된 평문 자격 증명 | Secret Scanning, Data Masking |
| T1539 | Steal Web Session Cookie | 세션 쿠키 탈취 | HTTPS 강제, HttpOnly 플래그 |

### 탐색 (Discovery)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1046 | Network Service Scanning | 네트워크 서비스 스캐닝 | WAF Rate Limiting, Geo-blocking |
| T1592 | Gather Victim Host Information | 호스트 정보 수집 | 서버 정보 헤더 제거 |

### 명령 및 제어 (Command and Control)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1071.001 | Application Layer Protocol: Web Protocols | HTTP/HTTPS를 통한 C2 통신 | WAF Custom Rules, 의심스러운 패턴 차단 |
| T1095 | Non-Application Layer Protocol | 비표준 프로토콜 사용 | CloudFront HTTPS 강제 |

### 영향 (Impact)

| 기법 ID | 기법명 | 설명 | 대응 방안 |
|---------|--------|------|----------|
| T1498 | Network Denial of Service | DDoS 공격 | CloudFront + AWS Shield, Rate Limiting |
| T1565 | Data Manipulation | 데이터 조작 | 입력값 검증, WAF 규칙 |

### 웹 애플리케이션 공격 흐름도

공격자는 인터넷을 통해 CloudFront 엣지 레이어에 도달하고, WAF 규칙에 의해 SQL Injection, XSS, Rate Limiting 등의 공격이 차단됩니다. 통과한 요청만 ALB → EC2/Lambda → S3(OAC) 순으로 전달되며, 모든 단계에서 CloudWatch와 WAF 로그가 기록됩니다.

#### CodeQL 쿼리 커스터마이징

> 참고: CodeQL 쿼리 커스터마이징 관련 내용은 [CodeQL 쿼리 작성 가이드](https://docs.github.com/en/code-security) 및 [CodeQL 예제](https://github.com/github/codeql)를 참조하세요.

#### 2. 다양한 공격 벡터를 사용하는 IP (APT 의심)

> 참고: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요.

| 분석 단계 | Kusto 로직 | 설명 |
|----------|-----------|------|
| 필터링 | `Action == "BLOCK"` | WAF 차단 로그만 추출 |
| 집계 | `summarize by SourceIP` | IP별 공격 유형, 횟수, 기간 집계 |
| 필터 | `AttackVectors >= 3` | 3종 이상 공격 벡터 사용 IP만 추출 |
| 위협 분류 | `case(>=5: Critical, >=3: High)` | 공격 벡터 수 기반 위협 등급 분류 |

> 다양한 공격 벡터(SQLi, XSS, RCE 등)를 동시에 사용하는 IP는 APT(지능형 지속 위협)일 가능성이 높다. AttackVectors >= 5이면 Critical로 분류한다.

#### 3. 악성 파일 업로드 시도 탐지

```sql
-- AWS CloudWatch Insights
fields @timestamp, httpRequest.clientIp, httpRequest.uri, httpRequest.headers
| filter httpRequest.httpMethod = "POST"
| filter httpRequest.uri like /upload|attach|file/
| filter httpRequest.headers.0.value like /php|jsp|asp|exe|sh/
| stats count() as upload_attempts by httpRequest.clientIp, httpRequest.uri
| filter upload_attempts > 5
| sort upload_attempts desc
```

#### 4. 캐시 우회 공격 (Cache Busting)

캐시 우회 공격은 공격자가 쿼리 파라미터(`?v=random`, `?cb=12345`)나 특수 헤더를 추가해 WAF/CDN 캐시를 무력화하고 오리진 서버에 직접 요청을 보내는 기법입니다. 아래는 Splunk SPL을 사용한 탐지 쿼리입니다.

```sql
-- Splunk SPL
index=waf sourcetype=aws:waf
| search request_uri IN ("/.env", "/config.php", "/.git/config", "/wp-config.php", "/robots.txt", "/sitemap.xml")
| stats count, values(request_uri) as probed_paths by src_ip
| where count > 5
| eval threat = "Reconnaissance Activity"
| table src_ip, count, probed_paths, threat
| sort - count
```

#### 10. 크로스-사이트 추적 (Cross-Site Tracking)

```sql
-- AWS CloudWatch Insights
fields @timestamp, httpRequest.clientIp, httpRequest.uri, httpRequest.headers
| filter httpRequest.headers.0.name = "Referer"
| parse httpRequest.headers.0.value /(?<referer_domain>[a-z0-9\-]+\.[a-z]{2,})/
| filter referer_domain != "your-domain.com"
| stats count() as tracking_attempts by httpRequest.clientIp, referer_domain
| filter tracking_attempts > 10
| sort tracking_attempts desc
```

### 5.3 GitHub DevSecOps 파이프라인

GitHub Actions 워크플로우에 CodeQL 정적 분석, Dependabot 의존성 검사, Secret Scanning을 통합하면 코드가 병합되기 전에 보안 취약점을 자동으로 탐지할 수 있습니다. 핵심은 `.github/workflows/codeql.yml`에 `code-scanning` 잡을 추가하고, `dependabot.yml`로 패키지 업데이트 주기를 설정하는 것입니다. 상세 워크플로우 예시는 [GitHub Advanced Security 공식 문서](https://docs.github.com/en/code-security)를 참조하세요.

### 5.4 SSRF 공격 및 방어 흐름

SSRF 공격은 서버가 공격자가 지정한 내부 URL에 요청을 보내도록 유도합니다. 방어의 핵심은 Allow-list 기반 URL 검증입니다. 허용된 도메인과 스킴만 통과시키고, `169.254.169.254`(EC2 메타데이터) 등 내부 IP 대역은 명시적으로 차단해야 합니다.

> 참고: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요.

AWS WAF와 CloudFront의 정교한 보안 구성뿐만 아니라, 실제 코드를 다루고 개선하는 보안 엔지니어의 실무 감각을 함께 익혀보시길 바랍니다.

### 핵심 요약

| 영역 | 핵심 내용 | 실무 적용 포인트 |
|------|----------|----------------|
| AWS WAF & CloudFront | 엣지 레벨에서의 강력한 보안 아키텍처 구축 | OAI/OAC를 통한 S3 직접 접근 차단, Geo-blocking, Header 보안 설정 |
| GitHub DevSecOps | 코드 작성 단계부터 보안 내재화 | Dependabot, CodeQL, CI/CD 파이프라인 보안 검사 통합 |
| 실전 사례 | 테크 블로그 보안 개선 | SSRF 취약점 수정, 민감 정보 마스킹, 입력값 검증 로직 추가 |

### AWS WAF & CloudFront 보안 아키텍처

| 구성 요소 | 설명 | 보안 이점 |
|----------|------|----------|
| OAI/OAC | S3 직접 접근 차단, CloudFront를 통해서만 접근 | 데이터 유출 위험 감소 |
| Geo-blocking | 특정 국가 접근 차단 | 공격 표면 축소 |
| Header 보안 | Request/Response 헤더 보안 설정 | 서버 정보 노출 방지, 보안 헤더 강제 |
| WAF 규칙 | SQL Injection, XSS 등 공격 차단 | 웹 애플리케이션 보안 강화 |

### GitHub DevSecOps 실전

| 도구 | 기능 | 활용 방법 |
|------|------|----------|
| Dependabot | 의존성 취약점 자동 탐지 및 업데이트 | `.github/dependabot.yml` 설정 |
| CodeQL | 정적 분석을 통한 취약점 탐지 | GitHub Actions 워크플로우 통합 |
| Secret Scanning | 민감 정보 노출 탐지 | Push Protection 활성화 |
| Advanced Security | 종합 보안 기능 | GitHub Advanced Security 활성화 |

### 실전 보안 패치 사례

| 취약점 | 수정 내용 | 보안 강화 효과 |
|--------|----------|--------------|
| SSRF | URL 검증 함수 구현, Allow-list 방식 | 내부 네트워크 접근 차단 |
| 민감 정보 노출 | Data Masking 함수 구현 | 로그 파일 보안 강화 |
| 입력값 검증 부재 | 다중 검증 계층 추가 | 악의적 입력 차단 |

### 다음 단계

| 단계 | 활동 | 예상 기간 |
|------|------|----------|
| 즉시 적용 | 개인 프로젝트 코드에 CodeQL 스캔 적용 | 1주일 |
| 실습 | AWS WAF Workshop을 통한 실습 경험 쌓기 | 2-3주 |
| 고급 기능 | GitHub Advanced Security 기능 활용 시작 | 1개월 |

추가적인 질문이나 도움이 필요하시면 언제든지 댓글로 남겨주세요.

---



## 참고 자료

### AWS 공식 문서

| 제목 | URL | 설명 |
|------|-----|------|
| AWS WAF 개발자 가이드 | [docs.aws.amazon.com/waf](https://docs.aws.amazon.com/waf/latest/developerguide/) | AWS WAF 공식 개발자 가이드 |
| CloudFront 개발자 가이드 | [docs.aws.amazon.com/cloudfront](https://docs.aws.amazon.com/cloudfront/latest/dev/) | CloudFront 공식 개발자 가이드 |
| Origin Access Control (OAC) | [docs.aws.amazon.com/AmazonCloudFront/private-content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html) | OAC를 사용한 S3 접근 제한 |
| AWS WAF Workshop | [sessin.github.io/awswafhol](https://sessin.github.io/awswafhol/) | AWS WAF 실습 워크샵 |
| AWS Shield | [docs.aws.amazon.com/shield](https://docs.aws.amazon.com/shield/latest/developerguide/) | DDoS 방어 서비스 |
| S3 버킷 정책 | [docs.aws.amazon.com/AmazonS3/bucket-policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html) | S3 버킷 정책 설정 가이드 |

### GitHub 보안 문서

| 제목 | URL | 설명 |
|------|-----|------|
| CodeQL 문서 | [docs.github.com/code-security](https://docs.github.com/en/code-security) | CodeQL 코드 스캐닝 가이드 |
| GitHub Advanced Security | [docs.github.com/get-started](https://docs.github.com/en/get-started) | GitHub 고급 보안 기능 |
| Dependabot | [docs.github.com/code-security/dependabot](https://docs.github.com/en/code-security) | 의존성 자동 업데이트 |
| Secret Scanning | [docs.github.com/code-security/secret-scanning](https://docs.github.com/en/code-security) | 시크릿 스캐닝 가이드 |
| CodeQL 쿼리 작성 | [docs.github.com/code-security/codeql](https://docs.github.com/en/code-security) | CodeQL 커스텀 쿼리 |

### 보안 프레임워크 및 표준

| 제목 | URL | 설명 |
|------|-----|------|
| MITRE ATT&CK Framework | [attack.mitre.org](https://attack.mitre.org/) | 사이버 공격 기법 및 전술 프레임워크 |
| OWASP Top 10 | [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/) | 웹 애플리케이션 보안 위협 Top 10 |
| OWASP Input Validation Cheat Sheet | [cheatsheetseries.owasp.org/Input_Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | 입력값 검증 가이드 |
| OWASP SSRF Prevention | [cheatsheetseries.owasp.org/SSRF_Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | SSRF 방어 가이드 |
| OWASP File Upload Cheat Sheet | [cheatsheetseries.owasp.org/File_Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | 파일 업로드 보안 가이드 |
| OWASP Logging Cheat Sheet | [cheatsheetseries.owasp.org/Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) | 로깅 보안 가이드 |
| CWE (Common Weakness Enumeration) | [cwe.mitre.org](https://cwe.mitre.org/) | 소프트웨어 취약점 분류 |

### Terraform 모듈 및 예제

| 제목 | URL | 설명 |
|------|-----|------|
| AWS CloudFront Terraform 모듈 | [registry.terraform.io/terraform-aws-cloudfront](https://registry.terraform.io/browse/modules?provider=aws/terraform-aws-cloudfront) | CloudFront IaC 모듈 |
| AWS WAF Terraform 모듈 | [github.com/trussworks/terraform-aws-wafv2](https://github.com/trussworks/terraform-aws-wafv2) | WAF IaC 모듈 |
| WAF CloudFront 통합 예제 | [docs.aws.amazon.com/waf/developerguide](https://docs.aws.amazon.com/waf/latest/developerguide/) | AWS 샘플 코드 |
| WAF 자동화 예제 | [docs.aws.amazon.com/aws-waf-automation-terraform](https://docs.aws.amazon.com//aws-waf-automation-terraform-samples) | WAF 자동화 Terraform |

### 실습 환경 및 도구

| 제목 | URL | 설명 |
|------|-----|------|
| DVWA (Damn Vulnerable Web App) | [github.com/digininja/DVWA](https://github.com/digininja/DVWA) | 취약한 웹 앱 실습 환경 |
| OWASP WebGoat | [github.com/WebGoat/WebGoat](https://github.com/WebGoat/WebGoat) | 웹 보안 학습 플랫폼 |
| CodeQL Action | [docs.github.com/code-security/code-scanning](https://docs.github.com/en/code-security/code-scanning) | GitHub Actions CodeQL 통합 |
| CodeQL 예제 | [github.com/github/codeql](https://github.com/github/codeql) | CodeQL 쿼리 예제 |

### Python 보안 관련 문서

| 제목 | URL | 설명 |
|------|-----|------|
| Python urllib.parse | [docs.python.org/urllib.parse](https://docs.python.org/3/library/urllib.parse.html) | URL 파싱 라이브러리 |
| Python requests 문서 | [requests.readthedocs.io](https://requests.readthedocs.io/) | HTTP 라이브러리 |
| Validators 라이브러리 | [github.com/kvesteri/validators](https://github.com/kvesteri/validators) | Python 입력값 검증 |

### 한국 보안 가이드 및 규제

| 제목 | URL | 설명 |
|------|-----|------|
| KISA 보호나라 | [boho.or.kr](https://www.boho.or.kr/) | 한국인터넷진흥원 보안 가이드 |
| 금융보안원 (FSI) | [fsec.or.kr](https://www.fsec.or.kr/) | 금융권 보안 가이드 |
| ISMS-P 인증 기준 | [isms.kisa.or.kr](https://isms.kisa.or.kr/) | 정보보호 관리체계 |
| 개인정보보호법 | [privacy.go.kr](https://www.privacy.go.kr/) | 개인정보보호위원회 |
| 국가사이버안전센터 (NCSC) | [ncsc.go.kr](https://www.ncsc.go.kr/) | 국가 차원 위협 정보 |

### 추가 학습 자료

| 제목 | URL | 설명 |
|------|-----|------|
| AWS 보안 모범 사례 | [docs.aws.amazon.com/security](https://docs.aws.amazon.com/security/) | AWS 보안 베스트 프랙티스 |
| DevSecOps Manifesto | [devsecops.org](https://www.devsecops.org/) | DevSecOps 원칙 |
| NIST Cybersecurity Framework | [nist.gov/cyberframework](https://www.nist.gov/cyberframework) | 사이버보안 프레임워크 |

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| AWS WAF 보안 | WAF 규칙 설정, CloudFront 통합, DDoS 방어 | [수강하기](https://edu.2twodragon.com/courses/aws-waf) |
| GitHub DevSecOps | CodeQL, Dependabot, Secret Scanning, GHAS | [수강하기](https://edu.2twodragon.com/courses/github-devsecops) |
| AWS 클라우드 보안 | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| AWS WAF 네트워크 시나리오 | AWS WAF와 전체적인 네트워크 보안 구성 | [youtu.be/r84IuPv_4TI](https://youtu.be/r84IuPv_4TI) |

### 컨테이너 보안 관련 (7주차 예습)

| 제목 | URL | 설명 |
|------|-----|------|
| 초보를 위한 도커 안내서 | [subicura.com/docker-guide-for-beginners](https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html) | Docker 기초 가이드 |
| 쿠버네티스 시작하기 | [subicura.com/kubernetes-basic](https://subicura.com/2019/05/19/kubernetes-basic-1.html) | Kubernetes 입문 |

---

원본 포스트: [클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전](https://twodragon.tistory.com/707)

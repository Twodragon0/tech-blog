---
layout: post
title: "클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안"
date: 2025-05-23 01:07:48 +0900
categories: [security, devsecops]
tags: [AWS, CDN, Cloudflare, GitHub, SAST, WAF, 보안, 보안-아키텍처, 애플리케이션-보안, 코드-보안]
excerpt: "클라우드 시큐리티 과정 7기 6주차: AWS WAF 보안 강화(웹 ACL 규칙, IP 기반 접근 제어, Geo-blocking), Cloudflare 종합 보안(DDoS 보호, WAF, SSL/TLS 1.3, CDN, Bot Management), GitHub 보안 자동화(Dependabot, CodeQL, Secret Scanning), 실무 보안 실습(DVWA 활용)까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/684
image: /assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security.svg
image_alt: "Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security"
toc: true
---
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


<img src="{{ '/assets/images/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_and_github_Security_image.png' | relative_url }}" alt="Cloud Security Course 7Batch 6Week: Cloudflare and GitHub Security" loading="lazy" class="post-image">


## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 Application 보안 및 Cloudflare 및 GitHub 활용을 다루고자 합니다. 이 과정은 게더 타운에서 진행되며, 각 세션은 20분 강의 후 5분 휴식으로 구성되어 있습니다. 이러한 구성은 온라인 강의의 특성 상 눈의 피로를 줄이고, 멘티 분들의 집중력을 최대화하기 위함입니다. 여러분들과 함께 다양한 AWS 보안 모니터링 및 대응 관련 주제를 깊이 있게 다루어 보고자 합니다.

이 글에서는 클라우드 시큐리티 과정 7기 - 6주차 Cloudflare 및 GitHub 보안에 대해 실무 중심으로 상세히 다룹니다.## 1. 강의 일정 및 구성

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


컨테이너 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다:

```mermaid
graph TB
    subgraph SecurityLayers["Security Layers"]
        ImageScan["Image Scanning - Trivy, Snyk"]
        SecretMgmt["Secret Management - K8s Secrets, Vault"]
        NonRoot["Non-root User - runAsNonRoot"]
        ReadOnly["Read-only Filesystem - readOnlyRootFilesystem"]
        CapDrop["Capabilities Drop - capabilities.drop: ALL"]
        NetworkPolicy["Network Policies - Pod Isolation"]
    end
    
    App["Application Container"]
    
    ImageScan -> SecretMgmt
    SecretMgmt -> NonRoot
    NonRoot -> ReadOnly
    ReadOnly -> CapDrop
    CapDrop -> NetworkPolicy
    NetworkPolicy -> App
    
    style ImageScan fill:#e1f5ff
    style SecretMgmt fill:#e1f5ff
    style NonRoot fill:#e1f5ff
    style ReadOnly fill:#e1f5ff
    style CapDrop fill:#e1f5ff
    style NetworkPolicy fill:#e1f5ff
    style App fill:#fff4e1
```


> **⚠️ 보안 주의사항**
> 
> 최신 보안 업데이트를 지속적으로 확인하고 적용해야 합니다. 특히 BPF(Berkeley Packet Filter) 관련 취약점 점검 가이드를 참고하시기 바랍니다.
> 
> - **BPF 점검 가이드**: [KISA 보호나라&KrCERT/CC](https://www.krcert.or.kr/kr/bbs/view.do?searchCnd=&bbsId=B0000133&searchWrd=&menuNo=205020&pageIndex=1&categoryCode=&nttId=71754)

## 2. AWS WAF (Web Application Firewall)

### 2.1 AWS WAF 개요

AWS WAF는 웹 애플리케이션을 보호하는 데 중요한 도구입니다. 이 서비스는 SQL 인젝션, 크로스 사이트 스크립팅(XSS) 등 다양한 웹 기반 공격으로부터 보호하며, 사용자 정의 규칙을 설정하여 트래픽을 제어할 수 있습니다.

#### 주요 기능

- **SQL Injection 방어**: SQL 인젝션 공격 자동 탐지 및 차단
- **XSS 방어**: 크로스 사이트 스크립팅 공격 차단
- **Rate Limiting**: 트래픽 제한을 통한 DDoS 공격 완화
- **Geo-blocking**: 특정 지역의 트래픽 차단
- **Custom Rules**: 사용자 정의 규칙을 통한 세밀한 제어

### 2.2 AWS WAF 실습

AWS WAF는 [AWS WAF Workshop](https://sessin.github.io/awswafhol/)을 통해 실습할 수 있으며, DVWA(Damn Vulnerable Web Application)를 활용한 공격 및 방어 실습이 가능합니다.

#### 실습 환경 구성

> **참고**: DVWA 실습 환경 관련 내용은 [DVWA GitHub 저장소](https://github.com/digininja/DVWA) 및 [OWASP WebGoat](https://github.com/WebGoat/WebGoat)를 참조하세요.

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

## 3. Cloudflare

### 3.1 Cloudflare 개요

Cloudflare는 웹사이트의 성능과 보안을 강화하기 위한 다양한 기능을 제공합니다. 전 세계에 분산된 네트워크를 통해 DDoS 공격 방어, WAF, CDN 등 종합적인 보안 및 성능 최적화 서비스를 제공합니다.

### 3.2 주요 보안 기능

#### DDoS 보호
- 대규모 트래픽 공격을 자동으로 차단
- Layer 3/4 및 Layer 7 공격 방어
- 실시간 위협 탐지 및 대응

#### WAF (웹 애플리케이션 방화벽)
- SQL 인젝션, XSS 등 웹 공격을 방어
- 사용자 정의 규칙 설정
- OWASP Top 10 취약점 자동 차단

#### SSL/TLS 지원
- 데이터 암호화를 통해 안전한 통신 보장
- 자동 인증서 관리
- 최신 TLS 버전 지원

#### 안전한 DNS 서비스
- DNS 하이재킹을 방지하고 신속한 도메인 응답을 제공
- DNSSEC 지원
- Anycast 네트워크를 통한 고가용성

#### 봇 관리
- 악의적인 봇 트래픽을 감지하고 차단
- AI 기반 봇 탐지
- 정상적인 크롤러 허용

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

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요..yml...
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

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요. 설정
2. Code Scanning 통합
3. 보안 알림 설정
4. 취약점 대응 프로세스 구축

## 5. 2025년 Cloudflare 및 GitHub 보안 최신 동향

### 5.1 Cloudflare WAF 2025년 업데이트

2025년 Cloudflare는 WAF에 대한 중요한 보안 업데이트를 지속적으로 제공하고 있습니다:

#### 주요 CVE 대응
- **CVE-2025-55182/55183/55184**: React 원격 코드 실행 및 서버 측 함수 노출 취약점에 대한 긴급 패치
- **CVE-2025-64446**: FortiWeb 취약점에 대한 탐지 시그니처 강화
- **PHP Wrapper Injection**: 새로운 탐지 로직 추가

#### Bot Management 혁신
> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.과 Code Scanning을 통해 의존성 취약점 및 코드 보안 이슈를 자동으로 탐지하고 대응할 수 있으며, CI/CD 파이프라인에 통합하여 지속적인 보안 검사를 수행할 수 있습니다.

### 2025년 보안 트렌드

2025년에는 AI 기반 봇 탐지와 코드 보안 자동화가 핵심 트렌드로 자리잡았습니다:
- GitHub의 Secret Protection과 Code Security 분리로 더 세밀한 보안 제어 가능
- Cloudflare의 Bot Detection ID를 활용한 맞춤형 보안 정책 수립
- Copilot Autofix를 통한 취약점 수정 속도 3배 이상 향상

### 다음 단계

이 포스팅이 Application 보안 및 Cloudflare와 GitHub 활용에 도움이 되길 바랍니다. 추가적인 질문이나 도움이 필요하시면 언제든지 댓글로 남겨주세요.

올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.
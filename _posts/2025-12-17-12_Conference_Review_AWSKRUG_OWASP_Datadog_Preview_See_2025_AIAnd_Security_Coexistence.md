---
author: Twodragon
categories:
- cloud
comments: true
date: 2025-12-17 12:26:37 +0900
description: AWSKRUG, OWASP, Datadog 컨퍼런스를 통해 2025년 AI와 보안의 공존, AWS re:Invent 보안 발표,
  Zero Trust 표준화 등 최신 트렌드를 확인하세요.
excerpt: AWSKRUG, OWASP, Datadog 컨퍼런스로 보는 2025년 AI 보안 트렌드와 실무 적용 방안
image: /assets/images/2025-12-17-12_Conference_Review_AWSKRUG_OWASP_Datadog_Preview_See_2025_AIand_Security_Coexistence.svg
image_alt: 'December Conference Review: Previewing 2025 AI and Security Coexistence
  with AWSKRUG OWASP Datadog'
keywords:
- AWSKRUG
- OWASP
- Datadog
- AI
- Conference
- AWS보안
- 컨퍼런스후기
- AI보안
- Zero Trust
layout: post
original_url: https://twodragon.tistory.com/704
tags:
- AWSKRUG
- OWASP
- Datadog
- AI
- Conference
title: '[12월 컨퍼런스 회고] AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존'
toc: true
---

## 요약

- **핵심 요약**: AWSKRUG, OWASP, Datadog 컨퍼런스로 보는 2025년 AI 보안 트렌드와 실무 적용 방안
- **주요 주제**: [12월 컨퍼런스 회고] AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존
- **키워드**: AWSKRUG, OWASP, Datadog, AI, Conference

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">[12월 컨퍼런스 회고] AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWSKRUG</span>
      <span class="tag">OWASP</span>
      <span class="tag">Datadog</span>
      <span class="tag">AI</span>
      <span class="tag">Conference</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>2025년 보안 트렌드: AI 공격(93% 리더 예상), Shadow AI, Supply Chain 공격 급증</li>
      <li>AWS re:Invent 2025: Security Agent, GuardDuty Extended, IAM Policy Autopilot 발표</li>
      <li>Zero Trust 표준화 및 Post-quantum 암호화(Cloudflare 52% 적용) 현실화</li>
      <li>AWSKRUG, OWASP, Datadog 컨퍼런스별 주요 인사이트</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS, Datadog, OWASP, AI IDE Kiro</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 아키텍트, DevOps 엔지니어, 보안 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 1. Executive Summary: 2025년 클라우드 보안 패러다임의 전환

### 1.1 경영진을 위한 핵심 요약

| 구분 | 주요 내용 | 비즈니스 영향 | 권장 조치 |
|------|---------|------------|----------|
| **전략적 위험** | AI 기반 공격이 일상화 (93% 리더 예상) | 데이터 유출, 랜섬웨어 위험 증가 | AI 보안 정책 수립 및 투자 |
| **기술 트렌드** | Zero Trust가 업계 표준으로 정착 | 레거시 시스템의 보안 취약성 노출 | Zero Trust 아키텍처 마이그레이션 |
| **규제 대응** | Post-quantum 암호화 준비 필요 | 장기적 데이터 보안 위협 | 암호화 전환 로드맵 수립 |
| **운영 효율** | AI 기반 보안 자동화로 생산성 향상 | 인건비 절감, 대응 시간 단축 | 자동화 도구 도입 검토 |

### 1.2 3대 핵심 트렌드

**트렌드 1: AI의 양면성 - 공격과 방어의 도구**
- 공격: LLM 기반 피싱, AI 생성 악성코드, Shadow AI 위험
- 방어: AWS Security Agent, IAM Policy Autopilot 등 자동화 도구
- 전략: AI 사용 거버넌스 체계 구축이 필수

**트렌드 2: Supply Chain 보안의 중요성 급부상**
- npm Shai-Hulud 웜 등 공급망 공격 180% 증가
- SBOM(Software Bill of Materials) 구축이 표준화
- 오픈소스 의존성 관리가 핵심 보안 과제로 부상

**트렌드 3: Zero Trust에서 Post-quantum까지 아키텍처 대전환**
- Zero Trust 아키텍처가 선택이 아닌 필수로 전환
- Cloudflare 52% 트래픽이 Post-quantum 암호화 적용
- 하이브리드 암호화 방식으로 점진적 전환 필요

### 1.3 컨퍼런스 주요 발표 요약

| 컨퍼런스 | 일시 | 핵심 발표 | 전략적 시사점 |
|---------|------|---------|-------------|
| **AWS re:Invent 2025** | 2025.12 | Security Agent, GuardDuty Extended, IAM Policy Autopilot | AI 기반 보안 자동화가 실무 수준 도달 |
| **AWSKRUG Kiro Launch** | 2025.12 | AI IDE Kiro, Shift-Left Security | 개발 생산성과 보안 통합 가능 |
| **OWASP Seoul** | 2025.12 | LLM 공격 기법, Top 10 변화 예측 | AI 공격 대응 체계 필요 |
| **Datadog Security 101** | 2025.12 | 통합 보안 모니터링, SIEM/CSPM 융합 | 단일 플랫폼 보안 관리 가능 |

### 1.4 투자 우선순위 가이드

**즉시 실행 (1-3개월)**
- IAM 정책 최적화 (비용: 낮음, 효과: 높음)
- CI/CD 보안 스캔 통합 (비용: 중간, 효과: 높음)
- GuardDuty Extended 활성화 (비용: 중간, 효과: 높음)

**단기 계획 (3-6개월)**
- Zero Trust 아키텍처 구축 (비용: 높음, 효과: 매우 높음)
- 통합 보안 모니터링 (비용: 중간, 효과: 높음)
- AI 사용 정책 수립 (비용: 낮음, 효과: 중간)

**장기 전략 (6-12개월)**
- Post-quantum 암호화 마이그레이션 (비용: 높음, 효과: 장기적)
- SBOM 자동화 체계 구축 (비용: 중간, 효과: 중간)
- 보안 문화 및 교육 프로그램 (비용: 중간, 효과: 높음)

## 2. 서론

12월은 한 해를 마무리하는 시기이자, 내년의 기술 트렌드를 가장 먼저 접할 수 있는 달이기도 합니다. 이번 달에는 **AWSKRUG AI IDE Kiro Launch Party**, **OWASP Seoul Chapter 송년회**, 그리고 **Datadog Security 101 세미나**에 연달아 참석하며, 개발 생산성의 도구인 AI와 이를 지키는 보안 기술이 어떻게 융합되고 있는지 생생하게 느낄 수 있었습니다.

특히 주목할 점은 **AI가 보안의 양면성을 동시에 보여주고 있다**는 것입니다. 한편으로는 AI 기반 보안 자동화 도구들이 개발 생산성을 높이고 위협을 사전에 차단하는 데 기여하고 있지만, 다른 한편으로는 **AI를 활용한 공격 기법이 급증**하고 있으며, 조직 내 **Shadow AI** 사용으로 인한 새로운 보안 위협이 부상하고 있습니다.

본 포스팅에서는 이 세 컨퍼런스에서 공유된 인사이트를 바탕으로 **2025년 보안 트렌드**와 **실무 적용 방안**을 종합적으로 정리합니다. 특히 AWS re:Invent 2025에서 발표된 보안 서비스들과 각 컨퍼런스별 핵심 내용을 실무 중심으로 상세히 다룹니다.

<img src="{{ '/assets/images/2025-12-17-12_Conference_Review_AWSKRUG_OWASP_Datadog_Preview_See_2025_AIand_Security_Coexistence_image.png' | relative_url }}" alt="December Conference Review: Previewing 2025 AI and Security Coexistence with AWSKRUG OWASP Datadog" loading="lazy" class="post-image">

> **📌 핵심 요약**
> 
> - **93%의 보안 리더가 일일 AI 기반 공격을 예상**하고 있으며, AI 보안의 양면성이 주요 화두
> - **AWS re:Invent 2025**에서 Security Agent, GuardDuty Extended, IAM Policy Autopilot 등 AI 기반 보안 자동화 서비스 발표
> - **Zero Trust Architecture**가 업계 표준으로 정착하며, Post-quantum 암호화가 현실화 (Cloudflare 52% 적용)
> - **Supply Chain 공격**이 급증하며, npm Shai-Hulud 웜 등 의존성 관리의 중요성 강조

2025년 보안 트렌드는 AI와 보안의 공존이 핵심입니다.

## 3. Technology Trend Analysis: AI와 보안의 융합

### 3.1 클라우드 보안 패러다임의 근본적 변화

2025년 클라우드 보안은 **반응적(Reactive) 대응에서 예측적(Predictive) 방어**로 진화하고 있습니다. 이는 AI, Machine Learning, 실시간 위협 인텔리전스의 융합으로 가능해졌습니다.

...
> ```

yaml
> # GitHub Actions 예시 (간단한 구조)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조 -->
<!-- 전체 코드는 위 GitHub 링크 참조 -->

> **참고**: 전체 CI/CD 보안 파이프라인 설정은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions) 및 [CodeQL 문서](https://docs.github.com/en/code-security)를 참조하세요.

### 5.2 중장기 보안 로드맵

#### 중기 적용 (3-6개월)

| 항목 | 적용 방법 | 예상 효과 | 투자 규모 |
|------|---------|----------|----------|
| **Zero Trust 아키텍처 구축** | ZTNA 기반 접근 제어 체계 구축, 모든 리소스에 최소 권한 원칙 적용 | 공격 표면 축소, 보안 강화 | 높음 |
| **통합 보안 모니터링** | SIEM/CSPM 통합 플랫폼 구축 (Datadog, AWS Security Hub 등) | 보안 가시성 향상, 대응 시간 단축 | 중간 |
| **AI 사용 정책 수립** | 조직 내 AI 사용 정책 및 거버넌스 체계 구축 | Shadow AI 위험 감소 | 중간 |
| **보안 자동화** | AWS Security Agent 등 AI 기반 자동 대응 시스템 도입 | 대응 시간 단축, 인적 오류 감소 | 중간 |

#### 장기 적용 (6-12개월)

| 항목 | 적용 방법 | 예상 효과 | 투자 규모 |
|------|---------|----------|----------|
| **Post-quantum 암호화 마이그레이션** | 하이브리드 방식으로 Post-quantum 암호화 점진적 도입 | 양자 컴퓨팅 시대 대비 | 높음 |
| **SBOM 구축** | 모든 소프트웨어에 대한 SBOM 자동 생성 및 관리 | Supply Chain 공격 대응 | 중간 |
| **보안 문화 구축** | 개발자 보안 교육, 보안 챔피언 프로그램 운영 | 조직 전반 보안 인식 제고 | 중간 |
| **지속적인 보안 개선** | 정기적인 보안 감사, 위협 모델링 업데이트 | 보안 수준 지속적 향상 | 중간 |

### 5.3 보안 로드맵 우선순위 매트릭스

| 항목 | 긴급도 | 중요도 | 우선순위 | 예상 기간 |
|------|-------|-------|---------|----------|
| **IAM 정책 최적화** | 높음 | 높음 | 최우선 | 1-2주 |
| **위협 탐지 강화** | 높음 | 높음 | 최우선 | 2-4주 |
| **CI/CD 보안 통합** | 높음 | 높음 | 최우선 | 1-2개월 |
| **Zero Trust 구축** | 중간 | 높음 | 높음 | 3-6개월 |
| **통합 모니터링** | 중간 | 높음 | 높음 | 2-4개월 |
| **Post-quantum 암호화** | 낮음 | 중간 | 중간 | 6-12개월 |
| **SBOM 구축** | 중간 | 중간 | 중간 | 3-6개월 |

### 5.4 예산 및 리소스 계획

#### 예산 배분 예시

| 항목 | 예산 비율 | 주요 비용 항목 |
|------|---------|-------------|
| **도구 및 서비스** | 40% | AWS 보안 서비스, 모니터링 도구 구독 |
| **인력** | 35% | 보안 엔지니어, DevOps 엔지니어 |
| **교육 및 인증** | 15% | 보안 교육, 자격증 취득 |
| **컨설팅** | 10% | 외부 보안 감사, 컨설팅 |

> **💡 실무 팁**
> 
> 보안 로드맵을 효과적으로 실행하기 위해서는:
> - **단계적 접근**: 한 번에 모든 것을 적용하려 하지 말고 단계적으로 진행
> - **ROI 측정**: 각 보안 투자에 대한 효과 측정 및 보고
> - **지속적인 검토**: 분기별로 로드맵 검토 및 조정
> - **이해관계자 소통**: 경영진 및 개발팀과의 지속적인 소통

## 결론

이번 12월 컨퍼런스들을 통해 2025년은 **AI와 보안이 공존하며 상호작용하는 해**가 될 것임을 확인했습니다. 93%의 보안 리더가 예상하는 AI 공격, Supply Chain 공격의 급증, Zero Trust의 표준화, Post-quantum 암호화의 현실화까지 - 보안 환경은 그 어느 때보다 빠르게 변화하고 있습니다.

### 핵심 인사이트 요약

| 영역 | 주요 트렌드 | 실무 적용 포인트 |
|------|----------|----------------|
| **AI 보안** | AI 기반 공격 급증, Shadow AI 위험 | AI 사용 정책 수립, 모니터링 체계 구축 |
| **자동화** | AI 기반 보안 자동화 도구 확산 | AWS Security Agent, IAM Policy Autopilot 활용 |
| **Zero Trust** | 업계 표준으로 정착 | ZTNA 기반 접근 제어 체계 구축 |
| **암호화** | Post-quantum 암호화 현실화 | 하이브리드 방식으로 점진적 마이그레이션 |
| **Supply Chain** | 공급망 공격 정교화 | SBOM 구축, 의존성 스캔 자동화 |

### AWS re:Invent 2025 보안 서비스의 의미

AWS re:Invent 2025에서 발표된 **Security Agent**, **Security Hub GA**, **GuardDuty Extended Threat Detection**, **IAM Policy Autopilot**, **AgentCore Identity** 등은 이러한 변화에 대응하기 위한 AWS의 전략적 방향을 보여줍니다.

특히 주목할 점은 **AI를 활용한 보안 자동화**가 단순한 트렌드를 넘어 실무에서 즉시 활용 가능한 수준에 도달했다는 것입니다. 개발자와 보안 팀의 생산성을 높이면서도 보안을 강화할 수 있는 도구들이 실제로 제공되고 있습니다.

### 다음 단계

이러한 트렌드를 미리 파악하고 준비하는 것이 앞으로의 보안 전략에서 핵심이 될 것입니다. 다음 단계로는:

1. **즉시 적용**: IAM 정책 최적화, 위협 탐지 강화, CI/CD 보안 통합
2. **단기 계획**: Zero Trust 아키텍처 구축, 통합 보안 모니터링
3. **중장기 전략**: Post-quantum 암호화 마이그레이션, SBOM 구축, 보안 문화 구축

> **📌 핵심 메시지**
> 
> 2025년은 AI와 보안이 융합되는 해입니다. AI는 공격의 도구이자 동시에 방어의 도구가 되고 있으며, 이를 효과적으로 활용하는 조직이 보안 경쟁에서 우위를 점할 것입니다. 지금 바로 시작하는 것이 중요합니다.

---

## 9. 참고 자료 (Comprehensive References)

### 9.1 공식 문서 및 발표 자료

#### AWS 공식 문서
1. **AWS re:Invent 2025 Security Sessions**
   - Security Keynote: "The Future of Cloud Security in the AI Era"
   - URL: https://reinvent.awsevents.com/learn/security/
   - 핵심 내용: Security Agent, GuardDuty Extended, IAM Policy Autopilot 발표

2. **AWS Security Hub Documentation**
   - URL: https://docs.aws.amazon.com/securityhub/
   - 활용: 멀티 어카운트 보안 통합 관리 가이드

3. **AWS GuardDuty Extended Threat Detection**
   - URL: https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_extended.html
   - 활용: EKS Runtime Monitoring 설정 방법

4. **AWS IAM Policy Autopilot**
   - URL: https://docs.aws.amazon.com/iam/latest/UserGuide/policy-autopilot.html
   - 활용: 최소 권한 정책 자동 생성 실습

5. **AWS Well-Architected Framework - Security Pillar**
   - URL: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/
   - 활용: 보안 아키텍처 설계 원칙 및 모범 사례

#### OWASP 공식 자료
6. **OWASP Top 10 - 2025 Preview**
   - URL: https://owasp.org/www-project-top-ten/
   - 핵심 내용: AI 기반 공격 포함 예정

7. **OWASP AI Security and Privacy Guide**
   - URL: https://owasp.org/www-project-ai-security-and-privacy-guide/
   - 활용: LLM 공격 기법 및 방어 전략

8. **OWASP Software Component Verification Standard (SCVS)**
   - URL: https://owasp.org/www-project-software-component-verification-standard/
   - 활용: SBOM 구축 및 Supply Chain 보안

#### Datadog 공식 자료
9. **Datadog Security Monitoring Documentation**
   - URL: https://docs.datadoghq.com/security/
   - 활용: SIEM, CSPM, ASM 통합 설정 가이드

10. **Datadog Cloud Security Posture Management (CSPM)**
    - URL: https://docs.datadoghq.com/security/cspm/
    - 활용: 클라우드 설정 오류 자동 탐지

11. **Datadog Application Security Management (ASM)**
    - URL: https://docs.datadoghq.com/security/application_security/
    - 활용: 런타임 애플리케이션 보호

### 9.2 컨퍼런스 세션 및 발표 자료

#### AWSKRUG AI IDE Kiro Launch Party
12. **AWS Kiro IDE 소개 및 데모**
    - 발표자: AWS Korea Solution Architect Team
    - 핵심 내용: AI 기반 코드 리뷰, 보안 취약점 자동 탐지
    - 슬라이드: (컨퍼런스 참석자 공유 자료)

13. **Shift-Left Security in Practice**
    - 발표자: DevSecOps 실무자 패널
    - 핵심 내용: CI/CD 파이프라인 보안 통합 사례

#### OWASP Seoul Chapter 송년회
14. **2025년 웹 애플리케이션 보안 트렌드**
    - 발표자: OWASP Korea Chapter Lead
    - 핵심 내용: LLM 기반 피싱, AI 공격 진화

15. **Supply Chain 공격 사례 분석: npm Shai-Hulud**
    - 발표자: 보안 연구원
    - 핵심 내용: 자가 복제 웜, 의존성 관리 중요성

#### Datadog Security 101 세미나
16. **통합 보안 모니터링 아키텍처**
    - 발표자: Datadog Solutions Engineer
    - 핵심 내용: SIEM/CSPM/ASM 통합, 상관관계 분석

17. **실전 보안 자동화 워크플로우**
    - 발표자: Datadog Customer Success Team
    - 핵심 내용: 자동 대응 플레이북, Lambda 통합

### 9.3 산업 리포트 및 통계

18. **Gartner Magic Quadrant for SIEM (2025)**
    - URL: https://www.gartner.com/en/documents/magic-quadrant-siem
    - 핵심 내용: SIEM 시장 동향, 주요 벤더 평가

19. **Forrester Wave: Cloud Security Posture Management (2025)**
    - URL: https://www.forrester.com/wave/cloud-security-posture-management
    - 핵심 내용: CSPM 시장 분석, 구매 가이드

20. **Cybersecurity Ventures: 2025 Cybercrime Report**
    - URL: https://cybersecurityventures.com/cybercrime-report/
    - 핵심 통계: 93% 보안 리더가 AI 공격 예상

21. **Verizon Data Breach Investigations Report (DBIR) 2025**
    - URL: https://www.verizon.com/business/resources/reports/dbir/
    - 핵심 내용: 데이터 침해 사고 분석, 공격 벡터 통계

22. **Cloudflare Post-Quantum Cryptography Report**
    - URL: https://blog.cloudflare.com/post-quantum-cryptography-report/
    - 핵심 통계: 전체 트래픽의 52% Post-quantum 암호화 적용

### 9.4 기술 표준 및 프레임워크

23. **NIST Cybersecurity Framework 2.0**
    - URL: https://www.nist.gov/cyberframework
    - 활용: 보안 프레임워크 구축 기준

24. **NIST Post-Quantum Cryptography Standardization**
    - URL: https://csrc.nist.gov/projects/post-quantum-cryptography
    - 활용: Post-quantum 알고리즘 선택 가이드

25. **Zero Trust Architecture - NIST SP 800-207**
    - URL: https://csrc.nist.gov/publications/detail/sp/800-207/final
    - 활용: Zero Trust 아키텍처 설계 원칙

26. **CIS AWS Foundations Benchmark**
    - URL: https://www.cisecurity.org/benchmark/amazon_web_services
    - 활용: AWS 보안 설정 체크리스트

27. **ISO/IEC 27001:2022 Information Security Management**
    - URL: https://www.iso.org/standard/27001
    - 활용: 정보보안 관리 체계 구축

### 9.5 오픈소스 도구 및 프로젝트

28. **Trivy - Container Vulnerability Scanner**
    - GitHub: https://github.com/aquasecurity/trivy
    - 활용: 컨테이너 이미지 취약점 스캔

29. **Syft - SBOM Generation Tool**
    - GitHub: https://github.com/anchore/syft
    - 활용: 소프트웨어 Bill of Materials 자동 생성

30. **TruffleHog - Secret Scanner**
    - GitHub: https://github.com/trufflesecurity/trufflehog
    - 활용: Git 히스토리에서 시크릿 탐지

31. **Checkov - IaC Security Scanner**
    - GitHub: https://github.com/bridgecrewio/checkov
    - 활용: Terraform, CloudFormation 보안 스캔

32. **OWASP ZAP - Web Application Security Scanner**
    - URL: https://www.zaproxy.org/
    - 활용: DAST (동적 애플리케이션 보안 테스트)

33. **Falco - Cloud Native Runtime Security**
    - URL: https://falco.org/
    - 활용: Kubernetes 런타임 위협 탐지

### 9.6 한국 보안 커뮤니티 및 자료

34. **KISA (한국인터넷진흥원) 보안공지**
    - URL: https://www.kisa.or.kr/
    - 활용: 국내 보안 동향, 취약점 공지

35. **AWSKRUG (AWS Korea User Group)**
    - URL: https://www.facebook.com/groups/awskrug
    - 활용: AWS 한국 사용자 커뮤니티, 정기 세미나

36. **GDGKR (Google Developer Group Korea)**
    - URL: https://gdg.community.dev/
    - 활용: 클라우드 및 보안 기술 공유

37. **한국정보보호학회 (KIISC)**
    - URL: https://www.kiisc.or.kr/
    - 활용: 학술 연구, 보안 컨퍼런스

38. **개인정보보호위원회 - 개인정보보호법**
    - URL: https://www.pipc.go.kr/
    - 활용: 개인정보보호 규정 및 가이드라인

### 9.7 교육 및 자격증

39. **AWS Certified Security - Specialty**
    - URL: https://aws.amazon.com/certification/certified-security-specialty/
    - 활용: AWS 보안 전문가 자격증

40. **Certified Information Systems Security Professional (CISSP)**
    - URL: https://www.isc2.org/Certifications/CISSP
    - 활용: 국제 정보보안 전문가 자격증

41. **Certified Kubernetes Security Specialist (CKS)**
    - URL: https://www.cncf.io/certification/cks/
    - 활용: Kubernetes 보안 전문가 자격증

42. **OWASP Top 10 Training**
    - URL: https://owasp.org/www-project-top-ten/
    - 활용: 웹 애플리케이션 보안 교육

### 9.8 블로그 및 뉴스 사이트

43. **AWS Security Blog**
    - URL: https://aws.amazon.com/blogs/security/
    - 활용: AWS 보안 최신 동향, 모범 사례

44. **Krebs on Security**
    - URL: https://krebsonsecurity.com/
    - 활용: 보안 사고 분석, 뉴스

45. **The Hacker News**
    - URL: https://thehackernews.com/
    - 활용: 최신 보안 뉴스, 취약점 공지

46. **Dark Reading**
    - URL: https://www.darkreading.com/
    - 활용: 기업 보안 전략, 트렌드 분석

47. **SANS Internet Storm Center**
    - URL: https://isc.sans.edu/
    - 활용: 위협 인텔리전스, 실시간 보안 동향

### 9.9 실습 환경 및 랩

48. **AWS Workshop Studio**
    - URL: https://workshops.aws/
    - 활용: AWS 보안 서비스 실습 (무료)

49. **Datadog Learning Center**
    - URL: https://learn.datadoghq.com/
    - 활용: Datadog 플랫폼 실습

50. **TryHackMe - Cloud Security Rooms**
    - URL: https://tryhackme.com/
    - 활용: 클라우드 보안 실습 (게이미피케이션)

51. **OWASP WebGoat**
    - URL: https://owasp.org/www-project-webgoat/
    - 활용: 웹 애플리케이션 보안 실습 환경

### 9.10 관련 GitHub 저장소

52. **AWS Security Reference Architecture**
    - GitHub: https://github.com/aws-samples/aws-security-reference-architecture-examples
    - 활용: AWS 보안 아키텍처 참고 구현

53. **Awesome Cloud Security**
    - GitHub: https://github.com/4ndersonLin/awesome-cloud-security
    - 활용: 클라우드 보안 리소스 큐레이션

54. **Kubernetes Security - Best Practice Guide**
    - GitHub: https://github.com/kabachook/k8s-security
    - 활용: Kubernetes 보안 가이드

55. **SecLists - Security Tester's Companion**
    - GitHub: https://github.com/danielmiessler/SecLists
    - 활용: 보안 테스트 페이로드 모음

### 9.11 팟캐스트 및 비디오

56. **AWS re:Invent YouTube Channel**
    - URL: https://www.youtube.com/@AWSEventsChannel
    - 활용: re:Invent 세션 다시보기

57. **Darknet Diaries Podcast**
    - URL: https://darknetdiaries.com/
    - 활용: 보안 사건 스토리텔링

58. **Kubernetes Security Podcast**
    - URL: https://kubernetessecuritypodcast.com/
    - 활용: 컨테이너 보안 최신 동향

### 9.12 추가 참고 도구

| 도구 | 용도 | URL |
|------|------|-----|
| **ScoutSuite** | 멀티 클라우드 보안 감사 | https://github.com/nccgroup/ScoutSuite |
| **Prowler** | AWS 보안 감사 도구 | https://github.com/prowler-cloud/prowler |
| **CloudMapper** | AWS 환경 시각화 | https://github.com/duo-labs/cloudmapper |
| **Snyk** | 의존성 취약점 스캔 (상용) | https://snyk.io/ |
| **GitGuardian** | 시크릿 탐지 (상용) | https://www.gitguardian.com/ |

### 9.13 컨퍼런스 및 이벤트 일정

| 행사명 | 일정 | 장소 | 주요 내용 |
|-------|------|------|---------|
| **AWS Summit Seoul 2025** | 2025년 5월 예정 | 코엑스 | re:Invent 핵심 내용 국내 발표 |
| **AWSKRUG re:Invent recap** | 2025년 1월 | 온/오프라인 | re:Invent 2024 심화 세션 |
| **OWASP Korea Day** | 2025년 상반기 | 미정 | 웹 애플리케이션 보안 트렌드 |
| **Black Hat Asia** | 2025년 3월 | 싱가포르 | 글로벌 보안 컨퍼런스 |
| **RSA Conference** | 2025년 4월 | 샌프란시스코 | 최대 규모 보안 컨퍼런스 |

---

**원본 포스트**: [12월 컨퍼런스 회고: AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존](https://twodragon.tistory.com/704)

**작성일**: 2025-12-17
**최종 업데이트**: 2025-12-17
**카테고리**: Cloud Security, DevSecOps, Conference Review
**태그**: AWSKRUG, OWASP, Datadog, AI Security, Zero Trust, Post-quantum, Supply Chain Security

<!-- quality-upgrade:v1 -->
## 경영진 요약
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | 중간 | 높음 | P1 |
| 구성 오류/권한 | 중간 | 높음 | P1 |
| 탐지/가시성 공백 | 낮음 | 중간 | P2 |

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
![포스트 시각 자료](/assets/images/2025-12-17-12_Conference_Review_AWSKRUG_OWASP_Datadog_Preview_See_2025_AIand_Security_Coexistence.svg)


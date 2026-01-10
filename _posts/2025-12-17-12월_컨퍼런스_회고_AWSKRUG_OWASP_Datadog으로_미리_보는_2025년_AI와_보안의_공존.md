---
layout: post
title: "[12월 컨퍼런스 회고] AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존"
date: 2025-12-17 12:26:37 +0900
categories: cloud
tags: [AWSKRUG, OWASP, Datadog, AI, Conference]
excerpt: "12월 컨퍼런스 회고: AWSKRUG AI IDE Kiro Launch Party, OWASP Seoul Chapter 송년회, Datadog Security 101 세미나 참석 후기. 2025년 보안 트렌드(AI 공격 93% 리더 예상, Shadow AI, Supply Chain 공격), AWS re:Invent 2025 보안 발표(Security Agent, GuardDuty Extended, IAM Policy Autopilot), Zero Trust 표준화, Post-quantum 암호화(Cloudflare 52% 적용) 현실화까지 정리."
comments: true
original_url: https://twodragon.tistory.com/704
image: /assets/images/2025-12-17-12월_컨퍼런스_회고_AWSKRUG_OWASP_Datadog으로_미리_보는_2025년_AI와_보안의_공존.svg
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


## 서론

12월은 한 해를 마무리하는 시기이자, 내년의 기술 트렌드를 가장 먼저 접할 수 있는 달이기도 합니다. 이번 달에는 AWSKRUG AI IDE Kiro Launch Party, OWASP Seoul Chapter 송년회, 그리고 Datadog Security 101 세미나에 연달아 참석하며, 개발 생산성의 도구인 AI와 이를 지키는 보안 기술이 어떻게 융합되고 있는지 생생하게 느낄 수 있었습니다. 본 포스팅에서는 이 행사들에서..

이 글에서는 [12월 컨퍼런스 회고] AWSKRUG, OWASP, Datadog으로 미리 보는 2025년: AI와 보안의 공존에 대해 실무 중심으로 상세히 다룹니다.


<img src="{{ '/assets/images/2025-12-17-12월_컨퍼런스_회고_AWSKRUG_OWASP_Datadog으로_미리_보는_2025년_AI와_보안의_공존_image.png' | relative_url }}" alt="포스트 이미지" loading="lazy" class="post-image">
*그림: 포스트 이미지*


## 1. 개요

### 1.1 배경 및 필요성

12월은 한 해를 마무리하는 시기이자, 내년의 기술 트렌드를 가장 먼저 접할 수 있는 달이기도 합니다. 이번 달에는 AWSKRUG AI IDE Kiro Launch Party, OWASP Seoul Chapter 송년회, 그리고 Datadog Security 101 세미나에 연달아 참석하며, 개발 생산성의 도구인 AI와 이를 지키는 보안 기술이 어떻게 융합되고 있는지 생생하게 느낄 수 있었습니다. 본 포스팅에서는 이 행사들에서.....

### 1.2 주요 개념

이 가이드에서 다루는 주요 개념:

- **보안**: 안전한 구성 및 접근 제어
- **효율성**: 최적화된 설정 및 운영
- **모범 사례**: 검증된 방법론 적용

## 2. 2025년 보안 트렌드: 컨퍼런스에서 본 미래

### 2.1 AI 보안의 양면성

컨퍼런스들을 관통하는 가장 큰 화두는 **AI 보안**이었습니다. 최신 통계에 따르면 **93%의 보안 리더가 일일 AI 기반 공격을 예상**하고 있습니다. AI는 방어의 도구이자 동시에 공격의 무기가 되고 있습니다.

특히 주목할 점은 **Shadow AI**의 위험성입니다. 조직의 승인 없이 사용되는 AI 시스템들이 새로운 보안 위협으로 부상하고 있으며, 이를 관리하기 위한 거버넌스 체계 구축이 시급합니다.

### 2.2 Supply Chain 공격의 진화

npm **Shai-Hulud** 웜 등 공급망 공격이 급증하고 있습니다. 오픈소스 생태계를 노리는 공격이 더욱 정교해지면서, 의존성 관리와 SBOM(Software Bill of Materials) 구축의 중요성이 강조되었습니다.

### 2.3 Zero Trust Architecture 정착

**ZTNA(Zero Trust Network Access)**가 업계 표준으로 정착하면서, "신뢰하지 않고 항상 검증한다"는 원칙이 모든 보안 아키텍처의 기본이 되고 있습니다.

### 2.4 Post-quantum 암호화 준비

양자 컴퓨팅 시대를 대비한 **Post-quantum 암호화**가 현실화되고 있습니다. Cloudflare는 이미 **전체 트래픽의 52%를 Post-quantum 암호화로 보호**하고 있다고 발표했습니다.

## 3. AWS re:Invent 2025 보안 서비스 발표

### 3.1 AI 기반 보안 자동화

AWS는 re:Invent 2025에서 보안 분야의 혁신적인 발표들을 선보였습니다:

- **AWS Security Agent**: AI 기반 자동 위협 대응 에이전트로, 실시간 보안 이벤트 분석 및 자동 대응 수행
- **Security Hub GA**: 통합 보안 관리 허브의 정식 출시로 멀티 어카운트 보안 통합 관리 강화
- **GuardDuty Extended Threat Detection**: 확장된 위협 탐지 기능으로 더욱 정교한 공격 패턴 식별

### 3.2 IAM 및 접근 제어 혁신

- **IAM Policy Autopilot**: AI가 최소 권한 원칙에 기반하여 IAM 정책을 자동 생성 및 최적화
- **AgentCore Identity**: AI 에이전트를 위한 전용 신원 관리 시스템으로, 에이전트 기반 워크로드의 보안 강화

## 4. 컨퍼런스별 주요 인사이트

### 4.1 AWSKRUG AI IDE Kiro Launch Party

AWS Kiro IDE는 AI 기반 개발 생산성 도구로, 보안 코드 리뷰와 취약점 자동 탐지 기능이 통합되어 있습니다. 개발 단계에서부터 보안을 고려하는 **Shift-Left Security**의 실현을 보여주었습니다.

### 4.2 OWASP Seoul Chapter 송년회

OWASP에서는 2025년 웹 애플리케이션 보안 트렌드와 함께 AI 기반 공격 기법의 진화에 대해 다루었습니다. 특히 LLM(Large Language Model)을 활용한 피싱 공격과 사회공학 기법의 고도화가 논의되었습니다.

### 4.3 Datadog Security 101 세미나

Datadog은 클라우드 네이티브 환경에서의 통합 보안 모니터링 방법론을 소개했습니다. SIEM, CSPM, 애플리케이션 보안을 단일 플랫폼에서 관리하는 접근법이 인상적이었습니다.

## 5. 실무 적용 방안

### 5.1 즉시 적용 가능한 보안 강화 방안

- **최소 권한 원칙**: AWS IAM Policy Autopilot 활용 검토
- **정기적인 보안 점검**: GuardDuty Extended Threat Detection 도입
- **자동화된 보안 스캔**: CI/CD 파이프라인에 보안 스캔 통합

### 5.2 중장기 보안 로드맵

- **Zero Trust 아키텍처**: ZTNA 기반 접근 제어 체계 구축
- **Post-quantum 암호화**: 암호화 알고리즘 마이그레이션 계획 수립
- **Shadow AI 거버넌스**: 조직 내 AI 사용 정책 및 모니터링 체계 수립

## 결론

이번 12월 컨퍼런스들을 통해 2025년은 **AI와 보안이 공존하며 상호작용하는 해**가 될 것임을 확인했습니다. 93%의 보안 리더가 예상하는 AI 공격, Supply Chain 공격의 급증, Zero Trust의 표준화, Post-quantum 암호화의 현실화까지 - 보안 환경은 그 어느 때보다 빠르게 변화하고 있습니다.

AWS re:Invent 2025에서 발표된 Security Agent, Security Hub GA, GuardDuty Extended Threat Detection, IAM Policy Autopilot, AgentCore Identity 등은 이러한 변화에 대응하기 위한 AWS의 전략적 방향을 보여줍니다. 이러한 트렌드를 미리 파악하고 준비하는 것이 앞으로의 보안 전략에서 핵심이 될 것입니다.
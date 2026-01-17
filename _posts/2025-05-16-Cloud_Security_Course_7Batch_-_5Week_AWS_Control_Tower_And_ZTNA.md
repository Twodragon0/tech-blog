---
layout: post
title: "클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA"
date: 2025-05-16 00:53:10 +0900
categories: [cloud]
tags: [AWS, Control-Tower, ZTNA, Zero-Trust]
excerpt: "클라우드 시큐리티 과정 7기 5주차: AWS Control Tower 멀티 계정 관리(Landing Zone 자동 설정, Guardrails 정책 적용 필수/권장/선택, 계정 팩토리 자동 계정 생성, Organizations 및 SCP 활용, 2025년 업데이트 계정 마이그레이션 개선 standalone 분리 불필요), ZTNA(Zero Trust Network Access) 개념 및 AWS 구현 방법(PrivateLink, VPC Endpoint, Security Group 최소 권한), 클라우드 환경 제로 트러스트 보안 모델 적용, 2025년 AWS 거버넌스 업데이트(Organizations 계정 마이그레이션 개선, Control Tower Guardrails 확장, SCP 정책 자동화), 실무 적용(멀티 계정 아키텍처 설계, 거버넌스 정책 자동화, 제로 트러스트 네트워크 구성)까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/683
image: /assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA.svg
image_alt: "Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA"
toc: true
certifications: [aws-saa]
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA</span>
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
      <span class="tag">ZTNA</span>
      <span class="tag">Zero-Trust</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AWS Control Tower 멀티 계정 관리</strong>: Landing Zone 자동 설정, Guardrails 정책 적용(필수/권장/선택), 계정 팩토리(자동 계정 생성), Organizations 및 SCP 활용, 2025년 업데이트(계정 마이그레이션 개선, standalone 분리 불필요)</li>
      <li><strong>ZTNA(Zero Trust Network Access)</strong>: Zero Trust 개념("절대 신뢰하지 말고, 항상 검증하라"), AWS 구현 방법(PrivateLink, VPC Endpoint, Security Group 최소 권한), 클라우드 환경 제로 트러스트 보안 모델 적용</li>
      <li><strong>2025년 AWS 거버넌스 업데이트</strong>: Organizations 계정 마이그레이션 개선(조직 간 직접 이동, 다운타임 최소화), Control Tower Guardrails 확장, SCP 정책 자동화</li>
      <li><strong>실무 적용</strong>: 멀티 계정 아키텍처 설계, 거버넌스 정책 자동화, 제로 트러스트 네트워크 구성, 보안 및 컴플라이언스 통합 관리</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS Control Tower, ZTNA, Zero Trust</span>
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

## 서론

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 AWS 취약점 점검 및 ISMS 대응 가이드에 관련된 내용을 다루고자 합니다. 이 과정은 게더 타운에서 진행되며, 각 세션은 20분 강의 후 5분 휴식으로 구성되어 있습니다. 이러한 구성은 온라인 강의의 특성 상 눈의 피로를 줄이고, 멘티 분들의 집중력을 최대화하기 위함입니다. 여러분들과 함께 다양한 AWS Control Tower 및 ZTNA 관련 주..

이 글에서는 클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA에 대해 실무 중심으로 상세히 다룹니다.

<img src="{{ '/assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA_image.jpg' | relative_url }}" alt="Cloud Security Course 7Batch 5Week: AWS Control Tower and ZTNA" loading="lazy" class="post-image">

<figure>
<img src="{{ '/assets/images/diagrams/diagram_zero_trust.png' | relative_url }}" alt="Zero Trust Security Architecture" loading="lazy" class="post-image">
<figcaption>Zero Trust 보안 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

컨테이너 보안은 DevSecOps 사이클을 통해 코드로 관리됩니다:

<img src="{{ '/assets/images/diagrams/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA_mermaid_chart_1.png' | relative_url }}" alt="mermaid_chart_1" loading="lazy" class="post-image">## 1. 개요

### 1.1 배경 및 필요성

안녕하세요, Twodragon입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 AWS 취약점 점검 및 ISMS 대응 가이드에 관련된 내용을 다루고자 합니다. 이 과정은 게더 타운에서 진행되며, 각 세션은 20분 강의 후 5분 휴식으로 구성되어 있습니다. 이러한 구성은 온라인 강의의 특성 상 눈의 피로를 줄이고, 멘티 분들의 집중력을 최대화하기 위함입니다. 여러분들과 함께 다양한 AWS Control Tower 및 ZTNA 관련 주.....

## 2. 핵심 내용

### 2.1 기본 설정

기본 설정을 시작하기 전에 다음 사항을 확인해야 합니다:

1. **요구사항 분석**: 필요한 기능 및 성능 요구사항 파악
2. **환경 준비**: 필요한 도구 및 리소스 준비
3. **보안 정책**: 보안 정책 및 규정 준수 사항 확인

### 2.2 단계별 구현

#### 단계 1: 초기 설정

초기 설정 단계에서는 기본 구성을 수행합니다.

```bash
# 예시 명령어
# 실제 설정에 맞게 수정 필요
```

#### 단계 2: 보안 구성

컨테이너 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다:

<img src="{{ '/assets/images/diagrams/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA_mermaid_chart_2.png' | relative_url }}" alt="mermaid_chart_2" loading="lazy" class="post-image">

보안 설정을 구성합니다:

- 접근 제어 설정
- 암호화 구성
- 모니터링 활성화

## 2. 2025년 AWS 거버넌스 업데이트

2025년에 발표된 AWS 거버넌스 관련 주요 업데이트를 정리합니다.

### 2.1 AWS Organizations 계정 마이그레이션 개선

기존에는 AWS 계정을 다른 조직으로 이동하려면 먼저 standalone 계정으로 분리한 후 다시 새 조직에 가입해야 했습니다. **2025년 업데이트로 이제 계정을 standalone으로 분리하지 않고도 조직 간 직접 이동이 가능**해졌습니다.

**주요 이점:**
- 계정 이동 과정 단순화
- 다운타임 최소화
- M&A 또는 조직 재구성 시 효율성 향상

### 2.2 AgentCore Identity - AI 에이전트 접근 제어

AI/ML 워크로드가 증가함에 따라 AWS는 **AgentCore Identity**를 도입하여 AI 에이전트에 대한 세밀한 접근 제어를 제공합니다.

**주요 기능:**
- AI 에이전트별 IAM 역할 및 정책 할당
- 에이전트 행위 감사 및 추적
- 최소 권한 원칙을 AI 워크로드에 적용
- Control Tower와 통합하여 멀티 계정 환경에서 AI 거버넌스 관리

### 2.3 IAM Policy Autopilot

**IAM Policy Autopilot**은 오픈소스 도구로, 애플리케이션 코드를 분석하여 IAM 정책을 자동으로 생성합니다.

**동작 방식:**
1. 애플리케이션 소스 코드 분석
2. AWS SDK 호출 패턴 식별
3. 필요한 최소 권한 IAM 정책 자동 생성
4. 기존 정책과의 차이 분석 및 권장 사항 제공

**사용 예시:**
```bash
# IAM Policy Autopilot 실행
iam-policy-autopilot analyze --source ./my-app --output policy.json
```

### 2.4 보안 모니터링 강화

#### AWS Security Hub GA

AWS Security Hub가 GA(General Availability)로 출시되어 **멀티 계정 보안 현황을 통합 관리**할 수 있게 되었습니다.

**주요 기능:**
- Control Tower와 자동 통합
- 모든 멤버 계정의 보안 상태 중앙 집중 관리
- 자동화된 보안 점수 산정
- 규정 준수 상태 대시보드

#### GuardDuty Extended Threat Detection

GuardDuty가 **Extended Threat Detection** 기능을 추가하여 EC2 및 ECS 환경에서의 위협 시퀀스를 탐지합니다.

**탐지 가능한 위협:**
- 다단계 공격 시퀀스 식별
- EC2 인스턴스 내 악성 행위 패턴
- ECS 컨테이너 런타임 위협
- 내부자 위협 및 측면 이동 탐지

### 2.5 Control Tower 업데이트 적용 권장 사항

1. **Organizations 계정 이동 기능 활용**: 기존 계정 구조 재편 시 새로운 직접 이동 기능 사용
2. **AI 워크로드 거버넌스**: AgentCore Identity를 통해 AI 에이전트에 대한 접근 제어 정책 수립
3. **IAM 정책 자동화**: IAM Policy Autopilot으로 과도한 권한을 가진 정책 식별 및 최적화
4. **Security Hub 통합**: 멀티 계정 보안 현황을 단일 대시보드에서 모니터링
5. **GuardDuty 확장 기능 활성화**: EC2/ECS 환경에서의 고급 위협 탐지 활성화

## 결론

클라우드 시큐리티 과정 7기 - 5주차 AWS Control Tower 및 ZTNA에 대해 다루었습니다. 2025년에 발표된 AWS 거버넌스 업데이트를 통해 더욱 효율적인 멀티 계정 관리와 강화된 보안 모니터링이 가능해졌습니다. 올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.
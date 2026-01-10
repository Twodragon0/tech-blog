---
layout: post
title: "클라우드 시큐리티 8기 OT 안내: DevSecOps부터 FinOps까지, 실무형 인재로 도약하라!"
date: 2025-11-21 18:28:12 +0900
categories: devsecops
tags: [Cloud-Security, DevSecOps, FinOps, Course]
excerpt: "클라우드 시큐리티 8기 OT 안내: 9주 커리큘럼 상세(1주차 인프라 본질/2025 보안 트렌드, 2주차 AWS 보안 아키텍처 VPC/IAM/S3/GuardDuty, 3주차 FinOps/ISMS-P, 4주차 통합 보안 취약점 점검, 5주차 Control Tower/Datadog SIEM/Cloudflare, 6주차 이후 DevSecOps 심화), 2025년 보안 트렌드 반영(AI 보안 93% 리더 일일 공격 예상, Shadow AI, Supply Chain 공격, Zero Trust, Post-quantum 암호화 Cloudflare 52%), AWS re:Invent 2025 발표 반영(Security Agent, GuardDuty Extended, IAM Policy Autopilot), 효율적 학습 루틴(20분 강의+5분 휴식), 대체 불가능한 클라우드 보안 전문가로 성장까지 정리."
comments: true
original_url: https://twodragon.tistory.com/700
image: /assets/images/2025-11-21-Cloud_Security_8Batch_OT_Guide_DevSecOpsFrom_FinOpsTo_Practical_Talent_Leap.svg
---
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 8기 OT 안내: DevSecOps부터 FinOps까지, 실무형 인재로 도약하라!</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag devops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Cloud-Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">FinOps</span>
      <span class="tag">Course</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>9주 커리큘럼 상세</strong>: 1주차(인프라 본질, 2025 보안 트렌드), 2주차(AWS 보안 아키텍처 VPC/IAM/S3/GuardDuty), 3주차(AWS FinOps, ISMS-P), 4주차(통합 보안 취약점 점검), 5주차(AWS Control Tower, Datadog SIEM, Cloudflare), 6주차 이후(DevSecOps 심화, CI/CD/Kubernetes 보안)</li>
      <li><strong>2025년 보안 트렌드 반영</strong>: AI 보안 양면성(93% 리더 일일 AI 공격 예상), Shadow AI 위협, Supply Chain 공격 급증, Zero Trust 표준화, Post-quantum 암호화(Cloudflare 52% 적용), AWS re:Invent 2025 발표 반영(Security Agent, GuardDuty Extended, IAM Policy Autopilot)</li>
      <li><strong>학습 방식</strong>: 효율적 학습 루틴(20분 강의 + 5분 휴식, 뇌과학 기반 최적화), 실무 중심 교육, 상호작용형 학습 환경, 실무 고민 공유 및 Q&A</li>
      <li><strong>기대 효과</strong>: DevSecOps/FinOps 실무 역량 강화, 대체 불가능한 클라우드 보안 전문가로 성장, 실무 문제 해결 능력 향상, 클라우드 보안 아키텍처 설계 능력, 비용 최적화 역량 확보</li>
      <li><strong>주요 학습 영역</strong>: DevSecOps 영역(보안 통합 개발, 컨테이너 보안, 코드 보안, 인프라 보안), FinOps 영역(비용 최적화, 리소스 태깅, 거버넌스, 예산 관리), 클라우드 보안 영역(네트워크 보안, 접근 제어, 위협 탐지, 데이터 보호)</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS, DevSecOps, FinOps, VPC, IAM, GuardDuty, Control Tower, Datadog, Cloudflare, Docker, Kubernetes</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">DevSecOps 엔지니어, 보안 엔지니어, 클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>


## 서론

안녕하세요, Twodragon입니다. 클라우드 시큐리티 과정 8기가 곧 시작됩니다! 

클라우드 환경이 확산되면서 보안과 비용 최적화의 중요성이 더욱 부각되고 있습니다. DevSecOps와 FinOps는 현대 클라우드 운영에서 필수적인 역량으로, 이번 과정을 통해 실무에 바로 적용 가능한 전문 지식을 습득할 수 있습니다.

이번 8기는 **'20분 강의 + 5분 휴식'**이라는 뇌과학적으로 가장 효율적인 학습 루틴으로 진행됩니다. 단순한 이론 주입식 교육이 아닌, 실무의 고민을 함께 나누는 시간이 될 것입니다.

<img src="{{ '/assets/images/2025-11-21-Cloud_Security_8Batch_OT_Guide_DevSecOpsFrom_FinOpsTo_Practical_Talent_Leap_image.png' | relative_url }}" alt="포스트 이미지" loading="lazy" class="post-image">
*그림: 포스트 이미지*


## 1. 과정 개요

### 1.1 학습 목표

이번 클라우드 시큐리티 8기 과정을 통해 다음 역량을 습득할 수 있습니다:

- **DevSecOps 실무 역량**: 보안을 개발 프로세스에 통합하는 실전 방법론
- **FinOps 전문성**: 클라우드 비용 최적화 및 거버넌스 역량
- **클라우드 보안 아키텍처**: AWS 기반 안전한 인프라 설계 및 운영
- **실무 문제 해결**: 실제 업무에서 마주치는 보안 이슈 해결 능력

### 1.2 대상자

이 과정은 다음 분들에게 적합합니다:

- **DevSecOps 엔지니어**: 보안 통합 개발 프로세스 구축을 원하는 분
- **보안 엔지니어**: 클라우드 보안 전문성을 키우고 싶은 분
- **클라우드 아키텍트**: 안전하고 효율적인 클라우드 아키텍처 설계를 원하는 분
- **DevOps 엔지니어**: 보안 역량을 강화하고 싶은 분
- **클라우드 관리자**: 비용 최적화와 보안을 동시에 고려해야 하는 분

### 1.3 학습 방식

- **온라인 미팅**: 실시간 화상 강의로 진행
- **효율적 학습 루틴**: 20분 강의 + 5분 휴식 (뇌과학 기반 최적화)
- **실무 중심**: 이론보다 실전 경험과 사례 중심
- **상호작용**: 실무 고민 공유 및 Q&A 시간

## 2. 2025년 보안 트렌드와 과정의 방향성

### 2.1 왜 지금 클라우드 보안인가?

2025년 보안 환경은 전례 없는 변화를 맞이하고 있습니다:

- **AI 보안의 양면성**: 93%의 보안 리더가 일일 AI 기반 공격을 예상하고 있습니다
- **Shadow AI 위협**: 조직 승인 없이 사용되는 AI 시스템이 새로운 보안 위험으로 부상
- **Supply Chain 공격 급증**: npm Shai-Hulud 웜 등 공급망을 노리는 공격이 정교해지고 있습니다
- **Zero Trust 표준화**: ZTNA가 업계 표준으로 정착하며 "절대 신뢰하지 말고, 항상 검증하라"가 기본 원칙이 되었습니다
- **Post-quantum 암호화**: Cloudflare가 전체 트래픽의 52%를 Post-quantum 암호화로 보호하는 시대

이러한 환경에서 클라우드 시큐리티 8기는 **실무에서 바로 적용 가능한 최신 보안 역량**을 제공합니다.

### 2.2 AWS re:Invent 2025 발표와 커리큘럼 연계

AWS re:Invent 2025에서 발표된 최신 보안 서비스들을 커리큘럼에 반영했습니다:

| AWS 신규 서비스 | 설명 | 관련 커리큘럼 |
|---------------|------|-------------|
| AWS Security Agent | AI 기반 자동 위협 대응 | 2주차 AWS 보안 아키텍처 |
| Security Hub GA | 통합 보안 관리 허브 정식 출시 | 5주차 보안 도구 |
| GuardDuty Extended Threat Detection | 확장된 위협 탐지 | 2주차 GuardDuty 심화 |
| IAM Policy Autopilot | AI 기반 IAM 정책 자동 생성 | 2주차 IAM 보안 |
| AgentCore Identity | AI 에이전트 전용 신원 관리 | 6주차 DevSecOps 심화 |

## 3. 커리큘럼 상세

### 3.1 전체 커리큘럼 개요

클라우드 시큐리티 8기는 총 9주 과정으로 구성됩니다:

| 주차 | 주제 | 핵심 내용 |
|------|------|----------|
| 1주차 | 인프라의 본질부터 보안의 미래까지 | 네트워크, 서버, 가상화 기초, 2025 보안 트렌드(AI 보안, Zero Trust) |
| 2주차 | AWS 보안 아키텍처의 핵심 | VPC, IAM, S3, GuardDuty Extended, Security Agent |
| 3주차 | AWS FinOps 및 ISMS-P | 비용 최적화, 거버넌스, 보안 감사 |
| 4주차 | 통합 보안 취약점 점검 | 취약점 스캔, ISMS-P 인증 대응, Supply Chain 보안 |
| 5주차 | AWS Control Tower 및 보안 도구 | Landing Zone, SCP, Security Hub, Datadog SIEM, Cloudflare |
| 6주차 이후 | DevSecOps 심화 | CI/CD 보안, 컨테이너 보안, AgentCore Identity, 통합 정리 |

### 3.2 주요 학습 영역

#### DevSecOps 영역

- **보안 통합 개발**: CI/CD 파이프라인에 보안 자동화 통합
- **컨테이너 보안**: Docker, Kubernetes 보안 모범 사례
- **코드 보안**: GitHub Advanced Security, 정적/동적 분석
- **인프라 보안**: IaC 보안, Terraform 보안 모범 사례

#### FinOps 영역

- **비용 최적화**: AWS Cost Explorer, 예산 관리
- **리소스 태깅 전략**: 비용 할당 및 추적
- **거버넌스**: AWS Control Tower, SCP를 통한 거버넌스
- **예산 관리**: 예산 알림 및 비용 이상 탐지

#### 클라우드 보안 영역

- **네트워크 보안**: VPC 설계, Security Group, NACL
- **접근 제어**: IAM 정책, 최소 권한 원칙
- **위협 탐지**: GuardDuty, CloudTrail, Config
- **데이터 보호**: S3 암호화, KMS 활용

## 3. 과정 특징 및 기대 효과

### 3.1 과정의 특징

> **💡 실무 중심 교육**
> 
> 단순한 이론 강의가 아닌, 실제 업무에서 바로 적용 가능한 실전 지식과 경험을 공유합니다.

> **💡 효율적 학습 구조**
> 
> 뇌과학 연구에 기반한 '20분 강의 + 5분 휴식' 구조로 집중력과 학습 효율을 극대화합니다.

> **💡 상호작용 중심**
> 
> 일방향 강의가 아닌, 실무 고민을 함께 나누고 해결하는 상호작용형 학습 환경을 제공합니다.

### 3.2 기대 효과

이 과정을 수료하시면:

1. **대체 불가능한 전문가로 성장**: DevSecOps와 FinOps를 모두 아우르는 전문 역량 확보
2. **실무 문제 해결 능력 향상**: 실제 업무에서 마주치는 보안 이슈를 스스로 해결할 수 있는 역량 습득
3. **클라우드 보안 아키텍처 설계 능력**: 안전하고 효율적인 클라우드 인프라를 설계할 수 있는 능력 확보
4. **비용 최적화 역량**: 보안과 비용을 동시에 고려한 최적의 솔루션 설계 능력
5. **커리어 발전**: 클라우드 보안 전문가로서의 커리어 경로 확장

## 4. 마무리

클라우드 시큐리티 8기는 단순한 교육 과정이 아닙니다. **대체 불가능한 클라우드 보안 전문가로 성장하는 여정**의 시작점입니다.

DevSecOps와 FinOps를 모두 아우르는 실무 역량을 키워, 보안과 비용을 동시에 고려할 수 있는 전문가가 되시길 기대합니다.

> "Security is not a product, but a process." - Bruce Schneier

보안은 단순히 도구를 도입하는 것이 아니라, **문화와 프로세스의 변화**가 필요합니다. 이번 과정을 통해 그 변화를 함께 만들어가시길 바랍니다.

클라우드 시큐리티 8기에서 만나요! 🚀
---
layout: post
title: "클라우드 시큐리티 8기 3주차: AWS FinOps 아키텍처부터 ISMS-P 보안 감사까지 완벽 공략!"
date: 2025-12-12 14:45:05 +0900
categories: finops
tags: [AWS, FinOps, ISMS-P, Audit, Cost-Optimization]
excerpt: "클라우드 시큐리티 8기 3주차: 2025년 FinOps 트렌드(AI/ML 비용 최적화 GPU 인스턴스/Spot Instance 최대 90% 절감, GreenOps 통합 Customer Carbon Footprint Tool, Unit Economics Cost per Transaction/User, Real-time Cost Visibility Cost Anomaly Detection), AWS 비용 관리 도구(Cost Optimization Hub 통합 대시보드, Compute Optimizer AI 기반 right-sizing, Application Cost Profiler 테넌트별 비용 배분, Cost Anomaly Detection ML 기반 탐지), ISMS-P 인증 대응(AWS Artifact/Config Rules/Security Hub/CloudTrail), FinOps+보안 통합, Commitment Management 자동화까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/703
image: /assets/images/2025-12-12-Cloud_Security_8Batch_3Week_AWS_FinOps_ArchitectureFrom_ISMS-P_Security_AuditTo_Complete_Strategy.svg
image_alt: "Cloud Security 8Batch 3Week: Complete Strategy from AWS FinOps Architecture to ISMS-P Security Audit"
---
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 8기 3주차: AWS FinOps 아키텍처부터 ISMS-P 보안 감사까지 완벽 공략!</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">FinOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">FinOps</span>
      <span class="tag">ISMS-P</span>
      <span class="tag">Audit</span>
      <span class="tag">Cost-Optimization</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>2025년 FinOps 트렌드: AI/ML 비용 최적화, GreenOps 통합, Commitment Management 강화</li>
      <li>AWS 비용 관리 도구: Cost Optimization Hub, Compute Optimizer, Application Cost Profiler</li>
      <li>ISMS-P 보안 감사 대응: AWS 기반 컴플라이언스 전략 및 주요 점검 항목</li>
      <li>FinOps 모범 사례: 태깅 전략, 예산 알림, 정기 리뷰</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS FinOps, ISMS-P, Cost Optimization Hub, Compute Optimizer, Application Cost Profiler, Cost Anomaly Detection, AWS Security Hub, AWS Artifact, AWS Config Rules, AWS CloudTrail, AWS Budgets, Savings Plans, Reserved Instances, Customer Carbon Footprint Tool</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">FinOps 전문가, 클라우드 관리자, 재무 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>


## 서론

안녕하세요, Twodragon입니다. 어느덧 클라우드 시큐리티 과정 8기도 중반부를 향해 달려가고 있습니다. 이번 3주차 세션 역시 우리만의 온라인 미팅에서 진행되었으며, '20분 몰입 + 5분 휴식'이라는 효율적인 루틴으로 집중도를 최대로 끌어올렸습니다.

이번 3주차에서는 **AWS FinOps 아키텍처**와 **ISMS-P 보안 감사 대응**을 중심으로 다뤘습니다. 특히 2025년 FinOps 트렌드와 AWS 비용 관리 도구의 최신 기능, 그리고 FinOps와 보안의 통합 접근법을 실무 중심으로 살펴봤습니다.

본 포스팅에서는 2025년 FinOps 트렌드, AWS 비용 관리 도구, ISMS-P 보안 감사 대응 전략, FinOps 모범 사례를 실무 중심으로 상세히 다룹니다.

<img src="{{ '/assets/images/2025-12-12-Cloud_Security_8Batch_3Week_AWS_FinOps_ArchitectureFrom_ISMS-P_Security_AuditTo_Complete_Strategy_image.png' | relative_url }}" alt="Cloud Security 8Batch 3Week: Complete Strategy from AWS FinOps Architecture to ISMS-P Security Audit" loading="lazy" class="post-image">

> **📌 핵심 요약**
> 
> - **2025년 FinOps 트렌드**: AI/ML 비용 최적화, GreenOps 통합, Commitment Management 강화, Real-time Cost Visibility, Unit Economics
> - **AWS 비용 관리 도구**: Cost Optimization Hub, Compute Optimizer, Application Cost Profiler, Cost Anomaly Detection
> - **ISMS-P 보안 감사 대응**: AWS Artifact, Config Rules, Security Hub, CloudTrail을 활용한 컴플라이언스 전략
> - **FinOps 모범 사례**: 태깅 전략, 예산 알림, 정기 리뷰, FinOps 문화 정착

## 1. 2025년 FinOps 트렌드

### 1.1 AI/ML 비용 최적화

2025년 가장 주목받는 FinOps 트렌드는 **AI/ML 워크로드 비용 관리**입니다. GenAI 워크로드의 급증으로 인해 AI 인프라 비용 관리가 핵심 과제로 부상했습니다.

#### GPU 인스턴스 최적화 전략

| 최적화 항목 | 설명 | 비용 절감 효과 |
|------------|------|--------------|
| **인스턴스 타입 선택** | 워크로드에 맞는 GPU 인스턴스 선택 (p4, p5, g5 등) | 20-30% 절감 |
| **Spot Instance 활용** | 학습 워크로드의 경우 Spot Instance 활용 | 최대 90% 절감 |
| **Auto Scaling** | 워크로드에 따른 자동 스케일링 | 30-50% 절감 |
| **모델 최적화** | 모델 경량화 및 양자화 | 추론 비용 50% 절감 |

#### Spot Instance 보안 고려사항

> **⚠️ 보안 주의사항**
> 
> Spot Instance 사용 시 보안 고려사항:
> - **체크포인트 저장**: 중단 시 데이터 손실 방지를 위한 체크포인트 자동 저장
> - **데이터 암호화**: 민감한 학습 데이터는 반드시 암호화하여 저장
> - **접근 제어**: Spot Instance에 대한 접근 제어 정책 수립
> - **모니터링**: Spot Instance 중단 시 자동 알림 및 대응 프로세스

#### 모델 서빙 최적화

| 최적화 기법 | 설명 | 비용 절감 효과 |
|------------|------|--------------|
| **모델 경량화** | 모델 압축 및 양자화 | 추론 비용 40-60% 절감 |
| **배치 처리** | 여러 요청을 배치로 처리 | 처리량 향상, 비용 절감 |
| **캐싱** | 자주 사용되는 결과 캐싱 | 반복 추론 비용 제거 |
| **Edge 배포** | 엣지 디바이스에 모델 배포 | 클라우드 추론 비용 절감 |

### 1.2 FinOps + GreenOps 통합

탄소 발자국 추적과 비용 최적화를 동시에 관리하는 **지속 가능한 클라우드 운영**이 중요해졌습니다.

#### AWS Customer Carbon Footprint Tool

| 기능 | 설명 | 활용 방법 |
|------|------|----------|
| **탄소 배출량 추적** | AWS 서비스 사용에 따른 탄소 배출량 측정 | 월간 탄소 배출량 리포트 |
| **리전별 비교** | 리전별 탄소 배출량 비교 | 그린 리전 우선 선택 |
| **트렌드 분석** | 시간에 따른 탄소 배출량 추이 분석 | 지속 가능성 목표 설정 |

#### 그린 리전 선택 전략

| 리전 특성 | 설명 | 비용 영향 |
|----------|------|----------|
| **재생 에너지 비율** | 재생 에너지 사용 비율이 높은 리전 선택 | 비용 영향 없음 |
| **탄소 중립** | 탄소 중립 인증을 받은 리전 선택 | 비용 영향 없음 |
| **에너지 효율** | 에너지 효율이 높은 데이터 센터 선택 | 간접적 비용 절감 |

> **💡 실무 팁**
> 
> GreenOps와 FinOps 통합 시 주의사항:
> - **비용 우선**: 그린 리전 선택 시 비용도 함께 고려
> - **성능 고려**: 그린 리전의 네트워크 지연 시간 확인
> - **데이터 지역화**: 규정 준수를 위한 데이터 지역화 요구사항 확인

### 1.3 Commitment Management 강화

**Savings Plans 및 Reserved Instances 자동화**가 더욱 정교해졌습니다.

#### 자동화된 커버리지 분석

| 분석 항목 | 설명 | 자동화 도구 |
|----------|------|-----------|
| **사용 패턴 분석** | 과거 사용 패턴 기반 최적 약정 추천 | AWS Cost Explorer, Compute Optimizer |
| **커버리지 최적화** | 현재 약정의 커버리지 분석 및 최적화 | AWS Savings Plans Recommendations |
| **약정 전환** | RI에서 Savings Plans로 전환 권장 | AWS Cost Optimization Hub |

#### Savings Plans vs Reserved Instances 비교

| 항목 | Savings Plans | Reserved Instances |
|------|--------------|-------------------|
| **유연성** | 높음 (인스턴스 타입 변경 가능) | 낮음 (특정 인스턴스 타입 고정) |
| **할인율** | 최대 72% | 최대 72% |
| **적용 범위** | Compute, EC2 Instance, Lambda, Fargate | EC2 Instance, RDS, ElastiCache 등 |
| **권장 사용** | 워크로드 변화가 많은 경우 | 안정적인 워크로드 |

### 1.4 Real-time Cost Visibility

**실시간 비용 모니터링 및 이상 탐지**가 필수 요소가 되었습니다.

#### AWS Cost Anomaly Detection

| 기능 | 설명 | 활용 방법 |
|------|------|----------|
| **ML 기반 탐지** | 머신러닝을 통한 비정상 비용 발생 자동 탐지 | 자동 알림 설정 |
| **다차원 분석** | 서비스, 계정, 태그 등 다양한 차원에서 분석 | 세분화된 비용 모니터링 |
| **근본 원인 분석** | 비용 급증의 근본 원인 자동 분석 | 빠른 대응 가능 |

#### 실시간 대시보드 구성

| 대시보드 유형 | 설명 | 대상 독자 |
|-------------|------|----------|
| **경영진 대시보드** | 전체 비용 현황 및 트렌드 | C-Level, 재무팀 |
| **팀별 대시보드** | 부서/프로젝트별 비용 현황 | 개발팀, 운영팀 |
| **서비스별 대시보드** | AWS 서비스별 비용 상세 | 아키텍트, DevOps |

### 1.5 Unit Economics

**비즈니스 메트릭과 클라우드 비용의 연계**가 강화되었습니다.

#### 주요 Unit Economics 메트릭

| 메트릭 | 설명 | 계산 방법 |
|--------|------|----------|
| **Cost per Transaction** | 트랜잭션당 비용 | 총 비용 / 총 트랜잭션 수 |
| **Cost per User** | 사용자당 비용 | 총 비용 / 활성 사용자 수 |
| **Cost per Feature** | 기능당 비용 | 기능별 리소스 비용 합계 |
| **Revenue per Dollar** | 달러당 수익 | 총 수익 / 총 비용 |

> **💡 실무 팁**
> 
> Unit Economics 측정 시 주의사항:
> - **정확한 데이터**: 비즈니스 메트릭과 클라우드 비용의 정확한 매핑 필요
> - **정기적 리뷰**: 월간 또는 분기별로 Unit Economics 리뷰 수행
> - **트렌드 분석**: 시간에 따른 Unit Economics 변화 추적

## 2. AWS 비용 관리 도구 (2025)

### 2.1 AWS Cost Optimization Hub

권장 사항을 중앙에서 관리하는 통합 도구입니다.

| 기능 | 설명 | 활용 방법 |
|------|------|----------|
| **통합 대시보드** | 모든 비용 최적화 권장 사항 한눈에 확인 | 일일/주간 비용 리뷰 |
| **우선순위 지정** | 비용 절감 잠재력 기반 우선순위 제공 | 우선순위 높은 항목부터 처리 |
| **실행 추적** | 최적화 실행 현황 모니터링 | 최적화 효과 측정 |
| **멀티 계정 지원** | 여러 계정의 권장 사항 통합 관리 | 조직 전체 비용 최적화 |

### 2.2 AWS Compute Optimizer

**AI 기반 right-sizing 권장**을 제공합니다.

| 최적화 대상 | 분석 방법 | 권장 사항 |
|------------|---------|----------|
| **EC2 인스턴스** | 14일 이상 사용 데이터 분석 | 인스턴스 타입, 크기 권장 |
| **EBS 볼륨** | IOPS 및 처리량 패턴 분석 | 스토리지 타입 및 크기 권장 |
| **Lambda 함수** | 메모리 사용 패턴 분석 | 메모리 할당 최적화 |
| **Auto Scaling 그룹** | 워크로드 패턴 분석 | 스케일링 정책 최적화 |

> **참고**: AWS Compute Optimizer 설정 관련 자세한 내용은 [AWS Compute Optimizer 공식 문서](https://docs.aws.amazon.com/compute-optimizer/)를 참조하세요.

### 2.3 AWS Application Cost Profiler

**애플리케이션별 비용 분석**을 지원합니다.

| 기능 | 설명 | 활용 시나리오 |
|------|------|-------------|
| **테넌트별 비용 배분** | 멀티테넌트 환경에서 정확한 비용 할당 | SaaS 애플리케이션 비용 관리 |
| **상세 보고서** | 애플리케이션 수준의 비용 가시성 | 기능별 비용 분석 |
| **차지백 지원** | 부서별/프로젝트별 비용 배분 | 내부 비용 배분 |

### 2.4 AWS Cost Anomaly Detection

**ML 기반 비정상 비용 발생 자동 탐지**를 제공합니다.

| 탐지 유형 | 설명 | 대응 방법 |
|----------|------|----------|
| **서비스별 이상** | 특정 서비스의 비용 급증 탐지 | 서비스별 알림 설정 |
| **계정별 이상** | 특정 계정의 비용 급증 탐지 | 계정별 모니터링 |
| **태그별 이상** | 특정 태그의 비용 급증 탐지 | 프로젝트별 모니터링 |

> **💡 실무 팁**
> 
> Cost Anomaly Detection 설정 시 주의사항:
> - **임계값 설정**: 너무 낮으면 False Positive 증가, 너무 높으면 탐지 누락
> - **알림 채널**: Slack, 이메일 등 적절한 알림 채널 설정
> - **대응 프로세스**: 비용 급증 시 즉시 대응할 수 있는 프로세스 수립

## 3. ISMS-P 보안 감사 대응

### 3.1 ISMS-P 인증 개요

ISMS-P(정보보호 및 개인정보보호 관리체계)는 조직의 정보보호 및 개인정보보호 관리 체계를 평가하는 국내 인증 제도입니다.

| 항목 | 내용 |
|------|------|
| **인증 범위** | 정보보호 관리체계(ISMS) + 개인정보보호 관리체계 |
| **인증 의무 대상** | 정보통신서비스 제공자, 집적정보통신시설 사업자 등 |
| **갱신 주기** | 3년 (연간 사후심사) |
| **주요 통제 항목** | 총 114개 통제 항목 (2025년 기준) |

### 3.2 클라우드 환경 ISMS-P 주요 점검 항목

클라우드 환경에서 특히 중요한 ISMS-P 통제 항목을 정리합니다.

| 통제 영역 | 주요 항목 | AWS 대응 방안 |
|----------|---------|--------------|
| **2.5 인증 및 권한관리** | IAM 정책, MFA 적용, 권한 최소화 | AWS IAM, MFA 강제, IAM Policy Autopilot |
| **2.6 접근통제** | VPC 네트워크 분리, Security Group 관리 | VPC 설계, Security Group 최소 권한 원칙 |
| **2.9 시스템 및 서비스 보안관리** | 보안 패치, 취약점 점검 | AWS Systems Manager Patch Manager, Security Hub |
| **2.10 시스템 및 서비스 운영관리** | 로깅, 모니터링, 백업 | CloudTrail, CloudWatch, AWS Backup |
| **2.11 암호화** | 데이터 암호화, 키 관리 | AWS KMS, S3 암호화, EBS 암호화 |
| **2.12 개인정보보호** | 개인정보 처리, 보관, 파기 | 데이터 분류, 접근 제어, 보관 기간 관리 |

### 3.3 AWS 기반 ISMS-P 대응 전략

AWS 환경에서 ISMS-P 인증을 준비하기 위한 핵심 전략입니다.

#### AWS Artifact 활용

| 문서 유형 | 설명 | 활용 방법 |
|----------|------|----------|
| **컴플라이언스 보고서** | SOC, PCI-DSS 등 인증 보고서 | ISMS-P 심사 시 증빙 자료로 제출 |
| **합의 평가 보고서** | AWS 서비스의 보안 평가 결과 | 클라우드 서비스 보안 수준 증명 |
| **계약 문서** | AWS 서비스 이용 약관 | 계약 관리 체계 증빙 |

#### AWS Config Rules를 통한 자동 컴플라이언스 확인

| Config Rule | ISMS-P 항목 | 설명 |
|------------|-----------|------|
| **s3-bucket-public-read-prohibited** | 2.6 접근통제 | S3 버킷 Public 읽기 차단 |
| **iam-password-policy** | 2.5 인증 및 권한관리 | IAM 비밀번호 정책 준수 |
| **encrypted-volumes** | 2.11 암호화 | EBS 볼륨 암호화 확인 |
| **cloud-trail-enabled** | 2.10 시스템 운영관리 | CloudTrail 활성화 확인 |

#### AWS Security Hub 통합 관리

| 기능 | 설명 | ISMS-P 활용 |
|------|------|------------|
| **통합 대시보드** | 모든 보안 서비스의 결과를 한 곳에서 확인 | 보안 상태 일목요연하게 파악 |
| **자동화된 컴플라이언스 체크** | CIS, PCI-DSS 등 표준 준수 상태 자동 확인 | ISMS-P 준수 상태 확인 |
| **보안 점수** | 보안 상태를 점수로 시각화 | 보안 개선 우선순위 설정 |

#### AWS CloudTrail 감사 로그

| 로그 유형 | 설명 | ISMS-P 활용 |
|----------|------|------------|
| **API 호출 로그** | 모든 AWS API 호출 기록 | 접근 통제 감사 증빙 |
| **이벤트 히스토리** | 보안 관련 이벤트 기록 | 보안 사고 조사 증빙 |
| **로그 보관** | 장기 보관 및 검색 | 규정 준수 요구사항 충족 |

> **💡 실무 팁**
> 
> ISMS-P 인증 준비 시 주의사항:
> - **조기 준비**: 인증 신청 전 최소 6개월 이상 준비 기간 확보
> - **문서화**: 모든 보안 활동을 문서화하여 증빙 자료 준비
> - **자동화**: 수동 작업은 최소화하고 AWS 도구를 통한 자동화 활용
> - **지속적 개선**: 인증 획득 후에도 지속적인 보안 개선 활동 수행

## 4. FinOps 모범 사례

### 4.1 태깅 전략

일관된 리소스 태깅으로 비용 추적 용이성을 확보합니다.

| 태그 키 | 태그 값 예시 | 용도 |
|--------|------------|------|
| **Environment** | Production, Staging, Development | 환경별 비용 분리 |
| **Project** | Project-A, Project-B | 프로젝트별 비용 추적 |
| **Team** | Backend, Frontend, DevOps | 팀별 비용 배분 |
| **CostCenter** | Engineering, Marketing | 부서별 비용 배분 |
| **Owner** | team-lead@example.com | 리소스 소유자 식별 |

> **참고**: AWS 태깅 모범 사례 관련 내용은 [AWS 태깅 전략 가이드](https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html)를 참조하세요.

### 4.2 예산 알림

AWS Budgets를 통한 예산 초과 사전 알림을 설정합니다.

| 예산 유형 | 설명 | 알림 임계값 |
|----------|------|------------|
| **비용 예산** | 총 비용 예산 설정 | 80%, 100%, 120% |
| **사용량 예산** | 특정 서비스 사용량 예산 | 80%, 100% |
| **RI/Savings Plans 예산** | 약정 관련 예산 | 커버리지 80% 미만 시 |

### 4.3 정기 리뷰

월간 비용 최적화 리뷰 미팅을 운영합니다.

| 리뷰 항목 | 설명 | 주기 |
|----------|------|------|
| **비용 트렌드 분석** | 월간 비용 변화 추이 분석 | 월간 |
| **최적화 권장 사항 검토** | Cost Optimization Hub 권장 사항 검토 | 월간 |
| **예산 대비 실적** | 예산 대비 실제 비용 비교 | 월간 |
| **Unit Economics 리뷰** | 비즈니스 메트릭과 비용 연계 분석 | 분기별 |

### 4.4 FinOps 문화 정착

개발팀의 비용 인식 제고를 위한 교육 및 문화 정착입니다.

| 활동 | 설명 | 주기 |
|------|------|------|
| **비용 교육** | 개발자 대상 클라우드 비용 교육 | 분기별 |
| **비용 대시보드 공유** | 팀별 비용 대시보드 공유 | 주간 |
| **비용 챔피언** | 팀 내 FinOps 챔피언 지정 | 연간 |
| **비용 메트릭 통합** | 개발 팀 KPI에 비용 메트릭 포함 | 연간 |

> **💡 실무 팁**
> 
> FinOps 문화 정착 시 주의사항:
> - **점진적 접근**: 한 번에 모든 것을 바꾸지 말고 단계적으로 접근
> - **긍정적 피드백**: 비용 절감 성과에 대한 긍정적 피드백 제공
> - **도구 활용**: 비용 가시성을 높이는 도구 적극 활용
> - **지속적 개선**: FinOps 프로세스를 지속적으로 개선

## 결론

클라우드 시큐리티 8기 3주차에서는 **AWS FinOps 아키텍처**부터 **ISMS-P 보안 감사**까지 다뤘습니다.

**2025년 FinOps 트렌드**에서는 AI/ML 비용 최적화, FinOps와 GreenOps 통합, Commitment Management 강화, Real-time Cost Visibility, Unit Economics 등 최신 트렌드를 살펴봤습니다. 특히 GenAI 워크로드의 급증으로 인한 AI 인프라 비용 관리가 핵심 과제로 부상했으며, Spot Instance 활용, 모델 최적화 등을 통한 비용 절감 전략을 다뤘습니다.

**AWS 비용 관리 도구**에서는 Cost Optimization Hub, Compute Optimizer, Application Cost Profiler, Cost Anomaly Detection 등 2025년 최신 도구들을 다뤘습니다. 각 도구의 특징과 실무 활용 방법을 중심으로 정리했으며, 통합 대시보드를 통한 비용 관리 전략을 살펴봤습니다.

**ISMS-P 보안 감사 대응**에서는 클라우드 환경에서의 ISMS-P 인증 준비 전략을 다뤘습니다. AWS Artifact, Config Rules, Security Hub, CloudTrail 등을 활용한 컴플라이언스 대응 방법을 살펴봤으며, 자동화된 컴플라이언스 확인을 통한 효율적인 인증 준비 전략을 정리했습니다.

**FinOps 모범 사례**에서는 태깅 전략, 예산 알림, 정기 리뷰, FinOps 문화 정착 등 실무에 바로 적용 가능한 모범 사례를 정리했습니다. 특히 개발팀의 비용 인식 제고를 위한 교육 및 문화 정착 방법을 다뤘습니다.

FinOps와 보안은 상호 보완적인 관계입니다. 비용 최적화와 보안을 동시에 고려하는 통합 접근법을 통해 안전하고 효율적인 클라우드 환경을 구축할 수 있습니다. 특히 2025년에는 AI/ML 비용 최적화와 GreenOps 통합이 중요한 트렌드로 부상했으며, 이러한 트렌드를 선제적으로 대응하는 것이 핵심입니다.

---

**원본 포스트**: [클라우드 시큐리티 8기 3주차: AWS FinOps 아키텍처부터 ISMS-P 보안 감사까지 완벽 공략!](https://twodragon.tistory.com/703)
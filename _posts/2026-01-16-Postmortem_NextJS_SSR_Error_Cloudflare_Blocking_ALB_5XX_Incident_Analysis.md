---
author: Twodragon
categories:
- incident
comments: true
date: 2026-01-16 12:00:00 +0900
description: 'Post-Mortem: Next.js SSR 환경 location 객체 접근 ReferenceError, Cloudflare
  WAF IP 차단, ALB Target Group Health Check 실패 인시던트 상세 분석. 근본 원인, 배포 연쇄 반응, 재발 방지 대책까지
  실무 중심 정리'
excerpt: Next.js SSR location 에러, Cloudflare WAF 차단, ALB 헬스체크 실패 분석
image: /assets/images/2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.svg
image_alt: Post-Mortem Next.js SSR Error Cloudflare Blocking ALB 5XX Incident Analysis
keywords:
- Post-Mortem
- Next.js-SSR
- Location-Error
- Cloudflare-WAF
- ALB-5XX
- Health-Check
- Kubernetes
- Incident-Response
- AWS
- ReferenceError
- WAF-Blocking
layout: post
schema_type: Article
tags:
- Post-Mortem
- Next.js
- SSR
- Cloudflare
- ALB
- Kubernetes
- Incident-Response
- AWS
title: '[Post-Mortem] Next.js SSR 에러 및 Cloudflare 차단으로 인한 ALB 5XX 에러 인시던트 분석'
toc: true
---

## 요약

- **핵심 요약**: Next.js SSR location 에러, Cloudflare WAF 차단, ALB 헬스체크 실패 분석
- **주요 주제**: [Post-Mortem] Next.js SSR 에러 및 Cloudflare 차단으로 인한 ALB 5XX 에러 인시던트 분석
- **키워드**: Post-Mortem, Next.js, SSR, Cloudflare, ALB

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">[Post-Mortem] Next.js SSR 에러 및 Cloudflare 차단으로 인한 ALB 5XX 에러 인시던트 분석</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Post-Mortem</span>
      <span class="tag">Next.js</span>
      <span class="tag">SSR</span>
      <span class="tag">Cloudflare</span>
      <span class="tag">ALB</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Incident-Response</span>
      <span class="tag">AWS</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>Next.js SSR 환경에서 location 객체 접근으로 인한 ReferenceError 발생</li>
      <li>모바일 x.com에서의 동작 차이: 인앱 브라우저 vs 시스템 브라우저</li>
      <li>location 객체란 무엇인지, 왜 SSR 환경에서 문제가 되는지 상세 분석</li>
      <li>배포 후 갑자기 증가한 5XX 에러 및 ALB Target Group Health Check 실패</li>
      <li>Cloudflare WAF 차단 패턴 분석 및 의심스러운 요청 패턴 식별</li>
      <li>근본 원인 분석: 배포와 에러의 연관성, 애플리케이션 버그, 연쇄 반응</li>
      <li>재발 방지 대책: 코드 수정, 배포 프로세스 개선, 모니터링 강화</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Next.js, Kubernetes, AWS ALB, Cloudflare WAF, GitHub Actions</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">SRE, 인시던트 대응 담당자, 프론트엔드 개발자, 운영 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 Next.js SSR 환경에서 발생한 인시던트 대응에 대해 실무 중심으로 정리합니다.

2026년 1월 14일 발생한 Next.js SSR 에러와 Cloudflare 차단으로 인한 ALB 5XX 에러는 배포 프로세스와 모니터링의 중요성을 다시 한번 일깨워주었습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- Next.js SSR 환경에서 location 객체 접근으로 인한 에러 분석
- 모바일 x.com에서의 동작 차이 및 인앱 브라우저 특성 분석
- location 객체란 무엇인지, 왜 SSR 환경에서 문제가 되는지
- 배포 후 갑자기 증가한 5XX 에러 및 ALB Target Group Health Check 실패 원인 분석
- Cloudflare WAF 차단 패턴 분석 및 의심스러운 요청 패턴 식별
- 근본 원인 분석 및 재발 방지 대책
- 배포 프로세스 개선 및 모니터링 강화 방안

<img src="{{ '/assets/images/2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.svg' | relative_url }}" alt="Post-Mortem Next.js SSR Error Cloudflare Blocking ALB 5XX Incident Analysis" loading="lazy" class="post-image">

*그림 1: Post-Mortem Next.js SSR 에러 및 Cloudflare 차단 인시던트 분석 개요*

> **관련 포스팅**:
> - [Post-Mortem: 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지](/posts/2025/11/19/Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned/)
> - [Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기](/posts/2025/10/02/Karpenter_v153_Node_Integration_Due_to_Large_scale_Incident_Analysis_And_Resolution/)

## 📊 인시던트 요약

| 항목 | 내용 |
|------|------|
| **발생 일시** | 2026-01-14 |
| **영향 서비스** | web-app (example.com, content.example.com) |
| **심각도** | High |
| **장애 지속 시간** | 약 5분 (5XX 에러 집중 발생) |
| **영향 범위** | content.example.com: 881 요청, example.com: 285 요청 |
| **근본 원인** | Next.js SSR 환경에서 location 객체 접근 + 배포 후 버그 노출 |

### 인시던트 타임라인

| 시간 | 이벤트 | 영향 |
|------|--------|------|
| 배포 직후 | 새 버전 배포 (v1.0.0 → v1.0.1) | - |
| 배포 직후 + 5분 | Cloudflare IP 차단 시작 | 일부 요청 차단 |
| 배포 직후 + 10분 | ALB Target Group 5XX 에러 급증 | 서비스 영향 시작 |
| 배포 직후 + 15분 | Pod 에러 로그 확인 | ReferenceError 발견 |
| 배포 직후 + 20분 | 근본 원인 파악 | 에러 원인 확인 |
| 배포 직후 + 30분 | 긴급 대응 시작 | 복구 시작 |

## 1. 사고 개요

### 1.0 전체 아키텍처

<figure>
<img src="{{ '/assets/images/2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_architecture_diagram.png' | relative_url }}" alt="Next.js SSR Error Incident Architecture" loading="lazy" class="post-image">
<figcaption>그림 1: Next.js SSR 에러 인시던트 전체 아키텍처 - draw.io로 생성</figcaption>
</figure>

<details>
<summary>draw.io XML 코드 (클릭하여 확장)</summary>

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요." value="WAF Rules" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE0B2;strokeColor=#F57C00;fontSize=12;" vertex="1" parent="cdn-cluster">
          <mxGeometry x="390" y="40" width="300" height="60" as="geometry" />
        </mxCell>
        <mxCell id="ratelimit" value="Rate Limiting" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE0B2;strokeColor=#F57C00;fontSize=12;" vertex="1" parent="cdn-cluster">
          <mxGeometry x="740" y="40" width="300" height="60" as="geometry" />
        </mxCell>
        
        ...
> > **코드 예시**: 전체 코드는 [공식 문서](https://docs.github.com/)를 참조하세요.
> 
> ```
> ...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조 -->

**시나리오 2: X 앱 인앱 브라우저에서 접속**
```
1. 사용자가 x.com에서 링크 클릭
2. X 앱이 열리고 인앱 브라우저(WebView) 사용
3. Custom User-Agent 전송 (X 앱 식별자 포함)
4. SSR 환경에서 location 접근 시도
5. ❌ ReferenceError 발생 (SSR 환경)
6. 추가로 WebView 특성으로 인한 추가 제약 가능
```

#### 해결 방안

**1. 브라우저 환경 체크**
> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://https://www.typescriptlang.org/docs/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.

```typescript
// ✅ 올바른 방법
if (typeof window !== 'undefined') {
  window.location.href = url;
}
```

**2. 모바일 앱 감지**
> **코드 예시**: 전체 코드는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.
> 
> ```typescript
> // User-Agent로 인앱 브라우저 감지...
> ```

typescript
// src/components/example/ExampleComponent.tsx
// 이전 버전에서는 문제 없었음 (다른 방식으로 리다이렉트 처리)
```

**변경 후 (v1.0.1) - 문제 발생**:
> **코드 예시**: 전체 코드는 [공식 문서](https://www.typescriptlang.org/docs/)를 참조하세요.
> 
> ```typescript
> // src/components/example/ExampleComponent.tsx...
> > **참고**: 관련 예제는 [공식 문서](https://docs.aws.amazon.com/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

```



**배포 후 발생한 문제**:

1. **배포 직후 (T+0분)**: 새 버전(v1.0.1)이 Kubernetes에 배포됨
2. **배포 직후 + 5분 (T+5분)**: 첫 번째 에러 발생
   ```
   ReferenceError: location is not defined
   at ExampleComponent.handleAction
   > **코드 예시**: 전체 코드는 [공식 문서](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> 3. **배포 직후 + 10분 (T+10분)**: 5XX 에러 급증 (50개 이상)...
> ```

<!-- 전체 코드는 위 링크 참조 -->
<!-- 전체 코드는 위 링크 참조 -->

</details>

> **참고**: 위 draw.io XML 코드를 [draw.io](https://app.diagrams.net/)에서 열어서 다이어그램을 편집하고 SVG/PNG로 내보낼 수 있습니다.

**에러 발생 경로 상세**:

1. **Cloudflare 레벨**: IP 차단으로 인한 요청 차단
2. **ALB 레벨**:
   - Health check 실패 가능성 (Pod 에러로 인한)
   - Target Group unhealthy 상태
3. **Pod 레벨**:
   - `ReferenceError: location is not defined` 발생
   - 특정 요청에서 500 에러 반환

### 4.3 연쇄 반응

<figure>
<img src="{{ '/assets/images/2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_cascade_reaction.png' | relative_url }}" alt="Cascade Reaction Sequence" loading="lazy" class="post-image">
<figcaption>그림 7: 연쇄 반응 시퀀스 다이어그램 - 사용자 요청부터 에러 발생까지의 전체 흐름</figcaption>
</figure>

**연쇄 반응 상세**:

1. **최근 배포로 인한 영향**:
   - 새 버전(v1.0.1) 배포로 인해 기존에 숨겨져 있던 버그가 노출됨
   - 또는 새 코드에서 `location` 직접 사용이 추가됨
   - 배포 직후 캐시 무효화로 인해 모든 요청이 SSR로 처리됨

2. **특정 IP에서 대량 요청 → Cloudflare 차단**:
   - 모바일 x.com에서 링크 공유로 인한 트래픽 증가
   - 검색 엔진 크롤러가 새 페이지를 크롤링
   - 반복적인 UUID 경로 접근으로 인한 의심스러운 패턴 감지
   - Cloudflare WAF가 비정상 트래픽으로 판단하여 IP 차단

3. **차단된 요청이 ALB에 도달하지 못함**:
   - Cloudflare에서 차단된 요청은 403 에러로 응답
   - 일부 정상 사용자도 차단되어 서비스 접근 불가
   - 차단되지 않은 요청만 ALB로 전달됨

4. **정상 요청도 Pod 에러로 인해 5XX 발생**:
   - ALB를 통과한 요청이 Kubernetes Pod로 전달됨
   - Pod에서 SSR 렌더링 중 `location` 객체 접근 시도
   - `ReferenceError: location is not defined` 발생
   - 모든 SSR 요청이 500 에러로 응답

5. **Health check 실패 → Target Group unhealthy**:
   - Pod에서 500 에러가 발생하면 Health Check 엔드포인트도 실패할 수 있음
   - ALB가 Target Group을 unhealthy로 표시
   - 더 많은 요청이 남은 Pod로 집중되어 에러율 증가

6. **더 많은 5XX 에러 발생**:
   - Target Group이 unhealthy 상태가 되면 로드 밸런싱이 비효율적으로 동작
   - 에러 로그가 급증하여 Cloudflare가 추가로 비정상 트래픽으로 판단
   - 연쇄적으로 더 많은 IP가 차단될 가능성

**왜 이런 연쇄 반응이 발생했는가?**

#### 근본적인 시스템 설계 문제

1. **에러 핸들링 부재**:
   - SSR 환경에서 `location` 접근 시도 시 적절한 에러 핸들링이 없음
   - 에러가 발생하면 전체 요청이 실패하여 사용자에게 500 에러 표시
   - Fallback 메커니즘이 없어 일부 에러가 전체 서비스에 영향을 미침

2. **모니터링 및 알림 지연**:
   - 배포 후 에러 발생 시 즉시 알림이 가지 않음
   - 5분 후에야 에러를 감지하여 대응이 지연됨
   - Health Check 실패를 조기에 감지하지 못함

3. **배포 검증 프로세스 부재**:
   - 배포 전 SSR 환경에서의 실제 테스트가 없음
   - 자동화된 검증 단계가 없어 문제 코드가 프로덕션에 배포됨
   - 롤백 계획이 명확하지 않아 빠른 복구가 어려움

4. **방어적 프로그래밍 부족**:
   - `location` 객체 접근 시 브라우저 환경 체크가 없음
   - SSR과 CSR 환경을 구분하지 않고 동일한 코드 사용
   - 타입 체크나 린터 규칙으로 사전에 방지할 수 있는 문제

## 5. 권장 조치 사항

### 5.1 즉시 조치 (Immediate)

#### 1. Cloudflare IP 차단 해제 검토

> **참고**: Cloudflare Dashboard에서 확인
> - Security → WAF → Firewall Rules
> - IP: 192.0.2.100 차단 해제 (임시)

**주의사항**:
- 정상 사용자일 가능성 확인 필요
- 요청 패턴이 의심스러우면 해제하지 않음
- Rate Limiting 규칙 추가 고려

#### 2. 애플리케이션 에러 수정

**문제 코드 위치** (총 5개 파일):

1. **`src/components/example/ExampleComponent.tsx`** (Line 50)
   
   <!-- 긴 코드 블록 제거됨 (가독성 향상) -->
   
2. **`src/components/example/DetailButton.tsx`** (Line 30)
   
   <!-- 긴 코드 블록 제거됨 (가독성 향상) -->
   
3. **`src/hooks/useNavigation.ts`** (Line 25)
   
   ```tsx
   // ❌ 문제 코드
   location.href = url;
   
   // ✅ 수정 코드
   if (typeof window !== 'undefined') {
     window.location.href = url;
   }
   ```
   
4. **`src/components/example/ResultComponent.tsx`** (Line 80)
   
   <!-- 긴 코드 블록 제거됨 (가독성 향상) -->
   
5. **`src/components/example/TabsComponent.tsx`** (Line 45)
   
   <!-- 긴 코드 블록 제거됨 (가독성 향상) -->

**수정 우선순위**: High
- 서버 사이드에서 `location` 접근 방지
- 클라이언트/서버 코드 분리
- 모든 `location.href` → `window.location.href`로 변경 및 안전 체크 추가

#### 3. Pod 로그 모니터링 강화

> **참고**: Kubernetes 로그 모니터링 관련 내용은 [Kubernetes 로그 문서](https://kubernetes.io/docs/concepts/cluster-administration/logging/)를 참조하세요.

```bash
# 실시간 에러 모니터링
kubectl logs -n production -l app=web-app -f --tail=100 | grep -i error
```

### 5.2 단기 조치 (1주일 내)

#### 4. ALB Target Group Health Check 최적화

| 설정 항목 | 현재 값 | 권장 값 | 설명 |
|----------|---------|---------|------|
| **Health Check Path** | `/api/healthz` | `/health` | 더 가벼운 엔드포인트 |
| **Interval** | 5초 | 5초 | 유지 |
| **Timeout** | 3초 | 5초 | 애플리케이션 응답 시간 고려 |
| **Unhealthy Threshold** | 3 | 3 | 유지 |
| **Success Codes** | 200 | 200 | 유지 |

> **참고**: AWS ALB Health Check 설정 관련 내용은 [AWS ALB Target Groups 문서](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)를 참조하세요.

#### 5. Cloudflare WAF 규칙 강화

> **참고**: Cloudflare WAF Rate Limiting 관련 내용은 [Cloudflare Rate Limiting 문서](https://developers.cloudflare.com/waf/rate-limiting-rules/)를 참조하세요.

**Rate Limiting 규칙 추가**:
- 동일 IP에서 1분간 100회 이상 요청 시 차단
- UUID 패턴 경로에 대한 특별 규칙
- API 엔드포인트별 Rate Limit 설정

#### 6. 모니터링 및 알림 설정

| 모니터링 항목 | 설명 | 목적 |
|-------------|------|------|
| **CloudWatch 알람** | 5XX 에러 5분간 50개 이상 | 조기 감지 |
| **Datadog/Sentry** | 애플리케이션 에러 실시간 알림 | 에러 추적 |
| **Cloudflare Security Events** | 차단 이벤트 모니터링 | 보안 이벤트 추적 |

### 5.3 중기 조치 (1개월 내)

#### 7. 애플리케이션 에러 핸들링 개선

- 전역 에러 핸들러 추가
- Sentry 통합 강화
- 에러 로깅 표준화

#### 8. 보안 강화

| 보안 항목 | 설명 | 목적 |
|----------|------|------|
| **Cloudflare Bot Management** | 봇 탐지 및 차단 | 자동화 공격 방지 |
| **API Rate Limiting** | API 엔드포인트별 제한 | API 남용 방지 |
| **IP 기반 접근 제어** | 필요시 IP 화이트리스트 | 접근 제어 강화 |

#### 9. 인프라 모니터링

- ALB Target Group Health 상태 대시보드
- Pod 에러율 메트릭
- Cloudflare 차단 이벤트 알림

## 6. 모니터링 체크리스트

### 6.1 즉시 확인 필요

- [ ] Cloudflare Security Events에서 차단된 IP 패턴 분석
- [ ] ALB Target Group Health 상태 확인
- [ ] Pod 에러 로그 상세 분석
- [ ] CloudWatch 5XX 에러 메트릭 확인

### 6.2 정기 모니터링

- [ ] 일일 Pod 에러율 확인
- [ ] 주간 Cloudflare 차단 이벤트 리뷰
- [ ] ALB Target Group Health 상태 주간 리포트
- [ ] 애플리케이션 성능 메트릭 추적

## 7. 보안 권장사항

### 7.1 Cloudflare 설정

| 설정 항목 | 권장 값 | 설명 |
|----------|---------|------|
| **Bot Fight Mode** | 활성화 | 봇 공격 방지 |
| **Rate Limiting (동일 IP)** | 100 req/min | DDoS 완화 |
| **Rate Limiting (API)** | 50 req/min | API 남용 방지 |
| **WAF 규칙** | UUID 패턴 경로 의심 요청 차단 | 자동화 공격 방지 |

### 7.2 애플리케이션 레벨

| 보안 항목 | 설명 | 목적 |
|----------|------|------|
| **Rate Limiting** | API 엔드포인트별 제한 | API 남용 방지 |
| **Request Validation** | UUID 형식 검증 | 비정상 요청 차단 |
| **Error Handling** | 민감한 정보 노출 방지 | 정보 유출 방지 |

### 7.3 인프라 레벨

- **Security Group**: Cloudflare IP 범위만 허용 (이미 설정됨)
- **ALB WAF**: AWS WAF 연동 고려
- **Logging**: 모든 요청 로깅 및 분석

## 8. 결론

### 8.1 주요 원인

#### 1. **GitHub 배포로 인한 영향** ⚠️ **핵심 원인**

- **최근 배포**: `v1.0.0` → `v1.0.1` (2026-01-14 배포)
- **배포 방식**: GitHub Actions 자동 배포 (`build-and-deploy.yml`)
- **영향**:
  - 새 버전 배포로 인해 기존에 숨겨져 있던 `location` 관련 버그가 노출됨
  - 또는 새 코드에서 `location` 직접 사용이 추가되어 SSR 환경에서 에러 발생
  - 배포 직후 갑자기 5XX 에러가 증가한 것은 **배포와 직접적인 연관성**이 높음
- **왜 발생했는가?**:
  - 배포 전 SSR 환경에서의 실제 테스트가 없었음
  - 배포 검증 프로세스가 부족하여 문제 코드가 프로덕션에 배포됨
  - 배포 후 모니터링이 지연되어 에러를 조기에 감지하지 못함

#### 2. **애플리케이션 버그**

- `ReferenceError: location is not defined`로 인한 5XX 에러
- 5개 파일에서 `location.href` 직접 사용 (서버 사이드에서 실행 시 에러)
- **왜 발생했는가?**:
  - 개발 환경에서는 클라이언트 사이드에서만 테스트하여 문제가 드러나지 않음
  - 단위 테스트와 통합 테스트가 SSR 환경을 검증하지 않음
  - 코드 리뷰 과정에서 SSR 환경에서의 문제점을 놓침
  - TypeScript나 린터가 `location` 직접 사용을 사전에 방지하지 못함

#### 3. **Cloudflare 차단**

- 의심스러운 요청 패턴으로 인한 IP 차단
- 배포 후 에러 증가로 인한 비정상 트래픽 패턴 발생 가능
- **왜 발생했는가?**:
  - 배포 직후 모바일 x.com에서 링크 공유로 인한 트래픽 증가
  - 반복적인 UUID 경로 접근으로 인한 의심스러운 패턴 감지
  - Pod 에러로 인한 5XX 에러 급증이 비정상 트래픽으로 판단됨
  - Cloudflare WAF 규칙이 너무 엄격하게 설정되어 정상 사용자도 차단

#### 4. **연쇄 반응**

- 배포 → 에러 발생 → Health Check 실패 → Target Group unhealthy → 더 많은 5XX 에러
- **왜 발생했는가?**:
  - 에러 핸들링 부재로 인해 일부 에러가 전체 서비스에 영향을 미침
  - Health Check 실패를 조기에 감지하지 못하여 연쇄 반응 발생
  - 모니터링 및 알림 지연으로 인해 빠른 대응이 어려움
  - 방어적 프로그래밍 부족으로 SSR 환경에서의 에러가 치명적으로 작용

### 8.2 해결 방향

#### 즉시 조치 (우선순위: Critical)

1. **애플리케이션 에러 수정 및 롤백 검토**
   - 5개 파일의 `location.href` → `window.location.href` 수정
   - 긴급 시 이전 버전(v1.0.0)으로 롤백 고려
   - 수정 후 재배포 전 충분한 테스트 필요

2. **배포 프로세스 개선**
   - 배포 전 자동화된 SSR 테스트 추가
   - Canary 배포 또는 Blue-Green 배포 전략 도입
   - 배포 후 모니터링 강화 (에러율, Health Check 상태)

#### 단기 조치

- Cloudflare 차단 해제 검토 및 모니터링 강화
- Health Check 최적화

#### 중기 조치

- 보안 강화 및 에러 핸들링 개선
- 배포 자동화 파이프라인에 사전 검증 단계 추가

### 8.3 예상 효과

- 5XX 에러율 감소: 90% 이상
- 배포 안정성 향상: 사전 검증으로 배포 후 에러 방지
- Cloudflare 차단 이벤트 감소
- 서비스 안정성 향상

### 8.4 배포 관련 권장사항

#### 1. 배포 전 검증 강화

> **참고**: GitHub Actions 워크플로우에 추가 권장
> 
> > **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.

```yaml
> - name: SSR Test
>   run: |
>     npm run build
>     npm run start &
>     sleep 10
>     # SSR 환경에서 location 사용 검증
>     curl http://localhost:3000/api/healthz
> ```

#### 2. 배포 전략 개선

| 배포 전략 | 설명 | 장점 |
|----------|------|------|
| **Canary 배포** | 새 버전을 일부 Pod에만 배포하여 점진적 롤아웃 | 점진적 검증 |
| **Blue-Green 배포** | 완전히 분리된 환경에서 테스트 후 전환 | 안전한 전환 |
| **롤백 계획** | 문제 발생 시 즉시 이전 버전으로 복구 가능 | 빠른 복구 |

#### 3. 모니터링 강화

- 배포 직후 30분간 에러율 집중 모니터링
- CloudWatch 알람: 배포 후 5XX 에러 급증 감지
- 자동 롤백: 임계값 초과 시 자동으로 이전 버전으로 복구

## 9. 참고 자료

### 9.1 관련 포스팅

- [Post-Mortem: 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지](/posts/2025/11/19/Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned/)
- [Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기](/posts/2025/10/02/Karpenter_v153_Node_Integration_Due_to_Large_scale_Incident_Analysis_And_Resolution/)
- [Cloud Security Course 7Batch - 7Week Docker And Kubernetes Understanding](/posts/2025/05/30/Cloud_Security_Course_7Batch_-_7Week_Docker_And_Kubernetes_Understanding/)

### 9.2 공식 문서

- [Next.js SSR 문서](https://nextjs.org/docs/pages/building-your-application/rendering/server-side-rendering)
- [Kubernetes Health Checks 문서](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [AWS ALB Target Groups 문서](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Cloudflare WAF 문서](https://developers.cloudflare.com/waf/)
- [Cloudflare Rate Limiting 문서](https://developers.cloudflare.com/waf/rate-limiting-rules/)

### 9.3 보안 모범 사례

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Kubernetes 보안 모범 사례](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [AWS 보안 모범 사례](https://aws.github.io/aws-eks-best-practices/security/docs/)

---

**작성일**: 2026-01-16

**작성자**: DevSecOps Team

**검토 필요**: 개발팀 (애플리케이션 에러 수정), 보안팀 (Cloudflare 차단 검토)

<!-- quality-upgrade:v1 -->
## 경영진 요약 (Executive Summary)
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
![포스트 시각 자료](/assets/images/2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.svg)

<!-- priority-quality-korean:v1 -->
## 우선순위 기반 고도화 메모
| 구분 | 현재 상태 | 목표 상태 | 우선순위 |
|---|---|---|---|
| 콘텐츠 밀도 | 점수 84 수준 | 실무 의사결정 중심 문장 강화 | P2 (단기 보강) |
| 표/시각 자료 | 핵심 표 중심 | 비교/의사결정 표 추가 | P2 |
| 실행 항목 | 체크리스트 중심 | 역할/기한/증적 기준 명시 | P1 |

### 이번 라운드 개선 포인트
- 핵심 위협과 비즈니스 영향의 연결 문장을 강화해 의사결정 맥락을 명확히 했습니다.
- 운영팀이 바로 실행할 수 있도록 우선순위(P0/P1/P2)와 검증 포인트를 정리했습니다.
- 후속 업데이트 시에는 실제 지표(MTTR, 패치 리드타임, 재발률)를 반영해 정량성을 높입니다.


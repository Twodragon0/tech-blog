# PDCA: 모니터링 기능

> 에러 추적, 성능 모니터링, 로그 관리

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `sentry-release.yml` |
| **서비스** | Sentry (Free Tier), Vercel Analytics |
| **모니터링 대상** | JavaScript 에러, 성능 메트릭, 서버 로그 |
| **상태** | Active |

---

## Plan (계획)

### 목표
- 실시간 에러 추적 및 알림
- 성능 병목 식별
- 비용 효율적 모니터링

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| 에러 탐지 시간 | < 1분 | - |
| Sentry 월간 이벤트 | < 5,000 (Free) | - |
| Core Web Vitals | Good | - |

### 모니터링 아키텍처
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │ ──▶ │   Sentry    │ ──▶ │   Alert     │
│   (Client)  │     │   (Error)   │     │   (Email)   │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │ ──▶ │  Analytics  │ ──▶ │  Dashboard  │
│   (Server)  │     │  (Metrics)  │     │   (Web)     │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐
│   GitHub    │ ──▶ │   Actions   │
│   Actions   │     │   Logs      │
└─────────────┘     └─────────────┘
```

---

## Do (실행)

### 1. Sentry 에러 추적

**배포 릴리스 (sentry-release.yml):**
```yaml
# 배포 시 Sentry 릴리스 생성
- name: Create Sentry Release
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
    SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
  run: |
    sentry-cli releases new $RELEASE_VERSION
    sentry-cli releases set-commits $RELEASE_VERSION --auto
    sentry-cli releases finalize $RELEASE_VERSION
```

**클라이언트 통합 (JavaScript):**
```javascript
// assets/js/sentry-init.js
Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: "production",
  tracesSampleRate: 0.1,  // 10% 샘플링 (비용 관리)
  beforeSend(event) {
    // PII 마스킹
    return maskSensitiveData(event);
  }
});
```

**Free Tier 최적화:**
- 월 5,000 이벤트 제한
- 샘플링 레이트 조절
- 중복 에러 그룹화

### 2. Vercel Analytics

**Web Vitals 모니터링:**
- LCP (Largest Contentful Paint)
- FID (First Input Delay)
- CLS (Cumulative Layout Shift)

**대시보드:**
- Vercel Dashboard → Analytics
- 실시간 트래픽 모니터링

### 3. 로컬 모니터링 스크립트

```bash
# Sentry 쿼터 확인
./scripts/monitor_sentry_quota.sh

# Sentry 로그 검증
node scripts/verify_sentry_logs.js

# Vercel 로그 확인
./scripts/check-vercel-logs.sh
```

### 4. 로그 관리

**Vercel Log Drains:**
- 서버 로그 중앙 집중화
- 로그 보관 기간 설정

**GitHub Actions 로그:**
```bash
# 최근 워크플로우 로그 확인
gh run view [run-id] --log
```

---

## Check (점검)

### 모니터링 항목

#### Sentry 상태
```bash
# Sentry 쿼터 확인
./scripts/monitor_sentry_quota.sh

# 최근 이슈 확인
# Sentry Dashboard → Issues
```

#### 성능 메트릭
- Vercel Analytics Dashboard
- Lighthouse CI (선택적)

#### 알림 설정
- [ ] Sentry 알림 규칙 확인
- [ ] 이메일 알림 동작 확인

### 점검 체크리스트
- [ ] Sentry 이벤트 쿼터 확인
- [ ] 미해결 에러 검토
- [ ] Core Web Vitals 점수
- [ ] 서버 로그 이상 확인

### 장애 대응
| 상황 | 대응 |
|------|------|
| Sentry 쿼터 초과 | 샘플링 레이트 낮춤 |
| 성능 저하 | 병목 구간 분석 |
| 에러 급증 | 롤백 검토 |

---

## Act (개선)

### 식별된 개선점
1. **알림 채널 추가**: Slack/Discord 연동
2. **대시보드 구성**: 커스텀 대시보드 생성
3. **자동화**: 에러 패턴 자동 분류

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] 에러 알림 채널 다양화
- [ ] 성능 기준선 설정
- [ ] 모니터링 대시보드 개선

---

## 비용 관리

### Sentry Free Tier
| 항목 | 제한 |
|------|------|
| 월간 이벤트 | 5,000 |
| 보관 기간 | 30일 |
| 팀원 | 1명 |

### 비용 절감 팁
1. **샘플링**: tracesSampleRate 조절
2. **필터링**: 불필요한 이벤트 제외
3. **그룹화**: 동일 에러 통합

```javascript
// 샘플링 최적화
Sentry.init({
  tracesSampleRate: 0.1,  // 10%
  beforeSend(event) {
    // 특정 에러 제외
    if (event.message?.includes('ResizeObserver')) {
      return null;
    }
    return event;
  }
});
```

---

## 관련 문서

- [Pipeline 전체 흐름](../pipeline/README.md)
- [Sentry 설정](../setup/sentry.md)
- [성능 최적화](../optimization/README.md)

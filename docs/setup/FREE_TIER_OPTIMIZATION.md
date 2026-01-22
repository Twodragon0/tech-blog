# Free Tier Optimization Guide

Sentry와 Cloudflare 무료 기능을 최대한 활용하는 가이드입니다.

---

## Sentry Free Tier (Developer Plan)

### 무료 제공 기능 (2025년 기준)

| 기능 | 무료 한도 | 활용 상태 |
|------|----------|----------|
| **Error Monitoring** | 5,000 이벤트/월 | ✅ 활성화 |
| **Tracing (Performance)** | 포함 | ✅ 5% 샘플링 |
| **Session Replay** | 50 replays/월 | ⚠️ 비활성화 (활성화 가능) |
| **Cron Monitoring** | 1 monitor | ❌ 미사용 |
| **Uptime Monitoring** | 1 monitor | ❌ 미사용 |
| **Alerts** | Email 알림 | ✅ 활성화 |
| **Custom Dashboards** | 10개 | ⚠️ 설정 필요 |
| **Logs** | 5GB/월 | ✅ warn/error만 |

### 활성화 방법

#### 1. Session Replay 활성화 (50 replays/월 무료)

`_includes/sentry.html`에서 다음 설정 변경:

```javascript
// 현재 설정 (비활성화)
replaysSessionSampleRate: 0.0,
replaysOnErrorSampleRate: 0.0,

// 추천 설정 (에러 발생 시만 녹화)
replaysSessionSampleRate: 0.0,      // 일반 세션은 녹화 안 함
replaysOnErrorSampleRate: 0.1,      // 에러 발생 시 10%만 녹화 (월 50개 제한 고려)
```

#### 2. Cron Monitoring 활성화 (1 monitor 무료)

**Sentry 대시보드에서 설정:**

1. [Sentry.io](https://sentry.io) 로그인
2. 좌측 메뉴 → **Crons** 클릭
3. **Create Monitor** 버튼 클릭
4. 설정:
   - **Name**: `daily-build-check` (원하는 이름)
   - **Schedule Type**: `Crontab`
   - **Schedule**: `0 9 * * *` (매일 오전 9시)
   - **Timezone**: `Asia/Seoul`
   - **Max Runtime**: `30 minutes`
   - **Failure Tolerance**: `1` (1번 실패 허용)

5. **Save** 클릭 후 **DSN** 복사

**GitHub Actions에서 사용:**

```yaml
# .github/workflows/daily-check.yml
name: Daily Build Check

on:
  schedule:
    - cron: '0 0 * * *'  # UTC 기준 (KST 09:00)

jobs:
  build-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Sentry Cron Check-in (Start)
        run: |
          curl -X POST "https://sentry.io/api/0/monitors/daily-build-check/checkins/" \
            -H "Authorization: DSN ${{ secrets.SENTRY_DSN }}" \
            -H "Content-Type: application/json" \
            -d '{"status": "in_progress"}'
      
      - name: Build
        run: bundle exec jekyll build
      
      - name: Sentry Cron Check-in (Complete)
        if: success()
        run: |
          curl -X POST "https://sentry.io/api/0/monitors/daily-build-check/checkins/latest/" \
            -H "Authorization: DSN ${{ secrets.SENTRY_DSN }}" \
            -H "Content-Type: application/json" \
            -d '{"status": "ok"}'
      
      - name: Sentry Cron Check-in (Failed)
        if: failure()
        run: |
          curl -X POST "https://sentry.io/api/0/monitors/daily-build-check/checkins/latest/" \
            -H "Authorization: DSN ${{ secrets.SENTRY_DSN }}" \
            -H "Content-Type: application/json" \
            -d '{"status": "error"}'
```

#### 3. Uptime Monitoring 활성화 (1 monitor 무료)

**Sentry 대시보드에서 설정:**

1. [Sentry.io](https://sentry.io) 로그인
2. 좌측 메뉴 → **Crons** 클릭
3. 상단 탭에서 **Uptime** 선택 (또는 **Monitors** → **Uptime**)
4. **Create Uptime Monitor** 클릭
5. 설정:
   - **Name**: `tech-blog-uptime`
   - **URL**: `https://tech.2twodragon.com`
   - **HTTP Method**: `GET`
   - **Check Interval**: `5 minutes` (무료는 5분 간격)
   - **Timeout**: `30 seconds`
   - **Expected Status**: `200-299`

6. **Alerting** 설정:
   - **Alert after**: `2 consecutive failures`
   - **Notify**: 이메일 알림 활성화

7. **Save** 클릭

**모니터링 확인:**
- Sentry Dashboard → Crons → Uptime 탭에서 상태 확인
- 다운타임 발생 시 이메일 알림 수신
- 가용성 통계 및 응답 시간 그래프 확인 가능

### 현재 최적화 설정

```javascript
// 동적 샘플링 (월 사용량에 따라 자동 조정)
sampleRate: dynamicSampleRate(),  // 50-100%

// 트레이싱 (Free 티어에서는 낮게)
tracesSampleRate: 0.05,  // 5%

// 에러 필터링 (불필요한 이벤트 제거)
beforeSend: filterErrors(),

// 로그 필터링 (warn/error만)
beforeSendLog: filterLogs(),
```

---

## Cloudflare Free Tier

### 무료 제공 기능

| 기능 | 설명 | 활용 상태 |
|------|------|----------|
| **CDN** | 글로벌 콘텐츠 배포 | ⚠️ Vercel 사용 중 |
| **DNS** | 빠른 DNS 확인 | ⚠️ 설정 가능 |
| **SSL/TLS** | 무료 SSL 인증서 | ⚠️ Vercel 사용 중 |
| **DDoS Protection** | 기본 DDoS 방어 | ⚠️ 설정 가능 |
| **WAF (Free Managed Ruleset)** | 기본 보안 규칙 | ⚠️ 설정 가능 |
| **Page Rules** | 3개 규칙 | ⚠️ 설정 가능 |
| **Analytics** | 기본 트래픽 분석 | ⚠️ 설정 가능 |
| **Caching** | 정적 자산 캐싱 | ⚠️ 설정 가능 |
| **Bot Fight Mode** | 기본 봇 차단 | ⚠️ 설정 가능 |
| **Browser Insights** | 성능 모니터링 | ⚠️ 설정 가능 |

### Cloudflare 설정 가이드

#### 1. DNS 설정 (Cloudflare에서 관리)

현재 Vercel을 사용 중이므로 두 가지 옵션:

**옵션 A: Cloudflare를 DNS만으로 사용 (프록시 비활성화)**
```
Type: CNAME
Name: tech
Target: cname.vercel-dns.com
Proxy: DNS only (회색 구름)
```

**옵션 B: Cloudflare 프록시 활성화 (전체 기능 사용)**
```
Type: CNAME
Name: tech
Target: cname.vercel-dns.com
Proxy: Proxied (주황색 구름)
```

> ⚠️ **주의**: 옵션 B 사용 시 Vercel의 Edge 기능과 충돌할 수 있음

#### 2. SSL/TLS 설정

```
SSL/TLS → Overview
- Encryption mode: Full (strict)
- Always Use HTTPS: On
- Automatic HTTPS Rewrites: On
- Minimum TLS Version: TLS 1.2
```

#### 3. Page Rules (3개 무료)

**Rule 1: 정적 자산 캐싱**
```
URL: tech.2twodragon.com/assets/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 year
```

**Rule 2: API 캐시 비활성화**
```
URL: tech.2twodragon.com/api/*
Settings:
  - Cache Level: Bypass
  - Disable Security: Off
```

**Rule 3: 검색엔진 최적화**
```
URL: tech.2twodragon.com/sitemap.xml
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 day
```

#### 4. Security 설정

```
Security → Settings
- Security Level: Medium
- Challenge Passage: 30 minutes
- Browser Integrity Check: On

Security → Bots
- Bot Fight Mode: On
- JavaScript Detections: On
```

#### 5. WAF (Free Managed Ruleset)

```
Security → WAF → Managed Rules
- Cloudflare Free Managed Ruleset: On (자동 배포됨)
```

#### 6. Speed 최적화

```
Speed → Optimization
- Auto Minify: JavaScript, CSS, HTML
- Brotli: On
- Early Hints: On
- Rocket Loader: Off (Jekyll과 호환성 문제)
```

#### 7. Caching 설정

```
Caching → Configuration
- Caching Level: Standard
- Browser Cache TTL: Respect Existing Headers
- Always Online: On

Caching → Cache Rules (무료 10개)
- /assets/* → Edge TTL: 1 month
- /feed.xml → Edge TTL: 1 hour
- /*.html → Edge TTL: 2 hours
```

#### 8. Analytics 활성화

```
Analytics & Logs → Web Analytics
- Enable: On (무료)
```

### Cloudflare + Vercel 함께 사용하기

두 서비스를 함께 사용할 때의 권장 설정:

```
1. Cloudflare DNS만 사용 (프록시 비활성화)
   - Vercel의 Edge Network 활용
   - Vercel의 SSL/캐싱 사용
   - Cloudflare는 DNS만 제공

2. 또는 Cloudflare 프록시 활성화
   - Cloudflare CDN + 보안 기능 사용
   - SSL Mode: Full (strict)
   - Vercel 원본 서버로 동작
```

---

## 통합 모니터링 대시보드

### Sentry 커스텀 대시보드 설정 (10개 무료)

1. **Error Overview**: 에러 트렌드, 영향받는 사용자
2. **Performance**: Web Vitals (LCP, FID, CLS)
3. **Browser Breakdown**: 브라우저별 에러 분포
4. **Page Performance**: 페이지별 로딩 시간
5. **API Errors**: /api/* 에러 추적

### Cloudflare Analytics

- 트래픽: 요청 수, 대역폭
- 보안: 차단된 위협, Bot 트래픽
- 성능: 캐시 히트율, 응답 시간

---

## 비용 절감 팁

### Sentry

1. **샘플링 최적화**: 에러는 100%, 트레이스는 5%
2. **필터링 강화**: 노이즈 에러 (CSP, 확장프로그램 등) 제외
3. **이벤트 크기 제한**: 8KB 이하로 축소
4. **중복 제거**: 동일 에러 그룹핑

### Cloudflare

1. **캐싱 극대화**: 정적 자산 장기 캐싱
2. **이미지 최적화**: Polish (Pro 이상) 대신 자체 최적화
3. **Page Rules 활용**: 3개를 효율적으로 사용

---

## 마이그레이션 체크리스트

### Cloudflare 설정 시

- [ ] DNS 레코드 이전
- [ ] SSL/TLS 모드 설정
- [ ] Page Rules 3개 설정
- [ ] WAF Free Ruleset 활성화
- [ ] Bot Fight Mode 활성화
- [ ] Analytics 활성화
- [ ] Always Online 활성화

### Sentry 설정 시

- [ ] DSN 설정 및 Loader Script 추가
- [ ] 환경별 설정 (production/development)
- [ ] 샘플링 레이트 조정
- [ ] 알림 설정 (Email)
- [ ] Session Replay 활성화 (선택)
- [ ] 커스텀 대시보드 생성

---

## 참고 자료

- [Sentry Pricing](https://sentry.io/pricing/)
- [Sentry Free Tier Documentation](https://docs.sentry.io/pricing/)
- [Cloudflare Free Plan](https://www.cloudflare.com/plans/free/)
- [Cloudflare WAF Documentation](https://developers.cloudflare.com/waf/)

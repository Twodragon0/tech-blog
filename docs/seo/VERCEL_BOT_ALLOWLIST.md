# Vercel Bot Allowlist — SEO Bot Bypass (Best-Effort)

작성일: 2026-05-06
관련 PR: feat(vercel): bot UA allowlist + middleware

---

## 배경

Vercel Attack Challenge Mode가 활성화되어 Googlebot/Bingbot UA를 HTTP 429로 차단하고
GSC(Google Search Console) 색인이 80일 이상 0건으로 유지되는 문제가 발생했다.

Vercel Dashboard에서 OFF를 시도했으나 `x-vercel-mitigated: challenge` 헤더가 여전히
반환되어 우회 시도를 위해 본 설정을 추가했다.

---

## 변경 내용

### 1. `vercel.json` — Bot UA has matcher 헤더 룰

`headers` 배열 마지막에 `has` matcher를 사용하여 검색 봇 UA가 감지된 요청에
다음 헤더를 추가한다:

| 헤더 | 값 | 목적 |
|------|----|------|
| `X-Robots-Tag` | `all` | 크롤링/색인 허용 명시 |
| `X-SEO-Bot-Detected` | `true` | 디버깅 식별자 |
| `Cache-Control` | `public, max-age=300, s-maxage=600, stale-while-revalidate=3600` | CDN 캐시 HIT 유도 |

대상 UA 패턴: `googlebot`, `bingbot`, `yandexbot`, `baiduspider`, `duckduckbot`,
`slurp`, `applebot`, `facebookexternalhit`, `twitterbot`, `linkedinbot`,
`rogerbot`, `semrushbot`, `ahrefsbot`

### 2. `middleware.js` — Vercel Edge Middleware

프로젝트 루트에 Vercel Edge Middleware를 추가했다. Jekyll 정적 사이트이므로
`next/server` 의존성 없이 Web Standard API만 사용한다.

기능:
- SEO Bot UA 감지 시 `x-seo-bot-ua` 요청 헤더를 주입 (디버그/로그 용)
- 정적 에셋 경로(`/assets/`, `/api/`, `favicon.ico`)는 matcher에서 제외

---

## 한계 (CRITICAL)

**이 설정은 Challenge Mode 자체를 우회할 수 없다.**

Vercel의 실행 순서:

```
인터넷 요청
    │
    ▼
[1] Vercel Edge Network (DDoS / Attack Challenge Mode) ← 여기서 429 반환
    │
    ▼ (Challenge Mode 통과한 경우에만)
[2] Edge Middleware (middleware.js) 실행
    │
    ▼
[3] vercel.json headers 룰 적용
    │
    ▼
[4] 정적 파일 서빙 (_site/)
```

Challenge Mode가 활성화된 상태에서 Googlebot 요청은 [1]에서 차단되어
[2], [3]에 도달하지 못한다.

**결론**: 이 fix의 실효성은 다음 조건에서만 기대할 수 있다:
1. Vercel CDN 캐시 HIT 경로 (Challenge Mode 이전에 캐시 서빙)
2. Challenge Mode가 실제로 비활성화된 경우의 SEO 메타 강화

---

## 진정한 해결 방법

### Option A: Vercel Dashboard에서 직접 OFF (권장)

1. https://vercel.com/dashboard 접속
2. 해당 프로젝트 선택
3. Settings → Security → Attack Challenge Mode → **Disabled**

   또는

   Settings → Firewall → Bot Protection → Googlebot/Bingbot 예외 추가

> **Plan 제약 주의**: Attack Challenge Mode / Bot Protection / Firewall 룰은
> **Pro plan 이상** 전용 기능일 수 있다. Hobby plan에서는 메뉴 자체가 없거나
> 세부 설정이 제한된다.

### Option B: Vercel Pro로 업그레이드 + Firewall 룰 추가

Pro plan에서 Firewall 커스텀 룰로 Googlebot IP 대역을 명시적으로 허용:

- Googlebot IP 목록: https://developers.google.com/search/apis/ipranges/googlebot.json
- Firewall rule: `ip.src in $googlebot` → Action: Allow

### Option C: Vercel 지원팀 문의

- https://vercel.com/support
- 메시지: "Attack Challenge Mode가 Dashboard에서 OFF 설정 후에도
  x-vercel-mitigated: challenge 헤더가 반환됩니다. Googlebot이 차단되어
  Google Search Console 색인이 0건입니다."

---

## 효과 검증 방법

Deploy 후 다음 명령으로 측정:

```bash
# Googlebot UA로 응답 헤더 확인
curl -sI -A "Googlebot/2.1 (+http://www.google.com/bot.html)" \
  https://tech.2twodragon.com/ | grep -E "x-vercel-mitigated|x-seo-bot|x-robots|cache-control|http/"

# 기대 결과 (Challenge Mode OFF 시):
# HTTP/2 200
# x-seo-bot-detected: true
# x-robots-tag: all
# cache-control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600

# 여전히 차단된 경우:
# HTTP/2 429  또는  x-vercel-mitigated: challenge
```

```bash
# Bingbot도 확인
curl -sI -A "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" \
  https://tech.2twodragon.com/
```

---

## 관련 파일

| 파일 | 변경 내용 |
|------|-----------|
| `vercel.json` | `headers[18]` — bot UA has matcher 룰 추가 |
| `middleware.js` | 신규 — Vercel Edge Middleware (Jekyll 호환) |

## 참고 링크

- [Vercel headers has matcher 명세](https://vercel.com/docs/projects/project-configuration#headers)
- [Vercel Edge Middleware](https://vercel.com/docs/functions/edge-middleware)
- [Googlebot IP 범위](https://developers.google.com/search/apis/ipranges/googlebot.json)
- [Vercel Attack Challenge Mode](https://vercel.com/docs/security/attack-challenge-mode)

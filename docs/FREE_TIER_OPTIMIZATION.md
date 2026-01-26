# Free Tier Optimization Guide

무료 티어 서비스들을 보안, 비용 최적화, 운영 효율성 관점에서 최대한 활용하기 위한 가이드입니다.

## 목차

1. [Vercel Hobby Plan](#1-vercel-hobby-plan)
2. [Upstash Redis Free Tier](#2-upstash-redis-free-tier)
3. [Prisma Postgres (Neon) / Prisma Accelerate](#3-prisma-postgres--prisma-accelerate)
4. [통합 아키텍처](#4-통합-아키텍처)
5. [보안 체크리스트](#5-보안-체크리스트)
6. [모니터링 및 알림](#6-모니터링-및-알림)

---

## 1. Vercel Hobby Plan

### 1.1 무료 티어 제한사항 (2025년 기준)

| 리소스 | Hobby (무료) | Pro ($20/월) |
|--------|--------------|--------------|
| **Serverless Function Timeout** | 10초 (기본), 최대 300초 설정 가능 | 15초 (기본), 최대 800초 |
| **Function Memory** | 최대 2GB | 최대 4GB |
| **Function Invocations** | 1,000,000회/월 | 무제한 (유료) |
| **Active CPU** | 4 CPU-hours/월 | 유료 (종량제) |
| **Provisioned Memory** | 360 GB-hours/월 | 유료 (종량제) |
| **Fast Data Transfer** | 100 GB/월 | 1 TB/월 |
| **Build Time** | 100 hours/월 | 유료 |
| **Deployments/Day** | 100개 | 6,000개 |
| **Concurrent Builds** | 1개 | 12개 |
| **Projects** | 200개 | 무제한 |

### 1.2 비용 최적화 전략

#### a) Function Duration 최적화

```javascript
// vercel.json
{
  "functions": {
    "api/chat.js": {
      "maxDuration": 60,  // Hobby에서도 최대 300초까지 설정 가능
      "memory": 1024      // 1GB로 설정 (기본값)
    }
  }
}
```

**권장사항:**
- `maxDuration`을 필요한 만큼만 설정 (타임아웃 비용 절감)
- 실제 실행 시간은 25초 이내로 유지 (안전 마진)
- 긴 작업은 Upstash Workflow로 분리

#### b) 정적 자산 캐싱 극대화

```javascript
// vercel.json headers 설정
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/posts/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=10800, s-maxage=10800, stale-while-revalidate=259200" }
      ]
    }
  ]
}
```

#### c) Edge Middleware 활용 (무료)

```javascript
// middleware.js - Edge에서 실행 (무료)
export function middleware(request) {
  // Rate limiting, Geo-blocking 등을 Edge에서 처리
  const country = request.geo?.country || 'KR';
  
  // 봇 차단 (Edge에서 무료로 처리)
  const userAgent = request.headers.get('user-agent') || '';
  if (isBotUserAgent(userAgent)) {
    return new Response('Forbidden', { status: 403 });
  }
  
  return NextResponse.next();
}
```

### 1.3 보안 설정

```javascript
// vercel.json 보안 헤더
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
        { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" }
      ]
    }
  ]
}
```

---

## 2. Upstash Redis Free Tier

### 2.1 무료 티어 제한사항 (2025년 3월 업데이트)

| 리소스 | Free Tier | Pay-as-you-go |
|--------|-----------|---------------|
| **Commands** | 500K/월 (이전 10K/일 → 변경됨) | $0.20/100K requests |
| **Data Size** | 256 MB | 100 GB |
| **Bandwidth** | 10 GB/월 | 첫 200GB 무료, 이후 $0.03/GB |
| **Max Request/Sec** | 10,000 | 10,000 |
| **Max Request Size** | 10 MB | 10 MB |
| **Databases** | 1개 | 무제한 |

### 2.2 Rate Limiting 구현 (비용 효율적)

```javascript
// lib/ratelimit.js
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

// 환경 변수에서 Redis 설정
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

// 사용자 티어별 Rate Limiter
export const ratelimit = {
  // 익명 사용자: 분당 10회
  anonymous: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, "1 m"),
    prefix: "ratelimit:anon",
    analytics: false, // 비용 절감: analytics 비활성화
  }),
  
  // 인증된 사용자: 분당 30회
  authenticated: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(30, "1 m"),
    prefix: "ratelimit:auth",
    analytics: false,
  }),
};

// 사용 예시
export async function checkRateLimit(identifier, tier = 'anonymous') {
  const limiter = ratelimit[tier] || ratelimit.anonymous;
  const { success, limit, remaining, reset } = await limiter.limit(identifier);
  
  return {
    success,
    headers: {
      'X-RateLimit-Limit': limit.toString(),
      'X-RateLimit-Remaining': remaining.toString(),
      'X-RateLimit-Reset': reset.toString(),
    }
  };
}
```

### 2.3 캐싱 전략 (월 500K 명령어 최적화)

```javascript
// lib/cache.js
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

// 캐시 래퍼 함수
export async function withCache(key, ttlSeconds, fetchFn) {
  // 1. 캐시 확인 (1 command)
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // 2. 데이터 fetch
  const data = await fetchFn();
  
  // 3. 캐시 저장 (1 command)
  await redis.setex(key, ttlSeconds, JSON.stringify(data));
  
  return data;
}

// 사용 예시: API 응답 캐싱
const result = await withCache(
  `api:weather:${city}`,
  3600, // 1시간 캐시
  () => fetchWeatherAPI(city)
);
```

### 2.4 명령어 사용량 추정

| 기능 | 예상 명령어/일 | 월간 합계 |
|------|---------------|-----------|
| Rate Limiting (1000 req/일) | 1,000 | 30,000 |
| API 캐싱 (500 req/일) | 1,000 | 30,000 |
| 세션 관리 (100 users/일) | 200 | 6,000 |
| **합계** | **2,200** | **~66,000** |

**여유분**: 500K - 66K = **434K 명령어** (87% 여유)

---

## 3. Prisma Postgres / Prisma Accelerate

### 3.1 Prisma Postgres Free Tier (Neon 기반)

| 리소스 | Free Tier |
|--------|-----------|
| **Storage** | 512 MB |
| **Compute** | 0.25 vCPU (autoscale) |
| **Branching** | 10개 |
| **Connection Limit** | 고정 10개 |

### 3.2 Prisma Accelerate Free Tier

| 리소스 | Free Tier | Growth |
|--------|-----------|--------|
| **Queries/Month** | 100,000 | $0.15/1000 초과분 |
| **Connection Pooling** | 포함 | 포함 |
| **Query Caching** | 포함 | 포함 |
| **Edge Deployment** | 포함 | 포함 |

### 3.3 Serverless 환경 최적화

```javascript
// prisma/client.js
import { PrismaClient } from '@prisma/client';
import { withAccelerate } from '@prisma/extension-accelerate';

// Singleton 패턴 (Cold Start 최소화)
const globalForPrisma = globalThis;

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient().$extends(withAccelerate());

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
```

### 3.4 쿼리 캐싱 활용

```javascript
// Accelerate 캐싱 활용
const posts = await prisma.post.findMany({
  cacheStrategy: {
    ttl: 60,    // 60초 캐시
    swr: 300,   // 5분 stale-while-revalidate
  },
  where: { published: true },
  take: 10,
});
```

---

## 4. 통합 아키텍처

### 4.1 권장 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel Edge Network                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Static    │  │   Edge      │  │  Serverless │     │
│  │   Assets    │  │  Middleware │  │  Functions  │     │
│  │  (CDN)     │  │ (무료)      │  │  (Hobby)    │     │
│  └─────────────┘  └─────────────┘  └──────┬──────┘     │
└─────────────────────────────────────────────┼───────────┘
                                              │
              ┌───────────────────────────────┼───────────┐
              │                               │           │
              ▼                               ▼           │
     ┌─────────────────┐           ┌─────────────────┐   │
     │  Upstash Redis  │           │ Prisma Postgres │   │
     │  (Free Tier)    │           │   (Free Tier)   │   │
     │                 │           │                 │   │
     │ • Rate Limiting │           │ • 512MB Storage │   │
     │ • 세션 캐싱     │           │ • Connection    │   │
     │ • API 캐싱      │           │   Pooling       │   │
     │                 │           │                 │   │
     │ 500K cmds/월    │           │ 100K queries/월 │   │
     └─────────────────┘           └─────────────────┘   │
              │                               │           │
              └───────────────────────────────┴───────────┘
                          Prisma Accelerate
                       (Connection Pooling & Cache)
```

### 4.2 환경 변수 설정

```bash
# .env.example

# Vercel
VERCEL_ENV=production
VERCEL_URL=https://tech.2twodragon.com

# Upstash Redis (Rate Limiting & Caching)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxxxx

# Prisma Postgres (via Accelerate)
DATABASE_URL=prisma://accelerate.prisma-data.net/?api_key=xxx
DIRECT_URL=postgres://user:pass@xxx.neon.tech/dbname

# DeepSeek API
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
```

---

## 5. 보안 체크리스트

### 5.1 환경 변수 보안

- [ ] `.env`는 절대 Git에 커밋하지 않음 (`.gitignore`에 포함)
- [ ] Vercel Dashboard에서 환경 변수 암호화 설정
- [ ] 환경별 (Production/Preview/Development) 분리
- [ ] API 키는 `sk-`로 시작하는지 검증

### 5.2 API 보안

- [ ] CORS 설정: 허용된 Origin만 허용
- [ ] Rate Limiting 적용 (Upstash Redis)
- [ ] Bot 차단 (User-Agent 검증)
- [ ] 입력 검증 및 XSS 방지
- [ ] SQL Injection 방지 (Prisma 사용 시 자동)

### 5.3 인프라 보안

- [ ] HTTPS 강제 (Vercel 자동 적용)
- [ ] Security Headers 설정
- [ ] CSP (Content Security Policy) 설정
- [ ] Upstash Redis TLS 암호화 (기본 적용)

---

## 6. 모니터링 및 알림

### 6.1 Vercel 모니터링

```javascript
// Vercel Analytics 활용 (무료)
// _app.js 또는 layout.js
import { Analytics } from '@vercel/analytics/react';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Analytics />
    </>
  );
}
```

### 6.2 사용량 대시보드 체크 주기

| 서비스 | 체크 주기 | 알림 임계값 |
|--------|-----------|-------------|
| Vercel Function Duration | 주간 | 80 CPU-hours (80%) |
| Upstash Commands | 주간 | 400K (80%) |
| Prisma Queries | 주간 | 80K (80%) |
| Data Transfer | 월간 | 80 GB (80%) |

### 6.3 비용 알림 설정

Vercel Dashboard > Settings > Billing > Spend Management에서:
- **Hard Limit**: 무료 티어 한도 (자동 차단)
- **Soft Limit**: 80% 도달 시 이메일 알림

---

## 부록: 비용 비교 (월간)

### 시나리오: 월 10,000 방문자 블로그

| 서비스 | Free Tier | 예상 비용 |
|--------|-----------|-----------|
| **Vercel Hosting** | Hobby Plan | **$0** |
| **Upstash Redis** | 500K cmds | **$0** |
| **Prisma Postgres** | 512MB + Accelerate | **$0** |
| **DeepSeek API** | 1000 채팅 | ~**$0.50** |
| **합계** | | **~$0.50/월** |

### 스케일업 시나리오: 월 100,000 방문자

| 서비스 | Plan | 예상 비용 |
|--------|------|-----------|
| **Vercel Hosting** | Pro | **$20** |
| **Upstash Redis** | Pay-as-you-go | **$2** |
| **Prisma Postgres** | Growth | **$5** |
| **DeepSeek API** | 10,000 채팅 | ~**$5** |
| **합계** | | **~$32/월** |

---

## 참고 자료

- [Vercel Pricing](https://vercel.com/pricing)
- [Vercel Limits](https://vercel.com/docs/limits)
- [Upstash Pricing](https://upstash.com/pricing)
- [Prisma Accelerate](https://www.prisma.io/accelerate)
- [Neon Pricing](https://neon.tech/pricing)

---

*Last Updated: 2026-01-26*

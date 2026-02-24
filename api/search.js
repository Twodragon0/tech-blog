// Vercel Serverless Function for Blog Post Search API
// 보안: 입력 검증, Rate Limiting, CORS 적용
// 성능: Upstash Redis 캐싱으로 반복 쿼리 최적화
// 검색: PostgreSQL Full-Text Search (simple dictionary for Korean+English)
//
// 사용법:
// GET /api/search?q=kubernetes
// GET /api/search?q=보안+자동화
//
// 응답 형식:
// {
//   "results": [{ "title": "...", "url": "...", "excerpt": "...", ... }],
//   "total": 5,
//   "cached": false,
//   "query": "kubernetes",
//   "took": 45
// }

import { PrismaClient } from '@prisma/client';
import { checkRateLimit, setRateLimitHeaders } from './lib/ratelimit.js';

// 최적화 설정
const CONFIG = {
  MAX_QUERY_LENGTH: 200,
  MIN_QUERY_LENGTH: 2,
  MAX_RESULTS: 20,
  CACHE_TTL: parseInt(process.env.SEARCH_CACHE_TTL || '3600', 10), // 1 hour
  RATE_LIMIT_RPM: parseInt(process.env.SEARCH_RATE_LIMIT_RPM || '30', 10),
  EXCERPT_LENGTH: 200,
};

// Prisma Client singleton (reused across warm invocations)
let prismaInstance = null;
function getPrisma() {
  if (!prismaInstance) {
    prismaInstance = new PrismaClient({ log: ['error'] });
  }
  return prismaInstance;
}

// Upstash Redis REST client (same pattern as api/lib/ratelimit.js)
class SearchRedis {
  constructor(url, token) {
    this.url = url;
    this.token = token;
  }

  async fetch(command, args = []) {
    const response = await fetch(`${this.url}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify([command, ...args]),
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.result;
  }

  async get(key) { return this.fetch('GET', [key]); }
  async setex(key, ttl, value) { return this.fetch('SET', [key, value, 'EX', ttl]); }
}

// Redis instance (lazy init)
let redisInstance = null;
function getRedis() {
  if (redisInstance) return redisInstance;
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (url && token) {
    redisInstance = new SearchRedis(url, token);
  }
  return redisInstance;
}

// Request ID 생성
function generateRequestId() {
  return `search-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Bot 보호: User-Agent 검증
function isBotUserAgent(userAgent) {
  if (!userAgent) return true;
  const botPatterns = [/bot/i, /crawler/i, /spider/i, /scraper/i, /curl/i, /wget/i, /python-requests/i];
  const allowedPatterns = [/mozilla/i, /chrome/i, /safari/i, /firefox/i, /edge/i, /mobile/i];
  if (allowedPatterns.some(p => p.test(userAgent))) return false;
  return botPatterns.some(p => p.test(userAgent));
}

// CORS 검증
function isAllowedOrigin(origin) {
  if (!origin) return false;
  const allowed = [
    'https://tech.2twodragon.com',
    'https://www.tech.2twodragon.com',
    ...(process.env.NODE_ENV === 'development' ? [
      'http://localhost:4000',
      'http://localhost:3000',
      'http://127.0.0.1:4000',
    ] : []),
  ];
  return allowed.includes(origin);
}

// 검색 쿼리 정제: SQL injection 방지 + tsquery 호환
function sanitizeQuery(raw) {
  let s = raw.normalize('NFC');
  s = s.replace(/[\x00-\x1F\x7F]/g, '');
  s = s.replace(/<[^>]*>/g, '');
  s = s.replace(/[\\'"`;]/g, '');
  s = s.replace(/[!&|():*<>~]/g, ' ');
  s = s.replace(/\s+/g, ' ');
  return s.trim();
}

// 검색어를 tsquery 형식으로 변환
function toTsQuery(query) {
  const terms = query.split(/\s+/).filter(t => t.length >= 1);
  if (terms.length === 0) return null;
  // 각 단어를 :* 접두사 매칭으로 변환 (부분 매칭 지원)
  return terms.map(t => `${t}:*`).join(' & ');
}

// 날짜 포맷팅
function formatDate(date) {
  if (!date) return '';
  const d = new Date(date);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}. ${m}. ${day}`;
}

export default async function handler(req, res) {
  const startTime = Date.now();
  const requestId = generateRequestId();

  // CORS 헤더
  let origin = req.headers.origin || '';
  if (!origin && req.headers.referer) {
    try { origin = new URL(req.headers.referer).origin; } catch { origin = ''; }
  }
  if (isAllowedOrigin(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Credentials', 'false');

  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('X-Request-ID', requestId);

  // Preflight
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  // GET only
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed', allowed: 'GET' });
  }

  try {
    // Bot 보호
    const userAgent = req.headers['user-agent'] || '';
    if (process.env.NODE_ENV === 'production' && isBotUserAgent(userAgent)) {
      return res.status(403).json({ error: 'forbidden' });
    }

    // Rate Limiting
    const clientIp = req.headers['x-forwarded-for']?.split(',')[0]?.trim()
      || req.headers['x-real-ip']
      || req.socket?.remoteAddress
      || 'unknown';

    const rateLimitResult = await checkRateLimit(clientIp, 'anonymous');
    setRateLimitHeaders(res, rateLimitResult.headers);

    if (!rateLimitResult.success) {
      return res.status(429).json({
        error: 'rate_limited',
        retryAfter: rateLimitResult.retryAfter,
      });
    }

    // 쿼리 파라미터 추출 및 검증
    const rawQuery = (req.query.q || '').trim();

    if (rawQuery.length < CONFIG.MIN_QUERY_LENGTH) {
      return res.status(400).json({
        error: 'query_too_short',
        minLength: CONFIG.MIN_QUERY_LENGTH,
      });
    }

    if (rawQuery.length > CONFIG.MAX_QUERY_LENGTH) {
      return res.status(400).json({
        error: 'query_too_long',
        maxLength: CONFIG.MAX_QUERY_LENGTH,
      });
    }

    const query = sanitizeQuery(rawQuery);
    if (!query || query.length < CONFIG.MIN_QUERY_LENGTH) {
      return res.status(400).json({ error: 'invalid_query' });
    }

    // Redis 캐시 확인
    const redis = getRedis();
    const cacheKey = `search:${query.toLowerCase()}`;
    let cached = false;

    if (redis) {
      try {
        const cachedResult = await redis.get(cacheKey);
        if (cachedResult) {
          const parsed = typeof cachedResult === 'string'
            ? JSON.parse(cachedResult)
            : cachedResult;

          // 비동기로 검색 로그 기록 (응답 지연 없음)
          logSearchQuery(query, parsed.length, true).catch(() => {});

          return res.status(200).json({
            results: parsed,
            total: parsed.length,
            cached: true,
            query,
            took: Date.now() - startTime,
          });
        }
      } catch (cacheErr) {
        // Redis 오류 시 캐시 무시 (fail-open)
        console.warn(`[${requestId}] Cache read error:`, cacheErr.message);
      }
    }

    // Prisma 풀텍스트 검색
    const prisma = getPrisma();
    let results = [];

    const tsquery = toTsQuery(query);

    if (tsquery) {
      try {
        const limit = CONFIG.MAX_RESULTS;
        results = await prisma.$queryRaw`
          SELECT 
            id, title, excerpt, url, category, tags, "publishedDate", "imageUrl",
            ts_rank(
              setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
              setweight(to_tsvector('simple', COALESCE(excerpt, '')), 'B') ||
              setweight(to_tsvector('simple', COALESCE(content, '')), 'C'),
              to_tsquery('simple', ${tsquery})
            ) as rank
          FROM "BlogPost"
          WHERE 
            to_tsvector('simple', COALESCE(title, '')) @@ to_tsquery('simple', ${tsquery})
            OR to_tsvector('simple', COALESCE(content, '')) @@ to_tsquery('simple', ${tsquery})
            OR to_tsvector('simple', COALESCE(excerpt, '')) @@ to_tsquery('simple', ${tsquery})
          ORDER BY rank DESC
          LIMIT ${limit}
        `;
      } catch (ftsErr) {
        console.warn(`[${requestId}] FTS query error:`, ftsErr.message);
        results = [];
      }
    }

    if (results.length === 0) {
      try {
        const likePattern = `%${query}%`;
        const limit = CONFIG.MAX_RESULTS;
        results = await prisma.$queryRaw`
          SELECT 
            id, title, excerpt, url, category, tags, "publishedDate", "imageUrl",
            0.0 as rank
          FROM "BlogPost"
          WHERE 
            title ILIKE ${likePattern}
            OR content ILIKE ${likePattern}
            OR excerpt ILIKE ${likePattern}
          ORDER BY "publishedDate" DESC
          LIMIT ${limit}
        `;
      } catch (likeErr) {
        console.warn(`[${requestId}] ILIKE query error:`, likeErr.message);
        results = [];
      }
    }

    // 결과 포맷팅
    const formattedResults = results.map(r => ({
      title: r.title,
      url: r.url,
      excerpt: (r.excerpt || '').substring(0, CONFIG.EXCERPT_LENGTH),
      category: r.category,
      tags: r.tags || [],
      date: formatDate(r.publishedDate),
      imageUrl: r.imageUrl,
      rank: parseFloat(r.rank) || 0,
    }));

    // Redis에 캐시 저장
    if (redis && formattedResults.length > 0) {
      try {
        await redis.setex(cacheKey, CONFIG.CACHE_TTL, JSON.stringify(formattedResults));
      } catch (cacheErr) {
        console.warn(`[${requestId}] Cache write error:`, cacheErr.message);
      }
    }

    // 비동기로 검색 로그 기록
    logSearchQuery(query, formattedResults.length, false).catch(() => {});

    const took = Date.now() - startTime;
    if (took > 3000) {
      console.warn(`[${requestId}] Slow search: "${query}" took ${took}ms`);
    }

    return res.status(200).json({
      results: formattedResults,
      total: formattedResults.length,
      cached: false,
      query,
      took,
    });

  } catch (error) {
    console.error(`[${requestId}] Search error:`, error.message);

    return res.status(503).json({
      results: [],
      total: 0,
      error: 'search_unavailable',
      fallback: true,
      query: req.query.q || '',
      took: Date.now() - startTime,
    });
  }
}

// 검색 로그 비동기 기록 (응답 지연 없음)
async function logSearchQuery(query, resultCount, cached) {
  try {
    const prisma = getPrisma();
    await prisma.searchQuery.create({
      data: {
        query: query.substring(0, 200),
        results: resultCount,
        cached,
      },
    });
  } catch (err) {
    // 로그 실패는 무시 (핵심 기능 아님)
  }
}

/**
 * Upstash Redis Rate Limiting Utility
 * 
 * 보안, 비용 최적화, 운영 효율성을 위한 Rate Limiting 구현
 * 
 * Free Tier Limits (2025년 기준):
 * - 500K commands/month
 * - 256MB storage
 * - 10GB bandwidth/month
 * 
 * 비용 최적화 전략:
 * - analytics: false로 설정하여 추가 명령어 사용 방지
 * - 적절한 TTL 설정으로 불필요한 키 저장 방지
 * - 필요한 경우에만 Redis 호출 (클라이언트 사이드 캐싱 활용)
 */

// Upstash Redis REST API 클라이언트 (서버리스 환경에 최적화)
class UpstashRedis {
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

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Upstash Redis error: ${error}`);
    }

    const data = await response.json();
    return data.result;
  }

  // 기본 Redis 명령어들
  async get(key) {
    return this.fetch('GET', [key]);
  }

  async set(key, value, options = {}) {
    const args = [key, value];
    if (options.ex) args.push('EX', options.ex);
    if (options.px) args.push('PX', options.px);
    if (options.nx) args.push('NX');
    if (options.xx) args.push('XX');
    return this.fetch('SET', args);
  }

  async incr(key) {
    return this.fetch('INCR', [key]);
  }

  async expire(key, seconds) {
    return this.fetch('EXPIRE', [key, seconds]);
  }

  async ttl(key) {
    return this.fetch('TTL', [key]);
  }

  async del(key) {
    return this.fetch('DEL', [key]);
  }

  // Pipeline 지원 (비용 최적화: 여러 명령어를 한 번에 실행)
  async pipeline(commands) {
    const response = await fetch(`${this.url}/pipeline`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(commands),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Upstash Redis pipeline error: ${error}`);
    }

    return response.json();
  }
}

/**
 * Sliding Window Rate Limiter
 * 
 * 알고리즘: Sliding Window Counter
 * - 현재 윈도우와 이전 윈도우의 가중 평균을 사용
 * - 정확도와 메모리 효율성의 균형
 * 
 * Redis 명령어 사용:
 * - limit() 호출당 2-3 commands (INCR + EXPIRE 또는 GET + INCR + EXPIRE)
 */
class SlidingWindowRateLimiter {
  constructor(redis, options = {}) {
    this.redis = redis;
    this.prefix = options.prefix || 'ratelimit';
    this.maxRequests = options.maxRequests || 10;
    this.windowMs = options.windowMs || 60000; // 1분
  }

  /**
   * Rate limit 체크
   * 
   * @param {string} identifier - 사용자 식별자 (IP, userId 등)
   * @returns {Promise<{success: boolean, limit: number, remaining: number, reset: number}>}
   */
  async limit(identifier) {
    const now = Date.now();
    const windowStart = Math.floor(now / this.windowMs) * this.windowMs;
    const key = `${this.prefix}:${identifier}:${windowStart}`;
    const windowSeconds = Math.ceil(this.windowMs / 1000);

    try {
      // Pipeline으로 INCR과 EXPIRE를 한 번에 실행 (1 HTTP call)
      const results = await this.redis.pipeline([
        ['INCR', key],
        ['EXPIRE', key, windowSeconds],
      ]);

      const currentCount = results[0].result || 0;
      const remaining = Math.max(0, this.maxRequests - currentCount);
      const reset = windowStart + this.windowMs;

      return {
        success: currentCount <= this.maxRequests,
        limit: this.maxRequests,
        remaining,
        reset: Math.ceil(reset / 1000), // Unix timestamp in seconds
        retryAfter: currentCount > this.maxRequests 
          ? Math.ceil((reset - now) / 1000) 
          : 0,
      };
    } catch (error) {
      // Redis 오류 시 요청 허용 (fail-open)
      // 프로덕션에서는 로깅 추가 권장
      console.error('[RateLimit] Redis error:', error.message);
      return {
        success: true,
        limit: this.maxRequests,
        remaining: this.maxRequests,
        reset: Math.ceil((now + this.windowMs) / 1000),
        retryAfter: 0,
        error: 'Redis unavailable, allowing request',
      };
    }
  }
}

/**
 * In-Memory Rate Limiter (Fallback)
 * 
 * Redis를 사용할 수 없는 경우의 폴백
 * 주의: 다중 인스턴스 환경에서는 정확하지 않음
 */
class InMemoryRateLimiter {
  constructor(options = {}) {
    this.maxRequests = options.maxRequests || 10;
    this.windowMs = options.windowMs || 60000;
    this.store = new Map();
    
    // 주기적으로 오래된 레코드 정리 (메모리 누수 방지)
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      for (const [key, record] of this.store.entries()) {
        if (record.resetAt < now) {
          this.store.delete(key);
        }
      }
    }, this.windowMs);
  }

  async limit(identifier) {
    const now = Date.now();
    const record = this.store.get(identifier);

    if (!record || record.resetAt < now) {
      // 새 윈도우 시작
      this.store.set(identifier, {
        count: 1,
        resetAt: now + this.windowMs,
      });
      return {
        success: true,
        limit: this.maxRequests,
        remaining: this.maxRequests - 1,
        reset: Math.ceil((now + this.windowMs) / 1000),
        retryAfter: 0,
      };
    }

    record.count++;
    const remaining = Math.max(0, this.maxRequests - record.count);
    const success = record.count <= this.maxRequests;

    return {
      success,
      limit: this.maxRequests,
      remaining,
      reset: Math.ceil(record.resetAt / 1000),
      retryAfter: success ? 0 : Math.ceil((record.resetAt - now) / 1000),
    };
  }

  // 정리 (프로세스 종료 시 호출)
  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

/**
 * Rate Limiter Factory
 * 
 * 환경 변수에 따라 적절한 Rate Limiter 반환
 */
function createRateLimiter(tier = 'anonymous') {
  const useUpstash = process.env.USE_UPSTASH_RATELIMIT === 'true';
  const upstashUrl = process.env.UPSTASH_REDIS_REST_URL;
  const upstashToken = process.env.UPSTASH_REDIS_REST_TOKEN;

  // 티어별 설정
  const tierConfigs = {
    anonymous: {
      maxRequests: parseInt(process.env.RATELIMIT_ANONYMOUS_RPM) || 10,
      windowMs: 60000,
      prefix: 'ratelimit:anon',
    },
    authenticated: {
      maxRequests: parseInt(process.env.RATELIMIT_AUTHENTICATED_RPM) || 30,
      windowMs: 60000,
      prefix: 'ratelimit:auth',
    },
  };

  const config = tierConfigs[tier] || tierConfigs.anonymous;

  // Upstash Redis 사용 가능 여부 확인
  if (useUpstash && upstashUrl && upstashToken) {
    const redis = new UpstashRedis(upstashUrl, upstashToken);
    return new SlidingWindowRateLimiter(redis, config);
  }

  // Fallback: In-Memory Rate Limiter
  console.warn('[RateLimit] Using in-memory rate limiter. Not recommended for production with multiple instances.');
  return new InMemoryRateLimiter(config);
}

// Singleton instances (메모리 효율성)
let anonymousLimiter = null;
let authenticatedLimiter = null;

/**
 * Rate Limit 체크 함수
 * 
 * @param {string} identifier - 사용자 식별자
 * @param {string} tier - 'anonymous' 또는 'authenticated'
 * @returns {Promise<{success: boolean, headers: Object}>}
 */
export async function checkRateLimit(identifier, tier = 'anonymous') {
  // Lazy initialization
  if (tier === 'authenticated') {
    if (!authenticatedLimiter) {
      authenticatedLimiter = createRateLimiter('authenticated');
    }
    const result = await authenticatedLimiter.limit(identifier);
    return formatResult(result);
  }

  if (!anonymousLimiter) {
    anonymousLimiter = createRateLimiter('anonymous');
  }
  const result = await anonymousLimiter.limit(identifier);
  return formatResult(result);
}

function formatResult(result) {
  return {
    success: result.success,
    headers: {
      'X-RateLimit-Limit': result.limit.toString(),
      'X-RateLimit-Remaining': result.remaining.toString(),
      'X-RateLimit-Reset': result.reset.toString(),
      ...(result.retryAfter > 0 && { 'Retry-After': result.retryAfter.toString() }),
    },
    retryAfter: result.retryAfter,
    error: result.error,
  };
}

/**
 * Rate Limit 응답 헤더 설정 헬퍼
 * 
 * @param {Response} res - Vercel Response 객체
 * @param {Object} headers - Rate limit 헤더
 */
export function setRateLimitHeaders(res, headers) {
  Object.entries(headers).forEach(([key, value]) => {
    res.setHeader(key, value);
  });
}

export { UpstashRedis, SlidingWindowRateLimiter, InMemoryRateLimiter };

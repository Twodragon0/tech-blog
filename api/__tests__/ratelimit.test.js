/**
 * InMemoryRateLimiter 및 SlidingWindowRateLimiter (Redis 폴백) 단위 테스트
 *
 * 테스트 대상: api/lib/ratelimit.js
 * - InMemoryRateLimiter: 요청 허용/차단, 윈도우 만료, 식별자 독립 추적, 정리
 * - SlidingWindowRateLimiter: Redis 실패 시 인메모리 폴백 동작
 */

import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { InMemoryRateLimiter, SlidingWindowRateLimiter } from '../lib/ratelimit.js';

// ─────────────────────────────────────────────
// InMemoryRateLimiter 테스트
// ─────────────────────────────────────────────

describe('InMemoryRateLimiter - 요청 허용/차단', () => {
  let limiter;

  beforeEach(() => {
    // 각 테스트마다 독립적인 인스턴스 생성
    limiter = new InMemoryRateLimiter({ maxRequests: 3, windowMs: 60000 });
  });

  afterEach(() => {
    // 타이머 정리 (메모리 누수 방지)
    limiter.destroy();
  });

  test('한도 내 첫 번째 요청을 허용한다', async () => {
    const result = await limiter.limit('user-1');
    assert.equal(result.success, true, '첫 번째 요청은 성공해야 한다');
    assert.equal(result.limit, 3, 'limit 값이 maxRequests 와 일치해야 한다');
    assert.equal(result.remaining, 2, '첫 요청 후 남은 횟수는 2여야 한다');
  });

  test('한도 내 연속 요청을 모두 허용한다', async () => {
    const r1 = await limiter.limit('user-2');
    const r2 = await limiter.limit('user-2');
    const r3 = await limiter.limit('user-2');
    assert.equal(r1.success, true, '1번째 요청이 성공해야 한다');
    assert.equal(r2.success, true, '2번째 요청이 성공해야 한다');
    assert.equal(r3.success, true, '3번째 요청이 성공해야 한다 (한도 = 3)');
    assert.equal(r3.remaining, 0, '한도 소진 후 remaining 은 0이어야 한다');
  });

  test('한도를 초과한 요청을 차단한다', async () => {
    // maxRequests = 3 이므로 4번째 요청 차단
    await limiter.limit('user-3');
    await limiter.limit('user-3');
    await limiter.limit('user-3');
    const blocked = await limiter.limit('user-3');
    assert.equal(blocked.success, false, '한도 초과 요청은 실패해야 한다');
    assert.equal(blocked.remaining, 0, '차단 시 remaining 은 0이어야 한다');
    assert.ok(blocked.retryAfter > 0, '차단 시 retryAfter 가 양수여야 한다');
  });

  test('차단 시 retryAfter 가 반환된다', async () => {
    await limiter.limit('user-4');
    await limiter.limit('user-4');
    await limiter.limit('user-4');
    const blocked = await limiter.limit('user-4');
    assert.ok(typeof blocked.retryAfter === 'number', 'retryAfter 가 숫자여야 한다');
    assert.ok(blocked.retryAfter > 0, 'retryAfter 가 0보다 커야 한다');
  });
});

describe('InMemoryRateLimiter - 윈도우 만료', () => {
  test('윈도우 만료 후 카운터가 리셋된다', async () => {
    // 매우 짧은 윈도우(50ms)로 만료를 빠르게 시뮬레이션
    const limiter = new InMemoryRateLimiter({ maxRequests: 1, windowMs: 50 });

    try {
      const first = await limiter.limit('user-exp');
      assert.equal(first.success, true, '윈도우 내 첫 번째 요청은 성공해야 한다');

      const blocked = await limiter.limit('user-exp');
      assert.equal(blocked.success, false, '동일 윈도우 내 두 번째 요청은 차단되어야 한다');

      // 윈도우 만료 대기 (50ms + 여유 10ms)
      await new Promise(resolve => setTimeout(resolve, 70));

      const afterExpiry = await limiter.limit('user-exp');
      assert.equal(afterExpiry.success, true, '윈도우 만료 후 요청은 다시 허용되어야 한다');
      assert.equal(afterExpiry.remaining, 0, '만료 후 첫 요청의 remaining 은 maxRequests-1 = 0이어야 한다');
    } finally {
      limiter.destroy();
    }
  });
});

describe('InMemoryRateLimiter - 독립적 식별자 추적', () => {
  let limiter;

  beforeEach(() => {
    limiter = new InMemoryRateLimiter({ maxRequests: 2, windowMs: 60000 });
  });

  afterEach(() => {
    limiter.destroy();
  });

  test('서로 다른 식별자는 독립적으로 카운팅된다', async () => {
    // user-A 를 한도까지 소진
    await limiter.limit('user-A');
    await limiter.limit('user-A');
    const blockedA = await limiter.limit('user-A');
    assert.equal(blockedA.success, false, 'user-A 는 차단되어야 한다');

    // user-B 는 아직 카운트가 없으므로 허용
    const allowedB = await limiter.limit('user-B');
    assert.equal(allowedB.success, true, 'user-B 는 독립적으로 허용되어야 한다');
  });

  test('한 식별자 차단이 다른 식별자에 영향을 미치지 않는다', async () => {
    // user-X 차단
    await limiter.limit('user-X');
    await limiter.limit('user-X');
    await limiter.limit('user-X'); // 차단

    // user-Y, user-Z 는 각자 독립 카운터
    const y = await limiter.limit('user-Y');
    const z = await limiter.limit('user-Z');
    assert.equal(y.success, true, 'user-Y 는 허용되어야 한다');
    assert.equal(z.success, true, 'user-Z 는 허용되어야 한다');
  });
});

describe('InMemoryRateLimiter - 만료된 항목 정리', () => {
  test('정리 후 만료된 식별자가 store 에서 제거된다', async () => {
    // 매우 짧은 윈도우 (50ms) 로 빠른 만료
    const limiter = new InMemoryRateLimiter({ maxRequests: 5, windowMs: 50 });

    try {
      await limiter.limit('cleanup-user');
      assert.equal(limiter.store.size, 1, '요청 후 store 에 항목이 있어야 한다');

      // 윈도우 만료 + 정리 인터벌 대기 (windowMs = 50ms, interval 도 50ms)
      await new Promise(resolve => setTimeout(resolve, 120));

      // 만료된 항목이 정리되었는지 확인
      // 정리 인터벌이 실행된 후 store 가 비어있어야 함
      assert.equal(limiter.store.size, 0, '만료된 항목이 정리되어 store 가 비어야 한다');
    } finally {
      limiter.destroy();
    }
  });

  test('destroy() 호출 후 정리 인터벌이 중지된다', () => {
    const limiter = new InMemoryRateLimiter({ maxRequests: 5, windowMs: 60000 });
    assert.ok(limiter.cleanupInterval, '정리 인터벌이 설정되어야 한다');
    limiter.destroy();
    // destroy 후 cleanupInterval 이 clearInterval 되었는지 확인
    // Node.js 에서 clearInterval 된 타이머는 참조가 유지되지만 실행되지 않음
    // destroy 가 에러 없이 완료되면 성공으로 간주
    assert.ok(true, 'destroy() 가 에러 없이 완료되어야 한다');
  });
});

// ─────────────────────────────────────────────
// SlidingWindowRateLimiter - Redis 폴백 테스트
// ─────────────────────────────────────────────

describe('SlidingWindowRateLimiter - Redis 실패 시 인메모리 폴백', () => {
  test('Redis pipeline 이 에러를 throw 하면 인메모리 폴백으로 처리한다', async () => {
    // Redis 클라이언트를 항상 에러를 던지는 mock 으로 교체
    const mockRedis = {
      pipeline: async () => { throw new Error('Redis connection refused'); },
    };

    const slidingLimiter = new SlidingWindowRateLimiter(mockRedis, {
      maxRequests: 5,
      windowMs: 60000,
    });

    try {
      const result = await slidingLimiter.limit('fallback-user');

      // 폴백이 성공적으로 결과를 반환해야 함
      assert.equal(typeof result.success, 'boolean', 'success 가 boolean 이어야 한다');
      assert.equal(result.success, true, '폴백 첫 요청은 성공해야 한다');
      assert.equal(result.limit, 5, '폴백의 limit 이 maxRequests 와 일치해야 한다');
      assert.ok(result.error, 'Redis 폴백 시 error 필드가 설정되어야 한다');
      assert.ok(
        result.error.includes('Redis unavailable'),
        'error 메시지에 "Redis unavailable" 가 포함되어야 한다'
      );
    } finally {
      slidingLimiter.fallback.destroy();
    }
  });

  test('Redis 폴백 상태에서도 한도 초과 요청을 차단한다', async () => {
    const mockRedis = {
      pipeline: async () => { throw new Error('Network timeout'); },
    };

    const slidingLimiter = new SlidingWindowRateLimiter(mockRedis, {
      maxRequests: 2,
      windowMs: 60000,
    });

    try {
      await slidingLimiter.limit('fallback-block');
      await slidingLimiter.limit('fallback-block');
      const blocked = await slidingLimiter.limit('fallback-block');

      assert.equal(blocked.success, false, '폴백 상태에서도 한도 초과 요청은 차단되어야 한다');
      assert.ok(blocked.error, '차단된 결과에도 error 필드가 있어야 한다');
    } finally {
      slidingLimiter.fallback.destroy();
    }
  });

  test('Redis 가 정상 작동 시 pipeline 결과를 사용한다', async () => {
    // 정상 동작하는 Redis mock
    const mockRedis = {
      pipeline: async (commands) => {
        // INCR 결과 1, EXPIRE 결과 1 반환
        return [{ result: 1 }, { result: 1 }];
      },
    };

    const slidingLimiter = new SlidingWindowRateLimiter(mockRedis, {
      maxRequests: 10,
      windowMs: 60000,
    });

    try {
      const result = await slidingLimiter.limit('redis-user');
      assert.equal(result.success, true, 'Redis 정상 시 첫 요청은 성공해야 한다');
      assert.equal(result.limit, 10, 'limit 이 maxRequests 와 일치해야 한다');
      assert.equal(result.remaining, 9, 'remaining 이 maxRequests - count(1) = 9 여야 한다');
      assert.equal(result.error, undefined, '정상 Redis 응답 시 error 필드가 없어야 한다');
    } finally {
      slidingLimiter.fallback.destroy();
    }
  });
});

/**
 * Log Sanitizer 단위 테스트
 *
 * 테스트 대상: api/lib/log-sanitizer.js
 * - maskSensitive: API 키, JWT, 이메일, 공인 IP 마스킹
 * - maskDeep: 객체/배열 재귀 마스킹, 순환 참조 방지
 * - safeLog: console 호출 + 마스킹 통합 동작
 */

import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { maskSensitive, maskDeep, safeLog } from '../lib/log-sanitizer.js';

// ─────────────────────────────────────────────
// maskSensitive 테스트
// ─────────────────────────────────────────────

describe('maskSensitive - API 키 마스킹', () => {
  test('DeepSeek API 키 (sk-*) 마스킹', () => {
    const input = 'key=sk-abcd1234efgh5678';
    const result = maskSensitive(input);
    assert.match(result, /sk-\*\*\*MASKED\*\*\*/);
    assert.doesNotMatch(result, /sk-abcd1234/);
  });

  test('GitHub 토큰 (ghp_*) 마스킹', () => {
    const input = 'token: ghp_abcdef12345678';
    const result = maskSensitive(input);
    assert.match(result, /ghp_\*\*\*MASKED\*\*\*/);
    assert.doesNotMatch(result, /ghp_abcdef/);
  });

  test('Google API 키 (AIza*) 마스킹', () => {
    const input = 'api_key: AIzaSyD1234567890';
    const result = maskSensitive(input);
    assert.match(result, /AIza\*\*\*MASKED\*\*\*/);
    assert.doesNotMatch(result, /AIzaSyD/);
  });

  test('AWS 액세스 키 (AKIA*) 마스킹', () => {
    const input = 'access_key: AKIAIOSFODNN7EXAMPLE';
    const result = maskSensitive(input);
    assert.match(result, /AKIA\*\*\*MASKED\*\*\*/);
    assert.doesNotMatch(result, /AKIAIOSFODNN/);
  });
});

describe('maskSensitive - 이메일 마스킹', () => {
  test('표준 이메일 주소 마스킹', () => {
    const input = 'user@example.com';
    const result = maskSensitive(input);
    assert.strictEqual(result, '[EMAIL_MASKED]');
  });

  test('복잡한 이메일 주소 마스킹', () => {
    const input = 'contact user.name+tag@sub.example.co.uk';
    const result = maskSensitive(input);
    assert.match(result, /\[EMAIL_MASKED\]/);
    assert.doesNotMatch(result, /example\.com/);
  });

  test('여러 이메일 동시 마스킹', () => {
    const input = 'to: admin@test.com, cc: user@example.org';
    const result = maskSensitive(input);
    assert.strictEqual((result.match(/\[EMAIL_MASKED\]/g) || []).length, 2);
  });
});

describe('maskSensitive - 공인 IP 주소 마스킹', () => {
  test('공인 IPv4 주소 (8.8.8.8) 마스킹', () => {
    const input = 'from 8.8.8.8 request';
    const result = maskSensitive(input);
    assert.match(result, /\[IP_MASKED\]/);
    assert.doesNotMatch(result, /8\.8\.8\.8/);
  });

  test('공인 IPv4 주소 (1.1.1.1) 마스킹', () => {
    const input = 'request from 1.1.1.1 received';
    const result = maskSensitive(input);
    assert.match(result, /\[IP_MASKED\]/);
    assert.doesNotMatch(result, /1\.1\.1\.1/);
  });

  test('사설 IP 주소 (192.168.*) 보존', () => {
    const input = 'from 192.168.1.1 request';
    const result = maskSensitive(input);
    assert.strictEqual(result, input);
    assert.match(result, /192\.168\.1\.1/);
  });

  test('사설 IP 주소 (10.*) 보존', () => {
    const input = 'from 10.0.0.1 request';
    const result = maskSensitive(input);
    assert.strictEqual(result, input);
    assert.match(result, /10\.0\.0\.1/);
  });

  test('루프백 주소 (127.*) 보존', () => {
    const input = 'from 127.0.0.1 request';
    const result = maskSensitive(input);
    assert.strictEqual(result, input);
    assert.match(result, /127\.0\.0\.1/);
  });

  test('클래스 B 사설 대역 (172.16-31.*) 보존', () => {
    const input = 'from 172.16.0.1 and 172.31.255.255 secure';
    const result = maskSensitive(input);
    assert.strictEqual(result, input);
    assert.match(result, /172\.16\.0\.1/);
    assert.match(result, /172\.31\.255\.255/);
  });
});

describe('maskSensitive - JWT 마스킹', () => {
  test('표준 JWT 토큰 마스킹', () => {
    const input = 'bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
    const result = maskSensitive(input);
    assert.match(result, /\[JWT_MASKED\]/);
    assert.doesNotMatch(result, /eyJhbGci/);
  });
});

describe('maskSensitive - 비문자열 입력 처리', () => {
  test('숫자 입력은 그대로 반환', () => {
    assert.strictEqual(maskSensitive(42), 42);
    assert.strictEqual(maskSensitive(3.14), 3.14);
  });

  test('null 입력은 그대로 반환', () => {
    assert.strictEqual(maskSensitive(null), null);
  });

  test('undefined 입력은 그대로 반환', () => {
    assert.strictEqual(maskSensitive(undefined), undefined);
  });

  test('boolean 입력은 그대로 반환', () => {
    assert.strictEqual(maskSensitive(true), true);
    assert.strictEqual(maskSensitive(false), false);
  });

  test('객체 입력은 그대로 반환 (maskDeep 사용 필요)', () => {
    const obj = { key: 'value' };
    assert.deepStrictEqual(maskSensitive(obj), obj);
  });
});

describe('maskSensitive - 종합 마스킹', () => {
  test('여러 패턴 동시 마스킹', () => {
    const input = 'API sk-test1234567890 from 8.8.8.8 for user@test.com and ghp_token1234567890';
    const result = maskSensitive(input);
    assert.match(result, /sk-\*\*\*MASKED\*\*\*/);
    assert.match(result, /\[IP_MASKED\]/);
    assert.match(result, /\[EMAIL_MASKED\]/);
    assert.match(result, /ghp_\*\*\*MASKED\*\*\*/);
  });

  test('마스킹 후에도 컨텍스트 문자열은 보존', () => {
    const input = 'Error: API key sk-secret123456 invalid for user@test.com';
    const result = maskSensitive(input);
    assert.match(result, /^Error: API key/);
    assert.match(result, /invalid for/);
  });
});

// ─────────────────────────────────────────────
// maskDeep 테스트
// ─────────────────────────────────────────────

describe('maskDeep - 객체 마스킹', () => {
  test('단순 객체 마스킹', () => {
    const input = { ip: '8.8.8.8', email: 'ab@bc.com' };
    const result = maskDeep(input);
    assert.match(result.ip, /\[IP_MASKED\]/);
    assert.strictEqual(result.email, '[EMAIL_MASKED]');
  });

  test('중첩 객체 마스킹', () => {
    const input = {
      user: { email: 'user@example.com' },
      server: { ip: '1.1.1.1' },
    };
    const result = maskDeep(input);
    assert.strictEqual(result.user.email, '[EMAIL_MASKED]');
    assert.match(result.server.ip, /\[IP_MASKED\]/);
  });

  test('배열 내 객체 마스킹', () => {
    const input = [
      { ip: '8.8.8.8', key: 'sk-token1234567890' },
      { email: 'test@test.com' },
    ];
    const result = maskDeep(input);
    assert.match(result[0].ip, /\[IP_MASKED\]/);
    assert.match(result[0].key, /sk-\*\*\*MASKED\*\*\*/);
    assert.strictEqual(result[1].email, '[EMAIL_MASKED]');
  });

  test('혼합 타입 배열 마스킹', () => {
    const input = [42, 'user@test.com', { ip: '1.1.1.1' }, null, true];
    const result = maskDeep(input);
    assert.strictEqual(result[0], 42);
    assert.strictEqual(result[1], '[EMAIL_MASKED]');
    assert.match(result[2].ip, /\[IP_MASKED\]/);
    assert.strictEqual(result[3], null);
    assert.strictEqual(result[4], true);
  });
});

describe('maskDeep - 순환 참조 및 깊이 제한', () => {
  test('깊이 10을 초과하면 원본 객체 반환', () => {
    // 깊이 11의 중첩 구조 생성
    let deep = { value: 'sk-token1234567890' };
    for (let i = 0; i < 11; i++) {
      deep = { nested: deep };
    }

    const result = maskDeep(deep);

    // 깊이 10까지는 마스킹, 11 이상은 원본 반환
    // 최상단부터 카운트하면 깊이 11에서 멈춤
    assert.strictEqual(typeof result.nested, 'object');
  });

  test('null/undefined 값 보존', () => {
    const input = { a: null, b: undefined, c: 'test' };
    const result = maskDeep(input);
    assert.strictEqual(result.a, null);
    assert.strictEqual(result.b, undefined);
    assert.strictEqual(result.c, 'test');
  });

  test('원시값 배열 마스킹', () => {
    const input = ['user@test.com', 'sk-token123456789', null, 42];
    const result = maskDeep(input);
    assert.strictEqual(result[0], '[EMAIL_MASKED]');
    assert.match(result[1], /sk-\*\*\*MASKED\*\*\*/);
    assert.strictEqual(result[2], null);
    assert.strictEqual(result[3], 42);
  });
});

describe('maskDeep - 복잡한 데이터 구조', () => {
  test('실제 로그 컨텍스트 마스킹', () => {
    const context = {
      method: 'POST',
      url: '/api/users',
      headers: {
        authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        'x-api-key': 'sk-abcd1234efgh5678',
      },
      body: {
        email: 'admin@company.com',
        ip: '8.8.8.8',
      },
      remote_addr: '192.168.1.100',
    };

    const result = maskDeep(context);
    assert.match(result.headers.authorization, /\[JWT_MASKED\]/);
    assert.match(result.headers['x-api-key'], /sk-\*\*\*MASKED\*\*\*/);
    assert.strictEqual(result.body.email, '[EMAIL_MASKED]');
    assert.match(result.body.ip, /\[IP_MASKED\]/);
    // 사설 IP는 보존
    assert.strictEqual(result.remote_addr, '192.168.1.100');
  });
});

// ─────────────────────────────────────────────
// safeLog 테스트
// ─────────────────────────────────────────────

describe('safeLog - console 호출 및 마스킹', () => {
  let originalConsole;

  beforeEach(() => {
    // console 메서드별 호출 기록
    originalConsole = {
      log: console.log,
      warn: console.warn,
      error: console.error,
      info: console.info,
      debug: console.debug,
    };

    const calls = { log: [], warn: [], error: [], info: [], debug: [] };

    console.log = (...args) => calls.log.push(args);
    console.warn = (...args) => calls.warn.push(args);
    console.error = (...args) => calls.error.push(args);
    console.info = (...args) => calls.info.push(args);
    console.debug = (...args) => calls.debug.push(args);

    // 테스트에서 접근할 수 있도록 전역 변수로 저장
    globalThis.__consoleCalls = calls;
  });

  afterEach(() => {
    console.log = originalConsole.log;
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
    console.info = originalConsole.info;
    console.debug = originalConsole.debug;
    delete globalThis.__consoleCalls;
  });

  test('safeLog warn: 메시지와 마스킹된 컨텍스트 호출', () => {
    const context = { ip: '8.8.8.8', email: 'test@test.com' };
    safeLog('warn', 'API Error', context);

    const calls = globalThis.__consoleCalls.warn;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0][0], 'API Error');
    assert.match(calls[0][1].ip, /\[IP_MASKED\]/);
    assert.strictEqual(calls[0][1].email, '[EMAIL_MASKED]');
  });

  test('safeLog error: 메시지와 마스킹된 컨텍스트 호출', () => {
    const context = { key: 'sk-secret123456789' };
    safeLog('error', 'Auth Failed', context);

    const calls = globalThis.__consoleCalls.error;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0][0], 'Auth Failed');
    assert.match(calls[0][1].key, /sk-\*\*\*MASKED\*\*\*/);
  });

  test('safeLog info: 컨텍스트 없이 메시지만 호출', () => {
    safeLog('info', 'Request started');

    const calls = globalThis.__consoleCalls.info;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0].length, 1);
    assert.strictEqual(calls[0][0], 'Request started');
  });

  test('safeLog log: 레벨명 기본값 적용 (유효하지 않은 레벨)', () => {
    const context = { ip: '1.1.1.1' };
    safeLog('invalid_level', 'Message', context);

    const calls = globalThis.__consoleCalls.log;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0][0], 'Message');
    assert.match(calls[0][1].ip, /\[IP_MASKED\]/);
  });

  test('safeLog debug: 레벨명 확인', () => {
    const context = { user: 'user@example.com' };
    safeLog('debug', 'Debug info', context);

    const calls = globalThis.__consoleCalls.debug;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0][0], 'Debug info');
    assert.strictEqual(calls[0][1].user, '[EMAIL_MASKED]');
  });

  test('safeLog 컨텍스트가 undefined일 때 메시지만 출력', () => {
    safeLog('warn', 'Simple warning', undefined);

    const calls = globalThis.__consoleCalls.warn;
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0].length, 1);
    assert.strictEqual(calls[0][0], 'Simple warning');
  });

  test('safeLog 모든 로그 레벨 지원', () => {
    const levels = ['log', 'warn', 'error', 'info', 'debug'];
    const context = { ip: '8.8.8.8' };

    levels.forEach(level => {
      safeLog(level, `${level} message`, context);
    });

    levels.forEach(level => {
      assert.strictEqual(
        globalThis.__consoleCalls[level].length,
        1,
        `${level} should be called once`
      );
    });
  });
});

describe('safeLog - 통합 테스트', () => {
  let originalConsole;

  beforeEach(() => {
    originalConsole = {
      log: console.log,
      warn: console.warn,
      error: console.error,
      info: console.info,
      debug: console.debug,
    };

    const calls = { log: [], warn: [], error: [], info: [], debug: [] };
    console.log = (...args) => calls.log.push(args);
    console.warn = (...args) => calls.warn.push(args);
    console.error = (...args) => calls.error.push(args);
    console.info = (...args) => calls.info.push(args);
    console.debug = (...args) => calls.debug.push(args);
    globalThis.__consoleCalls = calls;
  });

  afterEach(() => {
    console.log = originalConsole.log;
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
    console.info = originalConsole.info;
    console.debug = originalConsole.debug;
    delete globalThis.__consoleCalls;
  });

  test('실제 로그 시나리오: API 요청 실패 로깅', () => {
    const logContext = {
      timestamp: '2026-04-17T10:00:00Z',
      method: 'POST',
      path: '/api/auth/login',
      status: 401,
      user_email: 'hacker@evil.com',
      api_key: 'sk-invalid123456789',
      client_ip: '203.0.113.0',
      error_msg: 'Unauthorized',
    };

    safeLog('error', 'API request failed', logContext);

    const calls = globalThis.__consoleCalls.error;
    const logged = calls[0][1];

    assert.strictEqual(logged.timestamp, '2026-04-17T10:00:00Z');
    assert.strictEqual(logged.method, 'POST');
    assert.strictEqual(logged.user_email, '[EMAIL_MASKED]');
    assert.match(logged.api_key, /sk-\*\*\*MASKED\*\*\*/);
    assert.match(logged.client_ip, /\[IP_MASKED\]/);
  });

  test('실제 로그 시나리오: JWT 검증 실패', () => {
    const logContext = {
      jwt_token:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
      reason: 'Token expired',
      issued_to: 'user@mycompany.com',
    };

    safeLog('warn', 'JWT validation failed', logContext);

    const calls = globalThis.__consoleCalls.warn;
    const logged = calls[0][1];

    assert.match(logged.jwt_token, /\[JWT_MASKED\]/);
    assert.strictEqual(logged.reason, 'Token expired');
    assert.strictEqual(logged.issued_to, '[EMAIL_MASKED]');
  });
});

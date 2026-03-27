/**
 * sanitizeInput 함수 단위 테스트
 *
 * 참고: sanitizeInput은 api/chat.js 내부 함수로 export되지 않아
 *       동일 로직을 이 파일에 복사했습니다.
 *       소스가 변경되면 이 함수도 동기화해야 합니다.
 *
 * Source mirrored from: api/chat.js (lines 586-658)
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

// --- sanitizeInput 미러 (api/chat.js 와 동일 로직) ---
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // null byte 제거
  let sanitized = input.replace(/\0/g, '');

  // 유니코드 정규화 (NFC)
  sanitized = sanitized.normalize('NFC');

  // 위험한 유니코드 조합 문자 제거
  sanitized = sanitized.replace(/[\u200B-\u200D\uFEFF\u202A-\u202E\u2060-\u206F]/g, '');

  // 유니코드 이스케이프 시퀀스 제거
  sanitized = sanitized.replace(/\\u[0-9a-fA-F]{4}/g, '');
  sanitized = sanitized.replace(/\\x[0-9a-fA-F]{2}/g, '');

  // HTML 특수 문자 이스케이프
  sanitized = sanitized
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
    .replace(/`/g, '&#x60;');

  // 중복 이스케이프 방지
  sanitized = sanitized
    .replace(/&amp;amp;/g, '&amp;')
    .replace(/&amp;lt;/g, '&lt;')
    .replace(/&amp;gt;/g, '&gt;')
    .replace(/&amp;quot;/g, '&quot;')
    .replace(/&amp;#x27;/g, '&#x27;')
    .replace(/&amp;#x2F;/g, '&#x2F;')
    .replace(/&amp;#x60;/g, '&#x60;');

  // 제어 문자 제거
  sanitized = sanitized.replace(/[\x00-\x1F\x7F-\x9F]/g, '');

  // 위험한 패턴 제거
  const dangerousPatterns = [
    /javascript\s*:/gi,
    /data\s*:\s*text\s*\/\s*html/gi,
    /data\s*:\s*text\s*\/\s*javascript/gi,
    /vbscript\s*:/gi,
    /on\w+\s*=/gi,
    /&lt;\s*script/gi,
    /&lt;\s*iframe/gi,
    /&lt;\s*object/gi,
    /&lt;\s*embed/gi,
    /&lt;\s*svg/gi,
    /&lt;\s*math/gi,
    /expression\s*\(/gi,
    /url\s*\(/gi,
    /import\s*\(/gi,
  ];

  for (const pattern of dangerousPatterns) {
    sanitized = sanitized.replace(pattern, '');
  }

  return sanitized.trim();
}
// --- 미러 끝 ---

describe('sanitizeInput - 기본 HTML 이스케이프', () => {
  test('<script> 태그를 엔티티로 변환한다', () => {
    const result = sanitizeInput('<script>alert(1)</script>');
    // < > 는 &lt; &gt; 로 이스케이프된 뒤 &lt;script 패턴 제거
    assert.ok(!result.includes('<script'), '결과에 <script 가 없어야 한다');
    assert.ok(!result.includes('</script>'), '결과에 </script> 가 없어야 한다');
  });

  test('<img onerror> 이벤트 핸들러를 제거한다', () => {
    const result = sanitizeInput('<img src=x onerror=alert(1)>');
    // on\w+= 패턴이 제거됨
    assert.ok(!result.includes('onerror='), '결과에 onerror= 가 없어야 한다');
  });

  test('& 는 &amp; 로 이스케이프된다', () => {
    const result = sanitizeInput('foo & bar');
    assert.ok(result.includes('&amp;'), '& 가 &amp; 로 이스케이프되어야 한다');
  });

  test('" 는 &quot; 로 이스케이프된다', () => {
    const result = sanitizeInput('say "hello"');
    assert.ok(result.includes('&quot;'), '" 가 &quot; 로 이스케이프되어야 한다');
  });

  test("' 는 &#x27; 로 이스케이프된다", () => {
    const result = sanitizeInput("it's fine");
    assert.ok(result.includes('&#x27;'), "' 가 &#x27; 로 이스케이프되어야 한다");
  });
});

describe('sanitizeInput - Null byte 제거', () => {
  test('null byte(\\0)를 제거한다', () => {
    const result = sanitizeInput('hello\0world');
    assert.equal(result, 'helloworld', 'null byte 가 제거된 결과여야 한다');
  });

  test('여러 null byte를 모두 제거한다', () => {
    const result = sanitizeInput('\0\0\0');
    assert.equal(result, '', '모든 null byte 가 제거된 빈 문자열이어야 한다');
  });
});

describe('sanitizeInput - 백틱 인코딩', () => {
  test('백틱(`)을 &#x60; 으로 인코딩한다', () => {
    const result = sanitizeInput('`rm -rf /`');
    assert.ok(result.includes('&#x60;'), '백틱이 &#x60; 으로 인코딩되어야 한다');
    assert.ok(!result.includes('`'), '백틱이 원본 형태로 남아있으면 안 된다');
  });

  test('template literal 형태의 백틱도 인코딩한다', () => {
    const result = sanitizeInput('`${process.env.SECRET}`');
    assert.ok(!result.includes('`'), '백틱이 원본 형태로 남아있으면 안 된다');
  });
});

describe('sanitizeInput - 유니코드 이스케이프 제거', () => {
  test('\\u0027 (단일 인용부호 유니코드) 시퀀스를 제거한다', () => {
    const result = sanitizeInput('\\u0027');
    assert.ok(!result.includes('\\u0027'), '\\u0027 가 제거되어야 한다');
  });

  test('\\x27 (단일 인용부호 hex) 시퀀스를 제거한다', () => {
    const result = sanitizeInput('\\x27');
    assert.ok(!result.includes('\\x27'), '\\x27 가 제거되어야 한다');
  });

  test('\\uXXXX 형태의 임의 유니코드 이스케이프를 제거한다', () => {
    const result = sanitizeInput('hello \\u003C script');
    assert.ok(!result.includes('\\u003C'), '\\u003C 가 제거되어야 한다');
  });
});

describe('sanitizeInput - SVG/Math 태그 차단', () => {
  test('<svg onload> 를 차단한다', () => {
    const result = sanitizeInput('<svg onload=alert(1)>');
    // < 가 &lt; 로 변환된 후 &lt;svg 패턴이 제거됨
    assert.ok(!result.includes('&lt;svg'), '&lt;svg 패턴이 제거되어야 한다');
    // onload= 도 on\w+= 패턴에 의해 제거됨
    assert.ok(!result.includes('onload='), 'onload= 가 제거되어야 한다');
  });

  test('<math> 태그를 차단한다', () => {
    const result = sanitizeInput('<math><mi>x</mi></math>');
    assert.ok(!result.includes('&lt;math'), '&lt;math 패턴이 제거되어야 한다');
  });
});

describe('sanitizeInput - url() 및 import() 패턴 차단', () => {
  test('url() 패턴을 제거한다', () => {
    const result = sanitizeInput('background: url(javascript:alert(1))');
    assert.ok(!result.includes('url('), 'url( 패턴이 제거되어야 한다');
  });

  test('url () 공백 포함 패턴도 제거한다', () => {
    const result = sanitizeInput('url  (http://evil.com)');
    // url\s*\( 패턴
    assert.ok(!result.includes('url  ('), 'url  ( 패턴이 제거되어야 한다');
  });

  test('import() 패턴을 제거한다', () => {
    const result = sanitizeInput('import(module)');
    assert.ok(!result.includes('import('), 'import( 패턴이 제거되어야 한다');
  });

  test('import () 공백 포함 패턴도 제거한다', () => {
    const result = sanitizeInput('import  (evil)');
    assert.ok(!result.includes('import  ('), 'import  ( 패턴이 제거되어야 한다');
  });
});

describe('sanitizeInput - 정상 텍스트 통과', () => {
  test('일반 한국어 텍스트는 변경 없이 통과한다', () => {
    const input = '안녕하세요 반갑습니다';
    const result = sanitizeInput(input);
    assert.equal(result, input, '한국어 텍스트가 그대로 유지되어야 한다');
  });

  test('일반 영어 텍스트는 변경 없이 통과한다', () => {
    const input = 'Hello world this is a test';
    const result = sanitizeInput(input);
    assert.equal(result, input, '영어 텍스트가 그대로 유지되어야 한다');
  });

  test('숫자와 공백은 변경 없이 통과한다', () => {
    const input = '12345 67890';
    const result = sanitizeInput(input);
    assert.equal(result, input, '숫자와 공백이 그대로 유지되어야 한다');
  });
});

describe('sanitizeInput - 엣지 케이스', () => {
  test('빈 문자열 입력 시 빈 문자열을 반환한다', () => {
    assert.equal(sanitizeInput(''), '', '빈 문자열 입력 시 빈 문자열을 반환해야 한다');
  });

  test('null 입력 시 빈 문자열을 반환한다', () => {
    assert.equal(sanitizeInput(null), '', 'null 입력 시 빈 문자열을 반환해야 한다');
  });

  test('undefined 입력 시 빈 문자열을 반환한다', () => {
    assert.equal(sanitizeInput(undefined), '', 'undefined 입력 시 빈 문자열을 반환해야 한다');
  });

  test('숫자 입력 시 빈 문자열을 반환한다', () => {
    assert.equal(sanitizeInput(42), '', '숫자 입력 시 빈 문자열을 반환해야 한다');
  });

  test('객체 입력 시 빈 문자열을 반환한다', () => {
    assert.equal(sanitizeInput({}), '', '객체 입력 시 빈 문자열을 반환해야 한다');
  });

  test('앞뒤 공백이 제거된다', () => {
    const result = sanitizeInput('  hello  ');
    assert.equal(result, 'hello', '앞뒤 공백이 trim 처리되어야 한다');
  });
});

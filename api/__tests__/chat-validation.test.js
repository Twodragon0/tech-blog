/**
 * api/chat.js 의 검증 헬퍼 단위 테스트 — isBotUserAgent / validateUrl
 *
 * 두 함수의 성격이 다르다는 점을 먼저 알아야 한다.
 *
 * - `isBotUserAgent` 는 살아 있다. `handler` 가 `NODE_ENV === 'production'`
 *   일 때만 호출한다 (api/chat.js:98).
 * - `validateUrl` 은 **현재 아무 곳에서도 호출되지 않는다.** 레포 전체에서
 *   호출부가 0건이다. 여기 테스트를 두는 이유는 커버리지 숫자가 아니라,
 *   나중에 누군가 이 함수를 배선할 때 "검증된 함수"라고 믿고 쓰기 전에
 *   실제 동작 — 특히 아래 놀라운 항목들 — 을 먼저 보게 하려는 것이다.
 *
 * 여기 담긴 단언은 전부 실제 실행으로 확인한 현재 동작이며, "이래야 한다"는
 * 당위가 아니다. 동작을 바꾸려면 테스트도 같이 바꿔야 하고, 그때가 바로
 * 바꿔도 되는지 따져볼 지점이다.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { isBotUserAgent, validateUrl } from '../chat.js';

describe('isBotUserAgent - 봇으로 판정하는 경우', () => {
  test('User-Agent 가 없으면 봇으로 간주한다', () => {
    assert.equal(isBotUserAgent(undefined), true);
    assert.equal(isBotUserAgent(''), true);
    assert.equal(isBotUserAgent(null), true);
  });

  test('UA 를 숨기지 않는 CLI 클라이언트는 잡힌다', () => {
    for (const ua of ['curl/8.4.0', 'Wget/1.21', 'python-requests/2.31.0', 'Go-http-client/2.0']) {
      assert.equal(isBotUserAgent(ua), true, `${ua} 는 봇으로 판정되어야 한다`);
    }
  });
});

describe('isBotUserAgent - 허용 목록이 봇 목록보다 먼저 평가된다', () => {
  // 이것이 이 함수의 실질적 한계다. 브라우저 허용 패턴을 먼저 검사하고
  // 하나라도 맞으면 즉시 false 를 반환하므로, UA 에 'mozilla' 가 들어 있는
  // 순간 봇 패턴은 아예 검사되지 않는다.
  test('실제 Googlebot UA 는 봇으로 판정되지 않는다', () => {
    const googlebot =
      'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';
    assert.equal(isBotUserAgent(googlebot), false);
  });

  test('실제 bingbot UA 도 봇으로 판정되지 않는다', () => {
    const bingbot =
      'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)';
    assert.equal(isBotUserAgent(bingbot), false);
  });

  test('UA 에 mozilla 만 붙이면 scraper 도 통과한다', () => {
    // 즉 이 검사는 통제가 아니라 과속방지턱이다. UA 를 설정할 줄 아는
    // 클라이언트는 누구나 우회한다. 실제 남용 방어는 rate limiting 이다.
    assert.equal(isBotUserAgent('my-scraper/1.0'), true);
    assert.equal(isBotUserAgent('Mozilla/5.0 my-scraper/1.0'), false);
  });

  test('평범한 브라우저는 통과한다', () => {
    const chrome =
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    assert.equal(isBotUserAgent(chrome), false);
  });
});

describe('validateUrl - 차단하는 것', () => {
  test('빈 값과 공백만 있는 문자열', () => {
    assert.equal(validateUrl(''), null);
    assert.equal(validateUrl('   '), null);
    assert.equal(validateUrl(undefined), null);
    assert.equal(validateUrl(123), null);
  });

  test('위험한 스킴은 대소문자와 선행 공백을 섞어도 차단된다', () => {
    for (const url of [
      'javascript:alert(1)',
      ' javascript:alert(1)',
      'JaVaScRiPt:alert(1)',
      'data:text/html,<script>alert(1)</script>',
      'vbscript:msgbox(1)',
      'file:///etc/passwd',
    ]) {
      assert.equal(validateUrl(url), null, `${url} 은 차단되어야 한다`);
    }
  });

  test('루프백 호스트는 정확히 일치할 때 차단된다', () => {
    assert.equal(validateUrl('http://localhost/x'), null);
    assert.equal(validateUrl('http://LOCALHOST/x'), null);
    assert.equal(validateUrl('http://127.0.0.1/x'), null);
    assert.equal(validateUrl('http://[::1]/x'), null);
  });

  test('프래그먼트의 이벤트 핸들러 패턴은 차단된다', () => {
    // 프래그먼트는 URL 파서가 인코딩하지 않으므로 패턴 검사에 걸린다.
    assert.equal(validateUrl('http://example.com/#onerror=1'), null);
  });
});

describe('validateUrl - 통과시키는 것', () => {
  test('평범한 절대 URL', () => {
    assert.equal(
      validateUrl('https://tech.2twodragon.com/posts/x/'),
      'https://tech.2twodragon.com/posts/x/'
    );
    assert.equal(validateUrl('http://example.com'), 'http://example.com/');
  });

  test('상대 경로는 사이트 도메인 기준 절대 경로가 된다', () => {
    assert.equal(
      validateUrl('/posts/relative/'),
      'https://tech.2twodragon.com/posts/relative/'
    );
  });

  test('스킴 대문자는 정규화된다', () => {
    assert.equal(validateUrl('HTTPS://EXAMPLE.COM'), 'https://example.com/');
  });
});

describe('validateUrl - 배선 전에 반드시 알아야 할 동작', () => {
  // 아래 넷은 "통과시키는 것" 과 달리, 호출부가 무엇을 기대하느냐에 따라
  // 취약점이 될 수 있는 것들이다. 지금은 호출부가 없어 무해하다.

  test('프로토콜 상대 URL 은 외부 사이트로 나간다', () => {
    // `//evil.com` 은 상대 경로처럼 생겼지만 '://' 가 없어 상대 경로 분기를
    // 타고, URL 생성자가 이를 프로토콜 상대 URL 로 해석해 외부 절대 주소가
    // 된다. 입력이 상대 경로면 사이트 안에 머문다고 가정하는 호출부에서는
    // 오픈 리다이렉트가 된다.
    assert.equal(validateUrl('//evil.com'), 'https://evil.com/');
  });

  test('클라우드 메타데이터 주소가 통과한다', () => {
    // 루프백만 막고 링크로컬/사설 대역은 막지 않는다. 이 함수를 서버측
    // fetch 앞에 두면 SSRF 가 된다. 렌더링용 링크 검증이라면 무해하다.
    assert.equal(
      validateUrl('http://169.254.169.254/latest/meta-data/'),
      'http://169.254.169.254/latest/meta-data/'
    );
    assert.equal(validateUrl('http://10.0.0.1/'), 'http://10.0.0.1/');
  });

  test('URL 에 박힌 자격증명이 보존된다', () => {
    assert.equal(
      validateUrl('http://user:pass@example.com/'),
      'http://user:pass@example.com/'
    );
  });

  test('쿼리스트링의 위험 패턴은 인코딩되어 검사를 비껴간다', () => {
    // 패턴 검사는 urlObj.search 를 보는데, URL 생성자가 이미 `<` `>` 를
    // 퍼센트 인코딩한 뒤라 `/<script/i` 가 맞지 않는다. 결과적으로 값이
    // 무해해지긴 하나, 차단이 아니라 통과다.
    assert.equal(
      validateUrl('http://example.com/?q=<script>'),
      'http://example.com/?q=%3Cscript%3E'
    );
  });

  test('정확히 일치하지 않는 호스트는 통과한다 (의도된 동작)', () => {
    // 부분 문자열 검사였다면 정상 도메인을 오차단했을 것이다.
    assert.equal(
      validateUrl('http://localhost.evil.com/x'),
      'http://localhost.evil.com/x'
    );
  });
});

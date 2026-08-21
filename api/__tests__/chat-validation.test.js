/**
 * api/chat.js 의 검증 헬퍼 단위 테스트 — isBotUserAgent
 *
 * `isBotUserAgent` 는 살아 있다. `handler` 가 `NODE_ENV === 'production'`
 * 일 때만 호출한다 (api/chat.js:98).
 *
 * 여기 담긴 단언은 전부 실제 실행으로 확인한 현재 동작이며, "이래야 한다"는
 * 당위가 아니다. 동작을 바꾸려면 테스트도 같이 바꿔야 하고, 그때가 바로
 * 바꿔도 되는지 따져볼 지점이다.
 *
 * 같은 파일에 있던 `validateUrl` 테스트는 함수와 함께 삭제됐다. 호출부가
 * 레포 전체에서 0건이었고, chat.js 가 받는 건 message/sessionId/
 * conversationHistory/pageContext(title·tags·excerpt) 뿐이라 사용자 URL 이
 * 서버에 도달하는 경로 자체가 없었다. 이름과 보안 주석 때문에 "검증된
 * 함수" 로 믿고 SSRF 민감한 곳에 배선될 위험이 남는 편이 더 나빴다.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { isBotUserAgent } from '../chat.js';

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

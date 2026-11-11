// Global vitest setup for the JS regression suite (tests/js).
//
// jsdom does not implement Element.prototype.scrollIntoView. Several source
// files call it from inside setTimeout callbacks (tags-page.js, archive-filter.js,
// giscus-init.js, the quizzes). When such a timer fires AFTER its test has
// finished, the missing method throws an unhandled `TypeError:
// target.scrollIntoView is not a function`, which vitest promotes to a whole-run
// failure (exit 1) even though every test "passed" -- a timing-dependent flake.
//
// The per-test suites that ASSERT scrollIntoView was called (aws-saa-quiz,
// main-search, tags-page, archive-filter) save the current value in beforeEach
// and reinstall their own vi.fn(); installing this no-op at load time means the
// value they capture is a harmless function instead of `undefined`, so their
// restore keeps leaked timers safe. The afterEach below re-establishes the stub
// for any suite that `delete`s it (main-search), guaranteeing the method is
// always callable between tests regardless of hook ordering.
import { afterEach } from 'vitest';

function installScrollIntoViewStub() {
  if (typeof Element !== 'undefined' && typeof Element.prototype.scrollIntoView !== 'function') {
    Element.prototype.scrollIntoView = function () {};
  }
}

installScrollIntoViewStub();

afterEach(() => {
  installScrollIntoViewStub();
});

// --- 삼켜진 window error 바닥 가드 ------------------------------------------
//
// 이벤트 핸들러 안에서 던진 예외는 호출부로 전파되지 않는다. jsdom 은 그것을
// window 의 'error' 로 보고하고, 테스트는 아무것도 모른 채 계속 진행한다. 그래서
// "핸들러가 중간에 죽었다" 가 "에러" 가 아니라 "결과가 없다" 로만 보인다.
//
// 2026-09-23 에 그 형태로 하루를 썼다. jsdom 30.1.0 의 URL.createObjectURL 이
// `Cannot read properties of undefined (reading '_buffer')` 로 던지면서 다운로드
// 핸들러가 그 줄에서 멈췄고, 테스트는 `expected undefined to be defined` 라는
// 엉뚱한 증상만 보여줬다. 원인에 닿는 데 여러 단계의 이분이 필요했다.
//
// 수정 직후 전체 스위트를 계측하니 삼켜진 에러는 **0건**이다. 0 이므로 바닥으로
// 건다 — 이 가드가 그때 있었다면 첫 실행에서 원인이 그대로 출력됐다.
//
// 의도적으로 에러를 내는 테스트가 생기면 그 테스트 안에서 `swallowedErrors` 를
// 비우면 된다. 목록을 늘리지 말고, 왜 비우는지 그 자리에 적을 것.
const swallowedErrors = [];

if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    // 실제 예외를 실은 이벤트만 센다. 합성 `new Event('error')` 는 테스트가
    // 리스너를 자극하려고 직접 발행하는 픽스처이지(console-filter 가 그렇다)
    // 던져진 예외가 아니다 — 구분은 error/message 의 존재다. 면제 목록이
    // 아니므로 새 테스트가 생겨도 손볼 것이 없다.
    if (!event.error && !event.message) return;
    swallowedErrors.push(event.message || String(event.error));
  });
}

globalThis.swallowedErrors = swallowedErrors;

afterEach(() => {
  if (swallowedErrors.length === 0) return;
  const seen = swallowedErrors.join('\n  ');
  swallowedErrors.length = 0;
  throw new Error(
    '핸들러 안에서 예외가 던져졌고 테스트는 그것을 보지 못한 채 진행했다. ' +
      '단언이 통과했더라도 그 경로는 중간에 죽었다:\n  ' +
      seen,
  );
});

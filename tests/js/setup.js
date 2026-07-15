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

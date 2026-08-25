// Regression tests for the MutationObserver half of assets/js/ad-optimizer.js.
//
// These live in their OWN file on purpose. ad-optimizer never disconnects its
// document.body observer (it must keep watching for late Auto ads), and jsdom
// reuses one document.body across tests in a file — so every runScript() in a
// file leaves another live observer behind. With them accumulated, deleting the
// `google-auto-placed` branch from the observer STILL left the suite green:
// some other instance swept the node. Verified by probe — in isolation the node
// survives that mutation, in the shared file it does not. Vitest isolates per
// file, so one file per observer test keeps the mutation detectable.
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/ad-optimizer.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
  vi.runOnlyPendingTimers();
}

describe('ad-optimizer.js MutationObserver', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = '';
  });

  // Auto ads 는 예약된 스윕이 모두 끝난 뒤에도 계속 슬롯을 꽂는다. 그 시점에
  // 남은 방어선은 MutationObserver 뿐이다.
  //
  // 이 테스트의 초안은 주입 후 runOnlyPendingTimers() 를 한 번 더 불렀는데,
  // 그러면 뒤늦은 스윕이 노드를 지워버려 관찰자를 전혀 검증하지 못했다.
  // 실제로 관찰자에서 google-auto-placed 선택자를 빼는 변이를 넣어도 초안은
  // 통과했다. 그래서 타이머를 모두 소진시킨 뒤 microtask 만 흘린다.
  it('removes a table-nested auto-placed ad injected after every sweep has run', async () => {
    document.body.innerHTML =
      '<table><tbody><tr><td id="cell"></td></tr></tbody></table>';
    runScript();
    // 남은 예약 스윕까지 모두 소진 — 이후 제거는 관찰자만이 할 수 있다.
    vi.runAllTimers();

    const injected = document.createElement('div');
    injected.className = 'google-auto-placed';
    document.getElementById('cell').appendChild(injected);

    // MutationObserver 콜백은 microtask 로 전달된다.
    await Promise.resolve();
    await Promise.resolve();

    expect(document.querySelector('.google-auto-placed')).toBeNull();
    expect(document.querySelector('table')).not.toBeNull();
  });

  it('still wraps a non-table auto-placed ad injected after every sweep', async () => {
    document.body.innerHTML = '<div id="host"></div>';
    runScript();
    vi.runAllTimers();

    const injected = document.createElement('div');
    injected.className = 'google-auto-placed';
    document.getElementById('host').appendChild(injected);

    await Promise.resolve();
    await Promise.resolve();

    const ad = document.querySelector('.google-auto-placed');
    expect(ad).not.toBeNull();
    expect(ad.closest('.ad-container')).not.toBeNull();
  });

});

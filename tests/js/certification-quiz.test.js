// Regression tests for assets/js/certification-quiz.js
//
// certification-quiz.js is nearly byte-identical to aws-saa-quiz.js (see
// tests/js/aws-saa-quiz.test.js for the shared conversion/scoring logic
// walkthrough) with one structural difference: every localStorage key and
// downloaded filename is namespaced by a `certId` derived once, at script
// load time, from `window.location.pathname` via
// `getCertificationId()` (falls back to 'default' when the URL doesn't
// match `/certifications/<id>/`). These tests focus on that certId-specific
// behavior plus a representative slice of the shared quiz mechanics to
// confirm the shared logic still behaves the same way under this file.
//
// Same eval-and-drive-via-DOM-events technique as aws-saa-quiz.test.js:
// no exports exist, so we `new Function('window','document', SOURCE)` per
// test against a hand-built fixture. `location` is patched via delete +
// reassign (jsdom's documented workaround for the non-configurable
// window.location.hostname), matching tests/js/categories-page.test.js.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/certification-quiz.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function setLocationPath(pathname) {
  delete window.location;
  window.location = {
    hostname: 'localhost',
    href: `http://localhost${pathname}`,
    pathname,
    hash: '',
    origin: 'http://localhost',
  };
}

function runScript(handlerSink) {
  const origAdd = document.addEventListener.bind(document);
  document.addEventListener = (evt, handler, opts) => {
    handlerSink.push({ evt, handler, opts });
    return origAdd(evt, handler, opts);
  };
  try {
    // eslint-disable-next-line no-new-func
    new Function('window', 'document', SCRIPT_SOURCE)(window, document);
  } finally {
    document.addEventListener = origAdd;
  }
}

function questionCardHtml(num, { topic, text, options, answer, explanation }) {
  const optionsHtml = options
    .map((opt, idx) => `<p>${String.fromCharCode(65 + idx)}. ${opt}</p>`)
    .join('');
  return `
    <div class="question-card">
      <div class="question-header"><span class="question-number">문제 ${num}</span></div>
      <div class="question-topic">${topic}</div>
      <div class="question-text">${text}</div>
      <div class="question-options">${optionsHtml}</div>
      <div class="question-answer">
        <p>정답: ${answer}</p>
        <p><strong>해설:</strong> ${explanation}</p>
      </div>
    </div>`;
}

const Q1 = {
  topic: 'Security',
  text: 'What restricts unauthorized pod-to-pod traffic in a cluster?',
  options: ['NetworkPolicy', 'ConfigMap', 'Ingress', 'Service'],
  answer: 'A',
  explanation: 'A NetworkPolicy controls allowed traffic between pods.',
};

const Q2 = {
  topic: 'Storage',
  text: 'Which volume type persists data beyond pod lifecycle?',
  options: ['emptyDir', 'PersistentVolume', 'hostPath', 'configVolume'],
  answer: 'B',
  explanation: 'PersistentVolume survives pod restarts and rescheduling.',
};

function buildQuizFixture(questions, { wrapped = true } = {}) {
  const cardsHtml = questions.map((q, i) => questionCardHtml(i + 1, q)).join('');
  const inner = `
    <span id="total-questions"></span>
    <span id="progress-count"></span>
    <span id="accuracy-rate"></span>
    <select id="topic-filter">
      <option value="all">전체</option>
      <option value="Security">Security</option>
      <option value="Storage">Storage</option>
    </select>
    <input id="question-search" />
    <button type="button" class="view-button" data-view="card"></button>
    <button type="button" class="view-button" data-view="list"></button>
    <button type="button" id="reset-answers"></button>
    <button type="button" id="download-all-questions"></button>
    <div id="questions-container">${cardsHtml}</div>
    <div id="question-list-view"><table><tbody id="question-table-body"></tbody></table></div>
  `;
  document.body.innerHTML = wrapped ? `<div class="exam-questions">${inner}</div>` : inner;
}

function cardByNum(num) {
  return document.querySelectorAll('.question-card[data-converted]')[num - 1];
}

function selectOption(num, letter) {
  const radio = document.querySelector(`input[name="question-${num}"][value="${letter}"]`);
  radio.checked = true;
  radio.dispatchEvent(new Event('change', { bubbles: true }));
}

function clickCheck(num) {
  document.querySelector(`.check-button[data-question="${num}"]`).click();
}

describe('certification-quiz.js', () => {
  let registered;
  let originalAlert;
  let originalConfirm;

  beforeEach(() => {
    registered = [];
    localStorage.clear();
    document.body.innerHTML = '';
    originalAlert = window.alert;
    originalConfirm = window.confirm;
    window.alert = vi.fn();
    window.confirm = vi.fn(() => true);
    setLocationPath('/certifications/ckad/');
  });

  afterEach(() => {
    for (const r of registered) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    window.alert = originalAlert;
    window.confirm = originalConfirm;
    document.body.innerHTML = '';
    localStorage.clear();
    vi.restoreAllMocks();
  });

  describe('getCertificationId', () => {
    it('derives the localStorage key prefix from /certifications/<id>/ in the URL', () => {
      setLocationPath('/certifications/ckad/');
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');

      expect(localStorage.getItem('ckad-answers')).not.toBeNull();
      expect(JSON.parse(localStorage.getItem('ckad-answers'))['1']).toBe('A');
      expect(localStorage.getItem('aws-saa-answers')).toBeNull();
    });

    it('falls back to the "default" prefix when the URL has no /certifications/<id>/ segment', () => {
      setLocationPath('/some/other/page/');
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');

      expect(localStorage.getItem('default-answers')).not.toBeNull();
    });

    it('uses a different prefix per certification id so two certs do not collide in storage', () => {
      setLocationPath('/certifications/terraform-associate/');
      buildQuizFixture([Q1]);
      runScript(registered);
      selectOption(1, 'A');

      expect(localStorage.getItem('terraform-associate-answers')).not.toBeNull();
      expect(localStorage.getItem('ckad-answers')).toBeNull();
    });
  });

  describe('init / convertExistingQuestions (shared logic sanity)', () => {
    it('bails out silently when there is no .exam-questions ancestor', () => {
      buildQuizFixture([Q1], { wrapped: false });
      runScript(registered);

      expect(document.querySelector('.question-card').hasAttribute('data-converted')).toBe(false);
    });

    it('converts a raw card into an interactive card with radios and a hidden answer panel', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const card = cardByNum(1);
      expect(card.dataset.topic).toBe('Security');
      expect(card.dataset.answer).toBe('A');
      expect(card.querySelectorAll('.option-radio')).toHaveLength(4);
      expect(document.getElementById('answer-1').hidden).toBe(true);
      expect(document.getElementById('total-questions').textContent).toBe('1');
    });
  });

  describe('checkAnswer', () => {
    it('shows the correct icon and 100% accuracy for a right answer', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);

      expect(document.getElementById('status-1').innerHTML).toContain('status-icon correct');
      expect(document.getElementById('accuracy-rate').textContent).toBe('100%');
    });

    it('marks a wrong choice incorrect and highlights the real answer', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'C');
      clickCheck(1);

      expect(document.getElementById('status-1').innerHTML).toContain('status-icon incorrect');
      expect(document.querySelector('input[value="A"]').closest('.option-label').classList.contains('correct')).toBe(
        true
      );
    });

    it('alerts and makes no state change when nothing is selected', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      clickCheck(1);

      expect(window.alert).toHaveBeenCalledWith('답을 선택해주세요.');
      expect(document.getElementById('progress-count').textContent).toBe('0');
    });
  });

  describe('toggleExplanation', () => {
    it('reproduces the same inverted first-click hidden-state quirk as aws-saa-quiz.js', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const toggle = document.querySelector('.explanation-toggle[data-question="1"]');
      const answerDiv = document.getElementById('answer-1');

      toggle.click();
      expect(answerDiv.hidden).toBe(true);
      expect(toggle.getAttribute('aria-expanded')).toBe('true');

      toggle.click();
      expect(answerDiv.hidden).toBe(false);
      expect(toggle.getAttribute('aria-expanded')).toBe('false');
    });
  });

  describe('filterQuestions / searchQuestions', () => {
    it('topic filter shows only cards matching the selected topic', () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const select = document.getElementById('topic-filter');
      select.value = 'Storage';
      select.dispatchEvent(new Event('change', { bubbles: true }));

      expect(cardByNum(1).style.display).toBe('none');
      expect(cardByNum(2).style.display).toBe('');
    });

    it('search matches case-insensitively against question text', () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const search = document.getElementById('question-search');
      search.value = 'PERSISTENT';
      search.dispatchEvent(new Event('input', { bubbles: true }));

      expect(cardByNum(1).style.display).toBe('none');
      expect(cardByNum(2).style.display).toBe('');
    });
  });

  describe('switchView', () => {
    it('toggles card/list layout visibility', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      document.querySelector('.view-button[data-view="list"]').click();
      expect(document.getElementById('question-list-view').style.display).toBe('block');
      expect(document.getElementById('questions-container').classList.contains('hidden')).toBe(true);
    });
  });

  describe('download filenames and content use the certification id', () => {
    it('download-question uses the CERTID-prefixed filename and header', async () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const createSpy = vi.spyOn(URL, 'createObjectURL');
      const anchors = [];
      const origCreateElement = document.createElement.bind(document);
      vi.spyOn(document, 'createElement').mockImplementation((tag) => {
        const el = origCreateElement(tag);
        if (tag === 'a') anchors.push(el);
        return el;
      });

      document.querySelector('.download-question[data-question="1"]').click();

      const blob = createSpy.mock.calls[0][0];
      const text = await blob.text();
      expect(text).toContain('CKAD 기출문제 - 문제 1');
      const anchor = anchors.find((a) => a.download && a.download.startsWith('CKAD-'));
      expect(anchor).toBeDefined();
      expect(anchor.download).toBe('CKAD-문제-1.txt');
    });

    it('download-all-questions header and filename are also CERTID-prefixed', async () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const createSpy = vi.spyOn(URL, 'createObjectURL');
      document.getElementById('download-all-questions').click();

      const blob = createSpy.mock.calls[0][0];
      const text = await blob.text();
      expect(text).toContain('CKAD 기출문제 모음');
      expect(text).toContain('문제 1');
      expect(text).toContain('문제 2');
    });
  });

  describe('resetAllAnswers', () => {
    it('clears the CERTID-prefixed localStorage keys when confirmed', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);
      window.confirm = vi.fn(() => true);

      document.getElementById('reset-answers').click();

      expect(localStorage.getItem('ckad-answers')).toBeNull();
      expect(localStorage.getItem('ckad-checked')).toBeNull();
      expect(document.getElementById('progress-count').textContent).toBe('0');
    });

    it('does nothing when the confirm dialog is cancelled', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);
      window.confirm = vi.fn(() => false);

      document.getElementById('reset-answers').click();

      expect(localStorage.getItem('ckad-answers')).not.toBeNull();
      expect(document.getElementById('progress-count').textContent).toBe('1');
    });
  });

  describe('loadSavedAnswers (init path)', () => {
    it('restores answers saved under this certId prefix, ignoring other certs', () => {
      localStorage.setItem('ckad-answers', JSON.stringify({ '1': 'A' }));
      localStorage.setItem('ckad-checked', JSON.stringify({ '1': true }));
      localStorage.setItem('ckad-stats', JSON.stringify({ total: 1, answered: 1, correct: 1 }));
      // A different cert's saved state must not leak in.
      localStorage.setItem('terraform-associate-answers', JSON.stringify({ '1': 'C' }));

      buildQuizFixture([Q1]);
      runScript(registered);

      expect(document.querySelector('input[value="A"]').checked).toBe(true);
      expect(document.getElementById('accuracy-rate').textContent).toBe('100%');
    });

    it('ignores corrupted JSON without throwing', () => {
      localStorage.setItem('ckad-answers', '{not valid json');
      buildQuizFixture([Q1]);

      expect(() => runScript(registered)).not.toThrow();
      expect(document.getElementById('progress-count').textContent).toBe('0');
    });
  });
});

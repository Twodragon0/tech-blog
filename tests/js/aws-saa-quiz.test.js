// Regression tests for assets/js/aws-saa-quiz.js
//
// aws-saa-quiz.js is an IIFE that, on init(), converts static "question-card"
// markup (rendered by Jekyll from front matter) into an interactive quiz:
// it builds radio inputs from `<p>A. ...</p>` option paragraphs, wires up
// check/explanation buttons, tracks answered/correct counts in a closured
// `state` object, mirrors that state into localStorage (`aws-saa-*` keys),
// and renders a separate sortable/searchable table view of the same cards.
// All state lives inside the IIFE closure — there is nothing exported —
// so, following the pattern in tests/js/chat-widget.test.js and
// tests/js/toc.test.js, we eval the script fresh per test via `new Function`
// against a hand-built DOM fixture and drive it exclusively through real
// DOM events (click/change/input), then assert on the resulting DOM state
// and localStorage.
//
// Three `document.addEventListener(...)` calls (two 'click', one 'change')
// are registered directly on `document` inside setupEventListeners() on
// every run. Since `document` persists across tests within this file, we
// capture and remove those handlers in afterEach (same technique as
// tests/js/chat-widget.test.js's `registered` sink) so listeners from a
// previous test's eval don't double-fire on the next test's fixture.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/aws-saa-quiz.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

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

/**
 * Builds one `.question-card` block matching the static markup the Jekyll
 * layout renders before aws-saa-quiz.js converts it.
 */
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
  topic: 'Networking',
  text: 'What load balancer type should sit in a public subnet?',
  options: ['ALB in public subnet', 'NLB in private subnet', 'CLB in public subnet', 'ALB in private subnet'],
  answer: 'A',
  explanation: 'ALB in a public subnet accepts internet traffic safely.',
};

const Q2 = {
  topic: 'IAM',
  text: 'Which service enforces org-wide guardrails across accounts?',
  options: ['IAM Policy', 'Service Control Policy', 'Resource Policy', 'Security Group'],
  answer: 'B',
  explanation: 'SCPs apply at the AWS Organizations level.',
};

/**
 * Builds the full quiz page fixture. `wrapped` controls whether the
 * `#questions-container` lives inside a `.exam-questions` ancestor — init()
 * bails out entirely when that ancestor is missing.
 */
function buildQuizFixture(questions, { wrapped = true } = {}) {
  const cardsHtml = questions.map((q, i) => questionCardHtml(i + 1, q)).join('');
  const inner = `
    <span id="total-questions"></span>
    <span id="progress-count"></span>
    <span id="accuracy-rate"></span>
    <select id="topic-filter">
      <option value="all">전체</option>
      <option value="Networking">Networking</option>
      <option value="IAM">IAM</option>
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

describe('aws-saa-quiz.js', () => {
  let registered;
  let originalAlert;
  let originalConfirm;
  let originalScrollIntoView;

  beforeEach(() => {
    registered = [];
    localStorage.clear();
    document.body.innerHTML = '';
    originalAlert = window.alert;
    originalConfirm = window.confirm;
    window.alert = vi.fn();
    window.confirm = vi.fn(() => true);
    originalScrollIntoView = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    for (const r of registered) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    window.alert = originalAlert;
    window.confirm = originalConfirm;
    Element.prototype.scrollIntoView = originalScrollIntoView;
    document.body.innerHTML = '';
    localStorage.clear();
    vi.useRealTimers();
    // vi.spyOn on the same object+method returns the cached spy across
    // calls, so without restoring, a later test's `.mock.calls[0]` would
    // read a call recorded by an earlier test. Always restore.
    vi.restoreAllMocks();
  });

  describe('init / convertExistingQuestions', () => {
    it('bails out silently when there is no .exam-questions ancestor', () => {
      buildQuizFixture([Q1], { wrapped: false });
      runScript(registered);

      const card = document.querySelector('.question-card');
      expect(card.hasAttribute('data-converted')).toBe(false);
      expect(document.querySelector('.option-radio')).toBeNull();
    });

    it('converts a raw card into an interactive card with radios, actions, and a hidden answer panel', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const card = cardByNum(1);
      expect(card.dataset.topic).toBe('Networking');
      expect(card.dataset.answer).toBe('A');

      const radios = card.querySelectorAll('.option-radio');
      expect(radios).toHaveLength(4);
      expect(radios[0].name).toBe('question-1');
      expect(radios[0].getAttribute('aria-label')).toBe('선택지 A');

      expect(card.querySelector('.check-button')).not.toBeNull();
      expect(card.querySelector('.explanation-toggle')).not.toBeNull();

      const answerDiv = card.querySelector('.question-answer');
      expect(answerDiv.hidden).toBe(true);
      expect(answerDiv.id).toBe('answer-1');
      // The original "<strong>해설:</strong> " prefix is stripped from the
      // extracted HTML, then a single fresh "해설: " label is prepended —
      // so the rendered panel carries exactly one label, not a duplicate.
      expect(answerDiv.querySelector('.answer-explanation').textContent).toBe(
        '해설: ALB in a public subnet accepts internet traffic safely.'
      );

      expect(document.getElementById('total-questions').textContent).toBe('1');
    });

    it('skips a card with no recognizable "문제 N" header (study-tip cards) while still converting real questions', () => {
      buildQuizFixture([Q1]);
      const container = document.getElementById('questions-container');
      container.insertAdjacentHTML(
        'beforeend',
        `<div class="question-card">
           <div class="question-header"><span class="question-number">학습 전략</span></div>
           <div class="question-answer"><p>알아두면 좋은 팁입니다.</p></div>
         </div>`
      );

      runScript(registered);

      const cards = document.querySelectorAll('.question-card');
      expect(cards[0].hasAttribute('data-converted')).toBe(true);
      expect(cards[1].hasAttribute('data-converted')).toBe(false);
    });
  });

  describe('answer selection', () => {
    it('selecting a radio marks the label selected and persists the choice to localStorage', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'B');

      const label = document.querySelector('input[value="B"]').closest('.option-label');
      expect(label.classList.contains('selected')).toBe(true);

      const saved = JSON.parse(localStorage.getItem('aws-saa-answers'));
      expect(saved['1']).toBe('B');

      const statusEl = document.getElementById('status-1');
      expect(statusEl.innerHTML).toContain('status-icon pending');
    });
  });

  describe('checkAnswer', () => {
    it('shows the correct icon and 100% accuracy when the checked answer is right', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);

      expect(document.getElementById('status-1').innerHTML).toContain('status-icon correct');
      expect(document.getElementById('progress-count').textContent).toBe('1');
      expect(document.getElementById('accuracy-rate').textContent).toBe('100%');

      const answerDiv = document.getElementById('answer-1');
      expect(answerDiv.hidden).toBe(false);
      expect(answerDiv.classList.contains('show')).toBe(true);
    });

    it('marks the wrong choice incorrect, highlights the real answer, and reports 0% accuracy', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'C');
      clickCheck(1);

      expect(document.getElementById('status-1').innerHTML).toContain('status-icon incorrect');
      const wrongLabel = document.querySelector('input[value="C"]').closest('.option-label');
      const correctLabel = document.querySelector('input[value="A"]').closest('.option-label');
      expect(wrongLabel.classList.contains('incorrect')).toBe(true);
      expect(correctLabel.classList.contains('correct')).toBe(true);
      expect(document.getElementById('accuracy-rate').textContent).toBe('0%');
    });

    it('alerts and makes no state change when checking with nothing selected', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      clickCheck(1);

      expect(window.alert).toHaveBeenCalledWith('답을 선택해주세요.');
      expect(document.getElementById('status-1').innerHTML).toBe('');
      expect(document.getElementById('progress-count').textContent).toBe('0');
    });

    it('rechecking after switching to the correct answer updates the icon but the accuracy % stays stuck (state-write-order quirk)', () => {
      // Regression guard: checkAnswer() writes state.answers[questionId] = answer
      // BEFORE computing prevCorrect in the "already checked" branch, so
      // prevCorrect always equals the freshly-computed isCorrect and the
      // stats.correct counter is never adjusted on recheck — even though the
      // status icon (computed separately, after the branch) does update.
      // This locks in that actual (surprising) shipped behavior.
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'C'); // wrong
      clickCheck(1);
      expect(document.getElementById('accuracy-rate').textContent).toBe('0%');

      selectOption(1, 'A'); // now correct
      clickCheck(1);

      // Visual icon reflects the new (correct) answer...
      expect(document.getElementById('status-1').innerHTML).toContain('status-icon correct');
      // ...but the accuracy stat never got bumped back up.
      expect(document.getElementById('accuracy-rate').textContent).toBe('0%');
      expect(document.getElementById('progress-count').textContent).toBe('1');
    });
  });

  describe('toggleExplanation', () => {
    // Regression guard for a real inverted-state quirk: toggleExplanation()
    // reads `isExpanded` from the CURRENT aria-expanded value, then sets
    // `answerDiv.hidden = !isExpanded` — the negation of the pre-click
    // state, not of the intended post-click state. Net effect: the first
    // click flips aria-expanded/label to "expanded" while the panel stays
    // hidden; the second click is what actually reveals it. We lock in the
    // real observed sequence rather than the (different) intended one.
    it('toggles aria-expanded and the button label out of step with the actual hidden state', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const toggle = document.querySelector('.explanation-toggle[data-question="1"]');
      const answerDiv = document.getElementById('answer-1');

      toggle.click();
      expect(toggle.getAttribute('aria-expanded')).toBe('true');
      expect(answerDiv.hidden).toBe(true);
      expect(toggle.querySelector('.explanation-text').textContent).toBe('해설 숨기기');

      toggle.click();
      expect(toggle.getAttribute('aria-expanded')).toBe('false');
      expect(answerDiv.hidden).toBe(false);
      expect(toggle.querySelector('.explanation-text').textContent).toBe('해설 보기');
    });
  });

  describe('filterQuestions (topic-filter)', () => {
    it('hides cards not matching the selected topic and "all" shows everything again', () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const select = document.getElementById('topic-filter');
      select.value = 'IAM';
      select.dispatchEvent(new Event('change', { bubbles: true }));

      expect(cardByNum(1).style.display).toBe('none');
      expect(cardByNum(2).style.display).toBe('');

      select.value = 'all';
      select.dispatchEvent(new Event('change', { bubbles: true }));

      expect(cardByNum(1).style.display).toBe('');
      expect(cardByNum(2).style.display).toBe('');
    });
  });

  describe('searchQuestions', () => {
    it('filters cards by case-insensitive match on question text, topic, or option text', () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const search = document.getElementById('question-search');
      search.value = 'guardrails';
      search.dispatchEvent(new Event('input', { bubbles: true }));

      expect(cardByNum(1).style.display).toBe('none');
      expect(cardByNum(2).style.display).toBe('');
    });

    it('also filters the list-view table rows via filterQuestionTable', () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const search = document.getElementById('question-search');
      search.value = 'networking';
      search.dispatchEvent(new Event('input', { bubbles: true }));

      const rows = document.querySelectorAll('#question-table-body tr');
      expect(rows[0].style.display).toBe('');
      expect(rows[1].style.display).toBe('none');
    });
  });

  describe('switchView', () => {
    it('toggles between card and list layouts and marks the active view button', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const listBtn = document.querySelector('.view-button[data-view="list"]');
      const cardBtn = document.querySelector('.view-button[data-view="card"]');
      const listView = document.getElementById('question-list-view');
      const cardView = document.getElementById('questions-container');

      listBtn.click();
      expect(listView.style.display).toBe('block');
      expect(cardView.classList.contains('hidden')).toBe(true);
      expect(listBtn.classList.contains('active')).toBe(true);

      cardBtn.click();
      expect(listView.style.display).toBe('none');
      expect(cardView.classList.contains('hidden')).toBe(false);
      expect(cardBtn.classList.contains('active')).toBe(true);
    });
  });

  describe('generateQuestionTable', () => {
    it('builds one row per converted question and truncates question text over 80 chars', () => {
      const longQ = { ...Q1, text: 'x'.repeat(90) };
      buildQuizFixture([longQ, Q2]);
      runScript(registered);

      const rows = document.querySelectorAll('#question-table-body tr');
      expect(rows).toHaveLength(2);
      expect(rows[0].cells[1].textContent).toBe('x'.repeat(80) + '...');
      expect(rows[1].cells[1].textContent).toBe(Q2.text);
    });

    it('strips angle-bracket and quote characters from topic text in table cells', () => {
      buildQuizFixture([Q1]);
      // Set the raw topic text programmatically (assigning textContent is
      // always literal — this avoids the HTML parser turning a "<script>"
      // substring into a real element) BEFORE the one-time conversion pass
      // that generateQuestionTable() reads dataset.topic from.
      document.querySelector('.question-topic').textContent = `<script>'quote"`;
      runScript(registered);

      const row = document.querySelector('#question-table-body tr');
      expect(row.cells[2].textContent).toBe('scriptquote');
    });

    it('clicking a table link switches to card view and scrolls to + highlights the target question', () => {
      vi.useFakeTimers();
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const listBtn = document.querySelector('.view-button[data-view="list"]');
      listBtn.click();
      expect(document.getElementById('questions-container').classList.contains('hidden')).toBe(true);

      const link = document.querySelector('#question-table-body tr a.table-link');
      link.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      // switchView('card') runs synchronously inside the click handler.
      expect(document.getElementById('questions-container').classList.contains('hidden')).toBe(false);

      vi.advanceTimersByTime(100);

      const target = cardByNum(1);
      expect(target.id).toBe('question-1');
      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
      expect(target.style.animation).toContain('highlight');
    });
  });

  describe('download', () => {
    it('download-question includes only the question text, not the answer/explanation', async () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const createSpy = vi.spyOn(URL, 'createObjectURL');
      document.querySelector('.download-question[data-question="1"]').click();

      const blob = createSpy.mock.calls[0][0];
      const text = await blob.text();
      expect(text).toContain(Q1.text);
      expect(text).not.toContain('정답:');
    });

    it('download-both includes the answer and explanation text', async () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const createSpy = vi.spyOn(URL, 'createObjectURL');
      document.querySelector('.download-both[data-question="1"]').click();

      const blob = createSpy.mock.calls[0][0];
      const text = await blob.text();
      expect(text).toContain('정답: A');
      expect(text).toContain(Q1.explanation);
    });

    it('download-all-questions bundles every question separated by dashed rules', async () => {
      buildQuizFixture([Q1, Q2]);
      runScript(registered);

      const createSpy = vi.spyOn(URL, 'createObjectURL');
      document.getElementById('download-all-questions').click();

      const blob = createSpy.mock.calls[0][0];
      const text = await blob.text();
      expect(text).toContain('문제 1');
      expect(text).toContain('문제 2');
      expect(text).toContain('-'.repeat(50));
    });
  });

  describe('resetAllAnswers', () => {
    it('does nothing when the user cancels the confirm dialog', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);
      window.confirm = vi.fn(() => false);

      document.getElementById('reset-answers').click();

      expect(document.getElementById('progress-count').textContent).toBe('1');
      expect(document.querySelector('input[value="A"]').checked).toBe(true);
    });

    it('clears radios, status icons, answer panels, and localStorage when confirmed', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      selectOption(1, 'A');
      clickCheck(1);
      window.confirm = vi.fn(() => true);

      document.getElementById('reset-answers').click();

      expect(document.querySelector('input[value="A"]').checked).toBe(false);
      expect(document.getElementById('status-1').innerHTML).toBe('');
      expect(document.getElementById('answer-1').hidden).toBe(true);
      expect(document.getElementById('progress-count').textContent).toBe('0');
      expect(document.getElementById('accuracy-rate').textContent).toBe('0%');
      expect(localStorage.getItem('aws-saa-answers')).toBeNull();
      expect(localStorage.getItem('aws-saa-checked')).toBeNull();
    });
  });

  describe('loadSavedAnswers (init path)', () => {
    it('restores a previously checked correct answer and re-renders stats on load', () => {
      localStorage.setItem('aws-saa-answers', JSON.stringify({ '1': 'A' }));
      localStorage.setItem('aws-saa-checked', JSON.stringify({ '1': true }));
      localStorage.setItem('aws-saa-stats', JSON.stringify({ total: 1, answered: 1, correct: 1 }));

      buildQuizFixture([Q1]);
      runScript(registered);

      expect(document.querySelector('input[value="A"]').checked).toBe(true);
      expect(document.getElementById('status-1').innerHTML).toContain('status-icon correct');
      expect(document.getElementById('progress-count').textContent).toBe('1');
      expect(document.getElementById('accuracy-rate').textContent).toBe('100%');
      expect(document.getElementById('answer-1').hidden).toBe(false);
    });

    it('ignores corrupted JSON in localStorage without throwing', () => {
      localStorage.setItem('aws-saa-answers', '{not valid json');
      buildQuizFixture([Q1]);

      expect(() => runScript(registered)).not.toThrow();
      expect(document.getElementById('progress-count').textContent).toBe('0');
    });
  });

  describe('private-browsing resilience (safe localStorage wrappers)', () => {
    it('selecting an answer does not throw even when localStorage.setItem is unavailable', () => {
      buildQuizFixture([Q1]);
      runScript(registered);

      const originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = () => {
        throw new DOMException('QuotaExceededError');
      };

      try {
        expect(() => selectOption(1, 'A')).not.toThrow();
        const label = document.querySelector('input[value="A"]').closest('.option-label');
        expect(label.classList.contains('selected')).toBe(true);
      } finally {
        Storage.prototype.setItem = originalSetItem;
      }
    });
  });
});

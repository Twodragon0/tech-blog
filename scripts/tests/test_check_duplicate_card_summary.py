#!/usr/bin/env python3
"""Behaviour + wiring tests for ``scripts/check_duplicate_card_summary.py``.

The gate exists because `_includes/news-card.html:54` renders the card's
``summary=`` and the generator's fallback then printed the same text again under
``#### 요약``. Measured 2026-09-10 before the fix: 1,583 of 2,043 adjacent blocks
(77%) byte-identical to their card, across 193 of 217 digests.

Both halves are asserted: it must catch the duplicate, and it must NOT flag a
block that carries more than the card. A gate that fails on the second is worse
than none — it would push someone to delete the tail of every long summary.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "check_duplicate_card_summary.py"

_spec = importlib.util.spec_from_file_location(
    "check_duplicate_card_summary", MODULE_PATH
)
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

SVG_LINT = REPO_ROOT / ".github" / "workflows" / "svg-lint.yml"
BLOGWATCHER = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
SCRIPT_REL = "scripts/check_duplicate_card_summary.py"


def _post(summary: str, block: str | None, *, fenced: bool = False) -> str:
    card = (
        "{% include news-card.html\n"
        '  title="t"\n'
        '  url="https://example.com/a"\n'
        f'  summary="{summary}"\n'
        '  source="S"\n'
        '  severity="Medium"\n'
        "%}\n"
    )
    body = f"### 1.1 t\n\n{card}\n"
    if block is not None:
        body += f"#### 요약\n\n{block}\n\n"
    body += "#### 권장 조치\n\n- do a thing\n"
    if fenced:
        body = "```markdown\n" + body + "```\n"
    return "---\nlayout: post\n---\n\n" + body


class TestDetection:
    def test_identical_body_is_a_violation(self):
        s = "카드와 같은 문장입니다."
        assert gate.find_violations(_post(s, s)), "byte-identical duplicate not caught"

    def test_longer_body_is_not_a_violation(self):
        """Direction: the card truncates at 200 chars; the tail must survive."""
        s = "앞부분입니다."
        assert (
            gate.find_violations(_post(s, s + " 그리고 카드에 없는 뒷부분입니다."))
            == []
        )

    def test_absent_block_is_not_a_violation(self):
        assert gate.find_violations(_post("무언가입니다.", None)) == []

    def test_different_body_is_not_a_violation(self):
        assert gate.find_violations(_post("카드 문장.", "완전히 다른 분석 문장.")) == []

    def test_non_adjacent_block_is_not_attributed_to_this_card(self):
        """A block after intervening prose belongs to something else."""
        s = "카드 문장입니다."
        text = _post(s, None).replace(
            "#### 권장 조치",
            f"분석 문단이 먼저 옵니다.\n\n#### 요약\n\n{s}\n\n#### 권장 조치",
        )
        assert gate.find_violations(text) == []

    def test_fenced_example_is_ignored(self):
        """Docs showing the anti-pattern inside ``` must not fail the gate."""
        s = "카드와 같은 문장입니다."
        assert gate.find_violations(_post(s, s, fenced=True)) == []


class TestEscapingAwareComparison:
    """The 66 pairs that read as one sentence twice but never matched byte-wise.

    The gate's first version compared bytes and named this as a follow-up,
    estimating ~32. Measured 2026-09-11: 66 of the 289 remaining adjacent pairs
    — 45 quote-shape, 11 quote-shape + backslash, 1 backslash, 9 differing only
    by a trailing period.

    Each case below is one fold. They are asserted separately so a regression
    says which fold was lost, and paired with a near-miss that must still be
    reported as different — a normaliser that folds too much is the failure mode
    this class exists to catch.
    """

    def test_straight_vs_curly_quotes(self):
        assert gate.find_violations(
            _post("'MacroMaze' 웹훅 백도어입니다.", "“MacroMaze” 웹훅 백도어입니다.")
        ), "quote-shape-only difference not caught (45 of the 66)"

    def test_backslash_escaped_quotes(self):
        assert gate.find_violations(
            _post("\\”개인의 생산성\\” 질문입니다.", "”개인의 생산성” 질문입니다.")
        ), "backslash-escaped quotes not caught (11 of the 66)"

    def test_trailing_period_only(self):
        assert gate.find_violations(
            _post("AWS DevOps Agent 소개입니다.", "AWS DevOps Agent 소개입니다")
        ), "trailing-period-only difference not caught (9 of the 66)"

    def test_whitespace_run(self):
        assert gate.find_violations(
            _post("두   칸 띄어쓰기 문장입니다.", "두 칸 띄어쓰기 문장입니다.")
        )

    def test_one_real_character_is_still_a_difference(self):
        """The control. Folding must not reach actual content.

        The whole safety argument for folding is that no pair loses characters a
        reader would miss: stripping quotes, backslashes, whitespace and periods
        from both sides gave a length delta of 0 for all 66 live cases. A single
        extra word must therefore still read as different.
        """
        assert (
            gate.find_violations(
                _post("'MacroMaze' 백도어입니다.", "“MacroMaze” 신규 백도어입니다.")
            )
            == []
        ), "one added word was folded away — the normaliser reaches content"

    def test_a_different_number_is_a_difference(self):
        assert gate.find_violations(_post("CVSS 9.4 입니다.", "CVSS 9.9 입니다.")) == []

    def test_canonical_leaves_interior_punctuation_alone(self):
        """Only a TRAILING mark is folded; a sentence break is content."""
        assert gate.canonical("가. 나") != gate.canonical("가 나")
        assert gate.canonical("가 나.") == gate.canonical("가 나")


class TestEntityAndEmphasisFolds:
    """The 6 pairs left over after the escaping-aware pass (2026-09-13).

    Measured over the 223 adjacent pairs that survived #714: 5 differ only by
    ``&quot;`` facing a bare ``"``, and 1 only by markdown ``**`` the card does
    not carry. Both read as the same sentence twice.

    The folds are deliberately narrow. The entity fold names the quote
    entities instead of calling ``html.unescape``, which would also rewrite
    ``&amp;``/``&lt;`` and — for the entities Python matches without a trailing
    semicolon — stretches of ordinary prose. The emphasis fold requires a
    matching pair, so arithmetic is out of reach. A false negative here costs a
    duplicated sentence; a false positive fails a fail-closed publish, so the
    asymmetry is priced in on purpose.
    """

    def test_quote_entity_matches_the_bare_character(self):
        assert gate.find_violations(
            _post(
                "랜섬웨어 &quot;Reynolds&quot;가 EDR을 무력화합니다.",
                '랜섬웨어 "Reynolds"가 EDR을 무력화합니다.',
            )
        ), '&quot; vs " not caught (5 of the 6)'

    def test_the_sibling_quote_entities_are_folded_too(self):
        """None of these are live; a generator emitting one can emit the rest."""
        for ent in ("&apos;", "&#39;", "&#x27;", "&ldquo;", "&rsquo;", "&QUOT;"):
            assert gate.canonical(f"앞 {ent}가운데{ent} 뒤") == gate.canonical(
                "앞 가운데 뒤"
            ), f"{ent} survived the fold"

    def test_paired_markdown_emphasis_is_markup_not_content(self):
        assert gate.find_violations(
            _post(
                "이번 사례는 사회공학적 신뢰 조작의 전형입니다.",
                "이번 사례는 **사회공학적 신뢰 조작**의 전형입니다.",
            )
        ), "** vs no ** not caught (1 of the 6)"

    def test_a_single_unpaired_run_is_left_alone(self):
        """One `**` run has nothing to pair with, so an exponent survives.

        Stripping every `**` unconditionally would make `2**8` read as `28` —
        the one way this fold could reach content rather than markup. See
        ``test_two_exponent_runs_do_pair_with_each_other`` for where that
        protection ends.
        """
        assert gate.canonical("2**8 회 반복합니다") != gate.canonical(
            "28 회 반복합니다"
        )
        assert (
            gate.find_violations(_post("28회 반복합니다.", "2**8회 반복합니다.")) == []
        )

    def test_two_exponent_runs_do_pair_with_each_other(self):
        """Known limit, pinned so nobody re-derives the wrong reassurance.

        "Paired" is satisfied by the closing ``**`` of a DIFFERENT expression,
        so two runs in one string fold into each other. An earlier version of
        this file claimed `2**8` could never become `28`; that holds only for a
        single run, and the fixture above happened to be exactly that case.

        Why it is left open: the fold deletes markers, never content, so the
        worst outcome is two tokens joining. Measured 2026-09-13 over the 297
        posts — 12,718 emphasis matches, **0** where the removal joins two
        ASCII alphanumerics. (A bare ``isalnum()`` reports 1,566, because
        Hangul is alphanumeric and ``**강조**의`` → ``강조의`` counts; that is
        the fold working, not the hazard.) And the producer cannot reach this
        at all — the card is a derivative of the block, so both sides fold
        identically.
        """
        assert gate.canonical("2**8 + 3**4") == gate.canonical("28 + 34")
        assert gate.canonical("2**32 개와 2**64 개") == gate.canonical(
            "232 개와 264 개"
        )

    def test_space_padded_markers_are_not_emphasis(self):
        """Pins the ``(?=\\S)`` / ``(?<=\\S)`` guards.

        Markdown does not bold ``** x **``, and these guards are what keeps
        spaced arithmetic out of the fold: without them ``2 ** 8 + 3 ** 4``
        collapses to ``2 8 + 3 4``. Deleting them used to break no test at all,
        which is the reason this assertion exists.
        """
        assert gate.canonical("2 ** 8 + 3 ** 4") != gate.canonical("2 8 + 3 4")
        assert gate.canonical("** 공백 ** 입니다") == "** 공백 ** 입니다"

    def test_emphasised_text_that_actually_differs_is_still_different(self):
        assert (
            gate.find_violations(
                _post("**탐지 룰** 보강입니다.", "**패치 적용** 보강입니다.")
            )
            == []
        )

    def test_non_quote_entities_are_out_of_scope(self):
        """Scope marker, not a requirement.

        `&amp;` and `&lt;` render as `&` and `<`, so folding them would be
        defensible — but no live pair needs it, and each added entity is
        another chance to merge two different sentences. Widening this is a
        change with its own evidence, not a silent drift.
        """
        assert gate.canonical("A &amp; B") != gate.canonical("A & B")


class TestCorpusIsGreen:
    def test_live_corpus_has_no_violations(self):
        """A gate wired while red is a gate that gets muted."""
        offenders = {
            p.name: v
            for p in sorted((REPO_ROOT / "_posts").glob("*.md"))
            if (v := gate.check_post(p))
        }
        assert offenders == {}, (
            f"{sum(len(v) for v in offenders.values())} duplicate block(s) in "
            f"{len(offenders)} post(s): {sorted(offenders)[:5]}"
        )


class TestWiring:
    """A gate nobody runs has never been right — the repo's own rule."""

    def test_wired_into_svg_lint_corpus_sweep(self):
        body = "\n".join(
            ln
            for ln in SVG_LINT.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip().startswith("#")
        )
        assert re.search(rf"python3 {re.escape(SCRIPT_REL)} --all", body), (
            "svg-lint.yml no longer runs the corpus sweep. That schedule-driven "
            "--all run is what sees a cron-published digest: the bot's "
            "GITHUB_TOKEN push fires no push event."
        )

    def test_wired_into_publish_preflight(self):
        body = "\n".join(
            ln
            for ln in BLOGWATCHER.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip().startswith("#")
        )
        assert SCRIPT_REL in body, (
            "ai-blogwatcher.yml no longer runs this gate before committing. The "
            "generator is the producer of this defect, so the publish path is "
            "where it has to be caught."
        )

    def test_preflight_invocation_is_not_swallowed(self):
        body = BLOGWATCHER.read_text(encoding="utf-8")
        at = body.index(SCRIPT_REL)
        line = body[body.rfind("\n", 0, at) + 1 : body.find("\n", at)]
        assert "|| true" not in line and "|| :" not in line, (
            f"the pre-flight invocation is neutralised: {line.strip()!r}"
        )

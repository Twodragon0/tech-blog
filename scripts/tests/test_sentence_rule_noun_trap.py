#!/usr/bin/env python3
"""Guard: the dangling-ending deny-list judges grammar, not substrings.

``_DANGLING_ENDING_RE`` lists ``할`` as a prospective modifier (``수행할``,
``필요할``). But ``할`` is also the last syllable of the ordinary nouns 역할,
분할 and 관할, so before the lookbehind was added the rule reported
``주요 역할`` and ``네트워크 분할`` as incomplete sentences.

Measured 2026-09-09 over 52996 units (checklist items + card attributes +
table cells): terminal ``할`` matched 25, of which 23 were those nouns and 2
were real truncations. The exclusion costs nothing measurable — terminal
번역할 / 구분할 / 배분할 / 통역할 occur 0 times in this corpus.

Why the test lives here and not in test_auto_publish_qa.py: that file pins the
gate's contract, this one pins a specific linguistic trap and the corpus
measurement behind it. Keeping them apart means a future deny-list change has
to confront the measurement rather than adjust one assertion.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from news.qa_gate import validate_sentence_completeness

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS = REPO_ROOT / "_posts"


def _checklist(text: str) -> str:
    return f"- [ ] {text}\n"


# Nouns whose final syllable is 할. Flagging these is a substring accident.
NOUNS_ENDING_IN_HAL = [
    "과도한 권한을 가진 IAM 사용자/역할",
    "네트워크 분할",
    "담당자의 주요 역할",
    "작은 단위로 작업 분할",
    "데이터 주권과 법적 관할",
]

# Verb stem + prospective modifier -ㄹ. These are genuinely dangling and must
# still be caught, or the fix above would have been a silent disabling.
GENUINE_PROSPECTIVE = [
    "이 작업을 수행할",
    "추가 조치가 필요할",
    "미사용 리소스를 삭제할",
    "다른 기체가 존재할",
    "이후 효용이 감소할",
    "여러 팀에서 문제가 반복될",
]


@pytest.mark.parametrize("text", NOUNS_ENDING_IN_HAL)
def test_a_noun_ending_in_hal_is_not_dangling(text):
    assert not validate_sentence_completeness(_checklist(text)), (
        f"{text!r} was flagged as incomplete. 역할/분할/관할 are nouns; the "
        "deny-list's `할` is meant to catch a verb stem plus -ㄹ. If a new "
        "noun of this shape appears, extend the lookbehind — do not widen the "
        "accept-list, which would mask real truncations too."
    )


@pytest.mark.parametrize("text", GENUINE_PROSPECTIVE)
def test_a_real_prospective_modifier_is_still_caught(text):
    """Control. Without this, the lookbehind could have disabled `할` entirely."""
    assert validate_sentence_completeness(_checklist(text)), (
        f"{text!r} is a verb stem plus -ㄹ and must still be reported. The "
        "lookbehind excludes only 역/분/관 before 할."
    )


def test_the_lookbehind_is_narrow_and_explicit():
    """A blanket removal of `할` would pass every test above except this one.

    ``GENUINE_PROSPECTIVE`` covers verbs whose stems do not end in 역/분/관, so
    dropping `할` from the deny-list would break them — but replacing the
    lookbehind with something broad (say ``[^ ]할``) would not, while quietly
    losing single-word items. Pin the intent.
    """
    from news import qa_gate

    source = Path(qa_gate.__file__).read_text(encoding="utf-8")
    assert "(?<![역분관])할" in source, (
        "the narrow lookbehind is gone. 역할/분할/관할 are the three nouns "
        "measured in this corpus; a broader exclusion starts losing verbs."
    )


def test_the_corpus_still_has_no_noun_hal_checklist_item():
    """Canary on the measurement, not on the code.

    The 23 noun matches all lived in table cells, which this rule does not
    scan — so the fix changes 0 corpus outcomes today. If a checklist item of
    this shape ever lands, this test starts failing and tells the next reader
    that the fix above is now load-bearing rather than precautionary.
    """
    offenders = []
    for post in sorted(POSTS.glob("*.md")):
        for line in post.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not re.match(r"^- \[[ xX]\] ", stripped):
                continue
            text = re.sub(r"^- \[[ xX]\]\s*", "", stripped).strip()
            if re.search(r"[역분관]할\s*\**\s*$", text):
                offenders.append((post.name, text))
    assert not offenders, (
        f"a checklist item now ends in a 할-noun: {offenders[:3]}. Not a "
        "failure — the lookbehind is what keeps these from being reported. "
        "Update this canary's docstring and move on."
    )


def test_the_rule_still_reports_nothing_over_the_whole_corpus():
    """The premise of the keep-advisory verdict, pinned.

    0 of 2052 items. This is not asserted as a quality claim — it is the number
    the verdict reasoned from, so a change in it should surface as a test
    result rather than be discovered later. If it becomes non-zero, the rule
    has caught something real and the promotion question is worth reopening
    with fresh evidence.
    """
    firing = []
    for post in sorted(POSTS.glob("*.md")):
        issues = validate_sentence_completeness(post.read_text(encoding="utf-8"))
        if issues:
            firing.append((post.name, issues[0]))
    assert not firing, (
        f"validate_sentence_completeness now fires on {len(firing)} post(s): "
        f"{firing[:3]}. Read them before changing anything — either a real "
        "truncation landed (fix the post) or the deny-list gained a false "
        "positive (fix the pattern, and add the case to this file)."
    )

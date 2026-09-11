#!/usr/bin/env python3
"""Tests for ``scripts/check_excerpt_promises.py`` and the promise-aware closer.

The defect
----------
``seo_diversify_excerpts.py`` picked an excerpt's closing sentence from a hash
of the FILENAME. The closers make specific claims — a table of IoCs, an SBOM
section, a SOC discussion — and nothing checked the body. Measured 2026-09-10
over the 217 non-rollup digests, 150 carried a promise the text does not keep:
``공격 경로`` appeared in 1 of the 42 posts whose excerpt promised it, SOC in 8
of 42, SBOM in 21 of 50, an IoC table in 6 of 47.

The checklist promise, by contrast, was kept by 35 of 35 — so these tests pin
BOTH directions. A gate that flagged the boilerplate wholesale would have been
wrong about the one clause that was true, and the repair would have rewritten
65 excerpts that had nothing wrong with them.

What is asserted
----------------
* the gate fires on an unmet promise and stays quiet on a met one
* hand-written excerpts are out of scope (allow-by-default)
* the generator only ever picks a closer the body backs up
* the repair swaps ONLY the closing sentence — the opener carries the story
  names, and regenerating it would silently rewrite them
* the corpus is clean, so a new post cannot reintroduce the defect
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_excerpt_promises import main, violation  # noqa: E402
from seo_diversify_excerpts import (  # noqa: E402
    CLOSER_TEXTS,
    CLOSERS,
    NEUTRAL_CLOSER,
    _process_file,
    choose_closer_text,
    current_closer_index,
    eligible_closers,
)

# Indices used by name so a reordering of CLOSERS fails loudly here rather than
# silently changing what these tests mean.
CHECKLIST = 0
IOC_TABLE = 6

RICH_BODY = """
## 주요 이슈

| 분야 | 소스 | 핵심내용 | 영향도 |
|---|---|---|---|
| 취약점 | BleepingComputer | 커널 제로데이 | 높음 |
| IoC | ASEC | 해시 a1b2c3 | 중간 |

- [원문 1](https://example.com/a)
- [원문 2](https://example.com/b)
- [원문 3](https://example.com/c)

SBOM 으로 의존성을 식별하고 EDR 및 SOC 에서 차단합니다. 공격 경로와 영향을
평가한 뒤 탐지 룰과 패치를 적용합니다.

## 실무 체크리스트

- [ ] 영향 자산 식별
- [ ] 패치 적용
- [ ] 탐지 룰 배포
"""

# Same shape, but with none of the specific evidence: no SBOM/EDR/SOC/IoC and
# no 공격 경로. Only the checklist and link promises can hold here.
PLAIN_BODY = """
## 주요 이슈

| 분야 | 소스 | 핵심내용 |
|---|---|---|
| 동향 | 뉴스 | 요약 |

- [원문 1](https://example.com/a)
- [원문 2](https://example.com/b)
- [원문 3](https://example.com/c)

## 실무 체크리스트

- [ ] 확인
- [ ] 조치
- [ ] 공유
"""


# RICH_BODY with the IoC table row taken out: the IoC closer stops qualifying
# while the longer ones (탐지·패치, SBOM/EDR, SOC) still do. That combination is
# what makes the non-growth constraint observable.
NO_IOC_BODY = "\n".join(
    ln for ln in RICH_BODY.split("\n") if not ln.startswith("| IoC ")
).replace("IoC", "지표")


def _post(tmp_path: Path, excerpt: str, body: str, name: str = "p.md") -> Path:
    p = tmp_path / name
    p.write_text(
        f'---\nlayout: post\ntitle: "T"\nexcerpt: "{excerpt}"\n---\n{body}',
        encoding="utf-8",
    )
    return p


BASE = "어떤 이슈를 운영 관점에서 점검합니다."


class TestViolationDetection:
    def test_unmet_promise_is_reported(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[IOC_TABLE], PLAIN_BODY)
        why = violation(p)
        assert why is not None, "an IoC-table promise over a body with no IoCs passed"
        assert "IoC" in why

    def test_met_promise_is_silent(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[IOC_TABLE], RICH_BODY)
        assert violation(p) is None

    def test_checklist_promise_is_kept_not_flagged(self, tmp_path: Path) -> None:
        """The clause that was always true must not be swept up with the rest.

        35 of 35 posts kept this promise. A gate that treated the whole
        boilerplate as suspect would be wrong here, and the repair would churn
        65 correct excerpts.
        """
        p = _post(tmp_path, BASE + CLOSER_TEXTS[CHECKLIST], PLAIN_BODY)
        assert violation(p) is None

    def test_hand_written_excerpt_is_out_of_scope(self, tmp_path: Path) -> None:
        p = _post(
            tmp_path, "사람이 직접 쓴 요약입니다. IoC 정리표도 있습니다.", PLAIN_BODY
        )
        assert violation(p) is None, (
            "the gate judged prose it did not generate. It is deliberately "
            "allow-by-default — inferring promises from arbitrary text is the "
            "heuristic-next-door trap."
        )

    def test_post_without_excerpt_is_skipped(self, tmp_path: Path) -> None:
        p = tmp_path / "n.md"
        p.write_text('---\nlayout: post\ntitle: "T"\n---\nbody\n', encoding="utf-8")
        assert violation(p) is None


class TestExitCodes:
    def test_clean_file_exits_zero(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[CHECKLIST], PLAIN_BODY)
        assert main([str(p)]) == 0

    def test_violation_exits_one(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[IOC_TABLE], PLAIN_BODY)
        assert main([str(p)]) == 1

    def test_missing_named_file_exits_one(self, tmp_path: Path) -> None:
        """A typo'd path must not read as "nothing to check, all good"."""
        assert main([str(tmp_path / "nope.md")]) == 1


class TestGeneratorPicksHonestly:
    @pytest.mark.parametrize("body", [RICH_BODY, PLAIN_BODY])
    def test_chosen_closer_is_always_backed_by_the_body(
        self, tmp_path: Path, body: str
    ) -> None:
        # Several filenames, because the choice is seeded from the name.
        for n in range(12):
            path = tmp_path / f"2026-05-{n + 1:02d}-Tech_Security_Weekly_Digest_X.md"
            text = choose_closer_text(path, body)
            if text == NEUTRAL_CLOSER:
                pytest.fail("neutral closer used for a digest-shaped body")
            idx = CLOSER_TEXTS.index(text)
            assert CLOSERS[idx].requires(body), (
                f"{path.name}: picked a closer the body cannot back up"
            )

    def test_plain_body_cannot_reach_the_specific_promises(self) -> None:
        ok = set(eligible_closers(PLAIN_BODY))
        assert IOC_TABLE not in ok
        assert CHECKLIST in ok, (
            "closer 0 is the guaranteed fallback (measured 217/217); if it stops "
            "qualifying for a plain digest the rotation has nowhere safe to land"
        )

    def test_neutral_closer_for_a_body_with_no_evidence(self, tmp_path: Path) -> None:
        """A non-digest body gets a sentence that claims nothing, not a crash.

        The generator runs inside the cron publish. Raising here would turn one
        odd post into a failed publish; promising something would be the bug
        this whole change removes.

        The properties are asserted directly rather than as
        ``chosen == NEUTRAL_CLOSER``. That comparison is self-referential:
        pointing ``NEUTRAL_CLOSER`` at one of the real closers still satisfied
        it, so the test said nothing about the thing that matters — that the
        fallback makes no claim.
        """
        assert eligible_closers("") == []
        chosen = choose_closer_text(tmp_path / "x.md", "")
        assert chosen not in CLOSER_TEXTS, (
            f"the empty-evidence fallback is a real closer ({chosen!r}), so a "
            "body with nothing to back it up gets a promise anyway"
        )
        assert current_closer_index("어떤 요약입니다." + chosen) is None, (
            "the fallback is a gate-checkable promise; it must claim nothing"
        )
        assert violation(_post(tmp_path, "요약." + chosen, "", name="q.md")) is None


class TestRepairIsSurgical:
    def test_only_the_closing_sentence_changes(self, tmp_path: Path) -> None:
        opener = "인터폴 작전 · Storm-2949 를 중심으로 영향 범위와 패치 우선순위를 분석합니다."
        p = _post(tmp_path, opener + CLOSER_TEXTS[IOC_TABLE], PLAIN_BODY)
        changed, reason = _process_file(p, apply=True, repair_promises=True)
        assert changed and reason == "repaired"

        new = next(
            ln
            for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.startswith("excerpt:")
        )[len('excerpt: "') : -1]
        assert new.startswith(opener), (
            "the opener changed. It carries the story names, which are rebuilt "
            "from summary_card.highlights — a repair pass must not touch them."
        )
        idx = current_closer_index(new)
        assert idx is not None and CLOSERS[idx].requires(PLAIN_BODY)

    def test_replacement_never_grows_the_front_matter(self, tmp_path: Path) -> None:
        """`check_front_matter_growth.py --changed` ratchets every existing post.

        Swapping in a longer closing sentence grew front matter by 2-8 chars in
        41 of the 150 repairs, which failed the build. Exempting `excerpt` from
        that ratchet would blind it to real excerpt bloat, so the repair carries
        the constraint instead. Local `--all` does NOT catch this — that mode is
        a cap check with no baseline, which is why the first run looked clean.
        """
        # NO_IOC_BODY, not PLAIN_BODY: every closer PLAIN_BODY qualifies for is
        # already shorter than the IoC one, so the filter is a no-op there and
        # deleting it left this test green. The body below keeps the longer
        # closers eligible, which is the only shape that can detect the loss.
        longer = [
            i
            for i in eligible_closers(NO_IOC_BODY)
            if len(CLOSER_TEXTS[i]) > len(CLOSER_TEXTS[IOC_TABLE])
        ]
        assert longer, (
            "fixture no longer offers an eligible closer longer than the one "
            "being replaced, so this test cannot detect a lost constraint"
        )

        # Seeded across many filenames because the pick rotates on the name.
        for n in range(20):
            name = f"2026-05-{n % 28 + 1:02d}-Tech_Security_Weekly_Digest_{n}.md"
            p = _post(tmp_path, BASE + CLOSER_TEXTS[IOC_TABLE], NO_IOC_BODY, name=name)
            before = len(p.read_text(encoding="utf-8").split("---")[1])
            changed, reason = _process_file(p, apply=True, repair_promises=True)
            assert changed, f"{name}: expected a repair, got {reason!r}"
            after = len(p.read_text(encoding="utf-8").split("---")[1])
            assert after <= before, (
                f"{name}: front matter grew {before} -> {after}; the repair "
                "picked a longer closer than the one it replaced"
            )

    def test_length_constraint_yields_to_honesty(self, tmp_path: Path) -> None:
        """Fitting is a preference, not a veto — a true excerpt beats a short one.

        If no eligible closer is short enough, the unfiltered eligible set is
        used and the front matter grows. That is the correct trade: the ratchet
        exists to stop bloat, not to hold an excerpt at a claim the post cannot
        support.
        """
        shortest = min(len(t) for t in CLOSER_TEXTS)
        chosen = choose_closer_text(
            tmp_path / "2026-05-01-x.md", PLAIN_BODY, current=None, max_len=1
        )
        assert chosen in CLOSER_TEXTS and len(chosen) >= shortest
        idx = CLOSER_TEXTS.index(chosen)
        assert CLOSERS[idx].requires(PLAIN_BODY), (
            "an impossible length budget produced a closer the body cannot back "
            "up — the filter must yield to eligibility, never override it"
        )

    def test_kept_promise_is_left_untouched(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[CHECKLIST], PLAIN_BODY)
        before = p.read_text(encoding="utf-8")
        changed, reason = _process_file(p, apply=True, repair_promises=True)
        assert changed is False and reason == "promise-kept"
        assert p.read_text(encoding="utf-8") == before

    def test_repair_is_idempotent(self, tmp_path: Path) -> None:
        p = _post(tmp_path, BASE + CLOSER_TEXTS[IOC_TABLE], PLAIN_BODY)
        _process_file(p, apply=True, repair_promises=True)
        after_first = p.read_text(encoding="utf-8")
        changed, reason = _process_file(p, apply=True, repair_promises=True)
        assert changed is False and reason == "promise-kept"
        assert p.read_text(encoding="utf-8") == after_first

    def test_repair_does_not_regenerate_v1_excerpts(self, tmp_path: Path) -> None:
        """``--repair-promises`` swaps closers; it is not a v1 sweep.

        Two posts in the corpus carry a v1/hand-written excerpt with no
        recognised closer. Letting the repair fall through to the full rewrite
        path would rebuild their openers from highlights as a side effect of a
        run asked to do something else.
        """
        p = _post(
            tmp_path,
            "옛 형식 요약. DevSecOps 실무 대응 방안을 함께 다룹니다.",
            PLAIN_BODY,
        )
        before = p.read_text(encoding="utf-8")
        changed, reason = _process_file(p, apply=True, repair_promises=True)
        assert changed is False and reason == "not-generated"
        assert p.read_text(encoding="utf-8") == before


def test_corpus_is_clean() -> None:
    """The 150 repairs landed; a new post cannot reintroduce the defect."""
    proc = subprocess.run(
        [sys.executable, "scripts/check_excerpt_promises.py", "--all"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert "no posts to check" not in proc.stdout, "vacuous pass — no posts scanned"
    assert proc.returncode == 0, proc.stdout + proc.stderr

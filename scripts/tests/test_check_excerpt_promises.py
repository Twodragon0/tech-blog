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


def _closer_index(fragment: str) -> int:
    """Locate a closer by a fragment of its sentence, not by position.

    These tests were written against hardcoded indices, and then two closers
    were deleted — which silently repointed `IOC_TABLE = 6` at a different
    sentence instead of failing. Looking the sentence up makes a rename or a
    deletion an error here rather than a test that quietly checks the wrong
    thing.
    """
    hits = [i for i, t in enumerate(CLOSER_TEXTS) if fragment in t]
    assert len(hits) == 1, f"{fragment!r} matched {len(hits)} closers, expected 1"
    return hits[0]


CHECKLIST = _closer_index("팀에서 바로 나눠 가질 점검 항목")
IOC_TABLE = _closer_index("IoC 정리표")

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


class TestStagedScope:
    """`--staged` reads the index; the working tree can disagree with it.

    `git add x.md && rm x.md` leaves the file staged as an addition, so
    `--diff-filter=ACMR` lists it while there is nothing on disk. The gate used
    to exit 1 with `not found` and block the commit over a file the commit does
    not contain. Reproduced on main before the fix.

    A missing path must still be an error everywhere else — that asymmetry is
    the point, so both directions are asserted here.
    """

    def _repo(self, tmp_path: Path) -> Path:
        import subprocess as sp

        sp.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        sp.run(
            ["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True
        )
        sp.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
        (tmp_path / "_posts").mkdir()
        (tmp_path / "seed").write_text("x", encoding="utf-8")
        sp.run(["git", "add", "seed"], cwd=tmp_path, check=True)
        sp.run(["git", "commit", "-qm", "seed"], cwd=tmp_path, check=True)
        return tmp_path

    def test_staged_then_deleted_post_is_skipped(self, tmp_path: Path, monkeypatch):
        import subprocess as sp

        repo = self._repo(tmp_path)
        post = repo / "_posts" / "2026-09-12-x.md"
        post.write_text(
            f'---\nlayout: post\ntitle: "T"\nexcerpt: "{BASE}"\n---\n{PLAIN_BODY}',
            encoding="utf-8",
        )
        sp.run(["git", "add", str(post)], cwd=repo, check=True)
        post.unlink()

        import check_excerpt_promises as mod

        monkeypatch.setattr(mod, "ROOT", repo, raising=True)
        assert mod._staged_posts() == [], (
            "a staged-then-deleted post is still in the list; the gate will "
            "report it as `not found` and fail a commit that does not contain it"
        )
        assert mod.main(["--staged"]) == 0

    def test_staged_and_present_post_is_still_checked(
        self, tmp_path: Path, monkeypatch
    ):
        """The control: filtering must not empty the staged list wholesale."""
        import subprocess as sp

        repo = self._repo(tmp_path)
        post = repo / "_posts" / "2026-09-12-y.md"
        post.write_text(
            f'---\nlayout: post\ntitle: "T"\n'
            f'excerpt: "{BASE + CLOSER_TEXTS[IOC_TABLE]}"\n---\n{PLAIN_BODY}',
            encoding="utf-8",
        )
        sp.run(["git", "add", str(post)], cwd=repo, check=True)

        import check_excerpt_promises as mod

        monkeypatch.setattr(mod, "ROOT", repo, raising=True)
        assert mod._staged_posts() == [post]
        assert mod.main(["--staged"]) == 1, (
            "the staged post carries an unmet promise and must still be caught"
        )


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

    def test_missing_file_is_reported_as_missing_not_as_a_broken_promise(
        self, tmp_path: Path, capsys
    ) -> None:
        """Exit 1 is not enough — the reason has to be right.

        Without the explicit missing-path check the run still exits 1, because
        `violation()` turns the read error into an `unreadable:` finding. But
        the summary then tells the reader to run
        `seo_diversify_excerpts --apply --repair-promises`, which cannot fix a
        path that does not exist. Same exit code, wrong advice — only the
        message distinguishes the two, so the message is what this asserts.
        """
        main([str(tmp_path / "nope.md")])
        out = capsys.readouterr()
        combined = out.out + out.err
        assert "not found" in combined
        assert "--repair-promises" not in combined, (
            "a missing path was reported as an unmet promise, sending the "
            "reader to a repair command that cannot help"
        )


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


# Two SEPARATE tables, one naming a source column and the other an impact
# column. The sentence claims one table carries both, so this must NOT qualify.
# Without this fixture, reverting the predicate to a flat `any(...) and any(...)`
# over all rows left every test green — no post in the corpus splits them today,
# which is exactly why the hole needs a synthetic case.
TWO_TABLE_BODY = """
## 출처

| 분야 | 소스 |
|---|---|
| 취약점 | BleepingComputer |

## 등급

| 항목 | 영향도 |
|---|---|
| 커널 | 높음 |

- [원문 1](https://example.com/a)
- [원문 2](https://example.com/b)
- [원문 3](https://example.com/c)

## 실무 체크리스트

- [ ] 확인
- [ ] 조치
- [ ] 공유
"""

# A source-directory row that merely mentions IoC — a place that publishes them,
# not the 정리표 the sentence promises. Taken from a real corpus row.
IOC_MENTION_BODY = PLAIN_BODY.replace(
    "| 동향 | 뉴스 | 요약 |",
    "| KISA 사이버 위협 동향 | [krcert.or.kr](https://www.krcert.or.kr/) | "
    "국내 보안 권고 및 IOC |",
)


class TestPredicatesMatchTheirSentences:
    """Each predicate must be as strong as the claim it guards — no stronger.

    Every case here was written after a mutation survived: the corpus happens
    not to contain the shape that distinguishes the strong predicate from the
    weak one, so only a synthetic body can hold the distinction in place.
    """

    def test_source_and_impact_must_share_one_table(self) -> None:
        idx = _closer_index("소스와 영향도를 표로 정리해")
        assert idx not in eligible_closers(TWO_TABLE_BODY), (
            "two different tables satisfied a sentence that claims one table "
            "carries both columns"
        )
        assert idx in eligible_closers(PLAIN_BODY) or idx in eligible_closers(
            RICH_BODY
        ), "the predicate now rejects a body that genuinely has both in one table"

    def test_ioc_needs_a_column_not_a_mention(self) -> None:
        assert IOC_TABLE not in eligible_closers(IOC_MENTION_BODY), (
            "a row that merely mentions IOC satisfied a promise of an IoC 정리표"
        )
        assert IOC_TABLE in eligible_closers(RICH_BODY), (
            "the predicate now rejects a body with a real IoC column"
        )

    def test_fenced_tables_are_not_evidence(self) -> None:
        """A pipe table inside ``` is a code sample, not the post's own table.

        14 digests contain them.
        """
        fenced = PLAIN_BODY + "\n```\n| 소스 | 영향도 |\n|---|---|\n| a | b |\n```\n"
        idx = _closer_index("소스와 영향도를 표로 정리해")
        assert idx not in eligible_closers(fenced)

    def test_retirement_does_not_rely_on_the_predicate(self, monkeypatch) -> None:
        """`retired` must gate selection on its own.

        `_never` already makes a retired closer ineligible, so removing the
        `not c.retired` filter changed no test — belt and braces where only the
        braces were tested. If someone retires a closer whose predicate is still
        satisfiable, selection must still refuse it.
        """
        live = CLOSERS[0]
        trap = type(live)(
            text=" 은퇴했지만 술어는 참인 문장입니다.",
            requires=lambda _b: True,
            why="never",
            retired=True,
        )
        monkeypatch.setattr(
            "seo_diversify_excerpts.CLOSERS", (live, trap), raising=True
        )
        import seo_diversify_excerpts as mod

        assert 1 not in mod.eligible_closers(RICH_BODY), (
            "a retired closer with a satisfiable predicate became eligible"
        )


class TestRetiredClosers:
    """A withdrawn sentence must stay RECOGNISED, or its carriers go dark.

    Deleting the two bad closers outright looked tidier and silently removed 84
    published posts from coverage: `current_closer_index` returned None for
    them, the repair classified them as hand-written and skipped them, and the
    gate — allow-by-default on unknown endings — stopped reporting them. They
    kept advertising a SOC discussion and an attack-path walkthrough that are
    not in the text, which is the exact defect this whole change removes.
    Measured: "Hand-written" jumped 2 -> 86 before the retirement mechanism
    replaced the deletion.
    """

    def test_retired_closers_exist(self) -> None:
        retired = [i for i, c in enumerate(CLOSERS) if c.retired]
        assert retired, (
            "no retired closers. If a sentence is being withdrawn, mark it "
            "retired=True rather than deleting the entry — see this class's "
            "docstring for what deletion cost."
        )

    def test_retired_closer_is_never_selected(self, tmp_path: Path) -> None:
        for body in (RICH_BODY, PLAIN_BODY, NO_IOC_BODY, ""):
            for i in eligible_closers(body):
                assert not CLOSERS[i].retired, (
                    f"retired closer {i} is eligible again for {body[:20]!r}"
                )
        # And it cannot be reached through the generator either.
        for n in range(12):
            path = tmp_path / f"2026-05-{n + 1:02d}-Tech_Security_Weekly_Digest_X.md"
            text = choose_closer_text(path, RICH_BODY)
            assert text != NEUTRAL_CLOSER
            assert not CLOSERS[CLOSER_TEXTS.index(text)].retired

    def test_retired_closer_is_still_a_violation(self, tmp_path: Path) -> None:
        """The whole point: a carrier must be flagged, not skipped as prose."""
        retired = next(i for i, c in enumerate(CLOSERS) if c.retired)
        p = _post(tmp_path, BASE + CLOSER_TEXTS[retired], RICH_BODY)
        assert current_closer_index(BASE + CLOSER_TEXTS[retired]) == retired, (
            "a retired closer is no longer recognised, so its carriers read as "
            "hand-written and leave the gate's scope entirely"
        )
        assert violation(p) is not None, (
            "a retired closer passed the gate even against the richest body — "
            "retired predicates must never be satisfiable"
        )

    def test_retired_carrier_is_repaired_onto_a_live_closer(
        self, tmp_path: Path
    ) -> None:
        retired = next(i for i, c in enumerate(CLOSERS) if c.retired)
        p = _post(tmp_path, BASE + CLOSER_TEXTS[retired], RICH_BODY)
        changed, reason = _process_file(p, apply=True, repair_promises=True)
        assert changed and reason == "repaired", (reason,)
        assert violation(p) is None
        new = next(
            ln
            for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.startswith("excerpt:")
        )
        idx = current_closer_index(new[len('excerpt: "') : -1])
        assert idx is not None and not CLOSERS[idx].retired


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

    def test_opener_with_a_backslash_survives(self, tmp_path: Path) -> None:
        """`_yaml_safe` must touch only the new closer, not the whole excerpt.

        Applied to the whole string its `.replace("\\\\", "")` rewrote the
        opener too — `오늘 C:\\temp\\x 경로` came back as `오늘 C:tempx 경로`.
        That silently edits the part the "surgical" contract promises to leave
        alone, and no fixture had a backslash so the regression was invisible.
        """
        opener = "오늘 C:\\temp\\x 경로 이슈를 정리합니다."
        p = _post(tmp_path, opener + CLOSER_TEXTS[IOC_TABLE], PLAIN_BODY)
        _process_file(p, apply=True, repair_promises=True)
        new = next(
            ln
            for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.startswith("excerpt:")
        )[len('excerpt: "') : -1]
        assert new.startswith(opener), (
            f"the opener was rewritten: {new[: len(opener) + 10]!r}"
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

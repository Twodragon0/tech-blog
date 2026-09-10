"""Tests for ``scripts/seo_inject_related_links.py``.

Guards the GSC orphan-graph fix that appends "🔗 관련 포스트" sections to
Weekly-Digest posts. Three concerns:

1. Neighbor selection — preferred ±1, ±3, ±7 day offsets, skips self.
2. File injection — section appears in the right place (before the
   ``---`` + ``**작성자**`` footer) and contains the idempotence marker.
3. Idempotence — re-runs do not duplicate sections.
"""

from __future__ import annotations

import sys
from datetime import date as Date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from seo_inject_related_links import (  # noqa: E402
    MARKER,
    _build_section,
    _gather_digests,
    _inject,
    _pick_neighbors,
    _process_file,
)


def _fixture_post(
    tmp_path: Path,
    date_str: str,
    slug: str = "Tech_Security_Weekly_Digest_X",
    body_tail: str = "\n## 참고 자료\n\n| a | b |\n\n---\n\n**작성자**: Twodragon\n",
) -> Path:
    """Write a minimal post fixture under ``tmp_path``."""
    filename = f"{date_str}-{slug}.md"
    content = f"""---
layout: post
title: "Digest for {date_str}"
date: {date_str} 09:00:00 +0900
---

# Body for {date_str}
{body_tail}"""
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


class TestNeighborPicking:
    """``_pick_neighbors`` must walk the preferred-offset ladder first."""

    def test_prefers_plus_minus_1(self, tmp_path: Path) -> None:
        _fixture_post(tmp_path, "2026-05-17")
        _fixture_post(tmp_path, "2026-05-18")  # target
        _fixture_post(tmp_path, "2026-05-19")
        _fixture_post(tmp_path, "2026-05-10")
        catalog = _gather_digests(tmp_path)
        neighbors = _pick_neighbors(Date(2026, 5, 18), catalog, n=3)
        dates = {d for d, _, _ in neighbors}
        assert Date(2026, 5, 17) in dates
        assert Date(2026, 5, 19) in dates

    def test_excludes_self(self, tmp_path: Path) -> None:
        _fixture_post(tmp_path, "2026-05-17")
        _fixture_post(tmp_path, "2026-05-18")  # target
        _fixture_post(tmp_path, "2026-05-19")
        catalog = _gather_digests(tmp_path)
        neighbors = _pick_neighbors(Date(2026, 5, 18), catalog, n=3)
        dates = [d for d, _, _ in neighbors]
        assert Date(2026, 5, 18) not in dates

    def test_falls_back_when_preferred_offsets_missing(self, tmp_path: Path) -> None:
        """If ±1/±3/±7 are all missing, the catalog walk picks the
        nearest available dates by absolute distance."""
        _fixture_post(tmp_path, "2026-05-18")  # target
        _fixture_post(tmp_path, "2026-04-15")
        _fixture_post(tmp_path, "2026-06-20")
        _fixture_post(tmp_path, "2026-03-01")
        catalog = _gather_digests(tmp_path)
        neighbors = _pick_neighbors(Date(2026, 5, 18), catalog, n=3)
        assert len(neighbors) == 3

    def test_caps_at_n(self, tmp_path: Path) -> None:
        for d in ("2026-05-15", "2026-05-16", "2026-05-17", "2026-05-19", "2026-05-20"):
            _fixture_post(tmp_path, d)
        _fixture_post(tmp_path, "2026-05-18")
        catalog = _gather_digests(tmp_path)
        neighbors = _pick_neighbors(Date(2026, 5, 18), catalog, n=3)
        assert len(neighbors) == 3


class TestBuildSection:
    def test_includes_marker(self) -> None:
        section = _build_section([(Date(2026, 5, 17), "slug-a", "Title A")])
        assert MARKER in section
        assert "Title A" in section
        assert "/posts/2026/05/17/slug-a/" in section

    def test_empty_neighbors_returns_empty(self) -> None:
        assert _build_section([]) == ""


class TestInjection:
    def test_inserts_before_author_footer(self) -> None:
        body = "\n# Body\n\nContent here.\n\n---\n\n**작성자**: Twodragon\n"
        section = "\n---\n\n## 🔗 관련 포스트\n\n" + MARKER + "\n\n- link"
        out = _inject(body, section)
        # marker comes before the author line
        assert out.index(MARKER) < out.index("**작성자**")
        # original author line preserved
        assert "**작성자**: Twodragon" in out

    def test_appends_when_no_author_footer(self) -> None:
        body = "\n# Body\n\nNo author footer.\n"
        section = "\n## 🔗 관련 포스트\n\n" + MARKER + "\n\n- link"
        out = _inject(body, section)
        assert out.endswith("- link\n") or "- link" in out
        assert MARKER in out


class TestProcessFile:
    def test_injects_and_is_idempotent(self, tmp_path: Path) -> None:
        for d in ("2026-05-15", "2026-05-16", "2026-05-17", "2026-05-19"):
            _fixture_post(tmp_path, d)
        target = _fixture_post(tmp_path, "2026-05-18")
        catalog = _gather_digests(tmp_path)

        changed, reason = _process_file(target, catalog, apply=True)
        assert changed is True
        assert reason == "rewritten"
        text = target.read_text(encoding="utf-8")
        assert text.count(MARKER) == 1
        assert "## 🔗 관련 포스트" in text

        # Second run: no-op.
        #
        # The reason moved from "already-v1" to "no-change" on 2026-09-10 and the
        # distinction matters. "already-v1" meant "the marker is present, so I
        # refuse to look" — which froze every block against the catalog it was
        # first built from, so a block linking a since-superseded post could
        # never be corrected. Now the section is recomputed and compared, and
        # equality is what makes the run a no-op. Idempotence is still asserted
        # (changed2 is False, one marker, byte-identical file below); it is now
        # earned rather than assumed.
        changed2, reason2 = _process_file(target, catalog, apply=True)
        assert changed2 is False
        assert reason2 == "no-change"
        assert target.read_text(encoding="utf-8") == text
        assert text.count(MARKER) == 1

    def test_skipped_when_too_few_neighbors(self, tmp_path: Path) -> None:
        _fixture_post(tmp_path, "2026-05-18")
        _fixture_post(tmp_path, "2026-05-19")
        # Move the only neighbor out so the target has 0 viable peers
        catalog = {Date(2026, 5, 18): _gather_digests(tmp_path)[Date(2026, 5, 18)]}
        target = tmp_path / "2026-05-18-Tech_Security_Weekly_Digest_X.md"
        changed, reason = _process_file(target, catalog, apply=True)
        assert changed is False
        assert reason == "no-neighbors"

    @pytest.mark.parametrize(
        "tail",
        [
            "\n## 참고 자료\n\n| a | b |\n\n---\n\n**작성자**: Twodragon\n",
            "\n## 참고 자료\n\nReferences only — no author footer.\n",
            "\n# Body only\nNo references and no footer.\n",
        ],
    )
    def test_handles_varied_footers(self, tmp_path: Path, tail: str) -> None:
        for d in ("2026-05-15", "2026-05-17", "2026-05-19"):
            _fixture_post(tmp_path, d)
        target = _fixture_post(tmp_path, "2026-05-18", body_tail=tail)
        catalog = _gather_digests(tmp_path)
        changed, _ = _process_file(target, catalog, apply=True)
        assert changed is True
        text = target.read_text(encoding="utf-8")
        assert MARKER in text
        assert "## 🔗 관련 포스트" in text


# --- superseded posts must never become link targets ------------------------
#
# The 30 April 2026 dailies were consolidated into 4 weekly rollups: vercel.json
# 301s their URLs, and `superseded_by` in their front matter records where to.
# A "관련 포스트" entry pointing at one of them shows the reader the daily's
# title and lands them on a different article — measured 2026-09-10 on 5 live
# posts (2026-03-29/31, 05-01/02/03) carrying 7 such entries.
#
# This script is also the fix for the dead internal-link pipeline (it has had
# zero call sites since the one-off 2026-05-19 run), so it is about to run on
# every publish. It must not regenerate the bad links it is here to remove.


def _superseded_post(
    tmp_path: Path,
    date_str: str,
    dest: str,
    slug: str = "Tech_Security_Weekly_Digest_Old",
) -> Path:
    p = tmp_path / f"{date_str}-{slug}.md"
    p.write_text(
        f'---\nlayout: post\ntitle: "Superseded digest {date_str}"\n'
        f"date: {date_str} 09:00:00 +0900\nsuperseded_by: {dest}\n---\n\n"
        "# Body\n\n---\n\n**작성자**: Twodragon\n",
        encoding="utf-8",
    )
    return p


class TestSupersededExclusion:
    def test_superseded_post_is_not_in_the_catalog(self, tmp_path: Path) -> None:
        _fixture_post(tmp_path, "2026-04-10")
        _superseded_post(
            tmp_path,
            "2026-04-11",
            "/posts/2026/04/12/Week2_April_2026_Security_Digest/",
        )
        cat = _gather_digests(tmp_path)
        dates = {d.isoformat() for d in cat}
        assert "2026-04-10" in dates, (
            "control: a normal digest must still be catalogued"
        )
        assert "2026-04-11" not in dates, (
            "a post whose URL 301s elsewhere is still offered as a link target; "
            "readers would be sent to a different article than the link text names."
        )

    def test_neighbors_skip_superseded_and_reach_further(self, tmp_path: Path) -> None:
        """The ladder must step over a superseded neighbour, not link it."""
        _fixture_post(tmp_path, "2026-04-08")
        _superseded_post(
            tmp_path,
            "2026-04-09",
            "/posts/2026/04/12/Week2_April_2026_Security_Digest/",
        )
        target = _fixture_post(tmp_path, "2026-04-10")
        _fixture_post(tmp_path, "2026-04-13")
        cat = _gather_digests(tmp_path)
        picked = _pick_neighbors(Date(2026, 4, 10), cat, n=3)
        got = {d.isoformat() for d, _s, _t in picked}
        assert "2026-04-09" not in got
        assert got == {"2026-04-08", "2026-04-13"}, got
        assert target.is_file()

    def test_superseded_post_itself_is_not_processed(self, tmp_path: Path) -> None:
        """No point injecting a related-posts block into a page nobody reaches."""
        _fixture_post(tmp_path, "2026-04-08")
        _fixture_post(tmp_path, "2026-04-09")
        sup = _superseded_post(
            tmp_path,
            "2026-04-10",
            "/posts/2026/04/12/Week2_April_2026_Security_Digest/",
        )
        cat = _gather_digests(tmp_path)
        changed, reason = _process_file(sup, cat, apply=True)
        assert not changed and reason == "superseded", reason
        assert MARKER not in sup.read_text(encoding="utf-8")


class TestRefreshExistingBlock:
    """An existing v1 block must be refreshed, not skipped forever.

    ``_process_file`` used to return ``already-v1`` on sight of the marker, so a
    block generated against a stale catalog could never be corrected — the 7 bad
    entries above would have survived every future run.
    """

    def test_stale_block_is_rewritten(self, tmp_path: Path) -> None:
        _fixture_post(tmp_path, "2026-04-08")
        _superseded_post(
            tmp_path,
            "2026-04-09",
            "/posts/2026/04/12/Week2_April_2026_Security_Digest/",
        )
        _fixture_post(tmp_path, "2026-04-13")
        target = _fixture_post(tmp_path, "2026-04-10")
        # Seed a block that links the now-superseded neighbour.
        text = target.read_text(encoding="utf-8")
        stale = (
            f"\n---\n\n## 🔗 관련 포스트\n\n{MARKER}\n\n"
            "- [Old daily](/posts/2026/04/09/Tech_Security_Weekly_Digest_Old/) — 2026-04-09\n"
            "- [Other](/posts/2026/04/08/Tech_Security_Weekly_Digest_X/) — 2026-04-08\n"
        )
        target.write_text(
            text.replace("\n---\n\n**작성자**", stale + "\n---\n\n**작성자**"),
            encoding="utf-8",
        )

        cat = _gather_digests(tmp_path)
        changed, reason = _process_file(target, cat, apply=True)
        after = target.read_text(encoding="utf-8")
        assert changed, f"stale block was not refreshed ({reason})"
        assert "/posts/2026/04/09/" not in after, (
            "the superseded link survived the refresh"
        )
        assert after.count(MARKER) == 1, "refresh duplicated the section"

    def test_current_block_is_left_untouched(self, tmp_path: Path) -> None:
        """Control: idempotence. A correct block must not be rewritten."""
        _fixture_post(tmp_path, "2026-04-08")
        _fixture_post(tmp_path, "2026-04-13")
        target = _fixture_post(tmp_path, "2026-04-10")
        cat = _gather_digests(tmp_path)
        assert _process_file(target, cat, apply=True)[0] is True
        first = target.read_text(encoding="utf-8")
        changed, reason = _process_file(target, cat, apply=True)
        assert not changed and reason == "no-change", reason
        assert target.read_text(encoding="utf-8") == first
        assert first.count(MARKER) == 1


class TestAnchorTextIsCanonical:
    """Anchor text becomes body prose, so the proper-noun policy applies to it.

    The 2026-09-10 backfill copied target titles verbatim and turned
    ``check_digest_proper_nouns`` red on 4 posts (``쿠버네티스 -> Kubernetes``).
    Front matter is outside that gate's scope, so the titles sit there
    unflagged; a body copy is in scope. Fixing it with ``--fix`` alone would
    loop — the next injector run regenerates the Hangul form — so the injector
    reuses the gate's own josa-aware substitution.
    """

    def test_hangul_transliteration_is_canonicalized(self, tmp_path: Path) -> None:
        p = tmp_path / "2026-04-10-Tech_Security_Weekly_Digest_K.md"
        p.write_text(
            '---\nlayout: post\ntitle: "주간 다이제스트: 쿠버네티스·제로데이"\n'
            "date: 2026-04-10 09:00:00 +0900\n---\n\n# Body\n",
            encoding="utf-8",
        )
        cat = _gather_digests(tmp_path)
        title = cat[Date(2026, 4, 10)][2]
        assert "쿠버네티스" not in title, (
            "the anchor text still carries a Hangul transliteration; "
            "check_digest_proper_nouns will fail on any post linking here."
        )
        assert "Kubernetes" in title, title

    def test_non_entity_korean_is_left_alone(self, tmp_path: Path) -> None:
        """Control: only allow-listed proper nouns are substituted."""
        p = tmp_path / "2026-04-11-Tech_Security_Weekly_Digest_P.md"
        p.write_text(
            '---\nlayout: post\ntitle: "주간 보안 다이제스트: 제로데이·악성코드"\n'
            "date: 2026-04-11 09:00:00 +0900\n---\n\n# Body\n",
            encoding="utf-8",
        )
        cat = _gather_digests(tmp_path)
        title = cat[Date(2026, 4, 11)][2]
        assert title == "주간 보안 다이제스트: 제로데이·악성코드", title

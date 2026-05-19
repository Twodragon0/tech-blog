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

    def test_falls_back_when_preferred_offsets_missing(
        self, tmp_path: Path
    ) -> None:
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
        section = _build_section(
            [(Date(2026, 5, 17), "slug-a", "Title A")]
        )
        assert MARKER in section
        assert "Title A" in section
        assert "/posts/2026/05/17/slug-a/" in section

    def test_empty_neighbors_returns_empty(self) -> None:
        assert _build_section([]) == ""


class TestInjection:
    def test_inserts_before_author_footer(self) -> None:
        body = (
            "\n# Body\n\nContent here.\n\n---\n\n**작성자**: Twodragon\n"
        )
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

        # Second run: no-op
        changed2, reason2 = _process_file(target, catalog, apply=True)
        assert changed2 is False
        assert reason2 == "already-v1"

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

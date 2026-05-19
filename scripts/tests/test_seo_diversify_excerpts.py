"""Tests for ``scripts/seo_diversify_excerpts.py``.

These tests guard the GSC-recovery patch that rewrites Weekly-Digest excerpts
into one of 25 deterministic variants. Two layers of coverage:

1. Pure ``_build_diverse_excerpt`` — determinism, length window, v2 marker
   present, particle correctness on highlight anchors with trailing punctuation.
2. ``_process_file`` integration — confirms the auto-publish post-process
   hook in ``auto_publish_news`` will replace a v1 boilerplate excerpt with
   a v2-marked one and is idempotent on a second run (no re-write).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from seo_diversify_excerpts import (  # noqa: E402
    V2_MARKERS,
    _build_diverse_excerpt,
    _process_file,
)


V1_EXCERPT = (
    "X, Y, Z를 중심으로 2026년 05월 18일 주요 보안/기술 뉴스 15건과 대응 우선순위를 "
    "정리합니다. CVE, AI 등 최신 위협 동향과 DevSecOps 실무 대응 방안을 함께 다룹니다."
)


def _write_fixture_post(
    tmp_path: Path,
    filename: str,
    excerpt: str = V1_EXCERPT,
    highlights: list[tuple[str, str]] | None = None,
) -> Path:
    """Write a minimal Jekyll post fixture under ``tmp_path``."""
    if highlights is None:
        highlights = [
            ("BleepingComputer", "Critical Linux kernel zero-day patched"),
            ("The Hacker News", "Cloudflare worker SSRF disclosed"),
            ("ASEC", "APT group targets Korean telcos"),
        ]
    hl_lines = "\n".join(
        f'    - {{ source: "{s}", title: "{t}" }}' for s, t in highlights
    )
    body = f"""---
layout: post
title: "Sample digest title"
date: 2026-05-18 09:00:00 +0900
categories: [security]
tags: [Security-Weekly, DevSecOps]
excerpt: "{excerpt}"
image: /assets/images/{filename.replace('.md', '.svg')}
summary_card:
  title: "Sample digest title"
  highlights:
{hl_lines}
---

# Body
The body content lives here.
"""
    p = tmp_path / filename
    p.write_text(body, encoding="utf-8")
    return p


class TestBuildDiverseExcerpt:
    """Pure-function checks on ``_build_diverse_excerpt``."""

    def test_length_within_seo_window(self, tmp_path: Path) -> None:
        path = _write_fixture_post(tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md")
        excerpt = _build_diverse_excerpt(
            path,
            title="Sample digest title",
            highlights=["Critical Linux kernel zero-day", "Cloudflare worker SSRF"],
            existing=V1_EXCERPT,
        )
        assert 150 <= len(excerpt) <= 220, f"length out of range: {len(excerpt)}"

    def test_v2_marker_present(self, tmp_path: Path) -> None:
        path = _write_fixture_post(tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md")
        excerpt = _build_diverse_excerpt(
            path,
            title="Sample digest title",
            highlights=["Critical kernel zero-day", "Worker SSRF disclosed"],
            existing=V1_EXCERPT,
        )
        assert any(m in excerpt for m in V2_MARKERS), (
            f"v2 marker missing in: {excerpt}"
        )

    def test_no_v1_boilerplate_residue(self, tmp_path: Path) -> None:
        path = _write_fixture_post(tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md")
        excerpt = _build_diverse_excerpt(
            path,
            title="Sample digest title",
            highlights=["A", "B"],
            existing=V1_EXCERPT,
        )
        assert "DevSecOps 실무 대응 방안을 함께 다룹니다" not in excerpt

    def test_deterministic_by_filename(self, tmp_path: Path) -> None:
        path = _write_fixture_post(tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md")
        e1 = _build_diverse_excerpt(path, "t", ["h1", "h2"], V1_EXCERPT)
        e2 = _build_diverse_excerpt(path, "t", ["h1", "h2"], V1_EXCERPT)
        assert e1 == e2

    def test_no_yaml_breaking_double_quotes(self, tmp_path: Path) -> None:
        """Excerpts must be safe inside a YAML double-quoted scalar.

        Highlights containing ``"`` (decoded from ``&quot;``) used to break
        the front matter — guarded by the YAML-safe pass.
        """
        path = _write_fixture_post(tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md")
        excerpt = _build_diverse_excerpt(
            path,
            title="t",
            highlights=['cPanel 취약점 "Sorry" 랜섬웨어', 'Trellix "Sample" 케이스'],
            existing=V1_EXCERPT,
        )
        assert '"' not in excerpt


class TestProcessFile:
    """Integration: file-level rewrite and idempotence."""

    def test_rewrites_v1_excerpt(self, tmp_path: Path) -> None:
        path = _write_fixture_post(
            tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md"
        )
        changed, reason = _process_file(path, apply=True)
        assert changed is True
        assert reason in {"rewritten", "would-rewrite"}
        new_text = path.read_text(encoding="utf-8")
        new_excerpt_line = next(
            ln for ln in new_text.splitlines() if ln.startswith("excerpt:")
        )
        assert any(m in new_excerpt_line for m in V2_MARKERS)
        # original boilerplate gone
        assert "DevSecOps 실무 대응 방안을 함께 다룹니다" not in new_text

    def test_idempotent_second_run(self, tmp_path: Path) -> None:
        path = _write_fixture_post(
            tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md"
        )
        _process_file(path, apply=True)
        changed, reason = _process_file(path, apply=True)
        assert changed is False
        assert reason == "already-v2"

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        path = _write_fixture_post(
            tmp_path, "2026-05-18-Tech_Security_Weekly_Digest_X.md"
        )
        before = path.read_text(encoding="utf-8")
        changed, reason = _process_file(path, apply=False)
        assert changed is True
        assert reason == "would-rewrite"
        assert path.read_text(encoding="utf-8") == before

    def test_missing_excerpt_skipped(self, tmp_path: Path) -> None:
        path = tmp_path / "2026-05-18-Tech_Security_Weekly_Digest_X.md"
        path.write_text(
            "---\nlayout: post\ntitle: \"t\"\n---\n# body\n",
            encoding="utf-8",
        )
        changed, reason = _process_file(path, apply=True)
        assert changed is False
        assert reason == "no-excerpt"


@pytest.mark.parametrize(
    "highlights",
    [
        [],
        [("Src", "Single highlight only")],
        [("Src", 'Title with "double" quotes')],
    ],
)
def test_build_handles_edge_cases(
    tmp_path: Path, highlights: list[tuple[str, str]]
) -> None:
    """The builder must produce a YAML-safe, length-bounded excerpt under all
    highlight shapes the publisher might emit."""
    path = _write_fixture_post(
        tmp_path,
        "2026-05-18-Tech_Security_Weekly_Digest_X.md",
        highlights=highlights,
    )
    changed, _ = _process_file(path, apply=True)
    assert changed is True
    new_text = path.read_text(encoding="utf-8")
    excerpt_line = next(
        ln for ln in new_text.splitlines() if ln.startswith("excerpt:")
    )
    # No bare double quotes inside the value (the wrapper ones don't count)
    inner = excerpt_line[len('excerpt: "') : -1]
    assert '"' not in inner
    assert 150 <= len(inner) <= 220

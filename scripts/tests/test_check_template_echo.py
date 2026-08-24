#!/usr/bin/env python3
"""Tests for scripts/check_template_echo.py and its three wiring points.

Two halves:

* **Detector** — the gate must catch every shape the corpus actually produced
  (both include kinds, both whitespace-control forms) and must not fire on prose
  that merely discusses attack vectors.
* **Wiring guard** — a detector nobody runs is not a gate. The three enforcement
  points exist because the corpus has three write paths, and the cron path in
  particular runs with no local hooks; dropping any one of them silently
  restores the condition in which 490 defects accumulated unnoticed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_template_echo import check_text, main  # noqa: E402
from scripts.rewrite_template_echo_summaries import TEMPLATE_MARKERS  # noqa: E402

HOOK_SRC = REPO_ROOT / "scripts" / "install-hooks.sh"
HOOK_FILE = REPO_ROOT / ".githooks" / "pre-commit"
SVG_LINT = REPO_ROOT / ".github" / "workflows" / "svg-lint.yml"
BLOGWATCHER = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

FRONT_MATTER = '---\nlayout: post\ntitle: "t"\n---\n\n'


def _card(summary: str, kind: str = "news-card", dash: str = "-") -> str:
    return (
        f"{{%{dash} include {kind}.html\n"
        '  title="Acme breach"\n'
        '  url="https://example.org/a"\n'
        f'  summary="{summary}"\n'
        '  source="Acme"\n'
        '  severity="high"\n'
        f"{dash}%}}\n"
    )


ECHO = "Acme breach를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, 대응 우선순위를 정리합니다."
REAL = "Acme는 고객 인증 토큰 12만 건이 유출됐다고 8월 6일 공시했다. 토큰 회전이 진행 중이다."


class TestDetector:
    def test_clean_summary_passes(self):
        assert check_text(FRONT_MATTER + _card(REAL)) == []

    @pytest.mark.parametrize("marker", TEMPLATE_MARKERS)
    def test_every_marker_is_caught(self, marker):
        hits = check_text(FRONT_MATTER + _card(f"Acme breach {marker}, 대응합니다."))
        assert len(hits) == 1
        assert hits[0][1] == marker

    @pytest.mark.parametrize("dash", ["", "-"])
    def test_both_whitespace_control_forms(self, dash):
        """``\\s`` does not match ``-``.

        A gate spelled ``\\{%\\s*include`` skips every ``{%- include`` card —
        282 of 2117 on 2026-08-07 — and reports a clean corpus. That miss is why
        the patterns are imported from news_card_patterns rather than re-spelled
        here (contract C8/C11).
        """
        assert len(check_text(FRONT_MATTER + _card(ECHO, dash=dash))) == 1

    def test_spotlight_items_are_covered(self):
        """45 of the 490 defects lived in news-spotlight-item, not news-card."""
        text = FRONT_MATTER + _card(ECHO, kind="news-spotlight-item")
        assert len(check_text(text)) == 1

    def test_reports_the_line_of_the_summary(self):
        text = FRONT_MATTER + "\n\n\n" + _card(ECHO)
        line = check_text(text)[0][0]
        assert text.split("\n")[line - 1].strip().startswith('summary="')

    def test_prose_outside_a_card_is_not_flagged(self):
        """The gate is about a card attribute, not about the words.

        A post may legitimately write these phrases in its body — that is
        analysis, not a summary that claims to describe an article.
        """
        body = (
            FRONT_MATTER + f"이 절에서는 {TEMPLATE_MARKERS[0]}, 배포 순서를 다룬다.\n"
        )
        assert check_text(body) == []

    def test_multiple_defects_counted_separately(self):
        text = FRONT_MATTER + _card(ECHO) + "\n" + _card(ECHO, dash="")
        assert len(check_text(text)) == 2

    def test_card_without_summary_attribute(self):
        text = FRONT_MATTER + (
            "{%- include news-card.html\n"
            '  title="Acme breach"\n'
            '  url="https://example.org/a"\n'
            "-%}\n"
        )
        assert check_text(text) == []


class TestCli:
    def test_exit_code_and_output(self, tmp_path, capsys):
        bad = tmp_path / "2026-08-08-Bad_Weekly_Digest.md"
        bad.write_text(FRONT_MATTER + _card(ECHO), encoding="utf-8")
        assert main([str(bad)]) == 1
        out = capsys.readouterr()
        assert "FAIL" in out.out
        assert "rewrite_template_echo_summaries.py" in out.err

    def test_clean_file_exits_zero(self, tmp_path, capsys):
        good = tmp_path / "2026-08-08-Good_Weekly_Digest.md"
        good.write_text(FRONT_MATTER + _card(REAL), encoding="utf-8")
        assert main([str(good)]) == 0

    def test_corpus_is_at_zero(self):
        """No ratchet, no baseline — the gate only works from a clean corpus.

        If this ever fails, either a defect landed or the campaign regressed;
        do not add a baseline to make it green.
        """
        result = subprocess.run(
            [sys.executable, "scripts/check_template_echo.py", "--all", "--quiet"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            "the corpus re-acquired template-echo summaries:\n"
            f"{result.stdout}\n{result.stderr}"
        )


class TestWiring:
    """A detector nobody runs is not a gate."""

    def test_precommit_source_and_generated_hook_agree(self):
        """``.githooks/pre-commit`` is generated by ``install-hooks.sh``.

        Editing only the generated file works until the next
        ``bash scripts/install-hooks.sh`` silently reverts it.
        """
        for path in (HOOK_SRC, HOOK_FILE):
            text = path.read_text(encoding="utf-8")
            assert "check_template_echo.py" in text, (
                f"{path.name} no longer runs the template-echo gate. Human "
                "authoring and repair PRs are one of the three write paths into "
                "the corpus."
            )
            assert "--staged" in text.split("check_template_echo.py")[1][:40], (
                f"{path.name} runs the gate without --staged; a pre-commit hook "
                "must scope to what is being committed."
            )

    def test_ci_runs_the_gate_over_the_whole_corpus(self):
        text = SVG_LINT.read_text(encoding="utf-8")
        assert "check_template_echo.py --all" in text, (
            "svg-lint no longer runs the template-echo gate with --all. The "
            "corpus is at 0 with no baseline, and --all is what catches a defect "
            "that reached a branch without passing pre-commit (a cron push runs "
            "with no local hooks)."
        )
        assert "'scripts/check_template_echo.py'" in text, (
            "the workflow's paths filter does not include the gate script, so a "
            "change to the gate itself would not run it."
        )

    def test_blogwatcher_self_heals_then_blocks(self):
        text = BLOGWATCHER.read_text(encoding="utf-8")
        assert "check_template_echo.py" in text, (
            "the blogwatcher publish path no longer checks for template-echo "
            "summaries. That path is why the gate exists: its GitHub-Actions "
            "commit runs with no local hooks, so pre-commit never sees the post "
            "the cron writes."
        )
        assert "rewrite_template_echo_summaries.py" in text, (
            "the self-heal step is gone. The repair is deterministic (it lifts "
            "prose the post already carries, no network and no LLM), so a "
            "fixable defect should not block the weekly publish."
        )
        # The check must run AFTER the self-heal, or the heal proves nothing.
        heal = text.index("rewrite_template_echo_summaries.py")
        checks = [
            i for i in range(len(text)) if text.startswith("check_template_echo.py", i)
        ]
        assert any(i > heal for i in checks), (
            "every check_template_echo.py call precedes the self-heal, so a "
            "defect that survives the rewrite would still publish."
        )

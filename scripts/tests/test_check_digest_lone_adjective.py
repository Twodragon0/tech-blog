"""Tests for scripts/check_digest_lone_adjective.py + its blogwatcher wiring.

The CLI mirrors TestCorpusNoLoneAdjectiveAi so the blogwatcher publish path can
surface an unvetted lone-adjective+AI cover panel at publish time (warn), rather
than letting main's corpus test go red silently after the cron pushes.
"""
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_digest_lone_adjective import check_post, main  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
BLOGWATCHER = REPO / ".github" / "workflows" / "ai-blogwatcher.yml"


def _write(tmp, body_fm):
    p = Path(tmp) / "2026-01-01-X_Weekly_Digest.md"
    p.write_text(f"---\n{body_fm}\n---\nbody\n", encoding="utf-8")
    return str(p)


def test_flags_unvetted_lone_adjective():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "Quantum AI, breaks RSA" }')
        offenders = check_post(p)
        assert offenders and "Quantum" in offenders[0]


def test_vetted_brand_claude_is_clean():
    # 'claude' is in _DEFERRED_AI_ADJECTIVES (real brand, lone lead correct).
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "Claude AI, breaks PQC tests" }')
        assert check_post(p) == []


def test_vetted_compound_agentic_is_clean():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "Agentic AI, new risks" }')
        assert check_post(p) == []


def test_no_summary_card_is_clean():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, 'title: "x"')
        assert check_post(p) == []


def test_non_lead_ai_not_flagged():
    # multi-word lead (has space) is not a lone-adjective panel
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "새로운 위협 동향 정리" }')
        assert check_post(p) == []


def test_main_exit_codes():
    with tempfile.TemporaryDirectory() as d:
        bad = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "Quantum AI, breaks RSA" }')
        assert main([bad]) == 1
    with tempfile.TemporaryDirectory() as d:
        good = _write(d, 'summary_card:\n  highlights:\n    - { source: "X", title: "Claude AI, breaks PQC" }')
        assert main([good]) == 0


def test_wired_into_blogwatcher_publish():
    body = "\n".join(
        ln for ln in BLOGWATCHER.read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    )
    assert re.search(r"check_digest_lone_adjective\.py", body), (
        "ai-blogwatcher.yml no longer runs the lone-adjective pre-flight; an "
        "unvetted 'X AI' cover panel would break main's corpus test silently "
        "after the cron push. Re-add the warn step."
    )

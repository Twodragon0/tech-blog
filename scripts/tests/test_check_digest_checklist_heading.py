"""Tests for the publish-time canonical-checklist-heading gate.

Covers the recurrence hole closed after the 601 -> 0 structure campaign:
`check_digest_structure.py` counts the RAW SUBSTRING "## 실무 체크리스트", so a
demoted (`### 실무 체크리스트`) or suffixed (`## 실무 체크리스트 (P0)`) heading
still counts as 1 and passes silently, while the numbered tier-C form
(`## 9. 실무 체크리스트`) is only reported as the generic "found 0".
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import check_digest_checklist_heading as gate  # noqa: E402

_FM = '---\nlayout: post\ntitle: "x"\n---\n\n'
_ITEM = "## 1. 보안\n\n### 1.1 항목\n\n본문.\n\n"


def _post(tmp_path, body, name="2026-08-06-Tech_Blog_Weekly_Digest_x.md"):
    p = tmp_path / name
    p.write_text(_FM + body, encoding="utf-8")
    return p


# --- canonical / clean -------------------------------------------------------


def test_canonical_heading_is_clean(tmp_path):
    p = _post(tmp_path, _ITEM + "## 실무 체크리스트\n\n- [ ] 조치\n")
    assert gate.check_post(p) == []


def test_topical_item_checklist_is_not_flagged(tmp_path):
    """`#### 마이그레이션 체크리스트` etc. are legitimate item content."""
    body = (
        "## 1. 보안\n\n### 1.1 항목\n\n#### 마이그레이션 체크리스트\n\n- 항목\n\n"
        "## 실무 체크리스트\n\n- [ ] 조치\n"
    )
    assert gate.check_post(_post(tmp_path, body)) == []


def test_heading_inside_code_fence_is_ignored(tmp_path):
    body = (
        "## 실무 체크리스트\n\n- [ ] 조치\n\n"
        "```markdown\n### 실무 체크리스트\n```\n"
    )
    assert gate.check_post(_post(tmp_path, body)) == []


def test_non_digest_post_is_skipped(tmp_path):
    p = _post(tmp_path, "## 9. 실무 체크리스트\n", name="2026-08-06-Some_Post.md")
    assert gate.check_post(p) == []


# --- variants (the regression this gate blocks) ------------------------------


def test_numbered_tier_c_variant_is_flagged(tmp_path):
    v = gate.check_post(_post(tmp_path, _ITEM + "## 9. 실무 체크리스트\n\n- [ ] 조치\n"))
    assert len(v) == 1
    assert "9. 실무 체크리스트" in v[0]


def test_demoted_h3_variant_is_flagged(tmp_path):
    """Passes check_digest_structure today (substring count == 1)."""
    v = gate.check_post(_post(tmp_path, _ITEM + "### 실무 체크리스트\n\n- [ ] 조치\n"))
    assert len(v) == 1
    assert "### 실무 체크리스트" in v[0]


def test_suffixed_variant_is_flagged(tmp_path):
    """Also passes check_digest_structure today (no `$` anchor)."""
    v = gate.check_post(_post(tmp_path, _ITEM + "## 실무 체크리스트 (P0/P1)\n\n- [ ] 조치\n"))
    assert len(v) == 1
    assert "(P0/P1)" in v[0]


def test_stray_variant_alongside_canonical_is_flagged(tmp_path):
    body = _ITEM + "## 실무 체크리스트\n\n- [ ] 조치\n\n### 실무 체크리스트\n\n- [ ] 또\n"
    v = gate.check_post(_post(tmp_path, body))
    assert len(v) == 1
    assert "### 실무 체크리스트" in v[0]


def test_renamed_checklist_surface_is_flagged_as_missing(tmp_path):
    """No `실무 체크리스트` at all — report missing + the nearest candidate."""
    v = gate.check_post(_post(tmp_path, _ITEM + "## 실행 체크리스트\n\n- [ ] 조치\n"))
    assert len(v) == 1
    assert "missing" in v[0]
    assert "## 실행 체크리스트" in v[0]


def test_no_checklist_surface_at_all_is_flagged(tmp_path):
    v = gate.check_post(_post(tmp_path, _ITEM))
    assert len(v) == 1
    assert "missing" in v[0]


def test_duplicate_canonical_is_flagged(tmp_path):
    body = _ITEM + "## 실무 체크리스트\n\n- [ ] a\n\n## 실무 체크리스트\n\n- [ ] b\n"
    v = gate.check_post(_post(tmp_path, body))
    assert len(v) == 1
    assert "2" in v[0]


# --- CLI ---------------------------------------------------------------------


def test_cli_exit_1_on_variant(tmp_path, capsys):
    p = _post(tmp_path, _ITEM + "## 9. 실무 체크리스트\n")
    assert gate.main([str(p)]) == 1
    assert "FAIL" in capsys.readouterr().out


def test_cli_exit_0_on_canonical(tmp_path, capsys):
    p = _post(tmp_path, _ITEM + "## 실무 체크리스트\n\n- [ ] 조치\n")
    assert gate.main([str(p)]) == 0
    assert "OK" in capsys.readouterr().out


# --- corpus + wiring ---------------------------------------------------------


def test_corpus_is_clean():
    """Measured 2026-08-06: 184/184 digests carry exactly one canonical H2."""
    offenders = {}
    for p in sorted((REPO / "_posts").glob("*Weekly_Digest*.md")):
        v = gate.check_post(p)
        if v:
            offenders[p.name] = v
    assert offenders == {}, offenders


def _noncomment(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


def test_wired_into_blogwatcher_publish():
    wf = (REPO / ".github/workflows/ai-blogwatcher.yml").read_text(encoding="utf-8")
    assert "check_digest_checklist_heading.py" in _noncomment(wf)


@pytest.mark.parametrize("rel", [".githooks/pre-commit", "scripts/install-hooks.sh"])
def test_wired_into_precommit(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert re.search(
        r'check_digest_checklist_heading\.py"?\s+--staged', _noncomment(text)
    ), f"{rel} must run the gate on staged digests"


def test_self_heal_runs_before_the_blocking_verify():
    """restore_digest_structure must be attempted BEFORE the gate blocks."""
    wf = (REPO / ".github/workflows/ai-blogwatcher.yml").read_text(encoding="utf-8")
    step = wf.split("Canonical checklist heading pre-flight")[1].split("- name:")[0]
    assert step.index("restore_digest_structure.py") < step.rindex(
        "check_digest_checklist_heading.py"
    )

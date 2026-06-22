"""Tests for the upgrade_l20_cover ownership guard (no clobber of other systems)."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import upgrade_l20_cover as u

SPECS = u.SPECS_DIR


def _spec(name: str):
    p = SPECS / f"{name}.yml"
    if not p.exists():
        pytest.skip(f"spec not present: {name}")
    return u.load_spec(p)


def test_digest_slug_is_cron_owned():
    s = _spec("2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent")
    assert u.spec_ownership(s) == "cron"


def test_cover_style_post_is_content_mode_owned():
    s = _spec("2026-01-17-AI_Coding_Assistants_Comparison_Gemini_Claude_Code_ChatGPT_OpenCode_2025_2026_Research_Analysis")
    assert u.spec_ownership(s) == "content_mode"


def test_competing_digest_spec_is_not_l20_owned():
    # 2025-05-09 7Batch-4Week has a top-level _data/digest_covers spec → L22-owned.
    s = _spec("2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_and_ISMS_Response_Guide")
    assert u.spec_ownership(s) == "digest_covers"


def test_l20_exclusive_cover_is_spec_owned():
    # 12-19 ISMS-P: non-digest, no cover_style, no competing spec → spec-owned.
    s = _spec("2025-12-19-Cloud_Security_8Batch_4Week_Integration_Security_Vulnerability_Inspection_and_ISMS-P_Certification_Response")
    assert u.spec_ownership(s) == "spec"


def test_main_spec_refuses_cron_owned_with_exit_3():
    p = SPECS / "2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.yml"
    if not p.exists():
        pytest.skip("spec not present")
    assert u.main(["--spec", str(p)]) == 3  # refuse, do not write


def test_main_all_dry_run_does_not_write_but_succeeds():
    # --dry-run is harmless (no write) and must not be blocked by the guard.
    assert u.main(["--all", "--dry-run"]) == 0

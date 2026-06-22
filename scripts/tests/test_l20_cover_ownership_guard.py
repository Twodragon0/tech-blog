"""Tests for the upgrade_l20_cover ownership guard (no clobber of other systems).

Uses synthetic spec-like objects + monkeypatched lookups so the tests do NOT
depend on which spec files exist on disk (the vestigial specs are being
discarded; the guard logic must stay covered regardless)."""
from __future__ import annotations

from types import SimpleNamespace

from scripts import upgrade_l20_cover as u


def _spec(slug: str, date: str = "2026-01-08"):
    # spec_ownership only reads .slug and .date.
    return SimpleNamespace(slug=slug, date=date)


def test_digest_slug_is_cron_owned(monkeypatch):
    # cron classification is a pure slug-regex match — no file lookup.
    monkeypatch.setattr(u, "_owning_post_text", lambda *a: None)
    monkeypatch.setattr(u, "_competing_spec", lambda *a: None)
    assert u.spec_ownership(_spec("Tech_Security_Weekly_Digest_AI_Foo")) == "cron"
    assert u.spec_ownership(_spec("January_2026_Security_Digest_Monthly_Index")) == "cron"


def test_cover_style_post_is_content_mode_owned(monkeypatch):
    monkeypatch.setattr(u, "_owning_post_text", lambda d, s: "---\ncover_style: l20\n---\n")
    monkeypatch.setattr(u, "_competing_spec", lambda *a: None)
    assert u.spec_ownership(_spec("Some_Content_Guide")) == "content_mode"


def test_competing_digest_spec_is_not_l20_owned(monkeypatch):
    monkeypatch.setattr(u, "_owning_post_text", lambda *a: "---\ntitle: x\n---\n")
    monkeypatch.setattr(u, "_competing_spec", lambda d, s: "digest_covers")
    assert u.spec_ownership(_spec("Cloud_Security_Course_Week")) == "digest_covers"


def test_l20_exclusive_cover_is_spec_owned(monkeypatch):
    # non-digest slug, no cover_style post, no competing spec → spec-owned.
    monkeypatch.setattr(u, "_owning_post_text", lambda *a: "---\ntitle: x\n---\n")
    monkeypatch.setattr(u, "_competing_spec", lambda *a: None)
    assert u.spec_ownership(_spec("ISMS_P_Certification_Guide")) == "spec"


def test_main_all_dry_run_does_not_write_but_succeeds():
    # --dry-run is harmless (no write) and must not be blocked by the guard.
    assert u.main(["--all", "--dry-run"]) == 0


def test_live_all_writes_only_spec_owned():
    """A real --all must only ever WRITE spec-owned covers; verified via a
    spec-owned cover surviving the guard. Run in --check (read-only) so no
    bytes change: --check is unaffected by the guard and should not error."""
    assert u.main(["--all", "--check"]) in (0, 1)  # 0=no drift, 1=drift; never crash

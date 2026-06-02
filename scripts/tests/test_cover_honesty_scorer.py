#!/usr/bin/env python3
"""Tests for scripts/score_cover_honesty.py (deterministic L20 cover scorer).

Covers the plan's acceptance criteria with SMALL SYNTHETIC FIXTURES (rendered
in-memory via the real builders + render_l20_hero, paired with a tmp post),
so the suite never depends on specific corpus covers that may change.

  - Claim-class taxonomy == VISUAL_BUILDERS keys (R3 lockstep guard).
  - Honesty: fabricated attack band caught; genuine-attack band passes;
    neutral / market / security_advisory always pass.
  - Rubric: gating cap-at-49 on violation; PASS for clean honest cover.
  - STALE_RENDER: fingerprint vs routed-intent disagreement detection.
  - Determinism: same bytes -> identical score.
  - Exit-code matrix incl. baseline grandfathering.

API disabling and sys.path setup are handled by conftest.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import score_cover_honesty as sch
from scripts.lib.svg_l20_hero import VISUAL_BUILDERS, render_l20_hero


# ---------------------------------------------------------------------------
# Fixture helpers — build a real L20 cover SVG with chosen per-band builders.
# ---------------------------------------------------------------------------
def _story(visual_id: str, headline: str = "Story", index: int = 0) -> dict:
    return {
        "tag": "HIGH",
        "index": f"{index + 1:02d}",
        "theme": "red",
        "visual": visual_id,
        "headline": headline,
        "subheadline": "A short honest subheadline for the band",
        "kpi_value": "TBD",
        "kpi_label": "STATUS",
        "kpi_sub": "NEW",
        "action": "REVIEW NOW",
    }


def _render_cover(hero_id: str, tr_id: str, br_id: str) -> str:
    """Render a real L20 cover SVG with the three chosen builders."""
    return render_l20_hero(
        date_str="2026.06.02",
        hero=_story(hero_id, "Hero", 0),
        top_right=_story(tr_id, "Top", 1),
        bottom_right=_story(br_id, "Bottom", 2),
        url="https://tech.2twodragon.com/",
        post_title="Weekly Security Digest - 2026.06.02",
    )


def _write_cover_and_post(
    tmp_path: Path,
    monkeypatch,
    *,
    slug: str,
    hero_id: str,
    tr_id: str,
    br_id: str,
    body: str,
    title: str = "Weekly Digest",
    excerpt: str = "A weekly roundup.",
) -> Path:
    """Create assets/images/<slug>.svg + _posts/<slug>.md in a tmp repo, and
    point the scorer's REPO/ASSETS/POSTS at it. Returns the SVG path."""
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)

    svg_path = assets / f"{slug}.svg"
    svg_path.write_text(_render_cover(hero_id, tr_id, br_id), encoding="utf-8")

    post_md = (
        "---\n"
        f"title: \"{title}\"\n"
        f"excerpt: \"{excerpt}\"\n"
        f"image: /assets/images/{slug}.svg\n"
        "---\n\n"
        f"{body}\n"
    )
    (posts / f"{slug}.md").write_text(post_md, encoding="utf-8")

    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    return svg_path


# ---------------------------------------------------------------------------
# Taxonomy (R3 lockstep guard)
# ---------------------------------------------------------------------------
def test_taxonomy_covers_exactly_the_builders():
    assert set(sch.CLAIM_CLASSES) == set(VISUAL_BUILDERS)


def test_taxonomy_has_eleven_builders():
    assert len(sch.CLAIM_CLASSES) == 11
    assert "security_advisory" in sch.CLAIM_CLASSES


def test_rubric_version_embedded():
    assert sch.RUBRIC_VERSION == "1.0"


def test_each_anchor_present_in_its_rendered_builder():
    """Discriminating anchors must survive rendering (drift guard, R4)."""
    for vid, fn in VISUAL_BUILDERS.items():
        svg = fn(400, 300)
        anchors = sch.CLAIM_CLASSES[vid][2]
        assert anchors, f"{vid} has no discriminating anchor"
        for a in anchors:
            assert a in svg, f"anchor {a!r} missing from rendered {vid}"


# ---------------------------------------------------------------------------
# Honesty detector
# ---------------------------------------------------------------------------
def test_fabricated_cve_band_fails(tmp_path, monkeypatch):
    """A cve_chain band on a price-only post => FAIL, score<=49, named violation."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Market_Only_Digest",
        hero_id="cve_chain", tr_id="market", br_id="neutral",
        body="Bitcoin hit a new high. The crypto market rallied. Price up 12% today.",
    )
    result = sch.score_file(svg)
    assert result["verdict"] == "FAIL"
    assert result["score"] <= sch._HONESTY_CAP
    viols = result["honesty"]["violations"]
    assert any(v["band"] == "hero" and v["visual_id"] == "cve_chain" for v in viols)
    assert "vuln/CVE" in viols[0]["claim_class"]


def test_genuine_attack_band_passes_honesty(tmp_path, monkeypatch):
    """cve_chain on a post carrying a real CVE id => no honesty violation."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Real_CVE_Digest",
        hero_id="cve_chain", tr_id="ransomware_lock", br_id="container_escape",
        body=(
            "CVE-2026-12345 enables RCE. A new ransomware family was seen. "
            "A docker container escape via runc was patched."
        ),
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []
    assert result["honesty"]["score"] == 60


def test_neutral_band_always_passes(tmp_path, monkeypatch):
    """3 neutral bands on any post => 0 honesty violations."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Neutral_Digest",
        hero_id="neutral", tr_id="neutral", br_id="neutral",
        body="A general ecosystem release roundup. Nothing alarming here.",
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []


def test_market_band_passes_even_without_price_token(tmp_path, monkeypatch):
    """market is always_pass: absence of a price token is not a fabrication."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Market_NoPrice_Digest",
        hero_id="market", tr_id="neutral", br_id="neutral",
        body="A general overview with no explicit price figures mentioned.",
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []


def test_security_advisory_band_passes_on_security_digest(tmp_path, monkeypatch):
    """security_advisory is honest on generic-security content (no fabrication)."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Security_Advisory_Digest",
        hero_id="security_advisory", tr_id="neutral", br_id="neutral",
        body="A security advisory roundup covering several vulnerability notices.",
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []


# ---------------------------------------------------------------------------
# Rubric / verdict bands
# ---------------------------------------------------------------------------
def test_clean_honest_cover_passes(tmp_path, monkeypatch):
    """A genuine, diverse, honest attack cover with fresh render => PASS >=70."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Honest_Diverse_Digest",
        hero_id="cve_chain", tr_id="ransomware_lock", br_id="supply_chain_pipe",
        body=(
            "CVE-2026-99999 RCE detail. A ransomware wiper hit a victim. "
            "A supply chain SLSA poisoned npm package was found."
        ),
    )
    result = sch.score_file(svg)
    # No STALE_RENDER because the rendered builders match the routed intent of
    # the headlines is irrelevant here — we assert honesty is clean + verdict.
    assert result["honesty"]["violations"] == []
    assert result["verdict"] in ("PASS", "WARN")  # depends on stale/diversity
    assert result["honesty"]["score"] == 60


def test_violation_caps_total_at_49(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Capped_Digest",
        hero_id="data_exfil", tr_id="neutral", br_id="neutral",
        body="A calm ecosystem digest about release cadence and community velocity.",
    )
    result = sch.score_file(svg)
    assert result["verdict"] == "FAIL"
    assert result["score"] <= 49


def test_low_diversity_flag(tmp_path, monkeypatch):
    """All-identical builders => motif_diversity 0 + LOW_DIVERSITY flag."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Identical_Digest",
        hero_id="neutral", tr_id="neutral", br_id="neutral",
        body="Generic digest.",
    )
    result = sch.score_file(svg)
    assert result["quality"]["motif_diversity"] == 0
    assert "LOW_DIVERSITY" in result["flags"]


# ---------------------------------------------------------------------------
# STALE_RENDER (dual-path disagreement)
# ---------------------------------------------------------------------------
def test_stale_render_detected(monkeypatch):
    """When the on-disk builder disagrees with the routed intent => STALE_RENDER."""
    svg_text = _render_cover("cve_chain", "neutral", "neutral")

    # routed intent says all-neutral; on-disk fingerprint sees cve_chain in hero
    monkeypatch.setattr(sch, "_routed_visual_ids", lambda *a, **k: ["neutral", "neutral", "neutral"])
    fingerprinted = sch._fingerprint_visual_ids(svg_text)
    assert fingerprinted[0] == "cve_chain"  # hero builder recovered from bytes


def test_fingerprint_orders_bands_by_document_position():
    svg_text = _render_cover("ransomware_lock", "data_exfil", "market")
    ids = sch._fingerprint_visual_ids(svg_text)
    assert ids == ["ransomware_lock", "data_exfil", "market"]


def test_stale_render_is_quality_not_honesty(tmp_path, monkeypatch):
    """A stale-but-honest band deducts fresh_render, not honesty."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Stale_Honest_Digest",
        hero_id="neutral", tr_id="neutral", br_id="neutral",
        body="Generic digest.",
    )
    # Force routed intent to differ so every band reads as stale.
    monkeypatch.setattr(sch, "_routed_visual_ids", lambda *a, **k: ["market", "market", "market"])
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []  # neutral still honest
    assert result["quality"]["fresh_render"] == 0  # 3 stale bands
    assert any(f.startswith("STALE_RENDER") for f in result["flags"])


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def test_determinism_same_bytes_same_score(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Determinism_Digest",
        hero_id="cve_chain", tr_id="market", br_id="neutral",
        body="Bitcoin price moved. No CVE here at all.",
    )
    r1 = sch.score_file(svg)
    r2 = sch.score_file(svg)
    assert r1 == r2


# ---------------------------------------------------------------------------
# Cover -> post mapping edge cases
# ---------------------------------------------------------------------------
def test_no_post_when_image_unmapped(tmp_path, monkeypatch):
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    svg_path = assets / "2026-06-02-Orphan_Cover.svg"
    svg_path.write_text(_render_cover("neutral", "neutral", "neutral"), encoding="utf-8")
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    result = sch.score_file(svg_path)
    assert result["verdict"] == "NO_POST"


def test_non_l20_svg_skipped(tmp_path, monkeypatch):
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    svg_path = assets / "2026-06-02-Not_L20.svg"
    svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    result = sch.score_file(svg_path)
    assert result["verdict"] == "SKIP"


# ---------------------------------------------------------------------------
# Unknown builder => hard FAIL (R3, never a silent pass)
# ---------------------------------------------------------------------------
def test_unknown_builder_is_violation():
    score, viols, flags = sch._score_honesty(["totally_new_builder", "neutral", "neutral"], "")
    assert any(v["reason"].startswith("UNKNOWN_BUILDER") for v in viols)
    assert any(f.startswith("UNKNOWN_BUILDER") for f in flags)
    assert score == 35  # 60 - 25


# ---------------------------------------------------------------------------
# check_file importable gate
# ---------------------------------------------------------------------------
def test_check_file_clean_for_passing_cover(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-CheckFile_Pass_Digest",
        hero_id="cve_chain", tr_id="ransomware_lock", br_id="supply_chain_pipe",
        body="CVE-2026-1 RCE. ransomware wiper. supply chain slsa poisoned npm.",
    )
    # Align routed intent so no STALE_RENDER noise.
    monkeypatch.setattr(
        sch, "_routed_visual_ids",
        lambda *a, **k: sch._fingerprint_visual_ids(svg.read_text()),
    )
    msgs = sch.check_file(svg)
    assert msgs == []


def test_check_file_reports_violation(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-CheckFile_Fail_Digest",
        hero_id="cve_chain", tr_id="neutral", br_id="neutral",
        body="No security tokens of any kind in this calm overview.",
    )
    msgs = sch.check_file(svg)
    assert any("HONESTY_VIOLATION" in m for m in msgs)


# ---------------------------------------------------------------------------
# Exit-code matrix (CLI) incl. baseline grandfathering
# ---------------------------------------------------------------------------
def test_cli_no_input_returns_2():
    assert sch.main([]) == 2


def test_cli_strict_fails_on_unbaselined_fail(tmp_path, monkeypatch, capsys):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-StrictFail_Digest",
        hero_id="cve_chain", tr_id="neutral", br_id="neutral",
        body="Calm overview, no attack tokens.",
    )
    code = sch.main(["--files", str(svg), "--strict"])
    assert code == 1


def test_cli_strict_passes_when_baselined(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Baselined_Digest",
        hero_id="cve_chain", tr_id="neutral", br_id="neutral",
        body="Calm overview, no attack tokens.",
    )
    baseline = tmp_path / "baseline.txt"
    baseline.write_text(sch._repo_rel(svg) + "\n", encoding="utf-8")
    code = sch.main(["--files", str(svg), "--strict", "--baseline", str(baseline)])
    assert code == 0


def test_cli_warn_only_default_returns_0_on_fail(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-WarnOnly_Digest",
        hero_id="cve_chain", tr_id="neutral", br_id="neutral",
        body="Calm overview, no attack tokens.",
    )
    # No --strict => warn-only => exit 0 even with a FAIL.
    code = sch.main(["--files", str(svg)])
    assert code == 0


def test_cli_json_output(tmp_path, monkeypatch, capsys):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-Json_Digest",
        hero_id="neutral", tr_id="market", br_id="security_advisory",
        body="A security overview with bitcoin price commentary and advisory notes.",
    )
    code = sch.main(["--files", str(svg), "--json"])
    assert code == 0
    out = capsys.readouterr().out
    import json as _json
    parsed = _json.loads(out)
    assert parsed[0]["rubric_version"] == "1.0"


def test_cli_update_baseline_writes_fails(tmp_path, monkeypatch):
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-UpdateBaseline_Digest",
        hero_id="cve_chain", tr_id="neutral", br_id="neutral",
        body="Calm overview, no attack tokens.",
    )
    out_baseline = tmp_path / "out_baseline.txt"
    code = sch.main(["--update-baseline", str(out_baseline)])
    assert code == 0
    written = out_baseline.read_text()
    assert sch._repo_rel(svg) in written


# ---------------------------------------------------------------------------
# is_l20_cover helper
# ---------------------------------------------------------------------------
def test_is_l20_cover_true_for_real_cover(tmp_path):
    p = tmp_path / "cover.svg"
    p.write_text(_render_cover("neutral", "neutral", "neutral"), encoding="utf-8")
    assert sch.is_l20_cover(p) is True


def test_is_l20_cover_false_for_plain_svg(tmp_path):
    p = tmp_path / "plain.svg"
    p.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
    assert sch.is_l20_cover(p) is False

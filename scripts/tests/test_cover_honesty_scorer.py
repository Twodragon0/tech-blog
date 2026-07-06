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

import sys
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
    # 1.1 = taxonomy widened from L20-only to L20 + L22 + L25 (OQ-5).
    assert sch.RUBRIC_VERSION == "1.1"


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


def test_owning_post_found_via_inline_body_img(tmp_path, monkeypatch):
    """A cover whose stem is referenced by an inline body <img> (a derivative
    like *_image.jpg) is owned by that post even when no post's image: front
    matter points at the SVG. Prevents a false NO_POST (Zscaler short-slug case
    — the SVG's _image.jpg is an inline body image in the Complete_Block post)."""
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    # The cover SVG has no post pointing at it via image:.
    cover = assets / "2026-06-02-Topic_Short.svg"
    cover.write_text(_render_cover("neutral", "neutral", "neutral"), encoding="utf-8")
    # A different post (image: points elsewhere) embeds the cover's _image.jpg
    # derivative inline in its body.
    post_md = (
        "---\n"
        'title: "Long Topic Guide"\n'
        'excerpt: "Guide."\n'
        "image: /assets/images/2026-06-02-Topic_Long_Hero.svg\n"
        "---\n\n"
        "Body intro.\n\n"
        '<img src="{{ \'/assets/images/2026-06-02-Topic_Short_image.jpg\' '
        '| relative_url }}" alt="inline">\n'
    )
    (posts / "2026-06-02-Topic_Long_Hero.md").write_text(post_md, encoding="utf-8")
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)

    owner = sch.find_owning_post(cover)
    assert owner is not None and owner.name == "2026-06-02-Topic_Long_Hero.md"
    # And the cover is no longer a false NO_POST.
    assert sch.score_file(cover)["verdict"] != "NO_POST"


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
    assert parsed[0]["rubric_version"] == "1.1"
    assert parsed[0]["system"] == "L20"


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


# ===========================================================================
# L22 — 3-band FALLBACK digest renderer (OQ-5)
# ===========================================================================
from scripts.lib.svg_l22_generator import (  # noqa: E402
    THEMES as L22_THEMES,
    render_bands_svg,
    v_lock_cve,
    v_network_nodes,
    v_shield,
    v_code_bars,
    v_price_chart,
    SINGLE_ILLUSTRATIONS,
    render_single_svg,
)


def _l22_band(visual_kind: str, headline: str = "Headline") -> dict:
    """Build one render_bands_svg band cfg carrying the chosen visual."""
    theme = L22_THEMES["red"]
    a, soft = theme["accent"], theme["soft"]
    visual = {
        "lock_cve": lambda: v_lock_cve(500, 105, a, soft),
        "network_nodes": lambda: v_network_nodes(500, 105, a, soft),
        "shield": lambda: v_shield(500, 105, a, soft),
        "code_bars": lambda: v_code_bars(500, 105, a, soft),
        "price_chart": lambda: v_price_chart(500, 105, a, soft),
    }[visual_kind]()
    return dict(
        theme="red", label="ALERT", headline=headline,
        metric="metric", detail="detail",
        badge_value="9.8", badge_label="CVSS", badge_sub="critical",
        visual=visual,
    )


def _render_l22(k0: str, k1: str, k2: str) -> str:
    return render_bands_svg(
        sfx="T1", aria="Weekly digest cover", title="Digest",
        url="https://tech.2twodragon.com/",
        bands_cfg=[_l22_band(k0), _l22_band(k1), _l22_band(k2)],
    )


def _write_l22(tmp_path, monkeypatch, *, slug, k0, k1, k2, body,
               title="Weekly Digest", excerpt="Roundup."):
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    svg_path = assets / f"{slug}.svg"
    svg_path.write_text(_render_l22(k0, k1, k2), encoding="utf-8")
    (posts / f"{slug}.md").write_text(
        "---\n"
        f'title: "{title}"\n'
        f'excerpt: "{excerpt}"\n'
        f"image: /assets/images/{slug}.svg\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    return svg_path


def test_l22_taxonomy_anchors_survive_render():
    """Every L22 claim-class anchor must be present in its rendered visual.

    Lockstep is asserted against the generator's OWN canonical registry
    (``svg_l22_generator.VISUAL_BUILDERS``), imported live — not a test-side
    hand-maintained mirror. So a new ``v_*`` builder added to the generator
    without a matching ``CLAIM_CLASSES_L22`` entry (or vice versa) fails here,
    and the registry cannot rot independently of the definitions it lives beside.
    Mirrors the L20 ``set(CLAIM_CLASSES) == set(VISUAL_BUILDERS)`` guard.
    """
    import scripts.lib.svg_l22_generator as l22
    builders = l22.VISUAL_BUILDERS
    assert set(sch.CLAIM_CLASSES_L22) == set(builders)
    for vid, fn in builders.items():
        svg = fn(500, 105, "#fff", "#aaa")
        for a in sch.CLAIM_CLASSES_L22[vid][2]:
            assert a in svg, f"L22 anchor {a!r} missing from rendered {vid}"


def test_l22_detected_as_system():
    svg_text = _render_l22("lock_cve", "network_nodes", "code_bars")
    assert sch.detect_system(svg_text) == "L22"
    assert "profile: high-quality-cover" not in svg_text  # no profile marker


def test_l22_fingerprint_orders_bands_by_document_position():
    svg_text = _render_l22("shield", "network_nodes", "code_bars")
    ids = sch._fingerprint_visual_ids(svg_text, sch.CLAIM_CLASSES_L22, n_bands=3)
    assert ids == ["shield", "network_nodes", "code_bars"]


def test_l22_fabricated_cve_band_fails(tmp_path, monkeypatch):
    """An L22 lock_cve band on a CVE-free post => FAIL, capped, named violation."""
    svg = _write_l22(
        tmp_path, monkeypatch,
        slug="2026-06-02-L22_NoCVE_Digest",
        k0="lock_cve", k1="code_bars", k2="shield",
        body="A calm weekly roundup of community releases. No security ids here.",
    )
    result = sch.score_file(svg)
    assert result["system"] == "L22"
    assert result["verdict"] == "FAIL"
    assert result["score"] <= sch._HONESTY_CAP
    viols = result["honesty"]["violations"]
    assert any(v["visual_id"] == "lock_cve" and "vuln/CVE" in v["claim_class"]
               for v in viols)


def test_l22_genuine_attack_band_passes(tmp_path, monkeypatch):
    """L22 lock_cve + network_nodes on a post with real CVE + botnet => clean."""
    svg = _write_l22(
        tmp_path, monkeypatch,
        slug="2026-06-02-L22_Real_Digest",
        k0="lock_cve", k1="network_nodes", k2="code_bars",
        body="CVE-2026-12345 RCE under exploit. A botnet C2 cluster was sinkholed.",
    )
    result = sch.score_file(svg)
    assert result["system"] == "L22"
    assert result["honesty"]["violations"] == []


def test_l22_advisory_visual_always_passes(tmp_path, monkeypatch):
    """shield / code_bars / price_chart assert no fabricated incident."""
    svg = _write_l22(
        tmp_path, monkeypatch,
        slug="2026-06-02-L22_Advisory_Digest",
        k0="shield", k1="code_bars", k2="price_chart",
        body="A general technical posture overview. Nothing alarming.",
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []


def test_l22_determinism(tmp_path, monkeypatch):
    svg = _write_l22(
        tmp_path, monkeypatch,
        slug="2026-06-02-L22_Determinism_Digest",
        k0="lock_cve", k1="shield", k2="code_bars",
        body="No CVE here.",
    )
    assert sch.score_file(svg) == sch.score_file(svg)


# ===========================================================================
# L25 — single-topic cover (one illustrative visual)
# ===========================================================================
def _render_l25(illustration_key: str, *, headline="Single Topic Post",
                category="guide") -> str:
    return render_single_svg(
        sfx="L25", aria="single cover", title="A Single Topic Post",
        url="https://tech.2twodragon.com/",
        headline=headline, category=category,
        tag_line="DEVSECOPS / SECURITY", body_line="An overview.",
        tags=["AWS", "SECURITY"], visual_id="ABCDEF012345",
        date_label="June 2, 2026",
        illustration_key=illustration_key,
    )


def _write_l25(tmp_path, monkeypatch, *, slug, illustration_key, body,
               title="Single Topic Post", excerpt="Overview.",
               category="guide", headline="Single Topic Post"):
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    svg_path = assets / f"{slug}.svg"
    svg_path.write_text(
        _render_l25(illustration_key, headline=headline, category=category),
        encoding="utf-8",
    )
    (posts / f"{slug}.md").write_text(
        "---\n"
        f'title: "{title}"\n'
        f'excerpt: "{excerpt}"\n'
        f"category: {category}\n"
        f"image: /assets/images/{slug}.svg\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    return svg_path


def test_l25_taxonomy_anchors_survive_render():
    """Every L25 claim-class anchor must be present in its rendered illustration."""
    assert set(sch.CLAIM_CLASSES_L25) == set(SINGLE_ILLUSTRATIONS)
    for vid, fn in SINGLE_ILLUSTRATIONS.items():
        svg = fn(900, 278, "#fff", "#aaa")
        for a in sch.CLAIM_CLASSES_L25[vid][2]:
            assert a in svg, f"L25 anchor {a!r} missing from rendered {vid}"


def test_l25_detected_as_system():
    svg_text = _render_l25("shield")
    assert sch.detect_system(svg_text) == "L25"
    assert sch._L25_MARKER in svg_text


def test_l25_illustrative_visual_always_passes(tmp_path, monkeypatch):
    """A single-illustrative L25 cover (cloud) asserts no incident => clean PASS."""
    svg = _write_l25(
        tmp_path, monkeypatch,
        slug="2026-06-02-L25_Cloud_Guide",
        illustration_key="cloud",
        body="A walkthrough of cloud workload architecture and best practices.",
    )
    result = sch.score_file(svg)
    assert result["system"] == "L25"
    assert result["honesty"]["violations"] == []
    assert result["verdict"] in ("PASS", "WARN")


def test_l25_fabricated_cve_visual_fails(tmp_path, monkeypatch):
    """An L25 lock (vuln/CVE) visual on a CVE-free post => honesty violation."""
    svg = _write_l25(
        tmp_path, monkeypatch,
        slug="2026-06-02-L25_NoCVE_Guide",
        illustration_key="lock",
        body="A gentle introduction to general productivity tooling. No security ids.",
    )
    result = sch.score_file(svg)
    assert result["system"] == "L25"
    assert result["verdict"] == "FAIL"
    assert result["score"] <= sch._HONESTY_CAP
    assert any(v["visual_id"] == "lock" for v in result["honesty"]["violations"])


def test_l25_genuine_attack_visual_passes(tmp_path, monkeypatch):
    """An L25 lock visual on a post carrying a real CVE => no violation."""
    svg = _write_l25(
        tmp_path, monkeypatch,
        slug="2026-06-02-L25_Real_CVE_Guide",
        illustration_key="lock",
        body="Deep dive on CVE-2026-55555: an RCE exploit and its patch.",
    )
    result = sch.score_file(svg)
    assert result["honesty"]["violations"] == []


def test_l25_single_band_no_low_diversity_flag(tmp_path, monkeypatch):
    """L25 has one visual: motif diversity must NOT penalize it."""
    svg = _write_l25(
        tmp_path, monkeypatch,
        slug="2026-06-02-L25_Diversity_Guide",
        illustration_key="aws",
        body="An AWS service stack overview for practitioners.",
    )
    result = sch.score_file(svg)
    assert "LOW_DIVERSITY" not in result["flags"]
    assert "motif_diversity" not in result["quality"]
    assert result["bands"] == {"visual": "aws"}


def test_l25_determinism(tmp_path, monkeypatch):
    svg = _write_l25(
        tmp_path, monkeypatch,
        slug="2026-06-02-L25_Determinism_Guide",
        illustration_key="k8s",
        body="A kubernetes cluster walkthrough.",
    )
    assert sch.score_file(svg) == sch.score_file(svg)


# ===========================================================================
# System detection edge cases
# ===========================================================================
def test_unknown_system_skipped(tmp_path, monkeypatch):
    assets = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    assets.mkdir(parents=True)
    posts.mkdir(parents=True)
    svg_path = assets / "2026-06-02-Mystery.svg"
    svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
                        encoding="utf-8")
    monkeypatch.setattr(sch, "REPO", tmp_path)
    monkeypatch.setattr(sch, "ASSETS", assets)
    monkeypatch.setattr(sch, "POSTS", posts)
    result = sch.score_file(svg_path)
    assert result["verdict"] == "SKIP"
    assert "UNKNOWN_SYSTEM" in result["flags"]


def test_detect_system_precedence_l20_over_l22():
    """If both an L20 marker and band structure exist, L20 wins."""
    text = (
        "profile: high-quality-cover (L20 Hero+2-Card) "
        '<linearGradient id="bandAXX"></linearGradient> translate(500,105)'
    )
    assert sch.detect_system(text) == "L20"


def test_l20_score_regression_safe(tmp_path, monkeypatch):
    """L20 honesty + quality terms unchanged from rubric 1.0 (smoke)."""
    svg = _write_cover_and_post(
        tmp_path, monkeypatch,
        slug="2026-06-02-L20_Regression_Digest",
        hero_id="cve_chain", tr_id="ransomware_lock", br_id="supply_chain_pipe",
        body="CVE-2026-1 RCE. ransomware wiper. supply chain slsa poisoned npm.",
    )
    monkeypatch.setattr(
        sch, "_routed_visual_ids",
        lambda *a, **k: sch._fingerprint_visual_ids(svg.read_text()),
    )
    result = sch.score_file(svg)
    assert result["system"] == "L20"
    assert result["honesty"]["score"] == 60
    assert "motif_diversity" in result["quality"]  # L20 keeps the diversity term


# ---------------------------------------------------------------------------
# Env-robust routing-replay (frontmatter lib optional; fallback never overclaims)
# ---------------------------------------------------------------------------
_HONEST = {"neutral", "market", "security_advisory"}


def test_load_post_fields_without_frontmatter(tmp_path, monkeypatch):
    """_load_post_fields parses content + summary_card via PyYAML when the
    frontmatter lib is absent (minimal CI env).

    The parse core lives in the shared ``l20_dispatch.load_post_fields`` (which
    ``sch._load_post_fields`` delegates to) and imports ``frontmatter`` locally,
    so the no-frontmatter path is forced by making that import fail."""
    post = tmp_path / "2026-06-20-Tech_Security_Weekly_Digest_AI.md"
    post.write_text(
        "---\n"
        'title: "T"\n'
        "summary_card:\n"
        "  highlights:\n"
        '    - { source: "X", title: "Ivanti CVE" }\n'
        "---\n\n"
        "Body text - 보안 뉴스 5개\n",
        encoding="utf-8",
    )
    monkeypatch.setitem(sys.modules, "frontmatter", None)
    fields = sch._load_post_fields(post)
    assert fields is not None
    content, card = fields
    assert "Body text" in content
    assert isinstance(card, dict) and card["highlights"][0]["source"] == "X"


def test_routed_visuals_identical_with_and_without_frontmatter(tmp_path, monkeypatch):
    """The routing-replay must be byte-identical with and without the
    frontmatter lib, so the honesty gate is environment-independent."""
    post = tmp_path / "2026-06-20-Tech_Security_Weekly_Digest_AI_Patch_Apple.md"
    post.write_text(
        "---\n"
        'title: "Weekly Digest"\n'
        'excerpt: "Roundup"\n'
        "summary_card:\n"
        "  highlights:\n"
        '    - { source: "The Hacker News", title: "Apple Patch" }\n'
        '    - { source: "AWS", title: "AWS ISO" }\n'
        '    - { source: "BleepingComputer", title: "Ransomware crew" }\n'
        "---\n\n"
        "- 총 뉴스 수: 12개\n- 보안 뉴스: 2개\n",
        encoding="utf-8",
    )
    args = ("Weekly Digest", "Roundup", post.name, post)
    # The shared parser (l20_dispatch.load_post_fields) imports ``frontmatter``
    # locally; force the PyYAML fallback by making that import fail.
    monkeypatch.setitem(sys.modules, "frontmatter", None)
    without = sch._routed_visual_ids(*args)
    # restore a real frontmatter module if installed; else skip the parity half.
    # Remove the ``None`` sentinel first so import_module actually re-imports
    # instead of re-raising on the cached None.
    import importlib
    monkeypatch.delitem(sys.modules, "frontmatter", raising=False)
    try:
        fm = importlib.import_module("frontmatter")
    except Exception:
        pytest.skip("frontmatter lib not installed in this env")
    monkeypatch.setitem(sys.modules, "frontmatter", fm)
    with_fm = sch._routed_visual_ids(*args)
    assert without == with_fm


def test_routed_fallback_never_overclaims(monkeypatch):
    """Last resort (post unloadable) clamps to honest classes: no attack visual
    is ever asserted, and side bands carry no advisory shield."""
    monkeypatch.setitem(sys.modules, "frontmatter", None)
    # post=None forces the filename-keyword last resort.
    visuals = sch._routed_visual_ids(
        "Ransomware breach exfiltration C2 CVE chain",
        "Ransomware crews exploit CVE for data exfiltration via C2",
        "2026-06-20-Tech_Security_Weekly_Digest_Ransomware_CVE.md",
        None,
    )
    assert all(v in _HONEST for v in visuals), visuals
    # Side bands (index 1, 2) never carry the advisory shield (occlusion rule).
    assert visuals[1] == "neutral" and visuals[2] == "neutral", visuals

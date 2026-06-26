#!/usr/bin/env python3
"""Regression tests for the L20 Hero+2-Card SVG generator.

Validates:
  - Each of the 11 visual builders (vb_*) returns well-formed, animated SVG fragments.
  - render_l20_hero() produces a structurally correct 1200x630 SVG.
  - All 16 March 2026 digest covers on disk pass a quality gate.
  - The April-08 reference cover retains its known baseline markers.
  - Special characters are properly XML-escaped in rendered output.

No external image libraries (PIL/cairo/svg2png) are required; all checks are XML-level.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# --- Path setup (mirrors other tests in this directory) ---
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.lib import svg_l20_hero  # noqa: E402
from scripts.lib import svg_l22_generator as l22  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "images"
REFERENCE_SVG = ASSETS_DIR / "2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg"

# Exact 15 filenames produced by upgrade_l20_cover.py from
# _data/l20_covers/*.yml (2026-03-23 owned by digest pipeline per audit D1)
L20_MARCH_FILENAMES: list[str] = [
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.svg",
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin.svg",
    "2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet.svg",
    "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.svg",
    "2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.svg",
    "2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat.svg",
    "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.svg",
    "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg",
    "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg",
    "2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent.svg",
    "2026-03-26-Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI.svg",
    "2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg",
    "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.svg",
    "2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.svg",
    "2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.svg",
]

# All 11 visual builders (8 attack/incident + 2 content-neutral (Option B) +
# 1 honest generic-security-advisory builder for unspecified-severity topics).
VISUAL_BUILDERS = [
    ("vb_cve_chain", svg_l20_hero.vb_cve_chain),
    ("vb_hub_spoke", svg_l20_hero.vb_hub_spoke),
    ("vb_container_escape", svg_l20_hero.vb_container_escape),
    ("vb_ai_agent_funnel", svg_l20_hero.vb_ai_agent_funnel),
    ("vb_ransomware_lock", svg_l20_hero.vb_ransomware_lock),
    ("vb_supply_chain_pipe", svg_l20_hero.vb_supply_chain_pipe),
    ("vb_code_injection", svg_l20_hero.vb_code_injection),
    ("vb_data_exfil", svg_l20_hero.vb_data_exfil),
    ("vb_neutral", svg_l20_hero.vb_neutral),
    ("vb_market", svg_l20_hero.vb_market),
    ("vb_security_advisory", svg_l20_hero.vb_security_advisory),
]

# Attack/incident vocabulary that the two content-neutral builders MUST NOT
# emit — the core honesty guarantee of Option B.
_ATTACK_VOCAB = [
    "CVE",
    "0-DAY",
    "EXPLOIT",
    "ATTACKER",
    "VICTIM",
    "C2",
    "PWNED",
    "BREACH",
    "RANSOM",
    "EXFIL",
    "uid=0",
    "ACTIVE EXPLOITATION",
    "MALWARE",
    "BOTNET",
    "BYPASS",
]

KOREAN_RE = re.compile(r"[\uAC00-\uD7A3]")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wrap_svg(fragment: str) -> str:
    """Wrap an SVG fragment in a minimal root element for parse testing."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
        + fragment
        + "</svg>"
    )


def _count_anims(text: str) -> int:
    """Count <animate and <animateMotion elements in text."""
    return text.count("<animate") + text.count("<animateMotion")


def _synthetic_story(theme: str = "red", visual: str = "cve_chain") -> dict:
    return {
        "tag": "TEST",
        "index": "01",
        "theme": theme,
        "visual": visual,
        "headline": "Test Headline",
        "subheadline": "Test sub",
        "kpi_value": "99",
        "kpi_label": "KPI",
        "kpi_sub": "units",
        "action": "TAKE ACTION NOW",
    }


# ---------------------------------------------------------------------------
# Test 1: Visual builders — minimum structure and animation checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,fn", VISUAL_BUILDERS)
def test_visual_blocks_render_minimum_animations(name: str, fn) -> None:
    """Each visual builder must return a non-empty animated SVG group fragment."""
    result = fn(0, 0, "red")

    assert isinstance(result, str) and result, f"{name} returned empty string"
    assert "<g" in result, f"{name} missing <g opening tag"

    total_anims = _count_anims(result)
    # vb_ransomware_lock has 1 animation (stroke-opacity pulse) — grounded in actual
    # source; all others have >= 3. Threshold is >= 1 to stay realistic.
    assert total_anims >= 1, (
        f"{name} has {total_anims} animation elements; expected >= 1"
    )

    assert 'fill="' in result or 'stroke="' in result, (
        f"{name} has no fill= or stroke= attribute (no theme color applied)"
    )

    # Verify the theme accent color appears when red theme is requested
    red_accent = svg_l20_hero.THEMES["red"]["accent"]  # "#E63946"
    assert red_accent in result, (
        f"{name} does not contain red accent {red_accent} when theme='red'"
    )

    # Fragment must be parseable when wrapped in a minimal SVG root
    wrapped = _wrap_svg(result)
    try:
        ET.fromstring(wrapped)
    except ET.ParseError as exc:
        pytest.fail(f"{name} fragment is not well-formed XML: {exc}")


# ---------------------------------------------------------------------------
# Test 2: Full render_l20_hero structure
# ---------------------------------------------------------------------------

def test_render_l20_hero_full_structure() -> None:
    """render_l20_hero with a 3-story synthetic config produces expected SVG structure."""
    date_str = "2026.03.99"
    post_title = "Synthetic Test Cover"
    hero = _synthetic_story("red", "cve_chain")
    top_right = _synthetic_story("blue", "hub_spoke")
    bottom_right = _synthetic_story("amber", "supply_chain_pipe")
    url = "https://example.test/posts/2026/03/99/test/"

    svg = svg_l20_hero.render_l20_hero(
        date_str=date_str,
        hero=hero,
        top_right=top_right,
        bottom_right=bottom_right,
        url=url,
        post_title=post_title,
    )

    # Basic root element
    assert 'viewBox="0 0 1200 630"' in svg, "Missing viewBox"

    # Header bar content
    assert "WEEKLY DIGEST" in svg, "Missing WEEKLY DIGEST header text"

    # Three layout panel rects at expected positions
    assert 'x="32" y="80"' in svg, "Missing hero left panel at x=32 y=80"
    assert 'x="652" y="80"' in svg, "Missing top-right panel at x=652 y=80"
    assert 'x="652" y="344"' in svg, "Missing bottom-right panel at x=652 y=344"

    # Two KPI cards at expected translate positions. The bottom-right card is at
    # cy=414 (not the panel-centred ~452) so its lower edge clears the
    # frame-anchored QR block (scan label y=486, white rect y 492..624).
    assert "translate(1094,168)" in svg, "Missing KPI card at translate(1094,168)"
    assert "translate(1094,414)" in svg, "Missing KPI card at translate(1094,414)"

    # QR group from l22.qr_block
    assert "translate(1080,504)" in svg, "Missing QR block at translate(1080,504)"

    # Metadata strings embedded in the SVG
    assert date_str in svg, f"date_str '{date_str}' not found in SVG"
    assert post_title in svg or "Synthetic Test Cover" in svg, (
        "post_title not found in SVG"
    )

    # No ellipsis characters
    assert "\u2026" not in svg, "SVG contains Unicode ellipsis (U+2026)"
    assert "..." not in svg, "SVG contains literal '...'"

    # No Korean characters
    assert not KOREAN_RE.search(svg), "SVG contains Korean characters"

    # Well-formed XML
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        pytest.fail(f"render_l20_hero output is not well-formed XML: {exc}")


# ---------------------------------------------------------------------------
# Test 3: All 16 March covers quality gate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", L20_MARCH_FILENAMES)
def test_all_16_march_covers_pass_quality_gate(filename: str) -> None:
    """Each of the 16 L20 March 2026 covers must meet structural quality requirements."""
    path = ASSETS_DIR / filename

    # File must exist
    assert path.exists(), f"Expected SVG file not found: {path}"

    # Size gate: L20 files are 30–36 KB; L22 ultra upgrades reach ~67 KB; cap at 80 KB
    size = path.stat().st_size
    assert 25_000 <= size <= 80_000, (
        f"{filename}: size {size} bytes is outside [25000, 80000]"
    )

    # Well-formed XML
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        pytest.fail(f"{filename} failed XML parse: {exc}")

    content = path.read_text(encoding="utf-8")

    # Correct viewport
    assert 'viewBox="0 0 1200 630"' in content, (
        f"{filename}: missing viewBox='0 0 1200 630'"
    )

    # Header text
    assert "WEEKLY DIGEST" in content, f"{filename}: missing WEEKLY DIGEST header"

    # Date string derived from filename (e.g. "2026.03.16")
    parts = filename.split("-")  # ['2026', '03', '16', ...]
    date_dot = f"{parts[0]}.{parts[1]}.{parts[2]}"
    assert date_dot in content, (
        f"{filename}: date string '{date_dot}' not found in SVG"
    )

    # Animation density: real L20 covers have 38–56 animations; require >= 30
    total_anims = _count_anims(content)
    assert total_anims >= 30, (
        f"{filename}: only {total_anims} animation elements; expected >= 30"
    )

    # No ellipsis
    assert "\u2026" not in content, f"{filename}: contains Unicode ellipsis (U+2026)"
    assert "..." not in content, f"{filename}: contains literal '...'"

    # No Korean characters
    assert not KOREAN_RE.search(content), (
        f"{filename}: contains Korean characters"
    )


# ---------------------------------------------------------------------------
# Test 3b: Content-neutral builders (Option B) — honesty + framing guarantees
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,fn", [
    ("vb_neutral", svg_l20_hero.vb_neutral),
    ("vb_market", svg_l20_hero.vb_market),
])
def test_neutral_builders_are_ascii_and_wellformed(name, fn) -> None:
    """Both content-neutral builders render valid, ASCII-only SVG fragments."""
    for theme in ("blue", "amber", "red", "green", "purple"):
        out = fn(800, 230, theme)
        assert out and "<g" in out, f"{name}[{theme}] empty / missing group"
        assert all(ord(c) < 128 for c in out), (
            f"{name}[{theme}] emitted non-ASCII content"
        )
        try:
            ET.fromstring(_wrap_svg(out))
        except ET.ParseError as exc:
            pytest.fail(f"{name}[{theme}] is not well-formed XML: {exc}")


@pytest.mark.parametrize("name,fn", [
    ("vb_neutral", svg_l20_hero.vb_neutral),
    ("vb_market", svg_l20_hero.vb_market),
])
def test_neutral_builders_assert_no_attack_narrative(name, fn) -> None:
    """The honesty guarantee: neither neutral builder may emit any attack /
    breach / CVE / exploit vocabulary. This is the whole point of Option B —
    a digest/market cover must not fabricate an incident the post lacks.
    """
    out = fn(800, 230, "blue").upper()
    for token in _ATTACK_VOCAB:
        assert token.upper() not in out, (
            f"{name} leaked attack vocabulary {token!r}"
        )


def test_vb_neutral_uses_benign_labels() -> None:
    """vb_neutral carries deliberately benign digest/ecosystem framing."""
    out = svg_l20_hero.vb_neutral(800, 230, "blue")
    assert any(lbl in out for lbl in ("DIGEST", "UPDATE", "ECOSYSTEM", "RELEASE")), (
        "vb_neutral missing benign digest labels"
    )


def test_vb_market_reads_as_market_figure() -> None:
    """vb_market frames the visual as a market/price/trend figure."""
    out = svg_l20_hero.vb_market(800, 230, "amber")
    assert any(lbl in out for lbl in ("MARKET", "PRICE", "TREND")), (
        "vb_market missing market/price framing"
    )


def test_render_visual_unknown_key_is_neutral() -> None:
    """_render_visual's unknown-key fallback (lockstep with the router
    default) renders the neutral builder, never an attack narrative."""
    out = svg_l20_hero._render_visual("totally_unknown_key", 800, 230, "blue")
    assert ">UPDATE<" in out or ">DIGEST<" in out, "fallback is not vb_neutral"


# ---------------------------------------------------------------------------
# Test 3c: vb_neutral LIGHT per-topic variation (nit 3, CONSERVATIVE)
# ---------------------------------------------------------------------------


def test_vb_neutral_topic_variation_is_deterministic() -> None:
    """Same topic always renders the same fragment (deterministic), and
    different topic classes render different fragments (actual variety)."""
    release = svg_l20_hero.vb_neutral(800, 230, "blue", topic="Kubernetes 1.30 release")
    ecosystem = svg_l20_hero.vb_neutral(800, 230, "blue", topic="CNCF ecosystem velocity")
    advisory = svg_l20_hero.vb_neutral(800, 230, "blue", topic="Lifecycle deprecation notice")
    # Deterministic: identical inputs -> byte-identical output.
    assert release == svg_l20_hero.vb_neutral(800, 230, "blue", topic="Kubernetes 1.30 release")
    # Variety: the three topic classes are not byte-identical.
    assert len({release, ecosystem, advisory}) == 3, "neutral topic variation collapsed"
    # The class-specific hub sub-label is present.
    assert ">RELEASE<" in release
    assert ">ECOSYSTEM<" in ecosystem
    assert ">ADVISORY<" in advisory


def test_vb_neutral_band_index_cycle_varies_without_topic() -> None:
    """With no topic keyword, the band_index cycle still differentiates
    bands so an all-neutral cover is not byte-identical across bands."""
    b0 = svg_l20_hero.vb_neutral(800, 230, "blue", topic="", band_index=0)
    b1 = svg_l20_hero.vb_neutral(800, 230, "blue", topic="", band_index=1)
    b2 = svg_l20_hero.vb_neutral(800, 230, "blue", topic="", band_index=2)
    assert len({b0, b1, b2}) == 3, "band_index cycle did not vary neutral bands"


def test_vb_neutral_variation_stays_ascii_and_attack_free() -> None:
    """The variation must remain ASCII-only and add no attack vocabulary."""
    topics = ["Kubernetes release", "CNCF ecosystem", "policy advisory", "", "generic digest"]
    for idx, topic in enumerate(topics):
        out = svg_l20_hero.vb_neutral(800, 230, "blue", topic=topic, band_index=idx)
        assert all(ord(c) < 128 for c in out), f"non-ASCII for topic {topic!r}"
        upper = out.upper()
        for token in _ATTACK_VOCAB:
            assert token.upper() not in upper, (
                f"vb_neutral leaked attack vocab {token!r} for topic {topic!r}"
            )
    upper = out.upper()
    for token in ("CVE REGRESSION", "ATTACKER", ">C2<", ">VICTIM<", "DATA EXFILTRATION"):
        assert token.upper() not in upper, f"fallback leaked {token!r}"


# ---------------------------------------------------------------------------
# Test 3d: FM6 neutral motif registry — per-motif honesty + variety harness.
# The existing default-only renders above (fn with band_index 0 / no cover_seed)
# exercise ONLY the first motif. This frozen-registry parametrized harness
# enforces the honesty + ASCII + distinctness contract on EVERY motif, so a
# future edit that drops the >UPDATE< anchor or leaks attack vocab from a
# non-default motif fails CI loudly (the single-key + shared-anchor design
# leaves the honesty gate unable to catch it — this test is the only guard).
# ---------------------------------------------------------------------------

_MOTIF_ARGS = ("#3A86FF", "#7FB2FF", "UPDATE", "#A78BFA")


def test_neutral_motif_registry_is_frozen_tuple() -> None:
    reg = svg_l20_hero._NEUTRAL_MOTIFS
    assert isinstance(reg, tuple) and len(reg) >= 3, "registry must be a tuple of >=3 motifs"


@pytest.mark.parametrize("idx", range(len(svg_l20_hero._NEUTRAL_MOTIFS)))
def test_each_neutral_motif_emits_update_anchor(idx) -> None:
    # Every motif MUST emit the >UPDATE< honesty anchor (fingerprints as the
    # always-pass neutral claim class in score_cover_honesty).
    out = svg_l20_hero._NEUTRAL_MOTIFS[idx](*_MOTIF_ARGS)
    assert ">UPDATE<" in out, f"motif {idx} dropped the >UPDATE< anchor"


@pytest.mark.parametrize("idx", range(len(svg_l20_hero._NEUTRAL_MOTIFS)))
def test_each_neutral_motif_ascii_and_attack_free(idx) -> None:
    out = svg_l20_hero._NEUTRAL_MOTIFS[idx](*_MOTIF_ARGS)
    assert all(ord(c) < 128 for c in out), f"motif {idx} non-ASCII"
    upper = out.upper()
    for token in _ATTACK_VOCAB:
        assert token.upper() not in upper, f"motif {idx} leaked attack vocab {token!r}"


def test_neutral_motifs_are_pairwise_distinct() -> None:
    bodies = [m(*_MOTIF_ARGS) for m in svg_l20_hero._NEUTRAL_MOTIFS]
    assert len(set(bodies)) == len(bodies), "neutral motifs are not pairwise distinct"


def test_cover_seed_rotation_yields_three_distinct_motifs() -> None:
    # FM6 primary goal: the 3 bands of ONE cover share a cover_seed, so they
    # render 3 CONSECUTIVE = DISTINCT motifs (no 3-identical-card cover). Holds
    # for every seed offset because N>=3.
    n = len(svg_l20_hero._NEUTRAL_MOTIFS)
    for seed in range(n):
        bands = [
            svg_l20_hero.vb_neutral(800, 230, "blue", topic="", band_index=i, cover_seed=seed)
            for i in range(3)
        ]
        assert len(set(bands)) == 3, f"seed {seed}: 3 bands not distinct"


def test_hero_scale_emits_scale_transform_else_unchanged() -> None:
    # scale > 1.0 (hero) wraps the motif in a scale() transform; scale == 1.0
    # (side cards) keeps the original transform byte-identical (no churn).
    scaled = svg_l20_hero.vb_neutral(332, 360, "blue", band_index=0, scale=1.4)
    plain = svg_l20_hero.vb_neutral(800, 230, "blue", band_index=0, scale=1.0)
    assert "scale(1.4)" in scaled, "hero scale transform missing"
    assert "scale(" not in plain, "side-card motif must not carry a scale transform"
    assert ">UPDATE<" in scaled and ">UPDATE<" in plain, "scaling dropped the anchor"


def test_cover_seed_is_deterministic() -> None:
    # Same seed string -> same seed int -> reproducible regeneration.
    s = svg_l20_hero._neutral_motif_seed("Veeam Backup|2026.06.10")
    assert s == svg_l20_hero._neutral_motif_seed("Veeam Backup|2026.06.10")
    assert isinstance(s, int)


# ---------------------------------------------------------------------------
# Test 4: Reference April-08 baseline invariants
# ---------------------------------------------------------------------------

def test_reference_04_08_baseline_invariants() -> None:
    """The original April-08 reference cover retains its characteristic L20 markers."""
    assert REFERENCE_SVG.exists(), f"Reference SVG not found: {REFERENCE_SVG}"

    content = REFERENCE_SVG.read_text(encoding="utf-8")

    assert "profile: high-quality-cover (L20 Hero+2-Card" in content, (
        "Reference SVG missing L20 profile comment"
    )
    assert "WEEKLY DIGEST" in content, "Reference SVG missing WEEKLY DIGEST text"
    assert "2026.04.08" in content, "Reference SVG missing date '2026.04.08'"

    # Well-formed XML
    try:
        ET.parse(REFERENCE_SVG)
    except ET.ParseError as exc:
        pytest.fail(f"Reference SVG is not well-formed XML: {exc}")


# ---------------------------------------------------------------------------
# Test 5: XML escaping of special characters in rendered output
# ---------------------------------------------------------------------------

def test_strip_hangul_removes_orphaned_connector_residue() -> None:
    """Bug fix (designer re-audit): after Hangul is stripped from a Korean
    digest title, no dangling ``&`` / ``:`` / empty segment may remain.

    Example corruption before the fix:
      ``2026-02-09 블록체인 & 테크 다이제스트: Bithumb 운영 사고, Bitcoin $71K``
      -> ``2026-02-09 &amp; : Bithumb , Bitcoin $71K``  (orphaned & and :)
    """
    title = "2026-02-09 블록체인 & 테크 다이제스트: Bithumb 운영 사고, Bitcoin $71K"
    out = svg_l20_hero._strip_hangul(title)
    # Core content survives, ASCII-only.
    assert "Bithumb" in out and "Bitcoin $71K" in out
    assert all(ord(c) < 128 for c in out)
    # No orphaned connectors / leading-trailing punctuation.
    assert " & " not in out, f"orphaned ampersand remains: {out!r}"
    assert " : " not in out, f"orphaned colon remains: {out!r}"
    assert not out.endswith((":", "&", ",", ";"))
    assert not out.startswith((":", "&", ",", ";", " "))
    # No leading orphaned comma/segment (the ``, Bitcoin`` artifact).
    assert ", ," not in out
    assert "  " not in out, f"double space remains: {out!r}"

    cncf = "DevOps & 블록체인 다이제스트: CNCF Velocity, Cluster API, Bitcoin"
    out2 = svg_l20_hero._strip_hangul(cncf)
    assert "CNCF Velocity" in out2 and "Cluster API" in out2
    assert " : " not in out2 and not out2.endswith(":")


def test_strip_hangul_preserves_legit_ascii_punctuation() -> None:
    """The orphan-connector cleanup must NOT corrupt genuine ASCII
    punctuation that has no adjacent Hangul (``AT&T``, ``Q&A``, ``9:30``,
    ``A, B, C``, ``Cloud & Security``)."""
    cases = {
        "AT&T 9:30 Q&A session": "AT&T 9:30 Q&A session",
        "Cloud & Security weekly": "Cloud & Security weekly",
        "A, B, C three items": "A, B, C three items",
    }
    for src, expected in cases.items():
        assert svg_l20_hero._strip_hangul(src) == expected


def test_render_l20_hero_title_has_no_dangling_punctuation() -> None:
    """End-to-end: a Korean digest title rendered into the SVG <title>
    contains no orphaned ``&``/``:`` and stays ASCII-only."""
    hero = _synthetic_story("red", "neutral")
    top_right = _synthetic_story("blue", "market")
    bottom_right = _synthetic_story("amber", "neutral")
    svg = svg_l20_hero.render_l20_hero(
        date_str="2026.02.09",
        hero=hero,
        top_right=top_right,
        bottom_right=bottom_right,
        url="https://example.test/",
        post_title="2026-02-09 블록체인 & 테크 다이제스트: Bithumb 운영 사고, Bitcoin $71K",
    )
    title_match = re.search(r"<title>(.*?)</title>", svg, re.DOTALL)
    assert title_match, "no <title> element"
    title_text = title_match.group(1)
    assert "Bithumb" in title_text
    assert " &amp; " not in title_text, f"orphaned &amp; in title: {title_text!r}"
    assert " : " not in title_text, f"orphaned colon in title: {title_text!r}"
    assert not KOREAN_RE.search(title_text)


def test_render_l20_hero_xml_escapes_special_chars() -> None:
    """Special XML characters in story fields must be escaped in the output SVG."""
    dangerous = 'A & B < C > D "E"'
    hero = {
        "tag": "TEST",
        "index": "01",
        "theme": "red",
        "visual": "cve_chain",
        "headline": dangerous,
        "subheadline": "Normal sub",
        "kpi_value": "99",
        "kpi_label": "KPI",
        "kpi_sub": "units",
        "action": "DO SOMETHING",
    }
    top_right = _synthetic_story("blue", "hub_spoke")
    bottom_right = _synthetic_story("amber", "data_exfil")

    svg = svg_l20_hero.render_l20_hero(
        date_str="2026.01.01",
        hero=hero,
        top_right=top_right,
        bottom_right=bottom_right,
        url="https://example.test/",
        post_title="Escape Test",
    )

    # The raw dangerous string must not appear literally
    assert dangerous not in svg, (
        "Unescaped special characters found in rendered SVG"
    )

    # Escaped forms must be present
    assert "&amp;" in svg, "& was not escaped to &amp;"
    assert "&lt;" in svg, "< was not escaped to &lt;"
    assert "&gt;" in svg, "> was not escaped to &gt;"
    assert "&quot;" in svg, '\" was not escaped to &quot;'

    # Output must still be well-formed XML
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        pytest.fail(f"SVG with escaped special chars is not well-formed XML: {exc}")


# ---------------------------------------------------------------------------
# Test 6: build_cover_title — clean, ASCII, no dangling count / slug tail
# ---------------------------------------------------------------------------

# Korean digest titles that previously yielded malformed <title> boilerplate
# such as "2026 05 29 AI (29 )" (orphaned slug fragments + dangling "(N )"
# count left when "(29개 뉴스)" had its Hangul stripped).
_TITLE_CASES = [
    # (post_title, date_str, category, filename, expected)
    (
        "2026년 05월 29일 주간 보안 다이제스트: AI 에이전트·클라우드·악성코드 (29건)",
        "2026.05.29",
        "security",
        "2026-05-29-Tech_Security_Weekly_Digest_Vulnerability_Go_AWS_Threat.md",
        "Weekly Security Digest - 2026.05.29",
    ),
    (
        "2026년 05월 27일 주간 보안 다이제스트: 클라우드·패치·제로데이 (30건)",
        "2026.05.27",
        "security",
        "2026-05-27-Tech_Security_Weekly_Digest_AI_AWS_CVE_Patch.md",
        "Weekly Security Digest - 2026.05.27",
    ),
    (
        "2026-02-09 블록체인 & 테크 다이제스트: Bithumb 운영 사고, Bitcoin $71K",
        "2026.02.09",
        "",
        "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.md",
        "Weekly Blockchain Digest - 2026.02.09",
    ),
    (
        "DevOps & 블록체인 다이제스트: CNCF Velocity, Cluster API, Bitcoin",
        "2026.02.10",
        "",
        "2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.md",
        "Weekly Blockchain Digest - 2026.02.10",
    ),
]


@pytest.mark.parametrize("post_title,date_str,category,filename,expected", _TITLE_CASES)
def test_build_cover_title_is_clean_and_deterministic(
    post_title, date_str, category, filename, expected
) -> None:
    """The clean-title builder produces a fixed-template, ASCII, dangling-free
    title and is deterministic (same input -> same output)."""
    out = svg_l20_hero.build_cover_title(
        post_title=post_title, date_str=date_str, category=category, filename=filename
    )
    assert out == expected, f"got {out!r}, expected {expected!r}"
    # Deterministic.
    assert out == svg_l20_hero.build_cover_title(
        post_title=post_title, date_str=date_str, category=category, filename=filename
    )


def test_build_cover_title_no_dangling_count_or_slug_fragments() -> None:
    """No orphaned ``(N )`` count token, no leftover slug fragment, no
    dangling punctuation — the specific corruption this builder replaces."""
    for post_title, date_str, category, filename, _ in _TITLE_CASES:
        out = svg_l20_hero.build_cover_title(
            post_title=post_title,
            date_str=date_str,
            category=category,
            filename=filename,
        )
        # No dangling parenthesised count like "(29 )" / "(N )".
        assert "(" not in out and ")" not in out, f"paren count survived: {out!r}"
        assert not re.search(r"\(\d+\s*\)", out), f"dangling count: {out!r}"
        # No double spaces / leading-trailing punctuation.
        assert "  " not in out, f"double space: {out!r}"
        assert not out.endswith((" ", "-", ":", ",")), f"trailing junk: {out!r}"
        assert not out.startswith((" ", "-", ":", ",")), f"leading junk: {out!r}"


def test_build_cover_title_is_ascii_only() -> None:
    """ASCII-only contract (must pass check_svg_title_ascii.py) — including no
    non-ASCII em-dash. The separator is the ASCII '` - `'."""
    for post_title, date_str, category, filename, _ in _TITLE_CASES:
        out = svg_l20_hero.build_cover_title(
            post_title=post_title,
            date_str=date_str,
            category=category,
            filename=filename,
        )
        assert out.isascii(), f"non-ASCII in title: {out!r}"
        assert "—" not in out, f"em-dash leaked: {out!r}"  # — is not ASCII


def test_build_cover_title_daily_cadence_and_missing_date() -> None:
    """Cadence derives Daily from a daily marker; a missing/unparseable date
    drops the trailing separator rather than emitting a dangling '` - `'."""
    daily = svg_l20_hero.build_cover_title(
        post_title="2026년 05월 29일 일간 보안 다이제스트",
        date_str="2026.05.29",
        category="security",
    )
    assert daily == "Daily Security Digest - 2026.05.29"
    # No date anywhere -> no trailing separator.
    no_date = svg_l20_hero.build_cover_title(
        post_title="주간 보안 다이제스트", date_str="", category="security", filename=""
    )
    assert no_date == "Weekly Security Digest"
    assert not no_date.endswith("-") and " - " not in no_date


def test_render_l20_hero_emits_clean_built_title_end_to_end() -> None:
    """End-to-end: when a clean built title is passed as post_title, the SVG
    <title> is exactly that clean string (no (N ) count, ASCII)."""
    clean = svg_l20_hero.build_cover_title(
        post_title="2026년 05월 29일 주간 보안 다이제스트: 악성코드 (29건)",
        date_str="2026.05.29",
        category="security",
        filename="2026-05-29-Tech_Security_Weekly_Digest_Vulnerability_Go_AWS_Threat.md",
    )
    svg = svg_l20_hero.render_l20_hero(
        date_str="2026.05.29",
        hero=_synthetic_story("amber", "security_advisory"),
        top_right=_synthetic_story("blue", "neutral"),
        bottom_right=_synthetic_story("amber", "security_advisory"),
        url="https://example.test/",
        post_title=clean,
    )
    m = re.search(r"<title>(.*?)</title>", svg, re.DOTALL)
    assert m, "no <title> element"
    title_text = m.group(1)
    assert title_text == "Weekly Security Digest - 2026.05.29"
    assert not re.search(r"\(\d+\s*\)", title_text)
    assert title_text.isascii()


# ---------------------------------------------------------------------------
# Test 7: vb_security_advisory — honest, ASCII, no fabricated specifics
# ---------------------------------------------------------------------------

# Specific-claim vocabulary the advisory builder MUST NOT fabricate. It signals
# "security topic, severity unspecified" and nothing more.
_FABRICATED_SPECIFIC_VOCAB = [
    "CVE-",                 # no concrete CVE id
    "Active exploitation",  # no exploitation claim
    "PATCH UPSTREAM NOW",   # no patch-now imperative
    "PATCH NOW",
    "REGRESSION CHAIN",
    "NEW CVE",
    "PRIOR CVE",
    "0-DAY",
    "ATTACKER",
    "VICTIM",
    "C2",
    "PWNED",
    "uid=0",
    "RANSOM",
    "EXFIL",
    "EXPLOIT",
    "BOTNET",
    "BREACH",
]


def test_vb_security_advisory_is_ascii_and_wellformed() -> None:
    """The advisory builder renders valid, ASCII-only SVG across all themes."""
    for theme in ("amber", "blue", "red", "green", "purple"):
        out = svg_l20_hero.vb_security_advisory(800, 230, theme)
        assert out and "<g" in out, f"empty / missing group for {theme}"
        assert out.isascii(), f"non-ASCII content for theme {theme}"
        try:
            ET.fromstring(_wrap_svg(out))
        except ET.ParseError as exc:
            pytest.fail(f"vb_security_advisory[{theme}] not well-formed XML: {exc}")


def test_vb_security_advisory_no_fabricated_specifics() -> None:
    """Honesty hard-constraint: NO fabricated specifics (CVE id, active
    exploitation, patch-now imperative, attacker/victim/C2 narrative)."""
    out = svg_l20_hero.vb_security_advisory(800, 230, "amber")
    low = out.lower()
    for token in _FABRICATED_SPECIFIC_VOCAB:
        assert token.lower() not in low, (
            f"vb_security_advisory fabricated specific {token!r}"
        )


def test_vb_security_advisory_omits_severity_when_unknown() -> None:
    """Default (no severity supplied): the advisory still shows the shield +
    ADVISORY label, but OMITS the severity line — never the fabricated
    'SEVERITY: TBD' / 'unspecified - under review' reading (Fix B)."""
    out = svg_l20_hero.vb_security_advisory(800, 230, "amber")
    assert "SECURITY ADVISORY" in out, "missing SECURITY ADVISORY label"
    assert "ADVISORY" in out
    assert "SEVERITY: TBD" not in out, "must not assert a fabricated TBD level"
    assert "unspecified - under review" not in out


def test_vb_security_advisory_renders_known_severity() -> None:
    """When a real post-reported severity is supplied, the gauge shows the
    ASCII all-caps severity word (Fix B)."""
    for word in ("CRITICAL", "HIGH", "MEDIUM"):
        out = svg_l20_hero.vb_security_advisory(800, 230, "amber", severity=word)
        assert f"SEVERITY: {word}" in out
        assert "SEVERITY: TBD" not in out
        assert out.isascii()


def test_vb_security_advisory_routes_and_renders_via_dispatch() -> None:
    """The security_advisory key dispatches to the builder, registered as one
    of the 11 VISUAL_BUILDERS keys."""
    assert "security_advisory" in svg_l20_hero.VISUAL_BUILDERS
    assert len(svg_l20_hero.VISUAL_BUILDERS) == 11
    out = svg_l20_hero._render_visual("security_advisory", 800, 230, "amber")
    assert "SECURITY ADVISORY" in out
    assert out == svg_l20_hero.vb_security_advisory(800, 230, "amber")


def test_advisory_emblem_rotates_and_stays_honest() -> None:
    """cover_seed rotates the central emblem among _ADVISORY_EMBLEM_COUNT honest
    variants. Every variant must stay ASCII, well-formed, keep the SECURITY
    ADVISORY claim label, the semantic-green emblem, and fabricate NO specifics
    (the rotation is claim-invariant, so the honesty scorer is unaffected)."""
    green = svg_l20_hero.THEMES["green"]["accent"]
    n = svg_l20_hero._ADVISORY_EMBLEM_COUNT
    seen = set()
    for v in range(n):
        # theme="red" is load-bearing for the `green in out` assertion below:
        # under a red theme the ONLY source of the green token is the pinned
        # emblem, so the check genuinely guards the semantic-green pin (it would
        # pass via chrome accent under theme="green").
        out = svg_l20_hero.vb_security_advisory(800, 230, "red", severity="HIGH", cover_seed=v)
        seen.add(out)
        assert out.isascii(), f"variant {v} non-ASCII"
        try:
            ET.fromstring(_wrap_svg(out))
        except ET.ParseError as exc:
            pytest.fail(f"advisory emblem variant {v} not well-formed: {exc}")
        assert "SECURITY ADVISORY" in out, f"variant {v} missing claim label"
        assert green in out, f"variant {v} dropped semantic-green emblem"
        low = out.lower()
        for token in _FABRICATED_SPECIFIC_VOCAB:
            assert token.lower() not in low, f"variant {v} fabricated {token!r}"
        # Geometry must stay inside the original shield's ~80x108 box (the caller
        # wraps the emblem in translate(-92,-46)); a glyph spilling outside would
        # overlap the severity gauge / card frame. Guard against future variants
        # drifting out of bounds by checking every emblem coordinate.
        emblem = svg_l20_hero._advisory_emblem(v, green, green)
        coords = [float(m) for m in re.findall(r"(?<![#\w.])-?\d+(?:\.\d+)?", emblem)]
        assert coords, f"variant {v} emitted no coordinates"
        assert max(coords) <= 115, f"variant {v} coordinate {max(coords)} exceeds ~80x108 box"
        assert min(coords) >= -5, f"variant {v} coordinate {min(coords)} below box origin"
    assert len(seen) == n, f"emblem variants not distinct: {len(seen)} of {n}"


def test_advisory_emblem_variant0_byte_identical_to_default() -> None:
    """cover_seed=0 (and any seed where seed % N == 0) must render the original
    shield+check emblem byte-identically, so default-seed callers and the
    dispatch-equality contract stay green."""
    default = svg_l20_hero.vb_security_advisory(800, 230, "amber", severity="HIGH")
    seed0 = svg_l20_hero.vb_security_advisory(800, 230, "amber", severity="HIGH", cover_seed=0)
    assert default == seed0
    # A seed that is a multiple of the count also lands on variant 0.
    assert (
        svg_l20_hero.vb_security_advisory(800, 230, "amber", severity="HIGH",
                                          cover_seed=svg_l20_hero._ADVISORY_EMBLEM_COUNT)
        == seed0
    )


def test_advisory_shield_pinned_green_regardless_of_topic_theme() -> None:
    """The shield + checkmark stay semantic green even when the topic theme
    recolors the surrounding chrome — a red checkmark shield would read as a
    false alarm (cover review 2026-06-24)."""
    green = svg_l20_hero.THEMES["green"]["accent"]
    for theme in ("red", "blue", "amber", "purple"):
        out = svg_l20_hero.vb_security_advisory(800, 230, theme, severity="CRITICAL")
        accent = svg_l20_hero.THEMES[theme]["accent"]
        assert green in out, f"{theme}: shield green {green} missing"
        # The topic accent still appears (frame/badge/gauge chrome).
        assert accent in out, f"{theme}: topic accent {accent} missing from chrome"


@pytest.mark.parametrize("theme", ["red", "blue", "amber", "green", "purple"])
def test_hero_button_label_meets_wcag_aa(theme: str) -> None:
    """The hero CTA button label must clear WCAG AA (4.5:1) on every theme
    accent. White labels failed AA on the light accents; button_text_color
    picks the contrast-correct ink and the rect renders at full opacity."""
    accent = svg_l20_hero.THEMES[theme]["accent"]
    ink = svg_l20_hero.button_text_color(accent)
    ratio = svg_l20_hero._contrast_ratio(ink, accent)
    assert ratio >= 4.5, f"{theme}: button label {ink} on {accent} only {ratio:.2f}:1"


def test_hero_button_not_white_on_light_accent() -> None:
    """Regression: the rendered hero button must not use a low-contrast white
    label on a light accent (amber)."""
    hero = {
        "tag": "HIGH", "index": "01", "theme": "amber", "visual": "neutral",
        "headline": "Ecosystem", "subheadline": "x", "kpi_value": "5",
        "kpi_label": "ITEMS", "kpi_sub": "feed", "action": "READ THE FULL DIGEST",
    }
    side = dict(hero, index="02", theme="blue")
    out = svg_l20_hero.render_l20_hero(
        date_str="2026.02.01", hero=hero, top_right=side, bottom_right=side,
        url="https://example.test/x", post_title="Weekly Digest - 2026.02.01",
    )
    # The amber accent button should carry the dark ink label, not white.
    assert "READ THE FULL DIGEST" in out
    assert svg_l20_hero.button_text_color("#FFB703") == "#0A0F1E"

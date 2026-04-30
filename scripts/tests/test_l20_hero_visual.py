#!/usr/bin/env python3
"""Regression tests for the L20 Hero+2-Card SVG generator.

Validates:
  - Each of the 8 visual builders (vb_*) returns well-formed, animated SVG fragments.
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

# Exact 16 filenames produced by upgrade_2026_03_16_31_to_l20_hero.py
L20_MARCH_FILENAMES: list[str] = [
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.svg",
    "2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin.svg",
    "2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet.svg",
    "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.svg",
    "2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.svg",
    "2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat.svg",
    "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.svg",
    "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg",
    "2026-03-23-Tech_Security_Weekly_Digest_Ransomware.svg",
    "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg",
    "2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent.svg",
    "2026-03-26-Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI.svg",
    "2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg",
    "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.svg",
    "2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.svg",
    "2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.svg",
]

# All 8 visual builders
VISUAL_BUILDERS = [
    ("vb_cve_chain", svg_l20_hero.vb_cve_chain),
    ("vb_hub_spoke", svg_l20_hero.vb_hub_spoke),
    ("vb_container_escape", svg_l20_hero.vb_container_escape),
    ("vb_ai_agent_funnel", svg_l20_hero.vb_ai_agent_funnel),
    ("vb_ransomware_lock", svg_l20_hero.vb_ransomware_lock),
    ("vb_supply_chain_pipe", svg_l20_hero.vb_supply_chain_pipe),
    ("vb_code_injection", svg_l20_hero.vb_code_injection),
    ("vb_data_exfil", svg_l20_hero.vb_data_exfil),
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

    # Two KPI cards at expected translate positions
    assert "translate(1094,168)" in svg, "Missing KPI card at translate(1094,168)"
    assert "translate(1094,452)" in svg, "Missing KPI card at translate(1094,452)"

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

    # Size gate: real L20 files are 30–36 KB; allow headroom up to 60 KB
    size = path.stat().st_size
    assert 25_000 <= size <= 60_000, (
        f"{filename}: size {size} bytes is outside [25000, 60000]"
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

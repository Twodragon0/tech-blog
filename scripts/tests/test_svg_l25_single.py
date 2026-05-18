#!/usr/bin/env python3
"""Tests for ``scripts/lib/svg_l25_single.py`` + ``scripts/upgrade_l25_cover.py``.

Covers: well-formed XML output, marker comment placement, enum guards,
distinguishable visual builders, deterministic byte-stable rendering,
XML escaping, YAML schema validation, write/check drift lifecycle, and
empty-spec-dir CLI behavior.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.lib import svg_l25_single as l25  # noqa: E402
from scripts.upgrade_l25_cover import (  # noqa: E402
    SPECS_DIR, check, load_spec, main, render, write,
)

MARKER = "<!-- profile: high-quality-cover (2025 upgraded L25-single) -->"


def _minimal_spec(**overrides):
    spec = {
        "date": "2026-06-01",
        "slug": "Test_Single_Topic_Post",
        "post_title": "Test Single Topic Post",
        "category": "incident",
        "theme": "red",
        "headline": "Test Headline Goes Here",
        "subheadline": "Test subheadline for the L25 single cover",
        "visual": "network_nodes",
        "tag_chips": ["TAG ONE", "TAG TWO", "TAG THREE"],
        "kpi_strip": [
            {"label": "SEVERITY", "value": "HIGH"},
            {"label": "CVSS", "value": "9.8"},
            {"label": "STATUS", "value": "ACTIVE"},
        ],
        "url": "https://tech.2twodragon.com/posts/2026/06/01/Test_Single_Topic_Post/",
    }
    spec.update(overrides)
    return spec


def _write_spec(tmp_path: Path, data: dict, name: str = "sample.yml") -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


# 1. Renderer structure -----------------------------------------------------

class TestRendererStructure:
    def test_renders_well_formed_xml(self):
        ET.fromstring(l25.render_l25_single(_minimal_spec()))

    def test_renders_1200x630_viewbox(self):
        svg = l25.render_l25_single(_minimal_spec())
        assert 'viewBox="0 0 1200 630"' in svg
        assert 'width="1200"' in svg and 'height="630"' in svg

    def test_marker_on_line_3(self):
        """The marker MUST sit on line 3 to match the 28 grandfathered SVGs."""
        lines = l25.render_l25_single(_minimal_spec()).splitlines()
        assert lines[2].strip() == MARKER, f"got: {lines[2]!r}"

    def test_has_svg_root_and_closing(self):
        svg = l25.render_l25_single(_minimal_spec())
        assert svg.lstrip().startswith("<svg") and "</svg>" in svg


# 2. Enum guards ------------------------------------------------------------

class TestEnumGuards:
    @pytest.mark.parametrize("field,bad,msg", [
        ("category", "bogus", "unknown category"),
        ("theme", "rainbow", "unknown theme"),
        ("visual", "vaporware", "unknown visual"),
    ])
    def test_rejects_bad_enum(self, field, bad, msg):
        with pytest.raises(ValueError, match=msg):
            l25.render_l25_single(_minimal_spec(**{field: bad}))

    @pytest.mark.parametrize("category", sorted(l25.CATEGORIES))
    def test_accepts_all_categories(self, category):
        l25.render_l25_single(_minimal_spec(category=category))

    @pytest.mark.parametrize("theme", sorted(l25.THEMES))
    def test_accepts_all_themes(self, theme):
        l25.render_l25_single(_minimal_spec(theme=theme))


# 3. Visual builders --------------------------------------------------------

class TestVisualBuilders:
    def test_wired_minimum_four_visuals(self):
        """Spec floor: 4 visuals; we wire 6."""
        assert len(l25.VISUAL_BUILDERS) >= 4

    @pytest.mark.parametrize("visual_id", sorted(l25.VISUAL_BUILDERS))
    def test_each_visual_renders_non_empty(self, visual_id):
        svg = l25.render_l25_single(_minimal_spec(visual=visual_id))
        # Every L20 visual primitive wraps in translate(840,290) for L25.
        assert "translate(840,290)" in svg

    def test_distinct_visuals_distinguishable(self):
        """Slice the 600 bytes after the LAST hero visual anchor — at least
        four visual_ids must produce different windows (proves they aren't
        all aliased to the same builder).

        ``rfind`` is required because the visual frame decoration also
        emits a ``translate(840,290)`` group BEFORE the actual visual
        builder; we want the last anchor, which is always the visual
        builder's own translate."""
        windows = set()
        for vid in sorted(l25.VISUAL_BUILDERS):
            svg = l25.render_l25_single(_minimal_spec(visual=vid))
            idx = svg.rfind("translate(840,290)")
            windows.add(svg[idx:idx + 600])
        assert len(windows) >= 4, f"got {len(windows)} distinct outputs"

    def test_outage_timeline_signature(self):
        """``outage_timeline`` emits 5 incident phases + BLAST RADIUS arcs
        — proves the incident-postmortem replacement for ``shield`` renders
        timeline content (not the ransomware lock the L20 shield emits)."""
        svg = l25.render_l25_single(_minimal_spec(visual="outage_timeline"))
        for token in ("DETECT", "DIAGNOSE", "MITIGATE", "RESOLVE",
                      "POSTMORTEM", "BLAST RADIUS", "GLOBAL", "ASIA"):
            assert token in svg, f"missing {token!r}"

    def test_k8s_topology_signature(self):
        """``k8s_topology`` emits the api-server hex + 6 K8s object labels
        — proves the K8s-tutorial replacement for ``network_nodes`` carries
        real cluster vocabulary (POD/SVC/NS/CRD/CM/NODE) not CROSS/VECTOR."""
        svg = l25.render_l25_single(
            _minimal_spec(category="tutorial", theme="blue",
                          visual="k8s_topology"))
        for token in ("api-server", "CONTROL PLANE", "POD", "SVC",
                      "NS", "CRD", "CM", "NODE", "single-node"):
            assert token in svg, f"missing {token!r}"


# 4. Determinism + XML escape ----------------------------------------------

class TestDeterminismAndEscape:
    def test_byte_stable(self):
        a = l25.render_l25_single(_minimal_spec())
        b = l25.render_l25_single(_minimal_spec())
        assert a == b

    def test_ampersand_escaped(self):
        svg = l25.render_l25_single(_minimal_spec(headline="AT&T outage"))
        assert "AT&amp;T" in svg
        assert ">AT&T" not in svg

    def test_lt_gt_escaped(self):
        svg = l25.render_l25_single(
            _minimal_spec(subheadline='<script>alert("x")</script>')
        )
        assert "&lt;script&gt;" in svg
        assert "<script>" not in svg


# 5. load_spec YAML validation ---------------------------------------------

class TestLoadSpec:
    def test_load_valid(self, tmp_path):
        spec = load_spec(_write_spec(tmp_path, _minimal_spec()))
        assert spec.date == "2026-06-01"
        assert spec.category == "incident" and spec.theme == "red"
        assert len(spec.tag_chips) == 3 and len(spec.kpi_strip) == 3

    def test_rejects_unknown_top_level(self, tmp_path):
        data = _minimal_spec(); data["nonsense"] = "v"
        with pytest.raises(ValueError, match="unknown top-level"):
            load_spec(_write_spec(tmp_path, data))

    def test_rejects_missing_required(self, tmp_path):
        data = _minimal_spec(); del data["headline"]
        with pytest.raises(ValueError, match="missing required"):
            load_spec(_write_spec(tmp_path, data))

    def test_rejects_bad_category(self, tmp_path):
        with pytest.raises(ValueError, match="unknown category"):
            load_spec(_write_spec(tmp_path, _minimal_spec(category="bogus")))

    def test_rejects_too_many_chips(self, tmp_path):
        data = _minimal_spec(tag_chips=["A", "B", "C", "D", "E", "F"])
        with pytest.raises(ValueError, match="tag_chips must have at most 5"):
            load_spec(_write_spec(tmp_path, data))

    def test_rejects_too_many_kpis(self, tmp_path):
        data = _minimal_spec(kpi_strip=[
            {"label": str(i), "value": str(i)} for i in range(4)
        ])
        with pytest.raises(ValueError, match="kpi_strip must have at most 3"):
            load_spec(_write_spec(tmp_path, data))

    def test_rejects_kpi_missing_value(self, tmp_path):
        data = _minimal_spec(kpi_strip=[{"label": "X"}])
        with pytest.raises(ValueError, match=r"kpi_strip\[0\]: missing"):
            load_spec(_write_spec(tmp_path, data))

    def test_omitting_url_uses_canonical(self, tmp_path):
        data = _minimal_spec(); del data["url"]
        spec = load_spec(_write_spec(tmp_path, data))
        assert spec.url == (
            "https://tech.2twodragon.com/posts/2026/06/01/"
            "Test_Single_Topic_Post/"
        )


# 6. write / check lifecycle ------------------------------------------------

@pytest.fixture
def _tmp_assets(tmp_path, monkeypatch):
    """Redirect ``upgrade_l25_cover.ASSETS`` to a tmp dir so write() lands
    safely outside the real assets/images/ tree."""
    from scripts import upgrade_l25_cover as mod
    monkeypatch.setattr(mod, "ASSETS", tmp_path)
    return tmp_path


class TestWriteCheck:
    def test_no_drift_after_write(self, _tmp_assets):
        spec = load_spec(_write_spec(_tmp_assets, _minimal_spec()))
        assert write(spec) > 0
        assert spec.output_path.exists()
        assert check(spec) is None

    def test_detects_drift(self, _tmp_assets):
        spec = load_spec(_write_spec(_tmp_assets, _minimal_spec()))
        write(spec)
        spec.output_path.write_text("<svg>tampered</svg>", encoding="utf-8")
        assert "DRIFT" in (check(spec) or "")

    def test_missing_file_is_drift(self, _tmp_assets):
        spec = load_spec(_write_spec(_tmp_assets, _minimal_spec()))
        assert "does not exist" in (check(spec) or "")

    def test_dry_run_writes_nothing(self, _tmp_assets):
        spec = load_spec(_write_spec(_tmp_assets, _minimal_spec()))
        assert write(spec, dry_run=True) == 0
        assert not spec.output_path.exists()


# 7. CLI drift gate on empty spec dir --------------------------------------

class TestCliEmptySpecDir:
    """SPECS_DIR may legitimately hold prototype YAMLs while their on-disk
    SVGs live behind a ``.preview.svg`` suffix — that's a valid pre-batch
    state. These tests redirect SPECS_DIR to a tmp dir so CLI behaviour
    on an empty directory remains exercised regardless of real-repo state."""

    @pytest.fixture
    def _empty_specs_dir(self, tmp_path, monkeypatch):
        empty = tmp_path / "l25_covers_empty"
        empty.mkdir()
        from scripts import upgrade_l25_cover as mod
        monkeypatch.setattr(mod, "SPECS_DIR", empty)
        return empty

    def test_check_empty_dir_exits_zero(self, capsys, _empty_specs_dir):
        """Empty SPECS_DIR -> --all --check exits 0 with the no-specs notice."""
        assert main(["--all", "--check"]) == 0
        assert "no specs to process" in capsys.readouterr().out

    def test_all_empty_dir_exits_zero(self, capsys, _empty_specs_dir):
        assert main(["--all"]) == 0
        assert "no specs to process" in capsys.readouterr().out

    def test_spec_dir_present(self):
        """Real SPECS_DIR always exists (forward-looking infra)."""
        assert SPECS_DIR.is_dir(), f"{SPECS_DIR} missing"

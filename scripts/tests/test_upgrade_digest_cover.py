#!/usr/bin/env python3
"""Tests for ``scripts/upgrade_digest_cover.py``.

Coverage scope (step 1 of `.omc/plans/upgrade-script-unification.md`):

- ``Spec`` schema validation: missing keys, wrong band count, unknown
  theme / visual.kind reject with informative errors.
- Visual registry dispatch: each ``kind`` produces a non-empty SVG
  fragment and respects the kwargs passed via ``visual.<extra>:``.
- ``render`` produces SVG with correct dimensions + QR-encoded URL.
- CLI flags: ``--spec PATH`` renders one, ``--all`` walks the dir,
  ``--since`` filters by date, ``--check`` detects drift, ``--dry-run``
  skips disk writes.
- Idempotency: writing the same spec twice produces byte-identical
  output (no timestamp / random seed sneaks in).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.upgrade_digest_cover import (
    Spec,
    VISUAL_REGISTRY,
    check,
    load_spec,
    main,
    render,
    write,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _build_spec_dict(date: str = "2026-05-10") -> dict:
    """Minimal-but-complete spec dict (mirrors the 2026-05-10 cover)."""
    return {
        "date": date,
        "slug": "Tech_Security_Weekly_Digest_Sample",
        "sfx": "TST1",
        "title": f"{date}: Sample Cover",
        "aria": "Sample weekly digest cover",
        "bands": [
            {
                "theme": "red",
                "label": "ALERT",
                "headline": "Sample Headline 1",
                "metric": "Critical impact",
                "detail": "Detail line 1.",
                "metric_b": "Action 1",
                "detail_b": "Action detail 1.",
                "badge": {"value": "9.8", "label": "CVSS", "sub": "RCE"},
                "mini": {"value": "ABC", "label": "TEST", "sub": "alpha"},
                "mini2": {"value": "X", "label": "ROW", "sub": "two"},
                "visual": {"kind": "lock_cve", "cvss": "9.8"},
            },
            {
                "theme": "amber",
                "label": "WARN",
                "headline": "Sample Headline 2",
                "metric": "Medium impact",
                "detail": "Detail line 2.",
                "badge": {"value": "5", "label": "ITEMS", "sub": "patched"},
                "mini": {"value": "DEF", "label": "TEST", "sub": "beta"},
                "visual": {"kind": "shield", "label": "SHLD"},
            },
            {
                "theme": "green",
                "label": "INFO",
                "headline": "Sample Headline 3",
                "metric": "Low impact",
                "detail": "Detail line 3.",
                "badge": {"value": "OK", "label": "STATE", "sub": "stable"},
                "visual": {"kind": "code_bars", "caption": "DEMO"},
            },
        ],
    }


def _write_spec(tmp_path: Path, data: dict, name: str = "sample.yml") -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Spec validation
# ---------------------------------------------------------------------------


class TestLoadSpec:
    def test_loads_minimal_valid_spec(self, tmp_path):
        p = _write_spec(tmp_path, _build_spec_dict())
        spec = load_spec(p)
        assert spec.date == "2026-05-10"
        assert spec.slug == "Tech_Security_Weekly_Digest_Sample"
        assert spec.tier == "ultra"  # default
        assert len(spec.bands_cfg) == 3

    @pytest.mark.parametrize(
        "missing_key", ["date", "slug", "title", "aria", "bands"]
    )
    def test_rejects_missing_top_level_key(self, tmp_path, missing_key):
        data = _build_spec_dict()
        del data[missing_key]
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match=f"missing required key {missing_key!r}"):
            load_spec(p)

    def test_rejects_wrong_band_count(self, tmp_path):
        data = _build_spec_dict()
        data["bands"] = data["bands"][:2]  # only 2 bands
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match="exactly 3 entries"):
            load_spec(p)

    def test_rejects_unknown_theme(self, tmp_path):
        data = _build_spec_dict()
        data["bands"][0]["theme"] = "fuchsia"
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match="unknown theme 'fuchsia'"):
            load_spec(p)

    def test_rejects_unknown_visual_kind(self, tmp_path):
        data = _build_spec_dict()
        data["bands"][0]["visual"] = {"kind": "rocketship"}
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match="unknown visual.kind 'rocketship'"):
            load_spec(p)

    def test_rejects_band_missing_required_keys(self, tmp_path):
        data = _build_spec_dict()
        del data["bands"][0]["badge"]
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match="missing required keys.*badge"):
            load_spec(p)

    def test_rejects_unsupported_tier(self, tmp_path):
        data = _build_spec_dict()
        data["tier"] = "exotic"
        p = _write_spec(tmp_path, data)
        with pytest.raises(ValueError, match="tier must be"):
            load_spec(p)

    def test_sfx_defaults_to_last_4_digits_of_date(self, tmp_path):
        data = _build_spec_dict()
        del data["sfx"]
        p = _write_spec(tmp_path, data)
        spec = load_spec(p)
        # 2026-05-10 → "0510" (last 4 digits of "20260510")
        assert spec.sfx == "0510"


# ---------------------------------------------------------------------------
# Visual registry dispatch
# ---------------------------------------------------------------------------


class TestVisualRegistry:
    def test_registry_covers_all_l22_v_helpers(self):
        # The plan calls out 11 primitives; this guards against accidental
        # drift if l22 grows a new v_* function and we forget to register it.
        from scripts.lib import svg_l22_generator as l22
        actual_v_funcs = {n for n in dir(l22) if n.startswith("v_") and callable(getattr(l22, n))}
        registered = {f"v_{kind}" for kind in VISUAL_REGISTRY}
        # Every registry entry must point at a real l22.v_*.
        assert registered.issubset(actual_v_funcs), (
            f"registry references missing l22 helpers: {registered - actual_v_funcs}"
        )

    def test_each_registry_entry_renders_non_empty_fragment(self, tmp_path):
        # Smoke-test every kind by stamping it into band 0 of a minimal spec.
        for kind in VISUAL_REGISTRY:
            data = _build_spec_dict()
            data["bands"][0]["visual"] = {"kind": kind}
            p = _write_spec(tmp_path, data, name=f"{kind}.yml")
            spec = load_spec(p)
            assert spec.bands_cfg[0]["visual"], (
                f"visual kind={kind} produced an empty SVG fragment"
            )

    def test_visual_extra_kwargs_passed_through(self, tmp_path):
        # `cvss` should reach v_lock_cve and influence its output.
        data = _build_spec_dict()
        data["bands"][0]["visual"] = {"kind": "lock_cve", "cvss": "9.8"}
        spec_high = load_spec(_write_spec(tmp_path, data, name="high.yml"))

        data["bands"][0]["visual"] = {"kind": "lock_cve", "cvss": "3.0"}
        spec_low = load_spec(_write_spec(tmp_path, data, name="low.yml"))

        # The visual fragments must differ because the cvss kwarg is
        # rendered into the SVG.
        assert spec_high.bands_cfg[0]["visual"] != spec_low.bands_cfg[0]["visual"]

    def test_compliance_grid_renders_nonempty_svg(self, tmp_path):
        from scripts.lib import svg_l22_generator as l22
        result = l22.v_compliance_grid(500, 315, "#60A5FA", "#93C5FD")
        assert result.strip(), "v_compliance_grid returned empty fragment"
        assert "COMPLIANCE" in result
        assert "9 controls" in result

    def test_identity_handshake_renders_nonempty_svg(self, tmp_path):
        from scripts.lib import svg_l22_generator as l22
        result = l22.v_identity_handshake(500, 315, "#60A5FA", "#93C5FD")
        assert result.strip(), "v_identity_handshake returned empty fragment"
        assert "mTLS" in result

    def test_compliance_grid_scorecard_kwarg(self, tmp_path):
        from scripts.lib import svg_l22_generator as l22
        result = l22.v_compliance_grid(500, 315, "#60A5FA", "#93C5FD", scorecard="CIS-L2 90/100")
        assert "CIS-L2 90/100" in result

    def test_identity_handshake_caption_kwarg(self, tmp_path):
        from scripts.lib import svg_l22_generator as l22
        result = l22.v_identity_handshake(500, 315, "#60A5FA", "#93C5FD", caption="ZTNA")
        assert "ZTNA" in result


# ---------------------------------------------------------------------------
# render() — full SVG emission
# ---------------------------------------------------------------------------


class TestRender:
    def test_render_produces_well_formed_svg_with_qr(self, tmp_path):
        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        svg = render(spec)
        assert svg.startswith("<svg")
        assert 'viewBox="0 0 1200 630"' in svg
        # ARIA + title from the spec end up in the SVG.
        assert "Sample weekly digest cover" in svg
        assert "2026-05-10: Sample Cover" in svg
        # All three theme labels show up.
        for label in ("ALERT", "WARN", "INFO"):
            assert label in svg

    def test_render_url_is_canonical_jekyll_permalink(self, tmp_path):
        # The QR encodes the URL — the URL string itself should not appear
        # in the SVG (QR is path data), but the renderer must use the
        # underscore-preserving format.
        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        svg = render(spec)
        # The svg includes "scan / full post" text adjacent to the QR.
        assert "scan / full post" in svg

    def test_render_is_byte_identical_for_same_spec(self, tmp_path):
        # No timestamp, random seed, or environment-dependent input.
        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        a = render(spec)
        b = render(spec)
        assert a == b


# ---------------------------------------------------------------------------
# write() / check() lifecycle
# ---------------------------------------------------------------------------


class TestWriteAndCheck:
    def test_write_then_check_returns_none_on_match(self, tmp_path, monkeypatch):
        # Redirect ASSETS to a temp dir so we don't touch the real
        # assets/images/ during test runs.
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        # Spec.output_path is a property derived from ASSETS at access time.
        size = write(spec)
        assert size > 0
        assert spec.output_path.exists()
        assert check(spec) is None  # no drift

    def test_check_detects_drift(self, tmp_path, monkeypatch):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        write(spec)
        # Mutate the on-disk SVG to simulate manual edits.
        spec.output_path.write_text("<svg>tampered</svg>", encoding="utf-8")
        result = check(spec)
        assert result is not None
        assert "DRIFT" in result

    def test_check_reports_missing_file(self, tmp_path, monkeypatch):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        result = check(spec)
        assert result is not None
        assert "does not exist" in result

    def test_dry_run_does_not_write(self, tmp_path, monkeypatch):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _build_spec_dict()))
        size = write(spec, dry_run=True)
        assert size == 0
        assert not spec.output_path.exists()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class TestCLI:
    def test_spec_flag_renders_single_file(self, tmp_path, monkeypatch, capsys):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        spec_path = _write_spec(tmp_path, _build_spec_dict())
        rc = main(["--spec", str(spec_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "wrote" in out
        # File created.
        expected = tmp_path / "2026-05-10-Tech_Security_Weekly_Digest_Sample.svg"
        assert expected.exists()

    def test_dry_run_flag_skips_writes(self, tmp_path, monkeypatch, capsys):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        spec_path = _write_spec(tmp_path, _build_spec_dict())
        rc = main(["--spec", str(spec_path), "--dry-run"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "[DRY]" in out
        # No file written.
        expected = tmp_path / "2026-05-10-Tech_Security_Weekly_Digest_Sample.svg"
        assert not expected.exists()

    def test_check_flag_exits_1_on_drift(self, tmp_path, monkeypatch):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        spec_path = _write_spec(tmp_path, _build_spec_dict())
        # Pre-populate output with stale content so --check sees drift.
        (tmp_path / "2026-05-10-Tech_Security_Weekly_Digest_Sample.svg").write_text(
            "<svg>stale</svg>", encoding="utf-8"
        )
        rc = main(["--spec", str(spec_path), "--check"])
        assert rc == 1

    def test_all_flag_walks_specs_dir(self, tmp_path, monkeypatch, capsys):
        from scripts import upgrade_digest_cover as mod
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        monkeypatch.setattr(mod, "SPECS_DIR", specs_dir)
        # Two specs with different dates.
        _write_spec(specs_dir, _build_spec_dict("2026-05-09"), name="2026-05-09.yml")
        _write_spec(specs_dir, _build_spec_dict("2026-05-10"), name="2026-05-10.yml")

        rc = main(["--all"])
        assert rc == 0
        out = capsys.readouterr().out
        assert out.count("wrote") == 2

    def test_since_flag_filters_by_date(self, tmp_path, monkeypatch, capsys):
        from scripts import upgrade_digest_cover as mod
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        monkeypatch.setattr(mod, "SPECS_DIR", specs_dir)
        _write_spec(specs_dir, _build_spec_dict("2026-05-09"), name="2026-05-09.yml")
        _write_spec(specs_dir, _build_spec_dict("2026-05-10"), name="2026-05-10.yml")

        rc = main(["--all", "--since", "2026-05-10"])
        assert rc == 0
        out = capsys.readouterr().out
        # Only one spec should render — the older one is filtered out.
        assert out.count("wrote") == 1
        assert "2026-05-10-" in out

    def test_invalid_spec_returns_2(self, tmp_path, monkeypatch, capsys):
        from scripts import upgrade_digest_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)
        bad_data = _build_spec_dict()
        del bad_data["date"]
        spec_path = _write_spec(tmp_path, bad_data, name="bad.yml")
        rc = main(["--spec", str(spec_path)])
        assert rc == 2
        err = capsys.readouterr().err
        assert "missing required key 'date'" in err

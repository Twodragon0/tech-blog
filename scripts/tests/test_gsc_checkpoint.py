"""Smoke tests for scripts/gsc_checkpoint.py rendering logic.

The live `gsc_inspect.py` path requires GSC_SERVICE_ACCOUNT_JSON and is
out of scope here. These tests cover the deterministic pieces: delta
calculation and markdown structure produced from a stub state dict.

API disabling and path setup are handled by conftest.py.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "gsc_checkpoint.py"
    spec = importlib.util.spec_from_file_location("gsc_checkpoint", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gsc_checkpoint = _load_module()


class TestDelta:
    def test_decrease_renders_down_arrow(self):
        assert "▼" in gsc_checkpoint._delta(65, 109)

    def test_increase_renders_up_arrow(self):
        assert "▲" in gsc_checkpoint._delta(120, 100)

    def test_unchanged_renders_neutral_arrow(self):
        assert "→" in gsc_checkpoint._delta(100, 100)

    def test_missing_baseline_returns_na(self):
        assert gsc_checkpoint._delta(65, None) == "n/a"
        assert gsc_checkpoint._delta(None, 109) == "n/a"


class TestRender:
    def _stub_state(self, *, crawled=65, discovered=88, indexed=95, inspected=194):
        return {
            "schema_version": 1,
            "generated_at": "2026-05-29T01:00:00+00:00",
            "site_url": "https://tech.2twodragon.com",
            "totals": {
                "inspected": inspected,
                "indexed": indexed,
                "discovered_not_indexed": discovered,
                "crawled_not_indexed": crawled,
                "errors": 0,
            },
        }

    def test_renders_baseline_comparison_table(self):
        out = gsc_checkpoint._render(
            checkpoint_date="2026-05-29",
            baseline_date="2026-05-22",
            baseline_crawled=109,
            baseline_discovered=162,
            state=self._stub_state(),
        )
        # Baseline + current cells present
        assert "109" in out
        assert "65" in out
        assert "162" in out
        assert "88" in out
        # Deltas computed
        assert "▼-44" in out
        assert "▼-74" in out

    def test_renders_markdown_frontmatter(self):
        out = gsc_checkpoint._render(
            checkpoint_date="2026-05-29",
            baseline_date="2026-05-22",
            baseline_crawled=109,
            baseline_discovered=162,
            state=self._stub_state(),
        )
        assert out.startswith("---\n")
        assert "name: GSC indexing recovery checkpoint — 2026-05-29" in out
        assert "type: project" in out

    def test_handles_missing_baseline_gracefully(self):
        out = gsc_checkpoint._render(
            checkpoint_date="2026-05-29",
            baseline_date="2026-05-22",
            baseline_crawled=None,
            baseline_discovered=None,
            state=self._stub_state(),
        )
        # Table still renders; baseline cells and delta cells both say "n/a"
        # so no arithmetic-derived arrow appears inside the table rows.
        assert "n/a" in out
        # Extract the table block (between the header and the next blank line)
        # and assert no arrow shows up inside it. Arrows in the static
        # "Interpretation" prose below are expected and intentional.
        table_start = out.index("| Bucket")
        table_end = out.index("\n\n", table_start)
        table_block = out[table_start:table_end]
        for arrow in ("▼", "▲", "→"):
            assert arrow not in table_block, (
                f"Unexpected arrow {arrow!r} inside the comparison table "
                f"when baselines are None:\n{table_block}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Tests for ``scripts/dev/count_dom_nodes.py``."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COUNTER_PATH = REPO_ROOT / "scripts" / "dev" / "count_dom_nodes.py"


@pytest.fixture(scope="module")
def counter_module():
    spec = importlib.util.spec_from_file_location("count_dom_nodes", COUNTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_basic_tag_counts(counter_module, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(
        "<html><body><div><p>hi</p><p>there</p></div><span>x</span></body></html>",
        encoding="utf-8",
    )
    result = counter_module.analyze_file(html)
    assert result.tags["html"] == 1
    assert result.tags["body"] == 1
    assert result.tags["div"] == 1
    assert result.tags["p"] == 2
    assert result.tags["span"] == 1
    # 1+1+1+2+1 = 6
    assert result.total == 6


def test_void_elements_do_not_increase_depth(counter_module, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(
        "<html><body><div><img src=x><br><p>x</p></div></body></html>",
        encoding="utf-8",
    )
    result = counter_module.analyze_file(html)
    # html > body > div > p   →  depth 4
    assert result.max_depth == 4
    assert result.tags["img"] == 1
    assert result.tags["br"] == 1


def test_max_depth_tracks_deepest_branch(counter_module, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(
        "<html><body><a><b><c><d><e>x</e></d></c></b></a><span>x</span></body></html>",
        encoding="utf-8",
    )
    result = counter_module.analyze_file(html)
    # html > body > a > b > c > d > e  → depth 7
    assert result.max_depth == 7


def test_main_under_threshold_returns_zero(counter_module, tmp_path, capsys):
    html = tmp_path / "small.html"
    html.write_text("<html><body><p>x</p></body></html>", encoding="utf-8")
    rc = counter_module.main([str(html)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "DOM Node Report" in captured.out
    assert "Total elements" in captured.out


def test_main_over_threshold_returns_one(counter_module, tmp_path, capsys):
    html = tmp_path / "big.html"
    body = "".join(f"<div>{i}</div>" for i in range(50))
    html.write_text(f"<html><body>{body}</body></html>", encoding="utf-8")
    rc = counter_module.main([str(html), "--threshold", "10"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Warnings (over threshold)" in captured.out


def test_main_missing_file_returns_two(counter_module, tmp_path):
    rc = counter_module.main([str(tmp_path / "missing.html")])
    assert rc == 2


def test_render_report_lists_top_tags(counter_module, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(
        "<html><body>" + "<div></div>" * 5 + "<span></span>" * 3 + "</body></html>",
        encoding="utf-8",
    )
    result = counter_module.analyze_file(html)
    report = counter_module.render_report(html, result)
    assert "`<div>` × 5" in report
    assert "`<span>` × 3" in report
    assert "Top 10 tags" in report


def test_handles_self_closing_tags(counter_module, tmp_path):
    html = tmp_path / "page.html"
    # ``<br />`` style — handle_startendtag path.
    html.write_text("<html><body><br /><br /><p>x</p></body></html>", encoding="utf-8")
    result = counter_module.analyze_file(html)
    assert result.tags["br"] == 2

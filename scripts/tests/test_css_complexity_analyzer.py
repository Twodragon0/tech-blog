"""Tests for ``scripts/dev/analyze_css_complexity.py``.

We feed synthetic CSS through the analyzer (rather than asserting against the
shipped bundle) so the suite is hermetic — small regressions in the
production stylesheet will not break these tests.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYZER_PATH = REPO_ROOT / "scripts" / "dev" / "analyze_css_complexity.py"


@pytest.fixture(scope="module")
def analyzer():
    spec = importlib.util.spec_from_file_location("analyze_css_complexity", ANALYZER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_simple_rule_counts(analyzer):
    css = """
    .alpha { color: red; }
    .beta { color: blue; }
    .alpha, .gamma { color: green; }
    """
    stats = analyzer.analyze(css)
    assert stats.rule_count == 3
    # ``.alpha, .gamma`` splits into two selectors.
    assert stats.selector_count == 4


def test_nth_pseudo_classes_are_counted(analyzer):
    css = """
    .table tr:nth-child(even) { background: gray; }
    ul li:nth-of-type(2n+1) { color: red; }
    .none { color: blue; }
    """
    stats = analyzer.analyze(css)
    assert stats.nth_count == 2
    assert stats.examples["nth"]


def test_has_selector_is_counted(analyzer):
    css = ".card:has(img.loaded) { opacity: 1; } .other { opacity: 0; }"
    stats = analyzer.analyze(css)
    assert stats.has_count == 1


def test_universal_with_descendant_combinator(analyzer):
    # Plain ``* {}`` matches our universal pattern; ``.x *`` does too.
    # ``.x *p`` would be invalid CSS so we don't worry about it.
    css = """
    * { box-sizing: border-box; }
    .container * { margin: 0; }
    .scoped { color: red; }
    """
    stats = analyzer.analyze(css)
    assert stats.universal_descendant >= 2


def test_attribute_regex_selectors(analyzer):
    css = """
    [class*="VIpgJd"] { display: none; }
    a[href^="https://"] { color: blue; }
    img[src$=".svg"] { width: 100%; }
    [data-id] { display: block; }
    """
    stats = analyzer.analyze(css)
    # First three use substring/prefix/suffix matchers; ``[data-id]`` does not.
    assert stats.attr_regex_count == 3


def test_descendant_chain_length(analyzer):
    css = ".a .b .c .d { color: red; } .e { color: blue; }"
    stats = analyzer.analyze(css)
    assert stats.longest_descendant_chain == 4


def test_specificity_calculation(analyzer):
    # ``#id .class p`` → (1, 1, 1)
    a, b, c = analyzer._count_specificity("#id .class p")
    assert (a, b, c) == (1, 1, 1)
    # Two classes → (0, 2, 0)
    a, b, c = analyzer._count_specificity(".a.b")
    assert (a, b, c) == (0, 2, 0)


def test_render_markdown_contains_required_sections(analyzer, tmp_path):
    css_file = tmp_path / "sample.css"
    css_file.write_text(".x { color: red; } .y :has(img) { color: blue; }", encoding="utf-8")
    stats = analyzer.analyze(css_file.read_text(encoding="utf-8"))
    md = analyzer.render_markdown(stats, css_file)
    assert "# CSS Complexity Report" in md
    assert "Rules" in md
    assert "Anti-pattern counts" in md
    assert ":has()" in md


def test_main_writes_to_output_file(analyzer, tmp_path, capsys):
    css_file = tmp_path / "in.css"
    css_file.write_text(".a { color: red; }", encoding="utf-8")
    out_file = tmp_path / "out.md"
    rc = analyzer.main(["--input", str(css_file), "--output", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    body = out_file.read_text(encoding="utf-8")
    assert "Rules" in body
    captured = capsys.readouterr()
    # When ``--output`` is set we don't print the report to stdout.
    assert "Rules" not in captured.out


def test_main_prints_to_stdout_when_no_output(analyzer, tmp_path, capsys):
    css_file = tmp_path / "in.css"
    css_file.write_text(".a { color: red; }", encoding="utf-8")
    rc = analyzer.main(["--input", str(css_file)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Rules" in captured.out


def test_main_returns_nonzero_for_missing_file(analyzer, tmp_path, capsys):
    rc = analyzer.main(["--input", str(tmp_path / "nope.css")])
    assert rc == 2


def test_at_rule_blocks_are_traversed(analyzer):
    # Rules nested inside ``@media`` should still be counted.
    css = """
    @media (max-width: 600px) {
      .alpha { color: red; }
      .beta { color: blue; }
    }
    .gamma { color: green; }
    """
    stats = analyzer.analyze(css)
    assert stats.rule_count == 3


def test_comments_are_stripped(analyzer):
    css = "/* this should not be a rule */ .real { color: red; }"
    stats = analyzer.analyze(css)
    assert stats.rule_count == 1

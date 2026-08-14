"""Tests for scripts/check_asset_hint_version.py.

The gate exists because five `rel="prefetch"` hints in `_includes/head.html`
pointed at versionless URLs while `_includes/footer.html` and
`_includes/mermaid.html` loaded the same files with `?v={{ site.time }}`.
Separate URLs are separate cache entries, so every post page view downloaded
~14 KB compressed that was never used.

The first draft of the gate reported "0 violations" against the still-broken
head.html. The cause is pinned by `test_nested_liquid_quotes_still_detected`:
these templates write `href="{{ "/assets/js/x.js" | relative_url }}"`, nesting
double quotes inside a double-quoted attribute, and a quote-terminated
attribute regex stops at the inner quote and captures nothing. A gate that
cannot fail on the bug it was written for is not a gate, so that case is a
required test, not an edge case.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

check_asset_hint_version = pytest.importorskip("check_asset_hint_version")

check_file = check_asset_hint_version.check_file
collect_versioned_assets = check_asset_hint_version.collect_versioned_assets
_strip_liquid = check_asset_hint_version._strip_liquid


# The exact shape that shipped: Liquid with nested double quotes.
BROKEN_HINT = (
    '<link rel="prefetch" href="{{ "/assets/js/post-page.js" | relative_url }}"'
    ' as="script">\n'
)
# The exact shape of the loader in footer.html: single quotes inside, ?v= after.
VERSIONED_LOADER = (
    "<script src=\"{{ '/assets/js/post-page.js' | relative_url }}"
    "?v={{ site.time | date: '%Y%m%d%H%M' }}\" defer></script>\n"
)


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_nested_liquid_quotes_still_detected(tmp_path):
    """The regression that made the first version of this gate useless."""
    loader = _write(tmp_path, "footer.html", VERSIONED_LOADER)
    hint = _write(tmp_path, "head.html", BROKEN_HINT)

    versioned = collect_versioned_assets([loader])
    assert "/assets/js/post-page.js" in versioned, (
        "loader with nested single quotes inside a double-quoted src was not "
        "recognized as versioned"
    )

    violations = check_file(hint, versioned)
    assert len(violations) == 1
    assert "/assets/js/post-page.js" in violations[0][1]


def test_hint_with_matching_cache_buster_passes(tmp_path):
    loader = _write(tmp_path, "footer.html", VERSIONED_LOADER)
    hint = _write(
        tmp_path,
        "head.html",
        '<link rel="prefetch" href="{{ "/assets/js/post-page.js" | relative_url }}'
        "?v={{ site.time | date: '%Y%m%d%H%M' }}\" as=\"script\">\n",
    )
    versioned = collect_versioned_assets([loader])
    assert check_file(hint, versioned) == []


def test_hint_removed_passes(tmp_path):
    """The fix actually applied to head.html: delete the hint."""
    loader = _write(tmp_path, "footer.html", VERSIONED_LOADER)
    hint = _write(tmp_path, "head.html", "<title>no hints here</title>\n")
    versioned = collect_versioned_assets([loader])
    assert check_file(hint, versioned) == []


def test_versionless_everywhere_passes(tmp_path):
    """Fonts: preload and @font-face both omit ?v=, so they agree."""
    loader = _write(
        tmp_path,
        "font-face.html",
        "@font-face { src: url('{{ \"/assets/fonts/x-tier1.woff2\" | relative_url }}')"
        " format('woff2'); }\n"
        '<link rel="preload" as="font" type="font/woff2" crossorigin'
        ' href="{{ "/assets/fonts/x-tier1.woff2" | relative_url }}">\n',
    )
    versioned = collect_versioned_assets([loader])
    assert versioned == {}
    assert check_file(loader, versioned) == []


def test_data_attribute_loader_counts_as_versioned(tmp_path):
    """footer.html loads the search bundle via data-search-src, not src."""
    loader = _write(
        tmp_path,
        "footer.html",
        "<script src=\"{{ '/assets/js/footer-runtime.js' | relative_url }}\""
        " data-search-src=\"{{ '/assets/js/main-search.js' | relative_url }}"
        "?v={{ site.time | date: '%Y%m%d%H%M' }}\" defer></script>\n",
    )
    versioned = collect_versioned_assets([loader])
    assert "/assets/js/main-search.js" in versioned
    # The unversioned sibling in the same tag must NOT be marked versioned.
    assert "/assets/js/footer-runtime.js" not in versioned


def test_unversioned_asset_hint_is_not_flagged(tmp_path):
    """No ?v= anywhere for this asset -> the hint is consistent, so no error."""
    loader = _write(
        tmp_path,
        "footer.html",
        "<script src=\"{{ '/assets/js/subscribe-float.js' | relative_url }}\""
        " defer></script>\n",
    )
    hint = _write(
        tmp_path,
        "head.html",
        '<link rel="prefetch" href="{{ "/assets/js/subscribe-float.js"'
        ' | relative_url }}" as="script">\n',
    )
    versioned = collect_versioned_assets([loader])
    assert check_file(hint, versioned) == []


def test_stylesheet_rel_is_not_a_hint(tmp_path):
    """rel="stylesheet" actually uses the asset; only hints can go unused."""
    loader = _write(
        tmp_path,
        "footer.html",
        "<script src=\"{{ '/assets/css/main.css' | relative_url }}"
        "?v={{ site.time }}\"></script>\n",
    )
    sheet = _write(
        tmp_path,
        "head.html",
        '<link rel="stylesheet" href="{{ "/assets/css/main.css" | relative_url }}">\n',
    )
    versioned = collect_versioned_assets([loader])
    assert check_file(sheet, versioned) == []


def test_line_numbers_survive_liquid_stripping(tmp_path):
    """Reported lines must match the source file, not the stripped copy."""
    loader = _write(tmp_path, "footer.html", VERSIONED_LOADER)
    hint = _write(
        tmp_path,
        "head.html",
        "<head>\n"
        "  {% comment %}\n    multi-line\n    liquid block\n  {% endcomment %}\n"
        + BROKEN_HINT,
    )
    versioned = collect_versioned_assets([loader])
    violations = check_file(hint, versioned)
    assert len(violations) == 1
    assert violations[0][0] == 6, "line number drifted after Liquid removal"


def test_strip_liquid_preserves_newline_count():
    text = '{% comment %}\na\nb\n{% endcomment %}<link rel="prefetch">'
    assert _strip_liquid(text).count("\n") == text.count("\n")


def test_repo_templates_are_clean():
    """The live invariant: the shipped templates must have no mismatch."""
    files = check_asset_hint_version._all_template_paths()
    assert files, "no templates discovered — the gate would be vacuous"
    versioned = collect_versioned_assets(files)
    offenders = {
        str(path.relative_to(REPO)): check_file(path, versioned)
        for path in files
        if check_file(path, versioned)
    }
    assert offenders == {}, f"version-mismatched resource hints: {offenders}"

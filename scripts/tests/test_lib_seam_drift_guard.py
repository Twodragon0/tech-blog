#!/usr/bin/env python3
"""CI regression guard: no NEW local front-matter parser or SVG/XML escaper
may be introduced under scripts/ (outside scripts/lib/).

Why this guard exists
----------------------
``.omc/plans/scripts-lib-seam-consolidation.md`` (Stage 0 discovery,
2026-07-13) found front-matter parsing reinvented in ~21 live local functions
and SVG/XML escaping reinvented in 6 live local functions, scattered across
``scripts/``, despite ``python-frontmatter`` already being a declared
dependency (``requirements-blogwatcher.txt``) and a canonical
``scripts/lib/svg_utils.py:escape_xml_text`` already existing. This is the
exact class of divergence that caused prior corpus-wide SVG XML-escape
regressions (memory ``feedback_svg_xml_escape``; pinned by
``test_svg_render_english_only.py``): every local ``_escape_svg_text``
variant escapes bytes differently (quote form ``&#39;`` vs untouched,
Hangul-stripping, entity-awareness), so callers silently disagree with each
other and with the canonical helper. "Just call the canonical one" is unsafe
without a byte-equivalence proof (see plan Stage 4) — but *new* reinvention
has zero excuse, since the seam already exists.

This guard does NOT migrate anything (that is plan Stage 1/2/4/5). It FREEZES
the CURRENT set of offenders as an allowlist (baseline) and fails the build
the moment a NEW local front-matter parser or SVG/XML escaper appears
anywhere under ``scripts/`` outside the designated seam (``scripts/lib/``).
New work must either (a) import ``scripts.lib`` instead of hand-rolling, or
(b) if a new instance is genuinely justified, add it to the allowlist below
in the same PR with a one-line reason in the PR description — never silently.

Detection method
----------------
AST ``FunctionDef``/``AsyncFunctionDef`` name PREFIX-matches (not merely
"contains anywhere") one of the canonical reinvention name forms enumerated
in the plan's Stage 0 discovery greps:

- front-matter: ``parse_front_matter``, ``extract_front_matter``,
  ``parse_frontmatter``, ``extract_frontmatter``, ``_parse_front_matter``,
  ``read_front_matter``, ``split_front_matter``
- escapers: ``_escape_svg_text``, ``escape_svg_text``, ``_escape_xml``,
  ``escape_xml_text``, ``_xml_escape``, ``xml_escape``

This reproduces the Stage 0 grep's matching semantics
(``def <alternative>...`` — a name *starting with* one of the forms, e.g.
``extract_frontmatter_bounds`` matches ``extract_frontmatter``) via ``ast``
instead of regex, per the plan's Stage 3 instruction to prefer ``ast`` where
feasible.

Scope: ``scripts/**/*.py`` EXCLUDING ``scripts/lib/`` (the designated seam —
consolidation destination, permitted to define these), ``scripts/tests/``
(test code, not production reinvention), and ``scripts/_archive/`` (dead
code, explicitly out of scope per the plan's guardrails).

Known gaps (deliberately NOT enforced by this guard — separate, unscoped)
--------------------------------------------------------------------------
- ``scripts/lib/svg_l22_generator.py:_xml_escape`` and
  ``scripts/lib/image_utils.py:extract_front_matter_image`` are known live
  offenders (plan Stage 0 counts them among the 6/21) but live inside the
  excluded ``scripts/lib/`` directory, so this name-drift guard does not scan
  them; their migration is tracked by plan Stage 4/5, not this guard.
- Underscore-prefixed variants outside the plan's exact alternation list
  (e.g. ``_extract_frontmatter``, ``_extract_frontmatter_and_body``,
  ``_parse_frontmatter_fields``, ``_read_front_matter``,
  ``_split_front_matter`` — found in ``check_post_quote_safety.py``,
  ``backfill_digest_commentary.py``, ``score_cover_honesty.py``,
  ``seo_diversify_excerpts.py``) and other-domain escapers
  (``_yaml_escape_dq``, ``_html_escape_quotes``, ``_js_escape``,
  ``_escape_attr``, bare ``escape_svg``) are NOT covered here — different
  naming shape and/or a different escaping domain (YAML/JS/HTML, not
  SVG/XML) not targeted by this plan. Widening scope is a separate,
  explicitly-scoped decision, not silent guard creep.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

EXCLUDED_DIRS = (
    SCRIPTS_DIR / "lib",
    SCRIPTS_DIR / "tests",
    SCRIPTS_DIR / "_archive",
)

FRONT_MATTER_PREFIXES = (
    "parse_front_matter",
    "extract_front_matter",
    "parse_frontmatter",
    "extract_frontmatter",
    "_parse_front_matter",
    "read_front_matter",
    "split_front_matter",
)

ESCAPER_PREFIXES = (
    "_escape_svg_text",
    "escape_svg_text",
    "_escape_xml",
    "escape_xml_text",
    "_xml_escape",
    "xml_escape",
)

# --- Stage-3 baseline allowlist (captured 2026-07-13) -----------------------
# Format: "relative/path/from/scripts.py:function_name". Update in the SAME
# PR as any intentional migration (remove the entry, per plan Stage 4/5) or
# intentional new instance (add it, with a reason in the PR description).
# Goal (plan Stage 5): both sets shrink to empty.
ALLOWLIST_FRONT_MATTER = frozenset(
    {
        "add_cross_references.py:parse_front_matter",
        "add_last_modified_at.py:extract_frontmatter_bounds",
        "add_missing_tags.py:parse_front_matter",
        "add_quality_sections.py:parse_front_matter",
        "backfill_digest_titles.py:parse_frontmatter",
        "build_slack_post_message.py:extract_frontmatter",
        "buttondown_notify.py:parse_frontmatter",
        "check_kst_midnight.py:_parse_front_matter",
        "check_posts.py:extract_front_matter",
        "convert_vercel_redirects_to_jekyll.py:split_front_matter",
        "draft_rollup_spec.py:parse_frontmatter",
        "fetch_tistory_images.py:parse_frontmatter",
        "fix_summary_format.py:extract_front_matter",
        "generate_digest_svgs.py:extract_front_matter",
        "generate_og_banner.py:parse_frontmatter",
        "share_sns.py:parse_frontmatter",
        "trim_front_matter.py:split_front_matter",
        "upgrade_posts_quality_batch.py:split_front_matter",
        "upgrade_svg_banners.py:parse_front_matter",
        "verify_social_images.py:extract_front_matter",
    }
)

ALLOWLIST_ESCAPERS = frozenset(
    {
        "generate_content_summary.py:_escape_svg_text",
        "generate_digest_svgs.py:_escape_xml",
        "generate_high_quality_images.py:_escape_svg_text",
        "generate_post_images.py:_escape_svg_text",
        "news/svg_generator.py:_escape_svg_text",
    }
)


def _is_excluded(directory: Path) -> bool:
    return any(directory == d or d in directory.parents for d in EXCLUDED_DIRS)


def _iter_scanned_py_files():
    for f in sorted(SCRIPTS_DIR.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        if _is_excluded(f.parent):
            continue
        yield f


def _scan() -> tuple[dict[str, str], dict[str, str]]:
    """Return ``(front_matter_offenders, escaper_offenders)``, each a
    ``{"relpath:funcname": relpath}`` map of what currently exists under the
    scanned portion of ``scripts/``."""
    fm_found: dict[str, str] = {}
    esc_found: dict[str, str] = {}
    for f in _iter_scanned_py_files():
        rel = str(f.relative_to(SCRIPTS_DIR))
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = node.name
            key = f"{rel}:{name}"
            if any(name.startswith(p) for p in FRONT_MATTER_PREFIXES):
                fm_found[key] = rel
            if any(name.startswith(p) for p in ESCAPER_PREFIXES):
                esc_found[key] = rel
    return fm_found, esc_found


class TestLibSeamDriftGuard:
    def test_scripts_dir_exists(self):
        assert SCRIPTS_DIR.is_dir(), f"{SCRIPTS_DIR} not found (repo layout moved?)"

    def test_no_new_local_front_matter_parsers(self):
        fm_found, _ = _scan()
        unexpected = sorted(set(fm_found) - ALLOWLIST_FRONT_MATTER)
        assert not unexpected, (
            "NEW local front-matter parser(s) detected outside scripts/lib/: "
            f"{unexpected}. Use scripts.lib.frontmatter (wraps "
            "python-frontmatter, already a declared dependency) instead of "
            "hand-rolling '---' splitting/parsing. If this is a deliberate, "
            "justified new local parser, add it to ALLOWLIST_FRONT_MATTER in "
            "scripts/tests/test_lib_seam_drift_guard.py in this same PR and "
            "explain why in the PR description."
        )

    def test_no_new_local_svg_xml_escapers(self):
        _, esc_found = _scan()
        unexpected = sorted(set(esc_found) - ALLOWLIST_ESCAPERS)
        assert not unexpected, (
            "NEW local SVG/XML escaper(s) detected outside scripts/lib/: "
            f"{unexpected}. This is the exact reinvention pattern that caused "
            "prior corpus-wide SVG XML-escape regressions (every local "
            "variant escapes bytes slightly differently). Use "
            "scripts.lib.svg_utils.escape_xml_text/escape_xml_attr instead. "
            "If this is a deliberate, justified new local escaper, add it to "
            "ALLOWLIST_ESCAPERS in scripts/tests/test_lib_seam_drift_guard.py "
            "in this same PR and explain why in the PR description."
        )

    def test_allowlist_entries_still_exist(self):
        """Catch allowlist rot (plan risk R6): an entry that no longer
        matches anything in the tree (migrated/renamed) must be removed, not
        left stale forever. Plan Stage 5 goal is an empty allowlist."""
        fm_found, esc_found = _scan()
        all_found = set(fm_found) | set(esc_found)
        stale = sorted((ALLOWLIST_FRONT_MATTER | ALLOWLIST_ESCAPERS) - all_found)
        assert not stale, (
            f"Allowlist entries no longer found in scripts/: {stale}. Remove "
            "them from ALLOWLIST_FRONT_MATTER / ALLOWLIST_ESCAPERS in "
            "scripts/tests/test_lib_seam_drift_guard.py — this is migration "
            "progress, not a bug, but the allowlist must shrink to match "
            "reality (plan Stage 5 goal: both sets empty)."
        )

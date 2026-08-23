#!/usr/bin/env python3
"""Policy gate: a test may skip for a missing *environment*, never for a
missing *repo artifact*.

Both classes read identically in a pytest summary — one `s` — but they mean
opposite things:

- "fontTools is not installed" / "node is not on PATH" — the runner lacks an
  optional dependency. Skipping keeps local development usable, and CI
  declares the dependency so the test runs there.
- "owning post missing" / "not on disk" / "{TARGET} not found" — the file the
  test exists to guard is gone. That is the regression, and a skip reports it
  as green.

Eleven sites of the second kind were removed in the same commit as this file
(`test_draft_rollup_spec`, `test_svg_size_gate`, `test_stats_trend_consistency`,
`test_dependabot_auto_merge_workflow`, `test_asset_hint_version`). This guard
keeps them from coming back, and is written against skip *reasons* rather than
file/line locations so it does not go stale when unrelated skips move.

`pytest.importorskip` is judged by its module argument instead: a third-party
module is an environment fact, but a first-party module under `scripts/` can
only be missing because it was deleted or renamed.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import NamedTuple

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = REPO / "scripts" / "tests"

# Reasons that describe the *environment*, so a skip is honest. Matched
# case-insensitively as a substring of the skip reason.
ALLOWED_REASON_PATTERNS: dict[str, str] = {
    r"not installed": "optional third-party dependency absent",
    r"required for ": "optional third-party dependency absent",
    r"not on path": "external CLI tool absent",
    r"not available in this environment": "external CLI tool absent",
    r"not built": "site build artifact absent (local dev without a build)",
    r"not in golden baseline": (
        "intentional ratchet: corpus grew after the golden snapshot, so new "
        "posts are out of scope for a snapshot comparison"
    ),
}

# Lower bound on how many skip sites the scanner must find in the live suite.
# A parser that silently matches nothing would otherwise report a clean pass.
# Deliberately loose: legitimate dependency skips come and go.
MIN_EXPECTED_SITES = 8


class Site(NamedTuple):
    path: str
    line: int
    kind: str  # "skip" | "skipif" | "importorskip" | "skip-marker"
    detail: str  # reason text, or module name for importorskip


def _literal_text(node: ast.AST | None) -> str | None:
    """Best-effort literal text of a reason argument.

    Handles plain strings, f-strings (interpolations become ``{}``), and
    implicit/explicit ``+`` concatenation of the two. Returns ``None`` when the
    reason is not statically readable.
    """
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                parts.append("{}")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _literal_text(node.left), _literal_text(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _kwarg(call: ast.Call, name: str) -> ast.AST | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _attr_chain(node: ast.AST) -> str:
    """``pytest.mark.skipif`` -> ``"pytest.mark.skipif"``."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def collect_sites(source: str, path: str = "<memory>") -> list[Site]:
    """Every skip-producing call in ``source``."""
    sites: list[Site] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        chain = _attr_chain(node.func)
        if not chain.startswith("pytest."):
            continue
        tail = chain.rsplit(".", 1)[-1]

        if tail == "importorskip":
            module = _literal_text(node.args[0]) if node.args else None
            sites.append(Site(path, node.lineno, "importorskip", module or ""))
        elif tail == "skipif":
            reason = _literal_text(_kwarg(node, "reason"))
            sites.append(Site(path, node.lineno, "skipif", reason or ""))
        elif tail == "skip":
            # `pytest.mark.skip(...)` disables a test outright; `pytest.skip(...)`
            # is a runtime skip. Distinguished so the message can differ.
            kind = "skip-marker" if ".mark." in chain else "skip"
            reason = _literal_text(_kwarg(node, "reason"))
            if reason is None and node.args:
                reason = _literal_text(node.args[0])
            sites.append(Site(path, node.lineno, kind, reason or ""))
    return sites


def is_first_party(module: str) -> bool:
    """True when ``module`` resolves to a file this repo owns."""
    rel = module.replace(".", "/")
    for base in (REPO / "scripts", REPO):
        if (base / f"{rel}.py").is_file() or (base / rel / "__init__.py").is_file():
            return True
    return False


def classify(site: Site) -> str | None:
    """Return a violation message, or ``None`` when the site is allowed."""
    if site.kind == "importorskip":
        if not site.detail:
            return "importorskip() with a non-literal module name is unauditable"
        if is_first_party(site.detail):
            return (
                f"importorskip({site.detail!r}) targets a first-party module. It "
                "can only fail because the file was deleted or renamed, and then "
                "the whole module skips instead of going red. Import it directly."
            )
        return None

    if site.kind == "skip-marker":
        return (
            "pytest.mark.skip disables the test unconditionally. Delete the test "
            "or fix it; a permanently skipped test is dead weight that reads green."
        )

    if not site.detail:
        return (
            "skip reason is missing or not a literal string, so the policy cannot "
            "tell an absent dependency from an absent repo artifact. Spell it out."
        )

    lowered = site.detail.lower()
    for pattern in ALLOWED_REASON_PATTERNS:
        if re.search(pattern, lowered):
            return None
    return (
        f"skip reason {site.detail!r} is not an environment fact. If the test "
        "target is missing from the repo, assert it instead — a skip reports the "
        "regression as green. If this really is an environment condition, add its "
        "phrasing to ALLOWED_REASON_PATTERNS with the rationale."
    )


def _live_sites() -> list[Site]:
    sites: list[Site] = []
    for path in sorted(TESTS_DIR.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        sites.extend(collect_sites(path.read_text(encoding="utf-8"), path.name))
    return sites


# ---------------------------------------------------------------------------
# The policy, applied to the live suite
# ---------------------------------------------------------------------------


def test_no_skip_hides_a_missing_repo_artifact() -> None:
    violations = [
        f"{s.path}:{s.line} [{s.kind}] {msg}"
        for s in _live_sites()
        if (msg := classify(s)) is not None
    ]
    assert not violations, "Skip-path policy violations:\n  " + "\n  ".join(violations)


def test_scanner_sees_the_live_suite() -> None:
    """Non-vacuity: the parser must actually be finding skip sites."""
    sites = _live_sites()
    assert len(sites) >= MIN_EXPECTED_SITES, (
        f"only {len(sites)} skip sites found across {TESTS_DIR}; expected at "
        f"least {MIN_EXPECTED_SITES}. The AST scan is probably broken, which "
        "would make the policy test above pass while checking nothing."
    )


# ---------------------------------------------------------------------------
# Non-vacuity: the classifier on synthetic sources
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "snippet",
    [
        'pytest.skip(f"owning post missing: {name}")',
        'pytest.skip("2026-04-05-Week1.svg not on disk")',
        'pytest.skip(f"{TARGET} not found")',
        'pytest.skip("Week2 rollup post missing")',
        'pytest.skip("Post file for 2026-04-12 not found")',
        "pytest.skip(reason=some_variable)",
        '@pytest.mark.skip(reason="flaky")\ndef test_x(): pass',
    ],
)
def test_banned_skips_are_flagged(snippet: str) -> None:
    sites = collect_sites(snippet)
    assert sites, f"scanner found no site in: {snippet}"
    assert all(classify(s) is not None for s in sites), (
        f"policy accepted a repo-artifact skip: {snippet}"
    )


@pytest.mark.parametrize(
    "snippet",
    [
        'pytest.skip("qrcode library not installed")',
        'pytest.skip("bundle not available in this environment")',
        'pytest.importorskip("PIL", reason="Pillow required for raster generation")',
        'pytest.importorskip("fontTools")',
        'pytest.mark.skipif(cond, reason="node is not on PATH; cannot run")',
        'pytest.mark.skipif(cond, reason="_site/assets/css/post-page.css not built")',
    ],
)
def test_environment_skips_are_allowed(snippet: str) -> None:
    sites = collect_sites(snippet)
    assert sites, f"scanner found no site in: {snippet}"
    assert all(classify(s) is None for s in sites), (
        f"policy rejected a legitimate environment skip: {snippet} -> "
        f"{[classify(s) for s in sites]}"
    )


def test_first_party_importorskip_is_flagged() -> None:
    """The exact shape removed from test_asset_hint_version.py."""
    sites = collect_sites('pytest.importorskip("check_asset_hint_version")')
    assert len(sites) == 1
    msg = classify(sites[0])
    assert msg is not None and "first-party" in msg


def test_first_party_detection_distinguishes_the_two_cases() -> None:
    assert is_first_party("check_asset_hint_version")
    assert is_first_party("news.qa_gate")
    assert not is_first_party("fontTools")
    assert not is_first_party("PIL")

#!/usr/bin/env python3
"""Resource-hint cache-buster consistency gate for Jekyll templates.

A ``<link rel="preload">`` / ``<link rel="prefetch">`` only helps if its href
is **byte-identical** to the URL the page actually requests.  The HTTP cache
keys on the full URL including the query string, so a hint pointing at::

    /assets/js/post-page.js

can never satisfy a tag that loads::

    /assets/js/post-page.js?v=202608130114

The browser downloads both.  The hint becomes pure waste — extra bytes and an
extra request competing for bandwidth with the copy the page will actually
run.

This is the bug that shipped in ``_includes/head.html`` and survived until
2026-08-14: five JS files were hinted without ``?v=`` while ``footer.html``
and ``mermaid.html`` loaded them with ``?v={{ site.time }}``.  It cost ~14 KB
compressed per post page view.  It went unnoticed because Chrome only warns
about an unused **preload**, not an unused **prefetch**, so an earlier
preload→prefetch switch silenced the console warning while leaving the URL
mismatch in place.

The rule enforced here:

    If an asset under /assets/ is referenced somewhere in the templates WITH
    a ``?v=`` cache-buster, then every resource hint pointing at that same
    asset must carry a ``?v=`` too.

Assets that are versionless everywhere (fonts, for example) are consistent by
definition and pass.  The gate does not compare the *values*, only presence —
comparing values across Liquid expressions would be brittle, and presence is
enough to catch the split-cache-entry failure.

Usage:
    python3 scripts/check_asset_hint_version.py            # default: --all
    python3 scripts/check_asset_hint_version.py --all
    python3 scripts/check_asset_hint_version.py --staged   # staged templates
    python3 scripts/check_asset_hint_version.py _includes/head.html
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = ("_includes", "_layouts")
TEMPLATE_SUFFIXES = (".html",)

# <link ... rel="preload|prefetch" ... href="..."> in any attribute order.
_LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_REL_RE = re.compile(r"""\brel\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_HREF_RE = re.compile(r"""\bhref\s*=\s*["']([^"']*)["']""", re.IGNORECASE)

# Any reference to an /assets/ file: src="...", href="...", data-*-src="...".
_ASSET_REF_RE = re.compile(
    r"""(?:src|href)\s*=\s*["']([^"']*?/assets/[^"']+?)["']""", re.IGNORECASE
)
# data-search-src="/assets/js/main-search.js?v=..." (footer.html loads the
# search bundle through an attribute, not a src=).
_DATA_SRC_RE = re.compile(
    r"""\bdata-[a-z-]*src\s*=\s*["']([^"']*?/assets/[^"']+?)["']""", re.IGNORECASE
)

HINT_RELS = {"preload", "prefetch", "modulepreload"}

# Liquid expression, possibly spanning lines: {{ ... }} or {% ... %}.
_LIQUID_RE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)
_ASSET_PATH_RE = re.compile(r"/assets/[A-Za-z0-9_./-]+")


def _strip_liquid(text: str) -> str:
    """Collapse Liquid expressions so ordinary attribute parsing works.

    Templates here write ``href="{{ "/assets/js/x.js" | relative_url }}"`` —
    double quotes nested inside a double-quoted attribute.  A quote-terminated
    attribute regex stops at the inner quote and yields an empty value, which
    is precisely why the first version of this gate reported 0 violations
    against head.html while the bug was still present.

    Each Liquid expression is replaced by the /assets/ path it contains (or by
    nothing), so the example above becomes ``href="/assets/js/x.js"``.  Newline
    count is preserved so reported line numbers still match the source file.
    """

    def _replace(match: re.Match[str]) -> str:
        body = match.group(0)
        path_match = _ASSET_PATH_RE.search(body)
        replacement = path_match.group(0) if path_match else ""
        return replacement + "\n" * body.count("\n")

    return _LIQUID_RE.sub(_replace, text)


def _normalize(url: str) -> str:
    """Reduce a Liquid-laden href to a comparable /assets/... path.

    ``{{ "/assets/js/x.js" | relative_url }}?v={{ site.time }}`` becomes
    ``/assets/js/x.js``.  Returns "" when no /assets/ path is present.
    """
    stripped = url.split("?", 1)[0]
    match = re.search(r"/assets/[A-Za-z0-9_./-]+", stripped)
    return match.group(0) if match else ""


def _has_cache_buster(url: str) -> bool:
    """True when the URL carries a ?v= query (Liquid value or literal)."""
    return bool(re.search(r"\?[^\"']*\bv=", url))


def collect_versioned_assets(files: list[Path]) -> dict[str, Path]:
    """Map /assets/... path -> first template that loads it with ?v=."""
    versioned: dict[str, Path] = {}
    for path in files:
        try:
            text = _strip_liquid(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in (_ASSET_REF_RE, _DATA_SRC_RE):
            for raw in pattern.findall(text):
                if not _has_cache_buster(raw):
                    continue
                asset = _normalize(raw)
                if asset:
                    versioned.setdefault(asset, path)
    return versioned


def check_file(path: Path, versioned: dict[str, Path]) -> list[tuple[int, str]]:
    """Return (line_no, message) for every version-mismatched resource hint."""
    try:
        text = _strip_liquid(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return []

    violations: list[tuple[int, str]] = []
    for match in _LINK_TAG_RE.finditer(text):
        tag = match.group(0)
        rel_match = _REL_RE.search(tag)
        if not rel_match:
            continue
        rels = {r.strip().lower() for r in rel_match.group(1).split()}
        if not (rels & HINT_RELS):
            continue

        href_match = _HREF_RE.search(tag)
        if not href_match:
            continue
        href = href_match.group(1)
        asset = _normalize(href)
        if not asset or asset not in versioned:
            continue
        if _has_cache_buster(href):
            continue

        line_no = text.count("\n", 0, match.start()) + 1
        loader = versioned[asset]
        loader_rel = loader.relative_to(REPO) if loader.is_relative_to(REPO) else loader
        rel_name = "/".join(sorted(rels & HINT_RELS))
        violations.append(
            (
                line_no,
                f"rel=\"{rel_name}\" href points at {asset} without a ?v= "
                f"cache-buster, but {loader_rel} loads it WITH ?v=. "
                f"The two URLs are separate cache entries, so this hint is "
                f"downloaded and never used.",
            )
        )
    return violations


def _all_template_paths() -> list[Path]:
    files: list[Path] = []
    for directory in TEMPLATE_DIRS:
        base = REPO / directory
        if not base.is_dir():
            continue
        for suffix in TEMPLATE_SUFFIXES:
            files.extend(sorted(base.rglob(f"*{suffix}")))
    return files


def _staged_template_paths() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, OSError):
        return []
    staged = []
    for name in out.split("\0"):
        if not name:
            continue
        path = REPO / name
        if path.suffix.lower() in TEMPLATE_SUFFIXES and path.is_file():
            if any(name.startswith(f"{d}/") for d in TEMPLATE_DIRS):
                staged.append(path)
    return staged


def _explicit_paths(raw: list[str]) -> list[Path]:
    return [Path(p) if Path(p).is_absolute() else REPO / p for p in raw]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Flag preload/prefetch hints whose href lacks the ?v= cache-buster "
            "used by the tag that actually loads the asset. Exits 1 on any "
            "violation."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check templates in the git staging area.",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check every template (default when no paths given).",
    )
    parser.add_argument("paths", nargs="*", help="Explicit template paths to check.")
    args = parser.parse_args()

    # The versioned-asset index must always be built from the WHOLE template
    # set: head.html carries the hint while footer.html carries the ?v= loader,
    # so a --staged run that only sees head.html would otherwise find nothing.
    versioned = collect_versioned_assets(_all_template_paths())

    if args.staged:
        files = _staged_template_paths()
    elif args.paths:
        files = _explicit_paths(args.paths)
    else:
        files = _all_template_paths()

    files = [f for f in files if f.is_file()]
    if not files:
        print("[asset-hint] No template files to check.")
        sys.exit(0)

    total = 0
    for path in files:
        violations = check_file(path, versioned)
        if violations:
            rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            for line_no, msg in violations:
                print(f"{rel}:{line_no}: {msg}", file=sys.stderr)
            total += len(violations)

    if total:
        print(
            f"\n[asset-hint] FAIL — {total} resource hint(s) point at a "
            f"versioned asset without ?v=.\n"
            f"  Fix by either:\n"
            f"    1. Deleting the hint (correct when the current page already "
            f"loads the asset — the preload scanner finds it anyway), or\n"
            f"    2. Appending the same ?v= expression the loader uses.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[asset-hint] OK — {len(files)} template(s) checked, 0 violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""CI regression guard: every third-party package the tests can reach must be
declared in ``scripts/requirements-ci.txt``.

There are two requirements files and CI installs only one of them. ``jekyll.yml``
runs ``pip install -r scripts/requirements-ci.txt``; ``scripts/requirements.txt``
is never installed there. So a package listed only in the latter is present on
every laptop in this repo and absent in CI.

Measured 2026-09-01: ``test_optional_narrowing_guards.py`` did
``import scripts.generate_missing_diagrams``, that module does a module-level
``from dotenv import load_dotenv``, and ``python-dotenv`` was declared only in
``scripts/requirements.txt``. The full local suite reported ``5115 passed`` and
CI failed with ``ModuleNotFoundError: No module named 'dotenv'``. The local green
was not wrong about the code; it was answering a different question.

Two distinct failure shapes are pinned here, and they are not the same problem:

``test_module_level_imports_reachable_from_tests_are_declared``
    the LOUD one. An undeclared import raises at collection and CI goes red, so
    this guard does not stop a regression from being noticed — it stops the
    round trip, and it names the fix at the point where the dependency is added
    rather than twenty minutes later in a CI log.

``test_importorskip_targets_are_declared``
    the SILENT one, and the reason this file matters. ``pytest.importorskip``
    fails open: the test does not fail, it disappears. That already happened here
    — ``scripts/requirements-ci.txt`` installed neither Pillow nor fontTools, and
    the two raster tests written to reproduce a bug *caused by Pillow being absent
    on the cron runner* skipped for that same missing dependency. They had never
    executed in CI. ``test_ci_pytest_deps_guard.py`` pins those two by name; this
    one generalises the rule so the third instance does not need someone to
    remember.

Direction: presence. A dependency may be added freely; only removing one that
something reaches trips this.

Why the import name is not the distribution name: ``import PIL`` comes from
``Pillow``, ``import yaml`` from ``PyYAML``, ``import dotenv`` from
``python-dotenv``. A guard comparing the two strings directly would flag every
one of them. Derivable cases are derived; the rest are listed in
``IMPORT_TO_DISTRIBUTION`` and an unresolvable name is a failure telling the
author to add one or the other, never a silent pass.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / "scripts" / "requirements-ci.txt"
SCRIPTS_DIR = REPO_ROOT / "scripts"
TESTS_DIR = SCRIPTS_DIR / "tests"

# Import names that no normalisation rule can turn into their distribution name.
# Keep this small: if a new entry is derivable, teach `_candidates` instead.
IMPORT_TO_DISTRIBUTION = {
    "PIL": "pillow",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
}

# Floors that make the scanners non-vacuous. A regex that stops matching, or a
# layout change that empties a directory, must fail loudly rather than pass by
# finding nothing to check. Set below what is present today, not at it, so
# ordinary deletions do not trip them.
MIN_REACHABLE_MODULES = 40
MIN_THIRD_PARTY_IMPORTS = 3
MIN_IMPORTORSKIP_TARGETS = 3


# ---------------------------------------------------------------------------
# requirements-ci.txt
# ---------------------------------------------------------------------------


def _normalize(name: str) -> str:
    """PEP 503-style normalisation: casefold and fold `_`/`.` to `-`."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _declared_distributions() -> set[str]:
    out: set[str] = set()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # strip extras and any version specifier: `fonttools[woff]>=4.63.0`
        name = re.split(r"[\[<>=!~;\s]", line, maxsplit=1)[0]
        if name:
            out.add(_normalize(name))
    return out


def _candidates(import_name: str) -> set[str]:
    """Distribution names that could plausibly provide ``import_name``."""
    base = _normalize(import_name)
    out = {base, f"python-{base}", f"py{base}"}
    mapped = IMPORT_TO_DISTRIBUTION.get(import_name)
    if mapped:
        out.add(_normalize(mapped))
    return out


def _is_declared(import_name: str) -> bool:
    return bool(_candidates(import_name) & _declared_distributions())


# ---------------------------------------------------------------------------
# What the tests can reach
# ---------------------------------------------------------------------------


def _local_module_names() -> set[str]:
    """Every module name that resolves inside `scripts/`, so it is not a package."""
    names = {p.stem for p in SCRIPTS_DIR.rglob("*.py")}
    names |= {d.name for d in SCRIPTS_DIR.iterdir() if d.is_dir()}
    names.add("scripts")
    return names


def _reachable_script_modules() -> set[str]:
    """`scripts.` modules referenced from the test suite, as dotted paths.

    Three reference forms appear in this suite and all three are collected:
    ``import scripts.x``, ``from scripts.x import y``, and a path string handed
    to ``spec_from_file_location`` (``"scripts/x.py"``). `scripts/tests/**` is
    excluded — a test's own imports are the test's business and pytest itself is
    already declared.
    """
    out: set[str] = set()
    for test_file in sorted(TESTS_DIR.rglob("*.py")):
        src = test_file.read_text(encoding="utf-8")
        for match in re.finditer(r"^\s*import\s+scripts\.([A-Za-z0-9_.]+)", src, re.M):
            out.add(match.group(1))
        for match in re.finditer(
            r"^\s*from\s+scripts\.([A-Za-z0-9_.]+)\s+import", src, re.M
        ):
            out.add(match.group(1))
        for match in re.finditer(r'["\']scripts/([A-Za-z0-9_/]+)\.py["\']', src):
            out.add(match.group(1).replace("/", "."))
    return {m for m in out if not m.startswith("tests.")}


def _module_level_third_party_imports(module: str) -> set[str]:
    """Top-level third-party imports of one `scripts.` module.

    Only direct children of the module body count. An import inside
    ``try: ... except ImportError:`` or ``if TYPE_CHECKING:`` is optional by
    construction and must not be required here — that is the semantics, not an
    oversight.
    """
    path = SCRIPTS_DIR / (module.replace(".", "/") + ".py")
    if not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover - the syntax floor guard owns this
        return set()

    stdlib = set(sys.stdlib_module_names)
    local = _local_module_names()
    found: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        else:
            continue
        for name in names:
            if name in stdlib or name in local or name == "__future__":
                continue
            found.add(name)
    return found


def _importorskip_targets() -> set[str]:
    out: set[str] = set()
    for test_file in sorted(TESTS_DIR.rglob("*.py")):
        src = test_file.read_text(encoding="utf-8")
        for match in re.finditer(r"""importorskip\(\s*["']([A-Za-z0-9_.]+)["']""", src):
            out.add(match.group(1))
    return out


# ---------------------------------------------------------------------------
# Canaries — a scanner that finds nothing must not read as compliant
# ---------------------------------------------------------------------------


def test_requirements_ci_exists() -> None:
    assert REQUIREMENTS.is_file(), f"{REQUIREMENTS} not found"
    assert _declared_distributions(), f"{REQUIREMENTS.name} declares nothing"


def test_scanners_are_not_vacuous() -> None:
    """Pin that each scanner still finds work, so a broken regex fails loudly."""
    modules = _reachable_script_modules()
    assert len(modules) >= MIN_REACHABLE_MODULES, (
        f"only {len(modules)} scripts modules found reachable from the test "
        f"suite (floor {MIN_REACHABLE_MODULES}); the reference-form regexes in "
        f"_reachable_script_modules() have probably stopped matching, which "
        f"would make the completeness test below pass by checking nothing"
    )

    third_party = {imp for m in modules for imp in _module_level_third_party_imports(m)}
    assert len(third_party) >= MIN_THIRD_PARTY_IMPORTS, (
        f"only {len(third_party)} third-party imports found across {len(modules)} "
        f"reachable modules (floor {MIN_THIRD_PARTY_IMPORTS}); the stdlib/local "
        f"filter in _module_level_third_party_imports() is probably over-filtering"
    )

    targets = _importorskip_targets()
    assert len(targets) >= MIN_IMPORTORSKIP_TARGETS, (
        f"only {len(targets)} importorskip targets found (floor "
        f"{MIN_IMPORTORSKIP_TARGETS}); if they were deliberately removed, lower "
        f"the floor in the same commit"
    )


# ---------------------------------------------------------------------------
# The invariants
# ---------------------------------------------------------------------------


def test_module_level_imports_reachable_from_tests_are_declared() -> None:
    """The loud shape: an undeclared import turns CI red at collection.

    Reproduced 2026-09-01 with `python-dotenv`. This assertion is what makes the
    two-requirements-file split visible where the dependency is introduced.
    """
    missing: list[str] = []
    for module in sorted(_reachable_script_modules()):
        for import_name in sorted(_module_level_third_party_imports(module)):
            if not _is_declared(import_name):
                missing.append(f"{import_name} (imported by scripts/{module}.py)")

    assert not missing, (
        "these packages are imported at module level by scripts/ modules the "
        "test suite loads, but are not declared in scripts/requirements-ci.txt "
        "— they will import fine locally and raise ModuleNotFoundError in CI:\n  "
        + "\n  ".join(missing)
        + "\n\nFix: add the distribution to scripts/requirements-ci.txt with a "
        "comment saying what breaks without it. Note that scripts/requirements.txt "
        "is NOT installed by CI. If the import name differs from the distribution "
        "name and is not derivable, add it to IMPORT_TO_DISTRIBUTION here too. Do "
        "not reach for pytest.importorskip — it fails open."
    )


def test_importorskip_targets_are_declared() -> None:
    """The silent shape: an undeclared target makes the test vanish, not fail.

    A local module name is a legitimate target (the suite uses importorskip to
    express "this helper must be importable"), so those are excluded rather than
    demanded of requirements-ci.txt.
    """
    local = _local_module_names()
    missing = sorted(
        target
        for target in _importorskip_targets()
        if target not in local and not _is_declared(target)
    )

    assert not missing, (
        "these pytest.importorskip targets are not declared in "
        "scripts/requirements-ci.txt, so in CI the tests behind them SKIP "
        "instead of running — silently:\n  " + "\n  ".join(missing) + "\n\n"
        "This is the exact shape of the 2026-08-18 Pillow/fontTools incident "
        "documented in scripts/requirements-ci.txt: tests written to reproduce a "
        "missing-dependency bug skipped for that same missing dependency. Declare "
        "the package, or make the import hard if the skip is not wanted."
    )


@pytest.mark.parametrize(
    ("import_name", "distribution"),
    sorted(IMPORT_TO_DISTRIBUTION.items()),
)
def test_mapping_entries_are_actually_needed(
    import_name: str, distribution: str
) -> None:
    """A mapping entry for a name that normalises fine is dead weight.

    Without this, IMPORT_TO_DISTRIBUTION accumulates guesses nobody rechecks and
    the table stops describing which names genuinely need help.
    """
    derivable = {_normalize(import_name), f"python-{_normalize(import_name)}"}
    assert _normalize(distribution) not in derivable, (
        f"IMPORT_TO_DISTRIBUTION maps {import_name!r} -> {distribution!r}, but "
        f"that is already derivable by _candidates(); drop the entry"
    )

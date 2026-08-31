"""Guard: scripts/ must parse on the oldest Python that CI pins.

The local interpreter is newer than CI's. Measured 2026-08-24: this machine runs
3.13/3.14 while thirteen workflows that execute `scripts/` pin 3.11. Syntax
introduced after 3.11 therefore parses locally, passes pre-commit, passes the
full local suite — and then fails at *collection* time in CI, which takes the
whole run down rather than failing one test.

Not hypothetical: PR #599 shipped a backslash inside an f-string expression
(legal from 3.12 via PEP 701). CI's 3.11 raised
``SyntaxError: f-string expression part cannot include a backslash`` and aborted
collection of all 4319 tests.

Why ruff and not ast
--------------------
``ast.parse(source, feature_version=(3, 11))`` does **not** reject this — that
parameter gates a narrow set of grammar features, and the 3.13 tokenizer handles
f-strings the PEP 701 way regardless. Verified both directions on 2026-08-24:
``ast.parse`` accepted the construct at ``feature_version=(3, 11)``, a real 3.11
(`uv run --python 3.11`) raised SyntaxError, and
``ruff check --target-version py311`` reported it. So ruff is the check.

The floor is derived from the workflows rather than hardcoded, so bumping CI's
Python relaxes this guard instead of leaving a stale number behind.

Limitation, stated so a green result is not over-read: this is a *syntax* check.
A 3.12+ standard-library call parses fine here and would still fail at runtime
on 3.11.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
SCRIPTS = REPO_ROOT / "scripts"

_PIN_RE = re.compile(
    r"^\s*python-version:\s*['\"]?(\d+)\.(\d+)['\"]?\s*$", re.MULTILINE
)
_ENV_RE = re.compile(
    r"^\s*PYTHON_VERSION:\s*['\"]?(\d+)\.(\d+)['\"]?\s*$", re.MULTILINE
)


def pinned_versions() -> dict[str, tuple[int, int]]:
    """Lowest Python version each workflow pins, literal or via PYTHON_VERSION."""
    found: dict[str, tuple[int, int]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        versions = [
            (int(a), int(b)) for a, b in _PIN_RE.findall(text) + _ENV_RE.findall(text)
        ]
        if versions:
            found[wf.name] = min(versions)
    return found


def syntax_floor() -> tuple[int, int]:
    versions = pinned_versions()
    assert versions, "no workflow pins a python-version — has setup-python moved?"
    return min(versions.values())


def ruff_target() -> str:
    cfg = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return cfg.get("tool", {}).get("ruff", {}).get("target-version", "")


def test_a_floor_is_discoverable():
    """If this breaks, the check below is silently measuring nothing."""
    versions = pinned_versions()
    assert len(versions) >= 5, f"only found pins in {sorted(versions)}"
    assert syntax_floor() >= (3, 8), syntax_floor()


def test_ruff_target_version_matches_the_ci_floor():
    """A stale target-version is worse than none: it reads as protection."""
    floor = syntax_floor()
    expected = f"py{floor[0]}{floor[1]}"
    actual = ruff_target()
    assert actual == expected, (
        f"[tool.ruff] target-version is {actual!r} but the oldest Python any "
        f"workflow pins is {floor[0]}.{floor[1]} ({expected!r}). Update "
        "pyproject.toml, or update the workflows — they must agree or ruff "
        "accepts syntax CI cannot parse."
    )


def test_ruff_is_installed():
    """Fail rather than skip.

    A skipped gate is a gate that has never run. Repo policy since PR #579:
    absent tooling is a failure, not a skip. ruff is declared in
    scripts/requirements-ci.txt for exactly this test.
    """
    assert shutil.which("ruff"), (
        "ruff is not on PATH. It is declared in scripts/requirements-ci.txt; "
        "install it (`pip install -r scripts/requirements-ci.txt`) rather than "
        "letting this check silently pass."
    )


def _invalid_syntax_lines(target: str, path: Path) -> list[str]:
    res = subprocess.run(
        [
            "ruff",
            "check",
            "--no-cache",
            "--target-version",
            target,
            "--output-format",
            "concise",
            str(path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # Only syntax diagnostics matter here; ordinary lint findings are out of scope
    # and must not turn this into a style gate.
    return [ln for ln in res.stdout.splitlines() if "invalid-syntax" in ln]


def test_every_script_parses_at_the_ci_floor():
    floor = syntax_floor()
    target = f"py{floor[0]}{floor[1]}"
    offenders = _invalid_syntax_lines(target, SCRIPTS)
    assert offenders == [], (
        f"these use syntax newer than Python {floor[0]}.{floor[1]}, which CI pins. "
        "They parse locally and abort test collection in CI:\n  "
        + "\n  ".join(offenders)
    )


def test_the_check_actually_rejects_newer_syntax(tmp_path):
    """Proof the assertion above is not vacuously green.

    A backslash inside an f-string expression is the exact construct that broke
    PR #599: legal from 3.12, SyntaxError on 3.11. Written with chr(92) so this
    file itself stays 3.11-clean.
    """
    sample = tmp_path / "pep701_sample.py"
    backslash_n = chr(92) + "n"
    sample.write_text(
        f'x = ["a"]\ny = f"{{ x[0].split(\'{backslash_n}\') }}"\n',
        encoding="utf-8",
    )
    assert backslash_n in sample.read_text(encoding="utf-8"), (
        "sample lost its backslash"
    )

    assert _invalid_syntax_lines("py311", sample), "ruff did not flag it at py311"
    assert not _invalid_syntax_lines("py312", sample), "ruff flagged it at py312"

#!/usr/bin/env python3
"""CI config guard: both coverage floors exist, are wired, and mean what they say.

What went wrong
---------------
`[tool.coverage.report]` in pyproject.toml carries an `include` list of 9 path
patterns. Everything downstream of it — the terminal table, `coverage.json`, the
PR comment, and `fail_under` — therefore described **17 files / 4,755 statements
at 72%** while `scripts/` held **218 files / 34,747 statements at 39.76%**
(measured 2026-09-10). The floor governed 13.7% of the code, so a brand-new
500-line untested module could not move it, and the comment above `fail_under`
called it "a ratchet" without saying what it was bolted to.

Worse, there were two disagreeing numbers: pyproject said `fail_under = 50`
while `jekyll.yml` passed `--cov-fail-under=40` on the pytest line, and the CLI
flag wins. CI enforced 40; the file everyone reads claimed 50.

The fix is two NAMED floors — pyproject for the curated core, `.coveragerc-global`
for everything — and exactly one place setting each. This guard pins that shape,
because the failure mode is silent in both directions: deleting the global step
leaves a green build, and re-adding a CLI `--cov-fail-under` silently overrides
the file again.

Direction: presence and single-source assertions. Numbers are asserted as
"not lowered", never as an exact value, so improving coverage does not trip it.
"""

from __future__ import annotations

import configparser
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
GLOBAL_RC = REPO_ROOT / ".coveragerc-global"
JEKYLL = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"

# Floors as measured on 2026-09-10 (core 72.13%, global 39.76%). Asserted as a
# minimum so raising either is fine and lowering trips.
CORE_FLOOR_MIN = 50
GLOBAL_FLOOR_MIN = 39


def _jekyll_body() -> str:
    """jekyll.yml with comment-only lines dropped.

    Both floors are explained in prose that names the flags and files, so a raw
    text match would hit the explanation and stay green after the real
    invocation was deleted.
    """
    return "\n".join(
        ln
        for ln in JEKYLL.read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    )


def test_config_files_exist():
    """Canary: a rename must fail loudly rather than pass vacuously."""
    for p in (PYPROJECT, GLOBAL_RC, JEKYLL):
        assert p.is_file(), f"{p} not found"


def test_core_floor_is_set_in_pyproject():
    cfg = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    report = cfg["tool"]["coverage"]["report"]
    assert "fail_under" in report, (
        "pyproject lost its fail_under. The curated slice would then have no "
        "floor at all, and the well-tested modules could rot unnoticed."
    )
    assert report["fail_under"] >= CORE_FLOOR_MIN, (
        f"core floor dropped to {report['fail_under']} (was >= {CORE_FLOOR_MIN}). "
        "Lower it only with a reason in the PR body."
    )


def test_global_floor_is_set_and_covers_everything():
    cfg = configparser.ConfigParser()
    cfg.read(GLOBAL_RC, encoding="utf-8")
    assert cfg.has_section("report"), f"{GLOBAL_RC.name} has no [report] section"
    floor = cfg.getint("report", "fail_under", fallback=None)
    assert floor is not None, f"{GLOBAL_RC.name} sets no fail_under"
    assert floor >= GLOBAL_FLOOR_MIN, (
        f"global floor dropped to {floor} (was >= {GLOBAL_FLOOR_MIN})."
    )
    # The whole point is that this config does NOT narrow the scope.
    assert not cfg.has_option("report", "include"), (
        f"{GLOBAL_RC.name} grew an `include` list. That makes it a second "
        "curated slice, and nothing is left watching the other ~30,000 "
        "statements — the exact defect this file exists to prevent."
    )
    omit = cfg.get("report", "omit", fallback="")
    assert "scripts/tests" in omit, (
        "the global config no longer omits scripts/tests, so the test suite's "
        "own coverage inflates the number it is supposed to measure."
    )


# The GATING invocation only. jekyll.yml also runs the same command inside the
# PR-comment step as `$(... 2>/dev/null)` purely to read the number, and a loose
# pattern matched THAT — so deleting the gating step left this guard green. Found
# by mutating the step away and watching only the other assertion trip.
# Anchored on a line that starts the command and neither redirects nor captures.
_GATING_RE = re.compile(
    r"^\s*python3 -m coverage report --rcfile=\.coveragerc-global\s*$", re.MULTILINE
)


def test_global_floor_runs_in_ci():
    body = _jekyll_body()
    assert _GATING_RE.search(body), (
        "jekyll.yml no longer runs the global coverage floor as a gating step. "
        "Deleting it leaves a green build and returns the ratchet to 13.7% of "
        "the code. Note the PR-comment step runs the same command captured in "
        "`$( ... 2>/dev/null )` — that one gates nothing and does not count."
    )


def test_global_floor_step_is_not_swallowed():
    """`coverage report` exits 2 on a breach — that has to reach the job."""
    raw = JEKYLL.read_text(encoding="utf-8")
    m = _GATING_RE.search(
        "\n".join(ln for ln in raw.splitlines() if not ln.lstrip().startswith("#"))
    )
    assert m, (
        "no gating invocation to inspect — test_global_floor_runs_in_ci explains "
        "what is missing."
    )
    at = raw.index("python3 -m coverage report --rcfile=.coveragerc-global\n")
    line = raw[raw.rfind("\n", 0, at) + 1 : raw.find("\n", at)]
    assert "|| true" not in line and "|| :" not in line, (
        f"the global floor invocation is neutralised: {line.strip()!r}"
    )
    # And the step itself must not be continue-on-error.
    step_start = raw.rindex("- name:", 0, at)
    step_text = raw[step_start:at]
    assert "continue-on-error" not in step_text, (
        "the global coverage floor step is continue-on-error, so a breach "
        "cannot fail the build."
    )


def test_ci_installs_something_that_provides_coverage():
    """The global floor step shells out to ``coverage`` directly, not via pytest.

    ``scripts/requirements-ci.txt`` never names ``coverage``; it arrives
    transitively through ``pytest-cov`` (verified in a clean venv on 2026-09-10:
    ``pip install pytest-cov==7.1.0`` pulled coverage 7.16.0 and
    ``python3 -m coverage report --rcfile=.coveragerc-global`` exited 0). Dropping
    pytest-cov because "pytest is what we run" would take the global floor's
    interpreter module with it. That failure is loud, not silent — the step exits
    non-zero — so this asserts the declaration, not the behaviour.
    """
    req = (REPO_ROOT / "scripts" / "requirements-ci.txt").read_text(encoding="utf-8")
    declared = [
        ln.strip()
        for ln in req.splitlines()
        if re.match(r"^\s*(pytest-cov|coverage)\b", ln)
    ]
    assert declared, (
        "scripts/requirements-ci.txt declares neither pytest-cov nor coverage, so "
        "`python3 -m coverage report --rcfile=.coveragerc-global` has no module to "
        "run and the global floor step cannot execute."
    )


def test_pr_comment_does_not_window_the_total_row():
    """The global row is grepped out of `coverage report` — don't pipe it first.

    `coverage` prints notes AFTER the TOTAL row ("N files skipped due to
    complete coverage.", plus "N empty files skipped." once `skip_empty` is
    set). Measured 2026-09-11: exactly 2 trailing lines, so the `| tail -3 |`
    that used to sit before the grep had zero margin — one more note pushes
    TOTAL out of the window and the comment renders an empty
    `| Whole of scripts/ | | | |` row.

    Cosmetic, since the step is `continue-on-error`. Pinned anyway because it
    fails silently and the fix costs nothing: only one line can start with
    TOTAL, so the grep needs no window.
    """
    body = _jekyll_body()
    m = re.search(r"^\s*GLOBAL=\$\((.+)\)\s*$", body, re.MULTILINE)
    assert m, "the PR comment no longer extracts a global coverage row"
    pipeline = m.group(1)
    assert "coverage report --rcfile=.coveragerc-global" in pipeline
    assert "tail" not in pipeline and "head" not in pipeline, (
        f"the TOTAL row is extracted through a line window: {pipeline!r}. "
        "Coverage appends notes after TOTAL, so a window can drop it."
    )


def test_pr_comment_reads_coverage_json_once():
    """One `open()`, one parse — the second call also leaked its handle."""
    body = _jekyll_body()
    assert body.count("json.load(open(") == 0, (
        "coverage.json is parsed via a bare json.load(open(...)), which reads "
        "the file a second time and leaks the handle"
    )
    assert "import glob" not in body, "unused import left in the inline script"


def test_no_cli_flag_overrides_the_core_floor():
    """A `--cov-fail-under` on the pytest line silently beats pyproject.

    That is how CI came to enforce 40 while pyproject said 50. If a CLI floor is
    ever wanted again, make it equal to pyproject's and say why here.
    """
    body = _jekyll_body()
    assert "--cov-fail-under" not in body, (
        "jekyll.yml passes --cov-fail-under again. The CLI flag wins over "
        "pyproject's fail_under, so the file everyone reads stops being the "
        "floor that CI applies."
    )

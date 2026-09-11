#!/usr/bin/env python3
"""CI/hook wiring guard: the excerpt-promise gate must stay armed and corpus-wide.

Why a wiring guard and not just the gate's own tests
----------------------------------------------------
``check_excerpt_promises.py`` can be perfectly correct and enforce nothing. This
repo has already shipped a gate that was inert from creation — it printed a
count, never called ``sys.exit()``, and no workflow invoked it — and a gate
whose scope was quietly narrowed to a diff so a cron push sailed past it. Both
failures are silent: the job goes green either way.

Three specific ways this one could go dark, each asserted below:

1. the svg-lint step is deleted, or neutralised with ``|| true`` /
   ``continue-on-error``
2. the step is narrowed off ``--all``. The corpus reached 0 by repairing 150
   posts; the recurrence path is a cron bot push, which a ``--staged`` or
   ``--changed`` scope cannot see at all
3. the pre-commit step is deleted, so the local publish path — the one the
   2026-09-04 QR incident came through — stops checking

Direction: presence assertions. Adding scope trips nothing; removing it trips.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SVG_LINT = REPO_ROOT / ".github" / "workflows" / "svg-lint.yml"
PRE_COMMIT = REPO_ROOT / ".githooks" / "pre-commit"
GATE = REPO_ROOT / "scripts" / "check_excerpt_promises.py"
GENERATOR = REPO_ROOT / "scripts" / "seo_diversify_excerpts.py"

_ALL_INVOCATION = re.compile(
    r"^\s*run:\s*python3 scripts/check_excerpt_promises\.py --all\s*$", re.MULTILINE
)


def _uncommented(text: str) -> str:
    """Comment-only lines dropped.

    The step is documented in prose that names the script and the flag, so a
    raw text match would hit the explanation and stay green after the real
    invocation was deleted.
    """
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def test_gate_and_generator_exist():
    """Canary: a rename must fail loudly rather than pass vacuously."""
    for p in (GATE, GENERATOR, SVG_LINT, PRE_COMMIT):
        assert p.is_file(), f"{p} not found (moved/renamed?)"


def test_gate_exits_nonzero_on_violations():
    """A gate that only prints is not a gate — this repo has shipped one."""
    src = GATE.read_text(encoding="utf-8")
    assert "sys.exit(main())" in src, (
        "check_excerpt_promises.py no longer propagates main()'s return code, so "
        "violations would print and the job would still pass."
    )
    assert "return 1" in src


def test_svg_lint_runs_the_gate_over_the_whole_corpus():
    body = _uncommented(SVG_LINT.read_text(encoding="utf-8"))
    assert _ALL_INVOCATION.search(body), (
        "svg-lint.yml no longer runs `check_excerpt_promises.py --all` as a "
        "gating step. The corpus is at 0 only because 150 posts were repaired; "
        "the recurrence path is a cron bot push, which a diff-scoped run cannot "
        "see."
    )
    assert "check_excerpt_promises.py --staged" not in body, (
        "the corpus gate was narrowed to --staged. Scheduled runs have no "
        "staged files, so that scope makes the job vacuously green."
    )


def test_svg_lint_step_is_not_neutralised():
    raw = SVG_LINT.read_text(encoding="utf-8")
    at = raw.index("python3 scripts/check_excerpt_promises.py --all")
    line = raw[raw.rfind("\n", 0, at) + 1 : raw.find("\n", at)]
    assert "|| true" not in line and "|| :" not in line, (
        f"the excerpt-promise gate is neutralised: {line.strip()!r}"
    )
    step = raw[raw.rindex("- name:", 0, at) : at]
    assert "continue-on-error" not in step, (
        "the excerpt-promise step is continue-on-error, so a violation cannot "
        "fail the build."
    )


def test_path_filters_watch_both_sides():
    """The gate's verdict depends on the generator's predicates, not just its own.

    ``CLOSERS`` lives in the generator and both sides read that one list, so a
    predicate edit there changes what the gate enforces. If only the gate's own
    path is filtered, that edit lands without the gate ever running.
    """
    raw = SVG_LINT.read_text(encoding="utf-8")
    for name in ("check_excerpt_promises.py", "seo_diversify_excerpts.py"):
        assert raw.count(f"'scripts/{name}'") >= 2, (
            f"scripts/{name} is missing from a paths filter, so a change to it "
            "would not trigger the workflow that enforces it."
        )


def test_pre_commit_runs_the_gate_on_staged_posts():
    body = _uncommented(PRE_COMMIT.read_text(encoding="utf-8"))
    assert "check_excerpt_promises.py" in body, (
        "the pre-commit step is gone. CI would still catch it, but only after a "
        "push — and the hand-run publish path is exactly where the 2026-09-04 "
        "cover incident entered."
    )
    assert "--staged" in body
    at = body.index("check_excerpt_promises.py")
    line = body[body.rfind("\n", 0, at) + 1 : body.find("\n", at)]
    assert "|| true" not in line, f"the pre-commit invocation is swallowed: {line!r}"


def test_documented_repair_command_is_real():
    """The failure message tells the reader how to fix it — that has to work.

    Asserted by RUNNING the flag, not by grepping for it: the failure mode is
    that the advice in the error message silently stops being executable, and
    a substring match cannot see that.

    Note for anyone probing this test: renaming the flag to
    ``--repair-promises-x`` does NOT trip it, and that is correct rather than a
    gap. argparse accepts unambiguous prefixes, so the documented command still
    runs. The mutations that do trip it are the ones that actually break the
    advice — deleting the ``add_argument`` call, or dropping the repair line
    from the gate's error message.
    """
    src = GATE.read_text(encoding="utf-8")
    assert "--repair-promises" in src, (
        "the gate no longer tells the reader how to fix a violation"
    )
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/seo_diversify_excerpts.py",
            "--repair-promises",
            "--month",
            "1970-01",  # matches nothing: we are testing the parser, not the corpus
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert "unrecognized arguments" not in proc.stderr, (
        "the gate points at `seo_diversify_excerpts.py --apply "
        "--repair-promises` but the generator rejects that flag, so the advice "
        f"in the error message is dead:\n{proc.stderr}"
    )

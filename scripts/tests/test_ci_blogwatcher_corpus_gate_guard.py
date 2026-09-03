#!/usr/bin/env python3
"""CI regression guard: corpus gates run BEFORE the cron publishes, not 3h45m after.

svg-lint.yml carries these gates at `--all` and sweeps main daily at 03:45 UTC.
The blogwatcher pushes at 00:00 UTC. So until 2026-08-26 a violation the cron
introduced sat on main for most of four hours with nothing objecting, and every
PR opened in that window inherited the red — PR CI builds a merge commit on top
of base main, so a defect in base propagates to unrelated PRs. Measured on the
08-25 digest: cron pushed 98a4170d at 00:00, the scheduled sweep failed it at
04:23.

Audit finding (2026-08-26): of the 28 gate scripts that svg-lint/check-svg or
pre-commit run, the publish path ran 10. The blocker was never cost — all nine
wired here finish in ~3.3s over 277 posts — it was that eight of them accept no
file argument at all (argparse rc=2 on a path), only `--all` or `--staged`, and
`--staged` is meaningless on an Actions commit that runs with no local hooks.

`check_filename_entities` is the cautionary one. It was wired into pre-commit as
`--staged` only, so nobody had ever run it at `--all` — and it was RED, on two
entity-residue filenames sitting in assets/images/_unused_archive/ since they
were archived. Wiring it before that cleanup would have failed the cron every
night. Hence the rule this guard exists to protect: run a dormant gate at the
scope you intend to wire, and read the output, before wiring it.

Direction: presence + non-softening + ordering. Removing a gate, wrapping one in
`|| true`, or moving the step after the commit trips this.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

PREFLIGHT_STEP = "Corpus gate pre-flight"
COVER_STEP = "Verify L20 cover"
PUBLISH_STEP = "Commit and publish"

# Gates promoted into the publish path on 2026-08-26, with the invocation each
# one actually supports. The mode is part of the invariant: check_kst_midnight
# takes a path, the rest take --all because they take nothing else.
CORPUS_GATES = (
    ("scripts/check_kst_midnight.py", '"$POST_FILE"'),
    ("scripts/check_card_title_language.py", "--all"),
    ("scripts/check_post_boilerplate.py", "--all"),
    ("scripts/check_broken_links.py", "--all"),
    ("scripts/check_spec_slug_consistency.py", "--all"),
    ("scripts/check_l20_spec_slug_consistency.py", "--all"),
    ("scripts/check_post_image_variants.py", ""),
    ("scripts/check_orphan_cover_rasters.py", "assets/images"),
    ("scripts/check_filename_entities.py", "--all"),
)

# Cover-scoped gates added to the existing cover step, which already resolves
# $SVG. check_l20_generic_hero reads the COVER: handed a post path it reports
# "0 L20 cover(s) checked" and exits 0, which reads exactly like a pass.
COVER_GATES = (
    "scripts/check_l20_generic_hero.py",
    "scripts/check_svg_size_gate.py",
)


def _doc() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps() -> dict[str, dict]:
    job = _doc()["jobs"]["auto-publish"]
    return {s["name"]: s for s in job["steps"] if s.get("name")}


def _find(fragment: str) -> dict:
    for name, step in _steps().items():
        if fragment in name:
            return step
    pytest.fail(f"no step whose name contains {fragment!r} in ai-blogwatcher.yml")


def _uncommented(shell: str) -> str:
    """Comment-only lines removed.

    These steps explain in prose which gates they run and why, naming every
    script. Matching raw text would hit the explanation and keep passing after
    the command itself was deleted.
    """
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def test_workflow_exists():
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found"


def test_preflight_step_exists():
    assert _find(PREFLIGHT_STEP)["run"], f"{PREFLIGHT_STEP} step has an empty body"


@pytest.mark.parametrize(("script", "mode"), CORPUS_GATES)
def test_gate_is_invoked_in_the_preflight(script: str, mode: str):
    body = _uncommented(_find(PREFLIGHT_STEP)["run"])
    line = next((ln for ln in body.splitlines() if script in ln), None)
    assert line is not None, (
        f"{script} is no longer run before publish. svg-lint runs it at --all on "
        "a 03:45 UTC timer, which is ~3h45m after the cron pushes — main goes red "
        "in between and every PR opened in that window inherits it."
    )
    assert mode in line, (
        f"{script} is invoked as {line.strip()!r}, expected mode {mode!r}. "
        "Eight of these accept no file argument (argparse rc=2 on a path); "
        "--staged is meaningless on an Actions commit with no local hooks."
    )


@pytest.mark.parametrize(("script", "_mode"), [(s, m) for s, m in CORPUS_GATES])
def test_gate_is_not_softened(script: str, _mode: str):
    body = _uncommented(_find(PREFLIGHT_STEP)["run"])
    for line in body.splitlines():
        if script in line:
            for softener in ("|| true", "|| echo", "|| :"):
                assert softener not in line, (
                    f"{script} is softened with {softener!r}. A gate that cannot "
                    "end the step is decoration — the digest publishes anyway and "
                    "main goes red at 03:45."
                )


def test_preflight_step_is_not_continue_on_error():
    step = _find(PREFLIGHT_STEP)
    assert not step.get("continue-on-error"), (
        "continue-on-error on the corpus gate step defeats every gate in it at once"
    )


def test_preflight_shares_the_partition_of_its_neighbours():
    assert _find(PREFLIGHT_STEP).get("if") == (
        "env.RUN_CHECKS == 'true' && steps.check_post.outputs.post_created == 'true'"
    ), (
        "the corpus gate step's condition drifted from the other pre-flights. It "
        "must behave identically for the untrusted-dispatch partition and the "
        "no-post case."
    )


def test_preflight_runs_before_the_commit():
    """A gate after the commit cannot stop the commit."""
    names = list(_steps())
    at = next(i for i, n in enumerate(names) if PREFLIGHT_STEP in n)
    assert at < names.index(PUBLISH_STEP), (
        f"{PREFLIGHT_STEP} runs after {PUBLISH_STEP}, where blocking is impossible"
    )


@pytest.mark.parametrize("script", COVER_GATES)
def test_cover_gate_is_scoped_to_todays_cover(script: str):
    body = _uncommented(_find(COVER_STEP)["run"])
    line = next((ln for ln in body.splitlines() if script in ln), None)
    assert line is not None, f"{script} is no longer run on the cron's cover"
    assert '"${SVG}"' in line, (
        f"{script} must take the resolved ${{SVG}} path. check_l20_generic_hero in "
        "particular reports '0 L20 cover(s) checked' and exits 0 when handed "
        "anything that is not a cover — a pass that checked nothing."
    )
    assert "|| true" not in line, f"{script} is softened with '|| true'"


def test_filename_entities_is_wired_only_at_all_scope():
    """--staged here would be a no-op, which is how this gate stayed dormant.

    It lived in pre-commit as `--staged` and had never been run at --all. When it
    finally was (2026-08-26) it failed on two archived filenames. `--staged`
    inside the cron would reproduce exactly that dormancy: green forever, because
    nothing is staged at this point in the job.
    """
    body = _uncommented(_find(PREFLIGHT_STEP)["run"])
    line = next(ln for ln in body.splitlines() if "check_filename_entities.py" in ln)
    assert "--staged" not in line, (
        "check_filename_entities is wired with --staged, which matches nothing "
        "here and reproduces the dormancy that hid two failures for months"
    )


# The whole-directory run, not a single-file one. ai-blogwatcher.yml already
# contains `pytest scripts/tests/test_briefing_stats.py` in another step, and a
# plain `"pytest scripts/tests/" in line` substring test matches that too — the
# same near-miss that let a mutation probe pass in #660 after the full-suite
# step had been deleted. Require whitespace or end-of-line after the directory.
_FULL_SUITE_RE = re.compile(r"pytest\s+scripts/tests/(?=\s|$)")


def test_pytest_suite_runs_in_the_preflight():
    """The corpus check_*.py gates above are not the whole story.

    Every guard in scripts/tests/ that reads `_posts/` — excerpt quality,
    digest structure, cover honesty — otherwise runs only in jekyll.yml's build
    job, and that job never fires for the cron's push: a commit made with the
    default GITHUB_TOKEN triggers no push-event workflows. Measured 2026-09-03
    on `35854337`: 1 run total (CodeQL `dynamic`), 0 push-event runs, against 9
    for the comparable human push `b81ed099`.

    So this line is the only thing that runs those guards before a digest is
    published. Deleting it restores the gap silently — the cron stays green.
    """
    body = _uncommented(_find(PREFLIGHT_STEP)["run"])
    line = next((ln for ln in body.splitlines() if _FULL_SUITE_RE.search(ln)), None)
    assert line is not None, (
        "the pre-flight no longer runs pytest over all of scripts/tests/. A "
        "single-file invocation does not count. Without it, every pytest guard "
        "that reads _posts/ is dormant on the one push that creates posts."
    )
    for softener in ("|| true", "|| echo", "|| :"):
        assert softener not in line, (
            f"the pre-flight pytest run is softened with {softener!r}. A gate "
            "that cannot end the step is decoration — the digest publishes "
            "anyway."
        )

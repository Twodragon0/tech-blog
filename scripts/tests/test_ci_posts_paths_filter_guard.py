#!/usr/bin/env python3
"""CI regression guard: a post-only push must still run the pytest job.

`pytest scripts/tests/` runs in exactly one place — the `build` job of
jekyll.yml. On a `push` that job is gated on
`needs.check-changes.outputs.should-build`, which dorny/paths-filter derives
from the `should-build:` pattern list. `**_posts/**` is the only entry in that
list a post edit matches: the others cover `_includes`, `_layouts`, `_sass`,
`assets`, `_config.yml`, `vercel.json`, `.github/workflows` and `**/*.py`.

Drop `**_posts/**` and every corpus-wide pytest guard that reads `_posts/`
(excerpt quality, digest structure, card titles, boilerplate) goes dormant on
the one change type it exists to catch. It goes dormant **silently**, because a
skipped job reports neither red nor a missing required check — the same failure
shape as `check_filename_entities`, wired `--staged`-only and therefore never
run at all, and `check_broken_links`, which printed a count and never called
`sys.exit()`. Neither was noticed by the CI going green.

The blogwatcher makes this concrete rather than theoretical: it pushes a new
digest straight to main at 00:00 UTC, touching `_posts/` and its cover. That
push is the single highest-volume producer of post content in the repo and it
has no human reviewer, so the paths-filter is what decides whether anything
inspects it before the 03:45 UTC svg-lint sweep.

Direction: presence + coupling. Removing the pattern, renaming the filter key,
or decoupling the build job from it all trip this. Adding patterns does not.

Related, deliberately not duplicated here:
  test_ci_digest_kpi_gate_guard.py  pins the pytest step itself, its
      `--cov-fail-under` floor, and `**/*.py` in this same filter list.
      This file adds only the `_posts` half of that list, which nothing pinned.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"

FILTER_KEY = "should-build"
GATED_JOB = "build"
FILTER_JOB = "check-changes"

# Any of these is an acceptable spelling of "a change under _posts/". The guard
# asserts the capability, not one exact glob, so a legitimate reformatting of
# the pattern does not read as a removal.
POSTS_PATTERNS = ("**_posts/**", "_posts/**", "**/_posts/**", "_posts/**.md")


def _doc() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _filters_block() -> dict:
    """Parse the `filters:` block scalar handed to dorny/paths-filter.

    `filters:` is a literal block scalar, so the outer parse yields a *string*;
    the pattern lists only exist after parsing that string as YAML in its own
    right. Doing both parses with a real YAML parser (rather than scanning
    lines) is what keeps the `#` comments inside that list from terminating a
    hand-rolled collector early and hiding every entry below them.
    """
    steps = _doc()["jobs"][FILTER_JOB]["steps"]
    for step in steps:
        with_ = step.get("with") or {}
        if "filters" in with_:
            return yaml.safe_load(with_["filters"]) or {}
    return {}


def test_workflow_exists() -> None:
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found"


def test_filter_step_is_still_there() -> None:
    """Canary: a moved or renamed filter step must fail loudly, not vacuously.

    Without this, `_filters_block()` returning `{}` would make the membership
    assertion below fail with a confusing message about `_posts` when the real
    change was that the whole step went away.
    """
    block = _filters_block()
    assert block, (
        f"no step in the '{FILTER_JOB}' job passes `with.filters:` to "
        "dorny/paths-filter any more. If the change-detection step moved, point "
        "this guard at its new home rather than deleting the guard."
    )


def test_should_build_key_is_still_named_that() -> None:
    block = _filters_block()
    assert FILTER_KEY in block, (
        f"the '{FILTER_KEY}' filter key is gone (found: {sorted(block)}). The "
        f"'{GATED_JOB}' job's `if:` reads "
        f"needs.{FILTER_JOB}.outputs.{FILTER_KEY}, so a rename here silently "
        "evaluates to empty and the job stops running on every push."
    )


def test_posts_changes_trigger_the_build_job() -> None:
    patterns = _filters_block().get(FILTER_KEY) or []
    assert any(p in patterns for p in POSTS_PATTERNS), (
        f"no _posts pattern left in the '{FILTER_KEY}' filter (have: {patterns}).\n"
        "pytest runs only inside the 'build' job, and on a push that job is "
        f"gated on this list. Without a _posts entry, a post-only push — which "
        "is what the blogwatcher cron produces every night at 00:00 UTC — skips "
        "the job entirely, so every corpus guard that reads _posts/ stops "
        "running. A skipped job is not a red job, so nothing reports it.\n"
        f"If you reformatted the glob, add the new spelling to POSTS_PATTERNS "
        "in this file."
    )


def test_build_job_is_gated_on_that_filter() -> None:
    """The coupling is the reason the assertion above matters.

    If the `build` job stopped consulting `should-build`, the filter list would
    be inert and this guard would be pinning a value nothing reads — passing
    while protecting nothing.
    """
    condition = str(_doc()["jobs"][GATED_JOB].get("if", ""))
    assert f"needs.{FILTER_JOB}.outputs.{FILTER_KEY}" in condition, (
        f"the '{GATED_JOB}' job no longer gates on "
        f"needs.{FILTER_JOB}.outputs.{FILTER_KEY} (if: {condition!r}). Either "
        "the gate was removed — in which case this guard is pinning a value "
        "nothing reads and should be deleted — or it was rewired, in which case "
        "point the guard at the new output."
    )


# The whole-directory run, not a single-file one. The `build` job also contains
# `pytest scripts/tests/test_post_image_class_hooks.py::TestCompiledCss`, and a
# plain `"pytest scripts/tests/" in body` substring test matches that too — so it
# stayed green in a mutation probe that had removed the full-suite step. Require
# `scripts/tests/` to be followed by whitespace or end-of-line, which the
# single-file invocation (followed by `test_…`) cannot satisfy.
_FULL_SUITE_RE = re.compile(r"pytest\s+scripts/tests/(?=\s|$)", re.M)


def test_pytest_step_lives_in_the_gated_job() -> None:
    """Non-vacuity for the whole file: the gate must actually cover pytest.

    Every assertion above is about protecting the pytest run. If the full-suite
    step ever moves to an ungated job, the filter stops being load-bearing and
    this guard would keep passing while guarding nothing.
    """
    steps = _doc()["jobs"][GATED_JOB]["steps"]
    bodies = [str(s.get("run", "")) for s in steps]
    assert any(_FULL_SUITE_RE.search(b) for b in bodies), (
        f"no step in the '{GATED_JOB}' job runs pytest over all of "
        "`scripts/tests/`. A single-file invocation does not count — this guard "
        "exists to protect the corpus-wide suite. If the full run moved to "
        "another job, repoint the guard at that job."
    )

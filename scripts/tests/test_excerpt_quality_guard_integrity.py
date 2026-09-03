#!/usr/bin/env python3
"""Regression guard: the excerpt-quality guard cannot be quietly removed.

`scripts/tests/test_excerpt_quality.py` (#658) is the only thing asserting that
post excerpts are present, sized, distinct, and not an echo of the title. It is
a **ratchet on a currently-clean corpus** — 287/287 present, 0 title echoes, 0
duplicates as measured 2026-09-02 — which is exactly the shape that disappears
without anyone noticing. Nothing fails when you delete a passing test.

The three ways it stops protecting anything, none of which turn CI red:

  1. the file is deleted or renamed          -> pytest collects nothing
  2. one of its tests is dropped or renamed  -> that dimension goes unchecked
  3. a test is skipped                       -> green, having asserted nothing

This file closes all three. Companion to
`test_ci_posts_paths_filter_guard.py`, which keeps `**_posts/**` in the
`should-build` paths-filter so the suite actually runs when a post changes —
that one guards *whether it runs*, this one guards *whether it still exists*.
Both protect #658's file; neither modifies it.

Direction: presence, plus a floor. Adding tests to the guarded file is free —
the names below are a required subset, not the full inventory, because the file
is expected to grow. Removing, renaming, or skipping one trips this.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD_REL = "scripts/tests/test_excerpt_quality.py"
GUARD = REPO_ROOT / GUARD_REL

# Messages below quote GUARD_REL rather than GUARD.relative_to(REPO_ROOT): an
# assertion message must not be able to raise. relative_to() throws ValueError
# for any path outside the repo, so the failure that reports a missing file
# would itself crash whenever GUARD is repointed — which is precisely what the
# non-vacuity probe for this file does.

# The dimensions #658 established. A subset check, deliberately: the owner
# expects to add assertions, and a count would make a legitimate extension fail.
REQUIRED_TESTS = (
    "test_posts_dir_is_not_empty",
    "test_every_post_has_an_excerpt",
    "test_excerpt_length_is_within_bounds",
    "test_excerpt_does_not_echo_the_title",
    "test_excerpts_are_not_duplicated_across_posts",
)

# The guarded file's own non-vacuity canary: it refuses to pass when the corpus
# glob returns implausibly few posts. Drop it to 0 and all five tests above pass
# by inspecting an empty list.
MIN_POSTS_FLOOR = 200


def _source() -> str:
    return GUARD.read_text(encoding="utf-8")


def test_guard_file_exists():
    assert GUARD.is_file(), (
        f"{GUARD_REL} is gone. It is the only check on "
        "post excerpt quality — presence, length, title echo, cross-post "
        "duplication. If it moved, repoint this guard; if it was deleted on "
        "purpose, delete this guard in the same commit and say why."
    )


def test_required_tests_are_still_declared():
    """Matched as `def <name>(`, not as a substring.

    A substring test would let a longer name satisfy a shorter one —
    `test_every_post_has_an_excerpt` is contained in a hypothetical
    `test_every_post_has_an_excerpt_and_a_title`, so renaming the first to the
    second would read as "still there" while the original assertion was gone.
    """
    src = _source()
    missing = [
        name for name in REQUIRED_TESTS if not re.search(rf"^def {name}\(", src, re.M)
    ]
    assert not missing, (
        f"{len(missing)} excerpt-quality test(s) no longer declared in "
        f"{GUARD_REL}: {missing}. Each one is a dimension nothing else covers "
        "— check_template_echo.py inspects `summary_card` card attributes, not "
        "front-matter `excerpt:`. Adding tests is fine; removing or renaming "
        "one means updating REQUIRED_TESTS here in the same commit."
    )


def test_no_required_test_is_skipped():
    """A skipped test is indistinguishable from a deleted one, but stays green.

    Without this, the name check above is satisfiable by a body of
    `pytest.skip(...)` — the assertion this file exists to protect would report
    success having inspected nothing.
    """
    src = _source()
    skipped = []
    for name in REQUIRED_TESTS:
        m = re.search(rf"^def {name}\(", src, re.M)
        if not m:
            continue  # test_required_tests_are_still_declared owns that failure
        # From the decorator block above the def through the end of its body.
        head = src[: m.start()].rsplit("\n\n\n", 1)[-1]
        body = src[m.start() :].split("\n\n\ndef ", 1)[0]
        if "pytest.mark.skip" in head or re.search(r"\bpytest\.skip\(", body):
            skipped.append(name)
    assert not skipped, (
        f"these excerpt-quality tests are skipped: {skipped}. A skip is a "
        "silent removal — the suite stays green while the dimension goes "
        "unchecked. If the corpus genuinely cannot satisfy one, fix the corpus "
        "or delete the test deliberately rather than parking it."
    )


def test_non_vacuity_floor_not_lowered():
    """The guarded file's own canary must keep refusing an empty corpus.

    Direction is `>=`: raising the floor is fine, lowering it is the weakening.
    At 0 every assertion in that file passes over an empty list — the exact
    "green because it checked nothing" failure the floor was added to prevent.
    """
    m = re.search(r"^MIN_POSTS\s*=\s*(\d+)", _source(), re.M)
    assert m, (
        f"MIN_POSTS is gone from {GUARD_REL}. It is the non-vacuity floor: "
        "without it a broken `_posts/*.md` glob makes every excerpt assertion "
        "pass by inspecting an empty list."
    )
    assert int(m.group(1)) >= MIN_POSTS_FLOOR, (
        f"MIN_POSTS was lowered to {m.group(1)} (floor {MIN_POSTS_FLOOR}). "
        "That is how a scanner starts passing without scanning. If the corpus "
        "really shrank below this, lower MIN_POSTS_FLOOR here in the same "
        "commit and say why."
    )

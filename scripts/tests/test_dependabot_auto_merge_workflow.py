#!/usr/bin/env python3
"""CI config regression guards for .github/workflows/dependabot-auto-merge.yml.

Concrete incident this protects against
----------------------------------------
The workflow once carried an ``Approve PR`` step running
``gh pr review --approve``. Because the repo setting "Allow GitHub Actions to
create and approve pull requests" is disabled by design, that step failed on
EVERY Dependabot PR with::

    failed to create review: GraphQL: GitHub Actions is not permitted to
    approve pull requests. (addPullRequestReview)

which blocked the entire auto-merge workflow (PRs #369/#368/#393/#370). The
step was removed; ``gh pr merge --auto`` does not need it. These guards make a
silent re-introduction of the self-approve anti-pattern — or an accidental
removal of the real auto-merge mechanism — fail loudly and reviewably.

Invariant directions
---------------------
* self-approve step : MUST be ABSENT  (presence => regression)
* ``gh pr merge --auto`` : MUST be PRESENT (absence => merge mechanism lost)
* fetch-metadata pin comment : the pinned SHA must be labelled with the tag it
  actually resolves to (consistency; stale labels break supply-chain audits)

Comments are stripped before scanning for the self-approve / auto-merge tokens,
because the workflow header legitimately *mentions* ``gh pr review --approve``
when explaining why it is not used. A naive substring scan would self-trip.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / ".github" / "workflows" / "dependabot-auto-merge.yml"

# fetch-metadata pin currently in use and the tag it resolves to. If you repin
# fetch-metadata, update BOTH and confirm the SHA resolves to the new tag via
#   gh api repos/dependabot/fetch-metadata/tags
_FETCH_METADATA_SHA = "25dd0e34f4fe68f24cc83900b1fe3fe149efef98"
_FETCH_METADATA_TAG = "v3.1.0"


def _strip_yaml_comments(text: str) -> str:
    """Remove YAML comments line-by-line.

    A ``#`` starts a comment when it is the first non-space character or is
    preceded by whitespace. ``run:`` shell lines in this workflow contain no
    ``#`` inside quotes, so this conservative rule is sufficient and avoids
    matching commentary that merely references a banned token.
    """
    out: list[str] = []
    for line in text.splitlines():
        cut = None
        for i, ch in enumerate(line):
            if ch == "#" and (i == 0 or line[i - 1] in " \t"):
                cut = i
                break
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


@pytest.fixture(scope="module")
def raw() -> str:
    if not TARGET.is_file():
        pytest.skip(f"{TARGET} not found")
    return TARGET.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def code(raw: str) -> str:
    """Workflow text with YAML comments stripped (real steps only)."""
    return _strip_yaml_comments(raw)


def test_target_exists() -> None:
    """Canary: a moved/renamed workflow should fail clearly, not vacuously."""
    assert TARGET.is_file(), f"{TARGET} not found — update this guard if moved."


def test_no_self_approve_step(code: str) -> None:
    """`gh pr review --approve` must NOT be re-introduced (presence=regression).

    The self-approve step fails on every run ("GitHub Actions is not permitted
    to approve pull requests") and is a circular control with no independent
    review value. If you intentionally re-enable PR approval, do it via the
    repo setting + a non-GITHUB_TOKEN identity, and update this guard with the
    rationale.
    """
    assert "gh pr review --approve" not in code, (
        "Self-approve step re-introduced in dependabot-auto-merge.yml. This "
        "fails on every run because 'Allow GitHub Actions to approve PRs' is "
        "disabled by design. Remove it; 'gh pr merge --auto' does not need it."
    )


def test_auto_merge_mechanism_present(code: str) -> None:
    """The actual merge mechanism must remain (absence=broken automation)."""
    assert "gh pr merge --auto" in code, (
        "'gh pr merge --auto' is gone from dependabot-auto-merge.yml — the "
        "workflow no longer auto-merges anything. Restore the auto-merge step."
    )


def test_fetch_metadata_pin_comment_accurate(raw: str) -> None:
    """The fetch-metadata SHA pin must be labelled with the tag it resolves to.

    Stale version comments (the pin said `# v2.4.0` while the SHA was v3.1.0)
    undermine supply-chain audits. If you repin, update _FETCH_METADATA_SHA /
    _FETCH_METADATA_TAG above after confirming the resolution via the API.
    """
    pin_lines = [
        ln for ln in raw.splitlines()
        if "dependabot/fetch-metadata@" in ln and "uses:" in ln
    ]
    assert pin_lines, "fetch-metadata `uses:` pin line not found."
    line = pin_lines[0]
    if _FETCH_METADATA_SHA in line:
        assert _FETCH_METADATA_TAG in line, (
            f"fetch-metadata pinned to {_FETCH_METADATA_SHA[:12]} but comment "
            f"does not say {_FETCH_METADATA_TAG}. The SHA resolves to "
            f"{_FETCH_METADATA_TAG}; fix the comment (or update this guard if "
            f"you repinned)."
        )
        # The previously-wrong label must not linger.
        assert "v2.4.0" not in line, (
            "Stale '# v2.4.0' comment on the fetch-metadata pin — the SHA is "
            f"{_FETCH_METADATA_TAG}."
        )

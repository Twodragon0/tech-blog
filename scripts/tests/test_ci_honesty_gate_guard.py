#!/usr/bin/env python3
"""CI regression guard: the L20 cover honesty scorer must stay BLOCKING.

Why this guard exists
---------------------
L20 digest cover cards display a content-descriptor subheadline, but visual
routing (and thus the honest visual class) is keyed off a separate ``route_hint``
field so the displayed text can NEVER drive routing (see
``scripts/news/l20_dispatch.py`` :func:`_apply_real_content` /
:func:`resolve_digest_band_visuals`, and the unit tests
``test_l20_realcontent.py::TestContentDescriptorSubheadline``).

The CORPUS-LEVEL enforcement of that invariant is the ``score_cover_honesty.py``
gate in ``.github/workflows/svg-lint.yml``: if a future change ever let the
displayed subheadline leak into routing, a band could assert attack evidence its
post lacks, and the ``--strict`` scorer would FAIL the build. That protection
disappears *silently* if someone drops ``--strict``, points ``--baseline`` at a
different file, marks the step ``continue-on-error``, or neutralises it with
``|| true``. This guard makes any such weakening fail loudly and reviewably.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control). Direction: presence /
exact-flag assertions — any removal trips. If a change here is intentional,
update this guard in the same PR and say why.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "svg-lint.yml"
BASELINE = REPO_ROOT / "scripts" / "cover_honesty_baseline.txt"


def _honesty_step_block(text: str) -> str:
    """Return the YAML lines of the ``id: cover_honesty`` step block.

    Spans from the ``- name:`` line that owns ``id: cover_honesty`` to the next
    top-level ``- name:`` step (or EOF). Returns ``""`` when the step is absent.
    """
    lines = text.splitlines()
    # Locate the step whose body declares ``id: cover_honesty``.
    id_idx = next(
        (i for i, ln in enumerate(lines) if re.match(r"\s*id:\s*cover_honesty\b", ln)),
        None,
    )
    if id_idx is None:
        return ""
    # Walk back to the owning ``- name:`` line.
    start = id_idx
    while start >= 0 and not re.match(r"\s*-\s+name:", lines[start]):
        start -= 1
    if start < 0:
        return ""
    indent = len(lines[start]) - len(lines[start].lstrip())
    # Walk forward to the next sibling step at the same indent.
    end = id_idx + 1
    while end < len(lines):
        ln = lines[end]
        if re.match(r"\s*-\s+name:", ln) and (len(ln) - len(ln.lstrip())) == indent:
            break
        end += 1
    return "\n".join(lines[start:end])


def _command_text(block: str) -> str:
    """The step block with comment-only lines removed.

    The honesty step's surrounding docstring/comments legitimately MENTION
    ``--strict`` / ``--baseline``; asserting on those would let the real ``run:``
    flags be deleted while a stale comment kept the guard green. Stripping lines
    whose first non-space char is ``#`` leaves only the executable command, so
    the flag assertions reflect what actually runs. (Skill rule: never match
    commentary.)
    """
    return "\n".join(
        ln for ln in block.splitlines() if not ln.lstrip().startswith("#")
    )


class TestHonestyGateGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_baseline_file_exists(self):
        assert BASELINE.is_file(), (
            f"{BASELINE} not found — the honesty gate's grandfathered baseline "
            "must exist; if relocated, update this guard and the workflow."
        )

    def test_honesty_step_present(self):
        block = _honesty_step_block(WORKFLOW.read_text(encoding="utf-8"))
        assert block, (
            "The 'cover_honesty' step disappeared from svg-lint.yml. This is the "
            "BLOCKING gate that catches a cover asserting attack evidence its post "
            "lacks (the route_hint->routing invariant). If intentional, update "
            "this guard."
        )

    def test_step_runs_strict_scorer_with_baseline(self):
        cmd = _command_text(_honesty_step_block(WORKFLOW.read_text(encoding="utf-8")))
        assert "score_cover_honesty.py" in cmd, "honesty scorer no longer invoked"
        assert "--strict" in cmd, (
            "--strict was removed from the honesty scorer run command; without it "
            "the gate reports but never fails the build, silently disabling "
            "enforcement of the route_hint->routing invariant."
        )
        assert "--baseline scripts/cover_honesty_baseline.txt" in cmd, (
            "the honesty baseline path changed; the gate must grandfather ONLY "
            "scripts/cover_honesty_baseline.txt. If intentional, update this guard."
        )

    def test_step_not_neutralized(self):
        block = _honesty_step_block(WORKFLOW.read_text(encoding="utf-8"))
        cmd = _command_text(block)
        assert "continue-on-error: true" not in block, (
            "the honesty step is marked continue-on-error; a FAIL would no longer "
            "block the build."
        )
        assert "|| true" not in cmd, (
            "the honesty scorer is neutralised with '|| true'; a FAIL would be "
            "swallowed."
        )

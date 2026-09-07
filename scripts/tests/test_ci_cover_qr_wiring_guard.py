#!/usr/bin/env python3
"""Wiring guard: the cover QR gate runs locally, in CI, and in the cron — and
the local one stays scoped to digest covers.

Until 2026-09-07 ``check_cover_qr_urls.py`` ran only in ``check-svg.yml`` and
inside the blogwatcher cron, so **the local publish path had no QR check at
all**. That is the path the 09-04 incident came through: ``f4a459d1`` was a
hand-run publish from a laptop that committed a cover whose QR path data was
the empty string — a blank white square under a "scan / full post" label — and
it then held main red for three days.

The scope assertion is the load-bearing part of this file
-------------------------------------------------------
The gate derives the expected URL from the **cover** filename, which equals the
post's slug only when cover stem == post stem. Digest covers satisfy that by
construction; the rest of the corpus does not.

Measured 2026-09-07 by running the gate over all 336 covers instead of the 214
digests: 12 "failures", **all false positives**. Resolving each cover to its
owner post through the post's ``image:`` field — never by filename stem, which
misreports owners — shows 11 encode the owner post's canonical URL, whose
filename differs from the cover's by case (``..._Governance_and_...`` vs
``..._Governance_And_...``) or by truncation, and the 12th encodes a URL the
post declares in ``redirect_from``. None were broken.

So a well-meaning "why only digests?" widening would block 12 unrelated commits
and train everyone to reach for ``--no-verify``. If you want corpus-wide local
coverage, fix the derivation (resolve cover -> post via ``image:``) first, then
widen this — and update this test with the new measurement.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/check_cover_qr_urls.py"
HOOK = REPO / ".githooks" / "pre-commit"
INSTALL = REPO / "scripts" / "install-hooks.sh"
CHECK_SVG = REPO / ".github" / "workflows" / "check-svg.yml"
BLOGWATCHER = REPO / ".github" / "workflows" / "ai-blogwatcher.yml"

# The staged-cover selector must not widen past digest covers. Matching on the
# distinctive part of the pattern rather than the whole regex keeps this from
# failing on cosmetic edits to the character classes around it.
_DIGEST_SCOPE_RE = re.compile(r"Weekly_Digest_[^'\"\s]*\\\.svg")


def _noncomment(text: str) -> str:
    """Drop comment-only lines.

    Every one of these files explains the gate in prose that names the script,
    so a raw-text match would hit the explanation and keep passing after the
    invocation itself was deleted.
    """
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def test_all_wiring_files_exist():
    """Canary: a renamed file must fail loudly, not vacuously pass."""
    for path in (HOOK, INSTALL, CHECK_SVG, BLOGWATCHER):
        assert path.is_file(), f"{path} not found"


def test_wired_into_active_pre_commit_hook():
    body = _noncomment(HOOK.read_text(encoding="utf-8"))
    assert SCRIPT in body, (
        f"The active .githooks/pre-commit no longer invokes {SCRIPT}. The local "
        "publish path is the one that shipped the 09-04 blank QR. Re-add the "
        "gate and regenerate via scripts/install-hooks.sh."
    )


def test_wired_into_canonical_hook_source():
    """install-hooks.sh regenerates the hook; a gate only in the generated file
    disappears on the next run of the installer."""
    body = _noncomment(INSTALL.read_text(encoding="utf-8"))
    assert SCRIPT in body, (
        f"scripts/install-hooks.sh (the canonical hook source) does not invoke "
        f"{SCRIPT}. Running install-hooks.sh would drop the gate from the "
        "generated hook. Add it to the heredoc."
    )


def test_local_gate_stays_scoped_to_digest_covers():
    """Direction: scope must stay narrow. See the module docstring for the 12."""
    for path in (HOOK, INSTALL):
        body = _noncomment(path.read_text(encoding="utf-8"))
        assert _DIGEST_SCOPE_RE.search(body), (
            f"{path.name}: the staged-cover selector for {SCRIPT} is no longer "
            "restricted to '*Weekly_Digest_*.svg'. Widening it to every cover "
            "produces 12 false positives — the gate derives the expected URL "
            "from the COVER filename, which is only the post slug for digests. "
            "Fix the derivation (cover -> post via the post's image: field) "
            "before widening, and re-measure."
        )


def test_still_wired_into_check_svg_ci_corpus_wide():
    """The local gate is scoped; the corpus-wide CI sweep must remain."""
    body = _noncomment(CHECK_SVG.read_text(encoding="utf-8"))
    assert re.search(rf"python3 {re.escape(SCRIPT)}\s*$", body, re.M), (
        f"check-svg.yml no longer runs a bare `python3 {SCRIPT}` (its default "
        "glob is the whole digest corpus). The pre-commit gate only sees staged "
        "files, so removing this leaves already-committed covers unchecked."
    )


def test_still_wired_into_blogwatcher_cron():
    body = _noncomment(BLOGWATCHER.read_text(encoding="utf-8"))
    assert SCRIPT in body, (
        f"ai-blogwatcher.yml no longer invokes {SCRIPT}. The cron commits covers "
        "with no local hooks, so this is the only gate on that path."
    )

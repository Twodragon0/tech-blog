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
It briefly pinned the local gate to digest covers only, because the gate derived
the expected URL from the **cover** filename and that equals the post's slug only
when cover stem == post stem — true for digests by construction, not for the rest
of the corpus, where running it produced 16 extra failures.

Re-measured the same day: those 16 were **not** false positives. Probed against
production, the cover-derived URL returned **404 for 16/16** and the URL derived
from the owner post — resolved through the post's ``image:`` field, never by
filename stem, which misreports owners — returned **200 for 16/16**. The gate and
``fix_qr_url_in_covers.py`` had each derived it from the filename, so they agreed
with each other while both were wrong, and 16 covers shipped a QR that scans to a
404. One further cover legitimately encodes a ``redirect_from`` target its post
declares, which serves the post, so the derivation accepts those too.

With the derivation fixed and the 16 QRs re-encoded the corpus is 336/336, so the
scope is now the whole corpus. Narrowing it back to digests would silently stop
checking 122 covers.
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

# The staged-cover selector must cover the whole assets/images/*.svg corpus.
# A `Weekly_Digest` fragment in it means someone narrowed the scope back to
# digests, which would stop checking 122 covers.
_CORPUS_SCOPE_RE = re.compile(r"\^assets/images/\[\^/\]\*\\\.svg\$")
_NARROWED_RE = re.compile(r"Weekly_Digest_[^'\"\s]*\\\.svg")


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


def test_local_gate_covers_the_whole_corpus():
    """Direction: scope must stay wide. See the module docstring for the 16."""
    for path in (HOOK, INSTALL):
        body = _noncomment(path.read_text(encoding="utf-8"))
        assert _CORPUS_SCOPE_RE.search(body), (
            f"{path.name}: the staged-cover selector for {SCRIPT} no longer "
            "matches the whole 'assets/images/*.svg' corpus."
        )
        assert not _NARROWED_RE.search(body), (
            f"{path.name}: the staged-cover selector for {SCRIPT} was narrowed "
            "back to '*Weekly_Digest_*.svg'. That stops checking 122 non-digest "
            "covers — and it is where 16 QRs that scan to a 404 were hiding, "
            "because the old cover-filename derivation agreed with the fixer "
            "while both were wrong. The derivation now resolves the owner post "
            "via its image: field and the corpus is 336/336."
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

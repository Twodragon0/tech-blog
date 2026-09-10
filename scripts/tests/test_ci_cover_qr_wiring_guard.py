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


# --- cron self-heal wiring ---------------------------------------------------
#
# The cron gate was blocking with no self-heal while printing the name of a
# deterministic fixer it never ran. On 2026-09-04 that failed the publish and a
# human hand-published the digest hours later (f4a459d1). It now follows the
# self-heal-then-block shape the six post pre-flight steps in the same workflow
# use. These assertions pin the three parts that make that shape a gate rather
# than a rubber stamp: the fixer runs, it runs BEFORE a re-verify, and the
# re-verify is bare (an un-negated, unswallowed invocation is what blocks).

FIXER = "scripts/fix_qr_url_in_covers.py"
_COVER_STEP_RE = re.compile(r"\s*-\s+name:\s*Verify L20 cover\b")


def _cover_step_commands() -> list[str]:
    """Executable (non-comment, non-blank) lines of the cover-verify step."""
    lines = BLOGWATCHER.read_text(encoding="utf-8").splitlines()
    start = next((i for i, ln in enumerate(lines) if _COVER_STEP_RE.match(ln)), None)
    assert start is not None, (
        "the 'Verify L20 cover' step is gone from ai-blogwatcher.yml; this guard "
        "cannot see the QR gate any more. If the step was renamed, update "
        "_COVER_STEP_RE in the same PR."
    )
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if re.match(r"\s*-\s+name:", ln) and (len(ln) - len(ln.lstrip())) == indent:
            break
        end += 1
    return [
        ln for ln in lines[start:end] if ln.strip() and not ln.lstrip().startswith("#")
    ]


def test_cron_qr_gate_has_a_self_heal():
    cmds = _cover_step_commands()
    assert any(FIXER in ln for ln in cmds), (
        f"The cron QR gate no longer runs {FIXER}. It is back to blocking while "
        "telling the log about a fixer nobody invokes — the 2026-09-04 shape, "
        "which cost a publish day and needed a hand-published digest (f4a459d1)."
    )


def test_self_heal_precedes_a_bare_re_verify():
    """Heal first, then block on an un-negated re-run — order is the whole point."""
    cmds = _cover_step_commands()
    fix_i = next(i for i, ln in enumerate(cmds) if FIXER in ln)
    bare = [
        i
        for i, ln in enumerate(cmds)
        if SCRIPT in ln
        and ln.lstrip().startswith("python3")
        and "||" not in ln
        and "if " not in ln
    ]
    assert bare, (
        f"No bare `python3 {SCRIPT}` re-verify in the cover step. Without it the "
        "self-heal decides whether the cover ships, and a cover the fixer could "
        "not repair (no QR block, no owner post) would be published anyway."
    )
    assert any(i > fix_i for i in bare), (
        "the re-verify runs BEFORE the self-heal, so it re-checks the unhealed "
        "cover. Keep the order: gate-in-if -> fixer -> bare gate."
    )


def test_self_heal_does_not_swallow_the_blocking_re_verify():
    cmds = _cover_step_commands()
    for ln in cmds:
        if SCRIPT in ln and ln.lstrip().startswith("python3"):
            assert "|| true" not in ln, (
                f"the blocking `{SCRIPT}` re-verify is neutralised with '|| true'. "
                "A cover with a QR that scans to a 404 would ship silently — the "
                "exact failure the 16-cover incident in this module's docstring "
                "describes. Only the self-heal line may swallow its exit code."
            )

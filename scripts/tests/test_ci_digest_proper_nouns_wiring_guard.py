#!/usr/bin/env python3
"""CI/pre-commit wiring guard for the digest proper-noun canonicalization gate.

check_digest_proper_nouns.py enforces English-canonical proper nouns in digest
bodies (deny-by-default). The enforcement only has teeth if it is actually
wired into (a) the generated pre-commit hook and (b) the svg-lint CI workflow.
Either wire can be dropped silently in an unrelated edit; this guard fails
loudly if that happens.

Direction: presence assertion. If the gate is intentionally moved/renamed,
update this guard in the same PR and say why. See notes/digest-proper-noun-policy.md.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/check_digest_proper_nouns.py"
HOOK = REPO / ".githooks" / "pre-commit"
INSTALL = REPO / "scripts" / "install-hooks.sh"
CI = REPO / ".github" / "workflows" / "svg-lint.yml"
BLOGWATCHER = REPO / ".github" / "workflows" / "ai-blogwatcher.yml"


def _noncomment(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def test_script_exists():
    assert (REPO / SCRIPT).is_file(), f"{SCRIPT} missing (moved/renamed?)"


# The hooks invoke it as: python3 "$REPO_ROOT/scripts/...py" --staged
# so allow an optional closing quote between the path and the --staged flag.
_STAGED_RE = re.compile(rf"{re.escape(SCRIPT)}\"?\s+--staged")


def test_wired_into_active_pre_commit_hook():
    body = _noncomment(HOOK.read_text(encoding="utf-8"))
    assert _STAGED_RE.search(body), (
        "The active .githooks/pre-commit no longer invokes "
        f"'{SCRIPT} --staged'. Digest proper-noun canonicalization is no longer "
        "enforced locally. Re-add the gate (regenerate via scripts/install-hooks.sh)."
    )


def test_wired_into_canonical_hook_source():
    # install-hooks.sh is the canonical source that regenerates .githooks/pre-commit;
    # if the gate is only in the generated file it will vanish on the next re-run.
    body = _noncomment(INSTALL.read_text(encoding="utf-8"))
    assert _STAGED_RE.search(body), (
        "scripts/install-hooks.sh (the canonical hook source) does not invoke "
        f"'{SCRIPT} --staged'. Running install-hooks.sh would drop the gate from "
        "the generated hook. Add it to the heredoc in install-hooks.sh."
    )


def test_wired_into_svg_lint_ci():
    body = _noncomment(CI.read_text(encoding="utf-8"))
    assert re.search(rf"{re.escape(SCRIPT)}\s+--changed", body), (
        "svg-lint.yml no longer runs the digest proper-noun gate "
        f"('{SCRIPT} --changed'). New digests could reintroduce Hangul proper "
        "nouns without CI catching it. Re-add the PR-diff-scoped step."
    )


def test_ci_path_filter_triggers_on_script_change():
    body = CI.read_text(encoding="utf-8")
    # The script must be in the push+PR path filters so edits to it re-run the gate.
    assert body.count(f"'{SCRIPT}'") >= 2, (
        f"'{SCRIPT}' is missing from the push and/or pull_request path filters in "
        "svg-lint.yml; edits to the guard would not trigger the workflow."
    )


def test_blogwatcher_auto_fixes_new_digests():
    # The trusted publish path pushes straight to main, where the svg-lint gate
    # runs --changed. Without an auto --fix at publish time, every new digest
    # with a Hangul proper noun would turn svg-lint red on main. Guard the
    # self-heal so it is not silently dropped.
    body = _noncomment(BLOGWATCHER.read_text(encoding="utf-8"))
    assert re.search(rf"{re.escape(SCRIPT)}\s+--fix", body), (
        "ai-blogwatcher.yml no longer auto-fixes proper nouns in new digests "
        f"('{SCRIPT} --fix'). New digests could push non-canonical proper nouns "
        "to main and turn the svg-lint gate red. Re-add the --fix step."
    )

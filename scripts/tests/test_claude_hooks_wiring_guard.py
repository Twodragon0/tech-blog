#!/usr/bin/env python3
"""Regression guard: no hook script sits in .claude/hooks/ without being wired.

`memory-guard.sh` and `protect-files.sh` were added in `19362c0a` alongside the
rest of the agent setup and **never referenced by settings.json**. Nothing
noticed for months, because an unwired hook is indistinguishable from a working
one by inspection: the file is there, it is executable, it reads like a control.
Both were removed in the commit that added this guard — see that commit message
for why neither was worth wiring instead.

This is the same shape as `check_broken_links` (printed a count, never called
`sys.exit()`) and `check_filename_entities` (wired `--staged`-only, so never run
at `--all`): a control that exists, looks live, and enforces nothing. The repo
has now paid for that pattern three times, so it gets a guard.

Direction: both ways round.
  * a script in .claude/hooks/ that settings.json never names  -> fail
  * a command in settings.json naming a script that is missing -> fail
Adding a hook is fine; adding one and forgetting to wire it is not.

Deliberately not asserted: the executable bit. Every hook is invoked as
`bash "<path>"`, so the mode bit is inert here and pinning it would be
decoration — the thing this file exists to prevent.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"

# Hooks that exist to diagnose one specific open question, not to enforce a
# standing rule — and the date by which that question must be closed out.
#
# A diagnostic carries a standing cost (core-bare-watch is ~140ms on every Bash
# tool call, measured) and stops earning it the moment the question is answered
# or goes cold. This repo has already let three temporary things become
# permanent: memory-guard.sh and protect-files.sh sat unwired for months,
# check_broken_links never called sys.exit() from the day it was written, and
# check_filename_entities was wired --staged-only so it had never run at --all.
# None of those had an owner or a date; all three were found by accident.
#
# So the date is enforced rather than remembered. On expiry the two legitimate
# moves are: delete the hook (the question went cold, or the log answered it),
# or move the date and say in the same commit what is still being waited on.
DIAGNOSTIC_HOOKS = {
    # core.bare flipped to true twice on 2026-09-02 with no identified cause;
    # every plain-git reproduction attempt failed (see the script header), so
    # only observation can catch it. Four weeks of quiet is enough to call it.
    "core-bare-watch.sh": datetime.date(2026, 10, 1),
}


def _hook_commands() -> list[str]:
    """Every `command` string across every event and matcher in settings.json."""
    doc = json.loads(SETTINGS.read_text(encoding="utf-8"))
    out = []
    for groups in (doc.get("hooks") or {}).values():
        for group in groups:
            for hook in group.get("hooks") or []:
                cmd = hook.get("command")
                if isinstance(cmd, str):
                    out.append(cmd)
    return out


def _referenced_scripts() -> set[str]:
    return {
        name
        for cmd in _hook_commands()
        for name in re.findall(r"([A-Za-z0-9_.-]+\.sh)", cmd)
    }


def _scripts_on_disk() -> set[str]:
    return {p.name for p in HOOKS_DIR.glob("*.sh")}


def test_settings_file_exists():
    assert SETTINGS.is_file(), f"{SETTINGS} not found"


def test_hooks_dir_is_not_empty():
    """Canary: an empty glob would make the membership checks pass vacuously."""
    assert _scripts_on_disk(), (
        f"no *.sh under {HOOKS_DIR}. If the hooks moved, repoint this guard; "
        "otherwise both assertions below would pass by comparing empty sets."
    )


def test_settings_declares_at_least_one_hook():
    """Canary for the other side: no commands means nothing to cross-check."""
    assert _hook_commands(), (
        "settings.json declares no hook commands at all. Every script in "
        ".claude/hooks/ would then read as unwired — which is true, but the "
        "interesting failure is one script slipping through, not all of them."
    )


def test_every_hook_script_is_wired():
    orphans = sorted(_scripts_on_disk() - _referenced_scripts())
    assert not orphans, (
        f"{len(orphans)} hook script(s) in .claude/hooks/ are never named by "
        f"settings.json: {orphans}. An unwired hook never runs, and reads to "
        "the next person like an active control. Wire it, or delete it — "
        "leaving it is the option that has already cost this repo twice."
    )


def test_every_wired_script_exists():
    missing = sorted(_referenced_scripts() - _scripts_on_disk())
    assert not missing, (
        f"settings.json wires {len(missing)} script(s) that are not on disk: "
        f"{missing}. The hook fails at runtime, and a failing PostToolUse hook "
        "surfaces only as a stderr line nobody reads."
    )


def test_diagnostic_hooks_have_not_outlived_their_review_date():
    """A diagnostic with a standing cost needs an expiry, not a good intention.

    Direction: today must be on or before each review date. Moving a date
    forward is fine and is the documented escape hatch — it just has to be a
    deliberate edit with a reason, which is the whole point.
    """
    today = datetime.date.today()
    overdue = {
        name: due
        for name, due in DIAGNOSTIC_HOOKS.items()
        if today > due and (HOOKS_DIR / name).is_file()
    }
    assert not overdue, (
        "diagnostic hook(s) past their review date: "
        + ", ".join(f"{n} (due {d})" for n, d in sorted(overdue.items()))
        + ".\nTwo legitimate moves, both one edit:\n"
        "  (a) the question is answered or went cold -> delete the hook, its "
        "settings.json entry, and its DIAGNOSTIC_HOOKS row;\n"
        "  (b) still waiting on something -> move the date here and say what, "
        "in the same commit.\n"
        "Leaving it is the option that turned three earlier temporaries into "
        "permanent fixtures of this repo."
    )


def test_diagnostic_registry_names_real_hooks():
    """Non-vacuity: a renamed hook must not silently leave the registry inert.

    The expiry check skips entries whose file is absent, so that a deleted
    diagnostic does not keep failing CI. That same skip would hide a typo or a
    rename — the row would sit there matching nothing, and the expiry would
    never fire again.
    """
    ghosts = sorted(n for n in DIAGNOSTIC_HOOKS if not (HOOKS_DIR / n).is_file())
    assert not ghosts, (
        f"DIAGNOSTIC_HOOKS names {ghosts}, which are not in .claude/hooks/. "
        "If the hook was removed, drop its row too; if it was renamed, update "
        "the key — otherwise the expiry silently stops applying."
    )

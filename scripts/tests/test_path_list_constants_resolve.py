#!/usr/bin/env python3
"""Every module-level list of repo paths under scripts/ must resolve on disk.

Why this is mechanical rather than a note
-----------------------------------------
On 2026-09-18 the A-H3 self-rerun control in `ops_health_orchestrator.py` was
found inert: it excluded four workflow NAMES from auto-rerun, and after those
four workflows were consolidated into one file named "Ops Orchestrator", not a
single entry matched anything. A name that matches nothing excludes nothing, and
nothing failed — the list still read as a security fix.

The follow-up audit swept every string-list constant in `scripts/` (298
module-level, plus function-local, which is the level A-H3 actually lived at).
Result was a NEGATIVE one: no other control had gone stale. Two spent migration
tools had dead path entries, and that was all.

A negative result decays. This guard is the part that does not: it re-runs the
mechanical half of that audit on every commit, so the next list to rot fails
instead of waiting for someone to sweep again. It would have caught
`DEFAULT_L22_SCRIPTS`.

Deliberate scope limits
-----------------------
* **Module level only.** Function-local lists are overwhelmingly synthetic test
  fixtures (`a.yml`, `2026-02-01-Zeta.md`) that must NOT exist on disk. Scoping
  to module level excludes them by construction rather than by allow-list — and
  an allow-list is the thing that rots.
* **Path-shaped entries only**, and a list qualifies only if ≥60 % of its
  entries are path-shaped, so vocabulary maps are not dragged in.
* Globs, URLs and Liquid fragments are excluded because they are not paths.
  Measured: without those three exclusions this reported 6 lists, 4 of them
  false — `CORPUS_GLOBS` (`_posts/*.md`), `_SEARCH_GLOBS` (`scripts/**/*.py`),
  `INVALID_LINKS` (`https://…json-en.html`), `_GROUND_TRUTH_OPENERS`
  (`{% include news-card.html`). Running the check before wiring it is what
  surfaced that; a gate nobody has run has never been right.

This cannot catch the A-H3 case itself — a workflow NAME is not a path. That one
is pinned by `test_ops_health_orchestrator.test_self_rerun_exclusions_match_live_workflows`.
What generalises is the rule, not the regex: **a control that names its targets
must be asked whether those names still hit anything.**
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOT = REPO_ROOT / "scripts"

# Where a repo-relative entry is allowed to resolve. Entries in these lists are
# written relative to whichever directory their own script treats as the base,
# so the guard accepts any of them rather than guessing one. Guessing is how the
# audit's own first pass produced four false "missing" results.
BASES = (
    "",
    "scripts",
    "scripts/tests",
    "scripts/dev",
    "scripts/build",
    "_posts",
    "assets/images",
    ".github/workflows",
    "_data",
)

_EXT = re.compile(r"\.(py|ya?ml|md|sh|json|js|mjs|rb|html|txt|svg)$")
# Not paths: glob patterns, URLs, Liquid/template fragments, and bare suffixes.
# The last class was added 2026-09-18 when this guard fired on
# `SOURCE_SUFFIXES = (".py", ".yml", ".yaml", ".sh")` in a new dev script — a
# suffix tuple is a filter, not a list of files. Found by the guard doing its
# job on new code, which is the point.
_NOT_A_PATH = re.compile(r"[*?]|://|\{[%{]|^\.\w+$")

# Entries known dead, kept deliberately. Each says what would remove it — an
# exemption without an exit condition is a permanent hole, which this repo has
# already paid for.
KNOWN_DEAD: dict[str, str] = {
    "scripts/upgrade_2026_02_25_to_ultra.py": (
        "extract_cfg_to_yaml.py --all-l22-scripts. Commit 79b003ee ('unify "
        "digest-cover renderer — extract 5 scripts to YAML') completed the "
        "migration these were the input to and deleted them; the 33 resulting "
        "specs are in _data/digest_covers/. No workflow or hook calls the tool. "
        "Remove this entry when the script itself is removed."
    ),
    "scripts/upgrade_2026_04_26_to_ultra.py": "Same as upgrade_2026_02_25_to_ultra.py — deleted by 79b003ee.",
    "scripts/upgrade_2026_04_27_29_to_ultra.py": "Same as upgrade_2026_02_25_to_ultra.py — deleted by 79b003ee.",
    "scripts/upgrade_2026_05_to_ultra.py": "Same as upgrade_2026_02_25_to_ultra.py — deleted by 79b003ee.",
    "scripts/upgrade_5_digest_svgs_to_ultra.py": "Same as upgrade_2026_02_25_to_ultra.py — deleted by 79b003ee.",
    "2026-02-17-Weekly_Tech_Security_Digest_AI_Cloud_Risk.svg": (
        "regenerate_generator_digest_svgs.py TARGET_IMAGES, a one-off regen tool "
        "referenced only from notes/per-pr/. The cover was renamed or retired; "
        "`--list` still prints it and a regen run skips it. Remove this entry "
        "when the tool is removed or its target list is refreshed."
    ),
    "2026-02-18-Krebs_Security_Digest_Kimwolf_Patch_Tuesday.svg": (
        "Same as 2026-02-17-Weekly_Tech_Security_Digest_AI_Cloud_Risk.svg."
    ),
}


def _collection_strings(node: ast.expr) -> list[str] | None:
    """String entries of an all-literal set/list/tuple/frozenset, or dict keys."""
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"frozenset", "set", "tuple", "list"}
    ):
        return _collection_strings(node.args[0]) if node.args else None
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        vals = [
            e.value
            for e in node.elts
            if isinstance(e, ast.Constant) and isinstance(e.value, str)
        ]
        return vals if len(vals) == len(node.elts) and vals else None
    if isinstance(node, ast.Dict):
        keys = [
            k.value
            for k in node.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)
        ]
        return keys if len(keys) == len(node.keys) and keys else None
    return None


def _path_lists() -> list[tuple[str, str, list[str]]]:
    """(relative file, constant name, path-shaped entries) for each qualifying list."""
    found: list[tuple[str, str, list[str]]] = []
    for path in sorted(SCAN_ROOT.rglob("*.py")):
        if "_archive" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in tree.body:  # module level only — see the docstring
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names, value = [node.target.id], node.value
            else:
                continue
            if not names or value is None:
                continue
            entries = _collection_strings(value)
            if not entries or len(entries) < 2:
                continue
            pathish = [
                e for e in entries if _EXT.search(e) and not _NOT_A_PATH.search(e)
            ]
            if len(pathish) / len(entries) < 0.6:
                continue
            found.append(
                (str(path.relative_to(REPO_ROOT)), names[0], pathish),
            )
    return found


def _resolves(entry: str) -> bool:
    return any((REPO_ROOT / base / entry).exists() for base in BASES)


def test_every_path_list_entry_resolves() -> None:
    """A dead entry is silently skipped, shrinking coverage unnoticed."""
    problems: list[str] = []
    for rel, const, entries in _path_lists():
        for entry in entries:
            if _resolves(entry) or entry in KNOWN_DEAD:
                continue
            problems.append(f"{rel}:{const} -> {entry!r} resolves nowhere")
    assert problems == [], (
        "\n".join(problems)
        + "\n\nEither restore/rename the target, drop the entry, or add it to "
        "KNOWN_DEAD with what would remove it. An entry that matches nothing "
        "selects nothing — and nothing fails to tell you."
    )


def test_scanner_is_not_vacuous() -> None:
    """A tightened regex would make the check above pass on an empty set.

    Floor guards the EXTRACTOR, not the count. Measured 2026-09-18: 18 path
    lists across scripts/. A deliberate removal lowers this in the same change,
    with the reason; a collapse toward zero means `_EXT` / `_NOT_A_PATH` /
    `_collection_strings` stopped matching — fix those, do not lower the floor.
    """
    lists = _path_lists()
    assert len(lists) >= 14, (
        f"Only {len(lists)} path-shaped list(s) found (18 on 2026-09-18). The "
        "extractor probably broke."
    )
    total = sum(len(e) for _, _, e in lists)
    assert total >= 100, (
        f"Only {total} path entr(ies) across those lists (146 on 2026-09-18)."
    )


def test_known_dead_entries_are_still_dead() -> None:
    """Remove the exemption when its target comes back.

    Otherwise the list grows stale in the other direction: entries that resolve
    fine but are still excused, so a later break in them goes unreported.
    """
    revived = sorted(e for e in KNOWN_DEAD if _resolves(e))
    assert revived == [], (
        f"{revived} now exist on disk but are still in KNOWN_DEAD. Drop them — "
        "an exemption for a living file hides the next time it dies."
    )


def test_every_exemption_states_what_would_remove_it() -> None:
    """An exemption without an exit condition is permanent by accident."""
    vague = sorted(name for name, why in KNOWN_DEAD.items() if len(why) < 40)
    assert vague == [], (
        f"{vague} are exempted with a reason too short to act on. Say what the "
        "entry was for, why it is dead, and what would take it off the list."
    )


def test_globs_and_urls_are_not_treated_as_paths() -> None:
    """Pins the three exclusions the pre-wiring run found necessary.

    Without them this guard reported 6 lists, 4 of them false. Each string below
    is a real entry from one of those four.
    """
    for not_a_path in (
        "_posts/*.md",  # CORPUS_GLOBS
        "scripts/**/*.py",  # _SEARCH_GLOBS
        "https://www.json.org/json-en.html",  # INVALID_LINKS
        "{% include news-card.html",  # _GROUND_TRUTH_OPENERS
        ".py",  # SOURCE_SUFFIXES — a suffix filter, not a file
        ".yaml",
    ):
        assert _NOT_A_PATH.search(not_a_path), (
            f"{not_a_path!r} would now be treated as a repo path and reported as "
            "dead. It is a glob/URL/Liquid fragment."
        )
    # Not vacuous: a real path must still pass the filter.
    real = "scripts/ops_health_orchestrator.py"
    assert _EXT.search(real) and not _NOT_A_PATH.search(real)
    assert _resolves(real)

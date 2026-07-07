"""Regression guard: scripts/README.md must not document non-existent scripts.

Incident this prevents (2026-07-07 audit): scripts/README.md listed ~15 Python
scripts that no longer existed on disk (a removed audio/video/TTS + link-fixing
pipeline plus a deleted monitor_api_usage.py). The drift silently misled both
human contributors and AI agents, who were shown `python3 scripts/<ghost>.py`
as real commands. 8 dead rows were pruned; this guard keeps them pruned.

Invariant (presence, direction = every documented script must exist):
    For every markdown table row whose FIRST cell is a backtick-wrapped
    `<name>.py`, the file scripts/<name>.py MUST exist.

Deliberate exclusions (legitimately reference files outside scripts/):
- "Replaces" / description columns: only the FIRST cell is treated as the
  documented script, so names cited in later columns are ignored.
- Sections whose heading contains "MOVED": those scripts were relocated to
  another repo (e.g. online-course/scripts/audio_video/) on purpose.

If you intentionally remove a script, delete its README row too. If you add a
script, you may (optionally) document it — the second test only WARNS about
active scripts missing from the README, it does not fail the build.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
README = SCRIPTS_DIR / "README.md"

# First-cell `<name>.py` of a markdown table row, e.g. "| `check_posts.py` | ..."
_ROW_RE = re.compile(r"^\|\s*`([A-Za-z0-9_]+\.py)`\s*\|")
_HEADING_RE = re.compile(r"^#{2,4}\s+(.*)")


def documented_scripts(readme_text: str) -> list[tuple[str, str, int]]:
    """Return (script_name, section_heading, line_no) for every first-column
    `.py` table row, skipping rows under a heading that contains "MOVED"."""
    out: list[tuple[str, str, int]] = []
    section = ""
    for i, line in enumerate(readme_text.splitlines(), start=1):
        h = _HEADING_RE.match(line)
        if h:
            section = h.group(1)
            continue
        m = _ROW_RE.match(line)
        if m and "MOVED" not in section.upper():
            out.append((m.group(1), section, i))
    return out


def test_readme_exists():
    """Canary: a moved/renamed README should fail loudly, not vacuously pass."""
    assert README.is_file(), f"{README} not found (moved or renamed?)"


def test_readme_documents_no_ghost_scripts():
    """Every script documented in scripts/README.md must exist on disk."""
    documented = documented_scripts(README.read_text(encoding="utf-8"))
    assert documented, "parser found zero documented scripts — check _ROW_RE"

    ghosts = [
        (name, section, ln)
        for name, section, ln in documented
        if not (SCRIPTS_DIR / name).is_file()
    ]
    if ghosts:
        lines = "\n".join(
            f"  - {name} (README.md:{ln}, section '{section}') "
            f"-> scripts/{name} does not exist"
            for name, section, ln in ghosts
        )
        pytest.fail(
            "scripts/README.md documents scripts that no longer exist:\n"
            f"{lines}\n\n"
            "Fix: delete the stale table row(s) from scripts/README.md (and "
            "update the section's '(N scripts)' count). If a script was "
            "intentionally relocated, move its entry under a section whose "
            "heading contains 'MOVED'."
        )


def test_readme_missing_active_scripts_warning(recwarn):
    """Non-failing hygiene signal: active scripts absent from the README.

    This does NOT fail the build (documenting every one-shot helper is not
    required); it only surfaces a warning so the gap is visible in -W output.
    """
    documented = {name for name, _, _ in documented_scripts(README.read_text(encoding="utf-8"))}
    on_disk = {p.name for p in SCRIPTS_DIR.glob("*.py")}
    undocumented = sorted(on_disk - documented)
    if undocumented:
        import warnings

        warnings.warn(
            f"{len(undocumented)} scripts/*.py are not documented in README.md "
            f"(informational): {', '.join(undocumented[:10])}"
            + (" ..." if len(undocumented) > 10 else ""),
            stacklevel=1,
        )


# --- Non-vacuous self-verification (skill requirement) ---------------------
# Proves the guard actually trips on a ghost row, using a synthetic string so
# no real file is touched.

def test_guard_is_non_vacuous():
    synthetic = (
        "## All Scripts Reference\n"
        "### Post Validation (1 scripts)\n"
        "| Script | Purpose | Options |\n"
        "|--------|---------|---------|\n"
        "| `definitely_not_a_real_script_xyz.py` | ghost | - |\n"
    )
    parsed = documented_scripts(synthetic)
    assert parsed == [("definitely_not_a_real_script_xyz.py", "Post Validation (1 scripts)", 5)]
    assert not (SCRIPTS_DIR / "definitely_not_a_real_script_xyz.py").is_file()


def test_guard_ignores_replaces_column_and_moved_section():
    """First-cell-only + MOVED-skip must exclude legitimate non-scripts/ refs."""
    synthetic = (
        "## All Scripts Reference\n"
        "### Link Management (1 scripts)\n"
        "| `fix_links_unified.py` | Link fixing | `fix_all_links.py`, `fix_github_links.py` |\n"
        "### Audio/Video Generation (MOVED)\n"
        "| `generate_tts_simple.py` | moved to online-course | - |\n"
    )
    names = [n for n, _, _ in documented_scripts(synthetic)]
    # "Replaces" column names ignored; MOVED-section row ignored.
    assert names == ["fix_links_unified.py"]

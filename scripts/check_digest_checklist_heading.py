"""Canonical `## 실무 체크리스트` heading guard for weekly digests.

The 601 -> 0 structure campaign (PRs #494-#502) ended with every digest owning
exactly one canonical global checklist surface. Nothing stops the cron from
re-introducing a variant tomorrow: `check_digest_structure.py` counts the RAW
SUBSTRING ``"## 실무 체크리스트"`` (unanchored, no heading level), so

    ### 실무 체크리스트          -> contains the substring, counts as 1, PASSES
    ## 실무 체크리스트 (P0/P1)   -> no `$` anchor, counts as 1, PASSES
    ## 9. 실무 체크리스트        -> counts as 0, reported only as the generic
                                    "expected exactly one …, found 0" (tier C)

and the structure gate runs on ``--staged``/``--changed`` only, which the cron's
GitHub-Actions commit never triggers. So a drifted heading lands in the corpus
and is discovered weeks later, by hand.

This gate anchors on the heading line (level + exact text) and runs at publish
time on the freshly written post. Topical item checklists (`#### 마이그레이션
체크리스트`) are NOT the global surface and are never flagged; only headings
that carry the words "실무 체크리스트" without being canonical, or the absence
of the canonical surface entirely.

Exit 1 if any digest lacks exactly one canonical `## 실무 체크리스트`.

Usage:
    python3 scripts/check_digest_checklist_heading.py _posts/2026-08-06-*Weekly_Digest*.md
    python3 scripts/check_digest_checklist_heading.py --staged
    python3 scripts/check_digest_checklist_heading.py --all
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

CANONICAL = "## 실무 체크리스트"
_CANONICAL_TEXT = "실무 체크리스트"

_FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in Path(path).name


def _body(text: str) -> str:
    m = _FRONT_MATTER_RE.match(text)
    return text[m.end():] if m else text


def _strip_code_fences(text: str) -> str:
    """Drop fenced blocks (delimiters and interior) — same contract as R0."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _headings(clean_body: str) -> list:
    """Return (level, text, raw_line) for every heading outside code fences."""
    found = []
    for line in clean_body.split("\n"):
        m = _HEADING_RE.match(line)
        if m:
            found.append((len(m.group(1)), m.group(2).strip(), line.strip()))
    return found


def check_text(text: str) -> list:
    """Return violation strings for one digest body (empty == clean)."""
    headings = _headings(_strip_code_fences(_body(text)))

    canonical = [h for h in headings if h[0] == 2 and h[1] == _CANONICAL_TEXT]
    # A heading that carries the canonical words but is not the canonical form.
    variants = [
        h for h in headings if _CANONICAL_TEXT in h[1] and not (h[0] == 2 and h[1] == _CANONICAL_TEXT)
    ]

    violations = []
    for _level, _t, raw in variants:
        violations.append(
            f"variant checklist heading: {raw!r} (canonical is exactly {CANONICAL!r})"
        )
    if not canonical and not variants:
        candidates = [h[2] for h in headings if "체크리스트" in h[1]]
        hint = f" nearest: {candidates[0]!r}" if candidates else ""
        violations.append(
            f"missing canonical checklist heading {CANONICAL!r}.{hint}"
        )
    elif len(canonical) > 1:
        violations.append(
            f"expected exactly one canonical {CANONICAL!r}, found {len(canonical)}"
        )
    return violations


def check_post(path) -> list:
    path = Path(path)
    if not _is_digest_post(path):
        return []
    return check_text(path.read_text(encoding="utf-8"))


def _all_paths() -> list:
    return sorted(p for p in POSTS_DIR.glob("*.md") if _is_digest_post(p))


def _git_paths(cmd: list) -> list:
    try:
        out = subprocess.check_output(cmd, cwd=str(REPO), stderr=subprocess.DEVNULL, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths = []
    for line in out.splitlines():
        p = line.strip()
        if _POST_PATH_RE.match(p):
            full = REPO / p
            if full.exists() and _is_digest_post(full):
                paths.append(full)
    return sorted(paths)


def _explicit(args_paths: list) -> list:
    paths = []
    for a in args_paths:
        p = Path(a)
        if not p.is_absolute():
            cwd_p = Path.cwd() / p
            p = cwd_p if cwd_p.exists() else REPO / a
        if p.exists() and _is_digest_post(p):
            paths.append(p)
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag Weekly_Digest posts whose global checklist surface is not "
            "exactly one canonical '## 실무 체크리스트' H2 heading."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--changed", metavar="BASE", default=None)
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)

    if args.staged:
        files = _git_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    elif args.changed:
        files = _git_paths(
            ["git", "diff", "--name-only", f"{args.changed}...HEAD", "--diff-filter=ACM"]
        )
    elif args.paths:
        files = _explicit(args.paths)
    else:
        files = _all_paths()

    if not files:
        print("[digest-checklist-heading] No digest post files to check.")
        return 0

    rc = 0
    for path in files:
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        violations = check_post(path)
        if violations:
            rc = 1
            print(f"FAIL {rel}")
            for v in violations:
                print(f"  - {v}")
        else:
            print(f"OK   {rel}")

    if rc:
        print(
            "\n[digest-checklist-heading] FAIL — the global checklist surface "
            "drifted. Numbered ('## N. 실무 체크리스트') forms are auto-fixable "
            "with `python3 scripts/restore_digest_structure.py <post>` (rule R5); "
            "renamed or re-levelled headings need a manual edit to exactly "
            f"'{CANONICAL}'.",
            file=sys.stderr,
        )
    else:
        print(f"[digest-checklist-heading] OK — {len(files)} digest(s), 0 violations.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

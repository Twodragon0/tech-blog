"""Structural invariant guard for weekly-digest posts (Sub-project 0).

Verifies: single contiguous ## 1..N section numbering, no body H1, and a
single checklist surface (global 실무 체크리스트 only). Exit non-zero on any
violation. Run in pre-commit / CI over changed digest posts.

Only ~5 digest posts have been backfilled to satisfy this guard as of
2026-07-16; the ~176 legacy `_posts/*Weekly_Digest*.md` posts still have the
structural defects. Every mode below FILTERS to digest posts only (filename
contains "Weekly_Digest") so non-digest posts are always skipped, and CI
MUST use `--changed <BASE>` (PR-diff-scoped) rather than `--all` until the
corpus-wide backfill lands.

Usage:
    python3 scripts/check_digest_structure.py --staged        # staged digest posts
    python3 scripts/check_digest_structure.py --changed main  # digest posts changed vs BASE
    python3 scripts/check_digest_structure.py --all            # every digest post (legacy will FAIL)
    python3 scripts/check_digest_structure.py path/a.md path/b.md
"""

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")


def _body(text: str) -> str:
    # drop YAML front matter
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[m.end() :] if m else text


def _strip_code_fences(lines: list) -> list:
    """Remove fenced code blocks (``` ... ```) from a list of lines.

    A line toggles fence state when its stripped form starts with three
    backticks. Lines inside a fence, and the fence delimiter lines
    themselves, are excluded from the result. This lets structural checks
    ignore example content (headings, checkboxes, keywords) that only
    appears inside a code/markdown EXAMPLE block.
    """
    out = []
    in_code = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            out.append(ln)
    return out


def check_text(text: str) -> list:
    """Structural violations for a post's full text (front matter included)."""
    body = _body(text)
    lines = _strip_code_fences(body.split("\n"))
    clean_body = "\n".join(lines)
    violations = []

    # (b) no body H1
    for ln in lines:
        if re.match(r"^#\s+\S", ln):
            violations.append(f"body H1 heading found: {ln.strip()[:60]}")

    # (a) numbering: '## N.' headings must be 1,2,3,... contiguous (ignore '## 실무 체크리스트' etc.)
    nums = [
        int(m.group(1)) for ln in lines for m in [re.match(r"^##\s+(\d+)\.", ln)] if m
    ]
    if nums and nums != list(range(1, len(nums) + 1)):
        violations.append(f"broken section numbering: {nums}")

    # (d) single checklist surface. The defect is a CHECKBOX per-item checklist
    # ('- [ ]') duplicating the global P0/P1/P2. Topic-specific prose advisory
    # ('- ' bullets under '#### 권장 조치') is legitimate content and is kept.
    if clean_body.count("## 실무 체크리스트") != 1:
        violations.append(
            f"expected exactly one 실무 체크리스트, found {clean_body.count('## 실무 체크리스트')}"
        )
    # any checkbox item appearing BEFORE the global checklist lives in an item
    # body → it is a per-item checklist (the empirical defect).
    head = clean_body.split("## 실무 체크리스트")[0]
    if re.search(r"^\s*-\s*\[[ xX]?\]", head, re.MULTILINE):
        violations.append(
            "per-item checkbox checklist present in an item body (should be removed)"
        )
    # Heading-anchored, NOT a bare substring: the defect is a per-item
    # "대응 체크리스트" HEADING (## / ### / ####). A bare substring also matched
    # incidental prose like a reference-table cell "랜섬웨어 사고 대응 체크리스트"
    # (false positive surfaced on 2026-02-08). Front-matter excerpts are already
    # excluded by _body(); this narrows the remaining body-prose false positives.
    if re.search(r"^#{2,4}\s+.*대응 체크리스트", clean_body, re.MULTILINE):
        violations.append(
            "per-item 대응 체크리스트 heading present (should be removed)"
        )

    return violations


def check_post(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        return check_text(fh.read())


# --- ratchet ---------------------------------------------------------------
#
# The legacy corpus (~125 digest posts as of 2026-07-31) carries pre-existing
# structural defects that need a staged backfill campaign, NOT a single blast
# (see notes/digest-proper-noun-policy.md §4). Until that lands, a file-scoped
# gate blocks every UNRELATED improvement to those posts too — e.g. a pure
# 비트코인→Bitcoin proper-noun swap trips the gate on defects it did not cause.
#
# --ratchet compares each file against its base revision and fails only on
# violations that are NEW. Pre-existing ones are reported as grandfathered, so
# a legacy post can still be improved while any structural REGRESSION (in new
# and legacy posts alike) still breaks the build. Unlike a baseline file this
# needs no state to keep in sync, and it keeps protecting legacy posts.


def _git_show(rev: str, rel: str):
    """File text at *rev*, or None when the path does not exist there (new file)."""
    try:
        return subprocess.check_output(
            ["git", "show", f"{rev}:{rel}"],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _merge_base(base: str) -> str:
    """Merge base of *base* and HEAD, mirroring `git diff BASE...HEAD` semantics."""
    try:
        return (
            subprocess.check_output(
                ["git", "merge-base", base, "HEAD"],
                cwd=str(REPO),
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            or base
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return base


def _kind(violation: str) -> str:
    """The violation's KIND, with any embedded post content stripped.

    Some messages quote the offending content ("body H1 heading found: # DevSecOps
    관점 분석: AI 기반 피싱, 안드로이드 …", "broken section numbering: [1, 1, 2]").
    Comparing whole strings makes the ratchet content-sensitive: editing a
    *defective* line for an unrelated reason changes the message, so the same
    single defect reads as "one violation disappeared + one new violation appeared".

    Measured 2026-08-04 on 2026-05-05: a pure 안드로이드→Android / 리눅스→Linux
    proper-noun swap kept the defect set identical (6 before, 6 after) yet reported
    "+1 new" — the exact class of spurious block the ratchet exists to remove.

    Keying on the kind and counting per kind keeps regressions visible: adding a
    4th body H1 to a post that already has 3 still trips (count 4 > 3). What it
    deliberately stops flagging is a *reworded* instance of an already-present
    defect, which is not a regression.
    """
    return violation.split(": ", 1)[0]


def new_violations(current: list, base: list) -> list:
    """Violations in *current* with no counterpart of the same kind in *base*.

    Multiset difference over ``_kind()`` rather than raw strings. base=None (the
    file does not exist at the base revision) => every violation is new.
    """
    if base is None:
        return list(current)
    remaining = Counter(_kind(v) for v in base)
    out = []
    for v in current:
        k = _kind(v)
        if remaining[k] > 0:
            remaining[k] -= 1
        else:
            out.append(v)
    return out


def _is_digest_post(path: Path) -> bool:
    """Only Weekly_Digest posts have the structure this guard checks."""
    return "Weekly_Digest" in path.name


def _all_post_paths() -> list:
    """Return all digest _posts/*.md files."""
    return sorted(p for p in POSTS_DIR.glob("*.md") if _is_digest_post(p))


def _staged_post_paths() -> list:
    """Return staged _posts/*.md digest paths from the git index."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
            text=True,
        )
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


def _changed_post_paths(base: str) -> list:
    """Return digest _posts/*.md paths changed vs *base* (e.g. 'main' or 'origin/main')."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base}...HEAD", "--diff-filter=ACM"],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
            text=True,
        )
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


def _explicit_paths(args_paths: list) -> list:
    """Resolve explicit file paths (absolute or relative to cwd / repo), digest-only."""
    paths = []
    for a in args_paths:
        p = Path(a)
        if not p.is_absolute():
            cwd_p = Path.cwd() / p
            p = cwd_p if cwd_p.exists() else REPO / a
        if not p.exists():
            print(f"[digest-structure] WARNING: file not found: {a}", file=sys.stderr)
            continue
        if _is_digest_post(p):
            paths.append(p)
        # Non-digest posts are silently skipped — they have different structure.
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Flag Weekly_Digest _posts/*.md with structural defects (broken "
            "section numbering, body H1, duplicate checklist surface). "
            "Non-digest posts are always skipped. Exits 1 if any violations found."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check staged digest posts (git diff --cached).",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check every digest post (WARNING: legacy un-backfilled posts will FAIL).",
    )
    mode.add_argument(
        "--changed",
        metavar="BASE",
        default=None,
        help="Only check digest posts changed vs BASE (git diff BASE...HEAD).",
    )
    parser.add_argument(
        "--ratchet",
        action="store_true",
        help=(
            "Fail only on violations NEW vs the base revision (HEAD for --staged, "
            "merge-base for --changed). Pre-existing legacy defects are reported as "
            "grandfathered. Lets unrelated improvements land on legacy posts while "
            "still blocking structural regressions."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Explicit post file paths to check (non-digest paths are skipped).",
    )
    args = parser.parse_args()

    base_rev = None
    if args.ratchet:
        if args.staged:
            base_rev = "HEAD"
        elif args.changed:
            base_rev = _merge_base(args.changed)
        else:
            parser.error("--ratchet requires --staged or --changed BASE")

    if args.staged:
        files = _staged_post_paths()
    elif args.changed:
        files = _changed_post_paths(args.changed)
    elif args.paths:
        files = _explicit_paths(args.paths)
    elif args.all:
        files = _all_post_paths()
    else:
        # Default: behave like --all.
        files = _all_post_paths()

    if not files:
        print("[digest-structure] No digest post files to check.")
        sys.exit(0)

    rc = 0
    checked = 0
    grandfathered = 0
    for path in files:
        vs = check_post(str(path))
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        checked += 1

        if base_rev is not None:
            base_text = _git_show(base_rev, str(rel))
            base_vs = None if base_text is None else check_text(base_text)
            fresh = new_violations(vs, base_vs)
            carried = len(vs) - len(fresh)
            grandfathered += carried
            if fresh:
                rc = 1
                print(f"FAIL {rel}  (+{len(fresh)} new, {carried} pre-existing)")
                for v in fresh:
                    print(f"  - {v}")
            elif carried:
                print(
                    f"OK   {rel}  ({carried} pre-existing violation(s) grandfathered)"
                )
            else:
                print(f"OK   {rel}")
            continue

        if vs:
            rc = 1
            print(f"FAIL {rel}")
            for v in vs:
                print(f"  - {v}")
        else:
            print(f"OK   {rel}")

    if rc:
        print(
            f"\n[digest-structure] FAIL — structural violations found in one or "
            f"more of {checked} digest post(s).",
            file=sys.stderr,
        )
    elif base_rev is not None:
        # Never report grandfathered debt silently — it is deferred, not absent.
        print(
            f"[digest-structure] OK (ratchet vs {base_rev}) — {checked} digest post(s) "
            f"checked, 0 new violations, {grandfathered} pre-existing carried over."
        )
    else:
        print(
            f"[digest-structure] OK — {checked} digest post(s) checked, 0 violations."
        )

    sys.exit(rc)


if __name__ == "__main__":
    main()

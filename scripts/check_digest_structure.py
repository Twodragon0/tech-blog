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
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")


def _body(text: str) -> str:
    # drop YAML front matter
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[m.end():] if m else text


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


def check_post(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        body = _body(fh.read())
    lines = _strip_code_fences(body.split("\n"))
    clean_body = "\n".join(lines)
    violations = []

    # (b) no body H1
    for ln in lines:
        if re.match(r"^#\s+\S", ln):
            violations.append(f"body H1 heading found: {ln.strip()[:60]}")

    # (a) numbering: '## N.' headings must be 1,2,3,... contiguous (ignore '## 실무 체크리스트' etc.)
    nums = [int(m.group(1)) for ln in lines
            for m in [re.match(r"^##\s+(\d+)\.", ln)] if m]
    if nums and nums != list(range(1, len(nums) + 1)):
        violations.append(f"broken section numbering: {nums}")

    # (d) single checklist surface. The defect is a CHECKBOX per-item checklist
    # ('- [ ]') duplicating the global P0/P1/P2. Topic-specific prose advisory
    # ('- ' bullets under '#### 권장 조치') is legitimate content and is kept.
    if clean_body.count("## 실무 체크리스트") != 1:
        violations.append(f"expected exactly one 실무 체크리스트, found {clean_body.count('## 실무 체크리스트')}")
    # any checkbox item appearing BEFORE the global checklist lives in an item
    # body → it is a per-item checklist (the empirical defect).
    head = clean_body.split("## 실무 체크리스트")[0]
    if re.search(r"^\s*-\s*\[[ xX]?\]", head, re.MULTILINE):
        violations.append("per-item checkbox checklist present in an item body (should be removed)")
    if "대응 체크리스트" in clean_body:
        violations.append("per-item 대응 체크리스트 heading present (should be removed)")

    return violations


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
        "paths",
        nargs="*",
        help="Explicit post file paths to check (non-digest paths are skipped).",
    )
    args = parser.parse_args()

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
    for path in files:
        vs = check_post(str(path))
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        checked += 1
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
    else:
        print(f"[digest-structure] OK — {checked} digest post(s) checked, 0 violations.")

    sys.exit(rc)


if __name__ == "__main__":
    main()

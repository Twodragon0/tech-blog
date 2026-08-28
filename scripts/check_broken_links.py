#!/usr/bin/env python3
"""Fail on internal /posts/ links in post BODIES that resolve to nothing.

History, because the numbers here are counter-intuitive
------------------------------------------------------
This script existed but was inert: it printed a count, never called
`sys.exit()`, and was wired to no workflow and no hook. Reviving it looked like
a one-line fix — add an exit code — and that would have been wrong. Measured
2026-08-24: it reported **370 broken links, and all 370 were false positives.**

Two causes, both now handled:

1. Its link regex allowed a leading `\\s`, so the YAML list items under
   ``redirect_from:`` in front matter matched. Those are not links; they are
   declarations of old URLs that should redirect *to this post* — the opposite
   of broken. 370 of 370 flagged links were exactly this. Front matter is now
   excluded from the scan.
2. A body link pointing at a URL some post declares in ``redirect_from`` is
   valid: jekyll-redirect-from serves it. So the valid-target set is
   permalinks ∪ every declared ``redirect_from`` target, not permalinks alone.
   This matters here because the site is pinned to ``timezone: UTC`` while posts
   are authored in KST, so a post's filename date and its live URL date can
   differ by one day and the filename-date URL lives in ``redirect_from``
   (see CLAUDE.md, "Date / Timezone Rule").

Body count after both fixes: 0. That is what makes it safe to wire fail-closed
with no legacy ratchet — any hit is fresh drift. Wiring the old version would
have produced a permanently red job, which is the state this repo has twice
decided is worse than no gate at all (see NEVER_CONFIGURED in
scripts/tests/test_ci_secret_absence_guard.py).

Fenced blocks are stripped: a `/posts/...` path inside a code sample is
illustrative text, matching how the other corpus gates here treat fences.

Parsing note: front matter is split with `python-frontmatter` (declared in both
requirements files) rather than a hand-rolled `---` splitter, so this script
needs no entry in ALLOWLIST_FRONT_MATTER in
scripts/tests/test_lib_seam_drift_guard.py. That also means `redirect_from` is
read as real YAML instead of by regex, which handles both the block-list and
inline-list forms for free.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Set, Tuple

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

_FILENAME_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md")
# Markdown link, HTML href, or a bare path preceded by whitespace.
_LINK_RE = re.compile(r"""(?:href=["']|\]\(|\s)(/posts/[^\s)\\'"<>]+/)""")


def parse(path: Path) -> Tuple[dict, str]:
    """Return (metadata, body). Front matter is never scanned for links."""
    try:
        post = frontmatter.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        # A post whose YAML will not parse is check_posts.py's problem, not this
        # gate's. Treat it as bodyless rather than crashing the whole scan.
        return {}, ""
    return dict(post.metadata), post.content


def strip_fences(text: str) -> str:
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def redirect_targets(metadata: dict) -> Set[str]:
    """URLs declared under `redirect_from:` — these resolve, so they are valid.

    YAML gives a list for the block form and for the inline `[a, b]` form, and a
    bare string when someone writes a single value without a list.
    """
    raw = metadata.get("redirect_from")
    if raw is None:
        return set()
    if isinstance(raw, str):
        raw = [raw]
    return {str(x).strip() for x in raw if str(x).strip()}


def valid_targets(posts: Iterable[Path]) -> Set[str]:
    targets: Set[str] = set()
    for path in posts:
        m = _FILENAME_RE.match(path.name)
        if m:
            y, mo, d, title = m.groups()
            targets.add(f"/posts/{y}/{mo}/{d}/{title}/")
        metadata, _ = parse(path)
        targets |= redirect_targets(metadata)
    return targets


def broken_links(path: Path, targets: Set[str]) -> List[str]:
    _, body = parse(path)
    return [
        m.group(1)
        for m in _LINK_RE.finditer(strip_fences(body))
        if m.group(1) not in targets
    ]


def staged_posts() -> List[Path]:
    res = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "--", "_posts"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return [
        REPO_ROOT / line
        for line in res.stdout.split("\n")
        if line.strip().endswith(".md") and (REPO_ROOT / line).exists()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true", help="scan every post (default)")
    scope.add_argument("--staged", action="store_true", help="scan staged posts only")
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    args = parser.parse_args()

    corpus = sorted(POSTS_DIR.glob("*.md"))
    if not corpus:
        print("[broken-links] no posts found", file=sys.stderr)
        return 1

    # Targets always come from the whole corpus: a staged post may legitimately
    # link to a post it does not contain.
    targets = valid_targets(corpus)
    scoped = staged_posts() if args.staged else corpus
    if args.staged and not scoped:
        print("[broken-links] no staged posts — nothing to check.")
        return 0

    offenders = []
    for path in scoped:
        for link in broken_links(path, targets):
            offenders.append(f"{path.name}: {link}")

    if offenders:
        print(
            "[broken-links] FAIL — these body links resolve to no post and no "
            "declared redirect:\n",
            file=sys.stderr,
        )
        for line in offenders:
            print(f"  {line}", file=sys.stderr)
        print(
            f"\n{len(offenders)} broken link(s). Fix the link, or add the URL to the "
            "target post's `redirect_from:` if it is a legitimate old address.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(
            f"[broken-links] OK — {len(scoped)} post(s) scanned against "
            f"{len(targets)} valid target(s), 0 broken."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

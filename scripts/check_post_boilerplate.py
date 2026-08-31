#!/usr/bin/env python3
"""Block byte-identical body blocks from being injected across multiple posts.

Why this gate exists
--------------------
``autonomous_post_modernizer.py`` (removed 2026-08-24) raised each post's
quality score by appending fixed blocks: one of three hardcoded Mermaid
diagrams under the heading "아키텍처 및 워크플로우 다이어그램", and a
byte-identical four-item checklist. It reached 60 published posts — 43 of them
carrying the *same* diagram — and every existing gate passed it:

* ``check_digest_checklist_heading.py`` matches the canonical
  ``## 실무 체크리스트`` string, and the injected heading was a different one.
* ``check_template_echo.py`` inspects news-card ``summary=`` attributes, not
  body prose.
* ``score_cover_honesty.py`` governs cover SVGs, not post bodies.

The scorer that drove the injection rewards the *presence* of a diagram and a
checklist, not their relevance — so slop read as improvement. This gate closes
that loop from the other side: a block that says the same thing in many posts
says nothing about any of them.

What it checks
--------------
Exact-duplicate whole blocks only, which is the demonstrated failure mode:

* a ```mermaid`` fence whose body appears in 2+ posts
* a post's complete set of ``- [ ]`` checklist items appearing in 2+ posts

Individual checklist *lines* are deliberately not checked: 119 posts legitimately
share "클라우드 인프라 보안 설정 정기 감사" from the digest generator's canonical
checklist, so a per-line rule would be all false positives. On the corpus as of
2026-08-24 this gate reports 0 violations across 11 distinct Mermaid fences and
213 distinct checklist sets.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

_MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
_CHECKBOX_RE = re.compile(r"^\s*- \[ \] (.+)$", re.MULTILINE)


def strip_code_fences(text: str) -> str:
    """Drop fenced blocks so fenced checkboxes cannot be counted as real."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def mermaid_bodies(text: str) -> List[str]:
    """Normalised bodies of every Mermaid fence in the post."""
    return [m.group(1).strip() for m in _MERMAID_RE.finditer(text)]


def checklist_signature(text: str) -> Tuple[str, ...]:
    """The post's checklist as an order-independent set of item texts."""
    items = {m.group(1).strip() for m in _CHECKBOX_RE.finditer(strip_code_fences(text))}
    return tuple(sorted(items))


def build_index(
    posts: List[Path],
) -> Tuple[Dict[str, Set[str]], Dict[Tuple[str, ...], Set[str]]]:
    """Map each block to the set of post names carrying it."""
    diagrams: Dict[str, Set[str]] = defaultdict(set)
    checklists: Dict[Tuple[str, ...], Set[str]] = defaultdict(set)
    for path in posts:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for body in mermaid_bodies(text):
            diagrams[body].add(path.name)
        sig = checklist_signature(text)
        if sig:
            checklists[sig].add(path.name)
    return diagrams, checklists


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
    scope.add_argument("--all", action="store_true", help="report on every post")
    scope.add_argument(
        "--staged", action="store_true", help="report only on staged posts"
    )
    args = parser.parse_args()

    corpus = sorted(POSTS_DIR.glob("*.md"))
    if not corpus:
        print("[post-boilerplate] no posts found", file=sys.stderr)
        return 1

    # The duplicate index is always built over the whole corpus: a new post that
    # copies an existing block is a violation even though the old post is clean.
    diagrams, checklists = build_index(corpus)

    scoped = {p.name for p in (staged_posts() if args.staged else corpus)}
    if args.staged and not scoped:
        print("[post-boilerplate] no staged posts — nothing to check.")
        return 0

    violations: List[str] = []

    for body, owners in sorted(diagrams.items()):
        if len(owners) > 1 and owners & scoped:
            first = body.splitlines()[0] if body.splitlines() else "(empty)"
            violations.append(
                f"identical Mermaid diagram in {len(owners)} posts "
                f"[{first[:60]}]: "
                + ", ".join(sorted(owners)[:4])
                + (" ..." if len(owners) > 4 else "")
            )

    for sig, owners in sorted(checklists.items()):
        if len(owners) > 1 and owners & scoped:
            violations.append(
                f"identical checklist ({len(sig)} items) in {len(owners)} posts "
                f"[{sig[0][:50]}]: "
                + ", ".join(sorted(owners)[:4])
                + (" ..." if len(owners) > 4 else "")
            )

    if violations:
        print(
            "[post-boilerplate] FAIL — a body block is repeated verbatim across posts.\n"
            "A block that says the same thing everywhere says nothing anywhere. Write\n"
            "content specific to each post, or remove the block.\n",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(f"\n{len(violations)} violation(s).", file=sys.stderr)
        return 1

    print(
        f"[post-boilerplate] OK — {len(scoped)} post(s) in scope; "
        f"{len(diagrams)} distinct Mermaid fence(s), "
        f"{len(checklists)} distinct checklist(s), 0 duplicates."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

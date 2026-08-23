"""Template-echo card summary guard.

A "template echo" summary says nothing about the article it sits on: it repeats
the headline and bolts on one of three fixed clauses.

    "<제목>를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, …"
    "<제목> 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, …"
    "… 공격 경로·영향 자산·탐지 포인트를 정리하고, …"

490 of them were replaced with body-grounded prose across PRs #521/#525
(2026-08-07 … 08). The corpus is now at **0** — measured over all 259 posts, not
just digests — so this gate has no ratchet and no baseline: any hit is new drift.

Why a gate rather than trusting the fix
---------------------------------------
The clauses no longer appear anywhere in ``scripts/`` — the generator path that
emitted them is gone. That is exactly the state in which a regression is
invisible: nothing fails, the corpus just quietly re-acquires them, and it is
found by hand weeks later (which is how the 490 accumulated). Three enforcement
points, because the corpus has three separate write paths:

* **pre-commit** (``--staged``) — human authoring and repair PRs.
* **CI** (``--all``) — catches anything that reached a branch by another route,
  including a cron push that bypassed local hooks.
* **blogwatcher publish** (explicit path) — the cron's GitHub-Actions commit runs
  with no local hooks at all, so pre-commit never sees the post it writes. There
  the gate runs self-heal-then-block: ``rewrite_template_echo_summaries.py``
  rewrites from the post's own prose (no network, no LLM, contract-enforced), and
  only a defect that survives that blocks the publish.

Detection is deliberately narrow: the three literal clauses, inside a
``summary=`` attribute of a news-item include. Not a similarity heuristic — the
markers are the measured defect class, and a fuzzy "summary resembles title"
rule has no corpus evidence behind it and would fire on legitimately short
summaries.

Exit 1 if any checked post carries a template-echo summary.

Usage:
    python3 scripts/check_template_echo.py --all
    python3 scripts/check_template_echo.py --staged
    python3 scripts/check_template_echo.py --changed origin/main
    python3 scripts/check_template_echo.py _posts/2026-08-08-*Weekly_Digest*.md
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"
sys.path.insert(0, str(REPO))

# Imported, never re-declared (contract C8): the gate and the repair tool must
# agree on what a defect IS, and the card patterns must agree on what a card is.
# A re-spelled ``\{%\s*include`` here would silently skip every ``{%- include``
# card — the miss that made PRs #512/#513 under-fixes.
from scripts.news_card_patterns import CARD_RE, SUMMARY_RE  # noqa: E402
from scripts.rewrite_template_echo_summaries import (  # noqa: E402
    TEMPLATE_MARKERS,
    _is_template_echo,
)

_POST_PATH_RE_PREFIX = "_posts/"


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check_text(text: str) -> list:
    """Return ``(line, marker, excerpt)`` for every template-echo summary."""
    found = []
    for card in CARD_RE.finditer(text):
        match = SUMMARY_RE.search(card.group(0))
        if not match:
            continue
        value = match.group(2)
        if not _is_template_echo(value):
            continue
        marker = next(m for m in TEMPLATE_MARKERS if m in value)
        line = _line_of(text, card.start() + match.start(2))
        excerpt = value if len(value) <= 90 else value[:87] + "…"
        found.append((line, marker, excerpt))
    return found


def check_post(path) -> list:
    return check_text(Path(path).read_text(encoding="utf-8"))


def _all_paths() -> list:
    return sorted(POSTS_DIR.glob("*.md"))


def _git_paths(cmd: list) -> list:
    try:
        out = subprocess.check_output(
            cmd, cwd=str(REPO), stderr=subprocess.DEVNULL, text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths = []
    for line in out.splitlines():
        rel = line.strip()
        if not rel.startswith(_POST_PATH_RE_PREFIX) or not rel.endswith(".md"):
            continue
        if "/" in rel[len(_POST_PATH_RE_PREFIX) :]:
            continue
        full = REPO / rel
        if full.exists():
            paths.append(full)
    return sorted(paths)


def _explicit(args_paths: list) -> list:
    paths = []
    for arg in args_paths:
        p = Path(arg)
        if not p.is_absolute():
            cwd_p = Path.cwd() / p
            p = cwd_p if cwd_p.exists() else REPO / arg
        if p.exists():
            paths.append(p)
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag posts whose news-card summary= only echoes the headline plus "
            "one of three fixed template clauses."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--changed", metavar="BASE", default=None)
    parser.add_argument("paths", nargs="*")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only failures and the final summary line",
    )
    args = parser.parse_args(argv)

    if args.staged:
        files = _git_paths(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
        )
    elif args.changed:
        files = _git_paths(
            [
                "git",
                "diff",
                "--name-only",
                f"{args.changed}...HEAD",
                "--diff-filter=ACM",
            ]
        )
    elif args.paths:
        files = _explicit(args.paths)
    else:
        files = _all_paths()

    if not files:
        print("[template-echo] No post files to check.")
        return 0

    rc = 0
    defects = 0
    for path in files:
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        hits = check_post(path)
        if hits:
            rc = 1
            defects += len(hits)
            print(f"FAIL {rel}")
            for line, marker, excerpt in hits:
                print(f"  {rel}:{line}: template clause {marker!r}")
                print(f'    summary="{excerpt}"')
        elif not args.quiet:
            print(f"OK   {rel}")

    if rc:
        print(
            f"\n[template-echo] FAIL — {defects} template-echo summary(ies). "
            "These describe no article. Repair them from the post's own prose:\n"
            "    python3 scripts/rewrite_template_echo_summaries.py <post>\n"
            "Spotlight items have no prose to lift, so they are handled by "
            "`--mode drop` (the attribute is deleted rather than kept lying).",
            file=sys.stderr,
        )
    else:
        print(f"[template-echo] OK — {len(files)} post(s), 0 template-echo summaries.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

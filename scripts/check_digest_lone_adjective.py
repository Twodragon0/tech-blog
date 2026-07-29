"""Lone-adjective+AI panel guard for weekly-digest posts (publish-time pre-flight).

A digest's ``summary_card.highlights[].title`` feeds the L20 cover side-cards
via ``build_lead_headline``. When a title reads "<Word> AI, …" and the lead
resolves to a lone ``<Word>``, the cover shows a bare adjective panel. That is
allowed ONLY when the word is vetted in ``_AI_COMPOUND_ADJECTIVES`` (join, e.g.
"Agentic AI") or ``_DEFERRED_AI_ADJECTIVES`` (lone lead is correct, e.g. the
"Claude" brand). Otherwise ``TestCorpusNoLoneAdjectiveAi`` fails on ``main``
AFTER the cron pushes the digest — a silent, delayed break (observed 2026-07-29
"Claude AI").

This CLI runs the SAME check scoped to specific posts so the blogwatcher
publish path surfaces the exact offending word + remediation at publish time,
instead of a cryptic corpus-test failure discovered later. It is a DETECTION
guard: a lone-adjective panel needs a human vetting decision (join vs defer), so
it is never auto-fixed.

Exit 1 if any unvetted lone-adjective+AI panel is found.

Usage:
    python3 scripts/check_digest_lone_adjective.py _posts/2026-07-29-*Weekly_Digest*.md
    python3 scripts/check_digest_lone_adjective.py --staged
    python3 scripts/check_digest_lone_adjective.py --all
"""
import argparse
import glob
import html as _html
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"
sys.path.insert(0, str(REPO))

from scripts.news.l20_dispatch import (  # noqa: E402
    build_lead_headline,
    _AI_COMPOUND_ADJECTIVES,
    _DEFERRED_AI_ADJECTIVES,
)

_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def check_post(path: str) -> list:
    """Return offender strings for one post (empty == clean)."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
    if not m:
        return []
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return []
    if not isinstance(fm, dict):
        return []
    sc = fm.get("summary_card")
    if not isinstance(sc, dict):
        return []
    offenders = []
    for hl in sc.get("highlights", []) or []:
        title = (hl.get("title", "") or "") if isinstance(hl, dict) else ""
        lead = build_lead_headline(title)
        if not lead or " " in lead:
            continue
        # literal "<lead> AI" adjacency (AI standalone, not "OpenAI")
        if re.search(rf"\b{re.escape(lead)}\s+AI\b", _html.unescape(title)):
            low = lead.lower()
            if low in _AI_COMPOUND_ADJECTIVES or low in _DEFERRED_AI_ADJECTIVES:
                continue
            offenders.append(f"lone {lead!r} <- {title[:70]!r}")
    return offenders


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
            "Flag Weekly_Digest posts whose summary_card highlights would render "
            "an unvetted lone-adjective+AI cover panel (TestCorpusNoLoneAdjectiveAi "
            "would fail on main). Detection only — vetting is a human decision."
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
        files = _git_paths(["git", "diff", "--name-only", f"{args.changed}...HEAD", "--diff-filter=ACM"])
    elif args.paths:
        files = _explicit(args.paths)
    else:
        files = _all_paths()

    if not files:
        print("[digest-lone-adjective] No digest post files to check.")
        return 0

    rc = 0
    for path in files:
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        offenders = check_post(str(path))
        if offenders:
            rc = 1
            print(f"FAIL {rel}")
            for o in offenders:
                print(f"  - {o}")
        else:
            print(f"OK   {rel}")

    if rc:
        print(
            "\n[digest-lone-adjective] FAIL — unvetted lone-adjective+AI cover "
            "panel(s). Vet each word in scripts/news/l20_dispatch.py: add to "
            "_AI_COMPOUND_ADJECTIVES if the join fixes the cover (e.g. 'Agentic "
            "AI'), or _DEFERRED_AI_ADJECTIVES if the lone lead is correct (e.g. a "
            "brand like 'Claude'). This mirrors TestCorpusNoLoneAdjectiveAi.",
            file=sys.stderr,
        )
    else:
        print(f"[digest-lone-adjective] OK — {len(files)} digest(s) checked, 0 offenders.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

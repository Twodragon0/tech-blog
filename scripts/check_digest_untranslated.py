"""Untranslated-English guard for weekly-digest posts.

Weekly digests are auto-generated. When the translation fallback chain
(Gemini CLI -> DeepSeek API -> raw English) has no API key available — which
happens on the `repository_dispatch` publish path where LLM secrets are
intentionally zeroed out for security — the `#### 요약` prose and
`summary="..."` news-card fields are emitted as raw ENGLISH RSS text instead
of Korean. This guard flags that regression so it never lands silently.

Detection (per 요약 block / summary= field):
  1. Strip legitimately-English spans: quoted article titles ('...' / "...")
     and parenthetical glosses ((next-best-product)). A Korean sentence that
     merely *cites* an English headline is NOT a violation.
  2. On the remainder, an English SENTENCE is present when there are >= 3
     English stop-words AND the Hangul ratio is < 0.55 (i.e. the prose itself
     is English, not Korean-with-proper-nouns).

Only Weekly_Digest posts are checked; every mode filters to them. Mirrors the
CLI of check_digest_structure.py.

Usage:
    python3 scripts/check_digest_untranslated.py --staged        # staged digest posts
    python3 scripts/check_digest_untranslated.py --changed main  # digest posts changed vs BASE
    python3 scripts/check_digest_untranslated.py --all           # every digest post
    python3 scripts/check_digest_untranslated.py path/a.md path/b.md
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")

# English function words that signal an English *sentence* (not a proper noun).
_STOP = frozenset(
    "the a an is are was were with that this these those has have had been will "
    "from into over under between during about their its his her they them we you "
    "which who whom whose when where while because although though and or but of "
    "to in on for by as at it he she can could would should may might must not".split()
)

# Quote characters that wrap a cited English title/phrase.
_QUOTES = "\"'‘’“”″‟"
# A quoted span: opening quote, >=2 non-quote chars, closing quote.
_QUOTED_SPAN = re.compile(rf"[{_QUOTES}][^{_QUOTES}]{{2,}}?[{_QUOTES}]")
# A parenthetical gloss that is mostly ASCII (e.g. "(next-best-product)").
_ASCII_PAREN = re.compile(r"\([A-Za-z0-9 .,&'/+-]{2,}\)")
# A multi-word proper-noun sequence: 2+ consecutive Capitalized/ALL-CAPS tokens
# (e.g. "GeForce NOW", "The Adventures of Elliot: The Millennium Tales",
# "Steam Summer Sale"). Real English PROSE is distinguished by *lowercase*
# function words (is/the/with/that) mid-sentence; a Title-Cased headline is a
# cited name, not prose, so we strip it before counting stop-words. Small
# joiners (of/the/and/&/:/-) are allowed *inside* such a run.
_PROPER_SEQ = re.compile(
    r"\b[A-Z][A-Za-z0-9]*(?:[ :/&-]+(?:of|the|and|for|in|on|[A-Z][A-Za-z0-9]*))+\b"
)


def _body(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[m.end() :] if m else text


def _strip_code_fences(text: str) -> str:
    out, in_code = [], False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            out.append(ln)
    return "\n".join(out)


def _summary_blocks(body: str) -> list:
    """Every '#### 요약' prose block (text up to the next heading / rule / blank-gap)."""
    return re.findall(
        r"####\s*요약\s*\n+(.+?)(?:\n\n|\n####|\n---|\n##\s)", body, flags=re.S
    )


def _summary_fields(body: str) -> list:
    """Every news-card summary="..." attribute value."""
    return re.findall(r'summary="([^"]+)"', body)


def is_untranslated(text: str) -> bool:
    """True when *text* contains an English sentence (not just cited titles)."""
    # Drop cited English titles / ASCII glosses / Title-Cased proper-noun
    # sequences first, then URLs — what remains is candidate PROSE.
    stripped = _QUOTED_SPAN.sub(" ", text)
    stripped = _ASCII_PAREN.sub(" ", stripped)
    stripped = _PROPER_SEQ.sub(" ", stripped)
    stripped = re.sub(r"https?://\S+", " ", stripped)

    words = re.findall(r"[A-Za-z]+", stripped.lower())
    stops = sum(1 for w in words if w in _STOP)
    hangul = len(re.findall(r"[가-힣]", stripped))
    ascii_letters = len(re.findall(r"[A-Za-z]", stripped))
    hangul_ratio = hangul / (hangul + ascii_letters + 1)
    return stops >= 3 and hangul_ratio < 0.55


def check_post(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        body = _strip_code_fences(_body(fh.read()))
    violations = []
    for i, block in enumerate(_summary_blocks(body), 1):
        if is_untranslated(block):
            snippet = re.sub(r"\s+", " ", block.strip())[:70]
            violations.append(f"영문 요약 블록 #{i}: {snippet}")
    for i, field in enumerate(_summary_fields(body), 1):
        if is_untranslated(field):
            snippet = re.sub(r"\s+", " ", field.strip())[:70]
            violations.append(f"영문 summary= 필드 #{i}: {snippet}")
    return violations


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def _all_post_paths() -> list:
    return sorted(p for p in POSTS_DIR.glob("*.md") if _is_digest_post(p))


def _git_post_paths(cmd: list) -> list:
    try:
        out = subprocess.check_output(
            cmd, cwd=str(REPO), stderr=subprocess.DEVNULL, text=True
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


def _staged_post_paths() -> list:
    return _git_post_paths(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    )


def _changed_post_paths(base: str) -> list:
    return _git_post_paths(
        ["git", "diff", "--name-only", f"{base}...HEAD", "--diff-filter=ACM"]
    )


def _explicit_paths(args_paths: list) -> list:
    paths = []
    for a in args_paths:
        p = Path(a)
        if not p.is_absolute():
            cwd_p = Path.cwd() / p
            p = cwd_p if cwd_p.exists() else REPO / a
        if not p.exists():
            print(
                f"[digest-untranslated] WARNING: file not found: {a}", file=sys.stderr
            )
            continue
        if _is_digest_post(p):
            paths.append(p)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Flag Weekly_Digest _posts/*.md whose 요약/summary= fields contain raw "
            "untranslated English (translation-fallback regression). Cited English "
            "titles inside Korean prose are NOT flagged. Exits 1 if any found."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check staged digest posts (git diff --cached).",
    )
    mode.add_argument("--all", action="store_true", help="Check every digest post.")
    mode.add_argument(
        "--changed",
        metavar="BASE",
        default=None,
        help="Only check digest posts changed vs BASE (git diff BASE...HEAD).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Explicit post file paths (non-digest paths are skipped).",
    )
    args = parser.parse_args()

    if args.staged:
        files = _staged_post_paths()
    elif args.changed:
        files = _changed_post_paths(args.changed)
    elif args.paths:
        files = _explicit_paths(args.paths)
    else:
        files = _all_post_paths()

    if not files:
        print("[digest-untranslated] No digest post files to check.")
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
            f"\n[digest-untranslated] FAIL — untranslated English found in one or "
            f"more of {checked} digest post(s). Translate 요약/summary= to Korean "
            f"(preserve proper nouns / CVE IDs).",
            file=sys.stderr,
        )
    else:
        print(
            f"[digest-untranslated] OK — {checked} digest post(s) checked, 0 violations."
        )

    sys.exit(rc)


if __name__ == "__main__":
    main()

"""Proper-noun canonicalization guard for weekly-digest posts.

Policy (decided 2026-07-28, owner call — see notes/digest-proper-noun-policy.md):
digest BODY proper nouns use the **English canonical** spelling. Empirically the
worst offender was intra-document mixing: 112 of 194 digests used *both*
비트코인 and Bitcoin in the same file.

This guard is **deny-by-default**: only the Hangul forms in ``ENTITIES`` are
ever flagged or rewritten. An unlisted Hangul token is never touched (the entity
over-matching lesson from the L20 topic-tag guard).

Scope & masking:
  * Only the post BODY is inspected — front matter (title:/excerpt:) is owned by
    the re-translate workflow (재발 방지 B) and left untouched.
  * These spans are masked out before detection AND skipped during --fix, so a
    Hangul form inside them is preserved: fenced/inline code, cited quoted
    titles ('...'/"..."), URLs, and CVE IDs.
  * Replacement is **josa-aware**: 구글 → Google, 구글은 → Google은, 구글의 →
    Google의 (particle preserved), but 구글링 (a derived verb) is left ALONE
    because 링 is not a particle. This prevents mangling Korean derivations.

Only Weekly_Digest posts are checked; every mode filters to them. Mirrors the
CLI of check_digest_untranslated.py.

Usage:
    python3 scripts/check_digest_proper_nouns.py --staged        # staged digest posts
    python3 scripts/check_digest_proper_nouns.py --changed main  # digest posts changed vs BASE
    python3 scripts/check_digest_proper_nouns.py --all           # every digest post (report only)
    python3 scripts/check_digest_proper_nouns.py --fix --staged  # rewrite Hangul forms -> canonical
    python3 scripts/check_digest_proper_nouns.py path/a.md
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

_POST_PATH_RE = re.compile(r"^_posts/[^/]+\.md$")

# --- Canonical map (deny-by-default allow-list): Hangul form -> English -------
# Only these Hangul spellings are ever flagged/rewritten. Grow this list only
# after measuring that an entity is genuinely mixed across digests.
ENTITIES = {
    "비트코인": "Bitcoin",
    "이더리움": "Ethereum",
    "쿠버네티스": "Kubernetes",
    "리눅스": "Linux",
    "도커": "Docker",
    "구글": "Google",
    "마이크로소프트": "Microsoft",
    "아마존": "Amazon",
    "깃허브": "GitHub",
    "클라우드플레어": "Cloudflare",
    # 2026-07-29 corpus-vetted additions (post-researcher measurement): genuine
    # Hangul/English mixing with NO substring-collision trap. Deliberately EXCLUDES
    # 애플 (→애플리케이션/application collision, ~0 genuine), 리플 (→리플래시/리플리카),
    # and domestic-only 네이버/카카오 (never written in English) +
    # already-English-canonical OpenAI/Nvidia/Ubuntu/… — tracked in
    # notes/digest-proper-noun-policy.md.
    "안드로이드": "Android",   # 6 files mixed; always standalone ("안드로이드 악성/펌웨어")
    "텔레그램": "Telegram",     # mixed; always standalone ("텔레그램 봇/기반/지갑")
    # 2026-07-30 additions: previously DEFERRED on a naive-substring premise, but
    # the josa+word-boundary matcher (_ENTITY_RE) already resolves their compound
    # noise, so NO bespoke exclusion is needed. Verified with the real matcher on
    # the digest corpus (see notes/digest-proper-noun-policy.md §2 re-measurement).
    "메타": "Meta",       # 21/21 genuine (메타의 광고, 메타가 크리에이터, 메타의 파이썬).
                          # 메타데이터/메타버스/메타분석/메타문자 = 메타+Hangul-non-josa →
                          # already excluded by the lookahead (0 leaks).
    "시스코": "Cisco",     # 2/2 genuine (시스코가 분기 실적, 시스코 Unified). 샌프란시스코 =
                          # 시스코 embedded in a larger Hangul token → already excluded by the
                          # (?<![가-힣…]) lookbehind (0 leaks).
    # 윈도우 (→Windows) STAYS DEFERRED: genuine homonym. The "window" sense
    # (컨텍스트/안정화/슬라이딩/익스플로잇 윈도우, "블록 N 윈도우", "유지보수 기간(윈도우)")
    # cannot be regex-separated from the OS sense — a deny-prefix still leaves ~25%
    # false positives (intervening numbers/parens defeat the prefix anchor). Any
    # genuine Windows mixing must be fixed per-post by hand, not auto-canonicalized.
}

# Common Korean particles (josa) that legitimately attach to a noun. When one of
# these directly follows an entity it is preserved (구글은 -> Google은). Ordered
# longest-first so the alternation is greedy where it matters.
_JOSA = [
    "으로서", "으로써", "에서는", "에게서", "이라는", "라는", "이라고", "라고",
    "으로", "에서", "에게", "한테", "부터", "까지", "보다", "처럼", "같이",
    "이나", "이란", "이든", "든지", "조차", "마저", "밖에", "만큼", "이랑",
    "은", "는", "이", "가", "을", "를", "의", "와", "과", "도", "만", "로",
    "에", "랑", "나", "뿐", "및",
]
_JOSA_ALT = "|".join(sorted(_JOSA, key=len, reverse=True))

# Per-entity deny lookahead: a trailing context that proves the Hangul form is
# NOT the entity. Only add one after measuring a real corpus false positive.
#
# 메타: also a productive Sino-Korean prefix ("meta-"). The compound-noun senses
# (메타데이터/메타버스/메타분석) are already excluded because 데이터/버스/분석 are
# Hangul, but the HYPHENATED prefix (메타-하네스 = "meta-harness") passes the
# [^가-힣] branch and would be rewritten to the nonsense "Meta-하네스".
# Measured 2026-07-31 across the digest corpus: entity+hyphen occurs 4x total —
# 메타-하네스 x2 (2026-07-30, prefix sense) and 비트코인-REIT x2 (2026-06-18,
# genuine Bitcoin). So the rule must be per-entity: a blanket hyphen exclusion
# would silently skip the two legitimate 비트코인-REIT rewrites.
#
# 2026-08-04 — the prefix sense also occurs SPACE-separated, which the hyphen
# deny alone lets through (a space also satisfies the [^가-힣] branch). Measured
# across ALL of _posts/, 메타 + separator + token occurs 4x:
#
#   SPACE  + 광고의     x3  (2026-07-16, digest)      genuine Meta — must rewrite
#   SPACE  + 주제입니다  x1  (2026-02-02, NON-digest)  prefix ("메타 주제")
#   HYPHEN + 하네스     x2  (2026-07-30, digest)      prefix (denied above)
#
# NOTE on evidence strength: 2026-02-02-Weekly_Tech_AI_Blockchain_Digest.md is
# OUTSIDE this guard's scope (_is_digest_post requires "Weekly_Digest" in the
# filename), so 메타 주제 is NOT a measured false positive *of the guard*. It is
# kept as a narrow, PREVENTIVE deny because it proves the author does write that
# phrase, and ai-blogwatcher.yml runs --fix automatically at publish time: the day
# a cron digest uses it, the body would be silently corrupted to "Meta 주제".
# The deny is an enumeration of the specific prefix noun, not a blanket "메타 +
# space" rule — a blanket rule would wrongly skip the 3 genuine 메타 광고 rewrites.
_ENTITY_DENY = {
    "메타": r"[-–—]|\s*주제",
}

# Per-entity matcher: the Hangul form, NOT embedded in a larger Hangul/Latin
# token, and followed by end-of-string, a non-Hangul char, or a known particle.
# 구글링 fails all three lookahead branches (링 is Hangul and not a particle),
# so a derived word is never rewritten.
_ENTITY_RE = {
    ko: re.compile(
        rf"(?<![가-힣A-Za-z0-9]){re.escape(ko)}"
        + (rf"(?!{_ENTITY_DENY[ko]})" if ko in _ENTITY_DENY else "")
        + rf"(?=$|[^가-힣]|(?:{_JOSA_ALT}))"
    )
    for ko in ENTITIES
}

# Spans preserved verbatim (masked for detection, skipped for --fix).
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_URL = re.compile(r"https?://\S+")
_CVE = re.compile(r"CVE-\d{4}-\d{3,7}", re.IGNORECASE)
_QUOTES = "\"'‘’“”"
# A cited title inside prose ("...법의 미래"). The (?<!=) guard means a news-card
# attribute value — title="...", summary="...", source="..." — is NOT treated as
# a cited title: those are translated display copy and MUST be canonicalized too,
# otherwise the prose says "Bitcoin" while the adjacent card says "비트코인" (the
# very intra-document mixing this guard exists to kill). Empirically verified on
# 2026-07-23 digest before shipping.
_QUOTED_SPAN = re.compile(rf"(?<!=)[{_QUOTES}][^{_QUOTES}\n]{{2,}}?[{_QUOTES}]")

_PROTECTED = [_FENCED_CODE, _INLINE_CODE, _URL, _CVE, _QUOTED_SPAN]


def _split_front_matter(text: str) -> tuple:
    """Return (front_matter_including_delimiters, body). Body is everything after
    the closing '---'. Front matter is never modified by this guard."""
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return "", text


def _protected_spans(body: str) -> list:
    """Merged, sorted (start, end) intervals that must be preserved verbatim."""
    spans = []
    for rx in _PROTECTED:
        for m in rx.finditer(body):
            spans.append((m.start(), m.end()))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def _unprotected_segments(body: str) -> list:
    """Yield (text, is_protected) segments covering the whole body in order."""
    segs = []
    pos = 0
    for s, e in _protected_spans(body):
        if s > pos:
            segs.append((body[pos:s], False))
        segs.append((body[s:e], True))
        pos = e
    if pos < len(body):
        segs.append((body[pos:], False))
    return segs


def find_violations(body: str) -> list:
    """Return [(hangul, canonical, count)] for entity Hangul forms present in the
    UNPROTECTED body. Empty list == compliant."""
    searchable = "".join(t for t, prot in _unprotected_segments(body) if not prot)
    out = []
    for ko, en in ENTITIES.items():
        n = len(_ENTITY_RE[ko].findall(searchable))
        if n:
            out.append((ko, en, n))
    return out


def fix_body(body: str) -> tuple:
    """Return (new_body, total_replacements). Only unprotected segments are
    rewritten; particles are preserved by the lookahead (구글은 -> Google은)."""
    total = 0
    parts = []
    for text, prot in _unprotected_segments(body):
        if prot:
            parts.append(text)
            continue
        for ko in ENTITIES:
            text, n = _ENTITY_RE[ko].subn(ENTITIES[ko], text)
            total += n
        parts.append(text)
    return "".join(parts), total


def check_post(path: str) -> list:
    """Return human-readable violation strings for one post (report mode)."""
    with open(path, encoding="utf-8") as fh:
        _, body = _split_front_matter(fh.read())
    violations = []
    for ko, en, n in find_violations(body):
        violations.append(f"{ko} -> {en} ({n}회)")
    return violations


def fix_post(path: Path) -> int:
    """Rewrite Hangul entity forms to canonical English in the body. Returns the
    number of replacements (0 == file untouched)."""
    original = path.read_text(encoding="utf-8")
    fm, body = _split_front_matter(original)
    new_body, n = fix_body(body)
    if n:
        path.write_text(fm + new_body, encoding="utf-8")
    return n


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
            print(f"[digest-proper-nouns] WARNING: file not found: {a}", file=sys.stderr)
            continue
        if _is_digest_post(p):
            paths.append(p)
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce English-canonical proper nouns in Weekly_Digest _posts/*.md "
            "bodies (deny-by-default allow-list). Cited titles / code / URLs / CVE "
            "IDs and the front matter are preserved. Exits 1 if any Hangul form is "
            "found; --fix rewrites them in place."
        )
    )
    parser.add_argument("--fix", action="store_true",
                        help="Rewrite Hangul entity forms to canonical English in place.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true",
                      help="Only process staged digest posts (git diff --cached).")
    mode.add_argument("--all", action="store_true",
                      help="Process every digest post.")
    mode.add_argument("--changed", metavar="BASE", default=None,
                      help="Only process digest posts changed vs BASE (git diff BASE...HEAD).")
    parser.add_argument("paths", nargs="*",
                        help="Explicit post file paths (non-digest paths are skipped).")
    args = parser.parse_args(argv)

    if args.staged:
        files = _staged_post_paths()
    elif args.changed:
        files = _changed_post_paths(args.changed)
    elif args.paths:
        files = _explicit_paths(args.paths)
    else:
        files = _all_post_paths()

    if not files:
        print("[digest-proper-nouns] No digest post files to process.")
        return 0

    rc = 0
    checked = fixed = 0
    for path in files:
        rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        checked += 1
        if args.fix:
            n = fix_post(path)
            if n:
                fixed += 1
                print(f"FIXED {rel}  ({n} replacement(s))")
            else:
                print(f"OK    {rel}")
        else:
            vs = check_post(str(path))
            if vs:
                rc = 1
                print(f"FAIL {rel}")
                for v in vs:
                    print(f"  - {v}")
            else:
                print(f"OK   {rel}")

    if args.fix:
        print(f"\n[digest-proper-nouns] --fix done — {fixed}/{checked} post(s) rewritten.")
        return 0
    if rc:
        print(
            f"\n[digest-proper-nouns] FAIL — non-canonical (Hangul) proper nouns "
            f"found in one or more of {checked} digest post(s). Use English "
            f"canonical spellings (e.g. 비트코인 -> Bitcoin), or run with --fix. "
            f"Cited titles / code / CVE IDs are exempt.",
            file=sys.stderr,
        )
    else:
        print(f"[digest-proper-nouns] OK — {checked} digest post(s) checked, 0 violations.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

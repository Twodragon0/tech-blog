#!/usr/bin/env python3
"""Trusted post-processing translator for weekly-digest posts (재발 방지 B단계).

Part A (`scripts/check_digest_untranslated.py`) DETECTS digest posts whose
`#### 요약` prose or news-card `summary="..."` / `title="..."` fields fell back
to raw ENGLISH — which happens whenever the auto-publish translation chain runs
with no LLM key. On the untrusted `repository_dispatch` publish path the LLM
secrets are intentionally zeroed out (ai-blogwatcher.yml, MED-1 partition), so
the fallback emits English instead of Korean.

Part B (this script) is the CORRECTION. It runs in a TRUSTED context (scheduled
`digest-translate-backfill.yml`, never `repository_dispatch`) WITH the keys
available, finds the untranslated spans using `is_untranslated()`, translates
English -> Korean by REUSING the existing helpers in
`scripts/news/content_generator.py` + `scripts/news/enhancer.py` (no new API
plumbing), and writes the Korean back in place — preserving Jekyll `{% include %}`
structure, frontmatter, tables, code blocks, and proper nouns / CVE / MITRE IDs.

Safety properties:
  * GRACEFUL NO-OP without keys — if neither Gemini nor DeepSeek is available it
    changes nothing and exits 0 (never writes a partial/garbage translation).
  * OUTPUT VALIDATED — a translation is only written if it contains Hangul and is
    not more than MAX_LEN_RATIO x the source length; otherwise the original is
    kept (fail-safe). This bounds prompt-injection in RSS content: the only thing
    that can ever land in a post is short, validated Korean text.
  * IDEMPOTENT — re-running on already-Korean text is a no-op.

Usage (mirrors check_digest_untranslated.py, plus --dry-run):
    python3 scripts/retranslate_digest.py --staged
    python3 scripts/retranslate_digest.py --changed HEAD~5
    python3 scripts/retranslate_digest.py --all --dry-run
    python3 scripts/retranslate_digest.py _posts/2026-07-25-...Weekly_Digest...md
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

# --- Path setup so both `import check_digest_untranslated` (scripts/ dir) and
# `from scripts.news import ...` (repo root) resolve regardless of whether we
# are run as a script or imported as scripts.retranslate_digest in tests.
# Mirrors backfill_digest_enrichment.py's established pattern. ---
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (str(_REPO_ROOT), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Reuse detection + path-selection from Part A (single source of truth).
from check_digest_untranslated import (  # noqa: E402
    _all_post_paths,
    _changed_post_paths,
    _explicit_paths,
    _staged_post_paths,
    is_untranslated,
)

# Reuse the existing translation backends — do NOT reimplement API calls.
from scripts.news.content_generator import (  # noqa: E402
    _html_escape_quotes,
    _translate_to_korean_deepseek,
)
from scripts.news.enhancer import (  # noqa: E402
    _allow_deepseek,
    _gemini_call,
    check_gemini_available,
)

# A translated span is only accepted if it is at most this many times the
# source length. Korean renderings of English are usually shorter or comparable
# in character count; anything much longer signals a runaway / injected model
# response, which we reject and keep the original.
MAX_LEN_RATIO = 3.0

# One physical '<indent>key="value"' news-card attribute line. Values never
# contain a raw inner double-quote (they are &quot;-escaped at generation), so
# '.*' up to the closing quote at end-of-line is exact.
_FIELD_RE = re.compile(r'^(?P<indent>\s*)(?P<key>title|summary)="(?P<val>.*)"\s*$')

# A '#### 요약' prose block: heading, then prose up to the next blank-gap /
# heading / rule. Matches check_digest_untranslated._summary_blocks so the
# region we rewrite is exactly the region Part A flags.
_SUMMARY_BLOCK_RE = re.compile(
    r"(####\s*요약\s*\n+)(.+?)(\n\n|\n####|\n---|\n##\s)", re.S
)


def _postprocess(raw: str) -> str:
    """Collapse whitespace to a single physical line and strip wrapping quotes."""
    if not raw:
        return ""
    return re.sub(r"\s+", " ", raw).strip().strip("\"'")


def _is_valid_korean(candidate: str, source: str) -> bool:
    """Output-validation gate (security): accept only bounded, inert Korean text.

    Fail-safe: any candidate that fails a check is rejected so the caller keeps
    the original English (Part A still flags it) rather than shipping suspect
    output. Besides Hangul + length bounds, we reject HTML/Liquid metacharacters
    so a prompt-injected model response (e.g. ``<script>…</script> 안녕`` or a
    ``{% … %}`` tag) can never land in a post body: the '#### 요약' block path
    injects the string raw into kramdown-rendered markdown (raw inline HTML is
    on) and Jekyll re-processes bodies through Liquid, so unescaped ``<``/``{%``/
    ``{{`` would become active markup, not displayed prose.
    """
    if not candidate:
        return False
    if not re.search(r"[가-힣]", candidate):
        return False
    if len(candidate) > MAX_LEN_RATIO * max(len(source), 1):
        return False
    # Reject active HTML / Liquid / CDATA metacharacters (stored-XSS guard).
    if re.search(r"<|{%|{{|\]\]>", candidate):
        return False
    return True


def _build_prompt(text: str, mode: str, context: str) -> str:
    """Gemini prompt mirroring content_generator's translation prompts, with
    an explicit instruction to preserve proper nouns / CVE / MITRE IDs."""
    if mode == "title":
        return (
            f"다음 {context} 제목을 한국어 한 줄로 자연스럽게 번역하세요. "
            "고유명사(회사명/제품명/행위자명), CVE ID, MITRE ATT&CK ID는 원문 표기를 "
            "그대로 유지하세요. 따옴표/번호/불릿/설명 없이 번역된 제목 한 줄만 출력하세요.\n"
            f"원문: {text}\n번역:"
        )
    return (
        f"다음 {context}를 한국어 2~3문장으로 자연스럽게 번역하세요. "
        "기술 용어와 고유명사(회사명/제품명/행위자명), CVE ID, MITRE ATT&CK ID, "
        "그리고 문장 끝의 한국어 조치 문구는 원문 표기를 그대로 유지하세요. "
        "마크다운/불릿/번호 없이 순수 문장만 출력하세요.\n"
        f"원문: {text[:1000]}\n번역:"
    )


def backend_available() -> bool:
    """True iff at least one translation backend (Gemini CLI/API or DeepSeek)
    is reachable. Used to short-circuit to a clean no-op when no key exists."""
    if check_gemini_available():
        return True
    if _allow_deepseek() and os.getenv("DEEPSEEK_API_KEY", ""):
        return True
    return False


def translate(text: str, mode: str, context: str = "기술 뉴스") -> str:
    """Translate English *text* -> Korean, reusing Gemini then DeepSeek.

    Returns "" if no backend is available OR the model output fails validation
    (fail-safe: the caller then keeps the original text unchanged).
    """
    text = text.strip()
    if not text:
        return ""

    # 1) Gemini (CLI free-tier first, API fallback — both inside _gemini_call).
    if check_gemini_available():
        candidate = _postprocess(_gemini_call(_build_prompt(text, mode, context), timeout=20))
        if _is_valid_korean(candidate, text):
            return candidate

    # 2) DeepSeek API fallback (reads DEEPSEEK_API_KEY internally).
    if _allow_deepseek() and os.getenv("DEEPSEEK_API_KEY", ""):
        candidate = _postprocess(
            _translate_to_korean_deepseek(text, context=context, mode=mode)
        )
        if _is_valid_korean(candidate, text):
            return candidate

    return ""


def _field_line(line: str, stats: dict) -> str:
    """Translate one news-card title="..." / summary="..." line if it is
    untranslated English; otherwise return it unchanged."""
    m = _FIELD_RE.match(line)
    if not m:
        return line
    key = m.group("key")
    raw_val = m.group("val")
    plain = html.unescape(raw_val)
    if not is_untranslated(plain):
        return line
    mode = "title" if key == "title" else "summary"
    translated = translate(plain, mode=mode, context="보안 뉴스")
    if not translated:
        return line  # fail-safe: keep original
    # Re-escape for safe single-line injection into the Liquid double-quoted
    # attribute (no inner double-quotes, no newlines).
    safe = _html_escape_quotes(re.sub(r"\s+", " ", translated).strip())
    stats["fields"] += 1
    return f'{m.group("indent")}{key}="{safe}"'


def _block_repl(m: "re.Match", stats: dict) -> str:
    """Replace a '#### 요약' prose block with its Korean translation if it is
    untranslated English; otherwise leave the whole match unchanged."""
    head, prose, tail = m.group(1), m.group(2), m.group(3)
    if not is_untranslated(prose):
        return m.group(0)
    translated = translate(prose, mode="summary", context="보안 뉴스 요약")
    if not translated:
        return m.group(0)  # fail-safe: keep original
    stats["blocks"] += 1
    return f"{head}{translated}{tail}"


def retranslate_text(text: str) -> tuple:
    """Return (new_text, stats). Pure function — no I/O.

    Order is irrelevant because 요약 blocks and title=/summary= attribute lines
    occupy disjoint regions of the post.
    """
    stats = {"fields": 0, "blocks": 0}
    text = _SUMMARY_BLOCK_RE.sub(lambda m: _block_repl(m, stats), text)
    text = "\n".join(_field_line(ln, stats) for ln in text.split("\n"))
    return text, stats


def retranslate_post(path: Path, dry_run: bool) -> dict:
    """Read, translate in place, (optionally) write. Returns a result dict."""
    with open(path, encoding="utf-8") as fh:
        original = fh.read()
    new, stats = retranslate_text(original)
    changed = new != original
    if changed and not dry_run:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    return {"changed": changed, **stats}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Translate untranslated-English 요약/summary=/title= spans in "
            "Weekly_Digest posts back to Korean (재발 방지 B단계). Trusted job "
            "only — never runs on repository_dispatch. Graceful no-op without keys."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true",
                      help="Only fix staged digest posts (git diff --cached).")
    mode.add_argument("--all", action="store_true",
                      help="Fix every digest post.")
    mode.add_argument("--changed", metavar="BASE", default=None,
                      help="Only fix digest posts changed vs BASE (git diff BASE...HEAD).")
    parser.add_argument("paths", nargs="*",
                        help="Explicit post file paths (non-digest paths are skipped).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what WOULD change without writing.")
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
        print("[digest-retranslate] No digest post files to process.")
        return 0

    # GRACEFUL NO-OP: with no translation backend, do nothing rather than risk a
    # partial write. (Also the common local case — corpus is already Korean.)
    if not backend_available():
        print(
            "[digest-retranslate] No translation backend available "
            "(no Gemini CLI/API and no DEEPSEEK_API_KEY) — nothing translated. "
            f"{len(files)} digest post(s) left unchanged."
        )
        return 0

    changed = 0
    for path in files:
        rel = path.relative_to(_REPO_ROOT) if path.is_relative_to(_REPO_ROOT) else path
        result = retranslate_post(path, dry_run=args.dry_run)
        if result["changed"]:
            changed += 1
            verb = "WOULD FIX" if args.dry_run else "FIXED"
            print(
                f"{verb} {rel} "
                f"(요약 blocks={result['blocks']}, fields={result['fields']})"
            )
        else:
            print(f"ok   {rel}")

    tail = "would change" if args.dry_run else "changed"
    print(f"[digest-retranslate] {changed}/{len(files)} digest post(s) {tail}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

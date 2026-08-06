"""Make bare URLs clickable, using the corpus' own anchor convention.

Corpus audit 2026-08-06: 123 bare ``https://…`` occurrences across 19 posts are
rendered as PLAIN TEXT. Verified on built output rather than inferred —
``_site/posts/2025/05/30/…Docker…/index.html`` contains the URL with no ``href``
around it. ``_config.yml`` sets ``markdown: kramdown`` without GFM input, and
kramdown does not auto-link bare URLs, so a reader simply cannot follow them.

The anchor text is NOT invented: it mirrors what the corpus already writes —
``[cisa.gov/known-exploited-vulnerabilities-catalog]``, ``[first.org/epss]``,
``[attack.mitre.org]`` — i.e. the host with a leading ``www.`` removed, plus the
path, falling back to the host alone when that would get unwieldy.

Explicitly OUT of scope: the 250 ``[바로가기]`` / ``[링크]`` anchors flagged by a
context-blind scan. Every one of them sits in a table's link column whose
neighbouring cell already carries the title, so replacing the anchor text would
duplicate that cell. They are correct as written.

Usage:
    python3 scripts/linkify_bare_urls.py --posts-glob '_posts/*.md' --dry-run
    python3 scripts/linkify_bare_urls.py _posts/2025-12-17-*.md
"""
import argparse
import glob
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent

LABEL_MAX = 50

_FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
# Not preceded by markdown-link / HTML-attribute / angle-bracket context.
_BARE_URL_RE = re.compile(r'(?<![\(\[<"=])\bhttps?://[^\s\)\]<>"\']+')
_TRAILING_PUNCT = ".,;:!?"
_INLINE_CODE_RE = re.compile(r"`[^`]*`")


def label_for(url: str) -> str:
    """Corpus convention: host without www., plus path when it stays short."""
    parts = urlparse(url)
    host = parts.netloc[4:] if parts.netloc.startswith("www.") else parts.netloc
    path = parts.path.rstrip("/")
    candidate = f"{host}{path}"
    return candidate if path and len(candidate) <= LABEL_MAX else host


def _linkify_line(line: str) -> str:
    # Protect inline code spans so their URLs are never rewritten.
    spans = []

    def _stash(m):
        spans.append(m.group(0))
        return f"\x00{len(spans) - 1}\x00"

    protected = _INLINE_CODE_RE.sub(_stash, line)

    def _replace(m):
        url = m.group(0)
        trailing = ""
        while url and url[-1] in _TRAILING_PUNCT:
            trailing = url[-1] + trailing
            url = url[:-1]
        if not url:
            return m.group(0)
        return f"[{label_for(url)}]({url}){trailing}"

    out = _BARE_URL_RE.sub(_replace, protected)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], out)


def transform(text: str) -> str:
    m = _FRONT_MATTER_RE.match(text)
    front, body = (text[: m.end()], text[m.end():]) if m else ("", text)

    out, in_fence, in_liquid = [], False, False
    for line in body.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        # A Liquid tag spans MULTIPLE lines ('{% include news-card.html' then
        # the attributes then '%}'), so a per-line '{%' guard misses the
        # attribute lines. It missed image="…/https://s3…" — a URL nested
        # inside another URL, which the '="' lookbehind also cannot see — and
        # rewrote it, corrupting the cover image on 3 digests.
        if not in_liquid and "{%" in line and "%}" not in line:
            in_liquid = True
        if in_liquid or "{%" in line or "{{" in line:
            out.append(line)
            if in_liquid and "%}" in line:
                in_liquid = False
            continue
        out.append(_linkify_line(line))
    return front + "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Wrap bare URLs in markdown links.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    if not files:
        print("[linkify-urls] no post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            continue
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[linkify-urls] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

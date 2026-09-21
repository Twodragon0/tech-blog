#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trim_front_matter.py - Automatically trim oversized front matter fields in Jekyll posts.

DO NOT WIRE THIS INTO CI, pre-commit, or the publish path, and do not run
`--fix` over the corpus without reopening the decision below.
------------------------------------------------------------------------
It reports 304/305 posts as "would be trimmed", which reads like a backlog.
It is not. Measured 2026-09-21, the two things it would change are both
regressions against what the repo has decided elsewhere:

1. **excerpt truncation to 150 chars.** CLAUDE.md's front-matter spec says
   `excerpt: "Summary (150-200 chars)"`. Of 305 posts, 288 exceed 150 chars
   and **287 of those sit inside the documented 150-200 range**. Trimming
   would push 287 posts OUT of spec to satisfy a limit this file chose on
   its own. `FIELD_LIMITS["excerpt"]` below is the disagreement.
2. **`keywords:` deletion whenever `tags` exist.** 300/305 posts carry
   `keywords:`, and `_includes/head.html:79` reads it —
   `{% assign meta_keywords = page.keywords | default: page.tags %}`.
   Deleting it silently swaps the meta-keywords source from a curated list
   to raw tags on 300 pages.

Raising the excerpt limit does NOT fix this — the operation is wrong
---------------------------------------------------------------------
An earlier version of this note said to reopen once `FIELD_LIMITS["excerpt"]`
was reconciled with the documented 150-200 range. **That instruction was
wrong**, and following it would have shipped the damage with a bigger number.
Measured 2026-09-21 at a 200 limit: only 4 posts exceed it, and all 4 lose
their closing predicate.

    before (204):  … 주요 보안 이슈와 DevSecOps 실무 대응 포인트를 주차 단위로 종합 정리합니다.
    after  (197):  … DevSecOps 실무 대응 포인트를 주차 단위로...

`truncate_at_word` cuts at `rfind(" ")`. Korean puts spaces between 어절, so a
space is not a safe cut point: the sentence ends in a predicate, and dropping
it leaves a dangling adverbial. The excerpt is the text listing pages, the RSS
feed and the Google result show. Saving 7-43 characters is not worth a broken
sentence on the most-read line of a post.

`description` is moot, not merely small: `_includes/head.html:56` is
`{% assign raw_description = page.excerpt | default: page.description %}`, and
all 305 posts have an excerpt — so `page.description` is never rendered.
Trimming its 159 over-limit values changes nothing anyone sees.

Two arguments that do NOT hold, recorded so they are not re-used:

* Trimming does not break `check_excerpt_promises`. Measured both ways — five
  posts at the 150 limit, and the four truncated at 200 — the gate stayed
  green (305 clean) each time. It is worse than neutral: truncation destroys
  the closing claim, so the gate passes *more* easily. Passing it here is not
  evidence of quality.
* "287 posts sit inside the documented range" was the argument against the 150
  limit specifically. It does not survive raising the limit, which is why the
  sentence-level measurement above is the real case.

`image_alt` does not survive either — the earlier note here was wrong
---------------------------------------------------------------------
This file previously called `image_alt` "the only field where this tool does
something defensible (29 posts over 80, max 109)". Both the numbers and the
conclusion were wrong. The counts came from a regex that mishandled
single-quoted YAML scalars; parsed as YAML it is **44 posts over 80, max 112,
91 words dropped**.

The conclusion fails on its own terms:

* **Nothing in the repo asks for 80.** The only length constraint applied to
  this field anywhere is `sitemap.xml:94`'s `truncate: 160`, and the longest
  value is 112 — already under it. `og:image:alt` (`head.html:184`),
  `twitter:image:alt` (`head.html:211`) and the rendered `<img alt>`
  (`_layouts/post.html:140`) impose none. 80 is this file's own invention,
  exactly as 150 was for excerpt.
* **The dropped words are the informative ones.** "…container supply chain
  attacks digest" becomes "…container supply"; "…prompt injection defense
  digest" becomes "…prompt injection". No predicate is lost because English
  alt text has none, but meaning is.
* **`<img alt>` is an accessibility surface.** CLAUDE.md commits this site to
  WCAG 2.1 AA. Making alt text shorter and less descriptive to satisfy a
  self-chosen limit is a regression against that, not a cleanup.

So all three fields fail, and this tool has no remaining defensible job.

Reopen if: a Korean-aware truncation (sentence-boundary, not space-boundary)
replaces `truncate_at_word` AND a consumer that actually enforces a length is
identified for the field being trimmed. Do not reopen by changing a number —
that was tried and recorded above. Full measurement: notes/decisions.md,
2026-09-21.

Usage:
    python3 scripts/trim_front_matter.py              # dry-run all posts
    python3 scripts/trim_front_matter.py --fix        # apply changes to all posts
    python3 scripts/trim_front_matter.py --dry-run    # explicit dry-run
    python3 scripts/trim_front_matter.py --fix _posts/2026-01-01-post.md  # specific files
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRONT_MATTER_THRESHOLD = 1000  # chars: only process posts exceeding this

FIELD_LIMITS = {
    "description": 160,
    "excerpt": 150,
    "image_alt": 80,
}

# Fields that keywords removal is conditioned on (tags already exist)
KEYWORDS_FIELD = "keywords"
TAGS_FIELD = "tags"

# Fields that must never be touched
PROTECTED_FIELDS = {
    "image",
    "title",
    "tags",
    "categories",
    "date",
    "layout",
    "author",
    "comments",
    "toc",
}


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------


def truncate_at_word(text: str, max_chars: int, suffix: str = "...") -> str:
    """
    Truncate text at the last complete word boundary within max_chars.
    Safe for Korean (Unicode) – does not split mid-codepoint.
    If suffix is "", no suffix is appended.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text

    if suffix:
        budget = max_chars - len(suffix)
    else:
        budget = max_chars

    if budget <= 0:
        return suffix

    # Try to break at a whitespace boundary within the budget
    truncated = text[:budget]
    last_space = truncated.rfind(" ")
    if last_space > budget // 2:
        truncated = truncated[:last_space]
    return truncated.rstrip() + suffix


def strip_quotes(value: str) -> tuple[str, str, str]:
    """
    Return (leading_quote, inner_value, trailing_quote).
    Handles single-quoted, double-quoted, and unquoted scalar strings.
    Multi-line block scalars (| or >) are returned unquoted.
    """
    v = value.strip()
    if v.startswith("'") and v.endswith("'") and len(v) >= 2:
        return ("'", v[1:-1], "'")
    if v.startswith('"') and v.endswith('"') and len(v) >= 2:
        return ('"', v[1:-1], '"')
    return ("", v, "")


def rebuild_scalar(leading: str, inner: str, trailing: str) -> str:
    """Re-wrap a scalar with its original quoting."""
    return f"{leading}{inner}{trailing}"


# ---------------------------------------------------------------------------
# Front matter parser (regex-based, preserves formatting)
# ---------------------------------------------------------------------------


def split_front_matter(content: str) -> tuple[str, str, str]:
    """
    Split a Jekyll file into (before_fm, front_matter_body, rest).
    Returns ("", "", content) if no valid front matter is found.
    """
    if not content.startswith("---"):
        return ("", "", content)
    # Second --- must appear on its own line
    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        return ("", "", content)
    fm_end = 3 + match.end()
    return ("---\n", content[3 : 3 + match.start()], content[fm_end:])


def front_matter_len(fm_body: str) -> int:
    return len(fm_body)


# ---------------------------------------------------------------------------
# Field-level trimming on raw YAML text
# ---------------------------------------------------------------------------


def _replace_scalar_field(fm_body: str, field: str, new_value: str) -> str:
    """
    Replace the scalar value of a top-level YAML field.
    Handles:
      - Single-line:  field: value
      - Single-line:  field: 'value'
      - Single-line:  field: "value"
      - Multi-line flow scalar that wraps (field: 'long...\n  continued')
    Does NOT handle block scalars (| or >) – those are rare in our posts.
    """
    # Pattern: field key at start of line, then colon, optional space, then value
    # Value may span multiple lines if it's a quoted string
    # We match greedily within quotes, or to end-of-line if unquoted.

    # --- Single-quoted multi-line ---
    sq_pattern = re.compile(
        r"^(" + re.escape(field) + r":\s*')((?:[^']|'')*?)('\s*\n)",
        re.MULTILINE | re.DOTALL,
    )
    m = sq_pattern.search(fm_body)
    if m:
        return (
            fm_body[: m.start()]
            + m.group(1)
            + new_value
            + m.group(3)
            + fm_body[m.end() :]
        )

    # --- Double-quoted multi-line ---
    dq_pattern = re.compile(
        r"^(" + re.escape(field) + r':\s*")((?:[^"\\]|\\.)*)("\s*\n)',
        re.MULTILINE | re.DOTALL,
    )
    m = dq_pattern.search(fm_body)
    if m:
        return (
            fm_body[: m.start()]
            + m.group(1)
            + new_value
            + m.group(3)
            + fm_body[m.end() :]
        )

    # --- Unquoted single-line ---
    uq_pattern = re.compile(
        r"^(" + re.escape(field) + r":\s*)(.+?)(\s*\n)",
        re.MULTILINE,
    )
    m = uq_pattern.search(fm_body)
    if m:
        return (
            fm_body[: m.start()]
            + m.group(1)
            + new_value
            + m.group(3)
            + fm_body[m.end() :]
        )

    return fm_body


def _get_scalar_value(fm_body: str, field: str) -> str | None:
    """
    Extract the raw (unquoted) value of a scalar field.
    Returns None if field not present.
    """
    # Single-quoted
    sq = re.search(
        r"^" + re.escape(field) + r":\s*'((?:[^']|'')*?)'\s*$",
        fm_body,
        re.MULTILINE | re.DOTALL,
    )
    if sq:
        return sq.group(1).replace("''", "'")

    # Double-quoted
    dq = re.search(
        r"^" + re.escape(field) + r':\s*"((?:[^"\\]|\\.)*)"\s*$',
        fm_body,
        re.MULTILINE | re.DOTALL,
    )
    if dq:
        # Basic unescape
        return dq.group(1).replace('\\"', '"').replace("\\n", "\n")

    # Unquoted single-line
    uq = re.search(
        r"^" + re.escape(field) + r":\s*(.+?)\s*$",
        fm_body,
        re.MULTILINE,
    )
    if uq:
        val = uq.group(1).strip()
        # Skip if it's a YAML block indicator or list indicator
        if val in ("|", ">", "|-", ">-") or val.startswith("-"):
            return None
        return val

    return None


def _field_exists(fm_body: str, field: str) -> bool:
    """Check if a top-level field exists in the front matter."""
    return bool(re.search(r"^" + re.escape(field) + r"\s*:", fm_body, re.MULTILINE))


def _remove_field(fm_body: str, field: str) -> str:
    """
    Remove a top-level YAML field (scalar or block list) from the front matter body.
    Handles:
      - Scalar:  field: value\n
      - Flow scalar spanning lines (quoted strings with continuation lines starting with spaces)
      - Block list:  field:\n- item\n- item\n  (list items may or may not be indented)
    """
    # Match the field key line, then greedily consume all following "continuation" lines:
    #   - lines starting with whitespace (indented continuation of a scalar)
    #   - lines starting with '- ' (YAML list items directly under the field key)
    # Stop at the next top-level key (not indented, not a list item).
    pattern = re.compile(
        r"^" + re.escape(field) + r"\s*:.*\n"  # key line
        r"(?:(?:[ \t]+.*|-[^\n]*)\n)*",  # zero or more continuation / list-item lines
        re.MULTILINE,
    )
    return pattern.sub("", fm_body)


# ---------------------------------------------------------------------------
# Core processing logic
# ---------------------------------------------------------------------------


def _get_quoting_style(fm_body: str, field: str) -> tuple[str, str]:
    """Return (open_quote, close_quote) used for the field, or ('', '')."""
    sq = re.search(
        r"^" + re.escape(field) + r":\s*'",
        fm_body,
        re.MULTILINE,
    )
    if sq:
        return ("'", "'")
    dq = re.search(
        r"^" + re.escape(field) + r':\s*"',
        fm_body,
        re.MULTILINE,
    )
    if dq:
        return ('"', '"')
    return ("", "")


def process_front_matter(fm_body: str) -> tuple[str, list[str]]:
    """
    Apply trimming rules to a front matter body string.
    Returns (new_fm_body, list_of_change_descriptions).
    """
    changes = []
    new_fm = fm_body

    # --- Trim scalar fields (description, excerpt, image_alt) ---
    for field, max_chars in FIELD_LIMITS.items():
        value = _get_scalar_value(new_fm, field)
        if value is None:
            continue

        # Collapse inline whitespace (YAML flow scalars can have \n + indent)
        clean_value = re.sub(r"\s+", " ", value).strip()

        if len(clean_value) <= max_chars:
            continue

        # Truncate
        suffix = "..." if field != "image_alt" else ""
        trimmed = truncate_at_word(clean_value, max_chars, suffix=suffix)

        # Rebuild with original quoting
        open_q, close_q = _get_quoting_style(new_fm, field)

        # For single-quoted YAML: escape internal single quotes as ''
        if open_q == "'":
            trimmed_yaml = trimmed.replace("'", "''")
        else:
            trimmed_yaml = trimmed

        new_fm = _replace_scalar_field(new_fm, field, trimmed_yaml)

        changes.append(f"  - {field}: {len(clean_value)} → {len(trimmed)} chars")

    # --- Remove keywords if tags field exists ---
    if _field_exists(new_fm, KEYWORDS_FIELD) and _field_exists(new_fm, TAGS_FIELD):
        new_fm = _remove_field(new_fm, KEYWORDS_FIELD)
        changes.append(f"  - {KEYWORDS_FIELD}: removed (tags exist)")

    return new_fm, changes


def process_file(
    filepath: Path,
    dry_run: bool = True,
) -> tuple[bool, list[str], int]:
    """
    Process a single Jekyll markdown file.

    Returns:
        (was_modified, change_lines, chars_saved)
    """
    content = filepath.read_text(encoding="utf-8")
    prefix, fm_body, rest = split_front_matter(content)

    if not fm_body:
        return False, [], 0

    fm_len = front_matter_len(fm_body)
    if fm_len <= FRONT_MATTER_THRESHOLD:
        return False, [], 0

    new_fm, changes = process_front_matter(fm_body)

    if not changes:
        return False, [], 0

    new_fm_len = front_matter_len(new_fm)
    chars_saved = fm_len - new_fm_len

    header_line = (
        f"[{'DRY RUN' if dry_run else 'FIXED'}] Processing: {filepath.name}\n"
        f"  Front matter: {fm_len} chars → {new_fm_len} chars (-{chars_saved})"
    )
    output_lines = [header_line] + changes

    if not dry_run:
        new_content = prefix + new_fm + "\n" + rest
        filepath.write_text(new_content, encoding="utf-8")

    return True, output_lines, chars_saved


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def collect_posts(paths: list[str]) -> list[Path]:
    """Resolve file paths, defaulting to all _posts/*.md."""
    if paths:
        result = []
        for p in paths:
            fp = Path(p)
            if not fp.exists():
                print(f"Warning: file not found: {p}", file=sys.stderr)
            else:
                result.append(fp)
        return result

    # Default: look for _posts relative to script location or cwd
    script_dir = Path(__file__).parent
    blog_root = script_dir.parent
    posts_dir = blog_root / "_posts"

    if not posts_dir.is_dir():
        # Fallback: try cwd
        posts_dir = Path.cwd() / "_posts"

    if not posts_dir.is_dir():
        print("Error: could not find _posts directory", file=sys.stderr)
        sys.exit(1)

    return sorted(posts_dir.glob("*.md"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trim oversized front matter fields in Jekyll posts."
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would change without modifying files (default behavior).",
    )
    mode_group.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="Apply changes to files.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Specific .md files to process (default: all _posts/*.md).",
    )

    args = parser.parse_args()

    # Default to dry-run when neither flag given
    dry_run = not args.fix

    posts = collect_posts(args.files)
    if not posts:
        print("No posts found.")
        sys.exit(0)

    total_fixed = 0
    total_saved = 0

    for post in posts:
        try:
            modified, lines, saved = process_file(post, dry_run=dry_run)
        except Exception as exc:
            print(f"Error processing {post.name}: {exc}", file=sys.stderr)
            continue

        if modified:
            total_fixed += 1
            total_saved += saved
            print("\n".join(lines))
            print()

    # Summary
    mode_label = "would be trimmed" if dry_run else "trimmed"
    print(
        f"Summary: {total_fixed} posts {mode_label}, saving ~{total_saved} chars total"
    )


if __name__ == "__main__":
    main()

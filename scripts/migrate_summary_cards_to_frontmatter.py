#!/usr/bin/env python3
"""Migrate `{% include ai-summary-card.html ... %}` blocks to frontmatter.

This script extracts the 6 attributes (title / categories_html / tags_html /
highlights_html / period / audience) from each `_posts/*.md` that uses the
ai-summary-card include with attributes, parses the embedded HTML into
structured data, and writes a `summary_card:` block into the post's YAML
frontmatter. The body include is then simplified to a no-attribute form
(`{% include ai-summary-card.html %}`) which lets the include template read
from `page.summary_card` directly.

Goals
-----
1. Byte-identical card HTML before and after migration (the include template
   was updated in commit 613a369e to support both forms).
2. Idempotent: posts already migrated (containing `summary_card:` in
   frontmatter or having the bare include) are skipped.
3. Reversible via `--reverse` for emergency rollback.

Usage
-----
    # Preview changes (no writes)
    python3 scripts/migrate_summary_cards_to_frontmatter.py --dry-run

    # Apply
    python3 scripts/migrate_summary_cards_to_frontmatter.py --commit

    # Rollback
    python3 scripts/migrate_summary_cards_to_frontmatter.py --reverse --commit
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup

# Match include block (both `{%` and `{%-` whitespace control variants).
INCLUDE_BLOCK_RE = re.compile(
    r"\{%-?\s*include\s+ai-summary-card\.html(?P<body>.*?)-?%\}",
    re.DOTALL,
)

# Match the bare (already migrated) form.
BARE_INCLUDE_RE = re.compile(
    r"\{%-?\s*include\s+ai-summary-card\.html\s*-?%\}",
)

# Each attribute matches name='...' or name="..." (DOTALL because values can
# span lines, e.g., tags_html). The closing quote must match the opener.
ATTR_RES = {
    name: re.compile(
        rf"\b{name}\s*=\s*(?P<q>['\"])(?P<val>.*?)(?P=q)",
        re.DOTALL,
    )
    for name in (
        "title",
        "categories_html",
        "tags_html",
        "highlights_html",
        "period",
        "audience",
    )
}

# Bare-variable form: name=identifier (no quotes), used when the post
# defines `{% capture identifier %}...{% endcapture %}` earlier in the body.
ATTR_VAR_RES = {
    name: re.compile(rf"\b{name}\s*=\s*(?P<var>[A-Za-z_][A-Za-z0-9_]*)\b")
    for name in ("categories_html", "tags_html", "highlights_html")
}

# Capture block: {% capture name %}...{% endcapture %}
CAPTURE_RE = re.compile(
    r"\{%\s*capture\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*%\}"
    r"(?P<body>.*?)"
    r"\{%\s*endcapture\s*%\}",
    re.DOTALL,
)

FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)


@dataclass
class SummaryCard:
    title: str = ""
    period: str = ""
    audience: str = ""
    categories: list[dict[str, str]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    highlights: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def extract_attributes(
    include_block_body: str,
    captures: dict[str, str] | None = None,
) -> dict[str, str]:
    """Parse the body of an include block into a dict of attribute values.

    `include_block_body` is the substring captured by INCLUDE_BLOCK_RE's
    `body` group (everything between `ai-summary-card.html` and `%}`).

    `captures` maps {% capture %} variable names to their captured text;
    bare-variable attributes (e.g., `categories_html=ai_categories_html`)
    are resolved against this dict.
    """
    captures = captures or {}
    out: dict[str, str] = {}
    for name, regex in ATTR_RES.items():
        m = regex.search(include_block_body)
        if m:
            out[name] = m.group("val")
    # Resolve bare-variable attribute forms via captures.
    for name, regex in ATTR_VAR_RES.items():
        if name in out:
            continue  # already resolved as quoted form
        m = regex.search(include_block_body)
        if m:
            var_name = m.group("var")
            if var_name in captures:
                out[name] = captures[var_name].strip("\n")
    return out


def extract_captures(content: str) -> dict[str, str]:
    """Extract {% capture name %}...{% endcapture %} blocks into a dict."""
    out: dict[str, str] = {}
    for m in CAPTURE_RE.finditer(content):
        out[m.group("name")] = m.group("body")
    return out


# Placeholders we substitute into HTML before BS4 parsing so that entity
# references survive the parse-and-extract round-trip. BS4 always decodes
# entities like `&#x27;` into raw chars, which prevents byte-identical
# round-tripping when the source HTML uses entity escapes (e.g., the
# pre-existing fix-malformed-liquid-includes step rewrites `'` → `&#x27;`).
_ENTITY_PLACEHOLDERS = [
    ("&#x27;", "\x00ENT_X27\x00"),
    ("&#39;", "\x00ENT_39\x00"),
    ("&apos;", "\x00ENT_APOS\x00"),
    ("&quot;", "\x00ENT_QUOT\x00"),
    ("&amp;", "\x00ENT_AMP\x00"),
]


def _protect_entities(html: str) -> str:
    for ent, ph in _ENTITY_PLACEHOLDERS:
        html = html.replace(ent, ph)
    return html


def _restore_entities(text: str) -> str:
    for ent, ph in _ENTITY_PLACEHOLDERS:
        text = text.replace(ph, ent)
    return text


def parse_categories_html(html: str) -> list[dict[str, str]]:
    """Parse `<span class="category-tag X">label</span>` items into list."""
    if not html:
        return []
    protected = _protect_entities(html)
    soup = BeautifulSoup(protected, "html.parser")
    out: list[dict[str, str]] = []
    for span in soup.find_all("span", class_="category-tag"):
        classes = [c for c in span.get("class", []) if c != "category-tag"]
        cls = classes[0] if classes else ""
        label = _restore_entities(span.get_text())
        out.append({"class": cls, "label": label})
    return out


def parse_tags_html(html: str) -> list[str]:
    """Parse `<span class="tag">x</span>` items into list of strings."""
    if not html:
        return []
    protected = _protect_entities(html)
    soup = BeautifulSoup(protected, "html.parser")
    return [
        _restore_entities(span.get_text())
        for span in soup.find_all("span", class_="tag")
    ]


def parse_highlights_html(html: str) -> list[dict[str, str]]:
    """Parse `<li><strong>source</strong>: title</li>` items.

    For items without `<strong>`, the entire li text becomes the title and
    source is empty string. HTML entities (e.g., `&#x27;`) are preserved
    so re-rendered output is byte-identical to the original include.
    """
    if not html:
        return []
    protected = _protect_entities(html)
    soup = BeautifulSoup(protected, "html.parser")
    out: list[dict[str, str]] = []
    for li in soup.find_all("li"):
        strong = li.find("strong")
        if strong:
            source = _restore_entities(strong.get_text())
            strong.extract()
            tail = _restore_entities(li.get_text())
            title = re.sub(r"^\s*:\s*", "", tail).strip()
        else:
            source = ""
            title = _restore_entities(li.get_text()).strip()
        out.append({"source": source, "title": title})
    return out


def build_summary_card(attrs: dict[str, str]) -> SummaryCard:
    sc = SummaryCard(
        title=attrs.get("title", ""),
        period=attrs.get("period", ""),
        audience=attrs.get("audience", ""),
        categories=parse_categories_html(attrs.get("categories_html", "")),
        tags=parse_tags_html(attrs.get("tags_html", "")),
        highlights=parse_highlights_html(attrs.get("highlights_html", "")),
    )
    return sc


# ---------------------------------------------------------------------------
# YAML emission (manual to control quoting and key order)
# ---------------------------------------------------------------------------


def _yaml_escape_double(s: str) -> str:
    """Escape a string for safe inclusion inside YAML double quotes.

    Only escapes backslash and double-quote; YAML double-quoted scalars
    accept most printable characters as-is.
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit_summary_card_yaml(sc: SummaryCard) -> str:
    """Emit `summary_card:` block as YAML, with stable key order.

    Quoting: every string scalar uses double quotes. Empty optional keys
    (period, audience) are omitted. Empty arrays are emitted as `[]`.
    """
    lines: list[str] = ["summary_card:"]
    lines.append(f'  title: "{_yaml_escape_double(sc.title)}"')
    if sc.period:
        lines.append(f'  period: "{_yaml_escape_double(sc.period)}"')
    if sc.audience:
        lines.append(f'  audience: "{_yaml_escape_double(sc.audience)}"')
    if sc.categories:
        lines.append("  categories:")
        for cat in sc.categories:
            cls = _yaml_escape_double(cat.get("class", ""))
            lbl = _yaml_escape_double(cat.get("label", ""))
            lines.append(f'    - {{ class: "{cls}", label: "{lbl}" }}')
    else:
        lines.append("  categories: []")
    if sc.tags:
        lines.append("  tags:")
        for tag in sc.tags:
            lines.append(f'    - "{_yaml_escape_double(tag)}"')
    else:
        lines.append("  tags: []")
    if sc.highlights:
        lines.append("  highlights:")
        for h in sc.highlights:
            src = _yaml_escape_double(h.get("source", ""))
            ttl = _yaml_escape_double(h.get("title", ""))
            lines.append(f'    - {{ source: "{src}", title: "{ttl}" }}')
    else:
        lines.append("  highlights: []")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Frontmatter manipulation
# ---------------------------------------------------------------------------


def split_frontmatter(content: str) -> tuple[str, str] | None:
    """Return (frontmatter_block_with_fences, rest) or None if not present."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None
    fm = m.group(0)  # incl. leading and trailing ---\n
    rest = content[m.end():]
    return fm, rest


def has_summary_card_in_frontmatter(fm: str) -> bool:
    return bool(re.search(r"^summary_card:\s*$", fm, re.MULTILINE))


def insert_summary_card_into_frontmatter(fm: str, sc_yaml: str) -> str:
    """Insert summary_card block before the closing `---\\n`."""
    # fm ends with '---\n'. Insert before that closing fence.
    if not fm.endswith("---\n"):
        raise ValueError("Frontmatter does not end with expected fence")
    inner = fm[:-4]  # strip closing '---\n'
    if not inner.endswith("\n"):
        inner += "\n"
    new_fm = inner + sc_yaml + "\n---\n"
    return new_fm


def remove_summary_card_from_frontmatter(fm: str) -> str:
    """Remove the summary_card: block from frontmatter (for --reverse)."""
    # Match `summary_card:` and all subsequent indented lines until next
    # top-level key or end of frontmatter inner.
    pattern = re.compile(
        r"^summary_card:\s*\n(?:[ \t].*\n|\n)*",
        re.MULTILINE,
    )
    new_fm = pattern.sub("", fm)
    return new_fm


# ---------------------------------------------------------------------------
# Migration entry points
# ---------------------------------------------------------------------------


@dataclass
class MigrationResult:
    path: str
    status: str  # "migrated", "skipped", "failed", "reversed"
    reason: str = ""
    new_content: str | None = None


# Compatible separator patterns the new include emits. To preserve
# byte-identical rendered HTML, we only migrate posts whose attribute HTML
# already uses these exact separators. Posts using divergent separators
# (e.g., a literal newline without 6-space indent) stay on the legacy
# include-with-attributes form via the include's fallback branch.
_CAT_OK_SEPS = {" "}
_TAGS_OK_SEPS = {"\n      "}
_HI_OK_SEPS = {"\n      "}


def _separators_between(html: str, end_tag: str, start_tag: str) -> set[str]:
    """Return the set of unique separator strings between consecutive
    `</end_tag>...<start_tag` runs. Empty set means there is at most one
    item, in which case the separator is irrelevant."""
    seps = re.findall(
        re.escape(end_tag) + r"(\s*?)(?=" + re.escape(start_tag) + ")",
        html,
        re.DOTALL,
    )
    return set(seps)


def _is_separator_compatible(attrs: dict[str, str]) -> tuple[bool, str]:
    """Check that the separators used in HTML attributes match what the new
    include template emits. Returns (compatible, reason_if_not)."""
    cat_seps = _separators_between(attrs.get("categories_html", ""), "</span>", "<span")
    if cat_seps and not cat_seps.issubset(_CAT_OK_SEPS):
        return False, f"categories separator divergent: {sorted(cat_seps)!r}"

    tag_seps = _separators_between(attrs.get("tags_html", ""), "</span>", "<span")
    if tag_seps and not tag_seps.issubset(_TAGS_OK_SEPS):
        return False, f"tags separator divergent: {sorted(tag_seps)!r}"

    hi_seps = _separators_between(attrs.get("highlights_html", ""), "</li>", "<li")
    if hi_seps and not hi_seps.issubset(_HI_OK_SEPS):
        return False, f"highlights separator divergent: {sorted(hi_seps)!r}"
    return True, ""


def migrate_post(
    content: str,
    path: str = "<input>",
    *,
    allow_separator_divergence: bool = False,
) -> MigrationResult:
    """Forward migration: include-with-attrs → frontmatter + bare include.

    `allow_separator_divergence=True` bypasses _is_separator_compatible. The
    summary_card render branch always uses canonical `\\n      ` separators,
    so on legacy posts whose include attributes used single-space or single-
    newline separators (e.g., output of scripts/unify_ai_summary_block.py)
    the rendered HTML will gain canonical whitespace between chips. This is
    a deliberate cosmetic-only delta — the content extracted via BS4 is
    structurally identical.
    """
    fm_split = split_frontmatter(content)
    if fm_split is None:
        return MigrationResult(path, "skipped", "no frontmatter")
    fm, rest = fm_split

    if has_summary_card_in_frontmatter(fm):
        return MigrationResult(path, "skipped", "already migrated")

    m = INCLUDE_BLOCK_RE.search(rest)
    if not m:
        return MigrationResult(path, "skipped", "no ai-summary-card include")

    # If the matched include is the bare form, no migration needed.
    full_block = m.group(0)
    if BARE_INCLUDE_RE.fullmatch(full_block.strip()):
        # Frontmatter has no summary_card but body uses bare include — leave alone.
        return MigrationResult(path, "skipped", "bare include without frontmatter")

    body = m.group("body")
    captures = extract_captures(rest)
    attrs = extract_attributes(body, captures)
    required = {"title", "categories_html", "tags_html", "highlights_html"}
    missing = required - set(attrs.keys())
    if missing:
        return MigrationResult(
            path, "failed", f"missing attributes: {sorted(missing)}"
        )

    if not allow_separator_divergence:
        compat, why = _is_separator_compatible(attrs)
        if not compat:
            return MigrationResult(path, "skipped", f"separator-incompatible: {why}")

    sc = build_summary_card(attrs)
    sc_yaml = emit_summary_card_yaml(sc)
    new_fm = insert_summary_card_into_frontmatter(fm, sc_yaml)

    # Replace the include block with the bare form.
    new_rest = (
        rest[: m.start()]
        + "{% include ai-summary-card.html %}"
        + rest[m.end() :]
    )
    # Remove any {% capture %} blocks whose variable was consumed by the
    # include (their HTML now lives in frontmatter, leaving them in the
    # body would produce stray output).
    consumed_vars: set[str] = set()
    for name, regex in ATTR_VAR_RES.items():
        vm = regex.search(body)
        if vm and vm.group("var") in captures:
            consumed_vars.add(vm.group("var"))
    if consumed_vars:
        def _strip_capture(match: re.Match) -> str:
            return "" if match.group("name") in consumed_vars else match.group(0)

        # Strip optional trailing newline so removed blocks do not leave
        # blank gaps in the body.
        capture_with_nl = re.compile(CAPTURE_RE.pattern + r"\n?", re.DOTALL)
        new_rest = capture_with_nl.sub(_strip_capture, new_rest)

    new_content = new_fm + new_rest
    return MigrationResult(path, "migrated", "", new_content)


def reverse_post(content: str, path: str = "<input>") -> MigrationResult:
    """Reverse migration: drop summary_card: from FM, restore include attrs.

    Note: the reverse is not byte-perfect for the original raw text; the
    include emitted will use a deterministic single-quote form.
    """
    fm_split = split_frontmatter(content)
    if fm_split is None:
        return MigrationResult(path, "skipped", "no frontmatter")
    fm, rest = fm_split
    if not has_summary_card_in_frontmatter(fm):
        return MigrationResult(path, "skipped", "no summary_card in frontmatter")

    # Parse summary_card from YAML
    import yaml

    inner = fm[4:-4]  # strip leading '---\n' and trailing '---\n'
    parsed = yaml.safe_load(inner) or {}
    sc_data = parsed.get("summary_card", {}) or {}
    sc = SummaryCard(
        title=sc_data.get("title", "") or "",
        period=sc_data.get("period", "") or "",
        audience=sc_data.get("audience", "") or "",
        categories=list(sc_data.get("categories", []) or []),
        tags=list(sc_data.get("tags", []) or []),
        highlights=list(sc_data.get("highlights", []) or []),
    )

    # Build legacy include block (single-quoted, matching common existing form)
    cat_html = " ".join(
        f'<span class="category-tag {c["class"]}">{c["label"]}</span>'
        for c in sc.categories
    )
    tags_html = "\n      ".join(
        f'<span class="tag">{t}</span>' for t in sc.tags
    )
    hl_html = "\n      ".join(
        f"<li><strong>{h['source']}</strong>: {h['title']}</li>"
        for h in sc.highlights
    )
    parts = [
        "{% include ai-summary-card.html",
        f"  title='{sc.title}'",
        f"  categories_html='{cat_html}'",
        f"  tags_html='{tags_html}'",
        f"  highlights_html='{hl_html}'",
    ]
    if sc.period:
        parts.append(f"  period='{sc.period}'")
    if sc.audience:
        parts.append(f"  audience='{sc.audience}'")
    parts.append("%}")
    legacy_block = "\n".join(parts)

    # Replace the bare include in body with the legacy block
    new_rest, n = re.subn(
        r"\{%-?\s*include\s+ai-summary-card\.html\s*-?%\}",
        legacy_block.replace("\\", "\\\\"),  # protect backslashes in re.subn
        rest,
        count=1,
    )
    if n == 0:
        return MigrationResult(path, "failed", "no bare include to restore")

    new_fm = remove_summary_card_from_frontmatter(fm)
    new_content = new_fm + new_rest
    return MigrationResult(path, "reversed", "", new_content)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate ai-summary-card include attributes into post "
            "frontmatter (option A)."
        )
    )
    parser.add_argument(
        "--posts-glob",
        default="_posts/*.md",
        help="Glob for posts to scan (default: _posts/*.md)",
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files (default).",
    )
    g.add_argument(
        "--commit",
        action="store_true",
        help="Apply changes to disk.",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse migration (frontmatter → include attrs).",
    )
    parser.add_argument(
        "--allow-separator-divergence",
        action="store_true",
        help=(
            "Bypass the byte-identity separator check. The summary_card "
            "render path always emits canonical chip separators, so legacy "
            "posts using single-space or single-newline separators will "
            "gain canonical whitespace — a cosmetic-only delta. Use to "
            "migrate the residual fallback posts left from "
            "unify_ai_summary_block.py output."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print one line per file processed.",
    )
    args = parser.parse_args(argv)

    if not args.commit and not args.dry_run:
        # Default to dry-run
        args.dry_run = True

    paths = sorted(glob.glob(args.posts_glob))
    if not paths:
        print(f"No posts matched glob: {args.posts_glob}", file=sys.stderr)
        return 1

    counts = {"migrated": 0, "reversed": 0, "skipped": 0, "failed": 0}
    failures: list[MigrationResult] = []

    def _run_one(content: str, path: str) -> MigrationResult:
        if args.reverse:
            return reverse_post(content, path)
        return migrate_post(
            content,
            path,
            allow_separator_divergence=args.allow_separator_divergence,
        )

    for path in paths:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        result = _run_one(content, path)
        counts[result.status] = counts.get(result.status, 0) + 1
        if result.status == "failed":
            failures.append(result)
        if args.verbose or result.status == "failed":
            print(f"  [{result.status}] {path}  {result.reason}")
        if args.commit and result.new_content is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(result.new_content)

    action = "reverse" if args.reverse else "forward"
    mode = "DRY-RUN" if args.dry_run else "COMMIT"
    print()
    print(f"=== {action.upper()} migration ({mode}) ===")
    print(f"Total scanned: {len(paths)}")
    for k, v in counts.items():
        if v:
            print(f"  {k}: {v}")
    if failures:
        print()
        print(f"Failures ({len(failures)}):")
        for r in failures:
            print(f"  {r.path}: {r.reason}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

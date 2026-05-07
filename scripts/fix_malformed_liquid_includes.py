#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

CURLY_QUOTES = {
    "\u201c": '"',  # LEFT DOUBLE QUOTATION MARK
    "\u201d": '"',  # RIGHT DOUBLE QUOTATION MARK
    "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
    "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
}

# Curly replacements for ASCII quotes found *inside* attribute values.
# These Unicode characters do NOT terminate an attribute delimiter, so they
# are safe to use as inner-value apostrophes / quote marks.
_CURLY_APOSTROPHE = "\u2019"  # RIGHT SINGLE QUOTATION MARK
_CURLY_RIGHT_DQ = "\u201d"    # RIGHT DOUBLE QUOTATION MARK


# ---------------------------------------------------------------------------
# Core attribute-conflict detection / fix
# ---------------------------------------------------------------------------

def _iter_attr_spans(inner: str):
    """Yield ``(attr_name, outer_quote, val_start, val_end)`` tuples.

    *inner* is the text **between** the opening ``{% include name.html``
    marker and the closing ``%}``.

    Simulates Liquid's naive tokeniser: the attribute value starts after
    ``=`` + opening-quote and ends at the **first** occurrence of the same
    ASCII quote character.

    Yields the *intended* full value span, including any "leftover" content
    that Liquid would see as a parse error because an inner apostrophe /
    double-quote terminated the value early.
    """
    pos = 0
    while pos < len(inner):
        ws = re.match(r"\s+", inner[pos:])
        if ws:
            pos += ws.end()
            continue

        attr_m = re.match(r"([\w][\w-]*)\s*=\s*([\"'])", inner[pos:])
        if not attr_m:
            pos += 1
            continue

        attr_name = attr_m.group(1)
        outer_quote = attr_m.group(2)
        val_start = pos + attr_m.end()

        # Liquid's first close quote
        first_close = inner.find(outer_quote, val_start)
        if first_close == -1:
            pos = val_start
            continue

        # Text after that first close quote, up to the next attribute or end
        after = inner[first_close + 1:]
        next_attr_m = re.search(r"\s+[\w][\w-]*\s*=\s*[\"']", after)
        between = after[: next_attr_m.start()] if next_attr_m else after

        last_close_in_between = between.rfind(outer_quote)
        if last_close_in_between >= 0 and between[:last_close_in_between].strip():
            # The attribute value was broken by an inner quote
            real_val_end = first_close + 1 + last_close_in_between
        else:
            real_val_end = first_close

        yield attr_name, outer_quote, val_start, real_val_end

        pos = real_val_end + 1


def detect_attr_conflicts(block: str) -> list[tuple[str, str]]:
    """Return ``(attr_name, description)`` for every attribute-quote conflict.

    A *conflict* occurs when an ASCII attribute delimiter (``'`` or ``"``)
    appears inside the value it delimits, causing Liquid to terminate the
    attribute early.

    Curly/typographic quote characters (U+2018 U+2019 U+201C U+201D) are
    **not** ASCII and do not conflict.
    """
    open_m = re.match(r"\{%-?\s*include\s+\S+\s*", block)
    close_m = re.search(r"-?%\}\s*$", block)
    if not open_m or not close_m:
        return []

    inner = block[open_m.end(): close_m.start()]
    conflicts: list[tuple[str, str]] = []
    pos = 0

    while pos < len(inner):
        ws = re.match(r"\s+", inner[pos:])
        if ws:
            pos += ws.end()
            continue

        attr_m = re.match(r"([\w][\w-]*)\s*=\s*([\"'])", inner[pos:])
        if not attr_m:
            pos += 1
            continue

        attr_name = attr_m.group(1)
        outer_quote = attr_m.group(2)
        val_start = pos + attr_m.end()

        first_close = inner.find(outer_quote, val_start)
        if first_close == -1:
            pos = val_start
            continue

        after = inner[first_close + 1:]
        next_attr_m = re.search(r"\s+[\w][\w-]*\s*=\s*[\"']", after)
        between = after[: next_attr_m.start()] if next_attr_m else after

        last_close_in_between = between.rfind(outer_quote)
        if last_close_in_between >= 0 and between[:last_close_in_between].strip():
            conflicts.append(
                (
                    attr_name,
                    f"outer={outer_quote!r} contains ASCII "
                    f"{'apostrophe' if outer_quote == chr(39) else 'double-quote'} "
                    f"inside value",
                )
            )
            pos = first_close + 1 + last_close_in_between + 1
            if next_attr_m is None:
                break
        else:
            pos = first_close + 1

    return conflicts


def _fix_attr_conflicts_in_block(block: str) -> tuple[str, int]:
    """Fix attribute-quote conflicts in a single Liquid include block.

    For each attribute whose value contains the same ASCII character used as
    the outer delimiter, replaces the inner occurrences with the curly Unicode
    counterpart:

    * ``'`` (U+0027) → ``'`` (U+2019 RIGHT SINGLE QUOTATION MARK)
    * ``"`` (U+0022) → ``"`` (U+201D RIGHT DOUBLE QUOTATION MARK)

    Curly quotes already present in values are **not** touched (they are safe
    inside any attribute value).

    Returns ``(fixed_block, change_count)``.
    """
    open_m = re.match(r"(\{%-?\s*include\s+\S+\s*)", block)
    close_m = re.search(r"(-?%\})\s*$", block)
    if not open_m or not close_m:
        return block, 0

    prefix = block[: open_m.end()]
    suffix = block[close_m.start():]
    inner = block[open_m.end(): close_m.start()]

    result = list(inner)
    changes = 0
    pos = 0

    while pos < len(inner):
        ws = re.match(r"\s+", inner[pos:])
        if ws:
            pos += ws.end()
            continue

        attr_m = re.match(r"([\w][\w-]*\s*=\s*)([\"'])", inner[pos:])
        if not attr_m:
            pos += 1
            continue

        outer_quote = attr_m.group(2)
        val_start = pos + attr_m.end()

        first_close = inner.find(outer_quote, val_start)
        if first_close == -1:
            pos = val_start
            continue

        after = inner[first_close + 1:]
        next_attr_m = re.search(r"\s+[\w][\w-]*\s*=\s*[\"']", after)
        between = after[: next_attr_m.start()] if next_attr_m else after

        last_close_in_between = between.rfind(outer_quote)
        if last_close_in_between >= 0 and between[:last_close_in_between].strip():
            curly = _CURLY_APOSTROPHE if outer_quote == "'" else _CURLY_RIGHT_DQ
            # Replace the first (conflict) close quote with curly
            result[first_close] = curly
            # Replace any additional outer_quote chars in the leftover span
            between_start = first_close + 1
            between_end = first_close + 1 + last_close_in_between
            for idx in range(between_start, between_end):
                if result[idx] == outer_quote:
                    result[idx] = curly
            changes += 1
            pos = between_end + 1
            if next_attr_m is None:
                break
        else:
            pos = first_close + 1

    fixed_inner = "".join(result)
    if fixed_inner == inner:
        return block, 0
    return prefix + fixed_inner + suffix, changes


def _curly_quotes_outside_values(block: str) -> bool:
    """Return True if *block* contains curly quotes **outside** attribute values.

    Curly quotes *inside* attribute values are safe (they do not terminate the
    delimiter and will not cause a build error).  Only flag curly quotes that
    appear in positions where the Jekyll / Liquid parser would see them outside
    a quoted value — e.g., as spurious characters in the attribute list.
    """
    open_m = re.match(r"\{%-?\s*include\s+\S+\s*", block)
    close_m = re.search(r"-?%\}\s*$", block)
    if not open_m or not close_m:
        # Can't parse — fall back to simple check
        return any(c in block for c in CURLY_QUOTES)

    inner = block[open_m.end(): close_m.start()]
    curly_chars = set(CURLY_QUOTES)

    # Build a mask: positions that are INSIDE an attribute value are "safe"
    safe = [False] * len(inner)
    pos = 0
    while pos < len(inner):
        ws = re.match(r"\s+", inner[pos:])
        if ws:
            pos += ws.end()
            continue
        attr_m = re.match(r"[\w][\w-]*\s*=\s*([\"'])", inner[pos:])
        if not attr_m:
            pos += 1
            continue
        outer_quote = attr_m.group(1)
        val_start = pos + attr_m.end()
        # Use the full (intended) value end
        first_close = inner.find(outer_quote, val_start)
        if first_close == -1:
            pos = val_start
            continue
        after = inner[first_close + 1:]
        next_attr_m = re.search(r"\s+[\w][\w-]*\s*=\s*[\"']", after)
        between = after[: next_attr_m.start()] if next_attr_m else after
        last_close_in_between = between.rfind(outer_quote)
        if last_close_in_between >= 0 and between[:last_close_in_between].strip():
            real_end = first_close + 1 + last_close_in_between
        else:
            real_end = first_close
        for i in range(val_start, real_end):
            if i < len(safe):
                safe[i] = True
        pos = real_end + 1

    # Check if any curly quote char sits outside a safe (value) region
    for i, ch in enumerate(inner):
        if ch in curly_chars and not safe[i]:
            return True
    return False


# ---------------------------------------------------------------------------
# Public API: fix_content / check_content
# ---------------------------------------------------------------------------

def fix_content(content: str) -> tuple[str, int]:
    """Apply all fixes to *content* and return ``(fixed_content, change_count)``."""
    fixed = content
    changes = 0

    patterns = [
        ("{%% include", "{% include"),
        ("%%}", "%}"),
    ]
    for old, new in patterns:
        count = fixed.count(old)
        if count:
            fixed = fixed.replace(old, new)
            changes += count

    def _fix_block(match: re.Match) -> str:
        nonlocal changes
        block = match.group(0)

        # Step 1: normalise curly quotes → ASCII inside the block
        # (they are always replaced with ASCII in include blocks to keep the
        # outer-delimiter logic simple, since the next step then fixes any
        # conflicts that arise from this replacement)
        normalised = block
        for curly, straight in CURLY_QUOTES.items():
            normalised = normalised.replace(curly, straight)

        # Step 2: fix any attribute-quote conflicts (inner ASCII quote = outer delimiter)
        fixed_block, n = _fix_attr_conflicts_in_block(normalised)

        if fixed_block != block:
            changes += 1 if n == 0 else n
        return fixed_block

    for include_name in ("news-card", "ai-summary-card"):
        fixed = re.sub(
            rf"\{{%-?\s*include\s+{include_name}\.html\b.*?-?%\}}",
            _fix_block,
            fixed,
            flags=re.DOTALL,
        )

    return fixed, changes


def check_content(content: str) -> list[tuple[int, str, str]]:
    """Return violations found in *content* without modifying it.

    Each violation is ``(lineno, include_name, description)``.

    Detects:

    1. Curly/typographic quotes **outside** attribute values in include blocks
       (inside values they are safe and will not be flagged).
    2. ASCII apostrophe inside a single-quoted include attribute value.
    3. ASCII double-quote inside a double-quoted include attribute value.
    """
    violations: list[tuple[int, str, str]] = []
    include_re = re.compile(
        r"\{%-?\s*include\s+(news-card|ai-summary-card)\.html\b.*?-?%\}",
        re.DOTALL,
    )
    for m in include_re.finditer(content):
        include_name = m.group(1)
        lineno = content[: m.start()].count("\n") + 1
        block = m.group(0)

        # 1. Curly quotes OUTSIDE attribute values
        if _curly_quotes_outside_values(block):
            for curly in CURLY_QUOTES:
                if curly in block:
                    violations.append(
                        (lineno, include_name, f"curly quote U+{ord(curly):04X} in block")
                    )
                    break  # one report per block

        # 2. Attribute-quote conflicts (ASCII apostrophe / double-quote inside value)
        for attr_name, desc in detect_attr_conflicts(block):
            violations.append((lineno, include_name, f"attr {attr_name!r}: {desc}"))

    return violations


def process_file(path: Path, write: bool) -> int:
    original = path.read_text(encoding="utf-8")
    if write:
        fixed, changes = fix_content(original)
        if changes:
            path.write_text(fixed, encoding="utf-8")
        return changes
    else:
        violations = check_content(original)
        if violations:
            for lineno, inc, desc in violations:
                print(f"  {path}:{lineno}: [{inc}] {desc}")
        return len(violations)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fix malformed Liquid include tags")
    parser.add_argument(
        "--path",
        default="_posts",
        help="target posts directory (default: _posts)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="check only; exit 1 if malformed tags are found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"skip: path not found: {root}")
        return 0

    total_files = 0
    total_issues = 0
    files_with_issues = 0

    for post in sorted(root.glob("*.md")):
        issues = process_file(post, write=not args.check)
        total_files += 1
        if issues:
            files_with_issues += 1
            total_issues += issues
            if not args.check:
                print(f"{post}: fixed {issues} malformed include tokens")

    if files_with_issues == 0:
        print(f"ok: scanned {total_files} files; no malformed include tags")
        return 0

    print(
        f"{'detected' if args.check else 'fixed'}: "
        f"{files_with_issues} files, {total_issues} violations"
    )
    return 1 if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())

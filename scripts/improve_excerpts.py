#!/usr/bin/env python3
"""Improve post excerpts for better RSS feed quality.

Strategy:
1. too_generic: Replace with description-based excerpt (150-250 chars)
2. too_short: Expand using description field
3. Already good: Skip
"""

import os
import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

# Minimum quality thresholds
MIN_EXCERPT_LEN = 80
MAX_EXCERPT_LEN = 250

GENERIC_PATTERNS = [
    r"^2\d{3}년 \d{2}월 \d{2}일 주요 보안/기술 뉴스 \d+건",
    r"^주요 보안/기술 뉴스 \d+건",
    r"^주요 기술 블로그 뉴스 \d+건",
]


def extract_yaml_field(fm_text, field):
    """Extract a YAML field value, handling multi-line strings."""
    # Try single-line first
    match = re.search(rf"^{field}:\s*['\"]?(.*?)(?:['\"]?\s*$)", fm_text, re.MULTILINE)
    if not match:
        return None

    value = match.group(1).strip().strip("'\"")

    # Check for multi-line continuation (indented lines after)
    lines_after = fm_text[match.end() :]
    continued = []
    for line in lines_after.split("\n"):
        if line.startswith("  ") and not line.strip().startswith("-"):
            continued.append(line.strip())
        else:
            break

    if continued:
        value = value + " " + " ".join(continued)

    return value.strip()


def is_generic(excerpt):
    """Check if excerpt matches generic patterns."""
    for pat in GENERIC_PATTERNS:
        if re.match(pat, excerpt):
            return True
    return False


def create_improved_excerpt(description, current_excerpt, title):
    """Create an improved excerpt from description."""
    # Clean description
    desc = description.strip().strip("'\"")
    desc = re.sub(r"\n\s+", " ", desc)

    # If description is good length and informative, use it
    if len(desc) > MAX_EXCERPT_LEN:
        # Truncate at sentence boundary
        sentences = re.split(r"[.。]\s*", desc)
        result = ""
        for s in sentences:
            candidate = result + s + "."
            if len(candidate) > MAX_EXCERPT_LEN:
                break
            result = candidate
        if len(result) < MIN_EXCERPT_LEN:
            # Just truncate
            result = desc[:MAX_EXCERPT_LEN].rsplit(" ", 1)[0]
            if not result.endswith((".", "다", "니다")):
                result += "."
        return result.strip()

    if len(desc) >= MIN_EXCERPT_LEN:
        return desc

    # Description too short - use it alone if still better than current excerpt
    # Never combine desc + excerpt as they often contain similar content
    if len(desc) > len(current_excerpt):
        return desc

    # Use title + description as fallback
    if title and len(desc) < MIN_EXCERPT_LEN:
        combined = f"{title} - {desc}".strip()
        if len(combined) > MAX_EXCERPT_LEN:
            return combined[:MAX_EXCERPT_LEN].rsplit(" ", 1)[0] + "."
        if len(combined) >= MIN_EXCERPT_LEN:
            return combined

    # Return description if it's at least somewhat useful
    if len(desc) > 30:
        return desc

    return current_excerpt


def process_file(filepath, dry_run=False):
    """Process a single file and improve its excerpt."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None, None, None

    fm_text = fm_match.group(1)

    # Extract fields
    excerpt = extract_yaml_field(fm_text, "excerpt") or ""
    description = extract_yaml_field(fm_text, "description") or ""
    title = extract_yaml_field(fm_text, "title") or ""

    # Determine if improvement needed
    needs_improvement = False
    reason = None

    if is_generic(excerpt):
        needs_improvement = True
        reason = "too_generic"
    elif len(excerpt) < MIN_EXCERPT_LEN:
        needs_improvement = True
        reason = "too_short"

    if not needs_improvement:
        return None, None, None

    # Create improved excerpt
    new_excerpt = create_improved_excerpt(description, excerpt, title)

    if new_excerpt == excerpt or len(new_excerpt) < len(excerpt):
        return None, None, None

    if dry_run:
        return reason, excerpt, new_excerpt

    # Replace excerpt in content
    # Find the exact excerpt line(s) in front matter
    # Handle both single-line and multi-line YAML excerpt
    excerpt_pattern = re.compile(r"^(excerpt:\s*)(.+(?:\n  .+)*)", re.MULTILINE)

    def replace_excerpt(m):
        prefix = "excerpt: "
        # Escape for YAML - use double quotes if contains special chars
        if any(
            c in new_excerpt
            for c in [
                ":",
                "'",
                '"',
                "#",
                "{",
                "}",
                "[",
                "]",
                ",",
                "&",
                "*",
                "?",
                "|",
                "-",
                "<",
                ">",
                "=",
                "!",
                "%",
                "@",
                "`",
            ]
        ):
            escaped = new_excerpt.replace('"', '\\"')
            return f'{prefix}"{escaped}"'
        return f"{prefix}{new_excerpt}"

    new_content = excerpt_pattern.sub(replace_excerpt, content, count=1)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return reason, excerpt, new_excerpt


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    total = 0
    generic_fixed = 0
    short_fixed = 0
    skipped = 0
    errors = []

    for filepath in sorted(POSTS_DIR.glob("*.md")):
        try:
            reason, old_exc, new_exc = process_file(filepath, dry_run)

            if reason is None:
                skipped += 1
                continue

            total += 1
            if reason == "too_generic":
                generic_fixed += 1
            elif reason == "too_short":
                short_fixed += 1

            if verbose or dry_run:
                tag = "[DRY]" if dry_run else "[OK]"
                print(f"\n{tag} {filepath.name} ({reason})")
                print(f"  OLD ({len(old_exc)}): {old_exc[:100]}")
                print(f"  NEW ({len(new_exc)}): {new_exc[:100]}")

        except Exception as e:
            errors.append((filepath.name, str(e)))
            print(f"  [ERR] {filepath.name}: {e}")

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Summary:")
    print(f"  Total improved: {total}")
    print(f"  Generic fixed: {generic_fixed}")
    print(f"  Short expanded: {short_fixed}")
    print(f"  Skipped (good): {skipped}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for name, err in errors:
            print(f"    - {name}: {err}")


if __name__ == "__main__":
    main()

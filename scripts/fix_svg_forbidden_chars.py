#!/usr/bin/env python3
"""
Fix forbidden characters in SVG <text> elements.

Replaces the following inside <text> and <tspan> text content only
(never touches attribute values, IDs, classes, font-family, or comments):

  U+00B7 middle dot     ·  ->  -   (hyphen)
  U+2022 bullet         •  ->  *
  U+2014 em dash        —  ->  --
  U+2013 en dash        –  ->  -
  U+201C left dquote    "  ->  "
  U+201D right dquote   "  ->  "
  U+2018 left squote    '  ->  '
  U+2019 right squote   '  ->  '

Also replaces Korean text in <text> elements with English equivalents
when a known mapping exists (for the 2026-04-26 digest file).

Usage:
    python3 scripts/fix_svg_forbidden_chars.py [--dry-run] [path ...]

    path  SVG file or directory (default: assets/images/)
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# Replacement map applied to text content inside <text>/<tspan> elements
CHAR_REPLACEMENTS: list[tuple[str, str]] = [
    ("\u00B7", "-"),    # middle dot
    ("\u2022", "*"),    # bullet
    ("\u2014", "--"),   # em dash
    ("\u2013", "-"),    # en dash
    ("\u201C", '"'),    # left double quotation mark
    ("\u201D", '"'),    # right double quotation mark
    ("\u2018", "'"),    # left single quotation mark
    ("\u2019", "'"),    # right single quotation mark
]

FORBIDDEN_RE = re.compile(
    r"[\u00B7\u2022\u2014\u2013\u201C\u201D\u2018\u2019]"
)

KOREAN_RE = re.compile(r"[\uAC00-\uD7A3]")

# Known Korean -> English mappings for text elements in SVG files.
# Keys are matched as substrings after stripping whitespace.
KOREAN_TEXT_REPLACEMENTS: list[tuple[str, str]] = [
    (
        "연구원들, 엔지니어링 소프트웨어 노리는 스턱스넷 이전 'fast16' 악성코드 발견",
        "Researchers Find Pre-Stuxnet 'fast16' Malware Targeting Engineering Software",
    ),
    (
        "연구원들, 엔지니어링 소프트웨어 노리는 스턱스넷 이전",
        "Researchers Find Pre-Stuxnet Malware",
    ),
    # Residual Korean suffix left after partial replacement of the long title
    # Note: curly apostrophes were already replaced to straight by the char fixer
    (
        "\u2018fast16\u2019 \uc545\uc131\ucf54\ub4dc \ubc1c\uacac",
        "'fast16' Malware Discovered",
    ),
    (
        "'fast16' \uc545\uc131\ucf54\ub4dc \ubc1c\uacac",
        "'fast16' Malware Discovered",
    ),
    (
        "기술적 배경 및 위협 분석",
        "Technical Background and Threat Analysis",
    ),
    (
        "실무 영향 분석",
        "Practical Impact Analysis",
    ),
]


def _apply_char_replacements(text: str) -> str:
    """Apply the forbidden-char replacement map to a string."""
    for old, new in CHAR_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def _apply_korean_replacements(text: str) -> str:
    """Replace known Korean strings with English equivalents."""
    stripped = text.strip()
    for korean, english in KOREAN_TEXT_REPLACEMENTS:
        if korean in stripped:
            # Preserve leading/trailing whitespace from the original
            leading = text[: len(text) - len(text.lstrip())]
            trailing = text[len(text.rstrip()) :]
            return leading + stripped.replace(korean, english) + trailing
    return text


def _fix_element_text(text: str | None) -> tuple[str | None, int]:
    """Fix a single text string. Returns (new_text, replacements_made)."""
    if not text:
        return text, 0
    original = text
    if KOREAN_RE.search(text):
        text = _apply_korean_replacements(text)
    text = _apply_char_replacements(text)
    count = sum(1 for a, b in zip(original, text) if a != b)
    # For length-changing replacements, just check inequality
    replaced = 0 if text == original else max(1, len(original) - len(text) + 1)
    return text, replaced


def _count_issues(text: str | None) -> int:
    if not text:
        return 0
    return len(FORBIDDEN_RE.findall(text)) + (1 if KOREAN_RE.search(text) else 0)


def fix_svg_file(path: Path, dry_run: bool = False) -> dict:
    """
    Fix forbidden chars in one SVG file.

    Returns a dict:
        modified: bool
        forbidden_replacements: int
        korean_replacements: int
        skipped_attrs: list[str]   # attrs that contained forbidden chars (skipped)
        error: str | None
    """
    result = {
        "modified": False,
        "forbidden_replacements": 0,
        "korean_replacements": 0,
        "skipped_attrs": [],
        "error": None,
    }

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        result["error"] = str(exc)
        return result

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        result["error"] = f"XML parse error: {exc}"
        return result

    def local(tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    modified = False

    for elem in tree.iter():
        tag = local(elem.tag)
        if tag not in ("text", "tspan"):
            continue

        # Fix elem.text
        if elem.text and (FORBIDDEN_RE.search(elem.text) or KOREAN_RE.search(elem.text)):
            original = elem.text
            new_text = original
            if KOREAN_RE.search(new_text):
                new_text = _apply_korean_replacements(new_text)
                if new_text != original:
                    result["korean_replacements"] += 1
            fixed = _apply_char_replacements(new_text)
            n_forbidden = len(FORBIDDEN_RE.findall(new_text))
            if fixed != new_text:
                result["forbidden_replacements"] += n_forbidden
            if fixed != original:
                elem.text = fixed
                modified = True

        # Fix child tail text (text after a child element, still inside <text>)
        for child in elem:
            if child.text and (FORBIDDEN_RE.search(child.text) or KOREAN_RE.search(child.text)):
                original = child.text
                new_text = original
                if KOREAN_RE.search(new_text):
                    new_text = _apply_korean_replacements(new_text)
                    if new_text != original:
                        result["korean_replacements"] += 1
                fixed = _apply_char_replacements(new_text)
                n_forbidden = len(FORBIDDEN_RE.findall(new_text))
                if fixed != new_text:
                    result["forbidden_replacements"] += n_forbidden
                if fixed != original:
                    child.text = fixed
                    modified = True

            if child.tail and (FORBIDDEN_RE.search(child.tail) or KOREAN_RE.search(child.tail)):
                original = child.tail
                new_text = original
                if KOREAN_RE.search(new_text):
                    new_text = _apply_korean_replacements(new_text)
                    if new_text != original:
                        result["korean_replacements"] += 1
                fixed = _apply_char_replacements(new_text)
                n_forbidden = len(FORBIDDEN_RE.findall(new_text))
                if fixed != new_text:
                    result["forbidden_replacements"] += n_forbidden
                if fixed != original:
                    child.tail = fixed
                    modified = True

    result["modified"] = modified

    if modified and not dry_run:
        # Write back using string replacement on raw content to preserve
        # XML declaration, DOCTYPE, namespace declarations, comments,
        # processing instructions, and exact attribute formatting.
        # We replace only the text node values we changed.
        #
        # Strategy: re-parse original and new side-by-side using regex
        # to replace text content between > and < that belongs to text/tspan.
        # This is safe because L22 SVGs are well-formed and have no CDATA.
        new_content = _apply_text_content_fix(content)
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
        else:
            # ElementTree modified in-memory but string approach found nothing?
            # Fall back to serialising via ET (may alter namespace declarations
            # but preserves correctness).
            ET.register_namespace("", "http://www.w3.org/2000/svg")
            ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
            tree.write(str(path), encoding="unicode", xml_declaration=False)

    return result


def _apply_text_content_fix(content: str) -> str:
    """
    Apply char replacements to text content between SVG text/tspan tags only.

    Uses a regex that matches text node content (between > and <) inside
    <text ...> ... </text> blocks. Handles nested <tspan> elements.

    Does NOT touch attribute values, comments, or CDATA.
    """
    # Match the content of <text> and <tspan> elements (non-greedy).
    # This captures the raw text nodes between tags.
    # Pattern: find everything inside a text or tspan element, then
    # replace individual text-node runs (between > and <).

    def replace_text_nodes(m: re.Match) -> str:
        block = m.group(0)
        # Replace chars in text nodes only: content between > and <
        def fix_node(nm: re.Match) -> str:
            text = nm.group(1)
            fixed = text
            # Korean replacements first
            stripped = text.strip()
            for korean, english in KOREAN_TEXT_REPLACEMENTS:
                if korean in stripped:
                    leading = text[: len(text) - len(text.lstrip())]
                    trailing = text[len(text.rstrip()) :]
                    fixed = leading + stripped.replace(korean, english) + trailing
                    break
            # Then forbidden chars
            for old, new in CHAR_REPLACEMENTS:
                fixed = fixed.replace(old, new)
            return ">" + fixed + "<"
        block = re.sub(r">([^<]+)<", fix_node, block)
        return block

    # Match each <text ...> block including nested tags
    pattern = re.compile(
        r"<text\b[^>]*>.*?</text>",
        re.DOTALL,
    )
    return pattern.sub(replace_text_nodes, content)


def collect_svg_files(targets: list[str]) -> list[Path]:
    paths: list[Path] = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            paths.extend(sorted(p.rglob("*.svg")))
        elif p.is_file() and p.suffix == ".svg":
            paths.append(p)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix forbidden chars in SVG <text> elements"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=[str(IMAGES_DIR)],
        help="SVG files or directories to process (default: assets/images/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing files",
    )
    args = parser.parse_args()

    svg_files = collect_svg_files(args.targets)
    if not svg_files:
        print("No SVG files found.")
        return 0

    total_modified = 0
    total_forbidden = 0
    total_korean = 0
    errors: list[str] = []

    for path in svg_files:
        result = fix_svg_file(path, dry_run=args.dry_run)
        if result["error"]:
            errors.append(f"{path}: {result['error']}")
            continue
        if result["modified"]:
            total_modified += 1
            total_forbidden += result["forbidden_replacements"]
            total_korean += result["korean_replacements"]
            mode = "[DRY-RUN]" if args.dry_run else "[FIXED]"
            rel = path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path
            print(
                f"{mode} {rel}  "
                f"(forbidden={result['forbidden_replacements']}, "
                f"korean={result['korean_replacements']})"
            )

    print()
    print(f"Files {'would be ' if args.dry_run else ''}modified: {total_modified}")
    print(f"Forbidden-char replacements: {total_forbidden}")
    print(f"Korean-text replacements: {total_korean}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

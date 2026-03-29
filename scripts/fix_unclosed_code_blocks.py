#!/usr/bin/env python3
"""
fix_unclosed_code_blocks.py - Detect and fix unclosed code blocks in Jekyll blog posts.

Algorithm:
  1. Scan all .md files in _posts/
  2. Skip YAML front matter (--- delimiters)
  3. Skip content inside HTML comments
  4. Track code-fence state with a stack; each opening ``` pushes, closing ``` pops
  5. If the file ends while still "inside" a code block → unclosed block detected
  6. Append a closing ``` at the end of the file (after the last non-empty line)
  7. Report all findings

Edge cases handled:
  - Front matter --- delimiters are not counted as code fences
  - HTML comment blocks (<!-- ... -->) are skipped
  - Lines starting with ``` *inside* a code block are treated as closing fences
    only when they are exactly ``` (no trailing language tag on a closer)
  - Markdown tutorial posts that intentionally show ``` as content: these are
    already inside a code block, so the fence is a closing delimiter, not an
    opener — no false positives
"""

import glob
import os
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

class FenceState:
    """Stateful parser that tracks code-fence open/close across a file."""

    def __init__(self):
        self.in_frontmatter: bool = False
        self.frontmatter_dashes: int = 0
        self.in_html_comment: bool = False
        self.in_code_block: bool = False
        self.open_line: Optional[int] = None   # 1-based line number
        self.open_lang: str = ""               # language tag on opening fence

    def feed(self, line: str, lineno: int) -> None:
        """Update state for one line (lineno is 1-based)."""
        stripped = line.strip()

        # --- Front matter tracking ---
        if lineno == 1 and stripped == "---":
            self.in_frontmatter = True
            self.frontmatter_dashes = 1
            return
        if self.in_frontmatter:
            if stripped == "---":
                self.frontmatter_dashes += 1
                if self.frontmatter_dashes >= 2:
                    self.in_frontmatter = False
            return  # nothing else to do inside front matter

        # --- HTML comment tracking ---
        if "<!--" in line:
            if "-->" not in line:
                self.in_html_comment = True
        if self.in_html_comment:
            if "-->" in line:
                self.in_html_comment = False
            return  # skip lines inside HTML comments

        # --- Code fence detection ---
        if stripped.startswith("```"):
            if not self.in_code_block:
                # Opening fence
                self.in_code_block = True
                self.open_line = lineno
                self.open_lang = stripped[3:].strip()
            else:
                # Closing fence — any line starting with ``` while inside a block
                self.in_code_block = False
                self.open_line = None
                self.open_lang = ""


def analyse_file(filepath: str):
    """
    Parse a markdown file and return info about any unclosed code block.

    Returns:
        dict with keys:
          'unclosed'   : bool
          'open_line'  : int | None    (1-based)
          'open_lang'  : str
          'total_lines': int
          'last_content_line': int     (1-based, last non-empty line)
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    state = FenceState()
    for lineno, line in enumerate(lines, start=1):
        state.feed(line, lineno)

    total = len(lines)
    last_content = total
    # Find last non-blank line
    for i in range(total - 1, -1, -1):
        if lines[i].strip():
            last_content = i + 1  # 1-based
            break

    return {
        "unclosed": state.in_code_block,
        "open_line": state.open_line,
        "open_lang": state.open_lang,
        "total_lines": total,
        "last_content_line": last_content,
    }


# ---------------------------------------------------------------------------
# Fix
# ---------------------------------------------------------------------------

def fix_file(filepath: str, info: dict, dry_run: bool = False) -> str:
    """
    Append a closing ``` to the file, right after the last content line.

    Strategy:
      - Read all lines
      - Trim any trailing blank lines
      - Append a blank line + ``` + newline
      - Write back

    Returns a human-readable description of what was done.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    lines = content.rstrip("\n").split("\n")

    # Add closing fence
    lines.append("")  # blank separator
    lines.append("```")

    new_content = "\n".join(lines) + "\n"

    action = (
        f"  Appended closing ``` (block opened at line {info['open_line']}"
        + (f" with lang '{info['open_lang']}'" if info['open_lang'] else " (bare)")
        + ")"
    )

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(new_content)

    return action


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect and fix unclosed code blocks in Jekyll _posts/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report issues without making changes",
    )
    parser.add_argument(
        "--posts-dir",
        default=None,
        help="Path to _posts/ directory (defaults to <repo-root>/_posts/)",
    )
    args = parser.parse_args()

    # Locate _posts/
    if args.posts_dir:
        posts_dir = args.posts_dir
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        posts_dir = os.path.join(script_dir, "..", "_posts")
    posts_dir = os.path.realpath(posts_dir)

    if not os.path.isdir(posts_dir):
        print(f"ERROR: _posts/ directory not found at: {posts_dir}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(glob.glob(os.path.join(posts_dir, "*.md")))
    print(f"Scanning {len(md_files)} markdown files in {posts_dir} ...")
    if args.dry_run:
        print("(DRY RUN — no files will be modified)\n")
    else:
        print()

    fixed_files = []
    clean_files = 0

    for filepath in md_files:
        fname = os.path.basename(filepath)
        info = analyse_file(filepath)

        if not info["unclosed"]:
            clean_files += 1
            continue

        # Unclosed block found
        print(f"UNCLOSED: {fname}")
        print(
            f"  Block opened at line {info['open_line']}"
            + (f" (lang: '{info['open_lang']}')" if info['open_lang'] else " (bare, no language tag)")
        )
        print(f"  File has {info['total_lines']} lines total")

        action_desc = fix_file(filepath, info, dry_run=args.dry_run)
        verb = "Would fix" if args.dry_run else "Fixed"
        print(f"  {verb}: {action_desc.strip()}")
        print()

        fixed_files.append(fname)

    # Summary
    print("=" * 60)
    if args.dry_run:
        print(f"DRY RUN complete.")
        print(f"  Files with unclosed code blocks: {len(fixed_files)}")
        print(f"  Files already clean:             {clean_files}")
    else:
        print(f"Scan complete.")
        print(f"  Files fixed:       {len(fixed_files)}")
        print(f"  Files clean:       {clean_files}")
        print(f"  Total files scanned: {len(md_files)}")

    if fixed_files:
        print()
        print("Fixed files:")
        for f in fixed_files:
            print(f"  {f}")

    return 0 if not fixed_files or not args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
fix_code_block_languages.py

Scans all _posts/*.md files and adds language tags to untagged code blocks (``` with no language).
Detects language from code content using heuristic pattern matching.

Usage:
    python3 scripts/fix_code_block_languages.py --dry-run  # Preview changes
    python3 scripts/fix_code_block_languages.py             # Apply changes
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Language detection patterns
# Each entry: (language_name, list_of_regex_patterns)
LANGUAGE_PATTERNS = [
    (
        "dockerfile",
        [
            r"^FROM\s+\S+",
            r"^RUN\s+",
            r"^COPY\s+",
            r"^CMD\s+",
            r"^ENTRYPOINT\s+",
            r"^WORKDIR\s+",
            r"^EXPOSE\s+",
            r"^ENV\s+\S+=",
            r"^ARG\s+",
            r"^LABEL\s+",
            r"^ADD\s+",
            r"^USER\s+",
            r"^VOLUME\s+",
            r"^HEALTHCHECK\s+",
        ],
    ),
    (
        "nginx",
        [
            r"server\s*\{",
            r"location\s+[/\w].*\{",
            r"proxy_pass\s+http",
            r"upstream\s+\w+\s*\{",
            r"listen\s+\d+",
            r"server_name\s+",
            r"root\s+/",
            r"nginx\.conf",
        ],
    ),
    (
        "sql",
        [
            r"^\s*SELECT\s+",
            r"^\s*INSERT\s+INTO\s+",
            r"^\s*UPDATE\s+\w+\s+SET\s+",
            r"^\s*DELETE\s+FROM\s+",
            r"^\s*CREATE\s+TABLE\s+",
            r"^\s*ALTER\s+TABLE\s+",
            r"^\s*DROP\s+TABLE\s+",
            r"^\s*CREATE\s+INDEX\s+",
            r"^\s*GRANT\s+",
            r"^\s*REVOKE\s+",
        ],
    ),
    (
        "hcl",
        [
            r'^resource\s+"[\w_]+"\s+"[\w_]+"',
            r'^provider\s+"[\w_]+"',
            r'^variable\s+"[\w_]+"',
            r'^output\s+"[\w_]+"',
            r'^module\s+"[\w_]+"',
            r'^data\s+"[\w_]+"',
            r"^terraform\s*\{",
            r"^locals\s*\{",
        ],
    ),
    (
        "go",
        [
            r"^package\s+(main|\w+)\s*$",
            r"^func\s+\w+\s*\(",
            r'^import\s+"[\w/.]+"',
            r"^import\s+\(",
            r"\bfmt\.Print",
            r"\bfmt\.Sprintf",
            r"\berr\s*:=\s*",
            r"\bgo\s+func\s*\(",
            r":=\s*make\(",
            r":=\s*new\(",
        ],
    ),
    (
        "python",
        [
            r"^import\s+\w+",
            r"^from\s+\w[\w.]*\s+import\s+",
            r"^def\s+\w+\s*\(",
            r"^class\s+\w+[\s:(]",
            r"\bprint\s*\(",
            r"^if\s+__name__\s*==\s*['\"]__main__['\"]",
            r"^\s*@\w+",
            r"^\s*elif\s+",
            r"\bself\.\w+",
            r"^\s*pass\s*$",
            r"\brange\s*\(",
            r"\blen\s*\(",
            r"\bdict\s*\(",
            r"\blist\s*\(",
        ],
    ),
    (
        "javascript",
        [
            r"\bfunction\s+\w+\s*\(",
            r"\bconst\s+\w+\s*=",
            r"\blet\s+\w+\s*=",
            r"\bvar\s+\w+\s*=",
            r"=>\s*\{",
            r"\bconsole\.log\s*\(",
            r"\brequire\s*\(",
            r"\bmodule\.exports\s*=",
            r"\bexport\s+(default|const|function|class)\s+",
            r"\basync\s+function\s+",
            r"\bawait\s+",
            r"\.then\s*\(",
            r"\.catch\s*\(",
            r"\bPromise\s*\.",
            r"\bnew\s+\w+\s*\(",
        ],
    ),
    (
        "json",
        [
            r"^\s*\{",  # starts with {
            r"^\s*\[",  # starts with [
            r'"[\w_-]+"\s*:',  # "key": pattern (inline or multiline)
            r"^\s*\}\s*,?\s*$",  # closing brace
            r"^\s*\]\s*,?\s*$",  # closing bracket
            r'^\s*"[\w_-]+"\s*:\s*"[^"]*"\s*,?\s*$',  # "key": "value"
            r'^\s*"[\w_-]+"\s*:\s*(true|false|null|\d+)\s*,?\s*$',  # "key": primitive
        ],
    ),
    (
        "yaml",
        [
            r"^---\s*$",
            r"^apiVersion:\s+\S+",
            r"^kind:\s+\S+",
            r"^metadata:\s*$",
            r"^spec:\s*$",
            r"^status:\s*$",
            r"^\s{2,}\w[\w_-]*:\s+\S",
            r"^\w[\w_-]+:\s+\S",
            r"^\s*-\s+\w",
            r"^\s*name:\s+\S+",
            r"^\s*namespace:\s+\S+",
            r"^\s*labels:\s*$",
            r"^\s*annotations:\s*$",
        ],
    ),
    (
        "html",
        [
            r"<(!DOCTYPE|html|head|body|div|span|p|a|ul|ol|li|h[1-6]|table|tr|td|th|form|input|button|script|style|link|meta|title|header|footer|nav|section|article|main)",
            r"</\w+>",
            r'<[a-z]+\s+[\w-]+=["\'"]',
            r"<!--.*-->",
        ],
    ),
    (
        "bash",
        [
            r"^\s*\$\s+",
            r"^#!.*sh\b",
            r"\bsudo\s+",
            r"\bapt(-get)?\s+(install|update|upgrade|remove)\b",
            r"\byum\s+(install|update|remove)\b",
            r"\bbrew\s+(install|update|upgrade|remove)\b",
            r"\bnpm\s+(install|run|build|start|test)\b",
            r"\bpip3?\s+(install|uninstall|freeze)\b",
            r"\bkubectl\s+",
            r"\bdocker\s+(run|build|pull|push|ps|images|exec|stop|rm|rmi)\b",
            r"\bhelm\s+(install|upgrade|uninstall|repo|chart)\b",
            r"\bterraform\s+(init|plan|apply|destroy)\b",
            r"\bcurl\s+",
            r"\bwget\s+",
            r"\bchmod\s+[0-7]+",
            r"\bmkdir\s+",
            r"\bcd\s+",
            r"\bls\s+",
            r"\bcat\s+",
            r"\bgrep\s+",
            r"\bsed\s+",
            r"\bawk\s+",
            r"\bexport\s+\w+=",
            r"\bgit\s+(clone|add|commit|push|pull|checkout|branch|status|log)\b",
            r"\becho\s+",
            r"\bif\s+\[\s*",
            r"\bfor\s+\w+\s+in\s+",
            r"\bwhile\s+",
            r"&&\s*\\?\s*$",
            r"\|\s*\\?\s*$",
            r"^\s*#\s+\w",
            r"\bsystemctl\s+",
            r"\bservice\s+\w+\s+(start|stop|restart|status)\b",
            r"\benv\s+\w+=",
            r"\bsource\s+",
            r"\b\.\s+\./",
        ],
    ),
]


def detect_language(code_lines: list[str]) -> str:
    """
    Detect language from code content by scoring pattern matches.
    Analyzes first 10 lines (or all if fewer).
    Returns detected language name or 'text' if uncertain.
    """
    sample = code_lines[:10]
    sample_text = "\n".join(sample)

    scores: dict[str, int] = defaultdict(int)

    for lang, patterns in LANGUAGE_PATTERNS:
        for pattern in patterns:
            if re.search(
                pattern,
                sample_text,
                re.MULTILINE | re.IGNORECASE if lang in ("sql",) else re.MULTILINE,
            ):
                scores[lang] += 1

    if not scores:
        return "text"

    # Pick highest score
    best_lang = max(scores, key=lambda k: scores[k])
    best_score = scores[best_lang]

    # Require at least 1 match; if tied, prefer more specific language
    if best_score == 0:
        return "text"

    # Special ambiguity: yaml vs json
    if best_lang == "yaml" and scores.get("json", 0) > 0:
        # JSON blocks usually start with { or [
        first_non_empty = next((l.strip() for l in sample if l.strip()), "")
        if first_non_empty.startswith(("{", "[")):
            best_lang = "json"

    # Special ambiguity: bash vs python/go/etc
    # If python/go score >= bash score, prefer them (bash patterns are broad)
    if best_lang == "bash":
        for competitor in (
            "python",
            "go",
            "javascript",
            "dockerfile",
            "nginx",
            "sql",
            "hcl",
        ):
            if scores.get(competitor, 0) >= best_score:
                best_lang = competitor
                break

    return best_lang


def process_file(filepath: Path, dry_run: bool) -> dict:
    """
    Process a single markdown file.
    Returns stats dict: {total_blocks, fixed_blocks, languages: {lang: count}}
    """
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    stats = {
        "total_blocks": 0,
        "fixed_blocks": 0,
        "languages": defaultdict(int),
        "changes": [],  # list of (line_num, old, new, lang)
    }

    # State machine to track position in document
    in_front_matter = False
    front_matter_done = False
    front_matter_count = 0  # Count --- to detect front matter boundaries

    in_code_block = False
    code_block_indent = ""
    code_block_fence = ""
    code_block_start_line = -1
    code_block_lines = []

    new_lines = list(lines)
    replacements = []  # (line_index, new_line_content)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n\r")

        # Front matter detection (--- at start of file)
        if not front_matter_done:
            if i == 0 and stripped.strip() == "---":
                in_front_matter = True
                front_matter_count = 1
                i += 1
                continue
            elif in_front_matter:
                if stripped.strip() == "---" and front_matter_count == 1:
                    in_front_matter = False
                    front_matter_done = True
                i += 1
                continue
            else:
                front_matter_done = True

        if in_code_block:
            # Check for closing fence
            closing = re.match(r"^(\s*)(`{3,}|~{3,})\s*$", stripped)
            if (
                closing
                and closing.group(2) == code_block_fence
                and closing.group(1) == code_block_indent
            ):
                in_code_block = False
                # We already processed the opening fence replacement earlier
                code_block_lines = []
        else:
            # Check for opening fence
            opening = re.match(r"^(\s*)(`{3,}|~{3,})(\S*)\s*$", stripped)
            if opening:
                indent = opening.group(1)
                fence = opening.group(2)
                lang_tag = opening.group(3)

                if lang_tag == "":
                    # Untagged code block - collect content and detect language
                    stats["total_blocks"] += 1

                    # Gather code content (next lines until closing fence)
                    code_content = []
                    j = i + 1
                    while j < len(lines):
                        next_stripped = lines[j].rstrip("\n\r")
                        closing = re.match(r"^(\s*)(`{3,}|~{3,})\s*$", next_stripped)
                        if (
                            closing
                            and closing.group(2) == fence
                            and closing.group(1) == indent
                        ):
                            break
                        code_content.append(next_stripped)
                        j += 1

                    detected_lang = detect_language(code_content)
                    stats["fixed_blocks"] += 1
                    stats["languages"][detected_lang] += 1
                    stats["changes"].append(
                        (
                            i + 1,
                            stripped,
                            f"{indent}{fence}{detected_lang}",
                            detected_lang,
                        )
                    )

                    replacements.append((i, f"{indent}{fence}{detected_lang}\n"))

                    # Skip into code block to avoid re-processing
                    in_code_block = True
                    code_block_indent = indent
                    code_block_fence = fence
                else:
                    # Tagged block - skip it entirely
                    in_code_block = True
                    code_block_indent = indent
                    code_block_fence = fence

        i += 1

    # Apply replacements (in reverse order to preserve indices)
    for line_idx, new_content in replacements:
        new_lines[line_idx] = new_content

    if replacements and not dry_run:
        filepath.write_text("".join(new_lines), encoding="utf-8")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Add language tags to untagged code blocks in Jekyll blog posts."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files.",
    )
    parser.add_argument(
        "--posts-dir",
        default="_posts",
        help="Directory containing markdown posts (default: _posts).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed changes per file.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    posts_dir = repo_root / args.posts_dir

    if not posts_dir.exists():
        print(f"Error: Posts directory not found: {posts_dir}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(posts_dir.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {posts_dir}")
        sys.exit(0)

    mode_label = "[DRY RUN] " if args.dry_run else ""
    print(f"{mode_label}Scanning {len(md_files)} posts in {posts_dir}...\n")

    total_files_changed = 0
    total_blocks_found = 0
    total_blocks_fixed = 0
    global_lang_stats: dict[str, int] = defaultdict(int)

    for filepath in md_files:
        try:
            stats = process_file(filepath, dry_run=args.dry_run)
        except Exception as e:
            print(f"  ERROR processing {filepath.name}: {e}", file=sys.stderr)
            continue

        total_blocks_found += stats["total_blocks"]

        if stats["fixed_blocks"] > 0:
            total_files_changed += 1
            total_blocks_fixed += stats["fixed_blocks"]
            for lang, count in stats["languages"].items():
                global_lang_stats[lang] += count

            print(f"  {'[WOULD FIX]' if args.dry_run else '[FIXED]'} {filepath.name}")
            print(f"    Untagged blocks found: {stats['total_blocks']}")

            if args.verbose or args.dry_run:
                for line_num, old, new, lang in stats["changes"]:
                    print(f"    Line {line_num:4d}: {old!r} → {new!r}  [{lang}]")
            else:
                lang_summary = ", ".join(
                    f"{lang}={cnt}" for lang, cnt in sorted(stats["languages"].items())
                )
                print(f"    Languages detected: {lang_summary}")
            print()

    # Summary
    print("=" * 60)
    print(f"{mode_label}Summary")
    print("=" * 60)
    print(f"  Posts scanned:          {len(md_files)}")
    print(f"  Posts with changes:     {total_files_changed}")
    print(f"  Untagged blocks found:  {total_blocks_found}")
    print(
        f"  Blocks {'would be ' if args.dry_run else ''}fixed:      {total_blocks_fixed}"
    )
    print()
    if global_lang_stats:
        print("  Language detection breakdown:")
        for lang, count in sorted(global_lang_stats.items(), key=lambda x: -x[1]):
            bar = "#" * min(count, 40)
            print(f"    {lang:<15s} {count:4d}  {bar}")
    print()

    if args.dry_run and total_blocks_fixed > 0:
        print("Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()

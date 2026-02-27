#!/usr/bin/env python3
"""
포스트 코드 블록 품질 자동 수정 스크립트
- 언어 태그 없는 코드 블록에 적절한 언어 태그 추가
- 열리지 않은(unclosed) 코드 블록 수정
"""

import re
import os
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

# Language detection patterns (order matters - more specific first)
LANG_PATTERNS = [
    # Shell/Bash
    (r'^\s*(sudo |apt |yum |brew |npm |pip |gem |bundle |docker |kubectl |helm |terraform |aws |gcloud |az |curl |wget |chmod |chown |mkdir |cp |mv |rm |ls |cd |cat |grep |sed |awk |export |source |echo |git |ssh |scp |systemctl |journalctl |make |go |cargo |rustup)', 'bash'),
    (r'^\s*\$\s+', 'bash'),
    (r'^\s*(#!/bin/bash|#!/bin/sh|#!/usr/bin/env bash)', 'bash'),
    (r'^\s*#.*install|#.*설치|#.*설정|#.*확인|#.*실행|#.*생성|#.*삭제', 'bash'),

    # YAML
    (r'^\s*(apiVersion:|kind:|metadata:|spec:|name:|namespace:|labels:|annotations:|replicas:|containers:|image:|ports:|env:|resources:|limits:|requests:|volumes:|volumeMounts:|serviceAccountName:|selector:|template:|data:|stringData:|type:|---\s*$)', 'yaml'),
    (r'^\s*[a-zA-Z_][a-zA-Z0-9_]*:\s*("|\'|true|false|null|\d+|\[|{|>|>-|\||\|-)', 'yaml'),

    # JSON
    (r'^\s*[{\[]', 'json'),
    (r'^\s*"[^"]+"\s*:', 'json'),

    # Python
    (r'^\s*(import |from .+ import |def |class |if __name__|print\(|try:|except |raise |with |async def |await |@)', 'python'),
    (r'^\s*(self\.|__init__|__main__|\.py)', 'python'),

    # JavaScript/TypeScript
    (r'^\s*(const |let |var |function |=>|import .+ from |export |require\(|module\.exports|console\.log|async |await )', 'javascript'),
    (r'^\s*(interface |type |enum |readonly |namespace )', 'typescript'),

    # Go
    (r'^\s*(package |func |type .+ struct|import \(|fmt\.|go |defer |chan |select {)', 'go'),

    # Rust
    (r'^\s*(fn |let mut |impl |pub |use |mod |struct |enum |trait |match |unsafe )', 'rust'),

    # SQL
    (r'^\s*(SELECT |INSERT |UPDATE |DELETE |CREATE |ALTER |DROP |FROM |WHERE |JOIN |GROUP BY|ORDER BY|GRANT |REVOKE )', 'sql', re.IGNORECASE),

    # Dockerfile
    (r'^\s*(FROM |RUN |CMD |ENTRYPOINT |COPY |ADD |ENV |EXPOSE |WORKDIR |ARG |LABEL |USER |VOLUME )', 'dockerfile'),

    # HCL/Terraform
    (r'^\s*(resource |data |variable |output |provider |module |terraform |locals )\s*"', 'hcl'),

    # INI/TOML config
    (r'^\s*\[.+\]\s*$', 'ini'),

    # HTML/XML
    (r'^\s*<(!DOCTYPE|html|head|body|div|span|script|style|link|meta|p|h[1-6]|ul|ol|li|table|tr|td|th|form|input|button|a |img )', 'html'),
    (r'^\s*<\?xml', 'xml'),

    # CSS
    (r'^\s*(\.|#|@media|@keyframes|body|html|div|span|:root)\s*{', 'css'),

    # Nginx/Apache config
    (r'^\s*(server\s*{|location\s|upstream\s|proxy_pass|listen\s|server_name)', 'nginx'),

    # Log output / plaintext
    (r'^\s*(ERROR|WARN|INFO|DEBUG|FATAL|WARNING)\s', 'text'),
    (r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', 'text'),

    # Markdown (nested)
    (r'^\s*(#{1,6}\s|>\s|\*\s|-\s|\d+\.\s)', 'markdown'),
]

# Patterns that indicate a code block is likely a terminal output/example
OUTPUT_PATTERNS = [
    r'^\s*\d+\.\s',  # numbered list in code block
    r'^\s*[-•]\s',     # bullet list in code block
    r'^\s*\|.*\|',     # table-like output
    r'^[A-Z][a-z]+:',  # Key: Value format
    r'^\s*→',          # arrow indicator
    r'^\s*✓|✗|✅|❌|⚠️',  # status indicators
]


def detect_language(code_content: str) -> str:
    """Detect the most likely language for a code block."""
    lines = code_content.strip().split('\n')
    if not lines:
        return 'text'

    # Check first few non-empty lines
    check_lines = [l for l in lines[:10] if l.strip()]
    if not check_lines:
        return 'text'

    scores = {}

    for line in check_lines:
        for pattern_tuple in LANG_PATTERNS:
            if len(pattern_tuple) == 3:
                pattern, lang, flags = pattern_tuple
            else:
                pattern, lang = pattern_tuple
                flags = 0

            if re.search(pattern, line, flags):
                scores[lang] = scores.get(lang, 0) + 1

    # Check output patterns
    output_score = 0
    for line in check_lines:
        for pattern in OUTPUT_PATTERNS:
            if re.search(pattern, line):
                output_score += 1

    if output_score > len(check_lines) * 0.5:
        return 'text'

    if scores:
        # Return the language with highest score
        best = max(scores, key=scores.get)
        return best

    # Default heuristics
    first_line = check_lines[0].strip()

    # If it looks like a command line
    if first_line.startswith('$') or first_line.startswith('#'):
        return 'bash'

    # If it looks like output/text
    if any(c in first_line for c in [':', '=', '→', '|']):
        return 'text'

    return 'text'


def fix_code_blocks(filepath: Path) -> tuple[int, int, list[str]]:
    """Fix code blocks in a post file. Returns (lang_fixes, unclosed_fixes, changes)."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    lang_fixes = 0
    unclosed_fixes = 0
    changes = []

    new_lines = []
    in_code_block = False
    code_block_start = -1
    code_block_content = []
    code_block_lang = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('```') and not in_code_block:
            # Opening code block
            in_code_block = True
            code_block_start = i
            code_block_content = []

            # Check if it has a language tag
            lang_part = stripped[3:].strip()

            if lang_part:
                code_block_lang = lang_part
                new_lines.append(line)
            else:
                code_block_lang = None
                # Will be fixed after we collect content
                new_lines.append(line)  # placeholder

            i += 1
            continue

        if in_code_block:
            if stripped == '```' or stripped == '```>':
                # Closing code block
                in_code_block = False

                if code_block_lang is None:
                    # Detect and fix language
                    detected = detect_language('\n'.join(code_block_content))
                    # Fix the opening line
                    opening_idx = len(new_lines) - len(code_block_content) - 1
                    old_opening = new_lines[opening_idx]
                    indent = old_opening[:len(old_opening) - len(old_opening.lstrip())]
                    new_lines[opening_idx] = f"{indent}```{detected}"
                    lang_fixes += 1
                    changes.append(f"  Line {code_block_start + 1}: Added language tag '{detected}'")

                # Add collected content
                for cl in code_block_content:
                    pass  # already added below

                # Fix closing line (remove trailing '>' if present)
                if stripped == '```>':
                    new_lines.append('```')
                else:
                    new_lines.append(line)

                code_block_content = []
                i += 1
                continue
            else:
                code_block_content.append(line)
                new_lines.append(line)
                i += 1
                continue

        new_lines.append(line)
        i += 1

    # Handle unclosed code block at end of file
    if in_code_block:
        unclosed_fixes += 1

        if code_block_lang is None:
            detected = detect_language('\n'.join(code_block_content))
            opening_idx = len(new_lines) - len(code_block_content) - 1
            if opening_idx >= 0:
                old_opening = new_lines[opening_idx]
                indent = old_opening[:len(old_opening) - len(old_opening.lstrip())]
                new_lines[opening_idx] = f"{indent}```{detected}"
                lang_fixes += 1
                changes.append(f"  Line {code_block_start + 1}: Added language tag '{detected}' (was unclosed)")

        new_lines.append('```')
        new_lines.append('')
        changes.append(f"  Line {code_block_start + 1}: Closed unclosed code block")

    new_content = '\n'.join(new_lines)

    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')

    return lang_fixes, unclosed_fixes, changes


def main():
    total_lang = 0
    total_unclosed = 0
    total_files = 0

    posts = sorted(POSTS_DIR.glob("*.md"))
    print(f"📝 Processing {len(posts)} posts...")
    print()

    for post in posts:
        lang_fixes, unclosed_fixes, changes = fix_code_blocks(post)

        if changes:
            total_files += 1
            total_lang += lang_fixes
            total_unclosed += unclosed_fixes
            print(f"✏️  {post.name}")
            for change in changes:
                print(change)
            print()

    print("=" * 60)
    print(f"Summary:")
    print(f"  Files modified: {total_files}")
    print(f"  Language tags added: {total_lang}")
    print(f"  Unclosed blocks fixed: {total_unclosed}")
    print("=" * 60)


if __name__ == "__main__":
    main()

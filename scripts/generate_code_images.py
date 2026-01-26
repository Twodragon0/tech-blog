#!/usr/bin/env python3
"""
코드 블록을 고퀄리티 SVG 이미지로 변환하는 스크립트

외부 라이브러리 없이 순수 Python으로 코드 이미지를 생성합니다.
Carbon/Ray.so 스타일의 고퀄리티 코드 이미지를 로컬에서 생성합니다.

Features:
- 다양한 프로그래밍 언어 지원
- 다크/라이트 테마 지원
- SVG 벡터 출력
- 라인 넘버 옵션
- macOS 스타일 윈도우 프레임
- 커스텀 스타일링
"""

import os
import re
import sys
import hashlib
import argparse
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images" / "code"

# 이미지 디렉토리 생성
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CodeBlock:
    """코드 블록 정보"""

    language: str
    code: str
    line_start: int
    line_end: int
    post_file: str
    index: int  # 같은 파일 내 코드 블록 인덱스


@dataclass
class Theme:
    """테마 설정"""

    name: str
    background: str
    text: str
    keyword: str
    string: str
    comment: str
    number: str
    function: str
    variable: str
    line_number: str
    title_bar: str
    border: str


# 테마 정의
THEMES = {
    "monokai": Theme(
        name="Monokai",
        background="#272822",
        text="#f8f8f2",
        keyword="#f92672",
        string="#e6db74",
        comment="#75715e",
        number="#ae81ff",
        function="#a6e22e",
        variable="#66d9ef",
        line_number="#75715e",
        title_bar="#3e3d32",
        border="#49483e",
    ),
    "dracula": Theme(
        name="Dracula",
        background="#282a36",
        text="#f8f8f2",
        keyword="#ff79c6",
        string="#f1fa8c",
        comment="#6272a4",
        number="#bd93f9",
        function="#50fa7b",
        variable="#8be9fd",
        line_number="#6272a4",
        title_bar="#21222c",
        border="#44475a",
    ),
    "github-dark": Theme(
        name="GitHub Dark",
        background="#0d1117",
        text="#c9d1d9",
        keyword="#ff7b72",
        string="#a5d6ff",
        comment="#8b949e",
        number="#79c0ff",
        function="#d2a8ff",
        variable="#ffa657",
        line_number="#484f58",
        title_bar="#161b22",
        border="#30363d",
    ),
    "one-dark": Theme(
        name="One Dark",
        background="#282c34",
        text="#abb2bf",
        keyword="#c678dd",
        string="#98c379",
        comment="#5c6370",
        number="#d19a66",
        function="#61afef",
        variable="#e06c75",
        line_number="#4b5263",
        title_bar="#21252b",
        border="#3e4451",
    ),
    "nord": Theme(
        name="Nord",
        background="#2e3440",
        text="#d8dee9",
        keyword="#81a1c1",
        string="#a3be8c",
        comment="#4c566a",
        number="#b48ead",
        function="#88c0d0",
        variable="#8fbcbb",
        line_number="#4c566a",
        title_bar="#242933",
        border="#3b4252",
    ),
}


# 언어별 키워드 및 하이라이팅 규칙
LANGUAGE_KEYWORDS = {
    "python": {
        "keywords": [
            "def",
            "class",
            "import",
            "from",
            "return",
            "if",
            "else",
            "elif",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "as",
            "is",
            "in",
            "not",
            "and",
            "or",
            "None",
            "True",
            "False",
            "lambda",
            "yield",
            "async",
            "await",
            "raise",
            "pass",
            "break",
            "continue",
            "global",
            "nonlocal",
            "assert",
        ],
        "builtins": [
            "print",
            "len",
            "range",
            "str",
            "int",
            "float",
            "list",
            "dict",
            "set",
            "tuple",
            "open",
            "input",
            "type",
            "isinstance",
            "getattr",
            "setattr",
            "hasattr",
            "enumerate",
            "zip",
            "map",
            "filter",
            "sorted",
            "reversed",
            "any",
            "all",
            "sum",
            "min",
            "max",
            "abs",
            "round",
        ],
    },
    "javascript": {
        "keywords": [
            "const",
            "let",
            "var",
            "function",
            "return",
            "if",
            "else",
            "for",
            "while",
            "do",
            "switch",
            "case",
            "break",
            "continue",
            "try",
            "catch",
            "finally",
            "throw",
            "new",
            "class",
            "extends",
            "import",
            "export",
            "from",
            "default",
            "async",
            "await",
            "yield",
            "this",
            "super",
            "typeof",
            "instanceof",
            "in",
            "of",
            "null",
            "undefined",
            "true",
            "false",
        ],
        "builtins": [
            "console",
            "document",
            "window",
            "Array",
            "Object",
            "String",
            "Number",
            "Boolean",
            "Promise",
            "JSON",
            "Math",
            "Date",
            "RegExp",
            "Error",
            "Map",
            "Set",
            "Symbol",
            "Proxy",
            "fetch",
            "setTimeout",
            "setInterval",
            "clearTimeout",
            "clearInterval",
        ],
    },
    "typescript": {
        "keywords": [
            "const",
            "let",
            "var",
            "function",
            "return",
            "if",
            "else",
            "for",
            "while",
            "do",
            "switch",
            "case",
            "break",
            "continue",
            "try",
            "catch",
            "finally",
            "throw",
            "new",
            "class",
            "extends",
            "implements",
            "interface",
            "type",
            "enum",
            "import",
            "export",
            "from",
            "default",
            "async",
            "await",
            "yield",
            "this",
            "super",
            "typeof",
            "instanceof",
            "in",
            "of",
            "null",
            "undefined",
            "true",
            "false",
            "public",
            "private",
            "protected",
            "static",
            "readonly",
            "abstract",
            "as",
            "is",
            "keyof",
            "never",
            "unknown",
            "any",
            "void",
        ],
        "builtins": [
            "console",
            "document",
            "window",
            "Array",
            "Object",
            "String",
            "Number",
            "Boolean",
            "Promise",
            "JSON",
            "Math",
            "Date",
            "RegExp",
            "Error",
            "Map",
            "Set",
            "Symbol",
            "Proxy",
            "fetch",
        ],
    },
    "bash": {
        "keywords": [
            "if",
            "then",
            "else",
            "elif",
            "fi",
            "for",
            "do",
            "done",
            "while",
            "until",
            "case",
            "esac",
            "in",
            "function",
            "return",
            "exit",
            "break",
            "continue",
            "export",
            "source",
            "alias",
            "unalias",
            "local",
            "declare",
            "readonly",
            "set",
            "unset",
            "shift",
            "trap",
        ],
        "builtins": [
            "echo",
            "printf",
            "read",
            "cd",
            "pwd",
            "ls",
            "mkdir",
            "rm",
            "cp",
            "mv",
            "cat",
            "grep",
            "sed",
            "awk",
            "find",
            "xargs",
            "sort",
            "uniq",
            "wc",
            "head",
            "tail",
            "cut",
            "tr",
            "test",
            "expr",
            "date",
            "sleep",
            "true",
            "false",
        ],
    },
    "yaml": {
        "keywords": ["true", "false", "null", "yes", "no", "on", "off"],
        "builtins": [],
    },
    "json": {
        "keywords": ["true", "false", "null"],
        "builtins": [],
    },
    "sql": {
        "keywords": [
            "SELECT",
            "FROM",
            "WHERE",
            "INSERT",
            "INTO",
            "VALUES",
            "UPDATE",
            "SET",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "TABLE",
            "INDEX",
            "VIEW",
            "DATABASE",
            "JOIN",
            "LEFT",
            "RIGHT",
            "INNER",
            "OUTER",
            "ON",
            "AND",
            "OR",
            "NOT",
            "IN",
            "LIKE",
            "BETWEEN",
            "IS",
            "NULL",
            "AS",
            "ORDER",
            "BY",
            "GROUP",
            "HAVING",
            "LIMIT",
            "OFFSET",
            "UNION",
            "ALL",
            "DISTINCT",
            "COUNT",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "CASE",
            "WHEN",
            "THEN",
            "ELSE",
            "END",
            "EXISTS",
            "PRIMARY",
            "KEY",
            "FOREIGN",
            "REFERENCES",
            "UNIQUE",
            "DEFAULT",
            "AUTO_INCREMENT",
        ],
        "builtins": [],
    },
    "dockerfile": {
        "keywords": [
            "FROM",
            "RUN",
            "CMD",
            "ENTRYPOINT",
            "COPY",
            "ADD",
            "WORKDIR",
            "EXPOSE",
            "ENV",
            "ARG",
            "VOLUME",
            "USER",
            "LABEL",
            "MAINTAINER",
            "HEALTHCHECK",
            "SHELL",
            "STOPSIGNAL",
            "ONBUILD",
            "AS",
        ],
        "builtins": [],
    },
    "go": {
        "keywords": [
            "package",
            "import",
            "func",
            "return",
            "if",
            "else",
            "for",
            "range",
            "switch",
            "case",
            "default",
            "break",
            "continue",
            "fallthrough",
            "go",
            "select",
            "chan",
            "defer",
            "map",
            "struct",
            "interface",
            "type",
            "const",
            "var",
            "nil",
            "true",
            "false",
            "iota",
            "make",
            "new",
            "append",
            "copy",
            "delete",
            "len",
            "cap",
            "close",
            "panic",
            "recover",
        ],
        "builtins": [
            "fmt",
            "os",
            "io",
            "strings",
            "strconv",
            "time",
            "sync",
            "context",
            "errors",
            "log",
            "net",
            "http",
            "json",
            "encoding",
            "regexp",
            "sort",
            "math",
            "crypto",
        ],
    },
}


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] [{level}] {icon} {message}")


def extract_code_blocks(post_file: Path) -> List[CodeBlock]:
    """포스트 파일에서 코드 블록 추출"""
    code_blocks = []

    try:
        with open(post_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 코드 블록 패턴: ```language ... ```
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.finditer(pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            language = match.group(1) or "text"
            code = match.group(2).strip()

            # 코드가 너무 짧으면 스킵 (최소 2줄)
            if code.count("\n") < 1:
                continue

            # 시작 라인 계산
            line_start = content[: match.start()].count("\n") + 1
            line_end = line_start + code.count("\n")

            code_blocks.append(
                CodeBlock(
                    language=language,
                    code=code,
                    line_start=line_start,
                    line_end=line_end,
                    post_file=post_file.name,
                    index=i + 1,
                )
            )

    except Exception as e:
        log_message(f"코드 블록 추출 실패: {post_file.name} - {e}", "ERROR")

    return code_blocks


def generate_code_hash(code: str, language: str) -> str:
    """코드 내용 기반 해시 생성"""
    content = f"{language}:{code}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def simple_syntax_highlight(
    code: str, language: str, theme: Theme
) -> List[Tuple[str, str]]:
    """간단한 문법 하이라이팅 (토큰화)"""
    tokens = []

    lang_config = LANGUAGE_KEYWORDS.get(
        language.lower(), {"keywords": [], "builtins": []}
    )
    keywords = set(lang_config.get("keywords", []))
    builtins = set(lang_config.get("builtins", []))

    # 토큰 패턴
    patterns = [
        # 문자열 (큰따옴표)
        (r'"(?:[^"\\]|\\.)*"', "string"),
        # 문자열 (작은따옴표)
        (r"'(?:[^'\\]|\\.)*'", "string"),
        # 여러 줄 문자열 (Python)
        (r'"""(?:[^"\\]|\\.)*"""', "string"),
        (r"'''(?:[^'\\]|\\.)*'''", "string"),
        # 백틱 문자열 (JavaScript)
        (r"`(?:[^`\\]|\\.)*`", "string"),
        # 주석 (한 줄)
        (r"#.*$", "comment"),
        (r"//.*$", "comment"),
        # 주석 (여러 줄)
        (r"/\*[\s\S]*?\*/", "comment"),
        # 숫자
        (r"\b\d+\.?\d*\b", "number"),
        # 키워드/식별자
        (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "identifier"),
        # 기타
        (r"[^\s]", "text"),
    ]

    combined_pattern = "|".join(f"({p[0]})" for p in patterns)

    for match in re.finditer(combined_pattern, code, re.MULTILINE):
        matched_text = match.group(0)

        # 토큰 타입 결정
        if (
            matched_text.startswith('"')
            or matched_text.startswith("'")
            or matched_text.startswith("`")
            or matched_text.startswith('"""')
            or matched_text.startswith("'''")
        ):
            token_type = "string"
        elif (
            matched_text.startswith("#")
            or matched_text.startswith("//")
            or matched_text.startswith("/*")
        ):
            token_type = "comment"
        elif re.match(r"^\d", matched_text):
            token_type = "number"
        elif matched_text in keywords:
            token_type = "keyword"
        elif matched_text in builtins:
            token_type = "function"
        else:
            token_type = "text"

        color = getattr(theme, token_type, theme.text)
        tokens.append((matched_text, color))

    return tokens


def create_svg_code_image(
    code_block: CodeBlock,
    theme: Theme,
    output_path: Path,
    line_numbers: bool = True,
    title_bar: bool = True,
    max_lines: int = 30,
) -> bool:
    """SVG 코드 이미지 생성"""
    try:
        # 코드 라인 분리
        code_lines = code_block.code.split("\n")
        truncated = False

        if len(code_lines) > max_lines:
            code_lines = code_lines[:max_lines]
            truncated = True

        # SVG 크기 계산
        font_size = 14
        line_height = 22
        char_width = 8.4  # 모노스페이스 폰트 대략적인 너비

        padding = 20
        title_bar_height = 40 if title_bar else 0
        line_num_width = 50 if line_numbers else 0

        # 최대 라인 너비 계산
        max_line_width = max(len(line) for line in code_lines) if code_lines else 0
        content_width = max_line_width * char_width + line_num_width + padding * 2
        content_width = max(content_width, 400)  # 최소 너비
        content_width = min(content_width, 800)  # 최대 너비

        content_height = len(code_lines) * line_height + padding * 2
        total_height = content_height + title_bar_height

        # SVG 시작
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{content_width}" height="{total_height}" viewBox="0 0 {content_width} {total_height}">',
            # 스타일 정의
            f"<defs>",
            f'  <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">',
            f'    <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.2"/>',
            f"  </filter>",
            f"</defs>",
        ]

        # 메인 컨테이너 (그림자 포함)
        svg_parts.append(f'<g filter="url(#shadow)">')

        # 배경
        svg_parts.append(
            f'<rect x="0" y="0" width="{content_width}" height="{total_height}" fill="{theme.background}" rx="10" ry="10"/>'
        )

        # 타이틀 바
        if title_bar:
            svg_parts.append(
                f'<rect x="0" y="0" width="{content_width}" height="{title_bar_height}" fill="{theme.title_bar}" rx="10" ry="10"/>'
            )
            svg_parts.append(
                f'<rect x="0" y="{title_bar_height - 10}" width="{content_width}" height="10" fill="{theme.title_bar}"/>'
            )

            # macOS 스타일 버튼
            svg_parts.append(
                f'<circle cx="20" cy="{title_bar_height // 2}" r="6" fill="#ff5f56"/>'
            )
            svg_parts.append(
                f'<circle cx="40" cy="{title_bar_height // 2}" r="6" fill="#ffbd2e"/>'
            )
            svg_parts.append(
                f'<circle cx="60" cy="{title_bar_height // 2}" r="6" fill="#27c93f"/>'
            )

            # 언어 라벨
            svg_parts.append(
                f'<text x="{content_width - 15}" y="{title_bar_height // 2 + 5}" text-anchor="end" fill="{theme.line_number}" font-family="monospace" font-size="12">{code_block.language}</text>'
            )

        svg_parts.append(f"</g>")

        # 코드 영역
        code_start_y = title_bar_height + padding

        for i, line in enumerate(code_lines):
            y = code_start_y + i * line_height + font_size

            # 라인 넘버
            if line_numbers:
                line_num = i + 1
                svg_parts.append(
                    f'<text x="{padding}" y="{y}" fill="{theme.line_number}" font-family="monospace" font-size="{font_size}" text-anchor="start">{line_num}</text>'
                )

            # 코드 라인 (HTML 이스케이프)
            escaped_line = html.escape(line)
            x = padding + line_num_width
            svg_parts.append(
                f'<text x="{x}" y="{y}" fill="{theme.text}" font-family="monospace" font-size="{font_size}">{escaped_line}</text>'
            )

        # 잘린 표시
        if truncated:
            y = code_start_y + len(code_lines) * line_height + font_size
            svg_parts.append(
                f'<text x="{padding + line_num_width}" y="{y}" fill="{theme.comment}" font-family="monospace" font-size="{font_size}" font-style="italic">... (more lines)</text>'
            )

        # SVG 종료
        svg_parts.append("</svg>")

        # 파일 저장
        svg_content = "\n".join(svg_parts)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        log_message(f"SVG 생성 완료: {output_path.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"SVG 생성 실패: {e}", "ERROR")
        return False


def generate_image_filename(post_file: str, code_block: CodeBlock) -> str:
    """이미지 파일명 생성"""
    post_stem = Path(post_file).stem
    code_hash = generate_code_hash(code_block.code, code_block.language)

    # 파일명: post-stem_code_index_lang_hash
    filename = f"{post_stem}_code_{code_block.index}_{code_block.language}_{code_hash}"

    # 파일명 정리 (특수문자 제거)
    filename = re.sub(r"[^\w\-]", "_", filename)
    filename = re.sub(r"_+", "_", filename)

    return filename


def process_post(
    post_file: Path,
    theme: Theme,
    line_numbers: bool = True,
    title_bar: bool = True,
    max_lines: int = 30,
    force: bool = False,
    max_blocks: Optional[int] = None,
) -> Tuple[int, int]:
    """단일 포스트의 모든 코드 블록 처리"""
    log_message(f"포스트 처리 시작: {post_file.name}")

    code_blocks = extract_code_blocks(post_file)

    if not code_blocks:
        log_message(f"코드 블록 없음: {post_file.name}", "WARNING")
        return 0, 0

    if max_blocks:
        code_blocks = code_blocks[:max_blocks]

    success_count = 0
    total_count = len(code_blocks)

    for block in code_blocks:
        filename = generate_image_filename(post_file.name, block)
        output_path = IMAGES_DIR / f"{filename}.svg"

        # 이미 존재하고 force가 아니면 스킵
        if output_path.exists() and not force:
            log_message(f"이미 존재: {output_path.name}", "INFO")
            success_count += 1
            continue

        # SVG 생성
        if create_svg_code_image(
            block, theme, output_path, line_numbers, title_bar, max_lines
        ):
            success_count += 1

    log_message(
        f"포스트 완료: {post_file.name} ({success_count}/{total_count})", "SUCCESS"
    )
    return success_count, total_count


def list_available_themes():
    """사용 가능한 테마 목록"""
    print("\n사용 가능한 테마:")
    print("-" * 40)
    for name, theme in THEMES.items():
        print(f"  - {name}: {theme.name}")
        print(f"    배경: {theme.background}, 텍스트: {theme.text}")
    print()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="코드 블록을 고퀄리티 SVG 이미지로 변환",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 최근 3개 포스트의 코드 블록 이미지 생성
  python3 scripts/generate_code_images.py --recent 3
  
  # 특정 포스트 처리
  python3 scripts/generate_code_images.py _posts/2026-01-15-example.md
  
  # 모든 포스트 처리
  python3 scripts/generate_code_images.py --all
  
  # 드라큘라 테마 사용
  python3 scripts/generate_code_images.py --all --theme dracula
  
  # 테마 목록 보기
  python3 scripts/generate_code_images.py --list-themes
        """,
    )

    parser.add_argument("post_file", nargs="?", help="처리할 포스트 파일")
    parser.add_argument("--all", action="store_true", help="모든 포스트 처리")
    parser.add_argument("--recent", type=int, default=0, help="최근 N개 포스트만 처리")
    parser.add_argument("--force", action="store_true", help="기존 이미지 덮어쓰기")
    parser.add_argument(
        "--theme",
        default="monokai",
        choices=list(THEMES.keys()),
        help="코드 테마 (기본: monokai)",
    )
    parser.add_argument(
        "--no-line-numbers", action="store_true", help="라인 넘버 숨기기"
    )
    parser.add_argument("--no-title-bar", action="store_true", help="타이틀 바 숨기기")
    parser.add_argument("--max-blocks", type=int, help="포스트당 최대 코드 블록 수")
    parser.add_argument(
        "--max-lines", type=int, default=30, help="코드 최대 라인 수 (기본: 30)"
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="사용 가능한 테마 목록"
    )

    args = parser.parse_args()

    # 테마 목록 출력
    if args.list_themes:
        list_available_themes()
        return

    # 테마 가져오기
    theme = THEMES.get(args.theme, THEMES["monokai"])

    # 포스트 목록 생성
    posts = []

    if args.post_file:
        post_path = Path(args.post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_path

        if not post_path.exists():
            log_message(f"파일을 찾을 수 없습니다: {post_path}", "ERROR")
            sys.exit(1)

        posts = [post_path]
    elif args.all:
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    elif args.recent > 0:
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[: args.recent]
    else:
        parser.print_help()
        sys.exit(1)

    if not posts:
        log_message("처리할 포스트가 없습니다.", "ERROR")
        sys.exit(1)

    log_message(f"총 {len(posts)}개 포스트 처리 시작")
    log_message(f"테마: {theme.name}")
    print()

    # 통계
    total_success = 0
    total_blocks = 0

    for post in posts:
        success, total = process_post(
            post,
            theme=theme,
            line_numbers=not args.no_line_numbers,
            title_bar=not args.no_title_bar,
            max_lines=args.max_lines,
            force=args.force,
            max_blocks=args.max_blocks,
        )
        total_success += success
        total_blocks += total
        print()

    # 요약
    log_message("=" * 60)
    log_message(
        f"처리 완료: {total_success}/{total_blocks}개 코드 블록 이미지 생성", "SUCCESS"
    )
    log_message(f"출력 디렉토리: {IMAGES_DIR}", "INFO")
    log_message("=" * 60)


if __name__ == "__main__":
    main()

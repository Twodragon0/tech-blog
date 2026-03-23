#!/usr/bin/env python3
"""
SVG 품질 검사 스크립트

검사 항목:
1. title 요소 누락 (FAIL)
2. 한국어 텍스트 감지 - <text> 요소 내 가-힣 (FAIL)
3. width/height 속성 누락 (WARNING)
4. viewBox 유효성 - 없거나 형식 오류 (FAIL)
5. 금지 특수문자 - ·, •, —, ", ' (WARNING)
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

SVG_NS = "http://www.w3.org/2000/svg"

KOREAN_RE = re.compile(r"[\uAC00-\uD7A3]")
FORBIDDEN_CHARS_RE = re.compile(r"[·•—\u201C\u201D\u2018\u2019]")
VIEWBOX_RE = re.compile(r"^-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s+\d+(\.\d+)?\s+\d+(\.\d+)?$")


class Issue(NamedTuple):
    level: str  # FAIL | WARNING
    message: str


def check_svg_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [Issue("FAIL", f"XML parse error: {exc}")]

    root = tree.getroot()

    # Strip namespace for tag comparisons
    def local(tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    # 1. title 요소 누락
    has_title = any(local(child.tag) == "title" for child in root)
    if not has_title:
        issues.append(Issue("FAIL", "Missing <title> element"))

    # 3. width/height 속성 누락
    if "width" not in root.attrib or "height" not in root.attrib:
        missing = [a for a in ("width", "height") if a not in root.attrib]
        issues.append(Issue("WARNING", f"Missing attribute(s): {', '.join(missing)}"))

    # 4. viewBox 유효성
    viewbox = root.attrib.get("viewBox", "").strip()
    if not viewbox:
        issues.append(Issue("FAIL", "Missing viewBox attribute"))
    elif not VIEWBOX_RE.match(viewbox):
        issues.append(Issue("FAIL", f"Invalid viewBox format: '{viewbox}'"))

    # 2 & 5. text 요소 검사
    for elem in tree.iter():
        if local(elem.tag) != "text":
            continue
        # Collect all text content in this element
        parts = []
        if elem.text:
            parts.append(elem.text)
        for child in elem:
            if child.text:
                parts.append(child.text)
            if child.tail:
                parts.append(child.tail)
        if elem.tail:
            parts.append(elem.tail)
        text_content = "".join(parts)

        # 2. 한국어 감지
        if KOREAN_RE.search(text_content):
            snippet = text_content[:40].replace("\n", " ")
            issues.append(Issue("FAIL", f"Korean text in <text> element: '{snippet}'"))

        # 5. 금지 특수문자
        found = set(FORBIDDEN_CHARS_RE.findall(text_content))
        if found:
            chars = ", ".join(repr(c) for c in sorted(found))
            issues.append(Issue("WARNING", f"Forbidden special characters in <text>: {chars}"))

    return issues


def collect_svg_files(targets: list[str]) -> list[Path]:
    paths: list[Path] = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            paths.extend(sorted(p.glob("*.svg")))
        elif p.is_file():
            paths.append(p)
        else:
            # Treat as glob pattern; try cwd first, then project root
            cwd_matches = sorted(Path.cwd().glob(target))
            root_matches = sorted(PROJECT_ROOT.glob(target))
            expanded = cwd_matches or root_matches
            if expanded:
                paths.extend(expanded)
            else:
                # Last resort: Path.glob on the parent with the name portion
                parent = p.parent
                name = p.name
                base = parent if parent != Path(".") else Path.cwd()
                paths.extend(sorted(base.glob(name)))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SVG quality checker for tech-blog assets"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=[str(IMAGES_DIR)],
        help="SVG files or directories to check (default: assets/images/)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Exit with code 1 if any FAIL issues are found",
    )
    args = parser.parse_args()

    svg_files = collect_svg_files(args.targets)

    if not svg_files:
        print("No SVG files found.")
        return 0

    total_fail = 0
    total_warn = 0
    total_pass = 0

    for path in svg_files:
        issues = check_svg_file(path)
        fails = [i for i in issues if i.level == "FAIL"]
        warns = [i for i in issues if i.level == "WARNING"]

        if fails:
            status = "FAIL"
            total_fail += 1
        elif warns:
            status = "WARNING"
            total_warn += 1
        else:
            status = "PASS"
            total_pass += 1

        rel = path.relative_to(PROJECT_ROOT) if path.is_absolute() and path.is_relative_to(PROJECT_ROOT) else path
        print(f"[{status}] {rel}")
        for issue in issues:
            prefix = "  [FAIL]" if issue.level == "FAIL" else "  [WARN]"
            print(f"{prefix} {issue.message}")

    print()
    print(
        f"Summary: {total_pass} PASS, {total_warn} WARNING, {total_fail} FAIL"
        f" / {len(svg_files)} files checked"
    )

    if args.ci and total_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

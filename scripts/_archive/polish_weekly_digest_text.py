#!/usr/bin/env python3

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


REPLACEMENTS = {
    "이번 항목은 최신 기술 동향과 현업 적용 포인트를 간결히 정리한 내용입니다.": "이번 소식은 해당 기술 변화의 배경과 실제 적용 영향을 중심으로 정리했습니다.",
    "실무 적용 전 영향 범위, 운영 리스크, 검증 절차를 동시에 점검해야 합니다.": "실무 적용 전에 영향 범위와 운영 리스크를 평가하고 검증 기준을 확정해야 합니다.",
}


def clean_line(line: str) -> str:
    s = line
    for old, new in REPLACEMENTS.items():
        s = s.replace(old, new)

    if s.strip().startswith("```"):
        return s

    if "..." in s or "…" in s:
        s = s.replace("…", " ")
        s = s.replace("...", " ")

    s = re.sub(r"\[([^\]]*?)\s+\]\((https?://[^)]+)\)", r"[\1](\2)", s)
    s = re.sub(r"\[([^\]]*?)\s+\]\((/[^)]+)\)", r"[\1](\2)", s)

    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+\|", " |", s)
    return s.rstrip()


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    in_code = False
    updated_lines = []

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            updated_lines.append(line)
            continue
        if in_code:
            updated_lines.append(line)
            continue
        updated_lines.append(clean_line(line))

    updated = "\n".join(updated_lines)
    if original.endswith("\n"):
        updated += "\n"

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = sorted(POSTS_DIR.glob("*Weekly_Digest*.md"))
    for file_path in files:
        if process(file_path):
            changed += 1
    print(f"weekly_digest_polished={changed} total={len(files)}")


if __name__ == "__main__":
    main()

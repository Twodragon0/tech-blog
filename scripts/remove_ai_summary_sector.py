#!/usr/bin/env python3

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


def strip_ai_summary_include(text: str) -> str:
    updated = re.sub(
        r"\n?\{%\s*include\s+ai-summary-card\.html[\s\S]*?%\}\n?",
        "\n",
        text,
    )
    updated = re.sub(r"\n{3,}", "\n\n", updated)
    return updated


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    if not original.startswith("---\n"):
        return False
    parts = original.split("---", 2)
    if len(parts) < 3:
        return False

    fm = parts[1]
    body = parts[2]

    new_body = strip_ai_summary_include(body).lstrip("\n")
    new_text = f"---{fm}---\n\n{new_body}"
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = sorted(POSTS_DIR.glob("*.md"))
    for file_path in files:
        if process(file_path):
            changed += 1
    print(f"ai_summary_sector_removed={changed} total={len(files)}")


if __name__ == "__main__":
    main()

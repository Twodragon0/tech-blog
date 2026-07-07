#!/usr/bin/env python3

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


def _is_candidate(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith(("#", "|", "- ", "* ", ">", "```", "{%", "<!--")):
        return False
    if "![" in s and "](" in s:
        return False
    if s.startswith("[") and "](" in s:
        return False
    if "http://" in s or "https://" in s:
        return False
    if re.search(r"[가-힣]", s):
        return False
    if len(s) < 40:
        return False
    letters = sum(ch.isalpha() for ch in s)
    ascii_letters = sum(ch.isascii() and ch.isalpha() for ch in s)
    if letters == 0:
        return False
    return ascii_letters / max(letters, 1) > 0.8


def _translate(text: str, cache: dict[str, str]) -> str:
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if key in cache:
        return cache[key]

    prompt = (
        "다음 기술 뉴스 문단을 한국어로 자연스럽고 간결하게 번역해 주세요. "
        "핵심 정보가 분명하게 전달되도록 1-2문장으로 정리하고, "
        "회사명/제품명/기술명은 원문 표기를 유지하세요. "
        "불릿/번호/따옴표 없이 결과 문장만 출력하세요.\n\n"
        f"원문:\n{text}\n\n번역:"
    )

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=40,
            cwd=ROOT,
        )
    except subprocess.TimeoutExpired:
        cache[key] = text
        return text
    out = text
    if result.returncode == 0:
        cand = re.sub(r"\s+", " ", result.stdout.strip())
        if cand and re.search(r"[가-힣]", cand):
            out = cand
    cache[key] = out
    return out


def process_file(path: Path, cache: dict[str, str]) -> bool:
    original = path.read_text(encoding="utf-8")
    if not original.startswith("---\n"):
        return False
    parts = original.split("---", 2)
    if len(parts) < 3:
        return False

    fm, body = parts[1], parts[2]
    lines = body.splitlines()
    changed = False
    in_code = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue

        if _is_candidate(line):
            start = i
            block = [line.strip()]
            i += 1
            while i < len(lines) and _is_candidate(lines[i]):
                block.append(lines[i].strip())
                i += 1

            source = " ".join(block)
            translated = _translate(source, cache)
            if translated != source:
                lines[start:i] = [translated]
                delta = (i - start) - 1
                i = start + 1
                changed = True
                if delta > 0:
                    i -= delta
            continue

        i += 1

    if not changed:
        return False

    new_body = "\n".join(lines)
    new_content = (
        f"---{fm}---{new_body if new_body.startswith(chr(10)) else chr(10) + new_body}"
    )
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    cache: dict[str, str] = {}
    changed = 0
    files = sorted(POSTS_DIR.glob("*Weekly_Digest*.md"))
    for file_path in files:
        if process_file(file_path, cache):
            changed += 1
    print(f"weekly_digest_updated={changed} total={len(files)}")


if __name__ == "__main__":
    main()

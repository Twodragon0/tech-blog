"""Structural invariant guard for weekly-digest posts (Sub-project 0).

Verifies: single contiguous ## 1..N section numbering, no body H1, and a
single checklist surface (global 실무 체크리스트 only). Exit non-zero on any
violation. Run in pre-commit / CI over changed digest posts.
"""
import re
import sys


def _body(text: str) -> str:
    # drop YAML front matter
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[m.end():] if m else text


def check_post(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        body = _body(fh.read())
    lines = body.split("\n")
    violations = []

    # (b) no body H1
    in_code = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#\s+\S", ln):
            violations.append(f"body H1 heading found: {ln.strip()[:60]}")

    # (a) numbering: '## N.' headings must be 1,2,3,... contiguous (ignore '## 실무 체크리스트' etc.)
    nums = [int(m.group(1)) for ln in lines
            for m in [re.match(r"^##\s+(\d+)\.", ln)] if m]
    if nums and nums != list(range(1, len(nums) + 1)):
        violations.append(f"broken section numbering: {nums}")

    # (d) single checklist surface. The defect is a CHECKBOX per-item checklist
    # ('- [ ]') duplicating the global P0/P1/P2. Topic-specific prose advisory
    # ('- ' bullets under '#### 권장 조치') is legitimate content and is kept.
    if body.count("## 실무 체크리스트") != 1:
        violations.append(f"expected exactly one 실무 체크리스트, found {body.count('## 실무 체크리스트')}")
    # any checkbox item appearing BEFORE the global checklist lives in an item
    # body → it is a per-item checklist (the empirical defect).
    head = body.split("## 실무 체크리스트")[0]
    if re.search(r"^\s*-\s*\[[ xX]?\]", head, re.MULTILINE):
        violations.append("per-item checkbox checklist present in an item body (should be removed)")
    if "대응 체크리스트" in body:
        violations.append("per-item 대응 체크리스트 heading present (should be removed)")

    return violations


def main(argv: list) -> int:
    rc = 0
    for path in argv:
        vs = check_post(path)
        if vs:
            rc = 1
            print(f"FAIL {path}")
            for v in vs:
                print(f"  - {v}")
        else:
            print(f"OK   {path}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

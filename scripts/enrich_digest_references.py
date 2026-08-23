"""Give each digest's 참고 자료 table per-post context — without inventing facts.

Corpus audit 2026-08-06: 151 digests carry a byte-identical 3-row table
(CISA KEV / MITRE ATT&CK / FIRST EPSS) and 174 have no description column, so
the section says nothing about the post it sits in — while the post's own news
cards already name every source it actually cited.

This transformer uses only what the post already contains:

* adds a 용도 column with CANONICAL descriptions for the standard resources
  (4 corpus posts already show the 3-column precedent, header '용도'), and
* appends the sources the post genuinely cited, with the citation count taken
  from its own news cards and the link derived from the cited URL's origin.

No LLM, no fetching, no generated prose. A table containing a resource outside
``RESOURCE_PURPOSE`` keeps its 2-column shape rather than getting an invented
description — the source rows are still appended.

Usage:
    python3 scripts/enrich_digest_references.py --posts-glob '_posts/*Weekly_Digest*.md' --dry-run
    python3 scripts/enrich_digest_references.py _posts/2026-08-05-*.md
"""

import argparse
import glob
import re
import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent

REFERENCE_HEADING = "## 참고 자료"
PURPOSE_COLUMN = "용도"

# Canonical purposes. Deliberately deny-by-default: an unmapped resource never
# receives a made-up description.
RESOURCE_PURPOSE = {
    "CISA KEV": "실제 악용 확인된 취약점 목록 — 패치 우선순위 기준",
    "CISA KEV Catalog": "실제 악용 확인된 취약점 목록 — 패치 우선순위 기준",
    "CISA KEV (Known Exploited Vulnerabilities)": "실제 악용 확인된 취약점 목록 — 패치 우선순위 기준",
    "MITRE ATT&CK": "공격 전술·기법 매핑 — 탐지 룰 설계",
    "FIRST EPSS": "취약점 악용 확률 점수 — CVSS 보완",
    "OWASP Top 10 for LLM": "LLM 애플리케이션 상위 위험 — AI 서비스 위협 모델링",
    "OWASP LLM Top 10": "LLM 애플리케이션 상위 위험 — AI 서비스 위협 모델링",
    "NIST AI RMF": "AI 위험 관리 프레임워크 — 거버넌스 통제 설계",
}

_CARD_RE = re.compile(r"\{%\s*include\s+news-card\.html(.*?)%\}", re.DOTALL)
_ROW_RE = re.compile(r"^\|(.*)\|[ \t]*$")
_SEP_CELL_RE = re.compile(r"^[\s:-]+$")


def _attr(card_body: str, key: str):
    m = re.search(rf'\b{key}="(.*?)"(?=\s+\w+="|\s*$)', card_body, re.DOTALL)
    return m.group(1) if m else None


def origin_of(url: str) -> str:
    """Scheme + host of a cited article URL (the source's own site)."""
    parts = urlparse(url)
    return f"{parts.scheme}://{parts.netloc}" if parts.scheme and parts.netloc else ""


def cited_sources(text: str) -> "OrderedDict":
    """{source name: (origin url, citation count)} in first-appearance order."""
    found: OrderedDict = OrderedDict()
    for body in _CARD_RE.findall(text):
        name, url = _attr(body, "source"), _attr(body, "url")
        if not name or not url:
            continue
        origin = origin_of(url)
        if not origin:
            continue
        if name in found:
            prev_origin, count = found[name]
            found[name] = (prev_origin, count + 1)
        else:
            found[name] = (origin, 1)
    return found


def _cells(line: str):
    m = _ROW_RE.match(line)
    return [c.strip() for c in m.group(1).split("|")] if m else None


def _split_reference_section(text: str):
    """(before, section, after) around the 참고 자료 section, or None."""
    m = re.search(rf"^{re.escape(REFERENCE_HEADING)}[ \t]*$", text, re.MULTILINE)
    if not m:
        return None
    rest = text[m.end() :]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    end = m.end() + (nxt.start() if nxt else len(rest))
    return text[: m.start()], text[m.start() : end], text[end:]


def _rewrite_section(section: str, sources: "OrderedDict") -> str:
    lines = section.split("\n")
    header_idx = next(
        (
            i
            for i, ln in enumerate(lines)
            if _cells(ln) and not all(_SEP_CELL_RE.match(c) for c in _cells(ln))
        ),
        None,
    )
    if header_idx is None:
        return section
    header = _cells(lines[header_idx])
    if len(lines) <= header_idx + 1 or not _cells(lines[header_idx + 1]):
        return section
    if not all(_SEP_CELL_RE.match(c) for c in _cells(lines[header_idx + 1])):
        return section

    body_end = header_idx + 2
    while body_end < len(lines) and _cells(lines[body_end]):
        body_end += 1
    rows = [_cells(ln) for ln in lines[header_idx + 2 : body_end]]
    if not rows:
        return section

    has_purpose = len(header) >= 3
    upgrade = not has_purpose and all(r[0] in RESOURCE_PURPOSE for r in rows)

    existing_labels = {r[0] for r in rows}
    existing_links = {r[1] for r in rows if len(r) > 1}
    new_rows = []
    for name, (origin, count) in sources.items():
        # display label drops a leading www. (matches the corpus convention:
        # "thehackernews.com", "cisa.gov/…"); the href keeps the real host.
        host = urlparse(origin).netloc
        label = host[4:] if host.startswith("www.") else host
        link = f"[{label}]({origin})"
        if name in existing_labels or any(link in cell for cell in existing_links):
            continue
        new_rows.append([name, link, f"본문 {count}건 인용"])

    if not upgrade and not new_rows:
        return section

    width = 3 if (has_purpose or upgrade) else 2
    out_header = header[:width] if len(header) >= width else header + [PURPOSE_COLUMN]
    rendered = [
        "| " + " | ".join(out_header) + " |",
        "|" + "|".join(["-" * 8 if i == 0 else "-" * 6 for i in range(width)]) + "|",
    ]
    for r in rows:
        cells = list(r[:width])
        while len(cells) < width:
            cells.append(RESOURCE_PURPOSE.get(r[0], ""))
        rendered.append("| " + " | ".join(cells) + " |")
    for r in new_rows:
        rendered.append("| " + " | ".join(r[:width]) + " |")

    return "\n".join(lines[:header_idx] + rendered + lines[body_end:])


def transform(text: str) -> str:
    parts = _split_reference_section(text)
    if not parts:
        return text
    before, section, after = parts
    return before + _rewrite_section(section, cited_sources(text)) + after


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Add 용도 column + cited sources to 참고 자료."
    )
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    files = [f for f in files if _is_digest_post(f)]
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("[enrich-references] no digest post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            print(f"OK   {f}")
            continue
        # Everything before the section must be byte-identical.
        if new.split(REFERENCE_HEADING)[0] != original.split(REFERENCE_HEADING)[0]:
            print(f"ABORT {f}: content outside 참고 자료 changed", file=sys.stderr)
            return 1
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[enrich-references] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

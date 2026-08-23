#!/usr/bin/env python3
"""Lossless structural restore for legacy digest posts.

WHY THIS IS NOT backfill_digest_structure.py
--------------------------------------------
backfill_digest_structure.transform_body (the LLM publish path, PR #452) resolves
the per-item checklist defect by DELETING the checkbox block. Measured on the
corpus that path takes 601 violations to 21 — but 211 of them by removing
reader-visible content. Owner decision (2026-08-04) is lossless restore only, so
this module converts markers instead:

    R1  item-region '#'/'##'/'###' non-section heading  ->  '####'
    R2  '#{1,4} 대응 체크리스트'                        ->  '**대응 체크리스트**'
    R3  item-region '- [ ] x'                          ->  '- x'
    R4  remaining top-level '## N.' sections           ->  renumbered 1..N
    R5  '## N. 실무 체크리스트'                         ->  '## 실무 체크리스트'
    R6  global-checklist plain '- x'                   ->  '- [ ] x'

R0 (a precondition, not a rewrite): fenced code blocks are verbatim and do not
move any rule's state machine — see _fence_flags. Added after the tier-B/C
batches caught R1 rewriting '# 예시' comments to '#### 예시' inside bash / yaml /
python fences of 2026-03-11 and 2026-03-27.

APPLY ORDER: R5, R1, R2, R3, R6, R4. Constraints found empirically by the unit
tests and by CI (the first draft had the first two backwards and lacked R6):

  * R5 BEFORE R1 — TOP_SECTION_RE only recognizes the UNNUMBERED
    '## 실무 체크리스트', so while the legacy numbered form is still present R1
    treats it as item-body content and demotes it to '#### 9. 실무 체크리스트'.
    R5 can then no longer match it (it anchors on '^##'), and the post keeps the
    'found 0' defect. This is exactly the 6 tier-C files.
  * R5 BEFORE R4 — R5 takes the checklist OUT of the numbered sequence. Renumber
    first and the checklist consumes an index, so removing its number afterwards
    leaves a gap: '## 1. 보안' + '## 3. 실무 체크리스트' + '## 7. AI/ML' becomes
    [1, 3] (still broken) instead of [1, 2].

  * R6 AFTER R5 — R6 anchors on the canonical '## 실무 체크리스트' heading, which
    R5 is what produces for the numbered legacy form.

R1 vs R2 is order-INDEPENDENT: _RESP_HEADING_RE spans '#{1,4}', so it catches the
heading whether or not R1 has already demoted it to '####'. R3 vs R6 likewise:
their scopes are disjoint (item regions vs the global checklist section).

WHY R6 EXISTS: R3 strips the per-item checkboxes, and in the legacy corpus those
were the ONLY '- [ ]' in the file — so validate_post_quality.validate_checklists
(which scores the document-wide count) dropped 2026-03-22 from 91 to 83 and broke
the frozen quality baseline. Rather than regenerate the baseline to accept the
drop, R6 converges the legacy global checklist on the form the CURRENT generator
already emits ('- [ ]', verified on the 2026-08-01/08-04 digests).

backfill_digest_structure.py and scripts/news/** are NOT modified. See
docs/superpowers/specs/2026-08-04-digest-structure-backfill-design.md and
docs/superpowers/plans/2026-08-05-restore-digest-structure.md.

Usage:
    python3 scripts/restore_digest_structure.py --dry-run _posts/2026-03-22-*.md
    python3 scripts/restore_digest_structure.py _posts/2026-03-22-*.md
    python3 scripts/restore_digest_structure.py --dry-run \
        --posts-glob '_posts/2026-03-*Weekly_Digest*.md'
"""

import argparse
import collections
import glob
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.backfill_digest_structure import (  # noqa: E402
    _split_front_matter,
)

# Copied from backfill_digest_structure.transform_body, where they are
# function-local and cannot be imported. test_restore_digest_structure.py has a
# drift guard that fails if the two definitions diverge.
ITEM_HEADING_RE = re.compile(r"^### \d+\.\d+")
TOP_SECTION_RE = re.compile(
    r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드|"
    r"GeekNews|Open Source)|"
    r"## 실무 체크리스트|## 서론|## 분석가 시점|## 경영진 브리핑|"
    r"## 위험 스코어카드|## 참고 자료|## 📊)"
)

_ANY_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def _fence_flags(lines: list) -> list:
    """R0: True for every line the rules must leave verbatim.

    Mirrors check_digest_structure._strip_code_fences: state toggles on the
    STRIPPED line (2026-02-08 closes its blocks with '  ```'), and both the
    delimiters and the interior are excluded. Without this, R1 rewrote bash /
    yaml / python comments ('# 예시' -> '#### 예시') inside fenced examples of
    2026-03-11 and 2026-03-27 — content the gate never flagged, since it ignores
    fence interiors. Fenced lines also do not move the item-region state
    machine, for the same reason.
    """
    flags = []
    in_code = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            flags.append(True)
            continue
        flags.append(in_code)
    return flags


def demote_item_headings(text: str) -> str:
    """R1: inside an item region, demote a stray #/##/### heading to ####.

    An item region opens at '### N.M ...' and closes at the next whitelisted
    top-level section heading. Outside an item region every line is verbatim,
    which is what preserves section intros ('### 이번 주 하이라이트' etc).
    The item heading itself is the region delimiter, not part of the body.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    in_item = False
    for i, line in enumerate(lines):
        if fenced[i]:
            out.append(line)
            continue
        if ITEM_HEADING_RE.match(line):
            in_item = True
            out.append(line)
            continue
        if TOP_SECTION_RE.match(line):
            in_item = False
            out.append(line)
            continue
        m = _ANY_HEADING_RE.match(line)
        if in_item and m and len(m.group(1)) < 4:
            out.append(f"#### {m.group(2)}")
        else:
            out.append(line)
    return front + "\n".join(out)


_RESP_HEADING_RE = re.compile(r"^#{1,4}\s+(.*대응 체크리스트.*?)\s*$")


def boldify_response_checklist(text: str) -> str:
    r"""R2: a per-item '대응 체크리스트' HEADING becomes bold emphasis.

    The gate flags the heading form (``^#{2,4}\s+.*대응 체크리스트``), not the
    content. Converting to '**...**' keeps every word the reader sees while
    removing the heading that made it a second checklist surface.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    for i, line in enumerate(lines):
        m = None if fenced[i] else _RESP_HEADING_RE.match(line)
        out.append(f"**{m.group(1)}**" if m else line)
    return front + "\n".join(out)


_ITEM_CHECKBOX_RE = re.compile(r"^(\s*)-\s*\[[ xX]?\]\s*(.*)$")


def unbox_item_checkboxes(text: str) -> str:
    """R3: inside an item region, '- [ ] x' becomes a plain '- x' bullet.

    Scoped to item regions on purpose: the checkboxes under the global
    '## 실무 체크리스트' are the intended deliverable and must survive.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    in_item = False
    for i, line in enumerate(lines):
        if fenced[i]:
            out.append(line)
            continue
        if ITEM_HEADING_RE.match(line):
            in_item = True
            out.append(line)
            continue
        if TOP_SECTION_RE.match(line):
            in_item = False
            out.append(line)
            continue
        m = _ITEM_CHECKBOX_RE.match(line) if in_item else None
        out.append(f"{m.group(1)}- {m.group(2)}" if m else line)
    return front + "\n".join(out)


_NUMBERED_TOP_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$")


def renumber_sections(text: str) -> str:
    """R4: renumber top-level '## N. ...' sections to a contiguous 1..N.

    Only the number changes. Unnumbered sections ('## 실무 체크리스트') are not
    part of the sequence and pass through untouched. Runs LAST: R1 must already
    have demoted the item-body headings that the corpus' broken sequences were
    actually made of, and R5 must already have unnumbered the checklist so it
    does not consume an index.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    n = 0
    for i, line in enumerate(lines):
        m = None if fenced[i] else _NUMBERED_TOP_RE.match(line)
        if m:
            n += 1
            out.append(f"## {n}. {m.group(2)}")
        else:
            out.append(line)
    return front + "\n".join(out)


_CHECKLIST_HEADING_RE = re.compile(r"^##\s+실무 체크리스트\s*$")
_TOP_HEADING_RE = re.compile(r"^##\s+")
_PLAIN_BULLET_RE = re.compile(r"^-\s+(?!\[)(.*)$")


def checkbox_global_checklist(text: str) -> str:
    """R6: inside the global '## 실무 체크리스트', plain '- x' becomes '- [ ] x'.

    Not cosmetic — it resolves a genuine conflict between two gates:

      * check_digest_structure treats a per-item '- [ ]' as a defect (R3 removes
        the marker), and in the legacy corpus those per-item boxes were the ONLY
        checkboxes in the file.
      * validate_post_quality.validate_checklists scores the document-wide '- [ ]'
        count (>=5 -> full 10). So R3 alone dropped 2026-03-22 from 91 to 83 and
        broke the frozen quality baseline.

    The fix is to converge on the canonical form instead of accepting the drop:
    the current generator emits '- [ ]' under '## 실무 체크리스트' (verified on the
    2026-08-01 and 2026-08-04 digests); only the legacy posts use plain bullets
    there. Marker-only, so still lossless.

    Scoped to column-0 bullets in that one section — nested bullets and every
    other section are untouched. Runs after R5 so the heading is already canonical.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    in_checklist = False
    for i, line in enumerate(lines):
        if fenced[i]:
            out.append(line)
            continue
        if _CHECKLIST_HEADING_RE.match(line):
            in_checklist = True
            out.append(line)
            continue
        if in_checklist and _TOP_HEADING_RE.match(line):
            in_checklist = False
            out.append(line)
            continue
        m = _PLAIN_BULLET_RE.match(line) if in_checklist else None
        out.append(f"- [ ] {m.group(1)}" if m else line)
    return front + "\n".join(out)


_NUMBERED_CHECKLIST_RE = re.compile(r"^##\s+\d+\.\s*(실무 체크리스트)\s*$")


def canonicalize_checklist_heading(text: str) -> str:
    """R5: '## 9. 실무 체크리스트' -> '## 실무 체크리스트'.

    check_digest_structure.py counts the LITERAL '## 실무 체크리스트', so the
    numbered legacy form reads as 'found 0'. Converging the content on the
    canonical form fixes that without touching the gate. Runs FIRST — see the
    module docstring: the numbered form is invisible to TOP_SECTION_RE, so R1
    would otherwise demote it out of R5's reach, and leaving it numbered until
    after R4 makes it consume a section index.
    """
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    fenced = _fence_flags(lines)
    out = []
    for i, line in enumerate(lines):
        m = None if fenced[i] else _NUMBERED_CHECKLIST_RE.match(line)
        out.append(f"## {m.group(1)}" if m else line)
    return front + "\n".join(out)


# See the APPLY ORDER note in the module docstring — R5 must lead, R4 must trail.
_RULES = (
    canonicalize_checklist_heading,  # R5 — first: unblocks R1/R6 and frees R4's index
    demote_item_headings,  # R1
    boldify_response_checklist,  # R2 (order vs R1 is irrelevant)
    unbox_item_checkboxes,  # R3
    checkbox_global_checklist,  # R6 — after R5 (needs canonical heading)
    renumber_sections,  # R4 — last: counts only genuine sections
)


def transform(text: str) -> str:
    """Apply the rules in _RULES order. Deterministic and idempotent."""
    for rule in _RULES:
        text = rule(text)
    return text


_MARKER_RE = re.compile(
    r"(?:^[ \t]*#{1,6}[ \t]+)|(?:^[ \t]*-[ \t]*(?:\[[ xX]?\][ \t]*)?)|\*\*",
    re.MULTILINE,
)
_NUMERIC_RE = re.compile(r"^\d+\.?$")
_HEADING_LINE_RE = re.compile(r"^[ \t]*#{1,6}[ \t]+")


def _audit_fence_flags(lines: list) -> list:
    """Second opinion on R0's verbatim region, for the lossless audit ONLY.

    Deliberately a separate definition from `_fence_flags`, not a call to it: if
    the audit reused the rules' own detector, a regression in fence DETECTION
    would move both sides together and the invariant would stay blind by
    construction — exactly the blindness this audit exists to remove. Kept in
    lockstep by test_audit_fence_flags_agree_with_rule_flags over the corpus.
    """
    flags, in_code = [], False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            flags.append(True)
            continue
        flags.append(in_code)
    return flags


def lossless_tokens(text: str) -> collections.Counter:
    """Context-aware token multiset: what a transform must leave untouched.

    A flat "strip every marker, count the rest" multiset is marker-BLIND, and
    that blindness hid a real corruption: R1 rewrote '# 예시' to '#### 예시'
    inside fenced bash/yaml examples (2026-03-11, 2026-03-27). Only the marker
    changed, so the multiset matched and the invariant passed while the post was
    damaged — the defect had to be found by hand (PR #500). The global numeric
    exclusion had the same shape of hole: deleting a standalone number from a
    table cell was invisible.

    So markers and numbers are compared where they are ALLOWED to change, and
    verbatim where they are not:

    * front matter — no rule touches it: compared line-verbatim.
    * fenced lines (R0's verbatim region) — compared line-verbatim, markers
      included, so any marker mis-conversion inside a fence trips the abort.
    * outside fences — markers are erased (R1/R2/R3/R6 change them by design),
      and a numeric-only token is dropped ONLY when it is the leading 'N.' slot
      of a heading, which is the one number R4/R5 own. Numbers anywhere else
      (prose, tables, '### 9.1' item numbers) must survive.

    main() enforces equality per file before writing.
    """
    front, body = _split_front_matter(text)
    counter: collections.Counter = collections.Counter()

    for line in front.split("\n"):
        if line.strip():
            counter[f"\x00fm\x00{line}"] += 1

    lines = body.split("\n")
    fenced = _audit_fence_flags(lines)
    for i, line in enumerate(lines):
        if fenced[i]:
            if line.strip():
                counter[f"\x00fence\x00{line}"] += 1
            continue
        tokens = _MARKER_RE.sub(" ", line).split()
        if tokens and _HEADING_LINE_RE.match(line) and _NUMERIC_RE.match(tokens[0]):
            tokens = tokens[1:]
        counter.update(tokens)
    return counter


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Lossless digest structure restore.")
    ap.add_argument("paths", nargs="*", help="post paths")
    ap.add_argument("--posts-glob", help="glob instead of explicit paths")
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
        print("[restore-structure] no digest post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            print(f"OK   {f}")
            continue
        before, after = lossless_tokens(original), lossless_tokens(new)
        if before != after:
            print(
                f"ABORT {f}: lossless invariant violated "
                f"(lost={list((before - after).elements())[:5]} "
                f"added={list((after - before).elements())[:5]})",
                file=sys.stderr,
            )
            return 1
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[restore-structure] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

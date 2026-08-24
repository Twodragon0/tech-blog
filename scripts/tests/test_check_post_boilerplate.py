"""Tests for the post-body boilerplate gate.

The gate exists because ``autonomous_post_modernizer.py`` shipped the same
Mermaid diagram into 43 posts and the same four-item checklist into 55, and
every pre-existing gate passed it. These tests keep the gate non-vacuous: they
prove it fires on a duplicate and that the live corpus is clean.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts import check_post_boilerplate as gate

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = REPO_ROOT / "_posts"


def test_mermaid_bodies_extracts_and_normalises():
    text = "intro\n\n```mermaid\ngraph TD\n  A --> B\n```\n\ntail\n"
    assert gate.mermaid_bodies(text) == ["graph TD\n  A --> B"]


def test_checklist_signature_is_order_independent():
    a = "- [ ] beta\n- [ ] alpha\n"
    b = "- [ ] alpha\n- [ ] beta\n"
    assert gate.checklist_signature(a) == gate.checklist_signature(b)


def test_fenced_checkbox_is_not_counted():
    """A '- [ ]' inside a fence is sample text, not a checklist item."""
    fenced = "```markdown\n- [ ] example only\n```\n"
    assert gate.checklist_signature(fenced) == ()


def test_index_detects_a_duplicated_diagram(tmp_path):
    """Proof the gate is not vacuously green."""
    body = "```mermaid\nsequenceDiagram\n  A->>B: x\n```\n"
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text(f"# t\n\n{body}", encoding="utf-8")
    diagrams, _ = gate.build_index(sorted(tmp_path.glob("*.md")))
    assert any(len(owners) == 2 for owners in diagrams.values())


def test_index_detects_a_duplicated_checklist(tmp_path):
    items = "- [ ] 항목 하나\n- [ ] 항목 둘\n"
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text(f"# t\n\n{items}", encoding="utf-8")
    _, checklists = gate.build_index(sorted(tmp_path.glob("*.md")))
    assert any(len(owners) == 2 for owners in checklists.values())


def test_distinct_blocks_are_not_flagged(tmp_path):
    (tmp_path / "a.md").write_text("- [ ] 고유 항목 A\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("- [ ] 고유 항목 B\n", encoding="utf-8")
    _, checklists = gate.build_index(sorted(tmp_path.glob("*.md")))
    assert all(len(owners) == 1 for owners in checklists.values())


def test_live_corpus_has_no_duplicate_diagram_or_checklist():
    diagrams, checklists = gate.build_index(sorted(POSTS_DIR.glob("*.md")))
    dup_diagrams = {
        body.splitlines()[0]: sorted(owners)
        for body, owners in diagrams.items()
        if len(owners) > 1
    }
    dup_checklists = {
        sig[0]: sorted(owners) for sig, owners in checklists.items() if len(owners) > 1
    }
    assert dup_diagrams == {}, dup_diagrams
    assert dup_checklists == {}, dup_checklists


def test_the_removed_modernizer_boilerplate_is_gone_from_the_corpus():
    """The exact headings the modernizer injected must not reappear."""
    headings = (
        "### 아키텍처 및 워크플로우 다이어그램",
        "## 실무 적용 및 운영 체크리스트 (Actionable Checklist)",
        "### 핵심 구성 및 보안 통제 항목 비교",
    )
    offenders = {}
    for path in sorted(POSTS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        hit = [h for h in headings if h in text]
        if hit:
            offenders[path.name] = hit
    assert offenders == {}, offenders


def test_per_line_duplication_is_deliberately_not_gated():
    """Documents why the gate compares whole blocks, not individual lines.

    Many posts legitimately share a single checklist line via the digest
    generator's canonical checklist, so a per-line rule would be all false
    positives. If this ever drops to 1, the per-line rule became viable and
    the gate's scope should be revisited.
    """
    counts: dict[str, int] = {}
    for path in sorted(POSTS_DIR.glob("*.md")):
        clean = gate.strip_code_fences(path.read_text(encoding="utf-8", errors="ignore"))
        for line in set(re.findall(r"^\s*- \[ \] (.+)$", clean, re.MULTILINE)):
            counts[line.strip()] = counts.get(line.strip(), 0) + 1
    assert counts, "corpus has no checklist items — helper probably broke"
    assert max(counts.values()) > 1

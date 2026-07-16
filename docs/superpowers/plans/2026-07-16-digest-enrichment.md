# Digest Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix weekly-security-digest post structure deterministically (Sub-project 0), then add source-grounded per-item detail (A) and body-level sequence diagrams (B), and backfill the 5 most recent digests as a pilot.

**Architecture:** All generation lives in `scripts/news/content_generator.py` (body assembly `generate_post_content`, per-item `generate_news_section`) and `scripts/news/enhancer.py` (LLM enhancement). Sub-project 0 is pure post-processing of the LLM/template output — no fetch, no new LLM calls, no hallucination risk. Sub-projects A/B add new small modules under `scripts/news/` and hook into the same splice point. Every failure mode degrades to current behavior, never to fabricated content.

**Tech Stack:** Python 3, pytest, Gemini CLI (`_gemini_call`), `requests` (lazy import), Jekyll/Liquid, mermaid.

## Global Constraints

- Honesty: no claim without source evidence. Unsupported expansion → fall back to safe short summary. (from spec Hard constraints)
- Diagrams in post **body** only, never in the summary card (`ai-summary-card`). (from spec + `remove_mermaid_from_summary.py`)
- Mermaid must be **Safari-safe** (no bare `-`, `&`, paren issues) and pass `scripts/validate_mermaid_syntax.py`. (from spec)
- Mermaid must render under enforcing CSP (no eval) — covered by existing PR #449 `mermaid-csp-render` guard. (from spec)
- Cost order: Gemini CLI (free) → local template → paid API last. Expansion uses `_gemini_call` first. (CLAUDE.md §Cost Optimization)
- Fetch is read-only GET of **public** news article URLs only; never upload user content externally. (org policy)
- Backfill scope = **only the 5 most recent digests** (`2026-07-11` … `2026-07-15`). Wider rollout is a separate future spec. (spec Non-goals)
- No FAQ sections, no `schema_type: FAQPage`. (CLAUDE.md §Content Structure)
- Commit messages: conventional commits, Korean or English, **no `Co-Authored-By: Claude`**. (CLAUDE.md §Commit Rules)

## Pilot digest set (the only files backfilled this iteration)

- `_posts/2026-07-11-Tech_Security_Weekly_Digest_Security_Threat_AWS_Patch.md`
- `_posts/2026-07-12-Tech_Security_Weekly_Digest_Rust_AI_Agent.md`
- `_posts/2026-07-13-Tech_Security_Weekly_Digest_AI_GPT_Malware.md`
- `_posts/2026-07-14-Tech_Security_Weekly_Digest_AI_Security_Malware_Go.md`
- `_posts/2026-07-15-Tech_Security_Weekly_Digest_Zero-Day_Patch_AWS_Security.md`

## File structure

| File | Responsibility | Created/Modified |
|------|---------------|------------------|
| `scripts/news/content_generator.py` | Body assembly, per-item splice, checklist, title | Modify |
| `scripts/news/source_fetcher.py` | Read-only cached article fetch (Sub-project A) | Create |
| `scripts/news/summary_expander.py` | Gemini-first source-grounded expansion + honesty gate (A) | Create |
| `scripts/news/flow_detector.py` | Decide if an item has a real sequence-able flow (B) | Create |
| `scripts/news/sequence_diagram.py` | Build one Safari-safe body `sequenceDiagram` (B) | Create |
| `scripts/tests/test_digest_structure.py` | Sub-project 0 unit tests | Create |
| `scripts/tests/test_source_fetcher.py` | A unit tests | Create |
| `scripts/tests/test_summary_expander.py` | A unit tests | Create |
| `scripts/tests/test_flow_detector.py` | B unit tests | Create |
| `scripts/tests/test_sequence_diagram.py` | B unit tests | Create |

---

## SUB-PROJECT 0 — Structural normalization & de-duplication (SHIP FIRST)

Deterministic. Fixes the user's cited complaints (numbering collision, body H1, inconsistent deep analysis, duplicate checklist, title mismatch). No LLM, no fetch.

### Task 1: `_normalize_deep_analysis` — demote LLM headings, kill body H1/H2 collisions

**Files:**
- Modify: `scripts/news/content_generator.py` (add function near `generate_news_section`, ~line 2755; call it at line 2823)
- Test: `scripts/tests/test_digest_structure.py` (create)

**Interfaces:**
- Produces: `_normalize_deep_analysis(text: str) -> str` — takes raw LLM markdown, returns markdown where every heading line (`#`..`###`) is demoted to `####` with any leading `N. ` / `N) ` numbering prefix stripped. Non-heading lines unchanged.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_digest_structure.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
from content_generator import _normalize_deep_analysis


def test_strips_body_h1():
    out = _normalize_deep_analysis("# DevSecOps 관점 분석\n본문\n")
    assert "\n# " not in ("\n" + out)
    assert not out.startswith("# ")
    assert "#### DevSecOps 관점 분석" in out


def test_demotes_colliding_h2_and_strips_number_prefix():
    src = "## 1. 기술적 배경\nA\n## 2. 실무 영향\nB\n## 3. 대응 체크리스트\nC\n"
    out = _normalize_deep_analysis(src)
    assert "## 1. " not in out and "## 2. " not in out and "## 3. " not in out
    assert "#### 기술적 배경" in out
    assert "#### 실무 영향" in out


def test_demotes_h3_to_h4():
    out = _normalize_deep_analysis("### 제목\n내용\n")
    assert "#### 제목" in out
    assert "### 제목" not in out


def test_non_heading_lines_unchanged():
    src = "일반 문단\n- [ ] 체크박스\n> 인용\n"
    assert _normalize_deep_analysis(src) == src


def test_hash_in_prose_not_treated_as_heading():
    # a line that only starts with '#' at column 0 followed by space is a heading
    src = "C# 언어에 대한 설명\n"
    assert _normalize_deep_analysis(src) == src
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name '_normalize_deep_analysis'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/news/content_generator.py` (immediately above `def generate_news_section`):

`re` is already imported at module level (content_generator.py:7) — use it directly.

```python
def _normalize_deep_analysis(text: str) -> str:
    """Demote LLM-emitted headings so per-item deep analysis never collides
    with the post's section numbering.

    The enhancer prompt (enhancer.py) asks the model for '### 제목' + a
    numbered list, but real output drifts to a body '# H1' and '## 1./2./3.'
    that reset the top-level '## 1..N' section counter. This rewrites every
    ATX heading line to a single consistent '#### ' level and strips any
    leading 'N. ' / 'N) ' ordinal prefix. Non-heading lines are untouched.
    """
    if not text:
        return text
    out_lines = []
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            out_lines.append(line)
            continue
        heading_text = m.group(2)
        # strip a leading ordinal like "1. ", "2) ", "3 - "
        heading_text = re.sub(r"^\d+\s*[.)\-]\s*", "", heading_text)
        out_lines.append(f"#### {heading_text}".rstrip())
    return "\n".join(out_lines)
```

- [ ] **Step 4: Wire it into the splice point**

Change `scripts/news/content_generator.py:2823` from:

```python
        if enhanced:
            section += enhanced + "\n\n"
```

to:

```python
        if enhanced:
            section += _normalize_deep_analysis(enhanced) + "\n\n"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: PASS (5 passed)

- [ ] **Step 6: Commit**

```bash
git add scripts/news/content_generator.py scripts/tests/test_digest_structure.py
git commit -m "fix(digest): normalize deep-analysis headings to #### (kill body H1 / ## 1.2.3 collision)"
```

### Task 2: Severity-based deep-analysis gate (replace positional `i <= 5`)

**Files:**
- Modify: `scripts/news/content_generator.py:1614-1618` (security section loop)
- Test: `scripts/tests/test_digest_structure.py` (extend)

**Interfaces:**
- Consumes: `_determine_severity(item) -> str` returning one of `"Critical"|"High"|"Medium"|"Low"` (content_generator.py:2134).
- Produces: `_is_deep_analysis_item(item: Dict) -> bool` — True when severity is Critical/High OR the item carries a CVE. Applied uniformly; no positional cutoff.

Rationale (spec Sub-project 0 #2): deep 기술 배경/실무 영향 blocks apply to **high-severity** items only, uniformly — not "section-1 top-5 only". Deep security analysis stays gated to `category in ("security","devsecops")` (the enhancer + templates are threat-focused); richer treatment of non-security items is delivered by Sub-project A, not by forcing the security template (spec Non-goals: no fabricated flow/analysis).

- [ ] **Step 1: Write the failing test**

```python
# append to scripts/tests/test_digest_structure.py
from content_generator import _is_deep_analysis_item


def test_deep_gate_true_for_critical():
    assert _is_deep_analysis_item(
        {"title": "actively exploited zero-day", "category": "security",
         "summary": "critical RCE under active attack"}
    ) is True


def test_deep_gate_true_when_cve_present():
    assert _is_deep_analysis_item(
        {"title": "patch CVE-2026-12345", "category": "security", "summary": "advisory"}
    ) is True


def test_deep_gate_false_for_low_severity_no_cve():
    assert _is_deep_analysis_item(
        {"title": "vendor renames product", "category": "security", "summary": "minor news"}
    ) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -k deep_gate -q`
Expected: FAIL — `ImportError: cannot import name '_is_deep_analysis_item'`

- [ ] **Step 3: Write minimal implementation**

Add near `_determine_severity` in `scripts/news/content_generator.py`:

```python
def _is_deep_analysis_item(item: Dict) -> bool:
    """Gate for per-item deep analysis: high-severity or CVE-bearing items only.

    Replaces the old positional `i <= 5` rule so the deep 기술 배경/실무 영향
    blocks appear consistently based on risk, not list position.
    """
    if _extract_cve_ids(item):
        return True
    return _determine_severity(item) in ("Critical", "High")
```

- [ ] **Step 4: Use the gate in the security section loop**

Change `scripts/news/content_generator.py:1614-1618` from:

```python
        for i, item in enumerate(regular_security, 1):
            is_critical = i <= 5  # 상위 5개 뉴스에 AI 강화 적용
            news_sections += generate_news_section(
                item, f"{section_num}.{i}", is_critical=is_critical
            )
```

to:

```python
        for i, item in enumerate(regular_security, 1):
            is_critical = _is_deep_analysis_item(item)  # 심각도 기반(위치 무관)
            news_sections += generate_news_section(
                item, f"{section_num}.{i}", is_critical=is_critical
            )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add scripts/news/content_generator.py scripts/tests/test_digest_structure.py
git commit -m "fix(digest): gate per-item deep analysis on severity/CVE, not list position"
```

### Task 3: Single checklist surface — strip per-item checklists

**Files:**
- Modify: `scripts/news/content_generator.py` — (a) extend `_normalize_deep_analysis` to drop the LLM `대응 체크리스트`/`체크리스트` sub-block; (b) remove the template `#### 권장 조치` block at lines 2974-2982.
- Test: `scripts/tests/test_digest_structure.py` (extend)

**Interfaces:**
- Consumes: `_normalize_deep_analysis` from Task 1.
- Decision (spec #4, verification (d) "single checklist surface"): the ONLY checklist in a digest is the global `## 실무 체크리스트` P0/P1/P2 (`_generate_news_specific_checklist`). Both per-item checklist forms are removed: the LLM-emitted `대응 체크리스트` (inside `enhanced`) and the deterministic template `#### 권장 조치`.

- [ ] **Step 1: Write the failing test**

```python
# append to scripts/tests/test_digest_structure.py
def test_normalize_drops_per_item_checklist_block():
    src = (
        "#### 기술적 배경\n설명\n\n"
        "#### 대응 체크리스트\n- [ ] 패치\n- [ ] 모니터링\n\n"
        "#### 실무 영향\n영향\n"
    )
    out = _normalize_deep_analysis(src)
    assert "대응 체크리스트" not in out
    assert "- [ ] 패치" not in out
    assert "#### 기술적 배경" in out  # non-checklist content kept
    assert "#### 실무 영향" in out


def test_security_template_has_no_recommended_actions_checklist():
    from content_generator import _generate_security_analysis_template
    tmpl = _generate_security_analysis_template(
        {"title": "CVE-2026-1 RCE", "category": "security", "summary": "x", "content": "y"}
    )
    assert "권장 조치" not in tmpl
    assert "- [ ]" not in tmpl
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -k "checklist or recommended" -q`
Expected: FAIL

- [ ] **Step 3: Extend `_normalize_deep_analysis` to drop the checklist sub-block**

Replace the loop body in `_normalize_deep_analysis` so that when a heading whose text contains `체크리스트` or `권장 조치` is seen, that heading and all following lines up to (but not including) the next heading or a `---` rule are skipped:

```python
def _normalize_deep_analysis(text: str) -> str:
    """(docstring unchanged from Task 1) ...also drops any per-item checklist
    sub-block so the global 실무 체크리스트 is the single checklist surface."""
    if not text:
        return text
    _CHECKLIST_MARKERS = ("체크리스트", "권장 조치")
    out_lines = []
    skipping = False
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            heading_text = re.sub(r"^\d+\s*[.)\-]\s*", "", m.group(2))
            if any(mark in heading_text for mark in _CHECKLIST_MARKERS):
                skipping = True
                continue
            skipping = False
            out_lines.append(f"#### {heading_text}".rstrip())
            continue
        if skipping:
            # a horizontal rule ends the skipped region
            if line.strip() == "---":
                skipping = False
                out_lines.append(line)
            continue
        out_lines.append(line)
    return "\n".join(out_lines)
```

- [ ] **Step 4: Remove the template `#### 권장 조치` block**

Delete lines 2974-2982 of `scripts/news/content_generator.py` (the `template += """#### 권장 조치 ... """` block), so `_generate_security_analysis_template` ends after the MITRE mapping and `return template`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add scripts/news/content_generator.py scripts/tests/test_digest_structure.py
git commit -m "fix(digest): single checklist surface — drop per-item 대응 체크리스트 / 권장 조치"
```

### Task 4: Title-keyword accuracy — assert title labels come from actual items

**Files:**
- Modify: `scripts/news/content_generator.py` — add `_title_keywords_from_items` helper; the existing `_extract_digest_title_labels` (line 437) already scans items, so this task adds a **guard** rather than a rewrite.
- Test: `scripts/tests/test_digest_structure.py` (extend)

**Interfaces:**
- Produces: `_title_keywords_from_items(news_items: List[Dict]) -> set[str]` — the normalized label set derivable from the selected items (reuses `_extract_digest_title_labels`). Used by the Task 5 guard to assert title keywords ⊆ item keywords.

- [ ] **Step 1: Write the failing test**

```python
# append to scripts/tests/test_digest_structure.py
from content_generator import _title_keywords_from_items


def test_title_keywords_subset_of_items():
    items = [
        {"title": "actively exploited zero-day patched", "summary": "", "category": "security"},
        {"title": "AWS security update", "summary": "", "category": "cloud"},
    ]
    kws = _title_keywords_from_items(items)
    assert isinstance(kws, set)
    # a keyword the items never mention must not appear
    assert "랜섬웨어" not in kws
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -k title_keywords -q`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Write minimal implementation**

Add near `_extract_digest_title_labels` in `scripts/news/content_generator.py`:

```python
def _title_keywords_from_items(news_items: List[Dict]) -> set:
    """The keyword set legitimately derivable from the selected items.

    Wraps _extract_digest_title_labels so a structural guard can assert that
    the title's keywords are a subset of what the items actually justify.
    """
    return set(_extract_digest_title_labels(news_items, mode="security"))
```

(If `_extract_digest_title_labels` has a different signature, match it — inspect line 437. It returns a list of labels; wrap in `set(...)`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/news/content_generator.py scripts/tests/test_digest_structure.py
git commit -m "feat(digest): expose title-keyword set for structural guard"
```

### Task 5: `check_digest_structure.py` — structural invariant guard

**Files:**
- Create: `scripts/check_digest_structure.py`
- Test: `scripts/tests/test_check_digest_structure.py` (create)

**Interfaces:**
- Produces: `check_post(path: str) -> list[str]` — returns a list of violation strings (empty = clean). CLI: `python3 scripts/check_digest_structure.py <files...>` exits non-zero if any violation.
- Checks the spec's Sub-project 0 verification set on a rendered post body:
  - (a) top-level `## N.` headings form exactly one contiguous `1..N` sequence
  - (b) no `# ` H1 inside the body (below front matter)
  - (d) exactly one `## 실무 체크리스트`, and no per-item `대응 체크리스트`/`#### 권장 조치`

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_check_digest_structure.py
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_digest_structure import check_post

_GOOD = """---
title: x
---
## 1. 보안 뉴스
### 1.1 항목
#### 기술적 배경
## 2. AI/ML 뉴스
## 실무 체크리스트
### P0 (즉시)
"""

_BAD_H1 = _GOOD.replace("#### 기술적 배경", "# DevSecOps 관점 분석")
_BAD_NUM = _GOOD.replace("## 2. AI/ML 뉴스", "## 1. 기술적 배경")
_BAD_DUP_CL = _GOOD + "\n#### 대응 체크리스트\n- [ ] x\n"


def _write(txt):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(txt); f.close(); return f.name


def test_clean_post_has_no_violations():
    assert check_post(_write(_GOOD)) == []


def test_flags_body_h1():
    assert any("H1" in v for v in check_post(_write(_BAD_H1)))


def test_flags_numbering_collision():
    assert any("numbering" in v.lower() for v in check_post(_write(_BAD_NUM)))


def test_flags_per_item_checklist():
    assert any("체크리스트" in v for v in check_post(_write(_BAD_DUP_CL)))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_check_digest_structure.py -q`
Expected: FAIL — `ModuleNotFoundError: check_digest_structure`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/check_digest_structure.py
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

    # (d) single checklist surface
    if body.count("## 실무 체크리스트") != 1:
        violations.append(f"expected exactly one 실무 체크리스트, found {body.count('## 실무 체크리스트')}")
    if "대응 체크리스트" in body:
        violations.append("per-item 대응 체크리스트 present (should be removed)")
    if re.search(r"^####\s+권장 조치", body, re.MULTILINE):
        violations.append("per-item 권장 조치 checklist present (should be removed)")

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_check_digest_structure.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/check_digest_structure.py scripts/tests/test_check_digest_structure.py
git commit -m "feat(digest): structural invariant guard (numbering, body H1, single checklist)"
```

### Task 6: `backfill_digest_structure.py` — apply Sub-project 0 to the 5 pilot posts in place

**Why in-place post-processing, not full regeneration:** Sub-project 0 is pure markdown transformation. Re-running `auto_publish_news.py --date 2026-07-11` fetches *current* news (see `--hours`), so it cannot reproduce a 5-day-old post's item set. The correct, deterministic, honest backfill reads each **existing** post body and applies the same `_normalize_deep_analysis` + per-item-checklist-strip transforms, preserving the actually-published content. This mirrors the established `scripts/backfill_digest_commentary.py` pattern (in-place, idempotent, `--dry-run`/`--posts-glob`). The generator fix (Tasks 1-3) covers all *future* posts.

**Files:**
- Create: `scripts/backfill_digest_structure.py`
- Test: `scripts/tests/test_backfill_digest_structure.py`
- Modify: the 5 pilot `_posts/*.md` (transformed bodies)

**Interfaces:**
- Consumes: `_normalize_deep_analysis` (Task 1) — imported from `scripts.news.content_generator`.
- Produces: `transform_body(body: str) -> str` (applies heading normalization + checklist strip to a full post body) and a CLI `--posts-glob`, `--dry-run`, `--limit`, idempotent.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_backfill_digest_structure.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backfill_digest_structure import transform_body

_POST = """---
title: x
---
## 1. 보안 뉴스
### 1.1 항목
# DevSecOps 관점 분석
## 1. 기술적 배경
내용
## 3. 대응 체크리스트
- [ ] 패치
## 2. AI/ML 뉴스
## 실무 체크리스트
### P0 (즉시)
"""


def test_transform_removes_body_h1_and_collision():
    out = transform_body(_POST)
    assert "\n# DevSecOps" not in out
    assert "## 1. 기술적 배경" not in out
    assert "#### 기술적 배경" in out


def test_transform_removes_per_item_checklist():
    out = transform_body(_POST)
    assert "대응 체크리스트" not in out
    assert "- [ ] 패치" not in out
    assert "## 실무 체크리스트" in out  # global one preserved


def test_transform_is_idempotent():
    once = transform_body(_POST)
    assert transform_body(once) == once


def test_frontmatter_preserved():
    assert transform_body(_POST).startswith("---\ntitle: x\n---\n")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_backfill_digest_structure.py -q`
Expected: FAIL — `ModuleNotFoundError: backfill_digest_structure`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/backfill_digest_structure.py
"""Backfill Sub-project 0 structural normalization into existing digest posts.

Deterministic, in-place, idempotent. Applies the same heading normalization
and per-item-checklist removal the generator now does at build time
(_normalize_deep_analysis), so already-published posts get the fixed
structure without re-fetching news. Mirrors backfill_digest_commentary.py.

Usage:
    python3 scripts/backfill_digest_structure.py --dry-run \
        --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
    python3 scripts/backfill_digest_structure.py \
        --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
"""
import argparse
import glob
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/news")
from content_generator import _normalize_deep_analysis  # noqa: E402


def _split_front_matter(text: str):
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    return (m.group(1), m.group(2)) if m else ("", text)


def transform_body(text: str) -> str:
    """Apply heading normalization + per-item checklist strip to a full post.

    Only the item deep-analysis regions are affected: _normalize_deep_analysis
    demotes stray #/##/### headings to #### and drops 대응 체크리스트/권장 조치
    sub-blocks. Top-level '## N.' section headings and the global
    '## 실무 체크리스트' use '## ' with no ordinal-collision, and are only
    touched if they were themselves malformed. Idempotent.
    """
    front, body = _split_front_matter(text)
    # Protect the true top-level section + global-checklist headings, normalize the rest.
    protected = re.compile(
        r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드)|## 실무 체크리스트|## 서론|"
        r"## 분석가 시점|## 경영진 브리핑|## 위험 스코어카드|## 참고 자료|### P[012] |#### 요약|"
        r"### \d+\.\d+|## 📊)"
    )
    out = []
    buf = []

    def flush():
        if buf:
            out.append(_normalize_deep_analysis("\n".join(buf)))
            buf.clear()

    for line in body.split("\n"):
        if protected.match(line):
            flush()
            out.append(line)
        else:
            buf.append(line)
    flush()
    return front + "\n".join(out)


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts-glob", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)
    files = sorted(glob.glob(args.posts_glob))
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("no files matched", file=sys.stderr)
        return 1
    changed = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        new = transform_body(original)
        if new != original:
            changed += 1
            if args.dry_run:
                print(f"WOULD CHANGE {path}")
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"CHANGED {path}")
        else:
            print(f"unchanged {path}")
    print(f"{changed}/{len(files)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_backfill_digest_structure.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Dry-run then apply to the 5 pilot posts**

Run:
```bash
python3 scripts/backfill_digest_structure.py --dry-run \
  --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
python3 scripts/backfill_digest_structure.py \
  --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
```
Expected: dry-run lists the changes; apply reports `CHANGED` for the posts with the defects. Do NOT touch cover SVGs (`cover-system` skill).

- [ ] **Step 6: Run the structural guard on all 5**

Run:
```bash
python3 scripts/check_digest_structure.py \
  _posts/2026-07-11-*.md _posts/2026-07-12-*.md _posts/2026-07-13-*.md \
  _posts/2026-07-14-*.md _posts/2026-07-15-*.md
```
Expected: `OK` for all 5, exit 0.

- [ ] **Step 7: Confirm the live defects are gone**

Run: `grep -nE '^# [A-Za-z]|^## [123]\. (기술|실무|대응)' _posts/2026-07-15-*.md`
Expected: no output (no body H1, no colliding `## 1./2./3.` analysis headings).

- [ ] **Step 8: Full test + lint pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py scripts/tests/test_check_digest_structure.py scripts/tests/test_backfill_digest_structure.py -q && ruff check scripts/check_digest_structure.py scripts/backfill_digest_structure.py scripts/news/content_generator.py`
Expected: PASS, no lint errors.

- [ ] **Step 9: Commit**

```bash
git add scripts/backfill_digest_structure.py scripts/tests/test_backfill_digest_structure.py _posts/2026-07-11-*.md _posts/2026-07-12-*.md _posts/2026-07-13-*.md _posts/2026-07-14-*.md _posts/2026-07-15-*.md
git commit -m "fix(digest): backfill 5 pilot digests with normalized structure (Sub-project 0)"
```

**STOP HERE for review.** Sub-project 0 ships independently. Review the 5 backfilled posts before starting Sub-project A.

---

## SUB-PROJECT A — Source-grounded summary detail (SECOND, after 0 reviewed)

Fetch the real article, expand the per-item analysis with Gemini-first (evidence-based, no fabrication), honesty-gate it, fall back to the current short summary on any failure.

### Task 7: `source_fetcher` — read-only cached article fetch (fail-closed)

**Files:**
- Create: `scripts/news/source_fetcher.py`
- Test: `scripts/tests/test_source_fetcher.py`

**Interfaces:**
- Produces: `fetch_article(url: str, *, cache_path: Optional[str] = None, ttl_days: int = 7, now: Optional[datetime] = None) -> Optional[str]` — returns extracted readable text, or `None` on any failure (network error, empty body, paywall/too-short). Caches by `sha256(url)` with an `expires_at` ISO field, mirroring `loader.py:load_published_urls`. `now` is injectable for deterministic TTL tests.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_source_fetcher.py
import sys, os, json, tempfile
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import source_fetcher


def test_fetch_failure_returns_none(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")
    monkeypatch.setattr(source_fetcher, "_http_get", boom)
    assert source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None


def test_short_body_treated_as_failure(monkeypatch):
    monkeypatch.setattr(source_fetcher, "_http_get", lambda url, timeout=10: "<html><body>x</body></html>")
    assert source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None


def test_cache_hit_skips_fetch(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump({key: {"text": "CACHED ARTICLE TEXT " * 20,
                         "expires_at": (now + timedelta(days=3)).isoformat()}}, fh)
    def fail(*a, **k):
        raise AssertionError("should not fetch on cache hit")
    monkeypatch.setattr(source_fetcher, "_http_get", fail)
    out = source_fetcher.fetch_article("https://example.com/a", cache_path=cache.name, now=now)
    assert out and out.startswith("CACHED ARTICLE TEXT")


def test_expired_cache_refetches(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump({key: {"text": "OLD", "expires_at": (now - timedelta(days=1)).isoformat()}}, fh)
    monkeypatch.setattr(source_fetcher, "_http_get",
                        lambda url, timeout=10: "<html><body>" + ("fresh article body " * 40) + "</body></html>")
    out = source_fetcher.fetch_article("https://example.com/a", cache_path=cache.name, now=now)
    assert out and "fresh article body" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_source_fetcher.py -q`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/news/source_fetcher.py
"""Read-only, cached fetch of public news article text (Sub-project A).

Fail-closed: any error / empty / too-short body returns None so the caller
keeps the existing short summary. Never raises to the caller. Cache mirrors
loader.load_published_urls (per-key expires_at ISO, 7-day TTL).
"""
import hashlib
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

_MIN_TEXT_LEN = 400  # below this we treat as paywall/empty → fail closed
_UA = "Mozilla/5.0 (compatible; tech-blog-digest/1.0; +https://tech.2twodragon.com)"


def _key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _http_get(url: str, timeout: int = 10) -> str:
    import requests  # lazy, matches repo pattern
    resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _extract_text(html: str) -> str:
    # strip script/style, tags → whitespace-collapsed text
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _load_cache(path: Optional[str]) -> dict:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_cache(path: Optional[str], data: dict) -> None:
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    except OSError:
        logging.debug("source_fetcher: cache write failed for %s", path)


def fetch_article(url: str, *, cache_path: Optional[str] = None,
                  ttl_days: int = 7, now: Optional[datetime] = None) -> Optional[str]:
    if not url or not url.startswith(("http://", "https://")):
        return None
    now = now or datetime.now()
    cache = _load_cache(cache_path)
    key = _key(url)
    entry = cache.get(key)
    if entry:
        try:
            if datetime.fromisoformat(entry["expires_at"]) > now:
                return entry.get("text") or None
        except (KeyError, ValueError):
            pass
    try:
        html = _http_get(url)
    except Exception as exc:  # fail-closed on ANY fetch error
        logging.info("source_fetcher: fetch failed (%s) — keeping short summary", exc)
        return None
    text = _extract_text(html)
    if len(text) < _MIN_TEXT_LEN:
        return None
    cache[key] = {"text": text, "expires_at": (now + timedelta(days=ttl_days)).isoformat()}
    _save_cache(cache_path, cache)
    return text
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_source_fetcher.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/news/source_fetcher.py scripts/tests/test_source_fetcher.py
git commit -m "feat(digest): source_fetcher — read-only cached article fetch, fail-closed"
```

### Task 8: `summary_expander` — Gemini-first source-grounded expansion

**Files:**
- Create: `scripts/news/summary_expander.py`
- Test: `scripts/tests/test_summary_expander.py`

**Interfaces:**
- Consumes: `_gemini_call(prompt, timeout)` from `scripts.news.enhancer` (enhancer.py:71); `fetch_article` from Task 7.
- Produces: `expand_summary(item: Dict, article_text: str, *, gemini=None) -> Optional[str]` — returns detailed original markdown grounded in `article_text`, or `None` if the LLM is unavailable/empty (caller then keeps the safe short summary). `gemini` is an injectable callable for tests (defaults to `enhancer._gemini_call`). The prompt forbids adding facts not present in `article_text`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_summary_expander.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import summary_expander


def test_returns_none_when_llm_empty():
    out = summary_expander.expand_summary(
        {"title": "t", "url": "u"}, "some real article text " * 30,
        gemini=lambda prompt, timeout=35: "")
    assert out is None


def test_prompt_includes_source_and_forbids_fabrication():
    captured = {}
    def fake(prompt, timeout=35):
        captured["p"] = prompt
        return "#### 분석\n실제 근거 기반 내용"
    out = summary_expander.expand_summary(
        {"title": "제로데이", "url": "https://x"}, "ARTICLE BODY EVIDENCE " * 20, gemini=fake)
    assert out and "실제 근거" in out
    assert "ARTICLE BODY EVIDENCE" in captured["p"]      # source is grounded in
    assert ("추가하지" in captured["p"]) or ("없는" in captured["p"])  # no-fabrication instruction


def test_returns_none_when_no_article_text():
    out = summary_expander.expand_summary({"title": "t", "url": "u"}, "",
                                          gemini=lambda p, timeout=35: "x")
    assert out is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_summary_expander.py -q`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/news/summary_expander.py
"""Gemini-first, source-grounded per-item expansion (Sub-project A).

Given the fetched article text, produce a more detailed ORIGINAL analysis
(what happened, mechanism, DevSecOps impact) that asserts nothing absent
from the source. Returns None when the source is empty or the LLM is
unavailable — the caller keeps the existing short summary. No paid API here;
uses the free Gemini CLI wrapper (enhancer._gemini_call, itself CLI-first).
"""
import logging
from typing import Callable, Dict, Optional

_MAX_SOURCE_CHARS = 6000   # bound prompt size / cost
_MIN_OUTPUT_CHARS = 120


def _default_gemini(prompt: str, timeout: int = 35) -> str:
    try:
        from enhancer import _gemini_call
    except ImportError:
        from scripts.news.enhancer import _gemini_call
    return _gemini_call(prompt, timeout=timeout)


def expand_summary(item: Dict, article_text: str, *,
                   gemini: Optional[Callable] = None) -> Optional[str]:
    if not article_text or not article_text.strip():
        return None
    gemini = gemini or _default_gemini
    title = item.get("title", "")
    source = article_text.strip()[:_MAX_SOURCE_CHARS]
    prompt = (
        "아래 [원문]만 근거로 DevSecOps 관점 분석을 한국어로 작성하라.\n"
        "규칙: [원문]에 없는 사실/수치/CVE/제품명을 추가하지 말 것. "
        "추측·일반론 금지. 원문에 근거가 없으면 그 문장을 쓰지 말 것.\n"
        "형식: '#### 기술적 배경'과 '#### 실무 영향' 두 소제목(#### 고정)만 사용, "
        "각 2-4문장. 체크리스트/권장 조치 목록은 쓰지 말 것.\n\n"
        f"제목: {title}\n[원문]\n{source}\n"
    )
    try:
        out = gemini(prompt, timeout=35)
    except Exception as exc:
        logging.info("summary_expander: LLM error (%s) — keeping short summary", exc)
        return None
    if not out or len(out.strip()) < _MIN_OUTPUT_CHARS:
        return None
    return out.strip()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_summary_expander.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/news/summary_expander.py scripts/tests/test_summary_expander.py
git commit -m "feat(digest): summary_expander — Gemini-first source-grounded expansion"
```

### Task 9: Honesty gate — reject expansions with unsupported tokens

**Files:**
- Modify: `scripts/news/summary_expander.py` (add `is_source_grounded`)
- Test: `scripts/tests/test_summary_expander.py` (extend)

**Interfaces:**
- Produces: `is_source_grounded(expanded: str, article_text: str) -> bool` — False when the expansion contains a CVE id, a numeric statistic, or a capitalized product token that does not appear in `article_text` (or the item title). Verifiable, deterministic, no LLM.

- [ ] **Step 1: Write the failing test**

```python
# append to scripts/tests/test_summary_expander.py
def test_honesty_rejects_unsupported_cve():
    assert summary_expander.is_source_grounded(
        "CVE-2026-9999 관련 위협", "article without that cve") is False


def test_honesty_rejects_unsupported_number():
    assert summary_expander.is_source_grounded(
        "총 622개의 취약점이 발견", "article mentions a few bugs, no counts") is False


def test_honesty_accepts_grounded_text():
    src = "The advisory covers CVE-2026-1234 affecting 3 products."
    assert summary_expander.is_source_grounded(
        "CVE-2026-1234 는 3 개 제품에 영향", src) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_summary_expander.py -k honesty -q`
Expected: FAIL — `AttributeError: is_source_grounded`

- [ ] **Step 3: Write minimal implementation**

```python
# append to scripts/news/summary_expander.py
import re

_CVE_RE = re.compile(r"CVE-\d{4}-\d+")
_NUM_RE = re.compile(r"\d[\d,]{1,}")  # multi-digit numbers / stats


def is_source_grounded(expanded: str, article_text: str) -> bool:
    """Every CVE and multi-digit statistic asserted in `expanded` must also
    appear in the source. Prevents the LLM inventing counts/identifiers."""
    hay = article_text or ""
    for cve in _CVE_RE.findall(expanded):
        if cve not in hay:
            return False
    for num in _NUM_RE.findall(expanded):
        norm = num.replace(",", "")
        if norm not in hay.replace(",", ""):
            return False
    return True
```

- [ ] **Step 4: Have `expand_summary` enforce the gate**

In `expand_summary`, before `return out.strip()`, add:

```python
    cleaned = out.strip()
    if not is_source_grounded(cleaned, source):
        logging.info("summary_expander: honesty gate rejected expansion — falling back")
        return None
    return cleaned
```
(remove the old `return out.strip()`.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_summary_expander.py -q`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add scripts/news/summary_expander.py scripts/tests/test_summary_expander.py
git commit -m "feat(digest): honesty gate — reject unsupported CVE/numbers in expansion"
```

### Task 10: Wire expander into `generate_news_section` (A behind fetch, fail-safe)

**Files:**
- Modify: `scripts/news/content_generator.py` (deep-analysis branch ~line 2819-2831)
- Test: `scripts/tests/test_digest_structure.py` (extend)

**Interfaces:**
- Consumes: `fetch_article` (Task 7), `expand_summary` (Task 8-9), `_normalize_deep_analysis` (Task 1).
- Behavior: for a deep-analysis item, try fetch → expand. On success, splice the normalized expansion. On ANY None, fall back to the current `enhance_content_with_fallback` path unchanged. A module env flag `DIGEST_SOURCE_EXPANSION=1` gates the new path so Sub-project 0 output is unaffected until A is enabled.

- [ ] **Step 1: Write the failing test**

```python
# append to scripts/tests/test_digest_structure.py
import content_generator


def test_expansion_disabled_by_default(monkeypatch):
    monkeypatch.delenv("DIGEST_SOURCE_EXPANSION", raising=False)
    # _maybe_source_expansion returns None when the flag is off
    assert content_generator._maybe_source_expansion(
        {"title": "t", "url": "https://x", "category": "security"}) is None


def test_expansion_returns_normalized_when_enabled(monkeypatch):
    monkeypatch.setenv("DIGEST_SOURCE_EXPANSION", "1")
    monkeypatch.setattr(content_generator, "_fetch_article_for", lambda url: "SRC " * 50)
    monkeypatch.setattr(content_generator, "_expand_summary_for",
                        lambda item, txt: "## 1. 배경\n내용")  # H2 → must be demoted
    out = content_generator._maybe_source_expansion(
        {"title": "t", "url": "https://x", "category": "security"})
    assert out is not None
    assert "## 1. 배경" not in out and "#### 배경" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -k expansion -q`
Expected: FAIL — `AttributeError: _maybe_source_expansion`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/news/content_generator.py` (near `generate_news_section`):

`os` is already imported at module level (content_generator.py:6) — use it directly.

```python
def _fetch_article_for(url: str):
    try:
        from source_fetcher import fetch_article
    except ImportError:
        from scripts.news.source_fetcher import fetch_article
    cache = os.path.join(
        os.path.dirname(__file__), "..", "..", "_data", "source_articles_cache.json")
    return fetch_article(url, cache_path=cache)


def _expand_summary_for(item, article_text):
    try:
        from summary_expander import expand_summary
    except ImportError:
        from scripts.news.summary_expander import expand_summary
    return expand_summary(item, article_text)


def _maybe_source_expansion(item):
    """Sub-project A entry: gated source-grounded expansion. Returns
    normalized markdown or None (caller keeps current behavior)."""
    if os.getenv("DIGEST_SOURCE_EXPANSION") != "1":
        return None
    article = _fetch_article_for(item.get("url", ""))
    if not article:
        return None
    expanded = _expand_summary_for(item, article)
    if not expanded:
        return None
    return _normalize_deep_analysis(expanded)
```

Then in the deep-analysis branch at line 2820, prefer the expansion:

```python
    if is_critical and category in ("security", "devsecops"):
        expanded = _maybe_source_expansion(item)
        if expanded:
            section += expanded + "\n\n"
            if cve_ids:
                section += generate_mitre_mapping(cve_ids[0], item)
            section += "\n---\n\n"
            return section
        enhanced = enhance_content_with_fallback(item)
        if enhanced:
            section += _normalize_deep_analysis(enhanced) + "\n\n"
            if cve_ids:
                section += generate_mitre_mapping(cve_ids[0], item)
            section += "\n---\n\n"
            return section
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add scripts/news/content_generator.py scripts/tests/test_digest_structure.py
git commit -m "feat(digest): wire source-grounded expansion behind DIGEST_SOURCE_EXPANSION flag"
```

### Task 11: Regenerate pilot with expansion ON; verify honesty + quality

- [ ] **Step 1** Set `DIGEST_SOURCE_EXPANSION=1` and ensure Gemini CLI is available (`check_gemini_available()` truthy); confirm no paid DeepSeek key is required.
- [ ] **Step 2** A/B backfill mechanism (finalize now that Task 6 review has revealed the real post structure): extend `backfill_digest_structure.py` (or add a sibling `backfill_digest_enrichment.py`) that, per existing pilot post, parses each item's source URL from the `{% include news-card.html … url="…" %}` blocks in the body, calls `_fetch_article_for(url)` → `_maybe_source_expansion(item)` (Task 10), and splices the normalized expansion into that item's deep-analysis region. Fail-closed per item (keep current text on None). Do NOT re-run `auto_publish_news.py --date` — it fetches *current* news and cannot reproduce the 5-day-old item set (same reason as Task 6).
- [ ] **Step 3** Run structural guard (Task 5) — expect OK on all 5.
- [ ] **Step 4** Manually diff 3 items: expanded body must read as original analysis, not a headline paraphrase, and assert nothing absent from the source. Count Gemini calls; confirm paid API not hit.
- [ ] **Step 5** Commit: `git commit -m "feat(digest): backfill 5 pilot digests with source-grounded detail"`

**STOP for review** before Sub-project B.

---

## SUB-PROJECT B — Body-level sequence diagrams (THIRD, after A reviewed)

One body-level `sequenceDiagram` per item, ONLY where a real flow exists. Default = no diagram (honest). Safari-safe, passes `validate_mermaid_syntax.py`.

### Task 12: `flow_detector` — decide if an item has a real sequence-able flow

**Files:**
- Create: `scripts/news/flow_detector.py`
- Test: `scripts/tests/test_flow_detector.py`

**Interfaces:**
- Produces: `has_flow(item: Dict, article_text: str) -> bool` — True only when the source describes an attack chain / exploitation steps / incident timeline. Keyword pre-pass (fast, deterministic); default False on uncertainty. (LLM classify is a future enhancement — YAGNI for pilot; keyword pass is honest because it defaults to no-diagram.)

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_flow_detector.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import flow_detector


def test_attack_chain_is_flow():
    assert flow_detector.has_flow(
        {"title": "loader chain"},
        "The attacker first sends a phishing email, then the loader downloads a payload, "
        "then it executes and exfiltrates data to the C2 server.") is True


def test_price_story_is_not_flow():
    assert flow_detector.has_flow(
        {"title": "bitcoin price"},
        "Bitcoin rose 5 percent today as investors reacted to macro news.") is False


def test_empty_source_is_not_flow():
    assert flow_detector.has_flow({"title": "x"}, "") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_flow_detector.py -q`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/news/flow_detector.py
"""Detect whether a news item describes a real, sequence-able flow (Sub-project B).

Conservative: defaults to False. A diagram is only worth drawing for attack
chains, exploitation steps, or incident timelines. Forcing a diagram onto a
price/opinion story would fabricate a flow (spec Non-goals), so uncertainty
resolves to no diagram.
"""
import re
from typing import Dict

# ordered-step / chain language (EN + KO)
_STEP_WORDS = ("first", "then", "next", "finally", "after", "subsequently",
               "먼저", "다음", "이후", "그다음", "마지막")
_CHAIN_WORDS = ("attack chain", "kill chain", "loader", "payload", "exfiltrat",
                "lateral movement", "privilege escalation", "c2", "command and control",
                "phishing", "dropper", "공격 체인", "감염 단계", "침투", "권한 상승")
_MIN_STEPS = 2


def has_flow(item: Dict, article_text: str) -> bool:
    text = (article_text or "").lower()
    if len(text) < 200:
        return False
    step_hits = sum(1 for w in _STEP_WORDS if w in text)
    chain_hit = any(w in text for w in _CHAIN_WORDS)
    # need both sequential language AND chain/attack vocabulary
    return step_hits >= _MIN_STEPS and chain_hit
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_flow_detector.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/news/flow_detector.py scripts/tests/test_flow_detector.py
git commit -m "feat(digest): flow_detector — conservative attack-chain detection"
```

### Task 13: `sequence_diagram` — build one Safari-safe body diagram

**Files:**
- Create: `scripts/news/sequence_diagram.py`
- Test: `scripts/tests/test_sequence_diagram.py`

**Interfaces:**
- Consumes: `_gemini_call` (enhancer.py:71) for step extraction; `flow_detector.has_flow` (Task 12).
- Produces: `build_sequence_diagram(item: Dict, article_text: str, *, gemini=None) -> Optional[str]` — returns a fenced ```mermaid `sequenceDiagram` block (Safari-safe participant/message labels: ASCII-ish, no bare `-`/`&`/parens in labels), or None. Steps are derived from `article_text`, never invented.
- Safari-safe rule (from `fix_all_mermaid_safari.py` / `validate_mermaid_syntax.py`): participant names are simple identifiers; message text has `-`, `&`, `(`, `)` stripped/replaced.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_sequence_diagram.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import sequence_diagram


def test_returns_none_without_flow():
    out = sequence_diagram.build_sequence_diagram(
        {"title": "price"}, "bitcoin rose today no flow here at all " * 10,
        gemini=lambda p, timeout=35: "")
    assert out is None


def test_builds_safari_safe_block():
    steps = "Attacker->>Victim: phishing email\nVictim->>Loader: opens attachment\nLoader->>C2: exfiltrate data"
    out = sequence_diagram.build_sequence_diagram(
        {"title": "loader chain"},
        "attacker first sends phishing then loader downloads payload then exfiltrate to c2 " * 5,
        gemini=lambda p, timeout=35: steps)
    assert out is not None
    assert out.startswith("```mermaid")
    assert "sequenceDiagram" in out
    assert out.rstrip().endswith("```")
    # Safari-safe: no bare parens/ampersand in message labels
    assert "(" not in out and ")" not in out and "&" not in out


def test_sanitizes_unsafe_chars_from_llm_steps():
    steps = "A->>B: exploit CVE-2026-1 (RCE) & pivot"
    out = sequence_diagram.build_sequence_diagram(
        {"title": "chain"}, "first then attack chain loader payload exfiltrate " * 20,
        gemini=lambda p, timeout=35: steps)
    assert out is not None
    assert "(" not in out and ")" not in out and "&" not in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/tests/test_sequence_diagram.py -q`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/news/sequence_diagram.py
"""Build one Safari-safe body-level mermaid sequenceDiagram (Sub-project B).

Only called for flow-positive items (flow_detector). Steps come from the
source via the LLM; labels are sanitized to the Safari-safe subset enforced
by validate_mermaid_syntax.py. Returns None on any failure → no diagram.
"""
import logging
import re
from typing import Callable, Dict, Optional

from flow_detector import has_flow  # sibling import (tests add news/ to path)

_ARROW_RE = re.compile(r"^\s*([\w ]+?)\s*-?->>?\s*([\w ]+?)\s*:\s*(.+?)\s*$")


def _default_gemini(prompt: str, timeout: int = 35) -> str:
    try:
        from enhancer import _gemini_call
    except ImportError:
        from scripts.news.enhancer import _gemini_call
    return _gemini_call(prompt, timeout=timeout)


def _safe_label(text: str) -> str:
    text = text.replace("&", " and ").replace("(", " ").replace(")", " ")
    text = text.replace("-", " ")            # bare hyphen breaks Safari mermaid
    return re.sub(r"\s+", " ", text).strip()


def _safe_actor(text: str) -> str:
    return re.sub(r"[^\w]", "_", text.strip()) or "Actor"


def build_sequence_diagram(item: Dict, article_text: str, *,
                           gemini: Optional[Callable] = None) -> Optional[str]:
    if not has_flow(item, article_text):
        return None
    gemini = gemini or _default_gemini
    prompt = (
        "아래 [원문]에 서술된 공격/침해 흐름을 mermaid sequenceDiagram 스텝으로만 출력하라.\n"
        "각 줄 형식: Actor->>Target: 행위 (원문에 있는 단계만, 지어내지 말 것). 3-6줄.\n"
        f"[원문]\n{(article_text or '')[:4000]}\n"
    )
    try:
        raw = gemini(prompt, timeout=35)
    except Exception as exc:
        logging.info("sequence_diagram: LLM error (%s) — no diagram", exc)
        return None
    if not raw:
        return None
    lines = []
    for ln in raw.split("\n"):
        m = _ARROW_RE.match(ln)
        if not m:
            continue
        src, dst, msg = _safe_actor(m.group(1)), _safe_actor(m.group(2)), _safe_label(m.group(3))
        if msg:
            lines.append(f"    {src}->>{dst}: {msg}")
    if len(lines) < 2:
        return None
    body = "sequenceDiagram\n" + "\n".join(lines)
    return "```mermaid\n" + body + "\n```"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest scripts/tests/test_sequence_diagram.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Validate against the real mermaid syntax gate**

Write a tiny post fixture embedding the generated block and run:
Run: `python3 scripts/validate_mermaid_syntax.py <fixture.md>`
Expected: exit 0 (Safari-safe).

- [ ] **Step 6: Commit**

```bash
git add scripts/news/sequence_diagram.py scripts/tests/test_sequence_diagram.py
git commit -m "feat(digest): sequence_diagram — Safari-safe body diagram for flow items"
```

### Task 14: Wire diagrams in, regenerate pilot, run all gates

**Files:**
- Modify: `scripts/news/content_generator.py` (deep-analysis branch — append diagram after expansion for flow items, behind the same `DIGEST_SOURCE_EXPANSION` flag)

- [ ] **Step 1** In `_maybe_source_expansion` (Task 10), after obtaining `article`, append a diagram when present:

```python
    result = _normalize_deep_analysis(expanded)
    try:
        from sequence_diagram import build_sequence_diagram
    except ImportError:
        from scripts.news.sequence_diagram import build_sequence_diagram
    diagram = build_sequence_diagram(item, article)
    if diagram:
        result += "\n\n#### 공격 흐름\n\n" + diagram
    return result
```

- [ ] **Step 2** Add a test asserting a diagram is appended only for flow items (monkeypatch `build_sequence_diagram`); extend `scripts/tests/test_digest_structure.py`. Run: `python3 -m pytest scripts/tests/test_digest_structure.py -q` → PASS.
- [ ] **Step 3** Re-run the A/B backfill from Task 11 Step 2 (now with the diagram append wired in) over the 5 pilot posts, `DIGEST_SOURCE_EXPANSION=1`.
- [ ] **Step 4** Run the FULL gate set:
```bash
python3 scripts/check_digest_structure.py _posts/2026-07-1{1,2,3,4,5}-*.md
python3 scripts/validate_mermaid_syntax.py _posts/2026-07-1{1,2,3,4,5}-*.md
node scripts/tests/check_mermaid_csp_render.mjs   # PR #449 guard (if run standalone)
python3 -m pytest scripts/tests/ -q
```
Expected: all pass; mermaid appears only on flow items; summary card has NO mermaid.
- [ ] **Step 5** Confirm summary-card cleanliness: `grep -c mermaid` inside any `ai-summary-card` include region = 0.
- [ ] **Step 6** Commit: `git commit -m "feat(digest): body sequence diagrams for flow items + pilot backfill"`

---

## Final verification (whole feature)

- [ ] `python3 -m pytest scripts/tests/ -q` — all pass, coverage for `auto_publish_news.py` still ≥ 40%.
- [ ] `ruff check scripts/` clean on new/modified files (note: `ops_health_orchestrator` reformats scripts/ in place — if run, `git checkout -- scripts/` anything unrelated).
- [ ] All 5 pilot posts pass `check_digest_structure.py`, `validate_mermaid_syntax.py`, mermaid-csp-render, and the digest fact-check.
- [ ] No paid API calls made (Gemini CLI only); no cover regeneration performed.
- [ ] Cover SVGs untouched (Sub-project scope excludes covers — see `cover-system` skill).
- [ ] Dispatch `oh-my-claudecode:code-reviewer` (opus) for an independent approval pass before declaring complete.

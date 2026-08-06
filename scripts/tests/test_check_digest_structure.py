import re
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
import check_digest_structure as cds
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

# A clean post: global checklist with P0 checkboxes AFTER '## 실무 체크리스트',
# and a low-severity item's prose advisory (`- `, no `[ ]`) which is KEPT.
_GOOD = _GOOD.replace(
    "#### 기술적 배경\n",
    "#### 기술적 배경\n#### 권장 조치\n- 관련 시스템 목록 확인\n- 벤더 권고 확인\n",
).replace("### P0 (즉시)\n", "### P0 (즉시)\n- [ ] 긴급 패치 확인\n")

_BAD_H1 = _GOOD.replace("#### 기술적 배경", "# DevSecOps 관점 분석")
_BAD_NUM = _GOOD.replace("## 2. AI/ML 뉴스", "## 1. 기술적 배경")
# per-item CHECKBOX checklist injected into the item body (BEFORE the global checklist)
_BAD_DUP_CL = _GOOD.replace(
    "## 2. AI/ML 뉴스",
    "#### 대응 체크리스트\n- [ ] 패치\n- [ ] 모니터링\n## 2. AI/ML 뉴스",
)


def _write(txt):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(txt); f.close(); return f.name


def test_clean_post_has_no_violations():
    # prose `- ` advisory under '#### 권장 조치' is allowed; only checkbox
    # per-item checklists are the defect.
    assert check_post(_write(_GOOD)) == []


def test_flags_body_h1():
    assert any("H1" in v for v in check_post(_write(_BAD_H1)))


def test_flags_numbering_collision():
    assert any("numbering" in v.lower() for v in check_post(_write(_BAD_NUM)))


def test_flags_per_item_checkbox_checklist():
    assert any("checklist" in v.lower() or "체크리스트" in v
               for v in check_post(_write(_BAD_DUP_CL)))


def test_does_not_flag_prose_advisory():
    # '#### 권장 조치' followed by prose `- ` bullets (no `[ ]`) is kept.
    prose = _GOOD  # already contains a prose 권장 조치 block
    assert check_post(_write(prose)) == []


def test_does_not_flag_대응_체크리스트_in_prose():
    # "대응 체크리스트" as incidental PROSE (e.g. a reference-table cell) is NOT
    # a per-item checklist heading → must not be flagged. Only ##/###/#### headings
    # are the defect. False positive surfaced on the 2026-02-08 digest.
    prose = _GOOD.replace(
        "## 2. AI/ML 뉴스",
        "## 2. AI/ML 뉴스\n| CISA Guide | 랜섬웨어 사고 대응 체크리스트 |",
    )
    assert not any("대응 체크리스트" in v for v in check_post(_write(prose)))


def test_flags_per_item_대응_체크리스트_heading():
    # A real per-item '#### 대응 체크리스트' heading (no checkbox) is still caught.
    bad = _GOOD.replace("## 2. AI/ML 뉴스", "#### 대응 체크리스트\n본문.\n## 2. AI/ML 뉴스")
    assert any("대응 체크리스트" in v for v in check_post(_write(bad)))


# A fenced code EXAMPLE block whose contents look like violations
# ('## 5. ...' numbering, '- [ ]' checkbox, '대응 체크리스트' heading) must be
# ignored by ALL checks, not just the H1 check. Outside the fence, the post
# has a single valid '## 실무 체크리스트' and no numbered headings at all
# (so the numbering check has nothing to flag) — i.e. the ONLY occurrences
# of these patterns anywhere in the body live inside the fence.
_GOOD_WITH_CODE_FENCE = """---
title: x
---
## 소개

다음은 예시 포맷입니다.

```markdown
## 5. 예시 섹션
- [ ] 예시 체크박스
#### 대응 체크리스트
```

본문 설명이 이어집니다.

## 실무 체크리스트
### P0 (즉시)
- [ ] 긴급 패치 확인
"""


def test_ignores_violations_inside_fenced_code_block():
    assert check_post(_write(_GOOD_WITH_CODE_FENCE)) == []


# ---------------------------------------------------------------------------
# CLI mode plumbing: digest-filename filter + --all exit code (Task A, PR
# follow-up). Every mode must filter to filenames containing "Weekly_Digest"
# — non-digest posts have different structure and would false-positive on
# these checks, so they are always skipped, even when explicitly named.
# ---------------------------------------------------------------------------


def test_non_digest_post_skipped_even_if_malformed(tmp_path, monkeypatch):
    # Malformed content (body H1) but a filename that is NOT a digest post.
    non_digest = tmp_path / "2026-07-11-Some_Regular_Post.md"
    non_digest.write_text(_BAD_H1, encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["check_digest_structure.py", str(non_digest)])
    with pytest.raises(SystemExit) as exc_info:
        cds.main()
    # Explicit-path mode filtered the non-digest file out -> nothing to
    # check -> clean pass, regardless of its (malformed) content.
    assert exc_info.value.code == 0


def test_all_mode_temp_dir_one_clean_one_bad_exits_nonzero(tmp_path, monkeypatch):
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    (posts_dir / "2026-07-11-Tech_Security_Weekly_Digest_Clean.md").write_text(
        _GOOD, encoding="utf-8"
    )
    (posts_dir / "2026-07-12-Tech_Security_Weekly_Digest_Bad.md").write_text(
        _BAD_H1, encoding="utf-8"
    )

    monkeypatch.setattr(cds, "REPO", tmp_path)
    monkeypatch.setattr(cds, "POSTS_DIR", posts_dir)
    monkeypatch.setattr(sys, "argv", ["check_digest_structure.py", "--all"])

    with pytest.raises(SystemExit) as exc_info:
        cds.main()
    assert exc_info.value.code != 0


# --- ratchet: legacy defects grandfathered, regressions still blocked --------
#
# Rationale: the legacy corpus carries pre-existing structural defects awaiting a
# staged backfill campaign. A file-scoped gate blocks UNRELATED improvements to
# those posts (e.g. a pure 비트코인→Bitcoin proper-noun swap). The ratchet compares
# against the base revision so only NEW violations fail.


def test_new_violations_grandfathers_preexisting():
    base = check_post(_write(_BAD_H1))
    current = check_post(_write(_BAD_H1))
    assert base  # sanity: the fixture really is defective
    assert cds.new_violations(current, base) == []


def test_new_violations_flags_added_defect():
    base = check_post(_write(_BAD_H1))
    # same pre-existing H1 defect PLUS a newly broken numbering
    current = check_post(_write(_BAD_H1.replace("## 2. AI/ML 뉴스", "## 1. 기술적 배경")))
    fresh = cds.new_violations(current, base)
    assert len(fresh) == 1 and "numbering" in fresh[0].lower()


def test_new_violations_treats_missing_base_as_all_new():
    # A brand-new post has no base revision: every violation must be reported,
    # so newly authored posts are still held to the full standard.
    current = check_post(_write(_BAD_H1))
    assert cds.new_violations(current, None) == current


def test_new_violations_is_multiset_not_set():
    # Two identical messages pre-existing, three now => exactly one is new.
    base = ["body H1 heading found: # x", "body H1 heading found: # x"]
    current = base + ["body H1 heading found: # x"]
    assert cds.new_violations(current, base) == ["body H1 heading found: # x"]


def test_new_violations_ignores_reworded_instance_of_same_defect():
    # A violation message that quotes post content must not make the ratchet
    # content-sensitive: editing a DEFECTIVE line for an unrelated reason (here a
    # 안드로이드→Android proper-noun swap inside an offending body H1) keeps the
    # defect set identical, so nothing is new. Measured on 2026-05-05: the swap
    # kept 6 violations at 6 yet reported "+1 new" before this fix.
    base = ["body H1 heading found: # 관점 분석: 안드로이드 스파이 도구"]
    current = ["body H1 heading found: # 관점 분석: Android 스파이 도구"]
    assert cds.new_violations(current, base) == []


def test_new_violations_still_counts_an_additional_instance_per_kind():
    # Rewording is forgiven, but an EXTRA instance of the same kind is not: a post
    # that had 2 body H1s and now has 3 is a regression regardless of the wording.
    base = ["body H1 heading found: # a", "body H1 heading found: # b"]
    current = [
        "body H1 heading found: # a2",
        "body H1 heading found: # b2",
        "body H1 heading found: # c",
    ]
    assert len(cds.new_violations(current, base)) == 1


def test_new_violations_still_flags_a_different_kind_after_rewording():
    # Kind-keyed comparison must not let a genuinely new KIND ride along with a
    # reworded pre-existing one.
    base = ["body H1 heading found: # old"]
    current = [
        "body H1 heading found: # new wording",
        "broken section numbering: [1, 1, 2]",
    ]
    fresh = cds.new_violations(current, base)
    assert len(fresh) == 1 and "numbering" in fresh[0].lower()


def test_kind_handles_messages_without_embedded_content():
    # Colon-free messages key on the whole string, so they still match exactly.
    msg = "per-item checkbox checklist present in an item body (should be removed)"
    assert cds._kind(msg) == msg
    assert cds.new_violations([msg], [msg]) == []


def test_ratchet_requires_a_diff_scoped_mode(monkeypatch, capsys):
    # --ratchet without --staged/--changed has no base revision to compare to.
    monkeypatch.setattr(sys, "argv", ["check_digest_structure.py", "--ratchet", "--all"])
    with pytest.raises(SystemExit) as exc:
        cds.main()
    assert exc.value.code != 0


def test_check_text_and_check_post_agree():
    assert cds.check_text(_BAD_H1) == check_post(_write(_BAD_H1))


# --- scorer/gate agreement invariant ----------------------------------------
#
# validate_post_quality.validate_checklists scores the DOCUMENT-WIDE '- [ ]'
# count, while this gate wants per-item checkboxes gone and only the global
# '## 실무 체크리스트' boxed (R3 removes, R6 restores). Those two only agree so
# long as every checkbox in a digest lives under the global heading — which is
# what R3+R6 converged the corpus on (measured 2026-08-06: doc-wide == section
# count for all 185 digests, and no checkbox hides inside a code fence).
#
# Pinning that equality is what makes "scope the scorer to the global section"
# unnecessary: scoping is a provable no-op while this holds, and it would zero
# the 66 non-digest posts that legitimately checklist under other headings.
# The day this fails, the scorer and the gate have started disagreeing again.


def _fence_stripped(text: str) -> str:
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _global_checklist_section(clean_body: str) -> str:
    m = re.search(r"^## 실무 체크리스트[ \t]*$", clean_body, re.MULTILINE)
    if not m:
        return ""
    rest = clean_body[m.end():]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def test_every_digest_checkbox_lives_under_the_global_checklist():
    repo = Path(__file__).resolve().parent.parent.parent
    offenders = {}
    for p in sorted((repo / "_posts").glob("*Weekly_Digest*.md")):
        clean = _fence_stripped(p.read_text(encoding="utf-8"))
        doc_wide = len(re.findall(r"- \[ \]", clean))
        in_section = len(re.findall(r"- \[ \]", _global_checklist_section(clean)))
        if doc_wide != in_section:
            offenders[p.name] = f"doc-wide={doc_wide} in-section={in_section}"
    assert offenders == {}, offenders


def test_fenced_checkboxes_do_not_inflate_any_digest_score():
    """A '- [ ]' inside a code fence would score but is not a real checklist."""
    repo = Path(__file__).resolve().parent.parent.parent
    offenders = {}
    for p in sorted((repo / "_posts").glob("*Weekly_Digest*.md")):
        raw = p.read_text(encoding="utf-8")
        if len(re.findall(r"- \[ \]", raw)) != len(
            re.findall(r"- \[ \]", _fence_stripped(raw))
        ):
            offenders[p.name] = "fenced checkbox inflates the document-wide count"
    assert offenders == {}, offenders


def test_placement_helpers_actually_detect_a_violation():
    """Proof the two corpus guards above are not vacuously green."""
    item_box = (
        "## 1. 보안\n\n### 1.1 기사\n\n- [ ] 항목별 조치\n\n"
        "## 실무 체크리스트\n\n- [ ] 전역 조치\n"
    )
    clean = _fence_stripped(item_box)
    assert len(re.findall(r"- \[ \]", clean)) == 2
    assert len(re.findall(r"- \[ \]", _global_checklist_section(clean))) == 1

    trailing_box = "## 실무 체크리스트\n\n- [ ] 전역\n\n## 참고 자료\n\n- [ ] 나중 항목\n"
    clean = _fence_stripped(trailing_box)
    assert len(re.findall(r"- \[ \]", clean)) == 2
    assert len(re.findall(r"- \[ \]", _global_checklist_section(clean))) == 1

    fenced = "## 실무 체크리스트\n\n- [ ] 전역\n\n```markdown\n- [ ] 예시\n```\n"
    assert len(re.findall(r"- \[ \]", fenced)) == 2
    assert len(re.findall(r"- \[ \]", _fence_stripped(fenced))) == 1

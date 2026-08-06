"""Tests for scripts/restore_digest_structure.py (lossless structure restore).

Contract (docs/superpowers/specs/2026-08-04-digest-structure-backfill-design.md):
  - R1..R5 are LOSSLESS: reader-visible text is never deleted, only markers change
  - item-region scoped: section intros / the global checklist are untouched
  - rule order matters (R1 before R2, R4 before R5)
  - idempotent
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from restore_digest_structure import (  # noqa: E402
    TOP_SECTION_RE,
    boldify_response_checklist,
    canonicalize_checklist_heading,
    checkbox_global_checklist,
    demote_item_headings,
    lossless_tokens,
    main,
    renumber_sections,
    transform,
    unbox_item_checkboxes,
)

_FM = '---\ntitle: "x"\n---\n'


# --- R1: item-region heading demotion --------------------------------------


def test_demotes_h1_inside_item_region():
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 어떤 기사\n"
        "# DevSecOps 관점 분석: 안드로이드 스파이 도구\n"
        "본문.\n"
    )
    out = demote_item_headings(_FM + body)
    assert "#### DevSecOps 관점 분석: 안드로이드 스파이 도구" in out
    # heading TEXT survives verbatim (lossless)
    assert "DevSecOps 관점 분석: 안드로이드 스파이 도구" in out


def test_does_not_touch_top_level_section_heading():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n본문.\n## 실무 체크리스트\n- [ ] 항목\n"
    out = demote_item_headings(_FM + body)
    assert "## 1. 보안 뉴스" in out
    assert "## 실무 체크리스트" in out


def test_does_not_touch_headings_outside_item_region():
    # 경영진 브리핑 등 섹션 intro는 item 영역이 아니므로 verbatim.
    body = "## 경영진 브리핑\n### 이번 주 하이라이트\n요약.\n"
    out = demote_item_headings(_FM + body)
    assert "### 이번 주 하이라이트" in out


def test_front_matter_preserved():
    out = demote_item_headings(_FM + "## 1. 보안 뉴스\n")
    assert out.startswith(_FM)


# --- R2: 대응 체크리스트 heading -> bold ------------------------------------


def test_boldifies_response_checklist_heading():
    # 게이트는 '#{2,4} 대응 체크리스트' 헤딩을 결함으로 잡는다. 텍스트는 살리고
    # 헤딩만 볼드 강조로 바꾼다 (무손실).
    body = "#### 대응 체크리스트\n- 패치 적용\n"
    out = boldify_response_checklist(_FM + body)
    assert "**대응 체크리스트**" in out
    assert "#### 대응 체크리스트" not in out
    assert "- 패치 적용" in out


def test_boldifies_two_hash_form_too():
    # R1이 강등하지 못한 경우(item 영역 밖)도 게이트는 '## 대응 체크리스트'를 잡는다.
    out = boldify_response_checklist(_FM + "## 대응 체크리스트\n본문.\n")
    assert "**대응 체크리스트**" in out


def test_leaves_other_headings_alone():
    out = boldify_response_checklist(_FM + "#### 권장 조치\n- 패치.\n")
    assert "#### 권장 조치" in out


# --- R3: item-region checkbox -> plain bullet -------------------------------


def test_unboxes_checkbox_inside_item_region():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n- [ ] 패치 적용\n- [x] 로그 점검\n"
    out = unbox_item_checkboxes(_FM + body)
    assert "- 패치 적용" in out and "- 로그 점검" in out
    assert "[ ]" not in out and "[x]" not in out


def test_keeps_global_checklist_checkboxes():
    # 전역 '## 실무 체크리스트' 하위 체크박스는 정당한 산출물이므로 보존.
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 기사\n"
        "본문.\n"
        "## 실무 체크리스트\n"
        "- [ ] 전역 항목\n"
    )
    out = unbox_item_checkboxes(_FM + body)
    assert "- [ ] 전역 항목" in out


def test_preserves_checkbox_text_exactly():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n- [ ]   여백 있는 항목\n"
    out = unbox_item_checkboxes(_FM + body)
    assert "여백 있는 항목" in out


# --- R4: section renumbering ------------------------------------------------


def test_renumbers_broken_sequence():
    body = "## 1. 보안 뉴스\n본문\n## 3. AI/ML 뉴스\n본문\n## 7. 클라우드 뉴스\n"
    out = renumber_sections(_FM + body)
    assert "## 1. 보안 뉴스" in out
    assert "## 2. AI/ML 뉴스" in out
    assert "## 3. 클라우드 뉴스" in out


def test_renumber_preserves_section_titles():
    out = renumber_sections(_FM + "## 5. 보안 뉴스\n")
    assert "보안 뉴스" in out


def test_renumber_ignores_unnumbered_sections():
    body = "## 1. 보안 뉴스\n## 실무 체크리스트\n## 4. AI/ML 뉴스\n"
    out = renumber_sections(_FM + body)
    assert "## 실무 체크리스트" in out
    assert "## 2. AI/ML 뉴스" in out


def test_renumber_leaves_correct_sequence_untouched():
    body = "## 1. 보안 뉴스\n## 2. AI/ML 뉴스\n"
    assert renumber_sections(_FM + body) == _FM + body


# --- R5: numbered checklist heading -> canonical ----------------------------


def test_removes_number_from_checklist_heading():
    # check_digest_structure.py:80 은 리터럴 '## 실무 체크리스트'를 센다. 번호형은
    # 인식되지 않아 'found 0'으로 오보고된다 (티어 C 6건).
    out = canonicalize_checklist_heading(_FM + "## 9. 실무 체크리스트\n- [ ] 항목\n")
    assert "## 실무 체크리스트" in out
    assert "## 9. 실무 체크리스트" not in out
    assert "- [ ] 항목" in out


def test_leaves_plain_checklist_heading_alone():
    body = _FM + "## 실무 체크리스트\n- [ ] 항목\n"
    assert canonicalize_checklist_heading(body) == body


def test_does_not_touch_other_numbered_sections():
    out = canonicalize_checklist_heading(_FM + "## 3. 보안 뉴스\n")
    assert "## 3. 보안 뉴스" in out


# --- R6: global checklist plain bullet -> checkbox ---------------------------


def test_checkboxes_global_checklist_bullets():
    """R3가 per-item 체크박스를 없애면 레거시 파일에는 '- [ ]' 가 하나도 남지 않아
    validate_post_quality.validate_checklists 점수가 떨어진다(03-22: 91→83).
    현재 생성기는 전역 체크리스트에 '- [ ]' 를 쓰므로 레거시를 그 형태로 수렴시킨다.
    """
    body = "## 실무 체크리스트\n\n### P0 (즉시)\n\n- **긴급 패치** 확인\n- 모니터링 강화\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- [ ] **긴급 패치** 확인" in out
    assert "- [ ] 모니터링 강화" in out


def test_does_not_double_box_existing_checkboxes():
    body = "## 실무 체크리스트\n- [ ] 이미 체크박스\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- [ ] 이미 체크박스" in out
    assert "- [ ] [ ]" not in out


def test_does_not_touch_bullets_outside_the_checklist_section():
    body = "## 1. 보안 뉴스\n- 일반 불릿\n## 실무 체크리스트\n- 체크리스트 항목\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- 일반 불릿" in out  # 다른 섹션은 불변
    assert "- [ ] 체크리스트 항목" in out


def test_checklist_section_closes_at_next_top_heading():
    body = "## 실무 체크리스트\n- 항목\n## 참고 자료\n- 링크\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- [ ] 항목" in out
    assert "- 링크" in out and "- [ ] 링크" not in out


def test_does_not_box_nested_bullets():
    # 들여쓴 하위 불릿은 체크박스로 바꾸지 않는다 (canonical 생성기는 column-0만 씀).
    body = "## 실무 체크리스트\n- 상위 항목\n  - 하위 설명\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- [ ] 상위 항목" in out
    assert "  - 하위 설명" in out


# --- transform(): composition, lossless invariant, order --------------------

_DEFECTIVE = (
    "## 1. 보안 뉴스\n"
    "### 1.1 어떤 기사\n"
    "# DevSecOps 관점 분석: 리눅스 익스플로잇\n"
    "본문 문단.\n"
    "#### 대응 체크리스트\n"
    "- [ ] 패치 적용\n"
    "- [x] 로그 점검\n"
    "## 5. AI/ML 뉴스\n"
    "### 5.1 다른 기사\n"
    "## 기술적 배경\n"
    "설명.\n"
    "## 9. 실무 체크리스트\n"
    "- [ ] 전역 항목\n"
)


def test_transform_is_lossless_on_token_multiset():
    """핵심 불변식: 마크다운 마커를 제거한 뒤 토큰 다중집합이 동일해야 한다.

    숫자 토큰은 R4/R5가 의도적으로 바꾸므로 제외한다. 이 검사가 '삭제 금지'를
    규칙이 아니라 테스트로 강제한다 (5·6월 proper-noun 파티션의 토큰 감사 기법).
    """
    before = lossless_tokens(_FM + _DEFECTIVE)
    after = lossless_tokens(transform(_FM + _DEFECTIVE))
    assert before == after, f"lost/added: {before - after} / {after - before}"


def test_transform_resolves_all_four_kinds():
    out = transform(_FM + _DEFECTIVE)
    assert "#### DevSecOps 관점 분석: 리눅스 익스플로잇" in out  # H1 demoted
    assert "#### 대응 체크리스트" not in out and "**대응 체크리스트**" in out
    assert "## 2. AI/ML 뉴스" in out  # renumbered
    assert "## 실무 체크리스트" in out  # number removed
    assert "- [ ] 전역 항목" in out  # global box kept


def test_transform_is_idempotent():
    once = transform(_FM + _DEFECTIVE)
    assert transform(once) == once


# --- lossless_tokens: marker-context sensitivity -----------------------------
#
# The multiset alone is marker-blind: `_MARKER_RE` erases heading/bullet markers
# everywhere, so a marker MIS-conversion inside a code fence ('# 예시' ->
# '#### 예시', the R0 defect of PR #500) leaves the token multiset identical and
# the invariant passes while the post is corrupted. And the numeric exclusion was
# global, so deleting a standalone number from a table was invisible too.
# Markers may legitimately change ONLY outside fences; numbers may legitimately
# change ONLY in a heading's leading 'N.' slot (R4/R5).


def test_fence_interior_heading_marker_change_is_caught():
    orig = _FM + "```bash\n# 예시 주석\n```\n"
    damaged = _FM + "```bash\n#### 예시 주석\n```\n"
    assert lossless_tokens(orig) != lossless_tokens(damaged)


def test_fence_interior_bullet_marker_change_is_caught():
    orig = _FM + "```\n- item\n```\n"
    damaged = _FM + "```\n- [ ] item\n```\n"
    assert lossless_tokens(orig) != lossless_tokens(damaged)


def test_fence_interior_text_change_is_still_caught():
    orig = _FM + "```\n# 예시 주석\n```\n"
    damaged = _FM + "```\n# 다른 주석\n```\n"
    assert lossless_tokens(orig) != lossless_tokens(damaged)


def test_standalone_number_deletion_outside_headings_is_caught():
    orig = _FM + "| 항목 | 3 |\n"
    damaged = _FM + "| 항목 | |\n"
    assert lossless_tokens(orig) != lossless_tokens(damaged)


@pytest.mark.parametrize(
    "orig,new",
    [
        ("### 제목\n", "#### 제목\n"),                       # R1 demote
        ("### 대응 체크리스트\n", "**대응 체크리스트**\n"),   # R2 boldify
        ("- [ ] 조치\n", "- 조치\n"),                         # R3 unbox
        ("- 조치\n", "- [ ] 조치\n"),                         # R6 checkbox
        ("## 9. 보안\n", "## 3. 보안\n"),                     # R4 renumber
        ("## 9. 실무 체크리스트\n", "## 실무 체크리스트\n"),  # R5 unnumber
        ("## 9. 보안\n", "#### 9. 보안\n"),                   # R5-then-R1 demote
    ],
)
def test_intended_rule_effects_do_not_trip_the_invariant(orig, new):
    assert lossless_tokens(_FM + orig) == lossless_tokens(_FM + new)


@pytest.mark.parametrize(
    "line",
    [
        "### 9.1 항목\n",       # item sub-number is not the heading number slot
        "발행 2026 년\n",       # prose number
        "| 건수 | 12 |\n",      # table number
    ],
)
def test_unchanged_content_never_trips_the_invariant(line):
    assert lossless_tokens(_FM + line) == lossless_tokens(_FM + line)


def test_invariant_backstops_an_r0_regression(monkeypatch, tmp_path, capsys):
    """If fence protection regresses, the invariant must ABORT — not write.

    This is the PR #500 defect replayed: with R0 disabled, R1 demotes the bash
    comment inside the fence. Before the tightening the multiset still matched
    and the file was written corrupted.
    """
    import restore_digest_structure as mod

    post = tmp_path / "2026-08-06-Tech_Blog_Weekly_Digest_x.md"
    post.write_text(
        _FM
        + "## 1. 보안\n\n### 1.1 기사\n\n```bash\n# 예시 주석\necho hi\n```\n\n"
        "## 실무 체크리스트\n\n- [ ] 조치\n",
        encoding="utf-8",
    )
    original = post.read_text(encoding="utf-8")

    monkeypatch.setattr(mod, "_fence_flags", lambda lines: [False] * len(lines))
    rc = mod.main([str(post)])

    assert rc == 1, "a fence-interior marker rewrite must abort"
    assert "lossless invariant violated" in capsys.readouterr().err
    assert post.read_text(encoding="utf-8") == original, "must not write on abort"


def test_audit_fence_flags_agree_with_rule_flags():
    """The two detectors are separate on purpose — they must not DRIFT.

    Disagreement would abort real posts (false positive), so this pins them to
    the corpus while keeping the audit independent of `_fence_flags` edits.
    """
    import pathlib

    import restore_digest_structure as mod

    repo = pathlib.Path(__file__).resolve().parent.parent.parent
    disagreeing = []
    for p in sorted((repo / "_posts").glob("*Weekly_Digest*.md")):
        lines = p.read_text(encoding="utf-8").split("\n")
        if mod._audit_fence_flags(lines) != mod._fence_flags(lines):
            disagreeing.append(p.name)
    assert disagreeing == [], disagreeing


def test_corpus_transform_stays_lossless_under_the_tightened_invariant():
    """Every digest must still pass — the tightening must not abort real posts."""
    import pathlib

    repo = pathlib.Path(__file__).resolve().parent.parent.parent
    offenders = []
    for p in sorted((repo / "_posts").glob("*Weekly_Digest*.md")):
        t = p.read_text(encoding="utf-8")
        if lossless_tokens(t) != lossless_tokens(transform(t)):
            offenders.append(p.name)
    assert offenders == [], offenders


def test_r1_and_r2_are_order_independent():
    # _RESP_HEADING_RE 가 '#{1,4}' 를 포괄하므로 R1이 '####'로 강등한 뒤든 전이든
    # R2가 잡는다. 둘 사이에는 순서 제약이 없다.
    body = _FM + "## 1. 보안 뉴스\n### 1.1 기사\n## 대응 체크리스트\n- 항목\n"
    assert boldify_response_checklist(demote_item_headings(body)) == demote_item_headings(
        boldify_response_checklist(body)
    )
    assert "**대응 체크리스트**" in transform(body)


def test_order_matters_r5_before_r1():
    """R5가 R1보다 먼저여야 한다 — 티어 C 6개가 이 케이스다.

    TOP_SECTION_RE 는 번호 없는 '## 실무 체크리스트'만 섹션으로 인식한다. 번호형이
    남아 있는 동안 R1은 그것을 item 바디로 보고 '#### 9. 실무 체크리스트'로 강등하며,
    그 뒤에는 R5('^##' 앵커)가 매칭하지 못해 'found 0' 결함이 그대로 남는다.
    """
    body = _FM + "## 1. 보안 뉴스\n### 1.1 기사\n본문.\n## 9. 실무 체크리스트\n- [ ] 항목\n"
    wrong = canonicalize_checklist_heading(demote_item_headings(body))
    assert "#### 9. 실무 체크리스트" in wrong  # 잘못된 순서의 증거
    assert "## 실무 체크리스트" not in wrong
    assert "## 실무 체크리스트" in transform(body)  # 올바른 순서


def test_order_matters_r5_before_r4():
    """R5가 R4보다 먼저여야 한다 — 아니면 체크리스트가 섹션 index를 소비한다.

    R4를 먼저 돌리면 [1, 2(체크리스트), 3] 이 되고, R5가 체크리스트 번호를 떼면
    남은 시퀀스가 [1, 3] 으로 여전히 파손이다.
    """
    body = _FM + "## 1. 보안 뉴스\n## 3. 실무 체크리스트\n## 7. AI/ML 뉴스\n"
    wrong = canonicalize_checklist_heading(renumber_sections(body))
    assert "## 3. AI/ML 뉴스" in wrong  # [1, 3] — 잘못된 순서의 증거
    assert "## 2. AI/ML 뉴스" in transform(body)  # [1, 2] — 연속


# --- CLI --------------------------------------------------------------------


def test_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-01-01-X_Weekly_Digest.md"
    p.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    original = p.read_text(encoding="utf-8")
    assert main(["--dry-run", str(p)]) == 0
    assert p.read_text(encoding="utf-8") == original


def test_apply_writes_and_skips_non_digest(tmp_path):
    d = tmp_path / "2026-01-01-X_Weekly_Digest.md"
    d.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    other = tmp_path / "2026-01-01-Regular_Post.md"
    other.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    assert main([str(d), str(other)]) == 0
    assert "**대응 체크리스트**" in d.read_text(encoding="utf-8")
    assert other.read_text(encoding="utf-8") == _FM + _DEFECTIVE  # 스코프 밖


# --- drift guard for the copied shared regexes ------------------------------


def test_shared_regexes_have_not_drifted():
    """ITEM_HEADING_RE / TOP_SECTION_RE 는 backfill_digest_structure.transform_body
    에서 복사했다. 그쪽은 function-local이라 import가 불가하므로 소스를 스캔해
    두 정의가 갈라지면 실패시킨다. 갈라지면 두 경로가 서로 다른 '섹션'을 인식해
    강등 범위가 조용히 달라진다.
    """
    src = (
        Path(__file__).resolve().parents[1] / "backfill_digest_structure.py"
    ).read_text(encoding="utf-8")
    assert r'r"^### \d+\.\d+"' in src, (
        "backfill_digest_structure.py 의 item-heading 정규식이 바뀌었다. "
        "restore_digest_structure.ITEM_HEADING_RE 를 맞춰 갱신하라."
    )
    for member in (
        "보안",
        "AI/ML",
        "클라우드",
        "DevOps",
        "블록체인",
        "기타",
        "트렌드",
        "GeekNews",
        "Open Source",
        "## 실무 체크리스트",
        "## 서론",
        "## 분석가 시점",
        "## 경영진 브리핑",
        "## 위험 스코어카드",
        "## 참고 자료",
        "## 📊",
    ):
        assert member in src, (
            f"backfill_digest_structure.py 의 섹션 whitelist 에서 {member!r} 가 "
            "사라졌다. restore_digest_structure.TOP_SECTION_RE 를 맞춰 갱신하라."
        )
        assert member in TOP_SECTION_RE.pattern, (
            f"TOP_SECTION_RE 에 {member!r} 가 없다 — backfill 쪽과 불일치."
        )


# --- R0: code-fence protection ---------------------------------------------
# Empirically required: without it R1 rewrote bash/yaml/python comments
# ('# 예시' -> '#### 예시') inside fenced blocks of 2026-03-11 and 2026-03-27
# during the tier-B/C batches. check_digest_structure._strip_code_fences already
# ignores fence interiors, so the transformer must too — otherwise it edits code
# the gate never asked about.

_FENCED_ITEM = (
    "## 1. 보안 뉴스\n"
    "### 1.1 기사\n"
    "```bash\n"
    "# 현재 인터넷 노출 자산 목록 추출 예시\n"
    "curl -s https://example.invalid/api\n"
    "```\n"
    "본문.\n"
)


def test_r1_does_not_demote_comments_inside_a_code_fence():
    out = demote_item_headings(_FM + _FENCED_ITEM)
    assert "# 현재 인터넷 노출 자산 목록 추출 예시" in out
    assert "#### 현재 인터넷 노출 자산 목록 추출 예시" not in out


def test_r2_does_not_boldify_inside_a_code_fence():
    body = "### 1.1 기사\n```markdown\n## 대응 체크리스트\n```\n"
    out = boldify_response_checklist(_FM + body)
    assert "## 대응 체크리스트" in out
    assert "**대응 체크리스트**" not in out


def test_r3_does_not_unbox_inside_a_code_fence():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n```markdown\n- [ ] 예시 항목\n```\n"
    out = unbox_item_checkboxes(_FM + body)
    assert "- [ ] 예시 항목" in out


def test_r4_does_not_renumber_inside_a_code_fence():
    body = "## 1. 보안 뉴스\n```markdown\n## 7. 예시 섹션\n```\n## 5. AI/ML 뉴스\n"
    out = renumber_sections(_FM + body)
    assert "## 7. 예시 섹션" in out   # example content untouched
    assert "## 2. AI/ML 뉴스" in out  # real section still renumbered


def test_r5_does_not_canonicalize_inside_a_code_fence():
    body = "```markdown\n## 9. 실무 체크리스트\n```\n"
    out = canonicalize_checklist_heading(_FM + body)
    assert "## 9. 실무 체크리스트" in out


def test_r6_does_not_box_bullets_inside_a_code_fence():
    body = "## 실무 체크리스트\n```bash\n- 예시 불릿\n```\n- 실제 항목\n"
    out = checkbox_global_checklist(_FM + body)
    assert "- 예시 불릿" in out
    assert "- [ ] 예시 불릿" not in out
    assert "- [ ] 실제 항목" in out


def test_indented_closing_fence_closes_the_block():
    """2026-02-08 uses '  ```' to close. The gate toggles on the STRIPPED line,
    so the transformer must too — otherwise the fence never closes and the rest
    of the post is silently treated as code and left untransformed.
    """
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 기사\n"
        "```bash\n"
        "  # 예시 주석\n"
        "  ```\n"
        "# 실제 H1\n"
    )
    out = demote_item_headings(_FM + body)
    assert "  # 예시 주석" in out       # inside the fence: verbatim
    assert "#### 실제 H1" in out        # after the indented closer: transformed


def test_transform_leaves_fenced_blocks_byte_identical():
    fenced = (
        "```python\n"
        "# GuardDuty 고위험 결과 자동 대응 Lambda 예시\n"
        "def handler(event, context):\n"
        "    return {'ok': True}\n"
        "```\n"
    )
    out = transform(_FM + "## 1. 보안 뉴스\n### 1.1 기사\n" + fenced)
    assert fenced in out

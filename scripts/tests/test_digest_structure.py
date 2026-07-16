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
    # NOTE: a raw `"### 제목" not in out` substring check is impossible to
    # satisfy here — "#### 제목" always contains "### 제목" as a substring
    # (drop the leading "#"). Check heading-line prefix instead, matching
    # the intent (no colliding "### " heading line survives).
    assert not out.startswith("### ")
    assert "\n### " not in out


def test_non_heading_lines_unchanged():
    src = "일반 문단\n- [ ] 체크박스\n> 인용\n"
    assert _normalize_deep_analysis(src) == src


def test_hash_in_prose_not_treated_as_heading():
    # a line that only starts with '#' at column 0 followed by space is a heading
    src = "C# 언어에 대한 설명\n"
    assert _normalize_deep_analysis(src) == src


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



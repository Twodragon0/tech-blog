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
    # Long enough to clear the module's own >=120-char floor (_MIN_OUTPUT_CHARS)
    # while still asserting the same "grounded, no-fabrication" behavior.
    fake_reply = (
        "#### 기술적 배경\n"
        "실제 근거 기반 내용을 원문에서 확인된 사실만 사용해 정리한 상세 분석 문단이다. "
        "추측이나 원문에 없는 수치는 포함하지 않는다.\n\n"
        "#### 실무 영향\n"
        "원문 근거만으로 실무 대응 관점의 시사점을 서술한다."
    )
    def fake(prompt, timeout=35):
        captured["p"] = prompt
        return fake_reply
    out = summary_expander.expand_summary(
        {"title": "제로데이", "url": "https://x"}, "ARTICLE BODY EVIDENCE " * 20, gemini=fake)
    assert out and "실제 근거" in out
    assert "ARTICLE BODY EVIDENCE" in captured["p"]      # source is grounded in
    assert ("추가하지" in captured["p"]) or ("없는" in captured["p"])  # no-fabrication instruction


def test_returns_none_when_no_article_text():
    out = summary_expander.expand_summary({"title": "t", "url": "u"}, "",
                                          gemini=lambda p, timeout=35: "x")
    assert out is None

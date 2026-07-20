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

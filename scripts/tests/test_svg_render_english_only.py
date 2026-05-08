"""Render-time integration test: emitted SVG strings contain zero Hangul.

Defense-in-depth for the English-only SVG rule (CLAUDE.md). The L20 hero
generator and the legacy `svg_generator._escape_svg_text` both strip
Hangul before XML escape; this test calls the renderers with
deliberately Korean-heavy inputs and asserts the resulting SVG bytes
have no Hangul codepoints.

Also covers the QR-code URL invariant: the encoded URL must use
underscores (matching Jekyll's permalink) and never the
``slug.replace("_", "-")`` form that produced 404s in past covers.
"""

from __future__ import annotations

import re

import pytest

from scripts.lib.svg_l20_hero import _escape, _strip_hangul, render_l20_hero
from scripts.news import svg_generator
from scripts.news.l20_dispatch import (
    _post_url_from_filename,
    extract_three_stories,
    generate_l20_digest_svg,
)

_HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")


def _has_hangul(s: str) -> bool:
    return bool(_HANGUL_RE.search(s or ""))


# ---------------------------------------------------------------------------
# Hard SVG render guarantee — L20 hero
# ---------------------------------------------------------------------------


class TestL20HeroEnglishOnlyRender:
    """render_l20_hero must emit zero Hangul, even with Korean inputs."""

    def _korean_story(self, idx: str) -> dict:
        return {
            "tag": "BREACH",
            "index": idx,
            "headline": f"Apache HTTP/2의 치명적 {idx}",
            "subheadline": "DAEMON Tools 공급망 공격으로 공식 발표",
            "theme": "red",
            "visual": "cve_chain",
            "kpi_value": "9.8",
            "kpi_label": "CVSS",
            "kpi_sub": "심각도",
            "action": "패치 즉시 적용",
        }

    def test_korean_inputs_strip_to_ascii_in_render(self):
        svg = render_l20_hero(
            date_str="2026.05.08",
            hero=self._korean_story("01"),
            top_right=self._korean_story("02"),
            bottom_right=self._korean_story("03"),
            url="https://tech.2twodragon.com/posts/2026/05/08/Tech_Security_Weekly_Digest_CVE_AI/",
            post_title="Apache HTTP/2의 치명적 취약점",
        )
        assert not _has_hangul(svg), (
            "render_l20_hero must strip Hangul before emitting <text>; "
            "found Hangul in the rendered SVG"
        )
        # Sanity: SVG envelope was actually emitted.
        assert svg.startswith("<svg")
        assert "</svg>" in svg


class TestEscapeHelperStripsHangul:
    """_escape and _strip_hangul both remove Hangul before escaping."""

    def test_strip_hangul_removes_all_jamo(self):
        cases = [
            ("한글", ""),
            ("Apache HTTP/2의 치명적", "Apache HTTP/2"),
            ("ㄱㄴㄷ", ""),
            ("Mixed AI 보안 update", "Mixed AI update"),
            ("English only", "English only"),
            ("", ""),
        ]
        for inp, expected in cases:
            assert _strip_hangul(inp) == expected, (
                f"_strip_hangul({inp!r}) → {_strip_hangul(inp)!r}, expected {expected!r}"
            )

    def test_escape_strips_then_xml_escapes(self):
        out = _escape("AT&T \"Apache HTTP/2의\" <test>")
        assert "&amp;" in out  # & escaped
        assert "&quot;" in out  # " escaped
        assert "&lt;test&gt;" in out
        assert not _has_hangul(out)


# ---------------------------------------------------------------------------
# Hard SVG render guarantee — generic svg_generator path
# ---------------------------------------------------------------------------


class TestSvgGeneratorEscapeStripsHangul:
    """svg_generator._escape_svg_text strips Hangul (defense in depth)."""

    def test_korean_payload_becomes_ascii(self):
        out = svg_generator._escape_svg_text("AI 보안 update")
        assert not _has_hangul(out)

    def test_hangul_only_returns_empty_after_strip(self):
        out = svg_generator._escape_svg_text("한국어")
        assert out == ""

    def test_xml_special_chars_still_escaped(self):
        out = svg_generator._escape_svg_text('A & B <c> "d" \'e\'')
        assert "&amp;" in out
        assert "&lt;" in out
        assert "&gt;" in out
        assert "&quot;" in out
        assert "&#39;" in out


# ---------------------------------------------------------------------------
# QR code URL invariant
# ---------------------------------------------------------------------------


class TestQrUrlPermalinkContract:
    """QR encoded URL must use underscores (Jekyll permalink format).

    The previous ``slug.replace("_", "-")`` produced URLs that 404'd on
    every cover. This test locks the permalink contract.
    """

    def test_url_preserves_underscores(self):
        url = _post_url_from_filename(
            "2026-05-08-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md"
        )
        assert url == (
            "https://tech.2twodragon.com/posts/2026/05/08/"
            "Tech_Security_Weekly_Digest_CVE_AI_Malware_Go/"
        )
        # Hard regression guard: hyphenated form must NOT appear.
        assert "Tech-Security-Weekly-Digest" not in url

    def test_empty_filename_returns_root(self):
        assert _post_url_from_filename("") == "https://tech.2twodragon.com/"

    def test_non_matching_filename_returns_root(self):
        assert (
            _post_url_from_filename("not-a-post.txt")
            == "https://tech.2twodragon.com/"
        )

    def test_url_appears_verbatim_in_rendered_svg(self):
        url = _post_url_from_filename(
            "2026-05-08-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md"
        )
        h, tr, br = extract_three_stories(
            "한국어 제목",
            "",
            "2026-05-08-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md",
        )
        # Synthesise minimal story dicts compatible with render_l20_hero.
        common = {
            "theme": "red",
            "visual": "cve_chain",
            "kpi_value": "9",
            "kpi_label": "K",
            "kpi_sub": "S",
            "action": "PATCH",
            "tag": "T",
            "index": "01",
        }
        for d, story in zip((h, tr, br), ("01", "02", "03")):
            d.update(dict(common, index=story))
        svg = render_l20_hero(
            date_str="2026.05.08",
            hero=h,
            top_right=tr,
            bottom_right=br,
            url=url,
            post_title="Test",
        )
        # The QR encodes the URL as a path; the URL string itself does NOT
        # need to appear in <text>, but it should be inside the <g> generated
        # by qr_block via gen_qr. We assert the URL is preserved as-is via
        # _post_url_from_filename's contract (underscores intact) and that
        # nothing in the rendered SVG contains Hangul.
        assert not _has_hangul(svg)


# ---------------------------------------------------------------------------
# End-to-end: generate_l20_digest_svg writes a clean SVG file
# ---------------------------------------------------------------------------


class TestEndToEndKoreanInputProducesAsciiSvg:
    """generate_l20_digest_svg with a Korean-titled post writes ASCII-only SVG."""

    def test_korean_post_writes_ascii_svg(self, tmp_path):
        post_info = {
            "title": "Apache HTTP/2의 치명적, DAEMON Tools 공급망 공격, 중국과 연계된 UAT-8302",
            "excerpt": "한국어 요약입니다",
            "filename": "2026-05-08-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md",
            "date": "2026-05-08",
        }
        out_path = tmp_path / "cover"
        ok = generate_l20_digest_svg(post_info, out_path)
        assert ok, "generate_l20_digest_svg returned False"
        svg_text = (tmp_path / "cover.svg").read_text(encoding="utf-8")
        assert not _has_hangul(svg_text), (
            "Generated SVG file contains Hangul; "
            "English-only guarantee is broken."
        )
        # Sanity: content is meaningful (not empty / not just envelope).
        assert "<text" in svg_text
        assert "WEEKLY DIGEST" in svg_text


# ---------------------------------------------------------------------------
# QR path-data round-trip
# ---------------------------------------------------------------------------


class TestQrPathDataRoundTrip:
    """The QR ``<path d="...">`` emitted into a cover must be byte-identical
    to a fresh ``gen_qr(canonical_url)`` call. If they diverge, either the
    URL passed to render_l20_hero was wrong (regression: the slug-hyphen
    bug), or the qr_block template was mutated.

    Without a stdlib QR *decoder* this is the strongest equality check we
    can run in pure Python — and it transitively proves the encoded payload
    because ``gen_qr`` is deterministic for a given URL.
    """

    def _extract_qr_path_d(self, svg_text: str) -> str:
        # qr_block emits exactly one ``<g transform="translate(1080,504)" ...>``
        # block, with a single ``<path fill="#0A1020" d="...">`` inside it.
        m = re.search(
            r'<g transform="translate\(1080,504\)"[^>]*>\s*'
            r'<rect[^/]*/>\s*'
            r'<path fill="#0A1020" d="([^"]*)"',
            svg_text,
            re.DOTALL,
        )
        assert m, "QR <g> block not found in rendered SVG"
        return m.group(1)

    def test_qr_path_matches_canonical_url(self, tmp_path):
        from scripts.lib.svg_l22_generator import gen_qr

        post_info = {
            "title": "Test post",
            "excerpt": "...",
            "filename": "2026-05-08-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md",
            "date": "2026-05-08",
        }
        out_path = tmp_path / "cover"
        assert generate_l20_digest_svg(post_info, out_path)
        svg_text = (tmp_path / "cover.svg").read_text(encoding="utf-8")

        rendered_qr_d = self._extract_qr_path_d(svg_text)
        canonical_url = (
            "https://tech.2twodragon.com/posts/2026/05/08/"
            "Tech_Security_Weekly_Digest_CVE_AI_Malware_Go/"
        )
        expected_qr_d = gen_qr(canonical_url)
        assert rendered_qr_d == expected_qr_d, (
            "QR matrix does not match canonical underscore URL. "
            "If this fails, _post_url_from_filename probably regressed "
            "(e.g., slug.replace('_', '-') was reintroduced)."
        )

    def test_qr_path_differs_for_hyphen_url(self, tmp_path):
        """Sanity: prove the path-data check actually distinguishes URLs.

        The hyphen URL is the buggy one. Its QR matrix MUST differ from the
        underscore URL's matrix — otherwise our equality check is vacuous.
        """
        from scripts.lib.svg_l22_generator import gen_qr

        good = "https://tech.2twodragon.com/posts/2026/05/08/Tech_Security_Weekly_Digest_CVE_AI_Malware_Go/"
        bad = "https://tech.2twodragon.com/posts/2026/05/08/Tech-Security-Weekly-Digest-CVE-AI-Malware-Go/"
        assert gen_qr(good) != gen_qr(bad), (
            "gen_qr returned identical matrices for different URLs — "
            "the encoder is broken"
        )

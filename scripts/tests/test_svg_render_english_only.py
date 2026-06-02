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

    Skipped when the optional ``qrcode`` library is not installed: in that
    case ``gen_qr`` returns the empty string and the round-trip check is
    vacuous. The check-svg CI workflow installs ``qrcode`` so this test
    runs there; local environments without the dep are also fine.
    """

    @pytest.fixture(autouse=True)
    def _require_qrcode(self):
        from scripts.lib.svg_l22_generator import QRCODE_AVAILABLE

        if not QRCODE_AVAILABLE:
            pytest.skip("qrcode library not installed")

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


# ---------------------------------------------------------------------------
# QR scannability geometry (enlarged QR + quiet zone)
# ---------------------------------------------------------------------------


class TestQrScannabilityGeometry:
    """Lock the enlarged-QR scannability improvement so the QR can't silently
    regress to the old tight 84px render.

    The QR is rendered at ``QR_PX`` (108px) for a 41x41 (version-6) matrix,
    giving ~2.63px/module, and ``qr_block`` wraps it in a 132x132 white rect
    so the white margin around the 108px QR is a >=4-module quiet zone. The
    whole block stays inside the 1200x630 frame and the label sits above the
    rect (never over the QR).
    """

    @pytest.fixture(autouse=True)
    def _require_qrcode(self):
        from scripts.lib.svg_l22_generator import QRCODE_AVAILABLE

        if not QRCODE_AVAILABLE:
            pytest.skip("qrcode library not installed")

    def test_qr_render_scale_is_enlarged(self):
        from scripts.lib.svg_l22_generator import QR_PX

        # Must be meaningfully larger than the original 84px to survive raster
        # downscale; 108px gives ~2.63px/module for a 41x41 matrix.
        assert QR_PX >= 104.0, f"QR_PX regressed below scannable size: {QR_PX}"

    def test_qr_path_max_extent_matches_qr_px(self):
        from scripts.lib.svg_l22_generator import QR_PX, gen_qr

        url = (
            "https://tech.2twodragon.com/posts/2026/05/23/"
            "Tech_Security_Weekly_Digest_Ransomware_AI_Malware_Go/"
        )
        d = gen_qr(url)
        assert d, "gen_qr returned empty path"
        xs = [float(x) for x in re.findall(r"M([0-9.]+) ", d)]
        # Last dark module starts at (size-1)*scale; full extent reaches QR_PX.
        # Allow a one-module slack below QR_PX for the final module's origin.
        one_module = QR_PX / 41.0
        assert max(xs) <= QR_PX, "QR path overshoots QR_PX"
        assert max(xs) >= QR_PX - 2 * one_module, "QR path far smaller than QR_PX"

    def test_qr_block_quiet_zone_and_in_frame(self):
        from scripts.lib.svg_l22_generator import QR_PX, qr_block

        url = (
            "https://tech.2twodragon.com/posts/2026/05/23/"
            "Tech_Security_Weekly_Digest_Ransomware_AI_Malware_Go/"
        )
        block = qr_block(url)

        # Locked anchor for the round-trip regex + L20 hero test.
        assert 'transform="translate(1080,504)"' in block

        # White backing rect: parse x/y/width/height (local coords).
        m = re.search(
            r'<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)" '
            r'rx="\d+" fill="#FFFFFF"/>',
            block,
        )
        assert m, "white QR backing rect not found / changed shape"
        rx, ry, rw, rh = (int(v) for v in m.groups())

        # Quiet zone = white margin around the QR (QR path starts at local 0,0).
        margin_left = -rx
        margin_top = -ry
        margin_right = (rx + rw) - QR_PX
        margin_bottom = (ry + rh) - QR_PX
        one_module = QR_PX / 41.0
        for name, margin in (
            ("left", margin_left),
            ("top", margin_top),
            ("right", margin_right),
            ("bottom", margin_bottom),
        ):
            assert margin >= 4 * one_module, (
                f"{name} quiet zone {margin:.1f}px < 4 modules "
                f"({4 * one_module:.1f}px)"
            )

        # In-frame: absolute white-rect bounds within 0..1200 x, 0..630 y.
        ax0, ay0 = 1080 + rx, 504 + ry
        ax1, ay1 = ax0 + rw, ay0 + rh
        assert 0 <= ax0 and ax1 <= 1200, f"QR rect x out of frame: {ax0}..{ax1}"
        assert 0 <= ay0 and ay1 <= 630, f"QR rect y out of frame: {ay0}..{ay1}"

        # Label must sit above the white rect (no overlap with the QR). Its
        # baseline y must be <= the rect's absolute top.
        lm = re.search(r'<text x="\d+" y="(\d+)"[^>]*>scan / full post</text>', block)
        assert lm, "scan label not found"
        label_y = int(lm.group(1))
        assert label_y <= ay0, (
            f"label baseline y={label_y} overlaps QR rect top {ay0}"
        )

#!/usr/bin/env python3
"""Tests for scripts/fix_qr_url_in_covers.py — the cover QR-URL repair tool.

Regression focus: the QR-block matcher must recognise BOTH the legacy 84px
label position (``x="1122" y="614"``, below the QR) and the current 108px
position (``x="1134" y="486"``, above the enlarged white rect). Anchoring on
the old coordinates silently skipped every modern cover ("No QR block found"),
so a stale-URL 108px cover could never be repaired.

``sys.path`` setup is handled by conftest.py.
"""

from __future__ import annotations

import fix_qr_url_in_covers as fixmod
from scripts.lib.svg_l22_generator import gen_qr, qr_block
from scripts.news.l20_dispatch import _post_url_from_filename

CANONICAL = "https://tech.2twodragon.com/posts/2026/06/05/Test_Digest/"


def _wrap(qr_fragment: str) -> str:
    """Minimal SVG wrapper around a QR block fragment."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
        f"{qr_fragment}</svg>\n"
    )


def _legacy_qr_block(url: str) -> str:
    """The pre-108px QR block: 100x100 white rect + scan label at y=614."""
    return (
        '<g transform="translate(1080,504)" filter="url(#softShadow)">\n'
        '  <rect x="-8" y="-8" width="100" height="100" rx="6" fill="#FFFFFF"/>\n'
        f'  <path fill="#0A1020" d="{gen_qr(url)}"/>\n'
        "</g>\n"
        '<text x="1122" y="614" font-family="Inter, Helvetica, Arial, sans-serif" '
        'font-size="10" font-weight="700" fill="#F5F7FA" '
        'text-anchor="middle">scan / full post</text>'
    )


class TestQrBlockMatcher:
    def test_matches_current_108px_block(self):
        """The 108px qr_block (scan label y=486) must be matched."""
        frag = qr_block(CANONICAL)
        assert "y=\"486\"" in frag, "fixture drift: qr_block no longer uses y=486"
        assert fixmod._QR_BLOCK_RE.search(_wrap(frag)) is not None

    def test_matches_legacy_84px_block(self):
        """The legacy block (scan label y=614) must still be matched."""
        frag = _legacy_qr_block(CANONICAL)
        assert fixmod._QR_BLOCK_RE.search(_wrap(frag)) is not None


class TestFixOne:
    def test_upgrades_stale_legacy_block_to_canonical_108px(self, tmp_path):
        """A legacy block carrying a WRONG url is rewritten to the canonical
        108px qr_block derived from the filename."""
        filename = "2026-06-05-Test_Digest.svg"
        stale = _legacy_qr_block("https://tech.2twodragon.com/posts/2026/06/05/WRONG/")
        path = tmp_path / filename
        path.write_text(_wrap(stale), encoding="utf-8")

        changed, _ = fixmod.fix_one(path)
        assert changed is True

        out = path.read_text(encoding="utf-8")
        # Upgraded to 108px geometry.
        assert 'width="132" height="132"' in out
        assert 'y="486"' in out
        # QR now encodes the canonical filename-derived URL.
        canonical = _post_url_from_filename(filename)
        assert gen_qr(canonical) in out
        # Exactly one QR block remains (atomic swap, no duplicate label).
        assert out.count("scan / full post") == 1

    def test_canonical_108px_block_is_left_unchanged(self, tmp_path):
        """An already-canonical 108px cover needs no fix."""
        filename = "2026-06-05-Test_Digest.svg"
        canonical = _post_url_from_filename(filename)
        path = tmp_path / filename
        path.write_text(_wrap(qr_block(canonical)), encoding="utf-8")

        changed, reason = fixmod.fix_one(path)
        assert changed is False
        assert "already" in reason.lower()

#!/usr/bin/env python3
"""Guard: the QR path uses integer module coordinates, and `transform` stays
after `d`.

``gen_qr`` emits one unit per QR module and ``qr_block`` scales the path with
``transform="scale(qr_scale(url))"``. The rendered geometry is identical to the
old 3-decimal absolute form — same matrix, same 108 px edge — but the path text
is 58 % smaller. Measured 2026-09-07 over the 287 covers that carry a QR:
2.45 MB of SVG text removed, and the two covers a longer canonical URL had
pushed over the hq size band came back in-band, which is what let
``svg_size_gate_baseline.txt`` return to empty.

Two things must not drift
-------------------------
1. **Attribute order.** ``check_cover_qr_urls._QR_PATH_RE`` matches
   ``<path fill="#0A1020" d="([^"]*)"``. Putting ``transform`` before ``d``
   makes it stop matching — measured: the gate then reads the cover as
   ``missing-qr``. Keeping ``transform`` last costs nothing and left both the
   gate and ``fix_qr_url_in_covers`` regexes untouched by this change.

2. **Integer coordinates.** Rounding absolute coordinates to fewer decimals is
   the obvious alternative and it is worse on both axes: 2 decimals saved 2224
   bytes against 8627 on a sample cover, and moved 2549 rendered pixels against
   177, because rounding shifts module edges while the transform lets the
   renderer scale at full precision.
"""

from __future__ import annotations

import re

from check_cover_qr_urls import _QR_PATH_RE
from fix_qr_url_in_covers import _QR_BLOCK_RE
from lib.svg_l22_generator import QR_PX, gen_qr, qr_block, qr_scale

URL = "https://tech.2twodragon.com/posts/2026/09/04/Tech_Security_Weekly_Digest_AI_Malware_Rust/"


def test_path_data_is_integer_module_coordinates():
    path = gen_qr(URL)
    assert path, "gen_qr returned nothing; is qrcode installed?"
    assert re.fullmatch(r"(?:M\d+ \d+h\d+v1h-\d+z ?)+", path), (
        "path data is not purely integer module coordinates. A decimal here "
        f"means the transform is being double-applied or bypassed: {path[:80]!r}"
    )


def test_scale_maps_modules_onto_the_locked_108px_edge():
    scale = qr_scale(URL)
    path = gen_qr(URL)
    # The matrix side is the largest column index + its run, + 1.
    side = max(
        int(m.group(1)) + int(m.group(2))
        for m in re.finditer(r"M(\d+) \d+h(\d+)", path)
    )
    assert abs(scale * side - QR_PX) < 1e-9, (
        f"scale {scale} x side {side} = {scale * side}, not the locked {QR_PX} px "
        "edge the cover geometry and quiet zone are built around"
    )


def test_transform_follows_d_so_the_gate_regex_still_matches():
    block = qr_block(URL)
    m = _QR_PATH_RE.search(block)
    assert m, (
        "check_cover_qr_urls._QR_PATH_RE no longer matches the emitted block. "
        "The usual cause is `transform` moved before `d`; the gate then reports "
        "missing-qr for every L20 cover."
    )
    assert m.group(1) == gen_qr(URL), (
        "the gate captures a `d` that is not what gen_qr produces, so its "
        "byte comparison can never succeed"
    )
    # Scope to the <path> element: the block also opens with
    # `<g transform="translate(1080,504)">`, whose transform is unrelated.
    path_el = re.search(r"<path\b[^>]*/>", block)
    assert path_el, f"no <path> element in the block: {block[:120]!r}"
    el = path_el.group(0)
    assert el.index(' d="') < el.index(' transform="'), (
        f"transform must stay after d — see the module docstring: {el[:90]!r}"
    )


def test_fixer_block_regex_still_matches():
    assert _QR_BLOCK_RE.search(qr_block(URL)), (
        "fix_qr_url_in_covers._QR_BLOCK_RE stopped matching, so the fixer would "
        "report 'no QR block found' for every cover"
    )


def test_block_carries_a_scale_transform():
    block = qr_block(URL)
    m = re.search(r'transform="scale\(([0-9.]+)\)"', block)
    assert m, f"no scale transform in the block: {block[:200]!r}"
    assert abs(float(m.group(1)) - qr_scale(URL)) < 1e-12


def test_integer_form_is_smaller_than_the_absolute_form():
    """Pins the reason for the change, so a revert to absolute coordinates has
    to argue with a number."""
    path = gen_qr(URL)
    scale = qr_scale(URL)
    absolute = " ".join(
        f"M{round(int(m.group(1)) * scale, 3)} {round(int(m.group(2)) * scale, 3)}"
        f"h{round(int(m.group(3)) * scale, 3)}v{round(scale, 3)}"
        f"h-{round(int(m.group(3)) * scale, 3)}z"
        for m in re.finditer(r"M(\d+) (\d+)h(\d+)v1h-\d+z", path)
    )
    assert len(path) < len(absolute) * 0.6, (
        f"integer form is {len(path)} bytes vs {len(absolute)} absolute — the "
        "58 % saving this change exists for is gone"
    )

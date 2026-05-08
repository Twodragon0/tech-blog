#!/usr/bin/env python3
"""CI gate: verify every weekly digest cover SVG has the canonical QR URL.

Reads each ``assets/images/*Tech_*Weekly_Digest_*.svg``, extracts the
QR path data (emitted by :func:`scripts.lib.svg_l22_generator.qr_block`),
and compares it against ``gen_qr(_post_url_from_filename(name))``. Any
mismatch indicates either:

- A regression in :func:`_post_url_from_filename` (e.g., the
  ``slug.replace("_", "-")`` bug returns).
- A manual SVG that hard-coded a stale URL (e.g., the
  ``/security/.../slug.html`` pattern from older upgrade scripts).

This is the canonical gate for QR correctness because we don't ship a
QR decoder dependency. ``gen_qr`` is deterministic per input URL, so a
byte-equal match between rendered path data and a fresh encode proves
the URL the renderer used was the canonical one.

Exit codes
----------
- ``0`` — all covers verified.
- ``1`` — at least one cover has a mismatched / missing QR.
- ``2`` — usage error.

Usage
-----
    python3 scripts/check_cover_qr_urls.py
    python3 scripts/check_cover_qr_urls.py --glob 'assets/images/2026-05-*.svg'
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib.svg_l22_generator import gen_qr  # noqa: E402
from scripts.news.l20_dispatch import _post_url_from_filename  # noqa: E402


_QR_PATH_RE = re.compile(
    r'<g transform="translate\(1080,504\)"[^>]*>\s*'
    r'<rect[^/]*/>\s*'
    r'<path fill="#0A1020" d="([^"]*)"',
    re.DOTALL,
)


def check_one(path: Path) -> tuple[str, str]:
    """Return ``("ok", "")`` or ``(reason, expected_url)``.

    Hand-drawn covers (research-based, certain L25 / hero variants) do
    not carry a QR by design. We only flag a missing QR when the cover
    was emitted by the L20 hero pipeline — those *must* have a QR
    block at translate(1080,504) per
    :func:`scripts.lib.svg_l22_generator.qr_block`.
    """
    text = path.read_text(encoding="utf-8")
    m = _QR_PATH_RE.search(text)
    if not m:
        # L20 auto-generated covers always emit the QR block. Hand-drawn
        # covers don't, and that's intentional.
        is_l20_auto = (
            "<!-- profile: high-quality-cover (L20 Hero+2-Card) -->" in text
            or "<!-- profile: high-quality-cover (L20 Hero+2-Card, research-based) -->" in text
        )
        if is_l20_auto:
            return ("missing-qr", _post_url_from_filename(path.name))
        return ("ok", "")
    rendered = m.group(1)
    canonical = _post_url_from_filename(path.name)
    expected = gen_qr(canonical)
    if rendered != expected:
        return ("mismatch", canonical)
    return ("ok", "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--glob",
        default="assets/images/*Tech_*Weekly_Digest_*.svg",
        help="cover SVG glob",
    )
    args = parser.parse_args(argv)

    paths = sorted(ROOT.glob(args.glob))
    if not paths:
        print(f"no files matched: {args.glob}", file=sys.stderr)
        return 2

    failures: list[tuple[Path, str, str]] = []
    ok_count = 0
    for p in paths:
        reason, expected = check_one(p)
        if reason == "ok":
            ok_count += 1
        else:
            failures.append((p, reason, expected))

    print(f"=== Cover QR URL check ===")
    print(f"Scanned:  {len(paths)}")
    print(f"OK:       {ok_count}")
    print(f"Failures: {len(failures)}")
    if failures:
        print()
        for p, reason, expected in failures:
            print(f"  [{reason}] {p.name}")
            if expected:
                print(f"           expected URL: {expected}")
        print()
        print(
            "Fix with:\n"
            "  python3 scripts/fix_qr_url_in_covers.py --commit"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Surgical QR-block replacement in weekly digest SVG covers.

Background
----------
``scripts/news/l20_dispatch._post_url_from_filename`` had a bug that
hyphenated the slug, producing 404 URLs in every QR code on every
auto-generated L20 cover (commit 88cbcd93 fixed the function).

Manual research-based covers (created by the ``scripts/upgrade_*.py``
upgrade scripts) suffered a different but similar bug: they hard-coded
``/security/YYYY/MM/DD/Slug.html`` URLs that 404 on the live site —
the correct Jekyll permalink is ``/posts/YYYY/MM/DD/Slug/``.

Fixing this without re-running the upgrade scripts (which would
overwrite the curated artwork) requires a surgical replacement: locate
the QR ``<g transform="translate(1080,504)"...>`` block produced by
``svg_l22_generator.qr_block`` and swap it with a freshly-generated one
encoding the canonical URL derived from the filename.

Usage
-----
    # Preview which files need fixing.
    python3 scripts/fix_qr_url_in_covers.py --check

    # Apply.
    python3 scripts/fix_qr_url_in_covers.py --commit
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib.svg_l22_generator import qr_block  # noqa: E402
from scripts.news.l20_dispatch import _post_url_from_filename  # noqa: E402

# QR block template emitted by ``svg_l22_generator.qr_block``:
#   <g transform="translate(1080,504)" filter="url(#softShadow)">
#     <rect ... fill="#FFFFFF"/>
#     <path fill="#0A1020" d="..."/>
#   </g>
#   <text ...>scan / full post</text>
#
# The matcher captures both the <g> wrapper and the trailing "scan / full post"
# label so the replacement stays atomic. The label POSITION changed across
# QR-geometry revisions: the legacy 84px block placed it at ``x="1122" y="614"``
# (below the QR), the current 108px block at ``x="1134" y="486"`` (above the
# enlarged 132x132 white rect). Anchor on the label's text content rather than
# its coordinates so the fixer upgrades BOTH geometries (and any future tweak).
_QR_BLOCK_RE = re.compile(
    r"<g transform=\"translate\(1080,504\)\"[^>]*>"
    r".*?</g>\s*"
    r"<text[^>]*>scan / full post</text>",
    re.DOTALL,
)


def fix_one(path: Path) -> tuple[bool, str]:
    """Return (changed, reason)."""
    text = path.read_text(encoding="utf-8")
    m = _QR_BLOCK_RE.search(text)
    if not m:
        return False, "no QR block found"
    canonical = _post_url_from_filename(path.name)
    new_qr = qr_block(canonical)
    new_text = text[: m.start()] + new_qr + text[m.end():]
    if new_text == text:
        return False, "QR matches canonical URL already"
    path.write_text(new_text, encoding="utf-8")
    return True, f"QR URL → {canonical}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report only")
    parser.add_argument("--commit", action="store_true", help="write changes")
    parser.add_argument(
        "--glob",
        default="assets/images/*Tech_*Weekly_Digest_*.svg",
        help="glob pattern for cover SVGs",
    )
    args = parser.parse_args(argv)
    if not args.check and not args.commit:
        args.check = True

    paths = sorted(ROOT.glob(args.glob))
    if not paths:
        print(f"no files matched glob: {args.glob}", file=sys.stderr)
        return 1

    changed = 0
    skipped_no_qr = 0
    already_correct = 0

    for p in paths:
        if args.commit:
            ok, reason = fix_one(p)
            if ok:
                changed += 1
                print(f"[fix] {p.name}: {reason}")
            elif reason == "no QR block found":
                skipped_no_qr += 1
            else:
                already_correct += 1
        else:
            text = p.read_text(encoding="utf-8")
            m = _QR_BLOCK_RE.search(text)
            if not m:
                skipped_no_qr += 1
                continue
            canonical = _post_url_from_filename(p.name)
            new_qr = qr_block(canonical)
            new_text = text[: m.start()] + new_qr + text[m.end():]
            if new_text == text:
                already_correct += 1
            else:
                changed += 1
                print(f"[needs-fix] {p.name} → {canonical}")

    mode = "COMMIT" if args.commit else "DRY-RUN"
    print()
    print(f"=== QR-URL fix ({mode}) ===")
    print(f"Total scanned:      {len(paths)}")
    print(f"Changed/needs-fix:  {changed}")
    print(f"Already correct:    {already_correct}")
    print(f"No QR block found:  {skipped_no_qr}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

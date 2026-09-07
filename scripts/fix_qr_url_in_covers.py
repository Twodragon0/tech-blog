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
encoding the canonical URL.

That URL comes from :mod:`scripts.check_cover_qr_urls`, resolved through the
owner post's ``image:`` field — NOT from the cover filename. Deriving it here
independently is how 16 covers came to carry a QR that scans to a 404: the
cover filename differs from the post filename by case
(``..._Replace_and_MFA_...`` vs ``..._Replace_And_MFA_...``) or by a shortened
slug, and because the gate derived it the same way, both agreed while both were
wrong. Verified against production 2026-09-07: cover-derived URL 404 for 16/16,
owner-derived URL 200 for 16/16.

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

# The gate is the single source of truth for "which URL should this cover
# encode". Importing from it keeps the fixer from writing a URL the gate would
# then reject — or, as happened before 2026-09-07, from writing a URL that 404s
# because both sides derived it from the cover filename and so agreed while
# being wrong.
from scripts.check_cover_qr_urls import (  # noqa: E402
    accepted_urls_for_cover,
    canonical_url_for_cover,
    cover_owners,
)
from scripts.lib.svg_l22_generator import qr_block  # noqa: E402

# QR block template emitted by ``svg_l22_generator.qr_block``:
#   <g transform="translate(1080,504)" filter="url(#softShadow)">
#     <rect ... fill="#FFFFFF"/>
#     <path fill="#0A1020" d="..."/>
#   </g>
#   <text ...>scan / full post</text>
#
# The matcher captures both the <g> wrapper and the trailing scan label so the
# replacement stays atomic.
#
# It is anchored on the label's TEXT, not its coordinates. The label position
# moved with the QR geometry — the legacy 84px block put it at
# ``x="1122" y="614"`` (below the QR), the current 108px block at
# ``x="1134" y="486"`` (above the enlarged white rect). The coordinate anchor
# survived that change and silently matched nothing: measured 2026-08-21,
# ``--check`` reported "Total scanned: 200 / No QR block found: 200 /
# Changed: 0", which reads as a clean corpus while having inspected none of it.
# All 200 live covers carry the caption verbatim, so the text is the stable key.
_QR_BLOCK_RE = re.compile(
    r"<g transform=\"translate\(1080,504\)\"[^>]*>"
    r".*?</g>\s*"
    r"<text[^>]*>\s*scan / full post\s*</text>",
    re.DOTALL,
)


def _needs_fix(text: str, cover_name: str, owners: dict) -> bool:
    """True when the rendered QR encodes none of the URLs the gate accepts.

    Accept-first, deliberately: one live cover encodes a ``redirect_from``
    target its post declares, which serves the post and which the gate treats
    as valid. Rewriting it to canonical would be a change nothing asked for, so
    the fixer touches only what the gate would reject.
    """
    m = _QR_BLOCK_RE.search(text)
    if not m:
        return False
    for url in accepted_urls_for_cover(cover_name, owners):
        if text[: m.start()] + qr_block(url) + text[m.end() :] == text:
            return False
    return True


def fix_one(path: Path, owners: dict | None = None) -> tuple[bool, str]:
    """Return (changed, reason)."""
    text = path.read_text(encoding="utf-8")
    m = _QR_BLOCK_RE.search(text)
    if not m:
        return False, "no QR block found"
    if owners is None:
        owners = cover_owners()
    if not _needs_fix(text, path.name, owners):
        return False, "QR matches canonical URL already"
    canonical = canonical_url_for_cover(path.name, owners)
    new_qr = qr_block(canonical)
    path.write_text(text[: m.start()] + new_qr + text[m.end() :], encoding="utf-8")
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
    owners = cover_owners()

    for p in paths:
        if args.commit:
            ok, reason = fix_one(p, owners)
            if ok:
                changed += 1
                print(f"[fix] {p.name}: {reason}")
            elif reason == "no QR block found":
                skipped_no_qr += 1
            else:
                already_correct += 1
        else:
            text = p.read_text(encoding="utf-8")
            if not _QR_BLOCK_RE.search(text):
                skipped_no_qr += 1
                continue
            if _needs_fix(text, p.name, owners):
                changed += 1
                print(
                    f"[needs-fix] {p.name} → {canonical_url_for_cover(p.name, owners)}"
                )
            else:
                already_correct += 1

    mode = "COMMIT" if args.commit else "DRY-RUN"
    print()
    print(f"=== QR-URL fix ({mode}) ===")
    print(f"Total scanned:      {len(paths)}")
    print(f"Changed/needs-fix:  {changed}")
    print(f"Already correct:    {already_correct}")
    print(f"No QR block found:  {skipped_no_qr}")

    # Non-vacuity. `Changed: 0` reads as "the corpus is fine", but it says the
    # same thing when the matcher is broken — which is how the coordinate-
    # anchored regex above went unnoticed through a QR geometry change while
    # missing 200/200 covers. Every cover matched by the default glob emits a
    # QR block, so a total miss is a template drift, not a clean report.
    if paths and skipped_no_qr == len(paths):
        print(
            f"\nERROR: no QR block matched in ANY of the {len(paths)} scanned "
            "covers. The template this fixer targets has drifted — update "
            "_QR_BLOCK_RE. Reporting 0 changes here would be indistinguishable "
            "from a healthy corpus.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

That proof holds only while ``qrcode`` is importable. Without it
``gen_qr`` returns ``""`` for every input, so the comparison becomes
``"" == ""`` and this gate reports OK on a cover whose QR is a blank
white square. Measured 2026-09-06 on the real 09-04 cover: with
``qrcode`` installed the gate returns ``Failures: 1``; with its import
blocked, the byte-identical file returns ``OK: 1`` and exit 0. That is
how ``2026-09-04-Tech_Security_Weekly_Digest_AI_Malware_Rust.svg``
shipped with ``d=""`` from a local publish (f4a459d1) and then held
main red for three days once CI — which does install ``qrcode`` — read
the same file. So refuse to run rather than pass vacuously: a gate that
cannot verify must not say OK.

Exit codes
----------
- ``0`` — all covers verified.
- ``1`` — at least one cover has a mismatched / missing QR.
- ``2`` — usage error, or ``qrcode`` is unavailable so nothing can be verified.

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

from scripts.lib.svg_l22_generator import QRCODE_AVAILABLE, gen_qr  # noqa: E402
from scripts.news.l20_dispatch import _post_url_from_filename  # noqa: E402

_QR_PATH_RE = re.compile(
    r'<g transform="translate\(1080,504\)"[^>]*>\s*'
    r"<rect[^/]*/>\s*"
    r'<path fill="#0A1020" d="([^"]*)"',
    re.DOTALL,
)


_IMAGE_FIELD_RE = re.compile(r"^image:\s*[\"']?(\S+?)[\"']?\s*$", re.M)
_REDIRECT_ITEM_RE = re.compile(r"^\s*-\s*(/\S+)\s*$", re.M)
_FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)

SITE_ORIGIN = "https://tech.2twodragon.com"


def _front_matter(post: Path) -> str:
    m = _FRONT_MATTER_RE.match(post.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else ""


def cover_owners(posts_dir: Path | None = None) -> dict[str, Path]:
    """Map ``assets/images/<cover>.svg`` -> the post that declares it.

    Keyed on the post's ``image:`` field, never on the filename stem. Stem
    matching misreports owners: on a case-insensitive filesystem
    ``..._Governance_and_...svg`` appears to match ``..._Governance_And_....md``
    while the live URL uses the post's casing, and several covers carry a
    shortened slug that shares no stem with their post at all.
    """
    posts_dir = (ROOT / "_posts") if posts_dir is None else posts_dir
    owners: dict[str, Path] = {}
    for post in sorted(posts_dir.glob("*.md")):
        m = _IMAGE_FIELD_RE.search(_front_matter(post))
        if m:
            owners.setdefault(m.group(1).lstrip("/"), post)
    return owners


def _declared_urls(post: Path) -> list[str]:
    """Canonical URL first, then any ``redirect_from`` target, as absolute URLs.

    A ``redirect_from`` entry is a real destination — it serves the post — so a
    QR encoding one is not broken. One live cover
    (``2025-12-24-Cloud_Security_Course_8Batch_5Week_...``) encodes the older
    ``/posts/{YYYY}/{MM}/{slug}/`` shape its post still declares.
    """
    urls = [_post_url_from_filename(post.name)]
    fm = _front_matter(post)
    if "redirect_from" in fm:
        after = fm.split("redirect_from", 1)[1]
        for item in _REDIRECT_ITEM_RE.findall(after):
            urls.append(f"{SITE_ORIGIN}{item}")
    return urls


def accepted_urls_for_cover(
    cover_name: str, owners: dict[str, Path] | None = None
) -> list[str]:
    """Every URL a QR on ``cover_name`` may legitimately encode, canonical first.

    Shared with ``fix_qr_url_in_covers.py`` on purpose: when the fixer derives
    the URL independently, the two can agree on a wrong answer. That is exactly
    what happened until 2026-09-07 — both used the cover filename, so the gate
    passed 16 covers whose QR scanned to a 404 and the fixer would have written
    the same 404 back.
    """
    if owners is None:
        owners = cover_owners()
    owner = owners.get(f"assets/images/{cover_name}")
    if owner is None:
        return [_post_url_from_filename(cover_name)]
    return _declared_urls(owner)


def canonical_url_for_cover(
    cover_name: str, owners: dict[str, Path] | None = None
) -> str:
    """The one URL a fixer should write."""
    return accepted_urls_for_cover(cover_name, owners)[0]


def check_one(path: Path, owners: dict[str, Path] | None = None) -> tuple[str, str]:
    """Return ``("ok", "")`` or ``(reason, expected_url)``.

    Hand-drawn covers (research-based, certain L25 / hero variants) do
    not carry a QR by design. We only flag a missing QR when the cover
    was emitted by the L20 hero pipeline — those *must* have a QR
    block at translate(1080,504) per
    :func:`scripts.lib.svg_l22_generator.qr_block`.

    The expected URL comes from the **owner post**, resolved through that
    post's ``image:`` field, falling back to the cover filename when no post
    claims the cover. Deriving it from the cover filename alone was correct
    only for digests, where cover stem == post stem by construction. Measured
    2026-09-07 over all 336 covers: 12 "mismatches", and every one was a false
    positive — 11 encoded the owner post's canonical URL (the post filename
    differs from the cover's by case or by truncation) and 1 encoded a URL the
    post declares in ``redirect_from``.
    """
    text = path.read_text(encoding="utf-8")
    accepted = accepted_urls_for_cover(path.name, owners)
    canonical = accepted[0]

    m = _QR_PATH_RE.search(text)
    if not m:
        # L20 auto-generated covers always emit the QR block. Hand-drawn
        # covers don't, and that's intentional.
        is_l20_auto = (
            "<!-- profile: high-quality-cover (L20 Hero+2-Card) -->" in text
            or "<!-- profile: high-quality-cover (L20 Hero+2-Card, research-based) -->"
            in text
        )
        if is_l20_auto:
            return ("missing-qr", canonical)
        return ("ok", "")
    rendered = m.group(1)
    if any(rendered == gen_qr(url) for url in accepted):
        return ("ok", "")
    return ("mismatch", canonical)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--glob",
        default="assets/images/*Tech_*Weekly_Digest_*.svg",
        help="cover SVG glob",
    )
    args = parser.parse_args(argv)

    # Before anything else: without qrcode the expected value is "" for every
    # cover, so every comparison succeeds and the report reads "Failures: 0".
    # Blocking here is safe for all three wired callers — check-svg.yml and
    # jekyll.yml install scripts/requirements-ci.txt (qrcode>=8.2) and
    # ai-blogwatcher.yml installs requirements-blogwatcher.txt (qrcode[pil]).
    # It fires only where the dependency is genuinely absent, which is exactly
    # where the previous "OK" was a lie.
    if not QRCODE_AVAILABLE:
        print(
            "cannot verify: the 'qrcode' package is not importable, so gen_qr() "
            "returns '' for every URL and every cover would compare equal. "
            "Install it (pip install -r scripts/requirements-ci.txt) and re-run.",
            file=sys.stderr,
        )
        return 2

    paths = sorted(ROOT.glob(args.glob))
    if not paths:
        print(f"no files matched: {args.glob}", file=sys.stderr)
        return 2

    failures: list[tuple[Path, str, str]] = []
    ok_count = 0
    # Built once: it reads every post's front matter, and re-deriving it per
    # cover turns a 336-file sweep into 336 corpus scans.
    owners = cover_owners()
    for p in paths:
        reason, expected = check_one(p, owners)
        if reason == "ok":
            ok_count += 1
        else:
            failures.append((p, reason, expected))

    print("=== Cover QR URL check ===")
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
        print("Fix with:\n  python3 scripts/fix_qr_url_in_covers.py --commit")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

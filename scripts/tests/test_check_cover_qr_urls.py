#!/usr/bin/env python3
"""Regression guard: the QR gate must not pass vacuously without ``qrcode``.

``check_cover_qr_urls.py`` proves a cover's QR by re-encoding the canonical
permalink with ``gen_qr`` and byte-comparing against the rendered path data.
``gen_qr`` returns ``""`` when the optional ``qrcode`` package is missing, and
``qr_block`` then emits ``<path ... d=""/>`` — a blank white square where the QR
should be. Both sides of the comparison are ``""``, so the gate reported
``Failures: 0`` on exactly the covers it existed to reject.

That is not hypothetical. ``2026-09-04-Tech_Security_Weekly_Digest_AI_Malware_Rust.svg``
shipped with ``d=""`` in f4a459d1 — a hand-run publish from a laptop, not the
blogwatcher — and every CI runner (all of which do install ``qrcode``) failed on
it for the next three days while the blank QR sat live on the site.

The control matters here as much as the treatment. A test that only asserts
"missing qrcode => exit 2" passes just as well against a fixture that is not a
violation at all, so ``test_control_*`` first proves the same bytes are rejected
when ``qrcode`` IS importable. Without that pairing this file would be another
probe with no control.

Note the absence of ``skipif(not QRCODE_AVAILABLE)`` on the control. Skipping
there would reproduce, in the guard, the very failure the guard exists to catch:
an environment without ``qrcode`` would report green while nothing was verified.
``qrcode`` is a declared dependency of every environment that runs this suite
(``scripts/requirements-ci.txt`` for svg-lint and jekyll,
``requirements-blogwatcher.txt`` for the cron corpus gate), so its absence is a
real failure and is asserted as one below.
"""

from __future__ import annotations

import check_cover_qr_urls as gate
import pytest
from lib.svg_l22_generator import QRCODE_AVAILABLE, qr_block

# The gate only inspects covers it knows the L20 pipeline emitted.
_L20_MARKER = "<!-- profile: high-quality-cover (L20 Hero+2-Card) -->"
_COVER_NAME = "2026-09-04-Tech_Security_Weekly_Digest_AI_Malware_Rust.svg"


def _write_cover(directory, name: str, qr_url: str | None) -> None:
    """Write a minimal L20-shaped cover.

    ``qr_url=None`` reproduces the blank-QR failure: the QR block is present and
    structurally valid, but its path data is empty — what ``qr_block`` emits when
    ``gen_qr`` has no ``qrcode`` to call.
    """
    if qr_url is None:
        block = (
            '<g transform="translate(1080,504)" filter="url(#softShadow)">\n'
            '  <rect x="-12" y="-12" width="132" height="132" rx="8" fill="#FFFFFF"/>\n'
            '  <path fill="#0A1020" d=""/>\n'
            "</g>"
        )
    else:
        block = qr_block(qr_url)
    (directory / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg">{_L20_MARKER}\n{block}\n</svg>',
        encoding="utf-8",
    )


@pytest.fixture
def blank_qr_cover(tmp_path, monkeypatch):
    """A single blank-QR cover, with the gate's glob root pointed at it."""
    _write_cover(tmp_path, _COVER_NAME, qr_url=None)
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    return tmp_path


def test_qrcode_is_installed_in_this_environment():
    """Asserted, not skipped — see the module docstring.

    Every runner that executes scripts/tests/ declares qrcode. If this fails, the
    control below cannot run, and a skip would have hidden that behind a green
    suite.
    """
    assert QRCODE_AVAILABLE, (
        "qrcode is not importable, so the control cannot distinguish a correct "
        "cover from a blank one. It is declared in scripts/requirements-ci.txt "
        "and requirements-blogwatcher.txt — install it rather than skipping."
    )


def test_control_blank_qr_is_rejected_when_qrcode_is_available(blank_qr_cover, capsys):
    """Control: these exact bytes ARE a violation, so the treatment is meaningful."""
    assert gate.main(["--glob", "*.svg"]) == 1
    out = capsys.readouterr().out
    assert "Failures: 1" in out
    assert "[mismatch]" in out


def test_gate_refuses_to_run_when_qrcode_is_unavailable(
    blank_qr_cover, monkeypatch, capsys
):
    """Treatment: the same cover must not be reported OK just because we went blind."""
    monkeypatch.setattr(gate, "QRCODE_AVAILABLE", False)

    exit_code = gate.main(["--glob", "*.svg"])

    assert exit_code == 2, (
        "the gate returned a non-refusal exit code with qrcode unavailable. If it "
        "returned 0 it just certified a blank QR, which is the f4a459d1 failure."
    )
    captured = capsys.readouterr()
    assert "cannot verify" in captured.err
    assert "Failures: 0" not in captured.out, (
        "the gate printed a passing report while unable to encode anything"
    )


def test_correct_cover_still_passes(tmp_path, monkeypatch, capsys):
    """The refusal must not swallow the happy path."""
    canonical = gate._post_url_from_filename(_COVER_NAME)
    _write_cover(tmp_path, _COVER_NAME, qr_url=canonical)
    monkeypatch.setattr(gate, "ROOT", tmp_path)

    assert gate.main(["--glob", "*.svg"]) == 0
    assert "Failures: 0" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Owner-post URL derivation
#
# The expected URL must come from the post that declares the cover in its
# `image:` field, not from the cover's own filename. Until 2026-09-07 both this
# gate and fix_qr_url_in_covers.py derived it from the filename, so they agreed
# with each other while both were wrong: 16 covers carried a QR that returned
# 404 in production (owner-derived URL returned 200 for all 16).
#
# The cover/post filename divergence is real, not hypothetical — e.g.
#   cover  ..._USIMeSIM_Replace_and_MFA_Importance.svg
#   post   ..._USIMeSIM_Replace_And_MFA_Importance.md
# differing only in the case of "and", which a case-insensitive filesystem
# hides locally and a case-sensitive server does not.
# ---------------------------------------------------------------------------

_COVER = "2025-04-29-Cover_Slug_and_Tail.svg"
_OWNER_POST = "2025-04-29-Cover_Slug_And_Tail.md"  # note: capital "And"


def _write_owner_post(posts_dir, name: str, cover: str, redirects=()) -> None:
    lines = ["---", f"image: /assets/images/{cover}"]
    if redirects:
        lines.append("redirect_from:")
        lines += [f"  - {r}" for r in redirects]
    lines += ["---", "", "body"]
    (posts_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture
def owner_setup(tmp_path):
    covers = tmp_path / "assets" / "images"
    posts = tmp_path / "_posts"
    covers.mkdir(parents=True)
    posts.mkdir()
    return covers, posts


def test_owner_is_resolved_via_image_field_not_filename_stem(owner_setup):
    covers, posts = owner_setup
    _write_owner_post(posts, _OWNER_POST, _COVER)
    owners = gate.cover_owners(posts)
    assert owners[f"assets/images/{_COVER}"].name == _OWNER_POST, (
        "the cover must map to the post that names it in image:. Stem matching "
        "would have found nothing here, since the stems differ in case."
    )


def test_qr_encoding_the_owner_post_url_is_accepted(owner_setup, monkeypatch):
    """The 16-cover case: owner-derived URL is the correct one."""
    covers, posts = owner_setup
    _write_owner_post(posts, _OWNER_POST, _COVER)
    owners = gate.cover_owners(posts)
    owner_url = gate.canonical_url_for_cover(_COVER, owners)
    assert "_And_" in owner_url, "expected the post's casing, not the cover's"

    _write_cover(covers, _COVER, qr_url=owner_url)
    assert gate.check_one(covers / _COVER, owners) == ("ok", "")


def test_qr_encoding_the_cover_filename_url_is_rejected(owner_setup):
    """Control for the test above: the old derivation's URL must now fail.

    Without this, `test_qr_encoding_the_owner_post_url_is_accepted` would also
    pass under a gate that accepted anything.
    """
    covers, posts = owner_setup
    _write_owner_post(posts, _OWNER_POST, _COVER)
    owners = gate.cover_owners(posts)

    from news.l20_dispatch import _post_url_from_filename

    cover_url = _post_url_from_filename(_COVER)
    assert "_and_" in cover_url
    _write_cover(covers, _COVER, qr_url=cover_url)
    reason, expected = gate.check_one(covers / _COVER, owners)
    assert reason == "mismatch"
    assert "_And_" in expected, "the reported expectation must be the live URL"


def test_declared_redirect_from_target_is_accepted(owner_setup):
    """A redirect_from URL serves the post, so a QR on it is not broken."""
    covers, posts = owner_setup
    legacy = "/posts/2025/04/Cover_Slug_And_Tail/"
    _write_owner_post(posts, _OWNER_POST, _COVER, redirects=[legacy])
    owners = gate.cover_owners(posts)

    _write_cover(covers, _COVER, qr_url=f"{gate.SITE_ORIGIN}{legacy}")
    assert gate.check_one(covers / _COVER, owners) == ("ok", "")


def test_unclaimed_cover_falls_back_to_its_own_filename(owner_setup):
    """No post declares it — the filename is the only thing left to go on."""
    covers, posts = owner_setup
    from news.l20_dispatch import _post_url_from_filename

    owners = gate.cover_owners(posts)  # empty
    assert gate.canonical_url_for_cover(_COVER, owners) == _post_url_from_filename(
        _COVER
    )


def test_fixer_writes_the_owner_post_url(owner_setup):
    """The regression that would silently re-introduce all 16 404s.

    If the fixer derives the URL itself, running it "to repair" a cover writes
    the 404 back and the gate — now correct — keeps rejecting it.
    """
    import fix_qr_url_in_covers as fixer
    from news.l20_dispatch import _post_url_from_filename

    covers, posts = owner_setup
    _write_owner_post(posts, _OWNER_POST, _COVER)
    owners = gate.cover_owners(posts)

    _write_cover(covers, _COVER, qr_url=_post_url_from_filename(_COVER))
    changed, reason = fixer.fix_one(covers / _COVER, owners)
    assert changed, f"fixer left the 404 QR in place: {reason}"
    assert "_And_" in reason, f"fixer wrote the cover-derived URL: {reason}"
    assert gate.check_one(covers / _COVER, owners) == ("ok", "")


def test_fixer_leaves_a_redirect_encoding_cover_alone(owner_setup):
    """Accept-first: the fixer must only touch what the gate rejects."""
    import fix_qr_url_in_covers as fixer

    covers, posts = owner_setup
    legacy = "/posts/2025/04/Cover_Slug_And_Tail/"
    _write_owner_post(posts, _OWNER_POST, _COVER, redirects=[legacy])
    owners = gate.cover_owners(posts)

    _write_cover(covers, _COVER, qr_url=f"{gate.SITE_ORIGIN}{legacy}")
    before = (covers / _COVER).read_text(encoding="utf-8")
    changed, _ = fixer.fix_one(covers / _COVER, owners)
    assert not changed
    assert (covers / _COVER).read_text(encoding="utf-8") == before

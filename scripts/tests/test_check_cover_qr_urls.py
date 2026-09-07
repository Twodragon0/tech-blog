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

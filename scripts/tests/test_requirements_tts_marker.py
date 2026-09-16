#!/usr/bin/env python3
"""Guard: the TTS environment marker must match TTS's real Requires-Python.

Concrete incident this protects against
----------------------------------------
``scripts/requirements.txt`` carried::

    # Coqui TTS currently does not publish wheels for Python 3.14+
    TTS>=0.22.0; python_version < "3.14"

Both halves were wrong. TTS 0.22.0 — the latest release and the lower bound in
that very line — declares ``Requires-Python: >=3.9.0, <3.12``, as does every
release back to 0.20.4. It is a self-imposed cap in package metadata, not a
wheel-availability gap.

The consequence was a marker that evaluated *true* on 3.12 and 3.13, so pip
tried to install a package it could never resolve::

    ERROR: Could not find a version that satisfies the requirement TTS>=0.22.0
    ERROR: No matching distribution found for TTS>=0.22.0

and took the whole file down with it. CI never noticed: ``generate-images.yml``
is the only workflow installing this file and it pins ``python-version: '3.11'``,
where the marker is true *and* TTS resolves. So the failure was local-only and
invisible for as long as nobody built a dev env on 3.12+. It surfaced on
2026-09-15 only as a side effect of an unrelated dry-run on 3.13.

Why a test rather than a comment
--------------------------------
The wrong value shipped *with a comment explaining it*. A second, longer comment
is not a stronger control than the first one was. The check has to be executable.

Re-verifying the upper bound
----------------------------
This guard deliberately does NOT hit PyPI: a network call would make the suite
fail offline and in CI sandboxes, for a value that changes about once a year.
When TTS relaxes its cap, re-measure and update ``_TTS_PYTHON_UPPER_BOUND`` and
the marker together::

    curl -s https://pypi.org/pypi/TTS/json \\
      | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['requires_python'])"
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / "scripts" / "requirements.txt"

# TTS 0.22.0 `Requires-Python: >=3.9.0, <3.12` — measured 2026-09-16.
_TTS_PYTHON_UPPER_BOUND = "3.12"

_TTS_LINE = re.compile(r"^\s*TTS\s*(?P<spec>[><=!~][^;]*)?;\s*(?P<marker>.+?)\s*$")


def _tts_line() -> str:
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("TTS") and not stripped.startswith("#"):
            return stripped
    raise AssertionError(
        f"No TTS requirement line found in {REQUIREMENTS}. If TTS was removed "
        "on purpose, delete this guard in the same commit — a guard whose "
        "subject is gone is just a tripwire for the next reader."
    )


def test_requirements_file_exists() -> None:
    """Canary: a moved/renamed file must fail clearly, not vacuously."""
    assert REQUIREMENTS.is_file(), f"{REQUIREMENTS} not found — update this guard."


def test_tts_is_marker_gated() -> None:
    """TTS must carry an environment marker at all.

    Without one, `pip install -r scripts/requirements.txt` fails outright on
    every interpreter >=3.12 instead of quietly skipping an optional extra.
    """
    line = _tts_line()
    assert ";" in line, (
        f"TTS declared without an environment marker: {line!r}. TTS caps itself "
        f"at Python <{_TTS_PYTHON_UPPER_BOUND}, so an unguarded declaration "
        "breaks the whole file on newer interpreters."
    )


def test_tts_marker_matches_declared_requires_python() -> None:
    """The marker's upper bound must equal TTS's own Requires-Python cap.

    A marker looser than the cap (the shipped `< "3.14"`) makes pip attempt an
    unresolvable install. A marker tighter than the cap silently drops TTS on
    interpreters that could have used it. Only equality is right.
    """
    line = _tts_line()
    m = _TTS_LINE.match(line)
    assert m, f"Could not parse the TTS requirement line: {line!r}"
    marker = m.group("marker")

    bound = re.search(r'python_version\s*<\s*["\'](?P<v>[0-9.]+)["\']', marker)
    assert bound, (
        f'TTS marker has no `python_version < "X.Y"` upper bound: {marker!r}. '
        f"TTS caps itself at <{_TTS_PYTHON_UPPER_BOUND}; express that as an "
        "upper bound so pip skips it rather than failing to resolve it."
    )
    assert bound.group("v") == _TTS_PYTHON_UPPER_BOUND, (
        f"TTS marker says python_version < {bound.group('v')!r} but TTS "
        f"declares Requires-Python <{_TTS_PYTHON_UPPER_BOUND} (measured "
        "2026-09-16 on 0.22.0, and unchanged since 0.20.4). "
        f"A looser bound makes `pip install -r {REQUIREMENTS.name}` fail on "
        "3.12/3.13 with 'No matching distribution found for TTS'; a tighter "
        "one drops TTS where it would have worked. If TTS relaxed its cap, "
        "re-measure via the PyPI command in this module's docstring and update "
        "_TTS_PYTHON_UPPER_BOUND and the marker together."
    )

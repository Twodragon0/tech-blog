"""scripts/requirements.txt must keep Pillow inside moviepy's range.

moviepy 2.x (2.2.1 is the latest on 2026-11-21) declares
``Requires-Dist: pillow<12.0,>=9.2.0``. Dependabot PR #792 (2026-10-24,
auto-merged) moved this file's pin to ``Pillow>=13.0.0,<14.0`` despite the
ignore rules in .github/dependabot.yml, and every "Generate Post Images" run
after it failed at ``pip install -r scripts/requirements.txt`` with
ResolutionImpossible. A ceiling at 12 alone is not enough either: a floor at
12 or above has no solution, and pip will not say so until install time.

This is a static check on the declared specifiers, so it runs offline. When
moviepy ships a release that accepts pillow>=12, raise both specs together.
"""

from __future__ import annotations

import re
from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"
MOVIEPY_PILLOW_CEILING = 12  # moviepy 2.x: pillow<12.0


def _spec(name: str) -> str | None:
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        code = line.split("#", 1)[0].strip()
        if re.match(rf"{re.escape(name)}(?![A-Za-z0-9_.-])", code, re.IGNORECASE):
            return code
    return None


def test_pillow_range_fits_moviepy():
    if _spec("moviepy") is None:
        return  # no moviepy, no constraint to honour
    pillow = _spec("Pillow")
    assert pillow is not None, (
        "scripts/requirements.txt declares moviepy but no Pillow pin"
    )
    ceiling = re.search(r"<\s*(\d+)", pillow)
    floor = re.search(r">=\s*(\d+)", pillow)
    assert ceiling and int(ceiling.group(1)) <= MOVIEPY_PILLOW_CEILING, (
        f"{pillow!r}: moviepy 2.x requires pillow<12.0, so Pillow needs a ceiling "
        "of <12 or lower"
    )
    assert floor is None or int(floor.group(1)) < MOVIEPY_PILLOW_CEILING, (
        f"{pillow!r}: a floor of 12 or above leaves no Pillow that moviepy accepts"
    )

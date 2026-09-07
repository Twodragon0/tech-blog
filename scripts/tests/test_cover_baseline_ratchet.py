"""CI regression guard: cover grandfather-baselines must not silently re-grow.

On 2026-06-23 all 16 grandfathered cover-honesty FAILs (3 L20 specs + 13 L22
digest specs) were retired to honest classes and the L20 spec-drift exemption
for Security_Vendor_Blog was resolved, leaving BOTH ``cover_honesty_baseline.txt``
and ``l20_drift_baseline.txt`` EMPTY. Those baselines are grandfather lists: a
``--strict`` honesty/drift gate passes for any cover listed in them. If a future
cron run or edit re-introduces a dishonest/overclaiming cover and quietly appends
it to a baseline (instead of fixing the cover), the blocking gate would go green
while the regression ships. This guard makes that re-population fail loudly.

As of 2026-06-24 the two remaining legacy size-gate entries (SKT, 12-17
Conference) were also brought in-band — SKT shrank when its honesty FAIL was
fixed; the Conference band's fake-CVSS lock_cve was swapped to an honest shield
(more honest AND ~410B smaller), landing it under the hq band. So ALL THREE
baselines are now empty.

Direction:
  * all three baselines: ``== 0`` entries (frozen empty; ANY new entry trips —
    fix the cover, do not baseline it). size-gate keeps a ``<= SIZE_MAX`` ratchet
    so a genuinely new legacy file can be grandfathered by raising SIZE_MAX in
    the same, reviewable commit.

If a change to any baseline is genuinely intentional, update the relevant
constant here in the same commit so the intent is reviewable.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"

HONESTY_BASELINE = SCRIPTS / "cover_honesty_baseline.txt"
L20_DRIFT_BASELINE = SCRIPTS / "l20_drift_baseline.txt"
SIZE_BASELINE = SCRIPTS / "svg_size_gate_baseline.txt"

# Frozen maxima. All baselines were retired to empty as of 2026-06-24.
#
# 2026-09-07, twice in one day. First 0 -> 2: two covers grew past the hq cap
# because their QR was re-encoded to a URL that actually resolves (the old one
# derived from the COVER filename and returned 404 in production for 16/16
# covers checked). The longer post slug bumps the QR to a higher version, and
# 100 % of the growth was inside the QR block.
#
# Then back to 0, by taking the escape hatch that entry described: `gen_qr` now
# emits integer module coordinates under a `transform="scale(...)"` instead of
# 3-decimal absolute ones, which shrinks the path text 58 %.
#
#   2025-09-17-NPM_Shai-Hulud_180…      76791 -> 64669  (cap 73728)
#   2025-12-17-12_Conference_Review…    74148 -> 61569
#
# So the Conference cover's ~410 B honest-shield saving recorded in the
# docstring above is intact again, with ~12 KB of headroom on top.
SIZE_MAX = 0


def _entry_count(path: Path) -> int:
    """Non-comment, non-blank lines in a baseline file."""
    if not path.is_file():
        return -1
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.split("#", 1)[0].strip()
        if s:
            n += 1
    return n


class TestCoverBaselineRatchet(unittest.TestCase):
    def test_baseline_files_exist(self) -> None:
        for p in (HONESTY_BASELINE, L20_DRIFT_BASELINE, SIZE_BASELINE):
            self.assertTrue(p.is_file(), f"missing baseline file: {p}")

    def test_honesty_baseline_stays_empty(self) -> None:
        n = _entry_count(HONESTY_BASELINE)
        self.assertEqual(
            n,
            0,
            f"cover_honesty_baseline.txt has {n} grandfathered FAIL(s); it must "
            "stay empty. Fix the cover's spec band to an honest class and "
            "regenerate instead of baselining. If genuinely intentional, raise "
            "this guard's expectation in the same commit.",
        )

    def test_l20_drift_baseline_stays_empty(self) -> None:
        n = _entry_count(L20_DRIFT_BASELINE)
        self.assertEqual(
            n,
            0,
            f"l20_drift_baseline.txt has {n} grandfathered drift entry(ies); it "
            "must stay empty. Correct the rotted spec so a fresh render matches "
            "the honest on-disk SVG instead of baselining the drift.",
        )

    def test_size_baseline_does_not_grow(self) -> None:
        n = _entry_count(SIZE_BASELINE)
        self.assertLessEqual(
            n,
            SIZE_MAX,
            f"svg_size_gate_baseline.txt grew to {n} (> {SIZE_MAX}); a new "
            "oversize cover was baselined. Shrink the cover (e.g. a more compact "
            "honest visual) to stay within its size band instead. If a new "
            "legacy file legitimately must be grandfathered, raise SIZE_MAX here.",
        )


if __name__ == "__main__":
    unittest.main()

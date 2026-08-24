"""Tests for the runtime env-var declaration contract.

Every credential guard in this repo before 2026-08-24 was keyed to CI secrets —
`test_ci_secret_absence_guard.py` walks `.github/workflows/`. Runtime
credentials live in the Vercel project, which that axis cannot see, and the gap
cost us `GA4_API_SECRET`: two PRs of first-party beacon work shipped into an
endpoint that dropped every report and answered 204 anyway.

CI cannot check Vercel (no token), so what CI *can* enforce is that a new
runtime dependency is never added without someone writing down what breaks when
it is absent. These tests keep that enforcement honest.
"""

from __future__ import annotations

import pytest

from scripts import check_runtime_env_contract as contract


def test_every_env_var_read_by_api_is_declared():
    refs = contract.referenced()
    undeclared = sorted(set(refs) - set(contract.declared()))
    assert undeclared == [], (
        f"add to REQUIRED or OPTIONAL in check_runtime_env_contract.py, "
        f"saying what breaks when absent: {undeclared}"
    )


def test_no_declaration_outlives_its_code():
    refs = contract.referenced()
    orphaned = sorted(set(contract.declared()) - set(refs))
    assert orphaned == [], f"declared but no longer read by api/: {orphaned}"


def test_the_three_categories_do_not_overlap():
    names = [
        set(contract.PLATFORM),
        set(contract.REQUIRED),
        set(contract.OPTIONAL),
    ]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert not a & b, f"a var is in two categories: {sorted(a & b)}"


@pytest.mark.parametrize("name", sorted(contract.REQUIRED))
def test_required_entries_say_what_breaks_and_where_to_provision(name: str):
    """A REQUIRED entry that just names a file teaches nobody anything.

    The whole failure mode was that absence looked like success, so the
    declaration has to record the symptom and the provisioning location.
    """
    note = contract.REQUIRED[name]
    assert "Absent:" in note, f"{name}: record what breaks when it is absent"
    assert "Provision:" in note, f"{name}: record where it gets provisioned"


def test_ga4_api_secret_is_required_not_optional():
    """Regression guard for the specific miscategorisation that caused the loss.

    `api/vitals.js` treats an absent secret as a soft drop, which reads like an
    optional dependency at the call site. It is not: with it unset, the feature
    collects zero data while reporting success.
    """
    assert "GA4_API_SECRET" in contract.REQUIRED
    assert "GA4_API_SECRET" not in contract.OPTIONAL


def test_test_fixtures_are_not_mistaken_for_dependencies():
    """`api/__tests__/sanitize.test.js` contains the literal 'process.env.SECRET'.

    It is assertion text for the sanitizer, not a runtime dependency. If the
    scanner ever starts walking __tests__, this fails and points at why.
    """
    assert "SECRET" not in contract.referenced()


def test_the_scanner_actually_finds_something():
    """Proof the two corpus assertions above are not vacuously green."""
    refs = contract.referenced()
    assert "GA4_API_SECRET" in refs
    assert any("vitals.js" in f for f in refs["GA4_API_SECRET"])
    assert len(refs) > 10

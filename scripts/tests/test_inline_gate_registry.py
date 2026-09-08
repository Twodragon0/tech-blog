#!/usr/bin/env python3
"""Guard: the inline publish gates stay registered, and a blocker stays healable.

Three gates run inside ``scripts/auto_publish_news.py`` rather than as steps of
``ai-blogwatcher.yml``, and one of them deletes the draft and exits. None of
them is greppable from the workflow — measured: ``grep digest_quality_report
.github/workflows/ai-blogwatcher.yml`` returns nothing.

That invisibility had a cost. The workflow's six self-heal-then-block steps were
built as though they covered the gate set, but they all run *after* the post
exists, so the earliest and most destructive gate never got a turn and carried
no self-heal. Two publish days were lost (2026-08-27, 2026-09-06), and both were
diagnosed by grepping the publisher rather than by reading the workflow.

The load-bearing assertion here is ``test_a_blocking_gate_must_self_heal``. The
others exist so that the registry cannot quietly stop describing the code.

Why a reverse scan and not just a forward one
---------------------------------------------
A forward check ("every registered symbol is called") passes happily while an
unregistered fourth gate sits next to the other three. The reverse direction is
what makes the registry a control instead of a comment, so the extractor it
depends on is attacked first, by ``test_the_extractor_finds_the_known_calls``:
an over-narrow pattern finds nothing, and nothing-found reads exactly like
nothing-wrong.
"""

from __future__ import annotations

import importlib
import io
import re
import tokenize
from pathlib import Path

import auto_publish_news as apn
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = REPO_ROOT / "scripts" / "auto_publish_news.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

# Deliberately broad: it must over-match rather than under-match, so a new
# gate-shaped call forces either a registry entry or a reviewed exemption below.
GATE_CALL_RE = re.compile(
    r"^\s*(?:\w+\s*=\s*)?"
    r"(run_[a-z_]*gate[a-z_]*|_run_[a-z_]*gate[a-z_]*|check_file|_check_[a-z_]+|validate_[a-z_]+)"
    r"\(",
    re.MULTILINE,
)

# Gate-shaped calls that are not publish gates. Empty on purpose: there is no
# hiding place yet, and adding one should require writing down why.
NOT_A_GATE: frozenset[str] = frozenset()


def _code_only(source: str) -> str:
    """Blank out comments and string literals, preserving byte offsets.

    Written after this file's own registry comment — ``# unlink(post) +
    sys.exit(1)`` — was counted as a third publish-terminating statement and
    failed the test it was documenting. A guard whose regex also reads
    commentary is a guard that trips on prose, and the naive fix
    (``line.split("#")[0]``) truncates code after any ``#`` inside a string.
    ``tokenize`` knows the difference.

    Same-length replacement keeps offsets usable for the ordering assertion.
    """
    lines = source.splitlines(keepends=True)
    line_start = [0]
    for line in lines:
        line_start.append(line_start[-1] + len(line))

    out = list(source)
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        (srow, scol), (erow, ecol) = token.start, token.end
        start = line_start[srow - 1] + scol
        end = line_start[erow - 1] + ecol
        for i in range(start, min(end, len(out))):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def _publisher_source() -> str:
    """The publisher with comments and string literals blanked."""
    return _code_only(PUBLISHER.read_text(encoding="utf-8"))


def _called_gate_symbols(source: str | None = None) -> set[str]:
    return set(GATE_CALL_RE.findall(_publisher_source() if source is None else source))


def _registered_symbols() -> set[str]:
    return {entry[0] for entry in apn.INLINE_PUBLISH_GATES}


def test_registry_is_present_and_well_formed():
    """Canary: an empty or reshaped registry makes every check below vacuous."""
    registry = apn.INLINE_PUBLISH_GATES
    assert len(registry) >= 3, registry
    for entry in registry:
        symbol, canonical, blocking, self_heal = entry
        assert symbol and canonical, entry
        assert isinstance(blocking, bool) and isinstance(self_heal, bool), entry
        assert "." in canonical, f"{canonical!r} is not a dotted path"


def test_a_blocking_gate_must_self_heal():
    """The invariant the two lost days bought.

    A gate that ends the run without a repair path turns any false positive into
    a lost publish day — and this one is deny-by-default over an 18-word
    allow-list, so false positives are measured, not hypothetical.
    """
    offenders = [
        symbol
        for symbol, _canonical, blocking, self_heal in apn.INLINE_PUBLISH_GATES
        if blocking and not self_heal
    ]
    assert not offenders, (
        f"{offenders} block the publish with no self-heal. Wire a deterministic "
        "fixer ahead of the block (see rewind_midword_cells.rewind_post for the "
        "shape), or make the gate advisory. Do not just flip the flag here."
    )


@pytest.mark.parametrize("entry", apn.INLINE_PUBLISH_GATES, ids=lambda e: e[0])
def test_registered_symbol_is_actually_called(entry):
    symbol = entry[0]
    assert symbol in _called_gate_symbols(), (
        f"{symbol!r} is registered as an inline gate but is not called in "
        f"{PUBLISHER.name}. Either the gate was removed (drop the row) or it was "
        "renamed (update the row)."
    )


@pytest.mark.parametrize("entry", apn.INLINE_PUBLISH_GATES, ids=lambda e: e[0])
def test_canonical_implementation_resolves(entry):
    """A rename in the implementing module must not leave the registry lying."""
    module_path, _, attribute = entry[1].rpartition(".")
    module = importlib.import_module(module_path)
    assert hasattr(module, attribute), (
        f"{entry[1]} no longer exists, so the registry points at nothing"
    )


def test_the_extractor_finds_the_known_calls():
    """Attack the extractor before trusting the reverse scan.

    If ``GATE_CALL_RE`` stops matching, the reverse test finds zero unregistered
    gates and passes — indistinguishable from a clean repo. These three call
    sites are known to exist, so the extractor must see all of them.
    """
    found = _called_gate_symbols()
    assert len(found) >= 3, f"the extractor collapsed to {found}"
    assert _registered_symbols() <= found, (
        f"the extractor misses registered gates: {_registered_symbols() - found}"
    )


def test_every_gate_shaped_call_is_registered():
    """The reverse direction: no unregistered inline gate."""
    unregistered = _called_gate_symbols() - _registered_symbols() - NOT_A_GATE
    assert not unregistered, (
        f"gate-shaped calls in {PUBLISHER.name} that INLINE_PUBLISH_GATES does "
        f"not describe: {sorted(unregistered)}. Add a row (with its blocking and "
        "self-heal flags) or, if it is not a publish gate, add it to NOT_A_GATE "
        "with a comment saying why."
    )


def test_publish_terminating_statements_belong_to_the_blocking_gate():
    """Only a registered blocking gate may end the run.

    A new blocker has to add a `sys.exit` or delete the post, so pinning those
    statements catches a gate that was added without touching the registry — the
    case the symbol scan above would miss if the new gate had an unusual name.
    """
    source = _publisher_source()
    terminators = [
        (m.start(), m.group(0))
        for m in re.finditer(r"sys\.exit\(|post_path\.unlink\(", source)
    ]
    blocking = [e for e in apn.INLINE_PUBLISH_GATES if e[2]]
    assert blocking, "no blocking gate is registered, yet the publisher can exit"

    # Each blocking gate rejects the same way: preserve the draft, delete it,
    # exit 1. So two terminators per blocking gate. This is what catches a new
    # blocker whose name the symbol scan above would not recognise — blocking
    # requires ending the run, and ending the run requires one of these.
    assert len(terminators) == 2 * len(blocking), (
        f"expected {2 * len(blocking)} publish-terminating statements (one "
        f"unlink + one exit for each of {[b[0] for b in blocking]}), found "
        f"{len(terminators)}: {[t[1] for t in terminators]}. A new one means a "
        "new blocking path — register it and give it a self-heal."
    )

    call_sites = []
    for symbol, _canonical, _blocking, _heal in blocking:
        pos = source.find(f"{symbol}(post_path")
        assert pos != -1, f"{symbol}'s call site moved; re-anchor this guard"
        call_sites.append(pos)
    assert all(pos > min(call_sites) for pos, _ in terminators), (
        "a publish-terminating statement runs before every blocking gate, so it "
        "cannot be attributed to one"
    )


def test_the_workflow_points_at_the_registry():
    """The whole problem was that the workflow gave no hint these exist."""
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "INLINE_PUBLISH_GATES" in text, (
        "ai-blogwatcher.yml no longer names INLINE_PUBLISH_GATES. Someone "
        "reading the workflow would again have no way to know that a gate which "
        "deletes the draft runs inside the publish step."
    )

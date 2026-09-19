#!/usr/bin/env python3
"""Ask whether a source-reading guard is satisfied by prose rather than code.

The failure this answers
------------------------
A guard that asserts ``"X" in source_file_text`` cannot tell a real occurrence
of ``X`` from a comment *about* ``X``. Three instances landed on 2026-09-18:

* ``check_secret_contract.code_consumers`` counted the comments explaining why
  ``PAGESPEED_API_KEY`` was removed as three consumers, so the contract reported
  0 violations for a secret with none.
* The first draft of ``test_ci_ops_failure_issue_inlines_report`` failed against
  a CORRECT workflow, because its own comment quoted the old bug verbatim.
* The first draft of ``test_gemini_image_flag_defaults`` passed against the
  reintroduced bug, because the string it searched for also appears in a log
  line.

Why this is a script and not a CI gate
--------------------------------------
Running it over every guard on 2026-09-18 found **zero** vacuous guards. The two
that the mechanical classifier flagged turned out to be deliberate:
``test_inline_gate_registry.test_the_workflow_points_at_the_registry`` asserts
that the workflow *comment* names the registry ("the whole problem was that the
workflow gave no hint these exist"), and
``test_sentry_csp_volume.test_docstring_records_why_401_403_is_not_fail_closed``
asserts on ``mod.__doc__`` by name. Documentation is legitimately the subject
sometimes, and a gate would need an allow-list to say so — which is the thing
that rots. So: a tool you run, not a check that runs itself.

Method
------
For each (test, target, literal) triple: confirm the test passes, then replace
the literal ONLY where it sits inside a comment or docstring, and re-run. If the
test now fails, the assertion was reading prose.

The control matters. A probe without one reports whatever the harness does — see
``notes/`` on the two PRs where a temp-file basename produced a fake CAUGHT.

Column accuracy matters too. A first pass here classified
``DEFAULT_THRESHOLD_PCT = 0.5  # max % of pixels that may differ`` as a comment
because the LINE contains one, and produced four false positives that way. The
span check below is per-column.

Usage
-----
    python3 scripts/dev/probe_guard_vacuity.py --scan
    python3 scripts/dev/probe_guard_vacuity.py \\
        --test scripts/tests/test_x.py --target scripts/y.py --literal "--flag"
"""

from __future__ import annotations

import argparse
import ast
import collections
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.lib import source_text  # noqa: E402

TESTS_DIR = REPO_ROOT / "scripts" / "tests"
SOURCE_SUFFIXES = (".py", ".yml", ".yaml", ".sh")


def blank_noncode(path: Path, literal: str) -> tuple[str, int]:
    """Replace `literal` with same-length filler only at non-code positions.

    Uses the one shared fold in `scripts/lib/source_text` (2026-09-19), so this
    tool and the guards it audits agree on what "code" means. Seven private
    copies of that idea did not agree, which is what the consolidation fixed.
    """
    text = path.read_text(encoding="utf-8")
    try:
        spans = source_text.noncode_spans(text, suffix=path.suffix)
    except SyntaxError:
        # A visible skip, not a quietly weaker fold. An unparseable file cannot
        # be classified, and pretending otherwise is the defect this tool hunts.
        return text, 0
    out, changed = list(text), 0
    for start, end in spans:
        offset = 0
        region = text[start:end]
        while True:
            j = region.find(literal, offset)
            if j < 0:
                break
            for k in range(start + j, min(start + j + len(literal), len(out))):
                if out[k] != "\n":
                    out[k] = "░"
            changed += 1
            offset = j + 1
    return "".join(out), changed


def _passes(test: Path) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test), "-q", "--tb=no"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return proc.returncode == 0


def probe(test: Path, target: Path, literal: str) -> str:
    if not _passes(test):
        return "CONTROL FAILED — the test does not pass unmutated; fix that first"
    mutated, changed = blank_noncode(target, literal)
    if changed == 0:
        return "n/a — the literal never appears in a comment or docstring"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(mutated, encoding="utf-8")
        still_passes = _passes(test)
    finally:
        target.write_text(original, encoding="utf-8")
    if still_passes:
        return f"OK — reads code (blanked {changed} prose occurrence(s), still passes)"
    return (
        f"VACUOUS — blanking {changed} prose occurrence(s) alone breaks the test. "
        "Either strip comments before asserting, or say in the test name that "
        "documentation IS the subject (both legitimate cases on 2026-09-18 did)."
    )


# Words in a test's own name that declare documentation to be the subject.
# Both legitimate hits on 2026-09-18 said so: `test_docstring_records_why_...`
# and `test_the_workflow_points_at_the_registry`. This annotates, it does not
# suppress — an allow-list of files would rot, a naming convention is visible at
# the call site.
_DOC_INTENT = ("docstring", "doc_", "_doc", "comment", "points_at", "names_")


def _enclosing_test(tree: ast.AST, lineno: int) -> str:
    best = ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = node.end_lineno or node.lineno
            if node.lineno <= lineno <= end:
                best = node.name
    return best


def candidates() -> list[tuple[Path, Path, str, str]]:
    """(test, target, literal) triples worth probing.

    A triple qualifies when a test asserts a literal substring and that literal
    appears in a repo source file the test references — but ONLY at non-code
    positions. Anything with a code occurrence needs no probe.
    """
    found: list[tuple[Path, Path, str, str]] = []
    for test in sorted(TESTS_DIR.rglob("test_*.py")):
        try:
            tree = ast.parse(test.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        targets: set[Path] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.BinOp):
                try:
                    expr = ast.unparse(node.value)
                except Exception:
                    continue
                parts = [a or b for a, b in re.findall(r"'([^']+)'|\"([^\"]+)\"", expr)]
                if parts and any(str(p).endswith(SOURCE_SUFFIXES) for p in parts):
                    cand = REPO_ROOT.joinpath(*parts)
                    if cand.is_file():
                        targets.add(cand)
        if not targets:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            for cmp_node in ast.walk(node.test):
                if not (isinstance(cmp_node, ast.Compare) and cmp_node.ops):
                    continue
                if not isinstance(cmp_node.ops[0], ast.In):
                    continue
                left = cmp_node.left
                if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
                    continue
                if len(left.value) < 5:
                    continue
                for target in targets:
                    _, changed = blank_noncode(target, left.value)
                    if not changed:
                        continue
                    text = target.read_text(encoding="utf-8")
                    mutated, _ = blank_noncode(target, left.value)
                    # a code occurrence survives the blanking
                    if text.count(left.value) == mutated.count(left.value) + changed:
                        if mutated.count(left.value) == 0:
                            found.append(
                                (
                                    test,
                                    target,
                                    left.value,
                                    _enclosing_test(tree, node.lineno),
                                )
                            )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", action="store_true", help="probe every candidate")
    parser.add_argument("--test", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--literal")
    args = parser.parse_args(argv)

    if args.test and args.target and args.literal:
        print(probe(args.test, args.target, args.literal))
        return 0

    if not args.scan:
        parser.error("pass --scan, or all of --test/--target/--literal")

    triples = candidates()
    print(f"{len(triples)} candidate(s) — literal present only in prose\n")
    vacuous, declared = 0, 0
    for test, target, literal, func in triples:
        verdict = probe(test, target, literal)
        if verdict.startswith("VACUOUS"):
            if any(word in func for word in _DOC_INTENT):
                declared += 1
                verdict += (
                    f"\n    …but `{func}` names documentation as its subject — "
                    "read the test before changing anything."
                )
            else:
                vacuous += 1
        print(
            f"{test.name}::{func}\n    {target.relative_to(REPO_ROOT)}  "
            f"{literal!r}\n    {verdict}\n"
        )
    print(
        f"vacuous: {vacuous} / {len(triples)}  "
        f"(plus {declared} that declare documentation as the subject)"
    )
    return 1 if vacuous else 0


if __name__ == "__main__":
    sys.exit(main())

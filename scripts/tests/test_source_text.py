#!/usr/bin/env python3
"""The shared "what counts as code" fold, pinned in both directions.

`scripts/lib/source_text` replaced seven private copies on 2026-09-19. Fed the
same snippet, those copies split into two families and neither matched what its
callers assumed:

    token in sample                     line-prefix (4x)   tokenize (2x)
    docstring mention                   kept               blanked
    trailing `# comment` mention        kept               blanked
    inside "a # not-a-comment string"   kept               blanked
    whole-line `# comment`              blanked            blanked

Both directions are dangerous and this file pins both:

* Under-folding lets prose satisfy a guard. Measured three times on 2026-09-18 —
  removal-rationale comments counted as secret consumers, a guard failed against
  a correct workflow because its own comment quoted the old bug, and a guard
  passed against a reintroduced bug because the string was also in a log line.
* Over-folding is worse. Blanking functional string literals would make
  `test_api_key_not_in_url` (the URL is built in an f-string) and
  `test_ci_python_lint_gate` (`run_command(["ruff", "--fix"])`) vacuous, and
  would let `code_consumers` declare a live credential unused.

Hence two functions rather than one, named for what they mean.
"""

from __future__ import annotations

import pytest

from scripts.lib.source_text import code_tokens_only, noncode_spans, without_comments

SAMPLE = '''"""Module doc mentions TOKEN_DOC."""
X = 1  # TOKEN_TRAILING
S = "a # not-a-comment TOKEN_INSTRING"
# TOKEN_WHOLELINE
URL = "https://example.test/y"  # TOKEN_URLTRAILING


def f():
    """Inner doc TOKEN_INNERDOC."""
    return "TOKEN_RETURNED"
'''

# What each function must do with each token. This table IS the contract.
_WITHOUT_COMMENTS = {
    "TOKEN_DOC": False,
    "TOKEN_TRAILING": False,
    "TOKEN_INSTRING": True,
    "TOKEN_WHOLELINE": False,
    "TOKEN_URLTRAILING": False,
    "TOKEN_INNERDOC": False,
    "TOKEN_RETURNED": True,
}
_CODE_TOKENS_ONLY = dict.fromkeys(_WITHOUT_COMMENTS, False)


@pytest.mark.parametrize("token,kept", sorted(_WITHOUT_COMMENTS.items()))
def test_without_comments_keeps_the_program(token: str, kept: bool) -> None:
    """Commentary out, string literals in."""
    assert (token in without_comments(SAMPLE)) is kept, (
        f"{token}: expected kept={kept}. Keeping a docstring or trailing comment "
        "lets prose satisfy a guard; dropping a real string literal makes guards "
        "that look for flags or URLs vacuous."
    )


@pytest.mark.parametrize("token,kept", sorted(_CODE_TOKENS_ONLY.items()))
def test_code_tokens_only_drops_every_literal(token: str, kept: bool) -> None:
    """For guards where a string would be a false positive (`symbol(` hunting)."""
    assert (token in code_tokens_only(SAMPLE)) is kept


def test_the_two_functions_actually_differ() -> None:
    """A refactor that made them aliases would silently break one family."""
    assert without_comments(SAMPLE) != code_tokens_only(SAMPLE), (
        "without_comments and code_tokens_only produced identical output. They "
        "serve opposite call sites — one keeps string literals on purpose."
    )


@pytest.mark.parametrize("fold", [without_comments, code_tokens_only])
def test_offsets_and_line_numbers_survive(fold) -> None:
    """Same-length blanking, because callers report positions.

    `test_inline_gate_registry` orders call sites by character offset and
    `test_api_key_not_in_url` prints line numbers to the developer.
    """
    folded = fold(SAMPLE)
    assert len(folded) == len(SAMPLE)
    assert folded.count("\n") == SAMPLE.count("\n")
    assert folded.splitlines()[1].startswith("X = 1"), "code itself must be intact"


def test_yaml_drops_hash_and_slash_comment_lines() -> None:
    """Workflows embed JS via actions/github-script; `//` is commentary there.

    This is the exact shape that made a guard fail against a correct workflow:
    the comment explaining the old bug quoted it verbatim.
    """
    yaml_text = "\n".join(
        [
            "jobs:",
            "  a:",
            "    # TOKEN_YAMLCOMMENT explaining the old bug",
            "    run: echo TOKEN_YAMLCODE",
            "    script: |",
            "      // TOKEN_JSCOMMENT",
            "      const x = 'TOKEN_JSCODE';",
        ]
    )
    folded = without_comments(yaml_text, suffix=".yml")
    assert "TOKEN_YAMLCOMMENT" not in folded
    assert "TOKEN_JSCOMMENT" not in folded
    assert "TOKEN_YAMLCODE" in folded
    assert "TOKEN_JSCODE" in folded


def test_yaml_keeps_trailing_hash() -> None:
    """A `#` mid-line in YAML is often data, not a comment.

    Guessing otherwise silently blanks real config — a URL fragment, a colour,
    a shell command. Whole-line only is the defensible rule here.
    """
    folded = without_comments(
        "    run: curl 'https://x/y#frag' # TOKEN_T", suffix=".yml"
    )
    assert "https://x/y#frag" in folded


def test_unparseable_python_raises_rather_than_degrading() -> None:
    """No silent fallback to a weaker fold.

    A guard helper that quietly drops to whole-line matching would let its
    caller keep passing while checking less than it thinks — the failure this
    module exists to end. Callers that legitimately sweep unparseable files
    (`scripts/dev/probe_guard_vacuity.py`) catch this at their own call site.
    """
    with pytest.raises(SyntaxError):
        without_comments("def broken(:\n    pass\n")


def test_code_consumers_uses_this_fold() -> None:
    """The contract checker and this module must not drift apart.

    `check_secret_contract` had its own copy until 2026-09-19, and the gap it
    left — docstrings counted as code — broke the very guard written to catch
    prose-as-consumer.
    """
    import check_secret_contract as contract

    source = __import__("pathlib").Path(contract.__file__).read_text(encoding="utf-8")
    assert "without_comments" in source, (
        "check_secret_contract no longer uses the shared fold. Two folds that "
        "agree today are two folds that will disagree later."
    )

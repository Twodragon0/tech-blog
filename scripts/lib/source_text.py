#!/usr/bin/env python3
"""One fold for "which part of this source file is actually code".

Why this exists
---------------
Seven copies of this idea were in the tree on 2026-09-19, and they did not agree.
Fed the same snippet, they split into two families and neither matched what its
callers assumed:

    sample                                    line-prefix    tokenize
    \"\"\"Docstring mentions TOKEN.\"\"\"            kept           blanked
    X = 1  # TOKEN trailing comment           kept           blanked
    S = "a # not-a-comment TOKEN"             kept           blanked
    # TOKEN whole-line comment                blanked        blanked

The line-prefix family missed trailing comments and docstrings — the exact trap
this audit's own classifier fell into, reading
``DEFAULT_THRESHOLD_PCT = 0.5  # max % of pixels`` as a comment line. The
tokenize family blanked functional string literals too, which is right for some
guards and wrong for others.

So the answer is not one function. It is two, named for what they mean:

* :func:`without_comments` — drop commentary, keep the program. Use when the
  thing you are looking for legitimately lives in a string: a CLI flag
  (``add_argument("--staged")``), a URL, a workflow command.
* :func:`code_tokens_only` — drop commentary AND every string literal. Use when
  a string would be a false positive: searching for ``symbol(`` call sites, or
  for a pattern that prose and sample data also contain.

Both blank in place with spaces, so line numbers and column offsets survive.
``test_inline_gate_registry`` depends on that for an ordering assertion, and
``test_api_key_not_in_url`` reports line numbers to the developer.

This is the same rule the repo already learned about generators and gates: the
producer and the checker must share one fold, not two functions that agree today.
"""

from __future__ import annotations

import ast
import io
import tokenize

__all__ = ["without_comments", "code_tokens_only", "noncode_spans"]

_FILLER = " "


def _blank(text: str, spans: list[tuple[int, int]]) -> str:
    """Replace each (start, end) character span with spaces of equal length."""
    if not spans:
        return text
    out = list(text)
    for start, end in spans:
        for i in range(start, min(end, len(out))):
            if out[i] != "\n":
                out[i] = _FILLER
    return "".join(out)


def _line_offsets(text: str) -> list[int]:
    offsets, pos = [0], 0
    for line in text.splitlines(keepends=True):
        pos += len(line)
        offsets.append(pos)
    return offsets


def _python_spans(text: str, *, strings: bool) -> list[tuple[int, int]]:
    """Character spans of comments, docstrings and optionally all strings."""
    offsets = _line_offsets(text)

    def at(row: int, col: int) -> int:
        return offsets[row - 1] + col if 0 < row <= len(offsets) else len(text)

    # No fallback on a tokenize/parse error. A guard helper that silently
    # degrades to a weaker fold is the failure this module exists to end: the
    # caller would keep passing while checking less than it thinks. Callers that
    # legitimately sweep unparseable files (scripts/dev/probe_guard_vacuity.py)
    # catch SyntaxError at their own call site, where the skip is visible.
    # One exception type out of this module. `tokenize.TokenError` is NOT a
    # subclass of SyntaxError (3.13 measured), so a caller writing the obvious
    # `except SyntaxError` would crash on an unterminated string instead of
    # skipping the file — found while writing this module's own tests.
    spans: list[tuple[int, int]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT or (
                strings and tok.type == tokenize.STRING
            ):
                spans.append((at(*tok.start), at(*tok.end)))
    except tokenize.TokenError as exc:
        raise SyntaxError(f"cannot tokenize source: {exc}") from exc

    if not strings:
        # Docstrings only — a bare string STATEMENT. A string that is assigned,
        # passed or returned is data and must survive.
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                end_row = node.end_lineno or node.lineno
                end_col = node.end_col_offset or 0
                spans.append((at(node.lineno, node.col_offset), at(end_row, end_col)))
    return spans


def _hash_comment_spans(text: str) -> list[tuple[int, int]]:
    """Whole-line ``#`` comments — for YAML, shell and friends.

    Deliberately not trailing ``#``: in YAML a ``#`` inside a quoted scalar or a
    ``run:`` block is data, and guessing wrong here silently blanks real config.
    """
    offsets = _line_offsets(text)
    spans = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            spans.append(
                (offsets[i] + (len(line) - len(stripped)), offsets[i] + len(line))
            )
    return spans


def _slash_comment_spans(text: str) -> list[tuple[int, int]]:
    """Whole-line ``//`` / ``*`` comments — embedded JS, CSS-ish blocks."""
    offsets = _line_offsets(text)
    spans = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.lstrip()
        if stripped.startswith(("//", "*", "/*")):
            spans.append(
                (offsets[i] + (len(line) - len(stripped)), offsets[i] + len(line))
            )
    return spans


def noncode_spans(text: str, *, suffix: str = ".py") -> list[tuple[int, int]]:
    """Character spans that are commentary rather than program."""
    if suffix == ".py":
        return _python_spans(text, strings=False)
    spans = _hash_comment_spans(text)
    if suffix in {".yml", ".yaml", ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx"}:
        # A workflow can embed JS (actions/github-script), and api/ is JS, so
        # `//` lines are commentary in both. This is exactly how a guard's own
        # explanation of a bug got mistaken for the bug on ops-orchestrator.yml,
        # 2026-09-18. `#` stays included for the YAML half of a mixed file.
        spans += _slash_comment_spans(text)
    return spans


def without_comments(text: str, *, suffix: str = ".py") -> str:
    """Blank comments and docstrings; keep every other string literal.

    Use when the thing you search for can legitimately live in a string.
    """
    return _blank(text, noncode_spans(text, suffix=suffix))


def code_tokens_only(text: str) -> str:
    """Blank comments AND all string literals. Python only.

    Use when a string would be a false positive — searching for ``symbol(``
    call sites, or for a pattern that sample data in the file also contains.
    """
    return _blank(text, _python_spans(text, strings=True))

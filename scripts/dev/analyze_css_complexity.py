#!/usr/bin/env python3
"""Analyze a compiled CSS bundle for selector complexity hot-spots.

Reads the compiled stylesheet (default: ``_site/assets/css/main.css``) and emits
a Markdown summary suitable for performance audits. Reports:

* Total rule count and average / max selector specificity (a, b, c tuple).
* Longest selector (string length) and the longest descendant chain.
* Universal selector (`*`) count combined with descendant combinators.
* `:nth-*` / `:nth-of-type` / `:nth-last-*` usage count.
* Attribute selectors with substring/regex matchers (``[class*=]`` etc.).
* `:has()` selector count (still relatively expensive when broad).

Usage::

    python3 scripts/dev/analyze_css_complexity.py
    python3 scripts/dev/analyze_css_complexity.py --input _site/assets/css/post.css

Pure stdlib — no external dependencies. Designed for static analysis runs;
does not parse or execute CSS, just lexes the selector portion of each rule.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

DEFAULT_INPUT = Path("_site/assets/css/main.css")

# Strip comments and at-rule blocks we don't want to count as rules.
# Conservative regex: works on minified or pretty-printed CSS.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
# Capture selector list followed by a `{`. We deliberately do NOT match
# nested braces (CSS doesn't have them outside ``@`` blocks we ignore).
_RULE_RE = re.compile(r"([^{}]+)\{[^{}]*\}")
# Detect at-rule preludes like ``@media (min-width: 600px) {``; we scan their
# bodies normally because they wrap real rules.
_AT_RULE_RE = re.compile(r"@[\w-]+\s*[^{};]*\{")

_NTH_RE = re.compile(r":nth-(?:child|of-type|last-child|last-of-type)\(")
_HAS_RE = re.compile(r":has\(")
_ATTR_REGEX_RE = re.compile(r"\[[^\]=]+[*^$|~]=")
_UNIVERSAL_RE = re.compile(r"(^|\s|>|~|\+)\*(\s|>|~|\+|$)")
# Pseudo-class / pseudo-element list for specificity scoring.
_PSEUDO_ELEMENT_RE = re.compile(r"::[\w-]+")
_PSEUDO_CLASS_RE = re.compile(r":(?!:)[\w-]+(?:\([^)]*\))?")
_ID_RE = re.compile(r"#[\w-]+")
_CLASS_RE = re.compile(r"\.[\w-]+")
_ATTR_RE = re.compile(r"\[[^\]]+\]")
_TYPE_RE = re.compile(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)")


@dataclass
class CssStats:
    rule_count: int = 0
    selector_count: int = 0  # selectors after splitting comma lists
    longest_selector: str = ""
    longest_descendant_chain: int = 0
    longest_descendant_example: str = ""
    universal_descendant: int = 0
    nth_count: int = 0
    has_count: int = 0
    attr_regex_count: int = 0
    spec_sum: tuple[int, int, int] = (0, 0, 0)
    spec_max: tuple[int, int, int] = (0, 0, 0)
    spec_max_selector: str = ""
    examples: dict[str, list[str]] = field(default_factory=dict)


def _strip_comments(css: str) -> str:
    return _COMMENT_RE.sub("", css)


def _iter_rules(css: str) -> Iterable[str]:
    """Yield raw selector text for each declaration block.

    Handles nested at-rules by stripping their headers (``@media …{``) and
    matching the wrapped rules normally. We rely on the fact that the
    project's compiled CSS does not use CSS Nesting (``&``) — at-rules
    contain plain rules.
    """
    text = _strip_comments(css)
    # Remove ``@media (...) {`` style headers and their matching close brace.
    # Easier: replace at-rule headers with empty string so the inner block is
    # exposed to ``_RULE_RE``. The outer ``}`` is harmless because the regex
    # only matches non-brace selectors.
    text = _AT_RULE_RE.sub("", text)
    for match in _RULE_RE.finditer(text):
        yield match.group(1)


def _split_selector_list(selector_block: str) -> list[str]:
    # Selector list separated by commas, ignoring commas inside ``()``.
    out: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in selector_block:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            piece = "".join(current).strip()
            if piece:
                out.append(piece)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        out.append(tail)
    return out


def _count_specificity(selector: str) -> tuple[int, int, int]:
    """Return (a, b, c) per CSS Selectors Level 3 specificity rules.

    Approximation: ignores ``:not()`` / ``:is()`` / ``:where()`` argument
    descent. Good enough for ranking, not for browser reproduction.
    """
    work = _PSEUDO_ELEMENT_RE.sub(" ", selector)
    a = len(_ID_RE.findall(work))
    work = _ID_RE.sub(" ", work)
    classes = len(_CLASS_RE.findall(work))
    work = _CLASS_RE.sub(" ", work)
    attrs = len(_ATTR_RE.findall(work))
    work = _ATTR_RE.sub(" ", work)
    pseudos = len(_PSEUDO_CLASS_RE.findall(work))
    work = _PSEUDO_CLASS_RE.sub(" ", work)
    types = len(_TYPE_RE.findall(work))
    elements = len(re.findall(r"::[\w-]+", selector))
    return a, classes + attrs + pseudos, types + elements


def _descendant_chain_length(selector: str) -> int:
    # Count whitespace-separated compound selectors. Combinators like ``>``
    # ``+`` ``~`` count as descendant boundaries for the purpose of "how many
    # ancestors must the engine walk?".
    flat = re.sub(r"\s*[>+~]\s*", " ", selector.strip())
    parts = [p for p in flat.split() if p]
    return len(parts)


def _record_example(stats: CssStats, key: str, value: str, limit: int = 3) -> None:
    bucket = stats.examples.setdefault(key, [])
    if len(bucket) < limit and value not in bucket:
        bucket.append(value)


def analyze(css_text: str) -> CssStats:
    stats = CssStats()
    for selector_block in _iter_rules(css_text):
        stats.rule_count += 1
        for selector in _split_selector_list(selector_block):
            stats.selector_count += 1

            if len(selector) > len(stats.longest_selector):
                stats.longest_selector = selector

            chain = _descendant_chain_length(selector)
            if chain > stats.longest_descendant_chain:
                stats.longest_descendant_chain = chain
                stats.longest_descendant_example = selector

            spec = _count_specificity(selector)
            stats.spec_sum = (
                stats.spec_sum[0] + spec[0],
                stats.spec_sum[1] + spec[1],
                stats.spec_sum[2] + spec[2],
            )
            if spec > stats.spec_max:
                stats.spec_max = spec
                stats.spec_max_selector = selector

            if _UNIVERSAL_RE.search(selector):
                stats.universal_descendant += 1
                _record_example(stats, "universal", selector)
            n_nth = len(_NTH_RE.findall(selector))
            if n_nth:
                stats.nth_count += n_nth
                _record_example(stats, "nth", selector)
            n_has = len(_HAS_RE.findall(selector))
            if n_has:
                stats.has_count += n_has
                _record_example(stats, "has", selector)
            n_attr = len(_ATTR_REGEX_RE.findall(selector))
            if n_attr:
                stats.attr_regex_count += n_attr
                _record_example(stats, "attr_regex", selector)
    return stats


def render_markdown(stats: CssStats, source: Path) -> str:
    sel_count = stats.selector_count or 1
    avg_spec = (
        stats.spec_sum[0] / sel_count,
        stats.spec_sum[1] / sel_count,
        stats.spec_sum[2] / sel_count,
    )

    def fmt_examples(key: str) -> str:
        ex = stats.examples.get(key, [])
        if not ex:
            return "_(none)_"
        return "<br>".join(f"`{e}`" for e in ex)

    lines = [
        f"# CSS Complexity Report — `{source}`",
        "",
        f"- **Rules**: {stats.rule_count}",
        f"- **Selectors (post-split)**: {stats.selector_count}",
        f"- **Longest selector** ({len(stats.longest_selector)} chars): "
        f"`{stats.longest_selector}`",
        f"- **Longest descendant chain**: {stats.longest_descendant_chain} compound parts",
        f"  - Example: `{stats.longest_descendant_example}`",
        f"- **Average specificity (a, b, c)**: "
        f"({avg_spec[0]:.2f}, {avg_spec[1]:.2f}, {avg_spec[2]:.2f})",
        f"- **Max specificity**: {stats.spec_max} → `{stats.spec_max_selector}`",
        "",
        "## Anti-pattern counts",
        "",
        "| Pattern | Count | Examples |",
        "|---------|-------|----------|",
        f"| `*` with descendant combinator | {stats.universal_descendant} | "
        f"{fmt_examples('universal')} |",
        f"| `:nth-*()` selectors | {stats.nth_count} | {fmt_examples('nth')} |",
        f"| `:has()` selectors | {stats.has_count} | {fmt_examples('has')} |",
        f"| Attribute regex (`[attr*=]` / `[attr^=]` / `[attr$=]`) | "
        f"{stats.attr_regex_count} | {fmt_examples('attr_regex')} |",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help=f"Compiled CSS file to analyze (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional path to write the Markdown report. Prints to stdout if omitted.")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"error: {args.input} not found", file=sys.stderr)
        return 2

    css = args.input.read_text(encoding="utf-8")
    stats = analyze(css)
    md = render_markdown(stats, args.input)
    if args.output:
        args.output.write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

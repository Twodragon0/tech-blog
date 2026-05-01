#!/usr/bin/env python3
"""Count DOM nodes in built HTML pages and report tag-level distribution.

Reads one or more rendered HTML files (typical: ``_site/index.html`` or a
post page) and reports:

* Total element count.
* Per-tag count (top 10 by count).
* Maximum nesting depth.

PageSpeed Insights flags pages with > 1500 DOM nodes as "excessive". This
helper makes it easy to spot which tag (or which Liquid include) is
contributing the most to that budget.

Usage::

    python3 scripts/dev/count_dom_nodes.py _site/index.html
    python3 scripts/dev/count_dom_nodes.py _site/index.html _site/posts/.../index.html

Pure stdlib (uses ``html.parser``).
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class DomCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter[str] = Counter()
        self.total = 0
        self.depth = 0
        self.max_depth = 0
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        self.total += 1
        if tag in VOID_ELEMENTS:
            return
        self._stack.append(tag)
        self.depth = len(self._stack)
        if self.depth > self.max_depth:
            self.max_depth = self.depth

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Self-closing variants like ``<br />``; treat as a single element.
        self.tags[tag] += 1
        self.total += 1

    def handle_endtag(self, tag: str) -> None:
        # Pop until we find the matching tag (handle browser-ish lenient HTML).
        while self._stack:
            popped = self._stack.pop()
            if popped == tag:
                break
        self.depth = len(self._stack)


def analyze_file(path: Path) -> DomCounter:
    counter = DomCounter()
    counter.feed(path.read_text(encoding="utf-8", errors="replace"))
    return counter


def render_report(path: Path, counter: DomCounter) -> str:
    top = counter.tags.most_common(10)
    lines = [
        f"## `{path}`",
        "",
        f"- **Total elements**: {counter.total}",
        f"- **Max nesting depth**: {counter.max_depth}",
        "- **Top 10 tags**:",
    ]
    for tag, count in top:
        lines.append(f"  - `<{tag}>` × {count}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="HTML files to analyze")
    parser.add_argument("--threshold", type=int, default=1500,
                        help="Warn (exit 1) if any page exceeds this node count.")
    args = parser.parse_args(argv)

    over = []
    chunks: list[str] = ["# DOM Node Report", ""]
    for path in args.paths:
        if not path.exists():
            print(f"error: {path} not found", file=sys.stderr)
            return 2
        counter = analyze_file(path)
        chunks.append(render_report(path, counter))
        if counter.total > args.threshold:
            over.append((path, counter.total))

    print("\n".join(chunks))
    if over:
        print("\n**Warnings (over threshold)**:")
        for path, count in over:
            print(f"- {path}: {count} > {args.threshold}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

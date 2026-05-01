#!/usr/bin/env python3
"""Compare Lighthouse LHR JSON reports from two builds and gate on LCP regression.

Inputs are two directories of Lighthouse CLI output (the ``lhci collect`` shape
or ``lighthouse --output=json --output-path=...`` shape). For each URL that
appears in both directories the script computes the median LCP across runs
and compares ``head`` against ``base``.

If any URL's ``head_LCP - base_LCP`` exceeds ``--threshold-lcp-ms`` the
script exits with code 1 and writes a Markdown comparison table summarising
every URL. CLS / TBT / FCP are reported alongside LCP for context but are
informational only — they do not gate.

Usage::

    python3 scripts/dev/compare_lighthouse_runs.py \\
        --base-dir lhci-base --head-dir lhci-head \\
        --threshold-lcp-ms 200 --output-md lighthouse-comparison.md

Designed to be invoked by ``.github/workflows/lighthouse-ci.yml`` after a
``lhci collect`` run on each build, but also runs locally for manual
diagnosis. Pure stdlib — no extra pip dependencies.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

# Lighthouse audit ids we read.
LCP_AUDIT = "largest-contentful-paint"
CLS_AUDIT = "cumulative-layout-shift"
TBT_AUDIT = "total-blocking-time"
FCP_AUDIT = "first-contentful-paint"


def _lhr_files(report_dir: Path) -> list[Path]:
    """Return Lighthouse-report JSON files inside ``report_dir``.

    Matches the ``lhci collect`` output convention (``lhr-<timestamp>.json``)
    and the bare ``lighthouse --output=json --output-path=...`` convention.
    """
    if not report_dir.exists():
        return []
    candidates = list(report_dir.glob("lhr-*.json"))
    if not candidates:
        candidates = [
            p for p in report_dir.glob("*.json")
            if p.name not in {"manifest.json", "links.json"}
        ]
    return sorted(candidates)


def _load_metric(audit_data: dict, audit_id: str) -> float | None:
    """Read ``audits[audit_id].numericValue`` from a parsed LHR dict."""
    audits = audit_data.get("audits", {})
    audit = audits.get(audit_id) or {}
    value = audit.get("numericValue")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _collect_metrics(report_dir: Path) -> dict[str, dict[str, list[float]]]:
    """Group metric samples by URL across every LHR file in ``report_dir``."""
    by_url: dict[str, dict[str, list[float]]] = {}
    for path in _lhr_files(report_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        url = data.get("finalDisplayedUrl") or data.get("finalUrl") or data.get("requestedUrl")
        if not url:
            continue
        bucket = by_url.setdefault(url, {"lcp": [], "cls": [], "tbt": [], "fcp": []})
        for key, audit in (("lcp", LCP_AUDIT), ("cls", CLS_AUDIT), ("tbt", TBT_AUDIT), ("fcp", FCP_AUDIT)):
            metric = _load_metric(data, audit)
            if metric is not None:
                bucket[key].append(metric)
    return by_url


def _median(samples: list[float]) -> float | None:
    return statistics.median(samples) if samples else None


def _normalise_url(url: str) -> str:
    """Strip the localhost scheme+host so ``http://localhost:4000/foo/`` and
    ``http://127.0.0.1:4000/foo/`` compare equal across base/head runs."""
    for prefix in ("http://localhost:4000", "http://127.0.0.1:4000", "http://localhost", "http://127.0.0.1"):
        if url.startswith(prefix):
            return url[len(prefix):] or "/"
    return url


def _format_ms(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.0f} ms"


def _format_unitless(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def compare(base_dir: Path, head_dir: Path, threshold_ms: float) -> tuple[list[dict], int]:
    """Compute per-URL deltas. Returns (rows, exit_code)."""
    base_metrics = _collect_metrics(base_dir)
    head_metrics = _collect_metrics(head_dir)

    base_norm = {_normalise_url(u): v for u, v in base_metrics.items()}
    head_norm = {_normalise_url(u): v for u, v in head_metrics.items()}

    urls = sorted(set(base_norm) & set(head_norm))
    rows: list[dict] = []
    failed = False
    for url in urls:
        base_lcp = _median(base_norm[url]["lcp"])
        head_lcp = _median(head_norm[url]["lcp"])
        delta = None
        verdict = "skip"
        if base_lcp is not None and head_lcp is not None:
            delta = head_lcp - base_lcp
            if delta > threshold_ms:
                verdict = f"FAIL (+{threshold_ms:.0f}ms threshold)"
                failed = True
            else:
                verdict = "PASS"
        rows.append({
            "url": url,
            "base_lcp": base_lcp,
            "head_lcp": head_lcp,
            "delta_lcp": delta,
            "base_cls": _median(base_norm[url]["cls"]),
            "head_cls": _median(head_norm[url]["cls"]),
            "base_tbt": _median(base_norm[url]["tbt"]),
            "head_tbt": _median(head_norm[url]["tbt"]),
            "base_fcp": _median(base_norm[url]["fcp"]),
            "head_fcp": _median(head_norm[url]["fcp"]),
            "verdict": verdict,
        })
    return rows, (1 if failed else 0)


def render_markdown(rows: list[dict], threshold_ms: float) -> str:
    """Render a Markdown report of the comparison."""
    lines = [
        "# Lighthouse perf gate",
        "",
        f"LCP regression threshold: **+{threshold_ms:.0f} ms** (head vs base, median of N runs).",
        "CLS, TBT, FCP shown for context only — they are not gating.",
        "",
        "| URL | Base LCP | Head LCP | Δ LCP | Δ CLS | Δ TBT | Verdict |",
        "|-----|----------|----------|-------|-------|-------|---------|",
    ]
    for row in rows:
        delta_lcp = row["delta_lcp"]
        delta_cls = (
            row["head_cls"] - row["base_cls"]
            if row["head_cls"] is not None and row["base_cls"] is not None
            else None
        )
        delta_tbt = (
            row["head_tbt"] - row["base_tbt"]
            if row["head_tbt"] is not None and row["base_tbt"] is not None
            else None
        )
        delta_lcp_str = "n/a" if delta_lcp is None else f"{delta_lcp:+.0f} ms"
        delta_cls_str = "n/a" if delta_cls is None else f"{delta_cls:+.3f}"
        delta_tbt_str = "n/a" if delta_tbt is None else f"{delta_tbt:+.0f} ms"
        lines.append(
            "| {url} | {base_lcp} | {head_lcp} | {delta_lcp} | {delta_cls} | {delta_tbt} | {verdict} |".format(
                url=row["url"],
                base_lcp=_format_ms(row["base_lcp"]),
                head_lcp=_format_ms(row["head_lcp"]),
                delta_lcp=delta_lcp_str,
                delta_cls=delta_cls_str,
                delta_tbt=delta_tbt_str,
                verdict=row["verdict"],
            )
        )
    if not rows:
        lines.append("| (no comparable URLs found) |  |  |  |  |  |  |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, required=True, help="Directory of base-branch LHR JSON files")
    parser.add_argument("--head-dir", type=Path, required=True, help="Directory of head-branch LHR JSON files")
    parser.add_argument(
        "--threshold-lcp-ms",
        type=float,
        default=200.0,
        help="Fail if head_LCP - base_LCP exceeds this (default: 200 ms)",
    )
    parser.add_argument("--output-md", type=Path, default=None, help="Optional Markdown output path")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout summary")
    args = parser.parse_args()

    rows, exit_code = compare(args.base_dir, args.head_dir, args.threshold_lcp_ms)
    md = render_markdown(rows, args.threshold_lcp_ms)
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(md, encoding="utf-8")
    if not args.quiet:
        print(md)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

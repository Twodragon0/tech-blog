#!/usr/bin/env python3
"""
L20 Visual Regression Sweep
Renders 31 L20 Hero+2-Card weekly-digest cover SVGs + 1 reference to PNG,
computes perceptual hashes, and writes REPORT.md.

Flags:
  --strict          Exit 1 if any cover has Hamming > threshold (default: exit 0)
  --threshold N     Hamming distance threshold for --strict mode (default: 25)
"""

import argparse
import os
import sys
import hashlib
import subprocess
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# PIL
from PIL import Image
import io

# --- Config ---
REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[2]))
ASSETS = REPO_ROOT / "assets" / "images"
OUT_DIR = REPO_ROOT / "reports" / "l20-visual-regression"
PNG_DIR = OUT_DIR / "png"
REPORT_FILE = OUT_DIR / "REPORT.md"
# Prefer env var, then detect via 'which', fall back to macOS Homebrew path
_RSVG_ENV = os.environ.get("RSVG_CONVERT", "")
if _RSVG_ENV:
    RSVG = _RSVG_ENV
else:
    import shutil
    RSVG = shutil.which("rsvg-convert") or "/opt/homebrew/bin/rsvg-convert"
WIDTH, HEIGHT = 1200, 630
MAX_WORKERS = 4

# --- Target file lists ---
REFERENCE_NAME = "2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg"

TARGET_DATES_MAR = [
    "2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20",
    "2026-03-21", "2026-03-22", "2026-03-23", "2026-03-24", "2026-03-25",
    "2026-03-26", "2026-03-27", "2026-03-28", "2026-03-29", "2026-03-31",
]
TARGET_DATES_JANFEB = [
    "2026-01-23", "2026-01-25", "2026-01-29",
    "2026-02-01", "2026-02-04", "2026-02-05", "2026-02-07", "2026-02-08",
    "2026-02-11", "2026-02-12", "2026-02-13", "2026-02-17",
    "2026-02-20", "2026-02-21", "2026-02-22",
]
ALL_TARGET_DATES = set(TARGET_DATES_MAR + TARGET_DATES_JANFEB)


def collect_files():
    """Return (reference_path, [target_paths]) sorted."""
    svgs = sorted(ASSETS.glob("*.svg"))
    reference = None
    targets = []
    for svg in svgs:
        bn = svg.name
        if "Tech_Security_Weekly_Digest" not in bn:
            continue
        date = bn[:10]
        if bn == REFERENCE_NAME:
            reference = svg
        elif date in ALL_TARGET_DATES:
            targets.append(svg)
    return reference, targets


def render_svg_to_png(svg_path: Path, png_path: Path) -> str | None:
    """Render SVG to PNG via rsvg-convert. Returns error message or None on success."""
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [RSVG, "-w", str(WIDTH), "-h", str(HEIGHT), "-f", "png",
           str(svg_path), "-o", str(png_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            return result.stderr.decode("utf-8", errors="replace").strip()
        return None
    except subprocess.TimeoutExpired:
        return "rsvg-convert timeout"
    except Exception as e:
        return str(e)


def compute_phash(img: Image.Image) -> int:
    """8x8 perceptual hash: resize to 8x8 grayscale, compare each pixel to mean."""
    small = img.convert("L").resize((8, 8), Image.LANCZOS)
    pixels = list(small.getdata())
    mean = sum(pixels) / len(pixels)
    bits = 0
    for i, p in enumerate(pixels):
        if p >= mean:
            bits |= (1 << i)
    return bits


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def phash_hex(h: int) -> str:
    return f"{h:016x}"


def analyze_png(png_path: Path) -> dict:
    """Compute metrics from a rendered PNG."""
    data = png_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    size_kb = len(data) / 1024
    img = Image.open(io.BytesIO(data)).convert("RGB")
    # Average color
    px = list(img.getdata())
    n = len(px)
    avg_r = sum(p[0] for p in px) // n
    avg_g = sum(p[1] for p in px) // n
    avg_b = sum(p[2] for p in px) // n
    avg_color = f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
    ph = compute_phash(img)
    return {
        "sha256": sha256[:16],
        "size_kb": round(size_kb, 1),
        "avg_color": avg_color,
        "phash": ph,
    }


def categorize(dist: int) -> str:
    if dist <= 12:
        return "tight"
    elif dist <= 25:
        return "near"
    else:
        return "deviation"


def render_one(svg_path: Path) -> tuple[Path, str | None]:
    png_name = svg_path.stem + ".png"
    png_path = PNG_DIR / png_name
    err = render_svg_to_png(svg_path, png_path)
    return png_path, err


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="L20 Visual Regression Sweep")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit 1 if any cover has Hamming distance > threshold",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=25,
        metavar="N",
        help="Hamming distance threshold for --strict mode (default: 25)",
    )
    return parser.parse_args()


def check_strict_gate(rows: list[dict], threshold: int) -> list[dict]:
    """Return list of outlier rows with Hamming > threshold (excluding the reference).

    This is a pure function used both by main() and the test suite.
    """
    return [r for r in rows if r["hamming"] > threshold and not r["is_ref"]]


def main():
    args = parse_args()
    threshold = args.threshold

    PNG_DIR.mkdir(parents=True, exist_ok=True)

    reference_svg, target_svgs = collect_files()
    if reference_svg is None:
        print("ERROR: reference SVG not found!", file=sys.stderr)
        sys.exit(1)

    all_svgs = [reference_svg] + target_svgs
    print(f"Found: 1 reference + {len(target_svgs)} targets = {len(all_svgs)} total")

    # --- Parallel render ---
    print(f"Rendering {len(all_svgs)} SVGs at {WIDTH}x{HEIGHT}px (workers={MAX_WORKERS})...")
    render_errors = {}
    render_results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(render_one, svg): svg for svg in all_svgs}
        for i, future in enumerate(as_completed(futures), 1):
            svg = futures[future]
            png_path, err = future.result()
            if err:
                render_errors[svg.name] = err
                print(f"  [{i}/{len(all_svgs)}] FAIL {svg.name}: {err}")
            else:
                render_results[svg.name] = png_path
                print(f"  [{i}/{len(all_svgs)}] OK   {svg.name}")

    # --- Analyze reference ---
    ref_png = render_results.get(reference_svg.name)
    if ref_png is None:
        print(f"ERROR: reference render failed: {render_errors.get(reference_svg.name)}", file=sys.stderr)
        sys.exit(1)

    print(f"\nAnalyzing reference: {reference_svg.name}")
    ref_metrics = analyze_png(ref_png)
    ref_phash = ref_metrics["phash"]
    print(f"  pHash={phash_hex(ref_phash)} size={ref_metrics['size_kb']}KB avg={ref_metrics['avg_color']}")

    # --- Analyze all ---
    rows = []  # (svg_name, metrics, hamming_dist, category, is_ref, error)

    # Reference row (hamming=0)
    rows.append({
        "name": reference_svg.name,
        "size_kb": ref_metrics["size_kb"],
        "phash": phash_hex(ref_phash),
        "hamming": 0,
        "category": "tight",
        "is_ref": True,
        "error": None,
        "avg_color": ref_metrics["avg_color"],
    })

    print(f"\nAnalyzing {len(target_svgs)} target PNGs...")
    for svg in target_svgs:
        if svg.name in render_errors:
            rows.append({
                "name": svg.name,
                "size_kb": 0.0,
                "phash": "RENDER_FAIL",
                "hamming": 64,
                "category": "deviation",
                "is_ref": False,
                "error": render_errors[svg.name],
                "avg_color": "N/A",
            })
            continue
        png_path = render_results[svg.name]
        m = analyze_png(png_path)
        dist = hamming(m["phash"], ref_phash)
        cat = categorize(dist)
        rows.append({
            "name": svg.name,
            "size_kb": m["size_kb"],
            "phash": phash_hex(m["phash"]),
            "hamming": dist,
            "category": cat,
            "is_ref": False,
            "error": None,
            "avg_color": m["avg_color"],
        })

    # --- Sort by Hamming distance ---
    rows_sorted = sorted(rows, key=lambda r: r["hamming"])

    # --- Diagnostics for outliers ---
    outliers = check_strict_gate(rows, threshold)

    def diagnose(name: str) -> str:
        """Quick SVG inspection for outlier hypothesis."""
        svg_path = ASSETS / name
        try:
            content = svg_path.read_text(encoding="utf-8", errors="replace")[:4000]
        except Exception:
            return "Cannot read SVG"
        hints = []
        if "visual_id" in content:
            import re
            vid = re.search(r'visual_id[=:]\s*["\']?(\d+)', content)
            if vid:
                hints.append(f"visual_id={vid.group(1)}")
        # Check fill colors
        fills = set()
        import re
        for m in re.finditer(r'fill[=:]\s*["\']?(#[0-9a-fA-F]{3,6})', content):
            fills.add(m.group(1).lower())
        if fills:
            hints.append(f"dominant fills: {', '.join(sorted(fills)[:3])}")
        # Panel count heuristic
        rect_count = content.count("<rect")
        hints.append(f"~{rect_count} rects")
        return "; ".join(hints) if hints else "No structural hints found"

    # --- Summary counts ---
    tight_count = sum(1 for r in rows if r["category"] == "tight")
    near_count = sum(1 for r in rows if r["category"] == "near")
    dev_count = sum(1 for r in rows if r["category"] == "deviation")
    total = len(rows)
    pass_signal = "PASS" if tight_count / total >= 0.80 else "WARN"

    # --- Build report ---
    rsvg_ver = subprocess.run([RSVG, "--version"], capture_output=True, text=True).stdout.split("\n")[0].strip()
    scan_date = datetime.date.today().isoformat()

    lines = []
    lines.append(f"# L20 Visual Regression Report")
    lines.append(f"")
    lines.append(f"- **Scan date**: {scan_date}")
    lines.append(f"- **Total covers**: {total} (1 reference + {total - 1} targets)")
    lines.append(f"- **Reference**: `{reference_svg.name}`")
    lines.append(f"- **Tooling**: {rsvg_ver}")
    lines.append(f"- **Render size**: {WIDTH}x{HEIGHT}px")
    lines.append(f"")
    lines.append(f"## Results Table")
    lines.append(f"")
    lines.append(f"| filename | KB | pHash | Hamming | category |")
    lines.append(f"|----------|----|-------|---------|----------|")

    for r in rows_sorted:
        ref_marker = " **(REF)**" if r["is_ref"] else ""
        err_note = f" _(RENDER FAIL: {r['error'][:40]})_" if r["error"] else ""
        lines.append(
            f"| `{r['name']}`{ref_marker} | {r['size_kb']} | `{r['phash']}` | {r['hamming']} | {r['category']}{err_note} |"
        )

    lines.append(f"")
    lines.append(f"## Reference Baseline")
    lines.append(f"")
    lines.append(f"- **File**: `{reference_svg.name}`")
    lines.append(f"- **pHash**: `{phash_hex(ref_phash)}`")
    lines.append(f"- **Size**: {ref_metrics['size_kb']} KB")
    lines.append(f"- **Avg color**: {ref_metrics['avg_color']}")
    lines.append(f"")

    if outliers:
        lines.append(f"## Outliers (Hamming > {threshold})")
        lines.append(f"")
        for r in sorted(outliers, key=lambda x: x["hamming"], reverse=True):
            diag = diagnose(r["name"])
            lines.append(f"### `{r['name']}`")
            lines.append(f"- **Hamming**: {r['hamming']}")
            lines.append(f"- **Diagnosis hypothesis**: {diag}")
            lines.append(f"")
    else:
        lines.append(f"## Outliers (Hamming > {threshold})")
        lines.append(f"")
        lines.append(f"None — all covers within near/tight range.")
        lines.append(f"")

    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Tier | Count | Threshold |")
    lines.append(f"|------|-------|-----------|")
    lines.append(f"| tight (0-12) | {tight_count} | target |")
    lines.append(f"| near (13-25) | {near_count} | acceptable |")
    lines.append(f"| deviation (26+) | {dev_count} | investigate |")
    lines.append(f"")
    lines.append(f"**Overall signal: {pass_signal}** ({tight_count}/{total} tight = {100*tight_count//total}%)")
    lines.append(f"")
    lines.append(f"> Threshold: >=80% tight = PASS")
    lines.append(f"")

    report_text = "\n".join(lines) + "\n"
    REPORT_FILE.write_text(report_text, encoding="utf-8")
    print(f"\nReport written to: {REPORT_FILE}")

    # --- Stdout preview: top 10 + bottom 10 by Hamming ---
    print(f"\n{'='*80}")
    print(f"RESULT TABLE (top 10 by Hamming asc + bottom 10 by Hamming desc):")
    print(f"{'='*80}")
    print(f"{'Filename':<75} {'KB':>6} {'Hamming':>7} {'Cat':<10}")
    print(f"{'-'*75} {'-'*6} {'-'*7} {'-'*10}")

    top10 = rows_sorted[:10]
    bot10 = rows_sorted[-10:]
    shown = set()
    for r in top10:
        shown.add(r["name"])
        marker = "(REF)" if r["is_ref"] else ""
        print(f"{r['name'][:72]:<75} {r['size_kb']:>6.1f} {r['hamming']:>7} {r['category']:<10} {marker}")

    if len(rows_sorted) > 20:
        print(f"  ... ({len(rows_sorted) - 20} more rows) ...")

    for r in bot10:
        if r["name"] in shown:
            continue
        marker = "(REF)" if r["is_ref"] else ""
        print(f"{r['name'][:72]:<75} {r['size_kb']:>6.1f} {r['hamming']:>7} {r['category']:<10} {marker}")

    print(f"\n{'='*80}")
    print(f"SIGNAL: {pass_signal} ({tight_count}/{total} tight, {near_count} near, {dev_count} deviation)")
    print(f"{'='*80}")

    # Top 3 most deviated
    top3_dev = sorted([r for r in rows if not r["is_ref"]], key=lambda x: x["hamming"], reverse=True)[:3]
    print(f"\nTop 3 most deviated covers:")
    for i, r in enumerate(top3_dev, 1):
        print(f"  {i}. {r['name']}  Hamming={r['hamming']}  ({r['category']})")

    # --- Validation ---
    report_lines = REPORT_FILE.read_text().splitlines()
    table_rows = [l for l in report_lines if l.startswith("| `2026-")]
    ref_rows = [l for l in report_lines if "(REF)" in l]
    hamming_zero = [l for l in table_rows if "| 0 |" in l or "| 0|" in l or " 0 |" in l]

    print(f"\nValidation:")
    print(f"  Table rows found: {len(table_rows)} (expected {total})")
    print(f"  Reference row (REF marker): {len(ref_rows)}")
    print(f"  Hamming=0 row: {len(hamming_zero)}")
    print(f"  Tight+Near+Dev = {tight_count}+{near_count}+{dev_count} = {tight_count+near_count+dev_count} (expected {total})")

    assert len(table_rows) == total, f"Row count mismatch: {len(table_rows)} != {total}"
    assert len(ref_rows) >= 1, "Reference row missing"
    assert tight_count + near_count + dev_count == total, "Tier counts don't sum to total"

    # --- Strict mode: fail CI if any cover exceeds threshold ---
    if args.strict and outliers:
        worst = max(outliers, key=lambda r: r["hamming"])
        print(
            f"\n[STRICT] {len(outliers)} cover(s) exceed Hamming threshold {threshold}. "
            f"Worst: {worst['name']} (Hamming={worst['hamming']})",
            file=sys.stderr,
        )
        sys.exit(1)
    elif args.strict:
        print(f"\n[STRICT] All covers within Hamming threshold {threshold}. Gate passed.")


if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    main()

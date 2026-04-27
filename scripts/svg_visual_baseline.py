#!/usr/bin/env python3
"""
SVG Visual Regression Baseline Tool.

Usage:
    python3 scripts/svg_visual_baseline.py --capture             # render PNGs + write manifest
    python3 scripts/svg_visual_baseline.py --verify              # re-render and pixel-diff vs baseline
    python3 scripts/svg_visual_baseline.py --verify --threshold 1.0  # custom pass threshold (%)
    python3 scripts/svg_visual_baseline.py --verify --strict     # legacy SHA256-only comparison
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BASELINE_DIR = REPO_ROOT / "tests" / "visual-baselines"
DIFF_DIR = REPO_ROOT / "tests" / "visual-diffs"
MANIFEST_FILE = BASELINE_DIR / "manifest.json"

# Pass criteria (overridable via --threshold):
DEFAULT_THRESHOLD_PCT = 0.5   # max % of pixels that may differ
MAX_CONTIGUOUS_BLOCK = 100    # max side of a contiguous diff rectangle (pixels)
PIXEL_DIFF_THRESHOLD = 30     # per-pixel RGB sum threshold to count as "different"

TARGET_SVGS = [
    # LLM Security post
    "assets/images/2026-03-07-LLM_Security_Practical_Guide_Prompt_Injection_RAG_MCP.svg",
    # Mar 16-31 weekly digests
    "assets/images/2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.svg",
    "assets/images/2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin.svg",
    "assets/images/2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet.svg",
    "assets/images/2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.svg",
    "assets/images/2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.svg",
    "assets/images/2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat.svg",
    "assets/images/2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.svg",
    "assets/images/2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg",
    "assets/images/2026-03-23-Tech_Security_Weekly_Digest_Ransomware.svg",
    "assets/images/2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg",
    "assets/images/2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent.svg",
    "assets/images/2026-03-26-Tech_Security_Weekly_Digest_Kubernetes_Supply_Chain_AI.svg",
    "assets/images/2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg",
    "assets/images/2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.svg",
    "assets/images/2026-03-29-Tech_Security_Weekly_Digest_Ransomware_LLM_K8s_Supply_Chain.svg",
    "assets/images/2026-03-30-March_2026_Security_Digest_Monthly_Index.svg",
    "assets/images/2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.svg",
    # Jan 23-27 weekly digests (short filenames only)
    "assets/images/2026-01-23-Tech_Security_Weekly_Digest.svg",
    "assets/images/2026-01-24-Tech_Security_Weekly_Digest.svg",
    "assets/images/2026-01-25-Tech_Security_Weekly_Digest.svg",
    "assets/images/2026-01-26-Tech_Security_Weekly_Digest_Zero_Trust_Agentic_AI_Terraform.svg",
    "assets/images/2026-01-27-Tech_Security_Weekly_Digest_MS_Office_Kimi_Kimwolf_AWS.svg",
    # Feb digests (11 files, excluding 02-17/02-18 refs)
    "assets/images/2026-02-02-Weekly_Security_Threat_Intelligence_Digest.svg",
    "assets/images/2026-02-02-Weekly_Tech_AI_Blockchain_Digest.svg",
    "assets/images/2026-02-03-Weekly_Security_DevOps_Digest.svg",
    "assets/images/2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.svg",
    "assets/images/2026-02-09-Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic.svg",
    "assets/images/2026-02-10-AI_Cloud_Digest_Meta_Prometheus_Google_OTLP_AWS.svg",
    "assets/images/2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.svg",
    "assets/images/2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack.svg",
    "assets/images/2026-02-14-Weekly_Security_Digest_Microsoft_Zero_Day_Apple_Ivanti_EPMM.svg",
    "assets/images/2026-02-16-Daily_Tech_Digest_RSS_Roundup.svg",
    "assets/images/2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.svg",
    "assets/images/2026-02-20-Tech_Security_Weekly_Digest_Gemini_AI_Supply_Chain_Kubernetes.svg",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# Render dimensions for the 1200x630 OG canvas SVGs.
# rsvg-convert is deterministic across macOS and Linux given identical inputs,
# whereas qlmanage produces hardware-dependent output between Mac models.
RENDER_WIDTH = 1200
RENDER_HEIGHT = 630

_renderer_warned = {"qlmanage_fallback": False}


def _select_renderer() -> str:
    """Return 'rsvg-convert' if available, else 'qlmanage' (macOS fallback).

    Emits a one-time warning when falling back to qlmanage, since baselines
    captured with qlmanage are non-deterministic across Mac models.
    """
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    if shutil.which("qlmanage"):
        if not _renderer_warned["qlmanage_fallback"]:
            print(
                "  WARNING: rsvg-convert not found; falling back to qlmanage. "
                "Install with `brew install librsvg` for deterministic renders.",
                file=sys.stderr,
            )
            _renderer_warned["qlmanage_fallback"] = True
        return "qlmanage"
    print(
        "  ERROR: Neither rsvg-convert nor qlmanage is available. "
        "Install rsvg-convert: `brew install librsvg` (macOS) or "
        "`sudo apt-get install -y librsvg2-bin` (Linux).",
        file=sys.stderr,
    )
    return ""


def render_svg_to_png(
    svg_path: Path,
    out_png: Path,
    width: int = RENDER_WIDTH,
    height: int = RENDER_HEIGHT,
) -> bool:
    """Render SVG to a fixed-dimension PNG.

    Prefers `rsvg-convert` (deterministic across macOS and Linux). Falls back to
    `qlmanage` on macOS when rsvg-convert is unavailable, with a warning.
    """
    renderer = _select_renderer()
    if not renderer:
        return False

    out_png.parent.mkdir(parents=True, exist_ok=True)

    if renderer == "rsvg-convert":
        result = subprocess.run(
            [
                "rsvg-convert",
                "-w", str(width),
                "-h", str(height),
                "-o", str(out_png),
                str(svg_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not out_png.exists():
            print(
                f"  ERROR: rsvg-convert failed for {svg_path.name}: "
                f"{result.stderr.strip()}",
                file=sys.stderr,
            )
            return False
        return True

    # qlmanage fallback (macOS only). Note: qlmanage uses a single -s for
    # bounding box, so we pass the larger dimension to ensure the canvas fits.
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(max(width, height)), "-o", tmpdir, str(svg_path)],
            capture_output=True,
            text=True,
        )
        produced = list(Path(tmpdir).glob("*.png"))
        if not produced:
            print(f"  ERROR: qlmanage produced no output for {svg_path.name}", file=sys.stderr)
            return False
        produced[0].rename(out_png)
        return True


def _max_contiguous_block(diff_mask) -> int:
    """Return the maximum side length of any bounding box of contiguous differing pixels.

    Uses a fast sliding-window approach via numpy column/row projections rather than
    full connected-components (scipy not required).
    """
    import numpy as np

    rows = np.any(diff_mask, axis=1)
    cols = np.any(diff_mask, axis=0)
    if not rows.any():
        return 0
    row_indices = np.where(rows)[0]
    col_indices = np.where(cols)[0]
    max_h = int(row_indices[-1] - row_indices[0] + 1)
    max_w = int(col_indices[-1] - col_indices[0] + 1)
    return max(max_h, max_w)


def pixel_diff(baseline_png: Path, current_png: Path, diff_out: Path) -> dict:
    """Compare two PNGs pixel-by-pixel using Pillow + numpy.

    Returns a dict with keys:
        pct_diff   – percentage of differing pixels (float)
        max_block  – max contiguous block side length (int)
        total_px   – total pixel count
        diff_px    – number of differing pixels
    Also writes a red-overlay diff image to diff_out.
    """
    import numpy as np
    from PIL import Image

    baseline_img = Image.open(baseline_png).convert("RGB")
    current_img = Image.open(current_png).convert("RGB")

    # Resize current to match baseline dimensions if they differ (e.g. sub-pixel rounding)
    if baseline_img.size != current_img.size:
        current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

    base_arr = np.array(baseline_img, dtype=np.int32)
    curr_arr = np.array(current_img, dtype=np.int32)

    abs_diff = np.abs(base_arr - curr_arr).sum(axis=2)  # shape (H, W)
    diff_mask = abs_diff > PIXEL_DIFF_THRESHOLD

    total_px = diff_mask.size
    diff_px = int(diff_mask.sum())
    pct_diff = 100.0 * diff_px / total_px if total_px > 0 else 0.0
    max_block = _max_contiguous_block(diff_mask)

    # Write red-overlay diff image
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    overlay = np.array(current_img.copy())
    overlay[diff_mask] = [255, 0, 0]
    Image.fromarray(overlay.astype(np.uint8)).save(diff_out)

    return {
        "pct_diff": pct_diff,
        "max_block": max_block,
        "total_px": total_px,
        "diff_px": diff_px,
    }


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def generate_html_report(results: list[dict], threshold_pct: float) -> Path:
    """Write tests/visual-diffs/index.html with side-by-side comparison table."""
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DIFF_DIR / "index.html"

    # Sort by drift severity (descending)
    sorted_results = sorted(results, key=lambda r: r.get("pct_diff", 0.0), reverse=True)

    rows = []
    for r in sorted_results:
        name = r["name"]
        status = r["status"]
        pct = r.get("pct_diff", None)
        block = r.get("max_block", None)

        if status == "SKIP":
            row_class = "skip"
            status_cell = "<td class='skip'>SKIP</td>"
            pct_cell = "<td>—</td>"
            block_cell = "<td>—</td>"
            img_cells = "<td colspan='3'>SVG not found</td>"
        elif status == "RENDER_ERROR":
            row_class = "fail"
            status_cell = "<td class='fail'>RENDER ERROR</td>"
            pct_cell = "<td>—</td>"
            block_cell = "<td>—</td>"
            img_cells = "<td colspan='3'>Render failed</td>"
        else:
            passed = r.get("passed", False)
            row_class = "pass" if passed else "fail"
            status_label = "PASS" if passed else "DIFF"
            status_cell = f"<td class='{row_class}'>{status_label}</td>"
            pct_cell = f"<td>{pct:.3f}%</td>"
            block_cell = f"<td>{block}px</td>"

            baseline_rel = r.get("baseline_rel", "")
            current_rel = r.get("current_rel", "")
            diff_rel = r.get("diff_rel", "")

            def img_tag(src, label):
                if src:
                    return f"<td><figure><img src='{src}' alt='{label}' loading='lazy'><figcaption>{label}</figcaption></figure></td>"
                return f"<td>{label}: N/A</td>"

            img_cells = img_tag(baseline_rel, "Baseline") + img_tag(current_rel, "Current") + img_tag(diff_rel, "Diff")

        rows.append(f"""
        <tr class='{row_class}'>
            <td class='name'>{name}</td>
            {status_cell}
            {pct_cell}
            {block_cell}
            {img_cells}
        </tr>""")

    pass_count = sum(1 for r in results if r.get("passed") is True)
    fail_count = sum(1 for r in results if r.get("passed") is False and r["status"] not in ("SKIP", "RENDER_ERROR"))
    skip_count = sum(1 for r in results if r["status"] in ("SKIP", "RENDER_ERROR"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SVG Visual Regression Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #222; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
  .summary {{ margin-bottom: 1.5rem; font-size: 0.95rem; }}
  .pass {{ color: #1a7f37; font-weight: 600; }}
  .fail {{ color: #cf222e; font-weight: 600; }}
  .skip {{ color: #888; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
  th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; vertical-align: top; }}
  th {{ background: #f6f8fa; cursor: pointer; user-select: none; white-space: nowrap; }}
  th:hover {{ background: #eaeef2; }}
  tr.pass td {{ background: #f0fff4; }}
  tr.fail td {{ background: #fff0f0; }}
  tr.skip td {{ background: #fafafa; color: #888; }}
  td.name {{ font-family: monospace; font-size: 0.78rem; max-width: 260px; word-break: break-all; }}
  figure {{ margin: 0; }}
  figure img {{ max-width: 200px; max-height: 150px; border: 1px solid #ccc; display: block; }}
  figcaption {{ font-size: 0.75rem; color: #666; margin-top: 3px; }}
</style>
<script>
  function sortTable(col) {{
    const table = document.getElementById('report');
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const dir = table.dataset.sortDir === 'asc' ? -1 : 1;
    table.dataset.sortDir = dir === 1 ? 'asc' : 'desc';
    rows.sort((a, b) => {{
      const av = a.cells[col]?.innerText.trim() || '';
      const bv = b.cells[col]?.innerText.trim() || '';
      const an = parseFloat(av); const bn = parseFloat(bv);
      if (!isNaN(an) && !isNaN(bn)) return dir * (an - bn);
      return dir * av.localeCompare(bv);
    }});
    const tbody = table.querySelector('tbody');
    rows.forEach(r => tbody.appendChild(r));
  }}
</script>
</head>
<body>
<h1>SVG Visual Regression Report</h1>
<div class="summary">
  Threshold: <strong>{threshold_pct:.2f}%</strong> pixels diff &amp;
  max contiguous block &lt; <strong>{MAX_CONTIGUOUS_BLOCK}px</strong> &nbsp;|&nbsp;
  <span class="pass">PASS: {pass_count}</span> &nbsp;
  <span class="fail">FAIL: {fail_count}</span> &nbsp;
  <span class="skip">SKIP/ERR: {skip_count}</span>
</div>
<table id="report" data-sort-dir="asc">
  <thead>
    <tr>
      <th onclick="sortTable(0)">File</th>
      <th onclick="sortTable(1)">Status</th>
      <th onclick="sortTable(2)">% Diff</th>
      <th onclick="sortTable(3)">Max Block</th>
      <th>Baseline</th>
      <th>Current</th>
      <th>Diff (red overlay)</th>
    </tr>
  </thead>
  <tbody>
    {"".join(rows)}
  </tbody>
</table>
</body>
</html>
"""
    report_path.write_text(html, encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Capture
# ---------------------------------------------------------------------------

def capture():
    """Render all SVGs and write manifest."""
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    ok = 0
    total_bytes = 0

    valid_targets = []
    for rel in TARGET_SVGS:
        svg = REPO_ROOT / rel
        if svg.exists():
            valid_targets.append(svg)
        else:
            print(f"  SKIP (not found): {rel}", file=sys.stderr)

    renderer = _select_renderer() or "(none)"
    print(f"Rendering {len(valid_targets)} SVGs with {renderer} at {RENDER_WIDTH}x{RENDER_HEIGHT}...")
    for svg in valid_targets:
        out_png = BASELINE_DIR / (svg.stem + ".png")
        print(f"  {svg.name} -> {out_png.name}", end=" ", flush=True)
        if render_svg_to_png(svg, out_png):
            size = out_png.stat().st_size
            sha = sha256_file(out_png)
            manifest[svg.name] = {"png": out_png.name, "sha256": sha, "bytes": size}
            total_bytes += size
            ok += 1
            print(f"[{size // 1024}KB]")
        else:
            print("[FAILED]")

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2))
    print(f"\nCaptured {ok}/{len(valid_targets)} baselines")
    print(f"Total size: {total_bytes / 1024 / 1024:.1f} MB")
    print(f"Manifest: {MANIFEST_FILE}")
    return ok == len(valid_targets)


# ---------------------------------------------------------------------------
# Verify (strict SHA256 mode)
# ---------------------------------------------------------------------------

def verify_strict():
    """Re-render SVGs and compare SHA256 against manifest (legacy behavior)."""
    if not MANIFEST_FILE.exists():
        print("No manifest found. Run --capture first.", file=sys.stderr)
        return False

    manifest = json.loads(MANIFEST_FILE.read_text())
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    passed = 0
    failed = 0

    print(f"Verifying {len(manifest)} baselines (strict SHA256 mode)...")
    for svg_name, entry in manifest.items():
        svg = next((REPO_ROOT / r for r in TARGET_SVGS if Path(r).name == svg_name), None)
        if svg is None or not svg.exists():
            print(f"  SKIP (SVG not found): {svg_name}")
            continue

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tmp_png = Path(tf.name)

        try:
            if not render_svg_to_png(svg, tmp_png):
                print(f"  FAIL (render error): {svg_name}")
                failed += 1
                continue

            new_sha = sha256_file(tmp_png)
            if new_sha == entry["sha256"]:
                print(f"  PASS: {svg_name}")
                passed += 1
                tmp_png.unlink(missing_ok=True)
            else:
                diff_path = DIFF_DIR / entry["png"]
                tmp_png.rename(diff_path)
                print(f"  DIFF: {svg_name} -> {diff_path}")
                failed += 1
        finally:
            tmp_png.unlink(missing_ok=True)

    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


# ---------------------------------------------------------------------------
# Verify (per-pixel diff mode)
# ---------------------------------------------------------------------------

def verify(threshold_pct: float = DEFAULT_THRESHOLD_PCT):
    """Re-render SVGs and pixel-diff against baseline PNGs.

    Always generates tests/visual-diffs/index.html regardless of pass/fail.
    Exits 0 if all files pass, 1 otherwise.
    """
    if not MANIFEST_FILE.exists():
        print("No manifest found. Run --capture first.", file=sys.stderr)
        return False

    manifest = json.loads(MANIFEST_FILE.read_text())
    DIFF_DIR.mkdir(parents=True, exist_ok=True)

    # Temp dir for freshly-rendered PNGs during this run
    current_dir = DIFF_DIR / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    results = []
    passed_count = 0
    failed_count = 0

    print(f"Verifying {len(manifest)} baselines (pixel-diff, threshold={threshold_pct}%)...")

    for svg_name, entry in manifest.items():
        svg = next((REPO_ROOT / r for r in TARGET_SVGS if Path(r).name == svg_name), None)
        if svg is None or not svg.exists():
            print(f"  SKIP (SVG not found): {svg_name}")
            results.append({"name": svg_name, "status": "SKIP"})
            continue

        baseline_png = BASELINE_DIR / entry["png"]
        if not baseline_png.exists():
            print(f"  SKIP (baseline PNG missing): {svg_name}")
            results.append({"name": svg_name, "status": "SKIP"})
            continue

        current_png = current_dir / entry["png"]
        if not render_svg_to_png(svg, current_png):
            print(f"  FAIL (render error): {svg_name}")
            results.append({"name": svg_name, "status": "RENDER_ERROR"})
            failed_count += 1
            continue

        diff_png = DIFF_DIR / ("diff_" + entry["png"])
        metrics = pixel_diff(baseline_png, current_png, diff_png)

        pct = metrics["pct_diff"]
        block = metrics["max_block"]
        passed = pct <= threshold_pct and block <= MAX_CONTIGUOUS_BLOCK

        status_str = "PASS" if passed else "DIFF"
        print(
            f"  {status_str}: {svg_name}  "
            f"({pct:.3f}% diff, max_block={block}px)"
        )

        if passed:
            passed_count += 1
        else:
            failed_count += 1

        results.append({
            "name": svg_name,
            "status": status_str,
            "passed": passed,
            "pct_diff": pct,
            "max_block": block,
            "baseline_rel": f"../visual-baselines/{entry['png']}",
            "current_rel": f"current/{entry['png']}",
            "diff_rel": f"diff_{entry['png']}",
        })

    # Always generate the HTML report
    report_path = generate_html_report(results, threshold_pct)
    print(f"\nResult: {passed_count} passed, {failed_count} failed")
    print(f"HTML report: {report_path}")
    return failed_count == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SVG visual regression baseline tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true", help="Render SVGs and save baselines")
    group.add_argument("--verify", action="store_true", help="Re-render and diff against baselines")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD_PCT,
        metavar="N",
        help=f"Max %% of pixels allowed to differ (default: {DEFAULT_THRESHOLD_PCT})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Legacy SHA256-only comparison (backward compat, no HTML report)",
    )
    args = parser.parse_args()

    os.chdir(REPO_ROOT)

    if args.capture:
        success = capture()
    elif args.strict:
        success = verify_strict()
    else:
        success = verify(threshold_pct=args.threshold)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SVG Visual Regression Baseline Tool.

Usage:
    python3 scripts/svg_visual_baseline.py --capture   # render PNGs + write manifest
    python3 scripts/svg_visual_baseline.py --verify    # re-render and diff vs baseline
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BASELINE_DIR = REPO_ROOT / "tests" / "visual-baselines"
DIFF_DIR = REPO_ROOT / "tests" / "visual-diffs"
MANIFEST_FILE = BASELINE_DIR / "manifest.json"

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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def render_svg_to_png(svg_path: Path, out_png: Path, size: int = 400) -> bool:
    """Render SVG to PNG using qlmanage (macOS Quick Look).

    Size 400px keeps each PNG ~200KB (35 files ≈ 7MB total, within 10MB budget).
    Use size=1200 for high-fidelity renders when disk space is not a concern.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["qlmanage", "-t", "-s", str(size), "-o", tmpdir, str(svg_path)],
            capture_output=True,
            text=True,
        )
        # qlmanage outputs <name>.svg.png
        produced = list(Path(tmpdir).glob("*.png"))
        if not produced:
            print(f"  ERROR: qlmanage produced no output for {svg_path.name}", file=sys.stderr)
            return False
        # Move to final destination
        out_png.parent.mkdir(parents=True, exist_ok=True)
        produced[0].rename(out_png)
        return True


def capture():
    """Render all 33 SVGs and write manifest."""
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

    print(f"Rendering {len(valid_targets)} SVGs with qlmanage...")
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


def verify():
    """Re-render SVGs and compare SHA256 against manifest."""
    if not MANIFEST_FILE.exists():
        print("No manifest found. Run --capture first.", file=sys.stderr)
        return False

    manifest = json.loads(MANIFEST_FILE.read_text())
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    passed = 0
    failed = 0

    print(f"Verifying {len(manifest)} baselines...")
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


def main():
    parser = argparse.ArgumentParser(description="SVG visual regression baseline tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true", help="Render SVGs and save baselines")
    group.add_argument("--verify", action="store_true", help="Re-render and diff against baselines")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)

    if args.capture:
        success = capture()
    else:
        success = verify()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

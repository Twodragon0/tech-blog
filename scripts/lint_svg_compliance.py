#!/usr/bin/env python3
"""SVG compliance linter — CI gate for design-system defects.

Checks assets/images/2026-*.svg for:
1. Placeholder description text (generator artifact)
2. Accent/category color mismatch (Family A template covers only)
3. Missing domain signature (Family A covers only)

Conservative by design: false positives are worse than false negatives.
Accent/color checks only apply to SVGs that contain the VISUAL SYSTEM
template marker, proving they are Family A generated covers.

Usage:
    python3 scripts/lint_svg_compliance.py
    python3 scripts/lint_svg_compliance.py --files "assets/images/2026-04-*.svg"
    python3 scripts/lint_svg_compliance.py --report
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLACEHOLDER_TEXT = (
    "Clean technical cover with stronger depth, "
    "hierarchy, and category-specific structure."
)

SIGNATURE = "tech.2twodragon.com"

# Template marker present in all Family A generated covers
FAMILY_A_MARKER = "VISUAL SYSTEM"

# Category keyword → required accent colors (any match = pass).
# Only enforced on files that contain FAMILY_A_MARKER.
CATEGORY_RULES = {
    "ai_ml": {
        "keywords": [
            "AI_", "_AI_", "LLM_", "_LLM_", "Agent_", "_Agent_",
            "Claude_Code", "OpenCode", "Coding_Assistants",
        ],
        # Accept full cyan/sky family used across design-system versions
        "required_colors": [
            "#22d3ee", "#06b6d4",  # Tailwind cyan-400/500 (current)
            "#38bdf8", "#7dd3fc",  # sky-400/300 (legacy v1)
            "#67e8f9",             # cyan-300 (legacy v1)
        ],
        "label": "AI/ML",
    },
    "cloud": {
        "keywords": ["Cloud_Security", "AWS_", "GCP_", "EC2_"],
        # Accept full blue family
        "required_colors": [
            "#60a5fa", "#1d4ed8",  # blue-400/700 (current)
            "#3b82f6", "#38bdf8",  # blue-500, sky-400 (legacy)
        ],
        "label": "Cloud",
    },
    "devsecops": {
        "keywords": ["DevSecOps_", "Roadmap_"],
        # Accept full violet/purple family
        "required_colors": [
            "#a78bfa", "#6c5ce7",  # violet-400, indigo (current)
            "#6d28d9", "#7c3aed",  # violet-700/600 (legacy)
            "#8b5cf6",             # violet-500
        ],
        "label": "DevSecOps",
    },
    "threat": {
        "keywords": [
            "Ransomware_", "_Ransomware", "Rootkit_", "_Rootkit",
            "Threat_", "_Threat", "Malware_", "_Malware",
        ],
        "required_colors": [
            "#ef4444", "#f87171",  # red-500/400 (current)
            "#991b1b", "#dc2626",  # red-800/600 (legacy)
        ],
        "label": "Threat/Security",
    },
    "incident": {
        "keywords": ["Postmortem_", "_Postmortem", "Incident_", "_Incident"],
        "required_colors": ["#f59e0b", "#fbbf24"],  # amber-500/400
        "label": "Incident",
    },
}

# Digest/weekly covers use a different design system — skip accent/signature checks
DIGEST_RE = re.compile(
    r"(?:Weekly|Daily|Digest|Monthly_Index|Vendor_Blog)",
    re.IGNORECASE,
)

# Supplementary diagram/flow SVGs embedded in posts — skip all design-system checks
# Matches filenames with architecture/flow/diagram/etc. keywords AND
# the legacy kebab-case diagram files (devsecops-*, backup-strategy-*)
SUPPLEMENTARY_RE = re.compile(
    r"(?:"
    r"^2026-\d{2}-\d{2}-(?:devsecops|backup-strategy)-"  # kebab legacy
    r"|[-_](?:Flow|Matrix|Ecosystem|Timeline|Phases|Layer|"
    r"Diagram|Structure|Stack|Path|Scaling)(?:[-_.]|$)"   # diagram keywords in name
    r")",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def is_og_derivative(filename: str) -> bool:
    return "_og." in filename


def is_digest(filename: str) -> bool:
    return bool(DIGEST_RE.search(filename))


def is_supplementary(filename: str) -> bool:
    return bool(SUPPLEMENTARY_RE.search(filename))


def is_family_a(content: str) -> bool:
    """Return True if SVG contains the VISUAL SYSTEM template marker."""
    return FAMILY_A_MARKER in content


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_placeholder(content: str) -> str | None:
    """Flag generator placeholder description — applies to all SVGs."""
    if PLACEHOLDER_TEXT in content:
        return "Contains generator placeholder description (must be replaced before commit)"
    return None


def detect_category(filename: str) -> tuple[str, dict] | tuple[None, None]:
    """Return (category_id, rule) for the first matching category keyword.

    Matching uses the first 3 underscore-delimited word-segments after the
    date prefix to identify the PRIMARY topic, avoiding false positives from
    secondary keywords deep in long filenames like
    'Blockchain_..._DevSecOps_Perspective'.
    """
    # Strip date prefix: 2026-01-08-<rest>
    m = re.match(r'^\d{4}-\d{2}-\d{2}-(.+?)(?:\.svg)?$', filename)
    if not m:
        return None, None

    # Take first 3 underscore-segments as primary topic words
    segments = m.group(1).split('_')
    primary = '_'.join(segments[:3]) + '_'  # e.g. "AI_Coding_Assistants_"

    for cat_id, rule in CATEGORY_RULES.items():
        for kw in rule["keywords"]:
            if kw in primary:
                return cat_id, rule
    return None, None


def check_accent_colors(content: str, filename: str) -> str | None:
    """Flag accent/category mismatch. Only runs on Family A template SVGs."""
    cat_id, rule = detect_category(filename)
    if cat_id is None:
        return None  # unrecognised category — skip conservatively

    required = rule["required_colors"]
    content_lower = content.lower()
    has_required = any(c.lower() in content_lower for c in required)
    if not has_required:
        return (
            f"Category '{rule['label']}' detected but missing required accent color "
            f"(expected one of: {', '.join(required)})"
        )
    return None


def check_signature(content: str) -> str | None:
    """Flag missing domain signature on Family A covers."""
    if SIGNATURE not in content:
        return f"Missing domain signature '{SIGNATURE}'"
    return None


# ---------------------------------------------------------------------------
# Core lint function
# ---------------------------------------------------------------------------

def lint_file(path: str) -> list[str]:
    """Return list of violation strings for a file (empty = clean)."""
    filename = os.path.basename(path)
    violations = []

    # Skip OG image derivatives and supplementary diagram SVGs entirely
    if is_og_derivative(filename) or is_supplementary(filename):
        return violations

    content = load_svg(path)

    # Check 1: placeholder text — applies to every SVG we scan
    v = check_placeholder(content)
    if v:
        violations.append(v)

    # Digest covers use a different design system; skip checks 2 & 3
    if is_digest(filename):
        return violations

    # Checks 2 & 3 only apply to Family A template covers
    if is_family_a(content):
        v = check_accent_colors(content, filename)
        if v:
            violations.append(v)

        v = check_signature(content)
        if v:
            violations.append(v)

    return violations


def load_svg(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="SVG compliance linter")
    parser.add_argument(
        "--files",
        default="assets/images/2026-*.svg",
        help=(
            "Glob pattern OR space-separated list of file paths to scan "
            "(default: assets/images/2026-*.svg). "
            "When called from pre-commit, pass staged paths as positional-style "
            "via nargs so the hook can forward them directly."
        ),
        nargs="+",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write JSON report to reports/svg-lint.json",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # If a single token was passed and it looks like a glob pattern (contains *
    # or ?), expand it relative to repo root.  Otherwise treat every token as
    # a literal file path (pre-commit hook passes staged paths directly).
    raw = args.files  # always a list due to nargs="+"
    if len(raw) == 1 and ("*" in raw[0] or "?" in raw[0]):
        pattern = str(repo_root / raw[0])
        files = sorted(glob.glob(pattern))
    else:
        # Absolute paths → use as-is; relative paths → resolve from repo root
        files = sorted(
            str(repo_root / p) if not os.path.isabs(p) else p
            for p in raw
        )

    if not files:
        print(f"No files matched: {pattern}")
        sys.exit(0)

    results: dict[str, list[str]] = {}
    total_violations = 0
    files_with_violations = 0

    for path in files:
        filename = os.path.basename(path)
        violations = lint_file(path)
        results[filename] = violations
        if violations:
            files_with_violations += 1
            total_violations += len(violations)
            print(f"❌ {filename}")
            for v in violations:
                print(f"   ⚠️  {v}")
        else:
            print(f"✅ {filename}")

    # Summary
    print()
    total_files = len(files)
    clean_files = total_files - files_with_violations
    print("=" * 60)
    print(
        f"Scanned {total_files} files: "
        f"{clean_files} clean, "
        f"{files_with_violations} with violations "
        f"({total_violations} total)"
    )

    if args.report:
        report_dir = repo_root / "reports"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / "svg-lint.json"
        report = {
            "summary": {
                "total_files": total_files,
                "clean_files": clean_files,
                "files_with_violations": files_with_violations,
                "total_violations": total_violations,
            },
            "violations": {k: v for k, v in results.items() if v},
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report written: {report_path}")

    sys.exit(1 if total_violations > 0 else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Post Quality Validation Script for Ralph Loop

Validates blog posts against quality criteria and calculates a quality score.
Used by the Sisyphus Ralph Loop to determine if posts meet publication standards.

Usage:
    python3 scripts/validate_post_quality.py                    # Validate all posts
    python3 scripts/validate_post_quality.py _posts/2026-01-*.md # Specific pattern
    python3 scripts/validate_post_quality.py --threshold 80     # Custom threshold
    python3 scripts/validate_post_quality.py --drafts           # Validate drafts only
    python3 scripts/validate_post_quality.py --json             # JSON output
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================================
# Constants
# ============================================================================

POSTS_DIR = Path(__file__).parent.parent / "_posts"
DRAFTS_DIR = Path(__file__).parent.parent / "_drafts"
IMAGES_DIR = Path(__file__).parent.parent / "assets" / "images"

REQUIRED_FRONT_MATTER = ["title", "date", "category", "tags", "excerpt"]
RECOMMENDED_FRONT_MATTER = ["image", "layout", "categories"]

QUALITY_WEIGHTS = {
    "content_length": 20,
    "tables": 15,
    "code_blocks": 15,
    "checklist": 10,
    "front_matter": 20,
    "english_images": 10,
    "valid_links": 10,
}

MIN_CONTENT_LENGTH = 3000
MIN_TABLES = 2
MIN_CODE_BLOCKS = 1

# Korean character pattern
KOREAN_PATTERN = re.compile(r"[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\ud7b0-\ud7ff]")


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class QualityResult:
    """Quality validation result for a single post."""

    file_path: str
    title: str
    score: int
    passed: bool
    details: Dict[str, dict] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationSummary:
    """Summary of validation results."""

    total_posts: int
    passed: int
    failed: int
    average_score: float
    results: List[QualityResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_posts": self.total_posts,
            "passed": self.passed,
            "failed": self.failed,
            "average_score": round(self.average_score, 2),
            "pass_rate": round(self.passed / max(self.total_posts, 1) * 100, 1),
            "results": [r.to_dict() for r in self.results],
        }


# ============================================================================
# Validation Functions
# ============================================================================


def extract_front_matter(content: str) -> Tuple[Dict[str, str], str]:
    """Extract front matter and body from markdown content."""
    front_matter = {}
    body = content

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)

        for line in fm_text.split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Handle list values
                if value.startswith("[") and value.endswith("]"):
                    try:
                        value = value[1:-1]  # Remove brackets
                    except (ValueError, SyntaxError):
                        pass
                front_matter[key] = value

    return front_matter, body


def validate_content_length(body: str) -> Tuple[int, dict]:
    """Validate content length (excluding markdown syntax)."""
    # Remove code blocks
    clean_body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    # Remove headings
    clean_body = re.sub(r"^#+\s+.*$", "", clean_body, flags=re.MULTILINE)
    # Remove HTML tags
    clean_body = re.sub(r"<[^>]+>", "", clean_body)
    # Remove empty lines and count
    lines = [line.strip() for line in clean_body.split("\n") if line.strip()]
    length = len("".join(lines))

    score = 0
    if length >= MIN_CONTENT_LENGTH:
        score = QUALITY_WEIGHTS["content_length"]
    elif length >= MIN_CONTENT_LENGTH * 0.7:
        score = int(QUALITY_WEIGHTS["content_length"] * 0.75)
    elif length >= MIN_CONTENT_LENGTH * 0.5:
        score = int(QUALITY_WEIGHTS["content_length"] * 0.5)
    elif length >= MIN_CONTENT_LENGTH * 0.3:
        score = int(QUALITY_WEIGHTS["content_length"] * 0.25)

    return score, {
        "weight": QUALITY_WEIGHTS["content_length"],
        "score": score,
        "value": length,
        "threshold": MIN_CONTENT_LENGTH,
        "passed": length >= MIN_CONTENT_LENGTH,
    }


def validate_tables(body: str) -> Tuple[int, dict]:
    """Validate presence of markdown tables."""
    # Count table separators (|---|)
    table_count = len(re.findall(r"\|[-:]+\|", body))

    score = 0
    if table_count >= MIN_TABLES + 1:
        score = QUALITY_WEIGHTS["tables"]
    elif table_count >= MIN_TABLES:
        score = int(QUALITY_WEIGHTS["tables"] * 0.75)
    elif table_count >= 1:
        score = int(QUALITY_WEIGHTS["tables"] * 0.5)

    return score, {
        "weight": QUALITY_WEIGHTS["tables"],
        "score": score,
        "value": table_count,
        "threshold": MIN_TABLES,
        "passed": table_count >= MIN_TABLES,
    }


def validate_code_blocks(body: str) -> Tuple[int, dict]:
    """Validate presence of code blocks."""
    # Count code block markers (pairs of ```)
    code_markers = body.count("```")
    code_count = code_markers // 2

    score = 0
    if code_count >= MIN_CODE_BLOCKS + 1:
        score = QUALITY_WEIGHTS["code_blocks"]
    elif code_count >= MIN_CODE_BLOCKS:
        score = int(QUALITY_WEIGHTS["code_blocks"] * 0.75)

    return score, {
        "weight": QUALITY_WEIGHTS["code_blocks"],
        "score": score,
        "value": code_count,
        "threshold": MIN_CODE_BLOCKS,
        "passed": code_count >= MIN_CODE_BLOCKS,
    }


def validate_checklist(body: str) -> Tuple[int, dict]:
    """Validate presence of checklist items."""
    has_checklist = "- [ ]" in body or "- [x]" in body or "- [X]" in body
    checklist_count = body.count("- [ ]") + body.count("- [x]") + body.count("- [X]")

    score = QUALITY_WEIGHTS["checklist"] if has_checklist else 0

    return score, {
        "weight": QUALITY_WEIGHTS["checklist"],
        "score": score,
        "value": checklist_count,
        "threshold": 1,
        "passed": has_checklist,
    }


def validate_front_matter(front_matter: Dict[str, str]) -> Tuple[int, dict]:
    """Validate required front matter fields."""
    missing = [f for f in REQUIRED_FRONT_MATTER if f not in front_matter or not front_matter[f]]
    present = len(REQUIRED_FRONT_MATTER) - len(missing)
    total = len(REQUIRED_FRONT_MATTER)

    score = int(QUALITY_WEIGHTS["front_matter"] * (present / total))

    return score, {
        "weight": QUALITY_WEIGHTS["front_matter"],
        "score": score,
        "value": present,
        "threshold": total,
        "passed": len(missing) == 0,
        "missing": missing,
        "present": [f for f in REQUIRED_FRONT_MATTER if f in front_matter and front_matter[f]],
    }


def validate_english_images(content: str, front_matter: Dict[str, str]) -> Tuple[int, dict]:
    """Validate that image references use English filenames only."""
    # Find all image references
    image_refs = re.findall(r"!\[.*?\]\((.*?)\)", content)
    image_refs += re.findall(r'image:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)

    if "image" in front_matter:
        image_refs.append(front_matter["image"])

    korean_images = []
    for ref in image_refs:
        if ref and KOREAN_PATTERN.search(ref):
            korean_images.append(ref)

    score = QUALITY_WEIGHTS["english_images"] if not korean_images else 0

    return score, {
        "weight": QUALITY_WEIGHTS["english_images"],
        "score": score,
        "value": len(image_refs) - len(korean_images),
        "threshold": len(image_refs) if image_refs else 0,
        "passed": len(korean_images) == 0,
        "korean_images": korean_images[:5],  # Limit to first 5
    }


def validate_links(body: str) -> Tuple[int, dict]:
    """Validate link format (not actual URLs)."""
    # Find all markdown links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)

    broken = []
    for text, url in links:
        # Check for common issues
        if url.startswith("example.com") or "YOUR_" in url or "TODO" in url:
            broken.append(url)
        if not url.startswith(("http://", "https://", "/", "#", "mailto:")):
            if not url.endswith((".md", ".html", ".png", ".jpg", ".svg")):
                broken.append(url)

    total_links = len(links)
    valid_links = total_links - len(broken)

    if total_links == 0:
        score = QUALITY_WEIGHTS["valid_links"]  # No links to validate
    else:
        score = int(QUALITY_WEIGHTS["valid_links"] * (valid_links / total_links))

    return score, {
        "weight": QUALITY_WEIGHTS["valid_links"],
        "score": score,
        "value": valid_links,
        "threshold": total_links,
        "passed": len(broken) == 0,
        "broken": broken[:5],  # Limit to first 5
    }


def generate_suggestions(result: QualityResult) -> List[str]:
    """Generate improvement suggestions based on validation results."""
    suggestions = []

    details = result.details

    if not details.get("content_length", {}).get("passed"):
        current = details.get("content_length", {}).get("value", 0)
        needed = MIN_CONTENT_LENGTH - current
        suggestions.append(f"Add {needed}+ more characters of content (currently {current})")

    if not details.get("tables", {}).get("passed"):
        current = details.get("tables", {}).get("value", 0)
        needed = MIN_TABLES - current
        suggestions.append(f"Add {needed}+ more markdown table(s) for data organization")

    if not details.get("code_blocks", {}).get("passed"):
        suggestions.append("Add at least 1 code block with practical examples")

    if not details.get("checklist", {}).get("passed"):
        suggestions.append("Add a checklist section for actionable items (- [ ] item)")

    if not details.get("front_matter", {}).get("passed"):
        missing = details.get("front_matter", {}).get("missing", [])
        if missing:
            suggestions.append(f"Add missing front matter fields: {', '.join(missing)}")

    if not details.get("english_images", {}).get("passed"):
        korean = details.get("english_images", {}).get("korean_images", [])
        if korean:
            suggestions.append(f"Rename Korean image files to English: {korean[0]}")

    if not details.get("valid_links", {}).get("passed"):
        broken = details.get("valid_links", {}).get("broken", [])
        if broken:
            suggestions.append(f"Fix broken/placeholder links: {broken[0]}")

    return suggestions


# ============================================================================
# Main Validation
# ============================================================================


def validate_post(file_path: Path, threshold: int = 80) -> QualityResult:
    """Validate a single post and return quality result."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return QualityResult(
            file_path=str(file_path),
            title="[Error reading file]",
            score=0,
            passed=False,
            errors=[str(e)],
        )

    front_matter, body = extract_front_matter(content)
    title = front_matter.get("title", file_path.stem)

    # Run all validations
    details = {}
    total_score = 0

    # Content length
    score, detail = validate_content_length(body)
    details["content_length"] = detail
    total_score += score

    # Tables
    score, detail = validate_tables(body)
    details["tables"] = detail
    total_score += score

    # Code blocks
    score, detail = validate_code_blocks(body)
    details["code_blocks"] = detail
    total_score += score

    # Checklist
    score, detail = validate_checklist(body)
    details["checklist"] = detail
    total_score += score

    # Front matter
    score, detail = validate_front_matter(front_matter)
    details["front_matter"] = detail
    total_score += score

    # English images
    score, detail = validate_english_images(content, front_matter)
    details["english_images"] = detail
    total_score += score

    # Valid links
    score, detail = validate_links(body)
    details["valid_links"] = detail
    total_score += score

    result = QualityResult(
        file_path=str(file_path),
        title=title,
        score=total_score,
        passed=total_score >= threshold,
        details=details,
    )

    result.suggestions = generate_suggestions(result)

    return result


def validate_posts(
    paths: List[Path], threshold: int = 80, verbose: bool = True
) -> ValidationSummary:
    """Validate multiple posts and return summary."""
    results = []

    for path in paths:
        result = validate_post(path, threshold)
        results.append(result)

        if verbose:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.score:3d}/100 - {path.name}")
            if not result.passed and result.suggestions:
                for suggestion in result.suggestions[:3]:
                    print(f"       -> {suggestion}")

    passed = sum(1 for r in results if r.passed)
    avg_score = sum(r.score for r in results) / len(results) if results else 0

    return ValidationSummary(
        total_posts=len(results),
        passed=passed,
        failed=len(results) - passed,
        average_score=avg_score,
        results=results,
    )


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Validate blog post quality for Ralph Loop"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Post file paths or glob patterns (default: all posts)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Minimum quality score to pass (default: 80)",
    )
    parser.add_argument(
        "--drafts",
        action="store_true",
        help="Validate drafts instead of posts",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--failed-only",
        action="store_true",
        help="Only show failed posts",
    )

    args = parser.parse_args()

    # Determine which directory to scan
    base_dir = DRAFTS_DIR if args.drafts else POSTS_DIR

    # Get files to validate
    if args.paths:
        files = []
        for pattern in args.paths:
            if "*" in pattern:
                files.extend(Path(".").glob(pattern))
            else:
                files.append(Path(pattern))
    else:
        files = list(base_dir.glob("*.md"))

    if not files:
        print(f"No markdown files found in {base_dir}")
        sys.exit(1)

    # Sort by modification time (newest first)
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    # Run validation
    if not args.json:
        print(f"\nValidating {len(files)} posts (threshold: {args.threshold})")
        print("=" * 60)

    summary = validate_posts(files, args.threshold, verbose=not args.json)

    # Filter results if needed
    if args.failed_only:
        summary.results = [r for r in summary.results if not r.passed]

    # Output results
    if args.json:
        print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Total:   {summary.total_posts}")
        print(f"  Passed:  {summary.passed} ({summary.passed / max(summary.total_posts, 1) * 100:.1f}%)")
        print(f"  Failed:  {summary.failed}")
        print(f"  Average: {summary.average_score:.1f}/100")

        if summary.failed > 0:
            print(f"\nFailed posts need improvement before publishing.")
            sys.exit(1)
        else:
            print(f"\nAll posts meet quality threshold!")
            sys.exit(0)


if __name__ == "__main__":
    main()

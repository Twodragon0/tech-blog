#!/usr/bin/env python3
"""Convert Mermaid code blocks in Jekyll posts to SVG images."""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images/mermaid")


def extract_mermaid_blocks(filepath):
    """Extract mermaid code blocks with their positions."""
    content = filepath.read_text(encoding="utf-8")
    pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
    blocks = []
    for i, match in enumerate(pattern.finditer(content)):
        blocks.append(
            {
                "index": i,
                "full_match": match.group(0),
                "code": match.group(1).strip(),
                "start": match.start(),
                "end": match.end(),
            }
        )
    return content, blocks


def generate_svg(mermaid_code, output_path):
    """Generate SVG from mermaid code using mmdc."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_code)
        tmp_input = f.name

    try:
        result = subprocess.run(
            [
                "npx",
                "--yes",
                "@mermaid-js/mermaid-cli",
                "-i",
                tmp_input,
                "-o",
                str(output_path),
                "-t",
                "default",
                "-b",
                "transparent",
                "-q",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  WARNING: mmdc failed: {result.stderr[:200]}")
            return False
        return output_path.exists()
    except subprocess.TimeoutExpired:
        print("  WARNING: mmdc timed out")
        return False
    finally:
        os.unlink(tmp_input)


def clean_svg(svg_path):
    """Remove unnecessary attributes and clean SVG for web use."""
    content = svg_path.read_text(encoding="utf-8")
    # Remove fixed width/height, keep viewBox for responsive sizing
    content = re.sub(r'\s+style="[^"]*"', "", content, count=1)
    # Ensure viewBox exists
    if "viewBox" not in content:
        # Try to extract from width/height
        w_match = re.search(r'width="([\d.]+)"', content)
        h_match = re.search(r'height="([\d.]+)"', content)
        if w_match and h_match:
            w, h = w_match.group(1), h_match.group(1)
            content = content.replace("<svg ", f'<svg viewBox="0 0 {w} {h}" ', 1)
    svg_path.write_text(content, encoding="utf-8")


def post_slug(filepath):
    """Get slug from post filename."""
    name = filepath.stem
    # Remove date prefix
    match = re.match(r"\d{4}-\d{2}-\d{2}-(.*)", name)
    return match.group(1) if match else name


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(POSTS_DIR.glob("*.md"))
    total_converted = 0
    total_failed = 0

    for filepath in files:
        content, blocks = extract_mermaid_blocks(filepath)
        if not blocks:
            continue

        slug = post_slug(filepath)
        print(f"\n{filepath.name}: {len(blocks)} mermaid block(s)")

        new_content = content
        for block in reversed(blocks):  # Reverse to preserve positions
            svg_name = f"{slug}-mermaid-{block['index'] + 1}.svg"
            svg_path = IMAGES_DIR / svg_name
            img_ref = f"/assets/images/mermaid/{svg_name}"

            print(f"  [{block['index'] + 1}] Generating {svg_name}...", end=" ")

            if generate_svg(block["code"], svg_path):
                clean_svg(svg_path)
                # Replace mermaid block with image
                replacement = f"![Mermaid Diagram]({img_ref})"
                new_content = (
                    new_content[: block["start"]]
                    + replacement
                    + new_content[block["end"] :]
                )
                total_converted += 1
                print("OK")
            else:
                total_failed += 1
                print("FAILED (keeping original)")

        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")

    print(f"\nDone: {total_converted} converted, {total_failed} failed")


if __name__ == "__main__":
    main()

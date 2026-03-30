#!/bin/bash
# Generate high-quality SVG images for blog posts using AI CLIs
# Supports: claude, codex, gemini
# Usage: ./scripts/generate_svg_with_ai.sh [--engine claude|codex|gemini] [--recent N] [--force] [post_file]

set -euo pipefail

POSTS_DIR="_posts"
IMAGES_DIR="assets/images"
ENGINE="${ENGINE:-claude}"
RECENT=0
FORCE=false
SINGLE_POST=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --engine) ENGINE="$2"; shift 2 ;;
    --recent) RECENT="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    --help)
      echo "Usage: $0 [--engine claude|codex|gemini] [--recent N] [--force] [post_file]"
      echo "  --engine   AI engine to use (default: claude)"
      echo "  --recent   Process only N most recent posts"
      echo "  --force    Regenerate even if SVG exists"
      exit 0 ;;
    *) SINGLE_POST="$1"; shift ;;
  esac
done

# SVG template reference (the base structure all SVGs should follow)
read -r -d '' SVG_PROMPT_TEMPLATE << 'PROMPT_END' || true
Generate an SVG image (1200x630) for a tech blog post. The SVG must follow this exact structure:

1. Dark gradient background (#0a0c1a base)
2. Subtle grid lines (4 horizontal + 4 vertical, very low opacity)
3. A UNIQUE decorative illustration on the right side (x=880-1140, y=130-350) that visually represents the post's topic. This should be composed of SVG shapes (paths, circles, rects, lines) - NOT text. Make it recognizable and distinctive. Examples:
   - For security: shield with lock, firewall layers
   - For cloud/AWS: cloud shapes with connection lines
   - For Kubernetes: hexagonal pod shapes, helm wheel
   - For AI/LLM: neural network nodes, brain outline
   - For ransomware: warning triangle, encrypted file icon
   - For DevOps: pipeline flow, CI/CD arrows
   - For blockchain: chain links, distributed nodes
   Use semi-transparent fills (opacity 0.05-0.15) and strokes (opacity 0.2-0.4)
4. 3 small alert dots (bottom-left area, x=860-900, y=400-440)
5. 2 large background circles (x=1050, y=450, r=200 and r=140, very subtle)
6. Left accent bar (6px wide, gradient matching theme)
7. Date badge (rounded rect at x=80, y=60)
8. Main title in 2 lines (font-size 46, white, bold, at y=185 and y=245) - summarize the post topic in English
9. Subtitle line (font-size 19, at y=300)
10. Accent gradient line (at y=325, width 420)
11. Category label (font-size 14, uppercase, at y=370)
12. 3 keyword tag pills (at y=420, height=36, rx=18) with different colors
13. Bottom rule + footer text (tech.2twodragon.com)

Color themes:
- Security: red #ef4444 → orange #f59e0b, bg ending #1a0a0a
- Cloud/AWS: blue #3b82f6 → cyan #06b6d4, bg ending #0a0a1a
- DevSecOps: purple #a855f7 → blue #3b82f6, bg ending #12061a
- DevOps: green #22c55e → cyan #06b6d4, bg ending #0a1a0a

CRITICAL RULES:
- ALL text must be English only (no Korean/CJK characters)
- Escape & as &amp; in all text
- Valid XML - test with xml.etree.ElementTree
- viewBox="0 0 1200 630" width="1200" height="630"
- Output ONLY the SVG code, no markdown fences, no explanation
PROMPT_END

# Extract post metadata
extract_metadata() {
  local post_file="$1"
  local filename=$(basename "$post_file" .md)
  local date_part=$(echo "$filename" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}')

  # Extract title from front matter
  local title=$(sed -n '/^---$/,/^---$/p' "$post_file" | grep "^title:" | head -1 | sed 's/^title: *//; s/^"//; s/"$//')

  # Extract categories
  local categories=$(sed -n '/^---$/,/^---$/p' "$post_file" | grep -A5 "^categor" | grep "^- " | sed 's/^- //' | tr '\n' ',' | sed 's/,$//')
  if [ -z "$categories" ]; then
    categories=$(sed -n '/^---$/,/^---$/p' "$post_file" | grep "^category:" | sed 's/^category: *//')
  fi

  # Extract excerpt
  local excerpt=$(sed -n '/^---$/,/^---$/p' "$post_file" | grep "^excerpt:" | head -1 | sed 's/^excerpt: *//; s/^"//; s/"$//' | cut -c1-200)

  # Extract image path
  local image=$(sed -n '/^---$/,/^---$/p' "$post_file" | grep "^image:" | head -1 | sed 's/^image: *//')

  echo "$date_part|$title|$categories|$excerpt|$image|$filename"
}

# Generate SVG using Claude CLI
generate_with_claude() {
  local title="$1"
  local categories="$2"
  local excerpt="$3"
  local date_str="$4"
  local output_file="$5"

  local prompt="Generate an SVG image (viewBox 0 0 1200 630) for a tech blog post.

Title: $title
Date: $date_str
Category: $categories

Requirements:
- Dark gradient background (#0a0c1a to #1a0a0a)
- Subtle grid lines (4H+4V, opacity 0.03-0.04)
- RIGHT SIDE (x=880-1140, y=130-320): A unique decorative icon made of SVG shapes representing the topic. Use semi-transparent fills (0.05-0.15) and strokes (0.2-0.4). Make it visually distinctive.
- Left accent bar (6px, gradient red-to-orange for security, blue-to-cyan for cloud)
- Date badge at (80,60): '$date_str'
- 2-line title at y=185 and y=245 (font-size 46, white, bold)
- Subtitle at y=300 (font-size 19)
- 3 keyword tag pills at y=420 (rx=18, different colors)
- Footer: tech.2twodragon.com at y=545
- ALL text English only, no Korean
- Valid XML, escape & as &amp;
- Output ONLY the SVG XML, nothing else"

  echo "  Using Claude CLI..." >&2
  local prompt_file=$(mktemp /tmp/claude-prompt-XXXXX.txt)
  local raw_file=$(mktemp /tmp/claude-raw-XXXXX)
  echo "$prompt" > "$prompt_file"
  claude -p "$(cat "$prompt_file")" --output-format text 2>/dev/null > "$raw_file" || true

  # Extract SVG from raw output (handles terminal escape sequences)
  python3 -c "
import re
with open('$raw_file') as f:
    content = f.read()
content = re.sub(r'\x1b[^a-zA-Z]*[a-zA-Z]', '', content)
content = re.sub(r'\x1b\][^\x07\x1b]*[\x07\x1b]?', '', content)
m = re.search(r'(<svg[\s\S]*?</svg>)', content)
if m:
    with open('$output_file', 'w') as f:
        f.write(m.group(1))
" 2>/dev/null
  rm -f "$raw_file" "$prompt_file"
}

# Generate SVG using Codex CLI
generate_with_codex() {
  local title="$1"
  local categories="$2"
  local excerpt="$3"
  local date_str="$4"
  local output_file="$5"

  local prompt="Generate an SVG (1200x630) for blog post '$title' ($date_str, $categories). Dark gradient bg, unique icon for the topic on right side, 2-line title, 3 tag pills. All text English. Output ONLY SVG XML."

  echo "  Using Codex CLI..." >&2
  codex -q --full-auto "$prompt" 2>/dev/null | tr -d '\r' > "$output_file"

  python3 -c "
import re
with open('$output_file') as f:
    content = f.read()
m = re.search(r'(<svg[\\s\\S]*?</svg>)', content)
if m:
    with open('$output_file', 'w') as f:
        f.write(m.group(1))
" 2>/dev/null || true
}

# Generate SVG using Gemini CLI
generate_with_gemini() {
  local title="$1"
  local categories="$2"
  local excerpt="$3"
  local date_str="$4"
  local output_file="$5"

  local prompt="Generate an SVG (1200x630) for blog post '$title' ($date_str, $categories). Dark gradient bg, unique icon for the topic on right side, 2-line title, 3 tag pills. All text English. Output ONLY SVG XML."

  echo "  Using Gemini CLI..." >&2
  gemini -p "$prompt" 2>/dev/null | tr -d '\r' > "$output_file"

  python3 -c "
import re
with open('$output_file') as f:
    content = f.read()
m = re.search(r'(<svg[\\s\\S]*?</svg>)', content)
if m:
    with open('$output_file', 'w') as f:
        f.write(m.group(1))
" 2>/dev/null || true
}

# Validate SVG
validate_svg() {
  local svg_file="$1"

  # Check if file exists and has content
  if [ ! -s "$svg_file" ]; then
    echo "FAIL: Empty file" >&2
    return 1
  fi

  # Check starts with <svg
  if ! head -1 "$svg_file" | grep -q '<svg'; then
    echo "FAIL: Does not start with <svg" >&2
    return 1
  fi

  # Validate XML
  if ! python3 -c "import xml.etree.ElementTree as ET; ET.parse('$svg_file')" 2>/dev/null; then
    echo "FAIL: Invalid XML" >&2
    return 1
  fi

  # Check for Korean text
  if python3 -c "
import re
with open('$svg_file') as f:
    if re.search(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', f.read()):
        exit(1)
" 2>/dev/null; then
    : # No Korean - good
  else
    echo "FAIL: Contains Korean text" >&2
    return 1
  fi

  return 0
}

# Main processing
process_post() {
  local post_file="$1"
  local metadata=$(extract_metadata "$post_file")

  local date_part=$(echo "$metadata" | cut -d'|' -f1)
  local title=$(echo "$metadata" | cut -d'|' -f2)
  local categories=$(echo "$metadata" | cut -d'|' -f3)
  local excerpt=$(echo "$metadata" | cut -d'|' -f4)
  local image_path=$(echo "$metadata" | cut -d'|' -f5)
  local filename=$(echo "$metadata" | cut -d'|' -f6)

  if [ -z "$image_path" ]; then
    echo "SKIP: No image field in $filename" >&2
    return 0
  fi

  local svg_file="${IMAGES_DIR}/$(basename "$image_path")"

  if [ "$FORCE" = false ] && [ -f "$svg_file" ]; then
    echo "SKIP: $svg_file already exists" >&2
    return 0
  fi

  # Format date for display
  local month_names=("" "JANUARY" "FEBRUARY" "MARCH" "APRIL" "MAY" "JUNE" "JULY" "AUGUST" "SEPTEMBER" "OCTOBER" "NOVEMBER" "DECEMBER")
  local year=$(echo "$date_part" | cut -d'-' -f1)
  local month_num=$(echo "$date_part" | cut -d'-' -f2 | sed 's/^0//')
  local day=$(echo "$date_part" | cut -d'-' -f3 | sed 's/^0//')
  local formatted_date="${month_names[$month_num]} $day, $year"

  echo "Processing: $filename"
  echo "  Title: $title"
  echo "  Date: $formatted_date"
  echo "  Engine: $ENGINE"

  local tmp_file=$(mktemp /tmp/svg-gen-XXXXX.svg)
  local success=false

  # Try primary engine
  case $ENGINE in
    claude)  generate_with_claude "$title" "$categories" "$excerpt" "$formatted_date" "$tmp_file" ;;
    codex)   generate_with_codex "$title" "$categories" "$excerpt" "$formatted_date" "$tmp_file" ;;
    gemini)  generate_with_gemini "$title" "$categories" "$excerpt" "$formatted_date" "$tmp_file" ;;
  esac

  # Validate
  if validate_svg "$tmp_file"; then
    cp "$tmp_file" "$svg_file"
    echo "  ✅ Generated: $svg_file"
    success=true
  else
    echo "  ❌ Validation failed, trying fallback..." >&2
    # Try Claude as fallback if not already primary
    if [ "$ENGINE" != "claude" ]; then
      generate_with_claude "$title" "$categories" "$excerpt" "$formatted_date" "$tmp_file"
      if validate_svg "$tmp_file"; then
        cp "$tmp_file" "$svg_file"
        echo "  ✅ Generated (fallback claude): $svg_file"
        success=true
      fi
    fi
  fi

  rm -f "$tmp_file"

  if [ "$success" = false ]; then
    echo "  ❌ FAILED: Could not generate valid SVG" >&2
    return 1
  fi
}

# Get post files to process
if [ -n "$SINGLE_POST" ]; then
  POST_FILES=("$SINGLE_POST")
elif [ "$RECENT" -gt 0 ]; then
  POST_FILES=($(ls -1 "$POSTS_DIR"/*.md | sort -r | head -n "$RECENT"))
else
  POST_FILES=($(ls -1 "$POSTS_DIR"/*.md | sort -r))
fi

echo "========================================="
echo "  AI SVG Image Generator"
echo "  Engine: $ENGINE"
echo "  Posts: ${#POST_FILES[@]}"
echo "  Force: $FORCE"
echo "========================================="
echo ""

SUCCESS=0
FAILED=0
SKIPPED=0

for post in "${POST_FILES[@]}"; do
  result=$(process_post "$post" 2>&1) || true
  echo "$result"

  if echo "$result" | grep -q "✅"; then
    SUCCESS=$((SUCCESS + 1))
  elif echo "$result" | grep -q "SKIP"; then
    SKIPPED=$((SKIPPED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
  echo ""
done

echo "========================================="
echo "  Results: $SUCCESS generated, $SKIPPED skipped, $FAILED failed"
echo "========================================="

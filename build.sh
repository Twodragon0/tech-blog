#!/bin/bash
set -e  # Exit on any error
set -o pipefail  # Exit on pipe failures

# Set UTF-8 encoding for Korean filenames
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LANGUAGE=C.UTF-8

# Pinned Noto Sans KR variable font source (notofonts/noto-cjk @f8d1575)
# Update this SHA when bumping the upstream Noto release (see docs/optimization/NOTO_SANS_SELF_HOST_RUNBOOK.md §3).
export NOTO_VF_URL='https://raw.githubusercontent.com/notofonts/noto-cjk/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf'

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check required commands
log "Checking required commands..."
command -v bundle >/dev/null 2>&1 || error_exit "bundle command not found"
command -v ruby >/dev/null 2>&1 || error_exit "ruby command not found"

# Display environment info
log "Environment information:"
log "  Ruby version: $(ruby -v)"
log "  Bundler version: $(bundle -v)"
log "  Working directory: $(pwd)"
log "  LANG: $LANG"
log "  LC_ALL: $LC_ALL"

# ---------------------------------------------------------------------------
# Vercel-side build dependencies (AL2023 / RPM-based image only).
# Moved out of vercel.json installCommand to stay under its 256-char hard
# limit. The dnf/yum guard means this block silently skips on macOS / CI
# Ubuntu runners where the same dependencies are pre-installed via Homebrew
# (rsvg) or the workflow's apt-get step.
# ---------------------------------------------------------------------------
if command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
    log "Installing Vercel build dependencies (RPM-based runtime detected)..."
    # rsvg-convert (cascade priority 1 for rasterize_svg_covers.py)
    (dnf install -y --quiet librsvg2-tools 2>/dev/null \
     || yum install -y --quiet librsvg2-tools 2>/dev/null \
     || true)
    # Pillow (favicon) + cairosvg (cascade priority 2 fallback)
    (python3 -m pip install --quiet --no-cache-dir --break-system-packages Pillow 'cairosvg>=2.7.0,<3.0' 2>/dev/null \
     || pip3 install --quiet --no-cache-dir --break-system-packages Pillow 'cairosvg>=2.7.0,<3.0' 2>/dev/null \
     || true)
    log "  rsvg-convert: $(command -v rsvg-convert 2>/dev/null || echo 'not installed (cascade falls through to cairosvg)')"
fi

# ---------------------------------------------------------------------------
# Noto Sans KR woff2 subset regeneration (conditional, graceful failure)
# ---------------------------------------------------------------------------
if [ -f "scripts/build/generate_noto_2tier_subset.py" ]; then
  log "Checking Noto Sans KR woff2 subset freshness..."
  STAMP=".noto-subset.stamp"
  NEEDS_REGEN=0
  if [ ! -f "assets/fonts/noto-sans-kr-400-tier1.woff2" ]; then NEEDS_REGEN=1; fi
  if [ ! -f "assets/fonts/noto-sans-kr-700-tier2.woff2" ]; then NEEDS_REGEN=1; fi
  if [ ! -f "$STAMP" ] || [ "scripts/build/generate_noto_2tier_subset.py" -nt "$STAMP" ] || [ "scripts/build/noto_subset_top1k.txt" -nt "$STAMP" ]; then
    NEEDS_REGEN=1
  fi
  if [ "$NEEDS_REGEN" = "1" ]; then
    log "Regenerating Noto woff2 subsets (NOTO_VF_URL=${NOTO_VF_URL})..."
    # Ensure fonttools[woff] is available (graceful failure if pip not on PATH)
    pip install --quiet 'fonttools[woff]>=4.55.0' 2>/dev/null || true
    python3 scripts/build/generate_noto_2tier_subset.py || {
      log "WARN: Noto regeneration failed; using existing woff2 files (build continues)"
    }
    touch "$STAMP"
  else
    log "Noto woff2 subsets are up-to-date; skipping regeneration"
  fi
fi

log "Generating favicons..."
if ! python3 scripts/generate_favicon.py; then
    if [ -f "assets/images/favicon.png" ]; then
        log "Favicon 생성 실패했으나 기존 favicon.png 사용"
    else
        error_exit "Favicon generation failed (Pillow 필요: pip install Pillow)"
    fi
fi

# ---------------------------------------------------------------------------
# Rasterize SVG cover images (image: /assets/images/foo.svg in any post's
# front matter) that lack an _og.png companion. Must run BEFORE the modern-
# variants step below — that one derives _og.{webp,avif} from _og.png, so
# fresh PNGs from this step feed it within the same build.
#
# Backend cascade (rsvg-convert → cairosvg → soft-fail). A thin runtime
# without librsvg keeps building; the only consequence is SVG-only posts
# fall through to <img src="...svg"> via the is-svg-image class hook.
# ---------------------------------------------------------------------------
log "Rasterizing SVG covers without _og.png (skip-if-exists)..."
if ! python3 scripts/build/rasterize_svg_covers.py; then
    log "WARN: SVG → PNG rasterization reported errors; build continues with whatever covers exist on disk"
fi

# ---------------------------------------------------------------------------
# Backfill _og.avif / _og.webp from any _og.png that lacks modern variants.
# Idempotent (skip-if-exists), so steady-state builds add zero overhead;
# only fires when a new post lands an _og.png without companion variants.
# Soft failure: missing Pillow logs a warning and the build continues.
# ---------------------------------------------------------------------------
log "Backfilling _og.avif / _og.webp variants (skip-if-exists)..."
if ! python3 scripts/build/backfill_og_modern_variants.py; then
    log "WARN: modern-format backfill reported errors; build continues with whatever variants exist on disk"
fi

# Inject Sentry DSN from Vercel env var (if set, overrides _config.yml)
if [ -n "$SENTRY_DSN" ]; then
    log "Injecting Sentry DSN from environment variable..."
    python3 -c "
import re, sys
with open('_config.yml', 'r') as f:
    content = f.read()
dsn = sys.argv[1].strip().strip('\"').strip(\"'\")
content = re.sub(r'^sentry_dsn:.*$', 'sentry_dsn: \"' + dsn + '\"', content, flags=re.MULTILINE)
with open('_config.yml', 'w') as f:
    f.write(content)
print('DSN injected: ' + dsn[:30] + '...' + dsn[-15:])
" "$SENTRY_DSN"
    log "✅ Sentry DSN injected from env var"
fi

# Clean previous build
log "Cleaning previous build output..."
rm -rf _site || true

# Build Jekyll with verbose output
log "Building Jekyll site..."
# Support baseurl from environment (for GitHub Pages)
BASEURL="${BASEURL:-}"
BUILD_ARGS="--verbose --trace"
if [ -n "$BASEURL" ]; then
    BUILD_ARGS="$BUILD_ARGS --baseurl $BASEURL"
    log "Using baseurl: $BASEURL"
fi

set +e
bundle exec jekyll build $BUILD_ARGS 2>&1 | tee /tmp/jekyll-build.log
BUILD_EXIT=${PIPESTATUS[0]:-$?}
set -e
if [ "$BUILD_EXIT" -ne 0 ]; then
    log "Jekyll build failed (exit $BUILD_EXIT). Error summary:"
    grep -iE "error|exception|fatal" /tmp/jekyll-build.log | head -10 >&2 || true
    error_exit "Jekyll build failed"
fi

# Verify build output
if [ ! -d "_site" ]; then
    error_exit "_site directory not created"
fi

# Verify critical CSS file
log "Verifying CSS compilation..."
if [ -f "_site/assets/css/main.css" ]; then
    CSS_SIZE=$(stat -f%z "_site/assets/css/main.css" 2>/dev/null || stat -c%s "_site/assets/css/main.css" 2>/dev/null || echo "0")
    log "✅ CSS compiled successfully: _site/assets/css/main.css (${CSS_SIZE} bytes)"
else
    log "ERROR: CSS file not found at _site/assets/css/main.css"
    log "Checking _site/assets/css/ directory contents:"
    ls -la _site/assets/css/ 2>&1 || log "Directory does not exist"
    log "Checking if SCSS source exists:"
    ls -la assets/css/main.scss 2>&1 || log "SCSS source not found"
    error_exit "CSS compilation failed - main.css not generated"
fi

# Minify JS files in _site (preserves source files in assets/js/)
if command -v npx >/dev/null 2>&1 && npx terser --version >/dev/null 2>&1; then
    log "Minifying JS files in _site/assets/js/..."
    JS_FILES=( _site/assets/js/*.js )
    if [ -e "${JS_FILES[0]}" ]; then
        JS_BEFORE=$(du -sk _site/assets/js/*.js 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        for f in _site/assets/js/*.js; do
            npx terser "$f" -o "$f" -c passes=2 -m
        done
        JS_AFTER=$(du -sk _site/assets/js/*.js 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        log "JS minification complete: ${JS_BEFORE} KB -> ${JS_AFTER} KB"
    else
        log "No JS files found in _site/assets/js/, skipping minification"
    fi
else
    log "terser not available, skipping JS minification"
fi

log "Build completed successfully!"
log "Build output size: $(du -sh _site | cut -f1)"

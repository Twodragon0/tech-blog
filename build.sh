#!/bin/bash
set -e  # Exit on any error
set -o pipefail  # Exit on pipe failures

# Set UTF-8 encoding for Korean filenames
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LANGUAGE=C.UTF-8

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

log "Generating favicons..."
if ! python3 scripts/generate_favicon.py; then
    if [ -f "assets/images/favicon.png" ]; then
        log "Favicon 생성 실패했으나 기존 favicon.png 사용"
    else
        error_exit "Favicon generation failed (Pillow 필요: pip install Pillow)"
    fi
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

bundle exec jekyll build $BUILD_ARGS 2>&1 | tee /tmp/jekyll-build.log || {
    log "Jekyll build failed. Last 50 lines of output:"
    tail -n 50 /tmp/jekyll-build.log >&2
    error_exit "Jekyll build failed"
}

# Verify build output
if [ ! -d "_site" ]; then
    error_exit "_site directory not created"
fi

# Minify JavaScript (optional, graceful failure)
log "Minifying JavaScript..."
if [ -f "_site/assets/js/main.js" ]; then
    # Check if terser is available
    if command -v npx >/dev/null 2>&1 && [ -f "node_modules/.bin/terser" ] || [ -f "package.json" ]; then
        # Try to use local terser first, then npx
        if [ -f "node_modules/.bin/terser" ]; then
            ./node_modules/.bin/terser _site/assets/js/main.js -o _site/assets/js/main.js -c -m || log "WARNING: terser command failed, using unminified JS"
        elif npx --yes terser _site/assets/js/main.js -o _site/assets/js/main.js -c -m 2>/dev/null; then
            log "✅ JavaScript minified successfully"
        else
            log "WARNING: terser command failed, using unminified JS"
        fi
    else
        log "INFO: terser not available, skipping minification (optional step)"
    fi
else
    log "WARNING: _site/assets/js/main.js not found, skipping minification."
fi

log "Build completed successfully!"
log "Build output size: $(du -sh _site | cut -f1)"

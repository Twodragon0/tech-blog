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
python3 scripts/generate_favicon.py || error_exit "Favicon generation failed"

# Clean previous build
log "Cleaning previous build output..."
rm -rf _site || true

# Build Jekyll with verbose output
log "Building Jekyll site..."
bundle exec jekyll build --verbose --trace 2>&1 | tee /tmp/jekyll-build.log || {
    log "Jekyll build failed. Last 50 lines of output:"
    tail -n 50 /tmp/jekyll-build.log >&2
    error_exit "Jekyll build failed"
}

# Verify build output
if [ ! -d "_site" ]; then
    error_exit "_site directory not created"
fi

# Minify JavaScript
log "Minifying JavaScript..."
if [ -f "_site/assets/js/main.js" ]; then
    npx terser _site/assets/js/main.js -o _site/assets/js/main.js -c -m || log "WARNING: terser command failed, using unminified JS"
else
    log "WARNING: _site/assets/js/main.js not found, skipping minification."
fi

log "Build completed successfully!"
log "Build output size: $(du -sh _site | cut -f1)"

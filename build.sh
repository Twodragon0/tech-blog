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

# Inject Sentry DSN from Vercel env var (if set, overrides _config.yml)
if [ -n "$SENTRY_DSN" ]; then
    log "Injecting Sentry DSN from environment variable..."
    # Use python3 for safe YAML value replacement (avoids sed special char issues with URLs)
    python3 -c "
import re, sys
with open('_config.yml', 'r') as f:
    content = f.read()
dsn = sys.argv[1]
content = re.sub(r'^sentry_dsn:.*$', f'sentry_dsn: \"{dsn}\"', content, flags=re.MULTILINE)
with open('_config.yml', 'w') as f:
    f.write(content)
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
bundle exec jekyll build $BUILD_ARGS > /tmp/jekyll-build.log 2>&1
BUILD_EXIT=$?
set -e
cat /tmp/jekyll-build.log
if [ "$BUILD_EXIT" -ne 0 ]; then
    log "=== JEKYLL BUILD FAILED (exit $BUILD_EXIT) ==="
    log "=== ERROR LINES ==="
    grep -iE "error|exception|fatal|invalid" /tmp/jekyll-build.log >&2 || true
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

# Verify and Minify JavaScript
log "Verifying JavaScript..."
if [ -f "_site/assets/js/main.js" ]; then
    JS_SIZE_BEFORE=$(stat -f%z "_site/assets/js/main.js" 2>/dev/null || stat -c%s "_site/assets/js/main.js" 2>/dev/null || echo "0")
    log "📄 JS size before minification: ${JS_SIZE_BEFORE} bytes"
    
    # Verify table-wrapper code exists
    if grep -q "table-wrapper" "_site/assets/js/main.js"; then
        log "✅ table-wrapper code found in JS"
    else
        log "⚠️ WARNING: table-wrapper code NOT found in JS - checking source..."
        if grep -q "table-wrapper" "assets/js/main.js"; then
            log "✅ table-wrapper exists in source, copying fresh..."
            cp "assets/js/main.js" "_site/assets/js/main.js"
        fi
    fi
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
    
    JS_SIZE_AFTER=$(stat -f%z "_site/assets/js/main.js" 2>/dev/null || stat -c%s "_site/assets/js/main.js" 2>/dev/null || echo "0")
    log "📄 JS size after processing: ${JS_SIZE_AFTER} bytes"
else
    log "WARNING: _site/assets/js/main.js not found, skipping minification."
fi

log "Build completed successfully!"
log "Build output size: $(du -sh _site | cut -f1)"

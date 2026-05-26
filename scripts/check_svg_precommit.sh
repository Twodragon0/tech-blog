#!/bin/sh
# SVG Quality Gate — pre-commit fragment.
#
# Thin delegator: forwards to scripts/check_svg_size_gate.py so the
# pre-commit hook and the CI workflow share one implementation of the
# size-band classifier (std / hq / rollup). The Python script reads
# ``--staged`` and reproduces the legacy shell behavior exactly:
# warn-only, exit 0, restricted to files in the git index.
#
# Source of truth for bands + markers:
#   scripts/check_svg_size_gate.py
#
# To run manually:
#   python3 scripts/check_svg_size_gate.py --staged
#   python3 scripts/check_svg_size_gate.py --all
#
# Usage: called by .git/hooks/pre-commit (via install-hooks.sh).
# Exit code: 0 always (warn-only, does not block commit).

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

GATE="$REPO_ROOT/scripts/check_svg_size_gate.py"
if [ ! -f "$GATE" ]; then
  # Python gate missing — silently no-op rather than blocking commits.
  exit 0
fi

# Warn-only mode: ignore exit code, emit warnings to stderr-bound stdout.
python3 "$GATE" --staged || true
exit 0

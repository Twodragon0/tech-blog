#!/usr/bin/env bash
# API 키 설정 및 Gemini CLI 상태 확인 (값은 출력하지 않음)
set -e

echo "=== API & CLI verification ==="
[ -n "$GEMINI_API_KEY" ] && echo "GEMINI_API_KEY: set" || echo "GEMINI_API_KEY: not set"
[ -n "$CLAUDE_API_KEY" ] && echo "CLAUDE_API_KEY: set" || echo "CLAUDE_API_KEY: not set"
if command -v gemini &>/dev/null; then
  echo "Gemini CLI: $(gemini --version 2>/dev/null || echo 'installed')"
else
  echo "Gemini CLI: not found"
fi
echo "---"
echo "For image generation: set GEMINI_API_KEY or use Gemini CLI OAuth (see setup_gemini_oauth.sh)"
echo "For content improvement: set CLAUDE_API_KEY or GEMINI_API_KEY (see setup_ai_keys.sh)"

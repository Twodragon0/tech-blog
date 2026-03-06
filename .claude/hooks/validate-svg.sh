#!/bin/bash
# validate-svg.sh - Block Korean text in SVG files (macOS compatible)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
NEW_CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

if [[ "$FILE_PATH" == *.svg && -n "$NEW_CONTENT" ]]; then
  if echo "$NEW_CONTENT" | perl -CSD -e '$t=join("",<STDIN>); exit(1) if $t=~/[\x{AC00}-\x{D7AF}\x{1100}-\x{11FF}]/'; then
    exit 0
  else
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Korean characters detected in SVG file. SVG text must be English only."}}' >&2
    exit 2
  fi
fi
exit 0

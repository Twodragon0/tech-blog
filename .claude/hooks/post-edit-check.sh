#!/bin/bash
# post-edit-check.sh - Validate post front matter after edits
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" == *"_posts/"* && "$FILE_PATH" == *.md ]]; then
  BASENAME=$(basename "$FILE_PATH")
  if ! echo "$BASENAME" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}-[A-Za-z0-9_-]+\.md$'; then
    echo "Warning: Post filename should be YYYY-MM-DD-English_Title.md (no Korean)" >&2
  fi
fi
exit 0

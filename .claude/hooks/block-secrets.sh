#!/bin/bash
# PreToolUse hook: block editing of secret/database files
# Reads tool input from stdin as JSON

filepath=$(jq -r '.tool_input.file_path // empty')

if [[ -z "$filepath" ]]; then
  exit 0
fi

filename=$(basename "$filepath")

# Block database files
if [[ "$filepath" == *.db || "$filepath" == *.sqlite3 ]]; then
  echo "BLOCKED: Cannot edit database files ($filepath)" >&2
  exit 2
fi

exit 0

#!/bin/bash
# PostToolUse hook: auto-lint on file edit
# Reads tool input from stdin as JSON

PROJECT_ROOT="/Users/bany1111/local-workspace/daily-scheduler"
filepath=$(jq -r '.tool_input.file_path // empty')

if [[ -z "$filepath" ]]; then
  exit 0
fi

# Python files in backend
if [[ "$filepath" == */backend/* && "$filepath" == *.py ]]; then
  cd "$PROJECT_ROOT/backend" || exit 0
  uv run ruff format "$filepath"
  uv run ruff check --fix "$filepath"
  uv run pyrefly check "$filepath" --warn "implicit-any,unannotated-return"
  uv run pylint "$filepath"
  lint_exit=$?

  # Auto-regenerate OpenAPI types when schema files change
  if [[ "$filepath" == */schemas/*.py ]] || [[ "$filepath" == */routes/*.py ]]; then
    cd "$PROJECT_ROOT" || exit 0
    make generate-types 2>/dev/null &
  fi

  exit $lint_exit
fi

# TypeScript/JavaScript files in frontend
if [[ "$filepath" == */frontend/* && "$filepath" =~ \.(ts|tsx|js|jsx)$ ]]; then
  cd "$PROJECT_ROOT/frontend" || exit 0
  npx oxlint "$filepath"
  exit $?
fi

exit 0

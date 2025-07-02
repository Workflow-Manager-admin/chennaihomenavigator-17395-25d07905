#!/bin/bash
# Robust linter script – always uses the correct venv and project paths

PROJECT_ROOT="/home/kavia/workspace/code-generation/chennaihomenavigator-17395-25d07905"
VENV_PATH="$PROJECT_ROOT/venv"

if [ ! -f "$VENV_PATH/bin/flake8" ]; then
  echo "Error: flake8 not found in venv. Did you forget to install dependencies?" >&2
  exit 1
fi

"$VENV_PATH/bin/flake8" "$PROJECT_ROOT/homequestai_backend/src"
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

exit 0

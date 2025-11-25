#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/test_run.log"

mkdir -p "$LOG_DIR"

# Helper to run pytest and mirror output to log
run_and_log() {
  local phase="$1"; shift
  echo "===== $phase =====" | tee -a "$LOG_FILE"
  # Use env vars for predictable credentials during tests
  USERS_JSON='{"bob":"Password1!"}' \
  CSRF_TOKEN='TEST_CSRF_TOKEN' \
    pytest -q "$ROOT_DIR/tests" "$@" 2>&1 | tee -a "$LOG_FILE"
}

# Preserve current working copy
TMP_CURRENT="$ROOT_DIR/.tmp_input_current.py"
cp "$ROOT_DIR/input.py" "$TMP_CURRENT"

# 1) Original code should fail tests
cp "$ROOT_DIR/input_original.py" "$ROOT_DIR/input.py"
set +e
run_and_log "Tests against ORIGINAL code (expected to FAIL)"
ORIG_STATUS=${PIPESTATUS[0]}
set -e
if [ $ORIG_STATUS -eq 0 ]; then
  echo "ERROR: Tests unexpectedly passed against original code." | tee -a "$LOG_FILE"
  cp "$TMP_CURRENT" "$ROOT_DIR/input.py"
  exit 1
fi

# 2) Fixed code should pass tests
cp "$ROOT_DIR/input_fixed.py" "$ROOT_DIR/input.py"
run_and_log "Tests against FIXED code (expected to PASS)"
FIXED_STATUS=${PIPESTATUS[0]}
if [ $FIXED_STATUS -ne 0 ]; then
  echo "ERROR: Tests failed against fixed code." | tee -a "$LOG_FILE"
  cp "$TMP_CURRENT" "$ROOT_DIR/input.py"
  exit 1
fi

# Restore working copy (fixed)
cp "$TMP_CURRENT" "$ROOT_DIR/input.py"
rm -f "$TMP_CURRENT"

echo "All checks completed. Original: FAILED (expected). Fixed: PASSED." | tee -a "$LOG_FILE"

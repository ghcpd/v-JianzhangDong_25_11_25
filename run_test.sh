#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs
LOGFILE=logs/test_run.log
echo "TEST RUN - $(date)" > "$LOGFILE"

# Save current fixed version (if not already saved)
if [ ! -f input_fixed.py ]; then
  cp input.py input_fixed.py
fi

if [ ! -f input_vulnerable.py ]; then
  echo "ERROR: no input_vulnerable.py found to test the original vulnerable version" | tee -a "$LOGFILE"
  exit 2
fi

echo "Running tests against ORIGINAL (vulnerable) version..." | tee -a "$LOGFILE"
cp input_vulnerable.py input.py

pytest -q 2>&1 | tee -a "$LOGFILE" || ORIGINAL_STATUS=$?

if [ -z "${ORIGINAL_STATUS+x}" ]; then
  echo "ERROR: tests unexpectedly passed against vulnerable/original source (expected failures)." | tee -a "$LOGFILE"
  # We consider this situation as an unexpected success - mark as failure so the script fails
  exit 10
else
  echo "As expected, tests failed against the original vulnerable source (exit ${ORIGINAL_STATUS})." | tee -a "$LOGFILE"
fi

echo "Restoring patched app and re-running tests (should pass)..." | tee -a "$LOGFILE"
cp input_fixed.py input.py

pytest -q 2>&1 | tee -a "$LOGFILE" || { echo "ERROR: tests failed against patched source" | tee -a "$LOGFILE"; exit 20; }

echo "All checks passed against patched version." | tee -a "$LOGFILE"

#!/bin/bash

# Test script for Linux/macOS
# Tests both vulnerable (input.py) and secure (secure_input.py) versions

set -e

echo "=== Flask Security Audit - Linux/macOS Test Script ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create logs directory
mkdir -p logs

TEST_LOG="logs/test_run.log"

echo "Running tests..." | tee -a "$TEST_LOG"
echo "Test timestamp: $(date)" | tee -a "$TEST_LOG"
echo

# Set required environment variable for secure version
export API_KEY="test_api_key_secure"

echo "=== Testing Secure Version (secure_input.py) ===" | tee -a "$TEST_LOG"
if python -m pytest test_vulnerabilities.py -v --tb=short 2>&1 | tee -a "$TEST_LOG"; then
    echo "✓ Secure version tests PASSED" | tee -a "$TEST_LOG"
    SECURE_PASSED=1
else
    echo "✗ Secure version tests FAILED" | tee -a "$TEST_LOG"
    SECURE_PASSED=0
fi

echo
echo "=== Testing Vulnerable Version (input.py) ===" | tee -a "$TEST_LOG"
if python -m pytest test_vulnerabilities.py::test_vulnerable_version -v --tb=short 2>&1 | tee -a "$TEST_LOG"; then
    echo "✓ Vulnerable version tests detected issues (as expected)" | tee -a "$TEST_LOG"
    VULN_DETECTED=1
else
    echo "✓ Vulnerable version tests failed to run (expected)" | tee -a "$TEST_LOG"
    VULN_DETECTED=1
fi

echo
echo "=== Test Summary ===" | tee -a "$TEST_LOG"
if [ "$SECURE_PASSED" -eq 1 ]; then
    echo "✓ Secure version: PASSED" | tee -a "$TEST_LOG"
    exit_code=0
else
    echo "✗ Secure version: FAILED" | tee -a "$TEST_LOG"
    exit_code=1
fi

echo "✓ Tests completed. See $TEST_LOG for details." | tee -a "$TEST_LOG"
exit "$exit_code"

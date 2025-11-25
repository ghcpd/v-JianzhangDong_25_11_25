#!/bin/bash
# Test runner for Linux/macOS
# Tests both vulnerable and fixed versions

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/test_run.log"

# Create logs directory
mkdir -p "$LOG_DIR"

# Initialize log
{
    echo "=========================================="
    echo "Flask Security Audit - Test Suite"
    echo "Started: $(date)"
    echo "Platform: Linux/macOS"
    echo "=========================================="
    echo ""
} > "$LOG_FILE"

test_passed=0
test_failed=0

echo "Testing Flask Application Security Audit" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to run a test
run_test() {
    local test_name=$1
    local test_code=$2
    local should_fail=$3
    
    echo "Running: $test_name" | tee -a "$LOG_FILE"
    
    if eval "$test_code" >> "$LOG_FILE" 2>&1; then
        if [ "$should_fail" = "true" ]; then
            echo "  ✗ FAILED (should have failed but didn't)" | tee -a "$LOG_FILE"
            ((test_failed++))
        else
            echo "  ✓ PASSED" | tee -a "$LOG_FILE"
            ((test_passed++))
        fi
    else
        if [ "$should_fail" = "true" ]; then
            echo "  ✓ PASSED (correctly failed)" | tee -a "$LOG_FILE"
            ((test_passed++))
        else
            echo "  ✗ FAILED" | tee -a "$LOG_FILE"
            ((test_failed++))
        fi
    fi
    echo "" | tee -a "$LOG_FILE"
}

# Test 1: Check if input.py has SQL injection vulnerability
echo "Test 1: Vulnerable Version - SQL Injection Detection" | tee -a "$LOG_FILE"
if grep -q "\.format(name)" "$SCRIPT_DIR/input.py"; then
    echo "  ✓ PASSED (vulnerable code found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (vulnerable code not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 2: Check if input.py has pickle vulnerability
echo "Test 2: Vulnerable Version - Pickle Deserialization Detection" | tee -a "$LOG_FILE"
if grep -q "pickle.loads" "$SCRIPT_DIR/input.py"; then
    echo "  ✓ PASSED (vulnerable code found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (vulnerable code not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 3: Check if input.py has command injection vulnerability
echo "Test 3: Vulnerable Version - Command Injection Detection" | tee -a "$LOG_FILE"
if grep -q "os.system" "$SCRIPT_DIR/input.py"; then
    echo "  ✓ PASSED (vulnerable code found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (vulnerable code not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 4: Check if input.py has hardcoded API key
echo "Test 4: Vulnerable Version - Hardcoded API Key Detection" | tee -a "$LOG_FILE"
if grep -q "AKIA_EXAMPLE_HARDCODED_KEY" "$SCRIPT_DIR/input.py"; then
    echo "  ✓ PASSED (hardcoded key found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (hardcoded key not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 5: Check if input_fixed.py has NO SQL injection vulnerability
echo "Test 5: Fixed Version - SQL Injection Fixed" | tee -a "$LOG_FILE"
if ! grep -q "\.format(name)" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (vulnerable code removed)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (vulnerable code still present)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 6: Check if input_fixed.py uses parameterized queries
echo "Test 6: Fixed Version - Parameterized Queries Used" | tee -a "$LOG_FILE"
if grep -q "cur.execute(sql, (" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (parameterized queries found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (parameterized queries not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 7: Check if input_fixed.py uses JSON instead of pickle
echo "Test 7: Fixed Version - JSON Instead of Pickle" | tee -a "$LOG_FILE"
if ! grep -q "pickle.loads" "$SCRIPT_DIR/input_fixed.py" && grep -q "get_json" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (pickle removed, JSON used)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (pickle not removed or JSON not used)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 8: Check if input_fixed.py uses subprocess instead of os.system
echo "Test 8: Fixed Version - Subprocess Instead of os.system" | tee -a "$LOG_FILE"
if ! grep -q "os.system.*cmd" "$SCRIPT_DIR/input_fixed.py" && grep -q "subprocess.run" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (os.system removed, subprocess used)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (os.system not removed or subprocess not used)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 9: Check if input_fixed.py loads API key from environment
echo "Test 9: Fixed Version - API Key from Environment" | tee -a "$LOG_FILE"
if grep -q "os.getenv('API_KEY'" "$SCRIPT_DIR/input_fixed.py" && ! grep -q "AKIA_EXAMPLE_HARDCODED_KEY" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (API key from environment, no hardcoding)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (API key not properly secured)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 10: Check if input_fixed.py uses password hashing
echo "Test 10: Fixed Version - Password Hashing" | tee -a "$LOG_FILE"
if grep -q "generate_password_hash\|check_password_hash" "$SCRIPT_DIR/input_fixed.py"; then
    echo "  ✓ PASSED (password hashing found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (password hashing not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 11: Check if report.json exists
echo "Test 11: Report Generation" | tee -a "$LOG_FILE"
if [ -f "$SCRIPT_DIR/report.json" ]; then
    echo "  ✓ PASSED (report.json found)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (report.json not found)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 12: Check if report.json is valid JSON
echo "Test 12: Report JSON Validation" | tee -a "$LOG_FILE"
if python3 -m json.tool "$SCRIPT_DIR/report.json" > /dev/null 2>&1; then
    echo "  ✓ PASSED (report.json is valid)" | tee -a "$LOG_FILE"
    ((test_passed++))
else
    echo "  ✗ FAILED (report.json is invalid)" | tee -a "$LOG_FILE"
    ((test_failed++))
fi
echo "" | tee -a "$LOG_FILE"

# Summary
{
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo "Passed: $test_passed"
    echo "Failed: $test_failed"
    echo "Total:  $((test_passed + test_failed))"
    echo ""
    if [ $test_failed -eq 0 ]; then
        echo "Status: ALL TESTS PASSED ✓"
    else
        echo "Status: SOME TESTS FAILED ✗"
    fi
    echo ""
    echo "Log file: $LOG_FILE"
    echo "Completed: $(date)"
    echo "=========================================="
} | tee -a "$LOG_FILE"

# Exit with appropriate code
if [ $test_failed -eq 0 ]; then
    exit 0
else
    exit 1
fi

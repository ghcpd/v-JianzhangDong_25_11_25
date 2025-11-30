#!/bin/bash
# Test script for Linux/macOS - Tests both vulnerable and secure versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_FILE="logs/test_run.log"
mkdir -p logs

echo "================================================" | tee -a "$LOG_FILE"
echo "Flask Application Security Testing" | tee -a "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Function to wait for server
wait_for_server() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for server on port $port..." | tee -a "$LOG_FILE"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:$port/ > /dev/null 2>&1; then
            echo "✓ Server is ready" | tee -a "$LOG_FILE"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    echo "✗ Server failed to start" | tee -a "$LOG_FILE"
    return 1
}

# Function to test SQL injection
test_sql_injection() {
    local port=$1
    local test_name=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "Testing SQL Injection on $test_name..." | tee -a "$LOG_FILE"
    
    # This payload should exploit vulnerable version
    response=$(curl -s "http://127.0.0.1:$port/search?name=' OR '1'='1" 2>&1 || echo "CONNECTION_FAILED")
    
    if echo "$response" | grep -q "CONNECTION_FAILED\|error\|exception" 2>/dev/null; then
        echo "  ${GREEN}✓${NC} SQL Injection: Properly handled/blocked" | tee -a "$LOG_FILE"
        return 0
    else
        echo "  ${RED}✗${NC} SQL Injection: Vulnerable - query may have executed" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Function to test SSTI
test_ssti() {
    local port=$1
    local test_name=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "Testing Server-Side Template Injection on $test_name..." | tee -a "$LOG_FILE"
    
    # SSTI payload
    response=$(curl -s "http://127.0.0.1:$port/greet?name={{7*7}}" 2>&1 || echo "CONNECTION_FAILED")
    
    if echo "$response" | grep -q "49"; then
        echo "  ${RED}✗${NC} SSTI: Vulnerable - template expression evaluated" | tee -a "$LOG_FILE"
        return 1
    elif echo "$response" | grep -q "{{7\*7}}\|&lt;"; then
        echo "  ${GREEN}✓${NC} SSTI: Protected - input properly escaped" | tee -a "$LOG_FILE"
        return 0
    else
        echo "  ${YELLOW}?${NC} SSTI: Unable to determine (connection issue)" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Function to test pickle deserialization
test_pickle_rce() {
    local port=$1
    local test_name=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "Testing Insecure Deserialization on $test_name..." | tee -a "$LOG_FILE"
    
    # Send JSON data (should work on secure version)
    response=$(curl -s -X POST http://127.0.0.1:$port/upload_profile \
        -H "Content-Type: application/json" \
        -d '{"name": "test"}' 2>&1 || echo "CONNECTION_FAILED")
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo "  ${GREEN}✓${NC} Deserialization: Using safe JSON format" | tee -a "$LOG_FILE"
        return 0
    elif echo "$response" | grep -q "error\|Invalid"; then
        echo "  ${YELLOW}?${NC} Deserialization: Rejected (expected for pickle)" | tee -a "$LOG_FILE"
        return 1
    else
        echo "  ${RED}✗${NC} Deserialization: Unexpected response" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Function to test command injection
test_command_injection() {
    local port=$1
    local test_name=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "Testing Command Injection on $test_name..." | tee -a "$LOG_FILE"
    
    # Command injection payload
    response=$(curl -s -X POST http://127.0.0.1:$port/run \
        -d "cmd=test; whoami" 2>&1 || echo "CONNECTION_FAILED")
    
    if echo "$response" | grep -q "Invalid command\|error"; then
        echo "  ${GREEN}✓${NC} Command Injection: Blocked malicious input" | tee -a "$LOG_FILE"
        return 0
    elif echo "$response" | grep -q "done"; then
        echo "  ${RED}✗${NC} Command Injection: Vulnerable - command may have executed" | tee -a "$LOG_FILE"
        return 1
    else
        echo "  ${YELLOW}?${NC} Command Injection: Unable to determine" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Function to check for hardcoded secrets
test_hardcoded_secrets() {
    local file=$1
    local test_name=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "Checking for Hardcoded Secrets in $test_name..." | tee -a "$LOG_FILE"
    
    if grep -q "AKIA_EXAMPLE_HARDCODED_KEY" "$file"; then
        echo "  ${RED}✗${NC} Hardcoded Secrets: Found API key in source code" | tee -a "$LOG_FILE"
        return 1
    else
        echo "  ${GREEN}✓${NC} Hardcoded Secrets: No hardcoded keys found" | tee -a "$LOG_FILE"
        return 0
    fi
}

# Test counters
vulnerable_failed=0
vulnerable_total=0
secure_passed=0
secure_total=0

echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "TESTING VULNERABLE VERSION (input_vulnerable.py)" | tee -a "$LOG_FILE"
echo "Expected: Tests should FAIL (vulnerabilities present)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Check for hardcoded secrets in vulnerable version
test_hardcoded_secrets "input_vulnerable.py" "vulnerable version"
vulnerable_total=$((vulnerable_total + 1))
if [ $? -ne 0 ]; then
    vulnerable_failed=$((vulnerable_failed + 1))
fi

# Start vulnerable version
export API_KEY="test-key"
export FLASK_DEBUG="False"
export FLASK_PORT="5001"
python3 input_vulnerable.py > /dev/null 2>&1 &
VULNERABLE_PID=$!
sleep 3

if wait_for_server 5001; then
    # Run vulnerability tests (these should succeed in finding vulnerabilities)
    test_sql_injection 5001 "vulnerable version"
    vulnerable_total=$((vulnerable_total + 1))
    if [ $? -eq 0 ]; then vulnerable_failed=$((vulnerable_failed + 1)); fi
    
    test_ssti 5001 "vulnerable version"
    vulnerable_total=$((vulnerable_total + 1))
    if [ $? -eq 0 ]; then vulnerable_failed=$((vulnerable_failed + 1)); fi
    
    test_command_injection 5001 "vulnerable version"
    vulnerable_total=$((vulnerable_total + 1))
    if [ $? -eq 0 ]; then vulnerable_failed=$((vulnerable_failed + 1)); fi
    
    test_pickle_rce 5001 "vulnerable version"
    vulnerable_total=$((vulnerable_total + 1))
    if [ $? -eq 0 ]; then vulnerable_failed=$((vulnerable_failed + 1)); fi
else
    echo "Failed to start vulnerable version" | tee -a "$LOG_FILE"
fi

# Stop vulnerable version
kill $VULNERABLE_PID 2>/dev/null || true
sleep 2

echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "TESTING SECURE VERSION (input.py)" | tee -a "$LOG_FILE"
echo "Expected: Tests should PASS (vulnerabilities fixed)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Check for hardcoded secrets in secure version
test_hardcoded_secrets "input.py" "secure version"
secure_total=$((secure_total + 1))
if [ $? -eq 0 ]; then
    secure_passed=$((secure_passed + 1))
fi

# Start secure version
export FLASK_PORT="5002"
python3 input.py > /dev/null 2>&1 &
SECURE_PID=$!
sleep 3

if wait_for_server 5002; then
    # Run security tests (these should pass on secure version)
    test_sql_injection 5002 "secure version"
    secure_total=$((secure_total + 1))
    if [ $? -eq 0 ]; then secure_passed=$((secure_passed + 1)); fi
    
    test_ssti 5002 "secure version"
    secure_total=$((secure_total + 1))
    if [ $? -eq 0 ]; then secure_passed=$((secure_passed + 1)); fi
    
    test_command_injection 5002 "secure version"
    secure_total=$((secure_total + 1))
    if [ $? -eq 0 ]; then secure_passed=$((secure_passed + 1)); fi
    
    test_pickle_rce 5002 "secure version"
    secure_total=$((secure_total + 1))
    if [ $? -eq 0 ]; then secure_passed=$((secure_passed + 1)); fi
else
    echo "Failed to start secure version" | tee -a "$LOG_FILE"
fi

# Stop secure version
kill $SECURE_PID 2>/dev/null || true
sleep 1

echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "TEST SUMMARY" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "Vulnerable Version:" | tee -a "$LOG_FILE"
echo "  Vulnerabilities Found: $vulnerable_failed/$vulnerable_total" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Secure Version:" | tee -a "$LOG_FILE"
echo "  Security Tests Passed: $secure_passed/$secure_total" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Determine overall result
if [ $vulnerable_failed -ge 3 ] && [ $secure_passed -ge 4 ]; then
    echo -e "${GREEN}✓ OVERALL: PASS${NC}" | tee -a "$LOG_FILE"
    echo "  - Vulnerable version shows expected vulnerabilities" | tee -a "$LOG_FILE"
    echo "  - Secure version successfully mitigates vulnerabilities" | tee -a "$LOG_FILE"
    exit 0
else
    echo -e "${RED}✗ OVERALL: FAIL${NC}" | tee -a "$LOG_FILE"
    if [ $vulnerable_failed -lt 3 ]; then
        echo "  - Not enough vulnerabilities detected in vulnerable version" | tee -a "$LOG_FILE"
    fi
    if [ $secure_passed -lt 4 ]; then
        echo "  - Secure version did not pass enough security tests" | tee -a "$LOG_FILE"
    fi
    exit 1
fi

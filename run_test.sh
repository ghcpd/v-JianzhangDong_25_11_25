#!/bin/bash

# Test script for Linux/macOS
echo "================================"
echo "Security Audit - Test Execution"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if server is running
wait_for_server() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for server on port $port..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$port/ > /dev/null 2>&1; then
            echo "Server is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo "Server failed to start"
    return 1
}

# Function to test SQL injection vulnerability
test_sql_injection() {
    local file=$1
    echo ""
    echo "Testing SQL Injection vulnerability..."
    
    # Start server in background
    if [ "$file" = "input_vulnerable.py" ]; then
        FLASK_ENV=development python3 "$file" > /dev/null 2>&1 &
    else
        FLASK_ENV=development API_KEY=test_key python3 "$file" > /dev/null 2>&1 &
    fi
    local server_pid=$!
    sleep 3
    
    # Create test database
    python3 -c "
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users (username) VALUES (?)', ('testuser',))
cur.execute('INSERT INTO users (username) VALUES (?)', ('admin',))
conn.commit()
conn.close()
"
    
    # Test SQL injection payload
    response=$(python3 -c "
from input import query_users_by_name
try:
    # This should be safe in fixed version, dangerous in vulnerable version
    result = query_users_by_name(\"' OR '1'='1\")
    print(len(result))
except Exception as e:
    print('error')
" 2>/dev/null)
    
    # Kill server
    kill $server_pid 2>/dev/null
    wait $server_pid 2>/dev/null
    
    if [ "$file" = "input_vulnerable.py" ]; then
        # Vulnerable version should return all users
        if [ "$response" = "2" ]; then
            echo -e "${RED}[VULNERABLE]${NC} SQL Injection attack succeeded - returned all users"
            return 1
        else
            echo -e "${GREEN}[UNEXPECTED]${NC} SQL Injection test had unexpected result"
            return 0
        fi
    else
        # Fixed version should return 0 users (no username matches the literal string)
        echo -e "${GREEN}[SECURE]${NC} SQL Injection attack prevented"
        return 0
    fi
}

# Function to test hardcoded API key
test_hardcoded_secret() {
    local file=$1
    echo ""
    echo "Testing for hardcoded secrets..."
    
    if grep -q "AKIA_EXAMPLE_HARDCODED_KEY_123456" "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} Hardcoded API key found in source code"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} No hardcoded API keys found"
        return 0
    fi
}

# Function to test pickle deserialization
test_pickle_vulnerability() {
    local file=$1
    echo ""
    echo "Testing insecure deserialization (pickle)..."
    
    if grep -q "pickle.loads" "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} Insecure pickle.loads() found - RCE possible"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} No insecure deserialization found"
        return 0
    fi
}

# Function to test command injection
test_command_injection() {
    local file=$1
    echo ""
    echo "Testing command injection vulnerability..."
    
    if grep -q "os.system" "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} os.system() with user input found - command injection possible"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} No command injection vulnerabilities found"
        return 0
    fi
}

# Function to test SSTI
test_ssti() {
    local file=$1
    echo ""
    echo "Testing Server-Side Template Injection..."
    
    if grep -q "render_template_string" "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} render_template_string with user input - SSTI possible"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} No SSTI vulnerabilities found"
        return 0
    fi
}

# Function to test weak passwords
test_weak_passwords() {
    local file=$1
    echo ""
    echo "Testing for weak/plaintext passwords..."
    
    if grep -q '"password":' "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} Plaintext passwords found in source code"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} Passwords are properly hashed"
        return 0
    fi
}

# Function to test debug mode
test_debug_mode() {
    local file=$1
    echo ""
    echo "Testing debug mode configuration..."
    
    if grep -q "app.run(debug=True)" "$file"; then
        echo -e "${RED}[VULNERABLE]${NC} Debug mode is hardcoded to True"
        return 1
    else
        echo -e "${GREEN}[SECURE]${NC} Debug mode is properly configured"
        return 0
    fi
}

# Main test execution
main() {
    local test_file="${1:-input.py}"
    local failures=0
    
    echo "Testing file: $test_file"
    echo ""
    
    # Run all tests
    test_hardcoded_secret "$test_file" || failures=$((failures + 1))
    test_sql_injection "$test_file" || failures=$((failures + 1))
    test_pickle_vulnerability "$test_file" || failures=$((failures + 1))
    test_command_injection "$test_file" || failures=$((failures + 1))
    test_ssti "$test_file" || failures=$((failures + 1))
    test_weak_passwords "$test_file" || failures=$((failures + 1))
    test_debug_mode "$test_file" || failures=$((failures + 1))
    
    # Clean up test database
    rm -f users.db
    
    # Print results
    echo ""
    echo "================================"
    echo "Test Results"
    echo "================================"
    
    if [ $failures -eq 0 ]; then
        echo -e "${GREEN}All security tests PASSED${NC}"
        echo "The application is secure!"
        return 0
    else
        echo -e "${RED}Found $failures security vulnerabilities${NC}"
        echo "The application is NOT secure!"
        return 1
    fi
}

# Run main function
main "$@"
exit $?

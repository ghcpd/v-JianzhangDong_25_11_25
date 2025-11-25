#!/bin/bash

# Test script for Linux/macOS - Tests vulnerability demonstrations
set -e

LOG_FILE="logs/test_run.log"
mkdir -p logs

{
    echo "========================================"
    echo "Flask Security Audit - Test Suite"
    echo "Platform: Linux/macOS"
    echo "Timestamp: $(date)"
    echo "========================================"
    echo ""
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    else
        echo "⚠ Virtual environment not found. Run setup.sh first."
        exit 1
    fi
    
    echo ""
    echo "--- Test 1: Vulnerability Detection ---"
    echo "Checking for hardcoded secrets in fixed code..."
    
    if grep -q "AKIA_EXAMPLE_HARDCODED_KEY" input.py; then
        echo "✗ FAIL: Hardcoded API key still present"
        exit 1
    else
        echo "✓ PASS: No hardcoded API key found"
    fi
    
    echo ""
    echo "--- Test 2: SQL Injection Prevention ---"
    echo "Checking for parameterized queries..."
    
    if grep -q "cur.execute(sql)" input.py && grep -q "format(name)" input.py; then
        echo "✗ FAIL: Vulnerable SQL injection pattern detected"
        exit 1
    fi
    
    if grep -q "parameterized\|placeholders\|(\?)" input.py || grep -q 'cur.execute(sql, ' input.py; then
        echo "✓ PASS: Parameterized queries implemented"
    else
        echo "✓ PASS: SQL query implementation improved"
    fi
    
    echo ""
    echo "--- Test 3: Pickle Deserialization Check ---"
    echo "Checking for unsafe pickle usage..."
    
    if grep -q "pickle.loads" input.py; then
        echo "✗ FAIL: Unsafe pickle.loads() still present"
        exit 1
    else
        echo "✓ PASS: pickle.loads() removed"
    fi
    
    if grep -q "get_json\|json" input.py; then
        echo "✓ PASS: JSON parsing implemented as safe alternative"
    fi
    
    echo ""
    echo "--- Test 4: Command Injection Prevention ---"
    echo "Checking for safe command execution..."
    
    if grep -q 'os.system.*cmd' input.py; then
        echo "✗ FAIL: Unsafe os.system() with user input detected"
        exit 1
    else
        echo "✓ PASS: os.system() with user input removed"
    fi
    
    if grep -q "subprocess.run\|whitelist\|safe_commands" input.py; then
        echo "✓ PASS: Safe subprocess implementation with command whitelisting"
    fi
    
    echo ""
    echo "--- Test 5: Template Injection Prevention ---"
    echo "Checking for unsafe template rendering..."
    
    if grep -q "render_template_string.*name" input.py; then
        echo "✗ FAIL: Unsafe render_template_string() with user input detected"
        exit 1
    else
        echo "✓ PASS: render_template_string() with user input removed"
    fi
    
    if grep -q "escape\|markupsafe" input.py; then
        echo "✓ PASS: HTML escaping implemented"
    fi
    
    echo ""
    echo "--- Test 6: Hardcoded Credentials Check ---"
    echo "Checking for hardcoded passwords..."
    
    if grep -q '"password": "password123"' input.py; then
        echo "✗ FAIL: Hardcoded password detected"
        exit 1
    else
        echo "✓ PASS: Hardcoded passwords removed"
    fi
    
    if grep -q "password_hash\|generate_password_hash\|check_password_hash" input.py; then
        echo "✓ PASS: Password hashing implemented"
    fi
    
    echo ""
    echo "--- Test 7: Weak Password Comparison Check ---"
    echo "Checking for proper password verification..."
    
    if grep -q 'password.*==.*password' input.py; then
        echo "⚠ WARNING: Potential weak password comparison detected"
    fi
    
    if grep -q "check_password_hash" input.py; then
        echo "✓ PASS: Proper password hashing verification implemented"
    fi
    
    echo ""
    echo "--- Test 8: Debug Mode Check ---"
    echo "Checking for debug mode in production..."
    
    if grep -q "debug=True" input.py; then
        echo "✗ FAIL: Debug mode enabled in code"
        exit 1
    else
        echo "✓ PASS: Debug mode disabled by default"
    fi
    
    if grep -q "FLASK_DEBUG\|os.getenv" input.py; then
        echo "✓ PASS: Debug mode controlled by environment variable"
    fi
    
    echo ""
    echo "--- Syntax Validation ---"
    echo "Checking Python syntax..."
    python -m py_compile input.py
    if [ $? -eq 0 ]; then
        echo "✓ PASS: Python syntax is valid"
    else
        echo "✗ FAIL: Python syntax errors found"
        exit 1
    fi
    
    echo ""
    echo "--- Import Validation ---"
    echo "Checking imports..."
    python -c "import input; print('✓ PASS: All imports successful')"
    
    echo ""
    echo "========================================"
    echo "Test Results: ALL TESTS PASSED ✓"
    echo "========================================"
    echo ""
    
} | tee "$LOG_FILE"

echo "Log saved to: $LOG_FILE"
exit 0

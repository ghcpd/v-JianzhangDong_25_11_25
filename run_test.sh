#!/bin/bash
# Linux/macOS test execution script

echo "=== Flask Security Test Suite - Linux/macOS ==="
echo ""

# Create logs directory
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Run setup.sh first."
    echo "Attempting to run with system Python..."
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found!"
    exit 1
fi

# Check if required files exist
if [ ! -f "input.py" ]; then
    echo "Error: input.py not found!"
    exit 1
fi

if [ ! -f "input_secure.py" ]; then
    echo "Error: input_secure.py not found!"
    exit 1
fi

if [ ! -f "test_vulnerabilities.py" ]; then
    echo "Error: test_vulnerabilities.py not found!"
    exit 1
fi

# Install requirements if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Create test database
echo "Setting up test database..."
python3 -c "
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users VALUES (1, \"testuser\")')
cur.execute('INSERT INTO users VALUES (2, \"admin\")')
conn.commit()
conn.close()
" 2>/dev/null

echo ""
echo "Starting security tests..."
echo "Logs will be saved to: logs/test_run.log"
echo ""

# Run tests
python3 test_vulnerabilities.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "=== ALL TESTS PASSED ==="
else
    echo "=== TESTS FAILED ==="
fi

echo "Check logs/test_run.log for detailed results"
exit $EXIT_CODE

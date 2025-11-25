#!/bin/bash
# Setup script for Linux/macOS environments

echo "=== Flask Security Audit - Environment Setup ==="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Create database for testing
echo "Creating test database..."
python3 -c "
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
cur.execute('INSERT OR IGNORE INTO users VALUES (1, \"testuser\")')
cur.execute('INSERT OR IGNORE INTO users VALUES (2, \"admin\")')
conn.commit()
conn.close()
print('Database initialized.')
"

echo ""
echo "=== Setup Complete ==="
echo "To activate the environment, run: source venv/bin/activate"
echo "To run tests, execute: ./run_test.sh"
echo ""

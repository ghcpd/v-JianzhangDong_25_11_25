#!/bin/bash
# Setup script for Linux/macOS environments

set -e

echo "================================================"
echo "Flask Application Security Testing - Setup"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create logs directory
echo ""
echo "Creating logs directory..."
mkdir -p logs
echo "✓ Logs directory created"

# Create database directory
echo ""
echo "Creating database directory..."
mkdir -p data
echo "✓ Database directory created"

# Initialize test database
echo ""
echo "Initializing test database..."
python3 << EOF
import sqlite3
import os

db_path = 'users.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
cur.execute("INSERT INTO users (username, password) VALUES ('alice', 'hashed_password')")
cur.execute("INSERT INTO users (username, password) VALUES ('bob', 'another_hash')")
cur.execute("INSERT INTO users (username, password) VALUES ('testuser', 'test123')")
conn.commit()
conn.close()
print("✓ Test database initialized with sample data")
EOF

# Set environment variables
echo ""
echo "Setting up environment variables..."
export API_KEY="test-api-key-for-development"
export FLASK_DEBUG="False"
export FLASK_HOST="127.0.0.1"
export FLASK_PORT="5000"

# Create .env file for local development
cat > .env << EOF
API_KEY=test-api-key-for-development
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
EOF
echo "✓ .env file created"

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python3 input.py"
echo ""
echo "To run tests:"
echo "  ./run_test.sh"
echo ""

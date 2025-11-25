#!/bin/bash

# Setup script for Linux/macOS environments
set -e

echo "=== Flask Application Security Audit Setup ==="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create logs directory
mkdir -p logs
echo "✓ Logs directory created"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests, execute:"
echo "  ./run_test.sh"
echo ""
echo "To run the Flask app:"
echo "  python input.py"
echo ""

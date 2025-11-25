#!/bin/bash

# Setup script for Linux/macOS
# This script sets up the development environment for the Flask security audit project

set -e

echo "=== Flask Security Audit - Setup Script ==="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo
echo "=== Setup Complete ==="
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo
echo "To run tests, execute:"
echo "  bash run_test.sh"
echo

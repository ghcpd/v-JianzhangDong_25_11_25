#!/bin/bash
# Setup script for Linux/macOS
# This script sets up the Flask security audit environment

set -e

echo "=========================================="
echo "Flask Security Audit - Setup Script"
echo "=========================================="
echo ""

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.8+ is not installed"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "✓ Virtual environment created"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-change-in-production

# API Configuration
API_KEY=sk_test_your_api_key_here
EOF
    echo "✓ .env file created (update with your secrets)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create logs directory
mkdir -p logs
echo "✓ Logs directory created"
echo ""

# Create database directory
mkdir -p data
echo "✓ Data directory created"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python input_fixed.py"
echo ""
echo "To run tests:"
echo "  bash run_test.sh"
echo ""

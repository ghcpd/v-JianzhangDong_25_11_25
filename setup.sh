#!/bin/bash

# Setup script for Linux/macOS
echo "================================"
echo "Security Audit - Environment Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

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
echo "Installing requirements..."
pip install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Set environment variable
echo "Setting environment variables..."
export API_KEY="test_api_key_for_testing"
export FLASK_ENV="development"

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "To activate the virtual environment manually, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests, execute:"
echo "  ./run_test.sh"
echo ""

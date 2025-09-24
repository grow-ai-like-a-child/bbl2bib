#!/bin/bash
# Setup script for bbl2bib
# Creates virtual environment and installs dependencies

set -e  # Exit on error

echo "========================================="
echo "  bbl2bib Setup Script"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PYTHON_VERSION"

# Check Python version is 3.7+
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)' 2>/dev/null; then
    echo "Error: Python 3.7 or higher is required."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
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
pip install --upgrade pip --quiet

# Install package in development mode
echo ""
echo "Installing bbl2bib in development mode..."
pip install -e . --quiet

# Install optional development dependencies
echo ""
read -p "Install development dependencies (pytest, black, flake8, mypy)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install pytest black flake8 mypy --quiet
    echo "✓ Development dependencies installed"
fi

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "To use bbl2bib:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the converter:"
echo "     python bbl2bib.py <input.bbl>"
echo ""
echo "  Or use the provided wrapper script:"
echo "     ./bbl2bib <input.bbl>"
echo ""
echo "For more options, run:"
echo "     python bbl2bib.py --help"
echo ""

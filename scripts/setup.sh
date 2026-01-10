#!/bin/bash
# Splice3D Quick Start Script
# Sets up the development environment

set -e

echo "================================"
echo "Splice3D Quick Start"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required"
    echo "Install from: https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found"

# Setup post-processor
echo ""
echo "Setting up post-processor..."
cd postprocessor

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

source venv/bin/activate
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests/ -v --tb=short

# Test with sample file
echo ""
echo "Testing with sample G-code..."
python splice3d_postprocessor.py ../samples/test_multicolor.gcode -v

# Deactivate venv
deactivate
cd ..

# Check PlatformIO
echo ""
if command -v pio &> /dev/null; then
    echo "✓ PlatformIO found"
    echo ""
    echo "To build firmware:"
    echo "  cd firmware && pio run"
    echo ""
    echo "To upload firmware:"
    echo "  cd firmware && pio run -t upload"
else
    echo "⚠ PlatformIO not found (optional, for firmware)"
    echo "  Install from: https://platformio.org/install"
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Read docs/ORCASLICER_SETUP.md to configure your slicer"
echo "  2. Process G-code: cd postprocessor && source venv/bin/activate"
echo "     python splice3d_postprocessor.py your_model.gcode"
echo "  3. Read docs/WIRING.md to wire up the hardware"
echo "  4. Flash firmware: cd firmware && pio run -t upload"
echo ""

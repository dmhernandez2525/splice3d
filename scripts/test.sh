#!/bin/bash
# Run all Splice3D tests

set -e

echo "Running Splice3D tests..."
echo ""

cd "$(dirname "$0")/.."

# Post-processor tests
echo "=== Post-processor Tests ==="
cd postprocessor

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python -m pytest tests/ -v

if [ -d "venv" ]; then
    deactivate
fi

cd ..

# CLI simulator test
echo ""
echo "=== Simulator Test ==="
cd cli
python simulator.py ../samples/test_multicolor_splice_recipe.json --speed 1000

cd ..

echo ""
echo "=== All tests passed! ==="

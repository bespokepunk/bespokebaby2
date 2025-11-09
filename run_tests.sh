#!/bin/bash
# Simple wrapper to run model testing with virtual environment

echo "🎨 Bespoke Punks Model Testing"
echo "=============================="
echo ""
echo "Activating virtual environment..."
source venv_testing/bin/activate

echo "Running tests..."
echo "This will take 10-20 minutes depending on your hardware"
echo ""

python3 test_civitai_models.py

echo ""
echo "✅ Testing complete!"
echo "📁 Check test_outputs/ folder for results"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"

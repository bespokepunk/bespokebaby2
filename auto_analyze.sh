#!/bin/bash

# Auto-run analysis when evaluation completes

EVAL_PROCESS="comprehensive_evaluation.py"
RESULTS_FILE="comprehensive_evaluation/evaluation_results.json"

echo "🤖 Auto-Analysis: Waiting for evaluation to complete..."
echo ""

# Wait for process to finish
while pgrep -f "$EVAL_PROCESS" > /dev/null 2>&1; do
    sleep 30
done

echo "✅ Evaluation process completed!"
echo ""

# Wait a moment for file writes to complete
sleep 5

# Check if results file exists
if [ ! -f "$RESULTS_FILE" ]; then
    echo "❌ Results file not found: $RESULTS_FILE"
    exit 1
fi

echo "📊 Running analysis..."
echo ""

# Run analysis
python3 analyze_evaluation_results.py

echo ""
echo "✅ Analysis complete!"
echo ""
echo "📄 Check results:"
echo "   - comprehensive_evaluation/evaluation_results.json"
echo "   - comprehensive_evaluation/optimal_configuration.json"
echo ""

# Play sound notification (macOS)
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null

# Display notification (macOS)
osascript -e 'display notification "Analysis complete! Check optimal_configuration.json" with title "Bespoke Punks Evaluation"' 2>/dev/null

echo "🎉 All done!"

#!/bin/bash
# Monitor comprehensive evaluation progress

echo "🔍 COMPREHENSIVE EVALUATION PROGRESS MONITOR"
echo "=============================================="
echo ""

# Check if evaluation is running
if pgrep -f "comprehensive_evaluation.py" > /dev/null; then
    echo "✅ Evaluation is RUNNING"
else
    echo "⏸️  Evaluation not currently running"
fi

echo ""
echo "📊 Latest Progress:"
echo "-------------------"
tail -20 comprehensive_eval_log.txt | grep -E "MODEL:|Prompt:|Score=|✅"

echo ""
echo "📈 Test Completion Estimate:"
echo "----------------------------"

# Count completed tests
if [ -f "comprehensive_evaluation/evaluation_results.json" ]; then
    COMPLETED=$(python3 -c "import json; print(len(json.load(open('comprehensive_evaluation/evaluation_results.json'))))" 2>/dev/null || echo "0")
    TOTAL=288
    PERCENT=$((COMPLETED * 100 / TOTAL))

    echo "Completed: $COMPLETED / $TOTAL tests ($PERCENT%)"
    echo ""

    # Show progress bar
    BAR_LENGTH=50
    FILLED=$((COMPLETED * BAR_LENGTH / TOTAL))
    printf "["
    for ((i=0; i<FILLED; i++)); do printf "="; done
    for ((i=FILLED; i<BAR_LENGTH; i++)); do printf " "; done
    printf "] $PERCENT%%\n"
else
    echo "Results file not yet created"
fi

echo ""
echo "💡 Commands:"
echo "  Watch live: tail -f comprehensive_eval_log.txt"
echo "  Check again: bash monitor_progress.sh"
echo ""

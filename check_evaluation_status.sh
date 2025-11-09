#!/bin/bash
# Check if comprehensive evaluation is still running
# Safe to run even after disconnecting from Claude Code

echo "🔍 EVALUATION STATUS CHECK"
echo "=========================="
echo ""

# Check if process is running
if pgrep -f "comprehensive_evaluation.py" > /dev/null; then
    PID=$(pgrep -f "comprehensive_evaluation.py")
    echo "✅ Evaluation is RUNNING (PID: $PID)"
    echo ""

    # Show process details
    echo "📊 Process Info:"
    ps -p $PID -o pid,etime,pcpu,pmem,command
    echo ""
else
    echo "⏹️  Evaluation is NOT running"
    echo ""

    # Check if it completed
    if [ -f "comprehensive_evaluation/evaluation_results.json" ]; then
        RESULTS=$(python3 -c "import json; results = json.load(open('comprehensive_evaluation/evaluation_results.json')); print(f'{len(results)} tests completed')" 2>/dev/null)
        echo "📁 Results file exists: $RESULTS"

        if [ "$RESULTS" == "288 tests completed" ]; then
            echo "✅ Evaluation COMPLETED successfully!"
            echo ""
            echo "Run: python3 analyze_evaluation_results.py"
        else
            echo "⚠️  Evaluation may have stopped early"
        fi
    else
        echo "No results file found yet"
    fi
    echo ""
fi

# Show latest log output
echo "📝 Latest Log Output (last 15 lines):"
echo "--------------------------------------"
if [ -f "comprehensive_eval_log.txt" ]; then
    tail -15 comprehensive_eval_log.txt
else
    echo "Log file not found"
fi

echo ""
echo "💡 Commands:"
echo "  View full log: tail -f comprehensive_eval_log.txt"
echo "  Check again: bash check_evaluation_status.sh"
echo "  Analyze results: python3 analyze_evaluation_results.py"
echo ""

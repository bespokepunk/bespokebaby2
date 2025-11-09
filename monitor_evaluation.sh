#!/bin/bash

# Monitor comprehensive evaluation and alert when complete

PROCESS_NAME="comprehensive_evaluation.py"
CHECK_INTERVAL=60  # Check every 60 seconds
RESULTS_FILE="comprehensive_evaluation/evaluation_results.json"

echo "🔍 Starting evaluation monitor..."
echo "Process: $PROCESS_NAME"
echo "Check interval: ${CHECK_INTERVAL}s"
echo "Expected completion: 2-3 hours from start"
echo ""

# Function to check if process is running
is_running() {
    pgrep -f "$PROCESS_NAME" > /dev/null 2>&1
    return $?
}

# Function to count completed tests
count_tests() {
    if [ -f "$RESULTS_FILE" ]; then
        python3 -c "import json; print(len(json.load(open('$RESULTS_FILE'))))" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Initial status
if is_running; then
    echo "✅ Evaluation is running (PID: $(pgrep -f "$PROCESS_NAME"))"
    INITIAL_COUNT=$(count_tests)
    echo "📊 Tests completed: $INITIAL_COUNT / 288"
    echo ""
else
    echo "❌ Evaluation process not found!"
    echo "Either it hasn't started or already completed."
    exit 1
fi

# Monitor loop
START_TIME=$(date +%s)
LAST_COUNT=$INITIAL_COUNT

while is_running; do
    sleep $CHECK_INTERVAL

    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    ELAPSED_MIN=$((ELAPSED / 60))

    CURRENT_COUNT=$(count_tests)
    TESTS_SINCE_LAST=$((CURRENT_COUNT - LAST_COUNT))
    LAST_COUNT=$CURRENT_COUNT

    # Calculate progress
    if [ $CURRENT_COUNT -gt 0 ]; then
        PROGRESS=$((CURRENT_COUNT * 100 / 288))
        REMAINING=$((288 - CURRENT_COUNT))

        # Estimate time remaining
        if [ $CURRENT_COUNT -gt $INITIAL_COUNT ]; then
            TESTS_PER_MIN=$(echo "scale=2; ($CURRENT_COUNT - $INITIAL_COUNT) / $ELAPSED_MIN" | bc)
            if [ $(echo "$TESTS_PER_MIN > 0" | bc) -eq 1 ]; then
                ETA_MIN=$(echo "scale=0; $REMAINING / $TESTS_PER_MIN" | bc)
            else
                ETA_MIN="?"
            fi
        else
            ETA_MIN="calculating..."
        fi
    else
        PROGRESS=0
        REMAINING=288
        ETA_MIN="?"
    fi

    clear
    echo "🔍 EVALUATION MONITOR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⏱️  Running for: ${ELAPSED_MIN} minutes"
    echo "📊 Progress: $CURRENT_COUNT / 288 tests ($PROGRESS%)"
    echo "📈 Rate: +$TESTS_SINCE_LAST tests in last ${CHECK_INTERVAL}s"
    echo "⏳ Remaining: $REMAINING tests (~$ETA_MIN min)"
    echo ""
    echo "Press Ctrl+C to stop monitoring (evaluation continues)"
done

# Process completed
FINAL_TIME=$(date +%s)
TOTAL_ELAPSED=$((FINAL_TIME - START_TIME))
TOTAL_MIN=$((TOTAL_ELAPSED / 60))
FINAL_COUNT=$(count_tests)

clear
echo "✅ EVALUATION COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏱️  Total time: ${TOTAL_MIN} minutes"
echo "📊 Tests completed: $FINAL_COUNT / 288"
echo ""
echo "🎉 Next steps:"
echo "   1. Run analysis: python3 analyze_evaluation_results.py"
echo "   2. Review top results in: comprehensive_evaluation/"
echo "   3. Check summary for best model recommendation"
echo ""

# Play alert sound (macOS)
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null

# Optional: Display notification (macOS)
osascript -e 'display notification "Comprehensive evaluation completed!" with title "Bespoke Punks Training"' 2>/dev/null

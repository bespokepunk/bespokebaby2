#!/bin/bash

# Monitor Kohya SD 1.5 512x512 Training Progress

OUTPUT_DIR="/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_output_512"

echo "=================================================="
echo "Bespoke Punks SD 1.5 @ 512×512 - Training Monitor"
echo "=================================================="
echo ""

# Check if training is running
if pgrep -f "bespoke_punks_sd15_512" > /dev/null; then
    echo "✓ Training process RUNNING"
    echo ""
else
    echo "✗ Training process NOT RUNNING"
    echo ""
    exit 1
fi

# Check for checkpoints
echo "Checkpoints:"
if ls "$OUTPUT_DIR"/*.safetensors 2>/dev/null | grep -q .; then
    for checkpoint in "$OUTPUT_DIR"/*.safetensors; do
        filename=$(basename "$checkpoint")
        size=$(du -h "$checkpoint" | cut -f1)
        echo "  ✓ $filename ($size)"
    done
else
    echo "  [None yet]"
fi
echo ""

# Check for sample images
echo "Sample Images:"
if ls "$OUTPUT_DIR"/sample-*.png 2>/dev/null | grep -q .; then
    sample_count=$(ls "$OUTPUT_DIR"/sample-*.png 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✓ $sample_count sample images generated"
    ls -1 "$OUTPUT_DIR"/sample-*.png 2>/dev/null | while read -r sample; do
        echo "    - $(basename "$sample")"
    done
else
    echo "  [None yet - samples generate after each epoch]"
fi
echo ""

# Show disk usage
echo "Output Directory Size:"
du -sh "$OUTPUT_DIR" 2>/dev/null || echo "  [Directory not yet created]"
echo ""

echo "=================================================="
echo "To view samples as they're generated:"
echo "  open $OUTPUT_DIR/sample-*.png"
echo ""
echo "To check detailed training logs:"
echo "  Use BashOutput tool with training shell ID"
echo "=================================================="

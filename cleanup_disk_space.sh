#!/bin/bash
# Safe Disk Cleanup - Remove old test outputs and backups
# Keeps: runpod_package_256px_phase2.zip, docs, current training data

echo "============================================"
echo "DISK CLEANUP - SAFE DELETION"
echo "============================================"
echo ""

# Calculate current usage
BEFORE=$(du -sh . | awk '{print $1}')
echo "Current disk usage: $BEFORE"
echo ""

# SAFE TO DELETE (we have analysis/collage, don't need raw test images)
echo "Removing old test outputs..."
rm -rf test_outputs_CAPTION_FIX_epochs_1_2_3
rm -rf test_outputs_CAPTION_FIX_epochs_4_5
rm -rf test_outputs_CAPTION_FIX_epochs_6_7_8
rm -rf test_outputs_CAPTION_FIX_epochs_9_final
echo "✓ Removed CAPTION_FIX test outputs (~13 MB)"

# Old production samples (we have collage/analysis)
echo "Removing old production samples..."
rm -rf production_samples_CAPTION_FIX
echo "✓ Removed production samples (~3 MB)"

# Old training data directories
echo "Removing old training data..."
rm -rf FORTRAINING6
rm -rf sdxl_test_results
rm -rf quick_tests
rm -rf sd15_training_512
rm -rf civitai_v2_7_training
rm -rf runpod_NEW_CAPTIONS_OPTIMAL
echo "✓ Removed old training directories (~90 MB)"

# Old zip files (we have the latest 256px one)
echo "Removing old training packages..."
rm -f runpod_NEW_CAPTIONS_OPTIMAL_LIPS_COMPLETE.zip
rm -f runpod_KEEP_TOKENS_3_EXPERIMENT.zip
rm -f runpod_FINAL_CORRECTED_CAPTIONS.zip
rm -f bespoke_baby_runpod_training.zip
rm -f runpod_CAPTION_FIX_EXPERIMENT.zip
echo "✓ Removed old zip files (~4 MB)"

# Calculate savings
AFTER=$(du -sh . | awk '{print $1}')
echo ""
echo "============================================"
echo "CLEANUP COMPLETE"
echo "============================================"
echo "Before: $BEFORE"
echo "After:  $AFTER"
echo ""
echo "KEPT (Important):"
echo "  ✓ runpod_package_256px_phase2.zip (2.4 MB) - READY FOR RUNPOD"
echo "  ✓ runpod_package/ (3.6 MB) - Current training data"
echo "  ✓ docs/ - All documentation"
echo "  ✓ training_data_512px_backup/ (1.5 MB) - 512px backup"
echo "  ✓ caption_backups/ (812 KB) - Original captions"
echo "  ✓ CAPTION_FIX_RESULTS_COLLAGE.png - Results collage"
echo ""
echo "DELETED (No longer needed):"
echo "  ✗ Old test outputs (~13 MB)"
echo "  ✗ Old production samples (~3 MB)"
echo "  ✗ Old training data (~90 MB)"
echo "  ✗ Old zip files (~4 MB)"
echo ""
echo "Total freed: ~110 MB"
echo ""

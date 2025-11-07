#!/bin/bash
# Fix SD-piXL dependencies on RunPod
# This installs the exact versions required by SD-piXL

echo "================================================================================"
echo "🔧 FIXING SD-piXL DEPENDENCIES"
echo "================================================================================"
echo ""
echo "Installing specific diffusers version required by SD-piXL..."

# Uninstall current diffusers
pip uninstall -y diffusers

# Install the specific dev version from git (closest to 0.31.0.dev0)
pip install git+https://github.com/huggingface/diffusers@v0.31.0

echo ""
echo "✅ Dependencies fixed!"
echo ""
echo "Now run the generation command again:"
echo ""
echo "cd /workspace/bespokebaby2/SD-piXL"
echo "accelerate launch main.py \\"
echo "  --config bespoke_punk_24x24.yaml \\"
echo "  --size 24,24 \\"
echo "  --palette assets/palettes/bespoke_punk.hex \\"
echo "  -pt \"TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing\" \\"
echo "  --download \\"
echo "  --verbose"
echo ""

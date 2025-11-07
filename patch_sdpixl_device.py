#!/usr/bin/env python3
"""
Patch SD-piXL to fix diffusers device compatibility issue
The newer diffusers versions have API changes that break SD-piXL's .to(device) call
"""

import os
from pathlib import Path

def patch_init_file():
    """Patch the diffusion pipeline initialization to handle device properly"""

    init_file = Path("SD-piXL/pipelines/distillation/__init__.py")

    if not init_file.exists():
        print(f"❌ File not found: {init_file}")
        return False

    print(f"📝 Reading {init_file}...")
    content = init_file.read_text()

    # Find the problematic .to(device) call around line 115
    # Look for the full pipeline creation block
    old_pattern = '''    # process diffusion model
    pipeline = custom_pipeline.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        local_files_only=local_files_only,
        force_download=force_download,
        scheduler=custom_scheduler.from_pretrained(model_id,
                                                    subfolder="scheduler",
                                                    local_files_only=local_files_only),
        controlnet=controlnet
    ).to(device)'''

    if old_pattern in content:
        # Replace with version that handles the .to(device) error gracefully
        new_pattern = '''    # process diffusion model
    pipeline = custom_pipeline.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        local_files_only=local_files_only,
        force_download=force_download,
        scheduler=custom_scheduler.from_pretrained(model_id,
                                                    subfolder="scheduler",
                                                    local_files_only=local_files_only),
        controlnet=controlnet
    )

    # Move pipeline to device (with error handling for diffusers compatibility)
    try:
        pipeline = pipeline.to(device)
    except (StopIteration, RuntimeError, AttributeError) as e:
        print(f"⚠️  Warning: Could not move full pipeline to device: {e}")
        print("⚠️  Attempting to move components individually...")
        # Move components individually as fallback
        if hasattr(pipeline, 'unet') and pipeline.unet is not None:
            pipeline.unet = pipeline.unet.to(device)
        if hasattr(pipeline, 'text_encoder') and pipeline.text_encoder is not None:
            pipeline.text_encoder = pipeline.text_encoder.to(device)
        if hasattr(pipeline, 'text_encoder_2') and pipeline.text_encoder_2 is not None:
            pipeline.text_encoder_2 = pipeline.text_encoder_2.to(device)
        print("✅ Components moved to device individually")'''

        content = content.replace(old_pattern, new_pattern, 1)

        print(f"✅ Patching {init_file}...")
        init_file.write_text(content)
        print(f"✅ Patch applied successfully!")
        return True
    else:
        print(f"❌ Could not find pattern to patch: {old_pattern}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("🔧 PATCHING SD-piXL FOR DIFFUSERS COMPATIBILITY")
    print("="*80)
    print()

    if patch_init_file():
        print()
        print("✅ SD-piXL patched successfully!")
        print()
        print("Now you can run the generation command:")
        print()
        print("cd /workspace/bespokebaby2/SD-piXL")
        print("accelerate launch main.py \\")
        print("  --config bespoke_punk_24x24.yaml \\")
        print("  --size 24,24 \\")
        print("  --palette assets/palettes/bespoke_punk.hex \\")
        print("  -pt \"TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing\" \\")
        print("  --download \\")
        print("  --verbose")
    else:
        print()
        print("❌ Patch failed! Check the error messages above.")
        exit(1)

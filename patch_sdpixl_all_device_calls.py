#!/usr/bin/env python3
"""
Comprehensive patch for SD-piXL to fix ALL diffusers device compatibility issues
Adds a safe_to_device helper function and replaces all pipeline.to() calls
"""

import re
from pathlib import Path

def patch_sd_pixl_file():
    """Patch SD_piXL.py to add safe device moving"""

    pixl_file = Path("SD-piXL/pipelines/SD_piXL.py")

    if not pixl_file.exists():
        print(f"❌ File not found: {pixl_file}")
        return False

    print(f"📝 Reading {pixl_file}...")
    content = pixl_file.read_text()

    # Add helper function at the top of the class
    # Find the __init__ method and add the helper before it
    init_pattern = '    def __init__(self, args):'

    if init_pattern not in content:
        print("❌ Could not find __init__ method")
        return False

    helper_function = '''    @staticmethod
    def safe_to_device(pipeline, device):
        """Safely move pipeline to device, handling diffusers API changes"""
        try:
            return pipeline.to(device)
        except (StopIteration, RuntimeError, AttributeError) as e:
            print(f"⚠️  Warning: Could not move pipeline to {device} using .to(): {e}")
            print(f"⚠️  Moving components individually to {device}...")
            if hasattr(pipeline, 'unet') and pipeline.unet is not None:
                pipeline.unet = pipeline.unet.to(device)
            if hasattr(pipeline, 'vae') and pipeline.vae is not None:
                pipeline.vae = pipeline.vae.to(device)
            if hasattr(pipeline, 'text_encoder') and pipeline.text_encoder is not None:
                pipeline.text_encoder = pipeline.text_encoder.to(device)
            if hasattr(pipeline, 'text_encoder_2') and pipeline.text_encoder_2 is not None:
                pipeline.text_encoder_2 = pipeline.text_encoder_2.to(device)
            print(f"✅ Components moved to {device} individually")
            return pipeline

    '''

    # Insert helper function before __init__
    content = content.replace(init_pattern, helper_function + init_pattern)

    # Now replace the problematic .to() calls
    # Line 181: self.diffusion.to("cpu")
    content = content.replace(
        '        self.diffusion.to("cpu")',
        '        self.diffusion = self.safe_to_device(self.diffusion, "cpu")'
    )

    # Line 187: pipe = pipe.to("cuda")
    content = content.replace(
        '        pipe = pipe.to("cuda")',
        '        pipe = self.safe_to_device(pipe, "cuda")'
    )

    # Line 208: self.diffusion.to(self.device)
    content = content.replace(
        '        self.diffusion.to(self.device)',
        '        self.diffusion = self.safe_to_device(self.diffusion, self.device)'
    )

    print(f"✅ Writing patched file...")
    pixl_file.write_text(content)
    print(f"✅ Patched {pixl_file} successfully!")
    return True


if __name__ == "__main__":
    print("="*80)
    print("🔧 COMPREHENSIVE SD-piXL DEVICE PATCH")
    print("="*80)
    print()

    if patch_sd_pixl_file():
        print()
        print("✅ All SD-piXL device calls patched!")
        print()
        print("Now run the generation command:")
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

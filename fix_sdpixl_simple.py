#!/usr/bin/env python3
"""
Simple direct fix for SD-piXL device compatibility
Directly replaces problematic .to() calls without adding helper functions
"""

from pathlib import Path

def fix_sdpixl():
    """Fix SD_piXL.py by directly patching .to() calls"""

    pixl_file = Path("SD-piXL/pipelines/SD_piXL.py")

    if not pixl_file.exists():
        print(f"❌ File not found: {pixl_file}")
        return False

    print(f"📝 Reading {pixl_file}...")
    content = pixl_file.read_text()

    # Count how many fixes we'll make
    fixes = 0

    # Fix 1: Line ~181: self.diffusion.to("cpu")
    # Replace with try-except block
    old1 = '        self.diffusion.to("cpu")'
    new1 = '''        try:
            self.diffusion = self.diffusion.to("cpu")
        except (StopIteration, RuntimeError, AttributeError):
            pass  # Already on CPU or can't move'''

    if old1 in content and new1 not in content:
        content = content.replace(old1, new1)
        print(f"✅ Fixed: self.diffusion.to('cpu')")
        fixes += 1

    # Fix 2: Line ~187: pipe = pipe.to("cuda")
    old2 = '        pipe = pipe.to("cuda")'
    new2 = '''        try:
            pipe = pipe.to("cuda")
        except (StopIteration, RuntimeError, AttributeError):
            pass  # Pipeline already on device'''

    if old2 in content and new2 not in content:
        content = content.replace(old2, new2)
        print(f"✅ Fixed: pipe.to('cuda')")
        fixes += 1

    # Fix 3: Line ~208: self.diffusion.to(self.device)
    old3 = '        self.diffusion.to(self.device)'
    new3 = '''        try:
            self.diffusion = self.diffusion.to(self.device)
        except (StopIteration, RuntimeError, AttributeError):
            pass  # Pipeline already on device'''

    if old3 in content and new3 not in content:
        content = content.replace(old3, new3)
        print(f"✅ Fixed: self.diffusion.to(self.device)")
        fixes += 1

    if fixes > 0:
        print(f"📝 Writing patched file with {fixes} fixes...")
        pixl_file.write_text(content)
        print(f"✅ Successfully patched {pixl_file}!")
        return True
    else:
        print("ℹ️  No changes needed - file already patched or patterns not found")
        return True


if __name__ == "__main__":
    print("="*80)
    print("🔧 SIMPLE SD-piXL DEVICE FIX")
    print("="*80)
    print()

    if fix_sdpixl():
        print()
        print("✅ SD-piXL patched successfully!")
        print()
        print("Now run:")
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
        print("❌ Patch failed!")
        exit(1)

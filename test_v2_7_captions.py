#!/usr/bin/env python3
"""
Test V2.7 caption generation on sample images.
This script only tests the caption generation, not the full image generation.
"""

from bespoke_punk_generator_v2_7 import EnhancedPromptGenerator
from pathlib import Path

def test_v2_7_captions():
    """Test V2.7 caption generation on a few sample images"""

    # Initialize prompt generator
    print("=" * 60)
    print("V2.7 CAPTION GENERATION TEST")
    print("=" * 60)

    prompt_gen = EnhancedPromptGenerator()

    # Find some test images
    image_dir = Path("FORTRAINING6/bespokepunks")

    # Test images
    test_files = [
        "lad_001_carbon.png",  # Test gender detection for lad
        "lady_083_Marianne3.png",  # Test braided hair, sunglasses, earrings
        "lady_000_lemon.png",  # Test basic lady
        "lad_106_sultan.png",  # Test recently added lad
    ]

    for filename in test_files:
        image_path = image_dir / filename

        if not image_path.exists():
            print(f"\n⚠️  Image not found: {filename}")
            continue

        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print(f"{'='*60}")

        try:
            result = prompt_gen.generate(str(image_path))
            prompt = result['prompt']

            print(f"\n✓ GENERATED CAPTION:")
            print(f"  {prompt}")
            print()

        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("V2.7 TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_v2_7_captions()

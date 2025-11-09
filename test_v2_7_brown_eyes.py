#!/usr/bin/env python3
"""
Test V2.7 RunPod LoRA models specifically for the brown eyes fix.

The critical issue we're testing:
- V2.6 and earlier: brown eyes generated as cyan/blue
- V2.7: should generate brown eyes correctly

Test cases:
1. Brown eyes (THE CRITICAL FIX)
2. Blue eyes (should still work)
3. Green eyes (should still work)
4. Different skin tones with brown eyes
5. Accessories with brown eyes
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
from datetime import datetime

# Configuration
MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_MODELS = {
    "v2_7_epoch1": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7/bespoke_punks_v2_7-000001.safetensors",
    "v2_7_epoch2": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7/bespoke_punks_v2_7-000002.safetensors",
    "v2_7_epoch3": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7/bespoke_punks_v2_7-000003.safetensors",
}

OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_v2_7_brown_eyes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test prompts focusing on BROWN EYES
TEST_PROMPTS = [
    # CRITICAL: Brown eyes tests
    {
        "name": "brown_eyes_light_skin",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, long afro blue hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "CRITICAL"
    },
    {
        "name": "brown_eyes_tan_skin",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, short brown hair, brown eyes, tan skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "CRITICAL"
    },
    {
        "name": "brown_eyes_dark_skin",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, afro black hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "CRITICAL"
    },
    {
        "name": "brown_eyes_with_sunglasses",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, red fluffy short hair, wearing red sunglasses, brown eyes, tan skin, black solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "CRITICAL"
    },

    # Baseline: Other eye colors should still work
    {
        "name": "blue_eyes_light_skin",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, black short hair, blue eyes, light skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "BASELINE"
    },
    {
        "name": "green_eyes_tan_skin",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, long red hair, green eyes, tan skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "priority": "BASELINE"
    },
]

# Generation settings
GENERATION_CONFIG = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 24,
    "height": 24,
    "num_images_per_prompt": 3,  # Generate 3 variations to see consistency
}

def load_pipeline_with_lora(lora_path):
    """Load SD 1.5 pipeline with LoRA."""
    print(f"\nLoading pipeline with LoRA: {os.path.basename(lora_path)}")

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )

    # Load LoRA weights
    pipe.load_lora_weights(lora_path)
    pipe = pipe.to("mps")  # Use Metal Performance Shaders on Mac

    return pipe

def generate_test_images(pipe, prompt_config, model_name):
    """Generate test images for a given prompt."""
    prompt = prompt_config["prompt"]
    test_name = prompt_config["name"]
    priority = prompt_config["priority"]

    print(f"\n{'='*80}")
    print(f"[{priority}] Testing: {test_name}")
    print(f"Prompt: {prompt}")
    print(f"Model: {model_name}")

    # Generate multiple variations
    images = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients, soft edges, realistic, photographic",
        **GENERATION_CONFIG
    ).images

    # Save images
    for i, image in enumerate(images):
        filename = f"{test_name}_{model_name}_var{i+1}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        image.save(filepath)
        print(f"  Saved: {filename}")

    return images

def create_comparison_grid(model_name):
    """Create a comparison grid showing all test results for a model."""
    print(f"\nCreating comparison grid for {model_name}...")

    # This is a simple text summary - you can enhance with actual image grid
    summary_path = os.path.join(OUTPUT_DIR, f"SUMMARY_{model_name}.txt")
    with open(summary_path, "w") as f:
        f.write(f"V2.7 Brown Eyes Test Results - {model_name}\n")
        f.write(f"{'='*80}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("CRITICAL TESTS (Brown Eyes Fix):\n")
        for prompt_config in TEST_PROMPTS:
            if prompt_config["priority"] == "CRITICAL":
                f.write(f"  - {prompt_config['name']}\n")

        f.write("\nBASELINE TESTS (Other Eye Colors):\n")
        for prompt_config in TEST_PROMPTS:
            if prompt_config["priority"] == "BASELINE":
                f.write(f"  - {prompt_config['name']}\n")

        f.write(f"\nAll images saved to: {OUTPUT_DIR}\n")
        f.write("\nMANUAL VERIFICATION NEEDED:\n")
        f.write("1. Check brown eyes images - are eyes actually brown (not cyan/blue)?\n")
        f.write("2. Check blue/green eyes images - do they still work correctly?\n")
        f.write("3. Compare all 3 epochs - which performs best?\n")

    print(f"Summary saved: {summary_path}")

def main():
    print("="*80)
    print("V2.7 RUNPOD LORA - BROWN EYES FIX TESTING")
    print("="*80)
    print(f"\nTesting {len(LORA_MODELS)} LoRA models")
    print(f"Running {len(TEST_PROMPTS)} test prompts")
    print(f"Generating {GENERATION_CONFIG['num_images_per_prompt']} variations per test")
    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Test each LoRA model
    for model_name, lora_path in LORA_MODELS.items():
        print(f"\n{'#'*80}")
        print(f"# TESTING: {model_name}")
        print(f"{'#'*80}")

        # Load pipeline
        pipe = load_pipeline_with_lora(lora_path)

        # Run all test prompts
        for prompt_config in TEST_PROMPTS:
            generate_test_images(pipe, prompt_config, model_name)

        # Create summary
        create_comparison_grid(model_name)

        # Clean up
        del pipe
        torch.mps.empty_cache()

    print("\n" + "="*80)
    print("TESTING COMPLETE!")
    print("="*80)
    print(f"\nAll test images saved to: {OUTPUT_DIR}")
    print("\nNEXT STEPS:")
    print("1. Review the brown eyes images - are they actually brown?")
    print("2. Compare with old model results (if you have them)")
    print("3. Determine which epoch (1, 2, or 3) performs best")
    print("4. Download remaining epochs (4, 5, final) from RunPod if needed")
    print("\nIMPORTANT: Look for CRITICAL test results:")
    for prompt_config in TEST_PROMPTS:
        if prompt_config["priority"] == "CRITICAL":
            print(f"  - {prompt_config['name']}")

if __name__ == "__main__":
    main()

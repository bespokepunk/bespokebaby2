#!/usr/bin/env python3
"""
Test Bespoke Baby SD 1.5 LoRA - Epochs 5-9
"""
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path

epochs_to_test = [5, 6, 7, 8, 9]

# Test prompts - same for all epochs
test_prompts = [
    {
        "prompt": "portrait of bespoke punk, green solid background, black hair, blue eyes, light skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "01_bespoke_punk_green_bg"
    },
    {
        "prompt": "portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "02_bespoke_baby_pink_bg"
    },
    {
        "prompt": "portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "03_lad_blue_bg"
    },
    {
        "prompt": "portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "04_lady_purple_bg"
    },
]

gen_params = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512,
}

# Load base model once
print("=" * 60)
print("Loading SD 1.5 base model (once)...")
print("=" * 60)

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    safety_checker=None,
    requires_safety_checker=False
)

if torch.cuda.is_available():
    pipe = pipe.to("cuda")
elif torch.backends.mps.is_available():
    pipe = pipe.to("mps")

print("✓ Base model loaded\n")

# Test each epoch
for epoch in epochs_to_test:
    print("=" * 60)
    print(f"Testing Epoch {epoch}")
    print("=" * 60)
    
    lora_path = f"/Users/ilyssaevans/Downloads/bespoke_baby_sd15-{epoch:06d}.safetensors"
    output_dir = Path(f"test_outputs_sd15_epoch{epoch}")
    output_dir.mkdir(exist_ok=True)
    
    print(f"LoRA: {lora_path}")
    print(f"Output: {output_dir}/")
    
    # Load LoRA
    try:
        pipe.load_lora_weights(lora_path)
        print("✓ LoRA loaded\n")
    except Exception as e:
        print(f"✗ Error loading LoRA: {e}\n")
        continue
    
    # Generate images
    for i, test in enumerate(test_prompts, 1):
        print(f"[{i}/{len(test_prompts)}] {test['name']}")
        
        try:
            image = pipe(
                prompt=test["prompt"],
                negative_prompt=test["negative"],
                **gen_params
            ).images[0]
            
            output_path = output_dir / f"{test['name']}.png"
            image.save(output_path)
            print(f"  ✓ Saved")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Epoch {epoch} complete\n")

print("=" * 60)
print("All epochs tested!")
print("=" * 60)
print("\nOutputs saved in:")
for epoch in epochs_to_test:
    print(f"  - test_outputs_sd15_epoch{epoch}/")

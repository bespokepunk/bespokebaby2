import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path

print("Testing SDXL Epoch 1...")

test_prompts = [
    {"prompt": "pixel art, 24x24, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin", "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render", "name": "01_bespoke_punk_green_bg"},
    {"prompt": "pixel art, 24x24, portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin", "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render", "name": "02_bespoke_baby_pink_bg"},
    {"prompt": "pixel art, 24x24, portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin", "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render", "name": "03_lad_blue_bg"},
    {"prompt": "pixel art, 24x24, portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin", "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render", "name": "04_lady_purple_bg"},
]

print("Loading SDXL base model...")
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant="fp16").to("cuda")

print("Loading LoRA...")
pipe.load_lora_weights("/workspace/output/bespoke_baby_sdxl-000001.safetensors")

output_dir = Path("/workspace/test_epoch1")
output_dir.mkdir(exist_ok=True)

print(f"\nGenerating {len(test_prompts)} test images...")
for i, test in enumerate(test_prompts, 1):
    print(f"[{i}/{len(test_prompts)}] {test['name']}")
    image = pipe(prompt=test["prompt"], negative_prompt=test["negative"], num_inference_steps=30, guidance_scale=7.5, width=1024, height=1024).images[0]
    image.save(output_dir / f"{test['name']}.png")
    print(f"  ✓ Saved")

print(f"\n✓ Complete! Images in: {output_dir}/")

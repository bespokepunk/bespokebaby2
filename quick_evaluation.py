#!/usr/bin/env python3
"""
QUICK EVALUATION: Test critical configurations only (faster results)

Tests:
- All 4 models
- 3 key prompts (simple, checkered pattern, accessories)
- 2 generation configs (default, high CFG)
- 2 quantization levels (12, 15 colors)

Total: 4 × 3 × 2 × 2 = 48 tests (~30-45 minutes)
"""

import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
import json
from collections import Counter

# Reuse functions from comprehensive_evaluation.py
def quantize_to_pixel_art(img, n_colors=15):
    arr = np.array(img)
    original_shape = arr.shape
    pixels = arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    quantized_pixels = kmeans.cluster_centers_[kmeans.labels_]
    quantized_pixels = np.round(quantized_pixels).astype(np.uint8)
    quantized_arr = quantized_pixels.reshape(original_shape)
    return Image.fromarray(quantized_arr)

def analyze_output(img):
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    color_tuples = [tuple(p) for p in pixels]
    color_counts = Counter(color_tuples)
    top_colors = color_counts.most_common(5)
    bg_dominance = (top_colors[0][1] / len(color_tuples)) * 100 if top_colors else 0

    return {
        "unique_colors": len(unique_colors),
        "bg_dominance": bg_dominance,
    }

def score_output(analysis):
    score = 100
    colors = analysis['unique_colors']
    if colors < 8:
        score -= 30
    elif colors > 25:
        score -= 20
    elif 12 <= colors <= 20:
        score += 10

    bg = analysis['bg_dominance']
    if bg > 90:
        score -= 40
    elif 25 <= bg <= 70:
        score += 10
    elif bg < 15:
        score -= 20

    return max(0, min(100, score))

# QUICK TEST CONFIGURATION
TEST_PROMPTS = [
    {"name": "simple_green", "prompt": "bespoke, 24x24 pixel art portrait, bright green solid background, black hair, blue eyes, pale skin", "category": "simple"},
    {"name": "checkered", "prompt": "bespoke, 24x24 pixel art portrait, brown and yellow checkered pattern background, brown hair, brown eyes, light skin, mustache", "category": "pattern"},
    {"name": "sunglasses", "prompt": "bespoke, 24x24 pixel art portrait, purple solid background, long black hair, covered by purple sunglasses, light skin, pink lips", "category": "accessories"},
]

MODELS = {
    "V1_Epoch2": "models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000002.safetensors",
    "V2_Epoch1": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000001.safetensors",
    "V2_Epoch2": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000002.safetensors",
    "V2_Epoch3": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors",
}

GENERATION_CONFIGS = [
    {"name": "default", "steps": 30, "cfg": 7.5},
    {"name": "high_cfg", "steps": 30, "cfg": 10.0},
]

QUANTIZATION_CONFIGS = [
    {"name": "12_colors", "n_colors": 12},
    {"name": "15_colors", "n_colors": 15},
]

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("quick_evaluation")
OUTPUT_DIR.mkdir(exist_ok=True)
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

print("⚡ QUICK EVALUATION")
print("=" * 80)
print(f"Device: {DEVICE}")
total_tests = len(MODELS) * len(TEST_PROMPTS) * len(GENERATION_CONFIGS) * len(QUANTIZATION_CONFIGS)
print(f"Total tests: {total_tests} (estimated 30-45 minutes)")
print("=" * 80)

# Load base model
print(f"\n📦 Loading base model: {BASE_MODEL}")
pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None,
)
pipe = pipe.to(DEVICE)

all_results = []
test_count = 0

for model_name, lora_path in MODELS.items():
    print(f"\n{'='*80}")
    print(f"🧪 MODEL: {model_name}")
    print(f"{'='*80}")

    pipe.unload_lora_weights()
    pipe.load_lora_weights(lora_path)

    model_dir = OUTPUT_DIR / model_name
    model_dir.mkdir(exist_ok=True)

    for test_prompt in TEST_PROMPTS:
        print(f"\n  📝 {test_prompt['name']}")

        prompt_dir = model_dir / test_prompt['name']
        prompt_dir.mkdir(exist_ok=True)

        for gen_config in GENERATION_CONFIGS:
            print(f"    ⚙️  {gen_config['name']}: CFG={gen_config['cfg']}")

            image_512 = pipe(
                prompt=test_prompt["prompt"],
                negative_prompt="blurry, low quality, 3d, photorealistic, smooth, anti-aliasing",
                num_inference_steps=gen_config["steps"],
                guidance_scale=gen_config["cfg"],
                width=512,
                height=512,
            ).images[0]

            for quant_config in QUANTIZATION_CONFIGS:
                test_count += 1

                quantized_512 = quantize_to_pixel_art(image_512, n_colors=quant_config["n_colors"])
                quantized_24 = quantized_512.resize((24, 24), Image.NEAREST)

                quant_512_path = prompt_dir / f"{gen_config['name']}_{quant_config['name']}_512.png"
                quant_24_path = prompt_dir / f"{gen_config['name']}_{quant_config['name']}_24.png"

                quantized_512.save(quant_512_path)
                quantized_24.save(quant_24_path)

                analysis = analyze_output(quantized_24)
                score = score_output(analysis)

                result = {
                    "model": model_name,
                    "prompt_name": test_prompt['name'],
                    "prompt_category": test_prompt['category'],
                    "gen_config": gen_config['name'],
                    "cfg": gen_config['cfg'],
                    "steps": gen_config['steps'],
                    "quant_colors": quant_config['n_colors'],
                    "output_colors": analysis['unique_colors'],
                    "bg_dominance": analysis['bg_dominance'],
                    "score": score,
                    "path_512": str(quant_512_path),
                    "path_24": str(quant_24_path),
                }
                all_results.append(result)

                print(f"       {quant_config['name']}: {analysis['unique_colors']} colors, BG={analysis['bg_dominance']:.1f}%, Score={score}/100")

print(f"\n{'='*80}")
print(f"✅ QUICK EVALUATION COMPLETE! ({test_count} tests)")
print(f"{'='*80}")

# Save results
results_path = OUTPUT_DIR / "quick_results.json"
with open(results_path, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n📊 Results saved to: {results_path}")

# Show top 10
print(f"\n{'='*80}")
print(f"🏆 TOP 10 CONFIGURATIONS:")
print(f"{'='*80}")

sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)

for i, result in enumerate(sorted_results[:10], 1):
    print(f"\n{i}. Score: {result['score']}/100")
    print(f"   Model: {result['model']}")
    print(f"   Prompt: {result['prompt_name']}")
    print(f"   Settings: CFG={result['cfg']}, Quant={result['quant_colors']}→{result['output_colors']} colors")
    print(f"   Path: {result['path_24']}")

print(f"\n{'='*80}")
print("Run 'python analyze_evaluation_results.py' to see detailed analysis")
print(f"{'='*80}")

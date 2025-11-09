#!/usr/bin/env python3
"""
COMPREHENSIVE EVALUATION: Test ALL models, prompts, and settings

This systematically tests:
- All 4 model epochs (V1_Epoch2, V2_Epoch1, V2_Epoch2, V2_Epoch3)
- Diverse prompts (simple, complex, accessories, patterns)
- Different generation settings (CFG scale, inference steps)
- Different quantization settings (color counts)

Goal: Find the ABSOLUTE BEST configuration for production
"""

import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
import json
from collections import Counter

# TEST PROMPTS - Diverse coverage of Bespoke Punk features
TEST_PROMPTS = [
    {
        "name": "simple_solid_bg",
        "prompt": "bespoke, 24x24 pixel art portrait, bright green solid background, black hair, blue eyes, pale skin",
        "category": "simple",
        "expected_features": ["solid_bg", "simple_features"]
    },
    {
        "name": "checkered_pattern",
        "prompt": "bespoke, 24x24 pixel art portrait, brown and yellow checkered pattern background, brown hair, brown eyes, light skin, mustache",
        "category": "pattern",
        "expected_features": ["checkered_bg", "facial_hair"]
    },
    {
        "name": "gradient_bg",
        "prompt": "bespoke, 24x24 pixel art portrait, blue gradient background, dark brown hair, brown/dark skin, beard",
        "category": "gradient",
        "expected_features": ["gradient_bg", "beard"]
    },
    {
        "name": "sunglasses_accessory",
        "prompt": "bespoke, 24x24 pixel art portrait, purple solid background, long black hair, covered by purple sunglasses, light skin, pink lips",
        "category": "accessories",
        "expected_features": ["sunglasses", "long_hair"]
    },
    {
        "name": "hat_accessory",
        "prompt": "bespoke, 24x24 pixel art portrait, red solid background, black hair, red cap, black eyes, tan skin",
        "category": "accessories",
        "expected_features": ["hat", "cap"]
    },
    {
        "name": "complex_multi_accessory",
        "prompt": "bespoke, 24x24 pixel art portrait, teal gradient background, blonde hair, covered by black sunglasses, white/pale skin, earrings, necklace",
        "category": "complex",
        "expected_features": ["sunglasses", "earrings", "necklace", "gradient_bg"]
    },
]

# MODELS TO TEST
MODELS = {
    "V1_Epoch2": "models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000002.safetensors",
    "V2_Epoch1": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000001.safetensors",
    "V2_Epoch2": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000002.safetensors",
    "V2_Epoch3": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors",
}

# GENERATION SETTINGS TO TEST
GENERATION_CONFIGS = [
    {"name": "default", "steps": 30, "cfg": 7.5},
    {"name": "high_cfg", "steps": 30, "cfg": 10.0},
    {"name": "low_cfg", "steps": 30, "cfg": 5.0},
    {"name": "more_steps", "steps": 50, "cfg": 7.5},
]

# QUANTIZATION SETTINGS
QUANTIZATION_CONFIGS = [
    {"name": "15_colors", "n_colors": 15},
    {"name": "12_colors", "n_colors": 12},
    {"name": "20_colors", "n_colors": 20},
]

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("comprehensive_evaluation")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

def quantize_to_pixel_art(img, n_colors=15):
    """Reduce image to n_colors using k-means clustering"""
    arr = np.array(img)
    original_shape = arr.shape
    pixels = arr.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    quantized_pixels = kmeans.cluster_centers_[kmeans.labels_]
    quantized_pixels = np.round(quantized_pixels).astype(np.uint8)
    quantized_arr = quantized_pixels.reshape(original_shape)

    return Image.fromarray(quantized_arr)

def analyze_output(img, expected_features):
    """Analyze generated image quality"""
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)

    # Color distribution
    color_tuples = [tuple(p) for p in pixels]
    color_counts = Counter(color_tuples)
    top_colors = color_counts.most_common(5)

    # Background dominance (assuming top color is background)
    bg_dominance = (top_colors[0][1] / len(color_tuples)) * 100 if top_colors else 0

    # Check if it's mostly one color (might indicate failure)
    single_color_dominant = bg_dominance > 90

    return {
        "unique_colors": len(unique_colors),
        "bg_dominance": bg_dominance,
        "single_color_dominant": single_color_dominant,
        "top_5_colors": [(tuple(c), count) for c, count in top_colors]
    }

def score_output(analysis, expected_features, prompt_category):
    """Score output quality (0-100)"""
    score = 100

    # Color count scoring (target: 12-20 colors)
    colors = analysis['unique_colors']
    if colors < 8:
        score -= 30  # Too few colors, likely failed
    elif colors > 25:
        score -= 20  # Too many colors
    elif 12 <= colors <= 20:
        score += 10  # Perfect range

    # Background dominance (target: 25-70%)
    bg = analysis['bg_dominance']
    if bg > 90:
        score -= 40  # Single color dominance = failure
    elif 25 <= bg <= 70:
        score += 10  # Good background ratio
    elif bg < 15:
        score -= 20  # Fragmented

    # Category-specific scoring
    if prompt_category == "pattern" and colors > 15:
        score += 5  # Patterns need more colors

    return max(0, min(100, score))

print("🔬 COMPREHENSIVE EVALUATION")
print("=" * 80)
print(f"Device: {DEVICE}")
print(f"Testing: {len(MODELS)} models × {len(TEST_PROMPTS)} prompts × {len(GENERATION_CONFIGS)} configs × {len(QUANTIZATION_CONFIGS)} quantizations")
total_tests = len(MODELS) * len(TEST_PROMPTS) * len(GENERATION_CONFIGS) * len(QUANTIZATION_CONFIGS)
print(f"Total tests: {total_tests}")
print("=" * 80)

# Load base model
print(f"\n📦 Loading base model: {BASE_MODEL}")
pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None,
)
pipe = pipe.to(DEVICE)

# Results storage
all_results = []
test_count = 0

for model_name, lora_path in MODELS.items():
    print(f"\n{'='*80}")
    print(f"🧪 MODEL: {model_name}")
    print(f"{'='*80}")

    # Load LoRA
    pipe.unload_lora_weights()
    pipe.load_lora_weights(lora_path)

    model_dir = OUTPUT_DIR / model_name
    model_dir.mkdir(exist_ok=True)

    for test_prompt in TEST_PROMPTS:
        print(f"\n  📝 Prompt: {test_prompt['name']} ({test_prompt['category']})")

        prompt_dir = model_dir / test_prompt['name']
        prompt_dir.mkdir(exist_ok=True)

        for gen_config in GENERATION_CONFIGS:
            print(f"    ⚙️  {gen_config['name']}: CFG={gen_config['cfg']}, Steps={gen_config['steps']}")

            # Generate base image
            image_512 = pipe(
                prompt=test_prompt["prompt"],
                negative_prompt="blurry, low quality, 3d, photorealistic, smooth, anti-aliasing",
                num_inference_steps=gen_config["steps"],
                guidance_scale=gen_config["cfg"],
                width=512,
                height=512,
            ).images[0]

            # Save raw 512x512
            raw_path = prompt_dir / f"{gen_config['name']}_raw_512.png"
            image_512.save(raw_path)

            # Test different quantizations
            for quant_config in QUANTIZATION_CONFIGS:
                test_count += 1

                # Quantize
                quantized_512 = quantize_to_pixel_art(image_512, n_colors=quant_config["n_colors"])
                quantized_24 = quantized_512.resize((24, 24), Image.NEAREST)

                # Save
                quant_512_path = prompt_dir / f"{gen_config['name']}_{quant_config['name']}_512.png"
                quant_24_path = prompt_dir / f"{gen_config['name']}_{quant_config['name']}_24.png"

                quantized_512.save(quant_512_path)
                quantized_24.save(quant_24_path)

                # Analyze
                analysis = analyze_output(quantized_24, test_prompt['expected_features'])
                score = score_output(analysis, test_prompt['expected_features'], test_prompt['category'])

                # Store results
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
print(f"✅ EVALUATION COMPLETE! ({test_count} total tests)")
print(f"{'='*80}")

# Save results to JSON
results_path = OUTPUT_DIR / "evaluation_results.json"
with open(results_path, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n📊 Results saved to: {results_path}")
print(f"📁 All outputs in: {OUTPUT_DIR}/")

# Print top 10 results
print(f"\n{'='*80}")
print(f"🏆 TOP 10 CONFIGURATIONS:")
print(f"{'='*80}")

sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)

for i, result in enumerate(sorted_results[:10], 1):
    print(f"\n{i}. Score: {result['score']}/100")
    print(f"   Model: {result['model']}")
    print(f"   Prompt: {result['prompt_name']} ({result['prompt_category']})")
    print(f"   Settings: {result['gen_config']} (CFG={result['cfg']}, Steps={result['steps']})")
    print(f"   Quantization: {result['quant_colors']} → {result['output_colors']} colors")
    print(f"   BG Dominance: {result['bg_dominance']:.1f}%")
    print(f"   24x24: {result['path_24']}")

print(f"\n{'='*80}")
print("Analysis complete! Review outputs and scores to determine best configuration.")
print(f"{'='*80}")

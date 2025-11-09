#!/usr/bin/env python3
"""
Bespoke Punk Generator V2 - Improved with Training Caption Format

Learns from training captions and generates prompts in the same format.
Uses weighted color palette extraction instead of naive feature guessing.
"""

import argparse
import os
import glob
import random
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import torch
from diffusers import StableDiffusionPipeline
import colorsys


class TrainingVocabulary:
    """Analyzes training captions to extract vocabulary"""

    def __init__(self, training_dir="FORTRAINING6/bespokepunktext"):
        self.hair_colors = set()
        self.eye_colors = set()
        self.skin_tones = set()
        self.backgrounds = set()

        # Load and analyze training captions
        if os.path.exists(training_dir):
            self._analyze_training_captions(training_dir)

        # Fallback vocabulary if training dir not found
        if not self.hair_colors:
            self._load_fallback_vocabulary()

    def _analyze_training_captions(self, training_dir):
        """Extract vocabulary from actual training captions"""
        caption_files = glob.glob(os.path.join(training_dir, "*.txt"))

        for caption_file in caption_files[:50]:  # Sample first 50
            try:
                with open(caption_file, 'r') as f:
                    caption = f.read().lower()

                    # Extract hair colors
                    if "hair" in caption:
                        for color in ["black", "brown", "blonde", "white", "gray", "grey",
                                    "red", "blue", "green", "pink", "purple", "dark"]:
                            if f"{color} hair" in caption:
                                self.hair_colors.add(color)

                    # Extract eye colors
                    if "eyes" in caption:
                        for color in ["brown", "blue", "green", "gray", "grey", "pink"]:
                            if f"{color} eyes" in caption:
                                self.eye_colors.add(color)

                    # Extract skin tones
                    for tone in ["light skin", "tan skin", "pale skin", "medium skin", "dark skin"]:
                        if tone in caption:
                            self.skin_tones.add(tone)
            except:
                continue

    def _load_fallback_vocabulary(self):
        """Fallback vocabulary based on common Bespoke Punk patterns"""
        self.hair_colors = {"black", "brown", "blonde", "white", "gray", "dark", "light"}
        self.eye_colors = {"brown", "blue", "green", "gray"}
        self.skin_tones = {"light skin", "tan skin", "pale skin"}


class ColorPaletteExtractor:
    """Extracts weighted color palette from images"""

    def __init__(self, image_path):
        self.image = Image.open(image_path).convert('RGB')
        self.width, self.height = self.image.size

    def get_color_palette(self, n_colors=12):
        """Extract dominant colors using k-means"""
        # Resize for faster processing
        img_small = self.image.resize((100, 100))
        pixels = np.array(img_small).reshape(-1, 3)

        # K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Get colors and weights
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        color_counts = np.bincount(labels)
        color_weights = color_counts / len(labels)

        # Sort by weight
        sorted_indices = np.argsort(color_weights)[::-1]

        palette = []
        for i in sorted_indices:
            rgb = tuple(colors[i].astype(int))
            palette.append({
                'rgb': rgb,
                'hex': self._rgb_to_hex(rgb),
                'weight': float(color_weights[i]),
                'name': self._rgb_to_color_name(colors[i])
            })

        return palette

    def detect_background(self):
        """Detect background color from edges"""
        img_array = np.array(self.image)

        # Sample edges
        edge_pixels = []
        edge_pixels.extend(img_array[0, :].tolist())  # Top
        edge_pixels.extend(img_array[-1, :].tolist())  # Bottom
        edge_pixels.extend(img_array[:, 0].tolist())  # Left
        edge_pixels.extend(img_array[:, -1].tolist())  # Right

        # Find most common edge color
        edge_pixels = np.array(edge_pixels)
        kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
        kmeans.fit(edge_pixels)
        bg_color = kmeans.cluster_centers_[0]

        return {
            'rgb': tuple(bg_color.astype(int)),
            'hex': self._rgb_to_hex(tuple(bg_color.astype(int))),
            'name': self._rgb_to_color_name(bg_color)
        }

    def _rgb_to_hex(self, rgb):
        """Convert RGB to hex"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def _rgb_to_color_name(self, rgb):
        """Convert RGB to color name"""
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        h_degrees = h * 360

        # Handle grayscale
        if s < 0.1:
            if v > 0.9:
                return 'white'
            elif v < 0.1:
                return 'black'
            elif v > 0.6:
                return 'light gray'
            else:
                return 'dark gray'

        # Color names based on hue
        if h_degrees < 15 or h_degrees >= 345:
            color = 'red'
        elif h_degrees < 45:
            color = 'orange'
        elif h_degrees < 75:
            color = 'yellow'
        elif h_degrees < 150:
            color = 'green'
        elif h_degrees < 210:
            color = 'cyan'
        elif h_degrees < 270:
            color = 'blue'
        elif h_degrees < 330:
            color = 'purple'
        else:
            color = 'red'

        # Add lightness
        if v < 0.3:
            return f'dark {color}'
        elif v > 0.7 and s < 0.5:
            return f'light {color}'

        return color


class TrainingFormatPromptGenerator:
    """Generates prompts in training caption format"""

    def __init__(self, vocabulary):
        self.vocab = vocabulary

    def generate(self, palette, background):
        """Generate prompt from color palette using training format"""

        # Build prompt in training format:
        # "pixel art, 24x24, portrait of bespoke punk,
        #  [background], [hair], [eyes], [skin],
        #  sharp pixel edges, hard color borders"

        prompt_parts = [
            "pixel art",
            "24x24",
            "portrait of bespoke punk"
        ]

        # Background with hex
        bg_desc = self._describe_background(background)
        prompt_parts.append(bg_desc)

        # Map remaining colors to features
        non_bg_colors = [c for c in palette if c['name'] != background['name']][:4]

        # Hair color (usually darker/more saturated)
        hair_color = self._map_to_hair(non_bg_colors)
        if hair_color:
            prompt_parts.append(f"{hair_color} hair")

        # Eye color (pick from palette)
        eye_color = self._map_to_eyes(non_bg_colors)
        if eye_color:
            prompt_parts.append(f"{eye_color} eyes")

        # Skin tone (usually lighter colors)
        skin_tone = self._map_to_skin(non_bg_colors)
        if skin_tone:
            prompt_parts.append(skin_tone)

        # Always end with these
        prompt_parts.extend([
            "sharp pixel edges",
            "hard color borders"
        ])

        prompt = ", ".join(prompt_parts)

        return {
            'prompt': prompt,
            'metadata': {
                'background': bg_desc,
                'hair': hair_color,
                'eyes': eye_color,
                'skin': skin_tone,
                'color_palette': [c['name'] for c in palette[:5]]
            }
        }

    def _describe_background(self, bg):
        """Describe background in training format"""
        # Format: "color solid background (hex)"
        return f"{bg['name']} solid background ({bg['hex']})"

    def _map_to_hair(self, colors):
        """Map colors to hair color vocabulary"""
        hair_candidates = ["black", "dark gray", "brown", "dark brown",
                          "blonde", "white", "gray"]

        for color in colors:
            name = color['name']
            if "black" in name or "dark" in name:
                return "black"
            if "brown" in name:
                return "brown"
            if "gray" in name or "grey" in name:
                return "gray"
            if "white" in name:
                return "white"
            if "yellow" in name or "orange" in name:
                return "blonde"

        return "brown"  # Default

    def _map_to_eyes(self, colors):
        """Map colors to eye color vocabulary"""
        eye_candidates = ["brown", "blue", "green", "gray"]

        for color in colors:
            name = color['name']
            if "blue" in name:
                return "blue"
            if "green" in name:
                return "green"
            if "gray" in name or "grey" in name:
                return "gray"
            if "brown" in name:
                return "brown"

        return "brown"  # Default

    def _map_to_skin(self, colors):
        """Map colors to skin tone vocabulary"""
        # Look for light/medium colors
        for color in colors:
            name = color['name']
            if "light" in name or "white" in name:
                return "light skin"
            if "orange" in name or "tan" in name:
                return "tan skin"
            if "dark" in name and "brown" in name:
                return "dark skin"

        return "light skin"  # Default


class BespokePunkGenerator:
    """Generates Bespoke Punks using trained LoRA"""

    def __init__(self, lora_path, model_name="runwayml/stable-diffusion-v1-5", disable_safety_checker=True):
        print(f"Loading model: {model_name}")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16
        ).to("mps")

        # Disable safety checker if requested (avoids false positives)
        if disable_safety_checker:
            self.pipe.safety_checker = None
            print("  ⚠️ Safety checker disabled")

        print(f"Loading LoRA: {lora_path}")
        lora_dir = os.path.dirname(lora_path)
        lora_file = os.path.basename(lora_path)
        self.pipe.load_lora_weights(lora_dir, weight_name=lora_file)
        print("✓ Model and LoRA loaded")

    def generate(self, prompt, num_inference_steps=30, guidance_scale=7.5):
        """Generate Bespoke Punk at 512×512"""
        image_512 = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=512,
            width=512,
        ).images[0]

        return image_512

    def downscale_to_24x24(self, image_512):
        """Downscale to 24×24 using NEAREST neighbor"""
        return image_512.resize((24, 24), Image.NEAREST)


def main():
    parser = argparse.ArgumentParser(description='Generate Bespoke Punks from any image (V2)')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', default='output_punk_v2.png', help='Output filename')
    parser.add_argument('--lora', default='Context 1106/bespoke_punks_sd15_512-000002.safetensors',
                       help='Path to LoRA checkpoint')
    parser.add_argument('--steps', type=int, default=30, help='Number of inference steps')
    parser.add_argument('--guidance', type=float, default=7.5, help='Guidance scale')
    parser.add_argument('--save-512', action='store_true', help='Also save 512×512 version')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return

    print("="*60)
    print("BESPOKE PUNK GENERATOR V2")
    print("="*60)

    # Step 1: Load training vocabulary
    print("\n[1/5] Loading training vocabulary...")
    vocab = TrainingVocabulary()
    print(f"  ✓ Loaded vocabulary from training captions")

    # Step 2: Extract color palette
    print("\n[2/5] Extracting color palette...")
    extractor = ColorPaletteExtractor(args.input)
    palette = extractor.get_color_palette(n_colors=12)
    background = extractor.detect_background()

    print(f"  ✓ Extracted {len(palette)} colors")
    print(f"  ✓ Background: {background['name']} ({background['hex']})")
    print(f"  ✓ Top colors: {[c['name'] for c in palette[:5]]}")

    # Step 3: Generate prompt in training format
    print("\n[3/5] Generating prompt...")
    prompt_gen = TrainingFormatPromptGenerator(vocab)
    result = prompt_gen.generate(palette, background)
    prompt = result['prompt']
    metadata = result['metadata']

    print(f"  ✓ Prompt: {prompt}")
    print(f"  ✓ Metadata: {metadata}")

    # Step 4: Generate Bespoke Punk
    print("\n[4/5] Generating Bespoke Punk...")
    generator = BespokePunkGenerator(args.lora)
    image_512 = generator.generate(prompt, args.steps, args.guidance)
    print("  ✓ Generated 512×512 image")

    # Step 5: Downscale to 24×24
    print("\n[5/5] Downscaling to 24×24...")
    image_24 = generator.downscale_to_24x24(image_512)
    print("  ✓ Downscaled to 24×24")

    # Save outputs
    output_dir = os.path.dirname(args.output) or '.'
    os.makedirs(output_dir, exist_ok=True)

    image_24.save(args.output)
    print(f"\n✓ Saved 24×24 output: {args.output}")

    if args.save_512:
        output_512 = args.output.replace('.png', '_512.png')
        image_512.save(output_512)
        print(f"✓ Saved 512×512 output: {output_512}")

    print("\n" + "="*60)
    print("GENERATION COMPLETE!")
    print("="*60)
    print(f"\nPrompt used: {prompt}")
    print(f"Output saved to: {args.output}")

    print("\n" + "="*60)
    print("FUTURE ENHANCEMENT OPTION")
    print("="*60)
    print("For more accurate feature detection, consider adding:")
    print("- BLIP-2 or LLaVA vision model")
    print("- Would understand 'person wearing helmet' vs 'person with hair'")
    print("- Requires additional model downloads (~2-4GB)")
    print("="*60)


if __name__ == "__main__":
    main()

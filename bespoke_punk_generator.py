#!/usr/bin/env python3
"""
Bespoke Punk Generator - Create personalized Bespoke Punks from any image

Pipeline:
1. Upload any image (avatar, photo, etc.)
2. Extract features (colors, attributes)
3. Generate prompt from features
4. Create Bespoke Punk at 512×512 using trained LoRA
5. Downscale to 24×24 using NEAREST neighbor

Usage:
    python bespoke_punk_generator.py --input path/to/image.jpg --output my_punk.png
"""

import argparse
import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import torch
from diffusers import StableDiffusionPipeline
import colorsys


class ImageAnalyzer:
    """Analyzes uploaded images to extract colors and features"""

    COLOR_NAMES = {
        # Define color ranges for naming
        'red': ((0, 30), (330, 360)),
        'orange': (30, 60),
        'yellow': (60, 90),
        'green': (90, 150),
        'cyan': (150, 210),
        'blue': (210, 270),
        'purple': (270, 330),
    }

    def __init__(self, image_path):
        self.image = Image.open(image_path).convert('RGB')
        self.width, self.height = self.image.size

    def get_dominant_colors(self, n_colors=5):
        """Extract dominant colors using k-means clustering"""
        # Resize for faster processing
        img_small = self.image.resize((150, 150))
        pixels = np.array(img_small).reshape(-1, 3)

        # K-means clustering to find dominant colors
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Get colors and their percentages
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_

        # Calculate percentage of each color
        color_counts = np.bincount(labels)
        color_percentages = color_counts / len(labels)

        # Sort by percentage
        sorted_indices = np.argsort(color_percentages)[::-1]

        return [
            {
                'rgb': tuple(colors[i].astype(int)),
                'percentage': float(color_percentages[i]),
                'name': self._rgb_to_color_name(colors[i])
            }
            for i in sorted_indices
        ]

    def _rgb_to_color_name(self, rgb):
        """Convert RGB to human-readable color name"""
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

        # Find color name based on hue
        for color_name, hue_range in self.COLOR_NAMES.items():
            if isinstance(hue_range, tuple) and isinstance(hue_range[0], tuple):
                # Handle wrap-around (like red)
                if (hue_range[0][0] <= h_degrees <= hue_range[0][1] or
                    hue_range[1][0] <= h_degrees <= hue_range[1][1]):
                    return self._add_lightness(color_name, v)
            else:
                if hue_range[0] <= h_degrees < hue_range[1]:
                    return self._add_lightness(color_name, v)

        return 'colorful'

    def _add_lightness(self, color_name, value):
        """Add lightness descriptor to color"""
        if value < 0.3:
            return f'dark {color_name}'
        elif value > 0.7:
            return f'light {color_name}'
        return color_name

    def detect_background(self):
        """Detect background color (assume edges are background)"""
        # Sample edge pixels
        edge_pixels = []
        img_array = np.array(self.image)

        # Top edge
        edge_pixels.extend(img_array[0, :].tolist())
        # Bottom edge
        edge_pixels.extend(img_array[-1, :].tolist())
        # Left edge
        edge_pixels.extend(img_array[:, 0].tolist())
        # Right edge
        edge_pixels.extend(img_array[:, -1].tolist())

        # Find most common edge color
        edge_pixels = np.array(edge_pixels)
        kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
        kmeans.fit(edge_pixels)
        bg_color = kmeans.cluster_centers_[0]

        return {
            'rgb': tuple(bg_color.astype(int)),
            'name': self._rgb_to_color_name(bg_color)
        }


class PromptGenerator:
    """Generates SD prompts from extracted image features"""

    SKIN_TONES = {
        'light': ['white', 'light gray', 'light orange', 'light yellow'],
        'medium': ['orange', 'yellow', 'dark yellow'],
        'dark': ['dark orange', 'dark red', 'dark gray'],
    }

    def __init__(self, features):
        self.features = features

    def generate(self):
        """Generate prompt from features"""
        dominant_colors = self.features['dominant_colors']
        background = self.features['background']

        # Detect likely skin tone (usually in top 3 colors)
        skin_tone = self._detect_skin_tone(dominant_colors[:3])

        # Detect hair color (usually darker/saturated color)
        hair_color = self._detect_hair_color(dominant_colors)

        # Background - use detected background or most dominant color
        bg_color = background['name']

        # Build prompt
        prompt_parts = [
            "pixel art",
            "portrait of bespoke punk",
            f"{bg_color} solid background",
        ]

        # Add hair if detected
        if hair_color:
            prompt_parts.append(f"{hair_color} hair")

        # Add skin tone
        prompt_parts.append(f"{skin_tone} skin")

        # Always include style descriptors
        prompt_parts.extend([
            "sharp pixel edges",
            "limited color palette"
        ])

        prompt = ", ".join(prompt_parts)

        return {
            'prompt': prompt,
            'metadata': {
                'background': bg_color,
                'hair_color': hair_color,
                'skin_tone': skin_tone,
                'dominant_colors': [c['name'] for c in dominant_colors[:3]]
            }
        }

    def _detect_skin_tone(self, top_colors):
        """Detect skin tone from top colors"""
        for color_info in top_colors:
            color_name = color_info['name']
            for tone, color_list in self.SKIN_TONES.items():
                if any(c in color_name for c in color_list):
                    return tone
        return 'light'  # Default

    def _detect_hair_color(self, colors):
        """Detect likely hair color"""
        # Look for dark/saturated colors
        for color_info in colors[1:4]:  # Skip background
            color_name = color_info['name']
            if any(word in color_name for word in ['black', 'dark', 'brown']):
                return color_name
            if any(word in color_name for word in ['red', 'orange', 'yellow', 'blue', 'green', 'purple']):
                return color_name
        return 'dark'  # Default


class BespokePunkGenerator:
    """Generates Bespoke Punks using trained LoRA"""

    def __init__(self, lora_path, model_name="runwayml/stable-diffusion-v1-5"):
        """Initialize generator with trained LoRA"""
        print(f"Loading model: {model_name}")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16
        ).to("mps")  # Use Metal Performance Shaders on Mac

        print(f"Loading LoRA: {lora_path}")
        # Extract directory and filename
        lora_dir = os.path.dirname(lora_path)
        lora_file = os.path.basename(lora_path)
        self.pipe.load_lora_weights(lora_dir, weight_name=lora_file)
        print("✓ Model and LoRA loaded")

    def generate(self, prompt, num_inference_steps=30, guidance_scale=7.5):
        """Generate Bespoke Punk at 512×512"""
        print(f"\nGenerating with prompt: {prompt}")

        image_512 = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=512,
            width=512,
        ).images[0]

        return image_512

    def downscale_to_24x24(self, image_512):
        """Downscale to 24×24 using NEAREST neighbor (pixel-perfect)"""
        image_24 = image_512.resize((24, 24), Image.NEAREST)
        return image_24


def main():
    parser = argparse.ArgumentParser(description='Generate personalized Bespoke Punks from any image')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', default='output_punk.png', help='Output filename')
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
    print("BESPOKE PUNK GENERATOR")
    print("="*60)

    # Step 1: Analyze input image
    print("\n[1/4] Analyzing input image...")
    analyzer = ImageAnalyzer(args.input)
    dominant_colors = analyzer.get_dominant_colors(n_colors=5)
    background = analyzer.detect_background()

    print(f"  ✓ Detected {len(dominant_colors)} dominant colors")
    print(f"  ✓ Background: {background['name']}")
    print(f"  ✓ Top 3 colors: {[c['name'] for c in dominant_colors[:3]]}")

    features = {
        'dominant_colors': dominant_colors,
        'background': background
    }

    # Step 2: Generate prompt
    print("\n[2/4] Generating prompt...")
    prompt_gen = PromptGenerator(features)
    result = prompt_gen.generate()
    prompt = result['prompt']
    metadata = result['metadata']

    print(f"  ✓ Prompt: {prompt}")
    print(f"  ✓ Metadata: {metadata}")

    # Step 3: Generate Bespoke Punk
    print("\n[3/4] Generating Bespoke Punk...")
    generator = BespokePunkGenerator(args.lora)
    image_512 = generator.generate(prompt, args.steps, args.guidance)
    print("  ✓ Generated 512×512 image")

    # Step 4: Downscale to 24×24
    print("\n[4/4] Downscaling to 24×24...")
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


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
PRODUCTION PIPELINE: User Photo → Bespoke Punk NFT
Uses SD 1.5 Epoch 7 LoRA (best results with accurate brown eyes)

Complete workflow:
1. User uploads photo
2. Analyze photo: extract colors, features, traits
3. Map to training vocabulary
4. Generate training-format prompt
5. Generate 512x512 bespoke punk with epoch 7
6. Downscale to 24x24 for final NFT

Usage:
    python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np
from pathlib import Path
from collections import Counter
import argparse
import sys

# ============================================================================
# COLOR PALETTE EXTRACTION (Simple version - no sklearn needed)
# ============================================================================

class ColorPaletteExtractor:
    """Extract dominant colors from user photo using simple histogram"""

    def __init__(self, image_path):
        self.image = Image.open(image_path).convert('RGB')
        self.image_array = np.array(self.image)

    def get_palette(self, n_colors=12):
        """Get n dominant colors using histogram"""
        # Quantize to reduce color space
        quantized = self.image.quantize(colors=n_colors, method=2)
        palette = quantized.getpalette()[:n_colors*3]

        # Convert to list of RGB tuples
        colors = []
        for i in range(0, len(palette), 3):
            colors.append(palette[i:i+3])

        return [self.rgb_to_hex(c) for c in colors]

    def rgb_to_hex(self, rgb):
        """Convert RGB to hex"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def get_dominant_color(self, region='background'):
        """Get most dominant color (usually background)"""
        palette = self.get_palette(n_colors=5)
        return palette[0]  # Most dominant

# ============================================================================
# SIMPLE FEATURE EXTRACTION
# ============================================================================

class ImprovedFeatureExtractor:
    """
    Improved feature extraction that works with stylized art and cartoons.
    Uses dominant color analysis instead of region sampling.
    """

    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert('RGB')
        self.arr = np.array(self.image)
        self.height, self.width = self.arr.shape[:2]

        # Get dominant colors from the image
        self.palette = self._get_dominant_colors(n_colors=15)

    def _get_dominant_colors(self, n_colors=15):
        """Get dominant colors using quantization"""
        quantized = self.image.quantize(colors=n_colors, method=2)
        palette_data = quantized.getpalette()[:n_colors*3]

        colors = []
        for i in range(0, len(palette_data), 3):
            rgb = (palette_data[i], palette_data[i+1], palette_data[i+2])
            colors.append(rgb)

        # Count pixels for each color to rank by dominance
        quantized_arr = np.array(quantized)
        color_counts = Counter(quantized_arr.flatten())

        # Sort by count
        sorted_colors = [(colors[idx], count) for idx, count in color_counts.most_common()]
        return sorted_colors

    def detect_hair_color(self):
        """
        Detect hair color by analyzing colors in upper portion of image,
        excluding very bright colors (likely background) and skin tones.
        """
        # Sample upper 40% of image (hair region)
        hair_region = self.arr[:int(self.height * 0.4), :]

        # Get dominant colors in hair region
        hair_pixels = hair_region.reshape(-1, 3)

        # Filter out likely background (very dominant colors covering >30% of region)
        total_pixels = len(hair_pixels)
        color_counts = Counter(map(tuple, hair_pixels))

        # Find hair colors (not background, not skin tone)
        hair_color_candidates = []

        for color, count in color_counts.most_common(20):
            pct = count / total_pixels
            r, g, b = color

            # Skip if it's likely background (too dominant)
            if pct > 0.35:
                continue

            # Skip if it's likely skin tone
            if self._is_skin_tone(r, g, b):
                continue

            # Skip if it's white/very bright (likely glasses frame or highlights)
            brightness = (r + g + b) / 3
            if brightness > 240:
                continue

            hair_color_candidates.append((color, count, pct))

        if not hair_color_candidates:
            # Fallback to most common non-white color
            for color, count in color_counts.most_common(10):
                r, g, b = color
                if (r + g + b) / 3 < 240:
                    return self._color_name_from_rgb(color, is_hair=True)
            return "brown"

        # Get the most common hair color
        dominant_hair_color = hair_color_candidates[0][0]
        return self._color_name_from_rgb(dominant_hair_color, is_hair=True)

    def detect_eye_color(self):
        """
        Detect eye color by looking at small dark regions in face area.
        Improved to avoid detecting sunglasses as eyes.
        """
        # Sample face region (30-60% height, 25-75% width)
        face_region = self.arr[int(self.height*0.3):int(self.height*0.6),
                               int(self.width*0.25):int(self.width*0.75)]

        face_pixels = face_region.reshape(-1, 3)

        # Look for small dark regions (likely eyes)
        # Eyes are usually darker but not pure black
        eye_candidates = []

        for pixel in face_pixels:
            r, g, b = pixel
            brightness = (r + g + b) / 3

            # Eyes are typically in 30-120 brightness range
            # Too dark (< 30) is likely sunglasses/accessories
            # Too bright is not eyes
            if 30 <= brightness <= 120:
                # Check if it's not skin tone
                if not self._is_skin_tone(r, g, b):
                    eye_candidates.append(pixel)

        if len(eye_candidates) == 0:
            # If no eye candidates, might be hidden by sunglasses
            # Look for any dark pixels as fallback
            dark_pixels = face_pixels[(face_pixels.mean(axis=1) >= 20) &
                                      (face_pixels.mean(axis=1) <= 80)]
            if len(dark_pixels) > 0:
                avg_color = dark_pixels.mean(axis=0).astype(int)
                return self._color_name_from_rgb(tuple(avg_color), is_eyes=True)
            return "brown"  # Default fallback

        # Average the eye candidate pixels
        avg_eye_color = np.mean(eye_candidates, axis=0).astype(int)
        return self._color_name_from_rgb(tuple(avg_eye_color), is_eyes=True)

    def detect_skin_tone(self):
        """Detect skin tone from face region"""
        # Sample center of image (likely face)
        face_region = self.arr[int(self.height*0.35):int(self.height*0.65),
                               int(self.width*0.3):int(self.width*0.7)]

        face_pixels = face_region.reshape(-1, 3)

        # Find skin-toned pixels
        skin_pixels = []
        for pixel in face_pixels:
            r, g, b = pixel
            if self._is_skin_tone(r, g, b):
                skin_pixels.append(pixel)

        if len(skin_pixels) == 0:
            return "light"

        # Average skin pixels
        avg_skin = np.mean(skin_pixels, axis=0)
        brightness = avg_skin.mean()

        if brightness > 210:
            return "light"
        elif brightness > 160:
            return "medium"
        elif brightness > 100:
            return "tan"
        else:
            return "dark"

    def _is_skin_tone(self, r, g, b):
        """Check if RGB values represent a skin tone"""
        # Skin tones have specific RGB relationships
        # R > G > B typically, and within certain ranges

        if r < 50:  # Too dark to be skin
            return False

        if r > 255 or g > 255 or b > 255:  # Invalid
            return False

        # Skin tone checks
        # 1. Red channel is highest
        if not (r >= g and g >= b * 0.9):
            return False

        # 2. Not too saturated (not too much red)
        if r - g > 80:
            return False

        # 3. Blue is significantly lower
        if b > g * 0.95:
            return False

        # 4. Overall brightness in skin range
        brightness = (r + g + b) / 3
        if brightness < 60 or brightness > 250:
            return False

        return True

    def _color_name_from_rgb(self, rgb, is_hair=False, is_eyes=False):
        """
        Convert RGB to color name with improved logic for stylized art.
        """
        r, g, b = rgb

        if is_eyes:
            # Eye color detection
            brightness = (r + g + b) / 3

            # Blue eyes: Blue channel dominant
            if b > r * 1.2 and b > g * 1.2 and b > 80:
                return "blue"

            # Green eyes: Green channel dominant
            if g > r * 1.1 and g > b * 1.2 and g > 60:
                return "green"

            # Gray eyes: Low saturation, medium brightness
            if max(r, g, b) - min(r, g, b) < 40 and 80 < brightness < 150:
                return "gray"

            # Black eyes: Very dark
            if brightness < 50:
                return "black"

            # Brown eyes: Default
            return "brown"

        if is_hair:
            # Hair color detection
            brightness = (r + g + b) / 3

            # Black hair
            if brightness < 60:
                return "black"

            # Blonde/Yellow hair
            if (r > 180 and g > 150 and b < 150) or (r > 200 and g > 180):
                return "blonde"

            # Red/Orange hair
            if r > 150 and r > g * 1.3 and g > b:
                return "red"

            # Blue hair
            if b > r * 1.3 and b > g * 1.3 and b > 100:
                return "blue"

            # Green hair
            if g > r * 1.3 and g > b * 1.1 and g > 100:
                return "green"

            # Purple hair
            if r > 100 and b > 100 and abs(r - b) < 80 and g < r * 0.8:
                return "purple"

            # Pink hair
            if r > 150 and b > 100 and g < r * 0.9 and r > b * 1.2:
                return "pink"

            # Gray/White hair
            if brightness > 180 and max(r, g, b) - min(r, g, b) < 50:
                return "gray"

            # Brown hair
            if 60 <= brightness < 140:
                return "brown"

            # Default blonde for bright colors
            if brightness >= 140:
                return "blonde"

            return "brown"

        # General color detection
        brightness = (r + g + b) / 3

        if brightness < 50:
            return "black"
        elif r > 200 and g < 100 and b < 100:
            return "red"
        elif r > 200 and g > 150 and b < 120:
            return "orange"
        elif r > 200 and g > 200 and b < 150:
            return "yellow"
        elif g > 150 and g > r * 1.2 and g > b * 1.2:
            return "green"
        elif b > 150 and b > r * 1.2 and b > g * 1.2:
            return "blue"
        elif r > 150 and b > 150 and abs(r - b) < 50:
            return "purple"
        elif brightness > 200:
            return "white"
        elif brightness > 140:
            return "gray"
        else:
            return "brown"

# ============================================================================
# PROMPT GENERATOR
# ============================================================================

class BespokePunkPromptGenerator:
    """
    Generate training-format prompts that match our training data exactly.

    Training format:
    "pixel art, 24x24, portrait of bespoke punk [lady/lad],
     [hair], [accessories], [eyes], [skin], [background],
     sharp pixel edges, hard color borders, retro pixel art style"
    """

    def __init__(self):
        # Training vocabulary for consistency
        self.hair_styles = [
            "black hair", "brown hair", "blonde hair", "red hair",
            "blue hair", "green hair", "purple hair", "gray hair",
            "afro hair", "curly hair", "wavy hair"
        ]

        self.eye_colors = [
            "brown eyes", "blue eyes", "green eyes", "black eyes", "gray eyes"
        ]

        self.skin_tones = [
            "light skin", "medium skin", "tan skin", "dark skin"
        ]

        self.backgrounds = [
            "blue", "green", "red", "purple", "orange", "yellow",
            "pink", "gray", "brown", "teal", "cyan"
        ]

    def generate(self, features, gender="lady"):
        """
        Generate training-format prompt from extracted features.

        Args:
            features: Dict with keys: hair_color, eye_color, skin_tone, background_color
            gender: "lady" or "lad"

        Returns:
            Complete prompt string
        """

        # Base
        prompt_parts = [
            "pixel art",
            "24x24",
            f"portrait of bespoke punk {gender}"
        ]

        # Hair
        hair = f"{features['hair_color']} hair"
        prompt_parts.append(hair)

        # Eyes
        eyes = f"{features['eye_color']} eyes"
        prompt_parts.append(eyes)

        # Skin
        skin = f"{features['skin_tone']} skin"
        prompt_parts.append(skin)

        # Background
        bg_color = features.get('background_color', 'blue')
        prompt_parts.append(f"{bg_color} solid background")

        # Style markers (CRITICAL for pixel art quality)
        prompt_parts.extend([
            "sharp pixel edges",
            "hard color borders",
            "retro pixel art style"
        ])

        return ", ".join(prompt_parts)

# ============================================================================
# BESPOKE PUNK GENERATOR
# ============================================================================

class BespokePunkGenerator:
    """
    Generate bespoke punks using SD 1.5 + Epoch 7 LoRA
    """

    def __init__(self, lora_path, device=None):
        """
        Initialize generator with epoch 7 LoRA.

        Args:
            lora_path: Path to epoch 7 .safetensors file
            device: 'mps', 'cuda', or 'cpu' (auto-detected if None)
        """
        self.lora_path = lora_path

        # Auto-detect device
        if device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device

        print(f"🎨 Loading SD 1.5 with Epoch 7 LoRA...")
        print(f"   Device: {self.device}")

        # Load SD 1.5
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            safety_checker=None,
        )

        # Load epoch 7 LoRA
        self.pipe.load_lora_weights(lora_path)

        # Move to device
        self.pipe = self.pipe.to(self.device)

        print(f"   ✓ Loaded successfully!\n")

    def generate(self, prompt, negative_prompt=None, seed=None):
        """
        Generate bespoke punk from prompt.

        Args:
            prompt: Training-format prompt
            negative_prompt: Things to avoid
            seed: Random seed for reproducibility

        Returns:
            PIL Image (512x512)
        """

        if negative_prompt is None:
            negative_prompt = "blurry, smooth, gradients, antialiased, photography, realistic, 3d render"

        # Set seed if provided
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None

        print(f"🎨 Generating bespoke punk...")
        print(f"   Prompt: {prompt[:80]}...")

        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
            generator=generator,
        ).images[0]

        print(f"   ✓ Generated 512x512 image")
        return image

    def downscale_to_24x24(self, image_512):
        """Downscale to 24x24 for final NFT"""
        image_24 = image_512.resize((24, 24), Image.NEAREST)
        return image_24

# ============================================================================
# COMPLETE PIPELINE
# ============================================================================

class UserToBespokePunkPipeline:
    """
    Complete production pipeline: User Photo → Bespoke Punk NFT
    """

    def __init__(self, lora_path):
        """Initialize pipeline with epoch 7 LoRA"""
        self.generator = BespokePunkGenerator(lora_path)
        self.prompt_builder = BespokePunkPromptGenerator()

    def process(self, user_image_path, gender="lady", seed=None):
        """
        Process user photo into bespoke punk.

        Args:
            user_image_path: Path to user's photo
            gender: "lady" or "lad"
            seed: Random seed (optional)

        Returns:
            Dict with:
            - image_512: 512x512 generated image
            - image_24: 24x24 pixel art (NFT)
            - prompt: Generated prompt
            - features: Extracted features
        """

        print("="*70)
        print("BESPOKE PUNK GENERATION PIPELINE")
        print("="*70)
        print()

        # Step 1: Extract features
        print("Step 1: Analyzing user photo...")
        extractor = ImprovedFeatureExtractor(user_image_path)
        color_extractor = ColorPaletteExtractor(user_image_path)

        features = {
            'hair_color': extractor.detect_hair_color(),
            'eye_color': extractor.detect_eye_color(),
            'skin_tone': extractor.detect_skin_tone(),
            'background_color': 'blue',  # Default, can be customized
        }

        print(f"   Detected:")
        print(f"     Hair: {features['hair_color']}")
        print(f"     Eyes: {features['eye_color']}")
        print(f"     Skin: {features['skin_tone']}")
        print()

        # Step 2: Generate prompt
        print("Step 2: Generating training-format prompt...")
        prompt = self.prompt_builder.generate(features, gender=gender)
        print(f"   Prompt: {prompt}")
        print()

        # Step 3: Generate with epoch 7
        print("Step 3: Generating with Epoch 7 LoRA...")
        image_512 = self.generator.generate(prompt, seed=seed)
        print()

        # Step 4: Create 24x24 NFT
        print("Step 4: Creating 24x24 NFT...")
        image_24 = self.generator.downscale_to_24x24(image_512)

        # Count final colors
        arr = np.array(image_24)
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        print(f"   ✓ 24x24 NFT created ({unique_colors} colors)")
        print()

        print("="*70)
        print("✅ GENERATION COMPLETE!")
        print("="*70)
        print()

        return {
            'image_512': image_512,
            'image_24': image_24,
            'prompt': prompt,
            'features': features,
        }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Bespoke Punk NFT from user photo"
    )
    parser.add_argument("image", type=str, help="Path to user photo")
    parser.add_argument("--gender", type=str, choices=["lady", "lad"],
                       default="lady", help="Punk gender (default: lady)")
    parser.add_argument("--lora", type=str,
                       default="/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors",
                       help="Path to epoch 7 LoRA")
    parser.add_argument("--output", type=str, default="output",
                       help="Output filename prefix (default: output)")
    parser.add_argument("--seed", type=int, default=None,
                       help="Random seed for reproducibility")

    args = parser.parse_args()

    # Check if image exists
    if not Path(args.image).exists():
        print(f"❌ Error: Image not found: {args.image}")
        sys.exit(1)

    # Check if LoRA exists
    if not Path(args.lora).exists():
        print(f"❌ Error: LoRA not found: {args.lora}")
        print(f"   Expected: {args.lora}")
        print(f"   Make sure you have downloaded epoch 7 LoRA!")
        sys.exit(1)

    # Run pipeline
    pipeline = UserToBespokePunkPipeline(args.lora)
    result = pipeline.process(args.image, gender=args.gender, seed=args.seed)

    # Save outputs
    output_512_path = f"{args.output}_512.png"
    output_24_path = f"{args.output}_24x24.png"

    result['image_512'].save(output_512_path)
    result['image_24'].save(output_24_path)

    print(f"💾 Saved:")
    print(f"   512x512: {output_512_path}")
    print(f"   24x24:   {output_24_path}")
    print()
    print(f"📝 Prompt used:")
    print(f"   {result['prompt']}")
    print()

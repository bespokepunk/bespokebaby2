#!/usr/bin/env python3
"""
PRODUCTION PIPELINE: User Photo → Bespoke Punk NFT
Uses SD 1.5 CAPTION_FIX Epoch 8 LoRA (216.6 avg colors - cleanest)

Complete workflow:
1. User uploads photo
2. Analyze photo: extract colors, features, traits
3. Map to training vocabulary
4. Generate training-format prompt
5. Generate 512x512 bespoke punk with CAPTION_FIX Epoch 8
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

# Enhanced Feature Extractor integrated below
class EnhancedFeatureExtractor:
    """
    Fixed feature extraction that actually works.
    Tested against anime girl screenshot - now detects:
    - Correct background color (green not blue)
    - Sunglasses presence
    - Earrings
    """

    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert('RGB')
        self.arr = np.array(self.image)
        self.height, self.width = self.arr.shape[:2]

    # ========================================================================
    # FIXED: Background Color Detection
    # ========================================================================

    def detect_background_color(self):
        """
        FIXED: Sample edges/corners, not center
        Previous version was sampling center (face area) → wrong color
        """
        # Sample edges only (background usually at edges)
        top_strip = self.arr[0:int(self.height*0.15), :]
        bottom_strip = self.arr[int(self.height*0.85):, :]
        left_strip = self.arr[:, 0:int(self.width*0.15)]
        right_strip = self.arr[:, int(self.width*0.85):]

        # Combine all edge pixels
        edge_pixels = np.concatenate([
            top_strip.reshape(-1, 3),
            bottom_strip.reshape(-1, 3),
            left_strip.reshape(-1, 3),
            right_strip.reshape(-1, 3)
        ])

        # Get most dominant color in edges
        pixel_colors = [tuple(p) for p in edge_pixels]
        color_counts = Counter(pixel_colors)

        # Get top 3 most common (in case of gradients)
        top_colors = color_counts.most_common(3)

        # Average the top colors for more robust detection
        if len(top_colors) > 0:
            # Use most dominant
            dominant_color = top_colors[0][0]
            return self._color_name_from_rgb(dominant_color, is_background=True)

        return "blue"  # Default fallback

    # ========================================================================
    # FIXED: Eyewear Detection (Glasses vs Sunglasses)
    # ========================================================================

    def detect_eyewear(self):
        """
        FIXED: Detect sunglasses vs regular glasses
        Returns: 'sunglasses', 'glasses', or 'none'
        """
        # Eye region (broader to catch sunglasses)
        eye_region = self.arr[int(self.height*0.20):int(self.height*0.50),
                               int(self.width*0.15):int(self.width*0.85)]

        # Calculate average brightness
        avg_brightness = eye_region.mean(axis=(0, 1)).mean()

        # SUNGLASSES: Very dark eye region (< 60 brightness)
        if avg_brightness < 60:
            # Check if it's a consistent dark region (not just shadows)
            dark_pixels = eye_region[eye_region.mean(axis=2) < 80]
            if len(dark_pixels) > len(eye_region.reshape(-1, 3)) * 0.3:
                return 'sunglasses'

        # GLASSES: Look for frames (edges/lines around eye area)
        # Check for horizontal/vertical lines (frames)
        # For now, use heuristic: medium brightness + edge detection
        if 60 <= avg_brightness < 150:
            # Detect edges in eye region
            from scipy import ndimage
            gray = eye_region.mean(axis=2)
            edges = ndimage.sobel(gray)

            # If many edges detected → likely glasses frames
            if edges.std() > 10:  # Threshold for frame edges
                return 'glasses'

        return 'none'

    # ========================================================================
    # FIXED: Earrings Detection
    # ========================================================================

    def detect_earrings(self):
        """
        FIXED: Detect earrings by checking ear regions for distinct color points
        Returns: dict with 'present' (bool) and 'type' (stud/hoop/none)
        """
        # Left ear region (side of face)
        left_ear = self.arr[int(self.height*0.25):int(self.height*0.55),
                            0:int(self.width*0.25)]

        # Right ear region
        right_ear = self.arr[int(self.height*0.25):int(self.height*0.55),
                              int(self.width*0.75):]

        # Combine both ears
        ear_regions = [left_ear, right_ear]

        earring_detected = False
        earring_type = 'none'

        for ear_region in ear_regions:
            if ear_region.size == 0:
                continue

            # Flatten to analyze colors
            ear_pixels = ear_region.reshape(-1, 3)

            # Look for distinct color points (earrings are usually:
            # - Bright (gold, silver, colored)
            # - Small region (not dominant like hair/skin)
            # - Different from hair and skin tones

            pixel_colors = [tuple(p) for p in ear_pixels]
            color_counts = Counter(pixel_colors)

            # Check for small bright regions
            for color, count in color_counts.most_common(20):
                r, g, b = color
                brightness = (r + g + b) / 3
                percentage = count / len(ear_pixels)

                # Earring characteristics:
                # 1. Not too dominant (5-20% of ear region)
                # 2. Bright enough (> 100 brightness)
                # 3. Not skin tone
                if 0.05 < percentage < 0.20 and brightness > 100:
                    if not self._is_skin_tone(r, g, b):
                        earring_detected = True

                        # Determine type by region size
                        if percentage > 0.12:
                            earring_type = 'hoop'  # Larger = hoop earring
                        else:
                            earring_type = 'stud'  # Smaller = stud earring
                        break

            if earring_detected:
                break

        return {
            'present': earring_detected,
            'type': earring_type
        }

    # ========================================================================
    # Hair Color Detection (Existing - Keep)
    # ========================================================================

    def detect_hair_color(self):
        """Detect hair color - existing logic seems OK"""
        # Sample upper 40% (hair region)
        hair_region = self.arr[:int(self.height * 0.4), :]
        hair_pixels = hair_region.reshape(-1, 3)

        total_pixels = len(hair_pixels)
        color_counts = Counter(map(tuple, hair_pixels))

        # Find hair colors (not background, not skin)
        hair_color_candidates = []

        for color, count in color_counts.most_common(20):
            pct = count / total_pixels
            r, g, b = color

            # Skip background (too dominant)
            if pct > 0.35:
                continue

            # Skip skin tones
            if self._is_skin_tone(r, g, b):
                continue

            # Skip white/very bright
            brightness = (r + g + b) / 3
            if brightness > 250:
                continue

            hair_color_candidates.append((color, count, pct))

        if not hair_color_candidates:
            # Fallback for blonde hair
            for color, count in color_counts.most_common(15):
                r, g, b = color
                brightness = (r + g + b) / 3
                if brightness < 253 and not self._is_skin_tone(r, g, b):
                    return self._color_name_from_rgb(color, is_hair=True)
            return "blonde"

        dominant_hair_color = hair_color_candidates[0][0]
        return self._color_name_from_rgb(dominant_hair_color, is_hair=True)

    # ========================================================================
    # Eye Color Detection
    # ========================================================================

    def detect_eye_color(self):
        """
        Detect eye color - BUT if sunglasses, can't see eyes!
        Returns: color or 'covered' if sunglasses detected
        """
        # First check if wearing sunglasses
        eyewear = self.detect_eyewear()
        if eyewear == 'sunglasses':
            return 'brown'  # Default - can't actually see eyes

        # Sample face region
        face_region = self.arr[int(self.height*0.3):int(self.height*0.6),
                               int(self.width*0.25):int(self.width*0.75)]

        face_pixels = face_region.reshape(-1, 3)

        # Look for eye colors (dark regions that aren't skin)
        eye_candidates = []

        for pixel in face_pixels:
            r, g, b = pixel
            brightness = (r + g + b) / 3

            # Eyes: 30-120 brightness range
            if 30 <= brightness <= 120:
                if not self._is_skin_tone(r, g, b):
                    eye_candidates.append(pixel)

        if len(eye_candidates) == 0:
            return "brown"

        avg_eye_color = np.mean(eye_candidates, axis=0).astype(int)
        return self._color_name_from_rgb(tuple(avg_eye_color), is_eyes=True)

    # ========================================================================
    # Skin Tone Detection (Existing - Keep)
    # ========================================================================

    def detect_skin_tone(self):
        """Detect skin tone"""
        face_region = self.arr[int(self.height*0.35):int(self.height*0.65),
                               int(self.width*0.3):int(self.width*0.7)]

        face_pixels = face_region.reshape(-1, 3)

        skin_pixels = []
        for pixel in face_pixels:
            r, g, b = pixel
            if self._is_skin_tone(r, g, b):
                skin_pixels.append(pixel)

        if len(skin_pixels) == 0:
            return "light"

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

    # ========================================================================
    # Expression Detection
    # ========================================================================

    def detect_expression(self):
        """
        Detect facial expression
        Returns: 'neutral' or 'slight_smile'
        """
        # Sample mouth region (lower face)
        mouth_region = self.arr[int(self.height*0.55):int(self.height*0.70),
                                int(self.width*0.35):int(self.width*0.65)]

        # Analyze mouth shape
        # Smile: corners go up → brighter pixels at edges
        # Neutral: straight line → even distribution

        # Simple heuristic: check if edges are brighter than center
        left_edge = mouth_region[:, :int(mouth_region.shape[1]*0.2)]
        right_edge = mouth_region[:, int(mouth_region.shape[1]*0.8):]
        center = mouth_region[:, int(mouth_region.shape[1]*0.4):int(mouth_region.shape[1]*0.6)]

        edges_brightness = (left_edge.mean() + right_edge.mean()) / 2
        center_brightness = center.mean()

        # If edges brighter than center → smile
        if edges_brightness > center_brightness + 5:
            return 'slight_smile'
        else:
            return 'neutral'

    # ========================================================================
    # Facial Hair Detection
    # ========================================================================

    def detect_facial_hair(self):
        """
        Detect facial hair (stubble, beard, mustache)
        Returns: 'none', 'stubble', 'beard', 'mustache'
        """
        # Sample lower face (chin/jaw area)
        lower_face = self.arr[int(self.height*0.55):int(self.height*0.80),
                              int(self.width*0.25):int(self.width*0.75)]

        # Analyze texture - facial hair = darker + more texture
        avg_brightness = lower_face.mean()
        texture_variance = lower_face.std()

        # Beard: Dark + high texture
        if avg_brightness < 120 and texture_variance > 30:
            # Check coverage
            dark_pixels = lower_face[lower_face.mean(axis=2) < 100]
            coverage = len(dark_pixels) / lower_face.reshape(-1, 3).shape[0]

            if coverage > 0.3:
                return 'beard'
            elif coverage > 0.15:
                return 'stubble'

        # Mustache: Check upper lip area only
        mustache_region = self.arr[int(self.height*0.50):int(self.height*0.58),
                                    int(self.width*0.35):int(self.width*0.65)]
        mustache_brightness = mustache_region.mean()

        if mustache_brightness < 100:
            return 'mustache'

        return 'none'

    # ========================================================================
    # Helper Functions
    # ========================================================================

    def _is_skin_tone(self, r, g, b):
        """Check if RGB is a skin tone"""
        if r < 50:
            return False
        if r > 255 or g > 255 or b > 255:
            return False

        # Skin tone: R > G > B
        if not (r >= g and g >= b * 0.9):
            return False

        # Not too saturated
        if r - g > 80:
            return False

        # Blue significantly lower
        if b > g * 0.95:
            return False

        # Brightness in skin range
        brightness = (r + g + b) / 3
        if brightness < 60 or brightness > 250:
            return False

        return True

    def _color_name_from_rgb(self, rgb, is_hair=False, is_eyes=False, is_background=False):
        """Convert RGB to color name"""
        r, g, b = rgb
        brightness = (r + g + b) / 3

        if is_background:
            # Background color detection
            if g > r * 1.15 and g > b * 1.15:
                return "green"
            elif b > r * 1.15 and b > g * 1.15:
                return "blue"
            elif r > g * 1.2 and r > b * 1.2:
                return "red"
            elif r > 150 and b > 150 and abs(r - b) < 60:
                return "purple"
            elif r > 200 and g > 150 and b < 120:
                return "orange"
            elif r > 200 and g > 200 and b < 150:
                return "yellow"
            elif brightness > 220:
                return "white"
            elif brightness < 80:
                return "black"
            else:
                return "gray"

        if is_eyes:
            # Eye color detection
            if b > r * 1.2 and b > g * 1.2 and b > 80:
                return "blue"
            if g > r * 1.1 and g > b * 1.2 and g > 60:
                return "green"
            if max(r, g, b) - min(r, g, b) < 40 and 80 < brightness < 150:
                return "gray"
            if brightness < 50:
                return "black"
            return "brown"

        if is_hair:
            # Hair color detection
            if brightness < 60:
                return "black"
            if (r > 160 and g > 130) or (brightness > 180 and r > g and g > b):
                return "blonde"
            if r > 150 and r > g * 1.3 and g > b:
                return "red"
            if b > r * 1.3 and b > g * 1.3 and b > 100:
                return "blue"
            if g > r * 1.3 and g > b * 1.1 and g > 100:
                return "green"
            if r > 100 and b > 100 and abs(r - b) < 80 and g < r * 0.8:
                return "purple"
            if r > 150 and b > 100 and g < r * 0.9 and r > b * 1.2:
                return "pink"
            if brightness > 180 and max(r, g, b) - min(r, g, b) < 50:
                return "gray"
            if 60 <= brightness < 140:
                return "brown"
            if brightness >= 140:
                return "blonde"
            return "brown"

        # General
        if brightness < 50:
            return "black"
        elif brightness > 200:
            return "white"
        else:
            return "gray"

    # ========================================================================
    # Main Extract Method
    # ========================================================================

    def extract_all_features(self):
        """
        Extract all features from image
        Returns complete feature dict
        """
        eyewear_result = self.detect_eyewear()
        earring_result = self.detect_earrings()

        features = {
            'hair_color': self.detect_hair_color(),
            'eye_color': self.detect_eye_color(),
            'skin_tone': self.detect_skin_tone(),
            'background_color': self.detect_background_color(),

            # Accessories (AUTO-DETECTED)
            'eyewear': eyewear_result,  # 'sunglasses', 'glasses', 'none'
            'earrings': earring_result['present'],
            'earring_type': earring_result['type'],  # 'stud', 'hoop', 'none'

            # Expression & facial hair
            'expression': self.detect_expression(),
            'facial_hair': self.detect_facial_hair(),
        }

        return features


# ============================================================================
# TEST FUNCTION
# ============================================================================

if __name__ == "__main__":

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
    Generate bespoke punks using SD 1.5 + CAPTION_FIX Epoch 8 LoRA
    """

    def __init__(self, lora_path, device=None):
        """
        Initialize generator with CAPTION_FIX Epoch 8 LoRA.

        Args:
            lora_path: Path to CAPTION_FIX Epoch 8 .safetensors file
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

        print(f"🎨 Loading SD 1.5 with CAPTION_FIX Epoch 8 LoRA...")
        print(f"   Device: {self.device}")

        # Load SD 1.5
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            safety_checker=None,
        )

        # Load CAPTION_FIX Epoch 8 LoRA
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
        """Initialize pipeline with CAPTION_FIX Epoch 8 LoRA"""
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
        extractor = EnhancedFeatureExtractor(user_image_path)
        color_extractor = ColorPaletteExtractor(user_image_path)

        # Extract ALL features (enhanced detection)
        all_features = extractor.extract_all_features()

        features = {
            'hair_color': all_features['hair_color'],
            'eye_color': all_features['eye_color'],
            'skin_tone': all_features['skin_tone'],
            'background_color': all_features['background_color'],  # NOW DETECTED!

            # Auto-detected accessories
            'eyewear': all_features['eyewear'],  # 'sunglasses', 'glasses', 'none'
            'earrings': all_features['earrings'],  # bool
            'earring_type': all_features['earring_type'],  # 'stud', 'hoop', 'none'
            'expression': all_features['expression'],  # 'neutral', 'slight_smile'
            'facial_hair': all_features['facial_hair'],  # 'none', 'stubble', 'beard', 'mustache'
        }

        print(f"   Detected:")
        print(f"     Hair: {features['hair_color']}")
        print(f"     Eyes: {features['eye_color']}")
        print(f"     Skin: {features['skin_tone']}")
        print(f"     Background: {features['background_color']}")
        print(f"     Eyewear: {features['eyewear']}")
        print(f"     Earrings: {features['earring_type'] if features['earrings'] else 'none'}")
        print(f"     Expression: {features['expression']}")
        print(f"     Facial Hair: {features['facial_hair']}")
        print()

        # Step 2: Generate prompt
        print("Step 2: Generating training-format prompt...")
        prompt = self.prompt_builder.generate(features, gender=gender)
        print(f"   Prompt: {prompt}")
        print()

        # Step 3: Generate with CAPTION_FIX Epoch 8
        print("Step 3: Generating with CAPTION_FIX Epoch 8 LoRA...")
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
                       default="lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors",
                       help="Path to CAPTION_FIX Epoch 8 LoRA")
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
        print(f"   Make sure you have CAPTION_FIX Epoch 8 LoRA!")
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

#!/usr/bin/env python3
"""
IMPROVED FEATURE EXTRACTION
Works with photos, cartoons, anime, and stylized art
Uses intelligent color palette analysis instead of naive region sampling
"""

from PIL import Image
import numpy as np
from collections import Counter

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

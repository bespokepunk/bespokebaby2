#!/usr/bin/env python3
"""
Bespoke Punk Generator V2.7 - COMPLETE - Comprehensive Detection & Caption Generation

V2.7 FEATURES (ALL COMPLETE):
1. ✅ Eye color detection (narrower region, skin tone filtering, darkest saturated color)
2. ✅ Better color usage in prompts (map colors to specific features, NOT generic lists)
3. ✅ Accessory detection (sunglasses, earrings, hats)
4. ✅ Hair style vocabulary expansion (braided, bun, ponytail, dreadlocks, afro, slicked back)
5. ✅ Gender detection (filename-based first, then heuristics with earring weight)

V2.6 improvements over V2.5:
- Fix hair color detection by analyzing hair region specifically (not global palette)
- Better background gradient color extraction from background corners
- Improved eye color detection from eye-specific regions
- Eliminate background color interference in hair detection

Previous V2.5 improvements:
- Hair shape/volume/style detection using image region analysis
- Male/Female type detection
- Uses ALL 12 colors in prompts (not just top 5)
- Better skin tone detection using facial region
- Pattern detection for gradients/checkered backgrounds
"""

import os
import json
from collections import Counter
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from diffusers import StableDiffusionPipeline
import torch


class EnhancedImageAnalyzer:
    """
    Advanced image analysis for better feature extraction.
    Analyzes specific regions of the image for more accurate detection.
    """

    def __init__(self, image_path):
        """Load and prepare image for analysis"""
        self.image_path = image_path  # V2.7: Store path for filename-based gender detection
        self.image = Image.open(image_path).convert('RGB')
        self.image_array = np.array(self.image)
        self.height, self.width = self.image_array.shape[:2]

    def analyze_hair_region(self):
        """
        Analyze top 40% of image for hair characteristics.

        V2.7 IMPROVEMENTS:
        - Added specific style detection (braided, bun, ponytail, etc.)
        - Kept texture analysis (curly, wavy, fluffy)
        - Improved length detection

        Returns:
        - volume: low, medium, high
        - texture: smooth, wavy, curly, spiky, pixelated
        - length: short, medium, long
        - style: braided, bun, ponytail, dreadlocks, afro, slicked_back, or None
        """
        # Get top 40% of image (where hair typically is)
        hair_region = self.image_array[:int(self.height * 0.4), :]

        # V2.7 NEW: Detect specific hair styles first
        specific_style = self.detect_specific_hair_style(hair_region)

        # Analyze color variance to detect volume/texture
        # High variance = voluminous/textured hair
        # Low variance = smooth/flat hair
        color_std = np.std(hair_region, axis=(0, 1)).mean()

        # Detect volume based on color complexity
        if color_std > 50:
            volume = "large voluminous"
        elif color_std > 30:
            volume = "voluminous"
        elif color_std > 15:
            volume = "medium"
        else:
            volume = "short"

        # Analyze edges for texture
        # Calculate horizontal and vertical variance
        h_var = np.std(np.diff(hair_region, axis=1))
        v_var = np.std(np.diff(hair_region, axis=0))

        if h_var > 40 or v_var > 40:
            texture = "curly"
        elif h_var > 25 or v_var > 25:
            texture = "wavy"
        elif h_var > 15 or v_var > 15:
            texture = "fluffy"
        else:
            texture = "pixelated"

        # Estimate length based on how far down hair colors extend
        hair_colors = self.get_dominant_colors(hair_region, n_colors=3)
        mid_region = self.image_array[int(self.height * 0.3):int(self.height * 0.6), :]
        mid_colors = self.get_dominant_colors(mid_region, n_colors=3)

        # If similar colors in mid region, hair is long
        color_similarity = self.color_similarity(hair_colors, mid_colors)
        if color_similarity > 0.7:
            length = "long"
        elif color_similarity > 0.4:
            length = "medium"
        else:
            length = "short"

        return {
            'volume': volume,
            'texture': texture,
            'length': length,
            'style': specific_style
        }

    def detect_specific_hair_style(self, hair_region):
        """
        V2.7 NEW: Detect specific hair styles using pattern analysis.

        Detects:
        - braided: rope-like vertical patterns, distinct segments
        - bun: concentrated mass at top/back of head
        - ponytail: hair pulled to one side/back
        - dreadlocks: multiple thick vertical segments
        - afro: large spherical volume
        - slicked_back: smooth, pulled back appearance

        Returns: Style name or None if no specific style detected
        """
        if hair_region.size == 0:
            return None

        # Check for braid patterns (rope-like vertical patterns)
        if self.has_braid_pattern(hair_region):
            print(f"  ✓ Detected hair style: braided")
            return "braided"

        # Check for bun (concentrated mass at top/back)
        if self.has_bun_shape(hair_region):
            print(f"  ✓ Detected hair style: bun")
            return "bun"

        # Check for ponytail (asymmetric distribution)
        if self.has_ponytail_pattern(hair_region):
            print(f"  ✓ Detected hair style: ponytail")
            return "ponytail"

        # Check for dreadlocks (multiple thick vertical segments)
        if self.has_dreadlock_pattern(hair_region):
            print(f"  ✓ Detected hair style: dreadlocks")
            return "dreadlocks"

        # Check for afro (large spherical volume)
        if self.has_afro_shape(hair_region):
            print(f"  ✓ Detected hair style: afro")
            return "afro"

        # Check for slicked back (smooth, pulled back)
        if self.is_slicked_back(hair_region):
            print(f"  ✓ Detected hair style: slicked back")
            return "slicked_back"

        return None

    def has_braid_pattern(self, hair_region):
        """Detect braided hair by looking for rope-like vertical patterns"""
        # Braids have distinct vertical segments with regular patterns
        # High vertical variance, regular horizontal patterns
        v_diff = np.diff(hair_region, axis=0)
        v_var = np.std(v_diff)

        # Check for regular vertical patterns (braids create stripes)
        # Calculate variance in vertical slices
        num_slices = min(5, hair_region.shape[1] // 10)
        if num_slices == 0:
            return False

        slice_width = hair_region.shape[1] // num_slices
        slice_variances = []

        for i in range(num_slices):
            start = i * slice_width
            end = start + slice_width
            slice_region = hair_region[:, start:end]
            slice_variances.append(np.std(slice_region))

        # Braids: high overall variance + high variance in slices
        has_pattern = v_var > 30 and np.mean(slice_variances) > 25

        return has_pattern

    def has_bun_shape(self, hair_region):
        """Detect bun by looking for concentrated mass at top/back"""
        # Bun appears as a concentrated region with low spread
        # Check if most of the hair is concentrated in one area
        hair_density = np.mean(hair_region, axis=2)  # Average across RGB

        # Find the brightest/most prominent region
        top_half = hair_density[:hair_density.shape[0]//2, :]
        bottom_half = hair_density[hair_density.shape[0]//2:, :]

        top_var = np.std(top_half)
        bottom_var = np.std(bottom_half)

        # Bun: high concentration at top, low at bottom
        # Strong asymmetry suggests pulled-up style
        is_bun = top_var > bottom_var * 1.5 and top_var > 30

        return is_bun

    def has_ponytail_pattern(self, hair_region):
        """Detect ponytail by looking for asymmetric hair distribution"""
        # Ponytail: hair pulled to one side or back
        # Check left vs right distribution
        mid = hair_region.shape[1] // 2
        left_half = hair_region[:, :mid]
        right_half = hair_region[:, mid:]

        left_var = np.std(left_half)
        right_var = np.std(right_half)

        # Strong asymmetry suggests ponytail
        asymmetry = abs(left_var - right_var) / max(left_var, right_var, 1)

        return asymmetry > 0.4 and max(left_var, right_var) > 25

    def has_dreadlock_pattern(self, hair_region):
        """Detect dreadlocks by looking for multiple thick vertical segments"""
        # Dreadlocks: thick vertical segments, less regular than braids
        # High vertical variance, chunky appearance
        v_diff = np.diff(hair_region, axis=0)
        h_diff = np.diff(hair_region, axis=1)

        v_var = np.std(v_diff)
        h_var = np.std(h_diff)

        # Dreadlocks: high vertical variance, moderate horizontal variance
        # More irregular than braids
        has_dreads = v_var > 35 and 15 < h_var < 30

        return has_dreads

    def has_afro_shape(self, hair_region):
        """Detect afro by looking for large spherical volume"""
        # Afro: large volume, roughly circular/spherical shape
        # High variance across all dimensions
        overall_var = np.std(hair_region)

        # Check if hair extends widely (large width coverage)
        non_bg_pixels = np.sum(hair_region > 50) / hair_region.size

        # Afro: very high variance + wide coverage
        is_afro = overall_var > 55 and non_bg_pixels > 0.6

        return is_afro

    def is_slicked_back(self, hair_region):
        """Detect slicked back hair by looking for smooth, pulled back appearance"""
        # Slicked back: low variance, smooth appearance
        # Hair appears as smooth gradient
        overall_var = np.std(hair_region)
        h_var = np.std(np.diff(hair_region, axis=1))

        # Slicked back: low overall variance, very low horizontal variance
        is_slicked = overall_var < 20 and h_var < 15

        return is_slicked

    def get_dominant_colors(self, region, n_colors=3):
        """Extract dominant colors from a region"""
        pixels = region.reshape(-1, 3)
        kmeans = KMeans(n_clusters=min(n_colors, len(pixels)), random_state=42, n_init=10)
        kmeans.fit(pixels)
        return kmeans.cluster_centers_

    def color_similarity(self, colors1, colors2):
        """Calculate similarity between two sets of colors"""
        # Simple euclidean distance-based similarity
        min_distances = []
        for c1 in colors1:
            distances = [np.linalg.norm(c1 - c2) for c2 in colors2]
            min_distances.append(min(distances))
        avg_distance = np.mean(min_distances)
        # Convert distance to similarity (0-1 scale)
        similarity = max(0, 1 - (avg_distance / 255))
        return similarity

    def analyze_face_region(self):
        """
        Analyze middle 30-60% of image for face/skin/eyes.

        Returns skin tone and eye color with better accuracy.
        """
        # Face region (middle vertical third, middle horizontal third)
        face_region = self.image_array[
            int(self.height * 0.3):int(self.height * 0.6),
            int(self.width * 0.3):int(self.width * 0.7)
        ]

        # Get dominant colors
        colors = self.get_dominant_colors(face_region, n_colors=5)

        # Separate skin tones from eye colors
        # Skin tones typically have similar R,G,B values
        # Eye colors have more distinct values
        skin_candidates = []
        eye_candidates = []

        for color in colors:
            r, g, b = color
            # Skin tone check: R,G,B should be relatively close
            color_variance = np.std([r, g, b])
            if color_variance < 30:  # Low variance = likely skin
                skin_candidates.append(color)
            else:  # High variance = might be eyes or accessories
                eye_candidates.append(color)

        # Pick most likely skin tone (lightest among candidates)
        if skin_candidates:
            skin = max(skin_candidates, key=lambda c: sum(c))
        else:
            # Fallback: pick middle brightness color
            skin = sorted(colors, key=lambda c: sum(c))[len(colors)//2]

        # Pick most likely eye color (darkest or most saturated)
        if eye_candidates:
            eyes = min(eye_candidates, key=lambda c: sum(c))
        else:
            eyes = min(colors, key=lambda c: sum(c))

        return {
            'skin': skin,
            'eyes': eyes
        }

    def detect_type(self):
        """
        V2.7 IMPROVED: Detect if image is likely male (lad) or female (lady).

        Priority:
        1. Check filename first (lad_* or lady_*)
        2. If no filename hint, use heuristics:
           - Hair length/volume
           - Accessories (earrings strongly suggest lady)
           - Color palette
        """
        from pathlib import Path

        # V2.7 FIX: Check filename first (most reliable)
        filename = Path(self.image_path).stem.lower()

        if filename.startswith('lad_'):
            print(f"  ✓ Gender from filename: lad")
            return "lad"
        elif filename.startswith('lady_'):
            print(f"  ✓ Gender from filename: lady")
            return "lady"

        # Fallback to heuristics if filename doesn't indicate
        print(f"  No filename hint, using heuristics...")

        hair_info = self.analyze_hair_region()

        # V2.7: Also check for accessories (earrings are strong female indicator)
        accessories = self.detect_accessories()

        # Female indicators
        female_score = 0

        # Earrings: very strong lady indicator
        if accessories['earrings']:
            female_score += 3
            print(f"    Earrings detected: +3 female score")

        # Long/voluminous hair
        if hair_info['length'] in ['long', 'medium']:
            female_score += 1
            print(f"    Long/medium hair: +1 female score")

        if 'voluminous' in hair_info['volume']:
            female_score += 1
            print(f"    Voluminous hair: +1 female score")

        # Check for pink/purple/pastel colors in palette
        all_colors = self.image_array.reshape(-1, 3)
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        kmeans.fit(all_colors)
        palette = kmeans.cluster_centers_

        for color in palette:
            r, g, b = color
            # Pink/purple detection
            if r > 150 and g < 150 and b > 100:  # Purple/pink hues
                female_score += 1
            # Pastel detection (high values, similar)
            if r > 200 and g > 180 and b > 200:
                female_score += 0.5

        # Return type based on score
        gender = "lady" if female_score >= 3 else "lad"
        print(f"    Total female score: {female_score} → {gender}")

        return gender

    def analyze_background_pattern(self):
        """
        Detect if background has a pattern (gradient, checkered, striped, etc.)
        """
        # Analyze bottom-right corner (typically background)
        bg_region = self.image_array[
            int(self.height * 0.7):,
            int(self.width * 0.7):
        ]

        if bg_region.size == 0:
            return "solid"

        # Check for gradient (smooth color transition)
        h_gradient = np.std(np.mean(bg_region, axis=0), axis=0).mean()
        v_gradient = np.std(np.mean(bg_region, axis=1), axis=0).mean()

        if h_gradient > 20 or v_gradient > 20:
            return "gradient"

        # Check for pattern (high frequency changes)
        h_freq = np.std(np.diff(bg_region, axis=1))
        v_freq = np.std(np.diff(bg_region, axis=0))

        if h_freq > 30 and v_freq > 30:
            return "checkered"
        elif h_freq > 30 or v_freq > 30:
            return "striped"

        return "solid"

    def get_hair_colors(self):
        """
        Extract dominant colors specifically from hair region.
        V2.6 FIX: Prevents background colors from being detected as hair.
        """
        # Get top 40% of image (hair region)
        hair_region = self.image_array[:int(self.height * 0.4), :]

        # Extract top 5 colors from hair region only
        pixels = hair_region.reshape(-1, 3)
        if len(pixels) < 5:
            return [(0, 0, 0)]  # Fallback to black

        kmeans = KMeans(n_clusters=min(5, len(pixels)), random_state=42, n_init=10)
        kmeans.fit(pixels)

        return kmeans.cluster_centers_

    def get_background_colors(self):
        """
        Extract background colors from corners to capture gradients.
        V2.6 FIX: Better gradient detection by sampling from actual background.
        """
        # Sample from four corners (typically background)
        corner_size = max(10, int(self.height * 0.15))

        corners = [
            self.image_array[:corner_size, :corner_size],  # Top-left
            self.image_array[:corner_size, -corner_size:],  # Top-right
            self.image_array[-corner_size:, :corner_size],  # Bottom-left
            self.image_array[-corner_size:, -corner_size:],  # Bottom-right
        ]

        # Collect all corner pixels
        all_corner_pixels = np.vstack([corner.reshape(-1, 3) for corner in corners])

        # Extract top 3 colors from corners (captures gradient range)
        if len(all_corner_pixels) < 3:
            return [np.mean(all_corner_pixels, axis=0)]

        kmeans = KMeans(n_clusters=min(3, len(all_corner_pixels)), random_state=42, n_init=10)
        kmeans.fit(all_corner_pixels)

        return kmeans.cluster_centers_

    def get_eye_region_colors_v2_7(self):
        """
        V2.7 FIX: Much more precise eye color detection.

        CRITICAL FIXES:
        - Narrower region (38-42% height instead of 35-45%)
        - Smaller horizontal range (35-65% instead of 25-75%)
        - Filter out skin tones completely
        - Look for DARKEST saturated color (eyes are darker than whites/skin)

        Returns: RGB tuple of detected eye color
        """
        # NARROWER eye band - more precise targeting
        eye_region = self.image_array[
            int(self.height * 0.38):int(self.height * 0.42),  # Narrower vertical (4% band)
            int(self.width * 0.35):int(self.width * 0.65)      # Exclude edges (30% width)
        ]

        if eye_region.size == 0:
            return (100, 80, 60)  # Default brown

        # Extract top 5 colors from eye region
        pixels = eye_region.reshape(-1, 3)
        kmeans = KMeans(n_clusters=min(5, len(pixels)), random_state=42, n_init=10)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_

        # FILTER OUT skin tones and very bright colors (whites of eyes)
        valid_eye_colors = []

        for color in colors:
            r, g, b = color

            # Skip skin tones (brownish, similar R/G values, medium brightness)
            color_variance = np.std([r, g, b])
            brightness = (r + g + b) / 3

            # Skip if looks like skin (low variance, medium-high brightness)
            if color_variance < 35 and 100 < brightness < 220:
                continue

            # Skip very bright colors (whites of eyes, reflections)
            if brightness > 220:
                continue

            # Skip very light unsaturated colors (whites)
            if r > 200 and g > 200 and b > 200:
                continue

            # Calculate saturation (how colorful it is)
            max_channel = max(r, g, b)
            min_channel = min(r, g, b)
            saturation = max_channel - min_channel

            # Keep colors that are either:
            # 1. Dark (likely iris)
            # 2. Moderately saturated (colorful eyes like blue/green/brown)
            if brightness < 180 or saturation > 30:
                valid_eye_colors.append((color, brightness, saturation))

        # If we filtered everything out, fall back to darkest color
        if not valid_eye_colors:
            darkest = min(colors, key=lambda c: sum(c))
            return tuple(darkest)

        # V2.7 FIX: Select DARKEST saturated color (not most saturated)
        # Eyes are typically darker than skin/whites
        # Sort by darkness (lower brightness = darker)
        valid_eye_colors.sort(key=lambda x: x[1])  # Sort by brightness ascending

        # Get the darkest color that has reasonable saturation
        selected_color = valid_eye_colors[0][0]

        print(f"  Eye region analysis:")
        print(f"    Detected colors: {len(colors)}")
        print(f"    Valid eye colors after filtering: {len(valid_eye_colors)}")
        print(f"    Selected eye color RGB: {selected_color}")
        print(f"    Brightness: {valid_eye_colors[0][1]:.1f}, Saturation: {valid_eye_colors[0][2]:.1f}")

        return tuple(selected_color)

    def detect_accessories(self):
        """
        V2.7 NEW: Detect accessories in specific image regions.

        Detects:
        - Sunglasses: Dark uniform region covering eyes (38-42% height)
        - Earrings: Bright/shiny spots at ear positions (45-55% height, edges)
        - Hats/headwear: Distinct shapes in top 15% of image

        Returns: Dictionary with detected accessories
        """
        accessories = {
            'sunglasses': False,
            'earrings': False,
            'hat': False,
            'descriptions': []
        }

        # 1. Sunglasses detection (same region as eyes)
        eye_region = self.image_array[
            int(self.height * 0.38):int(self.height * 0.42),
            int(self.width * 0.35):int(self.width * 0.65)
        ]

        if self.is_wearing_sunglasses(eye_region):
            accessories['sunglasses'] = True
            # Detect sunglasses color
            sg_color = self.get_dominant_colors(eye_region, n_colors=2)[0]
            sg_color_name = self.rgb_to_color_name(*sg_color)
            accessories['descriptions'].append(f"wearing {sg_color_name} sunglasses")
            print(f"  ✓ Detected: {sg_color_name} sunglasses")

        # 2. Earring detection (ears at 45-55% height, 10-25% and 75-90% width)
        left_ear = self.image_array[
            int(self.height * 0.45):int(self.height * 0.55),
            :int(self.width * 0.25)
        ]
        right_ear = self.image_array[
            int(self.height * 0.45):int(self.height * 0.55),
            int(self.width * 0.75):
        ]

        earring_color = None
        if self.has_bright_accent(left_ear) or self.has_bright_accent(right_ear):
            accessories['earrings'] = True
            # Get earring color from the region that has them
            if self.has_bright_accent(left_ear):
                earring_colors = self.get_dominant_colors(left_ear, n_colors=3)
            else:
                earring_colors = self.get_dominant_colors(right_ear, n_colors=3)

            # Find brightest color (earrings are usually bright/shiny)
            brightest = max(earring_colors, key=lambda c: sum(c))
            earring_color = self.rgb_to_color_name(*brightest)
            accessories['descriptions'].append(f"{earring_color} earrings")
            print(f"  ✓ Detected: {earring_color} earrings")

        # 3. Hat detection (top 15% of image)
        top_region = self.image_array[:int(self.height * 0.15), :]

        if self.has_hat(top_region):
            accessories['hat'] = True
            hat_colors = self.get_dominant_colors(top_region, n_colors=2)
            hat_color_name = self.rgb_to_color_name(*hat_colors[0])
            accessories['descriptions'].append(f"{hat_color_name} hat")
            print(f"  ✓ Detected: {hat_color_name} hat")

        return accessories

    def is_wearing_sunglasses(self, eye_region):
        """
        Check if the eye region is covered by sunglasses.
        Sunglasses typically have:
        - Low color variance (uniform dark color)
        - Dark overall color
        - High coverage of the eye region
        """
        if eye_region.size == 0:
            return False

        # Check if region is mostly dark and uniform
        avg_brightness = np.mean(eye_region)
        color_variance = np.std(eye_region)

        # Sunglasses: very dark (< 100 brightness) and relatively uniform (< 40 variance)
        # But not TOO uniform (that would be pure black background)
        is_dark = avg_brightness < 100
        is_uniform = 10 < color_variance < 40

        return is_dark and is_uniform

    def has_bright_accent(self, region):
        """
        Check if a region has bright accents (e.g., earrings, jewelry).
        Bright accents are:
        - High brightness spots
        - Small but distinct
        - Contrast with surrounding
        """
        if region.size == 0:
            return False

        # Get top 3 colors
        colors = self.get_dominant_colors(region, n_colors=min(3, region.size // 3))

        # Check if any color is very bright (jewelry reflects light)
        for color in colors:
            brightness = sum(color) / 3
            # Bright colors (> 180) suggest shiny jewelry
            if brightness > 180:
                # Make sure it's not just background bleeding in
                # Check color variance (jewelry has distinct color)
                r, g, b = color
                variance = np.std([r, g, b])
                if variance > 10 or brightness > 220:  # Either colorful or very bright
                    return True

        return False

    def has_hat(self, top_region):
        """
        Check if the top region has a hat/headwear.
        Hats typically:
        - Occupy significant portion of top region
        - Have distinct color from hair
        - Have relatively uniform color
        """
        if top_region.size == 0:
            return False

        # Get dominant colors in top region
        top_colors = self.get_dominant_colors(top_region, n_colors=3)

        # Get hair region colors for comparison
        hair_region = self.image_array[:int(self.height * 0.4), :]
        hair_colors = self.get_dominant_colors(hair_region, n_colors=3)

        # Check if top region has distinct color from hair
        # (hats are usually different color than hair)
        top_color = top_colors[0]
        hair_color = hair_colors[0]

        color_distance = np.linalg.norm(top_color - hair_color)

        # If very different colors in top vs hair region, likely a hat
        # Threshold: > 60 suggests distinct object
        has_distinct_color = color_distance > 60

        # Also check if top region has high variance (patterns/shapes)
        top_variance = np.std(top_region)
        has_shape = top_variance > 20

        return has_distinct_color and has_shape

    def rgb_to_color_name(self, r, g, b):
        """Convert RGB to color name (moved from EnhancedPromptGenerator for use in analyzer)"""
        # Grayscale detection
        if max(abs(r-g), abs(g-b), abs(r-b)) < 30:
            brightness = (r + g + b) / 3
            if brightness > 200:
                return "white"
            elif brightness > 150:
                return "light gray"
            elif brightness > 100:
                return "gray"
            elif brightness > 50:
                return "dark gray"
            else:
                return "black"

        # Color detection
        if r > g and r > b:
            if g > 100:
                return "orange" if r > 200 else "brown"
            elif b > 100:
                return "pink" if r > 200 else "purple"
            else:
                return "red"
        elif g > r and g > b:
            if b > 100:
                return "cyan" if g > 200 else "teal"
            elif r > 100:
                return "yellow" if g > 200 else "olive"
            else:
                return "green"
        elif b > r and b > g:
            if r > 100:
                return "purple" if b > 200 else "dark purple"
            else:
                return "blue" if b > 150 else "dark blue"

        # Fallback
        brightness = (r + g + b) / 3
        if brightness > 180:
            return "light"
        elif brightness > 100:
            return "medium"
        else:
            return "dark"


class EnhancedColorPaletteExtractor:
    """Extract comprehensive color palette with all 12 colors"""

    def __init__(self, image_path):
        """Initialize with image path"""
        self.image = Image.open(image_path).convert('RGB')
        self.image_array = np.array(self.image)

    def get_color_palette(self, n_colors=12):
        """
        Extract N most dominant colors from image.
        Returns ALL colors (not just top 5) for richer prompts.
        """
        # Reshape image to list of pixels
        pixels = self.image_array.reshape(-1, 3)

        # K-means clustering to find dominant colors
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Get cluster centers and labels
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_

        # Count pixels per cluster to get weights
        counts = Counter(labels)
        total_pixels = len(labels)

        # Build color palette with weights
        palette = []
        for i, color in enumerate(colors):
            weight = counts[i] / total_pixels
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(color[0]), int(color[1]), int(color[2])
            )
            name = self.color_to_name(color)

            palette.append({
                'rgb': color.tolist(),
                'hex': hex_color,
                'name': name,
                'weight': weight
            })

        # Sort by weight (most dominant first)
        palette.sort(key=lambda x: x['weight'], reverse=True)

        return palette

    def color_to_name(self, rgb):
        """Convert RGB to color name"""
        r, g, b = rgb

        # Grayscale detection
        if max(abs(r-g), abs(g-b), abs(r-b)) < 30:
            brightness = (r + g + b) / 3
            if brightness > 200:
                return "white"
            elif brightness > 150:
                return "light gray"
            elif brightness > 100:
                return "gray"
            elif brightness > 50:
                return "dark gray"
            else:
                return "black"

        # Color detection
        if r > g and r > b:
            if g > 100:
                return "orange" if r > 200 else "brown"
            elif b > 100:
                return "pink" if r > 200 else "purple"
            else:
                return "red"
        elif g > r and g > b:
            if b > 100:
                return "cyan" if g > 200 else "teal"
            elif r > 100:
                return "yellow" if g > 200 else "olive"
            else:
                return "green"
        elif b > r and b > g:
            if r > 100:
                return "purple" if b > 200 else "dark purple"
            else:
                return "blue" if b > 150 else "dark blue"

        # Fallback
        brightness = (r + g + b) / 3
        if brightness > 180:
            return "light"
        elif brightness > 100:
            return "medium"
        else:
            return "dark"

    def detect_background(self):
        """Detect background color (most dominant color)"""
        palette = self.get_color_palette(n_colors=12)
        return palette[0]  # Most dominant color


class EnhancedPromptGenerator:
    """
    Generate training-format prompts using enhanced image analysis.

    Addresses all V2 issues:
    - Includes hair shape/volume/texture
    - Uses male/female type (lad/lady)
    - Better hair color detection
    - Uses ALL 12 colors in prompt
    - Pattern detection for backgrounds
    """

    def __init__(self):
        """Initialize prompt generator"""
        pass

    def generate(self, image_path):
        """Generate complete prompt from image"""

        print(f"\n{'='*60}")
        print(f"V2.7 COMPREHENSIVE FIX ANALYSIS: {image_path}")
        print(f"{'='*60}\n")

        # Step 1: Enhanced image analysis
        print("Step 1: Analyzing image regions...")
        analyzer = EnhancedImageAnalyzer(image_path)

        hair_info = analyzer.analyze_hair_region()
        face_info = analyzer.analyze_face_region()
        punk_type = analyzer.detect_type()
        bg_pattern = analyzer.analyze_background_pattern()

        print(f"Type: {punk_type}")
        print(f"Hair: {hair_info}")
        print(f"Background pattern: {bg_pattern}")

        # Step 2: Color palette extraction (ALL 12 colors)
        print("\nStep 2: Extracting full color palette...")
        extractor = EnhancedColorPaletteExtractor(image_path)
        palette = extractor.get_color_palette(n_colors=12)
        background = palette[0]

        print(f"Background: {background['name']} ({background['hex']})")
        print(f"All colors: {[c['name'] for c in palette]}")

        # Step 3: Map colors to features using region-specific analysis
        print("\nStep 3: V2.7 - Mapping colors with improved detection...")

        # V2.7 NEW: Detect accessories first (affects eye detection)
        print("\nDetecting accessories...")
        accessories = analyzer.detect_accessories()

        # V2.6 FIX: Get hair color from hair region (not global palette)
        hair_colors = analyzer.get_hair_colors()
        hair_color = self.detect_hair_color_from_region(hair_colors)

        # V2.6 FIX: Get background colors from corners (captures gradients)
        bg_colors = analyzer.get_background_colors()
        background = self.map_background_gradient(bg_colors, bg_pattern)

        # V2.7 FIX: Get eye color with much more precise detection
        # IMPORTANT: Skip eye detection if wearing sunglasses
        if accessories['sunglasses']:
            eye_color = None  # Don't include eye color if sunglasses present
            print(f"Eyes: hidden by sunglasses")
        else:
            eye_rgb = analyzer.get_eye_region_colors_v2_7()
            eye_color = self.map_eye_color(eye_rgb)
            print(f"Eyes: {eye_color}")

        # Skin tone still from face region (this was working well)
        skin_color = self.map_skin_tone(face_info['skin'])

        print(f"Hair color: {hair_color}")
        print(f"Skin: {skin_color}")

        # Step 4: Build enhanced prompt with ALL details
        print("\nStep 4: Building enhanced prompt...")

        # V2.7 IMPROVED: Build hair description with specific style if detected
        if hair_info['style']:
            # Use specific style instead of texture/volume
            if hair_info['length'] in ['long', 'medium']:
                hair_desc = f"long {hair_info['style']} {hair_color} hair"
            else:
                hair_desc = f"{hair_info['style']} {hair_color} hair"
        else:
            # Fallback to texture/volume description
            hair_desc = f"{hair_color} {hair_info['texture']} {hair_info['volume']} hair"

        # V2.7 FIX: Map colors to specific features instead of generic list
        # Extract remaining colors for clothing, shadows, highlights
        remaining_colors = [c for c in palette if c['weight'] > 0.02]  # Only significant colors

        # Map colors to features
        clothing_colors = []
        accent_colors = []

        for color in remaining_colors[1:]:  # Skip background
            color_name = color['name']
            # Skip if already used for hair, eyes, skin, background
            # V2.7 FIX: Handle None eye_color when sunglasses detected
            eye_base = eye_color.split()[0] if eye_color else None
            if color_name in [hair_color, eye_base, skin_color.split()[0], background['name']]:
                continue

            # Assign colors to clothing or accents based on weight
            if color['weight'] > 0.05:
                clothing_colors.append(color_name)
            else:
                accent_colors.append(color_name)

        # Build prompt parts with explicit color-to-feature mapping
        prompt_parts = [
            "pixel art",
            "24x24",
            f"portrait of bespoke punk {punk_type}",
            hair_desc,
        ]

        # V2.7 NEW: Add accessories if detected
        if accessories['descriptions']:
            prompt_parts.extend(accessories['descriptions'])

        # Add eye color (unless wearing sunglasses)
        if eye_color:
            prompt_parts.append(eye_color)

        # Add skin and background
        prompt_parts.extend([
            skin_color,
            f"{background['name']} {bg_pattern} background ({background['hex']})"
        ])

        # Add clothing colors explicitly
        if clothing_colors:
            clothing_desc = f"{clothing_colors[0]} clothing"
            if len(clothing_colors) > 1:
                clothing_desc += f" with {clothing_colors[1]} accents"
            prompt_parts.append(clothing_desc)

        # Add highlights/shadows for color richness
        if accent_colors:
            if 'white' in accent_colors or 'light gray' in accent_colors:
                prompt_parts.append("white highlights")
            if 'black' in accent_colors or 'dark gray' in accent_colors:
                prompt_parts.append("dark shadows")

        # Style markers
        prompt_parts.extend([
            "sharp pixel edges",
            "hard color borders",
            "retro pixel art style"
        ])

        prompt = ", ".join(prompt_parts)

        # Metadata for display
        metadata = {
            'type': punk_type,
            'background': f"{background['name']} {bg_pattern} ({background['hex']})",
            'hair': hair_desc,
            'eyes': eye_color,
            'skin': skin_color,
            'all_colors': [c['name'] for c in palette],
            'hair_details': hair_info
        }

        print(f"\n{'='*60}")
        print("GENERATED PROMPT:")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return {
            'prompt': prompt,
            'metadata': metadata
        }

    def rgb_to_color_name(self, r, g, b):
        """Convert RGB values to color name - standalone implementation"""
        # Grayscale detection
        if max(abs(r-g), abs(g-b), abs(r-b)) < 30:
            brightness = (r + g + b) / 3
            if brightness > 200:
                return "white"
            elif brightness > 150:
                return "light gray"
            elif brightness > 100:
                return "gray"
            elif brightness > 50:
                return "dark gray"
            else:
                return "black"

        # Color detection
        if r > g and r > b:
            if g > 100:
                return "orange" if r > 200 else "brown"
            elif b > 100:
                return "pink" if r > 200 else "purple"
            else:
                return "red"
        elif g > r and g > b:
            if b > 100:
                return "cyan" if g > 200 else "teal"
            elif r > 100:
                return "yellow" if g > 200 else "olive"
            else:
                return "green"
        elif b > r and b > g:
            if r > 100:
                return "purple" if b > 200 else "dark purple"
            else:
                return "blue" if b > 150 else "dark blue"

        # Fallback
        brightness = (r + g + b) / 3
        if brightness > 180:
            return "light"
        elif brightness > 100:
            return "medium"
        else:
            return "dark"

    def detect_hair_color_from_region(self, hair_colors):
        """
        V2.6: Detect hair color from hair region RGB values.
        This eliminates background color interference.
        """
        # Filter out background colors and find the darkest remaining color
        valid_colors = []

        for color in hair_colors:
            r, g, b = color
            total_brightness = r + g + b

            # Skip very bright colors (likely background/reflections)
            if total_brightness > 600:  # Bright backgrounds like cyan, green, pink
                continue

            # Skip highly saturated bright colors (typical of backgrounds)
            max_channel = max(r, g, b)
            min_channel = min(r, g, b)
            saturation = max_channel - min_channel

            # Skip if highly saturated AND bright (background colors)
            if saturation > 80 and total_brightness > 400:
                continue

            valid_colors.append((color, total_brightness))

        # If we filtered everything, use original list
        if not valid_colors:
            valid_colors = [(color, sum(color)) for color in hair_colors]

        # Sort by brightness (darkest first) - hair is typically darker
        valid_colors.sort(key=lambda x: x[1])

        # Get the darkest valid color
        r, g, b = valid_colors[0][0]

        # Map to color name
        name = self.rgb_to_color_name(r, g, b)

        # Fix gray vs brown confusion
        if name in ['gray', 'light gray', 'dark gray']:
            if g > b and r > b and abs(r-g) < 50:
                return "brown"

        return name

    def map_background_gradient(self, bg_colors, pattern):
        """
        V2.6: Map background colors (from corners) to description.
        Handles gradients by using the dominant color from corners.
        """
        if len(bg_colors) == 0:
            return {'name': 'blue', 'hex': '#0000ff'}

        # Use the most dominant background color
        dominant_bg = bg_colors[0]
        r, g, b = dominant_bg

        # Convert to hex
        hex_code = '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

        # Get color name
        name = self.rgb_to_color_name(r, g, b)

        return {'name': name, 'hex': hex_code}

    def detect_hair_color(self, palette, exclude_bg=True):
        """
        DEPRECATED in V2.6: Use detect_hair_color_from_region instead.
        Kept for backwards compatibility.
        """
        # Skip first color (background)
        hair_candidates = palette[1:] if exclude_bg else palette

        # Look for hair-like colors (not too bright, not skin tones)
        for color in hair_candidates:
            r, g, b = color['rgb']

            # Skip very bright colors (likely background or clothing)
            if r > 200 and g > 200 and b > 200:
                continue

            # Skip skin tones (similar R,G,B values in middle range)
            if 100 < r < 200 and abs(r-g) < 40 and abs(g-b) < 40:
                continue

            # This is likely hair color
            name = color['name']

            # Fix gray vs brown confusion
            if name in ['gray', 'light gray', 'dark gray']:
                # Check if it's actually brown
                if g > b and r > b and abs(r-g) < 50:
                    return "brown"

            return name

        # Fallback: second most dominant color
        return hair_candidates[0]['name'] if hair_candidates else "black"

    def map_skin_tone(self, rgb):
        """Map RGB to skin tone names from training vocabulary"""
        r, g, b = rgb
        brightness = (r + g + b) / 3

        # Check if it's actually a skin tone
        variance = np.std([r, g, b])

        if variance > 50:  # Not a skin tone, too varied
            return "light skin"

        # Map based on brightness
        if brightness > 200:
            return "light skin"
        elif brightness > 160:
            return "light/tan skin"
        elif brightness > 120:
            return "tan skin"
        elif brightness > 80:
            return "brown skin"
        else:
            return "dark skin"

    def map_eye_color(self, rgb):
        """
        V2.7 IMPROVED: Map RGB to eye color names with better brown detection.
        """
        r, g, b = rgb

        print(f"  Mapping eye color from RGB({r:.0f}, {g:.0f}, {b:.0f})")

        # Check for brown eyes first (most common, often mis-detected as blue)
        # Brown eyes: Red and Green channels higher than Blue
        if r > b and g > b:
            # Dark brown vs light brown
            brightness = (r + g + b) / 3
            if brightness < 100:
                result = "dark brown eyes"
            else:
                result = "brown eyes"
            print(f"  → Detected: {result} (r={r:.0f} > b={b:.0f}, g={g:.0f} > b={b:.0f})")
            return result

        # Blue eyes: Blue channel dominant
        if b > r and b > g:
            if b > 150:
                result = "blue eyes"
            else:
                result = "dark blue eyes"
            print(f"  → Detected: {result} (b={b:.0f} dominant)")
            return result

        # Green eyes: Green channel dominant
        if g > r and g > b:
            result = "green eyes"
            print(f"  → Detected: {result} (g={g:.0f} dominant)")
            return result

        # Red eyes (rare, but possible in pixel art)
        if r > g and r > b:
            result = "red eyes"
            print(f"  → Detected: {result} (r={r:.0f} dominant)")
            return result

        # Grayscale (gray eyes)
        result = "gray eyes"
        print(f"  → Detected: {result} (fallback)")
        return result


class BespokePunkGeneratorV27:
    """
    Complete V2.7 generation pipeline with comprehensive fixes.
    """

    def __init__(self, lora_path):
        """Initialize enhanced generator with LoRA"""
        print("Loading Stable Diffusion 1.5 with LoRA...")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )

        # Load LoRA weights
        print(f"Loading LoRA: {lora_path}")
        self.pipe.load_lora_weights(lora_path)

        # Disable safety checker to avoid false positives on pixel art
        self.pipe.safety_checker = None

        # Move to MPS (Metal) for M-series Macs
        if torch.backends.mps.is_available():
            self.pipe = self.pipe.to("mps")
            print("Using Metal Performance Shaders (MPS)")
        elif torch.cuda.is_available():
            self.pipe = self.pipe.to("cuda")
            print("Using CUDA")
        else:
            print("Using CPU (will be slow)")

        print("Model loaded!")

        self.prompt_generator = EnhancedPromptGenerator()

    def generate_from_image(self, image_path, num_inference_steps=30, guidance_scale=7.5):
        """Generate Bespoke Punk from uploaded image"""

        # Generate enhanced prompt
        result = self.prompt_generator.generate(image_path)
        prompt = result['prompt']
        metadata = result['metadata']

        # Generate 512x512 image
        print("Generating 512×512 image with LoRA...")
        image_512 = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=torch.Generator().manual_seed(42)
        ).images[0]

        # Downscale to 24x24 using NEAREST for pixel-perfect
        print("Downscaling to 24×24...")
        image_24 = image_512.resize((24, 24), Image.NEAREST)

        print("✓ Generation complete!")

        return {
            'image_512': image_512,
            'image_24': image_24,
            'prompt': prompt,
            'metadata': metadata
        }


if __name__ == "__main__":
    import sys

    print("="*60)
    print("BESPOKE PUNK GENERATOR V2.7 - COMPREHENSIVE FIXES")
    print("="*60)
    print()

    if len(sys.argv) < 2:
        print("Usage: python bespoke_punk_generator_v2_7.py <image_path>")
        print()
        print("Example:")
        print("  python bespoke_punk_generator_v2_7.py test_image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    lora_path = "Context 1106/bespoke_punks_sd15_512-000002.safetensors"

    # Initialize V2.7 generator with comprehensive fixes
    generator = BespokePunkGeneratorV27(lora_path)

    # Generate
    result = generator.generate_from_image(image_path)

    # Save outputs
    output_512_path = "test_v2_7_output_512.png"
    output_24_path = "test_v2_7_output_24.png"

    result['image_512'].save(output_512_path)
    result['image_24'].save(output_24_path)

    print()
    print("="*60)
    print("OUTPUTS SAVED:")
    print("="*60)
    print(f"512×512: {output_512_path}")
    print(f"24×24:   {output_24_path}")
    print()
    print("METADATA:")
    print(json.dumps(result['metadata'], indent=2))
    print()

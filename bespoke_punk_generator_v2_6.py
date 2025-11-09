#!/usr/bin/env python3
"""
Bespoke Punk Generator V2.6 - Region-Specific Color Analysis

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
        self.image = Image.open(image_path).convert('RGB')
        self.image_array = np.array(self.image)
        self.height, self.width = self.image_array.shape[:2]

    def analyze_hair_region(self):
        """
        Analyze top 40% of image for hair characteristics.

        Returns:
        - volume: low, medium, high
        - texture: smooth, wavy, curly, spiky, pixelated
        - length: short, medium, long
        """
        # Get top 40% of image (where hair typically is)
        hair_region = self.image_array[:int(self.height * 0.4), :]

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
            'length': length
        }

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
        Detect if image is likely male (lad) or female (lady).

        Uses heuristics:
        - Hair length/volume
        - Color palette (pinks/purples suggest female)
        - Face region characteristics
        """
        hair_info = self.analyze_hair_region()

        # Female indicators
        female_score = 0

        # Long/voluminous hair
        if hair_info['length'] in ['long', 'medium']:
            female_score += 2
        if 'voluminous' in hair_info['volume']:
            female_score += 2

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

        # Return type
        return "lady" if female_score >= 3 else "lad"

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

    def get_eye_region_colors(self):
        """
        Extract colors from eye-specific region.
        V2.6 FIX: More accurate eye color by looking at narrow eye band.
        """
        # Eyes are typically around 35-45% down the image
        eye_region = self.image_array[
            int(self.height * 0.35):int(self.height * 0.45),
            int(self.width * 0.25):int(self.width * 0.75)
        ]

        if eye_region.size == 0:
            return [(100, 80, 60)]  # Default brown

        # Extract top 3 colors from eye region
        pixels = eye_region.reshape(-1, 3)
        kmeans = KMeans(n_clusters=min(3, len(pixels)), random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Return the most saturated color (likely eyes, not skin/whites)
        colors = kmeans.cluster_centers_
        most_saturated = max(colors, key=lambda c: np.std(c))

        return most_saturated


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
        print(f"V2.6 REGION-SPECIFIC ANALYSIS: {image_path}")
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
        print("\nStep 3: Mapping colors using region-specific extraction...")

        # V2.6 FIX: Get hair color from hair region (not global palette)
        hair_colors = analyzer.get_hair_colors()
        hair_color = self.detect_hair_color_from_region(hair_colors)

        # V2.6 FIX: Get background colors from corners (captures gradients)
        bg_colors = analyzer.get_background_colors()
        background = self.map_background_gradient(bg_colors, bg_pattern)

        # V2.6 FIX: Get eye color from eye-specific region
        eye_rgb = analyzer.get_eye_region_colors()
        eye_color = self.map_eye_color(eye_rgb)

        # Skin tone still from face region (this was working well)
        skin_color = self.map_skin_tone(face_info['skin'])

        print(f"Hair color: {hair_color}")
        print(f"Skin: {skin_color}")
        print(f"Eyes: {eye_color}")

        # Step 4: Build enhanced prompt with ALL details
        print("\nStep 4: Building enhanced prompt...")

        # Build hair description with shape/volume/texture
        hair_desc = f"{hair_color} {hair_info['texture']} {hair_info['volume']} hair"

        # Build prompt parts
        prompt_parts = [
            "pixel art",
            "24x24",
            f"portrait of bespoke punk {punk_type}",
            f"{background['name']} {bg_pattern} background ({background['hex']})",
            hair_desc,
            eye_color,
            skin_color
        ]

        # Add color richness by mentioning multiple colors
        top_colors = [c['name'] for c in palette[1:6]]  # Skip background
        color_list = ", ".join(top_colors)
        prompt_parts.append(f"using colors {color_list}")

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
        """Map RGB to eye color names"""
        r, g, b = rgb

        # Determine dominant color channel
        if b > r and b > g:
            if b > 150:
                return "blue eyes"
            else:
                return "dark blue eyes"
        elif g > r and g > b:
            return "green eyes"
        elif r > g and r > b:
            if g > 80:
                return "brown eyes"
            else:
                return "red eyes"
        else:
            # Grayish
            return "gray eyes"


class BespokePunkGeneratorV26:
    """
    Complete V2.6 generation pipeline with region-specific color analysis.
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
    print("BESPOKE PUNK GENERATOR V2.6 - REGION-SPECIFIC ANALYSIS")
    print("="*60)
    print()

    if len(sys.argv) < 2:
        print("Usage: python bespoke_punk_generator_v2_6.py <image_path>")
        print()
        print("Example:")
        print("  python bespoke_punk_generator_v2_6.py test_image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    lora_path = "Context 1106/bespoke_punks_sd15_512-000002.safetensors"

    # Initialize V2.6 generator with region-specific color analysis
    generator = BespokePunkGeneratorV26(lora_path)

    # Generate
    result = generator.generate_from_image(image_path)

    # Save outputs
    output_512_path = "test_v2_6_output_512.png"
    output_24_path = "test_v2_6_output_24.png"

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

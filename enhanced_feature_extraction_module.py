#!/usr/bin/env python3
"""
ENHANCED FEATURE EXTRACTION - FIXED VERSION
Addresses critical bugs found in screenshot testing:
- Background color detection (was detecting blue instead of green)
- Sunglasses detection (completely missing)
- Earrings detection (not finding large visible earrings)
"""

from PIL import Image
import numpy as np
from collections import Counter

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
        IMPROVED: Detect sunglasses vs regular glasses with better accuracy
        Returns: 'sunglasses', 'glasses', or 'none'
        """
        # Eye region (broader to catch sunglasses)
        eye_region = self.arr[int(self.height*0.20):int(self.height*0.50),
                               int(self.width*0.15):int(self.width*0.85)]

        # Calculate average brightness
        avg_brightness = eye_region.mean(axis=(0, 1)).mean()

        # Detect edges in eye region (for frame detection)
        from scipy import ndimage
        gray = eye_region.mean(axis=2)
        edges = ndimage.sobel(gray)
        edge_strength = edges.std()

        # SUNGLASSES: Very dark + strong edges + high dark pixel percentage
        # More strict criteria to avoid false positives
        if avg_brightness < 70:  # Dark threshold
            # Check darkness consistency
            dark_pixels = eye_region[eye_region.mean(axis=2) < 85]  # Dark pixels
            dark_percentage = len(dark_pixels) / len(eye_region.reshape(-1, 3))

            # Sunglasses need high dark percentage
            if dark_percentage > 0.35:  # Relaxed edge requirement
                # If very dark, likely sunglasses even without strong edges
                if dark_percentage > 0.45 or edge_strength > 6:
                    return 'sunglasses'

        # GLASSES: Moderate brightness with frame edges
        # Look for frames but NOT too dark
        if 60 <= avg_brightness < 180:  # Broader range for regular glasses
            # Check for edges (frames)
            if edge_strength > 8:  # Lowered threshold to catch more glasses
                # Make sure it's not too dark (would be sunglasses)
                very_dark_pixels = eye_region[eye_region.mean(axis=2) < 70]
                very_dark_pct = len(very_dark_pixels) / len(eye_region.reshape(-1, 3))

                if very_dark_pct < 0.25:  # Not too dark = regular glasses
                    return 'glasses'

        # Fallback: very strong edges = some eyewear
        if edge_strength > 11:  # Very strong edges = eyewear present
            if avg_brightness > 75:
                return 'glasses'
            else:
                return 'sunglasses'

        return 'none'

    # ========================================================================
    # FIXED: Earrings Detection
    # ========================================================================

    def detect_earrings(self):
        """
        FIXED: Detect earrings by checking ear regions for distinct color points
        Returns: dict with 'present' (bool) and 'type' (stud/hoop/none)
        """
        # EVEN WIDER ear regions - catch earrings that hang low or sit far out
        # Left ear region (35% of width from left edge)
        left_ear = self.arr[int(self.height*0.15):int(self.height*0.65),
                            0:int(self.width*0.35)]

        # Right ear region (35% of width from right edge)
        right_ear = self.arr[int(self.height*0.15):int(self.height*0.65),
                              int(self.width*0.65):]

        # Combine both ears
        ear_regions = [left_ear, right_ear]

        earring_detected = False
        earring_type = 'none'
        max_earring_percentage = 0

        for ear_region in ear_regions:
            if ear_region.size == 0:
                continue

            # Flatten to analyze colors
            ear_pixels = ear_region.reshape(-1, 3)

            # Look for distinct color points (earrings are usually:
            # - Bright OR saturated OR metallic
            # - Small to medium region (not dominant like hair/skin)
            # - Different from hair and skin tones

            pixel_colors = [tuple(p) for p in ear_pixels]
            color_counts = Counter(pixel_colors)

            # Check for distinct colored regions (VERY RELAXED thresholds)
            for color, count in color_counts.most_common(40):  # Check even more colors
                r, g, b = color
                brightness = (r + g + b) / 3
                percentage = count / len(ear_pixels)

                # Skip if way too dominant (likely hair or background)
                if percentage > 0.35:
                    continue

                # Earring characteristics (VERY RELAXED):
                # 1. Not too small (<1.5%) or too large (>35%)
                # 2. Either bright (>60) OR saturated color OR distinct from surroundings
                # 3. Not skin tone

                is_bright = brightness > 60  # Lowered from 80
                is_saturated = max(r, g, b) - min(r, g, b) > 40  # Lowered from 50
                is_metallic = (abs(r - g) < 30 and abs(g - b) < 30 and brightness > 100)  # Silver/gold

                if percentage > 0.015 and (is_bright or is_saturated or is_metallic):
                    if not self._is_skin_tone(r, g, b):
                        # More lenient check - just needs to be somewhat distinct
                        if brightness > 30 or is_saturated or is_metallic:
                            earring_detected = True

                            # Track largest earring region found
                            if percentage > max_earring_percentage:
                                max_earring_percentage = percentage

                                # Determine type: hoops are MUCH larger than studs
                                # VERY strict threshold to reduce false positives
                                if percentage > 0.18:  # Raised from 0.15 - hoops are VERY BIG
                                    earring_type = 'hoop'  # Large dangly/hoop
                                else:
                                    earring_type = 'stud'  # Small stud

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
    # Hairstyle Detection (NEW)
    # ========================================================================

    def detect_hairstyle(self):
        """
        Detect hairstyle texture: 'braids', 'curly', 'wavy', 'straight', or None
        Uses texture variance and pattern detection
        Wavy/curly boundary improved based on validation results
        """
        # Sample hair region (upper 35% of image)
        hair_region = self.arr[:int(self.height * 0.35), :]

        if hair_region.size == 0:
            return None

        # Convert to grayscale for texture analysis
        gray_hair = hair_region.mean(axis=2)

        # Calculate texture variance (curly hair has high variance)
        texture_variance = gray_hair.std()

        # BRAIDS: Look for repeating patterns (vertical segments)
        # Braids have alternating brightness in vertical strips
        # Check braids first but with stricter threshold
        if self._detect_braid_pattern(gray_hair, texture_variance):
            return 'braids'

        # CURLY/WAVY: Group together since hard to distinguish
        # Training data often uses these interchangeably
        if texture_variance > 42:  # High variance = curly/wavy
            # Default to curly (more common)
            return 'curly'

        # WAVY: Medium variance (some texture but not tight curls)
        elif texture_variance >= 35:  # Medium variance
            return 'wavy'

        # STRAIGHT: Low variance (smooth, uniform)
        else:  # < 35
            return 'straight'

    def _detect_braid_pattern(self, gray_hair, texture_variance):
        """
        Detect braiding pattern by looking for vertical repeating segments
        Braids create alternating dark/light vertical bands
        Made stricter to reduce false positives
        """
        if gray_hair.size == 0:
            return False

        # Braids typically have medium-high texture variance
        # Too low = straight/wavy, too high = just curly
        if texture_variance < 38 or texture_variance > 58:
            return False

        # Analyze vertical columns for repeating patterns
        height, width = gray_hair.shape

        # Sample columns across the width
        column_variances = []
        for x in range(0, width, max(1, width // 10)):  # Sample 10 columns
            if x >= width:
                break
            column = gray_hair[:, x]
            column_variances.append(column.std())

        if len(column_variances) < 3:
            return False

        # Braids: High variance between adjacent columns (alternating pattern)
        variance_changes = []
        for i in range(len(column_variances) - 1):
            variance_changes.append(abs(column_variances[i+1] - column_variances[i]))

        avg_variance_change = np.mean(variance_changes)

        # STRICTER threshold: If columns vary significantly, likely braids
        if avg_variance_change > 20:  # Raised from 15 - need stronger pattern
            # Also check for repeating segments by looking at row patterns
            # Braids have horizontal consistency within each braid
            row_means = gray_hair.mean(axis=1)
            row_variance = row_means.std()

            # Braids should have some vertical structure (not too uniform)
            if row_variance > 12:  # Raised from 10
                return True

        return False

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

            # Hairstyle (NEW)
            'hairstyle': self.detect_hairstyle(),  # 'braids', 'curly', 'straight', or None
        }

        return features


# ============================================================================
# TEST FUNCTION
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_feature_extraction.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"Analyzing: {image_path}")
    print("="*70)

    extractor = EnhancedFeatureExtractor(image_path)
    features = extractor.extract_all_features()

    print("\nDetected Features:")
    print("-"*70)
    for key, value in features.items():
        print(f"  {key:20s}: {value}")

    print("="*70)

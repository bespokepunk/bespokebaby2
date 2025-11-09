#!/usr/bin/env python3
"""
Bespoke Punk Generator V3 - Hybrid Vision Model + Color Palette

Combines BLIP-2 vision-language model for semantic feature detection
with k-means color palette extraction for accurate prompt generation.

V3 Improvements over V2:
- Distinguishes helmets/hats from hair
- Detects accessories (sunglasses, earrings, necklaces)
- Identifies specific hairstyles (braids, curls, pixelated)
- More accurate skin tone detection
- Understands gradient/patterned backgrounds
"""

import json
import torch
from PIL import Image
import numpy as np
from difflib import get_close_matches
from transformers import Blip2Processor, Blip2ForConditionalGeneration

# Import V2 components we're reusing
from bespoke_punk_generator_v2 import (
    ColorPaletteExtractor,
    BespokePunkGenerator
)


class VisionFeatureDetector:
    """
    Uses BLIP-2 vision-language model to extract semantic features from images.

    Asks targeted questions to detect:
    - Hair color and style
    - Eye color
    - Skin tone
    - Headwear (hats, helmets, crowns)
    - Accessories (sunglasses, earrings, necklaces)
    - Background patterns
    """

    def __init__(self, model_name="Salesforce/blip2-opt-2.7b"):
        """Initialize BLIP-2 model"""
        print(f"Loading BLIP-2 model: {model_name}...")
        print("This is a ~5GB download on first run, please be patient...")

        self.processor = Blip2Processor.from_pretrained(model_name)
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16
        )

        # Use MPS for M-series Macs, CUDA for NVIDIA, CPU as fallback
        if torch.backends.mps.is_available():
            self.device = "mps"
            print("Using Metal Performance Shaders (MPS) for acceleration")
        elif torch.cuda.is_available():
            self.device = "cuda"
            print("Using CUDA for acceleration")
        else:
            self.device = "cpu"
            print("Using CPU (this will be slower)")

        self.model = self.model.to(self.device)
        print("BLIP-2 model loaded successfully!")

    def generate_caption(self, image, prompt="", max_tokens=100):
        """Generate a detailed caption for the image"""
        inputs = self.processor(image, text=prompt, return_tensors="pt").to(
            self.device,
            torch.float16 if self.device != "cpu" else torch.float32
        )

        out = self.model.generate(**inputs, max_new_tokens=max_tokens)
        caption = self.processor.decode(out[0], skip_special_tokens=True)

        return caption.strip()

    def ask_question(self, image, question, max_tokens=30):
        """Ask BLIP-2 a question about the image using prompt-based approach"""
        # For BLIP-2, use "Question: X Answer:" format
        prompt = f"Question: {question} Answer:"

        inputs = self.processor(image, text=prompt, return_tensors="pt").to(
            self.device,
            torch.float16 if self.device != "cpu" else torch.float32
        )

        out = self.model.generate(**inputs, max_new_tokens=max_tokens)
        full_output = self.processor.decode(out[0], skip_special_tokens=True)

        # Extract just the answer part (remove the question echo)
        if "Answer:" in full_output:
            answer = full_output.split("Answer:")[-1].strip()
        else:
            answer = full_output.strip()

        return answer

    def detect_features(self, image_path):
        """
        Detect all features using targeted questions.

        Returns dict with keys:
        - hair_description: Full description of hair
        - eye_color: Eye color
        - skin_tone: Skin tone description
        - headwear: What's on the head (hat, helmet, crown, etc.)
        - face_accessories: Sunglasses, visor, etc.
        - other_accessories: Earrings, necklaces, etc.
        - background: Background description
        """
        image = Image.open(image_path).convert('RGB')

        print("Analyzing image with BLIP-2...")

        features = {}

        # Hair - be specific to avoid confusing with headwear
        features['hair_description'] = self.ask_question(
            image,
            "What is the color and style of the person's hair? Ignore any hats or headwear."
        )

        # Eyes
        features['eye_color'] = self.ask_question(
            image,
            "What color are the person's eyes?"
        )

        # Skin tone
        features['skin_tone'] = self.ask_question(
            image,
            "What is the person's skin tone?"
        )

        # Headwear - separate from hair
        features['headwear'] = self.ask_question(
            image,
            "Is the person wearing any headwear like a hat, helmet, crown, or headband? If yes, describe it. If no, say 'none'."
        )

        # Face accessories (sunglasses, visor, etc.)
        features['face_accessories'] = self.ask_question(
            image,
            "Is the person wearing sunglasses, glasses, a visor, or any face accessories? Describe them or say 'none'."
        )

        # Other accessories
        features['other_accessories'] = self.ask_question(
            image,
            "What accessories is the person wearing? Look for earrings, necklaces, ties, or other items. Say 'none' if there are no accessories."
        )

        # Background
        features['background'] = self.ask_question(
            image,
            "Describe the background. Is it a solid color, gradient, pattern, or something else?"
        )

        print("Feature detection complete!")
        return features


class TraitVocabularyMapper:
    """
    Maps BLIP-2 outputs to training vocabulary using fuzzy matching.

    Uses the comprehensive trait vocabulary extracted from manually curated captions
    to ensure generated prompts use terms the model was trained on.
    """

    def __init__(self, vocab_json_path="bespoke_trait_vocabulary.json"):
        """Load trait vocabulary from JSON"""
        with open(vocab_json_path, 'r') as f:
            self.vocabulary = json.load(f)

        print(f"Loaded trait vocabulary:")
        for category, traits in self.vocabulary.items():
            print(f"  - {category}: {len(traits)} unique values")

    def fuzzy_match(self, text, category, threshold=0.6, n=3):
        """
        Fuzzy match text to vocabulary terms in a category.

        Args:
            text: Input text from BLIP-2
            category: Vocabulary category (hair, eyes, skin_tone, etc.)
            threshold: Minimum similarity score (0-1)
            n: Number of matches to return

        Returns:
            List of matching vocabulary terms
        """
        if category not in self.vocabulary:
            return []

        vocab_terms = self.vocabulary[category]

        # Try exact substring matching first
        text_lower = text.lower()
        exact_matches = [term for term in vocab_terms if term.lower() in text_lower]

        if exact_matches:
            return exact_matches[:n]

        # Fall back to difflib fuzzy matching
        matches = get_close_matches(text_lower, [t.lower() for t in vocab_terms], n=n, cutoff=threshold)

        # Map back to original case
        result = []
        for match in matches:
            for term in vocab_terms:
                if term.lower() == match:
                    result.append(term)
                    break

        return result

    def extract_hair_traits(self, hair_description):
        """Extract hair color and style from BLIP-2 description"""
        # Common hair colors to detect
        colors = ['black', 'brown', 'blonde', 'white', 'gray', 'grey', 'red',
                  'blue', 'green', 'purple', 'pink', 'orange', 'yellow']

        detected_color = None
        for color in colors:
            if color in hair_description.lower():
                detected_color = color
                break

        # Try to match to vocabulary
        matches = self.fuzzy_match(hair_description, 'hair', threshold=0.4, n=5)

        if matches:
            return matches[0]  # Best match

        # Fallback: construct from detected color
        if detected_color:
            # Look for style keywords
            if 'pixelated' in hair_description.lower() or 'pixel' in hair_description.lower():
                return f"{detected_color} pixelated hair"
            elif 'wavy' in hair_description.lower():
                return f"{detected_color} wavy hair"
            elif 'curly' in hair_description.lower():
                return f"{detected_color} curly hair"
            elif 'braid' in hair_description.lower():
                return f"{detected_color} braided hair"
            else:
                return f"{detected_color} hair"

        return "brown hair"  # Default fallback

    def extract_eye_color(self, eye_description):
        """Extract eye color from BLIP-2 description"""
        matches = self.fuzzy_match(eye_description, 'eyes', threshold=0.5, n=1)

        if matches:
            return matches[0]

        # Fallback to direct color extraction
        colors = ['brown', 'blue', 'green', 'gray', 'grey', 'black', 'hazel']
        for color in colors:
            if color in eye_description.lower():
                return f"{color} eyes"

        return "brown eyes"  # Default

    def extract_skin_tone(self, skin_description):
        """Extract skin tone from BLIP-2 description"""
        matches = self.fuzzy_match(skin_description, 'skin_tone', threshold=0.5, n=1)

        if matches:
            return matches[0]

        # Fallback to common terms
        skin_lower = skin_description.lower()
        if 'dark' in skin_lower or 'deep' in skin_lower:
            return "dark skin"
        elif 'tan' in skin_lower or 'medium' in skin_lower:
            return "tan skin"
        elif 'light' in skin_lower or 'pale' in skin_lower:
            return "light skin"

        return "light skin"  # Default

    def extract_headwear(self, headwear_description):
        """Extract headwear from BLIP-2 description"""
        if 'none' in headwear_description.lower() or 'not' in headwear_description.lower():
            return None

        matches = self.fuzzy_match(headwear_description, 'headwear', threshold=0.4, n=1)

        if matches:
            return matches[0]

        # Fallback to keyword detection
        hw_lower = headwear_description.lower()
        if 'helmet' in hw_lower:
            return "helmet"
        elif 'hat' in hw_lower:
            return "hat"
        elif 'crown' in hw_lower:
            return "crown"
        elif 'cap' in hw_lower:
            return "cap"

        return None

    def extract_accessories(self, face_acc_description, other_acc_description):
        """Extract accessories from BLIP-2 descriptions"""
        accessories = []

        # Face accessories
        if 'sunglasses' in face_acc_description.lower():
            # Check for gold/black/etc variants
            if 'gold' in face_acc_description.lower():
                accessories.append("gold sunglasses")
            elif 'black' in face_acc_description.lower():
                accessories.append("black sunglasses")
            else:
                accessories.append("sunglasses")
        elif 'glasses' in face_acc_description.lower():
            accessories.append("glasses")
        elif 'visor' in face_acc_description.lower():
            accessories.append("visor")

        # Other accessories
        other_lower = other_acc_description.lower()
        if 'earring' in other_lower:
            if 'gold' in other_lower or 'hoop' in other_lower:
                accessories.append("gold earrings")
            else:
                accessories.append("earrings")

        if 'necklace' in other_lower:
            accessories.append("necklace")

        if 'tie' in other_lower:
            accessories.append("tie")

        # Try fuzzy matching for any we didn't catch
        for desc in [face_acc_description, other_acc_description]:
            matches = self.fuzzy_match(desc, 'accessories', threshold=0.5, n=2)
            for match in matches:
                if match not in accessories:
                    accessories.append(match)

        return accessories


class HybridPromptGenerator:
    """
    Generates training-format prompts by combining:
    1. Color palette extraction (V2) for background colors
    2. BLIP-2 vision model (V3) for semantic features
    3. Trait vocabulary mapping for accurate terminology
    """

    def __init__(self, vocab_json_path="bespoke_trait_vocabulary.json"):
        """Initialize hybrid generator"""
        self.vision_detector = VisionFeatureDetector()
        self.vocab_mapper = TraitVocabularyMapper(vocab_json_path)

    def generate(self, image_path):
        """
        Generate training-format prompt from image.

        Returns dict with:
        - prompt: Complete training-format prompt
        - metadata: Breakdown of detected features
        """
        print(f"\n{'='*60}")
        print(f"V3 HYBRID GENERATION: {image_path}")
        print(f"{'='*60}\n")

        # Step 1: Extract color palette (V2 approach for background)
        print("Step 1: Extracting color palette...")
        extractor = ColorPaletteExtractor(image_path)
        palette = extractor.get_color_palette(n_colors=12)
        background = extractor.detect_background()

        print(f"Background: {background['name']} ({background['hex']})")

        # Step 2: Detect features with BLIP-2
        print("\nStep 2: Detecting features with BLIP-2...")
        vision_features = self.vision_detector.detect_features(image_path)

        print("\nBLIP-2 Outputs:")
        for key, value in vision_features.items():
            print(f"  {key}: {value}")

        # Step 3: Map to training vocabulary
        print("\nStep 3: Mapping to training vocabulary...")
        hair = self.vocab_mapper.extract_hair_traits(vision_features['hair_description'])
        eyes = self.vocab_mapper.extract_eye_color(vision_features['eye_color'])
        skin = self.vocab_mapper.extract_skin_tone(vision_features['skin_tone'])
        headwear = self.vocab_mapper.extract_headwear(vision_features['headwear'])
        accessories = self.vocab_mapper.extract_accessories(
            vision_features['face_accessories'],
            vision_features['other_accessories']
        )

        print(f"\nMapped Traits:")
        print(f"  Hair: {hair}")
        print(f"  Eyes: {eyes}")
        print(f"  Skin: {skin}")
        print(f"  Headwear: {headwear if headwear else 'none'}")
        print(f"  Accessories: {accessories if accessories else 'none'}")

        # Step 4: Detect background pattern from vision model
        bg_description = vision_features['background'].lower()
        if 'gradient' in bg_description or 'fade' in bg_description:
            bg_pattern = "gradient"
        elif 'stripe' in bg_description or 'striped' in bg_description:
            bg_pattern = "striped"
        elif 'check' in bg_description:
            bg_pattern = "checkered"
        elif 'split' in bg_description:
            bg_pattern = "split"
        else:
            bg_pattern = "solid"

        # Step 5: Build training-format prompt
        print("\nStep 4: Building training-format prompt...")

        prompt_parts = [
            "pixel art",
            "24x24",
            "portrait of bespoke punk",
            f"{background['name']} {bg_pattern} background ({background['hex']})",
            hair,
            eyes,
            skin
        ]

        # Add headwear if detected
        if headwear:
            prompt_parts.append(f"wearing {headwear}")

        # Add accessories if detected
        for acc in accessories:
            prompt_parts.append(f"wearing {acc}")

        # Add style markers
        prompt_parts.extend([
            "sharp pixel edges",
            "hard color borders"
        ])

        prompt = ", ".join(prompt_parts)

        # Metadata for display
        metadata = {
            'background': f"{background['name']} {bg_pattern} ({background['hex']})",
            'hair': hair,
            'eyes': eyes,
            'skin': skin,
            'headwear': headwear if headwear else 'none',
            'accessories': accessories if accessories else [],
            'color_palette': [c['name'] for c in palette[:5]]
        }

        print(f"\n{'='*60}")
        print("GENERATED PROMPT:")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return {
            'prompt': prompt,
            'metadata': metadata,
            'vision_raw': vision_features
        }


# Convenience wrapper for full pipeline
class BespokePunkGeneratorV3:
    """
    Complete V3 generation pipeline:
    1. Hybrid prompt generation (color + vision)
    2. LoRA generation at 512×512
    3. Downscale to 24×24
    """

    def __init__(self, lora_path, vocab_json_path="bespoke_trait_vocabulary.json"):
        """Initialize V3 generator"""
        self.prompt_generator = HybridPromptGenerator(vocab_json_path)
        self.image_generator = BespokePunkGenerator(lora_path)

    def generate_from_image(self, image_path, num_inference_steps=30, guidance_scale=7.5):
        """
        Generate Bespoke Punk from uploaded image.

        Returns:
        - image_512: 512×512 generated image
        - image_24: 24×24 pixel art
        - prompt: Generated prompt
        - metadata: Feature breakdown
        """
        # Generate prompt with hybrid approach
        result = self.prompt_generator.generate(image_path)
        prompt = result['prompt']
        metadata = result['metadata']

        # Generate with LoRA
        print("Generating 512×512 image with LoRA...")
        image_512 = self.image_generator.generate(
            prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        )

        # Downscale to 24×24
        print("Downscaling to 24×24...")
        image_24 = self.image_generator.downscale_to_24x24(image_512)

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
    print("BESPOKE PUNK GENERATOR V3 - HYBRID VISION MODEL")
    print("="*60)
    print()

    if len(sys.argv) < 2:
        print("Usage: python bespoke_punk_generator_v3.py <image_path>")
        print()
        print("Example:")
        print("  python bespoke_punk_generator_v3.py FORTRAINING6/bespokepunks/lady_050_x-6.png")
        sys.exit(1)

    image_path = sys.argv[1]
    lora_path = "Context 1106/bespoke_punks_sd15_512-000002.safetensors"

    # Initialize V3 generator
    generator = BespokePunkGeneratorV3(lora_path)

    # Generate
    result = generator.generate_from_image(image_path)

    # Save outputs
    output_512_path = "test_v3_output_512.png"
    output_24_path = "test_v3_output_24.png"

    result['image_512'].save(output_512_path)
    result['image_24'].save(output_24_path)

    print()
    print("="*60)
    print("OUTPUTS SAVED:")
    print("="*60)
    print(f"512×512: {output_512_path}")
    print(f"24×24:   {output_24_path}")
    print()

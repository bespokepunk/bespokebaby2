#!/usr/bin/env python3
"""
BESPOKE PUNK GENERATOR - Luxury Edition
Saks Fifth Avenue / Rodeo Drive Level Experience

Features:
- Enhanced auto-detection (glasses, earrings, expression, facial hair)
- Luxury à la carte trait selection (21 exclusive accessories)
- Elegant, world-class UI
- One-of-a-kind NFT experience
"""

import gradio as gr
from user_to_bespoke_punk_PRODUCTION import UserToBespokePunkPipeline
from PIL import Image
import os

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

# Feature visibility config - only show features with ≥70% accuracy
SHOW_FEATURES = {
    'hair_color': True,       # High accuracy
    'eye_color': True,        # High accuracy
    'skin_tone': True,        # High accuracy
    'background_color': True, # High accuracy
    'eyewear': True,          # 80.6% accuracy ✅
    'earrings': True,         # 100% accuracy ✅
    'expression': False,      # 50.2% accuracy ❌ UNRELIABLE
    'hairstyle': False,       # 28.9% accuracy ❌ UNRELIABLE
    'facial_hair': True,      # Decent accuracy
}

print("🎨 Initializing Bespoke Punk Generator...")
print("   This may take a minute on first run (downloading SD 1.5)...")

# Initialize pipeline with CAPTION_FIX Epoch 8
pipeline = UserToBespokePunkPipeline(
    lora_path="lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors"
)

print("✅ Pipeline ready!")
print()

# ============================================================================
# À LA CARTE TRAIT CATALOG
# ============================================================================

TRAIT_CATALOG = {
    "👑 Royal & Fantasy": {
        "crown": "Golden Crown with Gems",
        "tiara": "Pearl Diamond Tiara",
        "flower_crown": "Golden Flower Crown",
        "angel_wings": "Teal Angel Wings",
    },

    "🎀 Hair Accessories": {
        "bow_pink_red": "Pink & Red Bow",
        "bow_bitcoin": "Bitcoin Orange Bow",
        "bow_ethereum": "Ethereum Colored Bow",
        "bow_blue": "Large Blue Ribbon",
        "flower_in_hair": "Flower in Hair (Winehouse)",
    },

    "👓 Special Eyewear": {
        "party_glasses": "Translucent Party Glasses",
        "mog_goggles": "Cyberpunk Mog Goggles",
    },

    "🎩 Exclusive Hats": {
        "top_hat": "Fancy Top Hat",
        "wizard_hat": "Epic Wizard Hat",
        "fedora": "Classic Fedora",
    },

    "🎪 Headbands & Ears": {
        "bandana_orange": "Orange Polka Dot Bandana (1940s)",
        "bandana_red": "Red Polka Dot Bandana (1940s)",
        "cat_ears": "Cat Ears Headband",
    },

    "💎 Jewelry": {
        "gold_chain": "Thick Gold Chain",
        "diamond_pendant": "Diamond Pendant Necklace",
    },

    "🌟 Signature Touches": {
        "joint": "Joint with Smoke",
    },
}

# ============================================================================
# GENERATION FUNCTION
# ============================================================================

def generate_bespoke_punk(image, gender, selected_traits):
    """
    Generate bespoke punk from user photo + selected traits

    Args:
        image: PIL Image from upload
        gender: "Lady" or "Lad"
        selected_traits: List of selected trait IDs from checkboxes

    Returns:
        (punk_512, punk_24, features_md, prompt_used)
    """

    if image is None:
        return None, None, "⚠️ Please upload a photo first", ""

    # Save uploaded image temporarily
    temp_path = "/tmp/user_photo_temp.jpg"
    image.save(temp_path)

    # Map gender
    gender_mapped = gender.lower()  # "Lady" → "lady", "Lad" → "lad"

    # Generate with à la carte traits
    punk_512, punk_24, features, prompt = pipeline.generate_with_alacarte(
        user_image_path=temp_path,
        gender=gender_mapped,
        alacarte_traits=selected_traits if selected_traits else []
    )

    # Format detected features for display (only show reliable features ≥70%)
    feature_lines = []

    if SHOW_FEATURES['hair_color']:
        feature_lines.append(f"- 💇 Hair: `{features.get('hair_color', 'unknown')}`")
    if SHOW_FEATURES['eye_color']:
        feature_lines.append(f"- 👁️ Eyes: `{features.get('eye_color', 'unknown')}`")
    if SHOW_FEATURES['skin_tone']:
        feature_lines.append(f"- 🎨 Skin: `{features.get('skin_tone', 'unknown')}`")
    if SHOW_FEATURES['background_color']:
        feature_lines.append(f"- 🖼️ Background: `{features.get('background_color', 'unknown')}`")
    if SHOW_FEATURES['eyewear']:
        feature_lines.append(f"- 👓 Eyewear: `{features.get('eyewear', 'none')}`")
    if SHOW_FEATURES['earrings']:
        feature_lines.append(f"- 💍 Earrings: `{features.get('earring_type', 'none')}`")
    if SHOW_FEATURES['expression']:
        feature_lines.append(f"- 😊 Expression: `{features.get('expression', 'neutral')}`")
    if SHOW_FEATURES['hairstyle'] and 'hairstyle' in features:
        feature_lines.append(f"- 💈 Hairstyle: `{features.get('hairstyle', 'unknown')}`")
    if SHOW_FEATURES['facial_hair']:
        feature_lines.append(f"- 🧔 Facial Hair: `{features.get('facial_hair', 'none')}`")

    features_md = f"""
### ✨ Auto-Detected Features (≥70% accuracy)

{chr(10).join(feature_lines)}

{f"**À La Carte Selected:** {len(selected_traits)} trait(s)" if selected_traits else ""}

*Note: We only show features with validated accuracy ≥70%*
"""

    return punk_512, punk_24, features_md, f"```\n{prompt}\n```"


# Update pipeline to support à la carte
def add_alacarte_method():
    """Add à la carte generation method to pipeline"""

    def generate_with_alacarte(self, user_image_path, gender="lady", alacarte_traits=None, seed=None):
        """Generate with à la carte trait selection"""

        # Extract features
        from enhanced_feature_extraction_module import EnhancedFeatureExtractor
        extractor = EnhancedFeatureExtractor(user_image_path)
        all_features = extractor.extract_all_features()

        features = {
            'hair_color': all_features['hair_color'],
            'eye_color': all_features['eye_color'],
            'skin_tone': all_features['skin_tone'],
            'background_color': all_features['background_color'],
            'eyewear': all_features['eyewear'],
            'earrings': all_features['earrings'],
            'earring_type': all_features['earring_type'],
            'expression': all_features['expression'],
            'facial_hair': all_features['facial_hair'],
        }

        # Generate prompt with à la carte
        prompt = self.prompt_builder.generate(features, gender=gender, alacarte_traits=alacarte_traits)

        # Generate images
        image_512 = self.generator.generate(prompt, seed=seed)
        image_24 = self.generator.downscale_to_24x24(image_512)

        return image_512, image_24, features, prompt

    UserToBespokePunkPipeline.generate_with_alacarte = generate_with_alacarte

# Add method to pipeline
add_alacarte_method()

# ============================================================================
# LUXURY GRADIO UI
# ============================================================================

# Custom CSS for elegant, Saks Fifth Avenue vibe
custom_css = """
/* Saks Fifth Avenue / Rodeo Drive Luxury Theme */

.gradio-container {
    font-family: 'Helvetica Neue', 'Arial', sans-serif !important;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
}

.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #d4af37 0%, #f4e4c1 50%, #d4af37 100%);
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(212, 175, 55, 0.3);
}

.main-header h1 {
    font-size: 2.5rem;
    font-weight: 300;
    letter-spacing: 3px;
    color: #1a1a1a;
    margin: 0;
    text-transform: uppercase;
}

.main-header p {
    font-size: 1.1rem;
    color: #3a3a3a;
    font-style: italic;
    margin-top: 0.5rem;
    letter-spacing: 1px;
}

.trait-category {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.trait-category:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(212, 175, 55, 0.4);
    box-shadow: 0 4px 16px rgba(212, 175, 55, 0.2);
}

.trait-category h3 {
    color: #d4af37;
    font-weight: 300;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    font-size: 1.2rem;
}

button.primary {
    background: linear-gradient(135deg, #d4af37 0%, #f4e4c1 50%, #d4af37 100%) !important;
    color: #1a1a1a !important;
    font-weight: 500 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(212, 175, 55, 0.4) !important;
    transition: all 0.3s ease !important;
}

button.primary:hover {
    box-shadow: 0 6px 24px rgba(212, 175, 55, 0.6) !important;
    transform: translateY(-2px) !important;
}

.image-container {
    border: 2px solid rgba(212, 175, 55, 0.3);
    border-radius: 12px;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.03);
}

.features-display {
    background: rgba(212, 175, 55, 0.1);
    border-left: 4px solid #d4af37;
    padding: 1.5rem;
    border-radius: 8px;
    color: #f0f0f0;
    font-size: 0.95rem;
    line-height: 1.8;
}
"""

# Build the interface
with gr.Blocks(css=custom_css, title="Bespoke Punk Generator - Luxury Edition", theme=gr.themes.Soft()) as demo:

    # Header
    gr.HTML("""
        <div class="main-header">
            <h1>✨ Bespoke Punk Generator ✨</h1>
            <p>Craft Your Masterpiece</p>
        </div>
    """)

    with gr.Row():
        # LEFT COLUMN: Upload & Generation
        with gr.Column(scale=1):
            gr.Markdown("### 📸 Your Portrait")
            input_image = gr.Image(
                label="Upload Photo",
                type="pil",
                sources=["upload"],
                elem_classes=["image-container"]
            )

            gender = gr.Radio(
                choices=["Lady", "Lad"],
                value="Lady",
                label="Punk Type",
                info="Select your punk persona"
            )

            gr.Markdown("---")

            gr.Markdown("### 🎨 Your Bespoke Punk")
            output_512 = gr.Image(
                label="Full Resolution (512x512)",
                elem_classes=["image-container"]
            )
            output_24 = gr.Image(
                label="NFT (24x24 Pixel Art)",
                elem_classes=["image-container"]
            )

        # RIGHT COLUMN: À La Carte Selection
        with gr.Column(scale=1):
            gr.Markdown("### ✨ Enhance Your Punk")
            gr.Markdown("*Select exclusive accessories to customize your masterpiece*")
            gr.Markdown("---")

            # Create checkboxes for each category
            all_trait_checkboxes = []

            with gr.Accordion("👑 Royal & Fantasy", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["👑 Royal & Fantasy"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("🎀 Hair Accessories", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["🎀 Hair Accessories"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("👓 Special Eyewear", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["👓 Special Eyewear"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("🎩 Exclusive Hats", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["🎩 Exclusive Hats"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("🎪 Headbands & Ears", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["🎪 Headbands & Ears"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("💎 Jewelry", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["💎 Jewelry"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            with gr.Accordion("🌟 Signature Touches", open=False):
                for trait_id, trait_name in TRAIT_CATALOG["🌟 Signature Touches"].items():
                    checkbox = gr.Checkbox(label=trait_name, value=False, info=trait_id)
                    all_trait_checkboxes.append((trait_id, checkbox))

            gr.Markdown("---")

            generate_btn = gr.Button(
                "✨ Craft Your Punk ✨",
                variant="primary",
                size="lg",
                elem_classes=["primary"]
            )

    # Bottom: Features & Prompt
    with gr.Row():
        detected_features = gr.Markdown(
            "### 🔍 Detected Features\n*Upload a photo to see auto-detected features*",
            elem_classes=["features-display"]
        )
        prompt_display = gr.Textbox(
            label="Generated Prompt",
            lines=5,
            max_lines=10,
            interactive=False
        )

    # Tips section
    gr.Markdown("""
    ---
    ### 💡 Tips for Best Results:

    - **Clear Photos:** Use front-facing photos with good lighting
    - **Visible Features:** Make sure face is clearly visible
    - **Accessories:** Glasses and earrings will be auto-detected
    - **Expression:** Your smile or neutral expression will be captured
    - **Mix & Match:** Try combining different à la carte traits
    - **Experiment:** Generate multiple times with different accessories
    """)

    # Connect generation function
    def generate_wrapper(image, gender, *checkbox_values):
        """Wrapper to collect selected traits from checkboxes"""
        selected_traits = []
        for i, (trait_id, _) in enumerate(all_trait_checkboxes):
            if checkbox_values[i]:
                selected_traits.append(trait_id)

        return generate_bespoke_punk(image, gender, selected_traits)

    # Get all checkbox components
    checkbox_components = [cb for _, cb in all_trait_checkboxes]

    generate_btn.click(
        fn=generate_wrapper,
        inputs=[input_image, gender] + checkbox_components,
        outputs=[output_512, output_24, detected_features, prompt_display]
    )

# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🚀 LAUNCHING BESPOKE PUNK GENERATOR WEB INTERFACE")
    print("="*70)
    print()
    print("📌 The app will open in your browser automatically")
    print("📌 URL: http://127.0.0.1:7863")
    print()
    print("To stop the server: Press Ctrl+C")
    print("="*70)
    print()

    demo.launch(
        share=False,  # Set to True to get a public URL
        server_name="127.0.0.1",
        server_port=7863,  # Different port for luxury version
        show_error=True
    )

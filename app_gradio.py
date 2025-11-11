#!/usr/bin/env python3
"""
Gradio Web Interface for Bespoke Punk Generator
Powered by SD 1.5 CAPTION_FIX Epoch 8 LoRA (216.6 avg colors - cleanest)
"""

import gradio as gr
from user_to_bespoke_punk_PRODUCTION import UserToBespokePunkPipeline
from pathlib import Path
import tempfile
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

LORA_PATH = "lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors"

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

# Check if LoRA exists
if not Path(LORA_PATH).exists():
    print(f"⚠️  WARNING: LoRA not found at {LORA_PATH}")
    print("    Please update LORA_PATH in this file or download CAPTION_FIX Epoch 8!")

# Initialize pipeline (loads model once)
print("🎨 Initializing Bespoke Punk Generator...")
print("   This may take a minute on first run (downloading SD 1.5)...")

try:
    pipeline = UserToBespokePunkPipeline(LORA_PATH)
    print("✅ Pipeline ready!")
except Exception as e:
    print(f"❌ Error loading pipeline: {e}")
    pipeline = None

# ============================================================================
# GENERATION FUNCTION
# ============================================================================

def generate_punk(image, gender, seed, use_seed):
    """
    Generate initial bespoke punk from uploaded image (auto-detect only)

    Args:
        image: PIL Image from Gradio
        gender: "Lady" or "Lad"
        seed: Random seed (integer)
        use_seed: Whether to use the seed

    Returns:
        tuple: (image_512, image_24, prompt, features_text)
    """

    if pipeline is None:
        return None, None, "❌ Pipeline not initialized. Check LoRA path!", ""

    if image is None:
        return None, None, "❌ Please upload an image first!", ""

    try:
        # Save uploaded image to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        # Convert gender
        gender_lower = gender.lower()

        # Use seed if checkbox is checked
        actual_seed = int(seed) if use_seed else None

        # Generate with auto-detection only
        result = pipeline.process(
            user_image_path=temp_path,
            gender=gender_lower,
            seed=actual_seed
        )

        # Clean up temp file
        os.unlink(temp_path)

        # Format features for display (only show reliable features ≥70%)
        features = result['features']
        feature_lines = []

        if SHOW_FEATURES['hair_color']:
            feature_lines.append(f"- 💇 Hair: {features['hair_color']}")
        if SHOW_FEATURES['eye_color']:
            feature_lines.append(f"- 👁️ Eyes: {features['eye_color']}")
        if SHOW_FEATURES['skin_tone']:
            feature_lines.append(f"- 🎨 Skin: {features['skin_tone']}")
        if SHOW_FEATURES['background_color']:
            feature_lines.append(f"- 🖼️ Background: {features['background_color']}")
        if SHOW_FEATURES['eyewear']:
            feature_lines.append(f"- 👓 Eyewear: {features.get('eyewear', 'none')}")
        if SHOW_FEATURES['earrings']:
            feature_lines.append(f"- 💍 Earrings: {features.get('earring_type', 'none')}")
        if SHOW_FEATURES['expression']:
            feature_lines.append(f"- 😊 Expression: {features.get('expression', 'neutral')}")
        if SHOW_FEATURES['hairstyle'] and 'hairstyle' in features:
            feature_lines.append(f"- 💈 Hairstyle: {features.get('hairstyle', 'unknown')}")
        if SHOW_FEATURES['facial_hair']:
            feature_lines.append(f"- 🧔 Facial Hair: {features.get('facial_hair', 'none')}")

        features_text = "**✨ Auto-Detected Features** (≥70% accuracy):\n" + "\n".join(feature_lines)
        features_text += "\n\n*Note: We only show features with validated accuracy ≥70%*"

        # Return results
        return (
            result['image_512'],
            result['image_24'],
            result['prompt'],
            features_text
        )

    except Exception as e:
        error_msg = f"❌ Error generating punk: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None, None, error_msg, ""


def regenerate_with_traits(image, gender, seed, use_seed,
                           crown, tiara, flower_crown, angel_wings,
                           bow_pink, bow_bitcoin, bow_ethereum, bow_blue, flower_hair,
                           top_hat, wizard_hat, fedora, cat_ears, bandana_orange,
                           gold_chain, diamond_pendant, joint):
    """
    Regenerate punk with selected à la carte traits

    Args:
        image: PIL Image from Gradio
        gender: "Lady" or "Lad"
        seed: Random seed (integer)
        use_seed: Whether to use the seed
        crown...joint: Boolean checkboxes for à la carte traits

    Returns:
        tuple: (image_512, image_24, prompt, features_text)
    """

    if pipeline is None:
        return None, None, "❌ Pipeline not initialized. Check LoRA path!", ""

    if image is None:
        return None, None, "❌ Please upload an image first!", ""

    try:
        # Save uploaded image to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        # Convert gender
        gender_lower = gender.lower()

        # Use seed if checkbox is checked
        actual_seed = int(seed) if use_seed else None

        # Collect selected à la carte traits
        trait_mapping = {
            'crown': crown,
            'tiara': tiara,
            'flower_crown': flower_crown,
            'angel_wings': angel_wings,
            'bow_pink_red': bow_pink,
            'bow_bitcoin': bow_bitcoin,
            'bow_ethereum': bow_ethereum,
            'bow_blue': bow_blue,
            'flower_in_hair': flower_hair,
            'top_hat': top_hat,
            'wizard_hat': wizard_hat,
            'fedora': fedora,
            'cat_ears': cat_ears,
            'bandana_orange': bandana_orange,
            'gold_chain': gold_chain,
            'diamond_pendant': diamond_pendant,
            'joint': joint,
        }

        selected_traits = [trait_id for trait_id, is_selected in trait_mapping.items() if is_selected]

        if not selected_traits:
            return None, None, "⚠️ Please select at least one à la carte trait to add!", ""

        # Generate with à la carte!
        result = pipeline.process(
            user_image_path=temp_path,
            gender=gender_lower,
            seed=actual_seed,
            alacarte_traits=selected_traits
        )

        # Clean up temp file
        os.unlink(temp_path)

        # Format features for display
        features = result['features']
        features_text = f"""**✨ Auto-Detected Features:**
- 💇 Hair: {features['hair_color']}
- 👁️ Eyes: {features['eye_color']}
- 🎨 Skin: {features['skin_tone']}
- 🖼️ Background: {features['background_color']}
- 👓 Eyewear: {features.get('eyewear', 'none')}
- 💍 Earrings: {features.get('earring_type', 'none')}
- 😊 Expression: {features.get('expression', 'neutral')}
- 🧔 Facial Hair: {features.get('facial_hair', 'none')}

**✨ À La Carte Added:**
- {', '.join(selected_traits)}
"""

        # Return results
        return (
            result['image_512'],
            result['image_24'],
            result['prompt'],
            features_text
        )

    except Exception as e:
        error_msg = f"❌ Error generating punk: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None, None, error_msg, ""

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

# Custom CSS
custom_css = """
.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}

.output-section {
    border: 2px solid #667eea;
    border-radius: 10px;
    padding: 15px;
    margin-top: 10px;
}

.pixel-art {
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
}
"""

# Create interface
with gr.Blocks(css=custom_css, title="Bespoke Punk Generator") as demo:

    # Header
    gr.HTML("""
        <div class="header">
            <h1>🎨 Bespoke Punk NFT Generator</h1>
            <p>Upload your photo → Get your unique Bespoke Punk!</p>
            <p style="font-size: 0.9em; opacity: 0.9;">
                Powered by CAPTION_FIX Epoch 8 LoRA (Cleanest: 216.6 colors)
            </p>
        </div>
    """)

    with gr.Row():
        # Left column: Input
        with gr.Column(scale=1):
            gr.Markdown("### 📸 Upload Your Photo")

            input_image = gr.Image(
                label="Your Photo",
                type="pil",
                height=400
            )

            gender = gr.Radio(
                choices=["Lady", "Lad"],
                value="Lady",
                label="Punk Gender"
            )

            with gr.Accordion("⚙️ Advanced Settings", open=False):
                use_seed = gr.Checkbox(
                    label="Use fixed seed (reproducible results)",
                    value=False
                )
                seed = gr.Number(
                    label="Random Seed",
                    value=42,
                    precision=0,
                    info="Same seed = same output"
                )

            generate_btn = gr.Button(
                "✨ Generate Bespoke Punk",
                variant="primary",
                size="lg"
            )

            gr.Markdown("""
            ---
            **Tips:**
            - Use clear, front-facing photos
            - Make sure face is visible
            - Good lighting helps!
            """)

        # Right column: Output
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 Your Bespoke Punk")

            output_512 = gr.Image(
                label="512x512 (Full Resolution)",
                height=300
            )

            output_24 = gr.Image(
                label="24x24 (NFT - Pixel Art)",
                height=200,
                elem_classes=["pixel-art"]
            )

            gr.Markdown("### 📝 Generation Details")

            features_display = gr.Markdown(
                label="Detected Features"
            )

            prompt_display = gr.Textbox(
                label="Generated Prompt",
                lines=4,
                max_lines=6
            )

    # À La Carte Section (appears after initial generation)
    gr.Markdown("---")
    gr.Markdown("## ✨ Add À La Carte Accessories")
    gr.Markdown("*After seeing your initial punk, select exclusive traits below to regenerate with custom accessories!*")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion("👑 Royal & Fantasy", open=False):
                crown = gr.Checkbox(label="Golden Crown", value=False)
                tiara = gr.Checkbox(label="Pearl Tiara", value=False)
                flower_crown = gr.Checkbox(label="Flower Crown", value=False)
                angel_wings = gr.Checkbox(label="Angel Wings", value=False)

            with gr.Accordion("🎀 Hair Accessories", open=False):
                bow_pink = gr.Checkbox(label="Pink & Red Bow", value=False)
                bow_bitcoin = gr.Checkbox(label="Bitcoin Bow", value=False)
                bow_ethereum = gr.Checkbox(label="Ethereum Bow", value=False)
                bow_blue = gr.Checkbox(label="Blue Ribbon", value=False)
                flower_hair = gr.Checkbox(label="Flower in Hair", value=False)

        with gr.Column(scale=1):
            with gr.Accordion("🎩 Special Hats & Headwear", open=False):
                top_hat = gr.Checkbox(label="Fancy Top Hat", value=False)
                wizard_hat = gr.Checkbox(label="Wizard Hat", value=False)
                fedora = gr.Checkbox(label="Fedora", value=False)
                cat_ears = gr.Checkbox(label="Cat Ears", value=False)
                bandana_orange = gr.Checkbox(label="Orange Bandana", value=False)

            with gr.Accordion("💎 Jewelry & More", open=False):
                gold_chain = gr.Checkbox(label="Gold Chain", value=False)
                diamond_pendant = gr.Checkbox(label="Diamond Pendant", value=False)
                joint = gr.Checkbox(label="Joint with Smoke", value=False)

    regenerate_btn = gr.Button(
        "🎨 Regenerate with Selected Traits",
        variant="secondary",
        size="lg"
    )

    # Examples section
    gr.Markdown("---")
    gr.Markdown("### 💡 Example Results")
    gr.Markdown("""
    Your generated punk will have:
    - ✅ Accurate eye color (brown = brown!)
    - ✅ Matching hair color from your photo
    - ✅ Clean pixel art style
    - ✅ 12-15 colors in final 24x24 NFT
    - ✅ Solid color background
    """)

    gr.Markdown("---")
    gr.Markdown("### 🔗 Related Tools")
    gr.HTML("""
    <div style="background: #2a2a2a; padding: 15px; border-radius: 8px;">
        <p style="margin-bottom: 10px;">📝 <strong>Review Training Captions</strong></p>
        <a href="SUPABASE_REVIEW.html" target="_blank" style="color: #00ff88; text-decoration: none;">
            → Open Supabase Caption Review Interface
        </a>
        <p style="font-size: 0.9em; color: #888; margin-top: 5px;">
            Review and edit the 203 training captions used for this model
        </p>
    </div>
    """)

    # Connect initial generation button (auto-detect only)
    generate_btn.click(
        fn=generate_punk,
        inputs=[input_image, gender, seed, use_seed],
        outputs=[output_512, output_24, prompt_display, features_display]
    )

    # Connect regenerate button (with à la carte traits)
    regenerate_btn.click(
        fn=regenerate_with_traits,
        inputs=[
            input_image, gender, seed, use_seed,
            crown, tiara, flower_crown, angel_wings,
            bow_pink, bow_bitcoin, bow_ethereum, bow_blue, flower_hair,
            top_hat, wizard_hat, fedora, cat_ears, bandana_orange,
            gold_chain, diamond_pendant, joint
        ],
        outputs=[output_512, output_24, prompt_display, features_display]
    )

# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 LAUNCHING BESPOKE PUNK GENERATOR WEB INTERFACE")
    print("="*70)
    print()
    print("📌 The app will open in your browser automatically")
    print("📌 URL: http://127.0.0.1:7861")
    print()
    print("To stop the server: Press Ctrl+C")
    print("="*70)
    print()

    demo.launch(
        share=False,  # Set to True to get a public URL
        server_name="127.0.0.1",
        server_port=7860,  # Using 7860 (default)
        show_error=True
    )

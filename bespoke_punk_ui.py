#!/usr/bin/env python3
"""
Bespoke Punk Generator UI - Interactive Web Interface

Upload any image and generate a personalized 24x24 Bespoke Punk!
"""

import gradio as gr
import os
from PIL import Image
import numpy as np
from bespoke_punk_generator_v2 import (
    TrainingVocabulary,
    ColorPaletteExtractor,
    TrainingFormatPromptGenerator,
    BespokePunkGenerator
)

# Global state to avoid reloading models
generator = None
vocab = None
prompt_gen = None


def initialize_models(lora_path="Context 1106/bespoke_punks_sd15_512-000002.safetensors"):
    """Initialize models once at startup"""
    global generator, vocab, prompt_gen

    if generator is None:
        print("Initializing models...")
        vocab = TrainingVocabulary()
        prompt_gen = TrainingFormatPromptGenerator(vocab)
        generator = BespokePunkGenerator(lora_path)
        print("Models ready!")

    return generator, vocab, prompt_gen


def format_color_palette_html(palette):
    """Format color palette as HTML for display"""
    html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;'>"

    for i, color in enumerate(palette[:8]):  # Show top 8 colors
        hex_color = color['hex']
        name = color['name']
        weight = color['weight'] * 100

        html += f"""
        <div style='text-align: center;'>
            <div style='
                width: 60px;
                height: 60px;
                background-color: {hex_color};
                border: 2px solid #333;
                border-radius: 8px;
                margin-bottom: 5px;
            '></div>
            <div style='font-size: 11px; max-width: 60px;'>
                <strong>{name}</strong><br/>
                {hex_color}<br/>
                {weight:.1f}%
            </div>
        </div>
        """

    html += "</div>"
    return html


def generate_bespoke_punk(input_image, num_steps, guidance_scale):
    """Main generation function"""

    if input_image is None:
        return None, None, "Please upload an image first!", None

    try:
        # Initialize models
        gen, vocab, prompt_gen = initialize_models()

        # Save uploaded image temporarily
        temp_path = "temp_upload.png"
        input_image.save(temp_path)

        # Step 1: Extract color palette
        extractor = ColorPaletteExtractor(temp_path)
        palette = extractor.get_color_palette(n_colors=12)
        background = extractor.detect_background()

        # Format palette for display
        palette_html = format_color_palette_html(palette)

        # Step 2: Generate prompt
        result = prompt_gen.generate(palette, background)
        prompt = result['prompt']
        metadata = result['metadata']

        # Format metadata for display
        metadata_text = f"""
**Generated Prompt:**
```
{prompt}
```

**Extracted Features:**
- Background: {metadata['background']}
- Hair: {metadata['hair']}
- Eyes: {metadata['eyes']}
- Skin: {metadata['skin']}
- Top 5 Colors: {', '.join(metadata['color_palette'])}
        """

        # Step 3: Generate Bespoke Punk (safety checker disabled by default)
        image_512 = gen.generate(prompt, num_steps, guidance_scale)
        image_24 = gen.downscale_to_24x24(image_512)

        # Clean up
        os.remove(temp_path)

        return image_512, image_24, metadata_text, palette_html

    except Exception as e:
        return None, None, f"Error: {str(e)}", None


def create_ui():
    """Create Gradio interface"""

    with gr.Blocks(title="Bespoke Punk Generator", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🎨 Bespoke Punk Generator V2

        Upload any image (avatar, photo, artwork) and generate a personalized 24×24 Bespoke Punk!

        The system extracts colors and features from your image and generates a unique pixel art character.
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Input")
                input_image = gr.Image(
                    label="Upload Your Image",
                    type="pil",
                    height=300
                )

                gr.Markdown("### ⚙️ Settings")
                num_steps = gr.Slider(
                    minimum=20,
                    maximum=50,
                    value=30,
                    step=1,
                    label="Inference Steps",
                    info="More steps = higher quality (slower)"
                )

                guidance_scale = gr.Slider(
                    minimum=5.0,
                    maximum=15.0,
                    value=7.5,
                    step=0.5,
                    label="Guidance Scale",
                    info="How closely to follow the prompt"
                )

                generate_btn = gr.Button(
                    "✨ Generate Bespoke Punk",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=2):
                gr.Markdown("### 🎨 Color Palette")
                palette_display = gr.HTML(label="Extracted Colors")

                gr.Markdown("### 📝 Generated Prompt & Features")
                metadata_display = gr.Markdown()

                gr.Markdown("### 🖼️ Output")
                with gr.Row():
                    output_512 = gr.Image(
                        label="512×512 (High-Res Preview)",
                        height=300
                    )
                    output_24 = gr.Image(
                        label="24×24 (Final Pixel Art)",
                        height=300,
                        image_mode="nearest"  # Nearest neighbor for pixel-perfect display
                    )

        gr.Markdown("""
        ---
        ### 💡 Tips:
        - **Best results**: Upload clear images with distinct colors
        - **Color extraction**: The system finds the 12 most common colors
        - **Feature mapping**: Colors are mapped to hair, eyes, skin based on training data
        - **NSFW Filter**: Disabled by default to avoid false positives

        ### 📊 How it works:
        1. **Color Analysis**: Extracts dominant colors using k-means clustering
        2. **Vocabulary Mapping**: Maps colors to training caption terms (hair colors, eye colors, etc.)
        3. **Prompt Generation**: Creates prompt in exact training format
        4. **LoRA Generation**: Generates 512×512 using trained LoRA
        5. **Downscaling**: Converts to 24×24 using nearest neighbor interpolation

        ### 🚀 Future Enhancements:
        - BLIP-2 or LLaVA vision models for better feature detection
        - Would understand "person wearing helmet" vs "person with hair"
        - Better accessory and trait detection
        """)

        # Connect the button
        generate_btn.click(
            fn=generate_bespoke_punk,
            inputs=[input_image, num_steps, guidance_scale],
            outputs=[output_512, output_24, metadata_display, palette_display]
        )

        # Add examples
        gr.Markdown("### 📸 Try these examples:")
        gr.Examples(
            examples=[
                ["FORTRAINING6/bespokepunks/lad_001_carbon.png", 30, 7.5],
                ["FORTRAINING6/bespokepunks/lady_001_hazelnut.png", 30, 7.5],
            ],
            inputs=[input_image, num_steps, guidance_scale],
            outputs=[output_512, output_24, metadata_display, palette_display],
            fn=generate_bespoke_punk,
            cache_examples=False
        )

    return demo


if __name__ == "__main__":
    print("=" * 60)
    print("BESPOKE PUNK GENERATOR UI")
    print("=" * 60)

    # Initialize models at startup
    initialize_models()

    # Create and launch UI
    demo = create_ui()
    demo.launch(
        share=False,  # Set to True to get public URL
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )

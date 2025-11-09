# Bespoke Punk Generator

Generate personalized 24×24 Bespoke Punk avatars from any image!

## How It Works

1. **Upload any image** (avatar, photo, artwork, etc.)
2. **AI analyzes** colors, tones, and features
3. **Generates prompt** based on extracted features
4. **Creates Bespoke Punk** at 512×512 using trained LoRA
5. **Downscales to 24×24** for pixel-perfect output

## Installation

```bash
# Activate your virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install torch torchvision diffusers transformers accelerate pillow scikit-learn
```

## Usage

### Basic Usage

```bash
python bespoke_punk_generator.py --input path/to/your/image.jpg --output my_punk.png
```

### Save Both 512×512 and 24×24

```bash
python bespoke_punk_generator.py --input avatar.jpg --output my_punk.png --save-512
```

### Custom Parameters

```bash
python bespoke_punk_generator.py \
  --input photo.jpg \
  --output custom_punk.png \
  --lora "Context 1106/bespoke_punks_sd15_512-000002.safetensors" \
  --steps 40 \
  --guidance 8.0 \
  --save-512
```

## Parameters

- `--input, -i` : Path to input image (required)
- `--output, -o` : Output filename (default: output_punk.png)
- `--lora` : Path to LoRA checkpoint (default: epoch 2 checkpoint)
- `--steps` : Number of inference steps (default: 30, higher = better quality)
- `--guidance` : Guidance scale (default: 7.5, higher = more prompt adherence)
- `--save-512` : Also save the 512×512 version

## Examples

### From a Photo

```bash
python bespoke_punk_generator.py --input ~/Downloads/selfie.jpg --output me_punk.png
```

**What it does:**
- Detects skin tone from photo
- Extracts dominant colors for background/clothes
- Identifies hair color
- Generates matching Bespoke Punk

### From an Avatar

```bash
python bespoke_punk_generator.py --input avatar.png --output punk_avatar.png --save-512
```

**What it does:**
- Analyzes avatar's color palette
- Detects background color
- Creates Bespoke Punk with similar vibe

### From Abstract Art

```bash
python bespoke_punk_generator.py --input artwork.jpg --output art_punk.png
```

**What it does:**
- Extracts dominant colors
- Uses them for Bespoke Punk palette
- Creates unique punk inspired by the art

## How Feature Extraction Works

### Color Detection
- Uses k-means clustering to find 5 dominant colors
- Converts RGB to human-readable color names (red, blue, green, etc.)
- Detects lightness/darkness (light blue, dark red, etc.)

### Background Detection
- Samples edge pixels (top, bottom, left, right)
- Finds most common edge color as background
- Falls back to most dominant color if edges are mixed

### Skin Tone Detection
- Analyzes top 3 dominant colors
- Matches to skin tone categories (light, medium, dark)
- Uses color hue/saturation to identify skin-like colors

### Hair Color Detection
- Looks for dark/saturated colors in top 4 colors
- Identifies common hair colors (black, brown, blonde, etc.)
- Detects unusual colors (blue, purple, green) for creative punks

## Output

The script generates:

**24×24 PNG** - Final Bespoke Punk avatar
- Pixel-perfect downscaling using NEAREST neighbor
- Ready to use as profile picture
- True 24×24 dimensions matching original Bespoke Punks

**512×512 PNG** (optional with `--save-512`)
- High-resolution version
- Can be further edited if needed
- Shows full detail before downscaling

**Console Output:**
```
============================================================
BESPOKE PUNK GENERATOR
============================================================

[1/4] Analyzing input image...
  ✓ Detected 5 dominant colors
  ✓ Background: green
  ✓ Top 3 colors: ['green', 'dark gray', 'light orange']

[2/4] Generating prompt...
  ✓ Prompt: pixel art, portrait of bespoke punk, green solid background, dark gray hair, light skin, sharp pixel edges, limited color palette
  ✓ Metadata: {'background': 'green', 'hair_color': 'dark gray', 'skin_tone': 'light', 'dominant_colors': ['green', 'dark gray', 'light orange']}

[3/4] Generating Bespoke Punk...
  ✓ Generated 512×512 image

[4/4] Downscaling to 24×24...
  ✓ Downscaled to 24×24

✓ Saved 24×24 output: my_punk.png

============================================================
GENERATION COMPLETE!
============================================================
```

## Tips for Best Results

1. **Clear images work best** - Use images with clear subjects and simple backgrounds
2. **High contrast helps** - Images with distinct colors produce better results
3. **Experiment with different photos** - Try selfies, avatars, artwork, etc.
4. **Adjust guidance scale** - Lower (5-6) for more creative, higher (8-9) for more accurate to prompt
5. **More steps = better quality** - Try --steps 40 or 50 for higher quality (slower)

## Troubleshooting

**"Model not found"**
- Make sure you've downloaded the LoRA checkpoint from RunPod
- Check the path in `--lora` parameter

**"Input file not found"**
- Verify the image path is correct
- Use absolute paths if relative paths don't work

**"Out of memory"**
- Reduce --steps to 20-25
- Close other applications
- Model requires ~4GB VRAM/RAM

**Output doesn't look like Bespoke Punk**
- Try adjusting --guidance (7.5-9.0 range works best)
- Make sure you're using the correct LoRA checkpoint (epoch 2 recommended)

## Next Steps

Want to build a web interface? Check out:
- Flask/Django for web backend
- Gradio for quick UI (recommended for prototyping)
- React/Next.js for production-ready frontend

Need to customize prompts? Edit the `PromptGenerator` class in `bespoke_punk_generator.py`

Want better feature detection? Consider adding:
- Face detection for better positioning
- Accessory detection (glasses, hats, etc.)
- Style transfer for more accurate matching

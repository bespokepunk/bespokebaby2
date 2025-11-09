# PixNite v1.0 Training Correction

## Note: PixNite Latest Version is v1.0 (not v1.5)

You found that the latest version is **v1.0**, not v1.5 as I mentioned.

### Correct Model Info:
- **Name**: PixNite 1.5 - Pure Pixel Art
- **Latest Version**: v1.0
- **Link**: https://civitai.com/models/294183/pixnite-15-pure-pixel-art

There's also **PixNite XL** available if needed.

### Training Already Started
You've already kicked off PixNite v1.0 training - perfect!

Same settings apply:
- Resolution: 64 or 128 (whatever it accepted)
- Clip Skip: 1
- Network Dim: 32
- Epochs: 3

---

## While PixNite Trains: Test Nova Pixels Epoch 2 & 3

Epoch 2 preview looked MUCH better than Epoch 1!

Run: `python3 test_nova_epochs_2_3.py`

This will:
1. Test both Epoch 2 and Epoch 3
2. Generate 5 test prompts each
3. Try two downscaling methods:
   - Direct 512→24 (simple)
   - Quantize + sharpen + 24 (better)
4. Compare to originals

**If Epoch 2 or 3 works well**: We might not need Kohya at all!

---

## Next Steps Priority:

1. **NOW**: Test Nova Epochs 2 & 3 (script ready)
2. **WAIT**: For PixNite training to finish
3. **THEN**: Test PixNite epochs
4. **IF NEEDED**: Set up Kohya as backup

Don't rush to Kohya if Nova Epoch 2 already works!

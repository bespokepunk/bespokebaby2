#!/usr/bin/env python3
"""
Create SD-piXL config and palette files
Run this on RunPod after cloning SD-piXL
"""

import os
from pathlib import Path

def create_files():
    """Create config and palette files for SD-piXL"""

    print("Creating SD-piXL files...")

    # Palette (top 10 most used colors from your training data)
    palette_content = """000000
3ffe9e
6ae745
35dd88
ffffff
03dc73
949087
a2a2a2
ebe6ea
1d2740"""

    # Config
    config_content = """seed: 42
image: ~
automatic_caption: false
saving_resize: 512
prompt: "TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing"
negative_prompt: "blurry, gradient, smooth, antialiasing, high resolution"

generator:
  image_H: 24
  image_W: 24
  std: 1.0
  initialize_renderer: true
  initialization_method: palette-bilinear
  kmeans_nb_colors: 16
  init_distance: l1
  palette: "assets/palettes/bespoke_punk.hex"
  softmax_regularizer: 1.0
  smooth_softmax: true
  gumbel: true
  tau: 1.0

training:
  steps: 6001
  save_steps: 500
  learning_rate: 0.025
  lr_scheduler: "constant_with_warmup"
  lr_warmup_steps: 250
  lr_step_rules: "0.05:25,0.1:50,0.2:75,0.3:100,0.4:125,0.5:150,0.6:175,0.7:200,0.8:225,0.9:250,1:1000,0.75:1500,0.5:2000,0.375:2500,0.25:3000,0.125:4000,0.1"
  lr_cycles: 3
  adam_beta1: 0.9
  adam_beta2: 0.999
  adam_weight_decay: 0.01
  adam_epsilon: 1.0e-08
  clip_grad: true
  max_grad_norm: 1.0
  resize_mode: "nearest"
  fft_scale: 10.0
  tv_scale: 0.0
  laplacian_scale: 0.0
  laplacian_kernel: 5
  laplacian_sigma: 0.75
  laplacian_mode: "l1"
  gradient_loss_scale: 0.0
  bilateral_scale: 0.0
  bilateral_sigma_color: 1.0
  bilateral_sigma_space: 1.0
  bilateral_max_distance: 3
  augmentation:
    grayscale_prob: 0.1
    hflip_prob: 0.5
    distorsion_prob: 0.3
    distorsion_scale: 0.2
    random_tau: true
    random_tau_min: 0.7
    random_tau_max: 1.3

diffusion:
  model_id: sdxl
  vae_id: taesdxl
  lora_path: ~
  lora_scale: 1.0
  ldm_speed_up: false
  enable_xformers: true
  gradient_checkpoint: true
  num_inference_steps: 30
  guidance_scale: 7.5
  num_references: 5

controlnet:
  use_controlnet: false
  models_id: []
  controlnet_conditioning_scale: []
  control_guidance_start: 0.0
  control_guidance_end: 1.0

caption:
  blip_model_id: Salesforce/blip2-opt-2.7b
  min_new_tokens: 20
  max_new_tokens: 75
  query: ""
  skip_special_tokens: true

sd:
  guidance_scale: 40.
  grad_scale: 1.0
  t_min: 0.02
  t_max: 0.98
  t_bound_max: 0.8
  t_bound_reached: 0.5
  sampling_method_t: "bounded_max"
  im_size: ~
  w_mode: "cumprod"
"""

    # Write palette
    palette_path = Path("SD-piXL/assets/palettes/bespoke_punk.hex")
    palette_path.parent.mkdir(parents=True, exist_ok=True)
    with open(palette_path, 'w') as f:
        f.write(palette_content)
    print(f"✅ Created: {palette_path}")

    # Write config
    config_path = Path("SD-piXL/config/bespoke_punk_24x24.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"✅ Created: {config_path}")

    print("\n✅ All files created!")
    print("\nNext: Run the installation and generation commands")

if __name__ == "__main__":
    create_files()

#!/usr/bin/env python3
"""Package Phase 1B training data for RunPod"""

import shutil
from pathlib import Path

# Create package directory
package_dir = Path("runpod_package_phase1b")
training_dir = package_dir / "training_data" / "1_bespoke_baby"
training_dir.mkdir(parents=True, exist_ok=True)

# Source directory
source_dir = Path("runpod_package/training_data")

# Copy all files
print("Copying 512px images and Phase 1B captions...")
for file_path in source_dir.iterdir():
    if file_path.suffix in ['.png', '.txt']:
        shutil.copy2(file_path, training_dir / file_path.name)

# Copy config
shutil.copy2("runpod_package/training_config.toml", package_dir / "training_config.toml")

# Update config train_data_dir path
config_path = package_dir / "training_config.toml"
with open(config_path, 'r') as f:
    config = f.read()

config = config.replace('train_data_dir = "/workspace/training_data"',
                       'train_data_dir = "/workspace/runpod_package_phase1b/training_data"')

with open(config_path, 'w') as f:
    f.write(config)

# Count files
num_images = len(list(training_dir.glob("*.png")))
num_captions = len(list(training_dir.glob("*.txt")))

print(f"✓ Copied {num_images} images")
print(f"✓ Copied {num_captions} captions")
print(f"✓ Package structure created:")
print(f"  {package_dir}/")
print(f"    training_config.toml")
print(f"    training_data/")
print(f"      1_bespoke_baby/")
print(f"        {num_images} .png files")
print(f"        {num_captions} .txt files")

print("\nReady to zip!")

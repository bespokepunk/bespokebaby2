#!/usr/bin/env python3
"""
🚀 BESPOKE PUNK SDXL TRAINING FOR RUNPOD
Optimized for RunPod GPU instances with W&B monitoring
"""

import torch
import os
import json
import argparse
from pathlib import Path
from PIL import Image
import numpy as np
from tqdm import tqdm
import logging
from datetime import datetime

# Diffusers and training imports
from diffusers import StableDiffusionXLPipeline, DDPMScheduler, AutoencoderKL
from diffusers.optimization import get_scheduler
from peft import LoraConfig, get_peft_model, PeftModel
from torch.utils.data import Dataset, DataLoader
import gc
from diffusers import DDIMScheduler

# Optional W&B for monitoring
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("⚠️  wandb not available - training will proceed without monitoring")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_wandb_samples(unet, vae, text_encoder, text_encoder_2, tokenizer, tokenizer_2,
                           prompts, device, dtype, step, wandb_run, add_time_ids):
    """Generate sample images for W&B monitoring"""
    if not WANDB_AVAILABLE or not wandb_run:
        return

    logger.info(f"   Generating {len(prompts)} sample images...")

    # Set models to eval mode temporarily
    unet.eval()

    try:
        # Simple scheduler for inference
        scheduler = DDIMScheduler(
            num_train_timesteps=1000,
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample=False,
            set_alpha_to_one=False,
        )

        images_for_wandb = []
        captions_for_wandb = []

        with torch.no_grad():
            for prompt in prompts:
                # Encode text
                tokens_1 = tokenizer(
                    prompt,
                    padding="max_length",
                    max_length=77,
                    truncation=True,
                    return_tensors="pt"
                ).input_ids.to(device)

                tokens_2 = tokenizer_2(
                    prompt,
                    padding="max_length",
                    max_length=77,
                    truncation=True,
                    return_tensors="pt"
                ).input_ids.to(device)

                # Get text encoder outputs properly
                enc_1_output = text_encoder(tokens_1)
                enc_1 = enc_1_output.last_hidden_state  # [batch, seq_len, 768]

                enc_2_output = text_encoder_2(tokens_2)
                enc_2 = enc_2_output.last_hidden_state  # [batch, seq_len, 1280]
                pooled_enc_2 = enc_2_output.text_embeds  # [batch, 1280] - for CLIPTextModelWithProjection

                encoder_hidden_states = torch.cat([enc_1, enc_2], dim=-1)  # [batch, seq_len, 2048]

                # Start with random noise
                latents = torch.randn(
                    (1, 4, 64, 64),  # SDXL latent size for 512x512
                    device=device,
                    dtype=dtype
                )

                # Simple denoising (just a few steps for speed)
                scheduler.set_timesteps(20)
                for t in scheduler.timesteps[-5:]:  # Only last 5 steps for speed
                    latent_model_input = latents

                    noise_pred = unet(
                        latent_model_input,
                        t,
                        encoder_hidden_states=encoder_hidden_states,
                        added_cond_kwargs={
                            "text_embeds": pooled_enc_2,
                            "time_ids": add_time_ids.to(device)
                        }
                    ).sample

                    latents = scheduler.step(noise_pred, t, latents).prev_sample

                # Decode latents to image
                latents = latents / vae.config.scaling_factor
                image = vae.decode(latents).sample

                # Convert to PIL
                image = (image / 2 + 0.5).clamp(0, 1)
                image = image.cpu().permute(0, 2, 3, 1).float().numpy()[0]
                image = (image * 255).round().astype("uint8")

                from PIL import Image
                pil_image = Image.fromarray(image)

                images_for_wandb.append(wandb.Image(pil_image, caption=prompt[:100]))
                captions_for_wandb.append(prompt[:100])

        # Log to W&B
        wandb_run.log({
            "samples": images_for_wandb,
            "step": step
        })

        logger.info(f"   ✅ Logged {len(images_for_wandb)} samples to W&B")

    except Exception as e:
        logger.warning(f"   ⚠️  Sample generation error: {e}")
    finally:
        # Back to training mode
        unet.train()
        torch.cuda.empty_cache()

class BespokePunkDataset(Dataset):
    """Dataset for Bespoke Punk 24x24 pixel art training"""

    def __init__(self, images_dir, captions_dir, resolution=512):
        self.images_dir = Path(images_dir)
        self.captions_dir = Path(captions_dir)
        self.resolution = resolution

        # Match images with captions
        self.pairs = []
        for img_file in sorted(self.images_dir.glob("*.png")):
            caption_file = self.captions_dir / f"{img_file.stem}.txt"
            if caption_file.exists():
                self.pairs.append((img_file, caption_file))

        logger.info(f"📦 Loaded {len(self.pairs)} training pairs")

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        img_path, caption_path = self.pairs[idx]

        # Load image - use NEAREST for pixel art to preserve sharp edges
        image = Image.open(img_path).convert("RGB")
        image = image.resize((self.resolution, self.resolution), Image.NEAREST)

        # Convert to tensor and normalize
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image).permute(2, 0, 1)
        image = image * 2.0 - 1.0  # Normalize to [-1, 1]

        # Load caption
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption = f.read().strip()

        return {
            'pixel_values': image,
            'caption': caption,
            'image_name': img_path.stem
        }


def setup_wandb(config):
    """Initialize Weights & Biases monitoring"""
    if not WANDB_AVAILABLE:
        return None

    try:
        wandb.init(
            project=config.get('wandb_project', 'bespoke-punk-sdxl'),
            name=config.get('run_name', f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            config=config
        )
        logger.info("✅ W&B monitoring enabled")

        # Log sample prompts for reference
        sample_prompts = config.get('sample_prompts', [])
        if sample_prompts:
            wandb.config.update({"sample_prompts": sample_prompts})
            logger.info(f"📝 Loaded {len(sample_prompts)} sample prompts for W&B monitoring")

        return wandb
    except Exception as e:
        logger.warning(f"⚠️  W&B initialization failed: {e}")
        return None


def train_bespoke_punk_sdxl(
    images_dir="./FORTRAINING6/all",
    captions_dir="./FORTRAINING6/oldtext",
    output_dir="./models/bespoke_punk_sdxl",
    base_model="stabilityai/stable-diffusion-xl-base-1.0",
    resolution=512,
    train_batch_size=2,
    num_train_epochs=120,
    learning_rate=8e-5,
    lora_rank=16,
    lora_alpha=16,
    mixed_precision="fp16",
    gradient_accumulation_steps=1,
    save_steps=500,
    validation_steps=100,
    wandb_project="bespoke-punk-sdxl",
    wandb_api_key=None,
    sample_interval=100,
    seed=42
):
    """
    Main training function for Bespoke Punk SDXL model

    Args:
        images_dir: Directory containing training images
        captions_dir: Directory containing caption .txt files
        output_dir: Where to save trained model
        base_model: Base SDXL model to fine-tune
        resolution: Training resolution (512 recommended)
        train_batch_size: Batch size (2-4 for most GPUs)
        num_train_epochs: Number of training epochs
        learning_rate: Learning rate (8e-5 recommended)
        lora_rank: LoRA rank (16 recommended)
        lora_alpha: LoRA alpha (16 recommended)
        mixed_precision: "fp16" or "bf16"
        gradient_accumulation_steps: Accumulate gradients
        save_steps: Save checkpoint every N steps
        validation_steps: Validate every N steps
        wandb_project: W&B project name
        wandb_api_key: W&B API key
        seed: Random seed
    """

    # Set random seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🚀 Using device: {device}")

    if device.type == "cuda":
        logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

    # W&B Sample prompts for monitoring
    sample_prompts = [
        "TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing",
        "TOK bespoke punk, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing",
        "TOK bespoke, 24x24 pixel grid, female, pink background, blonde hair, green eyes, light skin, right-facing",
        "TOK bespoke punk style, 24x24 pixel art portrait, male, teal background, red hair, blue eyes with glasses, light skin, right-facing",
        "TOK bespoke, 24x24 pixel grid portrait, female, yellow background, black hair, hazel eyes, tan skin, right-facing",
    ]

    # Configuration
    config = {
        "base_model": base_model,
        "resolution": resolution,
        "train_batch_size": train_batch_size,
        "num_train_epochs": num_train_epochs,
        "learning_rate": learning_rate,
        "lora_rank": lora_rank,
        "lora_alpha": lora_alpha,
        "mixed_precision": mixed_precision,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "save_steps": save_steps,
        "validation_steps": validation_steps,
        "sample_interval": sample_interval,
        "seed": seed,
        "dataset_size": 0,  # Will be updated
        "trigger_word": "TOK",
        "style": "bespoke_punk_24x24_pixel_art",
        "sample_prompts": sample_prompts
    }

    logger.info("=" * 80)
    logger.info("🎨 BESPOKE PUNK SDXL TRAINING")
    logger.info("=" * 80)
    logger.info(f"📊 Configuration:")
    for key, value in config.items():
        logger.info(f"   {key}: {value}")

    # SDXL requires specific time_ids: [original_height, original_width, crop_top, crop_left, target_height, target_width]
    add_time_ids = torch.tensor([[resolution, resolution, 0, 0, resolution, resolution]], dtype=torch.float32)

    # Setup W&B if API key provided
    wb = None
    if wandb_api_key and WANDB_AVAILABLE:
        os.environ['WANDB_API_KEY'] = wandb_api_key
        config['wandb_project'] = wandb_project
        wb = setup_wandb(config)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load dataset
    logger.info("\n📦 Loading dataset...")
    dataset = BespokePunkDataset(images_dir, captions_dir, resolution)

    if len(dataset) == 0:
        raise ValueError("❌ No training pairs found! Check your directories.")

    config['dataset_size'] = len(dataset)
    logger.info(f"✅ Loaded {len(dataset)} training pairs")

    # Create dataloader
    dataloader = DataLoader(
        dataset,
        batch_size=train_batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )

    # Sample captions
    logger.info("\n📝 Sample training captions:")
    for i in range(min(3, len(dataset))):
        sample = dataset[i]
        logger.info(f"   {i+1}. {sample['caption'][:100]}...")

    # Load base model
    logger.info(f"\n📥 Loading base model: {base_model}")
    dtype = torch.float16 if mixed_precision == "fp16" else torch.bfloat16

    try:
        pipe = StableDiffusionXLPipeline.from_pretrained(
            base_model,
            torch_dtype=dtype,
            use_safetensors=True,
            variant="fp16" if mixed_precision == "fp16" else None
        )
        logger.info("✅ Base model loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load base model: {e}")
        raise

    # Extract components
    unet = pipe.unet.to(device)
    vae = pipe.vae.to(device)
    text_encoder = pipe.text_encoder.to(device)
    text_encoder_2 = pipe.text_encoder_2.to(device)
    tokenizer = pipe.tokenizer
    tokenizer_2 = pipe.tokenizer_2

    # Setup noise scheduler
    noise_scheduler = DDPMScheduler.from_pretrained(
        base_model,
        subfolder="scheduler"
    )

    # Clear pipeline to save memory
    del pipe
    gc.collect()
    torch.cuda.empty_cache()

    # Setup LoRA
    logger.info(f"\n🎯 Setting up LoRA (rank={lora_rank}, alpha={lora_alpha})")
    lora_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_alpha,
        target_modules=[
            "to_k", "to_q", "to_v", "to_out.0",
            "proj_in", "proj_out",
            "ff.net.0.proj", "ff.net.2"
        ],
        lora_dropout=0.0,
    )

    unet = get_peft_model(unet, lora_config)
    unet.train()

    # Enable gradient checkpointing
    unet.enable_gradient_checkpointing()

    # Freeze VAE and text encoders
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    text_encoder_2.requires_grad_(False)

    # Setup optimizer
    logger.info("\n⚙️  Setting up optimizer and scheduler")
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=learning_rate,
        betas=(0.9, 0.999),
        weight_decay=0.01,
        eps=1e-8
    )

    # Calculate training steps
    num_update_steps_per_epoch = len(dataloader) // gradient_accumulation_steps
    max_train_steps = num_train_epochs * num_update_steps_per_epoch

    lr_scheduler = get_scheduler(
        "cosine",
        optimizer=optimizer,
        num_warmup_steps=500,
        num_training_steps=max_train_steps
    )

    logger.info(f"📊 Training schedule:")
    logger.info(f"   Total steps: {max_train_steps}")
    logger.info(f"   Steps per epoch: {num_update_steps_per_epoch}")
    logger.info(f"   Warmup steps: 500")

    # Training loop
    logger.info("\n🚀 Starting training...\n")

    global_step = 0
    losses = []

    progress_bar = tqdm(total=max_train_steps, desc="Training")

    for epoch in range(num_train_epochs):
        logger.info(f"\n📅 Epoch {epoch + 1}/{num_train_epochs}")

        for step, batch in enumerate(dataloader):
            # Move to device
            pixel_values = batch["pixel_values"].to(device, dtype=dtype)
            captions = batch["caption"]

            # Encode images with VAE
            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

            # Add noise
            noise = torch.randn_like(latents)
            timesteps = torch.randint(
                0,
                noise_scheduler.config.num_train_timesteps,
                (latents.shape[0],),
                device=device
            )
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Encode text
            tokens_1 = tokenizer(
                captions,
                padding="max_length",
                max_length=77,
                truncation=True,
                return_tensors="pt"
            ).input_ids.to(device)

            tokens_2 = tokenizer_2(
                captions,
                padding="max_length",
                max_length=77,
                truncation=True,
                return_tensors="pt"
            ).input_ids.to(device)

            with torch.no_grad():
                # Get text encoder outputs properly
                enc_1_output = text_encoder(tokens_1)
                enc_1 = enc_1_output.last_hidden_state  # [batch, seq_len, 768]

                enc_2_output = text_encoder_2(tokens_2)
                enc_2 = enc_2_output.last_hidden_state  # [batch, seq_len, 1280]
                pooled_prompt_embeds = enc_2_output.text_embeds  # [batch, 1280] - for CLIPTextModelWithProjection

                # Combine encodings (concatenate along feature dimension)
                encoder_hidden_states = torch.cat([enc_1, enc_2], dim=-1)  # [batch, seq_len, 2048]

            # Predict noise
            # Expand time_ids to match batch size
            batch_time_ids = add_time_ids.repeat(latents.shape[0], 1).to(device)

            # Debug: Check for NaN in inputs
            if torch.isnan(encoder_hidden_states).any():
                logger.error("❌ NaN in encoder_hidden_states")
                optimizer.zero_grad()
                continue
            if torch.isnan(pooled_prompt_embeds).any():
                logger.error("❌ NaN in pooled_prompt_embeds")
                optimizer.zero_grad()
                continue
            if torch.isnan(noisy_latents).any():
                logger.error("❌ NaN in noisy_latents")
                optimizer.zero_grad()
                continue

            model_pred = unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=encoder_hidden_states,
                added_cond_kwargs={"text_embeds": pooled_prompt_embeds, "time_ids": batch_time_ids}
            ).sample

            # Check for NaN in model output
            if torch.isnan(model_pred).any():
                logger.error("❌ NaN in model_pred output")
                optimizer.zero_grad()
                continue

            # Calculate loss
            loss = torch.nn.functional.mse_loss(
                model_pred.float(),
                noise.float(),
                reduction="mean"
            )

            # Check for NaN loss
            if torch.isnan(loss) or torch.isinf(loss):
                logger.warning(f"⚠️  NaN/Inf loss detected at step {global_step}, skipping batch")
                optimizer.zero_grad()
                continue

            # Gradient accumulation
            loss = loss / gradient_accumulation_steps
            loss.backward()

            losses.append(loss.item() * gradient_accumulation_steps)

            if (step + 1) % gradient_accumulation_steps == 0:
                # Gradient clipping (more aggressive for stability)
                torch.nn.utils.clip_grad_norm_(unet.parameters(), 0.5)

                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

                global_step += 1
                progress_bar.update(1)

                # Update progress
                avg_loss = np.mean(losses[-100:]) if len(losses) >= 100 else np.mean(losses)
                progress_bar.set_postfix({
                    'loss': f'{avg_loss:.4f}',
                    'lr': f'{lr_scheduler.get_last_lr()[0]:.2e}'
                })

                # Log to W&B
                if wb and global_step % 10 == 0:
                    wb.log({
                        "train/loss": avg_loss,
                        "train/learning_rate": lr_scheduler.get_last_lr()[0],
                        "train/epoch": epoch,
                        "train/step": global_step
                    })

                # Save checkpoint
                if global_step % save_steps == 0:
                    checkpoint_dir = Path(output_dir) / f"checkpoint-{global_step}"
                    checkpoint_dir.mkdir(exist_ok=True, parents=True)

                    unet.save_pretrained(checkpoint_dir)

                    # Save metadata
                    metadata = {
                        "step": global_step,
                        "epoch": epoch,
                        "loss": avg_loss,
                        "learning_rate": lr_scheduler.get_last_lr()[0],
                        "config": config
                    }

                    with open(checkpoint_dir / "metadata.json", "w") as f:
                        json.dump(metadata, f, indent=2)

                    logger.info(f"\n💾 Saved checkpoint at step {global_step} (loss: {avg_loss:.4f})")

                # Generate sample images for W&B
                if wb and global_step % sample_interval == 0 and global_step > 0:
                    logger.info(f"\n🎨 Generating sample images for W&B...")
                    try:
                        generate_wandb_samples(
                            unet=unet,
                            vae=vae,
                            text_encoder=text_encoder,
                            text_encoder_2=text_encoder_2,
                            tokenizer=tokenizer,
                            tokenizer_2=tokenizer_2,
                            prompts=sample_prompts[:3],  # Generate 3 samples
                            device=device,
                            dtype=dtype,
                            step=global_step,
                            wandb_run=wb,
                            add_time_ids=add_time_ids
                        )
                    except Exception as e:
                        logger.warning(f"⚠️  Sample generation failed: {e}")

                # Validation logging
                if global_step % validation_steps == 0:
                    logger.info(f"\n📊 Step {global_step}/{max_train_steps}")
                    logger.info(f"   Loss: {avg_loss:.4f}")
                    logger.info(f"   LR: {lr_scheduler.get_last_lr()[0]:.2e}")
                    if device.type == "cuda":
                        logger.info(f"   GPU Memory: {torch.cuda.memory_allocated() / 1024**3:.1f}GB")

            # Memory cleanup
            if global_step % 100 == 0:
                torch.cuda.empty_cache()
                gc.collect()

    progress_bar.close()

    # Save final model
    logger.info("\n💾 Saving final model...")
    final_dir = Path(output_dir) / "final_model"
    final_dir.mkdir(exist_ok=True, parents=True)
    unet.save_pretrained(final_dir)

    # Save final metadata
    final_metadata = {
        "training_complete": True,
        "total_steps": global_step,
        "total_epochs": num_train_epochs,
        "final_loss": np.mean(losses[-100:]) if len(losses) >= 100 else np.mean(losses),
        "config": config,
        "timestamp": datetime.now().isoformat()
    }

    with open(final_dir / "metadata.json", "w") as f:
        json.dump(final_metadata, f, indent=2)

    logger.info(f"\n🎉 TRAINING COMPLETE!")
    logger.info(f"💾 Final model saved to: {final_dir}")
    logger.info(f"📊 Final loss: {final_metadata['final_loss']:.4f}")
    logger.info(f"🎯 Total steps: {global_step}")

    if wb:
        wb.finish()

    return final_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Bespoke Punk SDXL model on RunPod")

    parser.add_argument("--images_dir", type=str, default="./FORTRAINING6/all",
                        help="Directory containing training images")
    parser.add_argument("--captions_dir", type=str, default="./FORTRAINING6/oldtext",
                        help="Directory containing caption files")
    parser.add_argument("--output_dir", type=str, default="./models/bespoke_punk_sdxl",
                        help="Output directory for trained model")
    parser.add_argument("--base_model", type=str, default="stabilityai/stable-diffusion-xl-base-1.0",
                        help="Base SDXL model")
    parser.add_argument("--resolution", type=int, default=512,
                        help="Training resolution")
    parser.add_argument("--train_batch_size", type=int, default=2,
                        help="Training batch size")
    parser.add_argument("--num_train_epochs", type=int, default=120,
                        help="Number of training epochs")
    parser.add_argument("--learning_rate", type=float, default=1e-5,
                        help="Learning rate")
    parser.add_argument("--lora_rank", type=int, default=16,
                        help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=16,
                        help="LoRA alpha")
    parser.add_argument("--mixed_precision", type=str, default="fp16",
                        choices=["fp16", "bf16", "no"],
                        help="Mixed precision training")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1,
                        help="Gradient accumulation steps")
    parser.add_argument("--save_steps", type=int, default=500,
                        help="Save checkpoint every N steps")
    parser.add_argument("--validation_steps", type=int, default=100,
                        help="Validation every N steps")
    parser.add_argument("--wandb_project", type=str, default="bespoke-punk-sdxl",
                        help="W&B project name")
    parser.add_argument("--wandb_api_key", type=str, default=None,
                        help="W&B API key")
    parser.add_argument("--sample_interval", type=int, default=100,
                        help="Generate W&B samples every N steps")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")

    args = parser.parse_args()

    # Run training
    train_bespoke_punk_sdxl(
        images_dir=args.images_dir,
        captions_dir=args.captions_dir,
        output_dir=args.output_dir,
        base_model=args.base_model,
        resolution=args.resolution,
        train_batch_size=args.train_batch_size,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        mixed_precision=args.mixed_precision,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        save_steps=args.save_steps,
        validation_steps=args.validation_steps,
        wandb_project=args.wandb_project,
        wandb_api_key=args.wandb_api_key,
        sample_interval=args.sample_interval,
        seed=args.seed
    )

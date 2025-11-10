#!/usr/bin/env python3
"""
Backfill Historical Training Parameters

Populates training_runs.all_parameters for all historical training runs
by extracting data from existing columns, documentation, and observations.

This enables comprehensive parameter correlation analysis across all runs.

Usage:
    python scripts/backfill_parameters.py
"""

import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.qwvncbcphuyobijakdsr"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Ilyssa2025")

# =============================================================================
# HISTORICAL TRAINING RUN PARAMETER DATA
# =============================================================================
# Extracted from TRAINING_COMPARISON_ANALYSIS.md and database records

HISTORICAL_PARAMETERS = {
    "SD15_PERFECT_Nov9": {  # Actual database name
        "architecture": {
            "network_dim": 32,
            "network_alpha": 16,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "basic_v1",
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 4.5,
            "checkpoint_file_size_mb": 36
        }
    },

    "SDXL_435MB_Nov9": {  # Actual database name (was called SD15_PERFECT_SDXL conceptually)
        "architecture": {
            "network_dim": 64,
            "network_alpha": 32,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "detailed_v1",
            "num_images": 203,
            "image_resolution": "1024x1024",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.1,  # Key difference
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 2048
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 5.0,
            "checkpoint_file_size_mb": 36
        }
    },

    "SD15_ACCURATE_CAPTIONS": {
        "architecture": {
            "network_dim": 32,
            "network_alpha": 16,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "detailed_v1",
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 4.5,
            "checkpoint_file_size_mb": 36
        }
    },

    "SD15_bespoke_baby_Nov10": {  # Actual database name (was SD15_DIM64_TEST)
        "architecture": {
            "network_dim": 64,  # KEY DIFFERENCE - CAUSED FAILURE
            "network_alpha": 16,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "detailed_v1",
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 4.5,
            "checkpoint_file_size_mb": 72  # Larger file due to dim=64
        }
    },

    "SDXL_Current_Nov10": {  # Actual database name (was SD15_DIM128_TEST)
        "architecture": {
            "network_dim": 128,  # KEY DIFFERENCE - SEVERE FAILURE
            "network_alpha": 64,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "detailed_v1",
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 5.0,
            "checkpoint_file_size_mb": 144  # Much larger file
        }
    },

    "SD15_FINAL_CORRECTED_CAPTIONS": {
        "architecture": {
            "network_dim": 32,
            "network_alpha": 16,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "final_corrected_lips_12hex_v1",  # Most detailed captions
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,  # HYPOTHESIS: Should be 3 for this many hex codes
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 4.5,
            "checkpoint_file_size_mb": 36
        }
    },

    "SDXL_218MB_Nov8": {
        "architecture": {
            "network_dim": 64,
            "network_alpha": 32,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "pre_backup_unknown",
            "num_images": 203,
            "image_resolution": "1024x1024",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 2048
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 4.5,
            "checkpoint_file_size_mb": 218
        }
    },

    "SD15_36MB_Early_Nov9": {
        "architecture": {
            "network_dim": 32,
            "network_alpha": 16,
            "conv_dim": 0,
            "conv_alpha": 0
        },
        "hyperparameters": {
            "learning_rate": 0.0001,
            "lr_scheduler": "constant_with_warmup",
            "lr_warmup_steps": 100,
            "optimizer_type": "AdamW",
            "max_train_epochs": 10,
            "save_every_n_epochs": 1
        },
        "data": {
            "caption_version": "pre_backup_unknown",
            "num_images": 203,
            "image_resolution": "512x512",
            "keep_tokens": 1,
            "caption_dropout_rate": 0.0,
            "shuffle_caption": True,
            "caption_extension": ".txt"
        },
        "augmentation": {
            "color_aug": False,
            "flip_aug": True,
            "noise_offset": 0.0
        },
        "preprocessing": {
            "bucket_no_upscale": True,
            "bucket_reso_steps": 64,
            "min_bucket_reso": 320,
            "max_bucket_reso": 1024
        },
        "stability": {
            "gradient_checkpointing": True,
            "gradient_accumulation_steps": 1,
            "max_grad_norm": 1.0,
            "mixed_precision": "fp16",
            "xformers": True,
            "full_fp16": True
        },
        "derived": {
            "steps_per_epoch": 203,
            "total_steps": 2030,
            "total_training_time_hours": 3.0,
            "checkpoint_file_size_mb": 36
        }
    }
}

# Add any other historical runs if they exist
# Check database for other run_names and add their parameters here

def connect_db():
    """Connect to Supabase PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_all_training_runs(conn):
    """Get all training runs from database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, run_name, all_parameters
        FROM training_runs
        ORDER BY run_date
    """)
    runs = cur.fetchall()
    cur.close()
    return runs

def backfill_parameters(conn, run_id, run_name, parameters):
    """Update training_runs.all_parameters for a specific run"""
    cur = conn.cursor()

    # Convert parameters to JSON string
    params_json = json.dumps(parameters)

    # Update the run
    cur.execute("""
        UPDATE training_runs
        SET all_parameters = %s::jsonb
        WHERE id = %s
    """, (params_json, run_id))

    conn.commit()
    cur.close()

    print(f"✅ Updated run ID {run_id}: {run_name}")
    print(f"   - Architecture: dim={parameters['architecture']['network_dim']}, "
          f"alpha={parameters['architecture']['network_alpha']}")
    print(f"   - Hyperparams: lr={parameters['hyperparameters']['learning_rate']}, "
          f"epochs={parameters['hyperparameters']['max_train_epochs']}")
    print(f"   - Data: captions={parameters['data']['caption_version']}, "
          f"images={parameters['data']['num_images']}, "
          f"keep_tokens={parameters['data']['keep_tokens']}")
    print()

def main():
    print("=" * 80)
    print("BACKFILLING HISTORICAL TRAINING PARAMETERS")
    print("=" * 80)
    print()

    # Connect to database
    print("Connecting to Supabase...")
    conn = connect_db()
    print("✅ Connected\n")

    # Get all training runs
    print("Fetching training runs from database...")
    runs = get_all_training_runs(conn)
    print(f"Found {len(runs)} training runs\n")

    # Backfill each run
    updated_count = 0
    skipped_count = 0
    missing_count = 0

    for run_id, run_name, existing_params in runs:
        print(f"Processing: {run_name} (ID: {run_id})")

        # Check if already has parameters
        if existing_params:
            print(f"⏭️  Skipped (already has parameters)")
            skipped_count += 1
            print()
            continue

        # Check if we have historical data for this run
        if run_name not in HISTORICAL_PARAMETERS:
            print(f"⚠️  No historical parameter data available")
            print(f"   Please add parameters for '{run_name}' to HISTORICAL_PARAMETERS dict")
            missing_count += 1
            print()
            continue

        # Backfill parameters
        parameters = HISTORICAL_PARAMETERS[run_name]
        backfill_parameters(conn, run_id, run_name, parameters)
        updated_count += 1

    # Close connection
    conn.close()

    # Summary
    print("=" * 80)
    print("BACKFILL COMPLETE")
    print("=" * 80)
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped (already had params): {skipped_count}")
    print(f"⚠️  Missing parameter data: {missing_count}")
    print()

    if missing_count > 0:
        print("ACTION REQUIRED:")
        print("Add parameter data for missing runs to HISTORICAL_PARAMETERS dict")
        print("Then run this script again.")
        print()

    # Verification queries
    print("=" * 80)
    print("VERIFICATION QUERIES")
    print("=" * 80)
    print()
    print("Run these queries to verify the backfill:")
    print()
    print("1. Check all runs have parameters:")
    print("   SELECT run_name, ")
    print("          CASE WHEN all_parameters IS NULL THEN '❌ Missing' ELSE '✅ Has params' END")
    print("   FROM training_runs")
    print("   ORDER BY run_date;")
    print()
    print("2. View parameter comparison:")
    print("   SELECT * FROM v_training_comparison;")
    print()
    print("3. Find all runs with network_dim > 32:")
    print("   SELECT run_name, network_dim, quality_score, overall_verdict")
    print("   FROM v_training_comparison")
    print("   WHERE network_dim > 32;")
    print()
    print("4. Export for correlation analysis:")
    print("   SELECT * FROM v_parameter_correlation_data;")
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Hypothesis Generator - Phase 4 MLOps

AI-assisted generation of next experiments based on:
- Current unresolved issues
- Parameter gaps in exploration space
- Historical patterns and correlations
- Theory-driven hypotheses

Usage:
    python scripts/hypothesis_generator.py

    # For specific issue
    python scripts/hypothesis_generator.py --issue "wrong_background"

    # Generate training config
    python scripts/hypothesis_generator.py --generate-config
"""

import os
import sys
import json
import psycopg2
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.qwvncbcphuyobijakdsr"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Ilyssa2025")

# Hypothesis templates
HYPOTHESIS_TEMPLATES = {
    "keep_tokens_increase": {
        "name": "Increase keep_tokens for complex captions",
        "hypothesis": "Increasing keep_tokens from 1 to 3 will improve background color accuracy",
        "rationale": "SD15_FINAL_CORRECTED with 12+ hex codes took 7 epochs to learn green background with keep_tokens=1. Higher keep_tokens ensures critical color keywords are never dropped during training.",
        "expected_impact": "+30-40% background color accuracy (0% → 95%+) by Epoch 3",
        "confidence": 0.85,
        "priority": "HIGH",
        "parameter_changes": {
            "data.keep_tokens": 3  # Current: 1
        },
        "success_criteria": "Background color correct by Epoch 3-4 instead of Epoch 7"
    },

    "conv_dim_add": {
        "name": "Add convolutional LoRA for detail improvement",
        "hypothesis": "Adding conv_dim=8 will improve accessory rendering accuracy",
        "rationale": "Convolutional layers handle spatial features and fine details. Current runs use conv_dim=0. Testing conv_dim=8 may improve crown, earrings, necklace accuracy.",
        "expected_impact": "+15-20% accessory rendering accuracy",
        "confidence": 0.45,
        "priority": "MEDIUM",
        "parameter_changes": {
            "architecture.conv_dim": 8,  # Current: 0
            "architecture.conv_alpha": 4   # Current: 0
        },
        "success_criteria": "Crown and accessories clearly visible and accurate by Epoch 5"
    },

    "caption_dropout_test": {
        "name": "Test caption dropout for generalization",
        "hypothesis": "caption_dropout_rate=0.1 improves prompt variety and generalization",
        "rationale": "SD15_PERFECT_SDXL used caption_dropout=0.1 and showed better variety. Current runs use 0.0. Dropout may prevent overfitting to specific prompt structures.",
        "expected_impact": "+10% variety in generated outputs, better generalization to novel prompts",
        "confidence": 0.55,
        "priority": "MEDIUM",
        "parameter_changes": {
            "data.caption_dropout_rate": 0.1  # Current: 0.0
        },
        "success_criteria": "Model generates diverse outputs for similar prompts"
    },

    "dataset_expansion": {
        "name": "Expand dataset to 300+ images",
        "hypothesis": "Increasing dataset size from 203 to 300-400 images improves color variety learning",
        "rationale": "More training data typically improves generalization. Current 203 images may limit color/style variety.",
        "expected_impact": "+5-10% overall quality, better color variety",
        "confidence": 0.40,
        "priority": "LOW",
        "parameter_changes": {
            "data.num_images": 350  # Current: 203
        },
        "success_criteria": "Broader range of colors and styles learned",
        "blocker": "Requires creating 150+ new training images with captions"
    },

    "learning_rate_adjustment": {
        "name": "Test lower learning rate for stability",
        "hypothesis": "Reducing learning_rate to 5e-5 may improve training stability",
        "rationale": "Epoch 7 showed quality degradation while learning green background, suggesting instability. Lower LR may allow smoother convergence.",
        "expected_impact": "More stable convergence, less quality fluctuation",
        "confidence": 0.35,
        "priority": "LOW",
        "parameter_changes": {
            "hyperparameters.learning_rate": 5e-5  # Current: 1e-4
        },
        "success_criteria": "No quality degradation while learning new features"
    }
}

def connect_db():
    """Connect to Supabase PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_current_issues() -> List[str]:
    """Query database for unresolved issues"""
    conn = connect_db()
    cur = conn.cursor()

    # Get latest training run
    cur.execute("""
        SELECT id, run_name
        FROM training_runs
        ORDER BY run_date DESC
        LIMIT 1
    """)

    result = cur.fetchone()
    if not result:
        return []

    training_run_id = result[0]

    # Get issues from epoch results
    cur.execute("""
        SELECT DISTINCT unnest(issues_detail) as issue
        FROM epoch_results
        WHERE training_run_id = %s
          AND issues_detail IS NOT NULL
    """, (training_run_id,))

    issues = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return issues

def get_unexplored_parameters() -> List[str]:
    """Identify parameters not yet tested"""
    conn = connect_db()
    cur = conn.cursor()

    # Check which parameter values have been tested
    cur.execute("""
        SELECT DISTINCT
            all_parameters->'architecture'->>'conv_dim' as conv_dim,
            all_parameters->'data'->>'caption_dropout_rate' as caption_dropout
        FROM training_runs
        WHERE all_parameters IS NOT NULL
    """)

    results = cur.fetchall()
    cur.close()
    conn.close()

    unexplored = []

    # Check conv_dim
    conv_dims_tested = [int(r[0]) if r[0] and r[0] != 'null' else 0 for r in results]
    if 8 not in conv_dims_tested and 16 not in conv_dims_tested:
        unexplored.append("conv_dim (all runs used 0)")

    # Check caption_dropout
    dropout_tested = [float(r[1]) if r[1] and r[1] != 'null' else 0.0 for r in results]
    if 0.1 not in dropout_tested:
        unexplored.append("caption_dropout_rate (all runs used 0.0)")

    return unexplored

def rank_hypotheses(hypotheses: List[Dict], current_issues: List[str]) -> List[Dict]:
    """Rank hypotheses by priority, confidence, and relevance to current issues"""
    ranked = []

    for hyp in hypotheses:
        score = 0

        # Priority weight
        if hyp['priority'] == 'HIGH':
            score += 100
        elif hyp['priority'] == 'MEDIUM':
            score += 50
        else:
            score += 10

        # Confidence weight
        score += hyp['confidence'] * 50

        # Issue relevance
        if 'wrong_background' in current_issues and 'keep_tokens' in hyp.get('parameter_changes', {}):
            score += 50  # Highly relevant

        # Add score to hypothesis
        hyp['priority_score'] = score
        ranked.append(hyp)

    # Sort by score
    ranked.sort(key=lambda x: x['priority_score'], reverse=True)

    return ranked

def generate_report():
    """Generate hypothesis report"""
    print("\n" + "=" * 80)
    print("HYPOTHESIS GENERATOR - NEXT EXPERIMENTS")
    print("=" * 80)

    # Get current state
    print("\nAnalyzing current training runs...")
    current_issues = get_current_issues()
    unexplored = get_unexplored_parameters()

    print(f"\n🔍 Current Unresolved Issues:")
    if current_issues:
        for issue in current_issues:
            print(f"   - {issue}")
    else:
        print("   None detected")

    print(f"\n🗺️ Unexplored Parameter Space:")
    if unexplored:
        for param in unexplored:
            print(f"   - {param}")
    else:
        print("   Most parameters have been explored")

    # Generate hypotheses
    hypotheses = []
    for key, hyp_template in HYPOTHESIS_TEMPLATES.items():
        hypotheses.append(hyp_template)

    # Rank hypotheses
    ranked_hypotheses = rank_hypotheses(hypotheses, current_issues)

    # Print recommendations
    print(f"\n" + "=" * 80)
    print("RECOMMENDED EXPERIMENTS (Ranked by Priority)")
    print("=" * 80)

    for i, hyp in enumerate(ranked_hypotheses, 1):
        print(f"\n{'─' * 80}")
        print(f"Experiment #{i}: {hyp['name']}")
        print(f"{'─' * 80}")

        print(f"\n📊 Priority: {hyp['priority']} (score: {hyp.get('priority_score', 0):.0f})")
        print(f"🎲 Confidence: {hyp['confidence'] * 100:.0f}%")

        print(f"\n💡 Hypothesis:")
        print(f"   {hyp['hypothesis']}")

        print(f"\n📝 Rationale:")
        print(f"   {hyp['rationale']}")

        print(f"\n📈 Expected Impact:")
        print(f"   {hyp['expected_impact']}")

        print(f"\n⚙️ Parameter Changes:")
        for param, value in hyp['parameter_changes'].items():
            print(f"   {param}: → {value}")

        print(f"\n✅ Success Criteria:")
        print(f"   {hyp['success_criteria']}")

        if 'blocker' in hyp:
            print(f"\n⚠️ Blocker:")
            print(f"   {hyp['blocker']}")

    # Summary
    print(f"\n" + "=" * 80)
    print("RECOMMENDED ACTION PLAN")
    print("=" * 80)

    print(f"\nNext 3 experiments to run:")
    for i, hyp in enumerate(ranked_hypotheses[:3], 1):
        print(f"{i}. {hyp['name']} ({hyp['priority']} priority, {hyp['confidence']*100:.0f}% confidence)")

    print(f"\nRecommended order:")
    print(f"1. Run #{1} first (highest impact + confidence)")
    print(f"2. Run #{2} and #{3} in parallel if resources allow")
    print(f"3. Analyze results before proceeding to lower-priority experiments")

def generate_config(hypothesis_name: str):
    """Generate training config for a specific hypothesis"""
    if hypothesis_name not in HYPOTHESIS_TEMPLATES:
        print(f"❌ Hypothesis '{hypothesis_name}' not found")
        return

    hyp = HYPOTHESIS_TEMPLATES[hypothesis_name]

    print(f"\n📄 Training Config for: {hyp['name']}")
    print("=" * 80)

    print(f"\nParameter Changes:")
    print(json.dumps(hyp['parameter_changes'], indent=2))

    print(f"\nAdd these to your training_config.toml:")
    for param, value in hyp['parameter_changes'].items():
        param_parts = param.split('.')
        toml_param = param_parts[-1]
        print(f"{toml_param} = {json.dumps(value)}")

def main():
    generate_config_flag = '--generate-config' in sys.argv
    issue_filter = None

    for i, arg in enumerate(sys.argv):
        if arg == '--issue' and i + 1 < len(sys.argv):
            issue_filter = sys.argv[i + 1]

    if generate_config_flag:
        # Interactive config generation
        print("\nAvailable hypotheses:")
        for i, (key, hyp) in enumerate(HYPOTHESIS_TEMPLATES.items(), 1):
            print(f"{i}. {key}: {hyp['name']}")

        choice = input("\nSelect hypothesis number: ").strip()
        try:
            idx = int(choice) - 1
            key = list(HYPOTHESIS_TEMPLATES.keys())[idx]
            generate_config(key)
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    else:
        generate_report()

if __name__ == "__main__":
    main()

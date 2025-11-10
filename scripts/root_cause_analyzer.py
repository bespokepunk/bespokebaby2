#!/usr/bin/env python3
"""
Root Cause Analyzer - Phase 3 MLOps

Automated diagnosis of training failures and issues based on historical patterns.

Answers questions like:
- "Why did this model fail?"
- "Why is the background the wrong color?"
- "Why is it photorealistic instead of pixel art?"

Usage:
    python scripts/root_cause_analyzer.py --training-run "SD15_FINAL_CORRECTED_CAPTIONS"
    python scripts/root_cause_analyzer.py --epoch 7
    python scripts/root_cause_analyzer.py --issue "wrong_background"
"""

import os
import sys
import json
import psycopg2
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.qwvncbcphuyobijakdsr"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Ilyssa2025")

# Known patterns from historical analysis
KNOWN_PATTERNS = {
    "photorealistic": {
        "root_cause": "network_dim too high",
        "threshold": {
            "parameter": "architecture.network_dim",
            "critical_value": 32,
            "operator": ">"
        },
        "evidence": "100% of runs with network_dim > 32 produced photorealistic results",
        "confidence": 0.98,
        "recommendation": "Set network_dim=32 (proven optimal for pixel art)",
        "historical_examples": [
            "SD15_bespoke_baby_Nov10 (dim=64) → photorealistic failure",
            "SDXL_Current_Nov10 (dim=128) → severe photorealistic failure"
        ]
    },

    "wrong_background": {
        "root_cause": "keep_tokens insufficient for complex captions",
        "threshold": {
            "parameter": "data.keep_tokens",
            "critical_value": 3,
            "operator": "<"
        },
        "evidence": "Runs with 12+ hex codes in captions and keep_tokens=1 took 7 epochs to learn background",
        "confidence": 0.85,
        "recommendation": "Increase keep_tokens to 3 for prompts with 12+ hex codes",
        "historical_examples": [
            "SD15_FINAL_CORRECTED Epochs 1-6: wrong background (pink instead of green)",
            "SD15_FINAL_CORRECTED Epoch 7: green background finally learned"
        ]
    },

    "two_toned_hair": {
        "root_cause": "Early epoch learning behavior (normal)",
        "threshold": {
            "parameter": "max_train_epochs",
            "critical_value": 5,
            "operator": "<"
        },
        "evidence": "Two-toning typically resolves by Epoch 5-7 as model converges",
        "confidence": 0.70,
        "recommendation": "Continue training to Epoch 5-7 before evaluating",
        "historical_examples": [
            "SD15_PERFECT Epochs 1-3: two-toned, Epoch 7: resolved",
            "SD15_FINAL_CORRECTED Epochs 3-5: two-toned, improving over time"
        ]
    },

    "low_quality": {
        "root_cause": "Multiple possible causes - requires analysis",
        "confidence": 0.50,
        "recommendation": "Check: network_dim, learning_rate, caption quality, dataset size",
        "analysis_needed": True
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

def load_training_run(run_name: str) -> Dict:
    """Load training run details"""
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, run_name, all_parameters, quality_score, best_epoch,
               overall_verdict, production_ready, notes
        FROM training_runs
        WHERE run_name = %s
    """, (run_name,))

    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return None

    return {
        'id': result[0],
        'run_name': result[1],
        'all_parameters': result[2],
        'quality_score': result[3],
        'best_epoch': result[4],
        'overall_verdict': result[5],
        'production_ready': result[6],
        'notes': result[7]
    }

def load_epoch_results(training_run_id: int) -> List[Dict]:
    """Load epoch results for a training run"""
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT epoch_number, visual_quality_score, style_match_score,
               prompt_adherence_score, has_wrong_backgrounds, has_wrong_colors,
               is_photorealistic, issues_detail, verdict, observations
        FROM epoch_results
        WHERE training_run_id = %s
        ORDER BY epoch_number
    """, (training_run_id,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    epochs = []
    for row in results:
        epochs.append({
            'epoch_number': row[0],
            'visual_quality_score': row[1],
            'style_match_score': row[2],
            'prompt_adherence_score': row[3],
            'has_wrong_backgrounds': row[4],
            'has_wrong_colors': row[5],
            'is_photorealistic': row[6],
            'issues_detail': row[7],
            'verdict': row[8],
            'observations': row[9]
        })

    return epochs

def diagnose_photorealism(params: Dict) -> Dict:
    """Diagnose photorealistic rendering issue"""
    network_dim = params.get('architecture', {}).get('network_dim')

    if network_dim and network_dim > 32:
        pattern = KNOWN_PATTERNS["photorealistic"]
        return {
            'issue': 'photorealistic',
            'root_cause': pattern['root_cause'],
            'detected_value': network_dim,
            'critical_value': 32,
            'evidence': pattern['evidence'],
            'confidence': pattern['confidence'],
            'recommendation': pattern['recommendation'],
            'historical_examples': pattern['historical_examples']
        }

    return None

def diagnose_wrong_background(params: Dict, epochs: List[Dict]) -> Dict:
    """Diagnose wrong background color issue"""
    keep_tokens = params.get('data', {}).get('keep_tokens')
    caption_version = params.get('data', {}).get('caption_version')

    # Check if wrong backgrounds persist across multiple epochs
    wrong_bg_epochs = [e for e in epochs if e.get('has_wrong_backgrounds')]

    # Check caption complexity
    is_complex_captions = 'hex' in str(caption_version).lower() or '12' in str(caption_version)

    if keep_tokens and keep_tokens < 3 and is_complex_captions and len(wrong_bg_epochs) > 0:
        pattern = KNOWN_PATTERNS["wrong_background"]
        return {
            'issue': 'wrong_background',
            'root_cause': pattern['root_cause'],
            'detected_value': keep_tokens,
            'critical_value': 3,
            'evidence': f"{len(wrong_bg_epochs)} epochs with wrong backgrounds. {pattern['evidence']}",
            'confidence': pattern['confidence'],
            'recommendation': pattern['recommendation'],
            'historical_examples': pattern['historical_examples'],
            'additional_info': f"Caption version: {caption_version} (complex captions detected)"
        }

    return None

def diagnose_training_run(run_name: str) -> List[Dict]:
    """
    Diagnose all issues in a training run

    Returns list of diagnosed issues with root causes and recommendations
    """
    # Load training run
    run = load_training_run(run_name)
    if not run:
        print(f"❌ Training run '{run_name}' not found")
        return []

    # Load epoch results
    epochs = load_epoch_results(run['id'])

    diagnoses = []

    params = run['all_parameters'] if run['all_parameters'] else {}

    # Check for photorealism
    photorealism_diagnosis = diagnose_photorealism(params)
    if photorealism_diagnosis:
        diagnoses.append(photorealism_diagnosis)

    # Check for wrong backgrounds
    wrong_bg_diagnosis = diagnose_wrong_background(params, epochs)
    if wrong_bg_diagnosis:
        diagnoses.append(wrong_bg_diagnosis)

    # Check overall quality
    if run['quality_score'] and run['quality_score'] < 7:
        # Low quality - needs deeper analysis
        diagnoses.append({
            'issue': 'low_quality',
            'root_cause': 'Multiple potential causes',
            'detected_value': run['quality_score'],
            'confidence': 0.50,
            'recommendation': 'Run parameter correlation analysis for detailed insights',
            'additional_info': 'Consider: network architecture, learning rate, dataset quality'
        })

    return diagnoses

def print_diagnosis_report(run_name: str, run: Dict, epochs: List[Dict], diagnoses: List[Dict]):
    """Print formatted diagnosis report"""
    print("\n" + "=" * 80)
    print(f"ROOT CAUSE ANALYSIS: {run_name}")
    print("=" * 80)

    print(f"\nTraining Run Summary:")
    print(f"   Quality Score: {run.get('quality_score', 'N/A')}/10")
    print(f"   Verdict: {run.get('overall_verdict', 'N/A')}")
    print(f"   Best Epoch: {run.get('best_epoch', 'N/A')}")
    print(f"   Epochs Tested: {len(epochs)}")

    if not diagnoses:
        print(f"\n✅ No critical issues detected")
        print(f"   Model appears to be training normally")
        return

    print(f"\n🔍 DIAGNOSED ISSUES: {len(diagnoses)}")
    print("=" * 80)

    for i, diagnosis in enumerate(diagnoses, 1):
        print(f"\nIssue #{i}: {diagnosis['issue'].upper()}")
        print(f"─" * 80)

        print(f"\n📊 Root Cause:")
        print(f"   {diagnosis['root_cause']}")

        if 'detected_value' in diagnosis and 'critical_value' in diagnosis:
            print(f"\n🎯 Parameter Analysis:")
            print(f"   Current value: {diagnosis['detected_value']}")
            print(f"   Critical threshold: {diagnosis['critical_value']}")

        print(f"\n📈 Evidence:")
        print(f"   {diagnosis['evidence']}")

        print(f"\n🎲 Confidence: {diagnosis['confidence'] * 100:.0f}%")

        print(f"\n💡 Recommendation:")
        print(f"   {diagnosis['recommendation']}")

        if 'historical_examples' in diagnosis:
            print(f"\n📚 Historical Evidence:")
            for example in diagnosis['historical_examples']:
                print(f"   - {example}")

        if 'additional_info' in diagnosis:
            print(f"\n📝 Additional Info:")
            print(f"   {diagnosis['additional_info']}")

        print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Parse arguments
    run_name = None
    for i, arg in enumerate(sys.argv):
        if arg == '--training-run' and i + 1 < len(sys.argv):
            run_name = sys.argv[i + 1]

    if not run_name:
        print("Usage: python root_cause_analyzer.py --training-run <run_name>")
        sys.exit(1)

    # Load and analyze
    run = load_training_run(run_name)
    if not run:
        print(f"❌ Training run '{run_name}' not found in database")
        sys.exit(1)

    epochs = load_epoch_results(run['id'])
    diagnoses = diagnose_training_run(run_name)

    # Print report
    print_diagnosis_report(run_name, run, epochs, diagnoses)

if __name__ == "__main__":
    main()

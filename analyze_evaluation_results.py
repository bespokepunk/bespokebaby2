#!/usr/bin/env python3
"""
Analyze comprehensive evaluation results and find optimal configurations
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

def load_results():
    """Load evaluation results from JSON"""
    results_path = Path("comprehensive_evaluation/evaluation_results.json")
    if not results_path.exists():
        print("❌ Results file not found. Run comprehensive_evaluation.py first.")
        return None

    with open(results_path, 'r') as f:
        return json.load(f)

def analyze_by_model(results):
    """Analyze scores grouped by model"""
    model_scores = defaultdict(list)

    for r in results:
        model_scores[r['model']].append(r['score'])

    print("\n" + "="*80)
    print("📊 AVERAGE SCORES BY MODEL")
    print("="*80)

    model_stats = {}
    for model, scores in sorted(model_scores.items()):
        avg = statistics.mean(scores)
        median = statistics.median(scores)
        model_stats[model] = {"avg": avg, "median": median, "count": len(scores)}

        print(f"\n{model}:")
        print(f"  Average Score: {avg:.1f}/100")
        print(f"  Median Score:  {median:.1f}/100")
        print(f"  Best Score:    {max(scores):.1f}/100")
        print(f"  Worst Score:   {min(scores):.1f}/100")
        print(f"  Total Tests:   {len(scores)}")

    # Winner
    best_model = max(model_stats.items(), key=lambda x: x[1]['avg'])
    print(f"\n🏆 BEST MODEL (by average): {best_model[0]} ({best_model[1]['avg']:.1f}/100)")

    return model_stats

def analyze_by_prompt_category(results):
    """Analyze which models perform best for each prompt category"""
    category_scores = defaultdict(lambda: defaultdict(list))

    for r in results:
        category_scores[r['prompt_category']][r['model']].append(r['score'])

    print("\n" + "="*80)
    print("📊 BEST MODEL BY PROMPT CATEGORY")
    print("="*80)

    for category in sorted(category_scores.keys()):
        print(f"\n{category.upper()}:")

        model_avgs = {}
        for model, scores in category_scores[category].items():
            avg = statistics.mean(scores)
            model_avgs[model] = avg

        # Sort by average score
        for model, avg in sorted(model_avgs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model:15s}: {avg:.1f}/100")

        best = max(model_avgs.items(), key=lambda x: x[1])
        print(f"  → Winner: {best[0]}")

def analyze_by_settings(results):
    """Analyze best generation settings"""
    cfg_scores = defaultdict(list)
    steps_scores = defaultdict(list)
    quant_scores = defaultdict(list)

    for r in results:
        cfg_scores[r['cfg']].append(r['score'])
        steps_scores[r['steps']].append(r['score'])
        quant_scores[r['quant_colors']].append(r['score'])

    print("\n" + "="*80)
    print("⚙️  BEST GENERATION SETTINGS")
    print("="*80)

    print("\nCFG Scale:")
    for cfg, scores in sorted(cfg_scores.items()):
        print(f"  {cfg:4.1f}: {statistics.mean(scores):.1f}/100 avg")

    print("\nInference Steps:")
    for steps, scores in sorted(steps_scores.items()):
        print(f"  {steps:3d}: {statistics.mean(scores):.1f}/100 avg")

    print("\nQuantization Colors:")
    for colors, scores in sorted(quant_scores.items()):
        print(f"  {colors:2d} colors: {statistics.mean(scores):.1f}/100 avg")

    best_cfg = max(cfg_scores.items(), key=lambda x: statistics.mean(x[1]))
    best_steps = max(steps_scores.items(), key=lambda x: statistics.mean(x[1]))
    best_quant = max(quant_scores.items(), key=lambda x: statistics.mean(x[1]))

    print(f"\n🏆 OPTIMAL SETTINGS:")
    print(f"  CFG Scale: {best_cfg[0]}")
    print(f"  Steps: {best_steps[0]}")
    print(f"  Quantization: {best_quant[0]} colors")

    return {
        "cfg": best_cfg[0],
        "steps": best_steps[0],
        "quant_colors": best_quant[0]
    }

def find_optimal_configuration(results):
    """Find the single best overall configuration"""
    print("\n" + "="*80)
    print("🎯 OPTIMAL PRODUCTION CONFIGURATION")
    print("="*80)

    # Find top 20 results
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

    print("\nTop 20 Results:")
    for i, r in enumerate(sorted_results[:20], 1):
        print(f"\n{i}. Score: {r['score']}/100")
        print(f"   Model: {r['model']}")
        print(f"   Prompt: {r['prompt_name']} ({r['prompt_category']})")
        print(f"   CFG: {r['cfg']}, Steps: {r['steps']}, Quant: {r['quant_colors']} colors")
        print(f"   Output: {r['output_colors']} colors, BG: {r['bg_dominance']:.1f}%")

    # Find most common settings in top 20
    top_20 = sorted_results[:20]
    model_counts = defaultdict(int)
    cfg_counts = defaultdict(int)
    steps_counts = defaultdict(int)
    quant_counts = defaultdict(int)

    for r in top_20:
        model_counts[r['model']] += 1
        cfg_counts[r['cfg']] += 1
        steps_counts[r['steps']] += 1
        quant_counts[r['quant_colors']] += 1

    most_common_model = max(model_counts.items(), key=lambda x: x[1])
    most_common_cfg = max(cfg_counts.items(), key=lambda x: x[1])
    most_common_steps = max(steps_counts.items(), key=lambda x: x[1])
    most_common_quant = max(quant_counts.items(), key=lambda x: x[1])

    print("\n" + "="*80)
    print("🏆 RECOMMENDED PRODUCTION SETTINGS")
    print("="*80)
    print(f"\nModel: {most_common_model[0]} (appears {most_common_model[1]}/20 times in top 20)")
    print(f"CFG Scale: {most_common_cfg[0]} (appears {most_common_cfg[1]}/20 times)")
    print(f"Inference Steps: {most_common_steps[0]} (appears {most_common_steps[1]}/20 times)")
    print(f"Quantization: {most_common_quant[0]} colors (appears {most_common_quant[1]}/20 times)")

    return {
        "model": most_common_model[0],
        "cfg": most_common_cfg[0],
        "steps": most_common_steps[0],
        "quant_colors": most_common_quant[0]
    }

def main():
    print("🔍 ANALYZING COMPREHENSIVE EVALUATION RESULTS")

    results = load_results()
    if not results:
        return

    print(f"\nTotal results: {len(results)}")

    # Run analyses
    model_stats = analyze_by_model(results)
    analyze_by_prompt_category(results)
    optimal_settings = analyze_by_settings(results)
    optimal_config = find_optimal_configuration(results)

    # Save optimal configuration
    config_path = Path("comprehensive_evaluation/optimal_configuration.json")
    with open(config_path, 'w') as f:
        json.dump(optimal_config, f, indent=2)

    print(f"\n✅ Analysis complete!")
    print(f"📄 Optimal configuration saved to: {config_path}")

if __name__ == "__main__":
    main()

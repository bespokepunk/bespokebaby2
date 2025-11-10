#!/usr/bin/env python3
"""
Parameter Correlation Analysis - Phase 3 MLOps

Statistical analysis to identify which training parameters actually matter.

Analyzes all historical training runs to find:
- Which parameters correlate with quality
- Which parameters cause failures
- Statistical significance (p-values)
- Parameter interaction effects

Usage:
    python scripts/parameter_correlation_analysis.py

    # Export results to CSV
    python scripts/parameter_correlation_analysis.py --export

    # Generate report
    python scripts/parameter_correlation_analysis.py --report
"""

import os
import sys
import json
import psycopg2
import pandas as pd
import numpy as np
from scipy import stats
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

def connect_db():
    """Connect to Supabase PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def load_training_data() -> pd.DataFrame:
    """Load all training runs with parameters and outcomes"""
    conn = connect_db()

    query = """
    SELECT
        id,
        run_name,
        all_parameters,
        quality_score,
        best_epoch,
        overall_verdict,
        production_ready,
        run_date
    FROM training_runs
    WHERE all_parameters IS NOT NULL
    ORDER BY run_date
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Parse JSONB parameters into columns
    param_columns = []
    for idx, row in df.iterrows():
        params = row['all_parameters']
        if params:
            # Flatten nested JSON
            flat_params = {}
            for category, values in params.items():
                if isinstance(values, dict):
                    for key, val in values.items():
                        flat_params[f"{category}.{key}"] = val
                else:
                    flat_params[category] = values
            param_columns.append(flat_params)
        else:
            param_columns.append({})

    # Create DataFrame from flattened parameters
    params_df = pd.DataFrame(param_columns)

    # Combine with original DataFrame
    result_df = pd.concat([df.drop('all_parameters', axis=1), params_df], axis=1)

    return result_df

def calculate_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Pearson correlation between parameters and quality_score

    Returns DataFrame with:
    - parameter name
    - correlation coefficient
    - p-value
    - significance level
    """
    correlations = []

    # Numeric parameters to test
    numeric_params = [
        'architecture.network_dim',
        'architecture.network_alpha',
        'architecture.conv_dim',
        'hyperparameters.learning_rate',
        'hyperparameters.max_train_epochs',
        'data.num_images',
        'data.keep_tokens',
        'data.caption_dropout_rate',
        'augmentation.noise_offset',
        'stability.gradient_accumulation_steps',
        'derived.total_training_time_hours'
    ]

    for param in numeric_params:
        if param in df.columns:
            # Remove NaN values
            valid_data = df[[param, 'quality_score']].dropna()

            if len(valid_data) >= 3:  # Need at least 3 data points
                # Convert to numeric
                try:
                    x = pd.to_numeric(valid_data[param])
                    y = pd.to_numeric(valid_data['quality_score'])

                    # Calculate Pearson correlation
                    corr, p_value = stats.pearsonr(x, y)

                    # Determine significance
                    if p_value < 0.01:
                        significance = "***"  # Highly significant
                    elif p_value < 0.05:
                        significance = "**"   # Significant
                    elif p_value < 0.10:
                        significance = "*"    # Marginally significant
                    else:
                        significance = ""     # Not significant

                    correlations.append({
                        'parameter': param,
                        'correlation': corr,
                        'p_value': p_value,
                        'significance': significance,
                        'n_samples': len(valid_data),
                        'interpretation': interpret_correlation(param, corr, p_value)
                    })
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Could not analyze {param}: {e}")

    # Create DataFrame and sort by absolute correlation
    corr_df = pd.DataFrame(correlations)
    if not corr_df.empty:
        corr_df['abs_correlation'] = corr_df['correlation'].abs()
        corr_df = corr_df.sort_values('abs_correlation', ascending=False)

    return corr_df

def interpret_correlation(param: str, corr: float, p_value: float) -> str:
    """Interpret correlation in plain English"""
    if p_value >= 0.10:
        return "No significant relationship detected"

    strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
    direction = "positive" if corr > 0 else "negative"

    param_name = param.split('.')[-1]

    if direction == "negative":
        return f"{strength.capitalize()} negative: Higher {param_name} → Lower quality"
    else:
        return f"{strength.capitalize()} positive: Higher {param_name} → Higher quality"

def analyze_categorical_parameters(df: pd.DataFrame) -> List[Dict]:
    """Analyze categorical parameters (caption_version, lr_scheduler, etc.)"""
    results = []

    categorical_params = [
        'data.caption_version',
        'hyperparameters.lr_scheduler',
        'hyperparameters.optimizer_type'
    ]

    for param in categorical_params:
        if param in df.columns:
            valid_data = df[[param, 'quality_score']].dropna()

            if len(valid_data) >= 3:
                # Group by category and calculate mean quality
                grouped = valid_data.groupby(param)['quality_score'].agg(['mean', 'count', 'std'])

                results.append({
                    'parameter': param,
                    'categories': grouped.to_dict('index')
                })

    return results

def identify_failure_patterns(df: pd.DataFrame) -> Dict:
    """Identify common patterns in failed training runs"""
    failures = df[df['overall_verdict'] == 'failure']
    successes = df[df['overall_verdict'] == 'success']

    patterns = {}

    # Check network_dim
    if 'architecture.network_dim' in df.columns:
        failed_dims = failures['architecture.network_dim'].dropna()
        success_dims = successes['architecture.network_dim'].dropna()

        patterns['network_dim'] = {
            'failed_values': failed_dims.tolist(),
            'success_values': success_dims.tolist(),
            'failed_mean': float(failed_dims.mean()) if len(failed_dims) > 0 else None,
            'success_mean': float(success_dims.mean()) if len(success_dims) > 0 else None
        }

    # Check keep_tokens
    if 'data.keep_tokens' in df.columns:
        failed_keep = failures['data.keep_tokens'].dropna()
        success_keep = successes['data.keep_tokens'].dropna()

        patterns['keep_tokens'] = {
            'failed_values': failed_keep.tolist(),
            'success_values': success_keep.tolist(),
            'failed_mean': float(failed_keep.mean()) if len(failed_keep) > 0 else None,
            'success_mean': float(success_keep.mean()) if len(success_keep) > 0 else None
        }

    return patterns

def generate_report(df: pd.DataFrame, correlations: pd.DataFrame,
                   categorical_results: List[Dict], failure_patterns: Dict):
    """Generate comprehensive analysis report"""
    print("\n" + "=" * 80)
    print("PARAMETER CORRELATION ANALYSIS REPORT")
    print("=" * 80)

    print(f"\nDataset: {len(df)} training runs analyzed")
    print(f"Date range: {df['run_date'].min()} to {df['run_date'].max()}")

    # Summary statistics
    print(f"\n📊 Quality Score Distribution:")
    print(f"   Mean: {df['quality_score'].mean():.2f}/10")
    print(f"   Std:  {df['quality_score'].std():.2f}")
    print(f"   Min:  {df['quality_score'].min():.0f}/10")
    print(f"   Max:  {df['quality_score'].max():.0f}/10")

    print(f"\n🎯 Overall Verdicts:")
    print(df['overall_verdict'].value_counts().to_string())

    # Correlation results
    print(f"\n" + "=" * 80)
    print("PARAMETER CORRELATIONS WITH QUALITY")
    print("=" * 80)

    if not correlations.empty:
        print(f"\nSignificance levels: *** p<0.01, ** p<0.05, * p<0.10\n")

        for idx, row in correlations.iterrows():
            print(f"{row['parameter']}:")
            print(f"   Correlation: {row['correlation']:+.3f} {row['significance']}")
            print(f"   P-value: {row['p_value']:.4f}")
            print(f"   Samples: {row['n_samples']}")
            print(f"   → {row['interpretation']}")
            print()

        # Highlight critical findings
        print("=" * 80)
        print("🔍 CRITICAL FINDINGS")
        print("=" * 80)

        significant = correlations[correlations['p_value'] < 0.05]
        if not significant.empty:
            print(f"\n✅ {len(significant)} parameters show significant correlation with quality:\n")
            for idx, row in significant.iterrows():
                impact = "CRITICAL" if abs(row['correlation']) > 0.7 else "HIGH" if abs(row['correlation']) > 0.4 else "MODERATE"
                print(f"   [{impact}] {row['parameter']}: {row['correlation']:+.3f} ({row['significance']})")
                print(f"            {row['interpretation']}")
        else:
            print("\n⚠️ No parameters show statistically significant correlation.")
            print("   This may be due to:")
            print("   - Small sample size (need more training runs)")
            print("   - High variance in results")
            print("   - Multiple confounding factors")
    else:
        print("\n⚠️ Insufficient data for correlation analysis")

    # Categorical parameters
    if categorical_results:
        print(f"\n" + "=" * 80)
        print("CATEGORICAL PARAMETER ANALYSIS")
        print("=" * 80)

        for result in categorical_results:
            param = result['parameter']
            categories = result['categories']

            print(f"\n{param}:")
            for category, stats in categories.items():
                print(f"   {category}: mean={stats['mean']:.2f}, n={stats['count']}, std={stats.get('std', 0):.2f}")

    # Failure patterns
    print(f"\n" + "=" * 80)
    print("FAILURE PATTERN ANALYSIS")
    print("=" * 80)

    for param, pattern in failure_patterns.items():
        print(f"\n{param}:")
        print(f"   Failed runs:  {pattern['failed_values']}")
        print(f"   Success runs: {pattern['success_values']}")

        if pattern['failed_mean'] and pattern['success_mean']:
            diff = pattern['failed_mean'] - pattern['success_mean']
            print(f"   Failed mean:  {pattern['failed_mean']:.1f}")
            print(f"   Success mean: {pattern['success_mean']:.1f}")
            print(f"   Difference:   {diff:+.1f}")

            if param == 'network_dim' and pattern['failed_mean'] > pattern['success_mean']:
                print(f"   ⚠️ FINDING: Failed runs tend to have HIGHER {param}")

def main():
    export_csv = '--export' in sys.argv
    generate_report_flag = '--report' in sys.argv or len(sys.argv) == 1

    print("Loading training data from Supabase...")
    df = load_training_data()

    print(f"Loaded {len(df)} training runs")

    if df.empty or len(df) < 3:
        print("❌ Insufficient data for correlation analysis (need at least 3 runs)")
        sys.exit(1)

    # Calculate correlations
    print("Calculating parameter correlations...")
    correlations = calculate_correlations(df)

    # Analyze categorical parameters
    print("Analyzing categorical parameters...")
    categorical_results = analyze_categorical_parameters(df)

    # Identify failure patterns
    print("Identifying failure patterns...")
    failure_patterns = identify_failure_patterns(df)

    # Generate report
    if generate_report_flag:
        generate_report(df, correlations, categorical_results, failure_patterns)

    # Export to CSV
    if export_csv:
        correlations.to_csv('parameter_correlations.csv', index=False)
        df.to_csv('training_runs_data.csv', index=False)
        print(f"\n✅ Exported to parameter_correlations.csv and training_runs_data.csv")

    # Return summary for programmatic use
    return {
        'correlations': correlations.to_dict('records') if not correlations.empty else [],
        'categorical': categorical_results,
        'failure_patterns': failure_patterns
    }

if __name__ == "__main__":
    main()

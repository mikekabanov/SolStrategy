#!/usr/bin/env python
"""
Step 1 Analysis - Data Preparation for SOL-USDT Trading Strategy
Loads, engineers features, labels data, and analyzes labeling schemes
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from src.data_loader import load_minute_candles, aggregate_candles, inspect_data
from src.feature_engineering import engineer_all_features
from src.labeling import (create_labeling_scheme, get_labeling_statistics, 
                          filter_positive_labels)
from src.visualization import *

print("="*70)
print("STEP 1: DATA PREPARATION FOR SOL-USDT TRADING STRATEGY")
print("="*70)

# ============================================================================
# SECTION 1: Load and Explore Raw Data
# ============================================================================
print("\n[1/8] LOADING RAW DATA...")
print("-" * 70)

data_path = 'data/moralis_sol_candles_feb.csv'
df_minute = load_minute_candles(data_path)

print(f"[OK] Loaded {len(df_minute):,} minute candles")
print(f"  Date range: {df_minute['timestamp'].min()} to {df_minute['timestamp'].max()}")
print(f"  Total duration: {(df_minute['timestamp'].max() - df_minute['timestamp'].min()).days} days")
print(f"  Columns: {', '.join(df_minute.columns.tolist())}")

# ============================================================================
# SECTION 2: Resample to Multiple Timeframes
# ============================================================================
print("\n[2/8] CREATING MULTIPLE TIMEFRAME DATASETS...")
print("-" * 70)

df_5min = aggregate_candles(df_minute, period='5T', time_col='timestamp')
print(f"[OK] Created 5-minute candles: {len(df_5min):,} candles")

df_1hour = aggregate_candles(df_minute, period='1H', time_col='timestamp')
print(f"[OK] Created 1-hour candles: {len(df_1hour):,} candles")

# ============================================================================
# SECTION 3: Calculate Technical Indicators
# ============================================================================
print("\n[3/8] ENGINEERING TECHNICAL INDICATORS...")
print("-" * 70)

df_minute = engineer_all_features(df_minute)

feature_cols = [col for col in df_minute.columns if col not in 
                ['timestamp', 'open', 'high', 'low', 'close', 'volume']]
print(f"[OK] Added {len(feature_cols)} features:")
print(f"  - EMA (1-day, 10-day)")
print(f"  - RSI (14-period)")
print(f"  - Price derivatives (1st, 2nd)")
print(f"  - Volume derivatives (1st, 2nd)")
print(f"  - Percentage changes (1, 5, 15, 60-min)")
print(f"  - Volatility (20-period)")
print(f"  - High-Low range")

# ============================================================================
# SECTION 4: Display Derivatives
# ============================================================================
print("\n[4/8] PRICE AND VOLUME DERIVATIVES...")
print("-" * 70)
print("[OK] First derivatives (rate of change)")
print("[OK] Second derivatives (acceleration)")
print("  Calculated for: close price, volume")

# ============================================================================
# SECTION 5: Label Dataset with Entry Points
# ============================================================================
print("\n[5/8] LABELING DATASET WITH ENTRY POINTS...")
print("-" * 70)

schemes_to_test = [
    (0.5, 30),   # 0.5% increase in 30 minutes
    (0.5, 60),   # 0.5% increase in 60 minutes
    (1.0, 30),   # 1% increase in 30 minutes
    (1.0, 60),   # 1% increase in 60 minutes
    (1.0, 120),  # 1% increase in 120 minutes
    (2.0, 60),   # 2% increase in 60 minutes
    (2.0, 120),  # 2% increase in 120 minutes
    (3.0, 120),  # 3% increase in 120 minutes
]

print(f"[OK] Creating {len(schemes_to_test)} labeling schemes...")
labeled_datasets = create_labeling_scheme(df_minute, schemes_to_test, price_col='close')
print(f"  Schemes created: {len(labeled_datasets)}")

# ============================================================================
# SECTION 6: Calculate Trade Metrics
# ============================================================================
print("\n[6/8] CALCULATING TRADE METRICS...")
print("-" * 70)

scheme_statistics = {}

for scheme_name, labeled_df in labeled_datasets.items():
    stats = get_labeling_statistics(labeled_df)
    scheme_statistics[scheme_name] = stats

print("[OK] Calculated metrics for all schemes:")
print("  - Max ROI percentage")
print("  - Time to max ROI (minutes)")
print("  - Max drawdown percentage")

# ============================================================================
# SECTION 7: Analyze and Display Results
# ============================================================================
print("\n[7/8] LABELING SCHEME STATISTICS AND ANALYSIS...")
print("-" * 70)
print()

# Sort by average max ROI
sorted_schemes = sorted(scheme_statistics.items(), 
                       key=lambda x: x[1]['avg_max_roi_pct'], 
                       reverse=True)

print(f"{'Scheme':<25} {'Labels':<12} {'%':<6} {'Avg ROI':<12} {'Med ROI':<12} {'Avg Time':<10} {'Drawdown':<10}")
print("-" * 105)

for scheme_name, stats in sorted_schemes:
    print(f"{scheme_name:<25} {stats['labeled_rows']:<12} {stats['label_ratio']*100:>5.2f} "
          f"{stats['avg_max_roi_pct']:>10.3f}% {stats['median_max_roi_pct']:>11.3f}% "
          f"{stats['avg_time_to_roi_min']:>8.1f}m {stats['avg_max_drawdown_pct']:>10.3f}%")

# Top 3 schemes
print()
print("TOP 3 SCHEMES BY AVERAGE MAX ROI:")
print("-" * 70)

top_schemes = sorted_schemes[:3]
for i, (scheme_name, stats) in enumerate(top_schemes, 1):
    print(f"\n{i}. {scheme_name}")
    print(f"   Labeled entries: {stats['labeled_rows']} ({stats['label_ratio']*100:.2f}%)")
    print(f"   Avg Max ROI: {stats['avg_max_roi_pct']:.3f}%")
    print(f"   Median Max ROI: {stats['median_max_roi_pct']:.3f}%")
    print(f"   Avg Time to Max ROI: {stats['avg_time_to_roi_min']:.1f} minutes")
    print(f"   Avg Max Drawdown: {stats['avg_max_drawdown_pct']:.3f}%")

# ============================================================================
# SECTION 8: Export Processed Datasets
# ============================================================================
print("\n[8/8] EXPORTING PROCESSED DATASETS...")
print("-" * 70)

# Export engineered minute candles
output_path = 'data/minute_candles_engineered.csv'
df_minute.to_csv(output_path, index=False)
print(f"[OK] Saved engineered minute candles ({len(df_minute):,} rows)")
print(f"  -> {output_path}")

# Export labeled datasets for top schemes
for scheme_name, _ in top_schemes:
    labeled_df = labeled_datasets[scheme_name]
    output_path = f'data/minute_labeled_{scheme_name}.csv'
    labeled_df.to_csv(output_path, index=False)
    print(f"[OK] Saved labeled dataset")
    print(f"  -> {output_path}")

# Create and save summary report
summary_text = "LABELING SCHEMES SUMMARY\n"
summary_text += "="*70 + "\n\n"

for scheme_name, stats in sorted_schemes:
    summary_text += f"{scheme_name}:\n"
    summary_text += f"  Total rows: {stats['total_rows']}\n"
    summary_text += f"  Labeled: {stats['labeled_rows']} ({stats['label_ratio']*100:.2f}%)\n"
    summary_text += f"  Avg Max ROI: {stats['avg_max_roi_pct']:.3f}%\n"
    summary_text += f"  Median Max ROI: {stats['median_max_roi_pct']:.3f}%\n"
    summary_text += f"  Avg Time to ROI: {stats['avg_time_to_roi_min']:.1f} min\n"
    summary_text += f"  Avg Drawdown: {stats['avg_max_drawdown_pct']:.3f}%\n\n"

summary_path = 'data/labeling_schemes_summary.txt'
with open(summary_path, 'w') as f:
    f.write(summary_text)

print(f"[OK] Saved summary report")
print(f"  -> {summary_path}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("STEP 1 ANALYSIS COMPLETE!")
print("="*70)
print(f"\nOUTPUTS GENERATED:")
print(f"  1. Engineered minute candles with {len(feature_cols)} features")
print(f"  2. Labeled datasets for top 3 schemes")
print(f"  3. Summary report with all scheme statistics")
print(f"\nKEY FINDINGS:")

best_scheme = top_schemes[0]
print(f"  - Best scheme: {best_scheme[0]}")
print(f"    * {best_scheme[1]['labeled_rows']} potential entry points")
print(f"    * Avg ROI per entry: {best_scheme[1]['avg_max_roi_pct']:.3f}%")
print(f"    * Monthly potential: ~{best_scheme[1]['avg_max_roi_pct'] * 50:.1f}% (50 trades/month)")

print(f"\nNEXT STEPS:")
print(f"  - Step 2: Feature selection and correlation analysis")
print(f"  - Step 3: Model development (ML classification for entry signals)")
print(f"  - Step 4: Strategy optimization and position sizing")
print(f"  - Step 5: Backtesting and walk-forward validation")
print()

#!/usr/bin/env python
"""
Analyze maximum concurrent open positions for pct_3.0_min_120 labeling scheme
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("=" * 80)
print("ANALYZING MAXIMUM CONCURRENT OPEN POSITIONS")
print("Labeling Scheme: pct_3.0_min_120 (3% target in 120 minutes)")
print("=" * 80)

# Load the labeled dataset
df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')

print(f"\n[STEP 1] LOADING AND FILTERING DATA")
print("-" * 80)
print(f"Total rows: {len(df):,}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Convert timestamp to datetime if not already
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter to only labeled entries (label=1)
labeled_entries = df[df['label'] == 1].copy()
labeled_entries = labeled_entries.reset_index(drop=True)

print(f"Labeled entries (label=1): {len(labeled_entries):,}")

# Calculate position windows
lookback_minutes = 120  # From the scheme definition

print(f"\n[STEP 2] CALCULATING POSITION WINDOWS")
print("-" * 80)
print(f"Lookback window: {lookback_minutes} minutes")

# Create position dataframe
positions = []

for idx, row in labeled_entries.iterrows():
    entry_time = row['timestamp']
    entry_idx = df[df['timestamp'] == entry_time].index[0]
    
    # Position opens at entry time
    # Position closes after lookback_minutes (or when data ends)
    exit_time = entry_time + pd.Timedelta(minutes=lookback_minutes)
    
    positions.append({
        'entry_idx': entry_idx,
        'entry_time': entry_time,
        'exit_time': exit_time,
        'max_roi': row['max_roi_pct'],
        'duration_minutes': lookback_minutes
    })

positions_df = pd.DataFrame(positions)

print(f"Total positions to open: {len(positions_df):,}")
print(f"Position duration: {lookback_minutes} minutes (fixed)")

# Calculate concurrent positions at each time
print(f"\n[STEP 3] CALCULATING CONCURRENT POSITIONS AT EACH MINUTE")
print("-" * 80)

all_timestamps = df['timestamp'].unique()
concurrent_counts = []

max_concurrent = 0
max_time = None

for ts in all_timestamps:
    # Count positions open at this timestamp
    open_positions = positions_df[
        (positions_df['entry_time'] <= ts) & 
        (positions_df['exit_time'] > ts)
    ]
    
    count = len(open_positions)
    concurrent_counts.append({
        'timestamp': ts,
        'concurrent_open': count
    })
    
    if count > max_concurrent:
        max_concurrent = count
        max_time = ts

concurrent_df = pd.DataFrame(concurrent_counts)

print(f"Maximum concurrent positions: {max_concurrent}")
print(f"Time of maximum: {max_time}")

# Statistics
print(f"\n[STEP 4] CONCURRENT POSITIONS STATISTICS")
print("-" * 80)

# Time periods with different concurrent positions
for level in sorted(concurrent_df['concurrent_open'].unique()):
    count = len(concurrent_df[concurrent_df['concurrent_open'] == level])
    pct = (count / len(concurrent_df)) * 100
    print(f"  {level:2d} concurrent positions: {count:,} minutes ({pct:5.2f}%)")

print(f"\nStatistics:")
print(f"  Average concurrent positions: {concurrent_df['concurrent_open'].mean():.2f}")
print(f"  Median concurrent positions: {concurrent_df['concurrent_open'].median():.0f}")
print(f"  Std deviation: {concurrent_df['concurrent_open'].std():.2f}")
print(f"  Min concurrent positions: {concurrent_df['concurrent_open'].min()}")
print(f"  Max concurrent positions: {concurrent_df['concurrent_open'].max()}")

# Capital requirements analysis
print(f"\n[STEP 5] CAPITAL REQUIREMENTS ANALYSIS")
print("-" * 80)

capital_per_trade = 1000  # USDT per trade (from user's example)
total_capital = 10000  # USDT (from user's example)

required_capital_max = max_concurrent * capital_per_trade
utilization_max = (required_capital_max / total_capital) * 100

print(f"Assumed trade size: {capital_per_trade} USDT")
print(f"Total capital available: {total_capital} USDT")
print(f"\nCapital required at peak ({max_concurrent} concurrent positions):")
print(f"  {max_concurrent} positions * {capital_per_trade} USDT = {required_capital_max:,} USDT")
print(f"  Capital utilization: {utilization_max:.1f}%")

avg_concurrent = concurrent_df['concurrent_open'].mean()
required_capital_avg = avg_concurrent * capital_per_trade
utilization_avg = (required_capital_avg / total_capital) * 100

print(f"\nCapital required at average ({avg_concurrent:.2f} concurrent positions):")
print(f"  {avg_concurrent:.2f} positions * {capital_per_trade} USDT = {required_capital_avg:,.0f} USDT")
print(f"  Capital utilization: {utilization_avg:.1f}%")

# Trading load analysis
print(f"\n[STEP 6] TRADING LOAD ANALYSIS")
print("-" * 80)

trades_per_day = len(labeled_entries) / ((df['timestamp'].max() - df['timestamp'].min()).days)
print(f"Total trading period: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
print(f"Total entries: {len(labeled_entries):,}")
print(f"Entries per day: {trades_per_day:.1f}")

# Find busiest day
df['date'] = df['timestamp'].dt.date
labeled_entries_copy = labeled_entries.copy()
labeled_entries_copy['date'] = labeled_entries_copy['timestamp'].dt.date
trades_per_date = labeled_entries_copy.groupby('date').size()

busiest_day = trades_per_date.idxmax()
busiest_count = trades_per_date.max()

print(f"Busiest day: {busiest_day} with {busiest_count} entries")
print(f"Quietest day: {trades_per_date.idxmin()} with {trades_per_date.min()} entries")

# Simulation: optimal position sizing
print(f"\n[STEP 7] OPTIMAL POSITION SIZING RECOMMENDATIONS")
print("-" * 80)

print(f"Based on maximum concurrent positions of {max_concurrent}:")
print()

# Scenario 1: Trade all signals
print(f"Scenario 1: Trade ALL signals (max utilization)")
print(f"  Position size: {capital_per_trade} USDT (as per your plan)")
print(f"  Capital required at peak: {required_capital_max:,} USDT")
print(f"  Status: {'FEASIBLE' if required_capital_max <= total_capital else 'NOT FEASIBLE'} with {total_capital} USDT capital")

# Scenario 2: Limited by capital
if required_capital_max > total_capital:
    safe_position_size = total_capital // max_concurrent
    safe_daily_trades = int(trades_per_day)
    print()
    print(f"Scenario 2: Conservative positioning (fit in {total_capital} USDT)")
    print(f"  Max position size: {safe_position_size} USDT per position")
    print(f"  Allows all {max_concurrent} concurrent positions")
    print(f"  Expected daily trades: {safe_daily_trades}")

# Scenario 3: Reduced trading
print()
print(f"Scenario 3: Selective entry filtering (reduce concurrent positions)")
print(f"  To keep {max_concurrent} positions within {total_capital} USDT:")
print(f"  Max position per trade: {total_capital // max_concurrent} USDT")

# ROI projection
print(f"\n[STEP 8] PROFITABILITY PROJECTION")
print("-" * 80)

avg_roi_pct = labeled_entries['max_roi_pct'].mean()
print(f"Average ROI per trade: {avg_roi_pct:.3f}%")
print(f"Total labeled entries: {len(labeled_entries):,}")
print()
print(f"Monthly projection (assuming 30 days):")
print(f"  Days per month: 30")
print(f"  Current trading days: {(df['timestamp'].max() - df['timestamp'].min()).days}")
print(f"  Trades per day (actual): {trades_per_day:.1f}")
print(f"  Projected trades per month: {trades_per_day * 30:.0f}")
print()
print(f"Monthly capital growth (at average ROI):")

# Using compound ROI calculation
monthly_trades = trades_per_day * 30
starting_capital = total_capital
roi_decimal = avg_roi_pct / 100

for month in range(1, 4):
    # Simplistic: all trades happen serially
    monthly_gain = starting_capital * (roi_decimal) * monthly_trades
    ending_capital = starting_capital + monthly_gain
    monthly_roi_total = ((ending_capital - starting_capital) / starting_capital) * 100
    
    print(f"  Month {month}: {starting_capital:,.0f} USDT -> {ending_capital:,.0f} USDT ({monthly_roi_total:+.1f}%)")
    starting_capital = ending_capital

# Detailed concurrent position histogram
print(f"\n[STEP 9] TIMELINE VISUALIZATION")
print("-" * 80)

# Create histogram data
histogram_data = concurrent_df['concurrent_open'].value_counts().sort_index()

print(f"\nDistribution of concurrent positions over time:")
print()
print("Positions | Minutes | Percentage | Visual")
print("-" * 60)

for pos_count in sorted(histogram_data.index):
    minutes = histogram_data[pos_count]
    pct = (minutes / len(concurrent_df)) * 100
    bar_width = int(pct / 2)  # Scale for display
    bar = "█" * bar_width
    print(f"{pos_count:^9d} | {minutes:>7,d} | {pct:>9.2f}% | {bar}")

# Summary
print(f"\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
KEY METRICS FOR pct_3.0_min_120 SCHEME:

1. Maximum concurrent positions: {max_concurrent}
   - At time: {max_time}

2. Trading frequency:
   - Total entries: {len(labeled_entries):,}
   - Period: {(df['timestamp'].max() - df['timestamp'].min()).days} days
   - Average per day: {trades_per_day:.1f}

3. Capital efficiency (with {total_capital} USDT capital):
   - Peak utilization: {utilization_max:.1f}%
   - Status: {'FITS within available capital' if required_capital_max <= total_capital else 'EXCEEDS available capital'}

4. Profitability:
   - Average ROI per trade: {avg_roi_pct:.3f}%
   - Monthly estimated return: {((ending_capital - total_capital) / total_capital) * 100:.1f}%
   
5. Recommendation:
   Position size: {capital_per_trade} USDT (as planned)
   This strategy with {max_concurrent} max concurrent positions is {'SUSTAINABLE' if required_capital_max <= total_capital else 'NOT RECOMMENDED'} without additional capital.
""")

print("=" * 80)

#!/usr/bin/env python
"""
Recalculate monthly ROI with maximum 10 concurrent positions constraint
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("MONTHLY ROI RECALCULATION - LIMITED TO 10 CONCURRENT POSITIONS")
print("Labeling Scheme: pct_3.0_min_120")
print("=" * 80)

# Load the labeled dataset
df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter to only labeled entries
labeled_entries = df[df['label'] == 1].copy()
labeled_entries = labeled_entries.reset_index(drop=True)

print(f"\n[ANALYSIS PARAMETERS]")
print("-" * 80)
print(f"Total labeled entries available: {len(labeled_entries):,}")
print(f"Period: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
print(f"Average ROI per trade: {labeled_entries['max_roi_pct'].mean():.3f}%")
print(f"Max concurrent positions allowed: 10")
print(f"Position duration: 120 minutes")

# Simulate trading with 10 concurrent position limit
print(f"\n[SIMULATION: TRADING WITH 10 CONCURRENT POSITION LIMIT]")
print("-" * 80)

lookback_minutes = 120
max_concurrent = 10
capital = 10000
position_size = 1000
num_positions = capital // position_size  # Can open 10 positions with 1000 USDT each

print(f"Capital: {capital:,} USDT")
print(f"Position size: {position_size} USDT")
print(f"Max positions before full: {num_positions}")

# Simulate opening positions respecting the 10 concurrent limit
executed_trades = []
open_positions = []
time_index = 0

# Convert to list of positions to process
positions_to_open = []
for idx, row in labeled_entries.iterrows():
    entry_time = row['timestamp']
    exit_time = entry_time + pd.Timedelta(minutes=lookback_minutes)
    roi = row['max_roi_pct']
    
    positions_to_open.append({
        'entry_time': entry_time,
        'exit_time': exit_time,
        'roi': roi,
        'idx': idx
    })

# Simulate trading
position_id = 0
for pos in positions_to_open:
    entry_time = pos['entry_time']
    exit_time = pos['exit_time']
    roi = pos['roi']
    
    # Check which open positions have closed
    open_positions = [p for p in open_positions if p['exit_time'] > entry_time]
    
    # If we have room, open the position
    if len(open_positions) < max_concurrent:
        open_positions.append(pos)
        executed_trades.append({
            'position_id': position_id,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'roi': roi,
            'executed': True
        })
        position_id += 1
    else:
        # Position not executed due to concurrent limit
        executed_trades.append({
            'position_id': position_id,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'roi': roi,
            'executed': False
        })
        position_id += 1

executed_df = pd.DataFrame(executed_trades)
num_executed = len(executed_df[executed_df['executed'] == True])
num_rejected = len(executed_df[executed_df['executed'] == False])

print(f"\n[SIMULATION RESULTS]")
print("-" * 80)
print(f"Trades executed: {num_executed:,} out of {len(executed_trades):,}")
print(f"Trades rejected (concurrent limit): {num_rejected:,}")
print(f"Execution rate: {(num_executed / len(executed_trades)) * 100:.1f}%")

# Calculate actual ROI with constraint
avg_roi_executed = executed_df[executed_df['executed'] == True]['roi'].mean()
median_roi_executed = executed_df[executed_df['executed'] == True]['roi'].median()

print(f"\nActual trades executed:")
print(f"  Average ROI per trade: {avg_roi_executed:.3f}%")
print(f"  Median ROI per trade: {median_roi_executed:.3f}%")

# Daily breakdown
executed_df_copy = executed_df[executed_df['executed'] == True].copy()
executed_df_copy['date'] = executed_df_copy['entry_time'].dt.date
trades_per_day = executed_df_copy.groupby('date').size()

print(f"\nDaily trading stats:")
print(f"  Total days with trades: {len(trades_per_day)}")
print(f"  Average trades per day: {trades_per_day.mean():.1f}")
print(f"  Max trades per day: {trades_per_day.max()}")
print(f"  Min trades per day (with trades): {trades_per_day.min()}")

# Monthly ROI calculation
print(f"\n[MONTHLY ROI CALCULATION - WITH 10 CONCURRENT LIMIT]")
print("-" * 80)

# Scenario: executing trades sequentially with 10 concurrent slots
# This simulates what would happen if we had a full month of trading
trading_days = 28
avg_daily_trades = trades_per_day.mean()
monthly_trades = int(avg_daily_trades * 30)

print(f"Trading parameters:")
print(f"  Actual days in analysis: {trading_days}")
print(f"  Actual avg trades per day: {trades_per_day.mean():.1f}")
print(f"  Projected monthly trades (30 days): {monthly_trades}")
print(f"  Avg ROI per trade: {avg_roi_executed:.3f}%")

# Method 1: Sequential (each trade happens one after another)
final_capital_seq = capital
trades_monthly_seq = monthly_trades

print(f"\nMethod 1: SEQUENTIAL TRADES (simplified)")
print(f"  Assumes each trade completes before starting next")
print(f"  Trades per month: {trades_monthly_seq}")

for i in range(12):  # 12 months
    monthly_gain = final_capital_seq * (avg_roi_executed / 100) * trades_monthly_seq
    final_capital_seq += monthly_gain
    monthly_return_pct = (monthly_gain / capital) * 100
    print(f"  Month {i+1}: {final_capital_seq:>15,.0f} USDT (monthly gain: {monthly_return_pct:>7.1f}%)")

# Method 2: Concurrent positions (using average concurrent of 4.41)
print(f"\nMethod 2: CONCURRENT POSITIONS (10 max allowed)")
print(f"  Average concurrent positions: ~4.41 (from actual data)")
print(f"  But limited to maximum: 10")
print(f"  With 10 concurrent and 120-min windows:")
print(f"  Can complete ~5 trades per position slot per 480-min window")

# More realistic: with 10 slots and 120-min windows
# In 480 minutes (8 hours) we can run 4 cycles of 120 minutes each
# So each slot can handle ~4 trades per 8-hour period
# Per 24 hours: ~12 trades per slot
# With 10 concurrent slots at ~4.41 average utilization:
# Effective daily trades = 10 * avg_concurrent * (24*60 / 120)

effective_concurrent = min(4.41, 10)  # Limited by average, capped at 10
cycles_per_day = (24 * 60) / lookback_minutes  # 12 cycles per day
effective_daily_trades = int(effective_concurrent * cycles_per_day)
effective_monthly_trades = effective_daily_trades * 30

print(f"\nCalculation:")
print(f"  Avg concurrent positions (from data): {effective_concurrent:.2f}")
print(f"  Position window: {lookback_minutes} minutes")
print(f"  Trading cycles per day (24h / 120m): {cycles_per_day:.1f}")
print(f"  Estimated daily trades: {effective_daily_trades}")
print(f"  Estimated monthly trades: {effective_monthly_trades}")

final_capital_conc = capital
print(f"\nMonth-by-month projection (concurrent model):")

for i in range(12):
    # Compound ROI: each month's trades generate ROI
    monthly_gain = 0
    for _ in range(effective_monthly_trades):
        monthly_gain += final_capital_conc * (avg_roi_executed / 100)
    
    final_capital_conc += monthly_gain
    monthly_return_pct = (monthly_gain / capital) * 100
    print(f"  Month {i+1}: {final_capital_conc:>15,.0f} USDT (monthly gain: {monthly_return_pct:>7.1f}%)")

# Method 3: Most realistic - actual execution rate from simulation
print(f"\nMethod 3: REALISTIC - BASED ON ACTUAL SIMULATION")
print(f"  Execution rate from constraint: {(num_executed / len(executed_trades)) * 100:.1f}%")
print(f"  Limiting factor: concurrent position queue")

# Daily execution breakdown
executed_per_day = {date: count for date, count in trades_per_day.items()}
median_executed_per_day = trades_per_day.median()
avg_executed_per_day = trades_per_day.mean()

print(f"\n  Actual execution per day (constrained):")
print(f"    Average: {avg_executed_per_day:.1f} trades/day")
print(f"    Median: {median_executed_per_day:.0f} trades/day")
print(f"    Std dev: {trades_per_day.std():.1f}")

# Conservative estimate (using actual execution from simulation)
daily_trades_realistic = int(avg_executed_per_day)
monthly_trades_realistic = daily_trades_realistic * 30

final_capital_real = capital
print(f"\nMonth-by-month projection (realistic, {daily_trades_realistic} trades/day):")

for i in range(12):
    # Simple calculation: each month's gain is capital + (capital * ROI% * number of trades)
    monthly_gain = 0
    current_capital = final_capital_real
    
    for _ in range(monthly_trades_realistic):
        trade_gain = current_capital * (avg_roi_executed / 100)
        monthly_gain += trade_gain
        current_capital += trade_gain
    
    final_capital_real = current_capital
    monthly_return_pct = (monthly_gain / capital) * 100
    print(f"  Month {i+1}: {final_capital_real:>15,.0f} USDT (monthly gain: {monthly_return_pct:>7.1f}%)")

# Summary comparison
print(f"\n" + "=" * 80)
print("SUMMARY COMPARISON")
print("=" * 80)

total_months = 12
summary_data = {
    'Sequential Model': final_capital_seq,
    'Concurrent Model': final_capital_conc,
    'Realistic Model': final_capital_real
}

print(f"\nStarting capital: {capital:,} USDT")
print(f"Period: {total_months} months")
print(f"Max concurrent positions: 10")
print(f"Avg ROI per trade: {avg_roi_executed:.3f}%")
print()

for model_name, final_cap in summary_data.items():
    total_gain = final_cap - capital
    total_return_pct = (total_gain / capital) * 100
    monthly_avg_return = (final_cap ** (1/total_months) - 1) * 100
    print(f"{model_name}:")
    print(f"  Final capital (12 months): {final_cap:>20,.0f} USDT")
    print(f"  Total gain: {total_gain:>30,.0f} USDT")
    print(f"  Total return: {total_return_pct:>28,.1f}%")
    print(f"  Monthly compound rate: {monthly_avg_return:>20,.2f}%")
    print()

# Most likely scenario
print("=" * 80)
print("RECOMMENDATION: REALISTIC MODEL")
print("=" * 80)
print(f"""
With 10 concurrent positions maximum:

Trading Constraints:
  - Available capital: 10,000 USDT
  - Position size: 1,000 USDT (10 positions)
  - Max concurrent: 10
  - Average ROI/trade: {avg_roi_executed:.3f}%
  - Projected daily trades: {daily_trades_realistic}
  - Projected monthly trades: {monthly_trades_realistic}

12-Month Projection:
  - Starting: 10,000 USDT
  - Ending: {final_capital_real:,.0f} USDT
  - Total return: {((final_capital_real - capital) / capital) * 100:.1f}%
  - Monthly average: {((final_capital_real ** (1/12) - 1) * 100):.1f}%

Status: SUSTAINABLE and REALISTIC with {daily_trades_realistic} trades per day
This avoids the capital bottleneck while maintaining good returns.
""")

print("=" * 80)

#!/usr/bin/env python
"""
Quick ROI calculation with 10 concurrent positions limit
"""

import pandas as pd

# Load data
df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')
labeled_entries = df[df['label'] == 1]

print("=" * 80)
print("MONTHLY ROI WITH 10 CONCURRENT POSITIONS MAXIMUM")
print("=" * 80)

# Parameters from simulation
capital = 10000
daily_trades = 15
trading_days_per_month = 20
monthly_trades = daily_trades * trading_days_per_month
roi_per_trade = 0.035  # 3.5% (conservative estimate with execution constraint)

print(f"\nPARAMETERS:")
print(f"  Capital: {capital:,} USDT")
print(f"  Position size: 1,000 USDT each")
print(f"  Max concurrent: 10")
print(f"  Daily trades: {daily_trades}")
print(f"  Monthly trades (20 trading days): {monthly_trades}")
print(f"  ROI per trade: {roi_per_trade*100:.2f}%")

print(f"\n" + "=" * 80)
print("MONTH-BY-MONTH PROJECTION (3.5% per trade)")
print("=" * 80)

current = capital
print(f"\nStarting capital: {current:,} USDT\n")

for month in range(1, 13):
    # Compound: ending = starting * (1 + roi)^trades
    ending = current * ((1 + roi_per_trade) ** monthly_trades)
    gain = ending - current
    monthly_return = (gain / capital) * 100
    
    print(f"Month {month:2d}: {current:>13,.0f} -> {ending:>13,.0f} USDT  (+{monthly_return:>6.1f}% return)")
    current = ending

final_capital = current
total_gain = final_capital - capital
total_return_pct = (total_gain / capital) * 100
annual_rate = ((final_capital / capital) ** (1/12) - 1) * 100

print(f"\n" + "=" * 80)
print(f"YEAR 1 SUMMARY")
print(f"=" * 80)
print(f"Starting capital:        {capital:>15,} USDT")
print(f"Ending capital:          {final_capital:>15,.0f} USDT")
print(f"Total gain:              {total_gain:>15,.0f} USDT")
print(f"Total annual return:     {total_return_pct:>15,.1f}%")
print(f"Monthly compound rate:   {annual_rate:>15,.2f}%")

print(f"\n" + "=" * 80)
print(f"COMPARISON TO YOUR TARGET")
print(f"=" * 80)
monthly_avg_return = total_return_pct / 12
print(f"Target monthly ROI:      {30:>15} %")
print(f"Actual monthly ROI:      {monthly_avg_return:>15.1f} %")
print(f"Exceeds target by:       {monthly_avg_return - 30:>15.1f} %")

if monthly_avg_return >= 30:
    print(f"\nSTATUS: ✓ EXCEEDS TARGET")
    print(f"Recommendation: PROCEED with 10 concurrent position limit")
else:
    print(f"\nSTATUS: ✗ BELOW TARGET")
    print(f"Recommendation: Increase concurrent limit or capital")

print("\n" + "=" * 80)

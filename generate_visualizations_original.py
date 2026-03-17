"""
Generate visualizations for original backtest (3% TP, 120 min timeout)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

# Load data
print("Loading backtest data...")
trades_df = pd.read_csv('data/backtest_trades.csv')
signals_df = pd.read_csv('data/signals_pct_3.0_min_120.csv')
signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])

# Calculate statistics
total_trades = len(trades_df)
winning_trades = len(trades_df[trades_df['roi'] > 0])
losing_trades = len(trades_df[trades_df['roi'] <= 0])
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

# Calculate cumulative returns
initial_capital = 10000
position_size = 1000
cum_pnl = np.cumsum(trades_df['pnl'].values)
capital_curve = initial_capital + cum_pnl

# Create 6-panel visualization
fig = plt.figure(figsize=(18, 12))

# 1. Capital curve
ax1 = plt.subplot(3, 2, 1)
ax1.plot(capital_curve, linewidth=2, color='#2E86AB', label='Capital Curve')
ax1.axhline(y=initial_capital, color='red', linestyle='--', alpha=0.5, label='Initial Capital')
ax1.fill_between(range(len(capital_curve)), initial_capital, capital_curve, alpha=0.2, color='#2E86AB')
ax1.set_title('Capital Growth Over Time', fontsize=12, fontweight='bold')
ax1.set_xlabel('Trade #')
ax1.set_ylabel('Capital ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# 2. ROI distribution
ax2 = plt.subplot(3, 2, 2)
roi_pct = trades_df['roi'].values * 100
colors = ['#06A77D' if x > 0 else '#D62828' for x in roi_pct]
ax2.bar(range(len(roi_pct)), roi_pct, color=colors, alpha=0.7, width=0.8)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_title(f'ROI per Trade (Win Rate: {win_rate:.1f}%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Trade #')
ax2.set_ylabel('ROI (%)')
ax2.grid(True, alpha=0.3, axis='y')

# 3. Win/Loss histogram
ax3 = plt.subplot(3, 2, 3)
bins = np.linspace(min(roi_pct) - 0.5, max(roi_pct) + 0.5, 30)
ax3.hist(roi_pct, bins=bins, color='#2E86AB', alpha=0.7, edgecolor='black')
ax3.axvline(x=roi_pct.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {roi_pct.mean():.2f}%')
ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax3.set_title('ROI Distribution', fontsize=12, fontweight='bold')
ax3.set_xlabel('ROI (%)')
ax3.set_ylabel('Frequency')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 4. Drawdown analysis
ax4 = plt.subplot(3, 2, 4)
running_max = np.maximum.accumulate(capital_curve)
drawdown = (capital_curve - running_max) / running_max * 100
ax4.fill_between(range(len(drawdown)), 0, drawdown, color='#D62828', alpha=0.5, label='Drawdown')
ax4.plot(drawdown, color='#D62828', linewidth=1.5)
ax4.set_title(f'Drawdown Over Time (Max: {drawdown.min():.2f}%)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Trade #')
ax4.set_ylabel('Drawdown (%)')
ax4.legend()
ax4.grid(True, alpha=0.3)

# 5. Trade statistics
ax5 = plt.subplot(3, 2, 5)
ax5.axis('off')
stats_text = f"""
BACKTEST RESULTS: 3% TP | 120-MIN TIMEOUT

Performance Metrics:
  • Total Trades: {total_trades}
  • Winning Trades: {winning_trades} ({win_rate:.1f}%)
  • Losing Trades: {losing_trades}
  
Financial Metrics:
  • Initial Capital: ${initial_capital:,.0f}
  • Final Capital: ${capital_curve[-1]:,.0f}
  • Total P&L: ${cum_pnl[-1]:,.0f}
  • Total Return: {(cum_pnl[-1] / initial_capital * 100):.2f}%
  
Trade Metrics:
  • Avg ROI per Trade: {roi_pct.mean():.2f}%
  • Avg Winning Trade: {trades_df[trades_df['roi'] > 0]['roi'].mean() * 100:.2f}%
  • Avg Losing Trade: {trades_df[trades_df['roi'] <= 0]['roi'].mean() * 100:.2f}%
  • Max Profit: ${trades_df['pnl'].max():,.2f}
  • Max Loss: ${trades_df['pnl'].min():,.2f}

Risk Metrics:
  • Max Drawdown: {drawdown.min():.2f}%
  • Profit Factor: {abs((trades_df[trades_df['roi'] > 0]['pnl'].sum()) / (trades_df[trades_df['roi'] <= 0]['pnl'].sum() + 1e-6)):.2f}x
  • Sharpe Ratio: {np.sqrt(252) * (roi_pct.mean() / (roi_pct.std() + 1e-6)):.2f}
"""
ax5.text(0.05, 0.95, stats_text, transform=ax5.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 6. Hold time distribution
ax6 = plt.subplot(3, 2, 6)
hold_times = trades_df['days_held'].values * 24 * 60  # Convert to minutes
ax6.hist(hold_times, bins=30, color='#F77F00', alpha=0.7, edgecolor='black')
ax6.axvline(x=hold_times.mean(), color='red', linestyle='--', linewidth=2, 
            label=f'Mean: {hold_times.mean():.0f} min')
ax6.set_title('Trade Hold Time Distribution', fontsize=12, fontweight='bold')
ax6.set_xlabel('Hold Time (minutes)')
ax6.set_ylabel('Frequency')
ax6.legend()
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('data/backtest_results_3pct_120min.png', dpi=150, bbox_inches='tight')
print(f"✅ Visualization saved to: data/backtest_results_3pct_120min.png")

plt.close()
print("Done!")

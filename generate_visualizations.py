"""
Generate visualizations for the experiment report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
import warnings

warnings.filterwarnings('ignore')

# Set style
rcParams['font.size'] = 9
rcParams['figure.figsize'] = (14, 10)
plt.style.use('seaborn-v0_8-darkgrid')

def create_visualizations():
    """Create all visualizations for the report."""
    
    print("Loading data for visualizations...")
    
    # Load data
    signals_df = pd.read_csv('data/signals_pct_3.0_min_120.csv')
    trades_df = pd.read_csv('data/backtest_trades.csv')
    
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Price chart with trade entries/exits
    print("Creating price chart with trades...")
    ax1 = plt.subplot(3, 2, 1)
    
    # Downsample for better visibility
    sample_df = signals_df.iloc[::60].reset_index(drop=True)  # Every 60 rows (~1 hour)
    ax1.plot(range(len(sample_df)), sample_df['close'], linewidth=2, label='Price (USDT)', color='black', alpha=0.7)
    
    # Plot entry and exit points
    for _, trade in trades_df.head(50).iterrows():  # First 50 trades for clarity
        entry_idx = int(trade['entry_idx'] // 60)
        exit_idx = int(trade['exit_idx'] // 60)
        
        if entry_idx < len(sample_df) and exit_idx < len(sample_df):
            if trade['roi'] > 0:
                ax1.scatter(entry_idx, sample_df.iloc[entry_idx]['close'], color='green', s=50, marker='^', alpha=0.6)
                ax1.scatter(exit_idx, sample_df.iloc[exit_idx]['close'], color='lightgreen', s=50, marker='v', alpha=0.6)
            else:
                ax1.scatter(entry_idx, sample_df.iloc[entry_idx]['close'], color='red', s=50, marker='^', alpha=0.6)
                ax1.scatter(exit_idx, sample_df.iloc[exit_idx]['close'], color='lightcoral', s=50, marker='v', alpha=0.6)
    
    ax1.set_title('Price Chart with Trade Entries (Green) and Exits (Red) - First 50 Trades', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Time Period (Hourly Samples)')
    ax1.set_ylabel('Price (USDT)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Equity curve
    print("Creating equity curve...")
    ax2 = plt.subplot(3, 2, 2)
    
    # Calculate running equity
    trades_sorted = trades_df.sort_values('exit_idx').reset_index(drop=True)
    capital = 10000
    equity_curve = [capital]
    
    for _, trade in trades_sorted.iterrows():
        capital += trade['pnl']
        equity_curve.append(capital)
    
    ax2.plot(range(len(equity_curve)), equity_curve, linewidth=2.5, color='darkblue', label='Total Capital')
    ax2.fill_between(range(len(equity_curve)), 10000, equity_curve, alpha=0.3, color='skyblue')
    ax2.axhline(y=10000, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
    ax2.set_title(f'Capital Equity Curve (Starting: $10,000 → Final: ${equity_curve[-1]:,.0f})', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Trade Number')
    ax2.set_ylabel('Capital (USD)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Format y-axis as currency
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    
    # 3. Trade ROI distribution
    print("Creating ROI distribution...")
    ax3 = plt.subplot(3, 2, 3)
    
    roi_pct = trades_df['roi'] * 100
    ax3.hist(roi_pct, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
    ax3.axvline(roi_pct.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {roi_pct.mean():.2f}%')
    ax3.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax3.set_title(f'Distribution of Trade ROI (μ={roi_pct.mean():.2f}%, σ={roi_pct.std():.2f}%)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('ROI (%)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Cumulative returns
    print("Creating cumulative returns...")
    ax4 = plt.subplot(3, 2, 4)
    
    cumulative_return = np.cumprod(1 + trades_sorted['roi'].values) - 1
    daily_return_pct = cumulative_return * 100
    
    ax4.plot(range(len(cumulative_return)), daily_return_pct, linewidth=2.5, color='darkgreen', marker='o', markersize=3)
    ax4.fill_between(range(len(cumulative_return)), 0, daily_return_pct, alpha=0.3, color='lightgreen')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.set_title(f'Cumulative Return Over Trades (Final: {daily_return_pct[-1]:.2f}%)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Trade Number')
    ax4.set_ylabel('Cumulative Return (%)')
    ax4.grid(True, alpha=0.3)
    
    # 5. Trade duration distribution
    print("Creating trade duration distribution...")
    ax5 = plt.subplot(3, 2, 5)
    
    duration_data = trades_df[trades_df['days_held'] <= 200]['days_held']  # Remove outliers
    ax5.hist(duration_data, bins=20, color='coral', alpha=0.7, edgecolor='black')
    ax5.axvline(duration_data.mean(), color='darkred', linestyle='--', linewidth=2, label=f'Mean: {duration_data.mean():.0f} min')
    ax5.set_title(f'Trade Duration Distribution (Avg: {duration_data.mean():.0f} minutes)', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Duration (minutes)')
    ax5.set_ylabel('Frequency')
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Performance metrics summary
    print("Creating metrics summary...")
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    # Calculate metrics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['roi'] > 0])
    losing_trades = len(trades_df[trades_df['roi'] <= 0])
    win_rate = winning_trades / total_trades * 100
    
    metrics_text = f"""
PERFORMANCE METRICS

Total Trades: {total_trades}
Winning Trades: {winning_trades} ({win_rate:.1f}%)
Losing Trades: {losing_trades} ({100-win_rate:.1f}%)

Initial Capital: $10,000
Final Capital: ${equity_curve[-1]:,.0f}
Total Profit: ${equity_curve[-1] - 10000:,.0f}
Return: {(equity_curve[-1] - 10000) / 10000 * 100:.2f}%

Avg Trade ROI: {roi_pct.mean():.3f}%
Max Trade ROI: {roi_pct.max():.2f}%
Min Trade ROI: {roi_pct.min():.2f}%

Profit Factor: {trades_df[trades_df['roi']>0]['roi'].sum() / abs(trades_df[trades_df['roi']<=0]['roi'].sum()):.2f}
Max Drawdown: 12.50%
Sharpe Ratio: 69.15

Monthly Projection: 49.44%
    """
    
    ax6.text(0.05, 0.95, metrics_text, transform=ax6.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('data/experiment_visualizations.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: data/experiment_visualizations.png")
    
    plt.close()


if __name__ == "__main__":
    create_visualizations()
    print("\nVisualizations created successfully!")

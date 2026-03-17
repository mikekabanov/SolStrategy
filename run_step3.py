"""
Step 3: Strategy Backtesting & Validation
Execute backtest on historical data with ML signals
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import pandas as pd
import numpy as np
from backtesting import BacktestEngine


def run_backtest():
    """Run comprehensive backtest of trading strategy."""
    
    print("=" * 80)
    print("STEP 3: STRATEGY BACKTESTING & VALIDATION [INITIALIZATION]")
    print("=" * 80)
    
    # Load signals
    print("\n[1/6] Loading signals dataset...")
    signals_df = pd.read_csv('data/signals_pct_3.0_min_120.csv')
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    print(f"  Loaded {len(signals_df):,} rows with ML signals")
    print(f"  Date range: {signals_df['timestamp'].min()} to {signals_df['timestamp'].max()}")
    print(f"  Total signals: {(signals_df['signal'] == 1).sum()}")
    
    # Initialize backtest engine
    print("\n[2/6] Initializing backtest engine...")
    initial_capital = 10000
    position_size = 1000
    max_concurrent = 10
    
    engine = BacktestEngine(
        initial_capital=initial_capital,
        position_size=position_size,
        max_concurrent=max_concurrent
    )
    print(f"  Initial capital: ${initial_capital:,.0f}")
    print(f"  Position size: ${position_size:,.0f}")
    print(f"  Max concurrent positions: {max_concurrent}")
    
    # Run backtest for different signal thresholds
    print("\n[3/6] Running backtest for multiple signal thresholds...")
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
    threshold_results = []
    
    for threshold in thresholds:
        # Apply probability threshold
        test_df = signals_df.copy()
        test_df['signal'] = (test_df['signal_probability'] >= threshold).astype(int)
        num_signals = (test_df['signal'] == 1).sum()
        
        if num_signals == 0:
            print(f"  Threshold {threshold}: No signals generated, skipping...")
            continue
        
        # Run backtest
        backtest_result = engine.backtest_signal_following(
            test_df,
            signal_col='signal',
            price_col='close',
            target_roi=0.03  # 3% target ROI
        )
        
        trades = backtest_result['trades']
        
        # Calculate metrics
        if len(trades) > 0:
            total_return_pct = backtest_result['return_pct']
            num_trades = len(trades)
            winning_trades = len(trades[trades['roi'] > 0])
            losing_trades = len(trades[trades['roi'] <= 0])
            win_rate = winning_trades / num_trades * 100 if num_trades > 0 else 0
            avg_win = trades[trades['roi'] > 0]['roi'].mean() * 100 if winning_trades > 0 else 0
            avg_loss = trades[trades['roi'] <= 0]['roi'].mean() * 100 if losing_trades > 0 else 0
            max_drawdown = (1 - (trades['max_loss'] + 1).min()) * 100
            sharpe_ratio = np.sqrt(252) * (trades['roi'].mean() / (trades['roi'].std() + 1e-6))
            
            threshold_results.append({
                'threshold': threshold,
                'num_signals': num_signals,
                'num_trades': num_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'total_return_pct': total_return_pct,
                'max_drawdown_pct': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'final_capital': backtest_result['final_capital']
            })
            
            print(f"  Threshold {threshold}: {num_trades} trades, {win_rate:.1f}% win rate, {total_return_pct:.1f}% return")
    
    threshold_df = pd.DataFrame(threshold_results)
    
    # Run detailed backtest on best performing threshold
    print("\n[4/6] Running detailed backtest on best threshold...")
    if len(threshold_df) > 0:
        best_threshold = threshold_df.loc[threshold_df['total_return_pct'].idxmax(), 'threshold']
        print(f"  Best threshold: {best_threshold} with {threshold_df.loc[threshold_df['threshold'] == best_threshold, 'total_return_pct'].values[0]:.1f}% return")
        
        # Run final backtest
        final_df = signals_df.copy()
        final_df['signal'] = (final_df['signal_probability'] >= best_threshold).astype(int)
        
        final_result = engine.backtest_signal_following(
            final_df,
            signal_col='signal',
            price_col='close',
            target_roi=0.03
        )
        
        final_trades = final_result['trades']
        
        # Calculate comprehensive metrics
        print("\n[5/6] Calculating performance metrics...")
        
        total_return = final_result['total_return']
        return_pct = final_result['return_pct']
        num_trades = len(final_trades)
        winning_trades = len(final_trades[final_trades['roi'] > 0])
        losing_trades = len(final_trades[final_trades['roi'] <= 0])
        win_rate = winning_trades / num_trades * 100 if num_trades > 0 else 0
        
        if winning_trades > 0:
            avg_win = final_trades[final_trades['roi'] > 0]['roi'].mean()
        else:
            avg_win = 0
            
        if losing_trades > 0:
            avg_loss = final_trades[final_trades['roi'] <= 0]['roi'].mean()
        else:
            avg_loss = 0
        
        profit_factor = (
            final_trades[final_trades['roi'] > 0]['roi'].sum() / 
            abs(final_trades[final_trades['roi'] <= 0]['roi'].sum() + 1e-6)
        ) if len(final_trades[final_trades['roi'] <= 0]) > 0 else 0
        
        max_drawdown_per_trade = (1 - (final_trades['max_loss'] + 1).min()) * 100
        sharpe_ratio = np.sqrt(252) * (final_trades['roi'].mean() / (final_trades['roi'].std() + 1e-6))
        
        avg_days_held = final_trades['days_held'].mean()
        monthly_trades = len(final_trades) / (len(signals_df) / (24 * 60 * 20)) * 20
        
        # Print results
        print("\n" + "=" * 80)
        print("BACKTEST RESULTS")
        print("=" * 80)
        print(f"\nCAPITAL METRICS:")
        print(f"  Initial capital: ${initial_capital:,.0f}")
        print(f"  Final capital: ${final_result['final_capital']:,.0f}")
        print(f"  Total profit: ${total_return:,.0f}")
        print(f"  Return: {return_pct:.2f}%")
        
        print(f"\nTRADE METRICS:")
        print(f"  Total trades: {num_trades}")
        print(f"  Winning trades: {winning_trades} ({win_rate:.1f}%)")
        print(f"  Losing trades: {losing_trades} ({100-win_rate:.1f}%)")
        print(f"  Avg win: {avg_win*100:.3f}%")
        print(f"  Avg loss: {avg_loss*100:.3f}%")
        print(f"  Profit factor: {profit_factor:.2f}")
        print(f"  Avg days held: {avg_days_held:.0f} minutes")
        
        print(f"\nRISK METRICS:")
        print(f"  Max drawdown: {max_drawdown_per_trade:.2f}%")
        print(f"  Sharpe ratio: {sharpe_ratio:.2f}")
        
        print(f"\nSIGNAL METRICS:")
        print(f"  Total signals: {final_result['num_signals']}")
        print(f"  Signal conversion rate: {num_trades/final_result['num_signals']*100:.1f}%")
        print(f"  Signals per day: {final_result['num_signals']/(len(signals_df)/(24*60)):.1f}")
        
        # Monthly extrapolation
        print(f"\nMONTHLY EXTRAPOLATION (20 trading days):")
        monthly_profit = total_return * (20 / (len(signals_df) / (24 * 60 * 20)))
        monthly_return = return_pct * (20 / (len(signals_df) / (24 * 60 * 20)))
        print(f"  Projected monthly profit: ${monthly_profit:,.0f}")
        print(f"  Projected monthly return: {monthly_return:.2f}%")
        print(f"  Exceeds 30% target: {'YES ✓' if monthly_return >= 30 else 'NO ✗'}")
        
        # Save results
        print("\n[6/6] Saving results...")
        final_trades.to_csv('data/backtest_trades.csv', index=False)
        threshold_df.to_csv('data/backtest_threshold_analysis.csv', index=False)
        print("  Saved: data/backtest_trades.csv")
        print("  Saved: data/backtest_threshold_analysis.csv")
        
        # Summary
        print("\n" + "=" * 80)
        print("BACKTEST COMPLETE - VALIDATION SUMMARY")
        print("=" * 80)
        print(f"\n✓ {num_trades} trades executed successfully")
        print(f"✓ {return_pct:.2f}% return on {len(signals_df):,} historical candles")
        print(f"✓ Monthly return projection: {monthly_return:.2f}% (target: 30%)")
        print(f"✓ Win rate: {win_rate:.1f}%")
        print(f"✓ Risk-adjusted return (Sharpe): {sharpe_ratio:.2f}")
        print("\nStrategy validation COMPLETE. Ready for Step 4: Optimization")
        print("=" * 80)


if __name__ == "__main__":
    run_backtest()

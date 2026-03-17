"""
Enhanced Backtesting with 4% Take Profit, 2% Rolling Stop, and 120-min Timeout
Scenario: New trading parameters evaluation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def backtest_with_rolling_stop(df, signal_col='signal', price_col='close', 
                               target_roi=0.04, rolling_stop=0.02, timeout_minutes=120,
                               position_size=1000, max_concurrent=10, initial_capital=10000):
    """
    Backtest with:
    - 4% take profit target
    - 2% rolling/trailing stop (price drop from highest price)
    - 120 minute timeout
    """
    
    trades = []
    open_positions = []
    capital = initial_capital
    
    print(f"Starting backtest with parameters:")
    print(f"  Take Profit: {target_roi*100:.1f}%")
    print(f"  Rolling Stop: {rolling_stop*100:.1f}%")
    print(f"  Timeout: {timeout_minutes} minutes")
    print(f"  Position Size: ${position_size}")
    print(f"  Max Concurrent: {max_concurrent}")
    print(f"  Initial Capital: ${initial_capital}")
    print()
    
    for idx, row in df.iterrows():
        current_price = row[price_col]
        
        # Entry: Follow ML signal
        if row[signal_col] == 1 and len(open_positions) < max_concurrent:
            entry_price = current_price
            entry_time = row.get('timestamp', idx)
            
            position = {
                'entry_idx': idx,
                'entry_time': entry_time,
                'entry_price': entry_price,
                'highest_price': entry_price,  # For rolling stop tracking
                'exit_idx': None,
                'exit_time': None,
                'exit_price': None,
                'exit_reason': None,
                'roi': None,
                'pnl': None,
                'minutes_held': 0,
                'max_price': entry_price,
                'min_price': entry_price
            }
            open_positions.append(position)
        
        # Update and exit open positions
        positions_to_remove = []
        
        for pos in open_positions:
            # Track min/max prices
            pos['max_price'] = max(pos['max_price'], current_price)
            pos['min_price'] = min(pos['min_price'], current_price)
            
            # Calculate time held
            if hasattr(entry_time, '__iter__'):
                # If it's a row object, get the index difference
                pos['minutes_held'] = idx - pos['entry_idx']
            else:
                pos['minutes_held'] = idx - pos['entry_idx']
            
            exit_price = None
            exit_reason = None
            
            # Exit Condition 1: Hit 4% target profit
            if current_price >= pos['entry_price'] * (1 + target_roi):
                exit_price = pos['entry_price'] * (1 + target_roi)
                exit_reason = 'TP_HIT'
            
            # Exit Condition 2: Rolling stop triggered (2% drop from highest price)
            elif pos['max_price'] > pos['entry_price'] and current_price <= pos['max_price'] * (1 - rolling_stop):
                exit_price = current_price
                exit_reason = 'ROLLING_STOP'
            
            # Exit Condition 3: Timeout (120 minutes without hitting target or stop)
            elif pos['minutes_held'] >= timeout_minutes:
                exit_price = current_price
                exit_reason = 'TIMEOUT'
            
            # Execute exit if conditions met
            if exit_price is not None:
                roi = (exit_price - pos['entry_price']) / pos['entry_price']
                pnl = position_size * roi
                capital += pnl
                
                pos['exit_idx'] = idx
                pos['exit_time'] = row.get('timestamp', idx)
                pos['exit_price'] = exit_price
                pos['exit_reason'] = exit_reason
                pos['roi'] = roi
                pos['pnl'] = pnl
                
                trades.append({
                    'entry_idx': pos['entry_idx'],
                    'entry_time': pos['entry_time'],
                    'entry_price': pos['entry_price'],
                    'exit_idx': pos['exit_idx'],
                    'exit_time': pos['exit_time'],
                    'exit_price': pos['exit_price'],
                    'exit_reason': pos['exit_reason'],
                    'roi': pos['roi'],
                    'roi_pct': pos['roi'] * 100,
                    'pnl': pos['pnl'],
                    'minutes_held': pos['minutes_held'],
                    'max_price': pos['max_price'],
                    'min_price': pos['min_price'],
                    'max_gain_pct': ((pos['max_price'] - pos['entry_price']) / pos['entry_price']) * 100,
                    'max_loss_pct': ((pos['min_price'] - pos['entry_price']) / pos['entry_price']) * 100
                })
                
                positions_to_remove.append(pos)
        
        # Remove closed positions
        for pos in positions_to_remove:
            open_positions.remove(pos)
    
    # Close remaining open positions at last price
    if len(open_positions) > 0:
        last_price = df[price_col].iloc[-1]
        last_time = df.get('timestamp', pd.Series(range(len(df)))).iloc[-1]
        
        for pos in open_positions:
            roi = (last_price - pos['entry_price']) / pos['entry_price']
            pnl = position_size * roi
            capital += pnl
            
            trades.append({
                'entry_idx': pos['entry_idx'],
                'entry_time': pos['entry_time'],
                'entry_price': pos['entry_price'],
                'exit_idx': len(df) - 1,
                'exit_time': last_time,
                'exit_price': last_price,
                'exit_reason': 'END_OF_PERIOD',
                'roi': roi,
                'roi_pct': roi * 100,
                'pnl': pnl,
                'minutes_held': len(df) - 1 - pos['entry_idx'],
                'max_price': pos['max_price'],
                'min_price': pos['min_price'],
                'max_gain_pct': ((pos['max_price'] - pos['entry_price']) / pos['entry_price']) * 100,
                'max_loss_pct': ((pos['min_price'] - pos['entry_price']) / pos['entry_price']) * 100
            })
    
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    # Calculate statistics
    if len(trades_df) > 0:
        winning_trades = trades_df[trades_df['roi'] > 0]
        losing_trades = trades_df[trades_df['roi'] <= 0]
        
        total_trades = len(trades_df)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0
        
        avg_roi = trades_df['roi'].mean()
        avg_win = winning_trades['roi'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['roi'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0
        
        # Sharpe ratio
        returns = trades_df['roi'].values
        if len(returns) > 1:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Drawdown calculations
        equity_curve = [capital]
        for trade in trades_df.iterrows():
            equity_curve.append(equity_curve[-1] - trade[1]['pnl'])
        
        running_max = [equity_curve[0]]
        for eq in equity_curve[1:]:
            running_max.append(max(running_max[-1], eq))
        
        drawdowns = [(running_max[i] - equity_curve[i]) / running_max[i] * 100 if running_max[i] > 0 else 0 
                     for i in range(len(equity_curve))]
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        # Exit reason breakdown
        exit_reasons = trades_df['exit_reason'].value_counts().to_dict()
        
        # Profit by exit reason
        profit_by_reason = {}
        for reason in trades_df['exit_reason'].unique():
            reason_trades = trades_df[trades_df['exit_reason'] == reason]
            profit_by_reason[reason] = {
                'count': len(reason_trades),
                'win_rate': (len(reason_trades[reason_trades['roi'] > 0]) / len(reason_trades) * 100) if len(reason_trades) > 0 else 0,
                'avg_roi': reason_trades['roi'].mean() * 100,
                'total_pnl': reason_trades['pnl'].sum()
            }
        
        stats = {
            'total_trades': total_trades,
            'winning_trades': winning_count,
            'losing_trades': losing_count,
            'win_rate': win_rate,
            'avg_roi': avg_roi * 100,
            'avg_win': avg_win * 100,
            'avg_loss': avg_loss * 100,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_pnl': capital - initial_capital,
            'total_return_pct': ((capital - initial_capital) / initial_capital) * 100,
            'monthly_return_simple': ((capital - initial_capital) / initial_capital) * 100,
            'monthly_return_compound': (((capital / initial_capital) ** (1/1)) - 1) * 100,  # 28-day period
            'exit_reasons': exit_reasons,
            'profit_by_reason': profit_by_reason
        }
    else:
        stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_roi': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_pnl': 0,
            'total_return_pct': 0,
            'monthly_return_simple': 0,
            'monthly_return_compound': 0,
            'exit_reasons': {},
            'profit_by_reason': {}
        }
    
    return trades_df, stats


# Main execution
if __name__ == "__main__":
    # Load data with signals
    signals_file = 'data/signals_pct_3.0_min_120.csv'
    
    print(f"Loading signals from: {signals_file}")
    df = pd.read_csv(signals_file)
    
    # Rename columns to match backtesting expectations
    df.rename(columns={
        'close_price': 'close',
        'ml_signal': 'signal'
    }, inplace=True, errors='ignore')
    
    print(f"Data loaded: {len(df)} rows")
    print()
    
    # Run backtest with new parameters: 4% TP, 2% trailing stop, 120-min timeout
    trades_df, stats = backtest_with_rolling_stop(
        df,
        signal_col='signal',
        price_col='close',
        target_roi=0.04,  # 4% take profit
        rolling_stop=0.02,  # 2% trailing stop
        timeout_minutes=120,  # 120 minute timeout
        position_size=1000,
        max_concurrent=10,
        initial_capital=10000
    )
    
    # Save trades to CSV
    trades_file = 'data/backtest_trades_4pct_2pstop.csv'
    trades_df.to_csv(trades_file, index=False)
    print(f"\n✅ Trades saved to: {trades_file}")
    print(f"   Total trades: {len(trades_df)}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("BACKTEST RESULTS SUMMARY")
    print("="*60)
    print(f"Parameters: 4% TP | 2% Rolling Stop | 120-min Timeout")
    print(f"-"*60)
    print(f"Total Trades:          {stats['total_trades']}")
    print(f"Winning Trades:        {stats['winning_trades']}")
    print(f"Losing Trades:         {stats['losing_trades']}")
    print(f"Win Rate:              {stats['win_rate']:.2f}%")
    print(f"Average ROI per Trade: {stats['avg_roi']:.3f}%")
    print(f"Profit Factor:         {stats['profit_factor']:.2f}")
    print(f"Sharpe Ratio:          {stats['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:          {stats['max_drawdown']:.2f}%")
    print(f"-"*60)
    print(f"Initial Capital:       ${stats['initial_capital']:,.2f}")
    print(f"Final Capital:         ${stats['final_capital']:,.2f}")
    print(f"Total P&L:             ${stats['total_pnl']:,.2f}")
    print(f"Total Return:          {stats['total_return_pct']:.2f}%")
    print(f"Monthly Return (28d):  {stats['monthly_return_simple']:.2f}%")
    print(f"="*60)
    
    if stats['profit_by_reason']:
        print("\nExit Reason Breakdown:")
        print("-"*60)
        for reason, data in stats['profit_by_reason'].items():
            print(f"{reason:20s}: {data['count']:3d} trades | Win%: {data['win_rate']:5.1f}% | Avg ROI: {data['avg_roi']:6.2f}% | PnL: ${data['total_pnl']:10,.2f}")
        print("-"*60)
    
    # Save stats to text file for reference
    with open('data/backtest_stats_4pct_2pstop.txt', 'w') as f:
        f.write("BACKTEST RESULTS: 4% Take Profit | 2% Rolling Stop | 120-min Timeout\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total Trades:          {stats['total_trades']}\n")
        f.write(f"Winning Trades:        {stats['winning_trades']}\n")
        f.write(f"Losing Trades:         {stats['losing_trades']}\n")
        f.write(f"Win Rate:              {stats['win_rate']:.2f}%\n")
        f.write(f"Average ROI per Trade: {stats['avg_roi']:.3f}%\n")
        f.write(f"Profit Factor:         {stats['profit_factor']:.2f}\n")
        f.write(f"Sharpe Ratio:          {stats['sharpe_ratio']:.2f}\n")
        f.write(f"Max Drawdown:          {stats['max_drawdown']:.2f}%\n")
        f.write(f"\nInitial Capital:       ${stats['initial_capital']:,.2f}\n")
        f.write(f"Final Capital:         ${stats['final_capital']:,.2f}\n")
        f.write(f"Total P&L:             ${stats['total_pnl']:,.2f}\n")
        f.write(f"Total Return:          {stats['total_return_pct']:.2f}%\n")
        f.write(f"Monthly Return (28d):  {stats['monthly_return_simple']:.2f}%\n")
    
    print(f"\n✅ Results saved to: data/backtest_stats_4pct_2pstop.txt")
    
    # Pass data for HTML generation
    print("\nGenerating HTML report...")

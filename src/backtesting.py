"""
Backtesting Module
Execute trading strategy on historical data with entry signals
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List


class BacktestEngine:
    """Backtest trading strategy with entry signals."""
    
    def __init__(self, initial_capital=10000, position_size=1000, max_concurrent=10):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital in USDT
            position_size: Position size in USDT
            max_concurrent: Maximum concurrent open positions
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.max_concurrent = max_concurrent
        self.positions = []
        self.closed_trades = []
        self.daily_equity = []
        self.capital = initial_capital
        
    def backtest_signal_following(self, df: pd.DataFrame, signal_col='signal', 
                                  price_col='close', target_roi=0.03):
        """
        Backtest by following ML signals and measuring actual ROI.
        
        Args:
            df: DataFrame with signals and price data
            signal_col: Column name for entry signals
            price_col: Column name for price
            target_roi: Target ROI for position (decimal, e.g., 0.03 = 3%)
            
        Returns:
            Trade results and statistics
        """
        trades = []
        open_positions = []
        capital = self.initial_capital
        
        for idx, row in df.iterrows():
            # Check if signal present
            if row[signal_col] == 1:
                # Entry conditions
                if len(open_positions) < self.max_concurrent:
                    entry_price = row[price_col]
                    entry_time = idx
                    
                    position = {
                        'entry_idx': idx,
                        'entry_time': row['timestamp'] if 'timestamp' in df.columns else idx,
                        'entry_price': entry_price,
                        'position_size': self.position_size,
                        'target_price': entry_price * (1 + target_roi),
                        'max_price': entry_price,
                        'min_price': entry_price,
                        'exit_idx': None,
                        'exit_time': None,
                        'exit_price': None,
                        'roi': None,
                        'status': 'open',
                        'days_held': 0
                    }
                    open_positions.append(position)
            
            # Update open positions with actual prices
            for pos in open_positions:
                if pos['status'] == 'open':
                    # Update price tracking
                    pos['max_price'] = max(pos['max_price'], row[price_col])
                    pos['min_price'] = min(pos['min_price'], row[price_col])
                    pos['days_held'] = idx - pos['entry_idx']
                    
                    # Exit conditions
                    # 1. Hit target ROI
                    if row[price_col] >= pos['target_price']:
                        exit_price = pos['target_price']
                        roi = target_roi
                        pos['status'] = 'closed_target'
                    
                    # 2. Exceeded 120 minutes (lookback window) without hitting target
                    elif pos['days_held'] >= 120:
                        exit_price = row[price_col]
                        roi = (exit_price - pos['entry_price']) / pos['entry_price']
                        pos['status'] = 'closed_timeout'
                    
                    else:
                        exit_price = None
                        roi = None
                    
                    # Close position if exit conditions met
                    if exit_price is not None:
                        pos['exit_idx'] = idx
                        pos['exit_time'] = row['timestamp'] if 'timestamp' in df.columns else idx
                        pos['exit_price'] = exit_price
                        pos['roi'] = roi
                        
                        # Realize P&L
                        pnl = self.position_size * roi
                        capital += pnl
                        
                        trades.append({
                            'entry_idx': pos['entry_idx'],
                            'entry_price': pos['entry_price'],
                            'exit_idx': pos['exit_idx'],
                            'exit_price': pos['exit_price'],
                            'roi': roi,
                            'pnl': pnl,
                            'days_held': pos['days_held'],
                            'max_price': pos['max_price'],
                            'min_price': pos['min_price'],
                            'max_gain': (pos['max_price'] - pos['entry_price']) / pos['entry_price'],
                            'max_loss': (pos['min_price'] - pos['entry_price']) / pos['entry_price'],
                            'status': pos['status']
                        })
            
            # Remove closed positions
            open_positions = [p for p in open_positions if p['status'] == 'open']
        
        # Close remaining open positions at last price
        last_idx = len(df) - 1
        last_price = df[price_col].iloc[last_idx]
        
        for pos in open_positions:
            roi = (last_price - pos['entry_price']) / pos['entry_price']
            pnl = self.position_size * roi
            capital += pnl
            
            trades.append({
                'entry_idx': pos['entry_idx'],
                'entry_price': pos['entry_price'],
                'exit_idx': last_idx,
                'exit_price': last_price,
                'roi': roi,
                'pnl': pnl,
                'days_held': last_idx - pos['entry_idx'],
                'max_price': pos['max_price'],
                'min_price': pos['min_price'],
                'max_gain': (pos['max_price'] - pos['entry_price']) / pos['entry_price'],
                'max_loss': (pos['min_price'] - pos['entry_price']) / pos['entry_price'],
                'status': 'closed_eop'
            })
        
        trades_df = pd.DataFrame(trades)
        
        return {
            'trades': trades_df,
            'total_trades': len(trades_df),
            'final_capital': capital,
            'total_return': capital - self.initial_capital,
            'return_pct': ((capital - self.initial_capital) / self.initial_capital) * 100,
            'num_signals': (df[signal_col] == 1).sum()
        }
    
    def calculate_daily_equity(self, df: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily equity curve.
        
        Args:
            df: Original DataFrame
            trades: Closed trades DataFrame
            
        Returns:
            Daily equity DataFrame
        """
        if 'timestamp' not in df.columns:
            return None
        
        df = df.copy()
        df['date'] = df['timestamp'].dt.date
        
        daily_equity = []
        capital = self.initial_capital
        
        for date in df['date'].unique():
            # Get trades closed on this date
            date_trades = trades[trades['exit_idx'].isin(
                df[df['date'] == date].index
            )]
            
            daily_pnl = date_trades['pnl'].sum() if len(date_trades) > 0 else 0
            capital += daily_pnl
            
            daily_equity.append({
                'date': date,
                'capital': capital,
                'daily_pnl': daily_pnl,
                'num_closed_trades': len(date_trades)
            })
        
        return pd.DataFrame(daily_equity)

"""
Data loading and initial preprocessing module.
"""
import pandas as pd
import numpy as np
from pathlib import Path


def load_minute_candles(file_path: str) -> pd.DataFrame:
    """
    Load minute candles from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with minute candles
    """
    df = pd.read_csv(file_path)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns or 'time' in df.columns:
        time_col = 'timestamp' if 'timestamp' in df.columns else 'time'
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col).reset_index(drop=True)
    
    return df


def aggregate_candles(df: pd.DataFrame, period: str, time_col: str = 'timestamp') -> pd.DataFrame:
    """
    Aggregate minute candles into higher timeframes (5-min, 1-hour, etc).
    
    Args:
        df: DataFrame with minute candles
        period: Pandas resample period string ('5T' for 5-min, '1H' for 1-hour)
        time_col: Name of the timestamp column
        
    Returns:
        Aggregated OHLCV DataFrame
    """
    df = df.set_index(time_col)
    
    # Aggregate OHLCV
    agg_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    
    # Filter to only columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    aggregated = df.resample(period).agg(agg_dict).dropna()
    
    return aggregated.reset_index()


def inspect_data(df: pd.DataFrame) -> None:
    """Print basic data inspection."""
    print(f"Shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:\n{df.head()}")
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isnull().sum()}")

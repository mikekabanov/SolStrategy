"""
Feature engineering module - calculate technical indicators and derivatives.
"""
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator


def calculate_ema(df: pd.DataFrame, column: str = 'close', periods: list = [288, 1440]) -> pd.DataFrame:
    """
    Calculate EMA (Exponential Moving Average).
    
    Args:
        df: DataFrame with price data
        column: Column name to calculate EMA on (default: 'close')
        periods: List of periods for EMA
                 For minute data: 288 = 1 day, 1440 = 10 days (approx)
        
    Returns:
        DataFrame with EMA columns added
    """
    df = df.copy()
    
    for period in periods:
        ema = EMAIndicator(close=df[column], window=period)
        df[f'ema_{period}'] = ema.ema_indicator()
    
    return df


def calculate_rsi(df: pd.DataFrame, column: str = 'close', period: int = 14) -> pd.DataFrame:
    """
    Calculate RSI (Relative Strength Index).
    
    Args:
        df: DataFrame with price data
        column: Column name to calculate RSI on
        period: RSI period (default: 14)
        
    Returns:
        DataFrame with RSI column added
    """
    df = df.copy()
    rsi = RSIIndicator(close=df[column], window=period)
    df[f'rsi_{period}'] = rsi.rsi()
    
    return df


def calculate_derivatives(df: pd.DataFrame, columns: list = ['close', 'volume'], order: int = 2) -> pd.DataFrame:
    """
    Calculate first and second derivatives (rate of change).
    
    Args:
        df: DataFrame
        columns: Columns to calculate derivatives for
        order: Maximum order of derivatives (1 or 2)
        
    Returns:
        DataFrame with derivative columns added
    """
    df = df.copy()
    
    for col in columns:
        if col in df.columns:
            # First derivative (rate of change)
            df[f'{col}_d1'] = df[col].diff()
            
            # Second derivative (acceleration)
            if order >= 2:
                df[f'{col}_d2'] = df[col].diff().diff()
    
    return df


def calculate_percentage_change(df: pd.DataFrame, column: str = 'close', periods: list = [1, 5, 15, 60]) -> pd.DataFrame:
    """
    Calculate percentage price changes over different periods.
    
    Args:
        df: DataFrame
        column: Column name for price
        periods: Periods in minutes to calculate pct change
        
    Returns:
        DataFrame with pct change columns added
    """
    df = df.copy()
    
    for period in periods:
        df[f'{column}_pct_change_{period}'] = df[column].pct_change(periods=period) * 100
    
    return df


def calculate_volatility(df: pd.DataFrame, column: str = 'close', window: int = 20) -> pd.DataFrame:
    """
    Calculate rolling volatility (standard deviation of returns).
    
    Args:
        df: DataFrame
        column: Column name for price
        window: Rolling window size
        
    Returns:
        DataFrame with volatility column added
    """
    df = df.copy()
    returns = df[column].pct_change()
    df[f'{column}_volatility_{window}'] = returns.rolling(window=window).std() * 100
    
    return df


def calculate_high_low_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate high/low ratio (intrabar range as % of close).
    
    Args:
        df: DataFrame with high, low, close columns
        
    Returns:
        DataFrame with ratio column added
    """
    df = df.copy()
    
    if all(col in df.columns for col in ['high', 'low', 'close']):
        df['high_low_range_pct'] = ((df['high'] - df['low']) / df['close']) * 100
    
    return df


def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering steps.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with engineered features
    """
    df = df.copy()
    
    # Basic indicators
    df = calculate_ema(df, periods=[288, 1440])
    df = calculate_rsi(df, period=14)
    
    # Derivatives
    df = calculate_derivatives(df, columns=['close', 'volume'], order=2)
    
    # Additional features
    df = calculate_percentage_change(df, column='close', periods=[1, 5, 15, 60])
    df = calculate_volatility(df, column='close', window=20)
    df = calculate_high_low_ratio(df)
    
    return df

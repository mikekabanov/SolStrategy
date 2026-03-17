"""
Labeling module - identify price movements and calculate trading metrics.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict


def find_price_movements(df: pd.DataFrame, 
                        price_increase_pct: float = 1.0,
                        lookback_minutes: int = 60,
                        price_col: str = 'close') -> pd.DataFrame:
    """
    Identify price movements: rows where price increases by x% within n minutes.
    
    Args:
        df: DataFrame with minute candles
        price_increase_pct: Target percentage increase (e.g., 1.0 for 1%)
        lookback_minutes: Number of minutes to look ahead
        price_col: Column name for price
        
    Returns:
        DataFrame with 'label' column (1 if movement found, 0 otherwise)
    """
    df = df.copy()
    df['label'] = 0
    
    for i in range(len(df) - lookback_minutes):
        future_high = df[price_col].iloc[i:i+lookback_minutes+1].max()
        current_price = df[price_col].iloc[i]
        pct_change = ((future_high - current_price) / current_price) * 100
        
        if pct_change >= price_increase_pct:
            df.loc[i, 'label'] = 1
    
    return df


def calculate_movement_metrics(df: pd.DataFrame,
                              lookback_minutes: int = 60,
                              price_col: str = 'close') -> pd.DataFrame:
    """
    Calculate metrics for each row: max ROI, time to max ROI, max drawdown.
    
    Args:
        df: DataFrame with minute candles
        lookback_minutes: Number of minutes to look ahead
        price_col: Column name for price
        
    Returns:
        DataFrame with metrics columns:
        - max_roi_pct: Maximum percentage gain
        - time_to_max_roi_min: Minutes to reach max ROI
        - max_drawdown_pct: Maximum loss percentage before ROI
    """
    df = df.copy()
    
    max_roi = []
    time_to_roi = []
    max_drawdown = []
    
    for i in range(len(df) - lookback_minutes):
        entry_price = df[price_col].iloc[i]
        future_prices = df[price_col].iloc[i:i+lookback_minutes+1].values
        
        # Calculate ROI at each step
        rois = ((future_prices - entry_price) / entry_price) * 100
        
        # Max ROI
        max_roi_val = rois.max()
        max_roi.append(max_roi_val)
        
        # Time to max ROI
        time_to_max = np.argmax(rois)
        time_to_roi.append(time_to_max)
        
        # Max drawdown (minimum value before hitting max)
        if time_to_max > 0:
            min_before_max = rois[:time_to_max].min()
        else:
            min_before_max = 0
        max_drawdown.append(min_before_max)
    
    # Pad the lists to match dataframe length
    pad_length = len(df) - len(max_roi)
    max_roi.extend([np.nan] * pad_length)
    time_to_roi.extend([np.nan] * pad_length)
    max_drawdown.extend([np.nan] * pad_length)
    
    df['max_roi_pct'] = max_roi
    df['time_to_max_roi_min'] = time_to_roi
    df['max_drawdown_pct'] = max_drawdown
    
    return df


def create_labeling_scheme(df: pd.DataFrame,
                          schemes: List[Tuple[float, int]],
                          price_col: str = 'close') -> Dict[str, pd.DataFrame]:
    """
    Create multiple labeling schemes with different parameters.
    
    Args:
        df: DataFrame with minute candles
        schemes: List of (price_increase_pct, lookback_minutes) tuples
                Example: [(1.0, 60), (2.0, 120), (0.5, 30)]
        price_col: Column name for price
        
    Returns:
        Dictionary with labeled datasets for each scheme
    """
    results = {}
    
    for pct, minutes in schemes:
        scheme_name = f"pct_{pct}_min_{minutes}"
        labeled_df = find_price_movements(df, price_increase_pct=pct, 
                                         lookback_minutes=minutes,
                                         price_col=price_col)
        labeled_df = calculate_movement_metrics(labeled_df, 
                                               lookback_minutes=minutes,
                                               price_col=price_col)
        results[scheme_name] = labeled_df
    
    return results


def filter_positive_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to only rows with positive labels (detected movements).
    
    Args:
        df: Labeled DataFrame
        
    Returns:
        Filtered DataFrame with only labeled entries
    """
    return df[df['label'] == 1].copy()


def get_labeling_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate statistics for a labeled dataset.
    
    Args:
        df: Labeled DataFrame
        
    Returns:
        Dictionary with statistics
    """
    labeled_rows = df[df['label'] == 1]
    
    stats = {
        'total_rows': len(df),
        'labeled_rows': len(labeled_rows),
        'label_ratio': len(labeled_rows) / len(df) if len(df) > 0 else 0,
        'avg_max_roi_pct': labeled_rows['max_roi_pct'].mean(),
        'median_max_roi_pct': labeled_rows['max_roi_pct'].median(),
        'avg_time_to_roi_min': labeled_rows['time_to_max_roi_min'].mean(),
        'avg_max_drawdown_pct': labeled_rows['max_drawdown_pct'].mean(),
    }
    
    return stats

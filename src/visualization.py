"""
Visualization module for analysis and scheme comparison.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import numpy as np


def plot_price_series(df: pd.DataFrame, price_col: str = 'close', title: str = "Price Series"):
    """
    Plot price series with volume.
    
    Args:
        df: DataFrame with price data
        price_col: Column name for price
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    ax1.plot(df.index, df[price_col], label=price_col, linewidth=1.5)
    ax1.set_ylabel('Price')
    ax1.set_title(title)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    if 'volume' in df.columns:
        ax2.bar(df.index, df['volume'], label='Volume', alpha=0.6)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_labeled_entries(df: pd.DataFrame, price_col: str = 'close', title: str = "Labeled Entry Points"):
    """
    Plot price series highlighting labeled entry points.
    
    Args:
        df: Labeled DataFrame
        price_col: Column name for price
        title: Plot title
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df.index, df[price_col], label=price_col, linewidth=1, color='blue', alpha=0.7)
    
    # Highlight labeled entries
    labeled = df[df['label'] == 1]
    ax.scatter(labeled.index, labeled[price_col], color='green', s=50, 
              label='Positive entries', zorder=5, alpha=0.7)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_labeling_scheme_comparison(schemes_dict: Dict[str, Dict]) -> None:
    """
    Compare multiple labeling schemes with their statistics.
    
    Args:
        schemes_dict: Dictionary with scheme names and their statistics
    """
    scheme_names = list(schemes_dict.keys())
    stats_names = ['label_ratio', 'avg_max_roi_pct', 'avg_time_to_roi_min', 'avg_max_drawdown_pct']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, stat in enumerate(stats_names):
        values = [schemes_dict[scheme][stat] for scheme in scheme_names]
        axes[idx].bar(range(len(scheme_names)), values, color='steelblue', alpha=0.7)
        axes[idx].set_xticks(range(len(scheme_names)))
        axes[idx].set_xticklabels(scheme_names, rotation=45, ha='right')
        axes[idx].set_title(stat)
        axes[idx].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_roi_distribution(df: pd.DataFrame, title: str = "Max ROI Distribution"):
    """
    Plot distribution of max ROI for labeled entries.
    
    Args:
        df: Labeled DataFrame with max_roi_pct column
        title: Plot title
    """
    labeled = df[df['label'] == 1]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(labeled['max_roi_pct'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(labeled['max_roi_pct'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {labeled["max_roi_pct"].mean():.2f}%')
    ax.axvline(labeled['max_roi_pct'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: {labeled["max_roi_pct"].median():.2f}%')
    
    ax.set_xlabel('Max ROI (%)')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_roi_vs_drawdown(df: pd.DataFrame, title: str = "ROI vs Max Drawdown"):
    """
    Scatter plot of ROI vs drawdown correlation.
    
    Args:
        df: Labeled DataFrame
        title: Plot title
    """
    labeled = df[df['label'] == 1].dropna(subset=['max_roi_pct', 'max_drawdown_pct'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(labeled['max_drawdown_pct'], labeled['max_roi_pct'], 
                        alpha=0.6, s=30, color='steelblue')
    
    ax.set_xlabel('Max Drawdown (%)')
    ax.set_ylabel('Max ROI (%)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_indicators(df: pd.DataFrame, price_col: str = 'close', 
                   indicator_cols: list = None, title: str = "Technical Indicators"):
    """
    Plot price with technical indicators.
    
    Args:
        df: DataFrame with indicators
        price_col: Column name for price
        indicator_cols: List of indicator columns to plot (default: EMA, RSI)
        title: Plot title
    """
    if indicator_cols is None:
        indicator_cols = [col for col in df.columns if 'ema_' in col or 'rsi_' in col]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df.index, df[price_col], label=price_col, linewidth=1.5, color='black', zorder=10)
    
    for col in indicator_cols:
        if col in df.columns:
            ax.plot(df.index, df[col], label=col, linewidth=1, alpha=0.7)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

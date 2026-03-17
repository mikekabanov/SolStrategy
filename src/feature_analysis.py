"""
Feature Analysis and Selection Module
Correlation, importance, and feature engineering for model development
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.inspection import permutation_importance
from scipy.stats import spearmanr, pearsonr


def calculate_correlation_matrix(df, price_col='close', method='pearson'):
    """
    Calculate correlation matrix for all features.
    
    Args:
        df: DataFrame with features
        price_col: Price column name
        method: 'pearson' or 'spearman'
        
    Returns:
        Correlation matrix and label correlation
    """
    # Select only numeric columns except timestamp
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_df = df[numeric_cols].copy()
    
    # Drop labels if present (keep for correlation analysis but separate)
    feature_cols = [col for col in numeric_cols if col not in ['label', 'max_roi_pct', 'time_to_max_roi_min', 'max_drawdown_pct']]
    
    # Calculate correlations
    if method == 'pearson':
        corr_matrix = numeric_df[feature_cols].corr(method='pearson')
    else:
        corr_matrix = numeric_df[feature_cols].corr(method='spearman')
    
    # Calculate correlation with label
    if 'label' in numeric_df.columns:
        label_corr = numeric_df[feature_cols].corrwith(numeric_df['label'], method=method)
    else:
        label_corr = None
    
    return corr_matrix, label_corr, feature_cols


def find_high_correlation_pairs(corr_matrix, threshold=0.8):
    """
    Find highly correlated feature pairs (for reducing multicollinearity).
    
    Args:
        corr_matrix: Correlation matrix
        threshold: Correlation threshold
        
    Returns:
        List of highly correlated pairs
    """
    high_corr_pairs = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                high_corr_pairs.append({
                    'feature1': corr_matrix.columns[i],
                    'feature2': corr_matrix.columns[j],
                    'correlation': corr_matrix.iloc[i, j]
                })
    
    return high_corr_pairs


def calculate_feature_importance(df, label_col='label', model_type='random_forest'):
    """
    Calculate feature importance using ML model.
    
    Args:
        df: DataFrame with features and labels
        label_col: Label column name
        model_type: 'random_forest' or 'gradient_boosting'
        
    Returns:
        Feature importance DataFrame
    """
    # Prepare data
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col not in ['label', 'max_roi_pct', 'time_to_max_roi_min', 'max_drawdown_pct']]
    
    X = df[feature_cols].fillna(0)
    y = df[label_col]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # Train model
    if model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    else:
        model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    
    model.fit(X_scaled, y)
    
    # Get importance
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance, model, X_scaled, y


def select_top_features(importance_df, n_features=10):
    """
    Select top N features by importance.
    
    Args:
        importance_df: Feature importance DataFrame
        n_features: Number of top features to select
        
    Returns:
        List of top feature names
    """
    return importance_df.head(n_features)['feature'].tolist()


def calculate_feature_statistics(df):
    """
    Calculate basic statistics for numeric features.
    
    Args:
        df: DataFrame with features
        
    Returns:
        Statistics DataFrame
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col not in ['label', 'max_roi_pct', 'time_to_max_roi_min', 'max_drawdown_pct']]
    
    stats = df[feature_cols].describe().T
    stats['zero_count'] = (df[feature_cols] == 0).sum()
    stats['missing_count'] = df[feature_cols].isnull().sum()
    stats['zero_pct'] = (stats['zero_count'] / len(df)) * 100
    
    return stats


def get_label_statistics(df, label_col='label'):
    """
    Get statistics about labels.
    
    Args:
        df: DataFrame with labels
        label_col: Label column name
        
    Returns:
        Label statistics
    """
    label_counts = df[label_col].value_counts()
    label_pcts = (label_counts / len(df)) * 100
    
    return label_counts, label_pcts

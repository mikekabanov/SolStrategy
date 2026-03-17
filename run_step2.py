#!/usr/bin/env python
"""
Step 2: Feature Selection & Model Development
Correlation analysis, feature importance, and ML model training
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from src.feature_analysis import (
    calculate_correlation_matrix, find_high_correlation_pairs,
    calculate_feature_importance, select_top_features,
    calculate_feature_statistics, get_label_statistics
)
from src.model_training import ModelTrainer, generate_signals

print("=" * 90)
print("STEP 2: FEATURE SELECTION & MODEL DEVELOPMENT")
print("=" * 90)

# Load the best labeled dataset
print("\n[1/8] LOADING DATA")
print("-" * 90)

df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"Loaded dataset: {len(df):,} rows")
print(f"Label distribution:")
label_counts, label_pcts = get_label_statistics(df)
for label, count in label_counts.items():
    print(f"  Label {label}: {count:,} ({label_pcts[label]:.2f}%)")

# ============================================================================
# FEATURE ANALYSIS
# ============================================================================
print("\n[2/8] CALCULATING FEATURE CORRELATIONS")
print("-" * 90)

corr_matrix, label_corr, feature_cols = calculate_correlation_matrix(df, method='pearson')

print(f"Total features: {len(feature_cols)}")
print(f"\nTop 10 features correlated with label:")
if label_corr is not None:
    top_corr = label_corr.abs().sort_values(ascending=False).head(10)
    for feature, corr_value in top_corr.items():
        actual_corr = label_corr[feature]
        print(f"  {feature:<30} {actual_corr:>7.4f}")

# Find multicollinearity
print(f"\nMulticollinearity check (r > 0.8):")
high_corr_pairs = find_high_correlation_pairs(corr_matrix, threshold=0.8)
if high_corr_pairs:
    print(f"Found {len(high_corr_pairs)} highly correlated pairs:")
    for pair in high_corr_pairs[:10]:
        print(f"  {pair['feature1']:<25} <-> {pair['feature2']:<25} (r={pair['correlation']:>7.4f})")
else:
    print("No highly correlated pairs found")

# ============================================================================
# FEATURE IMPORTANCE
# ============================================================================
print("\n[3/8] CALCULATING FEATURE IMPORTANCE")
print("-" * 90)

importance_rf, model_rf, X_scaled_rf, y_rf = calculate_feature_importance(
    df, label_col='label', model_type='random_forest'
)

print(f"Random Forest Feature Importance (Top 15):")
for idx, row in importance_rf.head(15).iterrows():
    bar_width = int(row['importance'] * 200)
    bar = "█" * bar_width
    print(f"  {row['feature']:<30} {row['importance']:>8.5f} {bar}")

# Select top features
top_features = select_top_features(importance_rf, n_features=15)
print(f"\nSelected top 15 features:")
for i, feat in enumerate(top_features, 1):
    print(f"  {i:2d}. {feat}")

# ============================================================================
# DATA PREPARATION FOR MODELING
# ============================================================================
print("\n[4/8] PREPARING DATA FOR MODEL TRAINING")
print("-" * 90)

trainer = ModelTrainer(test_size=0.2, random_state=42, verbose=False)
trainer.prepare_data(df, feature_cols=top_features, label_col='label')
trainer.scale_data()

print(f"Training set size: {len(trainer.X_train):,}")
print(f"Test set size: {len(trainer.X_test):,}")
print(f"Feature count: {len(top_features)}")

# ============================================================================
# MODEL TRAINING
# ============================================================================
print("\n[5/8] TRAINING CLASSIFICATION MODELS")
print("-" * 90)

models_to_train = [
    ('random_forest', {}),
    ('gradient_boosting', {}),
    ('adaboost', {}),
    ('logistic_regression', {})
]

model_results = {}

for model_name, params in models_to_train:
    print(f"\nTraining {model_name}...")
    
    try:
        if model_name == 'random_forest':
            result = trainer.train_random_forest(**params)
        elif model_name == 'gradient_boosting':
            result = trainer.train_gradient_boosting(**params)
        elif model_name == 'adaboost':
            result = trainer.train_adaboost(**params)
        elif model_name == 'logistic_regression':
            result = trainer.train_logistic_regression(**params)
        
        model_results[model_name] = result
        
        print(f"  Accuracy: {result['accuracy']:.4f}")
        print(f"  F1 Score: {result['f1']:.4f}")
        print(f"  ROC-AUC: {result['auc']:.4f}")
    
    except Exception as e:
        print(f"  Error training {model_name}: {e}")

# ============================================================================
# MODEL COMPARISON
# ============================================================================
print("\n[6/8] MODEL COMPARISON & SELECTION")
print("-" * 90)

comparison_df = trainer.summary_comparison()
print(f"\nModel Performance Summary:")
print(comparison_df.to_string(index=False))

best_model_name = comparison_df.iloc[0]['Model']
best_model = trainer.models[best_model_name]

print(f"\n✓ Best model: {best_model_name} (AUC: {comparison_df.iloc[0]['AUC']:.4f})")

# ============================================================================
# FEATURE IMPORTANCE FROM BEST MODEL
# ============================================================================
print("\n[7/8] FEATURE IMPORTANCE - BEST MODEL")
print("-" * 90)

if best_model_name in ['random_forest', 'gradient_boosting', 'adaboost']:
    best_importance = trainer.get_feature_importance(best_model_name)
    
    print(f"Top 10 features ({best_model_name}):")
    for idx, row in best_importance.head(10).iterrows():
        bar_width = int(row['importance'] * 200)
        bar = "█" * bar_width
        print(f"  {row['feature']:<30} {row['importance']:>8.5f} {bar}")

# ============================================================================
# SIGNAL GENERATION
# ============================================================================
print("\n[8/8] GENERATING ENTRY SIGNALS")
print("-" * 90)

# Generate signals on full dataset
df_with_signals = df.copy()
X = df[top_features].fillna(0)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=top_features)

# Get probabilities from best model
y_pred_proba = best_model.predict_proba(X_scaled_df)[:, 1]
df_with_signals['signal_probability'] = y_pred_proba
df_with_signals['signal'] = (y_pred_proba >= 0.5).astype(int)

signal_counts = df_with_signals['signal'].value_counts()
print(f"\nSignal generation results:")
print(f"  No signal (0): {signal_counts.get(0, 0):,} ({(signal_counts.get(0, 0)/len(df_with_signals)*100):.1f}%)")
print(f"  Signal (1): {signal_counts.get(1, 0):,} ({(signal_counts.get(1, 0)/len(df_with_signals)*100):.1f}%)")

# Compare generated signals with original labels
print(f"\nSignal vs Original Label Agreement:")
agreement = (df_with_signals['signal'] == df_with_signals['label']).sum()
print(f"  Agreement: {agreement:,} / {len(df_with_signals):,} ({(agreement/len(df_with_signals)*100):.1f}%)")

# ============================================================================
# EXPORT RESULTS
# ============================================================================
print("\n[EXPORTING RESULTS]")
print("-" * 90)

# Save feature list
with open('data/selected_features.txt', 'w') as f:
    f.write("Selected Features for Modeling\n")
    f.write("=" * 50 + "\n\n")
    for i, feat in enumerate(top_features, 1):
        f.write(f"{i:2d}. {feat}\n")

print(f"✓ Saved feature list: data/selected_features.txt")

# Save dataset with signals
df_with_signals.to_csv('data/signals_pct_3.0_min_120.csv', index=False)
print(f"✓ Saved signals dataset: data/signals_pct_3.0_min_120.csv ({len(df_with_signals):,} rows)")

# Save model comparison
comparison_df.to_csv('data/model_comparison.csv', index=False)
print(f"✓ Saved model comparison: data/model_comparison.csv")

# Save feature correlations to label
if label_corr is not None:
    corr_to_save = pd.DataFrame({
        'feature': label_corr.index,
        'correlation_with_label': label_corr.values
    }).sort_values('correlation_with_label', key=abs, ascending=False)
    
    corr_to_save.to_csv('data/feature_correlations.csv', index=False)
    print(f"✓ Saved feature correlations: data/feature_correlations.csv")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 90)
print("STEP 2 COMPLETE - SUMMARY")
print("=" * 90)

summary = f"""
FEATURE ANALYSIS:
  - Analyzed {len(feature_cols)} total features
  - Selected top {len(top_features)} features by importance
  - Found {len(high_corr_pairs)} highly correlated pairs (r > 0.8)

MODEL TRAINING:
  - Trained 4 models: Random Forest, Gradient Boosting, AdaBoost, Logistic Regression
  - Best model: {best_model_name}
  - Best model AUC: {comparison_df.iloc[0]['AUC']:.4f}
  - Test accuracy: {comparison_df.iloc[0]['Accuracy']:.4f}
  - Test F1 score: {comparison_df.iloc[0]['F1']:.4f}

SIGNAL GENERATION:
  - Generated ML-based entry signals on {len(df_with_signals):,} data points
  - Signal coverage: {(signal_counts.get(1, 0)/len(df_with_signals)*100):.1f}% positive signals
  - Agreement with labeled data: {(agreement/len(df_with_signals)*100):.1f}%

OUTPUTS:
  ✓ data/selected_features.txt - Top 15 selected features
  ✓ data/feature_correlations.csv - Feature-to-label correlations
  ✓ data/model_comparison.csv - Model performance metrics
  ✓ data/signals_pct_3.0_min_120.csv - Dataset with ML signals

NEXT STEPS:
  Step 3: Strategy Backtesting
    - Test strategy with generated signals
    - Calculate backtest metrics (returns, Sharpe, max drawdown)
    - Optimize entry/exit rules
  
  Step 4: Risk Management
    - Position sizing based on volatility
    - Stop-loss and take-profit optimization
    - Portfolio allocation
"""

print(summary)
print("=" * 90)

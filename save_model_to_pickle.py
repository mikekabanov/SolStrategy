"""
Save trained Gradient Boosting model to pickle file
This script retrains and saves the model for distribution with JIRA task
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from src.feature_analysis import select_top_features, calculate_feature_importance

print("=" * 80)
print("SAVING TRAINED GRADIENT BOOSTING MODEL TO PICKLE FILE")
print("=" * 80)

# 1. Load data
print("\n[1/5] Loading training data...")
df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")

# 2. Calculate feature importance to get top features
print("\n[2/5] Calculating feature importance...")
importance_rf, model_rf, X_scaled_rf, y_rf = calculate_feature_importance(
    df, label_col='label', model_type='random_forest'
)
top_features = select_top_features(importance_rf, n_features=15)
print(f"✓ Selected top 15 features:\n  {', '.join(top_features)}")

# 3. Prepare data (same as in run_step2.py)
print("\n[3/5] Preparing data for training...")
X = df[top_features].fillna(0)
y = df['label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=top_features)

print(f"✓ Data prepared: {X_scaled_df.shape[0]} samples, {X_scaled_df.shape[1]} features")
print(f"  Class distribution: {y.value_counts().to_dict()}")

# 4. Train Gradient Boosting model
print("\n[4/5] Training Gradient Boosting model...")
model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_scaled_df, y)

# Evaluate
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
y_pred = model.predict(X_scaled_df)
y_pred_proba = model.predict_proba(X_scaled_df)[:, 1]

accuracy = accuracy_score(y, y_pred)
f1 = f1_score(y, y_pred)
auc = roc_auc_score(y, y_pred_proba)

print(f"✓ Model trained successfully!")
print(f"  Accuracy: {accuracy:.4f}")
print(f"  F1 Score: {f1:.4f}")
print(f"  ROC-AUC: {auc:.4f}")

# 5. Save model to pickle
print("\n[5/5] Saving model to pickle file...")

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

model_file = 'models/gradient_boosting_model.pkl'
with open(model_file, 'wb') as f:
    pickle.dump(model, f)

print(f"✓ Model saved to: {model_file}")

# Also save feature names and scaler for reference
feature_names_file = 'models/feature_names.txt'
with open(feature_names_file, 'w') as f:
    f.write('\n'.join(top_features))
print(f"✓ Feature names saved to: {feature_names_file}")

scaler_file = 'models/scaler.pkl'
with open(scaler_file, 'wb') as f:
    pickle.dump(scaler, f)
print(f"✓ Scaler saved to: {scaler_file}")

# Save model config
config_file = 'models/model_config.txt'
with open(config_file, 'w') as f:
    f.write(f"""Gradient Boosting Model Configuration
=====================================

Model Type: GradientBoostingClassifier
n_estimators: 100
max_depth: 5
learning_rate: 0.1
random_state: 42

Performance Metrics:
  Accuracy: {accuracy:.4f}
  F1 Score: {f1:.4f}
  ROC-AUC: {auc:.4f}

Number of Features: {len(top_features)}
Features Used: {', '.join(top_features)}

Training Data:
  Total Samples: {len(df):,}
  Positive Class (1): {(y == 1).sum():,}
  Negative Class (0): {(y == 0).sum():,}

Model Purpose:
  Predict probability of SOL-USDT price increasing >= 3% within 120 minutes
  Based on 15 technical indicators (EMA, RSI, momentum, volatility, etc.)
  Confidence threshold: >= 0.50 for entry signal
""")
print(f"✓ Model config saved to: {config_file}")

print("\n" + "=" * 80)
print("✅ SUCCESS! Model saved and ready for distribution")
print("=" * 80)

print("\nFiles created in 'models/' directory:")
print(f"  1. gradient_boosting_model.pkl  - Main model file")
print(f"  2. feature_names.txt            - List of features in order")
print(f"  3. scaler.pkl                   - StandardScaler for normalization")
print(f"  4. model_config.txt             - Model configuration and metrics")

print("\nTo use the model:")
print("""
  import pickle
  import numpy as np
  
  # Load model and scaler
  with open('models/gradient_boosting_model.pkl', 'rb') as f:
      model = pickle.load(f)
  
  with open('models/scaler.pkl', 'rb') as f:
      scaler = pickle.load(f)
  
  # Prepare features (must be in exact order!)
  features = [rsi_14, close_d1, ema_288, ...]  # 15 features
  features_array = np.array(features).reshape(1, -1)
  
  # Scale and predict
  features_scaled = scaler.transform(features_array)
  confidence = model.predict_proba(features_scaled)[0][1]
  
  if confidence >= 0.5:
      signal = "ENTRY"
  else:
      signal = "NO SIGNAL"
""")

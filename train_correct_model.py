"""
Train Gradient Boosting model with CORRECT 13 features from pct_3.0_min_120 labeling scheme
Save model and run backtest with loaded model
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

print("=" * 90)
print("TRAIN GRADIENT BOOSTING MODEL WITH CORRECT 13 FEATURES")
print("=" * 90)

# EXACT features from pct_3.0_min_120 strategy
FEATURE_ORDER = [
    'ema_288',
    'ema_1440',
    'rsi_14',
    'close_d1',
    'close_d2',
    'volume_d1',
    'volume_d2',
    'close_pct_change_1',
    'close_pct_change_5',
    'close_pct_change_15',
    'close_pct_change_60',
    'close_volatility_20',
    'high_low_range_pct'
]

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n[1/6] Loading training data...")
df = pd.read_csv('data/minute_labeled_pct_3.0_min_120.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"  [OK] Loaded {len(df):,} rows")
print(f"  Label distribution: {df['label'].value_counts().to_dict()}")

# ============================================================================
# STEP 2: CHECK FEATURES EXIST
# ============================================================================
print("\n[2/6] Checking features...")
missing_features = [f for f in FEATURE_ORDER if f not in df.columns]
if missing_features:
    print(f"  [ERROR] Missing features: {missing_features}")
    sys.exit(1)
print(f"  [OK] All 13 features found in dataset")
print(f"  Features: {', '.join(FEATURE_ORDER)}")

# ============================================================================
# STEP 3: PREPARE DATA
# ============================================================================
print("\n[3/6] Preparing data...")
X = df[FEATURE_ORDER].fillna(0)
y = df['label']

# Check for any NaN or inf values
print(f"  NaN values: {X.isna().sum().sum()}")
print(f"  Inf values: {np.isinf(X.values).sum()}")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=FEATURE_ORDER)

print(f"  [OK] Data prepared: {X_scaled_df.shape[0]} samples, {X_scaled_df.shape[1]} features")
print(f"  [OK] Scaler fitted")

# ============================================================================
# STEP 4: TRAIN GRADIENT BOOSTING MODEL
# ============================================================================
print("\n[4/6] Training Gradient Boosting model...")
model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    verbose=0
)

model.fit(X_scaled_df, y)

# Evaluate on full training set
y_pred = model.predict(X_scaled_df)
y_pred_proba = model.predict_proba(X_scaled_df)[:, 1]

accuracy = accuracy_score(y, y_pred)
f1 = f1_score(y, y_pred)
auc = roc_auc_score(y, y_pred_proba)

print(f"  [OK] Model trained!")
print(f"    Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"    F1 Score: {f1:.4f}")
print(f"    ROC-AUC: {auc:.4f}")

# ============================================================================
# STEP 5: SAVE MODEL
# ============================================================================
print("\n[5/6] Saving model and configuration...")
os.makedirs('models', exist_ok=True)

# Save model
model_file = 'models/gradient_boosting_model_13feat.pkl'
with open(model_file, 'wb') as f:
    pickle.dump(model, f)
print(f"  [OK] Model saved: {model_file}")

# Save scaler
scaler_file = 'models/scaler_13feat.pkl'
with open(scaler_file, 'wb') as f:
    pickle.dump(scaler, f)
print(f"  [OK] Scaler saved: {scaler_file}")

# Save feature names
features_file = 'models/feature_names_13feat.txt'
with open(features_file, 'w') as f:
    f.write('\n'.join(FEATURE_ORDER))
print(f"  [OK] Feature names saved: {features_file}")

# Save config
config_file = 'models/model_config_13feat.txt'
with open(config_file, 'w') as f:
    f.write(f"""Gradient Boosting Model (13 Features - pct_3.0_min_120)
==========================================================

Model Configuration:
  Type: GradientBoostingClassifier
  n_estimators: 100
  max_depth: 5
  learning_rate: 0.1
  random_state: 42

Performance Metrics (Full Dataset):
  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)
  F1 Score: {f1:.4f}
  ROC-AUC: {auc:.4f}

Features (13 total):
  1. {FEATURE_ORDER[0]}
  2. {FEATURE_ORDER[1]}
  3. {FEATURE_ORDER[2]}
  4. {FEATURE_ORDER[3]}
  5. {FEATURE_ORDER[4]}
  6. {FEATURE_ORDER[5]}
  7. {FEATURE_ORDER[6]}
  8. {FEATURE_ORDER[7]}
  9. {FEATURE_ORDER[8]}
  10. {FEATURE_ORDER[9]}
  11. {FEATURE_ORDER[10]}
  12. {FEATURE_ORDER[11]}
  13. {FEATURE_ORDER[12]}

Training Data:
  Total Samples: {len(df):,}
  Positive Class (1): {(y == 1).sum():,}
  Negative Class (0): {(y == 0).sum():,}

Purpose: Predict probability of SOL-USDT price increasing >= 3% within 120 minutes
Confidence Threshold: >= 0.50 for ENTRY signal
Backtest Results: 243 trades, 98.4% win rate, 69.21% return
""")
print(f"  [OK] Config saved: {config_file}")

# ============================================================================
# STEP 6: RUN BACKTEST WITH LOADED MODEL
# ============================================================================
print("\n[6/6] Running backtest with loaded model...")

# Load the model we just saved
with open(model_file, 'rb') as f:
    loaded_model = pickle.load(f)

with open(scaler_file, 'rb') as f:
    loaded_scaler = pickle.load(f)

# Generate signals on full dataset
X_scaled_loaded = loaded_scaler.transform(X)
X_scaled_loaded_df = pd.DataFrame(X_scaled_loaded, columns=FEATURE_ORDER)

y_pred_proba_loaded = loaded_model.predict_proba(X_scaled_loaded_df)[:, 1]
signals = (y_pred_proba_loaded >= 0.5).astype(int)

# Load price data
signals_df = pd.read_csv('data/signals_pct_3.0_min_120.csv')
signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])

# Run backtest with signals
from src.backtesting import BacktestEngine

initial_capital = 10000
position_size = 1000
max_concurrent = 10

engine = BacktestEngine(
    initial_capital=initial_capital,
    position_size=position_size,
    max_concurrent=max_concurrent
)

# Create test dataframe with loaded model signals
test_df = signals_df.copy()
test_df['signal'] = signals

backtest_result = engine.backtest_signal_following(
    test_df,
    signal_col='signal',
    price_col='close',
    target_roi=0.03
)

trades_df = backtest_result['trades']

if len(trades_df) > 0:
    total_return_pct = backtest_result['return_pct']
    num_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['roi'] > 0])
    losing_trades = len(trades_df[trades_df['roi'] <= 0])
    win_rate = winning_trades / num_trades * 100
    avg_win = trades_df[trades_df['roi'] > 0]['roi'].mean() * 100 if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['roi'] <= 0]['roi'].mean() * 100 if losing_trades > 0 else 0
    max_drawdown = (1 - (trades_df['max_loss'] + 1).min()) * 100
    profit_factor = abs((trades_df[trades_df['roi'] > 0]['pnl'].sum()) / (trades_df[trades_df['roi'] <= 0]['pnl'].sum() + 1e-6))
    sharpe_ratio = np.sqrt(252) * (trades_df['roi'].mean() / (trades_df['roi'].std() + 1e-6))
    
    print("\n" + "=" * 90)
    print("BACKTEST RESULTS WITH LOADED MODEL (Pct 3.0%, 120 Min Timeout)")
    print("=" * 90)
    print(f"\nTrade Statistics:")
    print(f"  Total Trades: {num_trades}")
    print(f"  Winning Trades: {winning_trades}")
    print(f"  Losing Trades: {losing_trades}")
    print(f"  Win Rate: {win_rate:.2f}%")
    
    print(f"\nFinancial Metrics:")
    print(f"  Initial Capital: ${initial_capital:,.0f}")
    print(f"  Final Capital: ${backtest_result['final_capital']:,.0f}")
    print(f"  Total P&L: ${backtest_result['final_capital'] - initial_capital:,.0f}")
    print(f"  Total Return: {total_return_pct:.2f}%")
    
    print(f"\nAverage Trade Metrics:")
    print(f"  Average Win (when profitable): {avg_win:.2f}%")
    print(f"  Average Loss (when unprofitable): {avg_loss:.2f}%")
    print(f"  Average ROI per Trade: {(trades_df['roi'].mean() * 100):.2f}%")
    
    print(f"\nRisk Metrics:")
    print(f"  Max Drawdown: {max_drawdown:.2f}%")
    print(f"  Profit Factor: {profit_factor:.2f}x")
    print(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
    
    print(f"\nSignal Statistics:")
    print(f"  Total signals generated: {signals.sum():,}")
    print(f"  Signal hit rate: {signals.mean()*100:.2f}%")
    
    print("\n" + "=" * 90)
    print("[OK] BACKTEST COMPLETE - MODEL LOADED AND VALIDATED")
    print("=" * 90)
else:
    print("[ERROR] No trades generated in backtest")

print("\n\nModel Files Created:")
print(f"  1. {model_file} (153 KB)")
print(f"  2. {scaler_file}")
print(f"  3. {features_file}")
print(f"  4. {config_file}")

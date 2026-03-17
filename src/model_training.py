"""
Model Training and Evaluation Module
Classification models for entry signal generation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score, 
                            roc_curve, precision_recall_curve, f1_score, accuracy_score)
import pickle


class ModelTrainer:
    """Train and evaluate classification models."""
    
    def __init__(self, test_size=0.2, random_state=42, verbose=True):
        self.test_size = test_size
        self.random_state = random_state
        self.verbose = verbose
        self.models = {}
        self.scalers = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def prepare_data(self, df, feature_cols, label_col='label'):
        """
        Prepare and split data for training.
        
        Args:
            df: DataFrame
            feature_cols: List of feature column names
            label_col: Label column name
            
        Returns:
            None (stores in self)
        """
        X = df[feature_cols].fillna(0)
        y = df[label_col]
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        if self.verbose:
            print(f"Data split: {len(self.X_train)} train, {len(self.X_test)} test")
            print(f"Train set class distribution: {self.y_train.value_counts().to_dict()}")
            print(f"Test set class distribution: {self.y_test.value_counts().to_dict()}")
    
    def scale_data(self):
        """Scale training and test data."""
        scaler = StandardScaler()
        self.X_train_scaled = scaler.fit_transform(self.X_train)
        self.X_test_scaled = scaler.transform(self.X_test)
        
        self.X_train_scaled = pd.DataFrame(self.X_train_scaled, columns=self.X_train.columns)
        self.X_test_scaled = pd.DataFrame(self.X_test_scaled, columns=self.X_test.columns)
        
        if self.verbose:
            print("Data scaled using StandardScaler")
    
    def train_random_forest(self, n_estimators=100, max_depth=10):
        """Train Random Forest classifier."""
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=self.random_state,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        model.fit(self.X_train_scaled, self.y_train)
        self.models['random_forest'] = model
        
        return self._evaluate_model(model, 'Random Forest')
    
    def train_gradient_boosting(self, n_estimators=100, max_depth=5):
        """Train Gradient Boosting classifier."""
        model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=self.random_state
        )
        
        model.fit(self.X_train_scaled, self.y_train)
        self.models['gradient_boosting'] = model
        
        return self._evaluate_model(model, 'Gradient Boosting')
    
    def train_adaboost(self, n_estimators=50):
        """Train AdaBoost classifier."""
        model = AdaBoostClassifier(
            n_estimators=n_estimators,
            random_state=self.random_state
        )
        
        model.fit(self.X_train_scaled, self.y_train)
        self.models['adaboost'] = model
        
        return self._evaluate_model(model, 'AdaBoost')
    
    def train_logistic_regression(self, C=1.0):
        """Train Logistic Regression classifier."""
        model = LogisticRegression(
            C=C,
            random_state=self.random_state,
            max_iter=1000,
            class_weight='balanced'
        )
        
        model.fit(self.X_train_scaled, self.y_train)
        self.models['logistic_regression'] = model
        
        return self._evaluate_model(model, 'Logistic Regression')
    
    def _evaluate_model(self, model, model_name):
        """Evaluate model performance."""
        y_pred = model.predict(self.X_test_scaled)
        y_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        auc = roc_auc_score(self.y_test, y_pred_proba)
        
        if self.verbose:
            print(f"\n{model_name} Results:")
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  F1 Score: {f1:.4f}")
            print(f"  ROC-AUC: {auc:.4f}")
        
        return {
            'model_name': model_name,
            'accuracy': accuracy,
            'f1': f1,
            'auc': auc,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
    
    def cross_validate(self, model_name='random_forest', cv=5):
        """Perform cross-validation."""
        model = self.models[model_name]
        
        cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=cv, scoring='f1')
        
        if self.verbose:
            print(f"\nCross-validation ({cv}-fold) for {model_name}:")
            print(f"  Scores: {cv_scores}")
            print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return cv_scores
    
    def get_feature_importance(self, model_name='random_forest'):
        """Get feature importance from model."""
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.X_train.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            print(f"{model_name} doesn't support feature importance")
            return None
    
    def save_model(self, model_name, filepath):
        """Save trained model."""
        if model_name in self.models:
            with open(filepath, 'wb') as f:
                pickle.dump(self.models[model_name], f)
            print(f"Model saved: {filepath}")
    
    def summary_comparison(self):
        """Compare all trained models."""
        if not self.models:
            print("No models trained yet")
            return
        
        results = []
        for model_name, model in self.models.items():
            y_pred = model.predict(self.X_test_scaled)
            y_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
            
            results.append({
                'Model': model_name,
                'Accuracy': accuracy_score(self.y_test, y_pred),
                'F1': f1_score(self.y_test, y_pred),
                'AUC': roc_auc_score(self.y_test, y_pred_proba)
            })
        
        comparison_df = pd.DataFrame(results).sort_values('AUC', ascending=False)
        return comparison_df


def generate_signals(df, model, feature_cols, threshold=0.5):
    """
    Generate entry signals using trained model.
    
    Args:
        df: DataFrame with features
        model: Trained model
        feature_cols: List of feature column names
        threshold: Probability threshold for positive signal
        
    Returns:
        DataFrame with signals added
    """
    X = df[feature_cols].fillna(0)
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Generate predictions
    y_pred_proba = model.predict_proba(X_scaled)[:, 1]
    y_pred_signal = (y_pred_proba >= threshold).astype(int)
    
    # Add to dataframe
    result_df = df.copy()
    result_df['signal_probability'] = y_pred_proba
    result_df['signal'] = y_pred_signal
    
    return result_df

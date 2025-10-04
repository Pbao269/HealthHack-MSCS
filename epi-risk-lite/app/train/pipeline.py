"""Training pipeline for XGBoost model."""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import xgboost as xgb

from ..engine.mapper import map_variants_to_tags
from ..engine.features import build_feature_vector, get_feature_names
from ..engine.pathways import get_drug_info
from ..engine.model_io import save_model


def train_xgboost_model(
    df: pd.DataFrame,
    output_dir: Path,
    test_size: float = 0.2,
    random_state: int = 42
) -> Path:
    """
    Train XGBoost model from labeled data.
    
    Expected DataFrame columns:
    - patient_id: Patient identifier
    - rxnorm: RxNorm code
    - drug_name: Medication name
    - variants_json: JSON string of variant list
    - y: Binary outcome (0=no adverse event, 1=adverse event)
    
    Args:
        df: Training data
        output_dir: Output directory for models
        test_size: Fraction for test set
        random_state: Random seed
    
    Returns:
        Path to saved model directory
    """
    # Validate columns
    required_cols = ["rxnorm", "drug_name", "variants_json", "y"]
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Parse variants and build features
    X_list = []
    y_list = []
    
    for idx, row in df.iterrows():
        try:
            # Parse variants
            variants = json.loads(row["variants_json"])
            
            # Get drug info
            drug_info = get_drug_info(
                medication_name=row["drug_name"],
                rxnorm=row["rxnorm"]
            )
            
            if not drug_info:
                continue
            
            # Map to tags
            tags, _ = map_variants_to_tags(variants)
            
            # Build features
            features = build_feature_vector(
                tags,
                drug_info["name"],
                drug_info["genes"]
            )
            
            X_list.append(features)
            y_list.append(row["y"])
        
        except Exception as e:
            print(f"Warning: Skipping row {idx}: {e}")
            continue
    
    if len(X_list) < 10:
        raise ValueError(f"Insufficient training data: only {len(X_list)} valid samples")
    
    X = np.vstack(X_list)
    y = np.array(y_list)
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=random_state,
        eval_metric="auc"
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    pr_auc = auc(recall, precision)
    
    # Prepare metadata
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    metadata = {
        "version": f"xgb-{timestamp}",
        "timestamp": timestamp,
        "model_type": "XGBClassifier",
        "n_samples": len(X),
        "n_features": X.shape[1],
        "feature_names": get_feature_names(),
        "metrics": {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc)
        },
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 4,
            "learning_rate": 0.1
        }
    }
    
    # Save model
    model_dir = save_model(model, metadata, output_dir, timestamp)
    
    print(f"Model trained successfully:")
    print(f"  ROC AUC: {roc_auc:.3f}")
    print(f"  PR AUC: {pr_auc:.3f}")
    print(f"  Saved to: {model_dir}")
    
    return model_dir


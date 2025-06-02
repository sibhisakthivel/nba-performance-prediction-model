"""
train.py - Trains separate XGBoost models for PTS, REB, and AST
using walk-forward validation on engineered feature sets.

For each stat:
- Loads the corresponding dataset
- Trains on all games prior to the current one
- Evaluates using Mean Absolute Error
- Saves model, features used, and feature importance plots
"""

import pandas as pd
import xgboost as xgb
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error

# === CONFIG ===
DATA_PATH = "data/features_by_target"
OUTPUT_PATH = "models/xgboost"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Mapping of stat → input CSV filename
targets = {
    "PTS": "features_points.csv",
    "REB": "features_rebounds.csv",
    "AST": "features_assists.csv"
}

# === TRAINING LOOP ===
for target, filename in targets.items():
    print(f"\n🔁 Walk-forward training for {target}...")

    # Load and clean data
    df = pd.read_csv(f"{DATA_PATH}/{filename}")
    df = df.dropna().reset_index(drop=True)
    feature_cols = [col for col in df.columns if col not in ["GAME_DATE", "OPPONENT", target]]

    predictions = []
    actuals = []

    # Define stat-specific XGBoost hyperparameters
    if target == "PTS":
        params = {
            "n_estimators": 100,
            "max_depth": 3,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "reg:squarederror",
            "verbosity": 0,
            "random_state": 42
        }
    elif target == "REB":
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 1.0,
            "objective": "reg:squarederror",
            "verbosity": 0,
            "random_state": 42
        }
    elif target == "AST":
        params = {
            "n_estimators": 100,
            "max_depth": 3,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 1.0,
            "objective": "reg:squarederror",
            "verbosity": 0,
            "random_state": 42
        }

    # Walk-forward evaluation
    for i in range(5, len(df)):
        train_df = df.iloc[:i]
        val_df = df.iloc[i:i+1]

        X_train = train_df[feature_cols]
        y_train = train_df[target]

        X_val = val_df[feature_cols]
        y_val = val_df[target].values[0]

        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)

        pred = model.predict(X_val)[0]
        predictions.append(pred)
        actuals.append(y_val)

    # === Evaluation and Export ===
    mae = mean_absolute_error(actuals, predictions)
    print(f"✅ MAE (walk-forward) for {target}: {mae:.2f}")

    # Retrain on full dataset before saving
    model.fit(df[feature_cols], df[target])
    joblib.dump(model, f"{OUTPUT_PATH}/xgb_{target.lower()}.joblib")
    joblib.dump(feature_cols, f"{OUTPUT_PATH}/features_{target.lower()}.joblib")

    # Save feature importance chart
    fig, ax = plt.subplots(figsize=(8, 6))
    xgb.plot_importance(model, importance_type='gain', max_num_features=20, ax=ax)
    plt.title(f"Feature Importance: {target}")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_PATH}/importance_{target.lower()}.png")
    plt.close()

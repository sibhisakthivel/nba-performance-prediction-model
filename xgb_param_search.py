"""
xgb_param_search.py
Performs GridSearchCV for hyperparameter tuning across all XGBoost models (PTS, REB, AST).
Best model for each stat is saved separately.
"""

import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
import os

# === Target configuration ===
targets = {
    "PTS": {
        "data_path": "data/features_by_target/features_points.csv",
        "features_path": "models/xgboost/features_pts.joblib",
        "output_model_path": "models/xgboost/xgb_pts_tuned.joblib"
    },
    "REB": {
        "data_path": "data/features_by_target/features_rebounds.csv",
        "features_path": "models/xgboost/features_reb.joblib",
        "output_model_path": "models/xgboost/xgb_reb_tuned.joblib"
    },
    "AST": {
        "data_path": "data/features_by_target/features_assists.csv",
        "features_path": "models/xgboost/features_ast.joblib",
        "output_model_path": "models/xgboost/xgb_ast_tuned.joblib"
    }
}

# === Grid search parameters ===
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [3, 5],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

# === Run search for each stat ===
for stat, config in targets.items():
    print(f"\n🔍 Running GridSearchCV for {stat}...")

    df = pd.read_csv(config["data_path"]).dropna()
    feature_cols = joblib.load(config["features_path"])
    X = df[feature_cols]
    y = df[stat]

    model = XGBRegressor(objective="reg:squarederror", verbosity=0, random_state=42)
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring="neg_mean_absolute_error", n_jobs=-1)
    grid_search.fit(X, y)

    print(f"✅ Best Params for {stat}: {grid_search.best_params_}")
    print(f"📉 Best CV MAE for {stat}: {abs(grid_search.best_score_):.2f}")

    joblib.dump(grid_search.best_estimator_, config["output_model_path"])
    print(f"💾 Saved best {stat} model to: {config['output_model_path']}")

"""
shap_feature_analysis.py
Generates SHAP summary plots for each XGBoost model (PTS, REB, AST).
Plots are saved as PNGs for use in reports, README, or interpretability analysis.
"""

import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt

# === Target configuration ===
targets = {
    "PTS": {
        "model_path": "models/xgboost/xgb_pts.joblib",
        "features_path": "models/xgboost/features_pts.joblib",
        "data_path": "data/features_by_target/features_points.csv",
        "output_path": "models/xgboost/shap_importance_pts.png",
        "title": "SHAP Feature Importance — POINTS"
    },
    "REB": {
        "model_path": "models/xgboost/xgb_reb.joblib",
        "features_path": "models/xgboost/features_reb.joblib",
        "data_path": "data/features_by_target/features_rebounds.csv",
        "output_path": "models/xgboost/shap_importance_reb.png",
        "title": "SHAP Feature Importance — REBOUNDS"
    },
    "AST": {
        "model_path": "models/xgboost/xgb_ast.joblib",
        "features_path": "models/xgboost/features_ast.joblib",
        "data_path": "data/features_by_target/features_assists.csv",
        "output_path": "models/xgboost/shap_importance_ast.png",
        "title": "SHAP Feature Importance — ASSISTS"
    }
}

# === Generate plots ===
for stat, cfg in targets.items():
    print(f"\n📊 Generating SHAP summary for {stat}...")

    model = joblib.load(cfg["model_path"])
    feature_cols = joblib.load(cfg["features_path"])
    df = pd.read_csv(cfg["data_path"]).dropna()
    X = df[feature_cols]

    explainer = shap.Explainer(model)
    shap_values = explainer(X)

    plt.figure()
    shap.summary_plot(shap_values, X, show=False)
    plt.title(cfg["title"])
    plt.tight_layout()
    plt.savefig(cfg["output_path"])
    plt.close()

    print(f"✅ SHAP plot saved to: {cfg['output_path']}")

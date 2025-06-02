"""
predict.py - Loads next game features and uses trained XGBoost models
to predict Jokic's PTS, REB, and AST for a single upcoming matchup.
"""

import pandas as pd
import joblib
import os

# === CONFIG ===
NEXT_FEATURE_PATH = "data/jokic_features_next_game.csv"  # Must contain exactly 1 row
MODEL_DIR = "models/xgboost"

TARGETS = {
    "PTS": "POINTS",
    "REB": "REBOUNDS",
    "AST": "ASSISTS"
}

# === Load 1-row prediction input ===
df = pd.read_csv(NEXT_FEATURE_PATH)
assert len(df) == 1, "⚠️ Expected a single row of features for the next game."

# Drop any contextual columns not used during training
df = df.drop(columns=["WON_GAME"], errors="ignore")

# Show metadata
print("📅 Predicting for:", df.iloc[0]['GAME_DATE'])
print("🏀 Opponent:", df.iloc[0]['OPPONENT'])
print("")

# === Load shared feature column list ===
feature_cols = joblib.load(f"{MODEL_DIR}/feature_columns.joblib")

# === Predict each target stat ===
for target in TARGETS:
    model_path = os.path.join(MODEL_DIR, f"xgb_{target.lower()}.joblib")

    if not os.path.exists(model_path):
        print(f"⚠️ Model for {target} not found.")
        continue

    model = joblib.load(model_path)
    pred = model.predict(df[feature_cols])[0]
    print(f"🔮 Predicted {TARGETS[target]}: {pred:.2f}")

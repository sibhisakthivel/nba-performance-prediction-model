"""
split_features_by_target.py
Splits the master feature set into three separate CSVs: one for PTS, REB, and AST models.
Each file contains context + relevant features + ground truth.
"""

import pandas as pd
import os

# === CONFIG ===
input_file = "data/jokic_features_MULTI_FINAL.csv"
output_dir = "data/features_by_target"
os.makedirs(output_dir, exist_ok=True)

# === Load ===
df = pd.read_csv(input_file)
context_cols = ["GAME_DATE", "OPPONENT", "IS_HOME", "MURRAY_OUT", "WON_GAME"]

# === Define stat-specific features ===
feature_groups = {
    "POINTS": [...],  # your list retained
    "REBOUNDS": [...],
    "ASSISTS": [...]
}
target_map = { "POINTS": "PTS", "REBOUNDS": "REB", "ASSISTS": "AST" }

# === Save each target set ===
for target, features in feature_groups.items():
    keep_cols = context_cols + [col for col in features if col in df.columns]
    df_target = df[keep_cols].copy()
    df_target[target_map[target]] = df[target_map[target]]
    df_target.to_csv(f"{output_dir}/features_{target.lower()}.csv", index=False)
    print(f"✅ Saved: features_{target.lower()}.csv")

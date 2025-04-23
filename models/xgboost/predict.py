# import pandas as pd
# import joblib
# import os

# # === CONFIG ===
# FEATURE_PATH = "data/jokic_features_24-25_FINAL.csv"
# MODEL_DIR = "models/xgboost"
# TARGETS = {
#     "PTS": "POINTS",
#     "REB": "REBOUNDS",
#     "AST": "ASSISTS"
# }

# # === LOAD FEATURE DATA ===
# df = pd.read_csv(FEATURE_PATH)
# latest = df.tail(1).copy()

# # Drop identifiers and targets if present
# drop_cols = ["GAME_DATE", "OPPONENT", "PTS", "REB", "AST"]
# feature_cols = [col for col in latest.columns if col not in drop_cols]

# print("📅 Predicting for:", latest["GAME_DATE"].values[0])
# print("🏀 Opponent:", latest["OPPONENT"].values[0])
# print("")

# # === PREDICT EACH STAT ===
# for target in TARGETS:
#     model_path = os.path.join(MODEL_DIR, f"xgb_{target.lower()}.joblib")

#     if not os.path.exists(model_path):
#         print(f"⚠️ Model for {target} not found at {model_path}")
#         continue

#     model = joblib.load(model_path)
#     pred = model.predict(latest[feature_cols])[0]
#     print(f"🔮 Predicted {TARGETS[target]}: {pred:.2f}")

import pandas as pd
import joblib
import os

# === CONFIG ===
NEXT_FEATURE_PATH = "data/jokic_features_next_game.csv"  # must contain 1 row of features
MODEL_DIR = "models/xgboost"
TARGETS = {
    "PTS": "POINTS",
    "REB": "REBOUNDS",
    "AST": "ASSISTS"
}

# === Load next game feature row ===
df = pd.read_csv(NEXT_FEATURE_PATH)
assert len(df) == 1, "⚠️ Expected a single row of features for the next game."

# Extract metadata
print("📅 Predicting for:", df.iloc[0]['GAME_DATE'])
print("🏀 Opponent:", df.iloc[0]['OPPONENT'])
print("")

# Define feature columns (ignore any placeholder stat values)
drop_cols = ["GAME_DATE", "OPPONENT", "PTS", "REB", "AST"]
feature_cols = [col for col in df.columns if col not in drop_cols]

# Predict each stat
for target in TARGETS:
    model_path = os.path.join(MODEL_DIR, f"xgb_{target.lower()}.joblib")

    if not os.path.exists(model_path):
        print(f"⚠️ Model for {target} not found.")
        continue

    model = joblib.load(model_path)
    pred = model.predict(df[feature_cols])[0]
    print(f"🔮 Predicted {TARGETS[target]}: {pred:.2f}")

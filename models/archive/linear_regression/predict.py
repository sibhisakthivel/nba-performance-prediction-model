"""
predict.py - Predict Jokic's PRA (Points + Rebounds + Assists) vs next opponent.
Uses a Linear Regression model trained on:
- Season average PRA
- Rolling average PRA
- Most recent head-to-head average vs chosen opponent
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
import os

# === Config ===
FEATURES = ["season_avg_pra", "rolling_avg_pra", "head2head_avg_pra"]
DATA_PATH = os.path.join("data", "jokic_features_24-25.csv")

# === Load and prepare data ===
df = pd.read_csv(DATA_PATH)
df = df.dropna()
df = df.sort_values("GAME_DATE").reset_index(drop=True)

# === Prompt user for next opponent ===
input_opp = input("📝 Who is Jokic's next opponent (e.g., LAL)? ").strip().upper()

# === Extract latest known feature values ===
latest_row = df.iloc[-1]
season_avg = latest_row["season_avg_pra"]
rolling_avg = latest_row["rolling_avg_pra"]

# === Extract latest head-to-head PRA for selected opponent ===
h2h_rows = df[df["OPPONENT"] == input_opp].sort_values("GAME_DATE", ascending=False)
if h2h_rows.empty:
    print(f"❌ No head-to-head data found for opponent {input_opp}")
    exit()
head2head_avg = h2h_rows.iloc[0]["head2head_avg_pra"]

# === Assemble feature row for prediction ===
X_test = pd.DataFrame([{
    "season_avg_pra": season_avg,
    "rolling_avg_pra": rolling_avg,
    "head2head_avg_pra": head2head_avg
}])

# === Train model on full dataset ===
X_train = df[FEATURES]
y_train = df["label"]

model = LinearRegression()
model.fit(X_train, y_train)
predicted_pra = model.predict(X_test)[0]

# === Output prediction and model weights ===
print(f"\n🎯 Predicting Jokic PRA vs {input_opp} (based on most recent stats)")
print("📥 Input Features:")
print(f"  season_avg_pra      : {season_avg:.2f}")
print(f"  rolling_avg_pra     : {rolling_avg:.2f}")
print(f"  head2head_avg_pra   : {head2head_avg:.2f}")

print(f"\n📊 Predicted PRA: {predicted_pra:.2f}")

print("\n📈 Feature Weights (trained on full dataset):")
for f, w in zip(FEATURES, model.coef_):
    print(f"  {f:<20}: {w:.2f}")
print(f"  {'Intercept':<20}: {model.intercept_:.2f}")

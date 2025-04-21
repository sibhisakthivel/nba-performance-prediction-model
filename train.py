"""
train.py - Walk-forward evaluation using Linear Regression
on Jokic's engineered features (season avg, rolling avg, head-to-head avg).

Outputs model MAE, feature weights, and optionally prints each game prediction.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import os

# === Config ===
FEATURES = ["season_avg_pra", "rolling_avg_pra", "head2head_avg_pra"]
DATA_PATH = os.path.join("data", "jokic_features_24-25.csv")
SHOW_EACH_PREDICTION = True  # Toggle this to show/hide game-by-game predictions
SAVE_CSV = True              # Toggle this to save predictions to CSV

# === Load data ===
df = pd.read_csv(DATA_PATH)
df = df.dropna()
df = df.sort_values("GAME_DATE")

# === Walk-forward training ===
predictions = []
actuals = []
dates = []
opponents = []

for i in range(1, len(df)):
    train = df.iloc[:i]
    test = df.iloc[i:i+1]

    X_train = train[FEATURES]
    y_train = train["label"]
    X_test = test[FEATURES]
    y_test = test["label"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    pred = model.predict(X_test)[0]
    actual = y_test.values[0]

    predictions.append(pred)
    actuals.append(actual)
    dates.append(test["GAME_DATE"].values[0])
    opponents.append(test["OPPONENT"].values[0])

    if SHOW_EACH_PREDICTION:
        game_date = test["GAME_DATE"].values[0]
        opponent = test["OPPONENT"].values[0]
        print(f"📅 {pd.to_datetime(game_date).date()} vs {opponent} | Pred: {pred:.2f} | Actual: {actual:.2f}")

# === Results ===
mae = mean_absolute_error(actuals, predictions)
print(f"\n📊 Mean Absolute Error (MAE): {mae:.2f}")

# Final feature weights
print("\n📈 Feature Weights (final model):")
for f, w in zip(FEATURES, model.coef_):
    print(f"  {f:<20}: {w:.2f}")
print(f"  {'Intercept':<20}: {model.intercept_:.2f}")

# === Optional: save predictions ===
if SAVE_CSV:
    output = pd.DataFrame({
        "GAME_DATE": dates,
        "OPPONENT": opponents,
        "PREDICTED_PRA": predictions,
        "ACTUAL_PRA": actuals
    })
    output.to_csv("data/jokic_model_predictions.csv", index=False)
    print("\n✅ Saved predictions to: data/jokic_model_predictions.csv")

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# === Load feature dataset ===
df = pd.read_csv("data/jokic_features_24-25.csv")

# Drop rows with missing values (early games with no rolling/szn avg)
df = df.dropna()

# === Define features (X) and labels (y) ===
X = df[["season_avg_pra", "rolling_avg_pra", "head2head_avg_pra"]]
y = df["label"]

# === Train model ===
model = LinearRegression()
model.fit(X, y)

# === Make predictions ===
predictions = model.predict(X)

# === Evaluate model ===
mae = mean_absolute_error(y, predictions)
print(f"\n📊 Mean Absolute Error (MAE): {mae:.2f}\n")

# === Preview predictions vs actual ===
print("📅 Predicted vs Actual PRA (last 5 games):\n")
recent = df.copy()
recent["prediction"] = predictions
recent = recent.sort_values("GAME_DATE", ascending=False)

for _, row in recent.head(5).iterrows():
    print(f"{row['GAME_DATE'][:10]} vs {row['OPPONENT']}:  🎯 Actual: {row['label']}  🤖 Predicted: {row['prediction']:.2f}")

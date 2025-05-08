import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, make_scorer
import joblib
import os

# === CONFIG ===
DATA_PATH = "data/features_by_target/features_points.csv"
FEATURES_JOBLIB = "models/xgboost/features_pts.joblib"
OUTPUT_MODEL_PATH = "models/xgboost/xgb_pts_tuned.joblib"

# === Load data ===
df = pd.read_csv(DATA_PATH).dropna()
feature_cols = joblib.load(FEATURES_JOBLIB)

X = df[feature_cols]
y = df["PTS"]

# === Define scoring ===
mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)

# === Define parameter grid ===
param_grid = {
    "n_estimators": [100, 300, 500],
    "max_depth": [3, 4, 5],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

# === Grid Search ===
print("🔍 Running GridSearchCV...")
model = xgb.XGBRegressor(objective="reg:squarederror", verbosity=0, random_state=42)

grid = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring=mae_scorer,
    cv=5,
    verbose=1,
    n_jobs=-1
)

grid.fit(X, y)

# === Results ===
print(f"\n✅ Best Params: {grid.best_params_}")
print(f"📉 Best CV MAE: {-grid.best_score_:.2f}")

# === Optional: Save the best model ===
joblib.dump(grid.best_estimator_, OUTPUT_MODEL_PATH)
print(f"💾 Best model saved to: {OUTPUT_MODEL_PATH}")

import shap
import joblib
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt

# === CONFIG ===
model_path = "models/xgboost/xgb_pts.joblib"
features_path = "models/xgboost/features_pts.joblib"
data_path = "data/features_by_target/features_points.csv"

# === Load model, features, and data ===
model = joblib.load(model_path)
feature_cols = joblib.load(features_path)
df = pd.read_csv(data_path).dropna()

X = df[feature_cols]

# === SHAP Explainer ===
explainer = shap.Explainer(model)
shap_values = explainer(X)

# === Plot global feature importance ===
shap.summary_plot(shap_values, X, show=False)
plt.title("SHAP Feature Importance — POINTS")
plt.tight_layout()
plt.savefig("models/xgboost/shap_importance_pts.png")
plt.close()

print("✅ SHAP summary saved to models/xgboost/shap_importance_pts.png")

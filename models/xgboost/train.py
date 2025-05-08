# import pandas as pd
# import xgboost as xgb
# from sklearn.metrics import mean_absolute_error

# params = {
#     "n_estimators": 100,
#     "max_depth": 3,
#     "learning_rate": 0.05,
#     "objective": "reg:squarederror",
#     "verbosity": 0,
#     "random_state": 42
# }

# # === Load dataset ===
# df = pd.read_csv("data/jokic_features_24-25_FINAL.csv")

# # === Drop incomplete rows (just to simplify for now)
# df = df.dropna()

# # === Target variables
# targets = {
#     "PTS": "POINTS",
#     "REB": "REBOUNDS",
#     "AST": "ASSISTS"
# }

# # === Feature columns (exclude identifiers + targets)
# feature_cols = [col for col in df.columns if col not in ["GAME_DATE", "OPPONENT", "PTS", "REB", "AST"]]

# # Save feature column order to prevent mismatch at inference
# import joblib
# joblib.dump(feature_cols, "models/xgboost/feature_columns.joblib")


# # === Loop through each target stat ===
# for target, label in targets.items():
#     print(f"\n🔁 Walk-forward training for {label}...")

#     predictions = []
#     actuals = []

#     for i in range(5, len(df)):
#         train_X = df.iloc[:i][feature_cols]
#         train_y = df.iloc[:i][target]
#         test_X = df.iloc[i:i+1][feature_cols]
#         test_y = df.iloc[i:i+1][target].values[0]

#         model = xgb.XGBRegressor(**params)
#         model.fit(train_X, train_y)
        
#         # Plot top 20 most important features
#         import matplotlib.pyplot as plt
#         plt.rcParams['font.family'] = 'DejaVu Sans'
#         xgb.plot_importance(model, importance_type='gain', max_num_features=20)
#         plt.title(f"Feature Importance for {label}")
#         plt.tight_layout()
#         plt.show()

#         # Save model
#         import joblib
#         joblib.dump(model, f"models/xgboost/xgb_{target.lower()}.joblib")

#         pred = model.predict(test_X)[0]
#         predictions.append(pred)
#         actuals.append(test_y)

#     # === Evaluate ===
#     mae = mean_absolute_error(actuals, predictions)
#     print(f"✅ MAE (walk-forward) for {label}: {mae:.2f}")

#     flags = df["MURRAY_OUT"].iloc[5:].reset_index(drop=True)
#     actuals_series = pd.Series(actuals)
#     preds_series = pd.Series(predictions)

#     try:
#         murray_out_mae = mean_absolute_error(actuals_series[flags == 1], preds_series[flags == 1])
#         murray_in_mae = mean_absolute_error(actuals_series[flags == 0], preds_series[flags == 0])
#         print(f"📊 MAE with Murray OUT: {murray_out_mae:.2f}")
#         print(f"📊 MAE with Murray IN:  {murray_in_mae:.2f}")
#     except ValueError:
#         print("⚠️ Not enough data points for one of the MURRAY_OUT conditions.")

import pandas as pd
import xgboost as xgb
import joblib
import os
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

# === CONFIG ===
DATA_PATH = "data/features_by_target"
OUTPUT_PATH = "models/xgboost"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Define training targets and file mapping
targets = {
    "PTS": "features_points.csv",
    "REB": "features_rebounds.csv",
    "AST": "features_assists.csv"
}

# Define model parameters (can tweak later)
params = {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1,
    "objective": "reg:squarederror",
    "verbosity": 0,
    "random_state": 42
}

# === MAIN LOOP ===
for target, filename in targets.items():
    print(f"\n🔁 Walk-forward training for {target}...")

    # Load CSV
    df = pd.read_csv(f"{DATA_PATH}/{filename}")
    df = df.dropna().reset_index(drop=True)

    feature_cols = [col for col in df.columns if col not in ["GAME_DATE", "OPPONENT", target]]

    predictions = []
    actuals = []

    # Walk-forward training
    for i in range(5, len(df)):
        train_df = df.iloc[:i]
        val_row = df.iloc[i:i+1]

        X_train = train_df[feature_cols]
        y_train = train_df[target]

        X_val = val_row[feature_cols]
        y_val = val_row[target]

        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)

        pred = model.predict(X_val)[0]
        predictions.append(pred)
        actuals.append(y_val.values[0])

    # Evaluate
    mae = mean_absolute_error(actuals, predictions)
    print(f"✅ MAE (walk-forward) for {target}: {mae:.2f}")

    # Save model and feature columns
    model.fit(df[feature_cols], df[target])  # Final training on full data
    joblib.dump(model, f"{OUTPUT_PATH}/xgb_{target.lower()}.joblib")
    joblib.dump(feature_cols, f"{OUTPUT_PATH}/features_{target.lower()}.joblib")

    # Save feature importance plot
    fig, ax = plt.subplots(figsize=(8, 6))
    xgb.plot_importance(model, importance_type='gain', max_num_features=20, ax=ax)
    plt.title(f"Feature Importance: {target}")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_PATH}/importance_{target.lower()}.png")
    plt.close()

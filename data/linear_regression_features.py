"""
linear_regression_features.py
Builds a simplified feature set for the linear regression model.
Includes rolling averages, season averages, and head-to-head PRA.
"""

import pandas as pd
import os
from collections import OrderedDict
from datetime import datetime

# === Load data ===
df = pd.read_csv(os.path.join("data", "jokic_game_logs.csv"))
gamelogs = {}

# Build structured game data
for _, row in df.iterrows():
    gamelogs[row["GAME_DATE"]] = {
        "points": row["PTS"],
        "rebounds": row["REB"],
        "assists": row["AST"],
        "matchup": row["MATCHUP"]
    }

# Sort chronologically
sorted_gamelogs = OrderedDict(sorted(gamelogs.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")))

# Initialize feature map
features = {}
season_start = datetime.strptime("2024-10-22", "%Y-%m-%d")
pra_history = []
rolling_history = []

for date in sorted_gamelogs:
    dt = datetime.strptime(date, "%Y-%m-%d")
    stats = gamelogs[date]
    current_pra = stats["points"] + stats["rebounds"] + stats["assists"]

    if dt < season_start:
        continue

    # Season avg
    season_avg = sum(pra_history) / len(pra_history) if pra_history else None
    pra_history.append(current_pra)

    # Rolling avg
    rolling_avg = sum(rolling_history[-10:]) / 10 if len(rolling_history) >= 10 else None
    rolling_history.append(current_pra)

    # H2H avg
    opp = stats["matchup"][-3:]
    h2h = [
        g for d, g in gamelogs.items()
        if g["matchup"][-3:] == opp and datetime.strptime(d, "%Y-%m-%d") < dt
    ]
    h2h_avg = (sum(g["points"] + g["rebounds"] + g["assists"] for g in h2h) / len(h2h)) if h2h else None

    features[date] = {
        "GAME_DATE": date,
        "OPPONENT": opp,
        "season_avg_pra": season_avg,
        "rolling_avg_pra": rolling_avg,
        "head2head_avg_pra": h2h_avg,
        "label": current_pra
    }

# Export
out_df = pd.DataFrame.from_dict(features, orient="index")
out_df["GAME_DATE"] = pd.to_datetime(out_df["GAME_DATE"])
out_df = out_df.sort_values("GAME_DATE", ascending=False)
out_df.to_csv("data/jokic_features_24-25.csv", index=False)
print("✅ Exported features to data/jokic_features_24-25.csv")

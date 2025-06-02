"""
build_rolling_opponent_stats.py
Generates 3-game rolling averages for team defensive stats across multiple seasons.
Calculates DEF_RATING and PACE from raw team game logs.
"""

import pandas as pd
import os
from glob import glob

# === CONFIGURATION ===
RAW_LOG_DIR = "data/team_game_logs"
OUTPUT_DIR = "data/opponent_rolling_stats_by_season"
SEASONS = ["2020", "2021", "2022", "2023", "2024"]

ROLLING_STATS = [
    "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT",
    "OREB", "TOV", "MIN"
]

# === Process each season folder ===
for season in SEASONS:
    season_folder = f"{season}-{int(season[-2:]) + 1}"
    folder_path = os.path.join(RAW_LOG_DIR, season_folder)

    if not os.path.exists(folder_path):
        print(f"❌ Missing folder for season: {folder_path}")
        continue

    csv_files = glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        print(f"⚠️ No CSV files found in {folder_path}")
        continue

    all_teams_df = []
    for file in csv_files:
        df = pd.read_csv(file)
        df["TEAM"] = os.path.basename(file).split("_")[0]
        all_teams_df.append(df)

    season_df = pd.concat(all_teams_df, ignore_index=True)
    season_df["DATE"] = pd.to_datetime(season_df["GAME_DATE"])

    missing = [col for col in ROLLING_STATS if col not in season_df.columns]
    if missing:
        print(f"⚠️ Missing required columns in {season_folder}: {missing}")
        continue

    # === Compute rolling averages ===
    season_df = season_df.sort_values(["TEAM", "DATE"])
    rolled = season_df.groupby("TEAM")[ROLLING_STATS].rolling(window=3, min_periods=1).mean().reset_index()
    rolled["DATE"] = season_df["GAME_DATE"].values
    rolled["TEAM"] = season_df["TEAM"].values

    # === Derived stats: DEF_RATING and PACE ===
    possessions = rolled["FGA"] + 0.44 * rolled["FTA"] + rolled["TOV"] - rolled["OREB"]
    rolled["DEF_RATING"] = 100 * rolled["PTS"] / possessions
    rolled["PACE"] = possessions / rolled["MIN"]

    rolled.replace([float("inf"), -float("inf")], pd.NA, inplace=True)

    out_path = os.path.join(OUTPUT_DIR, f"opponent_rolling_stats_{season}-{int(season[-2:]) + 1}.csv")
    rolled.to_csv(out_path, index=False)
    print(f"✅ Saved opponent stats for {season}: {out_path}")

"""
xgboost_features.py
Builds a comprehensive feature set for XGBoost models.
Combines rolling averages, head-to-head stats, rest days, and opponent defensive metrics.
Also includes Murray-absence-based statistics.
"""

import pandas as pd
import os

# === CONFIGURATION ===
JOKIC_LOG = "data/jokic_game_logs.csv"
MURRAY_LOG = "jokic_without_jamal_murray.csv"
OPPONENT_STATS_DIR = "data/opponent_rolling_stats_by_season"
OUTPUT = "data/jokic_features_MULTI_FINAL.csv"
SEASONS = ['2020', '2021', '2022', '2023', '2024']

# === Columns to track ===
STAT_COLS = [
    "PTS", "REB", "AST", "MIN",
    "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
    "FTA", "FTM", "FT_PCT"
]
DEF_STATS = [
    "DEF_RATING", "PACE", "PTS", "REB", "AST",
    "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
    "FTA", "FTM", "FT_PCT"
]

# === Load base data ===
jokic_df = pd.read_csv(JOKIC_LOG)
jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
jokic_df["IS_HOME"] = jokic_df["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
jokic_df["SEASON"] = jokic_df["SEASON"].astype(str)

# Add rest days
for season in jokic_df["SEASON"].unique():
    season_games = jokic_df[jokic_df["SEASON"] == season].sort_values("GAME_DATE")
    jokic_df.loc[season_games.index, "DAYS_RESTED"] = season_games["GAME_DATE"].diff().dt.days

murray_df = pd.read_csv(MURRAY_LOG)
murray_df["GAME_DATE"] = pd.to_datetime(murray_df["GAME_DATE"])

features = []

# === Build features game-by-game ===
for season in SEASONS:
    print(f"\n📅 Processing season: {season}")
    season_df = jokic_df[jokic_df["SEASON"].str.startswith(season)].sort_values("GAME_DATE")
    if season_df.empty:
        continue

    opp_path = os.path.join(OPPONENT_STATS_DIR, f"opponent_rolling_stats_{season}-{int(season[-2:])+1}.csv")
    if not os.path.exists(opp_path):
        print(f"❌ Missing opponent stats for {season}")
        continue
    opp_df = pd.read_csv(opp_path)
    opp_df["DATE"] = pd.to_datetime(opp_df["DATE"], errors="coerce")

    for i in range(1, len(season_df)):
        row = season_df.iloc[i]
        prev_games = season_df.iloc[:i]
        game_date = row["GAME_DATE"]
        opp_abbr = row["MATCHUP"].split()[-1]

        # === Base info ===
        f = {
            "GAME_DATE": game_date,
            "SEASON": season,
            "OPPONENT": opp_abbr,
            "IS_HOME": row["IS_HOME"],
            "DAYS_RESTED": row["DAYS_RESTED"],
            "WON_GAME": int(row["WL"] == "W"),
            "MURRAY_OUT": int(game_date in murray_df["GAME_DATE"].values)
        }

        # === Murray Out stats ===
        if f["MURRAY_OUT"]:
            m_prev = murray_df[murray_df["GAME_DATE"] < game_date]
            for stat in ["PTS", "REB", "AST"]:
                f[f"SEASON_AVG_{stat}_MURRAY_OUT"] = m_prev[stat].mean() if not m_prev.empty else None
        else:
            for stat in ["PTS", "REB", "AST"]:
                f[f"SEASON_AVG_{stat}_MURRAY_OUT"] = None

        # === Season averages ===
        for stat in STAT_COLS:
            f[f"SEASON_AVG_{stat}"] = prev_games[stat].mean()

        # === Rolling averages ===
        for window in [3, 5, 10]:
            for stat in STAT_COLS:
                f[f"ROLL_{window}_{stat}"] = (
                    prev_games[stat].rolling(window).mean().iloc[-1] if len(prev_games) >= window else None
                )

        # === Head-to-head stats ===
        h2h = jokic_df[(jokic_df["MATCHUP"].str.contains(opp_abbr)) & (jokic_df["GAME_DATE"] < game_date)]
        for stat in STAT_COLS:
            f[f"HEAD2HEAD_AVG_{stat}"] = h2h[stat].mean() if not h2h.empty else None

        # === Opponent defense ===
        keyword = opp_df["TEAM"].dropna().unique()[0].split()[0]  # crude match
        opp_recent = opp_df[
            (opp_df["TEAM"].str.contains(keyword, case=False)) & (opp_df["DATE"] < game_date)
        ]
        if not opp_recent.empty:
            latest = opp_recent.sort_values("DATE").iloc[-1]
            for col in DEF_STATS:
                f[f"OPP_{col}"] = latest.get(col, None)
        else:
            for col in DEF_STATS:
                f[f"OPP_{col}"] = None

        features.append(f)

final_df = pd.DataFrame(features)
final_df = final_df.merge(jokic_df[["GAME_DATE", "PTS", "REB", "AST"]], on="GAME_DATE", how="left")
final_df.to_csv(OUTPUT, index=False)
print(f"\n✅ Final feature set saved to: {OUTPUT}")

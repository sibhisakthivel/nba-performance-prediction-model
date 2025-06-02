"""
upcoming_game_features.py
Manually builds a 1-row feature set for Jokic's next game.
Combines rolling, head-to-head, and opponent defense features.
"""

import pandas as pd

# === CONFIG ===
jokic_log_path = "data/jokic_full.csv"
opponent_stats_path = "data/opponent_rolling_stats_24-25.csv"
output_path = "data/jokic_features_next_game.csv"

# Set manually before each game
next_opponent = "LAC"
next_game_date = "2025-04-21"

# === Load data ===
jokic_df = pd.read_csv(jokic_log_path)
opp_df = pd.read_csv(opponent_stats_path)

jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
opp_df["DATE"] = pd.to_datetime(opp_df["DATE"])

jokic_24 = jokic_df[jokic_df["GAME_DATE"] >= pd.Timestamp("2024-10-22")].copy()
jokic_24["IS_HOME"] = jokic_24["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
jokic_24["DAYS_RESTED"] = jokic_24["GAME_DATE"].diff().dt.days.fillna(0).astype(int)

# === Build feature row ===
features = {
    "GAME_DATE": next_game_date,
    "OPPONENT": next_opponent,
    "IS_HOME": 1,        # Set manually
    "DAYS_RESTED": 2     # Set manually
}

stat_cols = [
    "PTS", "REB", "AST", "MIN", "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT"
]

# Averages + rolling + h2h
for stat in stat_cols:
    features[f"SEASON_AVG_{stat}"] = jokic_24[stat].mean()
    features[f"ROLL_3_{stat}"] = jokic_24[stat].rolling(3).mean().iloc[-1]
    features[f"ROLL_5_{stat}"] = jokic_24[stat].rolling(5).mean().iloc[-1]
    features[f"ROLL_10_{stat}"] = jokic_24[stat].rolling(10).mean().iloc[-1]

    h2h = jokic_24[jokic_24["MATCHUP"].str.contains(next_opponent)]
    features[f"HEAD2HEAD_AVG_{stat}"] = h2h[stat].mean() if not h2h.empty else None

# Opponent defense
opp_recent = opp_df[(opp_df["TEAM"] == next_opponent) & (opp_df["DATE"] < pd.to_datetime(next_game_date))]
if not opp_recent.empty:
    latest = opp_recent.sort_values("DATE").iloc[-1]
    for col in [
        "DEF_RATING", "PACE", "PTS", "REB", "AST",
        "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
        "FTA", "FTM", "FT_PCT"
    ]:
        features[f"OPP_{col}"] = latest[col]
else:
    for col in [...]:  # same list as above
        features[f"OPP_{col}"] = None

# === Export ===
pd.DataFrame([features]).to_csv(output_path, index=False)
print(f"✅ Saved next game prediction features to: {output_path}")

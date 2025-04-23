import pandas as pd

# === CONFIG ===
jokic_log_path = "data/jokic_full.csv"
opponent_stats_path = "data/opponent_rolling_stats_24-25.csv"
output_path = "data/jokic_features_next_game.csv"

# === INPUT — UPDATE THESE TWO VALUES ===
next_opponent = "LAC"  # <- set manually
next_game_date = "2025-04-21"  # <- set manually

# === LOAD FILES ===
jokic_df = pd.read_csv(jokic_log_path)
opp_df = pd.read_csv(opponent_stats_path)

jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
opp_df["DATE"] = pd.to_datetime(opp_df["DATE"])

# Filter for 2024–25 season
jokic_24 = jokic_df[jokic_df["GAME_DATE"] >= pd.Timestamp("2024-10-22")].copy()
jokic_24 = jokic_24.sort_values("GAME_DATE").reset_index(drop=True)
jokic_24["IS_HOME"] = jokic_24["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
jokic_24["DAYS_RESTED"] = jokic_24["GAME_DATE"].diff().dt.days.fillna(0).astype(int)

# === CONTEXT FIELDS ===
features = {
    "GAME_DATE": next_game_date,
    "OPPONENT": next_opponent,
    "IS_HOME": 1,         # <- adjust manually
    "DAYS_RESTED": 2      # <- adjust manually
}

# === STAT COLUMNS TO TRACK ===
stat_cols = [
    "PTS", "REB", "AST", "MIN",
    "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT",
    "FTA", "FTM", "FT_PCT"
]

# Compute aggregates
past_games = jokic_24.copy()
h2h_games = past_games[past_games["MATCHUP"].str.contains(next_opponent)]

for stat in stat_cols:
    features[f"SEASON_AVG_{stat}"] = past_games[stat].mean()
    features[f"ROLL_3_{stat}"] = past_games[stat].rolling(3).mean().iloc[-1] if len(past_games) >= 3 else None
    features[f"ROLL_5_{stat}"] = past_games[stat].rolling(5).mean().iloc[-1] if len(past_games) >= 5 else None
    features[f"ROLL_10_{stat}"] = past_games[stat].rolling(10).mean().iloc[-1] if len(past_games) >= 10 else None
    features[f"HEAD2HEAD_AVG_{stat}"] = h2h_games[stat].mean() if not h2h_games.empty else None

# === DEFENSIVE STATS FOR OPPONENT ===
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
    for col in [
        "DEF_RATING", "PACE", "PTS", "REB", "AST",
        "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
        "FTA", "FTM", "FT_PCT"
    ]:
        features[f"OPP_{col}"] = None

# === SAVE OUTPUT ROW ===
pd.DataFrame([features]).to_csv(output_path, index=False)
print(f"✅ Saved next game prediction features to: {output_path}")

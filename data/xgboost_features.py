import pandas as pd

# === CONFIG ===
JOKIC_LOG = "data/jokic_full.csv"
OPPONENT_STATS = "data/opponent_rolling_stats_24-25.csv"
OUTPUT = "data/jokic_features_24-25_FINAL.csv"

# === LOAD ===
jokic_df = pd.read_csv(JOKIC_LOG)
opp_df = pd.read_csv(OPPONENT_STATS)

# Load filtered Jokic logs where Murray did not play
jokic_no_murray_df = pd.read_csv("jokic_without_jamal_murray_2024.csv")
jokic_no_murray_df["GAME_DATE"] = pd.to_datetime(jokic_no_murray_df["GAME_DATE"])

# === PREPROCESSING ===
jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
opp_df["DATE"] = pd.to_datetime(opp_df["DATE"])

# Filter only 2024–25 season (starting from 10/22)
jokic_df = jokic_df[jokic_df["GAME_DATE"] >= pd.Timestamp("2024-10-22")].sort_values("GAME_DATE").reset_index(drop=True)

# Add contextual features
jokic_df["IS_HOME"] = jokic_df["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
jokic_df["DAYS_RESTED"] = jokic_df["GAME_DATE"].diff().dt.days.fillna(0).astype(int)

# === Stat categories to include ===
stat_cols = [
    "PTS", "REB", "AST", "MIN",
    "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT",
    "FTA", "FTM", "FT_PCT"
]

# === Output container ===
feature_rows = []

# Generate rows for every game after 10/22 (starting with 10/24 vs OKC)
for i in range(1, len(jokic_df)):
    row = jokic_df.iloc[i]
    prev_games = jokic_df.iloc[:i]
    game_date = row["GAME_DATE"]
    opponent = row["MATCHUP"].split()[-1]
    h2h_games = prev_games[prev_games["MATCHUP"].str.contains(opponent)]

    features = {
        "GAME_DATE": game_date,
        "OPPONENT": opponent,
        "IS_HOME": row["IS_HOME"],
        "DAYS_RESTED": row["DAYS_RESTED"]
    }

    # === SEASON AVERAGES ===
    for stat in stat_cols:
        features[f"SEASON_AVG_{stat}"] = prev_games[stat].mean()

    # === ROLLING AVERAGES (3, 5, 10) ===
    for window in [3, 5, 10]:
        if len(prev_games) >= window:
            for stat in stat_cols:
                features[f"ROLL_{window}_{stat}"] = prev_games[stat].rolling(window).mean().iloc[-1]
        else:
            for stat in stat_cols:
                features[f"ROLL_{window}_{stat}"] = None

    # === HEAD-TO-HEAD AVERAGES (same season only) ===
    for stat in stat_cols:
        features[f"HEAD2HEAD_AVG_{stat}"] = h2h_games[stat].mean() if not h2h_games.empty else None
        
    # === MURRAY_OUT flag and rolling averages without Murray ===
    game_id = row["Game_ID"]
    game_date = row["GAME_DATE"]
    murray_out = game_id in jokic_no_murray_df["Game_ID"].values
    features["MURRAY_OUT"] = int(murray_out)

    if murray_out:
        # Filter games before this one where Murray was also out
        past_murray_games = jokic_no_murray_df[jokic_no_murray_df["GAME_DATE"] < game_date]
        if not past_murray_games.empty:
            for stat in stat_cols:
                features[f"SEASON_AVG_{stat}_MURRAY_OUT"] = past_murray_games[stat].mean()
        else:
            for stat in stat_cols:
                features[f"SEASON_AVG_{stat}_MURRAY_OUT"] = None
    else:
        for stat in stat_cols:
            features[f"SEASON_AVG_{stat}_MURRAY_OUT"] = None

    # === OPPONENT DEFENSIVE STATS (last known date before game) ===
    opp_recent = opp_df[(opp_df["TEAM"] == opponent) & (opp_df["DATE"] < game_date)]
    if not opp_recent.empty:
        latest_opp = opp_recent.sort_values("DATE").iloc[-1]
        for col in [
            "DEF_RATING", "PACE", "PTS", "REB", "AST",
            "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
            "FTA", "FTM", "FT_PCT"
        ]:

            features[f"OPP_{col}"] = latest_opp[col]
    else:
        for col in [
            "DEF_RATING", "PACE", "PTS", "REB", "AST",
            "FGA", "FGM", "FG_PCT", "FG3A", "FG3M", "FG3_PCT",
            "FTA", "FTM", "FT_PCT"
        ]:
            features[f"OPP_{col}"] = None

    feature_rows.append(features)

# === EXPORT ===
feature_df = pd.DataFrame(feature_rows)

# Re-load full Jokic game log
jokic_raw = pd.read_csv("data/jokic_full.csv")
jokic_raw["GAME_DATE"] = pd.to_datetime(jokic_raw["GAME_DATE"])

# Merge true outcome stats into the feature set
target_cols = ["PTS", "REB", "AST"]
feature_df = feature_df.merge(
    jokic_raw[["GAME_DATE"] + target_cols],
    how="left",
    on="GAME_DATE"
)

feature_df.to_csv(OUTPUT, index=False)
print(f"✅ Feature file saved to: {OUTPUT}")

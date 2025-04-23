# # import pandas as pd
# # from datetime import datetime

# # # === CONFIG ===
# # JOKIC_LOG = "data/jokic_full.csv"
# # OPPONENT_STATS = "data/opponent_rolling_stats_24-25.csv"
# # OUTPUT = "data/jokic_features_24-25.csv"

# # # Load input files
# # jokic_df = pd.read_csv(JOKIC_LOG)
# # opp_df = pd.read_csv(OPPONENT_STATS)

# # # Convert and filter for 2024-25 season
# # jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
# # jokic_df = jokic_df[jokic_df["GAME_DATE"].dt.year >= 2024].sort_values("GAME_DATE").reset_index(drop=True)
# # opp_df["DATE"] = pd.to_datetime(opp_df["DATE"])

# # # Add contextual features
# # jokic_df["IS_HOME"] = jokic_df["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
# # jokic_df["DAYS_RESTED"] = jokic_df["GAME_DATE"].diff().dt.days.fillna(0).astype(int)

# # # Stats to track
# # stat_cols = ["PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
# #              "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT", "TOV"]

# # # Container for feature rows
# # feature_rows = []

# # # Start from index 1 since we can't compute features before the first game
# # for i in range(1, len(jokic_df)):
# #     row = jokic_df.iloc[i]
# #     date = row["GAME_DATE"]
# #     opponent = row["MATCHUP"].split(" ")[-1]
# #     past_games = jokic_df.iloc[:i]
# #     h2h_games = past_games[past_games["MATCHUP"].str.contains(opponent)]

# #     features = {
# #         "GAME_DATE": date,
# #         "OPPONENT": opponent,
# #         "IS_HOME": row["IS_HOME"],
# #         "DAYS_RESTED": row["DAYS_RESTED"]
# #     }

# #     # Season and rolling averages
# #     for stat in stat_cols:
# #         features[f"SEASON_AVG_{stat}"] = past_games[stat].mean()
# #         features[f"ROLL_3_{stat}"] = past_games[stat].rolling(3).mean().iloc[-1]
# #         features[f"ROLL_5_{stat}"] = past_games[stat].rolling(5).mean().iloc[-1]
# #         features[f"ROLL_10_{stat}"] = past_games[stat].rolling(10).mean().iloc[-1]
# #         features[f"HEAD2HEAD_AVG_{stat}"] = h2h_games[stat].mean() if not h2h_games.empty else None

# #     # Merge opponent stats
# #     opp_row = opp_df[(opp_df["DATE"] == date) & (opp_df["TEAM"] == opponent)]
# #     for col in ["DEF_RATING", "PACE", "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
# #                 "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT", "OREB", "TOV"]:
# #         features[f"OPP_{col}"] = opp_row.iloc[0][col] if not opp_row.empty else None

# #     feature_rows.append(features)

# # # Build and save DataFrame
# # feature_df = pd.DataFrame(feature_rows)
# # feature_df.to_csv(OUTPUT, index=False)
# # print(f"✅ Feature file saved to {OUTPUT}")

# import pandas as pd

# # === CONFIG ===
# JOKIC_LOG = "data/jokic_full.csv"
# OPPONENT_STATS = "data/opponent_rolling_stats_24-25.csv"
# OUTPUT = "data/jokic_features_24-25_FINAL.csv"

# # === LOAD ===
# jokic_df = pd.read_csv(JOKIC_LOG)
# opp_df = pd.read_csv(OPPONENT_STATS)

# # === PREPROCESSING ===
# jokic_df["GAME_DATE"] = pd.to_datetime(jokic_df["GAME_DATE"])
# opp_df["DATE"] = pd.to_datetime(opp_df["DATE"])

# # Filter only 2024–25 season (starting from 10/22)
# jokic_df = jokic_df[jokic_df["GAME_DATE"] >= pd.Timestamp("2024-10-22")].sort_values("GAME_DATE").reset_index(drop=True)

# # Add contextual features
# jokic_df["IS_HOME"] = jokic_df["MATCHUP"].apply(lambda x: 0 if "@" in x else 1)
# jokic_df["DAYS_RESTED"] = jokic_df["GAME_DATE"].diff().dt.days.fillna(0).astype(int)

# # Define stat categories to track
# stat_cols = ["PTS", "REB", "AST", "MIN", "FG_PCT", "FG3_PCT", "FT_PCT"]

# # Final output
# feature_rows = []

# # Generate rows starting from game 2 (index 1 = 10/24 vs OKC)
# for i in range(1, len(jokic_df)):
#     row = jokic_df.iloc[i]
#     prev_games = jokic_df.iloc[:i]
#     game_date = row["GAME_DATE"]
#     opponent = row["MATCHUP"].split()[-1]
#     h2h_games = prev_games[prev_games["MATCHUP"].str.contains(opponent)]

#     features = {
#         "GAME_DATE": game_date,
#         "OPPONENT": opponent,
#         "IS_HOME": row["IS_HOME"],
#         "DAYS_RESTED": row["DAYS_RESTED"]
#     }

#     # === SEASON AVERAGES ===
#     for stat in stat_cols:
#         features[f"SEASON_AVG_{stat}"] = prev_games[stat].mean()

#     # === ROLLING AVERAGES ===
#     for window in [3, 5, 10]:
#         if len(prev_games) >= window:
#             for stat in stat_cols:
#                 features[f"ROLL_{window}_{stat}"] = prev_games[stat].rolling(window).mean().iloc[-1]
#         else:
#             for stat in stat_cols:
#                 features[f"ROLL_{window}_{stat}"] = None

#     # === HEAD-TO-HEAD AVERAGES (this season only) ===
#     for stat in stat_cols:
#         features[f"HEAD2HEAD_AVG_{stat}"] = h2h_games[stat].mean() if not h2h_games.empty else None

#     # === DEFENSIVE STATS (from most recent game BEFORE this date) ===
#     opp_recent = opp_df[(opp_df["TEAM"] == opponent) & (opp_df["DATE"] < game_date)]
#     if not opp_recent.empty:
#         latest_opp = opp_recent.sort_values("DATE").iloc[-1]
#         for col in ["DEF_RATING", "PACE", "PTS", "REB", "AST", "FG_PCT", "FG3_PCT", "FT_PCT"]:
#             features[f"OPP_{col}"] = latest_opp[col]
#     else:
#         for col in ["DEF_RATING", "PACE", "PTS", "REB", "AST", "FG_PCT", "FG3_PCT", "FT_PCT"]:
#             features[f"OPP_{col}"] = None

#     feature_rows.append(features)

# # === EXPORT ===
# feature_df = pd.DataFrame(feature_rows)
# feature_df.to_csv(OUTPUT, index=False)
# print(f"✅ Feature file saved to {OUTPUT}")

import pandas as pd

# === CONFIG ===
JOKIC_LOG = "data/jokic_full.csv"
OPPONENT_STATS = "data/opponent_rolling_stats_24-25.csv"
OUTPUT = "data/jokic_features_24-25_FINAL.csv"

# === LOAD ===
jokic_df = pd.read_csv(JOKIC_LOG)
opp_df = pd.read_csv(OPPONENT_STATS)

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
feature_df.to_csv(OUTPUT, index=False)
print(f"✅ Feature file saved to: {OUTPUT}")

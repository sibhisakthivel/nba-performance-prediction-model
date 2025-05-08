import pandas as pd
import os

# === CONFIG ===
input_file = "data/jokic_features_24-25_FINAL.csv"
output_dir = "data/features_by_target"
os.makedirs(output_dir, exist_ok=True)

# === LOAD ===
df = pd.read_csv(input_file)

# === Define base contextual columns ===
context_cols = ["GAME_DATE", "OPPONENT", "IS_HOME", "DAYS_RESTED", "MURRAY_OUT"]

# === Define stat-specific feature sets ===
feature_groups = {
    "POINTS": [
        "SEASON_AVG_PTS", "ROLL_3_PTS", "ROLL_5_PTS", "ROLL_10_PTS",
        "SEASON_AVG_FGA", "SEASON_AVG_FGM", "SEASON_AVG_FG_PCT",
        "ROLL_3_FGA", "ROLL_5_FGA", "ROLL_10_FGA",
        "SEASON_AVG_FTA", "SEASON_AVG_FTM", "SEASON_AVG_FT_PCT",
        "ROLL_3_FTA", "ROLL_5_FTA", "ROLL_10_FTA",
        "HEAD2HEAD_AVG_PTS", "OPP_DEF_RATING", "OPP_PACE", "OPP_PTS",
        "MURRAY_OUT", "SEASON_AVG_PTS_MURRAY_OUT"
    ],
    "REBOUNDS": [
        "SEASON_AVG_REB", "ROLL_3_REB", "ROLL_5_REB", "ROLL_10_REB",
        "HEAD2HEAD_AVG_REB",
        "OPP_REB", "OPP_DEF_RATING", "OPP_PACE",
        "IS_HOME", "DAYS_RESTED",
        "MURRAY_OUT", "SEASON_AVG_REB_MURRAY_OUT"
    ],
    "ASSISTS": [
        "SEASON_AVG_AST", "ROLL_3_AST", "ROLL_5_AST", "ROLL_10_AST",
        "HEAD2HEAD_AVG_AST",
        "SEASON_AVG_MIN",  # more minutes = more assist opportunities
        "SEASON_AVG_FG_PCT",  # teammates converting shots helps assists
        "OPP_AST", "OPP_DEF_RATING", "OPP_PACE",
        "IS_HOME", "DAYS_RESTED",
        "MURRAY_OUT", "SEASON_AVG_AST_MURRAY_OUT"
    ]
}

target_map = {
    "POINTS": "PTS",
    "REBOUNDS": "REB",
    "ASSISTS": "AST"
}

# === Export per target
for target, features in feature_groups.items():
    keep_cols = context_cols + [col for col in features if col in df.columns]
    df_target = df[keep_cols].copy()
    df_target[target_map[target]] = df[target_map[target]]
    df_target.to_csv(f"{output_dir}/features_{target.lower()}.csv", index=False)
    print(f"✅ Saved: features_{target.lower()}.csv")

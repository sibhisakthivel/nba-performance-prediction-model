# # import pandas as pd
# # import os
# # from datetime import datetime

# # # === CONFIG ===
# # input_dir = "data/team_game_logs/2024-25"
# # output_file = "data/opponent_rolling_stats_24-25.csv"
# # date_start = "2024-10-22"
# # date_end = "2025-04-22"

# # # Stat columns used
# # stat_columns = [
# #     "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
# #     "FG3A", "FG3M", "FG3_PCT", "FTM", "FTA", "FT_PCT",
# #     "OREB", "TOV"  # Needed for possessions calc
# # ]

# # # === SCRIPT ===
# # start_date = datetime.strptime(date_start, "%Y-%m-%d")
# # end_date = datetime.strptime(date_end, "%Y-%m-%d")
# # opponent_stats_by_date = {}

# # # Load team logs and assign stats to opponents
# # for file in os.listdir(input_dir):
# #     if file.endswith(".csv") and "2024-25" in file:
# #         df = pd.read_csv(os.path.join(input_dir, file))
# #         for _, row in df.iterrows():
# #             game_date = datetime.strptime(row["GAME_DATE"], "%b %d, %Y")
# #             if not (start_date <= game_date <= end_date):
# #                 continue

# #             opponent = row["MATCHUP"].split(" ")[-1]
# #             stats = {col: row[col] for col in stat_columns if col in row}

# #             if opponent not in opponent_stats_by_date:
# #                 opponent_stats_by_date[opponent] = {}

# #             if game_date not in opponent_stats_by_date[opponent]:
# #                 opponent_stats_by_date[opponent][game_date] = []

# #             opponent_stats_by_date[opponent][game_date].append(stats)

# # # Compute rolling averages
# # rolling_stats = []
# # for team, date_dict in opponent_stats_by_date.items():
# #     sorted_dates = sorted(date_dict.keys())
# #     cumulative = {col: 0 for col in stat_columns}
# #     game_count = 0

# #     for date in sorted_dates:
# #         for game_stats in date_dict[date]:
# #             for col in stat_columns:
# #                 cumulative[col] += game_stats[col]
# #             game_count += 1

# #         avg_stats = {
# #             "DATE": date.strftime("%Y-%m-%d"),
# #             "TEAM": team
# #         }
# #         for col in stat_columns:
# #             avg_stats[col] = cumulative[col] / game_count

# #         # Estimate possessions
# #         possessions = (
# #             avg_stats["FGA"]
# #             + 0.44 * avg_stats["FTA"]
# #             + avg_stats["TOV"]
# #             - avg_stats["OREB"]
# #         )

# #         # Estimate DEF_RATING and PACE
# #         avg_stats["DEF_RATING"] = 100 * avg_stats["PTS"] / possessions if possessions > 0 else None
# #         avg_stats["PACE"] = 48 * possessions / (240 / 5) if possessions > 0 else None

# #         rolling_stats.append(avg_stats)

# # # Build DataFrame
# # df_out = pd.DataFrame(rolling_stats)
# # df_out["DATE"] = pd.to_datetime(df_out["DATE"])
# # df_out = df_out.sort_values(by=["DATE", "PTS"])

# # # Save
# # os.makedirs(os.path.dirname(output_file), exist_ok=True)
# # df_out.to_csv(output_file, index=False)
# # print(f"✅ Saved rolling stats with DEF_RATING and PACE to: {output_file}")

# import os
# import pandas as pd
# from datetime import datetime
# import numpy as np

# # === CONFIG ===
# seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
# output_base_dir = "data/opponent_rolling_stats_by_season"
# os.makedirs(output_base_dir, exist_ok=True)

# # Stat columns to calculate rolling averages for
# stat_columns = [
#     "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
#     "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT",
#     "OREB", "TOV", "MIN"  # ✅ Add these
# ]

# # === SCRIPT ===
# for season in seasons:
#     print(f"\n📅 Processing season: {season}")
#     input_dir = f"data/team_game_logs/{season}"
#     output_file = f"{output_base_dir}/opponent_rolling_stats_{season}.csv"
#     opponent_stats_by_date = {}

#     for file in os.listdir(input_dir):
#         if file.endswith(".csv"):
#             df = pd.read_csv(os.path.join(input_dir, file))
#             for _, row in df.iterrows():
#                 game_date = datetime.strptime(row["GAME_DATE"], "%b %d, %Y")
#                 opponent = row["MATCHUP"].split(" ")[-1]
#                 stats = {col: row[col] for col in stat_columns if col in row}

#                 if opponent not in opponent_stats_by_date:
#                     opponent_stats_by_date[opponent] = {}

#                 if game_date not in opponent_stats_by_date[opponent]:
#                     opponent_stats_by_date[opponent][game_date] = []

#                 opponent_stats_by_date[opponent][game_date].append(stats)

#     # Compute rolling stats
#     rolling_stats = []
#     for team, date_dict in opponent_stats_by_date.items():
#         sorted_dates = sorted(date_dict.keys())
#         cumulative = {col: 0 for col in stat_columns}
#         game_count = 0

#         for date in sorted_dates:
#             for game_stats in date_dict[date]:
#                 for col in stat_columns:
#                     cumulative[col] += game_stats[col]
#                 game_count += 1

#             avg_stats = {col: cumulative[col] / game_count for col in stat_columns}
#             avg_stats["TEAM"] = team
#             avg_stats["DATE"] = date.strftime("%Y-%m-%d")

#             # Derived metrics
#             possessions = avg_stats["FGA"] + 0.44 * avg_stats["FTA"] - avg_stats["OREB"] + avg_stats["TOV"] if "OREB" in avg_stats and "TOV" in avg_stats else None
#             avg_stats["DEF_RATING"] = (avg_stats["PTS"] / possessions * 100) if possessions else np.nan
#             avg_stats["PACE"] = possessions / (avg_stats["MIN"] / 48.0) if possessions and "MIN" in avg_stats else np.nan

#             rolling_stats.append(avg_stats)

#     df_out = pd.DataFrame(rolling_stats)
#     df_out = df_out.sort_values(by=["DATE", "PTS"])
#     df_out.to_csv(output_file, index=False)
#     print(f"✅ Saved: {output_file}")

import pandas as pd
import os
from glob import glob

# === CONFIGURATION ===
RAW_LOG_DIR = "data/team_game_logs"
OUTPUT_DIR = "data/opponent_rolling_stats_by_season"
SEASONS = ["2020", "2021", "2022", "2023", "2024"]

# === COLUMNS TO USE FOR ROLLING STATS ===
ROLLING_STATS = [
    "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT",
    "OREB", "TOV", "MIN"
]

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

    # Read and concatenate all team game logs
    all_teams_df = []
    for file in csv_files:
        df = pd.read_csv(file)
        df["TEAM"] = os.path.basename(file).split("_")[0]  # crude TEAM extraction
        all_teams_df.append(df)

    season_df = pd.concat(all_teams_df, ignore_index=True)
    season_df["DATE"] = pd.to_datetime(season_df["GAME_DATE"])

    # Validate all required columns are present
    missing = [col for col in ROLLING_STATS if col not in season_df.columns]
    if missing:
        print(f"⚠️ Missing required columns in {season_folder}: {missing}")
        continue

    # Sort and compute rolling stats
    season_df = season_df.sort_values(["TEAM", "DATE"])
    rolled = season_df.groupby("TEAM")[ROLLING_STATS].rolling(window=3, min_periods=1).mean().reset_index()
    rolled["DATE"] = season_df["GAME_DATE"].values
    rolled["TEAM"] = season_df["TEAM"].values

    # Compute DEF_RATING and PACE
    possessions = rolled["FGA"] + 0.44 * rolled["FTA"] + rolled["TOV"] - rolled["OREB"]
    rolled["DEF_RATING"] = 100 * rolled["PTS"] / possessions
    rolled["PACE"] = possessions / rolled["MIN"]

    # Clean invalid values
    rolled.replace([float("inf"), -float("inf")], pd.NA, inplace=True)

    # Save
    out_path = os.path.join(OUTPUT_DIR, f"opponent_rolling_stats_{season}-{int(season[-2:]) + 1}.csv")
    rolled.to_csv(out_path, index=False)
    print(f"✅ Saved opponent stats for {season}: {out_path}")

# import pandas as pd
# import os
# from datetime import datetime

# # === CONFIG ===
# input_dir = "data/team_game_logs/2024-25"
# output_file = "data/opponent_rolling_stats_24-25.csv"
# date_start = "2024-10-22"
# date_end = "2025-04-22"

# # Stat columns used
# stat_columns = [
#     "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
#     "FG3A", "FG3M", "FG3_PCT", "FTM", "FTA", "FT_PCT",
#     "OREB", "TOV"  # Needed for possessions calc
# ]

# # === SCRIPT ===
# start_date = datetime.strptime(date_start, "%Y-%m-%d")
# end_date = datetime.strptime(date_end, "%Y-%m-%d")
# opponent_stats_by_date = {}

# # Load team logs and assign stats to opponents
# for file in os.listdir(input_dir):
#     if file.endswith(".csv") and "2024-25" in file:
#         df = pd.read_csv(os.path.join(input_dir, file))
#         for _, row in df.iterrows():
#             game_date = datetime.strptime(row["GAME_DATE"], "%b %d, %Y")
#             if not (start_date <= game_date <= end_date):
#                 continue

#             opponent = row["MATCHUP"].split(" ")[-1]
#             stats = {col: row[col] for col in stat_columns if col in row}

#             if opponent not in opponent_stats_by_date:
#                 opponent_stats_by_date[opponent] = {}

#             if game_date not in opponent_stats_by_date[opponent]:
#                 opponent_stats_by_date[opponent][game_date] = []

#             opponent_stats_by_date[opponent][game_date].append(stats)

# # Compute rolling averages
# rolling_stats = []
# for team, date_dict in opponent_stats_by_date.items():
#     sorted_dates = sorted(date_dict.keys())
#     cumulative = {col: 0 for col in stat_columns}
#     game_count = 0

#     for date in sorted_dates:
#         for game_stats in date_dict[date]:
#             for col in stat_columns:
#                 cumulative[col] += game_stats[col]
#             game_count += 1

#         avg_stats = {
#             "DATE": date.strftime("%Y-%m-%d"),
#             "TEAM": team
#         }
#         for col in stat_columns:
#             avg_stats[col] = cumulative[col] / game_count

#         # Estimate possessions
#         possessions = (
#             avg_stats["FGA"]
#             + 0.44 * avg_stats["FTA"]
#             + avg_stats["TOV"]
#             - avg_stats["OREB"]
#         )

#         # Estimate DEF_RATING and PACE
#         avg_stats["DEF_RATING"] = 100 * avg_stats["PTS"] / possessions if possessions > 0 else None
#         avg_stats["PACE"] = 48 * possessions / (240 / 5) if possessions > 0 else None

#         rolling_stats.append(avg_stats)

# # Build DataFrame
# df_out = pd.DataFrame(rolling_stats)
# df_out["DATE"] = pd.to_datetime(df_out["DATE"])
# df_out = df_out.sort_values(by=["DATE", "PTS"])

# # Save
# os.makedirs(os.path.dirname(output_file), exist_ok=True)
# df_out.to_csv(output_file, index=False)
# print(f"✅ Saved rolling stats with DEF_RATING and PACE to: {output_file}")

import os
import pandas as pd
from datetime import datetime
import numpy as np

# === CONFIG ===
seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
output_base_dir = "data/opponent_rolling_stats_by_season"
os.makedirs(output_base_dir, exist_ok=True)

# Stat columns to calculate rolling averages for
stat_columns = [
    "PTS", "REB", "AST", "FGA", "FGM", "FG_PCT",
    "FG3A", "FG3M", "FG3_PCT", "FTA", "FTM", "FT_PCT"
]

# === SCRIPT ===
for season in seasons:
    print(f"\n📅 Processing season: {season}")
    input_dir = f"data/team_game_logs/{season}"
    output_file = f"{output_base_dir}/opponent_rolling_stats_{season}.csv"
    opponent_stats_by_date = {}

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_dir, file))
            for _, row in df.iterrows():
                game_date = datetime.strptime(row["GAME_DATE"], "%b %d, %Y")
                opponent = row["MATCHUP"].split(" ")[-1]
                stats = {col: row[col] for col in stat_columns if col in row}

                if opponent not in opponent_stats_by_date:
                    opponent_stats_by_date[opponent] = {}

                if game_date not in opponent_stats_by_date[opponent]:
                    opponent_stats_by_date[opponent][game_date] = []

                opponent_stats_by_date[opponent][game_date].append(stats)

    # Compute rolling stats
    rolling_stats = []
    for team, date_dict in opponent_stats_by_date.items():
        sorted_dates = sorted(date_dict.keys())
        cumulative = {col: 0 for col in stat_columns}
        game_count = 0

        for date in sorted_dates:
            for game_stats in date_dict[date]:
                for col in stat_columns:
                    cumulative[col] += game_stats[col]
                game_count += 1

            avg_stats = {col: cumulative[col] / game_count for col in stat_columns}
            avg_stats["TEAM"] = team
            avg_stats["DATE"] = date.strftime("%Y-%m-%d")

            # Derived metrics
            possessions = avg_stats["FGA"] + 0.44 * avg_stats["FTA"] - avg_stats["OREB"] + avg_stats["TOV"] if "OREB" in avg_stats and "TOV" in avg_stats else None
            avg_stats["DEF_RATING"] = (avg_stats["PTS"] / possessions * 100) if possessions else np.nan
            avg_stats["PACE"] = possessions / (avg_stats["MIN"] / 48.0) if possessions and "MIN" in avg_stats else np.nan

            rolling_stats.append(avg_stats)

    df_out = pd.DataFrame(rolling_stats)
    df_out = df_out.sort_values(by=["DATE", "PTS"])
    df_out.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")

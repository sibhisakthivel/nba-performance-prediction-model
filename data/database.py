# import pandas as pd
# import os
# from collections import OrderedDict
# from datetime import datetime

# path = os.path.join("data", "jokic_game_logs.csv")
# df = pd.read_csv(path)

# # Initialize dictionary
# gamelogs = {}

# # Loop through each game
# for _, row in df.iterrows():
#     game_date = row["GAME_DATE"]

#     # Basic features from box score
#     points = row["PTS"]
#     rebounds = row["REB"]
#     assists = row["AST"]
#     minutes = row["MIN"]
#     fga = row["FGA"]
#     fgm = row["FGM"]
#     fta = row["FTA"]
#     ftm = row["FTM"]
#     win = 1 if row["WL"] == "W" else 0
#     home = 1 if "vs" in row["MATCHUP"] else 0
#     opponent = row["MATCHUP"][-3:]

#     # Store in hashmap by game date
#     gamelogs[game_date] = {
#         "points": points,
#         "rebounds": rebounds,
#         "assists": assists,
#         "minutes": minutes,
#         "fga": fga,
#         "fgm": fgm,
#         "fta": fta,
#         "ftm": ftm,
#         "win": win,
#         "home": home,
#         "opponent": opponent
#     }

# # # Print Game Logs
# # for date, stats in list(gamelogs.items())[:1]:
# #     print(f"{date}: {stats}")

# sorted_gamelogs = OrderedDict(
#     sorted(gamelogs.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
# )

# feature_map = {}

# for game_date in sorted_gamelogs.keys():
#     feature_map[game_date] = {
#         "season_avg_pra": None,
#         "rolling_avg_pra": None,
#         "head2head_avg_pra": None,
#         "label": None  # we'll use this for actual PRA from the game
#     }

# # Sort game dates chronologically
# sorted_game_dates = sorted(feature_map.keys(), key=lambda date: datetime.strptime(date, "%Y-%m-%d"))

# # Define current season start date
# season_start = datetime.strptime("2024-10-22", "%Y-%m-%d")

# season_pra_history = []
# print("\n🧠 Tracking Season PRA Calculation (First 5 games of CURRENT season only):\n")

# count = 0
# for game_date in sorted_game_dates:
#     game_dt = datetime.strptime(game_date, "%Y-%m-%d")

#     # Skip any games before the current season
#     if game_dt < season_start:
#         continue

#     # Compute season average only from games in the current season
#     if len(season_pra_history) == 0:
#         feature_map[game_date]["season_avg_pra"] = None
#         avg_display = "None"
#     else:
#         avg = sum(season_pra_history) / len(season_pra_history)
#         feature_map[game_date]["season_avg_pra"] = avg
#         avg_display = f"{avg:.2f}"

#     # Calculate and store actual PRA
#     stats = gamelogs[game_date]
#     current_pra = stats["points"] + stats["rebounds"] + stats["assists"]
#     feature_map[game_date]["label"] = current_pra
#     season_pra_history.append(current_pra)

#     # Only show debug for the first 5 games in this season
#     if count < 5:
#         print(f"📅 {game_date} | Season Avg PRA: {avg_display} | Current PRA: {current_pra} | History: {season_pra_history}")
#         count += 1

# # === Rolling 10 Average PRA === #
# rolling_pra_window = []

# print("\n🔁 Tracking Rolling 10-Game PRA (First 5 of 2024–25 season only):\n")

# count = 0
# for game_date in sorted_game_dates:
#     game_dt = datetime.strptime(game_date, "%Y-%m-%d")

#     # Skip games before current season
#     if game_dt < season_start:
#         continue

#     # Compute rolling average if at least 10 prior games
#     if len(rolling_pra_window) >= 10:
#         rolling_avg = sum(rolling_pra_window[-10:]) / 10
#         feature_map[game_date]["rolling_avg_pra"] = rolling_avg
#     else:
#         feature_map[game_date]["rolling_avg_pra"] = None

#     # Calculate current PRA and add to history
#     stats = gamelogs[game_date]
#     pra = stats["points"] + stats["rebounds"] + stats["assists"]
#     rolling_pra_window.append(pra)

#     # Debug print for first 5 games in current season
#     if count < 5:
#         avg_display = "None" if feature_map[game_date]["rolling_avg_pra"] is None else f"{feature_map[game_date]['rolling_avg_pra']:.2f}"
#         print(f"📅 {game_date} | Rolling Avg PRA: {avg_display} | Current PRA: {pra} | History: {rolling_pra_window}")
#         count += 1
        
# # === Head-to-Head PRA vs Timberwolves (only) ===
# h2h_path = os.path.join("data", "jokic_vs_timberwolves_2024.csv")
# h2h_df = pd.read_csv(h2h_path)

# # Parse and sort the H2H Timberwolves games by date
# h2h_df["GAME_DATE"] = pd.to_datetime(h2h_df["GAME_DATE"])
# h2h_df = h2h_df.sort_values("GAME_DATE")

# # Track prior Timberwolves games
# h2h_game_history = []

# for game_date in feature_map:
#     current_date = pd.to_datetime(game_date)

#     # Filter out only past Timberwolves games before this date
#     past_games = h2h_df[h2h_df["GAME_DATE"] < current_date]

#     if not past_games.empty:
#         total_pra = (past_games["PTS"] + past_games["REB"] + past_games["AST"]).sum()
#         count = past_games.shape[0]
#         avg = total_pra / count
#         feature_map[game_date]["head2head_avg_pra"] = avg
#     else:
#         feature_map[game_date]["head2head_avg_pra"] = None
        
# # # Print Game Logs
# # for date, stats in list(gamelogs.items())[:1]:
# #     print(f"{date}: {stats}")

# # # Sort by most recent
# # recent_games = sorted(feature_map.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"), reverse=True)

# # print("\n📊 Most Recent 5 Games – Features & Label:")
# # for date, features in recent_games[:5]:
# #     opponent = gamelogs[date]["opponent"]
# #     print(f"\n📅 {date} vs {opponent}")
# #     print(f"  🧮 Season Avg PRA:     {features['season_avg_pra']}")
# #     print(f"  🔁 Rolling 10 PRA:     {features['rolling_avg_pra']}")
# #     print(f"  🆚 Timberwolves Avg:   {features['head2head_avg_pra']}")
# #     print(f"  🎯 Actual PRA (Label): {features['label']}")

# # Build dataframe from feature_map
# export_rows = []

# for game_date in feature_map:
#     row = feature_map[game_date].copy()
#     row["GAME_DATE"] = game_date
#     row["OPPONENT"] = gamelogs[game_date]["opponent"]
#     export_rows.append(row)

# # Create DataFrame
# df = pd.DataFrame(export_rows)

# # Convert GAME_DATE to datetime
# df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

# # Filter for 2024–25 season
# df = df[df["GAME_DATE"] >= pd.to_datetime("2024-10-22")]

# # Sort by most recent game first
# df = df.sort_values("GAME_DATE", ascending=False)

# # Reorder columns
# ordered_columns = [
#     "GAME_DATE",
#     "OPPONENT",
#     "season_avg_pra",
#     "rolling_avg_pra",
#     "head2head_avg_pra",
#     "label"
# ]
# df = df[ordered_columns]
# df = df.round(2)

# # Save to CSV
# output_path = os.path.join("data", "jokic_features_24-25.csv")
# df.to_csv(output_path, index=False)

# print(f"\n✅ Exported corrected 2024–25 season data to: {output_path}")
# print(f"🗂️  Games included: {df.shape[0]}")

import pandas as pd
import os
from collections import OrderedDict
from datetime import datetime

# === Load Jokic's full game log ===
path = os.path.join("data", "jokic_game_logs.csv")
df = pd.read_csv(path)

# Build game logs hash
gamelogs = {}
for _, row in df.iterrows():
    game_date = row["GAME_DATE"]
    gamelogs[game_date] = {
        "points": row["PTS"],
        "rebounds": row["REB"],
        "assists": row["AST"],
        "minutes": row["MIN"],
        "fga": row["FGA"],
        "fgm": row["FGM"],
        "fta": row["FTA"],
        "ftm": row["FTM"],
        "win": 1 if row["WL"] == "W" else 0,
        "home": 1 if "vs" in row["MATCHUP"] else 0,
        "opponent": row["MATCHUP"][-3:]
    }

# Initialize feature map
sorted_gamelogs = OrderedDict(
    sorted(gamelogs.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
)
feature_map = {}
for game_date in sorted_gamelogs.keys():
    feature_map[game_date] = {
        "season_avg_pra": None,
        "rolling_avg_pra": None,
        "head2head_avg_pra": None,
        "label": None
    }

# Sort game dates
sorted_game_dates = sorted(feature_map.keys(), key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
season_start = datetime.strptime("2024-10-22", "%Y-%m-%d")

# === Season Average PRA ===
season_pra_history = []
print("\n🧠 Tracking Season PRA Calculation (First 5 games of CURRENT season only):\n")
count = 0
for game_date in sorted_game_dates:
    game_dt = datetime.strptime(game_date, "%Y-%m-%d")
    if game_dt < season_start:
        continue

    if len(season_pra_history) == 0:
        feature_map[game_date]["season_avg_pra"] = None
        avg_display = "None"
    else:
        avg = sum(season_pra_history) / len(season_pra_history)
        feature_map[game_date]["season_avg_pra"] = avg
        avg_display = f"{avg:.2f}"

    stats = gamelogs[game_date]
    current_pra = stats["points"] + stats["rebounds"] + stats["assists"]
    feature_map[game_date]["label"] = current_pra
    season_pra_history.append(current_pra)

    if count < 5:
        print(f"📅 {game_date} | Season Avg PRA: {avg_display} | Current PRA: {current_pra} | History: {season_pra_history}")
        count += 1

# === Rolling 10-Game Average PRA ===
rolling_pra_window = []
print("\n🔁 Tracking Rolling 10-Game PRA (First 5 of 2024–25 season only):\n")
count = 0
for game_date in sorted_game_dates:
    game_dt = datetime.strptime(game_date, "%Y-%m-%d")
    if game_dt < season_start:
        continue

    if len(rolling_pra_window) >= 10:
        rolling_avg = sum(rolling_pra_window[-10:]) / 10
        feature_map[game_date]["rolling_avg_pra"] = rolling_avg
    else:
        feature_map[game_date]["rolling_avg_pra"] = None

    stats = gamelogs[game_date]
    pra = stats["points"] + stats["rebounds"] + stats["assists"]
    rolling_pra_window.append(pra)

    if count < 5:
        avg_display = "None" if feature_map[game_date]["rolling_avg_pra"] is None else f"{feature_map[game_date]['rolling_avg_pra']:.2f}"
        print(f"📅 {game_date} | Rolling Avg PRA: {avg_display} | Current PRA: {pra} | History: {rolling_pra_window}")
        count += 1

# === Dynamic Head-to-Head PRA vs Actual Opponent ===
print("\n📊 Calculating Head-to-Head PRA vs each opponent...\n")
for game_date in sorted_game_dates:
    game_dt = datetime.strptime(game_date, "%Y-%m-%d")
    if game_dt < season_start:
        continue

    opponent = gamelogs[game_date]["opponent"]

    # Filter previous games vs same opponent
    recent_year_cutoff = game_dt.year - 2  # includes current and 2 previous seasons

    h2h_past_games = [
        stats for date, stats in gamelogs.items()
        if (
            stats["opponent"] == opponent and
            datetime.strptime(date, "%Y-%m-%d") < game_dt and
            datetime.strptime(date, "%Y-%m-%d").year >= recent_year_cutoff
        )
    ]

    if h2h_past_games:
        total_pra = sum(stats["points"] + stats["rebounds"] + stats["assists"] for stats in h2h_past_games)
        avg_pra = total_pra / len(h2h_past_games)
        feature_map[game_date]["head2head_avg_pra"] = avg_pra
    else:
        feature_map[game_date]["head2head_avg_pra"] = None

# === Export to CSV ===
export_rows = []
for game_date in feature_map:
    row = feature_map[game_date].copy()
    row["GAME_DATE"] = game_date
    row["OPPONENT"] = gamelogs[game_date]["opponent"]
    export_rows.append(row)

df = pd.DataFrame(export_rows)
df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
df = df[df["GAME_DATE"] >= pd.to_datetime("2024-10-22")]
df = df.sort_values("GAME_DATE", ascending=False)

ordered_columns = [
    "GAME_DATE",
    "OPPONENT",
    "season_avg_pra",
    "rolling_avg_pra",
    "head2head_avg_pra",
    "label"
]
df = df[ordered_columns]

output_path = os.path.join("data", "jokic_features_24-25.csv")
df.to_csv(output_path, index=False)

print(f"\n✅ Exported corrected 2024–25 season data to: {output_path}")
print(f"🗂️  Games included: {df.shape[0]}")

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

import pandas as pd
import os
from collections import OrderedDict
from datetime import datetime

path = os.path.join("data", "jokic_game_logs.csv")
df = pd.read_csv(path)

# Initialize dictionary
gamelogs = {}

# Loop through each game
for _, row in df.iterrows():
    game_date = row["GAME_DATE"]

    # Basic features from box score
    points = row["PTS"]
    rebounds = row["REB"]
    assists = row["AST"]
    minutes = row["MIN"]
    fga = row["FGA"]
    fgm = row["FGM"]
    fta = row["FTA"]
    ftm = row["FTM"]
    win = 1 if row["WL"] == "W" else 0
    home = 1 if "vs" in row["MATCHUP"] else 0
    opponent = row["MATCHUP"][-3:]

    # Store in hashmap by game date
    gamelogs[game_date] = {
        "points": points,
        "rebounds": rebounds,
        "assists": assists,
        "minutes": minutes,
        "fga": fga,
        "fgm": fgm,
        "fta": fta,
        "ftm": ftm,
        "win": win,
        "home": home,
        "opponent": opponent
    }

# Example: print 1 row
for date, stats in list(gamelogs.items())[:1]:
    print(f"{date}: {stats}")

# === Season Average PRA ===
pra_total = 0
game_count = 0

for stats in gamelogs.values():
    pra = stats["points"] + stats["rebounds"] + stats["assists"]
    pra_total += pra
    game_count += 1

szn_avg = pra_total / game_count if game_count > 0 else 0
print(f"✅ Season average PRA: {szn_avg:.2f}")

# === Last 10 Games Rolling Average PRA ===
sorted_gamelogs = OrderedDict(
    sorted(gamelogs.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
)

rolling_10_avg = {}
pra_history = []

for game_date, stats in sorted_gamelogs.items():
    pra = stats["points"] + stats["rebounds"] + stats["assists"]

    if len(pra_history) >= 1:
        avg = sum(pra_history[-10:]) / len(pra_history[-10:])
        rolling_10_avg[game_date] = avg
    else:
        rolling_10_avg[game_date] = None  # not enough data yet

    pra_history.append(pra)

print("\n✅ Rolling 10-game PRA average:")
for date in list(rolling_10_avg.keys())[-1:]:
    print(f"🏀{date}: {rolling_10_avg[date]}\n")
    
# === Head to Head Average PRA ===
h2h_path = os.path.join("data", "jokic_vs_timberwolves_2024.csv")
h2h_df = pd.read_csv(h2h_path)

# Sum PRA across all Timberwolves games
h2h_total = 0
h2h_count = 0

for _, row in h2h_df.iterrows():
    pra = row["PTS"] + row["REB"] + row["AST"]
    h2h_total += pra
    h2h_count += 1

h2h_avg = h2h_total / h2h_count if h2h_count > 0 else 0
print(f"✅ Head-to-head PRA vs Timberwolves: {h2h_avg:.2f}\n")

feature_map = {
    "Season Average PRA": szn_avg,
    "Rolling Average PRA": list(rolling_10_avg.values())[-1],
    "Head2Head Average PRA": h2h_avg
}

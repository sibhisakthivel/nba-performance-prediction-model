import pandas as pd
import os

path = os.path.join("data", "jokic_game_logs.csv")
df = pd.read_csv(path)

# Load cleaned Jokic data
# df = pd.read_csv("jokic_game_logs.csv")

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

# 

"""
jokic_gamelogs_without_teammate.py - Pulls Jokic game logs with teammate filter.
Removes all games where a selected teammate (e.g., Jamal Murray) played.
"""

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# === Prompt for teammate name to exclude ===
exclude_name = input("Enter the name of the teammate to exclude (e.g., Jamal Murray): ")

# === Step 1: Get player IDs ===
jokic_id = players.find_players_by_full_name("Nikola Jokic")[0]['id']
exclude_player = players.find_players_by_full_name(exclude_name)

if not exclude_player:
    print(f"No player found for '{exclude_name}'.")
    exit()

exclude_id = exclude_player[0]['id']

# === Step 2: Pull logs for Jokic and excluded teammate ===
seasons = ['2020', '2021', '2022', '2023', '2024']
jokic_logs = []
exclude_logs = []

for season in seasons:
    print(f"Fetching logs for {season}...")
    jokic_logs.append(
        playergamelog.PlayerGameLog(player_id=jokic_id, season=season, season_type_all_star='Regular Season').get_data_frames()[0]
    )
    exclude_logs.append(
        playergamelog.PlayerGameLog(player_id=exclude_id, season=season, season_type_all_star='Regular Season').get_data_frames()[0]
    )

# === Step 3: Filter games where teammate did not play ===
jokic_df = pd.concat(jokic_logs)
exclude_df = pd.concat(exclude_logs)

exclude_game_ids = set(exclude_df['Game_ID'])
filtered_df = jokic_df[~jokic_df['Game_ID'].isin(exclude_game_ids)]

# === Step 4: Sort and save ===
filtered_df['GAME_DATE'] = pd.to_datetime(filtered_df['GAME_DATE'])
filtered_df = filtered_df.sort_values(by="GAME_DATE", ascending=False)

filename = f"jokic_without_{exclude_name.lower().replace(' ', '_')}.csv"
filtered_df.to_csv(filename, index=False)
print(f"✅ Saved file: {filename}")

import os
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Step 1: Get Jokic's Player ID
jokic = players.find_players_by_full_name("Nikola Jokic")[0]
jokic_id = jokic['id']

# Step 2: Pull game logs across multiple seasons
all_logs = []
seasons = ['2024', '2023', '2022', '2021', '2020', '2019']  # Add/remove as needed

for season in seasons:
    print(f"Fetching {season} Regular Season...")
    reg_log = playergamelog.PlayerGameLog(player_id=jokic_id, season=season, season_type_all_star='Regular Season')
    reg_df = reg_log.get_data_frames()[0]
    reg_df['SEASON'] = season
    reg_df['SEASON_TYPE'] = 'Regular Season'
    all_logs.append(reg_df)

    print(f"Fetching {season} Playoffs...")
    po_log = playergamelog.PlayerGameLog(player_id=jokic_id, season=season, season_type_all_star='Playoffs')
    po_df = po_log.get_data_frames()[0]
    po_df['SEASON'] = season
    po_df['SEASON_TYPE'] = 'Playoffs'
    all_logs.append(po_df)

# Step 3: Combine logs
full_df = pd.concat(all_logs, ignore_index=True)

# Step 4: Convert and sort by GAME_DATE (most recent first)
full_df['GAME_DATE'] = pd.to_datetime(full_df['GAME_DATE'])
full_df = full_df.sort_values(by='GAME_DATE', ascending=False)

# Step 5: Save to CSV
output_path = os.path.join("data", "jokic_game_logs.csv")
full_df.to_csv(output_path, index=False)
print(f"✅ Saved Jokic game logs to {output_path}")
print("Saved Jokic game logs (most recent first).")

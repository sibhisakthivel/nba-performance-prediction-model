from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamGameLog
import pandas as pd
import os
import time

# Create output directory
output_dir = 'data/team_game_logs/2024-25'
os.makedirs(output_dir, exist_ok=True)

# List all seasons to collect
seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']

# Get NBA teams
nba_teams = teams.get_teams()

# Loop through each team and season
for season in seasons:
    output_dir = f"data/team_game_logs/{season}"
    os.makedirs(output_dir, exist_ok=True)

    for team in nba_teams:
        team_id = team['id']
        team_name = team['full_name'].replace(" ", "_")

        try:
            regular_df = TeamGameLog(team_id=team_id, season=season, season_type_all_star='Regular Season').get_data_frames()[0]
            playoff_df = TeamGameLog(team_id=team_id, season=season, season_type_all_star='Playoffs').get_data_frames()[0]

            frames = [regular_df, playoff_df]
            frames = [f for f in frames if not f.empty]
            combined_df = pd.concat(frames).sort_values(by="GAME_DATE")

            file_path = os.path.join(output_dir, f"{team_name}_{season}.csv")
            combined_df.to_csv(file_path, index=False)
            print(f"✅ Saved: {file_path} (Regular + Playoffs)")

            time.sleep(1)

        except Exception as e:
            print(f"❌ Error scraping {team_name} ({season}): {e}")

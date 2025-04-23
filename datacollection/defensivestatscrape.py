# from nba_api.stats.static import teams
# from nba_api.stats.endpoints import TeamGameLog
# import pandas as pd
# import os
# import time

# # Create output directory
# output_dir = 'data/team_game_logs/2024-25'
# os.makedirs(output_dir, exist_ok=True)

# # Set the current season (format must match NBA API: e.g., '2024-25')
# season = '2024-25'

# # Get all NBA team metadata
# nba_teams = teams.get_teams()

# # Loop through each team
# for team in nba_teams:
#     team_id = team['id']
#     team_name = team['full_name'].replace(" ", "_")

#     try:
#         # Scrape team game logs
#         game_log = TeamGameLog(team_id=team_id, season=season)
#         df = game_log.get_data_frames()[0]

#         # Save to CSV
#         file_path = os.path.join(output_dir, f"{team_name}_{season}.csv")
#         df.to_csv(file_path, index=False)
#         print(f"Saved: {file_path}")

#         time.sleep(1)  # Gentle delay to avoid rate limiting

#     except Exception as e:
#         print(f"Error scraping {team_name}: {e}")

from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamGameLog
import pandas as pd
import os
import time

# Create output directory
output_dir = 'data/team_game_logs/2024-25'
os.makedirs(output_dir, exist_ok=True)

# Set the current season
season = '2024-25'

# Get NBA teams
nba_teams = teams.get_teams()

# Loop through each team
for team in nba_teams:
    team_id = team['id']
    team_name = team['full_name'].replace(" ", "_")

    try:
        # Scrape REGULAR SEASON games
        regular_df = TeamGameLog(team_id=team_id, season=season, season_type_all_star='Regular Season').get_data_frames()[0]

        # Scrape PLAYOFF games
        playoff_df = TeamGameLog(team_id=team_id, season=season, season_type_all_star='Playoffs').get_data_frames()[0]

        # Combine both
        frames = [regular_df, playoff_df]
        frames = [f for f in frames if not f.empty]
        combined_df = pd.concat(frames).sort_values(by="GAME_DATE")

        # Save to CSV
        file_path = os.path.join(output_dir, f"{team_name}_{season}.csv")
        combined_df.to_csv(file_path, index=False)
        print(f"✅ Saved: {file_path} (Regular + Playoffs)")

        time.sleep(1)  # avoid rate limits

    except Exception as e:
        print(f"❌ Error scraping {team_name}: {e}")

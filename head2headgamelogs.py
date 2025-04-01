from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Prompt for team name
target_team = input("Enter team name to filter head-to-head matchups (e.g., Warriors): ").lower()

# Get Jokic's player ID
jokic_id = players.find_players_by_full_name("Nikola Jokic")[0]['id']

# Step 1: Get Jokic’s game log (edit season list if needed)
season = '2024'
log = playergamelog.PlayerGameLog(player_id=jokic_id, season=season, season_type_all_star='Regular Season')
jokic_df = log.get_data_frames()[0]

# Step 2: Filter for matchups against the target team
# The MATCHUP field looks like "DEN vs GSW" or "DEN @ GSW"
# We check if the team abbreviation (GSW) appears in MATCHUP

# Build lookup of NBA team names → abbreviations
team_list = teams.get_teams()
team_abbr = None
for t in team_list:
    if target_team in t['full_name'].lower() or target_team in t['nickname'].lower():
        team_abbr = t['abbreviation']
        break

if not team_abbr:
    print(f"No abbreviation found for team: {target_team}")
    exit()

# Step 3: Filter by MATCHUP string containing the target team abbreviation
jokic_vs_team = jokic_df[jokic_df['MATCHUP'].str.contains(team_abbr)]

# Step 4: Sort and save
jokic_vs_team['GAME_DATE'] = pd.to_datetime(jokic_vs_team['GAME_DATE'])
jokic_vs_team = jokic_vs_team.sort_values(by="GAME_DATE", ascending=False)

filename = f"jokic_vs_{target_team.lower().replace(' ', '_')}_2024.csv"
jokic_vs_team.to_csv(filename, index=False)
print(f"Saved filtered head-to-head file: {filename}")

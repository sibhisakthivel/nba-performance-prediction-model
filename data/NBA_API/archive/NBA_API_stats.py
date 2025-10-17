from nba_api.stats.endpoints import PlayerGameLog, CumeStatsPlayer
import pandas as pd
import time

# Parameters
player_id = '203999'  # Nikola Jokic
season = '2023-24'
season_type = 'Regular Season'

# Step 1: Get game IDs from PlayerGameLog
print(f"🔁 Fetching game logs for player {player_id} ({season})...")
time.sleep(1)
game_log = PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type)
game_df = game_log.get_data_frames()[0]
game_ids = game_df['Game_ID'].tolist()

# Step 2: Call CumeStatsPlayer
print(f"🔁 Fetching CumeStatsPlayer for {len(game_ids)} games...")
time.sleep(1)
cume_stats = CumeStatsPlayer(
    player_id=player_id,
    game_ids=game_ids,
    season=season,
    season_type_all_star=season_type
)

# Step 3: Save data to CSV
df = cume_stats.get_data_frames()[0]
filename = f'CumeStatsPlayer_{player_id}_{season}.csv'
df.to_csv(filename, index=False)
print(f"✅ CSV saved as {filename}")

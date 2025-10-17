import os
import time
import pandas as pd
from nba_api.stats.endpoints import LeagueGameLog

def save_league_game_logs(start_season: int, end_season: int, season_type: str = "Regular Season", save_dir: str = "data/LeagueGameLogs", sleep_time: float = 1.5):
    """
    Downloads and saves LeagueGameLog_T data for each NBA season in the range.

    Args:
        start_season (int): Starting season year (e.g., 2018 for 2018-19).
        end_season (int): Ending season year (inclusive).
        season_type (str): "Regular Season" or "Playoffs".
        save_dir (str): Folder where CSVs will be saved.
        sleep_time (float): Delay between API calls to avoid rate-limiting.
    """
    os.makedirs(save_dir, exist_ok=True)

    for season_start in range(start_season, end_season + 1):
        season_str = f"{season_start}-{str(season_start + 1)[-2:]}"
        print(f"Fetching LeagueGameLog_T for {season_str}...")

        try:
            logs = LeagueGameLog(
                season=season_str,
                season_type_all_star=season_type,
                player_or_team_abbreviation='T'
            )
            df = logs.get_data_frames()[0]
            filename = f"TeamGameLogs_{season_str.replace('-', '_')}.csv"
            filepath = os.path.join(save_dir, filename)
            df.to_csv(filepath, index=False)
            print(f"Saved: {filepath}")
        except Exception as e:
            print(f"Failed to fetch {season_str}: {e}")

        time.sleep(sleep_time)

# Example usage
save_league_game_logs(start_season=2021, end_season=2024)

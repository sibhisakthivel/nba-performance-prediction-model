import os
import time
import pandas as pd
from nba_api.stats.endpoints import BoxScoreAdvancedV3, LeagueGameLog

'''
In progress: calculate weighted player pace averages -> team pace
'''

# Convert "MM:SS" to float minutes
def time_str_to_float(min_str):
    try:
        minutes, seconds = map(int, min_str.split(":"))
        return minutes + seconds / 60
    except:
        return 0.0

def collect_and_save_team_advanced_stats(output_csv="data/processed/team_advanced_stats_weighted.csv", sleep_time=1.5):
    print("📥 Fetching GAME_IDs and GAME_DATES from LeagueGameLog...")
    log = LeagueGameLog(
        season="2024-25",
        season_type_all_star="Regular Season",
        player_or_team_abbreviation="T"
    )
    log_df = log.get_data_frames()[0][["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_DATE"]]
    log_df["GAME_DATE"] = pd.to_datetime(log_df["GAME_DATE"])
    game_team_pairs = log_df.drop_duplicates(subset=["GAME_ID", "TEAM_ID"])
    game_ids = game_team_pairs["GAME_ID"].drop_duplicates().tolist()

    print(f"✅ Found {len(game_ids)} unique GAME_IDs\n")
    records = []

    for i, game_id in enumerate(game_ids):
        try:
            print(f"🔄 Fetching game {i+1}/{len(game_ids)}: {game_id}")
            bs = BoxScoreAdvancedV3(game_id=game_id)
            df = bs.player_stats.get_data_frame()

            if df.empty or "minutes" not in df.columns:
                print(f"⚠️ Missing 'minutes' column or no data for game {game_id}. Skipping.")
                continue

            df["minutes_float"] = df["minutes"].apply(time_str_to_float)

            for team_id in df["teamId"].unique():
                team_df = df[df["teamId"] == team_id].copy()
                total_minutes = team_df["minutes_float"].sum()

                if total_minutes == 0:
                    continue  # Avoid division by zero

                weighted_stats = {}
                for stat in [
                    "offensiveRating", "defensiveRating", "netRating", "pace",
                    "effectiveFieldGoalPercentage", "trueShootingPercentage"
                ]:
                    weighted_stats[stat] = (
                        (team_df[stat] * team_df["minutes_float"]).sum() / total_minutes
                    )

                team_tricode = team_df["teamTricode"].iloc[0]
                game_date = game_team_pairs[
                    (game_team_pairs["GAME_ID"] == game_id) &
                    (game_team_pairs["TEAM_ID"] == team_id)
                ]["GAME_DATE"].values[0]

                records.append({
                    "gameId": game_id,
                    "teamId": team_id,
                    "team": team_tricode,
                    "date": game_date,
                    **weighted_stats
                })

            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Error fetching {game_id}: {e}")
            continue

    # Save results
    result_df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result_df.to_csv(output_csv, index=False)
    print(f"\n✅ Saved weighted team advanced stats to {output_csv}")

# Run the function
if __name__ == "__main__":
    collect_and_save_team_advanced_stats()

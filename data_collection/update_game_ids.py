import psycopg2
from nba_api.stats.endpoints import leaguegamelog
from requests.exceptions import ReadTimeout
import pandas as pd
import time

# ---- DB Connection ----
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",  
        host="localhost",
        port="5432"
    )

# ---- Fetch Game Log IDs for a Season/SeasonType ----
def get_game_logs(season, season_type, retries=5, sleep_time=5):
    for attempt in range(1, retries + 1):
        try:
            print(f"📅 Fetching game log for {season} ({season_type}), attempt {attempt}...")
            log = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=season_type,
                timeout=60
            )
            df = log.get_data_frames()[0]
            print(f"   ✅ Retrieved {len(df)} rows for {season_type}")
            return df

        except ReadTimeout as e:
            print(f"   ⚠️ Timeout (attempt {attempt}/{retries}): {e}")
            wait = sleep_time * (2 ** (attempt - 1))
            print(f"   ⏳ Retrying in {wait}s...")
            time.sleep(wait)

        except Exception as e:
            print(f"   ❌ Unexpected error for {season_type}: {e}")
            return None

    print(f"   ❌ Failed after max retries for {season_type}")
    return None

# ---- Insert into DB ----
def insert_games(df, season):
    conn = get_connection()
    cur = conn.cursor()

    grouped = df.groupby("GAME_ID")

    for game_id, group in grouped:
        try:
            # skip if already in table
            cur.execute("SELECT 1 FROM games WHERE game_id = %s;", (game_id,))
            if cur.fetchone():
                # print(f"   ⏭️ Skipping {game_id} (already in table)")
                continue

            game_date = group["GAME_DATE"].iloc[0]

            # Identify home & away
            home_row = group[group["MATCHUP"].str.contains("vs")]
            away_row = group[group["MATCHUP"].str.contains("@")]

            if home_row.empty or away_row.empty:
                print(f"   ⚠️ Skipping {game_id} (incomplete data: home or away missing)")
                continue

            home_row = home_row.iloc[0]
            away_row = away_row.iloc[0]

            home_team_id = str(home_row["TEAM_ID"])
            home_team_name = home_row["TEAM_NAME"]
            away_team_id = str(away_row["TEAM_ID"])
            away_team_name = away_row["TEAM_NAME"]

            cur.execute("""
                INSERT INTO games (season, game_id, game_date, home_team_id, home_team_name, away_team_id, away_team_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (int(season.split("-")[0]), game_id, game_date,
                  home_team_id, home_team_name,
                  away_team_id, away_team_name))

            # print(f"   ✅ Inserted {game_id}")

        except Exception as e:
            print(f"   ⚠️ Insert failed for {game_id}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"   💾 Finished inserting for season {season}")


# ---- Main ----
def populate_games(seasons):
    season_types = ["Regular Season", "Playoffs", "PlayIn"]  # include Play-In
    for season in seasons:
        for stype in season_types:
            df = get_game_logs(season, stype)
            if df is not None:
                insert_games(df, season)

# ---- Backup ----
def fetch_missing_games(season: str, missing_ids: list[str]) -> pd.DataFrame:
    """
    Fetches missing NBA games for a given season by their GAME_IDs.
    
    Args:
        season (str): NBA season string (e.g., "2024-25").
        missing_ids (list[str]): List of GAME_IDs to fetch.
    
    Returns:
        pd.DataFrame: DataFrame of the missing games with ID, date, and matchup.
    """
    # Pull season game log
    df = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season"
    ).get_data_frames()[0]

    # Only keep NBA regular season games (GAME_ID starting with 002)
    df = df[df["GAME_ID"].str.startswith("002")]

    # Keep only the missing ones
    missing_games = df[df["GAME_ID"].isin(missing_ids)]

    return missing_games[["GAME_ID", "GAME_DATE", "MATCHUP"]]

if __name__ == "__main__":
    populate_games(["2025-26"])

    # missing_ids = []
    # missing_games = fetch_missing_games("2022-23", missing_ids)
    # print(missing_games)

import psycopg2
import time
import re
from psycopg2.extras import execute_values
from nba_api.stats.endpoints import (
    boxscoretraditionalv3,
    boxscoreadvancedv3,
    boxscorefourfactorsv3,
    boxscoremiscv3,
    boxscoreusagev3,
    boxscorescoringv3,
    boxscoreplayertrackv3,
    boxscoredefensivev2,
    boxscorehustlev2
)

# --- DB CONNECTION ---
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )

# --- HELPER: camelCase → snake_case ---
def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

# --- HELPER: convert MM:SS → float minutes ---
def minutes_to_float(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        mm, ss = value.split(":")
        return int(mm) + int(ss) / 60.0
    except Exception:
        return None

# --- ENDPOINT MAPPING ---
ENDPOINTS = {
    "BoxScoreDefensiveV2": (boxscoredefensivev2.BoxScoreDefensiveV2, "boxscore_defensive_v2"),
    "BoxScoreTraditionalV3": (boxscoretraditionalv3.BoxScoreTraditionalV3, "boxscore_traditional_v3"),
    "BoxScoreMiscV3": (boxscoremiscv3.BoxScoreMiscV3, "boxscore_misc_v3"),
    "BoxScoreAdvancedV3": (boxscoreadvancedv3.BoxScoreAdvancedV3, "boxscore_advanced_v3"),
    "BoxScoreFourFactorsV3": (boxscorefourfactorsv3.BoxScoreFourFactorsV3, "boxscore_four_factors_v3"),
    "BoxScorePlayerTrackV3": (boxscoreplayertrackv3.BoxScorePlayerTrackV3, "boxscore_playertrack_v3"),
    "BoxScoreScoringV3": (boxscorescoringv3.BoxScoreScoringV3, "boxscore_scoring_v3"),
    "BoxScoreUsageV3": (boxscoreusagev3.BoxScoreUsageV3, "boxscore_usage_v3"),
    "BoxScoreHustleV2": (boxscorehustlev2.BoxScoreHustleV2, "boxscore_hustle_v2")
}

def get_completed_game_ids(endpoint: str, cur):
    _, table_name = ENDPOINTS[endpoint]
    cur.execute(f"SELECT DISTINCT game_id FROM {table_name};")
    return {row[0] for row in cur.fetchall()}

# --- GENERIC INSERT ---
def insert_boxscore(cur, conn, game_id, season, endpoint):
    api_cls, table_name = ENDPOINTS[endpoint]

    try:
        data = api_cls(game_id=game_id).get_data_frames()[0]
    except Exception as e:
        print(f"      ⚠️ API error for {endpoint}, game {game_id}: {e}")
        return

    if data.empty:
        print(f"      ⚠️ No data for {endpoint}, game {game_id}")
        return

    # Special handling for minutes columns
    if "minutes" in data.columns:
        data["minutes"] = data["minutes"].apply(minutes_to_float)
    if "matchupMinutes" in data.columns:
        data["matchupMinutes"] = data["matchupMinutes"].apply(minutes_to_float)

    # Add season + normalize column names
    data["season"] = season
    data.columns = [camel_to_snake(c) for c in data.columns]

    cols = list(data.columns)
    values = [tuple(x) for x in data.to_numpy()]

    insert_sql = f"""
        INSERT INTO {table_name} ({", ".join(cols)})
        VALUES %s
        ON CONFLICT (game_id, person_id) DO NOTHING;
    """

    try:
        execute_values(cur, insert_sql, values, page_size=100)
        conn.commit()
        print(f"         ✅ {endpoint}: Inserted {len(values)} rows for game {game_id}")
    except Exception as e:
        conn.rollback()
        print(f"      ⚠️ Insert failed for {endpoint}, game {game_id}: {e}")

# --- MAIN UPDATE LOOP ---
def update_boxscores(endpoints, seasons):
    conn = get_connection()
    cur = conn.cursor()

    for season in seasons:
        print(f"\n📅 Updating season {season}")
        cur.execute("SELECT game_id FROM games WHERE season = %s;", (season,))
        all_games = [row[0] for row in cur.fetchall()]
        print(f"   Found {len(all_games)} games in DB")

        # for endpoint in endpoints:
        #     _, table_name = ENDPOINTS[endpoint]
        #     print(f"   ↳ Endpoint {endpoint} → {table_name}")

        #     # done_games = get_completed_game_ids(endpoint, cur)
        #     # remaining = [g for g in all_games if g not in done_games]
        #     # remaining = all_games

        #     if table_name in ("boxscore_misc_v3", "boxscore_advanced_v3"):
        #         query = f"""
        #             SELECT t.game_id,
        #                 COUNT(DISTINCT t.person_id) AS ref_players,
        #                 COUNT(DISTINCT a.person_id) AS adv_players
        #             FROM boxscore_traditional_v3 t
        #             LEFT JOIN boxscore_advanced_v3 a ON t.game_id = a.game_id
        #             GROUP BY t.game_id
        #             HAVING COUNT(DISTINCT a.person_id) <> COUNT(DISTINCT t.person_id)
        #             ORDER BY t.game_id;
        #         """
        #         cur.execute(query)
        #         remaining = [row[0] for row in cur.fetchall()]
        #         print(f"      ⚠️ {len(remaining)} incomplete games found for {table_name}")
        #     else:
        #         remaining = all_games[:]
        
        for endpoint in endpoints:
            _, table_name = ENDPOINTS[endpoint]
            print(f"   ↳ Endpoint {endpoint} → {table_name}")

            # Fetch all games already scraped for this endpoint + season
            cur.execute(f"SELECT DISTINCT game_id FROM {table_name} WHERE season = %s;", (season,))
            done_games = {row[0] for row in cur.fetchall()}

            # Remaining = games not already in the endpoint’s table
            remaining = [g for g in all_games if g not in done_games]

            print(f"      {len(remaining)} games remaining (out of {len(all_games)})")

            for i, game_id in enumerate(remaining, 1):
                print(f"      ({i}/{len(remaining)}) Fetching {game_id}")
                insert_boxscore(cur, conn, game_id, season, endpoint)
                time.sleep(0.6)

    cur.close()
    conn.close()


if __name__ == "__main__":

    update_boxscores(
        ["BoxScoreDefensiveV2"],
        [2024, 2023, 2022, 2021, 2020]
    )


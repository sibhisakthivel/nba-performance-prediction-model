# # import time
# # import psycopg2
# # import pandas as pd
# # from nba_api.stats.endpoints import boxscoredefensivev2

# # # -------------------- DB Connection --------------------
# # def get_connection():
# #     return psycopg2.connect(
# #         dbname="nba",
# #         user="postgres",
# #         password="sibi",   # change this
# #         host="localhost",
# #         port="5432"
# #     )

# # # -------------------- Get game IDs from games table --------------------
# # def get_game_ids(season):
# #     conn = get_connection()
# #     cur = conn.cursor()
# #     cur.execute("""
# #         SELECT game_id FROM games
# #         WHERE season = %s 
# #         ORDER BY game_date;
# #     """, (season,))
# #     rows = cur.fetchall()
# #     cur.close()
# #     conn.close()
    
# #     valid_ids = [r[0] for r in rows if str(r[0]).startswith(("002", "004"))]
# #     return valid_ids

# # # -------------------- Insert rows into DB --------------------
# # def insert_defensive(cur, df):
# #     for _, row in df.iterrows():
# #         # Convert matchupMinutes ("MM:SS") to float minutes
# #         if isinstance(row["matchupMinutes"], str):
# #             mins, secs = map(int, row["matchupMinutes"].split(":"))
# #             matchup_minutes = mins + secs / 60
# #         else:
# #             matchup_minutes = row["matchupMinutes"]

# #         cur.execute("""
# #             INSERT INTO boxscore_defensive_v2 (
# #                 game_id, team_id, person_id, first_name, family_name, position,
# #                 jersey_num, matchup_minutes, partial_possessions, switches_on,
# #                 player_points, defensive_rebounds, matchup_assists,
# #                 matchup_turnovers, steals, blocks,
# #                 matchup_field_goals_made, matchup_field_goals_attempted,
# #                 matchup_field_goal_percentage,
# #                 matchup_three_pointers_made, matchup_three_pointers_attempted,
# #                 matchup_three_pointer_percentage
# #             )
# #             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
# #             ON CONFLICT (game_id, person_id) DO NOTHING;
# #         """, (
# #             row["gameId"], row["teamId"], row["personId"], row["firstName"], row["familyName"], row["position"],
# #             row["jerseyNum"], matchup_minutes, row["partialPossessions"], row["switchesOn"],
# #             row["playerPoints"], row["defensiveRebounds"], row["matchupAssists"],
# #             row["matchupTurnovers"], row["steals"], row["blocks"],
# #             row["matchupFieldGoalsMade"], row["matchupFieldGoalsAttempted"],
# #             row["matchupFieldGoalPercentage"],
# #             row["matchupThreePointersMade"], row["matchupThreePointersAttempted"],
# #             row["matchupThreePointerPercentage"]
# #         ))

# # # -------------------- Main ingestion --------------------
# # def update_boxscores(endpoints, seasons):
# #     conn = get_connection()
# #     cur = conn.cursor()

# #     for season in seasons:
# #         print(f"📅 Season {season}")
# #         game_ids = get_game_ids(season)
# #         print(f"   Found {len(game_ids)} games")

# #         for endpoint in endpoints:
# #             print(f"   ↳ Endpoint {endpoint}")

# #             for i, game_id in enumerate(game_ids, 1):
# #                 try:
# #                     if endpoint == "BoxScoreDefensiveV2":
# #                         data = boxscoredefensivev2.BoxScoreDefensiveV2(game_id=game_id).get_data_frames()[0]
# #                         insert_defensive(cur, data)

# #                     if i % 50 == 0:  # commit every 50 games
# #                         conn.commit()
# #                         print(f"      ✅ Inserted {i} games so far")

# #                     time.sleep(1.5)  # respect rate limiting

# #                 except Exception as e:
# #                     print(f"      ⚠️ Error for game {game_id}: {e}")
# #                     conn.rollback()

# #         conn.commit()

# #     cur.close()
# #     conn.close()
# #     print("✅ Update complete.")


# # # -------------------- Run Example --------------------
# # if __name__ == "__main__":
# #     update_boxscores(["BoxScoreDefensiveV2"], [2023, 2024])

# import time
# import psycopg2
# import pandas as pd
# from nba_api.stats.endpoints import boxscoredefensivev2

# # ---------- DB CONNECTION ----------
# def get_connection():
#     return psycopg2.connect(
#         dbname="nba",
#         user="postgres",
#         password="sibi",
#         host="localhost",
#         port="5432"
#     )

# # ---------- HELPERS ----------
# def convert_minutes(val):
#     if val is None or val == "":
#         return None
#     if isinstance(val, (int, float)):
#         return float(val)
#     try:
#         mins, secs = val.split(":")
#         return int(mins) + int(secs) / 60.0
#     except Exception:
#         return None

# def insert_boxscore_defensive(cur, conn, season, game_id, df):
#     df = df.copy()

#     # Convert matchupMinutes → float minutes
#     if "matchupMinutes" in df.columns:
#         df["matchupMinutes"] = df["matchupMinutes"].apply(convert_minutes)

#     for _, row in df.iterrows():
#         try:
#             cur.execute("""
#                 INSERT INTO boxscore_defensive_v2 (
#                     season, game_id, team_id, team_city, team_name, team_tricode, team_slug,
#                     person_id, first_name, family_name, name_i, player_slug, position, comment,
#                     jersey_num, matchup_minutes, partial_possessions, switches_on, player_points,
#                     defensive_rebounds, matchup_assists, matchup_turnovers, steals, blocks,
#                     matchup_field_goals_made, matchup_field_goals_attempted,
#                     matchup_field_goal_percentage, matchup_three_pointers_made,
#                     matchup_three_pointers_attempted, matchup_three_pointer_percentage
#                 ) VALUES (
#                     %s, %s, %s, %s, %s, %s, %s,
#                     %s, %s, %s, %s, %s, %s, %s,
#                     %s, %s, %s, %s, %s,
#                     %s, %s, %s, %s, %s,
#                     %s, %s,
#                     %s, %s,
#                     %s, %s
#                 )
#                 ON CONFLICT (game_id, person_id) DO NOTHING
#             """, (
#                 season, game_id,
#                 row.get("teamId"), row.get("teamCity"), row.get("teamName"),
#                 row.get("teamTricode"), row.get("teamSlug"),
#                 row.get("personId"), row.get("firstName"), row.get("familyName"),
#                 row.get("nameI"), row.get("playerSlug"), row.get("position"),
#                 row.get("comment"), row.get("jerseyNum"),
#                 row.get("matchupMinutes"), row.get("partialPossessions"),
#                 row.get("switchesOn"), row.get("playerPoints"),
#                 row.get("defensiveRebounds"), row.get("matchupAssists"),
#                 row.get("matchupTurnovers"), row.get("steals"), row.get("blocks"),
#                 row.get("matchupFieldGoalsMade"), row.get("matchupFieldGoalsAttempted"),
#                 row.get("matchupFieldGoalPercentage"),
#                 row.get("matchupThreePointersMade"), row.get("matchupThreePointersAttempted"),
#                 row.get("matchupThreePointerPercentage")
#             ))
#         except Exception as e:
#             print(f"   ⚠️ Insert failed for game {game_id} / player {row.get('personId')}: {e}")
#             conn.rollback()   # rollback failed statement
#             continue
#     conn.commit()

# # ---------- MAIN ----------
# def update_boxscores(endpoints, seasons):
#     conn = get_connection()
#     cur = conn.cursor()

#     for season in seasons:
#         print(f"\n📅 Updating season {season}")

#         # Get all game IDs from DB
#         cur.execute("SELECT game_id FROM games WHERE season = %s", (season,))
#         game_ids = [r[0] for r in cur.fetchall()]
#         print(f"   Found {len(game_ids)} games in DB")

#         for endpoint in endpoints:
#             if endpoint == "BoxScoreDefensiveV2":
#                 for i, game_id in enumerate(game_ids, start=1):
#                     print(f"      ({i}/{len(game_ids)}) Fetching {game_id}")
#                     try:
#                         df = boxscoredefensivev2.BoxScoreDefensiveV2(
#                             game_id=game_id
#                         ).get_data_frames()[0]
#                         insert_boxscore_defensive(cur, conn, season, game_id, df)
#                     except Exception as e:
#                         print(f"         ⚠️ Error for game {game_id}: {e}")
#                         time.sleep(2)

#     cur.close()
#     conn.close()

# if __name__ == "__main__":
#     update_boxscores(["BoxScoreDefensiveV2"], [2024])

import psycopg2
import time
from nba_api.stats.endpoints import boxscoredefensivev2
from nba_api.stats.library.http import NBAStatsHTTP
from psycopg2.extras import execute_values
import re

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

# --- Endpoint → table name mapping ---
ENDPOINT_TABLE_MAP = {
    "BoxScoreDefensiveV2": "boxscore_defensive_v2",
    # later you can add more here:
    # "BoxScoreTraditionalV3": "boxscore_traditional_v3",
    # "BoxScoreUsageV2": "boxscore_usage_v2",
}

def get_completed_game_ids(endpoint: str, cur):
    table_name = ENDPOINT_TABLE_MAP.get(endpoint, camel_to_snake(endpoint))
    cur.execute(f"SELECT DISTINCT game_id FROM {table_name};")
    return {row[0] for row in cur.fetchall()}

def minutes_to_float(value):
    """
    Convert MM:SS string to float minutes. 
    If already numeric or None, return as-is.
    """
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        mm, ss = value.split(":")
        return int(mm) + int(ss) / 60.0
    except Exception:
        return None

# --- Insert one game’s rows ---
def insert_boxscore_defensive_v2(cur, conn, game_id, season):
    try:
        data = boxscoredefensivev2.BoxScoreDefensiveV2(game_id=game_id).get_data_frames()[0]
    except Exception as e:
        print(f"      ⚠️ API error for game {game_id}: {e}")
        return

    if data.empty:
        print(f"      ⚠️ No data for game {game_id}")
        return

    data["season"] = season  # ✅ add season col
    data["matchupMinutes"] = data["matchupMinutes"].apply(minutes_to_float)

    # convert column names
    data.columns = [camel_to_snake(c) for c in data.columns]

    table_name = "boxscore_defensive_v2"
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
        print(f"         ✅ Inserted {len(values)} rows for game {game_id}")
    except Exception as e:
        conn.rollback()
        print(f"      ⚠️ Insert failed for game {game_id}: {e}")

# --- MAIN UPDATE LOOP ---
def update_boxscores(endpoints, seasons):
    conn = get_connection()
    cur = conn.cursor()

    for season in seasons:
        print(f"\n📅 Updating season {season}")
        cur.execute("SELECT game_id FROM games WHERE season = %s;", (season,))
        all_games = [row[0] for row in cur.fetchall()]
        print(f"   Found {len(all_games)} games in DB")

        for endpoint in endpoints:
            table_name = ENDPOINT_TABLE_MAP.get(endpoint, camel_to_snake(endpoint))
            print(f"   ↳ Endpoint {endpoint} → {table_name}")

            done_games = get_completed_game_ids(endpoint, cur)
            remaining = [g for g in all_games if g not in done_games]

            print(f"      {len(remaining)} games remaining (out of {len(all_games)})")

            for i, game_id in enumerate(remaining, 1):
                print(f"      ({i}/{len(remaining)}) Fetching {game_id}")
                insert_boxscore_defensive_v2(cur, conn, game_id, season)
                time.sleep(1.5)  # polite sleep between requests

    cur.close()
    conn.close()


if __name__ == "__main__":
    update_boxscores(["BoxScoreDefensiveV2"], [2024])

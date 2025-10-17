NBA_MODEL_PLAYERS = [
    # Superstars
    "Nikola Jokic", "Shai Gilgeous-Alexander", "Luka Doncic", "Giannis Antetokounmpo", "Jayson Tatum",
    "Anthony Edwards", "Donovan Mitchell", "Jalen Brunson",
    "LeBron James", "Stephen Curry", "Kevin Durant", "Anthony Davis",
    # Allstars
    "Victor Wembanyama", "Tyrese Haliburton", "Kawhi Leonard", "Cade Cunningham",
    "Evan Mobley", "Karl-Anthony Towns", "Devin Booker", "Jalen Williams",
    "Jaylen Brown", "Paolo Banchero", "Pascal Siakam", "Jimmy Butler",
    "Jaren Jackson Jr.", "De'Aaron Fox", "Chet Holmgren", "Darius Garland",
    "Jamal Murray", "James Harden", "Domantas Sabonis", "Bam Adebayo",
    "Trae Young", "Ja Morant", "Ivica Zubac", "Alperen Sengun",
    "Franz Wagner", "Derrick White", "Tyrese Maxey", "OG Anunoby",
    "Amen Thompson", "Aaron Gordon", "Damian Lillard", "Kyrie Irving",
    "Zion Williamson", "Scottie Barnes", "Desmond Bane", "Jalen Johnson",
    "LaMelo Ball", "Draymond Green", "Tyler Herro", "Julius Randle",
    "Lauri Markkanen", "Austin Reaves", "Rudy Gobert", "Trey Murphy III",
    "Jarrett Allen", "Norman Powell", "Dyson Daniels", "Mikal Bridges",
    "Deni Avdija", "Jalen Suggs", "Alex Caruso", "Fred VanVleet",
    "Isaiah Hartenstein", "Jaden McDaniels", "DeMar DeRozan", "Zach LaVine",
    "Jrue Holiday", "Kristaps Porzingis", "Coby White", "Brandon Ingram",
    "Michael Porter Jr.", "Andrew Nembhard", "Cam Johnson", "Myles Turner",
    "Naz Reid", "Lu Dort", "Josh Hart", "RJ Barrett",
    "Josh Giddey", "De'Andre Hunter", "Christian Braun", "Joel Embiid",
    "CJ McCollum", "Devin Vassell", "Anfernee Simons", "Tari Eason",
    "Payton Pritchard", "Paul George", "Aaron Nesmith", "Nikola Vucevic",
    "Dillon Brooks", "Mitchell Robinson", "Toumani Camara", "Herb Jones",
    "Jalen Duren", "Jalen Green", "Jordan Poole", "Bradley Beal",
    # # Good Players
    # "Sam Hauser", "Cam Thomas", "Nicolas Claxton", "Brandon Miller",
    # "Miles Bridges", "D'Angelo Russell", "Klay Thompson", "Cooper Flagg",
    # "Derrick Lively II", "Jaden Ivey", "Ausar Thompson", "Tobias Harris",
    # "Brandin Podziemski", "Buddy Hield", "Jabari Smith Jr.", "Bennedict Mathurin",
    # "John Collins", "Rui Hachimura", "Deandre Ayton", "Zach Edey",
    # "Andrew Wiggins", "Kyle Kuzma", "Gary Trent Jr.", "Kevin Porter Jr.",
    # "Quentin Grimes", "VJ Edgecombe", "Mark Williams", "Shaedon Sharpe",
    # "Donovan Clingan", "Malik Monk", "Keegan Murray", "Stephon Castle",
    # "Harrison Barnes", "Immanuel Quickley", "Isaiah Collier", "Ace Bailey",
    # "Walker Kessler", "Bub Carrington", "Alex Sarr", "Khris Middleton",
    # "Bilal Coulibaly", "Lonzo Ball"
]

import psycopg2
import time
from nba_api.stats.endpoints import boxscoredefensivev2, boxscoretraditionalv3, boxscoremiscv3
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
    "BoxScoreTraditionalV3": "boxscore_traditional_v3"
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

    # --- Filter rows by our player list ---
    data["full_name"] = data["first_name"] + " " + data["family_name"]
    data = data[data["full_name"].isin(NBA_MODEL_PLAYERS)]

    if data.empty:
        print(f"         ⚠️ No matching players in game {game_id}")
        return

    values = [tuple(x) for x in data[cols].to_numpy()]

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

# --- Insert one game’s rows ---
def insert_boxscore_traditional_v3(cur, conn, game_id, season):
    try:
        data = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id).get_data_frames()[0]
    except Exception as e:
        print(f"      ⚠️ API error for game {game_id}: {e}")
        return

    if data.empty:
        print(f"      ⚠️ No data for game {game_id}")
        return

    data["season"] = season
    data["minutes"] = data["minutes"].apply(minutes_to_float)  # normalize time
    data.columns = [camel_to_snake(c) for c in data.columns]

    table_name = "boxscore_traditional_v3"
    cols = list(data.columns)

    # --- Filter rows by our player list ---
    data["full_name"] = data["first_name"] + " " + data["family_name"]
    data = data[data["full_name"].isin(NBA_MODEL_PLAYERS)]

    if data.empty:
        print(f"         ⚠️ No matching players in game {game_id}")
        return

    values = [tuple(x) for x in data[cols].to_numpy()]

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
            
            BACKFILL = False  # toggle this manually

            if BACKFILL:
                remaining = all_games
            else:
                remaining = [g for g in all_games if g not in done_games]

            print(f"      {len(remaining)} games remaining (out of {len(all_games)})")

            for i, game_id in enumerate(remaining, 1):
                print(f"      ({i}/{len(remaining)}) Fetching {game_id}")

                if endpoint == "BoxScoreDefensiveV2":
                    insert_boxscore_defensive_v2(cur, conn, game_id, season)
                elif endpoint == "BoxScoreTraditionalV3":
                    insert_boxscore_traditional_v3(cur, conn, game_id, season)

                time.sleep(1.5)

    cur.close()
    conn.close()


if __name__ == "__main__":
    update_boxscores(["BoxScoreTraditionalV3"], [2024])

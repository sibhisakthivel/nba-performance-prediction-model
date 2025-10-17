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
    "Deni Avdija", "Isaiah Hartenstein", "Brandon Ingram", "Michael Porter Jr.",
    "Josh Giddey", "Devin Vassell", "Jalen Green", "Jordan Poole",
    "Miles Bridges", "Klay Thompson", "DeMar DeRozan", "Zach LaVine",
    "Toumani Camara", "Jalen Duren", "Stephon Castle", "Josh Hart",
    "Kristaps Porzingis",
    # Good Players
    "Jalen Suggs", "Alex Caruso", "Fred VanVleet",
    "Jaden McDaniels", "Nikola Vucevic", "Bradley Beal",
    "Jrue Holiday", "Coby White",
    "Andrew Nembhard", "Cam Johnson", "Myles Turner",
    "Naz Reid", "Lu Dort", "RJ Barrett",
    "De'Andre Hunter", "Christian Braun", "Joel Embiid",
    "CJ McCollum", "Anfernee Simons", "Tari Eason",
    "Payton Pritchard", "Paul George", "Aaron Nesmith",
    "Dillon Brooks", "Mitchell Robinson", "Herb Jones",
    "Sam Hauser", "Cam Thomas", "Nicolas Claxton", "Brandon Miller",
    "D'Angelo Russell", "Cooper Flagg",
    "Derrick Lively II", "Jaden Ivey", "Ausar Thompson", "Tobias Harris",
    "Brandin Podziemski", "Buddy Hield", "Jabari Smith Jr.", "Bennedict Mathurin",
    "John Collins", "Rui Hachimura", "Deandre Ayton", "Zach Edey",
    "Andrew Wiggins", "Kyle Kuzma", "Gary Trent Jr.", "Kevin Porter Jr.",
    "Quentin Grimes", "VJ Edgecombe", "Mark Williams", "Shaedon Sharpe",
    "Donovan Clingan", "Malik Monk", "Keegan Murray",
    "Harrison Barnes", "Immanuel Quickley", "Isaiah Collier", "Ace Bailey",
    "Walker Kessler", "Bub Carrington", "Alex Sarr", "Khris Middleton",
    "Bilal Coulibaly", "Lonzo Ball"
]

import psycopg2
import pandas as pd
import re
import time
from nba_api.stats.endpoints import playbyplayv3
from psycopg2.extras import execute_values
from sqlalchemy import create_engine

# --- DB CONNECTION ---
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )

# === Patch LeagueGameLogs ===

# --- 1. Find missing Play-In games ---
def get_missing_playin_games():
    conn = get_connection()
    query = """
        SELECT g.season, g.game_id, g.game_date, g.home_team_id, g.away_team_id
        FROM games g
        LEFT JOIN leaguegamelogs l
            ON g.game_id = l.game_id
        WHERE g.season >= 2020
        AND LEFT(g.game_id::text, 3) = '005'
        AND l.game_id IS NULL
        ORDER BY g.season, g.game_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- 2. Aggregate player boxscores into team totals ---
def aggregate_playin_game(game_id, season, game_meta):
    conn = get_connection()
    q = f"""
        SELECT *
        FROM boxscore_traditional_v3
        WHERE game_id = '{game_id}';
    """
    df = pd.read_sql(q, conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # --- Aggregate per team ---
    agg = df.groupby(["game_id", "team_id"], as_index=False).agg({
        "team_tricode": "first",          # TEAM_ABBREVIATION
        "team_name": "first",             # TEAM_NAME
        "minutes": "sum",                 # MIN
        "field_goals_made": "sum",        # FGM
        "field_goals_attempted": "sum",   # FGA
        "three_pointers_made": "sum",     # FG3M
        "three_pointers_attempted": "sum",# FG3A
        "free_throws_made": "sum",        # FTM
        "free_throws_attempted": "sum",   # FTA
        "rebounds_offensive": "sum",      # OREB
        "rebounds_defensive": "sum",      # DREB
        "rebounds_total": "sum",          # REB
        "assists": "sum",                 # AST
        "steals": "sum",                  # STL
        "blocks": "sum",                  # BLK
        "turnovers": "sum",               # TOV
        "fouls_personal": "sum",          # PF
        "points": "sum",                  # PTS
        "plus_minus_points": "sum"        # PLUS_MINUS
    })

    # --- Add season ---
    agg["SEASON_ID"] = season

    # --- Shooting percentages ---
    agg["FG_PCT"] = agg["field_goals_made"] / agg["field_goals_attempted"].replace(0, pd.NA)
    agg["FG3_PCT"] = agg["three_pointers_made"] / agg["three_pointers_attempted"].replace(0, pd.NA)
    agg["FT_PCT"] = agg["free_throws_made"] / agg["free_throws_attempted"].replace(0, pd.NA)

    # --- Derive WL ---
    max_pts = agg.groupby("game_id")["points"].transform("max")
    agg["WL"] = agg["points"].eq(max_pts).map({True: "W", False: "L"})

    # --- Add GAME_DATE ---
    agg["GAME_DATE"] = game_meta["game_date"].values[0]

    # --- Build MATCHUP ---
    home_team_id = game_meta["home_team_id"].values[0]
    away_team_id = game_meta["away_team_id"].values[0]
    home_abbr = agg.loc[agg["team_id"] == str(home_team_id), "team_tricode"].values[0]
    away_abbr = agg.loc[agg["team_id"] == str(away_team_id), "team_tricode"].values[0]

    def build_matchup(row):
        if row["team_id"] == str(home_team_id):
            return f"{row['team_tricode']} vs. {away_abbr}"
        else:
            return f"{row['team_tricode']} @ {home_abbr}"

    agg["MATCHUP"] = agg.apply(build_matchup, axis=1)

    # --- Add VIDEO_AVAILABLE ---
    agg["VIDEO_AVAILABLE"] = 1

    # --- Rename to match leaguegamelogs schema ---
    agg.rename(columns={
        "game_id": "GAME_ID",
        "team_id": "TEAM_ID",
        "team_tricode": "TEAM_ABBREVIATION",
        "team_name": "TEAM_NAME",
        "minutes": "MIN",
        "field_goals_made": "FGM",
        "field_goals_attempted": "FGA",
        "three_pointers_made": "FG3M",
        "three_pointers_attempted": "FG3A",
        "free_throws_made": "FTM",
        "free_throws_attempted": "FTA",
        "rebounds_offensive": "OREB",
        "rebounds_defensive": "DREB",
        "rebounds_total": "REB",
        "assists": "AST",
        "steals": "STL",
        "blocks": "BLK",
        "turnovers": "TOV",
        "fouls_personal": "PF",
        "points": "PTS",
        "plus_minus_points": "PLUS_MINUS"
    }, inplace=True)

    # --- Reorder to exact schema ---
    agg = agg[[
        "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN", "FGM", "FGA", "FG_PCT",
        "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB",
        "AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS", "VIDEO_AVAILABLE"
    ]]

    return agg

# --- 3. Insert rows into leaguegamelogs ---
def insert_into_leaguegamelogs(df):
    if df.empty:
        return
    
    df.columns = [c.lower() for c in df.columns]

    engine = create_engine("postgresql+psycopg2://postgres:sibi@localhost:5432/nba")
    df.to_sql("leaguegamelogs", engine, if_exists="append", index=False)

# --- 4. Main patch process ---
def patch_playins():
    missing = get_missing_playin_games()
    print(f"Found {len(missing)} missing Play-In games.")

    all_rows = []
    for _, row in missing.iterrows():
        game_id, season = row["game_id"], row["season"]
        print(f"Processing {season} game {game_id}...")
        game_meta = missing[missing["game_id"] == game_id]
        agg = aggregate_playin_game(game_id, season, game_meta)
        all_rows.append(agg)

    if all_rows:
        df_all = pd.concat(all_rows, ignore_index=True)
        print(f"Inserting {len(df_all)} rows into leaguegamelogs...")
        insert_into_leaguegamelogs(df_all)
        print("✅ Done!")
    else:
        print("No rows to insert.")

# === Patch Shot Data ===

# --- Clock parser ---
def parse_clock(clock_str):
    if not clock_str or pd.isna(clock_str):
        return (0, 0)

    if clock_str.startswith("PT"):
        match = re.match(r"PT(?:(\d+)M)?([\d\.]+)S", clock_str)
        if match:
            minutes = int(match.group(1)) if match.group(1) else 0
            seconds = int(float(match.group(2)))
            return (minutes, seconds)

    if ":" in clock_str:
        try:
            m, s = map(int, clock_str.split(":"))
            return (m, s)
        except ValueError:
            pass

    try:
        total_seconds = int(float(clock_str))
        minutes, seconds = divmod(total_seconds, 60)
        return (minutes, seconds)
    except ValueError:
        return (0, 0)

# --- Backfill single game ---
def backfill_game(conn, gid, game_date, htm, vtm):
    pbp = playbyplayv3.PlayByPlayV3(game_id=gid).get_data_frames()[0]

    # keep only shots
    shots = pbp[pbp["isFieldGoal"] == 1].copy()
    if shots.empty:
        print(f"⚠️  No shots found for {gid}")
        return

    # parse clock into minutes/seconds remaining
    shots[["minutes_remaining", "seconds_remaining"]] = shots["clock"].apply(
        lambda c: pd.Series(parse_clock(c))
    )

    # map columns to shotchartdetail schema
    records = []
    for _, row in shots.iterrows():
        record = (
            "Shot Chart Detail",        # grid_type
            row["gameId"],              # game_id
            int(row["actionNumber"]),   # game_event_id
            int(row["personId"]) if row["personId"] else None,  # player_id
            row["playerName"],          # player_name
            int(row["teamId"]) if row["teamId"] else None,      # team_id
            row["teamTricode"],         # team_name (fallback: abbr)
            int(row["period"]),         # period
            int(row["minutes_remaining"]),
            int(row["seconds_remaining"]),
            "Made Shot" if row["shotResult"] == "Made Shot" else "Missed Shot",  # event_type
            row["actionType"],          # action_type
            f"{row['shotValue']}PT Field Goal",  # shot_type (2PT or 3PT)
            None,                       # shot_zone_basic (TODO: derive from coords)
            None,                       # shot_zone_area
            None,                       # shot_zone_range
            int(row["shotDistance"]) if pd.notna(row["shotDistance"]) else 0,  # shot_distance
            int(row["xLegacy"]) if pd.notna(row["xLegacy"]) else 0,  # loc_x
            int(row["yLegacy"]) if pd.notna(row["yLegacy"]) else 0,  # loc_y
            1,                          # shot_attempted_flag
            1 if row["shotResult"] == "Made Shot" else 0,  # shot_made_flag
            game_date,                  # game_date
            htm,                        # htm
            vtm                         # vtm
        )
        records.append(record)

    # insert into DB
    cur = conn.cursor()
    insert_sql = """
        INSERT INTO shotchartdetail (
            grid_type, game_id, game_event_id, player_id, player_name, team_id, team_name,
            period, minutes_remaining, seconds_remaining, event_type, action_type, shot_type,
            shot_zone_basic, shot_zone_area, shot_zone_range, shot_distance, loc_x, loc_y,
            shot_attempted_flag, shot_made_flag, game_date, htm, vtm
        )
        VALUES %s
        ON CONFLICT (game_id, game_event_id) DO NOTHING
    """
    execute_values(cur, insert_sql, records)
    conn.commit()
    print(f"✅ Inserted {len(records)} shots for {gid}")

# --- Backfill all missing games ---
def backfill_missing_shots(season):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT l.game_id, l.game_date,
               MAX(CASE WHEN POSITION('vs' IN l.matchup) > 0 THEN l.team_abbreviation END) AS htm,
               MAX(CASE WHEN POSITION('@' IN l.matchup) > 0 THEN l.team_abbreviation END) AS vtm
        FROM leaguegamelogs l
        LEFT JOIN (
            SELECT DISTINCT game_id FROM shotchartdetail
        ) s ON l.game_id = s.game_id
        WHERE l.season_id IN (%s, '2'||%s, '4'||%s)
          AND s.game_id IS NULL
          AND (POSITION('vs' IN l.matchup) > 0 OR POSITION('@' IN l.matchup) > 0)
        GROUP BY l.game_id, l.game_date
        ORDER BY l.game_id
    """

    cur.execute(query, (season, season, season))
    games = cur.fetchall()

    print(f"📊 Found {len(games)} missing games to backfill")

    for i, (gid, gdate, htm, vtm) in enumerate(games, 1):
        print(f"↳ Backfilling {gid} ({i}/{len(games)})")
        backfill_game(conn, gid, gdate, htm, vtm)
        time.sleep(0.6)

    conn.close()

# --- Run ---
if __name__ == "__main__":
    # patch_playins()
    backfill_missing_shots("2020")

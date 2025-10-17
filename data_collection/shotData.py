import psycopg2
from psycopg2.extras import execute_values
from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
import time

# --- DB CONNECTION ---
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )

def get_missing_game_ids_by_season(seasons):
    """
    Returns dict of {season: [game_ids]} for all games in `games`
    that are not already in `shotchartdetail`.
    """
    conn = get_connection()
    query = """
        SELECT g.season, g.game_id
        FROM games g
        WHERE g.season = ANY(%s)
          AND NOT EXISTS (
              SELECT 1 FROM shotchartdetail s WHERE s.game_id = g.game_id LIMIT 1
          )
        ORDER BY g.season, g.game_date;
    """
    df = pd.read_sql(query, conn, params=(seasons,))
    conn.close()

    # group by season → list of game_ids
    grouped = df.groupby("season")["game_id"].apply(list).to_dict()
    return grouped

# --- SCRAPE SHOTCHART FOR ONE GAME ---
def fetch_shotchart(game_id, season):
    """
    Fetch all shots for a given game_id in a season.
    Returns list of tuples matching DB schema.
    """
    try:
        resp = shotchartdetail.ShotChartDetail(
            team_id=0,  # 0 = all teams
            player_id=0,  # 0 = all players
            game_id_nullable=game_id,
            season_nullable=season,
            context_measure_simple="FGA"
        )
        df = resp.get_data_frames()[0]

        rows = []
        for _, row in df.iterrows():
            rows.append((
                row.get("GRID_TYPE"),
                row.get("GAME_ID"),
                row.get("GAME_EVENT_ID"),
                row.get("PLAYER_ID"),
                row.get("PLAYER_NAME"),
                row.get("TEAM_ID"),
                row.get("TEAM_NAME"),
                row.get("PERIOD"),
                row.get("MINUTES_REMAINING"),
                row.get("SECONDS_REMAINING"),
                row.get("EVENT_TYPE"),
                row.get("ACTION_TYPE"),
                row.get("SHOT_TYPE"),
                row.get("SHOT_ZONE_BASIC"),
                row.get("SHOT_ZONE_AREA"),
                row.get("SHOT_ZONE_RANGE"),
                row.get("SHOT_DISTANCE"),
                row.get("LOC_X"),
                row.get("LOC_Y"),
                row.get("SHOT_ATTEMPTED_FLAG"),
                row.get("SHOT_MADE_FLAG"),
                row.get("GAME_DATE"),
                row.get("HTM"),
                row.get("VTM"),
            ))
        return rows
    except Exception as e:
        print(f"❌ Error fetching game {game_id}: {e}")
        return []

# --- INSERT INTO POSTGRES ---
def insert_shotchart(rows):
    if not rows:
        return
    conn = get_connection()
    cur = conn.cursor()
    query = """
        INSERT INTO shotchartdetail (
            grid_type, game_id, game_event_id, player_id, player_name,
            team_id, team_name, period, minutes_remaining, seconds_remaining,
            event_type, action_type, shot_type, shot_zone_basic, shot_zone_area,
            shot_zone_range, shot_distance, loc_x, loc_y, shot_attempted_flag,
            shot_made_flag, game_date, htm, vtm
        ) VALUES %s
        ON CONFLICT (game_id, game_event_id) DO NOTHING;
    """
    try:
        execute_values(cur, query, rows, page_size=500)
        conn.commit()
        print(f"✅ Inserted {len(rows)} shots")
    except Exception as e:
        print(f"❌ DB insert error: {e}")
    finally:
        cur.close()
        conn.close()

# --- MAIN LOOP ---
def update_shotcharts(seasons, game_ids_by_season):
    for season in seasons:
        game_ids = game_ids_by_season.get(season, [])
        total = len(game_ids)
        print(f"\n📅 Updating season {season} → {total} missing games")

        for i, game_id in enumerate(game_ids, start=1):
            print(f"   ↳ ({i}/{total}) Fetching {game_id} ({total - i} remaining)")
            rows = fetch_shotchart(game_id, season)
            insert_shotchart(rows)
            time.sleep(0.6)  # avoid rate limits

if __name__ == "__main__":
    seasons = [2020]
    game_ids_by_season = get_missing_game_ids_by_season(seasons)
    update_shotcharts(seasons, game_ids_by_season)


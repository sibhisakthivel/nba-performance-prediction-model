import pandas as pd
import psycopg2

# -----------------------------------------
# DB CONNECTION
# -----------------------------------------
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )


# -----------------------------------------
# CONFIGURATION
# -----------------------------------------
WEIGHTED_COLS = {
    "boxscore_traditional_v3": {
        "field_goals_percentage": ("field_goals_made", "field_goals_attempted"),
        "three_pointers_percentage": ("three_pointers_made", "three_pointers_attempted"),
        "free_throws_percentage": ("free_throws_made", "free_throws_attempted")
    },
    # add advanced, usage, etc. here
}

# Universal metadata columns for boxscore endpoints
BOX_SCORE_META_COLS = {
    "season", "game_id", "team_id", "team_city", "team_name",
    "team_tricode", "team_slug", "person_id", "first_name",
    "family_name", "name_i", "player_slug", "position",
    "comment", "jersey_num", "game_date", "is_home", "is_win"
}

ROLLING_WINDOWS = [5, 10]  # all rolling windows in one place


# -----------------------------------------
# LOAD
# -----------------------------------------
def load_table(conn, endpoint, season):
    # Detect which season column this endpoint uses
    season_col = None
    for col in ["season", "season_id", "season_year"]:
        query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{endpoint}' AND column_name = '{col}'
        """
        cur = conn.cursor()
        cur.execute(query)
        if cur.fetchone():
            season_col = col
            break

    if not season_col:
        raise ValueError(f"No season column found for {endpoint}")

    # Build query: join with leaguegamelogs for context
    sql = f"""
        SELECT b.*, g.game_date,
               (CASE WHEN POSITION('vs' IN g.matchup) > 0 THEN TRUE ELSE FALSE END) AS is_home,
               (CASE WHEN g.wl = 'W' THEN TRUE ELSE FALSE END) AS is_win
        FROM {endpoint} b
        JOIN leaguegamelogs g
          ON b.game_id = g.game_id
         AND b.team_id::int = g.team_id
        WHERE b.{season_col} = %s
    """

    return pd.read_sql(sql, conn, params=(season,))


# -----------------------------------------
# FEATURE HELPERS
# -----------------------------------------
def season_avg(values):
    return values.expanding().mean().shift()


def rolling_avg(values, window):
    return values.rolling(window, min_periods=window).mean().shift()


def split_avg(values, mask):
    """Compute season average for subset (home/away, win/loss)."""
    return values.where(mask).expanding().mean().shift()


def weighted_season_avg(num, denom):
    return (
        num.expanding().sum().shift()
        / denom.expanding().sum().shift().replace({0: pd.NA})
    )


def weighted_rolling_avg(num, denom, window):
    return (
        num.rolling(window, min_periods=window).sum().shift()
        / denom.rolling(window, min_periods=window).sum().shift().replace({0: pd.NA})
    )


def weighted_split_avg(num, denom, mask):
    return (
        num.where(mask).expanding().sum().shift()
        / denom.where(mask).expanding().sum().shift().replace({0: pd.NA})
    )


# -----------------------------------------
# MASTER WRAPPER FOR ONE STAT
# -----------------------------------------
def compute_stat_features(grp, stat, weighted_map):
    """Compute season/rolling/split averages for one stat (simple or weighted)."""
    features = {}

    if stat in weighted_map:
        num, denom = weighted_map[stat]

        # season + rolling
        features[f"{stat}_season_avg"] = weighted_season_avg(grp[num], grp[denom])
        for w in ROLLING_WINDOWS:
            features[f"{stat}_roll{w}"] = weighted_rolling_avg(grp[num], grp[denom], w)

        # splits
        features[f"{stat}_season_avg_home"] = weighted_split_avg(
            grp[num], grp[denom], grp["is_home"]
        )
        features[f"{stat}_season_avg_away"] = weighted_split_avg(
            grp[num], grp[denom], ~grp["is_home"]
        )
        features[f"{stat}_season_avg_win"] = weighted_split_avg(
            grp[num], grp[denom], grp["is_win"]
        )
        features[f"{stat}_season_avg_loss"] = weighted_split_avg(
            grp[num], grp[denom], ~grp["is_win"]
        )

    else:
        values = grp[stat]

        # season + rolling
        features[f"{stat}_season_avg"] = season_avg(values)
        for w in ROLLING_WINDOWS:
            features[f"{stat}_roll{w}"] = rolling_avg(values, w)

        # splits
        features[f"{stat}_season_avg_home"] = split_avg(values, grp["is_home"])
        features[f"{stat}_season_avg_away"] = split_avg(values, ~grp["is_home"])
        features[f"{stat}_season_avg_win"] = split_avg(values, grp["is_win"])
        features[f"{stat}_season_avg_loss"] = split_avg(values, ~grp["is_win"])

    return pd.DataFrame(features, index=grp.index)


# -----------------------------------------
# PROCESS
# -----------------------------------------
def process_features(df, endpoint):
    """Process features for a given endpoint dataframe."""
    for col in ["season_year", "season_id", "season"]:
        if col in df.columns:
            season_col = col
            break
    else:
        raise ValueError(f"No season column found in {endpoint} dataframe")
    group_cols = ["person_id", season_col]
    
    results = []
    weighted_map = WEIGHTED_COLS.get(endpoint, {})

    for _, grp in df.groupby(group_cols):
        grp = grp.sort_values("game_id").copy()

        # loop through all stat columns (excluding metadata)
        stat_cols = [
            c for c in grp.columns
            if pd.api.types.is_numeric_dtype(grp[c]) and c not in BOX_SCORE_META_COLS
        ]

        for stat in stat_cols:
            feats = compute_stat_features(grp, stat, weighted_map)

            # Find location after the stat
            insert_loc = grp.columns.get_loc(stat) + 1
            
            # Split grp into before / after, then re-concat
            left = grp.iloc[:, :insert_loc]
            right = grp.iloc[:, insert_loc:]
            grp = pd.concat([left, feats, right], axis=1)

        results.append(grp)

    return pd.concat(results, ignore_index=True)


# -----------------------------------------
# UPDATE DB / EXPORT
# -----------------------------------------
def update_db(endpoint, season, conn):
    df = load_table(conn, endpoint, season)
    print(f"Loaded {len(df)} rows from {endpoint} ({season})")

    df_processed = process_features(df, endpoint)

    # for now export → CSV
    df_processed.to_csv(f"processed_features/{endpoint}_{season}_processed.csv", index=False)
    print(f"✅ Saved processed features to {endpoint}_{season}_processed.csv")

    # later: insert back into Postgres

if __name__ == "__main__":
    conn = get_connection()

    endpoints = [
        "boxscore_traditional_v3",
        # "boxscore_advanced_v3",
        # "boxscore_usage_v3",
        # add more here
    ]

    seasons = [2024]

    for endpoint in endpoints:
        for season in seasons:
            print(f"\n📊 Processing {endpoint} for {season}...")
            update_db(endpoint, season, conn)

    conn.close()

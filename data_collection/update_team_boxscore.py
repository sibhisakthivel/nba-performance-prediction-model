import time
import psycopg2
from psycopg2.extras import execute_batch
from nba_api.stats.endpoints import (
    # boxscoretraditionalv3,
    boxscoreadvancedv3,
    boxscorefourfactorsv3,
    # boxscoremiscv3,
    boxscoreusagev3,
#     boxscorescoringv3,
#     boxscoreplayertrackv3,
#     boxscoredefensivev2,
#     boxscorehustlev2
)

# === Database Connection ===
def get_connection():
    return psycopg2.connect(
        dbname="nba",
        user="postgres",
        password="sibi",
        host="localhost",
        port="5432"
    )

# === Rename Maps ===
RENAME_MAPS = {
    # "boxscore_traditional_team_v3": {
    #     "gameId": "game_id",
    #     "teamId": "team_id",
    #     "teamCity": "team_city",
    #     "teamName": "team_name",
    #     "teamTricode": "team_tricode",
    #     "teamSlug": "team_slug",
    #     "minutes": "minutes",
    #     "fieldGoalsMade": "field_goals_made",
    #     "fieldGoalsAttempted": "field_goals_attempted",
    #     "fieldGoalsPercentage": "field_goals_percentage",
    #     "threePointersMade": "three_pointers_made",
    #     "threePointersAttempted": "three_pointers_attempted",
    #     "threePointersPercentage": "three_pointers_percentage",
    #     "freeThrowsMade": "free_throws_made",
    #     "freeThrowsAttempted": "free_throws_attempted",
    #     "freeThrowsPercentage": "free_throws_percentage",
    #     "reboundsOffensive": "rebounds_offensive",
    #     "reboundsDefensive": "rebounds_defensive",
    #     "reboundsTotal": "rebounds_total",
    #     "assists": "assists",
    #     "steals": "steals",
    #     "blocks": "blocks",
    #     "turnovers": "turnovers",
    #     "foulsPersonal": "fouls_personal",
    #     "points": "points",
    #     "plusMinusPoints": "plus_minus_points",
    #     "startersBench": "starters_bench",
    # },
    "boxscore_advanced_team_v3": {
        "gameId": "game_id",
        "teamId": "team_id",
        "teamCity": "team_city",
        "teamName": "team_name",
        "teamTricode": "team_tricode",
        "teamSlug": "team_slug",
        "minutes": "minutes",
        "estimatedOffensiveRating": "estimated_offensive_rating",
        "offensiveRating": "offensive_rating",
        "estimatedDefensiveRating": "estimated_defensive_rating",
        "defensiveRating": "defensive_rating",
        "estimatedNetRating": "estimated_net_rating",
        "netRating": "net_rating",
        "assistPercentage": "assist_percentage",
        "assistToTurnover": "assist_to_turnover",
        "assistRatio": "assist_ratio",
        "offensiveReboundPercentage": "offensive_rebound_percentage",
        "defensiveReboundPercentage": "defensive_rebound_percentage",
        "reboundPercentage": "rebound_percentage",
        "estimatedTeamTurnoverPercentage": "estimated_team_turnover_percentage",
        "turnoverRatio": "turnover_ratio",
        "effectiveFieldGoalPercentage": "effective_field_goal_percentage",
        "trueShootingPercentage": "true_shooting_percentage",
        "usagePercentage": "usage_percentage",
        "estimatedUsagePercentage": "estimated_usage_percentage",
        "estimatedPace": "estimated_pace",
        "pace": "pace",
        "pacePer40": "pace_per40",
        "possessions": "possessions",
        "PIE": "pie",
    },
    # "boxscore_misc_team_v3": {
    #     "gameId": "game_id",
    #     "teamId": "team_id",
    #     "teamCity": "team_city",
    #     "teamName": "team_name",
    #     "teamTricode": "team_tricode",
    #     "teamSlug": "team_slug",
    #     "minutes": "minutes",
    #     "pointsOffTurnovers": "points_off_turnovers",
    #     "pointsSecondChance": "points_second_chance",
    #     "pointsFastBreak": "points_fast_break",
    #     "pointsPaint": "points_paint",
    #     "oppPointsOffTurnovers": "opp_points_off_turnovers",
    #     "oppPointsSecondChance": "opp_points_second_chance",
    #     "oppPointsFastBreak": "opp_points_fast_break",
    #     "oppPointsPaint": "opp_points_paint",
    #     "blocks": "blocks",
    #     "blocksAgainst": "blocks_against",
    #     "foulsPersonal": "fouls_personal",
    #     "foulsDrawn": "fouls_drawn",
    # },
    "boxscore_fourfactors_team_v3": {
        "gameId": "game_id",
        "teamId": "team_id",
        "teamCity": "team_city",
        "teamName": "team_name",
        "teamTricode": "team_tricode",
        "teamSlug": "team_slug",
        "minutes": "minutes",
        "effectiveFieldGoalPercentage": "effective_field_goal_percentage",
        "freeThrowAttemptRate": "free_throw_attempt_rate",
        "teamTurnoverPercentage": "team_turnover_percentage",
        "offensiveReboundPercentage": "offensive_rebound_percentage",
        "oppEffectiveFieldGoalPercentage": "opp_effective_field_goal_percentage",
        "oppFreeThrowAttemptRate": "opp_free_throw_attempt_rate",
        "oppTeamTurnoverPercentage": "opp_team_turnover_percentage",
        "oppOffensiveReboundPercentage": "opp_offensive_rebound_percentage",
    },
    "boxscore_usage_team_v3": {
        "gameId": "game_id",
        "teamId": "team_id",
        "teamCity": "team_city",
        "teamName": "team_name",
        "teamTricode": "team_tricode",
        "teamSlug": "team_slug",
        "minutes": "minutes",
        "usagePercentage": "usage_percentage",
        "percentageFieldGoalsMade": "pct_field_goals_made",
        "percentageFieldGoalsAttempted": "pct_field_goals_attempted",
        "percentageThreePointersMade": "pct_three_pointers_made",
        "percentageThreePointersAttempted": "pct_three_pointers_attempted",
        "percentageFreeThrowsMade": "pct_free_throws_made",
        "percentageFreeThrowsAttempted": "pct_free_throws_attempted",
        "percentageReboundsOffensive": "pct_rebounds_offensive",
        "percentageReboundsDefensive": "pct_rebounds_defensive",
        "percentageReboundsTotal": "pct_rebounds_total",
        "percentageAssists": "pct_assists",
        "percentageTurnovers": "pct_turnovers",
        "percentageSteals": "pct_steals",
        "percentageBlocks": "pct_blocks",
        "percentageBlocksAllowed": "pct_blocks_allowed",
        "percentagePersonalFouls": "pct_personal_fouls",
        "percentagePersonalFoulsDrawn": "pct_personal_fouls_drawn",
        "percentagePoints": "pct_points",
    }
}

# === Helpers ===
def convert_minutes(val):
    if isinstance(val, str) and ":" in val:
        mins, secs = val.split(":")
        return int(mins) + int(secs) / 60.0
    return val

def insert_team_data(cursor, table_name, df, season, rename_map):
    df = df.copy()
    df["season"] = season

    df.rename(columns=rename_map, inplace=True)

    if "minutes" in df.columns:
        df["minutes"] = df["minutes"].apply(convert_minutes)

    columns = list(df.columns)
    values = list(df.itertuples(index=False, name=None))

    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """
    execute_batch(cursor, query, values, page_size=100)

def get_team_dfs(endpoint_func, game_id):
    resp = endpoint_func(game_id=game_id)
    frames = resp.get_data_frames()
    return [df for df in frames if "personId" not in df.columns]

# === Master Update Function ===
def update_team_boxscores(seasons, endpoints):
    conn = get_connection()
    cur = conn.cursor()

    endpoint_map = {
        # "traditional": (boxscoretraditionalv3.BoxScoreTraditionalV3, "boxscore_traditional_team_v3"),
        "advanced": (boxscoreadvancedv3.BoxScoreAdvancedV3, "boxscore_advanced_team_v3"),
        # "misc": (boxscoremiscv3.BoxScoreMiscV3, "boxscore_misc_team_v3"),
        "fourfactors": (boxscorefourfactorsv3.BoxScoreFourFactorsV3, "boxscore_fourfactors_team_v3"),
        "usage": (boxscoreusagev3.BoxScoreUsageV3, "boxscore_usage_team_v3")
    }

    for season in seasons:
        print(f"\n📅 Updating season {season}")

        for endpoint in endpoints:
            ep_func, table_name = endpoint_map[endpoint]
            rename_map = RENAME_MAPS.get(table_name, {})

            # get games missing from this table
            cur.execute(f"""
                SELECT g.game_id
                FROM games g
                WHERE g.season = %s
                AND NOT EXISTS (
                    SELECT 1 FROM {table_name} t WHERE t.game_id = g.game_id
                )
                ORDER BY g.game_id;
            """, (season,))
            game_ids = [row[0] for row in cur.fetchall()]
            print(f"   ↳ {endpoint} → {len(game_ids)} games missing")

            for idx, game_id in enumerate(game_ids, 1):
                print(f"      ({idx}/{len(game_ids)}) Fetching {endpoint} for {game_id}")
                try:
                    team_frames = get_team_dfs(ep_func, game_id)
                    for tf in team_frames:
                        insert_team_data(cur, table_name, tf, season, rename_map)
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ Failed for game {game_id} / {endpoint}: {e}")
                    conn.rollback()
                    
                time.sleep(0.6)


    cur.close()
    conn.close()


if __name__ == "__main__":
    # Example: update multiple seasons + endpoints
    update_team_boxscores(
        seasons=[2020],
        endpoints=["usage", "advanced", "fourfactors"]
    )


import os
import pandas as pd

def calculate_cumulative_allowed_averages(
    input_csv="data/LeagueGameLogs/TeamGameLogs_2024_25.csv",
    output_csv="data/processed/team_defense_cumavg.csv"
):
    # Load and parse game dates
    df = pd.read_csv(input_csv)
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    # Columns needed
    base_cols = [
        "GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_DATE",
        "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTA",
        "REB", "DREB", "OREB", "AST", "TOV", "STL", "BLK", "PF"
    ]
    team_stats = df[base_cols].copy()

    # Merge opponent stats via GAME_ID
    merged = pd.merge(
        team_stats,
        team_stats,
        on="GAME_ID",
        suffixes=('', '_OPP')
    )
    merged = merged[merged["TEAM_ID"] != merged["TEAM_ID_OPP"]]

    # Rename opponent stats for clarity
    stat_map = {
        "PTS": "PTS",
        "FGM": "FGM",
        "FGA": "FGA",
        "FG_PCT": "FG_PCT",
        "FG3M": "FG3M",
        "FG3A": "FG3A",
        "FG3_PCT": "FG3_PCT",
        "FTA": "FTA",
        "REB": "REB",
        "DREB": "DREB",
        "OREB": "OREB",
        "AST": "AST",
        "TOV": "TOV",
        "STL": "STL",
        "BLK": "BLK",
        "PF": "PF"
    }

    for stat in stat_map.keys():
        merged[stat_map[stat]] = merged[f"{stat}_OPP"]

    # Sort by team/date
    merged = merged.sort_values(by=["TEAM_ID", "GAME_DATE"])

    # Compute cumulative averages per team (excluding current game)
    for stat in stat_map.values():
        merged[stat] = (
            merged.groupby("TEAM_ID")[stat]
            .transform(lambda x: x.shift().expanding().mean())
        )

    # Drop first games
    merged = merged.dropna(subset=stat_map.values())

    # Rename columns for output
    merged = merged.rename(columns={
        "GAME_DATE": "DATE",
        "TEAM_ABBREVIATION": "TEAM"
    })

    # Final column list
    result_cols = ["DATE", "TEAM"] + list(stat_map.values())
    result = merged[result_cols].copy()

    # Save
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result.to_csv(output_csv, index=False)
    print(f"✅ Saved cumulative defensive averages to {output_csv}")

# Run it
calculate_cumulative_allowed_averages()

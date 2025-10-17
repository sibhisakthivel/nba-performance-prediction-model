from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
from pathlib import Path

def export_leaguegamelog_combined(seasons: list, out_dir: str):
    """
    Export LeagueGameLog for both regular season and playoffs into one CSV per season.
    
    Args:
        seasons (list): List of season strings, e.g. ["2022-23", "2023-24", "2024-25"]
        out_dir (str): Output directory for CSV files
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    for season in seasons:
        combined = []

        for stype in ["Regular Season", "Playoffs"]:
            log = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=stype
            )
            df = log.get_data_frames()[0]
            df["SEASON_TYPE"] = stype  # tag Regular/Playoffs
            combined.append(df)

        df_all = pd.concat(combined, ignore_index=True)

        out_path = Path(out_dir) / f"leaguegamelog_{season.replace('-', '')}.csv"
        df_all.to_csv(out_path, index=False)

        print(f"✅ Exported {len(df_all)} rows for {season} → {out_path}")

# Example usage:
export_leaguegamelog_combined(
    seasons=["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"],
    out_dir="/Users/sibhisibbye/vscode/NBA/gamelogs"
)

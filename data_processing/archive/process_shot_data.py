import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

def aggregate_team_shot_data_by_game(input_folder, output_folder, movement_types, shot_zones, shot_types, shot_ranges):
    def sorted_game_files():
        def extract_date(filename):
            try:
                parts = filename.split('_')
                date_str = ' '.join(parts[2:5])
                return datetime.strptime(date_str.replace(',', ''), '%b %d %Y')
            except Exception:
                return datetime.min

        files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
        files.sort(key=extract_date)
        return files

    os.makedirs(output_folder, exist_ok=True)

    def get_range(dist):
        if dist < 8:
            return '< 8 ft'
        elif dist < 16:
            return '8-16 ft'
        elif dist < 24:
            return '16-24 ft'
        else:
            return '24+ ft'

    def normalize_zone(zone):
        return 'Paint' if zone == 'In The Paint (Non-RA)' else zone

    movement_map = {
        'Driving': ['driving', 'drive'],
        'ISO': ['turnaround', 'pullup', 'step back'],
        'Putback': ['putback', 'tip'],
        'Cutting': ['cutting', 'alley oop'],
        'Static': ['jump shot', 'layup', 'hook', 'fadeaway', 'reverse', 'running']
    }

    def categorize_movement(action):
        action = action.lower()
        for move, keywords in movement_map.items():
            if any(keyword in action for keyword in keywords):
                return move
        return 'Static'

    type_map = {
        'jump': 'Jumpshot',
        'layup': 'Layup',
        'dunk': 'Dunk',
        'hook': 'Hook',
        'fadeaway': 'Fadeaway'
    }

    def get_type(action):
        action = action.lower()
        for key, val in type_map.items():
            if key in action:
                return val
        return 'Other'

    for file in sorted_game_files():
        df = pd.read_csv(os.path.join(input_folder, file))
        if df.empty or 'PLAYER_NAME' not in df.columns:
            print(f"⚠️ Skipping malformed or incomplete file: {file}")
            continue

        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        df = df.sort_values(by="GAME_DATE").reset_index(drop=True)

        game_id = df['GAME_ID'].iloc[0]
        game_date = df['GAME_DATE'].iloc[0]
        player_totals = defaultdict(lambda: defaultdict(int))
        player_info = {}
        team = None

        for _, row in df.iterrows():
            player = row['PLAYER_NAME'].strip()
            team = row['TEAM_NAME']
            made = row['SHOT_MADE_FLAG']
            action = row['ACTION_TYPE']
            zone = normalize_zone(row['SHOT_ZONE_BASIC'])
            dist = row['SHOT_DISTANCE']
            rng = get_range(dist)
            move = categorize_movement(action)
            shot_type = get_type(action)
            pt_type_label = '2pt' if '2PT' in row['SHOT_TYPE'] else '3pt'

            player_info[player] = team
            for key in [pt_type_label, move, rng, zone, shot_type, f'{zone} × {rng}', f'{shot_type} × {rng}']:
                player_totals[player][f'{key} FGA'] += 1
                player_totals[player][f'{key} FGM'] += made

        all_rows = []
        team_totals = defaultdict(int)

        for player, stats in player_totals.items():
            row_data = {
                'PLAYER': player,
                'TEAM': player_info[player],
                'GAME_ID': game_id,
                'GAME_DATE': game_date
            }

            def add_group(features):
                group_fga = sum(stats[f'{k} FGA'] for k in features if f'{k} FGA' in stats)
                group_fgm = sum(stats[f'{k} FGM'] for k in features if f'{k} FGM' in stats)
                for f in features:
                    fga = stats.get(f'{f} FGA', 0)
                    fgm = stats.get(f'{f} FGM', 0)
                    row_data[f'{f} FGA'] = fga
                    row_data[f'{f} FGA%'] = round(fga / group_fga * 100, 2) if group_fga > 0 else 0
                    row_data[f'{f} FGM'] = fgm
                    row_data[f'{f} FGM%'] = round(fgm / group_fgm * 100, 2) if group_fgm > 0 else 0
                    row_data[f'{f} FG%'] = round(fgm / fga * 100, 2) if fga > 0 else 0

                    team_totals[f'{f} FGA'] += fga
                    team_totals[f'{f} FGM'] += fgm

            add_group(['2pt', '3pt'])
            add_group(movement_types)
            add_group(shot_ranges)
            add_group(shot_zones)
            add_group(shot_types)
            add_group([f"{z} × {r}" for z in shot_zones for r in shot_ranges])
            add_group([f"{t} × {r}" for t in shot_types for r in shot_ranges])

            all_rows.append(row_data)

        # Generate team row
        team_row = {
            'PLAYER': 'TEAM',
            'TEAM': team,
            'GAME_ID': game_id,
            'GAME_DATE': game_date
        }
        for col in team_totals:
            if 'FGA' in col or 'FGM' in col:
                team_row[col] = team_totals[col]
        for col in list(team_totals):
            if col.endswith('FGA'):
                group = col.replace(' FGA', '')
                fga = team_totals.get(f'{group} FGA', 0)
                fgm = team_totals.get(f'{group} FGM', 0)
                team_row[f'{group} FG%'] = round(fgm / fga * 100, 2) if fga > 0 else 0

        all_rows.append(team_row)

        df_out = pd.DataFrame(all_rows)
        df_out = df_out.sort_values(by="GAME_DATE").reset_index(drop=True)
        output_file = os.path.join(output_folder, f"team_summary_2024-25_game_{game_id}.csv")
        df_out.to_csv(output_file, index=False)
        print(f"✅ Saved {len(all_rows)} player/team rows to {output_file}")

import unicodedata

def normalize_name(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8').strip()

def compute_rolling_averages(input_folder, team_output_path, player_output_root, players_to_track):
    files = [f for f in os.listdir(input_folder) if f.endswith(".csv") and 'team_summary' in f]

    def extract_date_from_file(file):
        path = os.path.join(input_folder, file)
        try:
            df = pd.read_csv(path)
            if df.empty or 'GAME_DATE' not in df.columns:
                print(f"⚠️ Skipping empty or malformed file during sort: {file}")
                return datetime.min
            return pd.to_datetime(df['GAME_DATE'].iloc[0])
        except Exception as e:
            print(f"⚠️ Error reading {file}: {e}")
            return datetime.min

    files = sorted(files, key=extract_date_from_file)

    # Normalize player names for consistency
    players_to_track = [normalize_name(p) for p in players_to_track]
    player_history = {p: [] for p in players_to_track}
    team_rows = []

    os.makedirs(player_output_root, exist_ok=True)
    player_out = {p: [] for p in players_to_track}

    for idx, file in enumerate(files):
        df = pd.read_csv(os.path.join(input_folder, file))
        print(f"🔍 File: {file} — Unique PLAYER values: {df['PLAYER'].unique()}")
        if df.empty:
            continue
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

        for _, row in df.iterrows():
            name = normalize_name(row["PLAYER"])
            if name.strip().upper() in ['TEAM', 'TEAM_TOTAL', 'TEAM TOTAL']:
                team_rows.append(row)
            elif name in players_to_track:
                player_history[name].append(row)

        for player in players_to_track:
            if len(player_history[player]) < 2:
                continue

            avg_row = {
                "PLAYER": player,
                "GAME_ID": df["GAME_ID"].iloc[0],
                "GAME_DATE": df["GAME_DATE"].iloc[0]
            }
            sample = player_history[player][:-1] if player in df["PLAYER"].apply(normalize_name).values else player_history[player]

            for col in sample[0].index:
                if 'FGA' in col or 'FGM' in col:
                    avg_row[col] = sum(r[col] for r in sample if col in r) / len(sample)
            for col in sample[0].index:
                if col.endswith('FGA%'):
                    base = col.replace('FGA%', 'FGA')
                    total = sum(avg_row.get(base, 0) for base in avg_row if base.endswith('FGA'))
                    avg_row[col] = round((avg_row.get(base, 0) / total * 100), 2) if total > 0 else 0
                elif col.endswith('FGM%'):
                    base = col.replace('FGM%', 'FGM')
                    total = sum(avg_row.get(base, 0) for base in avg_row if base.endswith('FGM'))
                    avg_row[col] = round((avg_row.get(base, 0) / total * 100), 2) if total > 0 else 0
                elif col.endswith('FG%'):
                    base_fga = col.replace(' FG%', ' FGA')
                    base_fgm = col.replace(' FG%', ' FGM')
                    fga = avg_row.get(base_fga, 0)
                    fgm = avg_row.get(base_fgm, 0)
                    avg_row[col] = round((fgm / fga * 100), 2) if fga > 0 else 0

            player_out[player].append(avg_row)

    for player, rows in player_out.items():
        if not rows:
            print(f"⚠️ No rows found for {player}, skipping file save.")
            continue
        path = os.path.join(player_output_root, f"{player.replace(' ', '_')}_rolling_avg.csv")
        pd.DataFrame(rows).sort_values("GAME_DATE").to_csv(path, index=False)
        print(f"✅ Saved {len(rows)} rolling rows for {player} to {path}")

    team_out = []
    for i in range(1, len(team_rows)):
        rows = team_rows[:i]
        avg_row = {
            "PLAYER": "TEAM",
            "GAME_ID": team_rows[i].get("GAME_ID"),
            "GAME_DATE": team_rows[i].get("GAME_DATE")
        }
        for col in team_rows[0].index:
            if 'FGA' in col or 'FGM' in col:
                avg_row[col] = sum(r[col] for r in rows if col in r) / i
        for col in team_rows[0].index:
            if col.endswith('FGA%'):
                base = col.replace('FGA%', 'FGA')
                total = sum(avg_row.get(base, 0) for base in avg_row if base.endswith('FGA'))
                avg_row[col] = round((avg_row.get(base, 0) / total * 100), 2) if total > 0 else 0
            elif col.endswith('FGM%'):
                base = col.replace('FGM%', 'FGM')
                total = sum(avg_row.get(base, 0) for base in avg_row if base.endswith('FGM'))
                avg_row[col] = round((avg_row.get(base, 0) / total * 100), 2) if total > 0 else 0
            elif col.endswith('FG%'):
                base_fga = col.replace(' FG%', ' FGA')
                base_fgm = col.replace(' FG%', ' FGM')
                fga = avg_row.get(base_fga, 0)
                fgm = avg_row.get(base_fgm, 0)
                avg_row[col] = round((fgm / fga * 100), 2) if fga > 0 else 0
        team_out.append(avg_row)

    df_team_out = pd.DataFrame(team_out)
    if "GAME_DATE" not in df_team_out.columns or df_team_out["GAME_DATE"].isnull().all():
        print("⚠️ GAME_DATE missing or all null in team output — skipping sort")
        df_team_out.to_csv(team_output_path, index=False)
    else:
        df_team_out = df_team_out.dropna(subset=["GAME_DATE"])
        df_team_out["GAME_DATE"] = pd.to_datetime(df_team_out["GAME_DATE"])
        df_team_out.sort_values("GAME_DATE").to_csv(team_output_path, index=False)
        print(f"✅ Saved {len(df_team_out)} team rolling rows to {team_output_path}")

if __name__ == "__main__":
    movement_types = ['Driving', 'ISO', 'Putback', 'Cutting', 'Static']
    shot_ranges = ['< 8 ft', '8-16 ft', '16-24 ft', '24+ ft']
    shot_zones = ['Restricted Area', 'Paint', 'Mid-Range', 'Left Corner 3', 'Right Corner 3', 'Above the Break 3', 'Backcourt']
    shot_types = ['Jumpshot', 'Layup', 'Dunk', 'Hook', 'Fadeaway', 'Other']

    input_folder = "raw_data/24-25/shot_data/nuggets/opp"
    output_folder = "processed_data/24-25/shot_data/nuggets/opp"
    team_output_path = "processed_data/24-25/shot_data/nuggets/opp_rolling_avg.csv"
    player_output_root = "processed_data/24-25/shot_data/nuggets"

    aggregate_team_shot_data_by_game(
        input_folder=input_folder,
        output_folder=output_folder,
        movement_types=movement_types,
        shot_zones=shot_zones,
        shot_types=shot_types,
        shot_ranges=shot_ranges
    )

    compute_rolling_averages(
        input_folder=output_folder,
        team_output_path=team_output_path,
        player_output_root=player_output_root,
        players_to_track=[]
    )

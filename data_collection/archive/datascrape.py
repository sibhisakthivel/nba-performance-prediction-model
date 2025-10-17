import os
import time
import pandas as pd
import unicodedata
import nba_api.stats.endpoints as endpoints
from nba_api.stats.endpoints import shotchartdetail, playergamelog, teamgamelog
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    PlayerGameLog, TeamGameLog, ShotChartDetail, BoxScoreTraditionalV2, BoxScoreAdvancedV2,
    BoxScoreFourFactorsV2, BoxScoreMiscV2, BoxScorePlayerTrackV2
)

def get_jokic_shot_data_by_game(season='2024-25', output_folder='raw_data/24-25/shot_data/jokic'):
    """
    Retrieve Nikola Jokic's shot chart data for each game in the 2024-25 season
    and save each game's data to a separate CSV file.
    
    Parameters:
    season (str): NBA season in format 'YYYY-YY' (default: '2024-25')
    output_folder (str): Folder to save CSV files (default: 'jokic_shot_data')
    """
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get Nikola Jokic's player ID
    jokic = players.find_players_by_full_name('Nikola Jokic')[0]
    player_id = jokic['id']
    print(f"Found Nikola Jokic - Player ID: {player_id}")
    
    # Get Jokic's game log for the season to get all game IDs
    try:
        game_log = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star='Regular Season'
        )
        games_df = game_log.get_data_frames()[0]
        print(f"Found {len(games_df)} games for {season} season")
    except Exception as e:
        print(f"Error retrieving game log: {e}")
        return
    
    # Process each game
    successful_games = 0
    failed_games = 0
    
    for index, game in games_df.iterrows():
        game_id = game['Game_ID']
        game_date = game['GAME_DATE']
        matchup = game['MATCHUP']
        
        print(f"Processing Game {index + 1}/{len(games_df)}: {game_date} - {matchup}")
        
        try:
            # Get shot chart data for this specific game
            shot_chart = shotchartdetail.ShotChartDetail(
                team_id=0,  # 0 for all teams
                player_id=player_id,
                game_id_nullable=game_id,
                season_nullable=season,
                season_type_all_star='Regular Season',
                context_measure_simple='FGA'  # Field Goal Attempts
            )
            
            # Get the shot data
            shot_data = shot_chart.get_data_frames()[0]  # First dataframe contains shot details
            
            if not shot_data.empty:
                # Create filename with game date and opponent
                opponent = matchup.split(' ')[-1]  # Get opponent team abbreviation
                filename = f"jokic_shots_{game_date}_{opponent}_game_{game_id}.csv"
                filepath = os.path.join(output_folder, filename)
                
                # Save to CSV
                shot_data.to_csv(filepath, index=False)
                print(f"  ✓ Saved {len(shot_data)} shots to {filename}")
                successful_games += 1
            else:
                print(f"  ⚠ No shot data found for game {game_id}")
                failed_games += 1
            
            # Rate limiting - NBA API has rate limits
            time.sleep(0.5)  # Wait 500ms between requests
            
        except Exception as e:
            print(f"  ✗ Error processing game {game_id}: {e}")
            failed_games += 1
            time.sleep(1)  # Wait longer on error
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed: {successful_games} games")
    print(f"Failed: {failed_games} games")
    print(f"Files saved to: {output_folder}/")

def analyze_shot_data_sample(output_folder='raw_data/24-25/shot_data/jokic'):
    """
    Helper function to analyze a sample of the shot data to understand the structure
    """
    csv_files = [f for f in os.listdir(output_folder) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the output folder")
        return
    
    # Load first CSV file as sample
    sample_file = csv_files[0]
    sample_path = os.path.join(output_folder, sample_file)
    df = pd.read_csv(sample_path)
    
    print(f"\n=== Sample Data Analysis ===")
    print(f"Sample file: {sample_file}")
    print(f"Number of shots: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Show shot outcome distribution
    if 'SHOT_MADE_FLAG' in df.columns:
        print(f"\nShot outcomes:")
        print(df['SHOT_MADE_FLAG'].value_counts())
    
    # Show shot types
    if 'ACTION_TYPE' in df.columns:
        print(f"\nShot types:")
        print(df['ACTION_TYPE'].value_counts())

# if __name__ == "__main__":
#     # Run the main function
#     get_jokic_shot_data_by_game()
    
#     # Analyze a sample of the data
#     analyze_shot_data_sample()

def fetch_boxscore_data(player_name, season, endpoint, output_folder):
    # 🔍 Get player ID
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        print(f"❌ Player '{player_name}' not found.")
        return
    player_id = player_dict[0]['id']

    # 📋 Get player's game logs
    game_log = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
    game_df = game_log.get_data_frames()[0]
    game_ids = game_df['Game_ID'].tolist()
    all_data = []

    # 🧠 Load the endpoint class
    try:
        boxscore_class = getattr(endpoints, endpoint)
    except AttributeError:
        print(f"❌ Endpoint '{endpoint}' is invalid or not found.")
        return

    for game_id in game_ids:
        try:
            response = boxscore_class(game_id=game_id)
            df = response.get_data_frames()[0]

            # Filter only the row corresponding to our player
            player_row = df[df.get('PLAYER_ID') == player_id] if 'PLAYER_ID' in df.columns else pd.DataFrame()

            if not player_row.empty:
                all_data.append(player_row)
            else:
                print(f"⚠️ {player_name} not found in {endpoint} for Game ID {game_id}")
                # Append placeholder row with at least GAME_ID and PLAYER_ID for alignment
                placeholder = pd.DataFrame([{
                    'PLAYER_ID': player_id,
                    'GAME_ID': game_id,
                    'NOTE': 'Player data not found in this boxscore'
                }])
                all_data.append(placeholder)

        except Exception as e:
            print(f"❌ Error fetching {endpoint} for Game ID {game_id}: {e}")
            continue

        time.sleep(0.6)  # ⏱ Rate limiting

    if not all_data:
        print(f"⚠️ No data found for {player_name}, {season}, {endpoint}")
        return

    final_df = pd.concat(all_data, ignore_index=True)

    # 📁 Save to output folder
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{endpoint}_{season.replace('-', '')}.csv")
    final_df.to_csv(output_path, index=False)
    print(f"✅ Saved {endpoint} data for {player_name} to {output_path}")

# fetch_boxscore_data(
#     player_name="Nikola Jokic",
#     season="2024-25",
#     endpoint="BoxScoreTraditionalV2",
#     output_folder="raw_data/24-25/box_scores/jokic"
# )

def update_missing_games(file_path, missing_game_data):
    """
    Updates or adds missing games in a boxscore CSV, matching by GAME_ID.
    Preserves original row order.
    """
    df = pd.read_csv(file_path, dtype={'GAME_ID': str})  # Keep GAME_ID as string

    for game_data in missing_game_data:
        game_id = str(game_data['GAME_ID']).zfill(10)
        game_data['GAME_ID'] = game_id

        new_row = pd.DataFrame([game_data])
        new_row = new_row.reindex(columns=df.columns, fill_value='')

        if game_id in df['GAME_ID'].values:
            df.loc[df['GAME_ID'] == game_id] = new_row.values
            print(f"🔁 Updated game {game_id}")
        else:
            df = pd.concat([df, new_row], ignore_index=True)
            print(f"➕ Added game {game_id}")

    df.reset_index(drop=True, inplace=True)
    df.to_csv(file_path, index=False)
    print(f"✅ File updated: {file_path}")

missing_game_ids = ["0022401193", "0022401180"]

file_path = "raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv"

missing_game_data = [
    {
        "GAME_ID": "0022401180",
        "PLAYER_NAME": "Nikola Jokic",
        "TEAM_ID": 1610612743,
        "TEAM_ABBREVIATION": "DEN",
        "MIN": 41,
        "PTS": 26,
        "OREB": 3,
        "DREB": 13,
        "REB": 16,
        "AST": 13,
        "FGM": 11,
        "FGA": 19,
        "FG_PCT": 0.579,
        "FG3M": 1,
        "FG3A": 2,
        "FG3_PCT": 0.500,
        "FTM": 3,
        "FTA": 7,
        "FT_PCT": 0.429,
        "STL": 2,
        "BLK": 0,
        "TO": 5,
        "PF": 3,
        "PLUS_MINUS": 11
    },
    {
        "GAME_ID": "0022401193",
        "PLAYER_NAME": "Nikola Jokic",
        "TEAM_ID": 1610612743,
        "TEAM_ABBREVIATION": "DEN",
        "MIN": 31,
        "PTS": 18,
        "OREB": 1,
        "DREB": 6,
        "REB": 7,
        "AST": 7,
        "FGM": 7,
        "FGA": 10,
        "FG_PCT": 0.700,
        "FG3M": 3,
        "FG3A": 5,
        "FG3_PCT": 0.600,
        "FTM": 1,
        "FTA": 2,
        "FT_PCT": 0.500,
        "STL": 2,
        "BLK": 1,
        "TO": 1,
        "PF": 3,
        "PLUS_MINUS": 34
    }
]

# update_missing_games(file_path, missing_game_data)

def fetch_team_data(team_name, season, endpoint, output_folder):
    # 🔍 Get team ID
    team_dict = teams.find_teams_by_full_name(team_name)
    if not team_dict:
        print(f"❌ Team '{team_name}' not found.")
        return
    team_id = team_dict[0]['id']
    team_abbr = team_dict[0]['abbreviation']

    # 🧠 Load the endpoint class
    try:
        endpoint_class = getattr(endpoints, endpoint)
    except AttributeError:
        print(f"❌ Endpoint '{endpoint}' is invalid or not found.")
        return

    print(f"📦 Fetching {endpoint} data for {team_name} ({season})...")

    try:
        if endpoint == "TeamGameLogs":
            response = endpoint_class(season_nullable=season, team_id_nullable=team_id)
        elif endpoint == "TeamEstimatedMetrics":
            response = endpoint_class(season=season)
        elif endpoint in ["LeagueDashTeamShotLocations", "LeagueDashTeamPtShot"]:
            response = endpoint_class(season=season, team_id=team_id)
        else:
            print(f"⚠️ Custom handling not defined for endpoint '{endpoint}'")
            return
        df = response.get_data_frames()[0]

        # Optionally filter if endpoint returns league-wide data
        if "TEAM_ID" in df.columns and endpoint != "TeamGameLogs":
            df = df[df["TEAM_ID"] == team_id]

        # 📁 Save to output folder
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f"{team_abbr}_{endpoint}_{season.replace('-', '')}.csv")
        df.to_csv(output_path, index=False)
        print(f"✅ Saved data to {output_path}")

    except Exception as e:
        print(f"❌ Error fetching {endpoint} for {team_name}: {e}")
    
# fetch_team_data(team_name='Denver Nuggets', 
#                 season='2024-25', 
#                 endpoint='TeamGameLogs', 
#                 output_folder='raw_data/24-25/shot_data/nuggets')

def extract_game_id_splits(team_gamelog_csv):
    df = pd.read_csv(team_gamelog_csv)

    # Sanity check for required columns
    required_cols = {'GAME_ID', 'MATCHUP', 'WL'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    # Standardize column types
    df['MATCHUP'] = df['MATCHUP'].astype(str)
    df['WL'] = df['WL'].astype(str)

    # Home/Away classification based on "vs." or "@"
    df['IS_HOME'] = df['MATCHUP'].str.contains(r'vs\.')
    df['IS_WIN'] = df['WL'] == 'W'

    # Extract GAME_IDs for each category
    home_game_ids = df[df['IS_HOME']]['GAME_ID'].tolist()
    away_game_ids = df[~df['IS_HOME']]['GAME_ID'].tolist()
    win_game_ids = df[df['IS_WIN']]['GAME_ID'].tolist()
    loss_game_ids = df[~df['IS_WIN']]['GAME_ID'].tolist()

    return home_game_ids, away_game_ids, win_game_ids, loss_game_ids

home_game_ids, away_game_ids, win_game_ids, loss_game_ids = extract_game_id_splits(team_gamelog_csv='raw_data/24-25/box_scores/nuggets/DEN_TeamGameLogs_202425.csv')

# print(home_game_ids, away_game_ids, win_game_ids, loss_game_ids)

game_id_splits = [home_game_ids, away_game_ids, win_game_ids, loss_game_ids]

def filter_by_game_id_splits(input_csv, game_id_splits, output_dir):
    df = pd.read_csv(input_csv)

    if 'GAME_ID' not in df.columns:
        raise ValueError("The input CSV does not contain a 'GAME_ID' column.")

    # Automatically extract base name from input filename (before season suffix)
    filename = os.path.splitext(os.path.basename(input_csv))[0]  # e.g. 'BoxScoreTraditionalV2_202425'
    base_name = filename.split('_')[0]  # → 'BoxScoreTraditionalV2'

    split_labels = ['home', 'away', 'win', 'loss']

    for ids, label in zip(game_id_splits, split_labels):
        filtered_df = df[df['GAME_ID'].isin(ids)]
        output_path = os.path.join(output_dir, f"{base_name}_{label}.csv")
        filtered_df.to_csv(output_path, index=False)
        print(f"✅ Saved {label} games ({len(filtered_df)} rows) → {output_path}")
        
# filter_by_game_id_splits(input_csv='raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv',
#                           game_id_splits=game_id_splits, 
#                           output_dir='raw_data/24-25/box_scores/jokic')

def get_team_shot_data_by_game(season='2024-25', output_folder='raw_data/24-25/shot_data/nuggets', team_name='Denver Nuggets'):
    """
    Retrieve team shot chart data for each game in the given season
    and save each game's data to a separate CSV file.
    
    Parameters:
    season (str): NBA season in format 'YYYY-YY' (default: '2024-25')
    output_folder (str): Folder to save CSV files
    team_name (str): Full name of the team (default: 'Denver Nuggets')
    """
    os.makedirs(output_folder, exist_ok=True)

    # Find team ID
    team_info = [team for team in teams.get_teams() if team['full_name'] == team_name][0]
    team_id = team_info['id']
    print(f"Found team: {team_name} - Team ID: {team_id}")

    # Get team game log
    try:
        game_log = teamgamelog.TeamGameLog(
            team_id=team_id,
            season=season,
            season_type_all_star='Regular Season'
        )
        games_df = game_log.get_data_frames()[0]
        print(f"Found {len(games_df)} games for {season} season")
    except Exception as e:
        print(f"Error retrieving team game log: {e}")
        return

    successful = 0
    failed = 0

    for i, game in games_df.iterrows():
        game_id = game['Game_ID']
        game_date = game['GAME_DATE']
        matchup = game['MATCHUP']
        opponent = matchup.split(' ')[-1]

        filename = f"{team_info['abbreviation']}_shots_{game_date}_{opponent}_game_{game_id}.csv"
        filepath = os.path.join(output_folder, filename)

        # Skip if already exists
        if os.path.exists(filepath):
            print(f"Skipping Game {i + 1}/{len(games_df)} ({game_date} - {matchup}): Already saved.")
            successful += 1
            continue

        print(f"Processing Game {i + 1}/{len(games_df)}: {game_date} - {matchup}")

        try:
            shot_chart = shotchartdetail.ShotChartDetail(
                team_id=0,  # 0 for all teams (includes both teams in game)
                player_id=0,  # 0 to get all players
                game_id_nullable=game_id,
                season_nullable=season,
                season_type_all_star='Regular Season',
                context_measure_simple='FGA'
            )
            shot_data = shot_chart.get_data_frames()[0]

            if not shot_data.empty:
                shot_data.to_csv(filepath, index=False)
                print(f"  ✓ Saved {len(shot_data)} shots to {filename}")
                successful += 1
            else:
                print(f"  ⚠ No shot data found for game {game_id}")
                failed += 1
        except Exception as e:
            print(f"  ✗ Error processing game {game_id}: {e}")
            print(f"Retrying game {game_id}...")
            time.sleep(2)
            try:
                shot_chart = shotchartdetail.ShotChartDetail(
                    team_id=0,
                    player_id=0,
                    game_id_nullable=game_id,
                    season_nullable=season,
                    season_type_all_star='Regular Season',
                    context_measure_simple='FGA'
                )
                shot_data = shot_chart.get_data_frames()[0]
                if not shot_data.empty:
                    shot_data.to_csv(filepath, index=False)
                    print(f"  ✓ Saved {len(shot_data)} shots to {filename} on retry")
                    successful += 1
                else:
                    print(f"  ⚠ No shot data found for game {game_id} on retry")
                    failed += 1
            except Exception as retry_e:
                print(f"  ✗ Retry failed for game {game_id}: {retry_e}")
                failed += 1
            time.sleep(1)

        time.sleep(0.5)

    print(f"\n=== Summary ===")
    print(f"✅ Successfully processed: {successful} games")
    print(f"❌ Failed: {failed} games")
    print(f"📁 Files saved to: {output_folder}/")

# if __name__ == "__main__":
#     get_team_shot_data_by_game()

def save_team_shots_allowed_per_game(team_abbrev, season, out_dir, max_retries=3, sleep_time=0.6):
    os.makedirs(out_dir, exist_ok=True)

    # Map abbrev to team ID
    team_info = [team for team in teams.get_teams() if team['abbreviation'] == team_abbrev.upper()]
    if not team_info:
        raise ValueError(f"No team found with abbreviation '{team_abbrev}'")
    team_id = team_info[0]['id']

    # Get game log
    game_log = TeamGameLog(team_id=team_id, season=season).get_data_frames()[0]
    game_ids = game_log['Game_ID'].tolist()
    matchups = game_log['MATCHUP'].tolist()
    total_games = len(game_ids)

    # Abbrev -> ID map
    abbrev_to_id = {team['abbreviation']: team['id'] for team in teams.get_teams()}

    for idx, (game_id, matchup) in enumerate(zip(game_ids, matchups), start=1):
        opp_abbrev = matchup.split(' ')[-1]
        filename = f"{season}_{team_abbrev}_vs_{opp_abbrev}_{game_id}.csv"
        filepath = os.path.join(out_dir, filename)

        prefix = f"[{idx}/{total_games}]"

        if os.path.exists(filepath):
            print(f"{prefix} Skipped (already exists): {filename}")
            continue

        opp_id = abbrev_to_id.get(opp_abbrev)
        if not opp_id:
            print(f"{prefix} Skipped (unknown opponent): {opp_abbrev} in {matchup}")
            continue

        for attempt in range(max_retries):
            try:
                shots = ShotChartDetail(
                    team_id=opp_id,
                    player_id=0,
                    game_id_nullable=game_id,
                    context_measure_simple='FGA',
                    season_nullable=season
                ).get_data_frames()[0]

                shots['GAME_ID'] = game_id
                shots['DEFENDING_TEAM'] = team_abbrev
                shots['SHOOTING_TEAM'] = opp_abbrev

                shots.to_csv(filepath, index=False)
                print(f"{prefix} Saved: {filename}")
                break

            except Exception as e:
                print(f"{prefix} Attempt {attempt + 1} failed: {filename}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"{prefix} ❌ Failed after {max_retries} attempts: {filename}")

        time.sleep(sleep_time)

# save_team_shots_allowed_per_game('DEN', '2024-25', 'raw_data/24-25/shot_data/nuggets/opp')

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()

# def collect_player_injury_split_logs(player_name, teammates, season, base_out_dir, endpoints, manual_fallback_path=None):
#     os.makedirs(base_out_dir, exist_ok=True)

#     # Convert full season (e.g. '2024-25') to short (e.g. '24-25')
#     short_season = season[-5:]

#     # Load manual fallback CSV if provided
#     manual_df = None
#     if manual_fallback_path:
#         manual_df = pd.read_csv(manual_fallback_path)
#         manual_df['GAME_ID'] = manual_df['GAME_ID'].astype(str).str.zfill(10)
#         if 'GAME_DATE' in manual_df.columns:
#             manual_df['GAME_DATE'] = pd.to_datetime(manual_df['GAME_DATE'])

#     # Get player ID
#     all_players = players.get_players()
#     player_info = next(p for p in all_players if normalize(p['full_name']) == normalize(player_name))
#     player_id = player_info['id']

#     player_games_df = PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
#     player_games_df['GAME_DATE'] = pd.to_datetime(player_games_df['GAME_DATE'])

#     # Get teammate presence
#     teammate_presence = {}
#     for teammate_name in teammates:
#         teammate_info = next((p for p in all_players if normalize(p['full_name']) == normalize(teammate_name)), None)
#         if not teammate_info:
#             print(f"⚠️ Could not find teammate: {teammate_name}")
#             continue
#         teammate_id = teammate_info['id']
#         teammate_games = PlayerGameLog(player_id=teammate_id, season=season).get_data_frames()[0]
#         games_played = set(teammate_games['Game_ID'])
#         teammate_presence[teammate_name] = games_played
#         time.sleep(0.6)

#     # Process each teammate
#     for teammate_name in teammates:
#         if teammate_name not in teammate_presence:
#             continue

#         games_with = []
#         games_without = []

#         for _, row in player_games_df.iterrows():
#             gid = row['Game_ID']
#             if gid in teammate_presence[teammate_name]:
#                 games_with.append((gid, row['GAME_DATE']))
#             else:
#                 games_without.append((gid, row['GAME_DATE']))

#         # For WITH / WITHOUT groups
#         for status, games in [('with', games_with), ('without', games_without)]:
#             for endpoint in endpoints:
#                 out_dir = os.path.join(
#                     base_out_dir,
#                     short_season,
#                     'injury',
#                     player_name.replace(' ', '_'),
#                     f"{status}_{teammate_name.replace(' ', '_')}",
#                     endpoint
#                 )
#                 os.makedirs(out_dir, exist_ok=True)

#                 saved_count = 0

#                 for game_id, game_date in games:
#                     df = pd.DataFrame()

#                     # Retry loop
#                     for attempt in range(5):
#                         try:
#                             if endpoint == 'BoxScoreTraditionalV2':
#                                 df = BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
#                             elif endpoint == 'BoxScoreAdvancedV2':
#                                 df = BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0]
#                             elif endpoint == 'BoxScoreFourFactorsV2':
#                                 df = BoxScoreFourFactorsV2(game_id=game_id).get_data_frames()[0]
#                             elif endpoint == 'BoxScoreMiscV2':
#                                 df = BoxScoreMiscV2(game_id=game_id).get_data_frames()[0]
#                             elif endpoint == 'BoxScorePlayerTrackV2':
#                                 df = BoxScorePlayerTrackV2(game_id=game_id).get_data_frames()[0]
#                             else:
#                                 print(f"⚠️ Unsupported endpoint: {endpoint}")
#                                 break

#                             df = df[df['PLAYER_ID'] == player_id].copy()
#                             if not df.empty:
#                                 break  # success

#                         except Exception as e:
#                             if attempt < 2:
#                                 time.sleep(2 ** attempt)
#                             else:
#                                 print(f"⚠️ Final API failure: {endpoint} | Game {game_id}")
#                         time.sleep(0.6)

#                     # Fallback for TraditionalV2 only
#                     if df.empty and endpoint == 'BoxScoreTraditionalV2' and manual_df is not None and season == '2024-25':
#                         df = manual_df[manual_df['GAME_ID'] == game_id].copy()
#                         if df.empty:
#                             print(f"❌ Missing in both API and manual fallback: {game_id}")
#                             continue

#                     if df.empty:
#                         continue

#                     df['GAME_ID'] = game_id
#                     df['GAME_DATE'] = game_date

#                     out_file = os.path.join(out_dir, f"{game_id}.csv")
#                     df.to_csv(out_file, index=False)
#                     saved_count += 1

#                 print(f"📁 [{status.upper()}] {player_name} | {teammate_name} | {endpoint}: {saved_count} files saved to {out_dir}")

# def collect_player_injury_split_logs(player_name, teammates, season, base_out_dir, endpoints, manual_fallback_path=None):
#     os.makedirs(base_out_dir, exist_ok=True)

#     # Convert full season (e.g. '2024-25') to short (e.g. '24-25')
#     short_season = season[-5:]

#     # Load manual fallback CSV if provided
#     manual_df = None
#     if manual_fallback_path:
#         manual_df = pd.read_csv(manual_fallback_path)
#         manual_df['GAME_ID'] = manual_df['GAME_ID'].astype(str).str.zfill(10)
#         if 'GAME_DATE' in manual_df.columns:
#             manual_df['GAME_DATE'] = pd.to_datetime(manual_df['GAME_DATE'])

#     # Get player ID
#     all_players = players.get_players()
#     player_info = next(p for p in all_players if normalize(p['full_name']) == normalize(player_name))
#     player_id = player_info['id']

#     player_games_df = PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
#     player_games_df['GAME_DATE'] = pd.to_datetime(player_games_df['GAME_DATE'])

#     # Get teammate presence
#     teammate_presence = {}
#     for teammate_name in teammates:
#         teammate_info = next((p for p in all_players if normalize(p['full_name']) == normalize(teammate_name)), None)
#         if not teammate_info:
#             print(f"⚠️ Could not find teammate: {teammate_name}")
#             continue
#         teammate_id = teammate_info['id']
#         teammate_games = PlayerGameLog(player_id=teammate_id, season=season).get_data_frames()[0]
#         games_played = set(teammate_games['Game_ID'])
#         teammate_presence[teammate_name] = games_played
#         time.sleep(0.6)

#     # Process each teammate
#     for teammate_name in teammates:
#         if teammate_name not in teammate_presence:
#             continue

#         games_with = []
#         games_without = []

#         for _, row in player_games_df.iterrows():
#             gid = row['Game_ID']
#             if gid in teammate_presence[teammate_name]:
#                 games_with.append((gid, row['GAME_DATE']))
#             else:
#                 games_without.append((gid, row['GAME_DATE']))

#         # For WITH / WITHOUT groups
#         for status, games in [('with', games_with), ('without', games_without)]:
#             for endpoint in endpoints:
#                 out_dir = os.path.join(
#                     base_out_dir,
#                     short_season,
#                     'injury',
#                     player_name.replace(' ', '_'),
#                     f"{status}_{teammate_name.replace(' ', '_')}",
#                     endpoint
#                 )
#                 os.makedirs(out_dir, exist_ok=True)

#                 saved_count = 0

#                 for game_id, game_date in games:
#                     df = pd.DataFrame()

#                     if endpoint == 'BoxScoreTraditionalV2':
#                         for attempt in range(3):
#                             try:
#                                 df = BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
#                                 df = df[df['PLAYER_ID'] == player_id].copy()
#                                 if not df.empty:
#                                     break
#                             except Exception as e:
#                                 if attempt < 2:
#                                     time.sleep(2 ** attempt)
#                                 else:
#                                     print(f"⚠️ Final API failure for TraditionalV2 | Game {game_id} — trying fallback")

#                         if df.empty and manual_df is not None and season == '2024-25':
#                             df = manual_df[manual_df['GAME_ID'] == game_id].copy()
#                             if df.empty:
#                                 print(f"❌ Missing in both API and manual fallback: {game_id}")
#                                 continue

#                     elif endpoint == 'BoxScoreAdvancedV2':
#                         for attempt in range(3):
#                             try:
#                                 df = BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0]
#                                 df = df[df['PLAYER_ID'] == player_id].copy()
#                                 if not df.empty:
#                                     break
#                             except Exception as e:
#                                 if attempt < 2:
#                                     time.sleep(2 ** attempt)
#                                 else:
#                                     print(f"❌ Skipped AdvancedV2 after 3 attempts: {game_id}")
#                         if df.empty:
#                             continue
#                     else:
#                         print(f"⚠️ Unsupported endpoint: {endpoint}")
#                         continue

#                     df['GAME_ID'] = game_id
#                     df['GAME_DATE'] = game_date

#                     out_file = os.path.join(out_dir, f"{game_id}.csv")
#                     df.to_csv(out_file, index=False)
#                     saved_count += 1

#                     time.sleep(0.6)

#                 print(f"📁 [{status.upper()}] {player_name} | {teammate_name} | {endpoint}: {saved_count} files saved to {out_dir}")

# collect_player_injury_split_logs(
#     player_name='Nikola Jokic',
#     teammates=['Jamal Murray', 'Aaron Gordon', 'Michael Porter Jr.'],
#     season='2024-25',
#     base_out_dir='raw_data',
#     endpoints=['BoxScoreFourFactorsV2', 'BoxScoreMiscV2', 'BoxScorePlayerTrackV2'],
#     manual_fallback_path='raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv'
# )

def collect_player_injury_split_logs(player_name, teammates, season, base_out_dir, endpoints, manual_fallback_path=None):
    os.makedirs(base_out_dir, exist_ok=True)

    # Convert full season (e.g. '2024-25') to short (e.g. '24-25')
    short_season = season[-5:]

    # Load manual fallback CSV if provided
    manual_df = None
    if manual_fallback_path:
        manual_df = pd.read_csv(manual_fallback_path)
        manual_df['GAME_ID'] = manual_df['GAME_ID'].astype(str).str.zfill(10)
        if 'GAME_DATE' in manual_df.columns:
            manual_df['GAME_DATE'] = pd.to_datetime(manual_df['GAME_DATE'])

    # Get player ID
    all_players = players.get_players()
    player_info = next(p for p in all_players if normalize(p['full_name']) == normalize(player_name))
    player_id = player_info['id']

    player_games_df = PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    player_games_df['GAME_DATE'] = pd.to_datetime(player_games_df['GAME_DATE'])

    # Get teammate presence
    teammate_presence = {}
    for teammate_name in teammates:
        teammate_info = next((p for p in all_players if normalize(p['full_name']) == normalize(teammate_name)), None)
        if not teammate_info:
            print(f"⚠️ Could not find teammate: {teammate_name}")
            continue
        teammate_id = teammate_info['id']
        teammate_games = PlayerGameLog(player_id=teammate_id, season=season).get_data_frames()[0]
        games_played = set(teammate_games['Game_ID'])
        teammate_presence[teammate_name] = games_played
        time.sleep(0.6)

    for loop_num in [1, 2]:
        print(f"\n🔁 Starting pass {loop_num} of data collection...")

        # Process each teammate
        for teammate_name in teammates:
            if teammate_name not in teammate_presence:
                continue

            games_with = []
            games_without = []

            for _, row in player_games_df.iterrows():
                gid = row['Game_ID']
                if gid in teammate_presence[teammate_name]:
                    games_with.append((gid, row['GAME_DATE']))
                else:
                    games_without.append((gid, row['GAME_DATE']))

            # For WITH / WITHOUT groups
            for status, games in [('with', games_with), ('without', games_without)]:
                for endpoint in endpoints:
                    out_dir = os.path.join(
                        base_out_dir,
                        short_season,
                        'injury',
                        player_name.replace(' ', '_'),
                        f"{status}_{teammate_name.replace(' ', '_')}",
                        endpoint
                    )
                    os.makedirs(out_dir, exist_ok=True)

                    saved_count = 0

                    for i, (game_id, game_date) in enumerate(games):
                        out_file = os.path.join(out_dir, f"{game_id}.csv")

                        if os.path.exists(out_file):
                            print(f"⏭️  [{status.upper()}] {endpoint} | {teammate_name} | Game {game_id} ({i+1}): already saved — skipping")
                            continue

                        df = pd.DataFrame()

                        if endpoint == 'BoxScoreTraditionalV2':
                            for attempt in range(3):
                                try:
                                    df = BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
                                    df = df[df['PLAYER_ID'] == player_id].copy()
                                    if not df.empty:
                                        break
                                except Exception:
                                    if attempt < 2:
                                        time.sleep(2 ** attempt)
                                    else:
                                        print(f"⚠️ Final API failure for TraditionalV2 | Game {game_id} — trying fallback")

                            if df.empty and manual_df is not None and season == '2024-25':
                                df = manual_df[manual_df['GAME_ID'] == game_id].copy()
                                if df.empty:
                                    print(f"❌ Missing in both API and manual fallback: {game_id}")
                                    continue

                        elif endpoint == 'BoxScoreAdvancedV2':
                            for attempt in range(3):
                                try:
                                    df = BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0]
                                    df = df[df['PLAYER_ID'] == player_id].copy()
                                    if not df.empty:
                                        break
                                except Exception:
                                    if attempt < 2:
                                        time.sleep(2 ** attempt)
                                    else:
                                        print(f"❌ Skipped AdvancedV2 after 3 attempts: {game_id}")
                            if df.empty:
                                continue

                        elif endpoint == 'BoxScoreFourFactorsV2':
                            for attempt in range(3):
                                try:
                                    df = BoxScoreFourFactorsV2(game_id=game_id).get_data_frames()[0]
                                    df = df[df['PLAYER_ID'] == player_id].copy()
                                    if not df.empty:
                                        break
                                except Exception:
                                    if attempt < 2:
                                        time.sleep(2 ** attempt)
                                    else:
                                        print(f"⚠️ Final API failure: {endpoint} | Game {game_id}")
                            if df.empty:
                                continue

                        elif endpoint == 'BoxScoreMiscV2':
                            for attempt in range(3):
                                try:
                                    df = BoxScoreMiscV2(game_id=game_id).get_data_frames()[0]
                                    df = df[df['PLAYER_ID'] == player_id].copy()
                                    if not df.empty:
                                        break
                                except Exception:
                                    if attempt < 2:
                                        time.sleep(2 ** attempt)
                                    else:
                                        print(f"⚠️ Final API failure: {endpoint} | Game {game_id}")
                            if df.empty:
                                continue

                        elif endpoint == 'BoxScorePlayerTrackV2':
                            for attempt in range(3):
                                try:
                                    df = BoxScorePlayerTrackV2(game_id=game_id).get_data_frames()[0]
                                    df = df[df['PLAYER_ID'] == player_id].copy()
                                    if not df.empty:
                                        break
                                except Exception:
                                    if attempt < 2:
                                        time.sleep(2 ** attempt)
                                    else:
                                        print(f"⚠️ Final API failure: {endpoint} | Game {game_id}")
                            if df.empty:
                                continue

                        else:
                            print(f"⚠️ Unsupported endpoint: {endpoint}")
                            continue

                        df['GAME_ID'] = game_id
                        df['GAME_DATE'] = game_date
                        df.to_csv(out_file, index=False)
                        print(f"💾 [{status.upper()}] {endpoint} | {teammate_name} | Game {game_id} ({i+1}): saved")
                        saved_count += 1

                        time.sleep(0.6)

                    print(f"📁 [{status.upper()}] {player_name} | {teammate_name} | {endpoint}: {saved_count} files saved to {out_dir}")

# if __name__ == "__main__":
#     collect_player_injury_split_logs(
#         player_name="Nikola Jokic",
#         teammates=[
#             "Jamal Murray",
#             "Aaron Gordon",
#             "Michael Porter Jr."
#         ],
#         season="2024-25",
#         base_out_dir="raw_data",
#         endpoints=[
#             "BoxScoreTraditionalV2",
#             "BoxScoreAdvancedV2",
#             "BoxScoreFourFactorsV2",
#             "BoxScoreMiscV2",
#             "BoxScorePlayerTrackV2"
#         ],
#         manual_fallback_path="raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv"
#     )

import os
import pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    TeamGameLog,
    BoxScoreTraditionalV2,
    BoxScoreAdvancedV2,
    BoxScoreMiscV2,
    BoxScoreFourFactorsV2,
    BoxScorePlayerTrackV2,
)
import time

def normalize(name):
    return name.lower().replace('.', '').replace(' ', '')

def collect_team_injury_split_logs(team_abbrev, player_names, season, base_out_dir, endpoints, fallback_csv_path=None):
    from nba_api.stats.endpoints import TeamGameLog, BoxScoreTraditionalV2, BoxScoreAdvancedV2, BoxScoreFourFactorsV2, BoxScoreMiscV2, BoxScorePlayerTrackV2
    import pandas as pd
    import os, time
    from nba_api.stats.static import players, teams

    nba_teams = teams.get_teams()
    team_info = next(t for t in nba_teams if t['abbreviation'].upper() == team_abbrev.upper())
    team_id = team_info['id']

    team_logs_df = TeamGameLog(team_id=team_id, season=season).get_data_frames()[0]
    short_season = season[-5:]

    # Load fallback if applicable
    fallback_df = None
    if (season == '2024-25' and team_abbrev == 'DEN' and fallback_csv_path):
        fallback_df = pd.read_csv(fallback_csv_path)
        fallback_df['GAME_ID'] = fallback_df['GAME_ID'].astype(str).str.zfill(10)
        if 'GAME_DATE' in fallback_df.columns:
            fallback_df['GAME_DATE'] = pd.to_datetime(fallback_df['GAME_DATE'])

    all_players = players.get_players()
    player_id_map = {normalize(p['full_name']): p['id'] for p in all_players}

    # Get all games for team
    # team_logs_df = team_logs_df[team_logs_df['TEAM_ABBREVIATION'] == team_abbrev].copy()
    team_logs_df['GAME_DATE'] = pd.to_datetime(team_logs_df['GAME_DATE'])
    team_game_ids = team_logs_df[['Game_ID', 'GAME_DATE']].drop_duplicates()

    # Get presence info for each player
    presence_map = {}
    for player in player_names:
        pid = player_id_map.get(normalize(player))
        if not pid:
            print(f"❌ Skipping {player}: ID not found")
            continue
        gdf = PlayerGameLog(player_id=pid, season=season).get_data_frames()[0]
        presence_map[player] = set(gdf['Game_ID'])
        time.sleep(0.6)

    # Main loop (runs twice to retry unsaved files)
    for attempt in [1, 2]:
        print(f"\n🔁 Iteration {attempt}/2")

        for player in player_names:
            if player not in presence_map:
                continue

            player_game_ids = presence_map[player]
            with_games = []
            without_games = []

            for _, row in team_game_ids.iterrows():
                gid, date = row['Game_ID'], row['GAME_DATE']
                if gid in player_game_ids:
                    with_games.append((gid, date))
                else:
                    without_games.append((gid, date))

            for status, games in [('with', with_games), ('without', without_games)]:
                for endpoint in endpoints:
                    out_dir = os.path.join(
                        base_out_dir,
                        short_season,
                        'injury',
                        'teams',
                        team_abbrev,
                        f'{status}_{player.replace(" ", "_")}',
                        endpoint
                    )
                    os.makedirs(out_dir, exist_ok=True)
                    saved = 0
                    skipped = 0

                    for gid, gdate in games:
                        out_file = os.path.join(out_dir, f"{gid}.csv")
                        if os.path.exists(out_file):
                            print(f"⏩ Skipped [{status.upper()}] {player} | {endpoint} | {gid}")
                            skipped += 1
                            continue

                        df = pd.DataFrame()
                        try:
                            if endpoint == 'BoxScoreTraditionalV2':
                                for i in range(3):
                                    try:
                                        df = BoxScoreTraditionalV2(game_id=gid).get_data_frames()[0]
                                        break
                                    except:
                                        time.sleep(2 ** i)

                                if df.empty and fallback_df is not None:
                                    df = fallback_df[fallback_df['GAME_ID'] == gid].copy()
                                    if df.empty:
                                        print(f"❌ Missing in both API and fallback: {gid}")
                                        continue

                            elif endpoint == 'BoxScoreAdvancedV2':
                                df = BoxScoreAdvancedV2(game_id=gid).get_data_frames()[0]
                            elif endpoint == 'BoxScoreFourFactorsV2':
                                df = BoxScoreFourFactorsV2(game_id=gid).get_data_frames()[0]
                            elif endpoint == 'BoxScoreMiscV2':
                                df = BoxScoreMiscV2(game_id=gid).get_data_frames()[0]
                            elif endpoint == 'BoxScorePlayerTrackV2':
                                df = BoxScorePlayerTrackV2(game_id=gid).get_data_frames()[0]
                            else:
                                print(f"⚠️ Unknown endpoint: {endpoint}")
                                continue

                        except Exception as e:
                            print(f"❌ Failed {endpoint} | {gid}: {e}")
                            continue

                        df['GAME_ID'] = gid
                        df['GAME_DATE'] = gdate
                        df.to_csv(out_file, index=False)
                        print(f"✅ Saved [{status.upper()}] {player} | {endpoint} | {gid}")
                        saved += 1
                        time.sleep(0.6)

                    print(f"\n📁 [{status.upper()}] {team_abbrev} | {player} | {endpoint}: {saved} saved, {skipped} skipped → {out_dir}")

# if __name__ == "__main__":
#     collect_team_injury_split_logs(
#         team_abbrev='DEN',
#         player_names=[
#             'Jamal Murray',
#             'Aaron Gordon',
#             'Michael Porter Jr.'
#         ],
#         season='2024-25',
#         base_out_dir='raw_data',
#         endpoints=[
#             'BoxScoreTraditionalV2'
#             # 'BoxScoreAdvancedV2',
#             # 'BoxScoreFourFactorsV2',
#             # 'BoxScoreMiscV2',
#             # 'BoxScorePlayerTrackV2'
#         ],
#         fallback_csv_path='raw_data/24-25/box_scores/nuggets/DEN_TeamGameLogs_202425.csv'
#     )

from nba_api.stats.endpoints import TeamGameLog, BoxScoreTraditionalV2, BoxScoreAdvancedV2, BoxScoreFourFactorsV2, BoxScoreMiscV2, BoxScorePlayerTrackV2

# Normalize team abbreviation
def get_team_id(team_abbrev):
    all_teams = teams.get_teams()
    team_info = next((team for team in all_teams if team['abbreviation'] == team_abbrev), None)
    return team_info['id'] if team_info else None

# Retrieve opponent abbreviation for a given matchup
def get_opponent_abbrev(matchup_str, team_abbrev):
    parts = matchup_str.split(" ")
    if parts[1] == "vs.":
        return parts[2]
    elif parts[1] == "@":
        return parts[2]
    return None

# Function to retrieve and save full box scores organized by opponent
def collect_head2head_boxscores(team_abbrev, season, base_out_dir, endpoints):
    short_season = season[-5:]
    team_id = get_team_id(team_abbrev)
    if not team_id:
        print(f"❌ Invalid team abbreviation: {team_abbrev}")
        return

    team_games_df = TeamGameLog(team_id=team_id, season=season).get_data_frames()[0]
    team_games_df['GAME_DATE'] = pd.to_datetime(team_games_df['GAME_DATE'])

    for idx, row in team_games_df.iterrows():
        game_id = row['Game_ID']
        matchup = row['MATCHUP']
        game_date = row['GAME_DATE']
        opponent_abbrev = get_opponent_abbrev(matchup, team_abbrev)

        if not opponent_abbrev:
            print(f"⚠️ Could not determine opponent for matchup: {matchup}")
            continue

        for endpoint in endpoints:
            out_dir = os.path.join(
                base_out_dir,
                short_season,
                'head2head',
                team_abbrev,
                opponent_abbrev,
                endpoint
            )
            os.makedirs(out_dir, exist_ok=True)

            out_file = os.path.join(out_dir, f"{game_id}.csv")
            if os.path.exists(out_file):
                print(f"⏭️  Already exists: {game_id} ({opponent_abbrev} - {endpoint})")
                continue

            df = pd.DataFrame()

            for attempt in range(3):
                try:
                    endpoint_class = globals()[endpoint]
                    df = endpoint_class(game_id=game_id).get_data_frames()[0]
                    break
                except Exception as e:
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                    else:
                        print(f"❌ Failed: {endpoint} | Game {game_id} | {str(e)}")

            if not df.empty:
                df['GAME_ID'] = game_id
                df['GAME_DATE'] = game_date
                df.to_csv(out_file, index=False)
                print(f"✅ Saved: {game_id} ({opponent_abbrev} - {endpoint})")

            time.sleep(0.6)

collect_head2head_boxscores(
    team_abbrev='DEN',
    season='2024-25',
    base_out_dir='raw_data',
    endpoints=[
        'BoxScoreTraditionalV2',
        'BoxScoreAdvancedV2'
        # 'BoxScoreFourFactorsV2',
        # 'BoxScoreMiscV2',
        # 'BoxScorePlayerTrackV2'
    ]
)

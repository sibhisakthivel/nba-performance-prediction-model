import os
import pandas as pd

def compute_season_averages(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df = df.iloc[::-1].reset_index(drop=True)

    # Exclude non-numeric columns that shouldn’t be averaged
    non_avg_cols = ['GAME_ID', 'PLAYER_ID', 'NOTE', 'GAME_DATE']
    avg_cols = [col for col in df.columns if col not in non_avg_cols and pd.api.types.is_numeric_dtype(df[col])]

    result_rows = []
    for i in range(len(df)):
        if i == 0:
            # First game: no prior data
            row = df.loc[i, ['GAME_ID']].to_dict()
            for col in avg_cols:
                row[col] = None
        else:
            prev_games = df.iloc[:i]
            row = {'GAME_ID': df.loc[i, 'GAME_ID']}
            for col in avg_cols:
                row[col] = prev_games[col].mean()
        result_rows.append(row)

    result_df = pd.DataFrame(result_rows)
    result_df.to_csv(output_csv, index=False)
    print(f"✅ Wrote rolling season averages to {output_csv}")

# compute_season_averages(input_csv='raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv',
#                         output_csv='processed_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_szn_avg.csv')

def compute_rolling_averages(input_csv, output_csv, window=5):
    df = pd.read_csv(input_csv)

    # ⏪ Reverse to start from earliest game
    df = df.iloc[::-1].reset_index(drop=True)

    # 🎯 Columns to average
    exclude_cols = ['GAME_ID', 'PLAYER_ID', 'TEAM_ID', 'NOTE']
    numeric_cols = df.select_dtypes(include='number').columns
    avg_cols = [col for col in numeric_cols if col not in exclude_cols]

    # 🧮 Compute true rolling averages using explicit row window
    rolling_rows = []
    for i in range(len(df)):
        if i < window:
            rolling_rows.append({col: None for col in avg_cols})
        else:
            prev_rows = df.iloc[i - window:i]
            rolling_avg = prev_rows[avg_cols].mean()
            rolling_rows.append(rolling_avg.to_dict())

    rolling_df = pd.DataFrame(rolling_rows)
    result_df = pd.concat([df[['GAME_ID']], rolling_df], axis=1)

    # ✅ Don't re-reverse — keep oldest game at the top
    result_df = result_df.reset_index(drop=True)

    # 💾 Save
    result_df.to_csv(output_csv, index=False)
    print(f"✅ Saved rolling {window}-game averages (chronological order) to {output_csv}")

# compute_rolling_averages(input_csv='raw_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_202425.csv',
#                         output_csv='processed_data/24-25/box_scores/jokic/BoxScoreTraditionalV2_r5_avg.csv')

def compute_rolling_avg_boxscores(input_folder, output_csv):
    all_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    all_paths = [os.path.join(input_folder, f) for f in all_files]

    dfs = []
    for path in all_paths:
        df = pd.read_csv(path)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        print(f"⚠️ No valid files in {input_folder}")
        return

    df = pd.concat(dfs, ignore_index=True)

    if 'GAME_DATE' not in df.columns or df['GAME_DATE'].isnull().all():
        print(f"⚠️ Missing GAME_DATE in files from {input_folder}")
        return

    # ✅ Sort from beginning to end of season
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE').reset_index(drop=True)

    # Select numeric columns to average
    non_avg_cols = ['GAME_ID', 'PLAYER_ID', 'NOTE', 'GAME_DATE']
    avg_cols = [col for col in df.columns if col not in non_avg_cols and pd.api.types.is_numeric_dtype(df[col])]

    result_rows = []
    for i in range(len(df)):
        row = {
            'GAME_ID': df.loc[i, 'GAME_ID'],
            'GAME_DATE': df.loc[i, 'GAME_DATE']
        }
        if i == 0:
            for col in avg_cols:
                row[col] = None
        else:
            prev_games = df.iloc[:i]
            for col in avg_cols:
                row[col] = prev_games[col].mean()
        result_rows.append(row)

    result_df = pd.DataFrame(result_rows)
    result_df = result_df.sort_values("GAME_DATE").reset_index(drop=True)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result_df.to_csv(output_csv, index=False)
    print(f"✅ Saved rolling season averages to {output_csv}")

compute_rolling_avg_boxscores(
    input_folder="raw_data/24-25/injury/Nikola_Jokic/with_Jamal_Murray/BoxScoreAdvancedV2",
    output_csv="processed_data/24-25/injury/Nikola_Jokic/with_Jamal_Murray/BoxScoreAdvancedV2_rolling.csv"
)

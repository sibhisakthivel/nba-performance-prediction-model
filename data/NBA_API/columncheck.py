import pandas as pd
import nba_api.stats.endpoints as endpoints
import time
from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.static import players

def get_all_endpoint_columns(test_game_id='0022401193'):
    """
    Get all columns from each boxscore endpoint using a test game ID
    """
    boxscore_endpoints = [
        "BoxScoreAdvancedV2",
        "BoxScoreDefensiveV2", 
        "BoxScoreFourFactorsV2",
        "BoxScoreHustleV2",
        "BoxScoreMiscV2",
        "BoxScorePlayerTrackV2",
        "BoxScoreScoringV2",
        "BoxScoreTraditionalV2",
        "BoxScoreUsageV2"
    ]
    
    endpoint_data = {}
    
    for endpoint_name in boxscore_endpoints:
        print(f"🔍 Checking {endpoint_name}...")
        
        try:
            # Get the endpoint class
            endpoint_class = getattr(endpoints, endpoint_name)
            
            # Try to get data
            response = endpoint_class(game_id=test_game_id)
            df = response.get_data_frames()[0]
            
            # Store the information
            endpoint_data[endpoint_name] = {
                'columns': list(df.columns),
                'num_rows': len(df),
                'status': 'Success'
            }
            
            print(f"✅ Success: {len(df.columns)} columns, {len(df)} rows")
            
        except Exception as e:
            endpoint_data[endpoint_name] = {
                'columns': [],
                'num_rows': 0,
                'status': f'Error: {str(e)}'
            }
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Rate limiting
    
    return endpoint_data

def find_deflections_in_endpoints(endpoint_data):
    """
    Look for deflection-related columns across all endpoints
    """
    deflection_keywords = ['deflection', 'deflections', 'defl', 'hustle', 'loose', 'contested']
    
    print("\n🔍 Searching for deflection-related columns...")
    print("=" * 60)
    
    found_deflections = False
    
    for endpoint_name, data in endpoint_data.items():
        if data['status'] == 'Success':
            # Check for deflection-related columns
            deflection_columns = []
            for col in data['columns']:
                for keyword in deflection_keywords:
                    if keyword.lower() in col.lower():
                        deflection_columns.append(col)
                        break
            
            if deflection_columns:
                print(f"🎯 {endpoint_name} - Found potential deflection columns:")
                for col in deflection_columns:
                    print(f"   - {col}")
                found_deflections = True
            else:
                print(f"➖ {endpoint_name} - No deflection-related columns found")
        else:
            print(f"❌ {endpoint_name} - {data['status']}")
    
    if not found_deflections:
        print("⚠️  No deflection-related columns found in any endpoint")
    
    return found_deflections

def display_all_columns(endpoint_data):
    """
    Display all columns from each endpoint in a formatted way
    """
    print("\n📊 ALL COLUMNS FROM EACH ENDPOINT:")
    print("=" * 80)
    
    for endpoint_name, data in endpoint_data.items():
        print(f"\n🎯 {endpoint_name}:")
        print(f"   Status: {data['status']}")
        
        if data['status'] == 'Success':
            print(f"   Rows: {data['num_rows']}")
            print(f"   Columns ({len(data['columns'])}): ")
            
            # Format columns in groups of 4 for better readability
            columns = data['columns']
            for i in range(0, len(columns), 4):
                group = columns[i:i+4]
                formatted_group = '   '.join(f"{col:<15}" for col in group)
                print(f"      {formatted_group}")
        
        print("-" * 60)

def check_hustle_endpoint_specifically(test_game_id='0022401193'):
    """
    Try different approaches to get BoxScoreHustleV2 working
    """
    print("\n🔍 SPECIFIC DEBUGGING FOR BoxScoreHustleV2:")
    print("=" * 50)
    
    try:
        # Method 1: Try with just game_id
        print("1️⃣ Trying with game_id only...")
        hustle_response = endpoints.BoxScoreHustleV2(game_id=test_game_id)
        hustle_df = hustle_response.get_data_frames()[0]
        print(f"✅ Success! {len(hustle_df)} rows, {len(hustle_df.columns)} columns")
        print(f"Columns: {list(hustle_df.columns)}")
        return hustle_df
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    try:
        # Method 2: Try with additional parameters
        print("2️⃣ Trying with additional parameters...")
        hustle_response = endpoints.BoxScoreHustleV2(
            game_id=test_game_id,
            start_period=1,
            end_period=10
        )
        hustle_df = hustle_response.get_data_frames()[0]
        print(f"✅ Success! {len(hustle_df)} rows, {len(hustle_df.columns)} columns")
        print(f"Columns: {list(hustle_df.columns)}")
        return hustle_df
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    try:
        # Method 3: Check if it returns multiple dataframes
        print("3️⃣ Checking for multiple dataframes...")
        hustle_response = endpoints.BoxScoreHustleV2(game_id=test_game_id)
        all_dfs = hustle_response.get_data_frames()
        print(f"✅ Found {len(all_dfs)} dataframes")
        
        for i, df in enumerate(all_dfs):
            print(f"   DataFrame {i}: {len(df)} rows, {len(df.columns)} columns")
            if len(df) > 0:
                print(f"   Columns: {list(df.columns)}")
        
        return all_dfs
        
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    return None

# Main execution
if __name__ == "__main__":
    print("🏀 NBA BOXSCORE ENDPOINT COLUMN CHECKER")
    print("=" * 60)
    
    # Get a test game ID from Jokic's recent games
    player_dict = players.find_players_by_full_name("Nikola Jokic")
    if player_dict:
        player_id = player_dict[0]['id']
        game_log = PlayerGameLog(player_id=player_id, season='2024-25')
        recent_game_id = game_log.get_data_frames()[0]['Game_ID'].iloc[0]
        print(f"🎯 Using test game ID: {recent_game_id}")
    else:
        recent_game_id = '0022401193'
        print(f"🎯 Using default test game ID: {recent_game_id}")
    
    # Get all endpoint columns
    endpoint_data = get_all_endpoint_columns(recent_game_id)
    
    # Look for deflections specifically
    find_deflections_in_columns = find_deflections_in_endpoints(endpoint_data)
    
    # Display all columns
    display_all_columns(endpoint_data)
    
    # Try to debug BoxScoreHustleV2 specifically
    hustle_result = check_hustle_endpoint_specifically(recent_game_id)

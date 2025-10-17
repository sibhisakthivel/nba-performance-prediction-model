from nba_api.stats import endpoints
from nba_api.stats.endpoints import (
    boxscoredefensivev2,
    boxscoremiscv3,
    boxscoretraditionalv3,
    boxscoreadvancedv3,
    boxscorefourfactorsv3,
    boxscorehustlev2,
    boxscorematchupsv3,
    boxscoreplayertrackv3,
    boxscorescoringv3,
    boxscoreusagev3
)

def list_nba_api_endpoints():
    # dir() gives all attributes in the module
    all_attrs = dir(endpoints)

    # keep only endpoint classes (they start with uppercase and aren't private)
    endpoint_classes = [
        attr for attr in all_attrs
        if attr[0].isupper() and not attr.startswith("_")
    ]

    # print nicely
    print("=== Available NBA API Endpoints ===")
    for ep in sorted(endpoint_classes):
        print(ep)
        
def inspect_boxscore(endpoint_func, game_id: str, extra_args: dict = None):
    """
    Calls a box score endpoint and prints its columns.
    """
    if extra_args is None:
        extra_args = {}

    endpoint = endpoint_func(game_id=game_id, **extra_args)
    df = endpoint.get_data_frames()[0]

    print(f"\n=== {endpoint_func.__name__} ===")
    print(df.columns.tolist())
    return df


# Example usage
if __name__ == "__main__":
    
    list_nba_api_endpoints()
        
    test_game_id = "0022200001"  # pick any valid NBA game ID

    endpoints = [
        boxscoredefensivev2.BoxScoreDefensiveV2,
        boxscoremiscv3.BoxScoreMiscV3,
        boxscoretraditionalv3.BoxScoreTraditionalV3,
        boxscoreadvancedv3.BoxScoreAdvancedV3,
        boxscorefourfactorsv3.BoxScoreFourFactorsV3,
        boxscorehustlev2.BoxScoreHustleV2,
        boxscorematchupsv3.BoxScoreMatchupsV3,
        boxscoreplayertrackv3.BoxScorePlayerTrackV3,
        boxscorescoringv3.BoxScoreScoringV3,
        boxscoreusagev3.BoxScoreUsageV3
    ]

    for ep in endpoints:
        try:
            inspect_boxscore(ep, test_game_id)
        except Exception as e:
            print(f"Error in {ep.__name__}: {e}")


import csv

player_team_core_stats = [
    'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'FTR', 
    'EFG%', 'TS%', 'TREB', 'OREB', 'DREB', 'TREB CHANCES', 'OREB CHANCES', 'DREB CHANCES',
    'TREB %', 'E TREB %', 'OREB %', 'DREB %', 'TREB CHANCES %', 'OREB CHANCES %', 'DREB CHANCES %',
    'AST', 'AST %', 'E AST %', 'AST CHANCES', 'AST CHANCES %', 'AST:TO', 'PASSES', 'TOUCHES',
    'STL', 'STL %', 'DEFLECTIONS', 'BLK', 'BLK %', 'TO', 'TO %', 'E TO %', 'PF'
]

player_team_rate_stats = [
    'NRTG', 'ENRTG', 'ORTG', 'EORTG', 'DRTG', 'EDRTG', 'PACE', 'EPACE', 'POSSESSIONS'
]

player_only_features = [
    'USAGE', 'EUSAGE', 'PIE', 'PER', 'EPOSSESSIONS'
]

def player_csv(core_stats, rate_stats, player_only_stats, prefix="SZN"):
    estimated_rate_stats = ['E AST %', 'E TREB %', 'E TO %']
    headers = ['DATE', 'PLAYER', 'TEAM']

    if prefix == "WIN" or prefix == "LOSE":
        headers += [f'{prefix} GAMES PLAYED', f'{prefix} AVG MIN']
    elif prefix in ["R3", "R5", "R10"]:
        headers += [f'{prefix} WIN %', f'{prefix} AVG MIN']
    else:
        headers += [f'{prefix} WIN %', f'{prefix} GAMES PLAYED', f'{prefix} AVG MIN']

    for stat in core_stats:
        if '%' in stat:
            headers += [
                f'{prefix} AVG {stat}',
                f'{prefix} AVG TEAM {stat}',
                f'{prefix} AVG TEAM {stat} Allowed'
            ]
        else:
            headers += [
                f'{prefix} AVG {stat}',
                f'{prefix} AVG TEAM {stat}',
                f'{prefix} AVG TEAM {stat} %',
                f'{prefix} AVG TEAM {stat} Allowed'
            ]

    for stat in rate_stats:
        headers.append(f'{prefix} AVG {stat}')
        headers.append(f'{prefix} AVG TEAM {stat}')
        if stat not in estimated_rate_stats:
            headers.append(f'{prefix} AVG TEAM {stat} Allowed')

    for stat in player_only_stats:
        headers.append(f'{prefix} {stat}')

    return headers

def team_csv(core_stats, rate_stats, prefix='SZN'):
    estimated_rate_stats = ['E AST %', 'E TREB %', 'E TO %']
    headers = ['DATE', 'TEAM']

    if prefix == "WIN" or prefix == "LOSE":
        headers = [f'{prefix} GAMES PLAYED']
    elif prefix in ["R3", "R5", "R10"]:
        headers = [f'{prefix} WIN %']
    else:
        headers = [f'{prefix} WIN %', f'{prefix} GAMES PLAYED']
    
    for stat in core_stats:
        headers += [
            f'OPP {prefix} AVG {stat}',
            f'OPP {prefix} AVG {stat} Allowed'
        ]

    for stat in rate_stats:
        headers.append(f'OPP {prefix} AVG {stat}')
        if stat not in estimated_rate_stats:
            headers.append(f'OPP {prefix} AVG {stat} Allowed')

    return headers

player_injury_features = [
    'GAMES PLAYED', 'WIN %', 'USG%', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 
    'FTM', 'FTA', 'FT%', 'FTR', 'EFG%', 'TS%', 'TREB', 'OREB', 'DREB', 
    'TREB CHANCES', 'OREB CHANCES', 'DREB CHANCES', 'TREB %', 'OREB %', 'DREB %', 
    'TREB CHANCES %', 'OREB CHANCES %', 'DREB CHANCES %',
    'AST', 'AST %', 'AST CHANCES', 'AST CHANCES %', 'AST:TO', 'PASSES', 'TOUCHES', 
    'STL', 'STL %', 'DEFLECTIONS', 'BLK', 'BLK %', 'TO', 'TO %', 'PF',
    'NRTG', 'ORTG', 'DRTG', 'PACE', 'POSSESSIONS', 'PIE', 'PER'
]

def player_injury(features, num_teammates=5):
    headers = ['DATE', 'PLAYER', 'TEAM']

    for i in range(1, num_teammates + 1):
        headers.append(f'Teammate {i} OUT')

        for stat in features:
            if '%' in stat:
                headers += [
                    f'{stat} with Teammate {i}',
                    f'{stat} without Teammate {i}',
                    f'Delta {stat} Teammate {i}',
                ]
            elif stat == 'GAMES PLAYED':
                headers += [
                    f'{stat} with Teammate {i}',
                    f'{stat} without Teammate {i}',
                ]
            else:
                headers += [
                    f'{stat} with Teammate {i}',
                    f'% {stat} with Teammate {i}',
                    f'{stat} without Teammate {i}',
                    f'% {stat} without Teammate {i}',
                    f'Delta {stat} Teammate {i}',
                    f'Delta % {stat} Teammate {i}',
                ]
    return headers

team_injury_features = [
    'GAMES PLAYED', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 
    'FTM', 'FTA', 'FT%', 'FTR', 'EFG%', 'TS%', 'TREB', 'OREB', 'DREB', 
    'TREB CHANCES', 'OREB CHANCES', 'DREB CHANCES', 'TREB %', 'OREB %', 'DREB %', 
    'TREB CHANCES %', 'OREB CHANCES %', 'DREB CHANCES %',
    'AST', 'AST %', 'AST CHANCES', 'AST CHANCES %', 'AST:TO', 'PASSES', 'TOUCHES', 
    'STL', 'STL %', 'DEFLECTIONS', 'BLK', 'BLK %', 'TO', 'TO %', 'PF',
    'NRTG', 'ORTG', 'DRTG', 'PACE', 'POSSESSIONS'
]

def team_injury(features, num_players=6, prefix='Team'):
    headers = ['DATE', 'TEAM']

    for i in range(1, num_players + 1):
        headers.append(f'{prefix} Player {i} OUT')

        for stat in features:
            if stat == 'GAMES PLAYED':
                headers += [
                    f'{prefix} {stat} with Player {i}',
                    f'{prefix} {stat} without Player {i}'
                ]
            else:
                headers += [
                    f'{prefix} {stat} with Player {i}',
                    f'{prefix} {stat} without Player {i}',
                    f'{prefix} Delta {stat} Player {i}',
                    f'{prefix} {stat} Allowed with Player {i}',
                    f'{prefix} {stat} Allowed without Player {i}',
                    f'{prefix} Delta {stat} Allowed Player {i}',
                ]
    return headers

player_headers = player_injury(player_injury_features)
team_headers = team_injury(team_injury_features, prefix='Team')
opp_headers = team_injury(team_injury_features, prefix='Opp')

# ✅ Movement shot types
movement_types = [
    '2pt', '3pt', 'Catch and Shoot', 'Driving', 'ISO', 'Putback', 'Cutting', 'Static'
]

# ✅ NBA-defined court shot zones
shot_zones = [
    'Restricted Area', 'Paint', 'Mid-Range',
    'Left Corner 3', 'Right Corner 3', 'Above the Break 3'
]

# ✅ High-level shot types (based on action_type)
shot_types = [
    'Jumpshot', 'Layup', 'Dunk', 'Hook', 'Fadeaway', 'Tip'
]

# ✅ Shot distance ranges (feet)
shot_ranges = [
    '< 8 ft', '8-16 ft', '16-24 ft', '24+ ft'
]

def player_shot(movement_types, shot_zones, shot_types, shot_ranges):
    headers = ['DATE', 'PLAYER', 'TEAM']

    # Movement-type features
    for move in movement_types:
        headers += [
            f'{move} FGA',
            f'{move} FGA%',
            f'{move} FGM',
            f'{move} FGM%',
            f'{move} FG%'
        ]

    # Shot range features
    for rng in shot_ranges:
        headers += [
            f'{rng} FGA',
            f'{rng} FGA%',
            f'{rng} FGM',
            f'{rng} FGM%',
            f'{rng} FG%'
        ]
    
    # Shot zone features
    for zone in shot_zones:
        headers += [
            f'{zone} FGA',
            f'{zone} FGA%',
            f'{zone} FGM',
            f'{zone} FGM%',
            f'{zone} FG%'
        ]
        
    # Shot type feautres
    for type in shot_types:
        headers += [
            f'{type} FGA',
            f'{type} FGA%',
            f'{type} FGM',
            f'{type} FGM%',
            f'{type} FG%'
        ]
        
    # Shot Zone × Range combinations
    for zone in shot_zones:
        for rng in shot_ranges:
            label = f'{zone} × {rng}'
            headers += [
            f'{label} FGA',
            f'{label} FGA%',
            f'{label} FGM',
            f'{label} FGM%',
            f'{label} FG%'
        ]

    # Shot Type × Range combinations
    for shot in shot_types:
        for rng in shot_ranges:
            label = f'{shot} × {rng}'
            headers += [
            f'{label} FGA',
            f'{label} FGA%',
            f'{label} FGM',
            f'{label} FGM%',
            f'{label} FG%'
        ]

    return headers

def team_shot(movement_types, shot_zones, shot_types, shot_ranges, prefix="Team"):
    headers = ['DATE', 'TEAM']

    # Movement-type allowed
    for move in movement_types:
        headers += [
            f'{prefix} {move} FGA',
            f'{prefix} {move} FGA%',
            f'{prefix} {move} FGM',
            f'{prefix} {move} FGM%',
            f'{prefix} {move} FG%'
            f'{prefix} {move} FGA Allowed',
            f'{prefix} {move} FGA% Allowed',
            f'{prefix} {move} FGM Allowed',
            f'{prefix} {move} FGM% Allowed',
            f'{prefix} {move} FG% Allowed'
        ]

    # Shot range features
    for rng in shot_ranges:
        headers += [
            f'{rng} FGA',
            f'{rng} FGA%',
            f'{rng} FGM',
            f'{rng} FGM%',
            f'{rng} FG%',
            f'{rng} FGA Allowed',
            f'{rng} FGA% Allowed',
            f'{rng} FGM Allowed',
            f'{rng} FGM% Allowed',
            f'{rng} FG% Allowed'
        ]
        
    # Shot zone features
    for zone in shot_zones:
        headers += [
            f'{zone} FGA',
            f'{zone} FGA%',
            f'{zone} FGM',
            f'{zone} FGM%',
            f'{zone} FG%',
            f'{zone} FGA Allowed',
            f'{zone} FGA% Allowed',
            f'{zone} FGM Allowed',
            f'{zone} FGM% Allowed',
            f'{zone} FG% Allowed'
        ]
        
    # Shot type feautres
    for type in shot_types:
        headers += [
            f'{type} FGA',
            f'{type} FGA%',
            f'{type} FGM',
            f'{type} FGM%',
            f'{type} FG%',
            f'{type} FGA Allowed',
            f'{type} FGA% Allowed',
            f'{type} FGM Allowed',
            f'{type} FGM% Allowed',
            f'{type} FG% Allowed'
        ]
        
    # Shot Zone × Range Allowed
    for zone in shot_zones:
        for rng in shot_ranges:
            label = f'{zone} × {rng}'
            headers += [
            f'{prefix} {label} FGA',
            f'{prefix} {label} FGA%',
            f'{prefix} {label} FGM',
            f'{prefix} {label} FGM%',
            f'{prefix} {label} FG%'
            f'{prefix} {label} FGA Allowed',
            f'{prefix} {label} FGA% Allowed',
            f'{prefix} {label} FGM Allowed',
            f'{prefix} {label} FGM% Allowed',
            f'{prefix} {label} FG% Allowed'
        ]

    # Shot Type × Range Allowed
    for shot in shot_types:
        for rng in shot_ranges:
            label = f'{shot} × {rng}'
            headers += [
            f'{prefix} {label} FGA',
            f'{prefix} {label} FGA%',
            f'{prefix} {label} FGM',
            f'{prefix} {label} FGM%',
            f'{prefix} {label} FG%'
            f'{prefix} {label} FGA Allowed',
            f'{prefix} {label} FGA% Allowed',
            f'{prefix} {label} FGM Allowed',
            f'{prefix} {label} FGM% Allowed',
            f'{prefix} {label} FG% Allowed'
        ]

    return headers

def last_n_raw_player_team(core_stats, rate_stats, player_only_stats, prefix_base="L", n=5):
    headers = ['DATE', 'PLAYER', 'TEAM']
    estimated_rate_stats = ['E AST %', 'E TREB %', 'E TO %']  # ✅ No "Allowed" cols for these

    # Define prefix categories
    two_field_prefixes = ['WIN L', 'LOSE L']
    three_field_prefixes = ['HOME L', 'AWAY L']
    full_field_prefixes = ['L', 'H2H L', 'H2H WIN L', 'H2H LOSE L', 'H2H HOME L', 'H2H AWAY L']

    for i in range(1, n + 1):
        prefix = f"{prefix_base}{i}"

        # ⛳️ Adjust initial headers based on prefix type
        headers.append(f'{prefix} MIN')
        if prefix_base in two_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} HOME/AWAY'
            ]
        elif prefix_base in three_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} WIN/LOSE',
                f'{prefix} L5 WIN%',
                f'{prefix} L10 WIN%'
            ]
        elif prefix_base in full_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} HOME/AWAY',
                f'{prefix} WIN/LOSE',
                f'{prefix} L5 WIN%',
                f'{prefix} L10 WIN%'
            ]
        else:
            raise ValueError(f"Unrecognized prefix_base: {prefix_base}")

        # 🔢 Stat headers
        for stat in core_stats:
            if '%' in stat:
                headers += [
                    f'{prefix} {stat}',
                    f'{prefix} TEAM {stat}',
                    f'{prefix} TEAM {stat} Allowed'
                ]
            else:
                headers += [
                    f'{prefix} {stat}',
                    f'{prefix} TEAM {stat}',
                    f'{prefix} TEAM {stat} %',
                    f'{prefix} TEAM {stat} Allowed'
                ]

        for stat in rate_stats:
            headers += [
                f'{prefix} {stat}',
                f'{prefix} TEAM {stat}'
            ]
            if stat not in estimated_rate_stats:
                headers.append(f'{prefix} TEAM {stat} Allowed')

        for stat in player_only_stats:
            headers.append(f'{prefix} {stat}')

    return headers

def last_n_raw_team_only(core_stats, rate_stats, prefix_base='OPP L', n=5):
    headers = ['DATE', 'PLAYER', 'TEAM']
    estimated_rate_stats = ['E AST %', 'E TREB %', 'E TO %']  # ✅ No "Allowed" cols for these

    # Prefix groups to determine initial headers
    full_field_prefixes = ['L', 'H2H L', 'OPP L', 'OPP H2H L']
    two_field_prefixes = ['WIN L', 'LOSE L', 'H2H WIN L', 'H2H LOSE L', 'OPP WIN L', 'OPP LOSE L']
    three_field_prefixes = ['HOME L', 'AWAY L', 'H2H HOME L', 'H2H AWAY L', 'OPP HOME L', 'OPP AWAY L']


    for i in range(1, n + 1):
        prefix = f"{prefix_base}{i}"

        # ⛳️ Adjust initial headers based on prefix type
        if prefix_base in two_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} HOME/AWAY'
            ]
        elif prefix_base in three_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} WIN/LOSE',
                f'{prefix} L5 WIN%',
                f'{prefix} L10 WIN%'
            ]
        elif prefix_base in full_field_prefixes:
            headers += [
                f'{prefix} DAYS RESTED',
                f'{prefix} HOME/AWAY',
                f'{prefix} WIN/LOSE',
                f'{prefix} L5 WIN%',
                f'{prefix} L10 WIN%'
            ]
        else:
            raise ValueError(f"Unrecognized prefix_base: {prefix_base}")

        # 🔢 Stat headers
        for stat in core_stats:
            if '%' in stat:
                headers += [
                    f'{prefix} {stat}',
                    f'{prefix} {stat} Allowed'
                ]
            else:
                headers += [
                    f'{prefix} {stat}',
                    f'{prefix} {stat} %',
                    f'{prefix} {stat} Allowed'
                ]

        for stat in rate_stats:
            headers.append(f'{prefix} {stat}')
            if stat not in estimated_rate_stats:
                headers.append(f'{prefix} {stat} Allowed')

    return headers

with open("szn_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="SZN"))

with open("r3_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="R3"))

with open("r5_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="R5"))

with open("r10_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="R10"))

with open("home_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="HOME"))

with open("away_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="AWAY"))

with open("win_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="WIN"))

with open("lose_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="LOSE"))

with open("last5.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="L", n=5))
    
with open("last5_win.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="WIN L"))

with open("last5_lose.csv.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="LOSE L"))

with open("last5_home.csv.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="HOME L"))

with open("last5_away.csv.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="AWAY L"))
    
with open("h2h1_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="H2H(1)"))

with open("h2h2_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="H2H(2)"))

with open("h2h3_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(player_csv(player_team_core_stats, player_team_rate_stats, player_only_features, prefix="H2H(3)"))

with open("h2h_last5.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="H2H L", n=5))
    
with open("h2h_last5_win.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="H2H WIN L"))

with open("h2h_last5_lose.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="H2H LOSE L"))

with open("h2h_last5_home.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="H2H HOME L"))

with open("h2h_last5_away.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_player_team(player_team_core_stats, player_team_rate_stats, player_only_features, prefix_base="H2H AWAY L"))

with open("opp_szn_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="SZN"))

with open("opp_r3_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="R3"))

with open("opp_r5_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="R5"))

with open("opp_r10_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="R10"))

with open("opp_home_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="HOME"))

with open("opp_away_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="AWAY"))

with open("opp_win_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="WIN"))

with open("opp_lose_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="LOSE"))

with open("opp_last5.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP L", n=5))

with open("opp_h2h1_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="H2H(1)"))

with open("opp_h2h2_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="H2H(2)"))

with open("opp_h2h3_avg.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(team_csv(player_team_core_stats, player_team_rate_stats, prefix="H2H(3)"))

with open("opp_h2h_last5.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP H2H L", n=5))

with open("opp_win_last5.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP WIN L"))

with open("opp_lose_last5.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP LOSE L"))

with open("opp_home_last5.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP HOME L"))

with open("opp_away_last5.csv", "w", newline="") as f:
    csv.writer(f).writerow(last_n_raw_team_only(player_team_core_stats, player_team_rate_stats, prefix_base="OPP AWAY L"))

with open("player_injury.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(player_injury(player_injury_features))

with open("team_injury.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(team_injury(team_injury_features))

with open("opp_injury.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(team_injury(team_injury_features, prefix='OPP', num_players=4))

with open("player_shot.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(player_shot(movement_types, shot_zones, shot_types, shot_ranges))

with open("team_shot.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(team_shot(movement_types, shot_zones, shot_types, shot_ranges))

with open("opp_shot.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(team_shot(movement_types, shot_zones, shot_types, shot_ranges, prefix='OPP'))

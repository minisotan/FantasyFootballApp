from espn_api.football import League  # Ensure you have the right library imported
import pandas as pd
from credentials import LEAGUE_ID, SEASON, SWID, ESPN_S2

# Initialize the league
league = League(league_id=LEAGUE_ID, year=SEASON, swid=SWID, espn_s2=ESPN_S2)

# Define the list of positions you want to include
positions = ['QB', 'RB', 'WR', 'TE', 'D/ST', 'K']

### Section 1: Team Stats
teams_data = []

for team in league.teams:
    total_points = sum(team.scores)
    
    # Count only the weeks with actual scores to calculate the average points correctly
    games_played = sum(1 for score in team.scores if score > 0)
    average_points = round(total_points / games_played, 1) if games_played > 0 else 0
    
    teams_data.append({
        'Team Name': team.team_name,
        'Wins': team.wins,
        'Losses': team.losses,
        'Total Points': total_points,
        'Average Points': average_points,
        'Points by Week': team.scores  # Already in the correct format
    })

# Create DataFrame for Team Stats
df_teams = pd.DataFrame(teams_data)

# Sort by Win-Loss Record and Total Points
df_teams = df_teams.sort_values(by=['Wins', 'Total Points'], ascending=False).reset_index(drop=True)

# Expand Points by Week into separate columns
points_by_week = pd.DataFrame(df_teams['Points by Week'].tolist()).add_prefix('Week ')
points_by_week.columns = [f'Week {i + 1}' for i in range(points_by_week.shape[1])]  # Rename columns to start from Week 1
df_teams = pd.concat([df_teams.drop(columns='Points by Week'), points_by_week], axis=1)

### Section 2: Top 10 Players by Position
top_players_data = []

for pos in positions:
    all_players = []
    
    for team in league.teams:
        for player in team.roster:
            if player.position == pos:
                total_points = player.total_points
                games_played = sum(1 for score in team.scores if score > 0)  # Count only games played
                avg_points = round(total_points / games_played, 1) if games_played > 0 else 0
                
                all_players.append({
                    'Player': player.name,
                    'Total Points': total_points,
                    'Average Points': avg_points,
                    'Position': pos
                })

    # Sort players by points and take the top 10
    top_players = sorted(all_players, key=lambda x: x['Total Points'], reverse=True)[:10]

    # Add the top players to the list
    top_players_data.append({
        'Position': pos,
        'Players': top_players
    })

# Create a DataFrame for the Top Players
df_top_players = pd.DataFrame(columns=['Position', 'Player', 'Total Points', 'Average Points'])

# Fill the DataFrame with the structured data
for entry in top_players_data:
    pos = entry['Position']
    for player_info in entry['Players']:
        df_top_players = pd.concat([df_top_players, pd.DataFrame([{
            'Position': pos,
            'Player': player_info['Player'],
            'Total Points': player_info['Total Points'],
            'Average Points': player_info['Average Points']
        }])], ignore_index=True)

# Now pivot the DataFrame to get the desired layout
top_players_layout = pd.DataFrame()

# Create a column for each position
for pos in positions:
    pos_data = df_top_players[df_top_players['Position'] == pos]
    pos_data = pos_data[['Player', 'Total Points', 'Average Points']].set_index(pd.Index(range(1, len(pos_data) + 1)))
    
    # Name the columns appropriately
    pos_data.columns = [f'{pos} Player', f'{pos} Total Points', f'{pos} Average Points']
    
    # Join with the main layout DataFrame
    top_players_layout = pd.concat([top_players_layout, pos_data], axis=1)

### Section 3: Top Performer of the Week by Position
weekly_data = []

# Hard-coded data for weeks 1-4
hard_coded_data = [
    {'Week': 'Week 1',
     'QB Player': 'Baker Mayfield', 'QB Points': 37.1,
     'RB Player': 'Saquon Barkley', 'RB Points': 32.2,
     'WR Player': 'Jayden Reed', 'WR Points': 31.1,
     'TE Player': 'Isaiah Likely', 'TE Points': 21.6,
     'D/ST Player': 'Bears D/ST', 'D/ST Points': 26,
     'K Player': 'Jake Moody', 'K Points': 26},
     
    {'Week': 'Week 2',
     'QB Player': 'Kyler Murray', 'QB Points': 33.9,
     'RB Player': 'Alvin Kamara', 'RB Points': 43,
     'WR Player': 'Marvin Harrison Jr.', 'WR Points': 27,
     'TE Player': 'George Kittle', 'TE Points': 17.1,
     'D/ST Player': 'Bills D/ST', 'D/ST Points': 16,
     'K Player': 'Austin Seibert', 'K Points': 22},
     
    {'Week': 'Week 3',
     'QB Player': 'Josh Allen', 'QB Points': 38.4,
     'RB Player': 'Saquon Barkley', 'RB Points': 31.6,
     'WR Player': 'Juan Jennings', 'WR Points': 41,
     'TE Player': 'Dallas Goedert', 'TE Points': 22,
     'D/ST Player': 'Packers D/ST', 'D/ST Points': 23,
     'K Player': 'Wil Lutz', 'K Points': 16},
     
    {'Week': 'Week 4',
     'QB Player': 'Jordan Love', 'QB Points': 35.6,
     'RB Player': 'Derrick Henry', 'RB Points': 34.4,
     'WR Player': 'Nico Collins', 'WR Points': 27.1,
     'TE Player': 'Taysom Hill', 'TE Points': 14.4,
     'D/ST Player': '49ers D/ST', 'D/ST Points': 23,
     'K Player': 'Nick Folk', 'K Points': 24},
]

# Adding hard-coded data to the weekly data
for entry in hard_coded_data:
    weekly_data.append(entry)

# Now gather data for weeks 5-14
max_weeks = 14  # Limit to weeks 1 through 14

# Loop through weeks 5 to 14
for week in range(4, max_weeks):
    week_label = f'Week {week + 1}'  # Correct week labeling
    week_top_performers = {}

    for pos in positions:
        all_players = []

        # Loop through each team to find players by position
        for team in league.teams:
            for player in team.roster:
                if player.position == pos:
                    # Fetch the player's points for the specific week from the player's stats
                    weekly_points = player.stats.get(week + 1, {}).get('points', 0)  # Use week + 1 since stats are 1-based
                    
                    # Only include players who have played that week
                    if weekly_points > 0:
                        # Add player and their points for that week
                        all_players.append({
                            'Player': player.name,
                            'Position': pos,
                            'Points': weekly_points
                        })

        # Find the top player for this position for the current week
        if all_players:
            top_player = max(all_players, key=lambda x: x['Points'])
            if top_player['Points'] > 0:  # Only include players with points
                week_top_performers[pos] = (top_player['Player'], top_player['Points'])

    # Add top performers to the weekly data, leaving blanks for unplayed weeks
    week_data = {'Week': week_label}
    for pos in positions:
        if pos in week_top_performers:
            week_data[f'{pos} Player'] = week_top_performers[pos][0]
            week_data[f'{pos} Points'] = week_top_performers[pos][1]
        else:
            week_data[f'{pos} Player'] = ''
            week_data[f'{pos} Points'] = ''
    
    weekly_data.append(week_data)

# Create DataFrame from the weekly data
df_weekly = pd.DataFrame(weekly_data)
### Export to Excel
with pd.ExcelWriter('fantasy_football_stats.xlsx', engine='xlsxwriter') as writer:
    df_teams.to_excel(writer, sheet_name='Team Stats', index=False)
    
    # Export the Top Players layout
    top_players_layout.to_excel(writer, sheet_name='Top 10 Players by Position', index=True)
    
    # Export the Weekly Performers layout (including weeks 1-14)
    df_weekly.to_excel(writer, sheet_name='Top Performers by Week', index=False)

print("Fantasy Football data for weeks 1-14 exported to fantasy_football_stats.xlsx")
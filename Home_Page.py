import pandas as pd
import streamlit as st

# Load the data
asi_data = pd.read_csv('Processed_ASI_Data.csv')

# Page configuration
st.set_page_config(page_title='MLS Trade Machine', page_icon='Handshake.png')

# App title
st.title("MLS Trade Machine")

# Description
st.markdown("Select the two teams to view players to trade between teams.")

# Create two columns for team selection
col1, col2 = st.columns(2)

# Get the unique team names and sort them
teams = sorted(list(asi_data['team_name'].unique()))

# Handle the first team selection
selected_team = st.session_state.get('selected_team', teams[0])
if selected_team not in teams:
    selected_team = teams[0]  # Default to the first team if the session state value is invalid

with col1:
    selected_team = st.selectbox('Choose the First Team:', teams, index=teams.index(selected_team))
    st.session_state['selected_team'] = selected_team

# Filter out the selected team from the second dropdown options
teams_for_second_selection = [team for team in teams if team != selected_team]

# Handle the second team selection
selected_team2 = st.session_state.get('selected_team2', teams_for_second_selection[0])
if selected_team2 not in teams_for_second_selection:
    selected_team2 = teams_for_second_selection[0]  # Default to the first available team if invalid

with col2:
    selected_team2 = st.selectbox('Choose the Second Team:', teams_for_second_selection, index=teams_for_second_selection.index(selected_team2))
    st.session_state['selected_team2'] = selected_team2

# removing DP players for the team being
asi_data.loc[asi_data['base_salary'] >= 743750, 'base_salary'] = 743750

# getting the amount spent by each team
raw_salaries = asi_data.groupby(['team_name', 'team_abbreviation'])['base_salary'].sum().reset_index()

# getting the salary cap for 2025
cap = 5950000

# getting the tam for 2025
tam = 2225000

# subtracting TAM
raw_salaries['base_salary'] = raw_salaries['base_salary'] - tam

# getting the gam for 2025
gam = pd.read_csv('2025 GAM.csv')
raw_salaries = pd.merge(raw_salaries, gam, left_on='team_abbreviation', right_on='Team')

# Calculate total salary for each team
team_totals = raw_salaries.groupby('team_abbreviation')['base_salary'].sum().reset_index()
team_totals = team_totals.rename(columns={'base_salary': 'total_salary'})

# Merge total salary back into raw_salaries
raw_salaries = pd.merge(raw_salaries, team_totals, on='team_abbreviation')

del raw_salaries['Team'], raw_salaries['team_abbreviation'], raw_salaries['base_salary']

# Adjust GAM to bring each team under the cap
def adjust_gam(row):
    if row['total_salary'] > cap:
        # Calculate the necessary GAM adjustment
        overage = row['total_salary'] - cap
        gam_used = min(overage, row['2025 GAM'])
        return gam_used
    return 0

# Apply GAM adjustments
raw_salaries['GAM_used'] = raw_salaries.apply(adjust_gam, axis=1)

raw_salaries['Remaining GAM'] = raw_salaries['2025 GAM'] - raw_salaries['GAM_used']

# Adjust the base salary with the GAM used
raw_salaries['adjusted_salary'] = raw_salaries['total_salary'] - raw_salaries['GAM_used']

del raw_salaries['GAM_used']


# Filter players for the selected teams
first_team_players = asi_data.loc[asi_data['team_name'] == selected_team].sort_values('player_name')
second_team_players = asi_data.loc[asi_data['team_name'] == selected_team2].sort_values('player_name')

# Selected players and GAM checks
selected_players_team1 = []
selected_players_team2 = []

with col1:
    for _, player in first_team_players.iterrows():
        if st.checkbox(player['player_name'], key=f"team1_{player['player_name']}"):
            selected_players_team1.append(player)

with col2:
    for _, player in second_team_players.iterrows():
        if st.checkbox(player['player_name'], key=f"team2_{player['player_name']}"):
            selected_players_team2.append(player)

# Accumulate information for Team 2 acquiring players from Team 1
team2_gam_spent = 0
team2_gam_shortfall = 0
team2_players_acquired = []
team2_shortfall_players = []

# Temporary GAM tracker for Team 2
team2_remaining_gam_temp = raw_salaries.loc[raw_salaries['team_name'] == selected_team2, 'Remaining GAM'].iloc[0]

for player in selected_players_team1:
    player_name = player['player_name']
    player_salary = player['base_salary']

    # Check if the player can be acquired with the temporary GAM
    if team2_remaining_gam_temp >= player_salary:
        team2_gam_spent += player_salary
        team2_players_acquired.append(player_name)
        team2_remaining_gam_temp -= player_salary  # Deduct temporarily
    else:
        team2_shortfall_players.append(player)

# Accumulate information for Team 1 acquiring players from Team 2
team1_gam_spent = 0
team1_gam_shortfall = 0
team1_players_acquired = []
team1_shortfall_players = []

# Temporary GAM tracker for Team 1
team1_remaining_gam_temp = raw_salaries.loc[raw_salaries['team_name'] == selected_team, 'Remaining GAM'].iloc[0]

for player in selected_players_team2:
    player_name = player['player_name']
    player_salary = player['base_salary']

    # Check if the player can be acquired with the temporary GAM
    if team1_remaining_gam_temp >= player_salary:
        team1_gam_spent += player_salary
        team1_players_acquired.append(player_name)
        team1_remaining_gam_temp -= player_salary  # Deduct temporarily
    else:
        team1_shortfall_players.append(player)

# Final GAM adjustments after all transactions
team1_remaining_gam = (
    raw_salaries.loc[raw_salaries['team_name'] == selected_team, 'Remaining GAM'].iloc[0]
    - team1_gam_spent
    + team2_gam_spent
)

team2_remaining_gam = (
    raw_salaries.loc[raw_salaries['team_name'] == selected_team2, 'Remaining GAM'].iloc[0]
    - team2_gam_spent
    + team1_gam_spent
)

# Determine which shortfall players can now be acquired
team2_resolved_acquisitions = []
for player in team2_shortfall_players:
    player_name = player['player_name']
    player_salary = player['base_salary']

    if team2_remaining_gam >= player_salary:
        team2_gam_spent += player_salary
        team2_resolved_acquisitions.append(player_name)
        team2_remaining_gam -= player_salary

team2_shortfall_players = [
    player['player_name']
    for player in team2_shortfall_players
    if player['player_name'] not in team2_resolved_acquisitions
]

team1_resolved_acquisitions = []
for player in team1_shortfall_players:
    player_name = player['player_name']
    player_salary = player['base_salary']

    if team1_remaining_gam >= player_salary:
        team1_gam_spent += player_salary
        team1_resolved_acquisitions.append(player_name)
        team1_remaining_gam -= player_salary

team1_shortfall_players = [
    player['player_name']
    for player in team1_shortfall_players
    if player['player_name'] not in team1_resolved_acquisitions
]

# Add resolved acquisitions to the acquired lists
team2_players_acquired.extend(team2_resolved_acquisitions)
team1_players_acquired.extend(team1_resolved_acquisitions)

# Display results for Team 2
if team2_players_acquired:
    st.success(f"{selected_team2} have acquired players: {', '.join(team2_players_acquired)}. Total GAM spent: \${int(team2_gam_spent):,}. {selected_team2} still have \${int(team2_remaining_gam):,} GAM remaining.")
if team2_shortfall_players:
    total_team2_shortfall = sum(player['base_salary'] for player in selected_players_team1 if player['player_name'] in team2_shortfall_players)
    st.error(f"{selected_team2} could not acquire players: {', '.join(team2_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team2_shortfall):,}.")

# Display results for Team 1
if team1_players_acquired:
    st.success(f"{selected_team} have acquired players: {', '.join(team1_players_acquired)}. Total GAM spent: \${int(team1_gam_spent):,}. {selected_team} still have \${int(team1_remaining_gam):,} GAM remaining.")
if team1_shortfall_players:
    total_team1_shortfall = sum(player['base_salary'] for player in selected_players_team2 if player['player_name'] in team1_shortfall_players)
    st.error(f"{selected_team} could not acquire players: {', '.join(team1_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team1_shortfall):,}.")

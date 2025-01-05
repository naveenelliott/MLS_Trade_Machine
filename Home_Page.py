import pandas as pd
import streamlit as st

# Load the data
asi_data = pd.read_csv('FinalCombinedDataset.csv')

rule_checking = asi_data.copy()

team_data = pd.read_csv('Team_Models.csv')

# Page configuration
st.set_page_config(page_title='MLS Trade Machine', page_icon='Handshake.png')

st.write(team_data)

# App title
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'AccidentalPresidency';
        src: url('AccidentalPresidency.ttf');
    }
    .center-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        font-family: 'AccidentalPresidency', sans-serif;
    }
    </style>
    <h1 class="center-title">MLS Trade Machine</h1>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Belanosima';
        src: url('Belanosima-SemiBold.ttf'); /* Ensure the file is accessible */
    }
    .subheader-text {
        font-family: 'Belanosima', sans-serif;
        font-size: 1.5em;
        font-weight: 500;
        color: black; /* Optional: Customize the color */
        margin-bottom: 0.5em; /* Add space below the subheader */
    }
    </style>
    <div class="subheader-text">
        This application simplifies the rules of MLS to determine whether a team can acquire specific player(s).
    </div>
    """,
    unsafe_allow_html=True
)

# Description
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'CookbookNormalRegular';
        src: url('CookbookNormalRegular-6YmjD.ttf');
    }
    .description-text {
        font-family: 'CookbookNormalRegular', sans-serif;
        font-size: 0.95em;
        line-height: 1.6; /* Adjust spacing for readability */
        margin-bottom: 0.7em; /* Add space below the subheader */
    }
    </style>
    <div class="description-text">
        1) Select the two teams you would like to make a transaction between OR select a first team and toggle the free agents button.<br>
        2) If two teams are selected, then toggle the player(s) you would like to trade between teams. If Free Agents are toggled, type the desired free agent into the search box and select their name.<br>
        3) Scroll down to see whether a team can make that transaction.
    </div>
    """,
    unsafe_allow_html=True
)

# Create two columns for team selection
col1, col2, col3 = st.columns(3)

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

with col3:
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
first_team_players = asi_data.loc[asi_data['team_name'] == selected_team].sort_values('NAME')
second_team_players = asi_data.loc[asi_data['team_name'] == selected_team2].sort_values('NAME')

# Selected players and GAM checks
selected_players_team1 = []
selected_players_team2 = []

with col1:
    for _, player in first_team_players.iterrows():
        if st.checkbox(player['NAME'], key=f"team1_{player['NAME']}"):
            selected_players_team1.append(player)

with col3:
    for _, player in second_team_players.iterrows():
        if st.checkbox(player['NAME'], key=f"team2_{player['NAME']}"):
            selected_players_team2.append(player)

# Accumulate information for Team 2 acquiring players from Team 1
team2_gam_spent = 0
team2_gam_shortfall = 0
team2_players_acquired = []
team2_shortfall_players = []

# Temporary GAM tracker for Team 2
team2_remaining_gam_temp = raw_salaries.loc[raw_salaries['team_name'] == selected_team2, 'Remaining GAM'].iloc[0]

for player in selected_players_team1:
    player_name = player['NAME']
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
    player_name = player['NAME']
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
    player_name = player['NAME']
    player_salary = player['base_salary']

    if team2_remaining_gam >= player_salary:
        team2_gam_spent += player_salary
        team2_resolved_acquisitions.append(player_name)
        team2_remaining_gam -= player_salary

team2_shortfall_players = [
    player['NAME']
    for player in team2_shortfall_players
    if player['NAME'] not in team2_resolved_acquisitions
]

team1_resolved_acquisitions = []
for player in team1_shortfall_players:
    player_name = player['NAME']
    player_salary = player['base_salary']

    if team1_remaining_gam >= player_salary:
        team1_gam_spent += player_salary
        team1_resolved_acquisitions.append(player_name)
        team1_remaining_gam -= player_salary

team1_shortfall_players = [
    player['NAME']
    for player in team1_shortfall_players
    if player['NAME'] not in team1_resolved_acquisitions
]

# Add resolved acquisitions to the acquired lists
team2_players_acquired.extend(team2_resolved_acquisitions)
team1_players_acquired.extend(team1_resolved_acquisitions)

for player in selected_players_team1+selected_players_team2:
    if player['ROSTER DESIGNATION'] == 'Designated Player':
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'Designated Player'
        ] -= 1
    elif player['ROSTER DESIGNATION'] == 'U22 Initiative':
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'U22 Initiative'
        ] -= 1


transfer_team = selected_team2



if isinstance(selected_players_team1, list):
    selected_players_team1 = pd.DataFrame(selected_players_team1)

    # Assign the transfer team column
    selected_players_team1['Transfer Team'] = transfer_team

    for _, new_player in selected_players_team1.iterrows():
        if new_player['ROSTER DESIGNATION'] == 'Designated Player':
            new_player = pd.DataFrame([new_player])
            new_player = pd.merge(new_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
            if new_player['Designated Player'].iloc[0] < new_player['Max Designated Players'].iloc[0]:
                difference = new_player['Max Designated Players'].iloc[0] - new_player['Designated Player'].iloc[0]
                #st.success(f"You have used one of {selected_team}'s available DP spots. They have {difference} spots remaining.")
                continue
            else:
                team1_dps = second_team_players.loc[second_team_players['ROSTER DESIGNATION'] == 'Designated Player']
                team1_dps = team1_dps['NAME']
                st.error(f"{selected_team2} could not acquire players: {new_player['NAME'][0]}. Too many Designated Players. You need to move on from one of these players: {', '.join(team1_dps)}.")

                if new_player['NAME'][0] in team2_players_acquired:
                    team2_players_acquired.remove(new_player['NAME'][0])
                if new_player['NAME'][0] in team2_shortfall_players:
                    team2_shortfall_players.remove(new_player['NAME'][0])

        elif new_player['ROSTER DESIGNATION'] == 'U22 Initiative':
            new_player = pd.DataFrame([new_player])
            new_player = pd.merge(new_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
            if new_player['U22 Initiative'].iloc[0] < new_player['Max U22 Initiative Players'].iloc[0]:
                difference = new_player['Max U22 Initiative Players'].iloc[0] - new_player['U22 Initiative'].iloc[0]
                #st.success(f"You have used one of {selected_team}'s available U22 Initative spots. They have {difference} spots remaining.")
                continue
            else:
                team1_u22 = second_team_players.loc[second_team_players['ROSTER DESIGNATION'] == 'U22 Initiative']
                team1_u22 = team1_u22['NAME']
                st.error(f"{selected_team2} could not acquire players: {new_player['NAME'][0]}. Too many U22 Initiative Players. You need to move on from one of these players: {', '.join(team1_u22)}.")

                if new_player['NAME'][0] in team2_players_acquired:
                    team2_players_acquired.remove(new_player['NAME'][0])
                if new_player['NAME'][0] in team2_shortfall_players:
                    team2_shortfall_players.remove(new_player['NAME'][0])

transfer_team2 = selected_team

if isinstance(selected_players_team2, list):
    selected_players_team2 = pd.DataFrame(selected_players_team2)

    selected_players_team2['Transfer Team'] = transfer_team2

    for _, new_player in selected_players_team2.iterrows():
        if new_player['ROSTER DESIGNATION'] == 'Designated Player':
            new_player = pd.DataFrame([new_player])
            new_player = pd.merge(new_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
            if new_player['Designated Player'].iloc[0] < new_player['Max Designated Players'].iloc[0]:
                difference = new_player['Max Designated Players'].iloc[0] - new_player['Designated Player'].iloc[0]
                #st.success(f"You have used one of {selected_team2}'s available DP spots. They have {difference} spots remaining.")
                continue
            else:
                team2_dps = first_team_players.loc[first_team_players['ROSTER DESIGNATION'] == 'Designated Player']
                team2_dps = team2_dps['NAME']
                st.error(f"{selected_team} could not acquire player(s): {new_player['NAME'][0]}. Too many Designated Players. You need to move on from one of these players: {', '.join(team2_dps)}.")
        
                if new_player['NAME'][0] in team1_players_acquired:
                    team1_players_acquired.remove(new_player['NAME'][0])
                if new_player['NAME'][0] in team1_shortfall_players:
                    team1_shortfall_players.remove(new_player['NAME'][0])
        elif new_player['ROSTER DESIGNATION'] == 'U22 Initiative':
            new_player = pd.DataFrame([new_player])
            new_player = pd.merge(new_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
            if new_player['U22 Initiative'].iloc[0] < new_player['Max U22 Initiative Players'].iloc[0]:
                difference = new_player['Max U22 Initiative Players'].iloc[0] - new_player['U22 Initiative'].iloc[0]
                #st.success(f"You have used one of {selected_team2}'s available U22 Initative spots. They have {difference} spots remaining.")
                continue
            else:
                team2_u22 = first_team_players.loc[first_team_players['ROSTER DESIGNATION'] == 'U22 Initiative']
                team2_u22 = team2_u22['NAME']
                st.error(f"{selected_team} could not acquire player(s): {new_player['NAME'][0]}. Too many U22 Initiative Players. You need to move on from one of these players: {', '.join(team2_u22)}.")

                if new_player['NAME'][0] in team1_players_acquired:
                    team1_players_acquired.remove(new_player['NAME'][0])
                if new_player['NAME'][0] in team1_shortfall_players:
                    team1_shortfall_players.remove(new_player['NAME'][0])
#first_team_dp = 

# Display results for Team 2
if team2_players_acquired:
    st.success(f"{selected_team2} have acquired players: {', '.join(team2_players_acquired)}. Total GAM spent: \${int(team2_gam_spent):,}. {selected_team2} still have \${int(team2_remaining_gam):,} GAM remaining.")
if team2_shortfall_players:
    total_team2_shortfall = sum(player['base_salary'] for player in selected_players_team1 if player['NAME'] in team2_shortfall_players)
    st.error(f"{selected_team2} could not acquire players: {', '.join(team2_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team2_shortfall):,}.")

# Display results for Team 1
if team1_players_acquired:
    st.success(f"{selected_team} have acquired players: {', '.join(team1_players_acquired)}. Total GAM spent: \${int(team1_gam_spent):,}. {selected_team} still have \${int(team1_remaining_gam):,} GAM remaining.")
if team1_shortfall_players:
    total_team1_shortfall = sum(player['base_salary'] for player in selected_players_team2 if player['NAME'] in team1_shortfall_players)
    st.error(f"{selected_team} could not acquire players: {', '.join(team1_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team1_shortfall):,}.")

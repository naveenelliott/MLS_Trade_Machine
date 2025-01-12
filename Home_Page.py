import pandas as pd
import streamlit as st

# Load the data
asi_data = pd.read_csv('./Data/FinalCombinedDataset.csv')
asi_data['NAME'] = asi_data['NAME'].str.title()
rule_checking = asi_data.copy()
team_data = pd.read_csv('./Data/Team_Models.csv')

st.set_page_config(layout="wide", page_title='MLS Trade Machine', page_icon='Handshake.png')
#st.write(team_data)

# App title
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'AccidentalPresidency';
        src: url('./Fonts/AccidentalPresidency.ttf');
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
        src: url('./Fonts/Belanosima-SemiBold.ttf'); /* Ensure the file is accessible */
    }
    .subheader-text {
        font-family: 'Belanosima', sans-serif;
        font-size: 1.5em;
        text-align: center;
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
with st.expander("Instructions", expanded=True):
    st.write(
        """
        1) Select the two teams you would like to make a transaction between.
        2) If two teams are selected, then toggle the player(s) you would like to trade between teams.
        3) Look at trade notifications to see whether a team can make that transaction.
        """
    )
st.divider()
# Create two columns for team selection
col1, col2, col3 = st.columns(3)

# Get the unique team names and sort them
teams = sorted(list(asi_data['team_name'].unique()))

# Handle the first team selection
selected_team = st.session_state.get('selected_team', teams[0])
if selected_team not in teams:
    selected_team = teams[0]  # Default to the first team if the session state value is invalid

roster_options = team_data['Model'].unique()

with col1:
    selected_team = st.selectbox('Choose the First Team:', teams, index=teams.index(selected_team))
    st.session_state['selected_team'] = selected_team
    team_1_data = team_data.loc[team_data['team_name'] == selected_team].reset_index(drop=True)


# Filter out the selected team from the second dropdown options
teams_for_second_selection = [team for team in teams if team != selected_team]

# Handle the second team selection
selected_team2 = st.session_state.get('selected_team2', teams_for_second_selection[0])
if selected_team2 not in teams_for_second_selection:
    selected_team2 = teams_for_second_selection[0]  # Default to the first available team if invalid

with col3:
    selected_team2 = st.selectbox('Choose the Second Team:', teams_for_second_selection, index=teams_for_second_selection.index(selected_team2))
    st.session_state['selected_team2'] = selected_team2
    team_2_data = team_data.loc[team_data['team_name'] == selected_team2].reset_index(drop=True)

with col2:    
    if (team_1_data['Total Designated Players'][0] != 3) and (team_1_data['U22 Initiative'][0] != 4):
        st.write(f'{selected_team} has roster flexibility. Choose a model to build a roster around. More info here.')
        
        # Radio for Team 1 with a unique key
        selected_roster_option_team1 = st.radio(
            f"Choose a roster model for {selected_team}:",
            roster_options,
            key=f"{selected_team}_roster_model"  # Unique key for Team 1
        )

        team_data.loc[team_data['team_name'] == selected_team, 'Model'] = selected_roster_option_team1

        if selected_roster_option_team1 == 'U22 Initiative Player Model':
            team_data.loc[team_data['team_name'] == selected_team, 'Max Designated Players'] = 2
            team_data.loc[team_data['team_name'] == selected_team, 'Max U22 Initiative Players'] = 4
        elif selected_roster_option_team1 == 'Three Designated Player Model':
            team_data.loc[team_data['team_name'] == selected_team, 'Max Designated Players'] = 3
            team_data.loc[team_data['team_name'] == selected_team, 'Max U22 Initiative Players'] = 3


    if (team_2_data['Total Designated Players'][0] != 3) and (team_2_data['U22 Initiative'][0] != 4):
        st.write(f'{selected_team2} has roster flexibility. Choose a model to build a roster around. More info here.')
        
        # Radio for Team 2 with a unique key
        selected_roster_option_team2 = st.radio(
            f"Choose a roster model for {selected_team2}:",
            roster_options,
            key=f"{selected_team2}_roster_model"  # Unique key for Team 2
        )

        team_data.loc[team_data['team_name'] == selected_team2, 'Model'] = selected_roster_option_team2

        if selected_roster_option_team2 == 'U22 Initiative Player Model':
            team_data.loc[team_data['team_name'] == selected_team2, 'Max Designated Players'] = 2
            team_data.loc[team_data['team_name'] == selected_team2, 'Max U22 Initiative Players'] = 4
        elif selected_roster_option_team2 == 'Three Designated Player Model':
            team_data.loc[team_data['team_name'] == selected_team2, 'Max Designated Players'] = 3
            team_data.loc[team_data['team_name'] == selected_team2, 'Max U22 Initiative Players'] = 3

st.divider()
# 2025 DP charge - 743750
# 2024 DP charge - 683750


asi_data.loc[asi_data['ROSTER DESIGNATION'] == 'Designated Player', 'base_salary'] = 743750

# have to use 2024 records
asi_data.loc[(asi_data['ROSTER DESIGNATION'] == 'Young Designated Player') & (asi_data['age'] <= 20), 'base_salary'] = 150000

# have to use 2024 records
asi_data.loc[(asi_data['ROSTER DESIGNATION'] == 'Young Designated Player') & (asi_data['age'] <= 23) & (asi_data['age'] >= 21), 'base_salary'] = 200000

# have to use 2024 records
asi_data.loc[(asi_data['ROSTER DESIGNATION'] == 'U22 Initiative') & (asi_data['age'] <= 20), 'base_salary'] = 150000

# have to use 2024 records
asi_data.loc[(asi_data['ROSTER DESIGNATION'] == 'U22 Initiative') & (asi_data['age'] <= 25) & (asi_data['age'] >= 21), 'base_salary'] = 200000

# need to eventually go through and for each TAM Player in the range of 683750 to 1683750, need to buy them down to 683750 until we use it all up
# the remaining gets converted into GAM amount


# getting the amount spent by each team
raw_salaries = asi_data.groupby(['team_name', 'team_abbreviation'])['base_salary'].sum().reset_index()

# getting the salary cap for 2025
cap = 5950000

# getting the tam for 2025
tam = 2225000

# subtracting TAM
raw_salaries['base_salary'] = raw_salaries['base_salary'] - tam

# getting the gam for 2025
gam = pd.read_csv('./Data/2025 GAM.csv')
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

# Prepare lists of player names
first_team_player_names = first_team_players['NAME'].tolist()
second_team_player_names = second_team_players['NAME'].tolist()

# Multi-select dropdown for the first team
with col1:
    selected_players_team1_names = st.multiselect(
        "Select First Team Players",
        options=first_team_player_names,
        key="team1_multiselect"
    )
    # Retrieve full player details for selected players
    selected_players_team1 = first_team_players[
        first_team_players['NAME'].isin(selected_players_team1_names)
    ]

# Multi-select dropdown for the second team
with col3:
    selected_players_team2_names = st.multiselect(
        "Select Second Team Players",
        options=second_team_player_names,
        key="team2_multiselect"
    )
    # Retrieve full player details for selected players
    selected_players_team2 = second_team_players[
        second_team_players['NAME'].isin(selected_players_team2_names)
    ]

combined_players = pd.concat([selected_players_team1, selected_players_team2])

for _, player in combined_players.iterrows():
    if player['ROSTER DESIGNATION'] == 'Designated Player':
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'Total Designated Players'
        ] -= 1
    elif player['ROSTER DESIGNATION'] == 'U22 Initiative':
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'U22 Initiative'
        ] -= 1
    if player['INTERNATIONAL'] == True:
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'Slot Numbers'
        ] -= 1
        team_data.loc[
            team_data['team_abbreviation'] == player['team_abbreviation'], 
            'Unfilled Slots'
        ] += 1

team1_notifications = []
team2_notifications = []

transfer_team = selected_team2

# Process selected players for Team 1
selected_players_team1 = pd.DataFrame(selected_players_team1)
selected_players_team1['Transfer Team'] = transfer_team
players_to_remove_team1 = []

for _, new_player in selected_players_team1.iterrows():
    if new_player['ROSTER DESIGNATION'] == 'Designated Player':
        temp_player = pd.DataFrame([new_player])
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
        if (temp_player['Total Designated Players'].iloc[0] >= temp_player['Max Designated Players'].iloc[0]):
            team1_dps = second_team_players.loc[second_team_players['ROSTER DESIGNATION'] == 'Designated Player']
            team1_dps = team1_dps['NAME']
            message = {
                "type": "error",
                "message": f"{selected_team2} could not acquire players: {new_player['NAME']} because there are too many DPs. They need to move on from one of these players: {', '.join(team1_dps)}."
            }
            team2_notifications.append(message)
            players_to_remove_team1.append(new_player['NAME'])
        else:
            team_data.loc[team_data['team_name'] == selected_team2, 'Total Designated Players'] += 1

    elif new_player['ROSTER DESIGNATION'] == 'U22 Initiative':
        temp_player = pd.DataFrame([new_player])
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
        if temp_player['U22 Initiative'].iloc[0] >= temp_player['Max U22 Initiative Players'].iloc[0]:
            team1_u22 = second_team_players.loc[second_team_players['ROSTER DESIGNATION'] == 'U22 Initiative']
            team1_u22 = team1_u22['NAME']
            message = {
                "type": "error",
                "message": f"{selected_team2} could not acquire players: {new_player['NAME']} because there are too many U22 Initiative players. They need to move on from one of these players: {', '.join(team1_u22)}."
            }
            team2_notifications.append(message)
            players_to_remove_team1.append(new_player['NAME'])
        else:
            team_data.loc[team_data['team_name'] == selected_team2, 'U22 Initiative'] += 1

    # Remove players after the loop
if not selected_players_team1.empty:  # Check if the DataFrame is not empty
    selected_players_team1 = selected_players_team1[~selected_players_team1['NAME'].isin(players_to_remove_team1)]

transfer_team2 = selected_team
# Process selected players for Team 2
selected_players_team2 = pd.DataFrame(selected_players_team2)
selected_players_team2['Transfer Team'] = transfer_team2


players_to_remove_team2 = []

for _, new_player in selected_players_team2.iterrows():
    if new_player['ROSTER DESIGNATION'] == 'Designated Player':
        temp_player = pd.DataFrame([new_player])
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
        if temp_player['Total Designated Players'].iloc[0] >= temp_player['Max Designated Players'].iloc[0] and ( temp_player['Model'].iloc[0] != "Three Designated Player Model"):
            team2_dps = first_team_players.loc[first_team_players['ROSTER DESIGNATION'] == 'Designated Player']
            team2_dps = team2_dps['NAME']
            message = {
                "type": "error",
                "message": f"{selected_team} could not acquire player(s): {new_player['NAME']} because there are too many DPs. They need to move on from one of these players: {', '.join(team2_dps)}."
            }
            team1_notifications.append(message)
            players_to_remove_team2.append(new_player['NAME'])
        else:
            team_data.loc[team_data['team_name'] == selected_team, 'Total Designated Players'] += 1

    elif new_player['ROSTER DESIGNATION'] == 'U22 Initiative':
        temp_player = pd.DataFrame([new_player])
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)
        if temp_player['U22 Initiative'].iloc[0] >= temp_player['Max U22 Initiative Players'].iloc[0]:
            team2_u22 = first_team_players.loc[first_team_players['ROSTER DESIGNATION'] == 'U22 Initiative']
            team2_u22 = team2_u22['NAME']
            message = {
                "type": "error",
                "message": f"{selected_team} could not acquire player(s): {new_player['NAME']} because there are too many U22 Initiative players. They need to move on from one of these players: {', '.join(team2_u22)}."
            }
            team1_notifications.append(message)
            players_to_remove_team2.append(new_player['NAME'])
        else:
            team_data.loc[team_data['team_name'] == selected_team, 'U22 Initiative'] += 1

# Remove players after the loop
if not selected_players_team2.empty:  # Check if the DataFrame is not empty
    selected_players_team2 = selected_players_team2[~selected_players_team2['NAME'].isin(players_to_remove_team2)]


# Accumulate information for Team 2 acquiring players from Team 1
team2_gam_spent = 0
team2_gam_shortfall = 0
team2_players_acquired = []
team2_shortfall_players = []

# Accumulate information for Team 1 acquiring players from Team 2
team1_gam_spent = 0
team1_gam_shortfall = 0
team1_players_acquired = []
team1_shortfall_players = []

# Temporary GAM tracker for Team 2
team2_remaining_gam_temp = raw_salaries.loc[raw_salaries['team_name'] == selected_team2, 'Remaining GAM'].iloc[0]

for _, player in selected_players_team1.iterrows():
    player_name = player['NAME']
    player_salary = player['base_salary']

    # Check if the player can be acquired with the temporary GAM
    if team2_remaining_gam_temp >= player_salary:
        team2_gam_spent += player_salary
        team2_players_acquired.append(player_name)
        team2_remaining_gam_temp -= player_salary  # Deduct temporarily
    else:
        team2_shortfall_players.append(player)


# Temporary GAM tracker for Team 1
team1_remaining_gam_temp = raw_salaries.loc[raw_salaries['team_name'] == selected_team, 'Remaining GAM'].iloc[0]
for _, player in selected_players_team2.iterrows():
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

# Temporary GAM tracker for international slot charges
team2_international_gam_spent = 0
team1_international_gam_spent = 0

# Process Team 1 to Team 2 transactions
for _, player in selected_players_team1.iterrows():
    if player['INTERNATIONAL']:
        temp_player = pd.DataFrame([player])
        temp_player['Transfer Team'] = selected_team2
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)

        if temp_player['Unfilled Slots'].iloc[0] <= 0:
            message = {
                "type": "info",
                "message": f"{selected_team2} needs to acquire an international slot for {temp_player['NAME'][0]}. This will cost $175,000 in GAM."
            }
            team2_notifications.append(message)
            team2_international_gam_spent += 175000
        else:
            team_abbr = temp_player['Transfer Team'].iloc[0]
            team_data.loc[team_data['team_name'] == team_abbr, 'Slot Numbers'] += 1
            team_data.loc[team_data['team_name'] == team_abbr, 'Unfilled Slots'] -= 1

# Process Team 2 to Team 1 transactions
for _, player in selected_players_team2.iterrows():
    if player['INTERNATIONAL']:
        temp_player = pd.DataFrame([player])
        temp_player['Transfer Team'] = selected_team
        temp_player = pd.merge(temp_player, team_data, left_on='Transfer Team', right_on='team_name', how='inner').reset_index(drop=True)

        if temp_player['Unfilled Slots'].iloc[0] <= 0:
            message = {
                "type": "info",
                "message": f"{selected_team} needs to acquire an international slot for {temp_player['NAME'][0]}. This will cost $175,000 in GAM."
            }
            team1_notifications.append(message)
            team1_international_gam_spent += 175000
        else:
            team_abbr = temp_player['Transfer Team'].iloc[0]
            team_data.loc[team_data['team_name'] == team_abbr, 'Slot Numbers'] += 1
            team_data.loc[team_data['team_name'] == team_abbr, 'Unfilled Slots'] -= 1

# Adjust remaining GAM after international slot charges
team2_remaining_gam -= team2_international_gam_spent
team1_remaining_gam -= team1_international_gam_spent

team2_gam_spent += team2_international_gam_spent
team1_gam_spent += team1_international_gam_spent

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

# Display results for Team 2
if team2_players_acquired:
    message = {
                "type": "success",
                "message": f"{selected_team2} have acquired players: {', '.join(team2_players_acquired)}. Total GAM spent: \${int(team2_gam_spent):,}. {selected_team2} still have \${int(team2_remaining_gam):,} GAM remaining."
            }
    team2_notifications.append(message)
if team2_shortfall_players:
    total_team2_shortfall = (
        selected_players_team1.loc[
            selected_players_team1['NAME'].isin(team2_shortfall_players), 'base_salary'
        ].sum()
    )
    message = {
                "type": "error",
                "message": f"{selected_team2} could not acquire players: {', '.join(team2_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team2_shortfall):,}."
            }
    team2_notifications.append(message)

if team1_players_acquired:
    message = {
                "type": "success",
                "message": f"{selected_team} have acquired players: {', '.join(team1_players_acquired)}. Total GAM spent: \${int(team1_gam_spent):,}. {selected_team} still have \${int(team1_remaining_gam):,} GAM remaining."
            }
    team1_notifications.append(message)
if team1_shortfall_players:
    total_team1_shortfall = (
        selected_players_team2.loc[
            selected_players_team2['NAME'].isin(team1_shortfall_players), 'base_salary'
        ].sum()
    )
    message = {
                "type": "error",
                "message": f"{selected_team} could not acquire players: {', '.join(team1_shortfall_players)}. The additional GAM needed after all transactions: \${int(total_team1_shortfall):,}."
            }
    team1_notifications.append(message)

with st.expander(f"🔔 {selected_team2} to {selected_team} Trade notifications", expanded=True):
    for notification in team1_notifications:
        # Display each notification with an icon based on the type
        if notification['type'] == 'success':
            st.success(notification['message'])
        elif notification['type'] == 'error':
            st.error(notification['message'])
        elif notification['type'] == 'info':
            st.info(notification['message'])

with st.expander(f"🔔 {selected_team} to {selected_team2} Trade notifications", expanded=True):
    for notification in team2_notifications:
        # Display each notification with an icon based on the type
        if notification['type'] == 'success':
            st.success(notification['message'])
        elif notification['type'] == 'error':
            st.error(notification['message'])
        elif notification['type'] == 'info':
            st.info(notification['message'])
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Establish connection to Google Sheets
conn = st.connection('gsheets', type=GSheetsConnection)

# Read google sheets data
existing_data = conn.read(worksheet='Player_New_Team', ttl=0)
existing_data.dropna(how='all', inplace=True)
existing_data['Player'] = existing_data['Player'].fillna('').astype(str)
existing_data['Current Team'] = existing_data['Current Team'].fillna('').astype(str)
existing_data['New Team'] = existing_data['New Team'].fillna('').astype(str)

# Load player data
asi_data = pd.read_csv('./Data/FinalCombinedDataset.csv')
asi_data['NAME'] = asi_data['NAME'].str.title()

player_names = asi_data['NAME'].unique()
team_names = asi_data['team_name'].unique()
team_names = list(team_names)  # Convert to a Python list
team_names.append('No Team (Free Agent)')

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
    <h1 class="center-title">Report a Transferred Player</h1>
    """,
    unsafe_allow_html=True
)

with st.expander("Instructions", expanded=True):
    st.write(
        """
        1) Select a player that has left the team that they are currently listed on.
        2) Their current team should be automatically generated. 
        3) Select a player that has left the team that they have changed to if they are not on a team, select No Team (Free Agent).
        4) Submit and we will process the change shortly!
        """
    )
st.divider()

col1, col2, col3 = st.columns(3)

# Select Player
with col1:
    selected_player = st.multiselect(
        "Select a Player",
        options=player_names,
        max_selections=1,  # Restrict to one selection
        key="single_player_multiselect"
    )

# Getting their current team if a player is selected
if selected_player:
    selected_team = asi_data.loc[asi_data['NAME'].isin(selected_player), 'team_name'].values[0]
else:
    selected_team = None

# Display current team
with col2:
    if selected_team:
        st.markdown(
            f"<p style='font-size:14px; '>Current Team Selected: {selected_team}</p>",
            unsafe_allow_html=True
        )

# Select New Team
with col3:
    new_team = st.multiselect(
        "Select a New Team for this Player",
        options=team_names,
        max_selections=1,  # Restrict to one selection
        key="new_team_multiselect"
    )

# Add a new row to the spreadsheet
if st.button("Add Player to Spreadsheet"):
    if selected_player and new_team:
        new_row = pd.DataFrame([{
            "Player": selected_player[0],
            "Current Team": selected_team,
            "New Team": new_team[0]
        }])
        # Append the new row to the spreadsheet
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet='Player_New_Team', data=updated_data)
        st.success("Player added to spreadsheet successfully!")
    else:
        st.error("Please select both a player and a new team.")


import os
import pandas as pd

# Path to the folder containing the CSV files
folder_path = "MLS_ROSTERS_2024_FINAL/"

# List to store DataFrames from all CSVs
dataframes = []

# Loop through each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, file_name)
        # Read the CSV into a DataFrame
        df = pd.read_csv(file_path)
        df['Team'] = os.path.splitext(file_name)[0]
        dataframes.append(df)

# Combine all DataFrames into one (optional)
rosters = pd.concat(dataframes, ignore_index=True)

rosters = rosters.loc[~rosters['NAME'].isin(['SUPPLEMENTAL ROSTER', 'SUPPLEMENTAL SPOT 31'])]

international = pd.read_csv('INTERNATIONAL_SLOTS.csv')

rosters['INTERNATIONAL'] = rosters['NAME'].isin(international['NAME'])

team_mapping = {
    'ATL': 'ATLANTA',
    'ATX': 'AUSTIN',
    'CHI': 'CHICAGO',
    'CIN': 'CINCINATTI',
    'CLB': 'COLUMBUS',
    'CLT': 'CHARLOTTE',
    'COL': 'COLORADO',
    'DCU': 'DC_UNITED',
    'FCD': 'DALLAS',
    'HOU': 'HOUSTON',
    'LAFC': 'LAFC',
    'LAG': 'LAGALAXY',
    'MIA': 'INTERMAIMI',
    'MIN': 'MINNESOTA_UNITED',
    'MTL': 'MONTREAL',
    'NER': 'NEWENGLAND',
    'NSH': 'NASHVILLE_SC',
    'NYC': 'NEW_YORK',
    'NYRB': 'NYRB',
    'ORL': 'ORLANDOCITY',
    'PHI': 'PHILLY',
    'POR': 'PORTLAND',
    'RSL': 'REALSALTLAKE',
    'SEA': 'SEATTLE',
    'SJE': 'SANJOSE',
    'SKC': 'SKC',
    'STL': 'ST.LOUIS',
    'TOR': 'TORONTO',
    'VAN': 'VANCOUVER'
}
# Reverse the mapping dictionary
reverse_team_mapping = {v: k for k, v in team_mapping.items()}

# Map the `rosters['Team']` column to match `international['Team']` codes
rosters['Team'] = rosters['Team'].map(reverse_team_mapping)

rosters.to_csv('Final_Roster_Before_ASI.csv', index=False)
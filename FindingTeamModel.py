import pandas as pd

end = pd.read_csv('FinalCombinedDataset.csv')

filtered = end[end['ROSTER DESIGNATION'].isin(['Designated Player', 'U22 Initiative'])]

# Count the occurrences of each designation for each team
designation_counts = (
    filtered.groupby(['team_abbreviation', 'ROSTER DESIGNATION'])
    .size()
    .unstack(fill_value=0)  # Create columns for each designation, filling missing values with 0
).reset_index()

# Add new columns based on conditions
designation_counts['Model'] = designation_counts['Designated Player'].apply(
    lambda x: 'Three Designated Player Model' if x == 3 else 'U22 Initiative Player Model'
)

designation_counts['Max Designated Players'] = designation_counts['Designated Player'].apply(
    lambda x: 3 if x == 3 else 2
)

designation_counts['Max U22 Initiative Players'] = designation_counts['Designated Player'].apply(
    lambda x: 3 if x == 3 else 4
)

slot_numbers = pd.read_csv('INT_SLOT_NUMBERS.csv')

final = pd.merge(designation_counts, slot_numbers, left_on=['team_abbreviation'], right_on=['Team'], how='inner')

del final['Team']

final.to_csv('Team_Models.csv', index=False)
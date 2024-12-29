import pandas as pd
import os
import unicodedata

def convert_to_initial_last_name(name):
    parts = name.split()
    if len(parts) > 2 and parts[-1].lower() in ['jr.', 'jr', 'sr.', 'sr', 'iii', 'ii']:
        # Handle names with suffixes
        return f"{parts[0][0]}. {' '.join(parts[-2:])}"
    elif len(parts) > 2:  # Assume two last names if more than two parts
        return f"{parts[0][0]}. {' '.join(parts[1:])}"  # Return first name + full last names
    elif len(parts) > 1:
        # Handle regular names
        return f"{parts[0][0]}. {parts[-1]}"
    return name

def other_conversion(name):
    parts = name.split()
    if len(parts) > 2 and parts[-1].lower() in ['jr.', 'jr', 'sr.', 'sr', 'iii', 'ii']:
        # Handle names with suffixes
        return f"{parts[0][0]}. {' '.join(parts[-2:])}"
    elif len(parts) > 1:
        # Handle regular names
        return f"{parts[0][0]}. {parts[-1]}"
    return name

def normalize_name(name):
    return unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')

# Load ASI data
asi_data = pd.read_csv('Processed_ASI_Data.csv')

folder_path = 'TradeMachine/'

# Initialize an empty list to store DataFrames
dataframes = []

# Loop through files, read each, and encode the team column
for file in os.listdir(folder_path):
    if file.endswith('.csv'):
        # Extract team name from file name (before the first underscore)
        team_name = file.split('_')[0]
        
        # Read the file into a DataFrame
        df = pd.read_csv(os.path.join(folder_path, file))
        
        # Add a column for the team name
        df['team'] = team_name
        
        # Append the DataFrame to the list
        dataframes.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(dataframes, ignore_index=True)

# Normalize names
asi_data['player_name'] = asi_data['player_name'].str.lower().apply(normalize_name)
combined_df['Player'] = combined_df['Player'].str.lower().apply(normalize_name)

# Add converted names
asi_data['converted_name'] = asi_data['player_name'].apply(convert_to_initial_last_name)
asi_data['converted_name2'] = asi_data['player_name'].apply(other_conversion)

asi_data['converted_name'] = asi_data['converted_name'].replace('a. jackson', 'az')
asi_data['converted_name'] = asi_data['converted_name'].replace('c. olney jr.', 'c. olney jr')
asi_data['converted_name'] = asi_data['converted_name'].replace('y. gomez andrade', 'yeimar')
asi_data['converted_name'] = asi_data['converted_name'].replace('s. ngoma', 's. ngoma jr.')

combined_df['Player'] = combined_df['Player'].replace('thiago', 't. martins')

# Perform initial matching
matched = pd.merge(asi_data, combined_df, left_on='converted_name', right_on='Player', how='inner')

# Identify unmatched rows and attempt full-name matching
unmatched_df = asi_data[~asi_data['converted_name'].isin(matched['converted_name'])]
unmatched = unmatched_df.merge(combined_df, left_on='player_name', right_on='Player', how='inner')

# Combine matched results and drop duplicates
matched['match_source'] = 'converted_name'
unmatched['match_source'] = 'full_name'

final_matched = pd.concat([matched, unmatched], ignore_index=True).drop_duplicates()

# Final unmatched rows
final_unmatched = asi_data[~asi_data['converted_name'].isin(final_matched['converted_name'])]
unmatched_2 = final_unmatched.merge(combined_df, left_on='converted_name2', right_on='Player', how='inner')


unmatched_2['match_source'] = 'converted_name2'
final_matched = pd.concat([final_matched, unmatched_2], ignore_index=True).drop_duplicates()

final_unmatched = asi_data[~asi_data['converted_name'].isin(final_matched['converted_name'])]

final_unmatched2 = combined_df[
    ~(
        combined_df['Player'].isin(final_matched['converted_name']) |
        combined_df['Player'].isin(final_matched['player_name'])
    )
]

loaned_out = final_unmatched2.loc[final_unmatched2['Player Status'] == 'Loaned Out']
final_unmatched2 = final_unmatched2.loc[final_unmatched2['Player Status'] != 'Loaned Out']

san_diego = final_unmatched2.loc[final_unmatched2['team'] == 'sandiego']
final_unmatched2 = final_unmatched2.loc[final_unmatched2['team'] != 'sandiego']



# Save results
loaned_out.to_csv('LoanedOut_Players.csv', index=False)
san_diego.to_csv('SDFC_Players.csv', index=False)


final_matched.drop(columns=['converted_name', 'converted_name2', 'Player', 'Jersey #', 'Position', 'match_source'], inplace=True)

final_matched.rename(columns={'team_abbreviation': 'ASA_team_abbreviation', 
                              'team': 'website_team'}, inplace=True)

final_matched.to_csv('FinalCombinedDataset.csv', index=False)

final_unmatched.drop(columns=['converted_name', 'converted_name2'], inplace=True)

final_unmatched.to_csv('FreeAgentsDataset.csv', index=False)
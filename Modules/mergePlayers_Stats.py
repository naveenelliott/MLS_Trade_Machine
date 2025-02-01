import pandas as pd
import unicodedata
from rapidfuzz import process, fuzz

# --- Step 1. Normalize Names ---

def normalize_name(name):
    """Normalize names by removing accents and converting to lowercase."""
    return unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')

# Load your datasets
teamStats_data = pd.read_csv('./Data/merged_mls_stats.csv')
raw_data = pd.read_csv('./Data/RawDataForModel.csv')

# Normalize and lowercase the names in both datasets
raw_data['Player'] = raw_data['Player'].str.lower().apply(normalize_name)
teamStats_data['Player'] = teamStats_data['Player'].str.lower().apply(normalize_name)

# --- Step 2. Fuzzy Matching ---

def get_best_match(name, choices, score_cutoff=80):
    """
    Return the best matching name from choices if it meets the score_cutoff;
    otherwise, return None.
    """
    match = process.extractOne(name, choices, scorer=fuzz.ratio)
    if match and match[1] >= score_cutoff:
        return match[0]
    return None

# Create a list of unique player names from the team stats data to match against.
team_names = teamStats_data['Player'].unique()

# For each player in raw_data, attempt to find the best match in team_names.
raw_data['Matched_Player'] = raw_data['Player'].apply(lambda x: get_best_match(x, team_names))

# --- Step 3. Merge the Data (optional) ---

# If you want to merge the datasets based on the matched names:
merged_data = pd.merge(
    raw_data,
    teamStats_data,
    left_on='Matched_Player',  # the fuzzy matched name from raw_data
    right_on='Player',         # the normalized name from teamStats_data
    how='left',
    indicator=True           # adds a column to show which rows matched
)

# --- Step 4. Produce a Summary of Matches ---

# Total unique players in raw_data (before matching)
total_unique_raw = raw_data['Player'].nunique()

# Count unique players in raw_data for which a fuzzy match was found
unique_matched = raw_data[raw_data['Matched_Player'].notnull()]['Player'].nunique()

print(f"Total unique players in raw_data: {total_unique_raw}")
print(f"Unique players with a fuzzy match: {unique_matched}")

# For a detailed list: count how many times each matched team name appears.
match_counts = raw_data[raw_data['Matched_Player'].notnull()]['Matched_Player'].value_counts()

print("\nMatched players (team stats names) and their occurrence count in raw_data:")
print(match_counts.reset_index().rename(columns={'index': 'Team_Player_Name', 'Matched_Player': 'Count'}))
import pandas as pd
import unicodedata
from rapidfuzz import process, fuzz

# --- Step 1. Normalize Names ---
def normalize_name(name):
    """Normalize names by removing accents and converting to lowercase."""
    return unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')

# Load your datasets
teamStats_data = pd.read_csv('../Data/merged_mls_stats.csv')
raw_data = pd.read_csv('../Data/FinalCombinedDataset.csv')

# --- Filter: Only include rows where Season is 2024 ---
# raw_data = raw_data[raw_data['Season'] == 2024]

# Normalize and lowercase the names in both datasets
raw_data['Player'] = raw_data['NAME'].str.lower().apply(normalize_name)
teamStats_data['Player'] = teamStats_data['Player'].str.lower().apply(normalize_name)

# --- Step 2. Apply Manual Name Mappings ---
# Create a dictionary for manual corrections.
name_mapping = {
    "cucho hernandez": "cucho",                  # Cucho Hernández -> Cucho
    "alex ring": "alexander ring",               # alex ring -> Alexander Ring
    "joao klauss": "klauss",                     # joao klauss -> klauss
    "coco carrasquilla": "adalberto carrasquilla", # coco carrasquilla -> Adalberto Carrasquilla
    "nouhou": "nouhou tolo",                     # nouhou -> Nouhou Tolo
    "ibrahim aliyu": "aliyu ibrahim",             # ibrahim aliyu -> Aliyu Ibrahim
    "maxi moralez": "maximiliano moralez",       # maxi moralez -> Maximiliano Moralez
    "jesus bueno": "jesus daniel bueno",         # jesus bueno -> jesus daniel bueno
    # "andres gomez": no mapping provided, leave as is
    "chris brady": "christopher brady",          # chris brady -> Christopher Brady
    "emiro garces": "carlos garces",             # emiro garces -> Carlos Garces
    "bode hidalgo": "bode davis",                # bode hidalgo -> Bode Davis
    "ralph priso": "ralph priso-mbongue",         # ralph priso -> Ralph Priso-Mbongue
    "max arfsten": "maximilian arfsten",         # max arfsten -> Maximilian Arfsten

    # --- New Mappings ---
    "nathan": "nathan cardoso",                  # nathan -> Nathan Cardoso
    "carl sainte": "carle-fred sainte",           # carl sainte -> Carle-Fred Sainte
    "idan toklomati": "idan markovich",          # idan toklomati -> Idan Markovich
    "sang bin jeong": "jeong sangbin",            # sang bin jeong -> Jeong Sangbin
    "ben lundt": "benjamin lundt",                # ben lundt -> Benjamin Lundt
    "gabriel pec": "gabriel chaves",              # gabriel pec -> Gabriel Chaves
    "cj olney": "christopher olney"               # cj olney -> Christopher Olney
}


# Apply the mapping to the Player column in raw_data.
raw_data['Player'] = raw_data['Player'].replace(name_mapping)

# --- Step 3. Fuzzy Matching ---

def get_best_match(name, choices, score_cutoff=80):
    """
    Return the best matching name from choices if it meets the score_cutoff;
    otherwise, return None.
    """
    match = process.extractOne(name, choices, scorer=fuzz.ratio)
    if match and match[1] >= score_cutoff:
        return match[0]
    return None

# Create a list of unique player names from teamStats_data to match against.
team_names = teamStats_data['Player'].unique()

# For each player in raw_data, attempt to find the best match in team_names.
raw_data['Matched_Player'] = raw_data['Player'].apply(lambda x: get_best_match(x, team_names))

# --- Step 4. Merge the Datasets ---
merged_data = pd.merge(
    raw_data,
    teamStats_data,
    left_on='Matched_Player',  # fuzzy matched name from raw_data
    right_on='Player',         # normalized name in teamStats_data
    how='left',
    suffixes=('_raw', '_team'),
    indicator=True            # adds a column '_merge' to indicate merge status
)

# --- (Optional) Print Summary Information ---
total_unique_raw = raw_data['Player'].nunique()
total_unique_team = teamStats_data['Player'].nunique()
unique_matched = raw_data[raw_data['Matched_Player'].notnull()]['Player'].nunique()
unmatched_players = raw_data[raw_data['Matched_Player'].isnull()]['Player'].unique()

print(f"Total unique players in raw_data (Season 2024): {total_unique_raw}")
print(f"Total unique players in teamStats_data: {total_unique_team}")
print(f"Unique players in raw_data with a fuzzy match: {unique_matched}")
print(f"Unique players in raw_data that did NOT get a fuzzy match: {len(unmatched_players)}")
if len(unmatched_players) > 0:
    print("List of unmatched players:")
    for player in unmatched_players:
        print(f"- {player}")

# --- Step 5. Save the Merged DataFrame as CSV ---
merged_data.to_csv('../Data/knnData.csv', index=False)

print("\nMerged data saved as '../Data/knnData.csv'.")
import pandas as pd
import ast
from datetime import datetime

# getting the gam for 2025
gam = pd.read_csv('2025 GAM.csv')

# getting the tam for 2025
tam = 2225000

# getting the salary cap for 2025
cap = 5950000

# dp salary budget charge
dp_charge = 743750

players = pd.read_csv('ASA_Players_API.csv')

players['season_name'] = players['season_name'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x
)

players = players.explode('season_name').reset_index(drop=True)

players = players.loc[players['season_name'] == '2024']

players['season_name'] = players['season_name'].astype(float)

salaries = pd.read_csv('Salary_Data_ASI.csv')

overall_players = pd.merge(players, salaries, on=['player_id', 'season_name'], how='inner')

overall_players = overall_players.loc[overall_players['mlspa_release'] == '2024-09-13']

dropped_columns = ['player_id', 'secondary_broad_position', 'secondary_general_position', 'competition', 
                   'position', 'height_ft', 'height_in', 'weight_lb', 'mlspa_release']

overall_players.drop(columns=dropped_columns, inplace=True)

overall_players.reset_index(drop=True, inplace=True)

teams = pd.read_csv('Teams_Data_ASI.csv')

teams = teams[['team_id', 'team_abbreviation']]

overall_players = pd.merge(overall_players, teams, on='team_id', how='inner')

del overall_players['team_id']

# Calculate current age
def calculate_age(birth_date):
    if pd.isnull(birth_date):
        return None
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

overall_players['age'] = overall_players['birth_date'].apply(calculate_age)

del overall_players['birth_date'], overall_players['guaranteed_compensation']

overall_players.loc[overall_players['player_name'] == 'Jasper Löeffelsend', 'nationality'] = 'Germany'
overall_players.loc[overall_players['player_name'] == 'Noah Cobb', 'nationality'] = 'USA'

overall_players['American'] = (overall_players['nationality'] == 'USA').astype(int)

overall_players.loc[overall_players['player_name'] == 'Kimani Stewart-Baynes', 'age'] = 19
overall_players.loc[overall_players['player_name'] == 'Ali Ahmed', 'age'] = 24
overall_players.loc[overall_players['player_name'] == 'Mohammed Sofo', 'age'] = 20
overall_players.loc[overall_players['player_name'] == 'Yutaro Tsukada', 'age'] = 23
overall_players.loc[overall_players['player_name'] == 'Esmir Bajraktarevic', 'age'] = 19
overall_players.loc[overall_players['player_name'] == 'Josh Bauer', 'age'] = 26
overall_players.loc[overall_players['player_name'] == 'Jasper Löeffelsend', 'age'] = 27
overall_players.loc[overall_players['player_name'] == 'Noah Cobb', 'age'] = 19

del overall_players['nationality']

overall_players.to_csv('Processed_ASI_Data.csv', index=False)

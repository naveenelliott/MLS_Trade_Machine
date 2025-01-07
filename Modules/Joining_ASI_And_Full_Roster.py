import pandas as pd
import unicodedata

def normalize_name(name):
    return unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')

# Load ASI data
asi_data = pd.read_csv('Processed_ASI_Data.csv')

roster = pd.read_csv('Final_Roster_Before_ASI.csv')

#roster = roster.loc[roster['CURRENT STATUS'].isna()]

asi_data['player_name'] = asi_data['player_name'].str.lower().apply(normalize_name)
roster['NAME'] = roster['NAME'].str.lower().apply(normalize_name)

# ignoring loffelsend
asi_data['player_name'] = asi_data['player_name'].replace('aleksey miranchuk', 'alexey miranchuk')
asi_data['player_name'] = asi_data['player_name'].replace('anthony markanich', 'anthony markanich jr')
asi_data['player_name'] = asi_data['player_name'].replace('charles sharp', 'charlie sharp')
asi_data['player_name'] = asi_data['player_name'].replace('christopher olney jr.', 'cj olney')
asi_data['player_name'] = asi_data['player_name'].replace('derrick etienne jr.', 'derrick etienne jr')
asi_data['player_name'] = asi_data['player_name'].replace('maxi moralez', 'maximiliano moralez')
asi_data['player_name'] = asi_data['player_name'].replace('monsef bakrar', 'mounsef bakrar')
asi_data['player_name'] = asi_data['player_name'].replace('jeong sang-bin', 'sang bin jeong')
asi_data['player_name'] = asi_data['player_name'].replace('serge ngoma', 'serge ngoma jr.')
asi_data['player_name'] = asi_data['player_name'].replace('tani oluwaseyi', 'tanitoluwa oluwaseyi')


roster['NAME'] = roster['NAME'].replace('dominic lankov', 'dominic iankov')
roster['NAME'] = roster['NAME'].replace('lan fray', 'ian fray')
roster['NAME'] = roster['NAME'].replace('lan harkes', 'ian harkes')
roster['NAME'] = roster['NAME'].replace('lan murphy', 'ian murphy')
roster['NAME'] = roster['NAME'].replace('maximiliano david ayala', 'david ayala')
roster['NAME'] = roster['NAME'].replace('mitja llenic', 'mitja ilenic')
roster['NAME'] = roster['NAME'].replace('luri tavares', 'iuri tavares')

# 670
end = pd.merge(asi_data, roster, left_on='player_name', right_on='NAME', how='inner')

unmatched_df = asi_data[~asi_data['player_name'].isin(end['player_name'])]

pre_houston_sje = unmatched_df.loc[~unmatched_df['team_abbreviation'].isin(['SJE', 'HOU'])]


unmatched_df_roster = roster[~roster['NAME'].isin(end['NAME'])]

removed_columns = ['primary_broad_position', 'primary_general_position', 'season_name',
                   'player_name', 'Team']

end.drop(columns=removed_columns, inplace=True)

end.loc[
    end['CURRENT STATUS'].isna() & end['ROSTER DESIGNATION'].isna(),
    'ROSTER DESIGNATION'
] = 'Squad Player'

end.to_csv('FinalCombinedDataset.csv', index=False)


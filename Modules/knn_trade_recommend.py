import pandas as pd
import streamlit as st
import unicodedata
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# --- Helper Functions for Name Standardization ---

def normalize_name(name):
    """Normalize names by removing accents and converting to lowercase."""
    return unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')

# Manual mapping dictionary (update as needed)
manual_mapping = {
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
    "nathan": "nathan cardoso",                  # nathan -> Nathan Cardoso
    "carl sainte": "carle-fred sainte",           # carl sainte -> Carle-Fred Sainte
    "idan toklomati": "idan markovich",          # idan toklomati -> Idan Markovich
    "sang bin jeong": "jeong sangbin",            # sang bin jeong -> Jeong Sangbin
    "ben lundt": "benjamin lundt",                # ben lundt -> Benjamin Lundt
    "gabriel pec": "gabriel chaves",              # gabriel pec -> Gabriel Chaves
    "cj olney": "christopher olney"               # cj olney -> Christopher Olney
}

def standardize_name(name):
    """Standardize the player name by lowercasing, normalizing, and applying manual mappings."""
    if not isinstance(name, str):
        return name
    name = name.lower().strip()
    name = normalize_name(name)
    return manual_mapping.get(name, name)

# --- Recommendation Function ---

def recommend_players(players, data):
    """
    Given a list of player names and a dataset, recommend similar players.
    Only candidates matching the selected player's position(s), having a lower salary,
    and with a roster designation other than 'Designated Player' are considered.
    The returned player names are converted to title case.
    """
    n_similar = 3
    recommendations = {}
    
    # Define the columns to consider for similarity (adjust as needed)
    columns_to_consider = [
        'Gls_standard','Ast_standard','G+A_standard','G-PK_standard','PK_standard','PKatt_standard','CrdY_standard','CrdR_standard','xG_standard',
        'npxG_standard','xAG_standard','npxG+xAG_standard','PrgC_standard','PrgP_standard','PrgR_standard','G+A-PK_standard','xG+xAG_standard',
        'GA_goalkeeping','GA90_goalkeeping','SoTA_goalkeeping','Saves_goalkeeping','Save%_goalkeeping','W_goalkeeping','D_goalkeeping',
        'L_goalkeeping','CS_goalkeeping','CS%_goalkeeping','PKatt_goalkeeping','PKA_goalkeeping','PKsv_goalkeeping','PKm_goalkeeping','90s_advanced_goalkeeping',
        'GA_advanced_goalkeeping','PKA_advanced_goalkeeping','FK_advanced_goalkeeping','CK_advanced_goalkeeping','OG_advanced_goalkeeping',
        'PSxG_advanced_goalkeeping','PSxG/SoT_advanced_goalkeeping','PSxG+/-_advanced_goalkeeping','/90_advanced_goalkeeping','Cmp_advanced_goalkeeping','Att_advanced_goalkeeping','Cmp%_advanced_goalkeeping',
        'Att (GK)_advanced_goalkeeping','Thr_advanced_goalkeeping','Launch%_advanced_goalkeeping','AvgLen_advanced_goalkeeping','Opp_advanced_goalkeeping',
        'Stp_advanced_goalkeeping','Stp%_advanced_goalkeeping','#OPA_advanced_goalkeeping','#OPA/90_advanced_goalkeeping','AvgDist_advanced_goalkeeping',
        'Gls_shooting','Sh_shooting,SoT_shooting','SoT%_shooting','Sh/90_shooting,SoT/90_shooting','G/Sh_shooting','G/SoT_shooting',
        'Dist_shooting','FK_shooting','PK_shooting','PKatt_shooting','xG_shooting','npxG_shooting','npxG/Sh_shooting','G-xG_shooting',
        'np:G-xG_shooting','Cmp_passing','Att_passing','Cmp%_passing','TotDist_passing','PrgDist_passing','Ast_passing','xAG_passing',
        'xA_passing','A-xAG_passing','KP_passing','1/3_passing','PPA_passing','CrsPA_passing','PrgP_passing','90s_pass_type',
        'Att_pass_type','Live_pass_type','Dead_pass_type','FK_pass_type','TB_pass_type','Sw_pass_type','Crs_pass_type','TI_pass_type','CK_pass_type',
        'In_pass_type','Out_pass_type','Str_pass_type','Cmp_pass_type','Off_pass_type','Blocks_pass_type','90s_goal_&_shot_creation',
        'SCA_goal_&_shot_creation','SCA90_goal_&_shot_creation','PassLive_goal_&_shot_creation','PassDead_goal_&_shot_creation',
        'TO_goal_&_shot_creation','Sh_goal_&_shot_creation','Fld_goal_&_shot_creation','Def_goal_&_shot_creation','GCA_goal_&_shot_creation',
        'GCA90_goal_&_shot_creation','Tkl_defense','TklW_defense','Def 3rd_defense','Mid 3rd_defense','Att 3rd_defense','Att_defense','Tkl%_defense',
        'Lost_defense','Blocks_defense','Sh_defense','Pass_defense','Int_defense','Tkl+Int_defense','Clr_defense','Err_defense','Touches_possession','Def Pen_possession',
        'Def 3rd_possession','Mid 3rd_possession','Att 3rd_possession','Att Pen_possession','Live_possession','Att_possession','Succ_possession',
        'Succ%_possession','Tkld_possession','Tkld%_possession','Carries_possession','TotDist_possession','PrgDist_possession','PrgC_possession','1/3_possession',
        'CPA_possession','Mis_possession','Dis_possession','Rec_possession','PrgR_possession','Mn/MP_playing_time','Min%_playing_time',
        '90s_playing_time','Starts_playing_time','Mn/Start_playing_time','Compl_playing_time','Subs_playing_time','Mn/Sub_playing_time',
        'unSub_playing_time','PPM_playing_time','onG_playing_time','onGA_playing_time','+/-_playing_time','+/-90_playing_time','On-Off_playing_time','onxG_playing_time',
        'onxGA_playing_time','xG+/-_playing_time','xG+/-90_playing_time','CrdY_miscellaneous','CrdR_miscellaneous','2CrdY_miscellaneous',
        'Fls_miscellaneous','Fld_miscellaneous','Off_miscellaneous','Crs_miscellaneous','Int_miscellaneous','TklW_miscellaneous','PKwon_miscellaneous',
        'PKcon_miscellaneous','OG_miscellaneous','Recov_miscellaneous','Won_miscellaneous','Lost_miscellaneous','Won%_miscellaneous'
    ]
    
    # Fill missing values and filter candidate columns
    data = data.fillna(0)
    columns_to_consider = [col for col in columns_to_consider if col in data.columns]
    
    # Standardize the 'NAME' column in the dataset
    data = data.copy()
    data['NAME'] = data['NAME'].astype(str).apply(standardize_name)
    
    # Standardize the input player names as well
    standardized_players = [standardize_name(p) for p in players]
    
    # Fit a scaler on the full dataset (for the selected numeric columns)
    scaler = StandardScaler()
    _ = scaler.fit_transform(data[columns_to_consider])  # Fit scaler on full data
    
    # Loop over each standardized player to find recommendations
    for player_name in standardized_players:
        # Get the selected player's stats for the similarity columns
        selected_player_stats = data[data['NAME'] == player_name][columns_to_consider]
        if selected_player_stats.empty:
            recommendations[player_name.title()] = ["Player not found in dataset"]
            continue

        # Retrieve the full row of the selected player for filtering
        selected_player = data[data['NAME'] == player_name].iloc[0]
        selected_pos1 = selected_player["Pos_1"]
        selected_pos2 = selected_player["Pos_2"]
        selected_salary = selected_player["base_salary"]
        
        # Filter candidate players:
        # 1. Exclude the selected player.
        # 2. Only keep candidates whose Pos_1 or Pos_2 matches one of the selected player's positions.
        # 3. Only keep candidates with a base_salary lower than that of the selected player.
        # 4. Exclude candidates with ROSTER DESIGNATION equal to 'Designated Player'.
        data_fil = data[data['NAME'] != player_name]
        data_fil = data_fil[
            ((data_fil["Pos_1"].isin([selected_pos1, selected_pos2])) | (data_fil["Pos_2"].isin([selected_pos1, selected_pos2])))
            & (data_fil["base_salary"] < selected_salary)
            & (data_fil["ROSTER DESIGNATION"] != "Designated Player")
        ]
        
        if data_fil.empty:
            recommendations[player_name.title()] = ["No matching candidate players found"]
            continue
        
        # Scale the features for the selected player and the filtered candidates
        selected_player_scaled = scaler.transform(selected_player_stats)
        candidate_scaled = scaler.transform(data_fil[columns_to_consider])
        
        # Train a KNN model on the filtered candidate set
        knn_filtered = NearestNeighbors(n_neighbors=n_similar, metric='euclidean')
        knn_filtered.fit(candidate_scaled)
        distances, indices = knn_filtered.kneighbors(selected_player_scaled)
        similar_players = data_fil.iloc[indices[0]]
        
        # Build the recommendation output, ensuring player names are in title case.
        recommendation = []
        for _, player in similar_players.iterrows():
            # Use title() to capitalize each word in the player's name.
            candidate_name = player['NAME'].title()
            team_name = player.get('team_name', 'Unknown Team')
            recommendation.append(f"{candidate_name} of {team_name}")
        
        recommendations[player_name.title()] = recommendation
        
    return recommendations

import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

def recommend_players(players, data):
    n_similar = 3
    recommendations = {}
    columns_to_consider = [
    'Shots', 'SoT', 'G', 'xG', 'xPlace', 'G-xG', 'KeyP', 'A', 'xA', 'A-xA', 'xG+xA', 'PA',
    'xPA', 'Passes', 'Pass %', 'xPass %', 'Score', 'Per100', 'Distance', 'Vertical', 'Touch %', 'Shots Faced',
    'Goals Conceded', 'Saves', 'Header %', 'xGA', 'G-xGA', 'G/xG', 'Dribbling', 'Fouling', 'Interrupting', 'Passing',
    'Receiving', 'Shooting', 'Goals Added', 'Shots_transition', 'SoT_transition', 'G_transition', 'xG_transition',
    'xPlace_transition', 'G-xG_transition', 'KeyP_transition', 'A_transition', 'xA_transition', 'A-xA_transition',
    'xG+xA_transition', 'Passes_defend', 'Pass %_defend', 'xPass %_defend', 'Score_defend', 'Per100_defend',
    'Distance_defend', 'Vertical_defend', 'Touch %_defend', 'Passes_middle', 'Pass %_middle', 'xPass %_middle',
    'Score_middle', 'Per100_middle', 'Distance_middle', 'Vertical_middle', 'Touch %_middle', 'Passes_attack',
    'Pass %_attack', 'xPass %_attack', 'Score_attack', 'Per100_attack', 'Distance_attack', 'Vertical_attack',
    'Touch %_attack'
    ]
    data = data.fillna(0)
    columns_to_consider = [col for col in columns_to_consider if col in data.columns]
    numeric_columns = [col for col in columns_to_consider if col in data.columns]
    data_aggregated = data.groupby(['Player', 'Team'], as_index=False)[numeric_columns].mean()

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data_aggregated[columns_to_consider])

    # Train the KNN model
    knn = NearestNeighbors(n_neighbors=n_similar, metric='euclidean')
    knn.fit(scaled_features)

    for player_name in players:
        data_fil = data_aggregated[data_aggregated['Player'] != player_name]
        # Get stats for the selected player
        selected_player_stats = data_aggregated[data_aggregated['Player'] == player_name][columns_to_consider]

        if selected_player_stats.empty:
            recommendations[player_name] = ["Player not found in dataset"]
            continue

        # Scale the selected player stats
        selected_player_scaled = scaler.transform(selected_player_stats)

        # Find similar players
        distances, indices = knn.kneighbors(selected_player_scaled)
        similar_players = data_fil.iloc[indices[0]]

        # Build the recommendation output
        recommendation = []
        for _, player in similar_players.iterrows():
            recommendation.append(f"{player['Player']} of {player['Team']}")

        recommendations[player_name] = recommendation
    return recommendations
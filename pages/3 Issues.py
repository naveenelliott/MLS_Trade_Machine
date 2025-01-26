import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

conn = st.connection('gsheets', type=GSheetsConnection)

existing_data = conn.read(worksheet='PMR', ttl=0)
existing_data.dropna(how='all', inplace=True)
existing_data['Player'] = existing_data['Player'].fillna('').astype(str)
existing_data['Current Team'] = existing_data['Current Team'].fillna('').astype(str)
existing_data['New Team'] = existing_data['New Team'].fillna('').astype(str)


asi_data = pd.read_csv('./Data/FinalCombinedDataset.csv')
asi_data['NAME'] = asi_data['NAME'].str.title()



#conn.update(worksheet='PMR', data=updated_df)
st.success("Input updated!")
st.rerun()  # Rerun to refresh the displayed DataFrame
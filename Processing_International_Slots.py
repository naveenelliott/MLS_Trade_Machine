import os
import pandas as pd

# Path to the folder containing the CSV files
folder_path = "INTERNATIONAL SLOTS/"

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
combined_df = pd.concat(dataframes, ignore_index=True)

combined_df["NO."] = pd.to_numeric(combined_df["NO."], errors="coerce")

# Group by 'File Name' and reassign sequential numbers
combined_df["NO."] = (
    combined_df.groupby("Team")["NO."]
    .apply(lambda group: range(1, len(group) + 1))
)

combined_df["NAME"] = combined_df["NAME"].str.replace(r"[*+^]", "", regex=True)


del combined_df['Validation Link'], combined_df['File Name']

combined_df["NO."] = (
    combined_df.groupby("Team").cumcount() + 1
)


combined_df.to_csv('INTERNATIONAL_SLOTS.csv', index=False)

slot_numbers = combined_df.groupby("Team").size().reset_index(name="Slot Numbers")

slot_numbers.to_csv('INT_SLOT_NUMBERS.csv', index=False)
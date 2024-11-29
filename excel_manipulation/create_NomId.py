# Load the data from the Excel file
import pandas as pd
# Read the Excel file
oscars_df = pd.read_excel('oscars.xlsx', sheet_name='oscars')

# Create a new column 'NomId_Number' that assigns a unique number to each unique NomId
# First, we will create a mapping for NomId, treating nulls as unique
nomid_mapping = {nomid: idx for idx, nomid in enumerate(oscars_df['NomId'].unique())}

# Now, we will create a new column 'NomId_Number' based on this mapping
oscars_df['NomId_Number'] = oscars_df['NomId'].map(nomid_mapping)

# For null values, we will assign a unique number starting from the last index
null_count = oscars_df['NomId'].isnull().sum()
oscars_df.loc[oscars_df['NomId'].isnull(), 'NomId_Number'] = range(len(nomid_mapping), len(nomid_mapping) + null_count)

# Display the head of the modified dataframe
oscars_df.to_excel('oscars.xlsx', index=False, sheet_name='oscars')


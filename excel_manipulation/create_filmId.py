# This script will read the Excel file, create unique identifiers for NomId and FilmId, and save the modified dataframe back to the same file.

import pandas as pd

# Load the data from the Excel file

oscars_df = pd.read_excel('oscars.xlsx', sheet_name='Sheet1')



# Create a unique identifier for FilmId
film_id_mapping = {film_id: idx + 1 for idx, film_id in enumerate(oscars_df['FilmId'].unique())}

# Now, we will create a new column 'FilmId_Number' based on this new mapping
oscars_df['FilmId_Number'] = oscars_df['FilmId'].apply(lambda x: film_id_mapping[x] if pd.notnull(x) else None)


# Save the modified dataframe back to the same Excel file
oscars_df.to_excel('oscars.xlsx', index=False)

# Display the head of the modified dataframe
print(oscars_df.head())
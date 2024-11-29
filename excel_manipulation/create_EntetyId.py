# Import required libraries
import pandas as pd
import numpy as np

def process_oscars_data(input_file, output_file):
    """
    Process the Oscars data to create EntityId column with proper handling of null values.
    
    Args:
        input_file (str): Path to input Excel file
        output_file (str): Path to save the processed Excel file
    """
    # Load the data
    print("Loading data from:", input_file)
    df = pd.read_excel(input_file)
    
    print("\
Initial data shape:", df.shape)
    print("\
Null values in NomineeIds before processing:", df['NomineeIds'].isna().sum())
    print("Question marks in NomineeIds before processing:", df[df['NomineeIds'] == '?'].shape[0])
    
    # Create a mapping of Nominees to new IDs for null/? NomineeIds
    null_nominees = df[df['NomineeIds'].isna() | (df['NomineeIds'] == '?')][['Nominees', 'NomineeIds']].drop_duplicates()
    new_ids = {nominee: f'temp_id_{i}' for i, nominee in enumerate(null_nominees['Nominees'].unique())}
    
    # Fill null/? NomineeIds with temporary IDs based on Nominees
    df['NomineeIds'] = df.apply(
        lambda row: new_ids[row['Nominees']] 
        if (pd.isna(row['NomineeIds']) or row['NomineeIds'] == '?') 
        else row['NomineeIds'], 
        axis=1
    )
    
    print("\
Null values in NomineeIds after filling:", df['NomineeIds'].isna().sum())
    print("Question marks in NomineeIds after filling:", df[df['NomineeIds'] == '?'].shape[0])
    
    # Create EntityId column by assigning unique numbers to each unique NomineeId
    def assign_entity_id(column):
        unique_values = column.unique()
        value_to_id = {value: idx for idx, value in enumerate(unique_values)}
        return column.map(value_to_id)
    
    df['EntityId'] = assign_entity_id(df['NomineeIds'])
    
    # Save the processed dataframe
    df.to_excel(output_file, index=False,sheet_name='oscars')
    print(f"\
Processed data saved to: {output_file}")
    
    # Display sample results
    print("\
Sample of the processed data:")
    print(df[['Nominees', 'NomineeIds', 'EntityId']].head(10))
    
    # Print some statistics
    print("\
Total unique EntityIds created:", df['EntityId'].nunique())
    print("Total rows processed:", len(df))

# Execute the processing
input_file = 'oscars.xlsx'
output_file = 'oscars_with_entityid_final.xlsx'
process_oscars_data(input_file, output_file)

# Complete script for processing Oscar data
import pandas as pd

def split_rows(df, name_column, id_column):
    """
    Split rows containing comma-separated values in specified columns.
    
    Parameters:
    df (DataFrame): Input DataFrame
    name_column (str): Column containing names to split
    id_column (str): Column containing IDs to split
    
    Returns:
    DataFrame: Processed DataFrame with split rows
    """
    new_rows = []
    for index, row in df.iterrows():
        if pd.notnull(row[name_column]) and ',' in str(row[name_column]):
            # Split both the names and IDs
            names = [n.strip() for n in str(row[name_column]).split(',')]
            ids = [i.strip() for i in str(row[id_column]).split(',')] if pd.notnull(row[id_column]) else [''] * len(names)
            
            # Make sure we have matching pairs
            for name, id_val in zip(names, ids):
                new_row = row.copy()
                new_row[name_column] = name
                new_row[id_column] = id_val
                new_rows.append(new_row)
        else:
            new_rows.append(row)
    return pd.DataFrame(new_rows)

# Main processing
def process_oscars_data(input_file, output_file):
    """
    Main function to process Oscar data file
    
    Parameters:
    input_file (str): Path to input Excel file
    output_file (str): Path to save processed Excel file
    """
    # Load the data
    print("Loading data from:", input_file)
    df = pd.read_excel(input_file)
    
    # Process the data
    print("Processing data...")
    split_df = split_rows(df, 'Nominees', 'NomineeIds')
    
    # Save the processed data
    print("Saving processed data to:", output_file)
    split_df.to_excel(output_file, index=False)
    
    return split_df

# Execute the processing
input_file = 'oscars.xlsx'
output_file = 'oscars_nominees_split.xlsx'
processed_df = process_oscars_data(input_file, output_file)

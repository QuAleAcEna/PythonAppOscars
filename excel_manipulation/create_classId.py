import pandas as pd

# Load the Excel file
file_path = 'oscars.xlsx'
data = pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dictionary of DataFrames

# Process each sheet
for sheet_name, df in data.items():
    # Assign unique numbers to 'class_id' based on unique values in 'name'
    df['class_id'] = df['Class'].astype('category').cat.codes
    data[sheet_name] = df

# Save back to the same file
with pd.ExcelWriter(file_path) as writer:
    for sheet_name, df in data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Data updated and saved back to:", file_path)
print("\
First few rows of updated data:")
print(data['Sheet1'].head())
import pandas as pd

# Load the Excel file
file_path = 'oscars.xlsx'
data = pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dictionary of DataFrames

# Add a new column 'categoryId' based on unique values in 'Category'
for sheet_name, df in data.items():
    df['categoryId'] = df['Category'].astype('category').cat.codes
    data[sheet_name] = df

# Save the updated data back to the same file
with pd.ExcelWriter(file_path) as writer:
    for sheet_name, df in data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("The 'categoryId' column has been added and saved back to the same file: oscars.xlsx")
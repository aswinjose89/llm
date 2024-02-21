import pandas as pd

# Specify the path to your JSON file
json_file_path = "./dataset/from_matt_af_quantumventura.json"

# Read the JSON file into a Pandas DataFrame
df = pd.read_json(json_file_path)

df['date'] = df['date'].dt.tz_localize(None)

# Specify the path for the Excel file
excel_file_path = "./dataset/from_matt_af_quantumventura.xlsx"

# Save the DataFrame as an Excel file
df.to_excel(excel_file_path, index=False)

print(f"Excel file '{excel_file_path}' created successfully.")

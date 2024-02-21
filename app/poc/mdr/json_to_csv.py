import pandas as pd

json_file_path="./dataset/from_matt_af_quantumventura.json"
df = pd.read_json(json_file_path)

# Specify the output CSV file path
csv_file_path = "./dataset/from_matt_af_quantumventura.csv"
# df= df.drop('date', axis=1)
# Save the DataFrame as a CSV file
df.to_csv(csv_file_path, index=False)

print(f"CSV file '{csv_file_path}' created successfully.")

import pandas as pd

csv_file_path="./dataset/success/dataset_under_25_years_llama.csv"
df = pd.read_csv(csv_file_path)

# Specify the path for the Excel file
excel_file_path = "./dataset/success/dataset_under_25_years.xlsx"

# Save the DataFrame as an Excel file
df.to_excel(excel_file_path, index=False)

print(f"Excel file '{excel_file_path}' created successfully.")

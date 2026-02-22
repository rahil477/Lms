import pandas as pd
import json

file_path = r'C:\Users\Rahil\Downloads\DigiArt_Academy_Jurnal_5533U.xlsx'

try:
    # Read all sheets
    xl = pd.ExcelFile(file_path)
    print(f"Sheets: {xl.sheet_names}")
    
    for sheet_name in xl.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("First 50 rows:")
        print(df.head(50).to_string())
        
except Exception as e:
    print(f"Error reading Excel: {e}")

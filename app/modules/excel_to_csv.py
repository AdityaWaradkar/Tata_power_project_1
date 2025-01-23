import pandas as pd
import os

def convert_excel_to_csv(excel_file, csv_file_name):
    assets_folder = os.path.join(os.getcwd(), '../../assets')
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    
    # Read the uploaded Excel file directly from the Streamlit file buffer
    df = pd.read_excel(excel_file)
    
    if len(df.columns) > 1:
        df.rename(columns={df.columns[1]: "Power MW"}, inplace=True)
    
    csv_file_path = os.path.join(assets_folder, csv_file_name)
    df.to_csv(csv_file_path, index=False)
    print(f"Excel file has been converted to CSV and saved as '{csv_file_name}' in the assets folder.")

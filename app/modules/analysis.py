import pandas as pd
import numpy as np
import os

def calculate_daily_losses(df, clipping_line=27.5):
    try:
        print("Processing 'Date' column...")
        df['Date'] = df['Date'].astype(str).str.split(' ').str[0]  # Extract date part as string
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        print("Successfully processed 'Date' column.")
    except Exception as e:
        print(f"Error processing 'Date' column: {e}")
        return None
    
    print("Extracting 'Day' from 'Date' column...")
    df['Day'] = df['Date'].dt.date  # Assign the date part to a new column
    
    df.columns = df.columns.str.strip()
    
    required_columns = ['incremented_energy MWh', 'Energy MWh']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return None
    
    print("Calculating losses for each row...")
    df['Loss Without Clipping'] = df['incremented_energy MWh'] - df['Energy MWh']
    
    df['Loss With Clipping'] = np.where(
        (df['incremented_energy MWh'] <= clipping_line) & (df['Energy MWh'] <= clipping_line),
        df['incremented_energy MWh'] - df['Energy MWh'],  # Case 1: Both below clipping line
        np.where(
            (df['incremented_energy MWh'] > clipping_line) & (df['Energy MWh'] <= clipping_line),
            clipping_line - df['Energy MWh'],  # Case 2: Incremented above but Energy below
            0  # Case 3: Both above clipping line, no loss considered
        )
    )
    
    df['Loss Difference'] = df['Loss Without Clipping'] - df['Loss With Clipping']
    
    print("Aggregating daily losses...")
    daily_losses = df.groupby('Day').agg(
        Loss_Without_Clipping=('Loss Without Clipping', 'sum'),
        Loss_With_Clipping=('Loss With Clipping', 'sum'),
        Loss_Difference=('Loss Difference', 'sum')
    ).reset_index()
    
    print("Daily losses calculated successfully.")
    return daily_losses

try:
    assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
    file_path = os.path.join(assets_folder, 'calculated_data.csv')
    
    df_calculated = pd.read_csv(file_path)
    print("Data loaded successfully from 'calculated_data.csv'.")
except Exception as e:
    print(f"Error loading data: {e}")
    df_calculated = None

if df_calculated is not None:
    results = calculate_daily_losses(df_calculated)
    if results is not None:
        print("\nFinal Results:")
        print(results)
        results_file_path = os.path.join(assets_folder, 'analysed_data.csv')
        results.to_csv(results_file_path, index=False)
        print(f"Results saved to '{results_file_path}'")
